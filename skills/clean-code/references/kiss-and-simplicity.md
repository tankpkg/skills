# KISS and Simplicity

Sources: Ousterhout (A Philosophy of Software Design), Hickey (Simple Made Easy), grugbrain.dev, Beck (Implementation Patterns), Fowler (Refactoring)

Covers: over-engineering detection, complexity budgets, abstraction decisions, YAGNI, simplicity vs DRY, red flags.

KISS (Keep It Simple, Stupid) is the active fight against the "complexity demon." Software development is the management of complexity; when complexity wins, progress stops. This reference provides the frameworks needed to recognize and eliminate unnecessary complexity before it becomes technical debt.

## 1. Simple vs. Easy (Hickey)
Rich Hickey defines simplicity as "one fold, one braid"—the opposite of "complecting" (interweaving). Understanding the distinction between these two concepts is fundamental to building maintainable systems.

- **Simple**: Objective. Refers to a component's lack of entanglement. A simple function has one responsibility and clear, direct inputs/outputs. It is independent of its surroundings.
- **Easy**: Subjective. Refers to "nearness to hand" or familiarity. A tool might be "easy" because you know it or because it's a "standard" library, but "complecting" because it introduces hidden global state, execution-order dependencies, or implicit context.

| Attribute | Simple | Easy |
| --- | --- | --- |
| Focus | Logic and dependencies | Developer comfort and familiarity |
| Meaning | Not entangled (one braid) | Near to hand (familiar) |
| Measurement | Objectively verifiable (Isolation test) | Subjectively felt (Familiarity) |
| Impact | Reduces system complexity | Reduces initial implementation effort |
| Long-term | High maintainability, predictable | High complexity debt, fragile |

### Examples of "Easy" but "Complected" Code
Many developers choose "easy" paths that lead to "complected" (interwoven) systems:
1. **Using Global State**: It's easy to access a global `config` object from anywhere. It complects every function with the entire system configuration.
2. **Execution Order Dependencies**: It's easy to rely on `init()` being called before `run()`. It complects the two functions with the dimension of time.
3. **Implicit Context**: It's easy to pass a `Context` object through 20 layers. It complects every layer with every possible field in that context.

## 2. Over-engineering Detection
Over-engineering occurs when a solution's complexity exceeds the problem's current requirements. It is often driven by a well-meaning desire to "plan for the future."

### Shallow Module Score (Ousterhout)
A module is "deep" if its interface is much simpler than its implementation. A "shallow" module exposes too much of its internal complexity, requiring callers to know too much.

**Heuristic**: `Shallow Module Score = (Parameters + Exceptions + Concepts) / Logic Lines`
- **Target (< 0.2)**: Deep module. Significant value hidden behind a tiny interface. Examples include Unix `read()`/`write()` or a high-level `processPayment()` function.
- **Red Flag (> 0.5)**: Shallow module. The overhead of learning and using the interface is too high for the logic it provides.

#### Case Study: Shallow vs. Deep
```ts
// SHALLOW (Score: 2.67) - Red Flag
// The caller must provide 8 distinct pieces of data.
// The function does almost no work itself.
function updateUserSettings(
  userId: string,
  theme: 'light' | 'dark',
  notifications: boolean,
  emailFrequency: 'daily' | 'weekly',
  timezone: string,
  language: string,
  marketingOptIn: boolean,
  updatedAt: Date
) {
  return db.users.update(userId, { 
    theme, 
    notifications, 
    emailFrequency, 
    timezone, 
    language, 
    marketingOptIn, 
    updatedAt 
  });
}

// DEEP (Score: 0.02) - Excellent
// The caller provides one ID. 
// The function manages complex business rules internally.
function processUserOnboarding(userData: UserOnboardingData) {
  // Logic hidden from caller:
  // 1. Validate domain-specific onboarding rules (10 lines)
  // 2. Initialize profile with defaults based on region (10 lines)
  // 3. Trigger external welcome email sequence (5 lines)
  // 4. Update multi-table synchronization (15 lines)
  // 5. Log audit trail with security context (5 lines)
}
```

### The Isolation Test (Complecting)
To detect complecting (interweaving), attempt to explain a component or function without mentioning any other part of the system.
- **Pass**: You can describe the logic using only local variables and input parameters. "This function takes a price and a tax rate and returns the total."
- **Fail**: You must reference global state, other class instances, or specific execution orders. "This function calculates the total, but it needs the `GlobalConfig` to be loaded and the `UserSession` to be active."

### Over-engineering Decision Steps
1. **Validation**: Does this solve a problem that exists *today* in the user requirements? (If no -> Stop).
2. **Explainability**: Can you explain the design to a peer in two sentences without using jargon (e.g., "monad", "factory", "provider")?
3. **Complexity Ratio**: Does the abstraction hide more complexity than it introduces? (Module Depth check).
4. **Maintenance**: If you deleted this abstraction and inlined the code, would the resulting code be harder to read?
5. **Red Flag Count**: If a design raises 2+ red flags (see Section 7), it is over-engineered. Simplify immediately.

