# Content Safety and Moderation

Sources: Jackbox Party Pack 5-10 moderation features, Rocketcrab chat moderation (tannerkrewson/rocketcrab), Fishbowl content filtering (avimoondra/fishbowl), OWASP input validation guidelines

Covers: Profanity filtering (multi-tier), human moderation queues, family-friendly mode, VIP censoring, chat moderation, accessibility patterns, mobile UX hardening for phone controllers.

## 1. Content Safety Tiers

Jackbox uses a 3-tier content filter system. Implement it as a room-level setting controlled by the VIP.

| Tier | What It Filters | Use Case |
|------|----------------|----------|
| **Off** | Nothing filtered | Private games among adults |
| **Moderate** | Slurs, hate speech, explicit sexual content | Default for most games |
| **Strict** | All profanity, innuendo, suggestive content | Family gatherings, work events, streaming |

### Configuration

```typescript
type ContentFilterLevel = 'off' | 'moderate' | 'strict';

interface ContentFilterConfig {
  level: ContentFilterLevel;
  customBlocklist: string[];  // Room-specific blocked words
  allowlist: string[];        // False positive overrides
}

const FILTER_WORD_LISTS: Record<ContentFilterLevel, string[]> = {
  off: [],
  moderate: ['SLURS_LIST', 'EXPLICIT_LIST'],  // Load from JSON files
  strict: ['SLURS_LIST', 'EXPLICIT_LIST', 'PROFANITY_LIST', 'SUGGESTIVE_LIST'],
};
```

## 2. Profanity Filtering

### Regex-Based Matcher

Use a word-boundary regex approach that handles common evasion tactics (letter substitution, spacing, repetition).

```typescript
class ProfanityFilter {
  private patterns: RegExp[] = [];

  constructor(wordLists: string[][]) {
    for (const list of wordLists) {
      for (const word of list) {
        // Build pattern that catches: f.u.c.k, f_u_c_k, fuuuck
        const spaced = word.split('').join('[\\s._\\-*]*');
        this.patterns.push(new RegExp(`\\b${spaced}\\b`, 'gi'));
      }
    }
  }

  check(text: string): { clean: boolean; matches: string[] } {
    const normalized = this.normalize(text);
    const matches: string[] = [];

    for (const pattern of this.patterns) {
      const found = normalized.match(pattern);
      if (found) matches.push(...found);
    }

    return { clean: matches.length === 0, matches };
  }

  censor(text: string): string {
    let result = text;
    for (const pattern of this.patterns) {
      result = result.replace(pattern, (match) => '*'.repeat(match.length));
    }
    return result;
  }

  private normalize(text: string): string {
    return text
      .replace(/0/g, 'o')
      .replace(/1/g, 'i')
      .replace(/3/g, 'e')
      .replace(/4/g, 'a')
      .replace(/5/g, 's')
      .replace(/@/g, 'a')
      .replace(/\$/g, 's');
  }
}
```

### Integration with Answer Submission

```typescript
const filter = new ProfanityFilter(FILTER_WORD_LISTS[room.settings.contentFilter]);

socket.on('answer:submit', ({ answer }: { answer: string }) => {
  const room = roomManager.getRoomBySocket(socket.id);
  if (!room) return;

  // Length validation
  if (answer.length > 280) {
    return socket.emit('error', { code: 'TOO_LONG', message: 'Answer too long' });
  }

  // Profanity check
  const result = filter.check(answer);
  if (!result.clean && room.settings.contentFilter !== 'off') {
    if (room.settings.moderationMode === 'censor') {
      // Auto-censor and accept
      room.submitAnswer(socket.id, filter.censor(answer));
    } else {
      // Reject submission
      socket.emit('error', {
        code: 'CONTENT_FILTERED',
        message: 'Your answer was filtered. Try again.',
      });
      return;
    }
  }

  room.submitAnswer(socket.id, answer);
  socket.emit('answer:accepted');
});
```

### Word List Management

Store word lists as JSON files, separated by severity and language:

```text
packages/shared/
  wordlists/
    en/
      slurs.json         # Hate speech, slurs (always filtered in moderate+)
      explicit.json      # Sexually explicit terms
      profanity.json     # Common swear words
      suggestive.json    # Innuendo, double entendres
    es/
      slurs.json
      profanity.json
```

## 3. Human Moderation Mode

For streaming or sensitive environments, route all player submissions through a moderation queue before displaying them. The VIP (or a designated moderator) approves or rejects each submission.

```typescript
interface ModerationItem {
  id: string;
  playerId: string;
  playerName: string;
  content: string;
  type: 'answer' | 'drawing' | 'chat';
  timestamp: number;
}
```

Implement a `ModerationManager` with three methods:
- `submit(item)` → adds to pending queue, returns ID
- `approve(itemId)` → moves from pending to approved, emits `content:revealed` to room
- `reject(itemId)` → moves from pending to rejected, emits `content:rejected` to submitter

