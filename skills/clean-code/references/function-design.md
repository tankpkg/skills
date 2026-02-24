# Function Design

Sources: Clean Code (Martin), A Philosophy of Software Design (Ousterhout)

This reference focuses on function readability, responsibility, and interface design.
Principles are language-agnostic with TypeScript examples.

## Naming
Functions should be verb phrases; classes and variables should be noun phrases.

Before:
```ts
function data(u: User) { return u.name.trim(); }
class PrintUser {}
const upd = true;
```

After:
```ts
function normalizeUserName(user: User) { return user.name.trim(); }
class UserPrinter {}
const isUpdated = true;
```

## Parameter Design
Rule: max 3 parameters. If more, introduce a parameter object.
Boolean parameters are a smell because they hide meaning and create forks.

Before:
```ts
function createUser(name: string, email: string, role: string, isActive: boolean) {
  return { name, email, role, isActive };
}
```

After:
```ts
type CreateUserParams = { name: string; email: string; role: string; isActive: boolean };
function createUser(params: CreateUserParams) {
  return { name: params.name, email: params.email, role: params.role, isActive: params.isActive };
}
```

Avoid flag arguments by splitting into two functions.

Before:
```ts
function renderReport(data: Report, compact: boolean) {
  return compact ? renderCompact(data) : renderFull(data);
}
```

After:
```ts
function renderCompactReport(data: Report) { return renderCompact(data); }
function renderFullReport(data: Report) { return renderFull(data); }
```

## Return Values
Prefer returning a value over mutating arguments.
Use early returns for guard clauses to reduce nesting.

Before:
```ts
function applyDiscount(order: Order) {
  if (order.total > 100) {
    order.total = order.total * 0.9;
  }
}
```

After:
```ts
function discountedTotal(order: Order) {
  if (order.total <= 100) return order.total;
  return order.total * 0.9;
}
```

## Command-Query Separation (CQS)
Queries return data; commands change state. Never both.

Before:
```ts
function updateEmail(user: User, email: string) {
  user.email = email;
  return user.email;
}
```

After:
```ts
function setEmail(user: User, email: string) { user.email = email; }
function getEmail(user: User) { return user.email; }
```

## Function Length
Target 20-30 lines. Longer is ok for lookups, pipelines, or state machines.

Before:
```ts
function calculate() {
  const items = loadItems();
  let total = 0;
  for (const item of items) { total += item.price; }
  const tax = total * 0.1;
  const shipping = total > 100 ? 0 : 10;
  const finalTotal = total + tax + shipping;
  return { total, tax, shipping, finalTotal };
}
```

After:
```ts
function calculate() {
  const total = calculateTotal(loadItems());
  const tax = calculateTax(total);
  const shipping = calculateShipping(total);
  return { total, tax, shipping, finalTotal: total + tax + shipping };
}
```

## Cyclomatic Complexity
Cyclomatic complexity measures decision paths.
Thresholds: 1-10 good, 11-20 refactor, 21+ rewrite.

Before:
```ts
function classify(score: number) {
  if (score > 90) return "A";
  if (score > 80) return "B";
  if (score > 70) return "C";
  if (score > 60) return "D";
  return "F";
}
```

After:
```ts
const thresholds = [
  { min: 90, grade: "A" },
  { min: 80, grade: "B" },
  { min: 70, grade: "C" },
  { min: 60, grade: "D" }
];
function classify(score: number) {
  const match = thresholds.find((t) => score > t.min);
  return match ? match.grade : "F";
}
```

## Cognitive Complexity
Cognitive complexity counts how hard code is to understand (nesting and flow).
Use it to detect tangled logic even when cyclomatic is low.

Before:
```ts
function canShip(order: Order) {
  if (order.items.length > 0) {
    if (order.address) {
      if (order.paymentStatus === "paid") {
        return true;
      }
    }
  }
  return false;
}
```

After:
```ts
function canShip(order: Order) {
  if (order.items.length === 0) return false;
  if (!order.address) return false;
  return order.paymentStatus === "paid";
}
```

## Depth vs Width (Ousterhout)
Prefer deep modules: simple public interfaces with rich internal behavior.

Before:
```ts
class CsvWriter {
  open(path: string) {}
  writeHeader(headers: string[]) {}
  writeRow(values: string[]) {}
  close() {}
}
```

After:
```ts
class CsvWriter {
  writeFile(path: string, rows: string[][]) { /* open, header, rows, close */ }
}
```

## Error Handling
Use exceptions for exceptional cases, return values for expected failures.

Before:
```ts
function parsePort(input: string) {
  const n = Number(input);
  return isNaN(n) ? -1 : n;
}
```

After:
```ts
function parsePort(input: string) {
  const n = Number(input);
  if (Number.isNaN(n)) throw new Error("Invalid port");
  return n;
}
```

## Comments
Comments should explain why, constraints, or tradeoffs, not what.

Before:
```ts
// loop through items
for (const item of items) { total += item.price; }
```

After:
```ts
// Pricing rule: discount applied after tax per legal requirement.
const finalTotal = applyPostTaxDiscount(total, tax);
```

## Anti-Patterns
| Anti-pattern | Example | Fix |
| --- | --- | --- |
| Long parameter list | `fn(a,b,c,d)` | Introduce Parameter Object |
| Boolean flags | `render(data, true)` | Split into two functions |
| Mixed command/query | `update().get()` | Separate methods |
| Deep nesting | `if/for/if/for` | Guard clauses + extract method |
| Overloaded names | `data()` | Rename to intent |
| Mutation of inputs | `args.x = 1` | Return new value |
| Hidden side effects | `get()` writes | Rename to `loadAndCache` |
| Repeated logic | same block in many functions | Extract method |

## Quick Checklist
- Verb names for functions, nouns for data.
- <=3 parameters, no boolean flags.
- Guard clauses to flatten nesting.
- CQS: queries return, commands mutate.
- Keep functions short and focused.

## Optional Result Type for Expected Failures
When failure is expected and frequent, return a Result type instead of throwing.

Before:
```ts
function findUser(id: string) {
  const user = db.get(id);
  if (!user) throw new Error("Not found");
  return user;
}
```

After:
```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function findUser(id: string): Result<User> {
  const user = db.get(id);
  return user ? { ok: true, value: user } : { ok: false, error: "Not found" };
}
```

## Complexity Review Prompts
- How many decision points exist in this function?
- Can nested conditions be converted to guard clauses?
- Are there duplicate branches that can be merged?
- Would a table lookup or polymorphism simplify the flow?

## Parameter Smell Table
| Smell | Example | Fix |
| --- | --- | --- |
| Too many params | `fn(a,b,c,d)` | Parameter object |
| Boolean flag | `save(user, true)` | Split function |
| Optional nulls | `save(user, null)` | Overload or new type |

## CQS Example Refactor
Before:
```ts
function saveAndCount(user: User, store: Store) {
  store.save(user);
  return store.count();
}
```

After:
```ts
function saveUser(user: User, store: Store) { store.save(user); }
function countUsers(store: Store) { return store.count(); }
```
