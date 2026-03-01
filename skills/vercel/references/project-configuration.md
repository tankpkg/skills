# Project Configuration

Sources: Vercel project configuration docs (2026), vercel.json schema

Covers: Complete vercel.json schema, all configuration fields, framework
presets, monorepo configuration, and common gotchas.

## Schema Autocomplete

Always include for IDE validation and autocomplete:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json"
}
```

## Build Settings

| Field | Type | Description |
|-------|------|-------------|
| `buildCommand` | `string\|null` | Override build command. `null` skips build. |
| `devCommand` | `string\|null` | Override local dev command. |
| `installCommand` | `string\|null` | Override install command. `""` skips install. |
| `outputDirectory` | `string\|null` | Build output directory (default: framework-specific). |
| `framework` | `string\|null` | Override framework detection. `null` for "Other". |
| `bunVersion` | `"1.x"` | Use Bun runtime instead of Node.js. |
| `ignoreCommand` | `string\|null` | Skip builds conditionally. Exit 0 = skip, 1 = build. |
| `public` | `boolean` | Make source and logs publicly accessible. |
| `fluid` | `boolean\|null` | Enable Fluid compute (default for new projects since April 2025). |

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "pnpm build",
  "installCommand": "pnpm install --frozen-lockfile",
  "outputDirectory": "dist",
  "framework": "nextjs"
}
```

## URL Handling

| Field | Type | Default | Effect |
|-------|------|---------|--------|
| `cleanUrls` | `boolean` | `false` | Remove `.html` extensions. `about.html` becomes `/about`. |
| `trailingSlash` | `boolean` | `undefined` | `true`: `/about` -> `/about/`. `false`: `/about/` -> `/about`. |

## Redirects

