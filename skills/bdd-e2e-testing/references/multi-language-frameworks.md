# BDD E2E Frameworks Across Languages

Sources: Smart and Molak (BDD in Action), Wynne and Hellesoy (The Cucumber Book), framework documentation

## Overview

All BDD frameworks share one execution model:
Features (Gherkin) -> Step Definitions (glue code) -> Interaction Layer -> System Under Test.

The three-layer architecture (BDD in Action) applies across every language and archetype:
1. Business Rules Layer: `.feature` files (Gherkin scenarios)
2. Business Flow Layer: Step definitions / action classes (the "what")
3. Technical Layer: Interaction layer — Page Objects, API clients, test helpers, CLI runners (the "how")

Feature files (layer 1) are portable across all frameworks. Only layers 2-3 change.

**Framework selection depends on both language AND archetype:**

| Archetype | TypeScript | Python | Java | .NET |
|-----------|-----------|--------|------|------|
| Web app (browser) | playwright-bdd | pytest-bdd + Playwright | Cucumber-JVM + Playwright | Reqnroll + Playwright |
| Library/package | playwright-bdd (`request` only) | pytest-bdd + Docker fixtures | Cucumber-JVM + Testcontainers | Reqnroll + Testcontainers |
| REST API | playwright-bdd (`request`) | pytest-bdd + `httpx`/`requests` | Cucumber-JVM + REST Assured | Reqnroll + HttpClient |
| CLI tool | playwright-bdd + `child_process` | pytest-bdd + `subprocess` | Cucumber-JVM + ProcessBuilder | Reqnroll + Process |
| Message queue | playwright-bdd + broker client | pytest-bdd + Docker broker | Cucumber-JVM + Testcontainers | Reqnroll + Testcontainers |

## TypeScript/JavaScript (Primary Ecosystem)

### playwright-bdd (Recommended)

Uses Playwright's native test runner with full fixture, parallel, and trace support.

```bash
npm install -D @playwright/test playwright-bdd @cucumber/cucumber
npx playwright install chromium
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
});
export default defineConfig({ testDir, use: { baseURL: 'http://localhost:3000' } });
```

```typescript
// steps/login.steps.ts
import { createBdd } from 'playwright-bdd';
import { expect } from '@playwright/test';
const { Given, When, Then } = createBdd();

Given('I am on the login page', async ({ page }) => {
  await page.goto('/login');
});
When('I log in as {string}', async ({ page }, username: string) => {
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill('secret_sauce');
  await page.getByRole('button', { name: 'Login' }).click();
});
Then('I should see the dashboard', async ({ page }) => {
  await expect(page.getByTestId('dashboard')).toBeVisible();
});
```

Run: `npx bddgen && npx playwright test`

### @cucumber/cucumber (Traditional Runner)

Full Cucumber ecosystem with custom World managing browser lifecycle.

```typescript
// cucumber.js -- config with parallel and reporters
module.exports = { default: {
  require: ['steps/**/*.ts'], requireModule: ['ts-node/register'],
  format: ['progress', 'html:reports/cucumber.html'], parallel: 4,
}};

// support/world.ts -- custom World manages browser lifecycle
import { setWorldConstructor, World } from '@cucumber/cucumber';
import { Browser, Page, chromium } from '@playwright/test';
export class BddWorld extends World {
  browser!: Browser; page!: Page;
  async openBrowser() { this.browser = await chromium.launch(); this.page = await this.browser.newPage(); }
  async closeBrowser() { await this.browser?.close(); }
}
setWorldConstructor(BddWorld);
```

Steps use `this.page` (World) instead of destructured `{ page }` (fixture).
More boilerplate, but full Cucumber ecosystem (Allure, JSON output, custom formatters).

### Cypress + @badeball/cypress-cucumber-preprocessor

Best when team already uses Cypress. Component testing + E2E in one tool.

```bash
npm install -D cypress @badeball/cypress-cucumber-preprocessor @bahmutov/cypress-esbuild-preprocessor
```

