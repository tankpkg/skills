# Troubleshooting and Optimization

Sources: Vercel CLI docs (2026), Vercel support documentation, production deployment patterns

Covers: Common errors and fixes, debugging commands, plan limits, cost
optimization strategies, recovery procedures, and vercel dev limitations.

## Diagnostic Commands

| Task | Command |
|------|---------|
| Check auth | `vercel whoami` |
| Check project linking | `vercel project inspect` |
| View build logs | `vercel inspect [deployment-url] --logs` |
| View runtime logs | `vercel logs --environment production` |
| Filter error logs | `vercel logs --level error --since 1h` |
| Filter by status code | `vercel logs --status-code 5xx --since 1h` |
| Stream live logs | `vercel logs --follow` |
| HTTP timing analysis | `vercel httpstat /api/endpoint` |
| Inspect deployment | `vercel inspect [deployment-url]` |
| Check env vars | `vercel env ls production` |
| Test build locally | `vercel build` |
| Purge CDN cache | `vercel cache purge --type cdn` |
| Purge data cache | `vercel cache purge --type data` |
| Invalidate cache tag | `vercel cache invalidate --tag foo` |

## Build Failures

| Error | Cause | Fix |
|-------|-------|-----|
| Missing environment variable | Variable not set for build environment | `vercel env ls production`, add missing vars |
| Command not found | Wrong build command or missing dependency | Check `buildCommand` in vercel.json or dashboard |
| Out of memory during build | Build process exceeds memory | Optimize build, reduce concurrent processes |
| Build timeout | Build exceeds time limit | Optimize build steps, use caching (Turborepo) |
| Module not found | Dependency not installed | Check `installCommand`, verify package.json |
| TypeScript errors | Type errors in production build | Fix types, don't use `skipLibCheck` as workaround |
| `now.json` deprecated | Using legacy config file | Rename to `vercel.json` (deadline: March 31, 2026) |

### Debug Build Locally

```bash
vercel env pull --environment=production  # Get production vars
vercel build --prod                       # Reproduce build locally
```

If local build succeeds but remote fails, check for missing env vars
or system dependencies.

## Function Errors

| Error | Cause | Fix |
|-------|-------|-----|
| FUNCTION_INVOCATION_TIMEOUT | Execution exceeds maxDuration | Increase `maxDuration`, optimize code, check DB queries |
| FUNCTION_INVOCATION_FAILED | Unhandled exception | Check logs: `vercel logs --level error` |
| FUNCTION_PAYLOAD_TOO_LARGE | Request/response body too large | Reduce payload size, use streaming |
| EDGE_FUNCTION_INVOCATION_TIMEOUT | Edge function exceeds 30s | Move to serverless, or optimize |
| FUNCTION_RATE_LIMIT | Too many concurrent invocations | Check concurrency limits for plan |
| NO_RESPONSE_FROM_FUNCTION | Function didn't return a response | Ensure all code paths return Response |
| FUNCTION_BOOT_TIMEOUT | Cold start too slow | Reduce bundle size, use Edge for lightweight ops |

### Debug Slow Functions

```bash
# Measure response time
vercel httpstat /api/slow-endpoint

# Check function logs
vercel logs --source serverless --query "slow-endpoint" --since 1h

# Check for timeout patterns
vercel logs --level error --query "timeout" --since 24h
```

## Edge Function Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Size limit exceeded | Bundle > 1MB compressed | Remove heavy deps, use serverless instead |
| Node.js API not available | Using fs, child_process, etc. | Use Web APIs or switch to serverless |
| Env var too large | Variable > 5KB | Use Edge Config for large values |
| Dynamic import failed | Not supported well in Edge | Use static imports |

## Domain and DNS Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Domain not verified | DNS not configured | `vercel domains inspect`, add required records |
| Certificate pending | DNS propagation incomplete | Wait up to 24h, verify DNS records |
| Domain in use | Assigned to another project | Use `--force` flag or remove from other project |
| CNAME conflict at apex | Apex domains can't use CNAME | Use A record (76.76.21.21) for apex |
| Wildcard not working | Not using Vercel nameservers | Migrate to ns1/ns2.vercel-dns.com |

## vercel dev Limitations

These features do not work locally with `vercel dev`:

| Feature | Limitation | Workaround |
|---------|-----------|------------|
| `has`/`missing` conditions | Not evaluated | Test on preview deployments |
| `cleanUrls` with Next.js | Returns 404 locally | Test on preview deployments |
| Bulk redirects | Not processed | Test on preview deployments |
| Edge Config | No local emulation | Use mock values in development |
| Image optimization | Limited local support | Test on preview deployments |
| Cron jobs | Not triggered locally | Call endpoints manually |
| Deployment protection | Not applicable | N/A |

## Plan Limits Reference

### Function Execution

