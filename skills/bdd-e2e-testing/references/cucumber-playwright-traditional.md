# Traditional Cucumber.js with Playwright

Sources: Wynne and Hellesoy (The Cucumber Book), Smart and Molak (BDD in Action), Cucumber.js documentation

## Installation

Install the core packages. Cucumber.js provides the BDD runner and Gherkin parser. Playwright provides browser automation. Use ts-node for TypeScript execution without a separate build step.

```bash
npm install --save-dev @cucumber/cucumber @playwright/test ts-node typescript
npx playwright install chromium
```

Configure `tsconfig.json` for CommonJS module resolution, which Cucumber.js requires:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "strict": true,
    "outDir": "dist",
    "sourceMap": true
  },
  "include": [".bdd/**/*.ts"]
}
```

## Project Structure

Place feature files at the top level of `.bdd/features/`, step definitions in a subdirectory, and support code (World, hooks, parameter types) in `support/`. Organize step definitions by domain concept (auth, navigation, cart), not by feature file.

```
project/
  .bdd/
    features/
      login.feature
      checkout.feature
    steps/
      auth.steps.ts
      navigation.steps.ts
      cart.steps.ts
    support/
      world.ts
      hooks.ts
      parameter-types.ts
    qa/
      findings/
      resolutions/
    cucumber.mjs
  tsconfig.json
```

## Cucumber Configuration (cucumber.mjs)

Define profiles in `.bdd/cucumber.mjs` at the project root. Profiles group CLI options for different execution contexts. Run a specific profile with `npx cucumber-js --profile smoke`.

```js
// .bdd/cucumber.mjs
const common = {
  requireModule: ['ts-node/register'],
  require: ['.bdd/steps/**/*.ts', '.bdd/support/**/*.ts'],
  paths: ['.bdd/features/**/*.feature'],
  publishQuiet: true,
};

export default {
  default: {
    ...common,
    format: ['progress-bar', 'html:.bdd/reports/cucumber-report.html'],
  },
  smoke: {
    ...common,
    tags: '@smoke and not @skip',
    format: ['progress-bar'],
  },
  ci: {
    ...common,
    format: ['json:.bdd/reports/cucumber-report.json', 'junit:.bdd/reports/junit.xml'],
    parallel: 4,
  },
  rerun: {
    ...common,
    format: ['rerun:.bdd/@rerun.txt'],
  },
};
```

## Custom World Class

The World is the central integration point. Cucumber creates a fresh World instance for every scenario, providing test isolation. Extend the base `World` class to hold Playwright's `Page`, `BrowserContext`, and shared state. Call `setWorldConstructor()` exactly once.

```typescript
// .bdd/support/world.ts
import { World, IWorldOptions, setWorldConstructor } from '@cucumber/cucumber';
import { Browser, BrowserContext, Page } from '@playwright/test';

export class PlaywrightWorld extends World {
  browser!: Browser;
  context!: BrowserContext;
  page!: Page;
  testData: Record<string, unknown> = {};

  constructor(options: IWorldOptions) {
    super(options);
  }

  async navigateTo(path: string): Promise<void> {
    const baseUrl = process.env.BASE_URL || 'http://localhost:3000';
    await this.page.goto(`${baseUrl}${path}`);
  }

  async takeScreenshot(name: string): Promise<Buffer> {
    return await this.page.screenshot({ path: `.bdd/reports/screenshots/${name}.png` });
  }
}

setWorldConstructor(PlaywrightWorld);
```

Access World properties in step definitions via `this`. Do not use arrow functions for step definitions -- they rebind `this` and break World access.

## Browser Lifecycle Management in Hooks

Launch the browser once in `BeforeAll`, create a fresh context and page per scenario in `Before`, capture evidence and clean up in `After`, and close the browser in `AfterAll`.

```typescript
// .bdd/support/hooks.ts
import {
  BeforeAll, AfterAll, Before, After, Status,
  setDefaultTimeout
} from '@cucumber/cucumber';
import { chromium, Browser } from '@playwright/test';
import { PlaywrightWorld } from './world';

setDefaultTimeout(30_000); // 30s for E2E; Cucumber default of 5s is too short

let browser: Browser;

BeforeAll(async function () {
  browser = await chromium.launch({
    headless: process.env.HEADLESS !== 'false',
  });
});

Before(async function (this: PlaywrightWorld) {
  this.browser = browser;
  this.context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
  });
  this.page = await this.context.newPage();
});

