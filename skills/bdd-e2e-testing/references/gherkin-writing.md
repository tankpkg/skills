# Writing Effective Gherkin for E2E Tests
Sources: Nicieja (Writing Great Specifications), Wynne and Hellesoy (The Cucumber Book), Smart and Molak (BDD in Action)

## Declarative vs Imperative Style

The single most important Gherkin decision. Imperative scenarios script UI actions. Declarative scenarios express business intent. Always choose declarative.

**Imperative (BAD) -- brittle, unreadable, breaks on UI changes:**

```gherkin
Scenario: User logs in and adds item to cart
  Given I am on the login page
  And I fill in "username" with "emma@example.com"
  And I fill in "password" with "secret123"
  And I click the "Login" button
  And I click the "Products" link in the navigation bar
  And I click the "Add to Cart" button next to "Running Shoes"
  Then I should see "Running Shoes" in the cart list
```

**Declarative (GOOD) -- stable, readable, expresses business intent:**

```gherkin
Scenario: Returning customer adds a product to their cart
  Given Emma is a returning customer
  And "Running Shoes" is available for $89.99
  When Emma adds "Running Shoes" to her cart
  Then her cart should contain "Running Shoes"
  And her cart total should be $89.99
```

The declarative version survives a complete UI redesign. Push mechanics into step definitions and the interaction layer -- never into feature files.

This principle applies to ALL archetypes, not just web apps:

```gherkin
# Library testing -- declarative, from the developer's perspective
Feature: Message consumption with redelivery protection
  As a service developer using a messaging library
  I want failed messages to be retried up to a configured limit
  So that poison messages don't loop forever

  Scenario: Message is retried and then rejected after max attempts
    Given a messaging app connected to RabbitMQ with max_attempts 2
    And a consumer for "order.process" that always fails
    When a message is published to "order.process"
    Then the message is redelivered 2 times
    And the message is rejected without requeue
```

## Feature File Header

Every feature file starts with a `Feature:` block that explains business value. Use the canonical three-line format or the alternative keywords `Ability:` and `Business Need:`.

```gherkin
Feature: Shopping cart management
  As a returning customer
  I want to add and remove products from my cart
  So that I can purchase exactly what I need
```

Use `Ability:` for functional capabilities (`Ability: Export financial reports`) and `Business Need:` for nonfunctional requirements (`Business Need: Sub-second search response`). Keep the description to 2-4 lines. If you need more, the feature is too broad -- split it.

## Scenario Naming

Name scenarios after business behavior, not technical actions. Use the "Friends Episode" notation: "The one where..."

**BAD -- technical action names:**

```gherkin
Scenario: Test login with valid credentials
Scenario: Click submit button on checkout form
Scenario: Verify database record created after signup
```

**GOOD -- business behavior names:**

```gherkin
Scenario: Returning customer signs in with saved credentials
Scenario: Shopper completes a purchase with express checkout
Scenario: New member receives a welcome email after registration
```

The scenario name should make sense to a product owner who has never seen code.

## Given: Passive State Snapshots

Givens describe the state of the world BEFORE the action. Write them as static snapshots, not as actions.

**BAD -- Givens as actions:**

```gherkin
Given Emma navigates to the product page
Given Emma searches for "laptop"
Given the admin creates a discount code "SAVE20"
```

**GOOD -- Givens as state snapshots:**

```gherkin
Given Emma is browsing the product catalog
Given a product "laptop" exists in the catalog
Given a discount code "SAVE20" is active for 20% off
```

Givens set the stage -- the "previously on..." recap. The step definition behind a Given can perform complex setup (API calls, database seeding, navigation), but the Gherkin reads as a fact about the world.

## The One When Rule

Each scenario has exactly ONE When step. One When = one business event = one testable behavior. If you need multiple Whens, split into multiple scenarios.

**BAD -- multiple Whens (testing two behaviors):**

```gherkin
Scenario: Customer shops and checks out
  Given Emma has an empty cart
  When Emma adds "Running Shoes" to her cart
  And Emma proceeds to checkout
  And Emma pays with her saved credit card
  Then she should see an order confirmation
```

