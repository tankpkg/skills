# BDD E2E Test Architecture, CI/CD, and Reporting

Sources: Smart and Molak (BDD in Action), Wynne and Hellesoy (The Cucumber Book), community best practices

## 3-Layer Automation Architecture

Smart and Molak define three layers that separate business intent from technical implementation.

### Layer 1: Business Rules (Feature Files)

Gherkin scenarios express WHAT the system should do in domain language. No locators, no endpoints.

```gherkin
Feature: Checkout
  Scenario: Free shipping on large orders
    Given Tracy has a cart totaling $150
    When she proceeds to checkout
    Then shipping should be free
```

### Layer 2: Business Flow (Step Definitions)

Steps translate Gherkin into domain actions. They orchestrate WHAT happens but not HOW. This layer remains stable when the UI changes.

```typescript
Given('Tracy has a cart totaling ${int}', async ({ cartPage }, total: number) => {
  await cartPage.addItemsToTotal(total);
});

When('she proceeds to checkout', async ({ checkoutPage }) => {
  await checkoutPage.startCheckout();
});

Then('shipping should be free', async ({ checkoutPage }) => {
  await checkoutPage.expectShippingCost(0);
});
```

### Layer 3: Technical (Interaction Layer)

Handles HOW to interact with the system. When the implementation changes, only this layer changes. For web apps this is Page Objects; for libraries/services this is test helpers and Docker fixtures; for CLIs this is command runners.

```typescript
export class CheckoutPage {
  constructor(private page: Page) {}

  async startCheckout() {
    await this.page.getByRole('button', { name: 'Checkout' }).click();
    await this.page.waitForURL('**/checkout');
  }

  async expectShippingCost(amount: number) {
    const shipping = this.page.getByTestId('shipping-cost');
    await expect(shipping).toHaveText(`$${amount.toFixed(2)}`);
  }
}
```

### Why 3 Layers Matter

| Concern | Layer | Changes when... |
|---------|-------|-----------------|
| Business rules | Feature files | Requirements change |
| Workflow orchestration | Step definitions | Process flow changes |
| System interaction | Interaction layer (Page Objects / test helpers / CLI runners) | Implementation changes |

Violating this separation (locators in step definitions, business logic in interaction layer) creates the "brittle test" anti-pattern -- the primary cause of BDD automation failure.

## Project Structure

### Web App Variant (TypeScript)

```
project-root/
  .bdd/
    playwright.config.ts        # Playwright + BDD config
    features/
      checkout/
        checkout.feature
        checkout-edge-cases.feature
      auth/
        login.feature
        registration.feature
    steps/
      checkout.steps.ts         # Steps by domain, NOT by feature
      auth.steps.ts
      common.steps.ts           # Shared navigation/assertion steps
    interactions/               # Page Objects for web archetype
      checkout.page.ts
      login.page.ts
      components/
        header.component.ts
    support/
      fixtures.ts               # Playwright fixtures
      hooks.ts                  # Before/After hooks
      world.ts                  # (Cucumber runner: custom World)
      parameter-types.ts        # Custom Cucumber parameter types
    test-data/
      users.json                # Test personas
      products.json             # Seed data
    reports/
      .gitkeep                  # Generated reports (gitignored)
    .features-gen/              # Generated spec files (gitignored)
```

### Library/Service Variant (Python)

```
project-root/
  .bdd/
    features/
      messaging/
        consumption.feature
        redelivery.feature
      connection/
        reconnection.feature
    steps/
      messaging.steps.py
      connection.steps.py
      common.steps.py
    interactions/              # Test helpers instead of Page Objects
      messaging_app.py         # Wraps library's public API
      docker_fixtures.py       # Docker-based infra (RabbitMQ, Redis)
      message_helpers.py       # Publish/consume/assert helpers
    support/
      conftest.py              # pytest fixtures, Docker lifecycle
      parameter_types.py
    qa/
      findings/
      resolutions/
    docker-compose.test.yml    # Real infrastructure for tests
```

Key organization rules from Wynne and Hellesoy:
- Feature files organized by **functional area**, not by page or component
- Step definitions organized by **domain concept**, not by feature file
- One step definition file should serve multiple feature files
- Feature-coupled step definitions (one step file per feature) is an anti-pattern

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: BDD E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1-5'  # Weekday regression

