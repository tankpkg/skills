# Modularity and Design

Sources: Ousterhout (A Philosophy of Software Design), Martin (Clean Architecture), Metz (Practical Object-Oriented Design), Parnas (On Decomposing Systems), Feathers (Working Effectively with Legacy Code)

Covers: coupling types, cohesion spectrum, module boundaries, API surface, dependency direction, composition vs inheritance, package organization.

## 1. Coupling Hierarchy (Worst to Best)
Coupling measures the degree of interdependence between modules. High coupling makes code fragile and hard to change.

| Type | Severity | Detection Signal | Fix Strategy |
| :--- | :--- | :--- | :--- |
| **Content** | Pathological | Accessing private fields or internal state of another module. | Encapsulate state; expose behavior via public methods. |
| **Common** | High | Multiple modules sharing mutable global variables or data structures. | Use Dependency Injection; make shared data immutable. |
| **Control** | Moderate | Passing flags (booleans/enums) to tell a module how to do its job. | Replace flags with polymorphism or separate methods. |
| **Stamp** | Low-Mod | Passing large objects when only a few fields are used. | Pass only needed primitives or use focused interfaces. |
| **Data** | Best | Modules communicate only by passing necessary data (parameters). | Maintain narrow, explicit interfaces; use value objects. |

### Control Coupling (Before/After)
**Before**: One module controls the internal logic of another by passing a flag.
```ts
function processOrder(order: Order, isExpress: boolean) {
  if (isExpress) {
    applyExpressShipping(order);
    notifyPrioritized(order);
  } else {
    applyStandardShipping(order);
  }
}
```

**After**: Use polymorphism to encapsulate the difference in behavior.
```ts
interface OrderStrategy {
  applyShipping(order: Order): void;
}
class ExpressStrategy implements OrderStrategy {
  applyShipping(order: Order) {
    applyExpressShipping(order);
    notifyPrioritized(order);
  }
}
```

## 2. Cohesion Spectrum
Cohesion measures how closely related the responsibilities inside a module are.

| Type | Quality | Code Signal | Fix |
| :--- | :--- | :--- | :--- |
| **Coincidental** | Worst | `Utils` or `Common` classes with unrelated methods. | Split by domain concept; move methods to their owners. |
| **Logical** | Very Low | Methods grouped by type (e.g., all "Export" methods in one class). | Use Strategy pattern or polymorphism. |
| **Temporal** | Low | Methods grouped because they happen at the same time (e.g., `init()`). | Group by information hiding, not by execution order. |
| **Procedural** | Moderate | Steps in a workflow grouped together; must be called in order. | Encapsulate the sequence; hide steps as private methods. |
| **Sequential** | High | The output of one step is the input to the next step. | Use pipelines or functional composition. |
| **Functional** | Best | Every part of the module contributes to a single, well-defined task. | Ensure Single Responsibility Principle (SRP) compliance. |

### Metz's Single Sentence Test
If you cannot describe a class's responsibility in one sentence without using "and" or "or", it likely lacks functional cohesion and should be split. 

**Example of Low Cohesion**:
`"This class handles user registration, sends welcome emails, AND calculates first-order discounts."`
**Fix**: Split into `UserRegistrar`, `WelcomeMailer`, and `DiscountCalculator`.

## 3. Module Boundaries
Modules should be formed around design decisions that are likely to change.

### The Secret-Hiding Principle (Parnas)
Design modules to hide a specific secret:
- **Data Structures**: The specific format of an internal cache or database record.
- **Hardware/API Details**: The specific library used for networking or the filesystem.
- **Business Policies**: The specific rules for tax calculation or discount tiers.

### Boundary Decision Tree
1. **Do they change for the same reason?** (Common Closure Principle)
   - If NO → Separate them.
2. **Do they share "secrets" (implementation details)?** (Parnas Principle)
   - If NO → Separate them.
3. **Can one be reused or released without the other?** (Common Reuse Principle)
   - If YES → Separate them.
4. **Do they serve different actors/stakeholders?**
   - If YES → Separate them.

## 4. API Depth and Information Hiding
Deep modules provide significant functionality through a simple interface.

### Ousterhout's Depth Ratio
A "Deep" module has a small interface relative to the complexity it encapsulates.
- **Goal**: High Functionality / Small API Surface.
- **Example (Deep)**: The Unix `open` system call. It hides thousands of lines of code dealing with file systems, disk drivers, and permissions behind a simple integer handle.
- **Example (Shallow)**: A class that provides getters and setters for every internal field. It provides no abstraction and forces callers to manage the internal state.

### Define Errors Out of Existence (Ousterhout)
Instead of forcing callers to handle errors, design the API so that "error" states are valid results or handled internally.
```ts
// Shallow: Caller must check existence
const item = cache.get("key");
if (!item) { /* error logic */ }

// Deep: Handles missing data internally
const item = cache.get("key", { default: "none" });
```

## 5. Dependency Direction
Dependencies must always point towards higher-level policy and business rules.

### Clean Architecture Layers (Inner = Stable, Outer = Volatile)
- **Entities (Domain)**: Core business rules. Most stable.
- **Use Cases**: Application-specific logic.
- **Interface Adapters**: Controllers, Repositories, Presenters.
- **Frameworks & Drivers**: UI, DB, External services. Most volatile.

### Dependency Inversion Principle (DIP)
When a high-level module (Service) needs a low-level module (Database), it should depend on an **Interface** instead of a concrete class.
```ts
// Violation: Service depends on concrete DB
class UserService {
  constructor(private db: PostgresDB) {} 
}

// DIP: Service depends on abstraction
interface UserRepository {
  save(user: User): void;
}
class UserService {
  constructor(private repo: UserRepository) {}
}
```