Config requires esbuild bundler plugin wiring in `cypress.config.ts` with
`addCucumberPreprocessorPlugin` and `createEsbuildPlugin`. Set `specPattern: '**/*.feature'`.
Steps use `cy.*` API: `cy.visit('/login')`, `cy.get('[data-testid="x"]').type(val)`.

### CodeceptJS BDD

Higher-level abstraction. Install: `npx create-codeceptjs . --playwright`

```javascript
exports.config = {
  helpers: { Playwright: { url: 'http://localhost:3000', browser: 'chromium' } },
  gherkin: { features: './features/*.feature', steps: ['./step_definitions/steps.js'] },
};
```

## Python

### pytest-bdd (Recommended)

Leverages pytest fixtures, markers, and parametrize. Most Pythonic approach.

```bash
pip install pytest pytest-bdd playwright && playwright install chromium
```

```python
# tests/conftest.py -- browser fixtures (pytest DI)
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()

@pytest.fixture
def page(browser):
    ctx = browser.new_context()
    page = ctx.new_page()
    yield page
    ctx.close()

# tests/step_defs/test_login.py
from pytest_bdd import scenario, given, when, then, parsers

@scenario('../features/login.feature', 'Successful login')
def test_login(): pass

@given('I am on the login page')
def navigate_to_login(page): page.goto('http://localhost:3000/login')

@when(parsers.parse('I log in as "{username}"'))
def perform_login(page, username):
    page.get_by_label('Username').fill(username)
    page.get_by_role('button', name='Login').click()

@then('I should see the dashboard')
def verify_dashboard(page): assert page.get_by_test_id('dashboard').is_visible()
```

Run: `pytest tests/ -v --gherkin-terminal-reporter`

### Behave (Standalone)

Closer to Cucumber's model. Uses mutable `context` object instead of fixture injection.

```python
# features/environment.py
from playwright.sync_api import sync_playwright

def before_scenario(context, scenario):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch()
    context.page = context.browser.new_page()

def after_scenario(context, scenario):
    context.browser.close()
    context.playwright.stop()
```

Steps access `context.page` instead of receiving `page` via fixture injection.
Prefer pytest-bdd when the team already uses pytest.

### pytest-bdd Without Browser (Library/Service Testing)

For testing libraries, packages, CLI tools, or services — no Playwright needed.
Use Docker fixtures for real infrastructure.

```bash
pip install pytest pytest-bdd testcontainers
```

```python
# .bdd/support/conftest.py — Docker fixtures for real infrastructure
import pytest
from testcontainers.rabbitmq import RabbitMqContainer

@pytest.fixture(scope="session")
def rabbitmq():
    with RabbitMqContainer("rabbitmq:3-management") as rabbit:
        yield rabbit

@pytest.fixture(scope="session")
def rabbitmq_url(rabbitmq):
    return rabbitmq.get_connection_url()

# .bdd/interactions/messaging_app.py — wraps the library under test
from my_messaging_lib import MessagingApp

class MessagingAppHelper:
    def __init__(self, url, **kwargs):
        self.app = MessagingApp(url=url, **kwargs)
        self.received = []

    def register_consumer(self, queue, handler=None):
        if handler is None:
            @self.app.consumer(queue)
            async def default_handler(msg):
                self.received.append(msg)
        else:
            self.app.consumer(queue)(handler)
```