env:
  CI: true
  BASE_URL: http://localhost:3000

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: cd .bdd && npx bddgen
      - run: npm run start:test &
      - run: npx wait-on $BASE_URL --timeout 30000
      - run: cd .bdd && npx playwright test --grep @smoke
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: smoke-report
          path: .bdd/playwright-report/
          retention-days: 7

  regression-tests:
    needs: smoke-tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: cd .bdd && npx bddgen
      - run: npm run start:test &
      - run: npx wait-on $BASE_URL --timeout 30000
      - run: cd .bdd && npx playwright test --shard ${{ matrix.shard }} --retries 2
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: results-${{ strategy.job-index }}
          path: |
            .bdd/playwright-report/
            .bdd/test-results/
          retention-days: 14

  merge-reports:
    needs: regression-tests
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { pattern: results-*, merge-multiple: true, path: all-results/ }
      - run: npx playwright merge-reports --reporter=html all-results/
      - uses: actions/upload-artifact@v4
        with:
          name: full-regression-report
          path: .bdd/playwright-report/
          retention-days: 30
```

### Tag-Based Test Selection

| Tag | Purpose | When to run |
|-----|---------|-------------|
| `@smoke` | Critical happy paths | Every push, pre-deploy |
| `@regression` | Full coverage | Nightly, pre-release |
| `@critical` | Revenue-impacting flows | Every push |
| `@slow` | Long-running scenarios | Nightly only |
| `@wip` | Work in progress | Never in CI (exclude) |
| `@flaky` | Known unstable tests | Quarantined, tracked |

```bash
cd .bdd && npx playwright test --grep @smoke                        # Smoke only
cd .bdd && npx playwright test --grep-invert "@slow|@flaky|@wip"    # Regression minus exclusions
cd .bdd && npx playwright test --grep @critical                     # Critical path on every PR
```

### Retry and Failure Capture

```typescript
// .bdd/playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI
    ? [['html'], ['junit', { outputFile: 'results.xml' }], ['json', { outputFile: 'results.json' }]]
    : [['html', { open: 'on-failure' }]],
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
});
```

## Reporting

### Report Format Selection by Audience

| Audience | Format | Tool | Key benefit |
|----------|--------|------|-------------|
| Developers | Playwright HTML | Built-in | Trace viewer, screenshots, step-by-step |
| QA / Test leads | Allure | allure-playwright | Trends, categories, history, flaky detection |
| CI/CD systems | JUnit XML | Built-in reporter | Universal CI integration (Jenkins, GitHub) |
| Stakeholders | Cucumber HTML | cucumber-html-reporter | Business-readable feature/scenario view |
| Custom dashboards | JSON | Built-in reporter | Programmatic access, custom aggregation |
| Compliance/audit | Living docs | Serenity/JS or Allure | Requirement traceability, evidence |

### Configuring Reporters

```typescript
// Playwright HTML (default, best for developers)
reporter: [['html', { open: 'never', outputFolder: '.bdd/reports/html' }]]

