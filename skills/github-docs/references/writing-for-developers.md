# Writing for Developers
Sources: Google Developer Documentation Style Guide, Write the Docs community, Diátaxis framework, Gen-Z UX research

Effective developer documentation prioritizes clarity, speed of comprehension, and utility. Developers do not read documentation like a novel; they scan it for answers. This reference defines the linguistic and structural standards for creating high-performance GitHub documentation that meets the high expectations of modern software engineers.

## Core Writing Principles for Developer Docs

Adhere to these fundamental principles to ensure documentation is direct, unambiguous, and professional.

### Active Voice
Use active voice to identify who or what is performing an action. Active voice is shorter and more direct than passive voice. It clearly assigns responsibility for an action.
*   **Good**: "The function returns a promise."
*   **Bad**: "A promise is returned by the function."
*   **Good**: "The script modifies the configuration file."
*   **Bad**: "The configuration file is modified by the script."

### Present Tense
Write in the present tense even for actions that happen in the future or after a specific trigger. Present tense is easier to read and more immediate.
*   **Good**: "The CLI sends the data to the server."
*   **Bad**: "The CLI will send the data to the server."
*   **Good**: "When you click 'Save', the application updates the record."
*   **Bad**: "When you click 'Save', the application will be updating the record."

### Second Person
Address the reader directly as "you." This makes instructions feel personal and actionable. Avoid "the user," "the developer," or third-person abstractions.
*   **Good**: "You can configure the timeout in the settings."
*   **Bad**: "Users can configure the timeout in the settings."
*   **Good**: "If you encounter an error, check the logs."
*   **Bad**: "When developers encounter errors, they should check the logs."

### Short Sentences
Limit sentences to a maximum of 25 words. Long, winding sentences increase cognitive load and make scanning difficult. If a sentence contains more than one comma or uses complex conjunctions, consider splitting it.

### One Idea per Sentence
Do not pack multiple instructions or concepts into a single sentence. Give each concept its own space to be processed by the reader.
*   **Bad**: "Download the package then run the install script and make sure to set your environment variables before starting the server."
*   **Good**: "Download the package. Run the install script. Set your environment variables before you start the server."

### Parallelism
Use the same grammatical structure for lists and headings. If the first item in a list starts with a verb, all items should start with a verb.
*   **Bad**:
    *   Initialize the database.
    *   Connecting to the server.
    *   User authentication.
*   **Good**:
    *   Initialize the database.
    *   Connect to the server.
    *   Authenticate the user.

## The Gen-Z Attention Span: Problem and Solutions

Modern developers, particularly those from Gen-Z, have a extremely high "time-to-value" threshold. Documentation must prove its worth within seconds or the developer will look for an alternative library.

### Front-load Value (The 3-Second Rule)
The first 100 words of any page must define exactly what the tool does and why it matters. Do not bury the value proposition under history, philosophy, or "Special Thanks" sections. Use a one-sentence tagline that summarizes the core utility.

### Visual > Text
Prioritize diagrams, code blocks, and tables over long paragraphs. A well-designed Mermaid diagram or a clean screenshot replaces hundreds of words of architectural description.
*   Use flowcharts for logic.
*   Use sequence diagrams for network requests.
*   Use tables for comparison and configuration options.

### Scannable Formatting
Use formatting to guide the eye through the "F-pattern" of reading:
*   **Bold keywords**: Highlight critical terms within sentences so they stand out during a fast scan.
*   **Bullets**: Use lists for any sequence or collection of items. Lists are easier to process than comma-separated values in a paragraph.
*   **Short paragraphs**: Keep paragraphs to 3-4 lines maximum. White space is as important as the text itself.

### Instant Gratification
Provide a working code example or a "Quick Start" command within the first 60 seconds of scrolling. The faster a developer sees the tool in action on their machine, the more likely they are to invest time in reading the rest of the docs.

### TL;DR Sections
For long-form content, complex tutorials, or architectural overviews, include a "TL;DR" summary at the top. List the primary steps, the expected outcome, and links to the most relevant sub-sections.

## Tone Calibration

The tone should be professional and authoritative but accessible. It must reflect a peer-to-peer relationship between the author and the developer.

### Conversational but not Chatty
Write like you are explaining a concept to a respected colleague. Avoid slang, inside jokes, memes, or unnecessary fluff that dates the documentation.
*   **Before**: "Hey guys! So, I was thinking it'd be super cool to show you how this API works because it's totally awesome."
*   **After**: "This guide demonstrates how to integrate the API into your application and manage its core features."

### Confident but not Arrogant
State facts clearly without bragging about the tool's performance or features. Avoid marketing adjectives like "groundbreaking," "world-class," or "game-changing."
*   **Before**: "Our revolutionary algorithm is the fastest on the planet, hands down, and will crush any competition."
*   **After**: "The algorithm processes 10,000 requests per second in standard benchmarking environments."

