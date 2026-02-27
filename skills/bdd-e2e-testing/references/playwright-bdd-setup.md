# playwright-bdd: Playwright-Native BDD Testing
Sources: Smart and Molak (BDD in Action), Wynne and Hellesoy (The Cucumber Book), playwright-bdd documentation

## Why playwright-bdd Over @cucumber/cucumber

playwright-bdd runs Gherkin features through Playwright's native test runner. Feature files are transpiled to `.spec.ts` files via `bddgen`, then executed with `npx playwright test`. This preserves the full Playwright ecosystem: fixtures, parallel workers, trace viewer, HTML reporter, and `expect` assertions.

| Concern | playwright-bdd | @cucumber/cucumber |
|---|---|---|
| Test runner | Playwright native | Cucumber CLI |
| Parallelism | Worker-based, automatic | `--parallel N`, manual isolation |
| Fixtures | Full Playwright fixture system | Custom World object |
| Trace/video | Built-in `--trace on` | Manual tracing API calls |
| Reporters | Playwright + Cucumber reporters | Cucumber reporters only |
| Browser lifecycle | Managed by fixtures | Managed in World hooks |
| Retries | `--retries N`, per-project | `--retry N`, global only |

Choose `@cucumber/cucumber` only when: existing Cucumber infrastructure must be preserved, or the team requires Cucumber's `--dry-run` / `--wip` flags.

## Installation

```bash
npm install -D playwright-bdd @playwright/test
npx playwright install chromium
```

Directory structure:

```
.bdd/
  features/
    login.feature
  steps/
    login.steps.ts
  support/
    fixtures.ts
  interactions/             # Page Objects for web, test helpers for other archetypes
  qa/
    findings/
    resolutions/
  playwright.config.ts
```

## Configuration: defineBddConfig

`defineBddConfig` returns a `testDir` path pointing to generated spec files:

```typescript
// .bdd/playwright.config.ts
import { defineConfig } from '@playwright/test';
import { defineBddConfig, cucumberReporter } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: '.bdd/features/**/*.feature',
  steps: ['.bdd/steps/*.ts', '.bdd/support/*.ts'],
  outputDir: '.bdd/.features-gen',
});

export default defineConfig({
  testDir,
  reporter: [
    cucumberReporter('html', { outputFile: 'cucumber-report/report.html' }),
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
});
```

Key options:

| Option | Purpose | Example |
|---|---|---|
| `features` | Glob for `.feature` files | `'.bdd/features/**/*.feature'` |
| `steps` | Glob or array for step files | `['.bdd/steps/*.ts', '.bdd/support/*.ts']` |
| `outputDir` | Generated `.spec.ts` location | `'.bdd/.features-gen'` |
| `tags` | Build-time tag filter | `'@smoke and not @wip'` |

For multi-project setups (desktop + mobile), call `defineBddConfig` per project with unique `outputDir` values. Pass device-specific step files via the `steps` array and filter with `tags`.

## The createBdd Factory

`createBdd()` returns typed step definition functions bound to a test fixture. Export from a central fixtures file:

```typescript
// .bdd/support/fixtures.ts
import { test as base, createBdd } from 'playwright-bdd';

export const test = base.extend<{
  todosPage: TodosPage;
  adminAPI: AdminAPI;
}>({
  todosPage: async ({ page }, use) => {
    await use(new TodosPage(page));
  },
  adminAPI: async ({ request }, use) => {
    await use(new AdminAPI(request));
  },
});

export const { Given, When, Then, BeforeScenario, AfterScenario } = createBdd(test);
```

Without custom fixtures:

```typescript
import { createBdd } from 'playwright-bdd';
export const { Given, When, Then } = createBdd();
```

Scoped steps with tag filtering -- bind steps to specific scenarios:

```typescript
const { Given: GivenAdmin } = createBdd(test, { tags: '@admin' });
const { Given: GivenUser } = createBdd(test, { tags: '@user' });
```

## The bddgen Workflow

