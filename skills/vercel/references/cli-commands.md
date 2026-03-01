# CLI Commands Reference

Sources: Vercel CLI documentation (2026), vercel/vercel AGENTS.md

Covers: All CLI commands organized by category, key flags, global options,
project specification, and usage patterns.

## Core Commands

### deploy (default command)

Deploy project to Vercel. Runs as default when no subcommand is given.

```bash
vercel                              # Preview deployment
vercel --prod                       # Production deployment
vercel deploy --prebuilt            # Deploy pre-built output
vercel deploy --prebuilt --archive=tgz  # Compress for large projects
```

| Flag | Short | Description |
|------|-------|-------------|
| `--prod` | | Deploy to production |
| `--prebuilt` | | Deploy output from `vercel build` |
| `--archive=tgz` | | Compress upload (faster for many files) |
| `--env KEY=value` | `-e` | Runtime environment variable |
| `--build-env KEY=value` | `-b` | Build-time environment variable |
| `--skip-domain` | | Skip auto-domain assignment |
| `--force` | `-f` | Force new build (ignore cache) |
| `--with-cache` | | Keep cache when using `--force` |
| `--logs` | `-l` | Print build logs |
| `--meta KEY=value` | `-m` | Deployment metadata |
| `--target=staging` | | Deploy to custom environment |
| `--no-wait` | | Return immediately (don't wait) |
| `--yes` | `-y` | Skip interactive prompts |

**Output**: stdout contains deployment URL. stderr contains errors (exit code != 0).

### build

Build project locally using Vercel's build pipeline. Output goes to `.vercel/output/`.

```bash
vercel build                        # Build with preview env vars
vercel build --prod                 # Build with production env vars
vercel build --target=staging       # Build for custom environment
vercel build --yes                  # Auto-pull env vars if missing
```

Run `vercel pull` first to sync env vars and project settings.

### dev

Start local development server replicating Vercel's environment.

```bash
vercel dev                          # Start dev server
vercel dev --listen 5005            # Custom port
vercel dev --yes                    # Skip setup questions
```

Run `vercel pull` first. Prefer framework-native dev commands (e.g., `next dev`)
when they provide equivalent functionality.

### pull

Sync environment variables and project settings to `.vercel/` directory.

```bash
vercel pull                         # Pull development vars
vercel pull --environment=preview   # Pull preview vars
vercel pull --environment=production  # Pull production vars
vercel pull --environment=preview --git-branch=feature  # Branch-specific
vercel pull --yes                   # Skip prompts
```

Output stored in `.vercel/.env.$target.local`. Always run before `vercel build` or `vercel dev`.

### link

Connect local directory to a Vercel project. Creates `.vercel/` directory.

```bash
vercel link                         # Interactive linking
vercel link --yes                   # Use defaults
vercel link --yes --project foo     # Link to specific project
vercel link --repo                  # Link all projects in monorepo
```

### logs

View and filter request logs or stream runtime logs.

```bash
vercel logs                         # Last 24h, current project
vercel logs --follow                # Live stream
```

| Filter | Flag | Example |
|--------|------|---------|
| Environment | `--environment` | `--environment production` |
| Log level | `--level` | `--level error --level warning` |
| Status code | `--status-code` | `--status-code 5xx` |
| Source | `--source` | `--source edge-function` |
| Full-text search | `--query` / `-q` | `--query "timeout"` |
| Time range | `--since` / `--until` | `--since 1h --until 30m` |
| Branch | `--branch` / `-b` | `--branch feature-x` |
| Request ID | `--request-id` | `--request-id req_xxx` |
| JSON output | `--json` / `-j` | Pipe to `jq` |
| Expand messages | `--expand` / `-x` | Full log content |
| Max entries | `--limit` / `-n` | `--limit 50` |

Sources: `serverless`, `edge-function`, `edge-middleware`, `static`.

### inspect

Retrieve deployment details.

```bash
vercel inspect [deployment-url]
vercel inspect [deployment-url] --logs   # Include build logs
vercel inspect [deployment-url] --wait   # Wait for completion
```

## Environment Variable Commands

```bash
vercel env add [name] [env] [branch]       # Add variable
vercel env update [name] [env]             # Update variable
vercel env rm [name] [env]                 # Remove variable
vercel env ls [env] [branch]              # List variables
vercel env pull [file]                     # Export to file (default: .env.local)
vercel env run -- <command>                # Run command with vars loaded
```

| Flag | Description |
|------|-------------|
| `--sensitive` | Mark variable as hidden in dashboard |
| `--force` | Overwrite without confirmation |
| `-e, --environment` | Target environment |
| `--git-branch` | Target Git branch |

See `references/environment-variables.md` for workflows.

## Domain and DNS Commands

### domains

```bash
vercel domains ls                          # List domains
vercel domains inspect [domain]            # Domain details
vercel domains add [domain] [project]      # Add to project
vercel domains add [domain] [project] --force  # Force add
vercel domains rm [domain]                 # Remove domain
vercel domains buy [domain]                # Purchase domain
vercel domains move [domain] [scope]       # Move to another team
vercel domains transfer-in [domain]        # Transfer domain in
```

### dns

```bash
vercel dns ls                              # List records
vercel dns add [domain] [name] [type] [value]  # Add record
vercel dns rm [record-id]                  # Remove record
vercel dns import [domain] [zonefile]      # Import zonefile
```

Record types: `A`, `AAAA`, `CNAME`, `TXT`, `MX` (with priority), `SRV` (priority weight port target), `CAA`.

### alias

```bash
vercel alias set [deployment-url] [custom-domain]
vercel alias rm [custom-domain]
vercel alias ls
```

### certs

```bash
vercel certs ls                            # List certificates
vercel certs issue [domain]                # Issue certificate
vercel certs issue [domain] --challenge-only  # Show DNS challenges
vercel certs rm [cert-id]                  # Remove certificate
```

## Deployment Lifecycle Commands

### promote

Promote a deployment to production.

```bash
vercel promote [deployment-url]
vercel promote [deployment-url] --timeout=5m
vercel promote status [project]
```

Warning: promoting preview deployments switches env vars to production values.

### rollback

Roll back production to a previous deployment. Instant, no rebuild.

```bash
vercel rollback                            # Previous deployment (all plans)
vercel rollback [deployment-url]           # Specific deployment (Pro/Enterprise)
vercel rollback status
```

### redeploy

Rebuild and redeploy an existing deployment.

```bash
vercel redeploy [deployment-url]
```

### rolling-release

Configure gradual traffic rollout.

```bash
vercel rolling-release configure --cfg='{"enabled":true,"stages":[...]}'
vercel rolling-release start --dpl=[deployment-id]
vercel rolling-release approve --dpl=[deployment-id]
vercel rolling-release complete --dpl=[deployment-id]
vercel rolling-release fetch
```

### list

```bash
vercel list                                # Current project deployments
vercel list [project-name]                 # Specific project
```

### remove

```bash
vercel remove [deployment-url]             # Remove deployment
vercel remove [project-name]               # Remove all deployments
```

## Project and Team Commands

```bash
vercel project ls                          # List projects
vercel project ls --json                   # JSON output
vercel project ls --update-required        # Projects needing Node.js update
vercel project add                         # Create project
vercel project inspect                     # Inspect linked project
vercel project rm                          # Remove project

vercel teams list                          # List teams
vercel teams add                           # Create team
vercel teams invite [email]                # Invite member
vercel switch                              # Switch team (interactive)
vercel switch [team-slug]                  # Switch to specific team

vercel target list                         # List custom environments
```

## Storage and Cache Commands

```bash
vercel blob list                           # List blobs
vercel blob put [file]                     # Upload file
vercel blob get [url]                      # Download blob
vercel blob del [url]                      # Delete blob
vercel blob copy [from] [to]              # Copy blob

vercel cache purge                         # Purge all cache
vercel cache purge --type cdn              # CDN cache only
vercel cache purge --type data             # Data cache only
vercel cache invalidate --tag foo          # Invalidate by tag
```

## Integration Commands

```bash
vercel integration add [name]              # Add marketplace integration
vercel integration list                    # List integrations
vercel integration remove [name]           # Remove integration
vercel integration discover               # Browse available integrations
vercel install [name]                      # Alias for integration add
```

## Utility Commands

```bash
vercel whoami                              # Current user
vercel login                               # Email login
vercel login --github                      # GitHub login
vercel logout                              # Logout
vercel open                                # Open project in dashboard
vercel init [template]                     # Initialize from template
vercel bisect                              # Binary search deployments for issues
vercel curl [path]                         # HTTP request with protection bypass
vercel httpstat [path]                     # HTTP timing statistics
vercel git connect                         # Connect Git provider
vercel git disconnect                      # Disconnect Git provider
vercel webhooks list                       # List webhooks
vercel webhooks create [url] --event [event]  # Create webhook
vercel telemetry status                    # Check telemetry
```

## Global Options

Available for all commands:

| Flag | Short | Description |
|------|-------|-------------|
| `--token [token]` | `-t` | Authorization token |
| `--scope [slug]` | `-S` | Execute from specific scope |
| `--project [name-or-id]` | | Specify project |
| `--team [slug-or-id]` | `-T` | Specify team |
| `--cwd [path]` | | Working directory |
| `--debug` | `-d` | Verbose output |
| `--no-color` | | Disable color and emoji |
| `--yes` | `-y` | Skip interactive prompts |
| `--global-config [path]` | `-Q` | Global config directory |
| `--local-config [path]` | `-A` | Path to vercel.json |

## Project Specification Precedence

1. `--project` flag (highest priority)
2. `VERCEL_PROJECT_ID` environment variable
3. `.vercel/project.json` from project linking (lowest priority)

## CI/CD Environment Variables

| Variable | Purpose |
|----------|---------|
| `VERCEL_TOKEN` | Authentication token (create at vercel.com/account/tokens) |
| `VERCEL_ORG_ID` | Organization/team ID |
| `VERCEL_PROJECT_ID` | Project ID |

Set these as CI secrets. Use `--token $VERCEL_TOKEN` on every command in CI.
