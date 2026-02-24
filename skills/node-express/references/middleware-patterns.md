# Middleware Patterns

Sources: Express.js official docs, Node.js best practices

## Execution Order Is the Architecture

Define global middleware before routers and router middleware before handlers.
Use explicit ordering for auth, validation, and error boundaries.

| Phase | Purpose | Example |
| --- | --- | --- |
| request entry | normalize and tag | request ID |
| security | gate access | auth |
| validation | reject bad input | Zod |
| business | route handlers | controllers |
| errors | map to response | error middleware |

```typescript
import express from "express";
import { requestId } from "./middleware/requestId";
import { authRequired } from "./middleware/auth";
import { validateBody } from "./middleware/validate";
import { errorHandler } from "./middleware/error";
import { usersRouter } from "./routes/users.routes";

const app = express();
app.use(express.json());
app.use(requestId());
app.use("/users", authRequired, usersRouter);
app.use(errorHandler);

export { app };
```

## Ordering Patterns Across Routers

Prefer router-level middleware for resource-specific rules.
Use `router.use` for shared concerns across the router.

```typescript
import { Router } from "express";
import { validateParams } from "../middleware/validate";
import { usersController } from "../controllers/users.controller";

const router = Router();

router.use("/users/:id", validateParams);
router.get("/users/:id", usersController.getById);
router.patch("/users/:id", usersController.update);

export { router as usersRouter };
```

## Error Handling Middleware (4-Parameter Signature)

Express treats a middleware with four parameters as an error handler.
Keep it last and return consistent envelopes.

```typescript
import { Request, Response, NextFunction } from "express";
import { AppError } from "../errors/appError";
import { logger } from "../logging/logger";

export function errorHandler(
  err: unknown,
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (res.headersSent) {
    return next(err);
  }

  const appErr = AppError.from(err);
  logger.error({ err: appErr, requestId: req.id }, "request failed");

  res.status(appErr.status).json({
    data: null,
    error: { code: appErr.code, message: appErr.message },
    meta: { requestId: req.id },
  });
}
```

## Async Error Wrapper (No Try/Catch Per Route)

Wrap async handlers and forward errors to `next`.
Keep handlers linear and predictable.

```typescript
import { Request, Response, NextFunction, RequestHandler } from "express";

export const asyncHandler =
  (handler: (req: Request, res: Response, next: NextFunction) => Promise<void>): RequestHandler =>
  (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
```

```typescript
router.post(
  "/users",
  asyncHandler(async (req, res) => {
    const user = await usersService.create(req.body);
    res.status(201).json({ data: user, error: null, meta: {} });
  })
);
```

## Request Validation With Zod Middleware

Validate and coerce input before it reaches handlers.
Reject unknown fields to avoid accidental writes.

```typescript
import { z } from "zod";
import { RequestHandler } from "express";

const createUserSchema = z
  .object({
    email: z.string().email(),
    name: z.string().min(2),
    role: z.enum(["admin", "member"]).default("member"),
  })
  .strict();

export const validateBody = (schema: z.ZodSchema): RequestHandler =>
  (req, res, next) => {
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({
        data: null,
        error: { code: "VALIDATION_ERROR", message: "Invalid request body", details: parsed.error.flatten() },
        meta: {},
      });
    }
    req.body = parsed.data;
    return next();
  };
```

```typescript
router.post("/users", validateBody(createUserSchema), usersController.create);
```

## Authentication Middleware (JWT Verification)

Verify JWT, attach `req.user`, and fail fast on missing or expired tokens.
Keep parsing logic centralized.

```typescript
import { RequestHandler } from "express";
import jwt, { JwtPayload } from "jsonwebtoken";
import { AppError } from "../errors/appError";

interface AuthPayload extends JwtPayload {
  sub: string;
  role: "admin" | "member";
}

export const authRequired: RequestHandler = (req, _res, next) => {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    return next(AppError.unauthorized("Missing bearer token"));
  }

  const token = header.slice("Bearer ".length);
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET as string) as AuthPayload;
    req.user = { id: payload.sub, role: payload.role };
    return next();
  } catch {
    return next(AppError.unauthorized("Invalid token"));
  }
};
```

## Rate Limiting (Token Bucket)

Use an in-memory token bucket for simple deployments.
Prefer Redis-backed buckets for multi-instance.

```typescript
type Bucket = { tokens: number; lastRefillMs: number };
const buckets = new Map<string, Bucket>();

export function tokenBucket({
  capacity,
  refillPerSec,
}: { capacity: number; refillPerSec: number }) {
  return function rateLimit(req: any, res: any, next: any) {
    const key = req.ip;
    const now = Date.now();
    const bucket = buckets.get(key) ?? { tokens: capacity, lastRefillMs: now };
    const elapsed = (now - bucket.lastRefillMs) / 1000;
    const refill = elapsed * refillPerSec;
    bucket.tokens = Math.min(capacity, bucket.tokens + refill);
    bucket.lastRefillMs = now;

    if (bucket.tokens < 1) {
      res.setHeader("Retry-After", "1");
      return res.status(429).json({ data: null, error: { code: "RATE_LIMIT", message: "Too many requests" }, meta: {} });
    }

    bucket.tokens -= 1;
    buckets.set(key, bucket);
    return next();
  };
}
```

```typescript
app.use(tokenBucket({ capacity: 30, refillPerSec: 1 }));
```

## Logging Middleware With Request IDs

Generate a request ID and log structured JSON.
Include latency, status, and route path.

```typescript
import crypto from "crypto";
import { logger } from "../logging/logger";

export const requestId = () => (req: any, _res: any, next: any) => {
  req.id = req.headers["x-request-id"] ?? crypto.randomUUID();
  next();
};

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

## CORS Configuration Patterns

Default to an allowlist and explicit methods.
Avoid wildcard credentials with `*`.

```typescript
import cors from "cors";

const corsOptions = {
  origin: ["https://app.example.com", "https://admin.example.com"],
  methods: ["GET", "POST", "PATCH", "DELETE"],
  credentials: true,
  maxAge: 600,
};

app.use(cors(corsOptions));
```

## Anti-Patterns and Fixes

| Anti-Pattern | Fix |
| --- | --- |
| register error middleware before routes | place error handler last |
| parse JWT inside every handler | use centralized auth middleware |
| validate inside handler | use Zod middleware at the edge |
| log strings without context | use JSON logs with requestId |
| use wildcard CORS with cookies | allowlist origins |
| ignore rate limiting | add token bucket or Redis limiter |

```typescript
// bad: error handler first
app.use(errorHandler);
app.use("/users", usersRouter);

// good: error handler last
app.use("/users", usersRouter);
app.use(errorHandler);
```
