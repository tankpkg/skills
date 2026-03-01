# Serverless and Edge Functions

Sources: Vercel CLI docs (2026), Vercel functions documentation

Covers: Serverless functions, edge functions, middleware, cold start mitigation,
streaming, Build Output API, storage, and advanced platform features.

## Serverless vs Edge Decision

| Need | Use Serverless | Use Edge |
|------|---------------|----------|
| Full Node.js APIs (fs, child_process) | Yes | No |
| Heavy compute (>30s) | Yes (up to 800s) | No (30s max) |
| Database queries, external APIs | Yes | Possible (Web fetch only) |
| Auth gating, redirects | No | Yes (middleware) |
| Geo-routing, A/B testing | No | Yes |
| Ultra-low latency (<10ms) | No (~250ms cold start) | Yes (~1ms cold start) |
| Global distribution | Regional | Automatic (200+ locations) |
| Native modules, C++ addons | Yes | No |
| Python, Go, Ruby runtime | Yes | No |

## Serverless Functions

### File-Based Routing

Files in `api/` become serverless endpoints. Next.js uses `app/api/`.

```
api/
├── hello.ts          # /api/hello
├── users/
│   └── [id].ts       # /api/users/:id
└── data.ts           # /api/data
```

### Supported Runtimes

| Runtime | Identifier | Notes |
|---------|-----------|-------|
| Node.js 20 | `nodejs20.x` | Default, full API access |
| Node.js 18 | `nodejs18.x` | Supported |
| Python 3.9/3.11 | `python3.9`, `python3.11` | Community runtime |
| Go | `go1.x` | Community runtime |
| Ruby 3.2 | `ruby3.2` | Community runtime |
| PHP | `vercel-php@0.5.2` | Community runtime |
| Bun | Set `bunVersion: "1.x"` | Uses Bun instead of Node.js |

### Runtime Configuration

```typescript
// Next.js App Router
export const runtime = 'nodejs';    // or 'edge'
export const maxDuration = 60;

export async function GET(request: Request) {
  return new Response('Hello');
}
```

### Memory and Duration Limits

**With Fluid Compute** (default since April 2025):

| Plan | Memory | Default Duration | Max Duration |
|------|--------|-----------------|-------------|
| Hobby | 2 GB / 1 vCPU (fixed) | 300s | 300s |
| Pro | Standard: 2 GB / 1 vCPU | 300s | 800s |
| Pro | Performance: 4 GB / 2 vCPU | 300s | 800s |
| Enterprise | Custom | 300s | 800s |

Memory is configured in the dashboard (Settings -> Functions), not in vercel.json.

**Without Fluid Compute** (legacy):

| Plan | Memory Range | Default Duration | Max Duration |
|------|-------------|-----------------|-------------|
| Hobby | 1024 MB | 10s | 60s |
| Pro | 128-3009 MB | 15s | 300s |
| Enterprise | 128-3009 MB | 15s | 900s |

### Cold Start Mitigation

1. **Use Edge runtime** for lightweight operations (auth, routing). ~1ms vs ~250ms.
2. **Minimize dependencies**. Import only what you need:
   ```typescript
   // Bad: imports entire lodash
   import _ from 'lodash';
   // Good: imports single function
   import debounce from 'lodash/debounce';
   ```
3. **Top-level initialization**. Connections and clients persist across invocations:
   ```typescript
   import { db } from './db';  // Initialized once, reused
   export async function GET() {
     return Response.json(await db.query('SELECT 1'));
   }
   ```
4. **Connection pooling** for databases. Use serverless-compatible pools.
5. **Lazy load** heavy dependencies only when needed.

## Edge Functions

### Characteristics

- V8 isolates (not Node.js). ~1ms cold start.
- Global deployment (200+ edge locations).
- Max execution: 30 seconds.
- Max compressed size: 1 MB. Max response: 4 MB.
- Auto-scales to 30,000 (Hobby/Pro) or 100,000+ (Enterprise).

### Available APIs

**Yes**: `fetch`, `Request`, `Response`, `Headers`, `URL`, `URLSearchParams`,
`ReadableStream`, `WritableStream`, `TextEncoder`, `TextDecoder`,
`crypto.subtle`, `Blob`, `File`, `FormData`, `setTimeout`, `setInterval`.

**No**: `fs`, `path`, `child_process`, `net`, `dgram`, `os`, `eval`,
`new Function()`, native modules, synchronous crypto.

### Edge Function Example

```typescript
export const config = { runtime: 'edge' };

export default async function handler(request: Request) {
  const country = request.headers.get('x-vercel-ip-country');
  return new Response(`Hello from ${country}`, {
    headers: { 'content-type': 'text/plain' },
  });
}
```

## Middleware

