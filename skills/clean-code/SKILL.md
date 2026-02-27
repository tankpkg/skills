---
name: "@tank/clean-code"
description: |
  Reusable, modular, performant, readable code — guided by KISS, SOLID, and
  pragmatic design. Covers code smell detection, refactoring recipes, function
  design, KISS/YAGNI decision frameworks, modularity (coupling, cohesion,
  boundaries), performance-aware patterns, and readability through cognitive
  load management. Synthesizes Martin (Clean Code), Ousterhout (A Philosophy
  of Software Design), Fowler (Refactoring), Metz (Practical OOD), Hickey
  (Simple Made Easy), Beck (Implementation Patterns), grugbrain.dev.

  Trigger phrases: "clean code", "refactor", "code smell", "code review",
  "code quality", "KISS", "keep it simple", "SOLID", "single responsibility",
  "DRY", "YAGNI", "over-engineered", "too complex", "simplify", "modularity",
  "coupling", "cohesion", "dependency", "reusable", "modular", "performance",
  "readability", "cognitive load", "naming", "function design", "extract method",
  "technical debt", "maintainability", "is this too abstract", "should I abstract",
  "N+1", "data structure"
---

# Clean Code

Write reusable, modular code with performance and readability in mind.

## Core Philosophy

1. **Code is read 10x more than written.** Optimize for the reader.
2. **Complexity is the apex predator.** Fight it at every level — function, module, system.
3. **Make the change easy, then make the easy change.** Small steps beat big rewrites.
4. **Don't build what you don't need.** Defer abstraction until the 3rd occurrence.
5. **Profile before optimizing, but design without obvious perf disasters.**

## Working Mode

1. Identify the smallest unit of change.
2. Confirm tests exist or add a characterization test.
3. Apply one refactoring at a time.
4. Re-run tests and reassess complexity.

## Quick Smell -> Fix Mapping

| Smell | Fix |
| --- | --- |
| Long method (>20 lines) | Extract Method |
| Magic number | Extract Constant |
| Feature envy | Move Method |
| Primitive obsession | Introduce Value Object |
| Data clumps | Introduce Parameter Object |
| Switch on type codes | Replace Conditional with Polymorphism |
| God class (>200 lines) | Extract Class |
| Pass-through methods | Collapse layers |
| Over-abstraction | Inline, delete unused generics |

## KISS Decision Framework

Before adding abstraction, answer these in order:

1. Have I seen this pattern 3+ times? NO -> Stop. Wait.
2. Is the interface simpler than the implementation? NO -> Shallow module, don't abstract.
3. Can I explain it to a junior in 5 minutes? NO -> Too complex.
4. Will it survive 3+ requirement changes? NO -> Premature.
5. All YES -> Abstract it.

**Shallow Module Score:** `(params + exceptions + concepts) / lines of logic`
- Score > 0.5 -> likely over-engineered.

**YAGNI Checklist — before building ANY feature:**
- Is this a CURRENT, validated requirement?
- Has a user explicitly requested it?
- Will it ship in the next release?
- Is cost of delay > cost of building?
- Any NO -> Defer.

See `references/kiss-and-simplicity.md` for full decision trees.

## SOLID Quick Reference

| Principle | One-liner | Signal it's violated |
| --- | --- | --- |
| Single Responsibility | One reason to change | Class description needs "and" |
| Open/Closed | Extend without modifying | Every new type requires editing existing code |
| Liskov Substitution | Subtypes replace base types | Subclass throws "not supported" |
| Interface Segregation | Small, focused interfaces | Implementors stub methods with `throw` |
| Dependency Inversion | Depend on abstractions | Business logic imports DB/HTTP libraries |

## Modularity Checklist

| Check | Target |
| --- | --- |
| Coupling | Data coupling (lowest). Eliminate content/common coupling. |
| Cohesion | Functional (highest). Refactor coincidental/logical. |
| Depth ratio | `functionality / public API > 10` |
| Dependency direction | Inward toward business rules |
| Composition vs inheritance | Default to composition. Inherit only for true "is-a" with >80% behavior reuse. |

See `references/modularity-and-design.md` for coupling/cohesion hierarchies.

## Performance Awareness

Do NOT optimize prematurely. DO avoid obvious disasters:

| Anti-Pattern | Signal | Fix |
| --- | --- | --- |
| N+1 fetches | Loop contains query/API call | Batch load or eager load |
| Nested loops on same data | O(n^2) with large n | Convert inner to hash set |
| Allocation in hot loop | Object creation per iteration | Hoist, reuse, or pool |
| String concat in loop | Immutable rebuilds | StringBuilder or join() |
| Computing unused results | Expensive call before guard | Move guards first |
| No TTL on cache | Stale data forever | Always set TTL |

See `references/performance-awareness.md` for data structure selection and caching decisions.

## Readability Rules

| Rule | Target |
| --- | --- |
| Function length | ≤ 20 lines |
| Parameters | ≤ 3 (use parameter object above) |
| Nesting depth | ≤ 3 levels (use guard clauses) |
| Cyclomatic complexity | ≤ 10 |
| Abstraction consistency | All statements at same zoom level |

**The 3am Test:** Would you understand this at 3am during an outage?

See `references/readability-patterns.md` for cognitive load scoring and review checklist.

## Naming Rules

| Element | Rule | Example |
| --- | --- | --- |
| Variable | Noun | `userCount` |
| Function | Verb | `calculateTotal()` |
| Boolean | `is/has/can` prefix | `isActive` |
| Class | Noun | `InvoicePrinter` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |

## Function Design Rules

| Rule | Target |
| --- | --- |
| Max parameters | 3 (introduce parameter object when >3) |
| Max lines | 20-30 (exceptions: table lookups, state machines) |
| Max nesting depth | 2 |
| CQS | Queries return data; commands change state. Never both. |

See `references/function-design.md` for parameter design, CQS, and complexity details.

## Anti-Patterns

| Anti-pattern | Remedy |
| --- | --- |
| Long parameter lists | Introduce Parameter Object |
| Flag arguments | Split into two functions |
| Shotgun surgery | Consolidate responsibility |
| Speculative generality | Inline or delete unused abstractions |
| Comments as deodorant | Refactor, then comment why |
| Premature generics | Concrete until 3rd type |
| Configurable everything | Build for current need, add config when requested |

## Reference Index

| File | Contents |
| --- | --- |
| `references/code-smells.md` | 10 code smells with detection heuristics, before/after examples, refactoring recipes |
| `references/refactoring-recipes.md` | Step-by-step refactoring patterns: Extract Method, Introduce Parameter Object, Replace Conditional, etc. |
| `references/function-design.md` | Naming, parameters, CQS, function length, cyclomatic/cognitive complexity, depth vs width |
| `references/kiss-and-simplicity.md` | KISS principle, over-engineering detection, YAGNI, complexity budgets, simplicity vs DRY |
| `references/modularity-and-design.md` | Coupling types, cohesion spectrum, module boundaries, dependency direction, composition vs inheritance |
| `references/performance-awareness.md` | Data structure selection, N+1, unnecessary computation, memory, caching, algorithmic awareness |
| `references/readability-patterns.md` | Cognitive load, visual structure, self-documenting code, narrative flow, review checklist |
