# Type Patterns

Sources: TypeScript Handbook, Effective TypeScript (Vanderkam)

## Discriminated Unions for State Machines
Use a literal tag to make state transitions explicit and safe.
Keep payload shapes tied to the tag so narrowing is automatic.

```ts
type Loading = { tag: "loading" };
type ErrorState = { tag: "error"; message: string; code?: number };
type Success = { tag: "success"; data: string[] };
type RequestState = Loading | ErrorState | Success;

const render = (state: RequestState) => {
  switch (state.tag) {
    case "loading":
      return "Loading...";
    case "error":
      return `Error: ${state.message}`;
    case "success":
      return state.data.join(", ");
  }
};
```

```ts
const transition = (state: RequestState, event: "retry" | "reset"): RequestState => {
  if (state.tag === "error" && event === "retry") return { tag: "loading" };
  if (event === "reset") return { tag: "loading" };
  return state;
};
```

## Branded Types for Type-Safe IDs
Branded strings prevent mixing IDs that share a primitive type.
Use constructor helpers at boundaries to keep the brand private.

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;

const toUserId = (raw: string): UserId => raw as UserId;
const toOrderId = (raw: string): OrderId => raw as OrderId;

const getUser = (id: UserId) => id;
// getUser(toOrderId("ord_1")); // type error
```

```ts
const parseUserId = (raw: string): UserId | null =>
  raw.startsWith("usr_") ? (raw as UserId) : null;
```

## Exhaustive Checking with `never`
Enforce coverage of every union case and get compiler help on additions.
Use a `never` assignment in the default branch.

```ts
type Event =
  | { type: "created"; id: string }
  | { type: "deleted"; id: string }
  | { type: "archived"; id: string };

const handle = (e: Event) => {
  switch (e.type) {
    case "created":
      return `c:${e.id}`;
    case "deleted":
      return `d:${e.id}`;
    case "archived":
      return `a:${e.id}`;
    default: {
      const _exhaustive: never = e;
      return _exhaustive;
    }
  }
};
```

## Template Literal Types for String Patterns
Model structured strings for events, CSS units, and routes.
Prefer a small union for base parts, then build with templates.

```ts
type EventName = "user" | "order" | "billing";
type EventAction = "created" | "updated" | "deleted";
type EventKey = `${EventName}:${EventAction}`;

const emit = (name: EventKey) => name;
emit("user:created");
```

```ts
type CssUnit = "px" | "rem" | "%";
type CssSize = `${number}${CssUnit}`;
const padding: CssSize = "12px";
```

```ts
type ApiBase = "/users" | "/orders";
type ApiRoute = `${ApiBase}/${string}` | ApiBase;
const route: ApiRoute = "/users/123";
```

## Conditional Types with `infer`
Extract inner types and build higher-order helpers.
Keep conditional helpers short and name them for reuse.

```ts
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type UnwrapArray<T> = T extends (infer U)[] ? U : T;

type A = UnwrapPromise<Promise<number>>; // number
type B = UnwrapArray<string[]>; // string
```

```ts
type FnReturn<T> = T extends (...args: any[]) => infer R ? R : never;
type R = FnReturn<(x: number) => { ok: true }>; // { ok: true }
```

## Mapped Types with Key Remapping
Remap keys to generate new object shapes and filter keys.
Use `as` in mapped types to rename or drop properties.

```ts
type PrefixKeys<T, P extends string> = {
  [K in keyof T as `${P}${string & K}`]: T[K]
};

type Input = { id: string; count: number };
type Prefixed = PrefixKeys<Input, "api_">;
// { api_id: string; api_count: number }
```

```ts
type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K]
};

type OnlyNumbers = PickByValue<{ a: number; b: string; c: number }, number>;
// { a: number; c: number }
```

## `satisfies` vs `as const` vs Type Annotation
Use `satisfies` to check shape while preserving inference.
Use `as const` to freeze literals but keep exact values.
Use annotation when you want to force a public contract.

```ts
type Role = "admin" | "member";
const permissions = {
  admin: ["read", "write"],
  member: ["read"]
} satisfies Record<Role, string[]>;

type Permission = typeof permissions[Role][number];
```

```ts
const routes = { users: "/users", orders: "/orders" } as const;
type Route = typeof routes[keyof typeof routes];
```

```ts
type RouteMap = Record<string, `/${string}`>;
const r: RouteMap = { users: "/users" };
```

## Index Signatures vs Record vs Map
| Choice | When to use | Notes |
| --- | --- | --- |
| `index signature` | Open set of keys, minimal constraints | Keys are `string` or `number` only |
| `Record<K, V>` | Finite key union, compile-time coverage | Gives exact key set |
| `Map<K, V>` | Large dynamic set or non-string keys | Runtime features like size, order |

```ts
type Status = "open" | "closed";
const byStatus: Record<Status, number> = { open: 1, closed: 2 };
```

```ts
type Bag = { [k: string]: number };
const bag: Bag = { apples: 2 };
```

```ts
const map = new Map<string, number>();
map.set("apples", 2);
```

## Type Predicates and Assertion Functions
Use predicates to narrow from `unknown` or unions.
Use assertion functions to stop execution on invalid data.

```ts
type User = { id: string; email: string };
const isUser = (v: unknown): v is User => {
  if (!v || typeof v !== "object") return false;
  const u = v as Record<string, unknown>;
  return typeof u.id === "string" && typeof u.email === "string";
};
```

```ts
const assertUser = (v: unknown): asserts v is User => {
  if (!isUser(v)) throw new Error("Invalid user");
};
```

## Narrowing Helpers for Unknown Inputs
Model safe parsing by returning a result object instead of throwing.
This keeps callers in control and makes failure explicit.

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
const ok = <T>(value: T): Result<T> => ({ ok: true, value });
const err = (error: string): Result<never> => ({ ok: false, error });

const parseNumber = (v: unknown): Result<number> =>
  typeof v === "number" ? ok(v) : err("not a number");

const n = parseNumber(3);
if (n.ok) n.value.toFixed(2);
```

## Anti-Patterns and Safer Alternatives
| Anti-pattern | Risk | Alternative |
| --- | --- | --- |
| `as any` at boundaries | Skips validation | Use `unknown` + predicate |
| `@ts-ignore` | Hides real issues | Use `@ts-expect-error` with reason |
| Unchecked `as` assertions | Creates false safety | Guard then narrow |
| Untagged unions | Incomplete narrowing | Add a discriminant |
| Enum for string literals | Extra runtime | `as const` object + union |
| Broad `string` for IDs | Mixed identifiers | Branded types |
| Deep conditional types | Hard to debug | Named helpers + tests |
| Index signature for finite keys | Missed coverage | `Record` with union keys |

```ts
const parse = (v: unknown): string => {
  if (typeof v !== "string") throw new Error("Expected string");
  return v;
};
```

```ts
const cfg = { retries: 3, baseUrl: "/api" } satisfies { retries: number; baseUrl: `/${string}` };
```
