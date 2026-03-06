# OpenCode Configuration Schema

Sources: OpenCode source (sst/opencode config.ts commit 715b844), official docs
(opencode.ai/docs/config, open-code.ai/docs/en/config), JSON schema at
opencode.ai/config.json

Covers: full opencode.json structure, all top-level keys, config file locations,
precedence, merging behavior, variable substitution, environment variables.

## Config File Format

OpenCode uses JSON or JSONC (JSON with Comments). Always start with:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  // Your config here
}
```

The `$schema` enables editor autocomplete and validation. If missing, OpenCode
auto-injects it on first run.

## File Locations (Precedence: lowest → highest)

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (lowest) | `.well-known/opencode` endpoint | Remote org defaults |
| 2 | `~/.config/opencode/opencode.json` | Global user prefs |
| 3 | `OPENCODE_CONFIG` env var path | Custom override |
| 4 | `opencode.json` in project root | Project-specific |
| 5 | `.opencode/` directory contents | Agents, commands, plugins |
| 6 | `OPENCODE_CONFIG_CONTENT` env var | Inline runtime JSON |
| 7 (highest) | Enterprise managed dir | `/Library/Application Support/opencode` (macOS), `/etc/opencode` (Linux) |

**Merging rules**: Configs are deep-merged, not replaced. Arrays (`plugin`,
`instructions`) are concatenated. Object keys from higher-priority configs
override lower ones. Non-conflicting settings from all layers are preserved.

**Custom config directory**: Set `OPENCODE_CONFIG_DIR` to load agents, commands,
modes, and plugins from a custom path (same structure as `.opencode/`).

**Directory naming**: `.opencode/` and `~/.config/opencode/` use **plural** subdirectory
names: `agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, `themes/`.
Singular names (`agent/`) also work for backwards compatibility.

## Full Top-Level Schema

```typescript
interface OpenCodeConfig {
  $schema?: string                    // "https://opencode.ai/config.json"
  logLevel?: "debug" | "info" | "warn" | "error"

  // === Model Selection ===
  model?: string                      // "provider/model-id" — primary model
  small_model?: string                // For lightweight tasks (title gen, etc.)
  default_agent?: string              // Default primary agent (fallback: "build")
  username?: string                   // Override system username in conversations

  // === Providers ===
  provider?: Record<string, ProviderConfig>
  disabled_providers?: string[]       // Block auto-loaded providers
  enabled_providers?: string[]        // Whitelist — ONLY these providers load
  // Note: disabled_providers takes priority over enabled_providers

  // === MCP Servers ===
  mcp?: Record<string, McpConfig>     // See references/mcp-servers.md

  // === Agents ===
  agent?: Record<string, AgentConfig> // See references/agents-commands-rules.md

  // === Commands ===
  command?: Record<string, CommandConfig>

  // === Skills ===
  skills?: {
    paths?: string[]                  // Additional skill folder paths
    urls?: string[]                   // Remote skill URLs
  }

  // === Plugins ===
  plugin?: string[]                   // npm package names or file:// URLs

  // === Permissions ===
  permission?: PermissionConfig       // See references/agents-commands-rules.md

  // === LSP Servers ===
  lsp?: false | Record<string, LspConfig>  // false = disable all

  // === Formatters ===
  formatter?: false | Record<string, FormatterConfig>  // false = disable all

  // === Instructions / Rules ===
  instructions?: string[]             // Glob patterns or file paths

  // === Sharing ===
  share?: "manual" | "auto" | "disabled"

  // === Auto-update ===
  autoupdate?: boolean | "notify"

  // === TUI ===
  tui?: {
    scroll_speed?: number             // Default: 3, min: 1
    scroll_acceleration?: { enabled: boolean }  // macOS-style, overrides scroll_speed
    diff_style?: "auto" | "stacked"
  }

  // === Server (opencode serve) ===
  server?: {
    port?: number
    hostname?: string
    mdns?: boolean                    // mDNS service discovery
    mdnsDomain?: string               // Default: "opencode.local"
    cors?: string[]                   // Additional CORS origins
  }

  // === Context Management ===
  compaction?: {
    auto?: boolean                    // Default: true
    prune?: boolean                   // Default: true — remove old tool outputs
    reserved?: number                 // Token buffer
  }

  // === File Watcher ===
  watcher?: { ignore?: string[] }     // Glob patterns to exclude

  // === Keybinds ===
  keybinds?: Record<string, string>   // See references/agents-commands-rules.md

  // === Theme ===
  theme?: string

  // === Experimental ===
  experimental?: {
    disable_paste_summary?: boolean
    batch_tool?: boolean
    openTelemetry?: boolean
    primary_tools?: string[]          // Tools only for primary agents
    continue_loop_on_deny?: boolean
    mcp_timeout?: number              // Global MCP timeout (ms)
  }

  // === Deprecated ===
  tools?: Record<string, boolean>     // Use permission instead
  mode?: Record<string, AgentConfig>  // Use agent instead
  layout?: "auto" | "stretch"
}
```

## Variable Substitution

Use variables anywhere in config values:

| Syntax | Source | Example |
|--------|--------|---------|
| `{env:VAR_NAME}` | Environment variable | `"{env:ANTHROPIC_API_KEY}"` |
| `{file:path}` | File contents | `"{file:~/.secrets/openai-key}"` |

File paths can be relative to config file directory, or absolute (`/`, `~`).
If env var is unset, substitutes empty string.

```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  },
  "mcp": {
    "my-server": {
      "type": "remote",
      "headers": { "Authorization": "Bearer {env:MY_API_KEY}" }
    }
  }
}
```

## LSP Server Configuration

```typescript
// false = disable all LSP
lsp?: false | Record<string, {
  command: string[]                   // e.g. ["typescript-language-server", "--stdio"]
  extensions?: string[]               // e.g. [".ts", ".tsx"]
  disabled?: boolean
  env?: Record<string, string>
  initialization?: Record<string, any>  // LSP initializationOptions
} | { disabled: true }>
```

## Formatter Configuration

```typescript
// false = disable all formatters
formatter?: false | Record<string, {
  disabled?: boolean
  command?: string[]                  // e.g. ["npx", "prettier", "--write", "$FILE"]
  environment?: Record<string, string>
  extensions?: string[]               // e.g. [".js", ".ts", ".jsx", ".tsx"]
}>
```

Built-in formatters (like `prettier`) can be disabled via `{ "prettier": { "disabled": true } }`.

## Common Configuration Recipes

### Minimal: just pick a model
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5"
}
```

### Lock to specific providers
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "enabled_providers": ["anthropic", "openai"],
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

### Restrict permissions (ask before editing/running)
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "deny"
  }
}
```

### Team config via remote
Organizations serve config at `.well-known/opencode`. Users override locally.

### Disable auto-update and auto-share
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "autoupdate": false,
  "share": "disabled"
}
```

## Key Data Locations

| Data | Path |
|------|------|
| Global config | `~/.config/opencode/opencode.json` |
| Auth credentials | `~/.local/share/opencode/auth.json` |
| MCP OAuth tokens | `~/.local/share/opencode/mcp-auth.json` |
| Session database | `~/.local/share/opencode/opencode.db` |
| Model cache | `~/.cache/opencode/models.json` (from models.dev) |
| Agents (global) | `~/.config/opencode/agents/*.md` |
| Skills (global) | `~/.config/opencode/skills/*/SKILL.md` |
| Plugins (global) | `~/.config/opencode/plugins/` |
| Commands (global) | `~/.config/opencode/commands/*.md` |
