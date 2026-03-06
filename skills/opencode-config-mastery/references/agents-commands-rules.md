# Agents, Commands, Rules & Permissions

Sources: OpenCode source (config.ts, agent.ts, command.ts), official docs
(opencode.ai/docs/agents, opencode.ai/docs/custom-commands)

Covers: agent configuration in opencode.json (brief — see opencode-agent-creator
skill for full agent authoring), custom slash commands, rules/instructions files,
keybind customization, and the global permission system.

NOTE: This reference covers the **configuration** side of agents (how to wire
them in opencode.json). For agent **creation** — role design, prompt engineering,
descriptions, oh-my-opencode integration — see the `opencode-agent-creator` skill.

## Agent Configuration in opencode.json

### JSON Format (centralized config)

```jsonc
{
  "agent": {
    "my-agent": {
      "description": "Use when the user needs help with X",
      "mode": "subagent",          // "primary" | "subagent" | "all"
      "model": "anthropic/claude-sonnet-4-6",
      "temperature": 0.1,
      "prompt": "You are a specialist in...",
      "color": "#38A3EE",
      "permission": {
        "edit": "allow",
        "bash": { "*": "ask", "git diff *": "allow" }
      }
    }
  }
}
```

### Markdown Format (file-based)

Place `.md` files in:
- `~/.config/opencode/agents/*.md` — global (all projects)
- `.opencode/agents/*.md` — project-specific

Filename (without `.md`) becomes the agent name. YAML frontmatter = config,
body = system prompt. See `opencode-agent-creator` skill for full format.

### Override Built-in Agents

Override any built-in agent (build, plan, general, explore) by defining
an agent with the same name:

```jsonc
{
  "agent": {
    "build": {
      "model": "anthropic/claude-opus-4-6",
      "temperature": 0.2
    }
  }
}
```

Only provided fields are overridden; others keep their defaults.

### Disable Agents

```jsonc
{
  "agent": {
    "unwanted-agent": { "disable": true }
  }
}
```

Works for built-in agents, plugin agents, and file-based agents.

### Set Default Agent

```jsonc
{
  "default_agent": "my-custom-agent"
}
```

This agent loads on startup instead of the default "build" agent.

## Custom Slash Commands

Commands are Markdown files that define reusable slash commands accessible
via `/command-name` in the TUI.

### File Locations

| Scope | Path |
|-------|------|
| Global | `~/.config/opencode/commands/*.md` |
| Project | `.opencode/commands/*.md` |

### Command Format

```markdown
---
description: Run the full test suite and report results
input: optional     # "required" | "optional" | "none"
---

Run the test suite for this project.

$INPUT

If tests fail, analyze the failures and suggest fixes.
Report results in a table format.
```

**Filename** = command name: `test-suite.md` → `/test-suite`

### Command Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `description` | string | — | Shown in `/` autocomplete |
| `input` | enum | `"optional"` | `"required"` = user must type after `/cmd`, `"optional"` = text after `/cmd` is available as `$INPUT`, `"none"` = no input accepted |

### The $INPUT Variable

When `input` is `"required"` or `"optional"`, the text typed after the
command name is substituted into `$INPUT`:

```
/test-suite auth module    →  $INPUT = "auth module"
/test-suite                →  $INPUT = "" (if optional)
```

### Command Examples

#### Quick commit
`.opencode/commands/commit.md`:
```markdown
---
description: Create a conventional commit with staged changes
input: optional
---
Look at the staged changes (git diff --cached) and create a commit.
If input is provided, use it as context: $INPUT
Follow conventional commit format (feat:, fix:, chore:, etc.).
```

#### Code review
`.opencode/commands/review.md`:
```markdown
---
description: Review current changes for bugs and best practices
input: none
---
Review all uncommitted changes in this repository.
Focus on: bugs, security issues, performance problems, and code style.
Present findings as a prioritized list.
```

#### Explain file
`.opencode/commands/explain.md`:
```markdown
---
description: Explain a file or code section
input: required
---
Read and explain: $INPUT
Provide a clear, concise explanation suitable for a new team member.
```

### Commands in opencode.json

Commands can also be defined in config (less common):

```jsonc
{
  "command": {
    "deploy": {
      "description": "Deploy to staging",
      "input": "none",
      "prompt": "Run the deployment pipeline..."
    }
  }
}
```

## Rules & Instructions

Rules are system-level instructions that apply across all agents. They're
like `.cursorrules` or `.github/copilot-instructions.md`.

### File-Based Rules

Place instruction files in the project. Reference them via glob patterns:

```jsonc
{
  "instructions": [
    ".opencode/rules/*.md",
    "CONVENTIONS.md",
    ".cursorrules"
  ]
}
```

OpenCode also auto-loads from these paths (no config needed):
- `.opencode/rules/*.md`
- `.opencode/instructions/*.md`
- `AGENTS.md` (project root)

### Inline Rules (in config)

Instructions can also be string arrays that are concatenated:

```jsonc
{
  "instructions": [
    "Always use TypeScript strict mode",
    "Prefer functional programming patterns",
    ".opencode/rules/*.md"
  ]
}
```

Strings that look like file paths/globs are loaded as files. Plain strings
are used as-is.

### Rule File Structure

