# Test Patterns

Sources: Unit Testing Principles (Khorikov), Growing Object-Oriented Software (Freeman/Pryce)
## AAA Pattern (Arrange-Act-Assert)
Goal: keep each test readable by isolating setup, execution, and verification.
Guidelines:
- One behavioral assertion per test, multiple property assertions ok.
- Put Act in the middle, single line when possible.
- Assert on outcomes, not on internal calls, unless interaction is the contract.
Example: pure function
```ts
import { describe, it, expect } from "vitest";
import { sum } from "./sum";

describe("sum", () => {
  it("should return 5 when given 2 and 3", () => {
    // Arrange
    const a = 2;
    const b = 3;

    // Act
    const result = sum(a, b);

    // Assert
    expect(result).toBe(5);
  });
});
```
Example: stateful object
```ts
import { describe, it, expect, beforeEach } from "vitest";
import { Inventory } from "./inventory";

describe("Inventory", () => {
  let inventory: Inventory;

  beforeEach(() => {
    inventory = new Inventory();
  });

  it("should reduce quantity when reserving stock", () => {
    // Arrange
    inventory.add({ sku: "A1", qty: 10 });

    // Act
    inventory.reserve("A1", 3);

    // Assert
    expect(inventory.get("A1")?.qty).toBe(7);
  });
});
```
## Test Doubles Decision Tree
Choose a double based on the collaboration type and the risk of side effects.
Decision tree:
- Does the collaborator provide data only?
  - Yes: use a Stub or Fake.
- Do you need to verify a protocol of calls is the contract?
  - Yes: use a Mock or Spy.
- Does the collaborator have significant behavior worth reusing?
  - Yes: use a Fake with in-memory implementation.
### Stub (return data, no verification)
```ts
import { describe, it, expect, vi } from "vitest";
import { BillingService } from "./billing-service";

describe("BillingService", () => {
  it("should apply discount for loyalty tier", () => {
    const pricing = { getBasePrice: vi.fn().mockReturnValue(100) };
    const loyalty = { getTier: vi.fn().mockReturnValue("gold") };
    const svc = new BillingService(pricing, loyalty);

    const total = svc.quote("sku-1");

    expect(total).toBe(90);
  });
});
```
### Mock (verify calls and arguments)
```ts
import { describe, it, expect, vi } from "vitest";
import { Newsletter } from "./newsletter";

describe("Newsletter", () => {
  it("should send welcome email when user subscribes", () => {
    const mailer = { send: vi.fn() };
    const newsletter = new Newsletter(mailer);

    newsletter.subscribe("a@example.com");

    expect(mailer.send).toHaveBeenCalledWith({
      to: "a@example.com",
      template: "welcome",
    });
  });
});
```
### Spy (wrap real collaborator, verify calls)
```ts
import { describe, it, expect, vi } from "vitest";
import { AuditLog } from "./audit-log";
import { UserService } from "./user-service";

describe("UserService", () => {
  it("should write an audit entry when user deactivated", () => {
    const log = new AuditLog();
    const spy = vi.spyOn(log, "record");
    const svc = new UserService(log);

    svc.deactivate("user-1");

    expect(spy).toHaveBeenCalledWith("user-1", "deactivate");
  });
});
```
### Fake (in-memory implementation)
```ts
import { describe, it, expect } from "vitest";
import { InMemoryRepo } from "./in-memory-repo";
import { UserRepo } from "./user-repo";
import { UserService } from "./user-service";

describe("UserService", () => {
  it("should persist user with generated id", () => {
    const repo: UserRepo = new InMemoryRepo();
    const svc = new UserService(repo);

    const user = svc.register("Ada");

    expect(repo.getById(user.id)?.name).toBe("Ada");
  });
});
```
## Naming Conventions
Two common formats:
- should_[expected]_when_[condition]
- descriptive sentence that reads as behavior
Examples:
```ts
it("should return empty list when no items exist", () => {});
it("returns empty list for new repository", () => {});
```
Rules:
- Name the behavior, not the method name.
- Mention the trigger or condition.
- Avoid implementation detail references.
## Pure Functions vs Stateful Code
Pure function strategy:
- Minimal setup, no doubles unless input generation.
- Assert on value outputs.
- Use property-based tests for invariants.
Stateful strategy:
- Arrange the state explicitly.
- Act with a single state transition.
- Assert on the new state and relevant events.
Pure example:
```ts
import { describe, it, expect } from "vitest";
import { normalizeEmail } from "./normalize-email";

describe("normalizeEmail", () => {
  it("should lowercase and trim whitespace", () => {
    const result = normalizeEmail("  Ada@Example.COM ");
    expect(result).toBe("ada@example.com");
  });
});
```
Stateful example:
```ts
import { describe, it, expect } from "vitest";
import { Cart } from "./cart";

describe("Cart", () => {
  it("should remove item when quantity becomes zero", () => {
    const cart = new Cart();
    cart.add({ sku: "A1", qty: 1 });

    cart.updateQty("A1", 0);

    expect(cart.items()).toEqual([]);
  });
});
```
## Parameterized / Table-Driven Tests
Use when the same behavior should hold across inputs.
```ts
import { describe, it, expect } from "vitest";
import { isAdult } from "./is-adult";

describe("isAdult", () => {
  const cases = [
    { age: 17, expected: false },
    { age: 18, expected: true },
    { age: 21, expected: true },
  ];

  it.each(cases)("age $age => $expected", ({ age, expected }) => {
    expect(isAdult(age)).toBe(expected);
  });
});
```
When to avoid:
- When each case requires different setup.
- When failures need deep context per case.
## Property-Based Testing
What it is:
- Generate many inputs to prove invariants, not specific examples.
- Good for pure functions, parsers, serializers, and math.

