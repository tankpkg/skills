# Slack

Send messages, manage channels, search conversations, and automate workflows in Slack.

## Overview

This skill teaches AI agents to interact with Slack workspaces through the Slack Web API. It covers messaging, channel management, user lookups, file uploads, search, and Block Kit for rich message formatting.

## Capabilities

### Messaging
- Send messages to channels, DMs, and group conversations
- Reply in threads to keep conversations organized
- Update and delete existing messages
- Schedule messages for future delivery
- Send ephemeral messages visible only to a specific user
- React to messages with emoji

### Rich Formatting (Block Kit)
- Compose messages with sections, headers, dividers, context blocks
- Add interactive elements: buttons, select menus, date pickers
- Build modal dialogs and home tab views
- Use mrkdwn formatting (bold, italic, code, links, mentions)

### Channel Management
- Create, archive, and unarchive channels
- Set channel topic and purpose
- Invite and remove users from channels
- List channels with pagination and filtering

### Search & Discovery
- Search messages across the workspace
- Search files by name, type, and content
- List users and find users by email

## Authentication

Slack uses OAuth 2.0 Bot Tokens (`xoxb-`) or User Tokens (`xoxp-`). Required scopes depend on actions.

## Permissions

| Permission | Scope | Reason |
|-----------|-------|--------|
| Network | `slack.com` | Slack Web API calls |
| Network | `*.slack.com` | Workspace-specific endpoints |
| Filesystem | Read `./**` | Read local files for upload |
| Subprocess | None | Not required |

## Best Practices

1. **Use Block Kit** for rich, readable messages
2. **Thread replies** to avoid channel noise
3. **Rate limits**: Slack uses tiered rate limiting — implement backoff
4. **Ephemeral messages** for error feedback only the relevant user sees
5. **Cursor-based pagination** — never rely on offset