**GOOD -- split into focused scenarios:**

```gherkin
Scenario: Customer adds a product to cart
  Given Emma has an empty cart
  And "Running Shoes" is available for $89.99
  When Emma adds "Running Shoes" to her cart
  Then her cart should contain 1 item

Scenario: Customer completes checkout with saved payment
  Given Emma has "Running Shoes" in her cart
  And Emma has a saved credit card on file
  When Emma checks out with her saved payment method
  Then she should receive an order confirmation
```

Use `And` after `When` only for parameters of the SAME action, not for additional actions.

## Start with Then

When stuck writing a scenario, start with the Then (expected outcome) and work backwards. Define what success looks like first, then figure out what triggers it (When) and what preconditions are needed (Given).

```gherkin
# Step 1: Write the outcome first
  Then Emma should see her monthly spending breakdown by category

# Step 2: What action triggers this?
  When Emma views her spending report for January 2025

# Step 3: What state must exist?
  Given Emma has made purchases in 3 categories during January 2025

# Final assembled scenario:
Scenario: Customer views categorized spending report
  Given Emma has made purchases in 3 categories during January 2025
  When Emma views her spending report for January 2025
  Then Emma should see her monthly spending breakdown by category
```

This technique prevents over-engineering Givens and keeps scenarios focused on observable outcomes.

## Then: Observable Outcomes

Thens verify what the **end user** can observe. Who the "end user" is depends on the archetype:

- **Web app user** observes: screen content, emails, notifications
- **Library consumer** observes: return values, callback invocations, queue state, error behavior
- **API consumer** observes: response status, response body, side effects
- **CLI user** observes: stdout, stderr, exit codes, file system changes

The rule is: verify outcomes at the end user's abstraction level. For a web app, database records are internal state. For a library that manages a message queue, the queue state IS the observable outcome.

**BAD for a web app -- leaking implementation details:**

```gherkin
Then the orders table should have a new row with status "confirmed"
Then the user's session token should be refreshed
```

**GOOD for a web app -- user-observable outcomes:**

```gherkin
Then Emma should see "Order #1234 confirmed" on the confirmation page
Then Emma should receive an order confirmation email
```

**GOOD for a library -- developer-observable outcomes:**

```gherkin
Then the message is acknowledged
And the queue is empty
Then the consumer receives the message payload
Then the error callback is invoked with "ConnectionError"
```

**GOOD for a CLI tool -- operator-observable outcomes:**

```gherkin
Then the exit code should be 0
And stdout should contain "3 files processed"
Then the output file should exist at "output/report.csv"
```

For API-level tests, keep assertions at the domain level:

```gherkin
Then the order status should be "confirmed"
Then Emma's loyalty points should increase by 89
```

## Background Section

Use Background for shared preconditions that apply to EVERY scenario in the file. Limit to 3-4 steps maximum.

```gherkin
Feature: Product reviews

  Background:
    Given Emma is a verified purchaser
    And she has purchased "Wireless Headphones"
    And the review period for her purchase is still open

  Scenario: Purchaser submits a star rating with text review
    When Emma submits a 4-star review with "Great sound quality"
    Then the review should appear on the product page
    And the product's average rating should update

  Scenario: Purchaser edits their existing review
    Given Emma has already submitted a 3-star review
    When Emma updates her review to 5 stars with "Even better after firmware update"
    Then her updated review should replace the original
```

**Avoid:** more than 4 steps, technical setup (database resets, API mocks), steps that only apply to some scenarios.

## Scenario Outline with Examples Table

Use Scenario Outlines when you have 3+ variations of the same behavior. Name the Examples blocks to group related variations.