### VIP Moderation Socket Events

| Event | Direction | Payload | VIP-Only |
|-------|-----------|---------|----------|
| `moderation:fetch` | Client → Server | none | Yes |
| `moderation:queue` | Server → VIP | `ModerationItem[]` | Yes |
| `moderation:approve` | Client → Server | `{ itemId }` | Yes |
| `moderation:reject` | Client → Server | `{ itemId }` | Yes |
| `content:revealed` | Server → All | `{ playerId, content }` | No |
| `content:rejected` | Server → Player | `{ reason }` | No |

Always check `requireVIP(socket, room)` before processing moderation events.

## 4. VIP Censoring

Jackbox allows the VIP to censor content in real-time during the reveal phase. Censored content is visually "scribbled out" and hidden from all players and audience.

```typescript
socket.on('content:censor', ({ contentId }: { contentId: string }) => {
  if (!requireVIP(socket, room)) return;

  room.censorContent(contentId);
  io.to(room.code).emit('content:censored', { contentId });
});
```

### Client-Side Censoring

```tsx
const AnswerCard = ({ answer, isCensored }: AnswerCardProps) => {
  if (isCensored) {
    return (
      <div className="relative bg-slate-200 p-6 rounded-xl">
        <p className="text-slate-400 italic line-through decoration-4">
          [Content removed by VIP]
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-md">
      <p className="text-xl font-bold">{answer.text}</p>
    </div>
  );
};
```

## 5. Chat Moderation

If the game includes a chat feature, apply rate limiting and content filtering from Rocketcrab's proven pattern.

### Rate Limiting Constants

```typescript
const CHAT_LIMITS = {
  MAX_MSG_LENGTH: 100,          // Characters per message
  MAX_MESSAGES_STORED: 20,      // Chat history limit
  MIN_MS_BETWEEN_MSGS: 1000,    // 1 second cooldown
  MAX_MSGS_PER_MINUTE: 10,      // Burst protection
} as const;
```

### Chat Handler

```typescript
const lastMessageTime = new Map<string, number>();
const messageCount = new Map<string, number[]>();

socket.on('chat:message', ({ text }: { text: string }) => {
  const room = roomManager.getRoomBySocket(socket.id);
  if (!room) return;

  // Length check
  if (text.length > CHAT_LIMITS.MAX_MSG_LENGTH) return;
  if (text.trim().length === 0) return;

  // Rate limit
  const now = Date.now();
  const lastTime = lastMessageTime.get(socket.id) ?? 0;
  if (now - lastTime < CHAT_LIMITS.MIN_MS_BETWEEN_MSGS) return;
  lastMessageTime.set(socket.id, now);

  // Burst protection
  const times = messageCount.get(socket.id) ?? [];
  const recentTimes = times.filter(t => now - t < 60_000);
  if (recentTimes.length >= CHAT_LIMITS.MAX_MSGS_PER_MINUTE) return;
  recentTimes.push(now);
  messageCount.set(socket.id, recentTimes);

  // Profanity filter
  const filtered = filter.censor(text);

  const message = {
    playerId: socket.id,
    playerName: room.getPlayerBySocketId(socket.id)?.name ?? 'Unknown',
    text: filtered,
    timestamp: now,
  };

  room.addChatMessage(message);
  io.to(room.code).emit('chat:message', message);
});
```

## 6. Family-Friendly Mode

When enabled, filter both prompts and player content for age-appropriate gameplay.

### Implementation

Add `isFamilyFriendly: boolean` to each prompt in the pack. When the room has `familyFriendly: true`, filter prompts before selection: `pack.filter(p => p.isFamilyFriendly)`. When the VIP enables family mode, automatically upgrade `contentFilter` to `'strict'` — the two settings work together. Family mode is a VIP-only setting, controlled during the lobby phase via `settings:update`.

## 7. Accessibility

Party games must accommodate diverse players. Implement these accessibility features as room-level or player-level settings.

### Accessibility Settings Model

```typescript
interface AccessibilitySettings {
  fontSize: 'default' | 'large' | 'xlarge';
  reduceMotion: boolean;
  highContrast: boolean;
  colorblindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia';
  subtitlesEnabled: boolean;
  screenReaderHints: boolean;
}

const DEFAULT_ACCESSIBILITY: AccessibilitySettings = {
  fontSize: 'default',
  reduceMotion: false,
  highContrast: false,
  colorblindMode: 'none',
  subtitlesEnabled: true,
  screenReaderHints: false,
};
```

### Implementation Patterns

