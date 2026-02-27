# Step Definition Patterns for BDD E2E Tests
Sources: Smart and Molak (BDD in Action), Wynne and Hellesoy (The Cucumber Book), Nicieja (Writing Great Specifications)

## The Three-Layer Architecture

Steps sit at the **Business Flow** layer -- bridging Gherkin (Business Rules) and the technical interaction layer. Steps express *what* in domain language; the interaction layer handles *how*.

```
Business Rules Layer:   Feature files / Gherkin scenarios
Business Flow Layer:    Step definitions + Action classes    <-- THIS FILE
Technical Layer:        Interaction layer (Page Objects / API clients / test helpers / CLI runners)
```

The technical layer adapts to what you're testing:
- **Web apps**: Page Objects wrapping Playwright browser interactions
- **Libraries/packages**: Test helpers wrapping the library's public API + Docker fixtures
- **REST APIs**: API clients wrapping HTTP request builders
- **CLI tools**: Command runners wrapping subprocess execution + output parsers
- **Message queues**: Broker helpers wrapping connection/publish/consume + Docker infra

## Step Matching: Cucumber Expressions vs Regex

### Cucumber Expressions (Preferred)

Built-in types: `{string}`, `{int}`, `{float}`, `{word}`, `{}` (anonymous).

```typescript
import { createBdd } from 'playwright-bdd';
const { Given, When, Then } = createBdd();

Given('a customer named {string} with {int} items in cart',
  async ({}, name: string, count: number) => {
    await customerHelper.createWithCart(name, count);
});

Then('the total should be {float}', async ({}, expected: number) => {
  await expect(checkoutPage.totalAmount).toHaveText(`$${expected.toFixed(2)}`);
});

When('{word} logs in', async ({}, username: string) => {
  await loginPage.loginAs(username);
});
```

### Regex (When Expressions Are Insufficient)

Anchor with `^...$` to prevent substring matches. Capture groups become arguments.

```typescript
Then(/^(\d+) products? should be visible$/, async ({}, count: string) => {
  await expect(catalogPage.productCards).toHaveCount(parseInt(count));
});

// Non-capturing group (?:...) for flexibility without extra args
When(/^the user (?:clicks|taps) the submit button$/, async ({}) => {
  await formPage.submit();
});

Given(/^the (admin|manager|editor) is on the dashboard$/, async ({}, role: string) => {
  await authHelper.loginWithRole(role);
  await dashboardPage.navigate();
});
```

Use Cucumber Expressions for 90% of steps. Regex only for optional words, alternation, or complex patterns.

## Custom Parameter Types

Transform captured strings into domain objects at the matching layer.

```typescript
import { defineParameterType } from 'playwright-bdd';

// "$49.99" -> { amount: 49.99, currency: 'USD' }
defineParameterType({
  name: 'money',
  regexp: /\$[\d,]+\.?\d*/,
  transformer: (s: string) => ({
    amount: parseFloat(s.replace(/[$,]/g, '')), currency: 'USD',
  }),
});

// Validates at parse time
defineParameterType({
  name: 'orderStatus',
  regexp: /pending|shipped|delivered|cancelled/,
  transformer: (s: string) => s as OrderStatus,
});

// "January 15, 2025" -> Date
defineParameterType({
  name: 'date',
  regexp: /[A-Z][a-z]+ \d{1,2}, \d{4}/,
  transformer: (s: string) => new Date(s),
});

Then('the order total is {money}', async ({}, price: Money) => {
  await expect(orderPage.total).toHaveText(formatMoney(price));
});
```

## Page Object Model Integration

Page Objects encapsulate selectors and low-level interactions. Steps call PO methods.

```typescript
// Technical Layer: .bdd/interactions/checkout.page.ts (Web archetype)
export class CheckoutPage {
  readonly promoCodeInput = this.page.getByLabel('Promo code');
  readonly applyPromoButton = this.page.getByRole('button', { name: 'Apply' });
  readonly totalAmount = this.page.getByTestId('order-total');

  constructor(private page: Page) {}
  async navigate() { await this.page.goto('/checkout'); }
  async applyPromoCode(code: string) {
    await this.promoCodeInput.fill(code);
    await this.applyPromoButton.click();
  }
}

// Business Flow Layer: .bdd/steps/checkout.steps.ts
When('the customer applies promo code {string}', async ({ page }, code: string) => {
  await new CheckoutPage(page).applyPromoCode(code);
});

Then('the order total should be {float}', async ({ page }, expected: number) => {
  await expect(new CheckoutPage(page).totalAmount).toHaveText(`$${expected.toFixed(2)}`);
});
```

