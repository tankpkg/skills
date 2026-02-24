# TDD Workflows

Sources: Test-Driven Development by Example (Beck), Kent Beck blog

## Classic TDD Cycle with a Stack Example

Goal: build a Stack from scratch using small red-green-refactor steps.

### Iteration 1: new stack is empty

RED test:
```ts
import { describe, it, expect } from "vitest";
import { Stack } from "./stack";

describe("Stack", () => {
  it("should be empty when created", () => {
    const stack = new Stack();
    expect(stack.isEmpty()).toBe(true);
  });
});
```

GREEN implementation:
```ts
export class Stack {
  isEmpty(): boolean {
    return true;
  }
}
```

REFACTOR:
- No refactor needed yet.

### Iteration 2: push makes stack non-empty

RED test:
```ts
import { describe, it, expect } from "vitest";
import { Stack } from "./stack";

describe("Stack", () => {
  it("should not be empty after push", () => {
    const stack = new Stack();
    stack.push("A");
    expect(stack.isEmpty()).toBe(false);
  });
});
```

GREEN implementation:
```ts
export class Stack {
  private hasItems = false;

  push(_item: string): void {
    this.hasItems = true;
  }

  isEmpty(): boolean {
    return !this.hasItems;
  }
}
```

REFACTOR:
- Rename hasItems -> count? not yet, keep minimal.

### Iteration 3: pop returns last pushed item

RED test:
```ts
import { describe, it, expect } from "vitest";
import { Stack } from "./stack";

describe("Stack", () => {
  it("should return last pushed item on pop", () => {
    const stack = new Stack();
    stack.push("A");
    stack.push("B");

    expect(stack.pop()).toBe("B");
  });
});
```

GREEN implementation:
```ts
export class Stack {
  private items: string[] = [];

  push(item: string): void {
    this.items.push(item);
  }

  pop(): string | undefined {
    return this.items.pop();
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }
}
```

REFACTOR:
- Remove temporary hasItems flag from earlier iteration.
- Consolidate behavior into items array.

### Iteration 4: pop on empty stack throws

RED test:
```ts
import { describe, it, expect } from "vitest";
import { Stack } from "./stack";

describe("Stack", () => {
  it("should throw when popping empty stack", () => {
    const stack = new Stack();
    expect(() => stack.pop()).toThrow("EmptyStack");
  });
});
```

GREEN implementation:
```ts
export class Stack {
  private items: string[] = [];

  push(item: string): void {
    this.items.push(item);
  }

  pop(): string {
    if (this.items.length === 0) {
      throw new Error("EmptyStack");
    }
    return this.items.pop() as string;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }
}
```

REFACTOR:
- Extract guard to a private method if more errors appear.

## Transformation Priority Premise (TPP)

Prefer the simplest transformation that passes the test, then incrementally
increase complexity.

Example order:
1) Return a constant
2) Return a member
3) Compute from input
4) Iterate
5) Use conditional

## Inside-Out vs Outside-In TDD

Decision tree:
- Is the domain model stable and well understood?
  - Yes: Inside-Out (start with domain objects).
  - No: Outside-In (start from a user-facing test, drive API design).
- Is integration risk high (network, DB, UI)?
  - Yes: Outside-In with thin integration tests.

Inside-Out example:
- Start with value objects and pure functions.
- Build services after domain behavior is firm.

Outside-In example:
- Start with a top-level API test.
- Use mocks for boundaries, then replace with integration tests.

## TDD with Legacy Code

Steps:
1) Write characterization tests to lock current behavior.
2) Identify seams (places to inject doubles).
3) Break dependencies with wrapper interfaces.
4) Refactor safely under test coverage.

Characterization test example:
```ts
import { describe, it, expect } from "vitest";
import { legacyPrice } from "./legacy-price";

describe("legacyPrice", () => {
  it("should keep existing price behavior for SKU-1", () => {
    expect(legacyPrice("SKU-1")).toBe(42);
  });
});
```

## TDD for API Endpoints

Approach:
- Test handler in isolation first.
- Then add integration tests for routing and middleware.

Example: test-first route handler
```ts
import { describe, it, expect } from "vitest";
import { createUserHandler } from "./create-user";

describe("createUserHandler", () => {
  it("should return 201 with user id", async () => {
    const repo = { create: async () => ({ id: "u-1" }) };
    const handler = createUserHandler(repo);

    const response = await handler({ body: { name: "Ada" } });

    expect(response.status).toBe(201);
    expect(response.body.id).toBe("u-1");
  });
});
```

## TDD for React Components

Pattern: render-test-first
1) Write a test for the user-visible behavior.
2) Render the component with minimal props.
3) Add only enough implementation to pass.

Example:
```ts
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Counter } from "./counter";

describe("Counter", () => {
  it("should render initial count", () => {
    render(<Counter initial={2} />);
    expect(screen.getByText("Count: 2")).toBeInTheDocument();
  });
});
```

## When NOT to Use TDD

Decision table:
- Exploratory spike with uncertain direction: avoid TDD, timebox spike.
- UI prototyping with rapid visual changes: avoid TDD, add tests later.
- Data pipelines with unstable schema: avoid TDD, write high-level checks.
- Safety-critical logic: TDD is useful, add extra verification.

## TDD Kata Exercises

Recommended katas:
- FizzBuzz
- String Calculator
- Bowling Game

Use katas to practice red-green-refactor timing and refactoring discipline.

## AI-Augmented TDD

Workflow:
1) Human writes the failing test and acceptance criteria.
2) AI generates the minimal implementation.
3) Human refactors for clarity and design.
4) AI suggests additional edge-case tests.

Guardrails:
- Do not let AI change the test intent.
- Keep refactors small and test-verified.

## Common Failures

Symptoms:
- Stuck in RED: test too big or unclear.
- Over-testing: asserting on internals or too many cases at once.
- Slow cycle: tests too heavy or running full suite each step.

Fixes:
- Shrink the test scope.
- Replace integration with unit tests where possible.
- Run targeted tests during green/refactor.

## Anti-Patterns Table

| Anti-pattern | Result | Correction |
| --- | --- | --- |
| Writing multiple tests before any green | Large failing surface | Keep one failing test at a time |
| Over-mocking collaborators | Brittle tests | Mock only boundary interactions |
| Refactoring without tests green | Breaks behavior | Keep tests green before refactor |
| Skipping refactor | Design rot | Refactor every few greens |
