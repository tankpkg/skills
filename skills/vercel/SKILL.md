---
name: "@tank/vercel"
description: |
  Vercel deployment and project management using the CLI. Covers all CLI
  commands (deploy, build, dev, pull, env, domains, dns, logs, promote,
  rollback), vercel.json configuration (redirects, rewrites, headers,
  functions, crons, images, regions), CI/CD workflows (GitHub Actions,
  GitLab CI, preview and production pipelines), environment variable
  management, domain and DNS setup, serverless and edge functions, and
  troubleshooting. Synthesizes Vercel CLI docs (2026), vercel.json schema,
  and production deployment patterns.

  Trigger phrases: "vercel", "vercel deploy", "vercel cli", "vercel build",
  "vercel dev", "vercel pull", "vercel env", "vercel domains", "vercel dns",
  "vercel logs", "vercel promote", "vercel rollback", "vercel.json",
  "deployment", "preview deployment", "production deployment", "CI/CD vercel",
  "serverless function", "edge function", "cron job vercel", "vercel monorepo",
  "vercel turborepo", "vercel domain", "vercel certificate", "deploy to vercel",
  "vercel environment variables", "vercel preview", "vercel production"
---

# Vercel Deployment and Management

Deploy, configure, and manage Vercel projects using the CLI. Covers the
complete lifecycle from project setup through production deployment,
monitoring, and troubleshooting.

## Core Philosophy

1. **Verify before acting** -- Run `vercel whoami` to confirm auth and
   `vercel project inspect` to confirm project linking before any operation.
2. **Pull before build** -- Always run `vercel pull` before `vercel build`
   or `vercel dev` to sync environment variables and project settings.
3. **Preview before production** -- Deploy to preview first, verify, then
   promote or deploy to production. Never skip preview in CI/CD.
4. **Use --yes in automation** -- Every interactive prompt has a flag-based
   path. Use `--yes` and `--token` for all CI/CD commands.
5. **Match functions to workload** -- Use Edge for auth/routing/geo (<30s,
   global), Serverless for heavy compute (up to 800s, regional).

## Quick-Start

### "I want to deploy my project"

| Step | Action |
|------|--------|
| 1 | Check auth: `vercel whoami` |
| 2 | Link project: `vercel link` (or `vercel link --yes` in CI) |
| 3 | Preview deploy: `vercel` |
| 4 | Production deploy: `vercel --prod` |
-> See `references/deployment-workflows.md` for CI/CD patterns

### "I need to set up CI/CD with GitHub Actions"

