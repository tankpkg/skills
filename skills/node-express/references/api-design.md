# API Design Patterns

Sources: REST API conventions, Express.js patterns

## RESTful Route Naming

Use plural resources and nouns. Avoid verbs in paths.
Prefer nested resources only for tight ownership.

| Resource | Routes | Methods |
| --- | --- | --- |
| users | /users, /users/:id | GET, POST, PATCH, DELETE |
| teams | /teams, /teams/:id | GET, POST, PATCH, DELETE |
| team members | /teams/:id/members | GET, POST |
| sessions | /sessions | POST, DELETE |

```typescript
import { Router } from "express";
const router = Router();

router.get("/users", usersController.list);
router.post("/users", usersController.create);
router.get("/users/:id", usersController.getById);
router.patch("/users/:id", usersController.update);
router.delete("/users/:id", usersController.remove);

export { router };
```

## Response Envelope Pattern

Return a predictable shape for success and error responses.
Keep `data` and `error` mutually exclusive.

```typescript
export type ApiEnvelope<T> = {
  data: T | null;
  error: { code: string; message: string; details?: unknown } | null;
  meta: Record<string, unknown>;
};

export function ok<T>(data: T, meta: Record<string, unknown> = {}): ApiEnvelope<T> {
  return { data, error: null, meta };
}

export function fail(code: string, message: string, details?: unknown): ApiEnvelope<null> {
  return { data: null, error: { code, message, details }, meta: {} };
}
```

## Pagination: Cursor-Based vs Offset

Use cursor pagination for large datasets and stable ordering.
Use offset for small lists and admin tooling.

| Pattern | Pros | Cons |
| --- | --- | --- |
| cursor | stable, fast at scale | needs cursor field |
| offset | easy to implement | slow, duplicates when data shifts |

```typescript
// cursor pagination
const listUsers = async (limit: number, cursor?: string) => {
  const rows = await db.user.findMany({
    take: limit + 1,
    ...(cursor ? { cursor: { id: cursor }, skip: 1 } : {}),
    orderBy: { id: "asc" },
  });
  const nextCursor = rows.length > limit ? rows[limit - 1].id : null;
  return { items: rows.slice(0, limit), nextCursor };
};
```

```typescript
// offset pagination
const listUsersOffset = async (limit: number, offset: number) => {
  const items = await db.user.findMany({ take: limit, skip: offset, orderBy: { createdAt: "desc" } });
  return { items, offset, limit };
};
```

## Filtering and Sorting Conventions

Use `filter[field]=value` for exact match and `sort=field,-field` for order.
Allow only explicit fields to avoid injection.

```typescript
import { z } from "zod";

const listQuerySchema = z.object({
  "filter[email]": z.string().email().optional(),
  "filter[role]": z.enum(["admin", "member"]).optional(),
  sort: z.string().optional(),
});

export function parseListQuery(query: unknown) {
  const parsed = listQuerySchema.parse(query);
  const orderBy = parsed.sort
    ? parsed.sort.split(",").map((field) =>
        field.startsWith("-") ? { [field.slice(1)]: "desc" } : { [field]: "asc" }
      )
    : [{ createdAt: "desc" }];

  return {
    filters: {
      email: parsed["filter[email]"] ?? undefined,
      role: parsed["filter[role]"] ?? undefined,
    },
    orderBy,
  };
}
```

## API Versioning Strategies

Prefer URL versioning for public APIs and header versioning for internal services.
Keep version upgrades additive when possible.

| Strategy | When to Use | Example |
| --- | --- | --- |
| URL path | public stable APIs | /v1/users |
| header | internal services | Accept-Version: 2024-01 |

```typescript
// URL versioning
app.use("/v1", v1Router);
app.use("/v2", v2Router);
```

```typescript
// header versioning
app.use((req, _res, next) => {
  req.apiVersion = req.header("accept-version") ?? "2024-01";
  next();
});
```

## Request and Response DTOs

Define DTOs with Zod and reuse across validation and service boundaries.
Normalize data shape before persistence.

```typescript
import { z } from "zod";

export const createUserDto = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  role: z.enum(["admin", "member"]).default("member"),
});

export type CreateUserDto = z.infer<typeof createUserDto>;
```

```typescript
export const userResponseDto = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string(),
  role: z.enum(["admin", "member"]),
  createdAt: z.string(),
});

export type UserResponseDto = z.infer<typeof userResponseDto>;
```

## Error Response Format (RFC 7807)

Return standardized problem details for errors.
Keep `type` stable and document error codes.

```typescript
type ProblemDetails = {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  errors?: Record<string, string[]>;
};

export function problem(res: any, details: ProblemDetails) {
  return res.status(details.status).json(details);
}
```

```typescript
problem(res, {
  type: "https://example.com/problems/validation",
  title: "Validation error",
  status: 400,
  detail: "Invalid request body",
  errors: { email: ["Invalid email"] },
});
```

## Health Check Endpoint

Expose liveness and readiness for orchestration.
Return service metadata and dependency status.

```typescript
router.get("/health", async (_req, res) => {
  const dbOk = await db.health();
  res.status(dbOk ? 200 : 503).json({
    data: { status: dbOk ? "ok" : "degraded" },
    error: null,
    meta: { db: dbOk ? "ok" : "down" },
  });
});
```

## Bulk Operations

Support batch create, update, and delete for admin and import workflows.
Return individual results per item so partial failures are visible.

```typescript
router.post("/users/bulk", asyncHandler(async (req, res) => {
  const items = z.array(createUserDto).max(100).parse(req.body);
  const results = await Promise.allSettled(
    items.map((item) => usersService.create(item))
  );
  const response = results.map((r, i) =>
    r.status === "fulfilled"
      ? { index: i, success: true, data: r.value }
      : { index: i, success: false, error: r.reason.message }
  );
  const hasFailures = response.some((r) => !r.success);
  res.status(hasFailures ? 207 : 201).json(ok(response));
}));
```

## Idempotency for Unsafe Methods

Accept an `Idempotency-Key` header for POST requests.
Return cached responses for duplicate keys within a TTL.

```typescript
const idempotencyCache = new Map<string, { status: number; body: unknown }>();

export function idempotent() {
  return (req: Request, res: Response, next: NextFunction) => {
    const key = req.header("idempotency-key");
    if (!key || req.method !== "POST") return next();

    const cached = idempotencyCache.get(key);
    if (cached) return res.status(cached.status).json(cached.body);

    const originalJson = res.json.bind(res);
    res.json = (body: unknown) => {
      idempotencyCache.set(key, { status: res.statusCode, body });
      setTimeout(() => idempotencyCache.delete(key), 24 * 60 * 60 * 1000);
      return originalJson(body);
    };
    next();
  };
}
```

## Anti-Patterns and Corrections

| Anti-Pattern | Correction |
| --- | --- |
| verbs in routes | use noun resources |
| ad hoc error shapes | use envelope or RFC 7807 |
| pagination without stable order | enforce orderBy |
| unbounded filters | whitelist filter fields |
| mixed versioning styles | pick one strategy |
| missing health checks | add /health |
| no idempotency on POST | accept Idempotency-Key |
| unlimited bulk size | enforce max batch size |

```typescript
// bad
router.post("/users/create", usersController.create);

// good
router.post("/users", usersController.create);
```
