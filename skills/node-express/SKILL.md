---
name: "@tank/node-express"
description: "Production-grade Node.js/Express patterns for API servers. Triggers: node, node.js, express, express.js, api server, rest api, backend, middleware, route handler, router, endpoint, request validation, zod, jwt, session auth, oauth, rate limiting, error handling, logging, graceful shutdown, prisma, drizzle, postgres, mysql, mongodb, http server, health check."
---

# @tank/node-express

Purpose: deliver actionable patterns for production Express APIs with predictable middleware, validation, auth, and operations.

## Core Philosophy

1) Fail loud, fail fast: reject invalid input at the edge, do not guess.
2) Middleware is the architecture: cross-cutting behavior lives in ordered middleware, not in handlers.
3) Types at the boundary: validate external data with schemas, then trust internal types.
4) Observable by default: logs, request IDs, and errors are first-class outputs.
5) Production-friendly defaults: graceful shutdown and safe timeouts are non-optional.

## Project Structure

```text
src/
  app.ts
  server.ts
  routes/
    index.ts
    users.routes.ts
  middleware/
    auth.ts
    error.ts
    rateLimit.ts
    requestId.ts
    validate.ts
  controllers/
    users.controller.ts
  services/
    users.service.ts
  db/
    client.ts
  schemas/
    users.schema.ts
  config/
    env.ts
  logging/
    logger.ts
  health/
    health.routes.ts
test/
  api/
    users.test.ts
```

## Operating Workflow

1. Boot `app.ts` with middleware order, then mount routes.
2. Keep handlers thin: parse, call service, return response.
3. Push domain logic into `services/` with explicit inputs/outputs.
4. Centralize errors in `middleware/error.ts`.
5. Export `server.ts` to control listening and shutdown.

## Quick Decision Trees

### Middleware vs Route Handler

| If the concern is... | Use | Example |
| --- | --- | --- |
| cross-cutting across routes | middleware | request IDs, auth |
| per-resource behavior | handler | create user |
| transform input/output | middleware | validation, response envelopes |
| business logic | handler/service | billing, scheduling |

### Error Handling Strategy

| Situation | Strategy | Why |
| --- | --- | --- |
| expected client errors | throw typed error + map in error middleware | single mapping point |
| async handler failures | async wrapper + error middleware | avoid try/catch in every route |
| downstream dependency failures | translate to 503/504 with retry metadata | predictable ops |
| unknown exceptions | log with request ID, return 500 | fail safe |

### Authentication Method Selection

| Need | Use | Notes |
| --- | --- | --- |
| stateless API, mobile clients | JWT | rotate keys, short exp |
| server-rendered web app | session cookie | httpOnly + CSRF |
| third-party login | OAuth | exchange for session/JWT |

## Capability Map

- Middleware ordering, error boundaries, and async wrappers.
- Request validation with Zod at the edge.
- Auth strategies: JWT, session, OAuth handoff.
- API design: routes, envelopes, pagination, DTOs.
- Production ops: shutdown, logging, health checks, Docker.

## Input Expectations

- Provide existing routes or controllers if they must be preserved.
- State persistence layer (Prisma, Drizzle, raw SQL) and DB type.
- Identify auth mode and token/session storage.
- Share operational constraints (K8s, PM2, Docker).

## Output Format

- Provide middleware order and placement guidance.
- Provide code snippets in TypeScript by default.
- Return explicit error and response formats.
- Note tradeoffs and safe defaults.

## Activation Triggers

- node
- node.js
- express
- express.js
- api server
- rest api
- backend
- middleware
- route handler
- router
- endpoint
- request validation
- zod
- jwt
- session auth
- oauth
- rate limiting
- error handling
- graceful shutdown
- structured logging

## Non-Goals

- Do not design UI or front-end components.
- Do not prescribe ORM choice unless asked.
- Do not embed secrets or credentials.
- Do not skip validation in favor of speed.

## Common Tasks

- Add request validation middleware with Zod schemas.
- Build error mapping for typed errors and unknowns.
- Add JWT verification and role gating.
- Add rate limiting and request ID logging.
- Set up graceful shutdown with connection draining.
- Define response envelope and pagination.

## Operational Standards

- Enforce request validation with Zod at every entry route.
- Standardize error envelope and problem details.
- Add correlation IDs, log latency, and response status.
- Use graceful shutdown with connection draining.
- Prefer cursor pagination for large collections.

## Anti-Patterns

| Don't | Do Instead |
| --- | --- |
| put auth logic inside handlers | centralized auth middleware |
| swallow errors with empty catch | throw typed errors, map centrally |
| accept unknown request bodies | validate with Zod and strip unknowns |
| build responses ad hoc | use `{ data, error, meta }` envelope |
| use global mutable singletons | inject dependencies per app instance |
| skip shutdown handlers | implement SIGTERM/SIGINT with drain |
| log plain strings | structured JSON with requestId |

## Reference Files

- `skills/node-express/references/middleware-patterns.md`
- `skills/node-express/references/api-design.md`
- `skills/node-express/references/production-patterns.md`