| Metric | Hobby | Pro | Enterprise |
|--------|-------|-----|-----------|
| Max duration (Fluid) | 300s | 800s | 800s |
| Max duration (legacy) | 60s | 300s | 900s |
| Memory | 2 GB fixed | 2 or 4 GB | Custom |
| Included GB-hours | 100 | 1,000 | Custom |
| Included invocations | 100K | 1M | Custom |
| Concurrency | Auto | Auto (30K) | Auto (100K+) |
| Edge cold start | ~1ms | ~1ms | ~1ms |
| Serverless cold start | ~250ms | ~250ms | ~250ms |

### Bandwidth and Builds

| Metric | Hobby | Pro | Enterprise |
|--------|-------|-----|-----------|
| Bandwidth | 100 GB/mo | 1 TB/mo | Custom |
| Bandwidth overage | N/A | $0.15/GB | Custom |
| Build minutes | 100/mo | 6,000/mo | Custom |
| Build overage | N/A | $0.50/100min | Custom |
| Deployments/day | 100 | 6,000 | Custom |
| Team members | 1 | Unlimited | Unlimited |

### Configuration Limits

| Limit | Value |
|-------|-------|
| Redirects per array | 2,048 |
| Env var total size | 64 KB per deployment |
| Env var (Edge) | 5 KB per variable |
| Cron jobs | 100 per project |
| Regions (Pro) | 3 |
| Custom environments (Pro) | 1 |
| Custom environments (Enterprise) | 12 |
| Firewall IP rules (Pro) | 25 |
| Function size (compressed) | 250 MB serverless, 1 MB edge |

## Cost Optimization

### Bandwidth

1. **Image optimization**: Use `next/image` or `/_vercel/image` API.
2. **CDN caching**: Set `Cache-Control: public, s-maxage=3600, stale-while-revalidate=30`.
3. **Compression**: Automatic (gzip/brotli). Verify with `Content-Encoding` header.
4. **Code splitting**: Reduce initial bundle size. Dynamic imports for heavy modules.

### Function Invocations

1. **Static generation** over SSR where possible (`export const dynamic = 'force-static'`).
2. **Edge caching**: Cache API responses at the CDN layer.
3. **Batch operations**: Combine multiple API calls into one function.
4. **Client-side fetch**: For non-critical, personalized content.

### Build Minutes

1. **Turborepo remote caching**: 80-95% cache hit rate. Set `TURBO_TOKEN` and `TURBO_TEAM`.
2. **Incremental builds**: Only rebuild changed packages in monorepo.
3. **Skip unnecessary builds**: Use `ignoreCommand` in vercel.json.
4. **Frozen lockfile**: `pnpm install --frozen-lockfile` prevents resolution overhead.

### Spend Management (Pro)

Configure in dashboard Settings -> Billing -> Spend Management:
- Set monthly spending limits per resource type.
- Configure alert thresholds (email notifications).
- Enable auto-pause at spending cap.

## Recovery Procedures

### Production Down

```bash
# 1. Confirm the issue
vercel logs --environment production --status-code 5xx --since 30m

# 2. Roll back immediately
vercel rollback

# 3. Verify recovery
vercel logs --environment production --status-code 5xx --since 5m

# 4. Investigate the bad deployment
vercel list --prod
vercel inspect [bad-deployment-url] --logs
```

### Build Broken

```bash
# 1. Check env vars
vercel env ls production

# 2. Test build locally
vercel env pull --environment=production
vercel build --prod

# 3. Check dependencies
vercel inspect [failed-deployment] --logs
```

### Slow Functions

```bash
# 1. Identify slow endpoints
vercel httpstat /api/suspect-endpoint

# 2. Check for cold starts (first request after idle)
vercel logs --source serverless --since 1h --json | jq 'select(.duration > 5000)'

# 3. Optimize
# - Reduce bundle size (check includeFiles/excludeFiles)
# - Use Edge runtime for lightweight operations
# - Add connection pooling for databases
# - Enable Fluid compute (default for new projects)
```

### Cache Issues

```bash
# Purge everything
vercel cache purge

# Purge specific cache type
vercel cache purge --type cdn
vercel cache purge --type data

# Invalidate by tag
vercel cache invalidate --tag products
```

## Prebuilt Deployment Gotchas

When using `vercel build` + `vercel deploy --prebuilt`:

| Missing Feature | Reason | Workaround |
|----------------|--------|------------|
| Skew Protection | No deployment ID at build time | Use Git-based deployments |
| `VERCEL_URL` | System vars not available | Hardcode or use build-time vars |
| `VERCEL_GIT_*` vars | Git metadata not available | Pass via `--build-env` |
| Deployment metadata | Not auto-populated | Use `--meta` flag manually |

Prefer Git-based deployments when these features are needed.