After(async function (this: PlaywrightWorld, scenario) {
  if (scenario.result?.status === Status.FAILED) {
    const screenshot = await this.takeScreenshot(
      `FAILED-${scenario.pickle.name.replace(/\s+/g, '-')}`
    );
    this.attach(screenshot, 'image/png');
  }
  await this.page?.close();
  await this.context?.close();
});

AfterAll(async function () {
  await browser?.close();
});
```

## Tagged Hooks for Conditional Setup

Use tagged hooks to run setup or teardown only for scenarios with specific tags. Tagged hooks execute in addition to untagged hooks. Order: `BeforeAll` -> `Before` (untagged) -> `Before` (tagged) -> steps -> `After` (tagged) -> `After` (untagged) -> `AfterAll`.

```typescript
Before({ tags: '@authenticated' }, async function (this: PlaywrightWorld) {
  await this.navigateTo('/login');
  await this.page.fill('[data-testid="email"]', 'test@example.com');
  await this.page.fill('[data-testid="password"]', 'password123');
  await this.page.click('[data-testid="login-button"]');
  await this.page.waitForURL('**/dashboard');
});

Before({ tags: '@mobile' }, async function (this: PlaywrightWorld) {
  await this.context.close();
  this.context = await this.browser.newContext({
    viewport: { width: 375, height: 812 },
    isMobile: true,
    hasTouch: true,
  });
  this.page = await this.context.newPage();
});

After({ tags: '@database' }, async function () {
  await fetch('http://localhost:3000/api/test/cleanup', { method: 'POST' });
});
```

## Cucumber Expressions vs Regular Expressions

Cucumber Expressions are the modern default with built-in parameter types. Regular expressions provide full regex power for complex matching. Prefer Cucumber Expressions for most steps.

```typescript
// Cucumber Expressions (preferred)
Given('the user has {int} items in the cart',
  async function (this: PlaywrightWorld, count: number) {
    // {int} automatically parses to number
});

When('the user searches for {string}',
  async function (this: PlaywrightWorld, query: string) {
    // {string} captures quoted text, strips quotes
});

Then('the total should be {float}',
  async function (this: PlaywrightWorld, total: number) {
    // {float} parses decimal numbers
});

// Regular Expressions (for complex patterns)
Given(/^the user "([^"]*)" has (\d+) items? in (?:the|their) cart$/,
  async function (this: PlaywrightWorld, username: string, count: string) {
    // Regex captures are always strings; parse manually
    const itemCount = parseInt(count, 10);
});
```

## Custom Parameter Types

Define custom parameter types to convert step arguments into domain objects. Register them in a file under `.bdd/support/` so Cucumber loads them before step definitions.

```typescript
// .bdd/support/parameter-types.ts
import { defineParameterType } from '@cucumber/cucumber';

defineParameterType({
  name: 'role',
  regexp: /admin|editor|viewer/,
  transformer: (s: string) => s as 'admin' | 'editor' | 'viewer',
});

defineParameterType({
  name: 'page_name',
  regexp: /dashboard|settings|profile|billing/,
  transformer: (s: string) => {
    const routes: Record<string, string> = {
      dashboard: '/dashboard',
      settings: '/settings',
      profile: '/profile',
      billing: '/billing',
    };
    return routes[s] || `/${s}`;
  },
});

// Usage in steps:
// Given('a user with {role} permissions', ...)
// When('the user navigates to the {page_name} page', ...)
```

## Formatters, Reporting, and Running Tests

Combine multiple formatters in a single run. Available built-in formatters:

| Formatter | Output | Use Case |
|-----------|--------|----------|
| `progress-bar` | Progress bar to stdout | Local development |
| `summary` | Pass/fail summary | Quick CI check |
| `html` | Self-contained HTML file | Stakeholder review |
| `json` | Machine-readable JSON | Allure, custom dashboards |
| `junit` | JUnit XML | CI/CD integration |
| `rerun` | Failed scenario paths | Re-running failures |
| `usage` | Step usage statistics | Finding unused/slow steps |

Common CLI patterns:

```bash
# Run all tests
npx cucumber-js

# Run with a profile
npx cucumber-js --profile ci

# Run by tag expression
npx cucumber-js --tags "@smoke and not @flaky"

# Run a specific feature or scenario by line number
npx cucumber-js .bdd/features/login.feature:12

# Dry run (validate Gherkin and step bindings without executing)
npx cucumber-js --dry-run

# Strict mode (fail on undefined or pending steps)
npx cucumber-js --strict

# Parallel execution
npx cucumber-js --parallel 4

# Rerun failed scenarios
npx cucumber-js --format rerun:@rerun.txt
npx cucumber-js @rerun.txt