Runs on the Edge runtime before requests reach functions or pages.
Place `middleware.ts` at the project root.

```typescript
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  if (!request.cookies.get('auth')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*'],
};
```

### Geolocation

```typescript
export function middleware(request: NextRequest) {
  const { country, city, region, latitude, longitude } = request.geo || {};
  const ip = request.ip;
  // Route based on location
}
```

### A/B Testing

```typescript
export function middleware(request: NextRequest) {
  const variant = Math.random() < 0.5 ? 'A' : 'B';
  const response = NextResponse.next();
  response.cookies.set('ab-variant', variant);
  if (variant === 'A') {
    return NextResponse.rewrite(new URL('/home-v2', request.url));
  }
  return response;
}
```

## Edge Config

Global low-latency data store. Reads in <1ms. Use for runtime configuration
that changes without redeployment.

```typescript
import { get } from '@vercel/edge-config';

export async function middleware(request: NextRequest) {
  const maintenance = await get('maintenance_mode');
  if (maintenance) {
    return new Response('Site under maintenance', { status: 503 });
  }
  return NextResponse.next();
}
```

Use cases: feature flags, maintenance mode, A/B test rules, dynamic redirects.

## Streaming Responses

```typescript
export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`data: chunk ${i}\n\n`));
        await new Promise(r => setTimeout(r, 100));
      }
      controller.close();
    }
  });
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
  });
}
```

## Build Output API

Framework adapters emit this directory structure for deployment:

```
.vercel/output/
├── config.json              # Routes, images, crons, overrides
├── static/                  # CDN-served files
│   ├── index.html
│   └── assets/
└── functions/               # Serverless and edge functions
    └── api/hello.func/
        ├── .vc-config.json  # Runtime, handler, memory, duration
        └── index.js
```

`.vc-config.json` example:
```json
{
  "runtime": "nodejs20.x",
  "handler": "index.js",
  "launcherType": "Nodejs",
  "maxDuration": 60
}
```

`vercel build` generates this structure. `vercel deploy --prebuilt` uploads it.

## Storage Integrations

| Service | Type | Setup |
|---------|------|-------|
| Vercel Blob | Object storage | `vercel integration add vercel-blob` |
| Upstash Redis | Key-value store | `vercel integration add upstash-redis` |
| Neon | PostgreSQL | `vercel integration add neon` |
| Edge Config | Low-latency config | `vercel edge-config create` |

```bash
# CLI blob operations
vercel blob put ./image.png --pathname images/logo.png
vercel blob list --prefix images/
vercel blob del images/old.png
```

Integrations auto-add environment variables (connection strings, tokens).

## Observability

**Speed Insights**: Real user performance metrics.
```tsx
import { SpeedInsights } from '@vercel/speed-insights/next';
// Add <SpeedInsights /> to layout
```

**Web Analytics**: Privacy-friendly page view tracking.
```tsx
import { Analytics } from '@vercel/analytics/react';
// Add <Analytics /> to layout
```

**Custom Events**:
```typescript
import { track } from '@vercel/analytics';
track('purchase', { product: 'Premium', value: 99 });
```

## Firewall and Security

- **DDoS protection**: Automatic for all plans. No configuration needed.
- **WAF custom rules**: Pro/Enterprise. Configure in dashboard Firewall settings.
- **IP blocking**: Hobby: 10, Pro: 25, Enterprise: 100 rules.
- **Attack Challenge Mode**: CAPTCHA for all traffic during active attacks.
- **Skew Protection**: Prevents version mismatches during deployments. Automatic in Next.js 14+.
- **Deployment Protection Bypass**: Use `x-vercel-protection-bypass` header with
  `VERCEL_AUTOMATION_BYPASS_SECRET` env var for CI/CD access to protected deploys.

## Cron Jobs

Schedule functions to run periodically. Configure in vercel.json `crons` array.

| Plan | Min Interval | Precision | Max Jobs |
|------|-------------|-----------|----------|
| Hobby | Daily | +/- 59 minutes | 100 |
| Pro | Per-minute | Per-minute | 100 |
| Enterprise | Per-minute | Per-minute | 100 |

Secure cron endpoints with `CRON_SECRET` env var:

```typescript
export async function GET(request: Request) {
  if (request.headers.get('authorization') !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }
  await performTask();
  return Response.json({ success: true });
}
```

## Feature Flags

```bash
npm install @vercel/flags
```

```typescript
import { flag } from '@vercel/flags/next';

export const showNewUI = flag({
  key: 'show-new-ui',
  decide: () => false,
  description: 'Enable redesigned dashboard',
});

// In component
const enabled = await showNewUI();
```

$30 per 1M flag requests. Configure targeting rules in Vercel dashboard.
