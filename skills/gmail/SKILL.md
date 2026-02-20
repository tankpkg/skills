# Gmail

Send, read, search, label, and manage email through the Gmail API.

## Overview

This skill teaches AI agents to work with Gmail programmatically — composing and sending emails, reading and searching messages, managing labels and filters, and handling attachments. It supports both simple send operations and complex thread-aware workflows.

## Capabilities

### Sending Email
- Compose and send plain text or HTML emails
- Add CC, BCC, and reply-to headers
- Attach files from the local filesystem or URLs
- Send replies and forwards within existing threads
- Schedule sends using Gmail's schedule feature
- Create and send from draft

### Reading & Searching
- Fetch messages by ID with full or metadata-only views
- Search using Gmail's powerful query syntax (`from:`, `to:`, `subject:`, `has:attachment`, `after:`, `before:`, `label:`)
- List messages with pagination support
- Fetch full thread conversations
- Parse MIME messages to extract body, attachments, and headers

### Organization
- Create, update, and delete labels
- Apply and remove labels from messages
- Batch modify labels across multiple messages
- Create filters for automatic label application
- Archive, trash, and permanently delete messages
- Mark messages as read/unread or starred/unstarred

### Drafts
- Create drafts for review before sending
- Update existing draft content
- List and delete drafts

## Authentication

Requires Google OAuth 2.0 with one of these scopes:

- `https://www.googleapis.com/auth/gmail.modify` — Read, send, delete, and manage labels
- `https://www.googleapis.com/auth/gmail.readonly` — Read-only access (for search/read workflows)
- `https://www.googleapis.com/auth/gmail.send` — Send-only access

Use the most restrictive scope that fits your use case.

## Example Usage

```json
{
  "action": "sendEmail",
  "to": ["team@example.com"],
  "subject": "Deploy complete",
  "body": "The v2.1 deployment finished successfully. All health checks passing.",
  "format": "plain"
}
```

```json
{
  "action": "searchMessages",
  "query": "from:alerts@monitoring.io after:2026/02/01 has:attachment",
  "maxResults": 10
}
```

## Permissions

| Permission | Scope | Reason |
|-----------|-------|--------|
| Network | `*.googleapis.com` | Gmail API calls |
| Network | `accounts.google.com` | OAuth authentication |
| Filesystem | Read `./**` | Read local files for attachments |
| Subprocess | None | Not required |

## Best Practices

1. **Use threads**: Always include `threadId` when replying to keep conversations organized
2. **Batch operations**: Use batch endpoints when modifying multiple messages
3. **Partial responses**: Request only the fields you need with the `fields` parameter
4. **Respect rate limits**: Gmail API has per-user and per-project quotas — implement backoff
5. **RFC 2822 compliance**: When constructing raw messages, ensure proper MIME formatting
