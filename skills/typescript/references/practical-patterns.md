# Practical Patterns

Sources: TypeScript Handbook, production TypeScript codebases

## Builder Pattern with Type-Safe Chaining
Use generic state to enforce required fields before `build`.
The builder state narrows as methods are chained.

```ts
type BuilderState = { url?: string; method?: "GET" | "POST"; body?: unknown };
class RequestBuilder<S extends BuilderState> {
  constructor(private readonly state: S) {}
  url(url: string) { return new RequestBuilder({ ...this.state, url }); }
  method(method: "GET" | "POST") { return new RequestBuilder({ ...this.state, method }); }
  body(body: unknown) { return new RequestBuilder({ ...this.state, body }); }
  build(this: RequestBuilder<S & { url: string; method: "GET" | "POST" }>) {
    return this.state;
  }
}
```

```ts
const req = new RequestBuilder({}).url("/api").method("GET").build();
```

## Result/Either for Error Handling
Replace exceptions with explicit success/failure flows.
Use helpers to compose results.

```ts
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

const map = <T, U, E>(r: Result<T, E>, f: (v: T) => U): Result<U, E> =>
  r.ok ? ok(f(r.value)) : r;
```

```ts
const parseJson = (s: string): Result<unknown, string> => {
  try { return ok(JSON.parse(s)); } catch { return err("invalid json"); }
};
```

## Dependency Injection without a Framework
Use constructors and typed factory functions.
Keep interfaces small and pass dependencies explicitly.

```ts
type Clock = { now: () => Date };
type Logger = { info: (m: string) => void };

class SessionService {
  constructor(private clock: Clock, private logger: Logger) {}
  open() {
    this.logger.info(`opened at ${this.clock.now().toISOString()}`);
  }
}
```

```ts
const makeSessionService = (deps: { clock: Clock; logger: Logger }) =>
  new SessionService(deps.clock, deps.logger);
```

## Type-Safe Event Emitter
Use a map of event names to payload types.
Expose strongly typed `on` and `emit` methods.

```ts
type Events = {
  userCreated: { id: string; email: string };
  orderPaid: { id: string; total: number };
};

class Emitter<E extends Record<string, unknown>> {
  private listeners: { [K in keyof E]?: Array<(p: E[K]) => void> } = {};
  on<K extends keyof E>(event: K, cb: (payload: E[K]) => void) {
    (this.listeners[event] ||= []).push(cb);
  }
  emit<K extends keyof E>(event: K, payload: E[K]) {
    this.listeners[event]?.forEach(fn => fn(payload));
  }
}
```

```ts
const bus = new Emitter<Events>();
bus.on("userCreated", p => p.email);
bus.emit("orderPaid", { id: "o1", total: 42 });
```

## Generic Repository Pattern
Model persistence with generic constraints and type-safe IDs.
Keep the interface consistent across entities.

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };
type Id<T extends string> = Brand<string, T>;

interface Repository<T, TId extends string> {
  get(id: Id<TId>): Promise<T | null>;
  save(entity: T): Promise<void>;
  delete(id: Id<TId>): Promise<void>;
}
```

```ts
type User = { id: Id<"UserId">; email: string };
type UserRepo = Repository<User, "UserId">;
```

## Zod Schema to TypeScript Inference
Let runtime validation define your static type.
Use `z.infer` to avoid duplicating types.

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().startsWith("usr_"),
  email: z.string().email()
});

type User = z.infer<typeof UserSchema>;
```

```ts
const parseUser = (v: unknown) => UserSchema.safeParse(v);
```

## Module Augmentation
Extend third-party types when you need project-specific fields.
Keep augmentations in a dedicated `types/` folder.

```ts
declare module "express-serve-static-core" {
  interface Request {
    userId?: string;
  }
}
```

```ts
const handler = (req: import("express").Request) => req.userId;
```

## Declaration Merging Patterns
Use interface merging for configuration and global augmentation.
Prefer `declare global` to add types to the global scope.

```ts
interface FeatureFlags {
  betaCheckout?: boolean;
}

interface FeatureFlags {
  newNav?: boolean;
}
```

```ts
declare global {
  interface Window {
    __appVersion?: string;
  }
}
```

## Overload Signatures vs Union Parameters
| Use | When | Example |
| --- | --- | --- |
| Overloads | Return type depends on parameter | `format(Date): string` |
| Union params | Same return type, multiple inputs | `parse(string | Buffer)` |

```ts
function format(input: Date): string;
function format(input: number): string;
function format(input: Date | number) {
  return typeof input === "number" ? new Date(input).toISOString() : input.toISOString();
}
```

```ts
const parse = (input: string | ArrayBuffer): string =>
  typeof input === "string" ? input : new TextDecoder().decode(input);
```

## `const` Assertions and Object Freeze
Use `as const` to lock literals; freeze to enforce runtime immutability.
Treat frozen objects as configuration sources.

```ts
const config = { retries: 3, mode: "safe" } as const;
type Mode = typeof config.mode;
```

```ts
const frozen = Object.freeze({ retry: 2, baseUrl: "/api" });
type Frozen = typeof frozen;
```

## Typed HTTP Client from Route Map
Use a central route map and derive request/response types.
Keep client thin; types guard usage.

```ts
type Routes = {
  "/users/:id": { params: { id: string }; response: { id: string; email: string } };
  "/orders/:id": { params: { id: string }; response: { id: string; total: number } };
};

type RouteKey = keyof Routes;
const request = async <K extends RouteKey>(route: K, params: Routes[K]["params"]): Promise<Routes[K]["response"]> => {
  const url = route.replace(":id", params.id);
  const res = await fetch(url);
  return res.json();
};
```

## Adapter Pattern for Legacy Modules
Wrap untyped modules at the boundary and expose typed functions.
Use `unknown` inputs and narrow once.

```ts
type LegacyUser = { id: string; email: string };
const legacyFetch = async (id: string): Promise<unknown> => ({ id, email: "a@b.com" });
const isLegacyUser = (v: unknown): v is LegacyUser => {
  if (!v || typeof v !== "object") return false;
  const u = v as Record<string, unknown>;
  return typeof u.id === "string" && typeof u.email === "string";
};
const fetchUser = async (id: string): Promise<LegacyUser> => {
  const v = await legacyFetch(id);
  if (!isLegacyUser(v)) throw new Error("Invalid user");
  return v;
};
```

## Anti-Patterns and Safer Alternatives
| Anti-pattern | Risk | Alternative |
| --- | --- | --- |
| Throwing in domain flow | Hard to compose | Return `Result` |
| Global service locator | Hidden dependencies | Constructor injection |
| Untyped event names | Runtime typos | Typed event map |
| Repository without IDs | Entity confusion | Branded IDs |
| Duplicated schema types | Drift | Infer from schema |
| Ad-hoc module patching | Hard to track | Central augmentations |
| Overloads for same return type | Noise | Use union params |
| `as const` on large data | Poor ergonomics | `satisfies` + slices |

```ts
type ServiceDeps = { clock: Clock; logger: Logger };
const make = (deps: ServiceDeps) => new SessionService(deps.clock, deps.logger);
```
