# Code Smells

Sources: Refactoring (Fowler), Clean Code (Martin)

This reference focuses on smell detection with concrete refactoring outcomes.
Each smell includes a before/after example and a minimal recipe.
Examples use TypeScript for readability.

Detection Checklist
| Smell | Heuristic | Tool |
| --- | --- | --- |
| Long Method | >20 lines or multiple responsibilities | Linter, function length rule |
| Large Class | >200 lines or >5 responsibilities | IDE class metrics |
| Feature Envy | Method touches another object's data more than its own | Static analysis, manual review |
| Data Clumps | Same set of parameters across multiple methods | Search for duplicated parameter lists |
| Primitive Obsession | Repeated primitives representing domain concepts | Domain review, type audit |
| Switch Statements | Repeated switch/if-else on type codes | Grep on switch/if patterns |
| Parallel Inheritance | Two hierarchies change in lockstep | Commit history review |
| Comments as Deodorant | Comments explain confusing code | Code review |
| Speculative Generality | Unused abstractions or flags | Dead code detection |
| Dead Code | Unreferenced functions or branches | Coverage reports |

## 1. Long Method (>20 lines)
Description: a single function does multiple steps or changes for multiple reasons.
Detection heuristic: many blank lines, comments like "step 1", or deep nesting.

Before:
```ts
function checkout(cart: Cart, user: User) {
  if (!user.isActive) throw new Error("Inactive");
  let total = 0;
  for (const item of cart.items) {
    const price = item.price * item.qty;
    total += price;
  }
  const tax = total * 0.1;
  const shipping = total > 100 ? 0 : 10;
  const finalTotal = total + tax + shipping;
  const receipt = { total, tax, shipping, finalTotal };
  saveReceipt(user.id, receipt);
  chargeCard(user.cardId, finalTotal);
  notifyUser(user.email, receipt);
}
```

After:
```ts
function checkout(cart: Cart, user: User) {
  assertActive(user);
  const pricing = calculatePricing(cart);
  const receipt = buildReceipt(pricing);
  finalizePurchase(user, receipt);
}
```

Refactoring recipe:
- Identify distinct responsibilities by comments or blank lines.
- Extract methods for each responsibility.
- Rename extracted methods with verb phrases.
- Re-run tests after each extraction.

## 2. Large Class (>200 lines, >5 responsibilities)
Description: a class knows too much and changes for too many reasons.
Detection heuristic: many unrelated fields, long constructor, multiple prefixes in methods.

Before:
```ts
class UserService {
  constructor(private db: Db, private mailer: Mailer, private cache: Cache) {}
  createUser(input: UserInput) { /* validation + insert + cache */ }
  sendWelcome(userId: string) { /* load + format + email */ }
  resetPassword(userId: string) { /* token + email */ }
  formatUser(user: User) { /* formatting */ }
  loadUser(userId: string) { /* db */ }
}
```

After:
```ts
class UserRepository { load(userId: string) { /* db */ } create(input: UserInput) { /* db */ } }
class UserMailer { sendWelcome(user: User) { /* email */ } resetPassword(user: User) { /* email */ } }
class UserFormatter { format(user: User) { /* formatting */ } }
```

Refactoring recipe:
- Group methods by responsibility.
- Extract classes per responsibility.
- Move relevant fields with their methods.
- Update call sites to use new collaborators.

## 3. Feature Envy
Description: a method uses another object's data more than its own.
Detection heuristic: method accesses many getters on another object.

Before:
```ts
class InvoicePrinter {
  print(invoice: Invoice) {
    const lines = invoice.items.map((i) => `${i.name}: ${i.price}`);
    return `Invoice ${invoice.id}\n${lines.join("\n")}`;
  }
}
```

After:
```ts
class Invoice {
  formatLines() { return this.items.map((i) => `${i.name}: ${i.price}`); }
}
class InvoicePrinter {
  print(invoice: Invoice) { return `Invoice ${invoice.id}\n${invoice.formatLines().join("\n")}`; }
}
```

Refactoring recipe:
- Find the data the method depends on.
- Move the method to the class that owns the data.
- Keep a small delegating method if needed.

## 4. Data Clumps
Description: groups of data travel together, indicating a missing concept.
Detection heuristic: repeated parameter groups in multiple methods.

Before:
```ts
function createAddress(street: string, city: string, zip: string) { /* ... */ }
function shipTo(street: string, city: string, zip: string) { /* ... */ }
```

After:
```ts
type Address = { street: string; city: string; zip: string };
function createAddress(address: Address) { /* ... */ }
function shipTo(address: Address) { /* ... */ }
```

Refactoring recipe:
- Identify repeated parameter groups.
- Introduce a value object for the group.
- Update signatures and call sites.

## 5. Primitive Obsession
Description: primitives are used instead of small domain objects.
Detection heuristic: repeated validation or formatting on raw strings/numbers.

Before:
```ts
function applyDiscount(total: number, code: string) {
  if (!code.startsWith("PROMO-")) throw new Error("Invalid");
  return total - 10;
}
```

