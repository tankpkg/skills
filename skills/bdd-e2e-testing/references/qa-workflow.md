# QA Verification Workflow

Sources: Smart and Molak (BDD in Action), Wynne and Hellesoy (The Cucumber Book), test-driven verification practices

## Core Principle: Code is Guilty Until Proven Innocent

BDD tests are verification instruments, not confirmation scripts. When you
write a feature file, you are defining what the application MUST do. When you
run it, you are checking whether it actually does it. Assume the code does
not work until the test proves otherwise.

When a test fails:
- The APPLICATION is wrong, not the test
- Fix the application code
- Document what you found and what you fixed
- Re-run to verify the fix

Never weaken a test to make it pass. Never mock a backend to avoid a failure.
Never skip a scenario because the feature is "not ready". The test is the
source of truth.

## Verification Workflow

Execute these steps in order. Do not skip any step.

### Step 1: Write Features

Write Gherkin scenarios that describe expected behavior. Place them in
`.bdd/features/` organized by functional area.

```gherkin
# .bdd/features/checkout/checkout.feature
Feature: Checkout
  Customers should be able to complete purchases with valid payment.

  @smoke @critical
  Scenario: Successful checkout with credit card
    Given Emma has 3 items in her cart totaling $89.97
    When she proceeds to checkout with a valid credit card
    Then the order should be confirmed
    And she should receive an order confirmation email

  @smoke
  Scenario: Checkout rejected with expired card
    Given Emma has items in her cart
    When she proceeds to checkout with an expired credit card
    Then the payment should be declined
    And she should see the error "Card expired"
```

### Step 2: Implement Steps

Wire Given/When/Then to real Playwright actions via Page Objects.
Every step MUST interact with the real application. See
`references/step-definitions.md` for implementation patterns.

### Step 3: Run Against Real Application

Execute the tests against the actual running application.

```bash
# Start the real application (not a mock server)
npm run start:dev &

# Run BDD tests
cd .bdd && npx bddgen && npx playwright test
```

NEVER use `page.route()` to intercept requests. NEVER use MSW, nock, or
any mocking library. NEVER stub API responses. The test must hit the real
backend with a real database.

### Step 4: Document Findings

After each test run, create or update a findings file in `.bdd/qa/findings/`.
One file per functional area (matching the feature file structure).

#### Findings File Format

```markdown
# Checkout Findings

Last run: 2026-02-25T14:30:00Z
Environment: http://localhost:3000
Branch: feature/checkout-flow

## Scenario: Successful checkout with credit card
- Status: FAILED
- Error: TimeoutError waiting for order confirmation page
- Evidence: Screenshot at .bdd/test-results/checkout-success-FAILED.png
- Trace: .bdd/test-results/checkout-success-trace.zip
- Root cause hypothesis: Order processing endpoint returns 500 when
  payment service response is slow (>3s timeout)

## Scenario: Checkout rejected with expired card
- Status: PASSED
- Notes: Error message displays correctly, payment declined as expected

## Summary
- Passed: 1/2
- Failed: 1/2
- Blocked: 0
```

#### Findings Rules

1. Record EVERY scenario result, not just failures
2. Include evidence: screenshots, traces, error messages
3. Write a root cause hypothesis for each failure — do not just paste the error
4. Include the environment and branch for reproducibility
5. Update the file on every run — do not create new files per run

### Step 5: Fix the Application Code

When a test fails, fix the APPLICATION, not the test.

| Situation | Action |
|-----------|--------|
| Test fails because feature is broken | Fix the feature code |
| Test fails because endpoint returns wrong data | Fix the endpoint |
| Test fails because UI element is missing | Fix the UI component |
| Test fails because of a race condition | Fix the application timing |
| Test fails because of a real bug | Fix the bug, document it |
| Test step is wrong (selector changed) | Update the Page Object ONLY — never remove the scenario |

NEVER do:
- Remove a failing scenario
- Add `@skip` or `@wip` tags to avoid failures
- Mock the failing service to make the test pass
- Weaken an assertion (e.g., change `toHaveText("$89.97")` to `toBeVisible()`)

### Step 6: Document Resolution

After fixing the code, create or update a resolution file in
`.bdd/qa/resolutions/`. One file per functional area.

#### Resolution File Format

```markdown
# Checkout Resolutions

## 2026-02-25: Order confirmation timeout

### Finding
Scenario "Successful checkout with credit card" failed with TimeoutError.
Order processing endpoint returned 500 when payment service was slow.

### Root Cause
The payment service client had a 3-second timeout but the payment provider
sometimes takes up to 5 seconds for card verification. The endpoint crashed
instead of waiting.

### Fix Applied
- File: `src/services/payment.ts` line 42
- Change: Increased payment client timeout from 3s to 10s
- Added: Retry logic with exponential backoff (max 3 attempts)
- Added: Proper error response (402 Payment Required) instead of 500

### Verification
- Re-ran "Successful checkout with credit card": PASSED
- Re-ran full checkout suite: 2/2 PASSED
- Updated findings file to reflect passing state
```

#### Resolution Rules

1. Link back to the specific finding
2. Document the root cause, not just the symptom
3. List exact files and lines changed
4. Include verification result (did the re-run pass?)
5. Keep a chronological log — append new resolutions, do not overwrite