```json
{
  "redirects": [
    { "source": "/old", "destination": "/new", "permanent": true },
    { "source": "/blog/:path*", "destination": "/news/:path*" },
    { "source": "/post/:path(\\d{1,})", "destination": "/news/:path*" }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `source` | `string` | Path pattern (excludes querystring). |
| `destination` | `string` | Target path or external URL. |
| `permanent` | `boolean` | `true` = 308, `false` = 307. Default: `true`. |
| `statusCode` | `number` | Explicit status (301/302/303/307/308). Overrides `permanent`. |
| `has` | `Array` | Match when property is present. |
| `missing` | `Array` | Match when property is absent. |

**Conditional redirects** (geo-routing example):

```json
{
  "redirects": [
    {
      "source": "/:path((?!uk/).*)",
      "has": [{ "type": "header", "key": "x-vercel-ip-country", "value": "GB" }],
      "destination": "/uk/:path*",
      "permanent": false
    }
  ]
}
```

**has/missing object types**: `"header"`, `"cookie"`, `"host"`, `"query"`.

Limit: 2,048 redirects per array. Use `bulkRedirectsPath` for more.

## Bulk Redirects

```json
{ "bulkRedirectsPath": "./redirects.csv" }
```

Supports CSV, JSON, JSONL files. Can point to a folder. Fields: `source`,
`destination`, `permanent`, `statusCode`, `caseSensitive`, `preserveQueryParams`.

CSV boolean shorthand: `t` (true) or `f` (false).

Does not work with `vercel dev`. No wildcard matching.

## Rewrites

Route requests without changing the visible URL.

```json
{
  "rewrites": [
    { "source": "/about", "destination": "/about-our-company.html" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**External rewrites** (reverse proxy):

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.example.com/:path*" }
  ]
}
```

**Cache external rewrites**: Add `x-vercel-enable-rewrite-caching` header, then
control TTL with `CDN-Cache-Control: max-age=60`. Include `Vercel-Cache-Tag`
for cache purging.

For same-application rewrites, prefer framework-native routing (Next.js
`next.config.js`, SvelteKit, Astro). Use vercel.json rewrites only for
external rewrites or frameworks without native routing.

## Headers

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ]
}
```

Supports `has`/`missing` conditions (same syntax as redirects).

**Separate client and CDN caching**:

```json
{
  "headers": [
    {
      "source": "/api/data",
      "headers": [
        { "key": "Cache-Control", "value": "private, max-age=0" },
        { "key": "CDN-Cache-Control", "value": "public, s-maxage=3600" }
      ]
    }
  ]
}
```

## Functions

Configure serverless function behavior per glob pattern.

```json
{
  "functions": {
    "api/heavy.ts": {
      "maxDuration": 60,
      "runtime": "nodejs20.x",
      "includeFiles": "data/**",
      "excludeFiles": "**/*.test.ts",
      "regions": ["sfo1"],
      "functionFailoverRegions": ["iad1"],
      "supportsCancellation": true
    },
    "api/*.ts": {
      "maxDuration": 30
    }
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `maxDuration` | `number` | Max execution time in seconds (up to plan limit). |
| `memory` | `number` | Memory in MB. Cannot set with Fluid compute (use dashboard). |
| `runtime` | `string` | Runtime identifier (e.g., `"nodejs20.x"`, `"vercel-php@0.5.2"`). |
| `includeFiles` | `string` | Glob for files to include in bundle. |
| `excludeFiles` | `string` | Glob for files to exclude from bundle. |
| `regions` | `Array` | Override project-level regions. |
| `functionFailoverRegions` | `Array` | Failover regions (Enterprise only). |
| `supportsCancellation` | `boolean` | Enable request cancellation (Node.js only). |

Glob pattern order matters -- more specific patterns first.

## Regions

```json
{
  "regions": ["iad1", "sfo1"],
  "functionFailoverRegions": ["cle1"]
}
```

Default: `["iad1"]`. Pro: up to 3 regions. Enterprise: unlimited.

Common regions: `iad1` (Washington DC), `sfo1` (San Francisco), `cdg1` (Paris),
`lhr1` (London), `fra1` (Frankfurt), `sin1` (Singapore), `hnd1` (Tokyo),
`syd1` (Sydney), `gru1` (Sao Paulo).

## Crons

```json
{
  "crons": [
    { "path": "/api/cleanup", "schedule": "0 0 * * *" },
    { "path": "/api/hourly", "schedule": "0 * * * *" }
  ]
}
```

Schedule format: `minute hour day-of-month month day-of-week` (UTC).
Max 100 jobs. Hobby: daily minimum. Pro: per-minute.

Cannot use both day-of-month and day-of-week (one must be `*`).
Cannot use named days/months (`MON`, `JAN`). Use numbers only.

Cron requests include `vercel-cron/1.0` user agent. Secure with
`CRON_SECRET` env var and authorization header check.

## Images

```json
{
  "images": {
    "sizes": [640, 750, 828, 1080, 1200],
    "remotePatterns": [
      { "protocol": "https", "hostname": "example.com", "pathname": "/images/**" }
    ],
    "minimumCacheTTL": 60,
    "formats": ["image/webp"],
    "dangerouslyAllowSVG": false
  }
}
```

`sizes` is required. Image optimization URL: `/_vercel/image?url={src}&w=640&q=75`
(or `/_next/image` for Next.js). Redeploying does not invalidate image cache.

## Framework-Specific Notes

**Next.js**: Use `outputFileTracingIncludes`/`outputFileTracingExcludes` in
`next.config.js` instead of `includeFiles`/`excludeFiles` in vercel.json.
Prefer `next.config.js` for redirects, rewrites, and headers.

**Framework-specific maxDuration**:

```typescript
// Next.js App Router
export const maxDuration = 30;

// Next.js Pages Router
export const config = { maxDuration: 30 };
```

SvelteKit, Astro, Nuxt: configure in adapter options or framework config.

## Monorepo Configuration

Root-level `vercel.json` applies to all projects. Project-level config overrides root.

```
monorepo/
├── vercel.json              # Shared config (headers, regions)
├── apps/
│   ├── web/
│   │   └── vercel.json      # Project-specific overrides
│   └── api/
│       └── vercel.json
```

Each app is a separate Vercel project. Use `buildCommand` with package filter:

```json
{
  "buildCommand": "pnpm --filter=web build",
  "installCommand": "pnpm install --frozen-lockfile",
  "outputDirectory": "apps/web/dist"
}
```

## Gotchas

| Issue | Cause | Workaround |
|-------|-------|------------|
| `has`/`missing` conditions return wrong results locally | Not supported in `vercel dev` | Test on preview deployments |
| cleanUrls returns 404 with `vercel dev` + Next.js | Local dev limitation | Test on preview deployments |
| Bulk redirects not working locally | Not supported in `vercel dev` | Test on preview deployments |
| Memory setting ignored | Fluid compute enabled | Set memory in dashboard Settings |
| `includeFiles` ignored in Next.js | Not supported | Use `outputFileTracingIncludes` |
| Glob pattern matches wrong function | Order-dependent | Put specific patterns before general |
| Edge function env var too large | 5KB per-variable limit | Use Edge Config for large values |
| now.json still being used | Deprecated | Migrate to vercel.json before March 31, 2026 |