Rule files are plain Markdown. They're injected into the system prompt
of every agent.

```markdown
# Project Conventions

## Code Style
- Use functional components with hooks (no class components)
- Prefer named exports over default exports
- Use `const` by default, `let` only when reassignment is needed

## Architecture
- Follow the repository pattern for data access
- Keep business logic in service files, not route handlers
- All API responses must include `{ success, data, error }` shape

## Testing
- Write tests alongside source files (*.test.ts)
- Minimum 80% coverage for new code
- Use descriptive test names: "should [expected behavior] when [condition]"
```

### Instruction Precedence

Instructions from all config layers are **concatenated** (not replaced):
1. Remote org instructions (`.well-known/opencode`)
2. Global instructions (`~/.config/opencode/`)
3. Project instructions (`opencode.json`, `.opencode/`)

All layers contribute — nothing is overridden.

## Keybind Customization

```jsonc
{
  "keybinds": {
    "leader": "ctrl+a",
    "agent:switch": "ctrl+t",
    "input:submit": "enter",
    "input:newline": "shift+enter",
    "session:new": "ctrl+n",
    "session:list": "ctrl+l",
    "messages:interrupt": "escape",
    "editor:open": "ctrl+e",
    "help:toggle": "?"
  }
}
```

### Available Keybind Actions

| Action | Default | Description |
|--------|---------|-------------|
| `leader` | `ctrl+a` | Leader key prefix for two-key combos |
| `agent:switch` | `ctrl+t` | Cycle through primary agents |
| `input:submit` | `enter` | Send message |
| `input:newline` | `shift+enter` | Insert line break |
| `input:paste` | `ctrl+v` | Paste from clipboard |
| `session:new` | `ctrl+n` | Start new session |
| `session:list` | `ctrl+l` | Show session picker |
| `session:share` | `ctrl+s` | Share current session |
| `messages:interrupt` | `escape` | Cancel current generation |
| `messages:clear` | — | Clear messages |
| `editor:open` | `ctrl+e` | Open $EDITOR for long input |
| `help:toggle` | `?` | Toggle help panel |

## Permission System (Global)

Permissions control what agents can do. Set globally in config, per-agent
in agent config, or both (agent-level overrides global).

### Global Permissions

```jsonc
{
  "permission": {
    "edit": "allow",           // File editing
    "bash": "ask",             // Shell commands
    "webfetch": "allow",       // HTTP requests
    "mcp": "ask",              // MCP tool calls
    "task": "allow"            // Agent delegation
  }
}
```

### Permission Values

| Value | Behavior |
|-------|----------|
| `"allow"` | Execute without user confirmation |
| `"ask"` | Prompt user before each execution |
| `"deny"` | Block entirely — agent cannot use this tool |

### Bash Sub-Permissions (Pattern Matching)

```jsonc
{
  "permission": {
    "bash": {
      "*": "ask",              // Default: ask for everything
      "git status *": "allow", // Allow git status
      "git diff *": "allow",   // Allow git diff
      "git push *": "deny",    // Never push
      "npm test *": "allow",   // Allow running tests
      "rm -rf *": "deny"       // Never recursive delete
    }
  }
}
```

Pattern matching uses glob-style `*` wildcards. First matching pattern wins.

### Task Sub-Permissions (Agent Delegation)

```jsonc
{
  "permission": {
    "task": {
      "*": "allow",            // Default: can delegate to anyone
      "oracle": "ask",         // Ask before consulting oracle (expensive)
      "dangerous-agent": "deny" // Never delegate to this agent
    }
  }
}
```

### MCP Tool Permissions

MCP tools follow the naming pattern `{server}_{tool}`:

```jsonc
{
  "permission": {
    "mcp_github_create_issue": "ask",
    "mcp_filesystem_*": "allow",
    "mcp_dangerous_server_*": "deny"
  }
}
```

### Permission Precedence

1. Agent-level permissions (highest priority)
2. Global permissions in project config
3. Global permissions in user config
4. Built-in defaults (`edit: allow`, `bash: ask`, etc.)

Agent permissions **override** global for that agent only.

### Common Permission Profiles

#### Locked-down (enterprise/compliance)
```jsonc
{
  "permission": {
    "edit": "ask",
    "bash": { "*": "ask", "rm *": "deny", "git push *": "deny" },
    "webfetch": "deny",
    "mcp": "ask"
  }
}
```

#### Developer-friendly (personal use)
```jsonc
{
  "permission": {
    "edit": "allow",
    "bash": { "*": "allow", "rm -rf *": "deny", "git push *": "ask" },
    "webfetch": "allow",
    "mcp": "allow"
  }
}
```

#### Read-only (review/audit)
```jsonc
{
  "permission": {
    "edit": "deny",
    "bash": { "*": "deny", "git log *": "allow", "git diff *": "allow" },
    "webfetch": "deny"
  }
}
```

## Other Config Keys

**Share**: `"share": "manual" | "auto" | "disabled"` — controls session sharing.

**Theme**: `"theme": "opencode"` — built-in or custom from
`~/.config/opencode/themes/` or `.opencode/themes/`.

**Watcher**: `"watcher": { "ignore": ["pattern/**"] }` — glob patterns added
to default ignores (node_modules, .git, etc. already excluded).
