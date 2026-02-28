// Room Timeline — structured event log for post-game forensics.
// Every significant room event is appended to an in-memory timeline.
// On game end (or crash), dump to structured JSON for debugging.
// In production, pipe to your logging service (Loki, Datadog, etc.).

// ── Types ──────────────────────────────────────────────────────────────────────

export type TimelineEventType =
  | "room:created"
  | "player:joined"
  | "player:left"
  | "player:disconnected"
  | "player:reconnected"
  | "player:kicked"
  | "vip:assigned"
  | "vip:transferred"
  | "phase:started"
  | "phase:ended"
  | "phase:timeout"
  | "submit:accepted"
  | "submit:rejected"
  | "vote:cast"
  | "score:awarded"
  | "game:started"
  | "game:ended"
  | "error:caught";

export interface TimelineEntry {
  ts: number; // Date.now()
  seq: number; // Monotonic sequence within room
  event: TimelineEventType;
  playerId?: string;
  phase?: string;
  data?: Record<string, unknown>;
}

export interface RoomTimeline {
  roomCode: string;
  createdAt: number;
  entries: TimelineEntry[];
}

// ── Timeline class ─────────────────────────────────────────────────────────────

export class Timeline {
  private roomCode: string;
  private createdAt: number;
  private entries: TimelineEntry[] = [];
  private seq = 0;
  private maxEntries: number;

  constructor(roomCode: string, opts?: { maxEntries?: number }) {
    this.roomCode = roomCode;
    this.createdAt = Date.now();
    this.maxEntries = opts?.maxEntries ?? 10_000;
  }

  /** Append an event. Silently drops if over maxEntries to prevent memory leaks. */
  push(
    event: TimelineEventType,
    details?: { playerId?: string; phase?: string; data?: Record<string, unknown> }
  ): void {
    if (this.entries.length >= this.maxEntries) return;

    this.entries.push({
      ts: Date.now(),
      seq: this.seq++,
      event,
      playerId: details?.playerId,
      phase: details?.phase,
      data: details?.data,
    });
  }

  /** Return the full timeline as a serializable object. */
  dump(): RoomTimeline {
    return {
      roomCode: this.roomCode,
      createdAt: this.createdAt,
      entries: this.entries,
    };
  }

  /** Return last N entries (for live debug endpoints). */
  tail(n = 50): TimelineEntry[] {
    return this.entries.slice(-n);
  }

  /** Filter entries by event type. */
  filter(type: TimelineEventType): TimelineEntry[] {
    return this.entries.filter((e) => e.event === type);
  }

  /** Summary stats for quick triage. */
  summary(): {
    totalEvents: number;
    duration: number;
    playerJoins: number;
    playerLeaves: number;
    phaseCount: number;
    errors: number;
    submits: number;
  } {
    return {
      totalEvents: this.entries.length,
      duration: Date.now() - this.createdAt,
      playerJoins: this.filter("player:joined").length,
      playerLeaves: this.filter("player:left").length,
      phaseCount: this.filter("phase:started").length,
      errors: this.filter("error:caught").length,
      submits:
        this.filter("submit:accepted").length +
        this.filter("submit:rejected").length,
    };
  }
}

// ── Integration example ────────────────────────────────────────────────────────
//
// const rooms = new Map<string, { timeline: Timeline; /* ...room state */ }>();
//
// function createRoom(code: string) {
//   const timeline = new Timeline(code);
//   timeline.push('room:created');
//   rooms.set(code, { timeline });
// }
//
// // On game end, dump for logging:
// function endGame(code: string) {
//   const room = rooms.get(code);
//   if (!room) return;
//   const dump = room.timeline.dump();
//   console.log(JSON.stringify(dump)); // or send to Loki/Datadog
//   rooms.delete(code);
// }
//
// // Debug endpoint (admin only, behind auth):
// app.get('/admin/room/:code/timeline', (req, res) => {
//   const room = rooms.get(req.params.code);
//   if (!room) return res.status(404).json({ error: 'Room not found' });
//   res.json({
//     summary: room.timeline.summary(),
//     recent: room.timeline.tail(100),
//   });
// });