Two-phase execution: generate, then run.

```json
{
  "scripts": {
    "test:e2e": "npx bddgen && npx playwright test",
    "test:smoke": "npx bddgen && npx playwright test --grep @smoke",
    "test:e2e:ui": "npx bddgen && npx playwright test --ui"
  }
}
```

Add `.bdd/.features-gen/` to `.gitignore`. Generated files are deterministic.

## Writing Steps with Playwright Fixtures

Steps receive Playwright fixtures via destructuring. The first argument is always the fixtures object; Cucumber parameters follow:

```typescript
import { expect } from '@playwright/test';
import { Given, When, Then } from '../support/fixtures';

Given('the user is on the login page', async ({ page }) => {
  await page.goto('/login');
});

When('the user logs in as {string} with password {string}',
  async ({ page }, email: string, password: string) => {
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
  }
);

Then('the dashboard is visible', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

Use fixture injection over manual construction:

```typescript
// BAD: page object recreated every step, no shared state
When('the user adds a todo {string}', async ({ page }, title: string) => {
  const todosPage = new TodosPage(page);
  await todosPage.addTodo(title);
});

// GOOD: fixture injected once per test, shared across steps
When('the user adds a todo {string}', async ({ todosPage }, title: string) => {
  await todosPage.addTodo(title);
});
```

## Hooks

Four hook types, all from `createBdd()`:

```typescript
const { BeforeScenario, AfterScenario } = createBdd(test);
const { BeforeWorker, AfterWorker } = createBdd(test);
```

### Scenario Hooks (per-test)

```typescript
BeforeScenario(async ({ page, $testInfo }) => {
  console.log(`Starting: ${$testInfo.title}`);
});

AfterScenario(async ({ page, $testInfo }) => {
  if ($testInfo.status !== $testInfo.expectedStatus) {
    await page.screenshot({ path: `screenshots/${$testInfo.title}.png` });
  }
});
```

### Tagged Hooks

```typescript
BeforeScenario({ tags: '@auth' }, async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
});

AfterScenario({ tags: '@cleanup' }, async ({ adminAPI }) => {
  await adminAPI.deleteUser('test@example.com');
});
```

### Worker Hooks (per-worker, shared across tests)

```typescript
BeforeWorker(async ({}) => {
  // expensive one-time setup: DB seeding, service health checks
});

AfterWorker(async ({}) => {
  // worker-level teardown
});
```

## DataTable and DocString Handling

```typescript
import { DataTable } from 'playwright-bdd';

// Two-column key-value table -> rowsHash()
// | field | value             |
// | name  | Alice             |
// | email | alice@example.com |
When('the user fills the form:', async ({ page }, dataTable: DataTable) => {
  const fields = dataTable.rowsHash(); // { name: 'Alice', email: 'alice@example.com' }
  for (const [field, value] of Object.entries(fields)) {
    await page.getByLabel(field).fill(value);
  }
});