### Helpful but not Condescending
Assume the reader is a competent engineer who lacks the specific context of your project. Explain "how" and "why" without implying a task is "easy" or "trivial."
*   **Before**: "It is trivial to set up this environment if you know basic Linux, so don't mess it up."
*   **After**: "Follow these steps to configure your Linux environment for local development."

### Professional but not Stuffy
Avoid overly formal, academic, or legalistic language. Use modern, standard technical terminology.
*   **Before**: "It is incumbent upon the developer to utilize the aforementioned methods to facilitate data persistence."
*   **After**: "Use these methods to save data to the database."

## Words and Phrases to Avoid

Certain words create friction, imply judgment, or add noise without value. Remove them during the editing phase.

| Avoid | Reason | Alternative |
| :--- | :--- | :--- |
| "just", "simply" | Condescending; implies the task is trivial. | Omit entirely. |
| "obviously", "clearly" | Alienating; if it were obvious, the user wouldn't be reading. | Explain the concept or omit. |
| "easy", "straightforward" | Subjective; varies based on experience level. | "Standard", "Typical". |
| "will" (Future tense) | Adds unnecessary length and distance. | Use present tense. |
| "leverage", "utilize" | Stuffy and formal. | "Use". |
| "seamlessly" | Marketing fluff; rarely true in software. | Describe the integration. |
| "please" | Unnecessary; instructions are imperative commands. | Use imperative verbs. |
| "once" | Ambiguous; can mean "after" or "one time". | "After". |
| "basically" | Filler word that weakens the statement. | Omit entirely. |

## Words and Phrases to Use

Use strong, specific language to reduce ambiguity and drive action.

### Imperative Verbs
Start instructions with a clear command. This removes ambiguity about who needs to act.
*   "Run `npm install`."
*   "Create a new file named `.env`."
*   "Configure the database credentials in `config.json`."
*   "Add the middleware to your Express stack."

### Precise Language
Be exact about data types, states, and outcomes. Avoid vague terms like "thing," "stuff," or "data" when a more specific term exists.
*   **Good**: "The function returns `null` if the ID is not found."
*   **Bad**: "The function doesn't return anything if there is no ID."
*   **Good**: "The process terminates with exit code 1."
*   **Bad**: "The process stops if something goes wrong."

## Paragraph Structure Rules

Structure paragraphs for rapid consumption and logical flow using the "Inverted Pyramid" pattern.

1.  **Lead with the conclusion/action**: The first sentence must contain the most important information.
2.  **Support with context**: The following sentences provide the "why" or additional details.
3.  **3-4 lines max**: Break up long blocks of text to maintain white space and reduce visual fatigue.
4.  **One topic per paragraph**: If you transition to a new concept or instruction, start a new paragraph.
5.  **Use headers aggressively**: Insert a descriptive header every 3-5 paragraphs to provide anchor points for scanning.

## Heading Hierarchy Best Practices

Headings serve as the primary navigation tool for the reader's eyes.

### Descriptive Headings
Use headings that describe the benefit or the specific task, not just the abstract topic.
*   **Good**: "How to authenticate with OAuth2"
*   **Bad**: "Authentication"
*   **Good**: "Setting up your development environment"
*   **Bad**: "Setup"

### Question-format Headings
For how-to content and FAQs, use questions that reflect common developer search queries.
*   **Example**: "How do I reset my API key?"
*   **Example**: "Where are the logs stored?"

### Consistent Grammatical Structure
Ensure all headings at the same level follow the same pattern.
*   **Consistent (Imperative)**:
    *   ## Install the CLI
    *   ## Create your account
    *   ## Deploy your project
*   **Inconsistent**:
    *   ## Installation
    *   ## Creating an account
    *   ## How to deploy

## Accessibility in Documentation

Documentation must be usable by everyone, including developers using assistive technologies.

### Alt Text for Images
Describe the purpose and information contained in the image, not just its visual appearance.
*   **Good**: "Diagram showing the flow of a GET request from the client to the database through the API gateway."
*   **Bad**: "A flowchart with blue boxes and arrows."

### Beyond Color
Never use color as the sole indicator of meaning.
*   **Bad**: "Correct parameters are shown in green, incorrect in red."
*   **Good**: "Correct parameters are marked with a checkmark (✓), incorrect with a cross (✗)."

### Semantic Hierarchy
Maintain a logical heading order (H1 -> H2 -> H3). Never skip levels to achieve a specific font size. This breaks navigation for screen reader users who rely on headers to understand the document's structure.

## Handling Code in Text

Properly formatting code elements within your prose improves readability and scannability.