### Stable Dependencies Principle (SDP)
Depend in the direction of stability. A module's **Instability (I)** is calculated as:
`I = Outgoing Dependencies / (Incoming Dependencies + Outgoing Dependencies)`
- `I = 0`: Maximally stable (many depend on it, it depends on nothing).
- `I = 1`: Maximally unstable (nothing depends on it, it depends on many).
- **Rule**: A module should only depend on modules that are **more stable** than itself.

## 6. Composition vs Inheritance
Inheritance is the most rigid form of coupling. Composition provides flexibility through delegation.

### Decision Criteria: When to use Inheritance
Use inheritance ONLY when all these are true:
- It is a genuine **"is-a"** relationship (e.g., `SavingsAccount` is a `BankAccount`).
- The subclass uses **100%** of the superclass behavior (no "unsupported" methods).
- The hierarchy is **shallow** (max 2 levels).
- You are following the **Template Method** pattern (superclass defines the skeleton, subclass fills in steps).

### Tell, Don't Ask (Metz)
Do not ask an object for its data to make a decision. Instead, tell the object what to do. This preserves encapsulation and prevents "Feature Envy".
```ts
// Asking (Weak encapsulation)
if (user.status === "active") {
  user.sendNotification(msg);
}

// Telling (Strong encapsulation)
user.notifyIfActive(msg);
```

## 7. Package Organization
The folder structure should reveal the application's domain, not its framework.

### Layer vs Feature Organization
**Package by Layer**:
```
src/
  controllers/
  services/
  repositories/
```
- **Pros**: Easy for small teams; standard layout.
- **Cons**: Features are scattered; hard to see domain boundaries.

**Package by Feature (Screaming Architecture)**:
```
src/
  billing/
  shipping/
  inventory/
```
- **Pros**: High feature cohesion; easy to delete/extract modules; domain-centric.
- **Cons**: Shared code requires careful management.

## 8. Dependency Injection (DI)
DI removes the responsibility of creating dependencies from the module itself.

### The Hollywood Principle
"Don't call us, we'll call you."
The framework or orchestrator is responsible for providing dependencies. The component itself should never reach out to a global "Service Locator" or "Registry".

### When it's Overkill
- **Pure Functions**: Math utilities, string formatters, or date parsers.
- **Value Objects**: Small, immutable data structures (e.g., `Money`, `Address`).
- **Standard Libraries**: Built-in language functions (e.g., `Math.abs`).

## 9. Advanced Modularity Principles

### Law of Demeter (Principle of Least Knowledge)
A module should only talk to its immediate friends, not to friends of friends.
```ts
// Violation: "Train wreck" - coupling to internal structure of multiple objects
const url = user.getAccount().getProfile().getAvatarUrl();

// Fix: "Tell" the object to provide what is needed
const url = user.getAvatarUrl(); 
// The User class handles the delegation internally.
```

### The Seam Model (Feathers)
A **Seam** is a place where you can alter behavior without editing in that place.
- **Object Seams**: Using polymorphism and interfaces to swap implementations.
- **Compile/Link Seams**: Swapping libraries at build time (e.g., a test database driver).
- **Purpose**: Seams are essential for bringing legacy code under test.

### Stable Abstractions Principle (SAP)
A module should be as abstract as it is stable.
- **Stable Modules** (like Domain/Entities) should be **Abstract** (interfaces/abstract classes) to allow flexibility without changing the source code.
- **Unstable Modules** (like UI/Controllers) should be **Concrete** (actual implementations) because they are easy to change.

## 10. Module Intercommunication
How modules talk to each other defines the "chattiness" and coupling of the system.

### Direct Calls vs. Events
- **Direct Calls**: Synchronous, explicit, but creates a compile-time dependency. Use when the result of the call is immediately required.
- **Event-Driven (Pub/Sub)**: Asynchronous, decoupled, but harder to trace. Use when one module needs to notify others of a change without knowing who they are (e.g., `OrderPlaced` event).

### The Interface Segregation Principle (ISP)
Clients should not be forced to depend on methods they do not use.
- **Problem**: A `LargeInterface` with 50 methods used by 10 different clients who each only need 5.
- **Fix**: Split `LargeInterface` into 10 smaller, focused interfaces.

## 11. Common Modularity Anti-Patterns

| Anti-Pattern | Description | Fix |
| :--- | :--- | :--- |
| **Pass-Through Methods** | A module just calls another module with the same parameters. | Inline the method or merge the modules if the abstraction is too thin. |
| **Temporary Variables** | Methods communicate via class fields rather than parameters. | Use sequential cohesion; pass return values to the next step. |
| **Divergent Change** | One module is frequently changed in different ways by different requirements. | Extract classes; apply SRP. |
| **Shotgun Surgery** | One requirement change forces small changes across many modules. | Move related behaviors into a single module; apply CCP. |
| **God Class** | A single class that does everything and knows everything. | Split by domain actor or responsibility; use composition. |

## 12. Summary Checklist
- [ ] **Coupling**: Are we communicating via Data Coupling?
- [ ] **Cohesion**: Does every module have a single, functional purpose?
- [ ] **Boundaries**: Are we hiding secrets that are likely to change?
- [ ] **API Surface**: Is the module "deep" (high functionality, narrow interface)?
- [ ] **Dependency**: Do dependencies point toward higher-level policies?
- [ ] **Composition**: Are we using composition by default over inheritance?
- [ ] **Structure**: Does our package layout "scream" the system's purpose?
- [ ] **DI**: Are we injecting volatile dependencies rather than creating them?
- [ ] **Seams**: Have we created enough seams to allow for easy testing and future changes?
- [ ] **Abstraction**: Is the stability of the module matched by its level of abstraction?

---
*Generated by Clean Code Skill v1.0.0*