After:
```ts
class PromoCode {
  constructor(public value: string) {
    if (!value.startsWith("PROMO-")) throw new Error("Invalid");
  }
}
function applyDiscount(total: number, code: PromoCode) { return total - 10; }
```

Refactoring recipe:
- Find primitives with domain rules.
- Introduce a value object with validation.
- Replace primitive parameter types with the new type.

## 6. Switch Statements
Description: repeated conditional logic based on type codes.
Detection heuristic: multiple switch blocks on the same field.

Before:
```ts
function priceFor(kind: string) {
  switch (kind) {
    case "book": return 10;
    case "video": return 20;
    default: return 0;
  }
}
```

After:
```ts
interface ItemType { price(): number; }
class Book implements ItemType { price() { return 10; } }
class Video implements ItemType { price() { return 20; } }
function priceFor(item: ItemType) { return item.price(); }
```

Refactoring recipe:
- Create an interface for the behavior.
- Implement a class per type.
- Replace switch logic with polymorphism.

## 7. Parallel Inheritance Hierarchies
Description: two class hierarchies evolve together; every subclass requires a partner.
Detection heuristic: adding a subclass forces a change in another hierarchy.

Before:
```ts
class PdfReport {}
class PdfExporter {}
class HtmlReport {}
class HtmlExporter {}
```

After:
```ts
interface Exporter { export(report: Report): void; }
class Report { constructor(public exporter: Exporter) {} export() { this.exporter.export(this); } }
class PdfExporter implements Exporter { export(report: Report) { /* ... */ } }
class HtmlExporter implements Exporter { export(report: Report) { /* ... */ } }
```

Refactoring recipe:
- Identify the paired hierarchies.
- Move one responsibility into a collaborator.
- Inject the collaborator into the remaining hierarchy.

## 8. Comments as Deodorant
Description: comments explain confusing code instead of improving it.
Detection heuristic: comments describe what the code does, not why.

Before:
```ts
// apply promotion if total is high
if (total > 100 && user.isVip) { total = total * 0.9; }
```

After:
```ts
if (eligibleForVipDiscount(total, user)) { total = applyVipDiscount(total); }
```

Refactoring recipe:
- Rename variables or extract a function that captures intent.
- Keep comments only for non-obvious reasons or constraints.

## 9. Speculative Generality
Description: abstractions or parameters that are unused or rarely used.
Detection heuristic: unused options, flags always false, TODO for "future" behavior.

Before:
```ts
function exportReport(format: "pdf" | "html", useCache = false) {
  // useCache is never true
  return format === "pdf" ? exportPdf() : exportHtml();
}
```

After:
```ts
function exportReport(format: "pdf" | "html") {
  return format === "pdf" ? exportPdf() : exportHtml();
}
```

Refactoring recipe:
- Remove unused parameters and dead flags.
- Inline abstractions that are not used.
- Re-introduce only when needed with tests.

## 10. Dead Code
Description: code paths or functions no longer used.
Detection heuristic: zero references, covered by no tests, or flagged by coverage.

Before:
```ts
function legacyDiscount(total: number) {
  if (total > 200) return total - 20;
  return total;
}
```

After:
```ts
// Removed legacyDiscount; coverage confirmed no callers.
```

Refactoring recipe:
- Confirm no call sites (search + coverage).
- Remove code and run tests.
- Note in changelog if it was a public API.

## Refactoring Anti-Patterns
- Refactor too much at once: isolate one smell at a time.
- Refactor without tests: add characterization tests first.

## Smell Interactions
- Long Method often coexists with Comments as Deodorant.
- Feature Envy commonly appears when data clumps are spread across classes.
- Large Class usually hides multiple Long Methods and Primitive Obsession.
- Switch Statements and Parallel Inheritance often indicate missing polymorphism.

## Review Prompts
- What is the single responsibility of this function or class?
- Which name would make a comment unnecessary?
- If this changed, how many files would need updates?
- Which parameters travel together and should become a value object?
- What is the smallest refactoring that improves readability?

## Minimal Smell Triage
1. Identify the smallest safe change.
2. Apply one refactoring that removes a smell.
3. Re-run tests and reassess complexity.

## Tooling Tips
- Use "Find All References" to detect dead code quickly.
- Use coverage reports to validate removals.
- Use metrics plugins to spot large methods and classes.

## False Positives to Watch
- Long methods may be acceptable for table-driven pipelines.
- Large classes can be legitimate when representing stable core data models.
- Switch statements can be fine for small, stable enums.
- Primitive types are fine for transient data without domain rules.

## Mini Examples
Magic Number:
```ts
// Before
const timeout = 5000;
// After
const DEFAULT_TIMEOUT_MS = 5000;
```

Data Clumps:
```ts
// Before
function ship(street: string, city: string, zip: string) {}
// After
type Address = { street: string; city: string; zip: string };
function ship(address: Address) {}
```

Dead Code:
```ts
// Before
function oldTax(total: number) { return total * 0.07; }
// After
// Removed oldTax after verifying no callers.
```
