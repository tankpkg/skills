---
name: "@tank/slack-message-writer"
description: |
  Write concise, polished Slack messages, choose the right Slack formatting mode,
  and automatically copy the finished message to the local clipboard. Covers
  composer markup, API mrkdwn, Markdown blocks, mentions, localized dates,
  accessibility fallbacks, announcements, status updates, incidents, decisions,
  requests, handoffs, and review asks. Synthesizes current official Slack Help
  Center and Slack developer formatting guidance.

  Trigger phrases: "write a Slack message", "draft a Slack message", "Slack copy",
  "copy this to my clipboard", "message the team", "Slack announcement",
  "Slack status update", "Slack incident update", "Slack review request",
  "Slack handoff", "format this for Slack", "Slack mrkdwn", "special Slack message",
  "make this Slack-ready", "send this on Slack", "compose a Slack reply"
---

# Slack Message Writer

Write Slack-native messages that are easy to scan, hard to misunderstand, and
ready to paste. Copy the final artifact to the clipboard unless the user opts out.

## Core Philosophy

1. **Lead with the point.** Put the decision, request, outcome, or incident state
   in the first line. Context follows the headline.
2. **Design for scanning.** Use short paragraphs, meaningful labels, and lists
   only when they reduce reading time.
3. **Match Slack's actual syntax.** Composer markup, API `mrkdwn`, standard
   Markdown blocks, and `rich_text` are different formats. Pick one before writing.
4. **Notify deliberately.** Mention the smallest useful audience. Never introduce
   `@channel`, `@here`, `@everyone`, or a user-group mention without explicit intent.
5. **Deliver, do not merely display.** Show the final message, copy those exact
   bytes to the clipboard, and confirm completion without claiming it was sent.

## Workflow

1. Infer the audience, purpose, desired action, deadline, and tone from context.
2. Ask one concise question only when a missing fact materially changes the message.
3. Select a delivery mode from the table below. Default to **Clipboard composer**.
4. Draft the message with the relevant recipe.
5. Remove throat-clearing, duplicate context, decorative formatting, and vague asks.
6. Check names, links, dates, identifiers, and notification scope. Do not invent any.
7. Display the final message in one fenced `text` block.
8. Pipe the exact unfenced text to `scripts/copy-to-clipboard.sh`.
9. Report `Copied to clipboard.` Do not say `sent` unless a separate Slack tool sent it.

## Delivery Modes

| User intent | Output mode | Formatting |
|---|---|---|
| Write, draft, reply, announce, copy | Clipboard composer | Slack markup: `*bold*`, `_italic_`, `~strike~`, code, quotes, Markdown-style links |
| Build a Web API message using `text` | API `mrkdwn` | Slack `mrkdwn`, `<url|label>`, ID-based mentions, `<!date...>` |
| Preserve an LLM's standard Markdown | API Markdown | `markdown_text` or a `markdown` block, with standard `**bold**` and lists |
| Build a structured app message | API rich layout | Prefer Block Kit `rich_text`; include accessible top-level fallback text |

Do not mix syntaxes. In particular, clipboard output should not contain API-only
forms such as `<@U123>` or `<!date...>` unless the user explicitly requested an
API payload.

## Quick-Start: Common Messages

### "Ask for action or review"

Use: request first, minimum context, owner or audience, deadline, link.

```text
*Review requested: onboarding copy*
Please review the updated onboarding copy by Thursday at 14:00.

Focus on:
- Whether the value proposition is clear
- Any missing objections

[Open the draft](https://example.com)
```

### "Share a status update"

Use: state, completed, next, risk or blocker. Omit empty sections.

```text
*Project Atlas: on track for Friday*
- *Done:* Import flow and validation
- *Next:* Migration rehearsal
- *Risk:* Final legal copy is due Thursday
```

### "Announce a change"

Use: what changed, who is affected, when, required action, source of truth.

```text
*New expense approval flow starts Monday*
Requests over $1,000 will require Finance approval. Existing requests are unchanged.

*Action:* Use the new form for requests created from Monday onward.
[Read the guide](https://example.com)
```

### "Post an incident update"

Use a stable sequence: status, impact, action underway, next update. Use absolute
times with a timezone in clipboard messages; use Slack localized dates for API mode.

```text
*Investigating: delayed report generation*
*Impact:* Reports are completing 20-30 minutes late. No data loss is observed.
*Current action:* We are draining the backed-up worker queue.
*Next update:* 15:30 UTC, or sooner if the status changes.
```

### "Record a decision"

Use: decision, reason, consequence, owner or follow-up.

```text
*Decision: keep the launch behind the existing feature flag*
The rollback path is already proven, and a second flag would add operational risk.

*Follow-up:* Maya will raise the rollout from 10% to 25% after tomorrow's error review.
```

### "Hand off work"

Use: current state, exact next action, known risk, links. Avoid a diary of completed work.

```text
*Handoff: billing migration rehearsal*
The staging migration completed and row counts match.

*Next:* Run the rollback rehearsal with the 2026-09-01 snapshot.
*Watch:* The cleanup step holds a table lock for about 40 seconds.
[Runbook](https://example.com)
```

## Formatting Judgment

| Signal | Use | Avoid |
|---|---|---|
| One key takeaway | Bold first-line headline | Multiple competing headings |
| Three or more parallel facts | Bulleted list | Bullets for a single sentence |
| Commands, IDs, literal values | Inline code or code block | Bold code-like text |
| Quoted source material | Block quote | Quoting your own summary |
| One primary action | A labeled action line | Several unlabeled links |
| Urgent operational change | Explicit impact and next update | Emoji-only urgency |
| Broad notification | Smallest relevant mention | Unrequested mass mentions |

Use at most one or two purposeful emoji when tone benefits. Never use emoji as the
only carrier of status, urgency, approval, or failure.

## Clipboard Delivery

Send only the final message body over standard input:

```bash
bash scripts/copy-to-clipboard.sh <<'SLACK_MESSAGE'
*Final Slack message*
Exact text to copy.
SLACK_MESSAGE
```

The heredoc adds one final newline; display the same message with that newline.
Never copy analysis, alternatives, the surrounding code fence, or the completion note.

## Decision Trees

| Question | If yes | If no |
|---|---|---|
| Did the user request API JSON or Block Kit? | Use API mode and load the reference | Use clipboard composer mode |
| Is there one explicit action? | Put it in the first two lines | Lead with the outcome or state |
| Does a mention notify many people? | Require explicit user intent | Use the narrow mention |
| Is a date viewed across timezones? | Use localized API date syntax in API mode | Include an explicit timezone |
| Is the message longer than one screen? | Cut detail or link to a document | Keep it self-contained |
| Is the content sensitive or surprising? | Preserve neutral wording and ask before adding names | Draft directly |

## Scripts

| Script | Usage |
|---|---|
| `scripts/copy-to-clipboard.sh` | Copy non-empty UTF-8 text from standard input as literal macOS plain text; rejects missing input, invalid UTF-8, and unsupported arguments |

## Reference Index

| File | Contents |
|---|---|
| `references/slack-formatting.md` | Current composer markup, API `mrkdwn`, standard Markdown blocks, rich text, mentions, dates, escaping, parsing controls, accessibility, limits, and mode-specific checks |
