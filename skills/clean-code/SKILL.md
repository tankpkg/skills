---
name: "@tank/clean-code"
description: "Actionable clean code patterns with code smell detection and refactoring recipes. Covers naming conventions, function design, SOLID practices, code smell identification, refactoring patterns, complexity management, and readability. Triggers: clean code, refactor, code smell, naming, function design, SOLID, single responsibility, DRY, complexity, readability, maintainability, technical debt, code review, code quality, extract method, long method, magic number, feature envy, data clumps, primitive obsession, command query separation."
---

# Clean Code Skill

Use this skill when you need concrete refactoring steps, smell detection heuristics, or naming and function design guidance with examples.

## Core Philosophy
- Code is read 10x more than written. Optimize for readers first.
- Make the change easy, then make the easy change. Small steps beat big rewrites.
- Depth over width. Prefer fewer, deeper modules with simple interfaces.

## Naming Rules
| Element | Rule | Example |
| --- | --- | --- |
| Variable | Noun | `userCount`, not `countUsers` |
| Function | Verb | `calculateTotal()`, not `totalCalculation()` |
| Boolean | `is/has/can` prefix | `isActive`, not `active` |
| Class | Noun | `InvoicePrinter`, not `PrintInvoice` |
| Constant | UPPER_SNAKE | `MAX_RETRIES`, not `maxRetries` |

Naming example:
```ts
// Before
const d = new Date();
function user(name: string) { return name.trim().toLowerCase(); }
const a = true;

// After
const createdAt = new Date();
function normalizeUserName(name: string) { return name.trim().toLowerCase(); }
const isActive = true;
```

## Function Design Rules
| Rule | Target |
| --- | --- |
| Max parameters | 3 (introduce parameter object when >3) |
| Max lines | 20-30 (exceptions: table lookups, state machines) |
| Max nesting depth | 2 |
| Cyclomatic complexity | 10 |

Function example:
```ts
// Before
function price(userId: string, tax: number, discount: number, promo: string) {
  if (!userId) throw new Error("Missing user");
  if (tax < 0) throw new Error("Invalid tax");
  return base(userId) + tax - discount + promoValue(promo);
}

// After
type PricingParams = { userId: string; tax: number; discount: number; promo: string };
function calculatePrice(params: PricingParams) {
  if (!params.userId) throw new Error("Missing user");
  if (params.tax < 0) throw new Error("Invalid tax");
  return base(params.userId) + params.tax - params.discount + promoValue(params.promo);
}
```

## Quick Smell -> Fix Mapping
| Smell | Fix |
| --- | --- |
| Long method | Extract Method |
| Magic number | Extract Constant |
| Feature envy | Move Method |
| Primitive obsession | Introduce Value Object |
| Data clumps | Introduce Parameter Object |
| Switch statements | Replace Conditional with Polymorphism |
| God class | Extract Class |

## SOLID Principles (with examples)

Single Responsibility: a module should have one reason to change.
```ts
// Before
class ReportService {
  generate(data: string) { return data.toUpperCase(); }
  save(report: string) { localStorage.setItem("report", report); }
}

// After
class ReportFormatter { format(data: string) { return data.toUpperCase(); } }
class ReportStore { save(report: string) { localStorage.setItem("report", report); } }
```

Open/Closed: extend behavior without modifying existing code.
```ts
// Before
function shippingCost(type: string) {
  if (type === "ground") return 5;
  if (type === "air") return 15;
  return 0;
}

// After
interface Shipping { cost(): number; }
class Ground implements Shipping { cost() { return 5; } }
class Air implements Shipping { cost() { return 15; } }
function shippingCost(method: Shipping) { return method.cost(); }
```

Liskov Substitution: subtypes must be usable wherever the base type is expected.
```ts
// Before
class Rectangle { constructor(public w: number, public h: number) {} area() { return this.w * this.h; } }
class Square extends Rectangle { set w(v: number) { this.h = v; } }

// After
interface Shape { area(): number; }
class Rectangle implements Shape { constructor(public w: number, public h: number) {} area() { return this.w * this.h; } }
class Square implements Shape { constructor(public size: number) {} area() { return this.size * this.size; } }
```

Interface Segregation: keep interfaces small and focused.
```ts
// Before
interface Printer { print(): void; scan(): void; fax(): void; }
class ReceiptPrinter implements Printer { print() {} scan() { throw new Error("N/A"); } fax() { throw new Error("N/A"); } }

// After
interface Printable { print(): void; }
class ReceiptPrinter implements Printable { print() {} }
```

Dependency Inversion: depend on abstractions, not concretions.
```ts
// Before
class OrderService { private db = new SqlDb(); save(order: Order) { this.db.insert(order); } }

// After
interface OrderStore { insert(order: Order): void; }
class OrderService { constructor(private store: OrderStore) {} save(order: Order) { this.store.insert(order); } }
```

## Anti-Patterns
| Anti-pattern | Why it hurts | Remedy |
| --- | --- | --- |
| Long parameter lists | Hard to read and order dependent | Introduce Parameter Object |
| Flag arguments | Mixed responsibilities | Split into two functions |
| Shotgun surgery | Many files change for one behavior | Consolidate responsibility |
| Lava flow | Dead code accumulates | Delete or archive |
| Magic numbers | Meaning hidden | Extract Constant |
| Speculative generality | Unused abstractions | Inline or delete |
| God class | Too many responsibilities | Extract Class |
| Comments as deodorant | Mask bad code | Refactor, then comment why |
| Overloaded names | Ambiguous meaning | Rename to reveal intent |

## Working Mode
1. Identify the smallest unit of change.
2. Confirm tests or add a characterization test.
3. Apply one refactoring at a time.
4. Re-run tests and reassess complexity.

## Reference Index
- `skills/clean-code/references/code-smells.md`
- `skills/clean-code/references/refactoring-recipes.md`
- `skills/clean-code/references/function-design.md`