### Step 7: Re-run and Verify

After fixing the code:

1. Re-run the specific failing scenario first
2. Re-run the full suite to check for regressions
3. Update the findings file to reflect the new status
4. Confirm all scenarios pass before marking the work complete

```bash
# Re-run specific scenario
cd .bdd && npx bddgen && npx playwright test --grep "Successful checkout"

# Re-run full suite
cd .bdd && npx bddgen && npx playwright test
```

## No-Mocking Enforcement

The following patterns are FORBIDDEN in BDD E2E tests:

### Forbidden: Route Interception

```typescript
// FORBIDDEN — never intercept API routes in E2E tests
await page.route('/api/orders', (route) => {
  route.fulfill({ json: { id: 'fake-order', status: 'confirmed' } });
});
```

### Forbidden: Request Mocking Libraries

```typescript
// FORBIDDEN — never use MSW, nock, or similar in E2E tests
import { setupServer } from 'msw/node';
const server = setupServer(
  rest.post('/api/orders', (req, res, ctx) => res(ctx.json({ id: 'fake' })))
);
```

### Forbidden: Test Doubles for Services

```typescript
// FORBIDDEN — never inject fake services
const fakePaymentService = { charge: async () => ({ success: true }) };
```

### Allowed: API Setup for Test Data

Using the real API to create test preconditions is correct — this is not mocking,
this is using the real application to set up state.

```typescript
// CORRECT — creating real data through real API for test setup
Given('Emma has 3 items in her cart', async ({ request }) => {
  const customer = await request.post('/api/test/customers', {
    data: { name: 'Emma', email: 'emma@test.com' },
  });
  await request.post('/api/test/cart/items', {
    data: { customerId: (await customer.json()).id, productIds: ['p1', 'p2', 'p3'] },
  });
});
```

### Allowed: Third-Party Service Stubs

The ONLY acceptable mock is for services completely outside your control:

```typescript
// ACCEPTABLE — third-party payment gateway sandbox/test mode
// This is NOT mocking — it is using the provider's test environment
const STRIPE_KEY = process.env.STRIPE_TEST_KEY; // Stripe test mode key
```

## QA Directory Lifecycle

### When to Create Files

| Event | Action |
|-------|--------|
| First test run for a feature area | Create `.bdd/qa/findings/{area}-findings.md` |
| First failure fixed for a feature area | Create `.bdd/qa/resolutions/{area}-resolutions.md` |
| Subsequent test runs | Update existing findings file |
| Subsequent fixes | Append to existing resolutions file |

### When NOT to Create Files

| Event | Action |
|-------|--------|
| All tests pass on first run | Create findings file showing all passed (still document it) |
| No tests written yet | Do not create qa/ files until tests exist and have run |

### File Naming Convention

Findings and resolutions match the feature area directory name:

```
.bdd/features/auth/         → .bdd/qa/findings/auth-findings.md
                             → .bdd/qa/resolutions/auth-resolutions.md
.bdd/features/checkout/     → .bdd/qa/findings/checkout-findings.md
                             → .bdd/qa/resolutions/checkout-resolutions.md
```

## Complete Example: Auth Verification Cycle

### 1. Feature Written

```gherkin
# .bdd/features/auth/login.feature
Feature: Login
  @smoke
  Scenario: Successful login
    Given the user is on the login page
    When the user logs in as "admin@test.com" with password "secure123"
    Then the dashboard should be visible
```

### 2. First Run: FAILED

```markdown
# .bdd/qa/findings/auth-findings.md

# Auth Findings

Last run: 2026-02-25T10:00:00Z
Environment: http://localhost:3000
Branch: main

## Scenario: Successful login
- Status: FAILED
- Error: Expected heading "Dashboard" but found "Loading..."
- Evidence: screenshot at .bdd/test-results/login-FAILED.png
- Root cause hypothesis: Dashboard page renders a loading spinner
  but never fetches user data after login redirect
```

### 3. Code Fixed

Developer finds the bug: `useEffect` dependency array in Dashboard component
was missing the `user` dependency, so it never re-fetched after login set
the user state.

### 4. Resolution Documented

```markdown
# .bdd/qa/resolutions/auth-resolutions.md

# Auth Resolutions

## 2026-02-25: Dashboard stuck on loading after login

### Finding
Login succeeded but dashboard showed "Loading..." indefinitely.

### Root Cause
Dashboard component's useEffect had empty dependency array []. After login
set user state, the effect never re-ran to fetch dashboard data.

### Fix Applied
- File: `src/components/Dashboard.tsx` line 18
- Change: Added `user` to useEffect dependency array
- Before: `useEffect(() => { fetchDashboard(); }, [])`
- After: `useEffect(() => { if (user) fetchDashboard(); }, [user])`

### Verification
- Re-ran "Successful login": PASSED
- Full auth suite: 1/1 PASSED
```

### 5. Findings Updated

```markdown
# .bdd/qa/findings/auth-findings.md (updated)

Last run: 2026-02-25T10:15:00Z

## Scenario: Successful login
- Status: PASSED
- Previously: FAILED (see resolutions/auth-resolutions.md)
```