# Multiple formatters in one run
npx cucumber-js \
  --format progress-bar \
  --format html:.bdd/reports/cucumber-report.html \
  --format json:.bdd/reports/cucumber-report.json
```

## Complete Working Example: Login Flow

```gherkin
# .bdd/features/login.feature
Feature: User Authentication
  Users must authenticate to access the application.

  Background:
    Given the application is running

  @smoke
  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user logs in with email "admin@example.com" and password "secure123"
    Then the user should see the dashboard
    And the welcome message should display "admin@example.com"

  @smoke
  Scenario: Failed login with invalid password
    Given the user is on the login page
    When the user logs in with email "admin@example.com" and password "wrong"
    Then the user should see the error "Invalid email or password"
    And the user should remain on the login page

  Scenario Outline: Login redirects by user role
    Given the user is on the login page
    When the user logs in with email "<email>" and password "<password>"
    Then the user should be redirected to the <landing> page

    Examples:
      | email              | password  | landing   |
      | admin@example.com  | secure123 | dashboard |
      | editor@example.com | edit456   | workspace |
      | viewer@example.com | view789   | reports   |
```

```typescript
// .bdd/steps/auth.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { PlaywrightWorld } from '../support/world';

Given('the application is running', async function (this: PlaywrightWorld) {
  const response = await this.page.request.get(
    process.env.BASE_URL || 'http://localhost:3000'
  );
  expect(response.ok()).toBeTruthy();
});

Given('the user is on the login page', async function (this: PlaywrightWorld) {
  await this.navigateTo('/login');
});

When(
  'the user logs in with email {string} and password {string}',
  async function (this: PlaywrightWorld, email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
    await this.page.waitForLoadState('networkidle');
  }
);

Then('the user should see the dashboard', async function (this: PlaywrightWorld) {
  await this.page.waitForURL('**/dashboard');
  await expect(this.page.locator('[data-testid="dashboard"]')).toBeVisible();
});

Then(
  'the welcome message should display {string}',
  async function (this: PlaywrightWorld, email: string) {
    await expect(
      this.page.locator('[data-testid="welcome-message"]')
    ).toContainText(email);
  }
);

Then(
  'the user should see the error {string}',
  async function (this: PlaywrightWorld, message: string) {
    await expect(
      this.page.locator('[data-testid="error-message"]')
    ).toHaveText(message);
  }
);

Then('the user should remain on the login page',
  async function (this: PlaywrightWorld) {
    expect(this.page.url()).toContain('/login');
  }
);

Then(
  'the user should be redirected to the {page_name} page',
  async function (this: PlaywrightWorld, route: string) {
    await this.page.waitForURL(`**${route}`);
  }
);
```

## Comparison: Traditional Cucumber vs playwright-bdd

| Aspect | Traditional @cucumber/cucumber | playwright-bdd |
|--------|-------------------------------|----------------|
| Test runner | Cucumber.js CLI | Playwright Test runner |
| Browser lifecycle | Manual (hooks + World) | Automatic (fixtures) |
| Parallel execution | `--parallel N` (process-level) | Built-in worker sharding |
| Fixtures | Not available; use World | Full Playwright fixture system |
| Trace viewer | Manual integration | Built-in `--trace on` |
| HTML reporter | Cucumber HTML formatter | Playwright HTML reporter |
| Allure support | Native via cucumber-allure | Via allure-playwright |
| Retries | `--retry N` (limited) | `retries` in config, per-test |
| Video/screenshots | Manual capture in hooks | Declarative in config |
| Step discovery | Regex/Cucumber Expressions | Same (wraps Cucumber parser) |
| Ecosystem maturity | 10+ years, battle-tested | Newer, rapidly evolving |
| Language-agnostic Gherkin | Full Cucumber ecosystem | Playwright-specific |
| CI/CD reporters | JSON, JUnit, rerun, custom | JUnit, JSON, HTML, blob |
| Learning curve | Higher (manual wiring) | Lower (convention-based) |
| Best for | Full Cucumber plugin ecosystem, multi-language BDD, existing Cucumber CI | Playwright-native DX with BDD syntax |

Choose traditional Cucumber when the project requires Cucumber-specific plugins (Allure Cucumber adapter, custom formatters), when the team shares Gherkin across multiple language implementations (Java, .NET, JS), or when existing CI pipelines depend on Cucumber JSON output. Choose playwright-bdd when the team prioritizes Playwright-native features like trace viewer, automatic screenshots, and fixture-based dependency injection.
