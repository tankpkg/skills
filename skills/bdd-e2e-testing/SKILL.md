# BDD E2E Testing

## Hard Rules

These are non-negotiable. Violating any of these means the work is wrong.

1. **ALL tests go in `.bdd/` at project root.** Never `tests/`, `e2e/`,
   `__tests__/`, or any other location. The `.bdd/` directory is the single
   source of truth for all BDD test artifacts.

2. **ZERO mocks. ZERO stubs. ZERO fakes.** Every scenario runs against the
   REAL system with REAL dependencies. For web apps: real browser, real
   backend, real DB — never `page.route()`, MSW, or nock. For libraries:
   real infrastructure in Docker (real RabbitMQ, real Redis, real DB) —
   never mock the transport or protocol layer. The only exception:
   third-party services you cannot control (payment gateways, SMS providers).

3. **Code is guilty until proven innocent.** When a test fails, the
   APPLICATION code is wrong — not the test. Fix the application, document
   the fix in `qa/resolutions/`, then re-verify. Never weaken a test to
   make it pass.

4. **Document everything.** Every test run produces findings. Every fix
   produces a resolution. The `.bdd/qa/` directory is the audit trail.

## Mandatory Directory Structure

```
.bdd/
  features/              # Gherkin specs (what SHOULD work)
    auth/
      login.feature
  steps/                 # Step definitions (by domain, NOT by feature)
    auth.steps.ts
  interactions/          # Interaction layer (adapts by archetype)
  support/               # Fixtures, hooks, config
    fixtures.ts
    hooks.ts
  qa/
    findings/            # What happened when tests ran
    resolutions/         # What was changed to fix failures
```

The `interactions/` directory adapts to what you're testing:

| Archetype | `interactions/` contains | Examples |
|-----------|--------------------------|----------|
| Web app | Page Objects | `login.page.ts`, `checkout.page.ts` |
| Library/package | Test helpers + fixtures | `pika_app.py`, `docker_fixtures.py` |
| REST API | API clients | `orders.client.ts`, `auth.client.ts` |
| CLI tool | Command runners | `cli.runner.ts`, `output.parser.ts` |
| Message queue | Broker helpers | `rabbit.helper.py`, `test_consumers.py` |

Create this structure FIRST before writing any test code.

## Core Philosophy

1. **BDD is collaboration first, automation second** — Feature files are
   shared artifacts born from Discovery workshops, not test scripts written
   by developers alone.

2. **Real E2E means zero mocks** — Every scenario runs against the actual
   system with real dependencies. The "end user" varies by archetype: a
   person in a browser, a developer consuming a library API, an operator
   running CLI commands. If any dependency is faked, it is not E2E.

3. **Declarative over imperative** — Scenarios describe WHAT the system does,
   not HOW the user clicks. "Given Emma has items in her cart" beats
   "Given the user clicks the add button 3 times".

## Testing Archetypes

The "end user" is whoever consumes your software. BDD describes behavior
from THEIR perspective against REAL infrastructure.

| What you test | End user | BDD tool | "Real E2E" means |
|---|---|---|---|
| Web app | Person in a browser | playwright-bdd / Playwright | Real browser, real backend, real DB |
| Library/package | Developer consuming the API | pytest-bdd / Behave | Real deps in Docker, zero mocks |
| REST API | API consumer / frontend | Playwright API / Supertest | Real HTTP, real DB |
| CLI tool | Person running commands | subprocess / pytest-bdd | Real filesystem, real processes |
| Message queue | Service developer | pytest-bdd + real broker | Real RabbitMQ/Kafka in Docker |

## Verification Workflow

This is the mandatory sequence. Do not skip steps.

| Step | Action | Output |
|------|--------|--------|
| 1. Write features | Describe expected behavior in Gherkin | `.bdd/features/*.feature` |
| 2. Implement steps | Wire Given/When/Then to real system interactions | `.bdd/steps/*.steps.{ts,py}` |
| 3. Run against real system | Execute with real dependencies, zero mocks | Test results |
| 4. Document findings | Record what passed, what failed, evidence | `.bdd/qa/findings/*.md` |
| 5. Fix the code | Change APPLICATION code, never weaken tests | Source code changes |
| 6. Document resolution | Record what changed, why, verification result | `.bdd/qa/resolutions/*.md` |
| 7. Re-run and verify | Confirm the fix works, update findings | Updated findings |

See `references/qa-workflow.md` for findings/resolution format and examples.

## Quick-Start

