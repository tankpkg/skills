# Tank Manifest Schema (skills.json)

Complete reference for the `skills.json` manifest format used by Tank packages.

## Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | string | See naming rules | Package identifier |
| `version` | string | Semver format | Current version |

## Optional Fields

| Field | Type | Max | Description |
|-------|------|-----|-------------|
| `description` | string | 500 chars | Brief package description |
| `permissions` | object | - | Permission declarations |
| `repository` | string | - | Source repository URL |
| `skills` | object | - | Skill dependencies |
| `audit` | object | - | Audit configuration |

## Name Validation

```
^(@[a-z0-9-]+/)?[a-z0-9][a-z0-9-]*$
```

- Max length: 214 characters
- Lowercase alphanumeric and hyphens only
- Optional scope prefix: `@org/name`
- Cannot start or end with hyphen
- No consecutive hyphens

**Valid examples:**
- `my-skill`
- `@tank/my-skill`
- `code-analysis-v2`

**Invalid examples:**
- `My-Skill` (uppercase)
- `@Tank/my-skill` (uppercase scope)
- `my--skill` (consecutive hyphens)
- `-my-skill` (leading hyphen)

## Version Format

Semver with optional prerelease and build metadata:

```
X.Y.Z[-prerelease][+build]
```

**Valid examples:**
- `1.0.0`
- `2.1.3-beta.1`
- `0.0.1-alpha+build.123`

## Permissions Structure

```json
{
  "permissions": {
    "network": {
      "outbound": ["api.example.com", "*.github.com"]
    },
    "filesystem": {
      "read": ["**/*.json", "src/**"],
      "write": ["output/**", "/tmp/**"]
    },
    "subprocess": true
  }
}
```

### Network Permissions

| Field | Type | Description |
|-------|------|-------------|
| `network.outbound` | string[] | Allowed outbound domains (supports wildcards) |

**Glob patterns supported:**
- `*` matches single domain part
- `**` matches multiple parts
- Exact match for full domain

**Examples:**
- `"api.github.com"` - exact match
- `"*.github.com"` - any subdomain
- `"**"` - all domains (discouraged)

### Filesystem Permissions

| Field | Type | Description |
|-------|------|-------------|
| `filesystem.read` | string[] | Glob patterns for readable paths |
| `filesystem.write` | string[] | Glob patterns for writable paths |

**Glob patterns:**
- `**` matches any directory depth
- `*` matches any single path segment
- Relative paths from skill directory

**Examples:**
- `["**/*.json"]` - all JSON files
- `["src/**"]` - all files under src/
- `["/tmp/**"]` - system temp directory

### Subprocess Permission

| Field | Type | Default |
|-------|------|---------|
| `subprocess` | boolean | `false` |

When `true`, allows the skill to spawn child processes.

## Skills Dependencies

Declare dependencies on other Tank skills:

```json
{
  "skills": {
    "@tank/playwright": "^1.0.0",
    "@tank/python": ">=2.0.0"
  }
}
```

## Complete Example

```json
{
  "name": "@tank/data-processor",
  "version": "1.2.0",
  "description": "Process and transform data files with validation and output formatting.",
  "permissions": {
    "network": {
      "outbound": ["api.tankpkg.dev"]
    },
    "filesystem": {
      "read": ["**/*.json", "**/*.csv", "**/*.yaml"],
      "write": ["output/**", "reports/**"]
    },
    "subprocess": false
  },
  "skills": {
    "@tank/python": "^3.0.0"
  },
  "repository": "https://github.com/tankpkg/skills"
}
```

## Schema Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid name format` | Name doesn't match regex | Use lowercase, hyphens, optional @scope/ |
| `Name too long` | > 214 characters | Shorten the name |
| `Invalid version` | Not semver | Use X.Y.Z format |
| `Missing required field` | No `name` or `version` | Add required fields |
| `Invalid permissions` | Wrong structure | Use nested network/filesystem/subprocess |
