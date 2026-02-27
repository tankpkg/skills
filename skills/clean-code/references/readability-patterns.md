# Readability Patterns

Sources: Ousterhout (A Philosophy of Software Design), Martin (Clean Code), Boswell & Foucher (The Art of Readable Code), Beck (Implementation Patterns)

Covers: cognitive load management, visual structure, self-documenting code, code narrative flow, comment guidelines, readability review checklist.

## Cognitive Load Management

Cognitive load is the total amount of mental effort being used in the working memory. In code, this effort is consumed by tracking dependencies, deciphering obscure logic, and maintaining state.

### Cognitive Load Score (CLS) Components
Use this heuristic to evaluate when a block of code becomes too difficult to safely maintain.

```
COGNITIVE LOAD SCORE = (External Dependencies × 2) + (Implicit Assumptions × 3) + (Indentation Depth × 1)
```

*   **External Dependencies:** Count of distinct concepts (classes, APIs, state) the reader must keep in mind.
*   **Implicit Assumptions:** Hidden requirements (e.g., "this list must be sorted", "this global must be set").
*   **Indentation Depth:** The physical nesting level. Each level multiplies the mental stack depth.

| Score | Rating | Action Required |
|-------|--------|-----------------|
| < 10 | Optimal | Maintain and preserve clarity. |
| 10-15 | High | Monitor; consider extracting variables or helpers. |
| > 15 | Critical | Must refactor; split logic or simplify dependencies. |