## Non-Browser Interaction Layers

The same 3-layer architecture applies when there is no browser. The interaction layer wraps whatever the "end user" interacts with.

### Library/Package Testing (pytest-bdd)

```python
# .bdd/interactions/messaging_app.py — wraps the library's public API
from my_messaging_lib import MessagingApp

class MessagingAppHelper:
    def __init__(self):
        self.app = None
        self.received_messages = []
        self.failures = []

    def create_app(self, rabbitmq_url: str, max_attempts: int = 3):
        self.app = MessagingApp(url=rabbitmq_url, max_redeliveries=max_attempts)
        return self.app

    def register_failing_consumer(self, queue: str):
        @self.app.consumer(queue)
        async def handler(msg):
            self.failures.append(msg)
            raise Exception("Intentional failure")

    def register_succeeding_consumer(self, queue: str):
        @self.app.consumer(queue)
        async def handler(msg):
            self.received_messages.append(msg)
```

```python
# .bdd/steps/messaging.steps.py
from pytest_bdd import given, when, then, parsers, scenario
from interactions.messaging_app import MessagingAppHelper

@given(parsers.parse('a messaging app connected to RabbitMQ with max_attempts {n:d}'))
def messaging_app_with_retries(rabbitmq_url, n):
    helper = MessagingAppHelper()
    helper.create_app(rabbitmq_url, max_attempts=n)
    return helper

@given(parsers.parse('a consumer for "{queue}" that always fails'))
def failing_consumer(messaging_app_with_retries, queue):
    messaging_app_with_retries.register_failing_consumer(queue)

@then(parsers.parse('the message is rejected without requeue'))
def verify_rejected(rabbitmq_management, queue_name):
    # Assert against REAL RabbitMQ management API — zero mocks
    stats = rabbitmq_management.get_queue_stats(queue_name)
    assert stats['messages'] == 0
    assert stats['messages_unacknowledged'] == 0
```

### CLI Tool Testing

```typescript
// .bdd/interactions/cli.runner.ts
import { execSync } from 'child_process';

export class CLIRunner {
  run(command: string, args: string[] = []): CLIResult {
    try {
      const stdout = execSync(`${command} ${args.join(' ')}`, {
        encoding: 'utf-8', timeout: 30_000,
      });
      return { exitCode: 0, stdout, stderr: '' };
    } catch (err: any) {
      return { exitCode: err.status, stdout: err.stdout, stderr: err.stderr };
    }
  }
}

// .bdd/steps/cli.steps.ts
When('the user runs {string}', async ({}, command: string) => {
  const runner = new CLIRunner();
  scenarioContext.set('result', runner.run(command));
});

Then('the exit code should be {int}', async ({}, expected: number) => {
  expect(scenarioContext.get<CLIResult>('result').exitCode).toBe(expected);
});

Then('stdout should contain {string}', async ({}, text: string) => {
  expect(scenarioContext.get<CLIResult>('result').stdout).toContain(text);
});
```

## Screenplay Pattern

From BDD in Action: Actors perform Tasks using Abilities, and ask Questions about the system. More composable than POM for complex multi-actor workflows.

