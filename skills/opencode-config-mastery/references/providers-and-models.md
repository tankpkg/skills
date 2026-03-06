# Provider & Model Configuration

Sources: OpenCode source (config.ts), official docs (opencode.ai/docs/providers),
models.dev API

Covers: provider setup, credentials, model selection, custom providers, local
models, base URL proxies, provider-specific options, model overrides.

## How Providers Work

OpenCode uses the AI SDK and Models.dev to support 75+ LLM providers. The full
model list is fetched from `https://models.dev/api.json` and cached at
`~/.cache/opencode/models.json`.

Model IDs always follow the format: `provider/model-id`
- `anthropic/claude-sonnet-4-5`
- `openai/gpt-4o`
- `google/gemini-2.5-pro`

## Credentials

### Using /connect (recommended)
Run `/connect` in the TUI, select a provider, and follow the flow. Credentials
are stored in `~/.local/share/opencode/auth.json`.

### Using environment variables
Set provider-specific env vars before running opencode:
```bash
ANTHROPIC_API_KEY=sk-ant-... opencode
OPENAI_API_KEY=sk-... opencode
```

### Using config (for special cases)
```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

## Provider Configuration Schema

```typescript
interface ProviderConfig {
  name?: string                       // Display name in UI
  api?: string                        // API identifier
  env?: string[]                      // Env var names for API key
  npm?: string                        // AI SDK package (e.g. "@ai-sdk/openai-compatible")

  // Model filtering
  whitelist?: string[]                // Only show these model IDs
  blacklist?: string[]                // Hide these model IDs

  // Per-model overrides
  models?: Record<string, {
    id?: string                       // Override model ID (e.g. ARN for Bedrock)
    name?: string                     // Display name
    limit?: {
      context: number
      output: number
      input?: number
    }
    cost?: {
      input: number
      output: number
      cache_read?: number
      cache_write?: number
    }
    variants?: Record<string, {
      disabled?: boolean
      [key: string]: any
    }>
  }>

  // SDK options
  options?: {
    apiKey?: string
    baseURL?: string                  // Custom endpoint / proxy
    timeout?: number | false          // ms, default: 300000. false = none
    setCacheKey?: boolean             // Enable prompt cache key
    headers?: Record<string, string>  // Custom HTTP headers
    [key: string]: any                // Provider-specific options
  }
}
```

## Major Providers Quick Reference

### Anthropic (Claude)
```jsonc
// Via /connect — Claude Pro/Max subscription or API key
// Or manually:
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### OpenAI (GPT)
```jsonc
// Via /connect — ChatGPT Plus/Pro subscription or API key
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```

### GitHub Copilot
Run `/connect` → select GitHub Copilot → authorize via device flow.
Some models may need Pro+ subscription.

### Google Vertex AI
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_LOCATION=global
```

### Amazon Bedrock
```jsonc
{
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile"
      }
    }
  }
}
```
Auth chain: Bearer token > AWS credential chain (profile, access keys, IAM roles).

### Azure OpenAI
```bash
export AZURE_RESOURCE_NAME=my-resource
```
Deployment name must match model name.

### GitLab Duo
```jsonc
{
  "provider": {
    "gitlab": {
      "options": {
        "instanceUrl": "https://gitlab.com",
        "featureFlags": {
          "duo_agent_platform_agentic_chat": true
        }
      }
    }
  }
}
```
For self-hosted: set `GITLAB_INSTANCE_URL`, `GITLAB_TOKEN`, optional `GITLAB_AI_GATEWAY_URL`.

### OpenCode Zen (curated models)
The OpenCode team's verified model list. Run `/connect` → select OpenCode Zen.
Good starting point for new users.

### OpenRouter
Aggregator providing access to many models via one API key.

### DeepSeek
Run `/connect` → search for DeepSeek → enter API key.

## Custom / Local Providers

Use `@ai-sdk/openai-compatible` for any OpenAI-compatible API:

### Ollama (local)
```jsonc
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": {
        "llama2": { "name": "Llama 2" }
      }
    }
  }
}
```

### LM Studio (local)
```jsonc
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": { "baseURL": "http://127.0.0.1:1234/v1" },
      "models": {
        "google/gemma-3n-e4b": { "name": "Gemma 3n (local)" }
      }
    }
  }
}
```

### llama.cpp (local)
```jsonc
{
  "provider": {
    "llama.cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-server (local)",
      "options": { "baseURL": "http://127.0.0.1:8080/v1" },
      "models": {
        "qwen3-coder:a3b": {
          "name": "Qwen3-Coder (local)",
          "limit": { "context": 128000, "output": 65536 }
        }
      }
    }
  }
}
```

### Proxy / Gateway (e.g., Helicone, Cloudflare AI Gateway)
```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://my-proxy.example.com/v1"
      }
    }
  }
}
```

## Provider Management

### Disable specific providers
```jsonc
{
  "disabled_providers": ["openai", "google"]
}
```
Prevents loading even if env vars / credentials exist.

### Allow only specific providers
```jsonc
{
  "enabled_providers": ["anthropic", "openai"]
}
```
All others are ignored. `disabled_providers` takes priority if both set.

## Model Selection

### Set default model
```jsonc
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```
`small_model` is used for lightweight tasks (title generation, etc.).

### Per-agent model override
```jsonc
{
  "agent": {
    "architect": {
      "model": "anthropic/claude-opus-4-5"
    },
    "quick-tasks": {
      "model": "anthropic/claude-haiku-4-5"
    }
  }
}
```

### Override model properties
```jsonc
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-opus-4-5": {
          "name": "Claude Opus (Custom Name)",
          "limit": { "context": 200000, "output": 32000 }
        }
      }
    }
  }
}
```

### Custom inference profiles (Bedrock ARN)
```jsonc
{
  "provider": {
    "amazon-bedrock": {
      "models": {
        "anthropic-claude-sonnet-4.5": {
          "id": "arn:aws:bedrock:us-east-1:xxx:application-inference-profile/yyy"
        }
      }
    }
  }
}
```

## Timeout Configuration

```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000
      }
    }
  }
}
```
Default: 300000ms (5 minutes). Set to `false` to disable.

## Provider Decision Tree

| Need | Provider | Auth Method |
|------|----------|-------------|
| Best coding quality | Anthropic Claude | `/connect` or API key |
| Budget-conscious | OpenCode Zen | `/connect` |
| Enterprise / compliance | Azure OpenAI or Bedrock | Config + IAM |
| Offline / air-gapped | Ollama or llama.cpp | Local, no auth |
| Multi-model routing | OpenRouter | API key |
| Existing subscription | GitHub Copilot | Device flow via `/connect` |
| Self-hosted GitLab | GitLab Duo | PAT or OAuth |