| Step | Action |
|------|--------|
| 1 | Set secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` |
| 2 | Use the 3-step pattern: pull -> build -> deploy |
| 3 | Use `--prebuilt --archive=tgz` for faster deploys |
-> See `references/deployment-workflows.md`

### "I need to configure my project"

| Step | Action |
|------|--------|
| 1 | Add `$schema` for autocomplete |
| 2 | Configure redirects, rewrites, headers, functions, crons |
| 3 | Set regions for function deployment |
-> See `references/project-configuration.md`

### "Something is broken"

| Symptom | Action |
|---------|--------|
| Build fails | Check env vars: `vercel env ls`, test locally: `vercel build` |
| Function timeout | Check limits, increase `maxDuration`, check Fluid compute |
| 5xx errors | `vercel logs --status-code 5xx --since 1h` |
| Slow function | `vercel httpstat /api/endpoint`, check cold starts |
| Domain not working | `vercel domains inspect`, check DNS propagation |
| Need to revert | `vercel rollback` (instant, no rebuild) |
-> See `references/troubleshooting.md`

## Project Detection

Before running commands, check for existing Vercel setup:

| Signal | Meaning | Next Step |
|--------|---------|-----------|
| `.vercel/` directory exists | Project is linked | Verify with `vercel project inspect` |
| `vercel.json` exists | Project has config | Read and respect existing settings |
| Neither exists | New project | Run `vercel link` to connect |
| `vercel.json` + no `.vercel/` | Config but not linked | Run `vercel link --yes` |

## Decision Trees

### Deployment Method

| Signal | Method | Reference |
|--------|--------|-----------|
| Push to Git, automatic deploys desired | Git integration (dashboard) | -- |
| CI/CD pipeline, custom build steps | CLI: pull -> build -> deploy | `references/deployment-workflows.md` |
| Quick manual deploy from local | `vercel` or `vercel --prod` | `references/cli-commands.md` |
| Monorepo with Turborepo | Turbo build + `vercel deploy --prebuilt` | `references/deployment-workflows.md` |
| Deploy without sharing source | `vercel build` + `vercel deploy --prebuilt` | `references/deployment-workflows.md` |

### Function Runtime

| Need | Runtime | Key Constraints |
|------|---------|----------------|
| Full Node.js APIs, heavy compute | Serverless (Node.js) | Regional, ~250ms cold start |
| Ultra-low latency, global | Edge | No fs/native modules, 30s max, 1MB compressed |
| Auth gating, redirects, geo-routing | Edge Middleware | Runs before every matched request |
| Python, Go, Ruby | Serverless (community) | Limited runtime support |

### Environment Variables

| Task | Command |
|------|---------|
| Add variable to production | `vercel env add NAME production` |
| Pull vars for local dev | `vercel env pull` |
| Run command with env vars | `vercel env run -- next dev` |
| Sync project settings + vars | `vercel pull` |
| Override var for one deploy | `vercel deploy --env KEY=value` |
-> See `references/environment-variables.md`

## Anti-Patterns

| Don't | Do Instead | Why |
|-------|-----------|-----|
| Deploy to production without preview | `vercel` first, then `vercel --prod` | Catch issues before users see them |
| Use interactive prompts in CI | Add `--yes --token $TOKEN` to all commands | CI has no TTY |
| Skip `vercel pull` before `vercel build` | Always pull first | Build needs env vars and project settings |
| Set memory in vercel.json with Fluid | Configure in dashboard Settings | Fluid compute manages memory differently |
| Use `has`/`missing` and test with `vercel dev` | Test conditional routes on preview deploys | Conditions don't work locally |
| Hardcode env vars in vercel.json | Use `vercel env add` or dashboard | Env vars don't belong in config files |
| Commit `.vercel/` directory | Add to `.gitignore` | Contains local project linking data |
| Use `vercel deploy` for monorepo CI | Use `turbo build` + `vercel deploy --prebuilt` | Turborepo caching saves 80%+ build time |
| Promote preview without checking env vars | Verify: promoted deploys use production env vars | Preview and production env vars differ |
| Use serverless for auth/redirects | Use Edge middleware | Edge is global, <1ms cold start |

## The 3-Step CI/CD Pattern

The standard deployment pattern for all CI/CD pipelines:

```bash
vercel pull --yes --environment=production --token=$VERCEL_TOKEN
vercel build --prod --token=$VERCEL_TOKEN
vercel deploy --prod --prebuilt --archive=tgz --token=$VERCEL_TOKEN
```

Step 1 syncs env vars and project config. Step 2 builds locally.
Step 3 uploads pre-built artifacts. Use `--archive=tgz` for large projects.

For preview deployments, remove `--prod` from build and deploy, and use
`--environment=preview` for pull.

## Reference Files

| File | Contents |
|------|----------|
| `references/cli-commands.md` | All CLI commands organized by category, key flags and options for each, global options, project specification precedence, usage examples |
| `references/project-configuration.md` | Complete vercel.json schema, all configuration fields with JSON examples, framework presets, monorepo config, routing (redirects, rewrites, headers), functions, crons, images, gotchas |
| `references/deployment-workflows.md` | CI/CD patterns (GitHub Actions, GitLab CI, Bitbucket), preview and production workflows, promote, rollback, rolling releases, monorepo deployment, deploy hooks, prebuilt deploys |
| `references/environment-variables.md` | Per-environment management, branch-specific vars, sensitive vars, pull vs env pull, env run, system variables, limits, security best practices |
| `references/domains-and-dns.md` | Domain lifecycle, DNS records (A, CNAME, MX, TXT, SRV, CAA), SSL certificates, wildcard domains, multi-tenant patterns, apex and www setup |
| `references/serverless-and-edge.md` | Serverless vs edge functions, middleware, geolocation, Edge Config, cold start mitigation, streaming, Build Output API, storage integrations, firewall, feature flags |
| `references/troubleshooting.md` | Common errors and fixes, debugging commands, plan limits by tier, cost optimization strategies, recovery procedures, cache management, vercel dev limitations |