```typescript
class BrowseTheWeb {
  constructor(readonly page: Page) {}
  static using(page: Page) { return new BrowseTheWeb(page); }
}

class Actor {
  private abilities = new Map<string, unknown>();
  can(ability: object) { this.abilities.set(ability.constructor.name, ability); return this; }
  abilityTo<T>(type: new (...a: any[]) => T): T { return this.abilities.get(type.name) as T; }
  async attemptsTo(...tasks: Task[]) { for (const t of tasks) await t.performAs(this); }
  async asks<T>(question: Question<T>): Promise<T> { return question.answeredBy(this); }
}

interface Task { performAs(actor: Actor): Promise<void>; }
interface Question<T> { answeredBy(actor: Actor): Promise<T>; }

const AddItemToCart = (product: string): Task => ({
  async performAs(actor) {
    const page = actor.abilityTo(BrowseTheWeb).page;
    await page.getByRole('button', { name: `Add ${product}` }).click();
    await page.getByTestId('cart-count').waitFor();
  },
});

const CartTotal: Question<number> = {
  async answeredBy(actor) {
    const page = actor.abilityTo(BrowseTheWeb).page;
    const text = await page.getByTestId('cart-total').textContent();
    return parseFloat(text!.replace(/[$,]/g, ''));
  },
};

// Steps using Screenplay
Given('{string} is browsing the store', async ({ page }, name: string) => {
  scenarioContext.set('actor', new Actor().can(BrowseTheWeb.using(page)));
});

When('they add {string} to the cart', async ({}, product: string) => {
  await scenarioContext.get<Actor>('actor').attemptsTo(AddItemToCart(product));
});

Then('the cart total should be {float}', async ({}, expected: number) => {
  const total = await scenarioContext.get<Actor>('actor').asks(CartTotal);
  expect(total).toBeCloseTo(expected, 2);
});
```

## Action Classes and Domain Helpers

Reusable domain actions between steps and page objects. Use API shortcuts for Given-step setup.

```typescript
export class CustomerActions {
  constructor(private request: APIRequestContext) {}

  async createVerifiedCustomer(name: string, plan: string): Promise<Customer> {
    const resp = await this.request.post('/api/test/customers', {
      data: { name, plan, verified: true },
    });
    return resp.json();
  }

  async seedCart(customerId: string, products: string[]) {
    await this.request.post(`/api/test/customers/${customerId}/cart`, {
      data: { products },
    });
  }
}

Given('{string} has a {string} plan with {int} products in cart',
  async ({ request }, name: string, plan: string, count: number) => {
    const actions = new CustomerActions(request);
    const customer = await actions.createVerifiedCustomer(name, plan);
    await actions.seedCart(customer.id, generateProductNames(count));
    scenarioContext.set('customer', customer);
  }
);
```

## Interaction Layer Comparison

The interaction layer pattern is the same across archetypes — only the wrapper changes.

| Criterion | Page Objects (Web) | Test Helpers (Library/Service) | Screenplay Pattern | Action Classes |
|---|---|---|---|---|
| **Best for** | Page-centric web apps | Libraries, message queues, infra | Complex multi-actor workflows | API-heavy setup, domain-rich apps |
| **Complexity** | Low | Low | High | Medium |
| **Composability** | Low (class methods) | Medium (fixtures compose) | High (tasks compose freely) | Medium (functions compose) |
| **Learning curve** | Familiar to web devs | Familiar to backend devs | Steep, unfamiliar abstractions | Moderate |
| **When to choose** | Web UI is the primary interface | No browser, testing a library/CLI/service | Multiple user roles interact | Heavy API setup, thin UI layer |
| **Combine with** | Action classes for API setup | Docker fixtures for infra | POM/helpers for encapsulation | POM/helpers for selectors |

**Recommendation**: For web apps, start with POM + Action Classes. For libraries/services, start with Test Helpers + Docker fixtures. Adopt Screenplay only when multi-actor scenarios create excessive duplication.

## Step Organization

### Domain-Driven File Structure

Organize by domain concept, not by feature file. Multiple features share step files.

```
.bdd/steps/
  authentication.steps.ts    # login, logout, session
  catalog.steps.ts           # search, browse, filter
  cart.steps.ts              # add, remove, update quantity
  checkout.steps.ts          # payment, shipping, promo codes
  navigation.steps.ts        # shared: "user is on {string} page"
  assertions.steps.ts        # shared: generic "should see" patterns
```

### Shared Steps and Composition

```typescript
Given('the user is on the {string} page', async ({ page }, pageName: string) => {
  const routes: Record<string, string> = {
    home: '/', catalog: '/products', cart: '/cart', checkout: '/checkout',
  };
  await page.goto(routes[pageName.toLowerCase()] ?? (() => { throw new Error(`Unknown: ${pageName}`); })());
});
```

**Never call steps from steps** -- extract helper functions instead:

```typescript
// BAD: hidden coupling, breaks traceability
Given('a logged-in admin on the dashboard', async (world) => {
  await Given('an admin user exists', world);   // anti-pattern
  await When('the admin logs in', world);        // anti-pattern
});

// GOOD: compose via plain TypeScript helpers
Given('a logged-in admin on the dashboard', async ({ page, request }) => {
  const admin = await createTestUser(request, { role: 'admin' });
  await loginViaAPI(request, admin);
  await page.goto('/dashboard');
});
```

## Data Handling

### DataTable and DocString

```typescript
// DataTable: .hashes() for header-row tables, .rowsHash() for 2-column key-value
Given('the following products exist:', async ({ request }, table: DataTable) => {
  for (const p of table.hashes()) {
    await request.post('/api/test/products', {
      data: { ...p, price: parseFloat(p.price) },
    });
  }
});

// DocString: multi-line content (JSON, HTML, etc.)
When('the API receives the following payload:', async ({ request }, docString: string) => {
  scenarioContext.set('apiResponse',
    await request.post('/api/products', { data: JSON.parse(docString) }));
});
```

### Scenario Context

Share state between steps of the same scenario. Never between scenarios.

```typescript
// playwright-bdd: fixture-based (auto-scoped per scenario)
class ScenarioContext {
  private data = new Map<string, unknown>();
  set<T>(key: string, value: T) { this.data.set(key, value); }
  get<T>(key: string): T {
    const v = this.data.get(key);
    if (v === undefined) throw new Error(`Context key "${key}" not set`);
    return v as T;
  }
}

export const test = base.extend<{ ctx: ScenarioContext }>({
  ctx: async ({}, use) => { const c = new ScenarioContext(); await use(c); },
});
```

For `@cucumber/cucumber`, use the World object (new instance per scenario, state via `this`):

```typescript
class CustomWorld extends World { customer?: Customer; lastResponse?: APIResponse; }
setWorldConstructor(CustomWorld);

Given('a customer named {string}', async function (this: CustomWorld, name: string) {
  this.customer = await createCustomer(name);
});
```

## Assertion Patterns

### Auto-Retry and Soft Assertions

Always prefer `expect(locator)` -- auto-retries until timeout. Never `expect(await locator.textContent())`.

```typescript
Then('the cart should show {int} items', async ({ page }, count: number) => {
  await expect(page.getByTestId('cart-badge')).toHaveText(String(count));
});

Then('the product {string} should be visible', async ({ page }, name: string) => {
  await expect(page.getByRole('heading', { name })).toBeVisible();
});

Then('the URL should contain {string}', async ({ page }, path: string) => {
  await expect(page).toHaveURL(new RegExp(path));
});

// Soft assertions: collect ALL failures instead of stopping at first
Then('the order summary should be correct', async ({ page }) => {
  await expect.soft(page.getByTestId('customer-name')).toHaveText('Alice');
  await expect.soft(page.getByTestId('item-count')).toHaveText('3');
  await expect.soft(page.getByTestId('total')).toHaveText('$149.97');
});
```

### Custom Matchers

Extend Playwright's `expect` with domain-specific assertions:

```typescript
export const expect = baseExpect.extend({
  async toHaveItemCount(locator: Locator, expected: number) {
    try { await baseExpect(locator).toHaveAttribute('data-count', String(expected)); }
    catch { return { pass: false, message: () => `expected ${expected} items`, name: 'toHaveItemCount' }; }
    return { pass: true, message: () => '', name: 'toHaveItemCount' };
  },
});
```

## Step Reuse Across Projects

**playwright-bdd** -- export registration functions from shared npm packages:

```typescript
// @myorg/shared-steps
export function registerAuthSteps() {
  const { Given } = createBdd();
  Given('{string} is logged in as {word}',
    async ({ page, request }, name: string, role: string) => {
      const token = await getAuthToken(request, name, role);
      await page.goto('/', { extraHTTPHeaders: { Authorization: `Bearer ${token}` } });
  });
}
// Consumer: import { registerAuthSteps } from '@myorg/shared-steps'; registerAuthSteps();
```

**Traditional Cucumber** -- mix shared modules into the World object:

```typescript
export class AuthMixin {
  async loginAs(this: World & { page: Page }, role: string) {
    const creds = testCredentials[role];
    await this.page.goto('/login');
    await this.page.getByLabel('Email').fill(creds.email);
    await this.page.getByLabel('Password').fill(creds.password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
  }
}
```

## No-Mocking Rules

BDD E2E tests MUST hit the real system. These patterns are FORBIDDEN regardless of archetype:

### Forbidden: Route Interception (Web)

```typescript
// FORBIDDEN in BDD E2E tests
await page.route('/api/**', (route) => {
  route.fulfill({ json: { items: [] } });
});
```

### Forbidden: Request Mocking Libraries (Web/API)

```typescript
// FORBIDDEN — never use MSW, nock, or similar
import { http, HttpResponse } from 'msw';
const handlers = [
  http.get('/api/products', () => HttpResponse.json([{ id: 1 }])),
];
```

### Forbidden: Mocking Transport/Protocol (Library/Service)

```python
# FORBIDDEN — never mock the library's real dependencies
from unittest.mock import MagicMock
mock_channel = MagicMock()  # Fake RabbitMQ channel
mock_connection = MagicMock()  # Fake connection

# FORBIDDEN — never patch the transport layer
@patch('aio_pika.connect_robust')
def test_something(mock_connect):
    mock_connect.return_value = fake_connection
```

### Forbidden: Injected Test Doubles

```typescript
// FORBIDDEN — never replace real services with fakes
const mockPayment = { charge: async () => ({ success: true }) };
app.use('/api/payment', mockPayment);
```

### Correct: Real Infrastructure in Docker (Library/Service)

```python
# CORRECT — real RabbitMQ in Docker, real connections, real protocol
@pytest.fixture(scope="session")
def rabbitmq_url():
    """Start real RabbitMQ in Docker via testcontainers or docker-compose."""
    with RabbitMQContainer("rabbitmq:3-management") as rabbit:
        yield rabbit.get_connection_url()

@given('a messaging app connected to RabbitMQ')
def connected_app(rabbitmq_url):
    app = MessagingApp(url=rabbitmq_url)  # Real connection, real broker
    return app
```

### Correct: API Setup Through Real Endpoints (Web)

Using the real API to create test data is NOT mocking — it is using the
application as intended.

```typescript
// CORRECT — real API call to seed test state
Given('a customer with {int} items in cart', async ({ request }, count: number) => {
  const customer = await request.post('/api/test/customers', {
    data: { name: 'Emma' },
  });
  for (let i = 0; i < count; i++) {
    await request.post('/api/test/cart/items', {
      data: { customerId: (await customer.json()).id, productId: `prod-${i}` },
    });
  }
});
```

### Decision Table: Is This Mocking?

| Pattern | Mocking? | Allowed? |
|---------|----------|----------|
| `page.route()` to intercept API | Yes | NEVER |
| MSW / nock to stub responses | Yes | NEVER |
| `unittest.mock.patch` on transport layer | Yes | NEVER |
| Fake in-memory database | Yes | NEVER |
| Injecting service doubles | Yes | NEVER |
| Mock aio_pika / mock Redis client | Yes | NEVER |
| `/api/test/seed` endpoint to create data | No | Always |
| Real RabbitMQ/Redis/DB in Docker | No | Always |
| Stripe test mode API key | No | Always |
| Test-specific environment variables | No | Always |
| Factory functions that call real API | No | Always |
| Testcontainers for infrastructure | No | Always |

## Step Definition Checklist

1. **No implementation details in steps** -- delegate to interaction layer (Page Objects, test helpers, CLI runners)
2. **No raw tool calls in steps** -- wrap Playwright, subprocess, broker connections in domain-named methods
3. **Fast setup, real verification** -- Given steps use API/fixtures; Then steps assert on real outcomes
4. **One assertion concept per Then** -- use soft assertions for compound checks
5. **Custom parameter types** -- money, dates, statuses, roles
6. **Helper functions over step-calling-steps** -- compose in plain TypeScript/Python
7. **Context scoped per scenario** -- never leak state between scenarios
8. **Auto-retry assertions** -- `expect(locator)` for web; explicit polling/waits for async systems
9. **No mocking** -- zero fakes, zero patches, zero stubs of any dependency
