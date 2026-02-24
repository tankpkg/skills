---
name: "@tank/typescript"
description: "Advanced TypeScript patterns for type-safe applications. Triggers: typescript, TS, type, interface, generic, union, discriminated union, branded type, utility type, conditional type, mapped type, template literal, infer, satisfies, as const, tsconfig, strict mode, type guard, type narrowing, type-safe."
---
# TypeScript

## When to Use
- Design APIs that enforce invariants at compile time, not in runtime comments.
- Model complex state machines, data flows, or protocol responses.
- Refactor JavaScript into TypeScript with minimal runtime change.
- Convert runtime validation into inferred types (schema-first).

## Core Philosophy
- Make illegal states unrepresentable.
- Narrow, don't assert.
- Prefer type inference with guardrails.

## Workflow
1. Identify domain invariants and impossible states.
2. Choose the smallest surface area for public types.
3. Model states with discriminated unions and explicit tags.
4. Add guards (type predicates or assertion functions) at boundaries.
5. Let inference flow through helpers; use `satisfies` to lock shape.
6. Add exhaustive checks to every switch on tagged unions.
7. Encode runtime validation with schema libraries or hand-rolled guards.

## Type Selection Decision Tree
- Need declaration merging or class implementation contracts? Use `interface`.
- Need unions, intersections, or mapped/conditional types? Use `type`.
- Need runtime values with stable string keys? Prefer const objects.
- Need closed set of values consumed at runtime? Use const object + union.
- Need bitwise or numeric enums interop? Use `enum` only if required.
- Need a flexible "dictionary" and stable key type? Use `Record`.
- Need literal inference from object values? Use `as const`.

```ts
const status = { idle: "idle", loading: "loading" } as const;
type Status = typeof status[keyof typeof status];
interface FetchState { status: Status }
```

## Utility Types Quick Reference
| Utility | Purpose | Example |
| --- | --- | --- |
| `Pick<T, K>` | Select keys | `Pick<User, "id" | "email">` |
| `Omit<T, K>` | Drop keys | `Omit<User, "password">` |
| `Partial<T>` | Optional props | `Partial<Config>` |
| `Required<T>` | All required | `Required<Config>` |
| `Record<K, V>` | Map keys to type | `Record<Role, Permission[]>` |
| `Exclude<T, U>` | Remove union members | `Exclude<Status, "idle">` |
| `Extract<T, U>` | Keep union members | `Extract<Event, { type: "click" }>` |
| `ReturnType<F>` | Function return | `ReturnType<typeof makeUser>` |
| `Parameters<F>` | Function params tuple | `Parameters<typeof fetcher>` |
| `Awaited<T>` | Promise unwrapping | `Awaited<ReturnType<typeof api>>` |

## Strict Config Recommendations
| Flag | Why it matters | Typical impact |
| --- | --- | --- |
| `strict` | Enables the full safety suite | Forces explicit modeling |
| `noImplicitAny` | Prevents untyped gaps | Forces types on inputs |
| `strictNullChecks` | Eliminates null surprises | Requires null-safe flow |
| `noUncheckedIndexedAccess` | Safer indexing | Adds `| undefined` |
| `exactOptionalPropertyTypes` | Distinguish `undefined` from missing | Tightens APIs |
| `useUnknownInCatchVariables` | Makes catch safe | Forces narrowing |
| `noPropertyAccessFromIndexSignature` | Disallow dot access on index signatures | Promotes safe access |
| `noImplicitOverride` | Safer overrides | Avoids shadowed behavior |

```ts
type User = { email?: string };
const email = (u: User) => u.email ?? "unknown";
```

## Anti-Patterns and Fixes
| Anti-pattern | Why it hurts | Safer alternative |
| --- | --- | --- |
| `as any` for speed | Hides invariants | Wrap boundary with a guard |
| `@ts-ignore` | Silences errors globally | Use `@ts-expect-error` with reason |
| Unnecessary type assertion | Masks missing checks | Use type predicate |
| Enum for string literals | Extra runtime + reverse map | `as const` object + union |
| Non-exhaustive switch | Missed states | `never` exhaustiveness |
| `string` for identifiers | Allows mixing IDs | Branded types |
| Implicit `any` in callbacks | Silent widening | Explicit generic constraints |
| Overloaded unions without guards | Ambiguous intent | Tagged unions with `type` |

```ts
type UserId = string & { readonly brand: "UserId" };
const isUserId = (v: string): v is UserId => v.startsWith("usr_");
```

## Output Expectations
- Provide concrete, type-safe designs and example code.
- Explain tradeoffs when multiple type designs are plausible.
- Favor narrow input types and broader output types.
- Show incremental migration paths when upgrading JS.

## Reference Index
- `skills/typescript/references/type-patterns.md`
- `skills/typescript/references/practical-patterns.md`
- `skills/typescript/references/config-and-tooling.md`

## Operating Rules
- Prefer `unknown` at boundaries and narrow with guards.
- Use `satisfies` to lock object shape without losing inference.
- Keep type-level logic readable; move complexity into helpers.
- If a type is hard to name, the runtime model is likely wrong.

```ts
const routes = {
  user: "/users/:id",
  order: "/orders/:id"
} satisfies Record<string, `/${string}`>;
type RouteKey = keyof typeof routes;
```

## Response Style
- Start with the core invariant or constraint, then types.
- Include a minimal runnable example when possible.
- Provide a migration note when strict flags are required.

## Fast Checks
- Is every union tagged for safe narrowing?
- Are index accesses accounted for (`noUncheckedIndexedAccess`)?
- Do public types avoid `any` and avoid unsafe assertions?
- Are all switches exhaustive with `never`?

```ts
type Event = { type: "start" } | { type: "stop" };
const handle = (e: Event) => {
  switch (e.type) {
    case "start": return 1;
    case "stop": return 2;
    default: {
      const _exhaustive: never = e;
      return _exhaustive;
    }
  }
};
```

## Common Deliverables
- Tagged unions and guard functions.
- Strict tsconfig tuning with rationale.
- Type-safe APIs for events, repositories, and results.
- Refactoring guidance for migrating JS to TS.

## Do and Don't
- Do: encode invariants with branded and tagged types.
- Do: keep helper types small and named.
- Don't: widen literals without a reason.
- Don't: return `any` from shared utilities.

```ts
const makeId = <B extends string>(s: string, b: B) =>
  s as string & { readonly brand: B };
```
