# Config and Tooling

Sources: TypeScript Handbook, tsconfig reference

## tsconfig for Libraries
Optimize for declaration output and safe public APIs.
Use `declaration` + `emitDeclarationOnly` when you build with a separate bundler.

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "declaration": true,
    "emitDeclarationOnly": true,
    "declarationMap": true,
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "noImplicitOverride": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  },
  "include": ["src"]
}
```

```ts
export type PublicApi = {
  id: string;
  name?: string;
};
```

## tsconfig for Next.js Apps
Align with Next defaults; avoid `emitDeclarationOnly`.
Keep `jsx` and module resolution aligned to Next.

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "preserve",
    "incremental": true,
    "noEmit": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["next-env.d.ts", "src/**/*.ts", "src/**/*.tsx"],
  "exclude": ["node_modules"]
}
```

```ts
export const getTitle = (v?: string) => v ?? "Untitled";
```

## tsconfig for Node.js Backends
Target a modern Node runtime and enable safe ESM or CJS explicitly.
Pair with `node` module resolution for backend workflows.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "useUnknownInCatchVariables": true,
    "noImplicitOverride": true
  },
  "include": ["src"]
}
```

```ts
export const readEnv = (key: string): string => {
  const value = process.env[key];
  if (!value) throw new Error(`Missing env ${key}`);
  return value;
};
```

## tsconfig for Monorepo Base
Use project references and a shared base config.
Keep build outputs isolated per package.

```json
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true,
    "incremental": true,
    "rootDir": "src",
    "outDir": "dist",
    "strict": true,
    "noUncheckedIndexedAccess": true
  }
}
```

```ts
export type PackageId = string & { readonly __brand: "PackageId" };
```

## Strict Mode Flags and Why They Matter
| Flag | Behavior | Why it matters |
| --- | --- | --- |
| `strict` | Enables all strict checks | Consistent safety baseline |
| `noImplicitAny` | Disallows implicit `any` | Removes untyped gaps |
| `strictNullChecks` | Treats null/undefined distinctly | Avoids null bugs |
| `noUncheckedIndexedAccess` | Indexing returns `T | undefined` | Safer maps |
| `exactOptionalPropertyTypes` | Optional means missing | Accurate API contracts |
| `useUnknownInCatchVariables` | `catch` is `unknown` | Forces narrowing |
| `noImplicitOverride` | Requires `override` keyword | Safer inheritance |
| `noPropertyAccessFromIndexSignature` | No dot access on index signature | Prevents unsafe lookups |

```ts
type User = { email?: string };
const email = (u: User) => u.email ?? "unknown";
```

## Path Aliases
Define in `tsconfig` and mirror in tooling (bundler, jest, eslint).
Prefer a single `@/` prefix for application code.

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/core/*": ["src/core/*"],
      "@/features/*": ["src/features/*"]
    }
  }
}
```

```ts
import { parseUser } from "@/core/parse";
```

## Project References for Monorepos
Use `references` to enable incremental builds and package boundaries.
Each package must set `composite: true`.

```json
{
  "files": [],
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/ui" }
  ]
}
```

```ts
export type CoreConfig = { apiBase: `/${string}` };
```

## Declaration Files (.d.ts)
Write `.d.ts` when you need to declare globals or untyped modules.
Keep them small and scoped to your actual usage.

```ts
declare module "legacy-lib" {
  export function parse(input: string): { ok: boolean; value?: string };
}
```

```ts
declare global {
  interface Window { __featureFlags?: Record<string, boolean> }
}
```

## Type-Checking JavaScript with JSDoc
Enable `checkJs` and annotate with JSDoc types.
This helps incremental migration without a full rewrite.

```json
{
  "compilerOptions": {
    "checkJs": true,
    "allowJs": true,
    "noEmit": true
  },
  "include": ["src/**/*.js"]
}
```

```ts
/** @param {string} id */
export const getUser = (id) => ({ id });
```

## Migration Strategy: JavaScript to TypeScript
Start at boundaries, move inward, and replace unsafe types with guards.
Use `unknown` at the edge and narrow in adapters.

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
const parseNumber = (v: unknown): Result<number> =>
  typeof v === "number" ? { ok: true, value: v } : { ok: false, error: "not number" };
```

```ts
export const readConfig = (v: unknown) => {
  const n = parseNumber((v as Record<string, unknown>).retries);
  if (!n.ok) throw new Error(n.error);
  return { retries: n.value };
};
```

## ESLint TypeScript Rules
Enable rules that prevent unsafe escape hatches.
Skip rules that duplicate TypeScript checks or harm ergonomics.

```ts
export const rules = {
  "@typescript-eslint/no-explicit-any": "error",
  "@typescript-eslint/no-unsafe-assignment": "error",
  "@typescript-eslint/no-unsafe-return": "error",
  "@typescript-eslint/consistent-type-imports": "warn",
  "@typescript-eslint/no-floating-promises": "error",
  "@typescript-eslint/await-thenable": "error"
};
```

```ts
export const skip = {
  "@typescript-eslint/no-inferrable-types": "off",
  "@typescript-eslint/ban-ts-comment": ["error", { "ts-expect-error": "allow-with-description" }]
};
```

## Performance: Compiler Options That Matter
Use incremental builds and avoid unnecessary type-checking of dependencies.
Balance `skipLibCheck` with the need for third-party type accuracy.

```json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo",
    "skipLibCheck": true,
    "disableReferencedProjectLoad": false
  }
}
```

```ts
export const perfNote = (ms: number) => `build in ${ms}ms`;
```

## Anti-Patterns and Safer Alternatives
| Anti-pattern | Risk | Alternative |
| --- | --- | --- |
| `skipLibCheck` everywhere | Missed type regressions | Use per-package overrides |
| Mixed `moduleResolution` | Confusing import behavior | Standardize across workspace |
| `allowJs` forever | Stuck migration | Move files incrementally |
| Global path aliases | Hidden coupling | Keep aliases scoped |
| `declare global` in app code | Type leaks | Centralize in `types/` |
| `any` in configs | Unsafe boundaries | `unknown` + parse |
| `noEmit` in libs | No declarations | Use `emitDeclarationOnly` |
| `esModuleInterop` toggled per package | Inconsistent runtime | Align per runtime target |

```ts
const parseEnv = (v: unknown): string => {
  if (typeof v !== "string") throw new Error("Expected string");
  return v;
};
```