## 3. Complexity Budgets
Complexity is a finite resource. A "complexity budget" ensures you spend it on the core domain, not on infrastructure or patterns.

### Cognitive Load Score
`Cognitive Load = Dependencies + Obscurity + Change Amplification`
- **Dependencies**: Number of distinct concepts/classes a developer must keep in their head to understand this file.
- **Obscurity**: Hidden side effects, global state dependencies, or "magic" behavior (e.g., auto-magical decorators).
- **Change Amplification**: The number of files/lines that must be updated to make one logical business change.

#### Scenario: Calculating Cognitive Load
Consider a `PaymentService`:
- It imports 8 other services (Dependencies = 8).
- It modifies a global `AuditLog` implicitly (Obscurity = 5).
- Adding a new payment method requires changing 10 files (Change Amplification = 10).
- **Total Score: 23** (Budget is 10). **Verdict**: Too complex.

### Abstraction Score (grugbrain)
Grug teaches that "abstraction demon spirit" enters through well-meaning developers.
`Abstraction Score = (Interfaces + Base Classes + Generics) / Concrete Implementations`
- **Safe (< 0.3)**: Mostly concrete code. High signal-to-noise ratio.
- **Danger (> 0.5)**: You are likely building a framework for problems you don't have yet.

**Grug's Law**: "Complexity is apex predator. Say 'no' to complexity is best weapon. Grug say: factor code later, not sooner."

## 4. Abstraction Timing
The most expensive abstractions are the ones created too early. "Premature abstraction is the root of much evil."

### The Rule of Three (Evolutionary Approach)
- **First time (V1: Inline)**:
  Write it inline. Solve the problem directly. No abstraction yet.
  ```ts
  function createUser(email: string) {
    if (!email.includes('@')) throw new Error('Invalid email');
    return db.users.create({ email });
  }
  ```
- **Second time (V2: Copy)**:
  Copy and paste. Note the similarity but resist the urge to "refactor." You still don't know the full pattern of variation.
  ```ts
  function createProduct(sku: string) {
    if (!sku.startsWith('P-')) throw new Error('Invalid SKU');
    return db.products.create({ sku });
  }
  ```
- **Third time (V3: Abstract)**:
  Now you have three data points. You can see what is constant (validation + creation) and what varies (the rule). This is the correct time to abstract.
  ```ts
  interface EntityRule<T> { field: keyof T; check: (v: any) => boolean; }
  function validateAndCreate<T>(data: T, rule: EntityRule<T>, repo: Repo<T>) {
    if (!rule.check(data[rule.field])) throw new Error('Invalid');
    return repo.create(data);
  }
  ```

