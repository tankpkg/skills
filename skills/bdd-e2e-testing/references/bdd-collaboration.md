# BDD Collaboration: Discovery, Formulation, and Living Documentation
Sources: Smart and Molak (BDD in Action), Nicieja (Writing Great Specifications), Wynne and Hellesoy (The Cucumber Book)

## The BDD Lifecycle

BDD is a collaboration practice, not a testing tool. The lifecycle flows through five phases
that connect business intent to validated software:

1. **Discovery**: Explore the problem space through structured conversations. Identify rules,
   examples, and unknowns before writing any specification or code.
2. **Formulation**: Express discovered rules and examples in a structured, business-readable
   format (Gherkin scenarios). This is a writing exercise, not a coding exercise.
3. **Automation**: Implement step definitions and support code that connect scenarios to the
   system under test. This is the first phase that involves code.
4. **Demonstration**: Run scenarios against the system to show stakeholders that behavior
   matches expectations. Use living documentation reports as evidence.
5. **Validation**: Confirm that the delivered behavior actually solves the original business
   problem. Feed learnings back into the next Discovery cycle.

Treat Discovery and Formulation as the highest-value phases. Teams that skip straight to
Automation produce brittle test scripts, not shared understanding.

## Three Amigos Workshop

### Who Participates

Assemble exactly three perspectives for each workshop:

- **Developer**: Identifies technical constraints, edge cases in implementation, and
  integration risks.
- **Tester**: Challenges assumptions, explores failure modes, and identifies missing
  scenarios through adversarial thinking.
- **Product Owner / Business Analyst**: Clarifies business intent, prioritizes rules,
  and resolves ambiguity in requirements.

Invite additional domain experts only when the story touches unfamiliar territory. Keep the
core group to three people to maintain focus.

### When to Hold

- Schedule a 25-minute session per user story, immediately before implementation begins.
- Hold sessions no more than 2-3 stories ahead of development to avoid stale context.
- Cancel the session if the story is trivially understood by all three perspectives.
- Reconvene if implementation reveals significant unknowns not covered in the original session.

### How to Run (25-Minute Format)

1. **Minutes 0-5**: Product Owner reads the story aloud and states the business goal.
   Participants ask clarifying questions about intent, not implementation.
2. **Minutes 5-15**: Use Example Mapping (see below) to explore rules and examples.
   The Tester drives edge case exploration. The Developer flags technical constraints.
3. **Minutes 15-22**: Review the map. Identify unresolved questions (pink cards).
   Decide which questions block implementation and which can be deferred.
4. **Minutes 22-25**: Agree on next steps. Assign question owners. Confirm the story
   is ready for Formulation or needs another session.

### Output

- A set of concrete rules with illustrating examples.
- A list of unresolved questions with assigned owners.
- A shared understanding that replaces lengthy written requirements.
- Optionally, draft scenario titles (not full Gherkin yet).

## Example Mapping

Example Mapping is the primary Discovery technique. Use colored cards (physical or virtual)
to structure the conversation:

| Card Color | Represents | Purpose |
|------------|-----------|---------|
| Yellow | Story | The user story being discussed. One per session. |
| Blue | Rules | Business rules that govern the story's behavior. |
| Green | Examples | Concrete examples that illustrate each rule. |
| Pink | Questions | Unknowns that cannot be resolved in the session. |

### Procedure

1. Write the story title on a yellow card. Place it at the top.
2. As the Product Owner explains the story, capture each distinct business rule on a
   blue card. Place blue cards in a row beneath the yellow card.
3. For each blue rule, generate concrete examples on green cards. Place green cards
   beneath their corresponding blue rule. Aim for 2-4 examples per rule.
4. When the group encounters an unknown, write it on a pink card. Do not debate
   unknowns longer than 2 minutes. Assign an owner and move on.
5. If a rule accumulates more than 5 examples, the rule is likely too broad. Split it
   into two or more narrower rules.
6. If the story accumulates more than 6 rules, the story is too large. Split it into
   smaller stories.
7. If pink cards outnumber green cards, the story is not ready for implementation.
   Schedule a follow-up session after resolving the questions.

### Walkthrough: E-Commerce Checkout

**Yellow Card (Story)**: "As a customer, I want to check out my cart so I can receive my items."

**Blue Card 1 (Rule)**: "Orders require a valid shipping address."
- Green: Customer enters a complete US address with ZIP code. Order proceeds.
- Green: Customer omits the ZIP code. System rejects the address with a specific error.
- Green: Customer enters an international address. System shows international shipping options.
- Pink: Do we validate addresses against a postal service API, or accept any format?

**Blue Card 2 (Rule)**: "Payment must be authorized before order confirmation."
- Green: Customer pays with a valid credit card. Authorization succeeds. Order confirmed.
- Green: Customer's card is declined. System shows a decline message and keeps the cart intact.
- Green: Payment gateway times out after 30 seconds. System shows a retry option.
- Pink: What is the exact timeout threshold? Who decides?

