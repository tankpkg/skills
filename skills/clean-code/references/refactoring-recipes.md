# Refactoring Recipes

Sources: Refactoring (Fowler)

This file provides step-by-step refactoring patterns with before/after code.
Use the decision tree at the end to pick the smallest safe move.

## Safety Checklist (Before Every Refactor)
- Ensure tests cover the behavior or add characterization tests.
- Make one refactoring at a time.
- Keep functions compiling and tests green after each step.
- Use version control to checkpoint before larger moves.
- Prefer mechanical transformations over clever rewrites.

## Extract Method
Use when a section of code can be named and reused.

Steps:
1. Identify a coherent block (single responsibility).
2. Create a new function with a descriptive verb name.
3. Move the block and pass required variables as parameters.
4. Replace the block with a call to the new function.

Before:
```ts
function formatInvoice(items: Item[]) {
  let total = 0;
  for (const item of items) {
    total += item.price;
  }
  const tax = total * 0.1;
  return { total, tax, final: total + tax };
}
```

After:
```ts
function formatInvoice(items: Item[]) {
  const total = calculateTotal(items);
  const tax = calculateTax(total);
  return { total, tax, final: total + tax };
}
```

## Extract Variable
Use when an expression is complex or repeated.

Steps:
1. Identify the expression.
2. Assign it to a well-named constant.
3. Replace the expression with the constant.

Before:
```ts
if (order.total > 100 && order.customer.isVip && order.items.length > 3) {
  applyDiscount(order);
}
```

After:
```ts
const qualifiesForDiscount =
  order.total > 100 && order.customer.isVip && order.items.length > 3;
if (qualifiesForDiscount) {
  applyDiscount(order);
}
```

## Introduce Parameter Object
Use when functions take many related parameters.

Steps:
1. Create a type or class for the parameter group.
2. Replace parameters with a single object.
3. Update call sites.

Before:
```ts
function schedule(start: Date, end: Date, timezone: string, title: string) {
  return { start, end, timezone, title };
}
```

After:
```ts
type ScheduleParams = { start: Date; end: Date; timezone: string; title: string };
function schedule(params: ScheduleParams) {
  return { start: params.start, end: params.end, timezone: params.timezone, title: params.title };
}
```

## Replace Conditional with Polymorphism
Use when the same conditional logic appears in multiple places.

Steps:
1. Define an interface for the varying behavior.
2. Create classes for each case.
3. Replace conditional with a method call.

Before:
```ts
function renderBadge(user: User) {
  if (user.type === "admin") return "ADMIN";
  if (user.type === "staff") return "STAFF";
  return "USER";
}
```

After:
```ts
interface UserType { badge(): string; }
class Admin implements UserType { badge() { return "ADMIN"; } }
class Staff implements UserType { badge() { return "STAFF"; } }
class Regular implements UserType { badge() { return "USER"; } }
function renderBadge(user: UserType) { return user.badge(); }
```

## Replace Magic Number with Symbolic Constant
Use when a numeric literal hides meaning.

Steps:
1. Identify repeated or meaningful numeric literals.
2. Extract them to a named constant.
3. Replace literal usage with the constant.

Before:
```ts
if (retryCount > 3) throw new Error("Too many retries");
```

After:
```ts
const MAX_RETRIES = 3;
if (retryCount > MAX_RETRIES) throw new Error("Too many retries");
```

## Move Method
Use when a method is more interested in another class's data.

When:
- Method references another object's fields more than its own.
- Callers already have access to the target object.

How:
1. Copy the method to the target class.
2. Adjust references to use target fields.
3. Replace the original method with a delegating call or remove it.

Example:
```ts
// Before
class CartService { total(cart: Cart) { return cart.items.reduce((s, i) => s + i.price, 0); } }
// After
class Cart { total() { return this.items.reduce((s, i) => s + i.price, 0); } }
```

## Inline Method
Use when a method is too trivial or its name does not add clarity.

Steps:
1. Replace calls with the method body.
2. Delete the method.
3. Ensure code still reads clearly.