### The 5-Minute Explainability Test
Find a junior developer (or a peer who doesn't know the task). Explain your abstraction.
- If they understand it in < 5 minutes: **Safe**.
- If they are confused or you need a whiteboard: **Too complex**.

### Abstraction Decision Steps
- **Q1**: Have I seen this exact pattern at least 3 times?
- **Q2**: Does this abstraction reduce the total line count of the system?
- **Q3**: Does this abstraction survive three different requirement changes?
- **Q4**: Does the implementation logic justify the interface overhead? (Module Depth)
- **Q5**: Is the abstraction easier to test than the concrete implementation?

## 5. YAGNI: The Implementation Budget
YAGNI (You Ain't Gonna Need It) is the antidote to "speculative generality."

### The YAGNI Checklist
Before building a feature or "pre-factoring" for future needs, verify:
- □ Is this a current requirement from a stakeholder?
- □ Will this code be executed in the next production release?
- □ Is the cost of building it *later* significantly higher (e.g., 5x) than now?
- □ Does this solve a problem we actually have, rather than a problem we *think* we might have?
- □ If we build this now and it's wrong, how hard is it to delete?

### Common YAGNI Traps
1. **The "Generic" Database Layer**: "We might switch to NoSQL later." (Result: 20 useless interfaces).
2. **The "Plugin" Architecture**: "We might need to add extensions." (Result: High indirection, zero plugins ever built).
3. **The "Universal" Configuration**: "We might need to tune every parameter." (Result: Config hell).

### Cost Analysis: Build vs. Defer
- **Building Now**: Implementation time + Testing time + Ongoing maintenance (Carry Cost).
- **Deferring**: Potential refactoring time later (Technical Debt) vs. Time saved now (Opportunity Cost).

**Decision**: If `Current Build Time + Carry Cost > Expected Future Refactor Time`, then **Defer**.

## 6. Simplicity vs. DRY
Duplication is often cheaper than the wrong abstraction. DRY (Don't Repeat Yourself) should target **Knowledge**, not **Syntax**.

### Knowledge vs. Code
- **Knowledge**: A business rule or algorithm (e.g., "Tax calculation for California"). This MUST be DRY. If the rule changes, every place using it must reflect the change.
- **Code**: Lines that look identical but represent different concepts (e.g., "Validation for User name" vs "Validation for Product name"). These can be WET (Write Everything Twice). They evolve independently.

### DRY vs. WET Decision Steps
1. **Shared Reason to Change**: If I change one instance, *must* I change the other? (Yes -> DRY)
2. **Coupling**: Does the abstraction couple unrelated parts of the system? (Yes -> Keep WET)
3. **Locality of Behavior**: Is the code easier to follow when it's local (duplicated) or when it's tucked away in a helper? (Local -> Keep WET)
4. **Readability**: Does extracting the logic make the caller harder to read (e.g., due to generics or callbacks)? (Yes -> Keep WET)

## 7. Red Flags and Remediation
Recognize these signals and take immediate action to simplify.

### Structural Red Flags
- **Pass-through methods**: Method A calls Method B, which calls Method C, all with the same signature. (Remedy: Inline or collapse layers).
- **Temporal Decomposition**: Code organized by "Step 1", "Step 2" instead of functional units. (Remedy: Group by responsibility).
- **Information Leakage**: A module's internal state or logic is spread across 3 other modules. (Remedy: Pull logic into the owner module).
- **Generic Obsession**: Creating `GenericManager<T>` when only `UserManager` exists. (Remedy: Rename to `UserManager` and remove generics).

### Cognitive Red Flags
- **The Club Test (Grug)**: You want to hit the code with a club after reading it for 10 minutes.
- **Dependency Fan-out**: One file imports > 10 other internal components. (Remedy: Split or group dependencies).
- **Whiteboard Necessity**: You cannot understand the flow without a diagram. (Remedy: Simplify control flow).

### Remediation Steps
1. **Inline First**: If an abstraction is confusing, inline it back into the caller to see the "real" code.
2. **Collapse Layers**: Merge modules that do too little (Shallow Modules).
3. **Values over Places**: Replace mutable objects with immutable data structures to remove time-dependencies.
4. **Delete Speculation**: Remove any code that is "prepared for the future" but unused today.

## 8. Case Study: Collapsing a Shallow Hierarchy
**Before (Over-engineered)**:
```ts
interface Shape { getArea(): number; }
abstract class BaseShape implements Shape { abstract getArea(): number; }
class Circle extends BaseShape { 
  constructor(private radius: number) { super(); }
  getArea() { return Math.PI * this.radius ** 2; }
}
class Square extends BaseShape {
  constructor(private side: number) { super(); }
  getArea() { return this.side ** 2; }
}
```
**After (Simplified)**:
```ts
type Shape = { type: 'circle'; radius: number } | { type: 'square'; side: number };
function getArea(shape: Shape): number {
  return shape.type === 'circle' ? Math.PI * shape.radius ** 2 : shape.side ** 2;
}
```
**Why?**: Removed 3 abstractions (interface, abstract class, class structure) in favor of a simple data type and a function.

## 9. Glossary of Simplicity
- **Complecting**: Interweaving concerns so they cannot be understood or changed independently.
- **Shallow Module**: A module with a complex interface relative to its internal logic.
- **Deep Module**: A module with a simple interface hiding significant implementation complexity.
- **Information Leakage**: When an internal design decision in one module is visible in other modules.
- **Cognitive Load**: The mental effort required to process information in a system.
- **YAGNI**: "You Ain't Gonna Need It"—avoiding speculative features.
- **WET**: "Write Everything Twice"—preferring duplication over wrong abstraction.
- **Abstraction Demon**: The psychological urge to build generic solutions for specific problems.
- **Pass-through**: A redundant layer of indirection that adds no value.
- **Change Amplification**: When one logical change requires many small edits across the codebase.
- **Temporal Coupling**: When the correctness of a system depends on the order of execution of its parts.
- **Place-Oriented Programming**: Focusing on "where" things are (mutable state) rather than "what" they are (values).

## 10. Summary Checklist for Code Reviews
When reviewing code for simplicity, ask:
1. **What is the single responsibility here?**
2. **Can I delete this abstraction and keep the code readable?**
3. **Is this solving a problem we have today or a problem we might have tomorrow?**
4. **Is the interface simpler than the implementation?**
5. **How many things do I need to know to change this logic?**

## 11. Practitioner's Cheat Sheet
| Task | Strategy | Key Framework |
| --- | --- | --- |
| Starting a feature | Build concrete first | Beck's "Make it work" |
| Found duplication | Wait for 3rd time | Rule of Three |
| Evaluating design | Check depth | Shallow Module Score |
| Adding a flag | Apply YAGNI | 5-Question Checklist |
| Refactoring | Remove complecting | Isolation Test |

**Final Rule**: When in doubt, choose the solution that is easier to delete. Git is your undo button; don't be afraid to throw away "clever" code that adds complexity.
