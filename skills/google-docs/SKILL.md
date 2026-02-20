# Google Docs

Create, edit, format, and collaborate on Google Docs programmatically.

## Overview

This skill teaches AI agents how to interact with Google Docs through the Google Docs API and Google Drive API. It covers document creation, content manipulation, formatting, real-time collaboration, and export workflows.

## Capabilities

### Document Lifecycle
- Create new documents with titles and initial content
- Clone existing documents as templates
- Move documents between Drive folders
- Export documents to PDF, DOCX, plain text, or HTML
- Archive and delete documents

### Content Manipulation
- Insert, replace, and delete text at specific locations
- Work with headers, footers, and footnotes
- Manage numbered and bulleted lists
- Insert and position inline images
- Create and modify tables (rows, columns, cell content)

### Formatting
- Apply paragraph styles (headings, normal text, title)
- Set character formatting (bold, italic, underline, font, size, color)
- Configure page setup (margins, orientation, page size)
- Apply named styles and custom style presets

### Collaboration
- Share documents with specific users or domains
- Set permission levels (viewer, commenter, editor)
- Read and resolve comments and suggestions
- Track revision history and restore previous versions

## Authentication

This skill requires Google OAuth 2.0 credentials with the following scopes:

- `https://www.googleapis.com/auth/documents` — Full access to Google Docs
- `https://www.googleapis.com/auth/drive.file` — Access to files created by the app

Store credentials securely and never embed them in skill files. Use environment variables or a credential manager.

## Example Usage

```json
{
  "action": "createDocument",
  "title": "Weekly Status Report",
  "content": "## Status Update\n\nProject is on track...",
  "folderId": "1a2b3c4d5e"
}
```

## Permissions

| Permission | Scope | Reason |
|-----------|-------|--------|
| Network | `*.googleapis.com` | Google Docs and Drive API calls |
| Network | `accounts.google.com` | OAuth authentication |
| Filesystem | Read `./**` | Read local files for upload |
| Subprocess | None | Not required |

## Best Practices

1. **Batch updates**: Use `batchUpdate` to combine multiple operations into a single API call
2. **Use document indexes**: The Docs API uses character indexes — always calculate positions carefully
3. **Handle rate limits**: Implement exponential backoff for 429 responses
4. **Template pattern**: Clone a template document instead of building from scratch for consistent formatting
