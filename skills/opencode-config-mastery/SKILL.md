---
name: "@tank/opencode-config-mastery"
description: |
  Expert OpenCode configuration for any project. Covers opencode.json schema,
  MCP server setup (local STDIO, remote HTTP, OAuth), provider and model
  configuration (75+ providers, custom/local models), plugin management
  (oh-my-opencode, morph, wakatime), agent wiring in config, custom slash
  commands, rules/instructions files, keybinds, permission system, and
  security best practices for MCP servers. Includes trusted MCP server
  catalog and context budget management strategies. Synthesizes OpenCode
  source (sst/opencode), official docs, MCP specification, OWASP MCP
  security guidelines, and community ecosystem analysis.

  Trigger phrases: "opencode.json", "opencode config", "configure opencode",
  "MCP server", "mcp setup", "add mcp", "mcp config", "mcp oauth",
  "opencode provider", "add provider", "custom provider", "local model",
  "ollama opencode", "LM Studio", "opencode plugin", "oh-my-opencode",
  "opencode permission", "permission config", "bash permission",
  "slash command", "custom command", "opencode command", ".opencode",
  "instructions file", "rules file", "AGENTS.md", ".cursorrules",
  "opencode keybind", "keybinds", "context budget", "too many tools",
  "MCP security", "tool poisoning", "opencode setup", "configure model",
  "small_model", "enabled_providers", "disabled_providers", "opencode agent config",
  "watcher ignore", "opencode share", "opencode theme", "opencode lsp",
  "opencode formatter", "variable substitution", "{env:}", "{file:}",
  "/connect", "auth.json", "mcp-auth.json"
---

# OpenCode Configuration Mastery

## Core Principles

1. **Start minimal, add complexity** — A valid config is just `{ "$schema":
   "https://opencode.ai/config.json", "model": "anthropic/claude-sonnet-4-5" }`.
   Add more only when you need it.
2. **Configs deep-merge** — Global + project configs combine. Arrays concatenate.
   Objects merge with project-level winning conflicts.
3. **OpenCode MCP ≠ Claude Desktop MCP** — Different format. Root key `"mcp"`,
   command as array, `"environment"` not `"env"`, explicit `"type"` required.
4. **Context budget is finite** — Every MCP tool costs tokens. 50+ tools ≈ 67k
   tokens. Scope tools per-agent, use lazy loading, disable unused servers.

## Quick-Start Recipes

### "Set up OpenCode from scratch"

1. Create `opencode.json` in project root:
   ```jsonc
   { "$schema": "https://opencode.ai/config.json" }
   ```
2. Run `opencode` → use `/connect` to authenticate a provider
3. Pick your model: set `"model": "provider/model-id"`
   → See `references/providers-and-models.md` for all providers

### "Add an MCP server"

**Local** (subprocess): `"mcp": { "name": { "type": "local", "command": ["npx", "-y", "@pkg/name"] } }`

**Remote** (HTTP): `"mcp": { "name": { "type": "remote", "url": "https://mcp.example.com/mcp" } }`

→ See `references/mcp-servers.md` for OAuth, tool management, all options
→ See `references/plugins-and-ecosystem.md` for trusted server catalog

### "Add a custom/local model (Ollama, LM Studio)"

```jsonc
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": { "llama2": { "name": "Llama 2" } }
    }
  },
  "model": "ollama/llama2"
}
```
→ See `references/providers-and-models.md` for all local setups

### "Add a plugin"

```jsonc
{
  "plugin": ["oh-my-opencode", "opencode-morph-fast-apply"]
}
```
→ See `references/plugins-and-ecosystem.md` for trusted plugin list

### "Create a custom slash command"

Create `.opencode/commands/my-command.md`:
```markdown
---
description: What this command does
input: optional
---
Instructions for the agent. User input available as $INPUT.
```
→ See `references/agents-commands-rules.md` for full format

### "Lock down permissions"