```gherkin
Scenario Outline: Shipping cost calculated by order weight
  Given Emma has items weighing <weight> kg in her cart
  When she proceeds to checkout with <shipping_method> shipping
  Then the shipping cost should be <cost>

  Examples: Standard shipping tiers
    | weight | shipping_method | cost   |
    | 0.5    | standard        | $4.99  |
    | 2.0    | standard        | $7.99  |
    | 5.0    | standard        | $12.99 |

  Examples: Express shipping tiers
    | weight | shipping_method | cost   |
    | 0.5    | express         | $9.99  |
    | 2.0    | express         | $14.99 |
    | 5.0    | express         | $24.99 |
```

Avoid combinatorial explosion -- use pairwise testing when inputs multiply. More than 10 rows usually means the logic belongs in unit tests.

## Tags

Tags categorize scenarios for selective execution and reporting.

```gherkin
@checkout @critical
Feature: Payment processing

  @smoke
  Scenario: Customer pays with credit card
    ...

  @regression @slow
  Scenario: Customer pays with bank transfer requiring 3D Secure
    ...

  @wip
  Scenario: Customer pays with cryptocurrency
    ...
```

**Standard tag conventions:**

| Tag | Purpose | Run frequency |
|-----|---------|---------------|
| `@smoke` | Core happy paths, must always pass | Every commit |
| `@critical` | Business-critical flows | Every PR |
| `@regression` | Full regression coverage | Nightly / release |
| `@wip` | Work in progress, expected to fail | Excluded from CI |
| `@slow` | Tests taking > 30 seconds | Nightly only |
| `@api` | API-level tests (no browser) | Every commit |
| `@manual` | Not yet automated | Excluded from CI |

Add domain tags (`@payments`, `@onboarding`) for business area filtering. Link to trackers with `@issue:JIRA-1234`.

## Data Tables

Use data tables to pass structured input data within a single step.

```gherkin
Scenario: Customer places a multi-item order
  Given Emma has the following items in her cart:
    | product          | quantity | price  |
    | Running Shoes    | 1        | $89.99 |
    | Sports Socks     | 3        | $12.99 |
    | Water Bottle     | 1        | $24.99 |
  When Emma completes checkout
  Then her order total should be $153.95
```

Data tables also work for verifying output:

```gherkin
Then the search results should include:
  | product       | price  | in_stock |
  | Running Shoes | $89.99 | yes      |
  | Trail Runners | $99.99 | yes      |
```

Keep tables under 8 rows. Larger datasets belong in unit tests.

## Doc Strings

Use doc strings (triple quotes) for multiline text: JSON payloads, HTML snippets, email bodies. Annotate with a content type hint (`"""json`, `"""html`).

```gherkin
Scenario: API returns product details in expected format
  Given a product "Running Shoes" exists with full details
  When the client requests product details via the API
  Then the response should contain:
    """json
    {
      "name": "Running Shoes",
      "price": 89.99,
      "currency": "USD",
      "available": true
    }
    """
```

## The Goldilocks Abstraction Level

Use the fewest steps possible without sacrificing readability. Too vague ("When she shops / Then she should be satisfied") is untestable. Too detailed (listing every click and scroll) is imperative scripting. Find the middle:

```gherkin
Scenario: Customer finds products by searching
  Given the catalog contains 12 running shoe products
  When Emma searches for "running shoes"
  Then she should see search results showing running shoe products
  And each result should display the product name, image, and price
```

This is stable across UI changes, readable by non-technical stakeholders, and specific enough to automate. If a scenario exceeds 7 steps, it is probably too detailed or testing multiple behaviors.

## Real Personas Instead of "The User"

Replace generic actors with named personas that carry context. Personas create empathy and encode assumptions about user state.

**BAD:**

```gherkin
Given the user is logged in
When the user adds an item to the cart
```

**GOOD:**

```gherkin
# Emma: returning customer with saved payment methods and order history
Given Emma is a returning customer with a saved credit card

# Marcus: first-time visitor, no account yet
Given Marcus is browsing the store for the first time

# Priya: store administrator with full permissions
Given Priya is signed in as a store administrator
```

Define 3-5 personas per project. Each persona implies preconditions that step definitions set up automatically.

## Feature Organization

Organize feature files by business domain, not by technical layer or test type:

```
features/
  catalog/product-search.feature, product-filtering.feature
  cart/add-to-cart.feature, update-quantities.feature
  checkout/payment-processing.feature, order-confirmation.feature
  account/registration.feature, sign-in.feature
```

Target 50-100 lines per feature file, maximum 5-8 scenarios per file. Split by stakeholder concern when a feature grows too large. Never organize by test type (`smoke/`, `regression/`) or by page (`login-page/`).

## Exploratory Outcome Paths

Use Nicieja's outcome path checklist to discover scenarios you would otherwise miss. For each feature, ask what happens when the customer is...

**Angry** -- main failure path. What does the frustrated customer do?

```gherkin
Scenario: Customer cancels order immediately after placing it
  Given Emma has just placed an order for "Running Shoes"
  When Emma cancels her order
  Then she should receive a full refund within 24 hours
```

**Scary** -- highest risk (data loss, double charges, security breaches):

```gherkin
Scenario: Payment fails mid-transaction without double-charging
  Given Emma is completing checkout for $89.99
  When the payment gateway times out
  Then Emma should not be charged
  And she should see "Payment could not be processed, please try again"
```

**Embarrassing** -- what breaks during a demo?

```gherkin
Scenario: Product page handles missing image gracefully
  Given "Running Shoes" exists but has no product image
  When Emma views the product detail page
  Then she should see a placeholder image
```

**Forgetful** -- user abandons mid-process:

```gherkin
Scenario: Cart persists after customer leaves and returns
  Given Emma has added "Running Shoes" to her cart
  When Emma leaves the site and returns 2 hours later
  Then her cart should still contain "Running Shoes"
```

**Desolate** -- testing nothingness (empty states, zero results):

```gherkin
Scenario: Search returns no results gracefully
  Given the catalog contains no products matching "quantum sneakers"
  When Emma searches for "quantum sneakers"
  Then she should see "No products found for 'quantum sneakers'"
```

**Greedy** -- testing excess (max quantities, huge inputs):

```gherkin
Scenario: Customer adds more than available stock
  Given "Running Shoes" has 3 units in stock
  When Emma tries to add 5 units to her cart
  Then her cart should contain 3 units
  And she should see "Only 3 units available"
```

Run through all six paths for every critical feature.

## Gherkin Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Imperative steps | Breaks on UI changes | Declarative business-intent steps |
| Multiple Whens | Tests multiple behaviors | Split into one-When scenarios |
| Incidental details | Irrelevant data clutters scenario | Remove data not affecting outcome |
| "The user" actor | No empathy or context | Named personas (Emma, Marcus) |
| Giant Background | Hides context | Max 3-4 steps, split features |
| Wrong-level assertions | Thens check internals the end user can't see | Verify at the end user's abstraction level |
| Copy-paste scenarios | Duplicated steps | Scenario Outline with Examples |
| Conjunction steps | "Given X and Y and Z" | Separate Given/And steps |
| Feature > 100 lines | Too many concerns | Split by business capability |
| Test-first naming | "Test login" | Name after business behavior |
| Combinatorial explosion | 50+ Examples rows | Pairwise testing or unit tests |
| Speci-fiction | Outdated scenarios | Tie to automated tests, delete stale |
| Flickering scenarios | Random pass/fail | Isolate state, explicit waits |
| Leaky scenarios | Cross-scenario dependency | Each scenario owns its state |

## Checklist: Before Committing a Feature File

1. Every scenario has exactly one When step
2. Scenario names describe business behavior, not technical actions
3. Givens read as state snapshots, not user actions
4. Thens verify observable outcomes, not internal state
5. No UI element references (button names, CSS selectors, page URLs)
6. A product owner can read and understand every scenario
7. Feature file is under 100 lines with 4 or fewer Background steps
8. Named personas replace "the user" or "I"
9. Exploratory paths (angry/scary/embarrassing/forgetful/desolate/greedy) considered
10. Scenario Outlines replace 3+ copy-pasted scenarios
11. Tags applied for CI filtering (@smoke, @critical, @wip)