**Blue Card 3 (Rule)**: "Out-of-stock items are removed from the cart at checkout."
- Green: Customer has 3 items, 1 goes out of stock during browsing. Checkout shows 2 items
  with a notification about the removed item.
- Green: All items go out of stock. Checkout is blocked with an empty-cart message.
- Green: Item quantity exceeds available stock. System adjusts quantity down and notifies.

**Blue Card 4 (Rule)**: "Order confirmation sends an email receipt."
- Green: Customer checks out successfully. Email arrives within 5 minutes with order details.
- Green: Customer's email address is invalid. Order still completes but email bounces silently.
- Pink: Do we retry bounced emails? What is the SLA for email delivery?

**Session Outcome**: 4 rules, 11 examples, 3 unresolved questions. The story is ready for
Formulation once the address validation question is resolved (it affects the scope of Rule 1).

## Feature Mapping

Use Feature Mapping when a feature is too complex for a single Example Mapping session.
Feature Mapping extends Example Mapping by adding two additional card types:

| Card Color | Represents |
|------------|-----------|
| Yellow (small) | Steps: individual user actions within the feature flow |
| Mauve | Consequences: outcomes or side effects triggered by steps |

### Procedure

1. Start with the feature goal on a yellow story card at the top.
2. Map the user journey as a sequence of yellow step cards arranged left to right.
3. At each step, identify rules (blue), examples (green), and questions (pink) as in
   standard Example Mapping.
4. Add mauve consequence cards where a step triggers downstream effects (emails sent,
   inventory updated, analytics events fired).
5. Use the visual flow to identify missing steps, redundant rules, and integration points.

Feature Mapping works best for multi-step workflows like onboarding flows, payment
processing pipelines, or approval chains where the sequence of actions matters as much
as the individual rules.

## The OOPSI Model

Use the OOPSI model (Smart and Molak) to structure scenario discovery from the outside in:

1. **Outcome**: Start with the business outcome the feature delivers. Ask: "What value does
   this create for the user or the business?"
2. **Outputs**: Identify the tangible outputs the system produces to achieve the outcome.
   Ask: "What does the user see, receive, or experience?"
3. **Process**: Map the process steps the user follows to trigger those outputs.
   Ask: "What does the user do, and in what order?"
4. **Scenarios**: Derive concrete scenarios from the process steps, covering both happy
   paths and edge cases.
5. **Inputs**: Identify the specific data inputs each scenario requires.
   Ask: "What data drives each variation?"

Work top-down through these levels. Teams that start at Inputs or Scenarios without
establishing Outcome and Outputs produce technically correct but business-irrelevant tests.

## Exploratory Outcome Paths

Use Nicieja's checklist to systematically explore edge cases and failure modes that
Three Amigos sessions might miss. For each feature, walk through these six personas:

### The Angry Path
Explore the primary failure scenario. Ask: "What happens when the main action fails?"
- Payment declined, form validation errors, permission denied, resource not found.
- Focus on the most common and most impactful failure for each rule.

### The Scary Path
Explore the highest-risk scenarios. Ask: "What could cause a data breach, financial loss,
or regulatory violation?"
- Unauthorized access to another user's data, double-charging, PII exposure.
- These scenarios often become security-focused acceptance criteria.

### The Embarrassing Path
Explore demo-day failures. Ask: "What would be humiliating to show a stakeholder?"
- Broken layouts, misspelled messages, wrong currency symbols, stale cached data.
- These scenarios protect the team's credibility and catch cosmetic-but-visible defects.

### The Forgetful Path
Explore abandonment and interruption. Ask: "What happens when the user leaves mid-process?"
- Browser closed during checkout, session timeout during form entry, back-button navigation.
- These scenarios reveal state management gaps and data persistence issues.

### The Desolate Path
Explore emptiness and absence. Ask: "What happens when there is nothing?"
- Empty search results, zero items in cart, no notifications, first-time user with no data.
- These scenarios catch null-state UI issues and missing empty-state handling.

### The Greedy Path
Explore excess and boundaries. Ask: "What happens with too much of everything?"
- 10,000 items in cart, 500-character name field, uploading a 2GB file, 1,000 concurrent users.
- These scenarios reveal performance limits, pagination gaps, and validation boundaries.

### Applying the Checklist

Walk through all six paths for each major feature during Discovery. Not every path produces
a scenario worth automating. Use judgment:
- Angry and Scary paths almost always produce critical scenarios.
- Embarrassing and Forgetful paths produce high-value scenarios for user-facing features.
- Desolate and Greedy paths produce scenarios best validated through targeted testing rather
  than full E2E automation.

## Living Documentation

### Tests as Single Source of Truth

Treat automated scenarios as the authoritative specification of system behavior. Apply
these principles:

- Every scenario must pass against the current system. A failing scenario means either the
  system has a bug or the specification is outdated. Both require immediate action.
