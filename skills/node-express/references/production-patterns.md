# Production Patterns

Sources: Node.js official docs, 12-Factor App methodology

## Graceful Shutdown With Connection Draining

Capture SIGTERM and SIGINT, stop accepting new requests, and drain existing connections.
Close database pools and background workers before exiting.

```typescript
import http from "http";
import { app } from "./app";
import { logger } from "./logging/logger";
import { db } from "./db/client";

const server = http.createServer(app);
const connections = new Set<http.Socket>();

server.on("connection", (socket) => {
  connections.add(socket);
  socket.on("close", () => connections.delete(socket));
});

function shutdown(signal: string) {
  logger.info({ signal }, "shutdown start");
  server.close(async () => {
    await db.disconnect();
    logger.info("shutdown complete");
    process.exit(0);
  });

  setTimeout(() => {
    logger.warn("forcing shutdown");
    for (const socket of connections) socket.destroy();
    process.exit(1);
  }, 10_000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

server.listen(process.env.PORT ?? 3000);
```

## Environment Configuration and Validation

Load environment variables once and validate with Zod.
Fail fast if required variables are missing.

```typescript
import "dotenv/config";
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});

export const env = envSchema.parse(process.env);
```

## Structured Logging With Correlation IDs

Prefer JSON logs and include request IDs.
Use a single logger instance with bindings.

```typescript
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  base: { service: "api" },
  redact: ["req.headers.authorization"],
});
```

```typescript
export const requestLogger = () => (req: any, res: any, next: any) => {
  const start = Date.now();
  res.on("finish", () => {
    logger.info({
      requestId: req.id,
      method: req.method,
      path: req.originalUrl,
      status: res.statusCode,
      latencyMs: Date.now() - start,
    });
  });
  next();
};
```

## Database Connection Management

Use connection pooling and retry with bounded backoff.
Surface connection health for readiness checks.

```typescript
import { PrismaClient } from "@prisma/client";

export const db = new PrismaClient({
  log: ["warn", "error"],
});

export async function connectWithRetry(attempts = 5) {
  for (let i = 0; i < attempts; i += 1) {
    try {
      await db.$connect();
      return;
    } catch (err) {
      const delay = Math.min(1000 * 2 ** i, 8000);
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw new Error("DB connection failed after retries");
}
```

## Process Management and Scaling

Use clustering for CPU-bound workloads, but prefer horizontal scaling in containers.
PM2 is useful for single-host deployments; keep configs explicit.

```typescript
import cluster from "cluster";
import os from "os";

if (cluster.isPrimary) {
  const workers = process.env.WORKERS ? Number(process.env.WORKERS) : os.cpus().length;
  for (let i = 0; i < workers; i += 1) cluster.fork();
  cluster.on("exit", () => cluster.fork());
} else {
  server.listen(process.env.PORT ?? 3000);
}
```

## Security Hardening Checklist

Apply security middleware and enforce sane defaults.
Document what is enabled and why.

| Control | Purpose | Default |
| --- | --- | --- |
| helmet | security headers | enabled |
| CORS allowlist | limit origins | required |
| rate limiting | protect endpoints | required |
| input sanitization | reject unknown fields | required |

```typescript
import helmet from "helmet";
import cors from "cors";
import { tokenBucket } from "./middleware/rateLimit";

app.use(helmet());
app.use(cors({ origin: ["https://app.example.com"], credentials: true }));
app.use(tokenBucket({ capacity: 60, refillPerSec: 1 }));
```

## Dependency Injection Without a Framework

Build an app factory that injects dependencies.
Keep tests fast by swapping fakes.

```typescript
type Deps = { usersService: UsersService; logger: typeof logger };

export function buildApp(deps: Deps) {
  const app = express();
  app.get("/users/:id", asyncHandler(async (req, res) => {
    const user = await deps.usersService.getById(req.params.id);
    res.json(ok(user));
  }));
  return app;
}
```

## Docker-Optimized Image

Use multi-stage builds and non-root user.
Copy only production dependencies and built output.

```typescript
// Dockerfile
// syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Health Checks and Readiness Probes

Separate liveness from readiness if dependencies can be down.
Fail readiness on DB or critical services.

```typescript
app.get("/health/live", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

app.get("/health/ready", async (_req, res) => {
  const dbOk = await db.health();
  res.status(dbOk ? 200 : 503).json({ status: dbOk ? "ok" : "degraded" });
});
```

## Uncaught Exception and Rejection Handling

Catch unhandled errors to log context before crashing.
Always exit after uncaught exceptions — do not swallow.
Let the orchestrator restart the process.

```typescript
process.on("uncaughtException", (err) => {
  logger.fatal({ err }, "uncaught exception — shutting down");
  shutdown("uncaughtException");
});

process.on("unhandledRejection", (reason) => {
  logger.error({ reason }, "unhandled rejection");
  // In production, treat as fatal:
  shutdown("unhandledRejection");
});
```

## Request Timeout Middleware

Enforce maximum request duration to prevent hung connections.
Return 503 so load balancers route to healthy instances.

```typescript
export function requestTimeout(ms: number) {
  return (req: Request, res: Response, next: NextFunction) => {
    const timer = setTimeout(() => {
      if (!res.headersSent) {
        res.status(503).json({ error: { code: "TIMEOUT", message: "Request timed out" } });
      }
    }, ms);
    res.on("finish", () => clearTimeout(timer));
    next();
  };
}

app.use(requestTimeout(30_000));
```

## Anti-Patterns and Fixes

| Anti-Pattern | Fix |
| --- | --- |
| ignore SIGTERM | implement graceful shutdown |
| ship without env validation | parse env with Zod |
| log to console without context | use JSON logger |
| unbounded DB retries | use capped backoff |
| build images with dev deps | multi-stage build |
| skip readiness checks | add /health/ready |
| swallow uncaught exceptions | log and exit |
| no request timeouts | add timeout middleware |

```typescript
// bad: direct process.exit in handlers
process.on("SIGTERM", () => process.exit(0));

// good: drain and close
process.on("SIGTERM", () => shutdown("SIGTERM"));
```