```jsonc
{
  "permission": {
    "edit": "ask",
    "bash": { "*": "ask", "rm *": "deny", "git push *": "deny" },
    "webfetch": "deny"
  }
}
```
→ See `references/agents-commands-rules.md` for permission patterns

### "Reduce context usage from MCP tools"

1. Disable tools globally, enable per-agent:
   ```jsonc
   {
     "tools": { "github_*": false },
     "agent": { "pr-reviewer": { "tools": { "github_*": true } } }
   }
   ```
2. Install lazy loader: `"plugin": ["opencode-mcp-tool-search"]`
3. Disable unused servers: `"mcp": { "unused": { "enabled": false } }`

## Decision Trees

### What to Configure

| Need | Config Key | Reference |
|------|-----------|-----------|
| Pick a model | `model`, `small_model` | providers-and-models.md |
| Add LLM provider | `provider` | providers-and-models.md |
| Connect external tool | `mcp` | mcp-servers.md |
| Install plugin | `plugin` | plugins-and-ecosystem.md |
| Control what agents can do | `permission` | agents-commands-rules.md |
| Add reusable commands | `.opencode/commands/` | agents-commands-rules.md |
| Set project conventions | `instructions` | agents-commands-rules.md |
| Override agent model/behavior | `agent` | agents-commands-rules.md |
| Customize keybinds | `keybinds` | agents-commands-rules.md |

### MCP: Local vs Remote

| Signal | Use Local | Use Remote |
|--------|-----------|------------|
| npx/uvx package available | ✓ | |
| Vendor provides hosted endpoint | | ✓ |
| Need OAuth authentication | | ✓ |
| Air-gapped environment | ✓ | |
| Docker-based server | ✓ | |
| Want zero local install | | ✓ |

### Provider Selection

| Need | Provider | Auth |
|------|----------|------|
| Best coding quality | Anthropic | `/connect` or API key |
| Budget-conscious | OpenCode Zen | `/connect` |
| Enterprise/compliance | Azure OpenAI, Bedrock | IAM + config |
| Offline/air-gapped | Ollama, llama.cpp | Local, no auth |
| Multi-model access | OpenRouter | API key |
| Existing subscription | GitHub Copilot | `/connect` |

### Security Checklist (Before Adding MCP Server)

☐ Known vendor or significant GitHub stars · ☐ Filesystem scoped to
specific dirs · ☐ API keys use `{env:VAR}` · ☐ Unused servers disabled ·
☐ Versions pinned (no `@latest`) · ☐ Permissions restrict dangerous tools
→ See `references/plugins-and-ecosystem.md` for OWASP MCP Top 10

## Anti-Patterns

| Pattern | Fix |
|---------|-----|
| `"mcpServers"` root key | Use `"mcp"` (OpenCode format) |
| `"command": "npx"` + `"args"` | Use `"command": ["npx", ...]` array |
| `"env": {}` for MCP | Use `"environment": {}` |
| Missing `"type"` on MCP | Add `"type": "local"` or `"remote"` |
| API keys in config | Use `"{env:VAR_NAME}"` substitution |
| 50+ MCP tools globally | Per-agent scoping or lazy loading |
| `@latest` in MCP commands | Pin specific versions |

## Reference Files

| File | Contents |
|------|----------|
| `references/config-schema.md` | Full opencode.json schema, all top-level keys, file locations, precedence, merging, variable substitution, LSP/formatter config |
| `references/mcp-servers.md` | Local/remote MCP setup, OAuth, tool naming, per-agent scoping, CLI commands, quick-start examples for popular servers |
| `references/providers-and-models.md` | Provider setup, credentials, all major providers, custom/local providers (Ollama, LM Studio, llama.cpp), model selection |
| `references/plugins-and-ecosystem.md` | OpenCode plugins (oh-my-opencode, morph, etc.), MCP registries, community servers by category, OWASP security, context budget |
| `references/agents-commands-rules.md` | Agent config in JSON, custom commands, rules/instructions, keybinds, permission system, common profiles |
