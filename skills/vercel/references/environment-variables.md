# Environment Variables

Sources: Vercel CLI docs (2026), Vercel environment variable documentation

Covers: Per-environment management, branch-specific variables, sensitive
variables, pull and run workflows, system variables, and limits.

## Three Default Environments

| Environment | When Applied | Typical Use |
|-------------|-------------|-------------|
| Development | `vercel dev`, `vercel env pull` | Local development |
| Preview | Non-production branches, PR deploys | Staging, testing |
| Production | Production branch (usually `main`) | Live site |

Variables set for one environment do not leak to others.

## Custom Environments

Pro: 1 custom environment per project. Enterprise: 12.

Create via dashboard (Project Settings -> Environments) or API. Custom
environments can track specific branches and have their own domains.

Deploy to a custom environment:

```bash
vercel deploy --target=staging
vercel pull --environment=staging
vercel build --target=staging
```

## CLI Operations

### Add Variables

```bash
vercel env add                           # Interactive (all environments)
vercel env add API_KEY                   # Add to all environments
vercel env add API_KEY production        # Add to production only
vercel env add API_KEY preview feature-x # Add to preview, feature-x branch
vercel env add API_KEY --sensitive       # Hidden in dashboard
vercel env add DB_URL production < secret.txt  # From file
echo "value" | vercel env add TOKEN production # From stdin
```

### Update Variables

```bash
vercel env update API_KEY                # Update across all environments
vercel env update API_KEY production     # Update production only
vercel env update API_KEY --sensitive    # Mark as sensitive
cat ~/.npmrc | vercel env update NPM_RC preview  # From stdin
```

### Remove Variables

```bash
vercel env rm API_KEY production         # Remove from production
vercel env rm API_KEY --yes              # Skip confirmation
```

### List Variables

```bash
vercel env ls                            # All environments
vercel env ls production                 # Production only
vercel env ls preview feature-x          # Preview, specific branch
```

## Pull to File

Export environment variables to a local file.

```bash
vercel env pull                          # -> .env.local (development vars)
vercel env pull .env.production          # Custom filename
vercel env pull --environment=preview    # Preview vars
vercel env pull --environment=production # Production vars
vercel env pull --environment=preview --git-branch=feature  # Branch-specific
vercel env pull --yes                    # Overwrite without prompt
```

## Run with Variables

Execute a command with environment variables loaded in memory.

```bash
vercel env run -- next dev               # Development vars
vercel env run -e preview -- npm test    # Preview vars
vercel env run -e production -- next build  # Production vars
vercel env run -e preview --git-branch feature-x -- next dev  # Branch-specific
```

Variables are loaded into the process environment, not written to disk.

## Pull vs Env Pull

| Command | Output | Use When |
|---------|--------|----------|
| `vercel pull` | `.vercel/.env.$target.local` + project settings | Before `vercel build` or `vercel dev` |
| `vercel env pull` | `.env.local` (or custom file) | Need vars in specific file format |
| `vercel env run` | In-memory only | Run one-off commands with vars |

In CI/CD, use `vercel pull` before `vercel build`. For local development,
`vercel env pull` or `vercel dev` (which pulls automatically).

## Runtime Injection

Override or add variables for a single deployment:

```bash
vercel deploy --env KEY=value --env KEY2=value2
vercel deploy --build-env KEY=value      # Build-time only
```

`--env` overrides dashboard values for that specific deployment.
`--build-env` is available only during the build step.

## System Environment Variables

Automatically available in every deployment:

| Variable | Example | Description |
|----------|---------|-------------|
| `VERCEL_ENV` | `production` | Current environment (`production`, `preview`, `development`) |
| `VERCEL_URL` | `my-app-abc.vercel.app` | Deployment URL (no protocol) |
| `VERCEL_BRANCH_URL` | `my-app-git-main.vercel.app` | Branch-based URL |
| `VERCEL_PROJECT_PRODUCTION_URL` | `my-app.vercel.app` | Production URL |
| `VERCEL_GIT_COMMIT_SHA` | `abc123` | Git commit SHA |
| `VERCEL_GIT_COMMIT_MESSAGE` | `fix: typo` | Commit message |
| `VERCEL_GIT_COMMIT_AUTHOR_LOGIN` | `username` | Commit author |
| `VERCEL_GIT_REPO_SLUG` | `my-repo` | Repository name |
| `VERCEL_GIT_REPO_OWNER` | `my-org` | Repository owner |
| `VERCEL_GIT_PROVIDER` | `github` | Git provider |
| `VERCEL_TARGET_ENV` | `staging` | Custom environment name (if applicable) |

Not available during prebuilt deployments (`vercel deploy --prebuilt`).

## Branch-Specific Variables

Override preview variables for specific Git branches:

```bash
# Default preview value
vercel env add API_URL preview
# Enter: https://staging-api.example.com

# Override for feature-x branch
vercel env add API_URL preview feature-x
# Enter: https://feature-x-api.example.com
```