- Delete scenarios that no longer reflect desired behavior. Commented-out or skipped
  scenarios are specification debt.
- Tag scenarios with `@Issue` or `@Story` annotations linking to backlog items. This creates
  traceability from business request to executable specification.
- Generate documentation reports from scenario results. Use Serenity BDD, Cucumber HTML
  reports, or Allure to produce stakeholder-readable evidence of system behavior.

### The Minimally Qualified Reader (MQR)

Define the target audience for every feature file. Nicieja's MQR concept asks: "Who is the
least experienced person who should be able to read and understand this specification?"

- For a payments feature, the MQR might be a new developer joining the payments team.
- For an admin dashboard, the MQR might be a support engineer who triages issues.
- Write scenarios at the MQR's level of domain knowledge. Avoid jargon the MQR would not
  know. Avoid over-explaining concepts the MQR already understands.

### Contextual Glossaries

Maintain a glossary per bounded context, not a single global glossary. This prevents
false cognates (same word, different meaning across contexts) from creating confusion:

- **Payments context**: "Transaction" means a financial exchange between customer and merchant.
- **Analytics context**: "Transaction" means a tracked user interaction event.
- **Inventory context**: "Transaction" means a stock movement record.

Place glossaries in the feature folder for each bounded context. Reference glossary terms
in scenario descriptions when introducing domain-specific language.

### Documentation Generation

Configure the build pipeline to produce living documentation artifacts:

- Generate HTML reports after every CI run. Publish them to a shared location accessible
  to non-technical stakeholders.
- Include feature coverage metrics: how many scenarios exist per feature, how many pass,
  how many are pending or manual-only.
- Use `@Manual` tags for scenarios that describe behavior verified through manual testing.
  Include them in reports to show complete coverage, not just automated coverage.

## When BDD Collaboration Adds Value

BDD collaboration (Discovery workshops, Example Mapping) is not free. Use this decision
table to determine when the investment pays off:

| Signal | BDD Collaboration | Skip Collaboration |
|--------|-------------------|-------------------|
| Multiple stakeholders with different expectations | Yes | - |
| Complex business rules with many edge cases | Yes | - |
| New domain the team has not worked in before | Yes | - |
| Regulatory or compliance requirements | Yes | - |
| Simple CRUD with obvious behavior | - | Yes |
| Team has deep existing domain knowledge | - | Yes |
| Spike or throwaway prototype | - | Yes |
| Bug fix with clear reproduction steps | - | Yes |
| Story has more than 3 acceptance criteria | Yes | - |
| Previous stories in this area had defects | Yes | - |
| Cross-team integration points | Yes | - |
| Single developer, no stakeholder ambiguity | - | Yes |

### Cost-Benefit Heuristics

- A 25-minute Three Amigos session costs roughly 1.25 person-hours (3 people x 25 min).
- A missed edge case discovered in production costs 10-100x more to fix than one discovered
  in Discovery.
- If the team consistently finds zero new insights in Three Amigos sessions for a category
  of stories, stop holding sessions for that category.
- If the team consistently discovers blocking questions in Three Amigos sessions, the
  upstream requirements process needs improvement.

### Scaling Collaboration

- For teams larger than 8 people, rotate Three Amigos participants rather than including
  everyone. Publish Example Maps to the full team after each session.
- For distributed teams, use virtual card tools (Miro, FigJam) for Example Mapping. Assign
  a facilitator to manage the timer and card placement.
- For mature teams with strong domain knowledge, replace formal Three Amigos with
  asynchronous Example Mapping: one person drafts the map, others review and annotate
  within 24 hours.
- Record decisions and rationale in the feature file's description block. This preserves
  context for future team members who were not present at Discovery.

## Collaboration Anti-Patterns

### Hand-Off Specifications
Writing specifications without the delivery team present produces "speci-fiction" --
documents that look authoritative but reflect assumptions rather than shared understanding.
Always include at least one developer and one tester in Discovery.

### Analysis Paralysis
Spending more time mapping examples than implementing the feature indicates over-specification.
Apply the rule: if a Three Amigos session exceeds 25 minutes, the story is too large. Split
it and schedule separate sessions.

### Specification as Test Script
Scenarios that read like manual test procedures ("Click the login button, enter username,
enter password, click submit") indicate the team is scripting, not specifying. Rewrite
scenarios at the business-intent level: "When the customer authenticates with valid
credentials."

### Stale Living Documentation
Reports that no one reads are waste. Measure documentation value by asking: "Has anyone
outside the development team referenced these reports in the last 30 days?" If not,
simplify the reports or stop generating them until there is demand.

### Solo Formulation
One person writing all Gherkin scenarios without review produces specifications that
reflect a single perspective. Use pair-writing or the Silent Definition Exercise: each
participant writes scenarios independently for 10 minutes, then the group compares and
merges. Differences reveal assumptions.