### Readability Threshold Rules

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| **Function Length** | <= 20 lines | Fits in one "mental screen". |
| **Parameter Count** | <= 3 | Working memory capacity (Miller's Law). |
| **Nesting Depth** | <= 3 levels | Exponential increase in state-tracking effort. |
| **Lines per File** | 200-500 | Navigable without scrolling fatigue. |
| **Path Complexity** | <= 10 | Mental limit for tracing execution paths. |

### Types of Cognitive Load

| Type | Source | Goal | Strategy |
|------|--------|------|----------|
| **Intrinsic** | The core problem domain. | Respect | Isolate and name clearly. |
| **Extraneous** | Poor naming, deep nesting, noise. | Eliminate | Refactor for locality and simplicity. |
| **Germane** | Effort spent building a mental model. | Support | Use consistent patterns and abstractions. |

## Visual Architecture

Whitespace and grouping communicate code structure more effectively than syntax alone. Proper visual structure allows a developer to "scan" rather than "read" every line.

### Whitespace as Architecture
Blank lines act as visual paragraph breaks. They define the "Lead" and "Supporting" sections of a code block.

#### Before (Visual Noise):
```python
def process_payment(order):
    if not order.is_valid():
        raise ValidationError()
    payment = Payment(order.total)
    payment.process()
    order.status = 'paid'
    order.save()
    send_confirmation_email(order.customer)
    update_inventory(order.items)
    log_transaction(payment)
```

#### After (Visual Structure):
```python
def process_payment(order):
    # Validation
    if not order.is_valid():
        raise ValidationError()
    
    # Payment processing
    payment = Payment(order.total)
    payment.process()
    
    # Order finalization
    order.status = 'paid'
    order.save()
    
    # Side effects (grouped by similarity)
    send_confirmation_email(order.customer)
    update_inventory(order.items)
    log_transaction(payment)
```

### Horizontal Density & Alignment
Line length should stay within the 80-120 character range to prevent "tunnel vision" or excessive eye scanning.

| Length | Readability | Action |
|--------|-------------|--------|
| < 80 chars | Optimal | Ideal for focus. |
| 80-120 chars | Good | Acceptable for most contexts. |
| > 120 chars | Poor | Break into multiple lines. |

### Vertical Ordering: The Newspaper Metaphor
Organize files and classes so the most important, high-level information is at the top.
1. **Headline:** File name and primary export. Tells the reader "what is this?".
2. **Lead Paragraph:** The main public entry point. Tells the reader "how does it start?".
3. **Body:** Intermediate logic and orchestration. Tells the reader "how is it coordinated?".
4. **Footnotes:** Lowest-level implementation details and helper functions. Tells the reader "how is it actually done?".

#### Newspaper Example:
```python
def generate_monthly_report(month, year):
    """Headline/Lead: Generate comprehensive monthly sales report."""
    sales_data = fetch_sales_data(month, year)
    analysis = analyze_trends(sales_data)
    return format_report(analysis)

# Body/Footnotes appear below as supporting details
def fetch_sales_data(month, year):
    # Low-level DB query details...
    return db.query("SELECT * FROM sales WHERE month = %s", (month,))
    
def analyze_trends(sales_data):
    # Algorithmic logic...
    
def format_report(analysis):
    # Formatting details...
```

## Self-Documenting Structure

Self-documenting code uses structure and naming to explain intent, reducing the need for separate comments.

### Information Packing in Naming
Pack units, state, and constraints directly into variable names to eliminate ambiguity.

| Ambiguous Name | Information-Packed Name | Benefit |
|----------------|-------------------------|---------|
| `delay = 5` | `delay_seconds = 5` | Eliminates unit confusion. |
| `url = get()` | `unsanitized_url = get()` | Signals security risk. |
| `size = 100` | `max_byte_size = 100` | Defines constraints and units. |
| `limit = 10` | `min_inclusive_limit = 10` | Clarifies boundary conditions. |

### Explanatory Variables
Extract complex boolean logic or arithmetic into named variables. This gives a name to an anonymous concept.

```typescript
// Before
if (val > 100 && status === 'ACTIVE' && !isOverridden) { ... }

// After
const isEligibleForDiscount = val > 100 && status === 'ACTIVE';
const canProceed = isEligibleForDiscount && !isOverridden;

if (canProceed) { ... }
```

### Composed Method
Every method should consist of calls to other methods, all at the same level of abstraction. This makes the high-level logic immediate.

```python
def make_sandwich():
    # All at the same "zoom level"
    prepare_bread()
    apply_fillings()
    close_sandwich()
```

### Guard Clauses as Documentation
Handle edge cases and invalid states first. This flattens the code and documents preconditions explicitly.

```python
def calculate_rate(user):
    if user is None: return 0
    if not user.active: return 0
    
    # Main logic is now clearly isolated from edge cases
    return user.base_rate * user.multiplier
```

## Code Narrative & Abstraction

Code should read like a top-down narrative, maintaining a consistent "zoom level" within any single function.

### Zoom Levels
| Level | Focus | Example |
|-------|-------|---------|
| **L1: System** | Flow between modules | "Fetch data from API, then save to DB." |
| **L2: Module** | Coordination of tasks | "Validate inputs, orchestrate service calls." |
| **L3: Logic** | Algorithms and data flow | "Filter items, calculate totals, handle errors." |
| **L4: Detail** | Implementation specifics | "Regex patterns, bitwise ops, raw SQL." |

**The Step-Down Rule:** Every function should be followed by those at the next level of abstraction. This allows the reader to follow the implementation details as they read down the file.

## Intentional Commenting

Comments should only exist when the code itself cannot communicate the necessary context.

### The Comment Decision Tree
1. Can I rename this variable/function to explain it? -> **Yes: Do it.**
2. Can I extract this into an explanatory variable? -> **Yes: Do it.**
3. Is this explaining *what* is happening? -> **Yes: Delete it (the code shows what).**
4. Is this explaining *why* a non-obvious decision was made? -> **Yes: Keep it.**

### Comment Types
| Type | Purpose | Convention |
|------|---------|------------|
| **Why** | Context/Rationale | "Using linear search here because list is small (<5)." |
| **Warning** | Consequence/Risk | "WARNING: Not thread-safe. Must call inside mutex." |
| **TODO** | Debt/Future Work | "TODO(author): Refactor to async [Issue #123]" |

## Readability Review Checklist

Use this detailed 40-point rubric to score code during reviews. A score below 25 requires immediate refactoring.

### 1. Naming & Intent (10 pts)
- [ ] **Proportionality:** Name length proportional to scope? (2)
- [ ] **Predicates:** Boolean variables are predicates (is/has/can)? (2)
- [ ] **Searchability:** Names are unique and searchable (no single letters)? (2)
- [ ] **Pronounceability:** Names can be spoken aloud without confusion? (1)
- [ ] **Abstraction:** Names reveal intent without reading implementation? (3)

### 2. Visual & Structural (10 pts)
- [ ] **Paragraphs:** Whitespace used to group conceptual paragraphs? (2)
- [ ] **Architecture:** "Newspaper" order (High-level -> Detail)? (3)
- [ ] **Density:** Line length < 100 characters? (2)
- [ ] **Alignment:** Horizontal alignment used for related assignments? (1)
- [ ] **Locality:** Code that changes together lives together? (2)

### 3. Logic & Flow (10 pts)
- [ ] **Preconditions:** Guard clauses used for early returns? (3)
- [ ] **Nesting:** Indentation depth <= 3 levels? (2)
- [ ] **Positivity:** Positive conditionals preferred over negative? (2)
- [ ] **Zoom Levels:** Consistent abstraction level in every function? (2)
- [ ] **Simplicity:** No "magic" bits or language-specific tricks? (1)

### 4. Communication & Debt (10 pts)
- [ ] **Rationale:** Comments explain "Why", not "What"? (4)
- [ ] **Hygiene:** No commented-out code or dead code present? (2)
- [ ] **Constants:** Magic numbers replaced with named constants? (2)
- [ ] **TODOs:** Are specific, assigned, and linked to issues? (2)

| Total Score | Readability Grade |
|-------------|-------------------|
| 35-40 | **A (Excellent):** Clean, maintainable, and obvious. |
| 28-34 | **B (Good):** Minor improvements possible. |
| 20-27 | **C (Fair):** Significant cognitive load; refactor soon. |
| < 20 | **F (Fail):** High risk; refactor before merging. |

### The Readability Pyramid

```
                    / \
                   /   \
                  / AI  \          - AI can generate code
                 /_______\
                /         \
               /  Testing  \       - AI can write tests
              /_____________\
             /               \
            /  Architecture   \    - AI struggles here
           /                   \
          /_____________________\
         /                       \
        /    Readability &        \  - Humans excel here
       /     Maintainability       \
      /_____________________________\
```

In 2026, with AI generating code, human value is concentrated in ensuring long-term maintainability through these patterns.

## Readability vs. Cleverness

"Everyone knows that debugging is twice as hard as writing a program in the first place. So if you're as clever as you can be when you write it, you are, by definition, not smart enough to debug it." - Brian Kernighan

### The Cleverness Spectrum

```
Simple <----------------------------------------> Clever
  ^                                                ^
  Boring but maintainable                  Impressive but unmaintainable
```

**Target: Maintain a position at least 80% towards the "Simple" side.**

### The 3am Test
Ask: "If I was paged at 3am and had to fix a bug in this code while half-asleep, could I?"
- **Clever code** (one-liners, complex bitwise ops, deep recursion) requires high-octane brain power to parse. It fails the 3am test.
- **Readable code** uses "boring" but familiar patterns that the brain processes automatically.

### Cleverness vs. Readability Comparison

| Feature | Clever Approach (Avoid) | Readable Approach (Prefer) |
|---------|-------------------------|---------------------------|
| **Logic** | `return !!(x & (x - 1)) ? 0 : 1;` | `return is_power_of_two(x);` |
| **Flow** | Nested ternary operators. | If/Else or Guard Clauses. |
| **Iteration** | Single-line complex list comprehension. | Named steps with explanatory variables. |
| **Types** | Overloaded "any" or generic objects. | Explicit interfaces and domain types. |

### Formatting as Communication

Formatting is not just aesthetics; it is a communication protocol. Consistency reduces the effort required to "sync" with the code's rhythm.

1. **Establish Team Conventions:** Document rules for brace placement, indentation (2 vs 4 spaces), and naming (snake_case vs camelCase).
2. **Automate the Mundane:** Use formatters (Prettier, Black, Gofmt) to remove "style" from the cognitive load budget entirely. A developer should never have to think about a semicolon or a bracket.
3. **Enforce in CI:** Ensure that code which doesn't match the style guide cannot be merged. This prevents "style drift" and keeps the narrative flow consistent across authors.

### Rule of 7 (Miller's Law)
The human mind can hold approximately 7 (plus or minus 2) items in working memory. Readability patterns work by reducing the number of "items" the reader must track.
- **Chunking:** Group variables into meaningful objects to reduce the count.
- **Focus:** Keep function parameters under 4 to stay within the optimal "immediate recall" range.
- **Visual Pauses:** Keep file "paragraphs" under 7 lines to avoid overwhelming the reader's visual stack.
- **Nesting:** Limit nesting to 3 levels. Each level adds a "stack frame" to the reader's memory. Exceeding 3 usually forces a memory swap, leading to logic errors.