Before:
```ts
function isEligible(user: User) { return user.isActive && user.age >= 18; }
if (isEligible(user)) enroll(user);
```

After:
```ts
if (user.isActive && user.age >= 18) enroll(user);
```

## Replace Temp with Query
Use when a temporary variable stores a derived value.

Steps:
1. Extract a function that computes the value.
2. Replace temp usage with the function call.

Before:
```ts
const total = order.items.reduce((s, i) => s + i.price, 0);
const tax = total * 0.1;
```

After:
```ts
function totalFor(order: Order) { return order.items.reduce((s, i) => s + i.price, 0); }
const tax = totalFor(order) * 0.1;
```

## Compose Method
Use to create a readable top-level flow by extracting steps.

Steps:
1. Outline the high-level steps as comments.
2. Extract each step into its own method.
3. Ensure each step does one thing.

Before:
```ts
function processOrder(order: Order) {
  validate(order);
  const total = order.items.reduce((s, i) => s + i.price, 0);
  charge(order.userId, total);
  notify(order.userId, total);
}
```

After:
```ts
function processOrder(order: Order) {
  validate(order);
  const total = calculateTotal(order);
  collectPayment(order, total);
  notifyUser(order, total);
}
```

## Rename Refactoring
Use when a name hides intent or forces comments.

Steps:
1. Rename the identifier to reflect intent.
2. Update all references (IDE rename).
3. Re-run tests.

Before:
```ts
function run(u: User) { return u.isActive && u.balance > 0; }
```

After:
```ts
function canPlaceOrder(user: User) { return user.isActive && user.balance > 0; }
```

## Decision Tree: Which Refactoring for Which Smell
1. Long Method -> Extract Method or Compose Method.
2. Magic Number -> Replace Magic Number with Symbolic Constant.
3. Feature Envy -> Move Method.
4. Data Clumps -> Introduce Parameter Object.
5. Primitive Obsession -> Introduce Value Object.
6. Switch Statements -> Replace Conditional with Polymorphism.
7. Temporary Variables Everywhere -> Replace Temp with Query.
8. Over-abstraction -> Inline Method or Remove Parameter.

## After Each Refactoring
- Run tests or at least the impacted suite.
- Re-check complexity and nesting depth.
- Re-read the changed code for clarity.

## Common Pitfalls
- Extracting with poor names that hide intent.
- Moving methods without moving the data they need.
- Introducing parameter objects but leaving call sites inconsistent.
- Replacing a switch with polymorphism but still checking type codes elsewhere.

## Micro-step Checklist
- Make a change that the compiler can check.
- Run tests after each structural move.
- Keep public APIs stable until refactor is complete.

## Example: Chain Two Refactorings
Before:
```ts
function send(order: Order, email: string, region: string, isExpress: boolean) {
  if (isExpress && region === "US") return fastShip(order, email);
  return standardShip(order, email);
}
```

After:
```ts
type ShippingParams = { order: Order; email: string; region: string };
function sendExpress(params: ShippingParams) { return fastShip(params.order, params.email); }
function sendStandard(params: ShippingParams) { return standardShip(params.order, params.email); }
```

## When Not to Refactor
- When behavior is unclear and tests do not exist yet.
- When the change window is too risky for large restructures.
- When a bug fix can be safely isolated without broad edits.

## Extract Class
Use when a class has multiple responsibilities.

Steps:
1. Identify a cohesive subset of fields and methods.
2. Create a new class for that subset.
3. Move fields and methods to the new class.
4. Delegate from the original class.

Before:
```ts
class User {
  constructor(public name: string, public email: string) {}
  formatDisplay() { return `${this.name} <${this.email}>`; }
  sendWelcome() { sendEmail(this.email, "Welcome"); }
}
```

After:
```ts
class UserProfile {
  constructor(public name: string, public email: string) {}
  formatDisplay() { return `${this.name} <${this.email}>`; }
}
class UserNotifier { sendWelcome(email: string) { sendEmail(email, "Welcome"); } }
```