### Inline Code
Use backticks for file names, variable names, functions, and inline commands.
*   **Example**: "The `config.js` file contains the `PORT` variable."

### Code Blocks
Use triple backticks with a language specifier for snippets longer than one line.
*   Always provide a "copy" button experience if possible.
*   Use comments sparingly to explain complex logic within the snippet.

## Inclusive Language in Tech

Writing for a global audience requires awareness of language choices that may be exclusionary or based on outdated metaphors.

*   **Avoid**: master/slave, whitelist/blacklist.
*   **Use**: primary/replica (or leader/follower), allowlist/denylist.
*   **Avoid**: Gendered pronouns when the identity is unknown.
*   **Use**: Gender-neutral "they" or address the reader as "you."

## Anti-patterns in Documentation

Avoid these common mistakes that reduce the quality and reliability of your documentation.

| Anti-pattern | Before | After |
| :--- | :--- | :--- |
| Wall of Text | A single 15-line paragraph explaining the entire architecture and setup process including dependencies and variables. | Break into three paragraphs with a bulleted list for dependencies and a code block for variables. |
| The "Black Box" | "Run the script and wait for it to finish." | "Run `sh install.sh`. The process takes 2-3 minutes. You will see a 'Success' message when finished." |
| Missing Context | "Enter the key here." | "Paste your API key into the `API_KEY` field in the `.env` file." |
| Tutorial as Reference | A guide that mixes step-by-step instructions with 50 pages of API property definitions. | Separate the "Quick Start" guide from the "API Reference" section. |
| The Outdated Snippet | A code example that uses version 1.0 syntax in 3.0 documentation. | Use a CI process to verify code snippets or manually test every snippet before release. |
| The Broken Link | A link to a dependency that returns a 404. | Regularly audit external links or use a link-checking tool in your CI pipeline. |
| The Missing Exit | A tutorial that leaves the user with a running process but no instructions on how to stop it. | Include a final step: "To stop the server, press `Ctrl+C` in your terminal." |

## The Diátaxis Framework: Context-Aware Writing

The style of your writing should shift depending on which of the four documentation types you are creating:

1.  **Tutorials (Learning-oriented)**: Use a gentle, step-by-step tone. Focus on the experience of doing.
2.  **How-to Guides (Task-oriented)**: Use strict imperative voice. Focus on solving a specific problem.
3.  **Reference (Information-oriented)**: Use neutral, objective, and extremely precise language. Focus on facts.
4.  **Explanation (Understanding-oriented)**: Use a more discursive tone. Focus on concepts, design choices, and architecture.

## The "Curse of Knowledge" Checklist

Before publishing, review your documentation against this checklist. Assume the perspective of a developer who has never seen your project before.

*   [ ] Have you defined all acronyms on their first use?
*   [ ] Is there a "Prerequisites" section listing required software and exact versions?
*   [ ] Does the "Quick Start" work on a fresh machine without hidden global dependencies?
*   [ ] Are there links to related documentation for deeper dives into complex topics?
*   [ ] Have you tested every code snippet by copying and pasting it into a fresh terminal?
*   [ ] Does the documentation explain "why" a specific configuration is recommended?
*   [ ] Is the most important information visible "above the fold" without scrolling?
*   [ ] Are error messages explained with clear, step-by-step resolution paths?
*   [ ] Is the language inclusive and free of culturally specific idioms or sports metaphors?
*   [ ] Does the documentation provide a clear way for users to report issues or suggest edits?
*   [ ] Are external dependencies version-locked in your examples to prevent breaking changes?

## Peer Review Protocol

When reviewing documentation written by others (or your own after a 24-hour break), ask these three questions:
1.  **Can I find the answer in 10 seconds?** (Scanning efficiency)
2.  **Is there any word that doesn't add value?** (Conciseness)
3.  **Will this snippet still work in 6 months?** (Sustainability)

## Overcoming the Curse of Knowledge

The "Curse of Knowledge" is the cognitive bias where an expert finds it difficult to imagine what it is like for a novice to learn a subject.
*   **Rubber Duck Documentation**: Explain your tool to someone outside your immediate team.
*   **Fresh Eyes Testing**: Ask a developer from a different department to follow your Quick Start guide while you watch (without helping).
*   **Audit for Assumptions**: Search for phrases like "as you already know" or "refer to the standard setup." These are red flags for hidden assumptions.

By following these guidelines, you create documentation that respects the developer's time and reduces the cognitive load required to use your software. Consistency in tone and structure builds trust and ensures that your project is accessible to the widest possible audience. Documentation is not just an auxiliary task; it is a core component of the developer experience. High-quality docs lead to fewer support requests, faster onboarding, and higher adoption rates for your tools and libraries.
