// Protocol Envelope — dedup, version gating, and phase guarding for Socket.IO party games.
// Wrap every client->server event in a ClientEnvelope. Server responds with ServerAck.
// Prevents: stale submits after phase change, duplicate events on reconnect, version drift after deploy.

import { randomUUID } from "crypto";
import type { Socket } from "socket.io";

// ── Types ──────────────────────────────────────────────────────────────────────

export interface ClientEnvelope<T = unknown> {
  protocolVersion: number;
  roomCode: string;
  playerId: string;
  phaseInstanceId: string; // UUID generated each time a phase starts
  clientSeq: number; // Monotonic per player session — dedup on reconnect
  sentAt: number; // client Date.now() — for latency tracking
  payload: T;
}

export interface ServerAck {
  clientSeq: number;
  accepted: boolean;
  reason?: "PHASE_MISMATCH" | "DUPLICATE" | "VERSION_MISMATCH" | "INVALID";
  serverTime: number;
  stateVersion: number;
}

// ── Server-side processor ──────────────────────────────────────────────────────

/**
 * Minimum protocol version the server supports. Clients below this are told to
 * refresh. Bump when you ship breaking event changes.
 */
const MIN_SUPPORTED_VERSION = 1;

/** Tracks the highest acked sequence number per player to reject replays. */
const lastAckedSeq = new Map<string, number>();

interface RoomRef {
  currentPhaseInstanceId: string;
  stateVersion: number;
}

/**
 * Process an incoming envelope. Returns the unwrapped payload if valid,
 * or `null` if the message should be silently dropped (ack already sent).
 */
export function processEnvelope<T>(
  envelope: ClientEnvelope<T>,
  room: RoomRef,
  socket: Socket
): T | null {
  const ack = (accepted: boolean, reason?: ServerAck["reason"]): void => {
    const response: ServerAck = {
      clientSeq: envelope.clientSeq,
      accepted,
      reason,
      serverTime: Date.now(),
      stateVersion: room.stateVersion,
    };
    socket.emit("ack", response);
  };

  // 1. Version gate
  if (envelope.protocolVersion < MIN_SUPPORTED_VERSION) {
    ack(false, "VERSION_MISMATCH");
    socket.emit("force-refresh", {
      minVersion: MIN_SUPPORTED_VERSION,
      message: "A new version is available. Please refresh your browser.",
    });
    return null;
  }

  // 2. Dedup — reject replays from reconnection burst
  const prevSeq = lastAckedSeq.get(envelope.playerId) ?? -1;
  if (envelope.clientSeq <= prevSeq) {
    ack(false, "DUPLICATE");
    return null;
  }
  lastAckedSeq.set(envelope.playerId, envelope.clientSeq);

  // 3. Phase guard — reject submits targeting an expired phase
  if (envelope.phaseInstanceId !== room.currentPhaseInstanceId) {
    ack(false, "PHASE_MISMATCH");
    return null;
  }

  // Valid
  ack(true);
  return envelope.payload;
}

// ── Phase instance ID helper ───────────────────────────────────────────────────

/** Call this every time a phase starts. Store the result in room state. */
export function newPhaseInstanceId(): string {
  return randomUUID();
}

// ── Client-side helper (browser) ───────────────────────────────────────────────

/**
 * Usage on the client:
 *
 * ```ts
 * const sender = createEnvelopeSender(PROTOCOL_VERSION, roomCode, playerId);
 *
 * socket.emit('submit-answer', sender(phaseInstanceId, { text: 'My answer' }));
 *
 * socket.on('ack', (ack: ServerAck) => {
 *   if (!ack.accepted && ack.reason === 'VERSION_MISMATCH') {
 *     window.location.reload();
 *   }
 * });
 * ```
 */
export function createEnvelopeSender(
  protocolVersion: number,
  roomCode: string,
  playerId: string
) {
  let seq = 0;

  return <T>(phaseInstanceId: string, payload: T): ClientEnvelope<T> => ({
    protocolVersion,
    roomCode,
    playerId,
    phaseInstanceId,
    clientSeq: ++seq,
    sentAt: Date.now(),
    payload,
  });
}

// ── Cleanup helper ─────────────────────────────────────────────────────────────

/** Call when a player fully leaves (after grace period). */
export function clearPlayerSeq(playerId: string): void {
  lastAckedSeq.delete(playerId);
}