All preview deployments use the default value except `feature-x`, which
uses its own override.

## Sensitive Variables

Mark variables as sensitive to hide values in the dashboard:

```bash
vercel env add API_SECRET --sensitive
vercel env update API_SECRET --sensitive
```

Sensitive variables:
- Hidden in dashboard UI (shown as `***`)
- Still available at runtime in functions
- Cannot be read back via CLI or API
- Can only be overwritten, not viewed

## Limits

| Limit | Value |
|-------|-------|
| Total size per deployment | 64 KB (all variables combined) |
| Per variable (Edge Functions/Middleware) | 5 KB |
| Variable name | Alphanumeric + underscores |
| Custom environments (Pro) | 1 per project |
| Custom environments (Enterprise) | 12 per project |

## Integration Variables

Marketplace integrations (Neon, Upstash, Vercel Blob) automatically add
environment variables to the project. These appear in the dashboard under
the integration's section and are available in all environments by default.

```bash
# Pull integration variables along with project vars
vercel env pull
```

## Security Best Practices

1. **Never commit .env files** to Git. Add `.env*` and `.vercel/` to `.gitignore`.
2. **Use --sensitive** for API keys, database URLs, and tokens.
3. **Rotate credentials** regularly. Update via `vercel env update`.
4. **Use CI secrets** (GitHub Secrets, GitLab CI variables) for `VERCEL_TOKEN`.
5. **Separate by environment**. Production database URLs should never appear in preview.
6. **Audit variables** periodically with `vercel env ls`.
7. **Use Edge Config** instead of env vars for large configuration data (>5KB).
8. **Never pass secrets via CLI flags**. Use `--env` for non-sensitive overrides only.

## Local Development Workflow

```bash
# Initial setup
vercel link --yes
vercel env pull                          # Creates .env.local

# Daily development
vercel dev                               # Loads vars automatically
# or
vercel env run -- next dev               # Loads vars into process
```

## CI/CD Workflow

```bash
# Set as CI secrets: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
vercel pull --yes --environment=production --token=$VERCEL_TOKEN
vercel build --prod --token=$VERCEL_TOKEN
vercel deploy --prod --prebuilt --token=$VERCEL_TOKEN
```

All environment variables are synced in the `pull` step. No need to
pass `--env` flags unless overriding specific values.

## Env Var Naming Conventions

| Prefix | Meaning | Behavior |
|--------|---------|----------|
| `NEXT_PUBLIC_` | Exposed to browser (Next.js) | Inlined at build time, visible in client JS |
| `NUXT_PUBLIC_` | Exposed to browser (Nuxt) | Available in client bundle |
| `VITE_` | Exposed to browser (Vite) | Replaced at build time |
| No prefix | Server-only | Available only in serverless/edge functions |

**Warning**: Variables with public prefixes are embedded in the JavaScript bundle.
Never put secrets in `NEXT_PUBLIC_`, `NUXT_PUBLIC_`, or `VITE_` prefixed variables.

## Common Patterns

### Database URL per Environment

```bash
vercel env add DATABASE_URL development
# Enter: postgresql://localhost:5432/mydb

vercel env add DATABASE_URL preview
# Enter: postgresql://staging-host:5432/mydb

vercel env add DATABASE_URL production --sensitive
# Enter: postgresql://prod-host:5432/mydb
```

### Feature Flags via Env Vars

```bash
vercel env add FEATURE_NEW_UI preview    # Enable in preview
# Enter: true

vercel env add FEATURE_NEW_UI production # Disable in production
# Enter: false
```

### Third-Party API Keys

```bash
vercel env add STRIPE_SECRET_KEY production --sensitive
vercel env add STRIPE_PUBLISHABLE_KEY production
# Publishable keys are public, so --sensitive is not needed

vercel env add STRIPE_SECRET_KEY preview --sensitive
# Use test mode key for preview
```

### Vercel Integration Variables

When adding marketplace integrations (Neon, Upstash, Vercel Blob), variables
are added automatically. Check which variables were added:

```bash
vercel env ls production | grep -i "neon\|upstash\|blob"
```

Common auto-added variables:
- `DATABASE_URL`, `DATABASE_URL_UNPOOLED` (Neon)
- `KV_REST_API_URL`, `KV_REST_API_TOKEN` (Upstash)
- `BLOB_READ_WRITE_TOKEN` (Vercel Blob)

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Var not available in function | Wrong environment selected | Check `vercel env ls production` |
| Var empty after deploy | Not synced before build | Run `vercel pull` before `vercel build` |
| `NEXT_PUBLIC_` var undefined | Not available at build time | Rebuild after adding variable |
| Edge function can't read var | Variable > 5KB | Use Edge Config for large values |
| Var visible in client bundle | Using `NEXT_PUBLIC_` prefix | Remove prefix for server-only vars |
| Different value in preview vs prod | Intentional per-env separation | Check with `vercel env ls` per env |