When to use:
- You can express invariants clearly.
- Exhaustive example testing is too large.
Example with fast-check:
```ts
import { describe, it, expect } from "vitest";
import fc from "fast-check";
import { reverse } from "./reverse";

describe("reverse", () => {
  it("should be its own inverse", () => {
    fc.assert(
      fc.property(fc.string(), (s) => {
        expect(reverse(reverse(s))).toBe(s);
      })
    );
  });
});
```
## Mutation Testing
Mutation testing introduces small changes (mutations) in code and checks whether
tests catch them. It measures test effectiveness, not just coverage.
What it catches that coverage misses:
- Assertions that do not verify correct outcomes.
- Tests that execute code without meaningful checks.
- Hidden dead paths that still pass.
Example with Stryker configuration excerpt:
```ts
export default {
  mutate: ["src/**/*.ts"],
  testRunner: "vitest",
  reporters: ["html", "clear-text", "progress"],
};
```
## Async Code Patterns
Promise-based async:
```ts
import { describe, it, expect } from "vitest";
import { fetchUser } from "./fetch-user";

describe("fetchUser", () => {
  it("should return user data", async () => {
    const user = await fetchUser("u-1");
    expect(user.id).toBe("u-1");
  });
});
```
Timers with fake clocks:
```ts
import { describe, it, expect, vi } from "vitest";
import { debounce } from "./debounce";

describe("debounce", () => {
  it("should call function after wait", () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    vi.advanceTimersByTime(100);

    expect(fn).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });
});
```
Async error path:
```ts
import { describe, it, expect } from "vitest";
import { fetchUser } from "./fetch-user";

describe("fetchUser", () => {
  it("should throw when user is missing", async () => {
    await expect(fetchUser("missing")).rejects.toThrow("NotFound");
  });
});
```
## Testing Error Paths and Edge Cases
Systematic checklist:
- Null/undefined inputs
- Empty collections
- Boundary values (min/max)
- Invalid formats
- Permission/authorization failures
Example:
```ts
import { describe, it, expect } from "vitest";
import { parsePort } from "./parse-port";

describe("parsePort", () => {
  it("should throw for non-numeric values", () => {
    expect(() => parsePort("abc")).toThrow("Invalid port");
  });

  it("should throw for out-of-range values", () => {
    expect(() => parsePort("70000")).toThrow("Invalid port");
  });
});
```
## Testing Pyramid
Typical ratio guideline:
- Unit: 70-80%
- Integration: 15-25%
- E2E: 5-10%

Examples:
- Unit: validate a pure function with no I/O.
- Integration: verify DB repository against a real database.
- E2E: confirm a user can log in via UI.
When to break the pyramid:
- UI-heavy apps with critical flows may need more E2E.
- Safety-critical domains might need more integration tests.
- Highly dynamic UI state can require broader UI tests.
## Anti-Patterns
Testing implementation details:
- Asserting on private method calls.
- Verifying exact SQL string unless it is the contract.
Fragile tests:
- Relying on real time and random order.
- Over-mocking and heavy setup.
Slow tests:
- Real network calls in unit tests.
- Full browser runs for every small change.
Fixes:
- Prefer contract tests for boundaries.
- Use fakes for I/O and mock only interactions that matter.
- Keep test setup local to each test or shared in a fixture.