| Feature | Host Screen (TV) | Player Controller (Phone) |
|---------|------------------|---------------------------|
| **Font size** | Already large (32px+) | Apply `text-lg` / `text-xl` / `text-2xl` based on setting |
| **Reduce motion** | Disable Framer Motion animations | Disable transition effects |
| **High contrast** | 7:1 ratio minimum (already recommended) | Swap to high-contrast palette |
| **Colorblind** | Use patterns/shapes alongside color | Same |
| **Subtitles** | Show text for all audio/voice | N/A (phone has no audio) |
| **Screen reader** | ARIA live regions for phase changes | ARIA labels on all controls |

### CSS Variables for Accessibility

```css
:root {
  --font-scale: 1;
  --motion-duration: 300ms;
  --contrast-bg: theme('colors.slate.900');
  --contrast-text: theme('colors.white');
}

[data-font-size="large"] { --font-scale: 1.25; }
[data-font-size="xlarge"] { --font-scale: 1.5; }
[data-reduce-motion="true"] { --motion-duration: 0ms; }
[data-high-contrast="true"] {
  --contrast-bg: #000;
  --contrast-text: #fff;
}
```

### Colorblind-Safe Player Colors

Use shapes alongside colors to distinguish players:

```typescript
const PLAYER_IDENTIFIERS = [
  { color: '#3B82F6', shape: 'circle',   label: 'Blue Circle' },
  { color: '#EF4444', shape: 'square',   label: 'Red Square' },
  { color: '#10B981', shape: 'triangle', label: 'Green Triangle' },
  { color: '#F59E0B', shape: 'diamond',  label: 'Yellow Diamond' },
  { color: '#8B5CF6', shape: 'star',     label: 'Purple Star' },
  { color: '#EC4899', shape: 'hexagon',  label: 'Pink Hexagon' },
  { color: '#06B6D4', shape: 'cross',    label: 'Cyan Cross' },
  { color: '#F97316', shape: 'heart',    label: 'Orange Heart' },
];
```

### ARIA for Phase Changes

```tsx
// Announce game phase changes to screen readers
const PhaseAnnouncer = ({ phase }: { phase: string }) => (
  <div role="status" aria-live="polite" className="sr-only">
    {phase === 'SUBMITTING' && 'Write your answer now. You have 60 seconds.'}
    {phase === 'VOTING' && 'Vote for your favorite answer now.'}
    {phase === 'RESULTS' && 'Round results are being shown.'}
  </div>
);
```

## 8. Mobile UX Hardening

Phone controllers are the primary interface for players. Harden them against common mobile browser issues.

Implement these as React hooks. All degrade gracefully when APIs are unavailable.

| Hook | API | Purpose |
|------|-----|---------|
| `usePreventExit(active)` | `window.onbeforeunload` | Warn before closing tab during game |
| `useLockOrientation('portrait')` | `screen.orientation.lock()` | Force portrait mode on phone |
| `useWakeLock(enabled)` | `navigator.wakeLock.request('screen')` | Prevent screen sleep during rounds |
| `useHaptics()` | `navigator.vibrate()` | Tactile feedback on button press |

### Haptic Feedback Patterns

```typescript
const vibrate = (pattern: 'tap' | 'success' | 'error' | 'countdown') => {
  if (!navigator.vibrate) return;
  const patterns: Record<string, number | number[]> = {
    tap: 30, success: [50, 30, 50], error: [100, 50, 100], countdown: 15,
  };
  navigator.vibrate(patterns[pattern]);
};
```

### Viewport and Touch

Set `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />` to prevent pinch-zoom. All interactive elements must be at least 48x48px (WCAG 2.5.5). For voting options in fast-paced games, use 64px+ button heights.

## 9. Content Reporting

Allow players to report content that bypasses the profanity filter. Store reports with `reporterId`, `contentId`, `contentType`, and `reason` (offensive/spam/harassment/other). Auto-escalation rule: when 2+ unique players report the same content, notify the VIP via `moderation:alert` so they can censor it.

## 10. Input Validation Checklist

Apply these validations to every player input before processing:

| Input Type | Validation | Max Length | Rate Limit |
|------------|-----------|------------|------------|
| Player name | Alphanumeric + spaces, trimmed | 20 chars | 1 per session |
| Answer text | Profanity filter, trimmed | 280 chars | 1 per phase |
| Vote | Valid target ID, not self-vote | N/A | 1 per phase |
| Chat message | Profanity filter, trimmed | 100 chars | 10/min |
| Drawing data | Max stroke count, max points per stroke | 50KB | 1 per phase |
| Room code | Uppercase alpha, exact length | 4-6 chars | 5/min |
| Settings | Zod schema validation | N/A | VIP only |

### Zod Validation Example

```typescript
import { z } from 'zod';

const answerSchema = z.object({
  answer: z.string().trim().min(1).max(280),
});

const voteSchema = z.object({
  targetId: z.string().uuid(),
});

const nameSchema = z.object({
  name: z.string().trim().min(1).max(20).regex(/^[a-zA-Z0-9 ]+$/),
});
```