```python
# .bdd/steps/messaging.steps.py
from pytest_bdd import scenario, given, when, then, parsers

@scenario('../features/messaging/consumption.feature',
          'Successful processing ACKs the message')
def test_successful_ack():
    pass

@given(parsers.parse('a messaging app connected to RabbitMQ'))
def messaging_app(rabbitmq_url):
    from interactions.messaging_app import MessagingAppHelper
    return MessagingAppHelper(url=rabbitmq_url)

@given(parsers.parse('a consumer for "{queue}" that succeeds'))
def succeeding_consumer(messaging_app, queue):
    messaging_app.register_consumer(queue)

@when(parsers.parse('a message is published to "{queue}"'))
def publish_message(rabbitmq_url, queue):
    # Publish via real AMQP connection — zero mocks
    import pika
    conn = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    ch = conn.channel()
    ch.basic_publish(exchange='', routing_key=queue, body=b'test payload')
    conn.close()

@then('the consumer receives the message payload')
def verify_received(messaging_app):
    assert len(messaging_app.received) == 1
    assert messaging_app.received[0] == b'test payload'

@then('the queue is empty')
def verify_queue_empty(rabbitmq, queue_name):
    # Assert against REAL RabbitMQ management API
    import requests
    resp = requests.get(
        f'http://localhost:{rabbitmq.get_exposed_port(15672)}'
        f'/api/queues/%2F/{queue_name}',
        auth=('guest', 'guest'))
    assert resp.json()['messages'] == 0
```

Run: `pytest .bdd/ -v --gherkin-terminal-reporter`

## Java

### Cucumber-JVM

The reference Cucumber implementation. Mature, JUnit 5 integration, wide IDE support.

Dependencies: `cucumber-java`, `cucumber-junit-platform-engine` (7.18+),
`com.microsoft.playwright` (1.44+).

```java
public class LoginSteps {
    private Playwright playwright;
    private Browser browser;
    private Page page;

    @Before public void setup() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
        page = browser.newPage();
    }
    @Given("I am on the login page")
    public void navigateToLogin() { page.navigate("http://localhost:3000/login"); }

    @When("I log in as {string}")
    public void performLogin(String username) {
        page.getByLabel("Username").fill(username);
        page.getByLabel("Password").fill("secret_sauce");
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Login")).click();
    }
    @Then("I should see the dashboard")
    public void verifyDashboard() { assertTrue(page.getByTestId("dashboard").isVisible()); }

    @After public void teardown() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }
}
```

### Serenity BDD

Rich reporting and Screenplay pattern built-in. Wraps Cucumber-JVM.

```java
@When("{actor} logs in as {string}")
public void actorLogsIn(Actor actor, String username) {
    actor.attemptsTo(
        Navigate.to("/login"),
        Enter.theValue(username).into(LoginPage.USERNAME_FIELD),
        Click.on(LoginPage.LOGIN_BUTTON)
    );
}
```

Generates HTML reports with screenshots at each step, aggregated feature coverage,
and requirement traceability. Best for regulated industries.

## .NET

### Reqnroll (SpecFlow Successor)

SpecFlow was archived in 2024. Reqnroll is the community-driven open-source fork.
Same syntax, same binding attributes, new package name.

```bash
dotnet new nunit -n MyBddTests && cd MyBddTests
dotnet add package Reqnroll.NUnit && dotnet add package Microsoft.Playwright
```

```csharp
[Binding]
public class LoginSteps {
    private IPlaywright _pw; private IBrowser _browser; private IPage _page;

    [BeforeScenario] public async Task Setup() {
        _pw = await Playwright.CreateAsync();
        _browser = await _pw.Chromium.LaunchAsync();
        _page = await _browser.NewPageAsync();
    }
    [Given("I am on the login page")]
    public async Task NavigateToLogin() => await _page.GotoAsync("http://localhost:3000/login");

    [When("I log in as {string}")]
    public async Task LogInAs(string username) {
        await _page.GetByLabel("Username").FillAsync(username);
        await _page.GetByLabel("Password").FillAsync("secret_sauce");
        await _page.GetByRole(AriaRole.Button, new() { Name = "Login" }).ClickAsync();
    }
    [Then("I should see the dashboard")]
    public async Task VerifyDashboard() =>
        await Assertions.Expect(_page.GetByTestId("dashboard")).ToBeVisibleAsync();

    [AfterScenario] public async Task Teardown() {
        if (_browser != null) await _browser.CloseAsync();
        _pw?.Dispose();
    }
}
```

