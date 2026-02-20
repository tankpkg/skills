# Notion

Query, create, and update Notion pages, databases, and blocks through the Notion API.

## Overview

This skill teaches AI agents to interact with Notion workspaces — creating and querying databases, building pages with rich content blocks, managing properties, and automating workspace organization. Supports both internal integrations and OAuth-based public integrations.

## Capabilities

### Database Operations
- Create databases with typed properties (title, text, number, select, multi-select, date, person, files, checkbox, URL, email, phone, formula, relation, rollup, status)
- Query databases with filters and sorts
- Compound filters with `and`/`or` logic
- Paginate through large result sets
- Update database properties and schema

### Page Operations
- Create pages within databases or as standalone pages
- Update page properties (all property types supported)
- Archive and restore pages
- Retrieve page content as block trees
- Set page icons (emoji or external URL) and cover images

### Block Operations
- Append child blocks to pages or other blocks
- Supported block types: paragraph, headings (1-3), bulleted list, numbered list, to-do, toggle, code, quote, callout, divider, table of contents, bookmark, image, embed, file, PDF, table, column list
- Update existing block content
- Delete blocks
- Retrieve block children with pagination

### Search & Discovery
- Search across entire workspace by title
- Filter search by object type (page or database)
- Sort by relevance or last edited time

## Authentication

Notion uses bearer token authentication:

- **Internal integrations**: Use the integration token directly
- **Public integrations**: Use OAuth 2.0 flow to obtain access tokens

Set the `Authorization: Bearer <token>` header and `Notion-Version: 2022-06-28` header on all requests.

## Example Usage

```json
{
  "action": "queryDatabase",
  "databaseId": "abc123",
  "filter": {
    "property": "Status",
    "status": { "equals": "In Progress" }
  },
  "sorts": [
    { "property": "Priority", "direction": "ascending" }
  ]
}
```

```json
{
  "action": "createPage",
  "parentDatabaseId": "abc123",
  "properties": {
    "Name": "Implement auth flow",
    "Status": "To Do",
    "Priority": "High",
    "Assignee": "alice@example.com"
  },
  "content": [
    { "type": "heading_2", "text": "Requirements" },
    { "type": "bulleted_list_item", "text": "Support OAuth 2.0" },
    { "type": "bulleted_list_item", "text": "Add rate limiting" }
  ]
}
```

## Permissions

| Permission | Scope | Reason |
|-----------|-------|--------|
| Network | `api.notion.com` | Notion API calls |
| Filesystem | Read `./**` | Read local files for page content |
| Subprocess | None | Not required |

## Best Practices

1. **Paginate everything**: All list endpoints return max 100 results — always check `has_more` and use `start_cursor`
2. **Respect rate limits**: Notion enforces ~3 requests/second per integration — use backoff on 429
3. **Use the block tree**: Pages are trees of blocks, not flat documents — build content hierarchically
4. **Property type matching**: When setting property values, match the exact type schema (e.g., `rich_text` not plain string)
5. **Notion-Version header**: Always include it — API behavior changes between versions
6. **Batch appends**: Append up to 100 child blocks in a single request instead of one at a time