// Allure (best for QA teams tracking quality over time)
reporter: [['allure-playwright', { outputFolder: '.bdd/allure-results' }]]
// Then: cd .bdd && npx allure generate allure-results -o allure-report --clean
```

### Screenshot on Failure (Cucumber Runner)

For the Cucumber runner, attach screenshots manually in After hooks:

```typescript
After(async function (scenario) {
  if (scenario.result?.status === 'FAILED') {
    const screenshot = await this.page.screenshot({ fullPage: true });
    this.attach(screenshot, 'image/png');
  }
});
```

For playwright-bdd, `screenshot: 'only-on-failure'` in config handles this automatically.

## Test Data Management

### Strategy Comparison

| Strategy | Speed | Isolation | Complexity | Best for |
|----------|-------|-----------|------------|----------|
| API-based setup | Fast | High | Low | Most scenarios |
| Database seeding | Fast | Medium | High | Complex state |
| Factory functions | N/A | High | Medium | Data generation |
| Fixture files | N/A | Low | Low | Static reference data |

### API-Based Setup (Recommended)

```typescript
Given('a verified customer with {int} orders', async ({ request }, orderCount: number) => {
  const customer = await request.post('/api/test/customers', {
    data: { verified: true, orderCount },
  });
  this.customerId = (await customer.json()).id;
});
```

### Factory Functions

Inspired by FactoryGirl/FactoryBot pattern from Wynne and Hellesoy:

```typescript
function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: randomUUID(),
    name: 'Tracy',
    email: `tracy-${Date.now()}@test.com`,
    role: 'customer',
    ...overrides,
  };
}
```

### Test Isolation Rules

From Wynne and Hellesoy: "Leaky scenarios" (data dependency between tests) is a primary anti-pattern.

- Each scenario gets a fresh World/context (Cucumber enforces this)
- Use unique identifiers (timestamps, UUIDs) to prevent collision
- Prefer API setup over shared seed data
- Database truncation in Before hooks, not After (handles crashes)
- Never rely on execution order between scenarios

## Parallel Execution

### playwright-bdd Sharding

Playwright distributes test files across workers. Sharding splits across CI machines.

```bash
npx playwright test --workers 4              # Local: 4 parallel workers
npx playwright test --shard 1/4              # CI: distribute across machines
```

### Cucumber --parallel Flag

```bash
npx cucumber-js --parallel 4                 # Each worker gets its own World
```

### Worker Isolation Requirements

- **Unique test data**: Each worker creates data with unique identifiers
- **No shared mutable state**: Workers cannot share database rows
- **Independent browser contexts**: Playwright handles this automatically
- **Idempotent setup**: Before hooks must be safe to run concurrently

```typescript
// Good: unique email per test run
const email = `user-${Date.now()}-${Math.random().toString(36).slice(2)}@test.com`;

// Bad: fixed email that collides across workers
const email = 'testuser@test.com';
```

## Performance Optimization

### Reuse Authentication State

The single biggest performance win. Log in once, save state, reuse across tests.

```typescript
// .bdd/support/auth.setup.ts -- runs once before all tests
setup('authenticate as customer', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('tracy@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: '.bdd/.auth/customer.json' });
});

// .bdd/playwright.config.ts
projects: [
  { name: 'auth-setup', testMatch: /auth\.setup\.ts/ },
  {
    name: 'e2e-tests',
    dependencies: ['auth-setup'],
    use: { storageState: '.bdd/.auth/customer.json' },
  },
]
```

### Test Prioritization Strategy

| Priority | Category | Run frequency | Typical count |
|----------|----------|---------------|---------------|
| P0 | Smoke / critical path | Every push | 10-20 scenarios |
| P1 | Core business flows | Every PR merge | 50-100 scenarios |
| P2 | Edge cases, error paths | Nightly | 100-300 scenarios |
| P3 | Visual, accessibility | Weekly | 20-50 scenarios |

### Additional Performance Tips

- **API over UI for setup**: 10-50x faster than clicking through UI
- **Chromium only for speed**: Cross-browser only in nightly runs
- **Minimize navigation**: Group scenarios sharing a starting page using Background
- **No arbitrary waits**: Use `waitForSelector`, `waitForURL`, `expect` auto-retry
- **Screenshots only on failure**: Never capture on every step

## Checklist: Production-Ready BDD E2E Suite

- [ ] All tests in `.bdd/` directory at project root
- [ ] 3-layer architecture enforced (.bdd/features / .bdd/steps / .bdd/interactions)
- [ ] Feature files organized by domain, steps by concept
- [ ] CI pipeline with smoke (every push) and regression (nightly)
- [ ] Parallel execution configured (sharding for web, pytest-xdist for Python)
- [ ] Retry policy: 2 retries in CI, 0 locally
- [ ] Evidence captured on failure (screenshots for web, logs for services)
- [ ] Reports uploaded as CI artifact
- [ ] JUnit XML for CI status integration
- [ ] Test data isolated per scenario (no shared mutable state)
- [ ] Tags used for test selection (@smoke, @regression, @wip)
- [ ] Flaky tests quarantined with @flaky tag and tracked
- [ ] No arbitrary waits in test code
- [ ] Real infrastructure used (Docker for services, real browser for web)
- [ ] Reports accessible to both developers and stakeholders