Supports DI via container plugins (Microsoft.Extensions.DI, Autofac).

## Framework Selection Matrix

| Criteria              | playwright-bdd | @cucumber/cucumber | Cypress+Cucumber | pytest-bdd | Behave  | Cucumber-JVM | Serenity BDD | Reqnroll |
|-----------------------|:--------------:|:------------------:|:----------------:|:----------:|:-------:|:------------:|:------------:|:--------:|
| Parallel support      | Native         | --parallel N       | Limited          | pytest-xdist| No     | JUnit 5      | JUnit 5      | NUnit    |
| Playwright integration| Native         | Manual World       | N/A (Cypress)    | Fixtures   | Manual  | Manual       | Plugin       | Manual   |
| Report quality        | Good           | Good + Allure      | Good             | Basic      | Basic   | Good         | Excellent    | Good     |
| Community size        | Growing        | Large              | Medium           | Large      | Medium  | Very Large   | Large        | Growing  |
| Learning curve        | Low            | Medium             | Low              | Low        | Low     | Medium       | High         | Medium   |
| CI/CD support         | Excellent      | Good               | Good             | Excellent  | Good    | Excellent    | Excellent    | Good     |
| Living documentation  | Basic          | Good               | Basic            | Basic      | Basic   | Good         | Excellent    | Good     |

## Migration Paths

### SpecFlow to Reqnroll (.NET)

Direct migration -- same Gherkin, same binding attributes:
1. Replace NuGet: `dotnet remove package SpecFlow.NUnit && dotnet add package Reqnroll.NUnit`
2. Find-replace namespace: `TechTalk.SpecFlow` -> `Reqnroll` in all .cs files
3. Feature files and step definition attributes: no changes needed

### Cypress to playwright-bdd (TypeScript)

1. Install playwright-bdd alongside Cypress (parallel run period)
2. Feature files: copy as-is (Gherkin is universal)
3. Rewrite step definitions: `cy.visit()` -> `page.goto()`, `cy.get()` -> `page.locator()`,
   `cy.should('be.visible')` -> `expect(locator).toBeVisible()`
4. Migrate one feature file at a time, validate, repeat

### @cucumber/cucumber to playwright-bdd (TypeScript)

1. Feature files: no changes needed
2. Step definitions: `this.page` -> destructured `{ page }` from `createBdd()`
3. Remove custom World class and Before/After browser lifecycle hooks
4. Config: replace `cucumber.js` with `defineBddConfig` in `playwright.config.ts`
5. Run command: `npx cucumber-js` -> `npx bddgen && npx playwright test`

### Cross-Language Migration

Feature files are portable across all frameworks and languages:
1. Copy `.feature` files as-is (Gherkin is language-agnostic)
2. Rewrite step definitions in target language
3. Rewrite page objects / automation layer
4. Adapt hooks to target framework's lifecycle

The three-layer architecture makes this practical: only layers 2 and 3 change.

## Quick Decision Guide

**playwright-bdd:** Starting fresh with TypeScript. Simplest setup, native Playwright
trace viewer and parallel execution.

**@cucumber/cucumber:** Need full Cucumber ecosystem, Allure reporting, or integrating
with existing Cucumber infrastructure across teams.

**Cypress + Cucumber:** Team already invested in Cypress, need component testing
alongside E2E.

**pytest-bdd (with Playwright):** Python web app with pytest already in use. Fixture-based DI.

**pytest-bdd (without browser):** Python library, service, CLI, or message queue testing.
Docker fixtures for real infrastructure. No Playwright needed.

**Behave:** Python team wanting closest-to-Cucumber experience with context objects.

**Cucumber-JVM:** Java/Kotlin enterprise project. Most mature, widest IDE support.

**Serenity BDD:** Need rich living documentation, Screenplay pattern, compliance
reporting for regulated industries.

**Reqnroll:** .NET project, migrating from SpecFlow, or need Visual Studio integration.