// Multi-row with header -> hashes()
// | name  | role  |
// | Alice | admin |
// | Bob   | user  |
Then('the users exist:', async ({ page }, dataTable: DataTable) => {
  const users = dataTable.hashes(); // [{ name: 'Alice', role: 'admin' }, ...]
  for (const user of users) {
    await expect(page.getByText(user.name)).toBeVisible();
  }
});
```

DataTable methods: `hashes()` (array of objects), `rowsHash()` (key-value), `rows()` (2D without header), `raw()` (2D with header).

DocStrings arrive as a plain string parameter after fixtures:

```typescript
When('the user submits JSON:', async ({ request }, docString: string) => {
  await request.post('/api/users', { data: JSON.parse(docString) });
});
```

## Tags and Filtering

Build-time: `defineBddConfig({ tags: '@smoke' })` -- only generates specs for matching scenarios.
Run-time: `npx playwright test --grep @smoke` or `--grep-invert @slow`.
Tag expressions support boolean logic: `@smoke and not @wip`, `@critical or @regression`.

## Parallel Execution

Set `fullyParallel: true` and `workers: process.env.CI ? 4 : undefined` in config. Each worker gets its own browser context. For scenarios that must run sequentially, create a second project with `tags: '@serial'` and `fullyParallel: false`, using a separate `outputDir`.

## Trace Viewer, Screenshots, Reporters

Configure in `use`: `trace: 'on-first-retry'`, `screenshot: 'only-on-failure'`, `video: 'retain-on-failure'`. View traces with `npx playwright show-trace test-results/.../trace.zip`.

Use `cucumberReporter` from `playwright-bdd` for Cucumber-format output alongside Playwright reporters:

```typescript
reporter: [
  ['html', { open: 'never' }],
  cucumberReporter('html', { outputFile: 'cucumber-report/report.html' }),
  cucumberReporter('json', { outputFile: 'cucumber-report/report.json' }),
],
```

The `cucumberReporter('message', ...)` format produces ndjson compatible with Allure and other Cucumber ecosystem tools.

## Custom Parameter Types

```typescript
import { defineParameterType } from 'playwright-bdd';

defineParameterType({
  name: 'role',
  regexp: /admin|editor|viewer/,
  transformer: (s: string) => s as 'admin' | 'editor' | 'viewer',
});

// Step: Given a user with role "admin"
Given('a user with role {role}', async ({ adminAPI }, role) => {
  await adminAPI.createUser('test@example.com', role);
});
```

## Complete Working Example

Four files comprise a minimal working project. The feature file, step definitions, fixtures, and config shown in previous sections combine as follows:

```gherkin
# .bdd/features/login.feature
@auth
Feature: User Login

  @smoke @critical
  Scenario: Successful login
    Given the user is on the login page
    When the user logs in as "admin@test.com" with password "secure123"
    Then the dashboard is visible

  @smoke
  Scenario Outline: Failed login
    Given the user is on the login page
    When the user logs in as "<email>" with password "<password>"
    Then the error "<message>" is shown

    Examples:
      | email          | password  | message                   |
      | wrong@test.com | secure123 | Invalid email or password |
      | admin@test.com | wrongpass | Invalid email or password |
```

```typescript
// .bdd/support/fixtures.ts -- central fixture + createBdd export
import { test as base, createBdd } from 'playwright-bdd';
export const test = base.extend<{}>({});
export const { Given, When, Then, BeforeScenario, AfterScenario } = createBdd(test);
```

```typescript
// .bdd/steps/login.steps.ts
import { expect } from '@playwright/test';
import { Given, When, Then } from '../support/fixtures';

Given('the user is on the login page', async ({ page }) => {
  await page.goto('/login');
});

When('the user logs in as {string} with password {string}',
  async ({ page }, email: string, password: string) => {
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
  },
);

Then('the dashboard is visible', async ({ page }) => {
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

Then('the error {string} is shown', async ({ page }, msg: string) => {
  await expect(page.getByRole('alert')).toHaveText(msg);
});
```

```typescript
// .bdd/playwright.config.ts
import { defineConfig } from '@playwright/test';
import { defineBddConfig, cucumberReporter } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: '.bdd/features/**/*.feature',
  steps: ['.bdd/steps/*.ts', '.bdd/support/*.ts'],
  outputDir: '.bdd/.features-gen',
});

export default defineConfig({
  testDir,
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [cucumberReporter('html', { outputFile: 'cucumber-report/report.html' })],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
});
```

Run: `npx bddgen && npx playwright test`

## Common Pitfalls

**Stale generated files**: Always run `bddgen` before `playwright test`. Stale `.spec.ts` files cause confusing failures when feature files change.

**Missing step files in config**: If `steps` glob does not match step definition files, `bddgen` generates specs with undefined steps that fail at runtime.

**Shared mutable state**: Each scenario gets a fresh `page` fixture. Do not store state in module-level variables -- use fixtures instead.

**Duplicate outputDir**: Multi-project configs without unique `outputDir` values cause generated file collisions.