### "I need to set up BDD E2E tests for a web app"

| Step | Action |
|------|--------|
| 1. Create `.bdd/` | Create the mandatory directory structure above |
| 2. Choose framework | New project: `playwright-bdd`. Existing Cucumber: `@cucumber/cucumber` + Playwright. See `references/playwright-bdd-setup.md` |
| 3. Write first feature | Start with a smoke test. Declarative style. See `references/gherkin-writing.md` |
| 4. Implement steps | Wire to Playwright via Page Objects. See `references/step-definitions.md` |
| 5. Run and document | Run tests, document findings. See `references/qa-workflow.md` |
| 6. Set up CI | GitHub Actions pipeline. See `references/test-architecture.md` |

### "I need to test a library, CLI tool, or service (no browser)"

| Step | Action |
|------|--------|
| 1. Create `.bdd/` | Same structure, but `interactions/` holds test helpers and Docker fixtures instead of Page Objects |
| 2. Choose framework | Python: `pytest-bdd`. TypeScript: `playwright-bdd` with `request` fixture (no browser). See `references/multi-language-frameworks.md` |
| 3. Write first feature | Describe behavior from the developer/operator perspective. See `references/gherkin-writing.md` |
| 4. Implement steps | Wire to real infrastructure via interaction layer. See `references/step-definitions.md` |
| 5. Run and document | Run against real deps (Docker), document findings. See `references/qa-workflow.md` |

### "My BDD tests are brittle and hard to maintain"

| Symptom | Fix | Reference |
|---------|-----|-----------|
| Steps break when UI/API changes | Move details into interaction layer (Page Objects, helpers) | `references/step-definitions.md` |
| Feature files read like code | Rewrite declaratively, raise abstraction | `references/gherkin-writing.md` |
| Steps can't be reused | Organize by domain, use shared step libraries | `references/step-definitions.md` |
| Scenarios take too long | Bypass UI for setup (API seeding), parallelize | `references/test-architecture.md` |
| Agent mocks dependencies | HARD RULE VIOLATION. Remove all mocks, use real services/infra | `references/step-definitions.md` |

## Decision Trees

### Which framework?

| Signal | Recommendation |
|--------|---------------|
| TypeScript web app | `playwright-bdd` — native Playwright runner, fixtures, parallel |
| TypeScript API-only (no browser) | `playwright-bdd` with `request` fixture — same DX, no browser overhead |
| Existing Cucumber.js ecosystem | `@cucumber/cucumber` + Playwright — keep existing features/steps |
| Python web app | `pytest-bdd` + Playwright |
| Python library/service/CLI | `pytest-bdd` + Docker fixtures (Testcontainers or docker-compose) |
| Java project | Cucumber-JVM or Serenity BDD |
| .NET project | Reqnroll (SpecFlow successor) |

### When does BDD add value?

| Signal | BDD worth it? |
|--------|---------------|
| Non-technical stakeholders review scenarios | **Yes** — shared language pays off |
| Three Amigos workshops happen regularly | **Yes** — Discovery drives quality |
| Solo developer, no collaboration | **No** — overhead without collaboration benefit |
| Rapidly changing UI, stable business rules | **Yes** — declarative scenarios survive UI rewrites |
| Library/API with complex behavior contracts | **Yes** — Gherkin documents the contract from the consumer's perspective |

## Reference Files

| File | Contents |
|------|----------|
| `references/qa-workflow.md` | Verification workflow, findings format, resolution format, re-verification loop, examples |
| `references/playwright-bdd-setup.md` | playwright-bdd setup with `.bdd/` structure, createBdd(), defineBddConfig, bddgen, fixtures, hooks, complete working example |
| `references/cucumber-playwright-traditional.md` | Traditional @cucumber/cucumber + Playwright setup with `.bdd/` structure, Custom World, hooks, formatters, complete example |
| `references/gherkin-writing.md` | Declarative Gherkin craft, good/bad pairs, Scenario Outline, Background, tags, Data Tables, anti-patterns |
| `references/step-definitions.md` | Step patterns, Page Object Model, Screenplay, action classes, no-mocking rules, assertion patterns |
| `references/bdd-collaboration.md` | Three Amigos, Example Mapping, Feature Mapping, living documentation |
| `references/test-architecture.md` | 3-layer architecture, `.bdd/` project structure, CI/CD pipeline, reporting, parallel execution |
| `references/multi-language-frameworks.md` | TypeScript, Python, Java, .NET framework selection and migration |
