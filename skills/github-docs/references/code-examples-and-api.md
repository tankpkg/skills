# Code Examples and API Documentation
Sources: Google Developer Documentation Style Guide, Stripe API docs patterns, tRPC/Drizzle/Got documentation analysis

## The 7 Rules of Effective Code Examples

High-quality code examples are the primary way developers evaluate a library. Follow these rules to ensure clarity and utility.

### 1. Complete and Runnable
Ensure every example is a self-contained unit. A developer should be able to copy the snippet, paste it into a file, and run it with minimal effort. Include necessary imports and initialization logic.
- Always include `import` or `require` statements.
- Provide mock initialization for external services (e.g., `const client = new Client({ apiKey: '...' })`).
- If the example depends on an environment variable, explicitly mention it in a comment like `// Ensure PROCESS_ENV_KEY is set`.

### 2. Realistic but Minimal
Use real-world use cases that solve actual problems. Avoid abstract logic that does not demonstrate the library's value. 
- Strip away all noise that is not related to the specific feature being demonstrated.
- Do not include boilerplate like heavy logging or complex error handling unless that is the focus of the example.
- Focus on the shortest path to a successful result.

### 3. Progressive Disclosure
Start with the simplest possible "Hello World" example. Gradually introduce more complex scenarios, configurations, and edge cases.
- Level 1: Basic setup and one function call.
- Level 2: Passing options and handling common variations.
- Level 3: Integration with other parts of the system or advanced customization.
This prevents overwhelming new users while still providing value to advanced developers.

### 4. Show Error Handling
Documentation that only shows the "happy path" is incomplete. Include examples of how to handle common failures, network errors, or invalid inputs.
- Use explicit `try/catch` blocks in examples where appropriate.
- Demonstrate how to check for specific error codes or classes provided by the library.
- This builds trust and prepares developers for production environments where things inevitably go wrong.

### 5. Annotate with Comments
Use comments to explain why a specific function is called or what a non-obvious parameter does.
- Focus on the "why" rather than the "what." Instead of `// Set timeout to 100`, use `// Prevent long-running requests from blocking the main thread`.
- If the code is self-documenting, keep comments minimal to avoid clutter.
- Use line-level comments for tactical explanations and block comments for architectural context.

### 6. Use Realistic Data
Replace generic placeholders like `foo`, `bar`, and `baz` with meaningful data.
- User documentation: Use `jane.doe@example.com` or `user_01HG`.
- Product documentation: Use `sku: "TSHIRT-BLUE-L"` or `price: 29.99`.
- Realistic data helps developers map the code to their own domain and understand the expected data types and formats visually.

### 7. Show Expected Output
Always include a comment showing the result of the execution. This allows developers to verify their understanding without having to run the code.
- Use a consistent format for output comments: `// => { status: 'success', id: 123 }`.
- For multi-line outputs, use a block comment after the execution line.
- This serves as a "mental assertion" for the developer reading the docs.

## Code Example Structure Pattern

Standardize the presentation of code examples to improve scannability across the README and supporting documents.

### Basic Usage ("The Quick Start")
The introductory snippet. It must be under 10 lines and demonstrate the core value proposition. Use default settings and no optional parameters.
```typescript
import { greet } from 'my-lib';

// Simple greeting with default options
const message = greet('World');
console.log(message); // => "Hello, World!"
```

### Common Use Case
A 15-20 line example showing how the library solves a standard problem. This should be the most prominent example in the documentation.
```typescript
import { createClient } from 'my-lib';

const client = createClient({ token: 'your-api-token' });

// Fetching user details with error handling
try {
  const user = await client.users.get('user-123');
  console.log(user.name);
} catch (error) {
  console.error('Failed to fetch user:', error.message);
}
```

### Advanced Usage
Demonstrate deep configuration, custom middleware, or integration with other tools. Use this section to showcase the library's flexibility.
- Complex filtering/sorting logic.
- Custom authentication flows.
- Batch processing or streaming data patterns.

### Error Handling Example
Dedicated snippet showing how to wrap calls in try/catch blocks or handle rejected promises specifically for the library's custom error classes.
- Distinguish between network errors and validation errors.
- Show how to implement retry logic or graceful fallbacks.

## Before and After Examples

For migration guides or refactoring tools, use side-by-side comparisons or clear "Before/After" headers.

### Refactoring Comparison
| Before (Native/Verbose) | After (With MyLib) |
|--------------------------|---------------------------|
| `fetch(url).then(res => res.json()).then(...)` | `const data = await myLib.get(url);` |
| `if (!res.ok) throw new Error(...)` | `// Errors handled automatically` |
| `const result = list.filter(...).map(...)` | `const result = myLib.query(list, ...);` |

### Migration Scenario
When moving from v1 to v2, show exactly what changed in the syntax.
- Highlight deprecated methods and their replacements.
- Use `diff` blocks to show additions and removals clearly.
```diff
- const client = new Client(key);
+ const client = createClient({ apiKey: key });
```

## API Reference Documentation Pattern

The API reference must be precise and exhaustive. Use a structured layout for every exported function, class, and method.

### Function Header
Use a consistent heading level (usually `###`) for each function name. Include a one-sentence summary of its purpose.

### Function Signature
Display the full signature including types. Use code blocks for readability.
```typescript
function transform(input: RawData, options?: TransformOptions): ResultData
```

### Parameter Table
Document every input parameter clearly.

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | `RawData` | Yes | - | The raw data object retrieved from the database. |
| `options` | `Object` | No | `{}` | Optional configuration for the transformation. |
| `options.strict` | `boolean` | No | `false` | If true, throws an error on missing fields. |

### Return Value
Describe the structure of the returned object or the behavior of the returned promise. Mention if the result can be null or undefined.
- "Returns a `Promise` that resolves to a `User` object."
- "Returns `null` if the record is not found and `strict` is false."

### Throws and Errors
List all custom errors the function might throw. Explain the conditions that trigger each error so developers can implement targeted catch blocks.
- `InvalidTokenError`: Thrown when the provided API key is expired or malformed.
- `RateLimitError`: Thrown when the client exceeds the allowed request frequency.

### Usage Example
Provide a 3-5 line snippet showing the function in isolation.

## Options Object Documentation Pattern

When functions accept a large configuration object, document the properties in a dedicated table.

### Property Table
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `timeout` | `number` | `3000` | Max time in milliseconds before the request fails. |
| `retry` | `boolean` | `true` | Whether to automatically retry on network failure. |
| `headers` | `Record<string, string>` | `{}` | Custom HTTP headers for the request. |

### Grouping Options
If an object has more than 10 options, group them into categories such as:
- **Connection**: Timeout, retry, proxy settings.
- **Formatting**: Locales, timezone, decimal precision.
- **Hooks**: Lifecycle callbacks and event listeners.
This improves scannability and helps users find relevant settings quickly.

## HTTP API Documentation Structure

For REST or GraphQL APIs, follow a standardized endpoint documentation structure.

### Endpoint and Method
State the HTTP method and the full path clearly at the top.
`POST /v1/customers`

### Authentication
Specify the required scope or permission level.
- "Requires `customers:write` scope."
- "Authentication: Bearer Token in `Authorization` header."

### Request Body Table
Document the JSON payload. Include data types, constraints (e.g., "max 255 chars"), and required status.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Full name of the customer. |
| `email` | `string` | Yes | Valid email address for notifications. |

### Curl Example
Provide a shell command that users can run immediately in their terminal.
```bash
curl -X POST https://api.example.com/v1/customers \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com"}'
```

### Response Example
Show a successful `201 Created` JSON response. Include all fields, even optional ones, to provide a complete schema overview.
```json
{
  "id": "cust_998877",
  "object": "customer",
  "created": 1672531200,
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

### Error Response Table
List common HTTP error codes and the structure of the error body.
- `400 Bad Request`: Missing required fields.
- `401 Unauthorized`: Invalid or missing API key.

## TypeScript and JSDoc Patterns

Use inline documentation to power IDE features like IntelliSense and provide a seamless development experience.

### Inline JSDoc
Every public member must have a JSDoc block.
```typescript
/**
 * Fetches user data from the remote server.
 * 
 * @example
 * const user = await getUser('123');
 * 
 * @param id - The unique identifier for the user.
 * @returns A promise resolving to the User object.
 * @throws {NotFoundError} If the user does not exist.
 */
async function getUser(id: string): Promise<User>
```

### Type Definitions
Export interfaces and types so users can benefit from strong typing in their own code. 
- Document complex union types or enums with comments on each member.
- Use TSDoc tags like `@alpha`, `@beta`, or `@deprecated` to signal the stability of the API.

## Inline Examples vs Separate Directory

Choose the right location for code based on complexity and purpose.

### Use Inline Examples When:
- Demonstrating a single function or method in a README or reference page.
- The code is under 20 lines and requires no external files.
- It is essential for understanding the immediate context of the documentation.

### Use an `/examples` Directory When:
- The example requires multiple files or complex project structure.
- It demonstrates a full project integration (e.g., Express + Database + Auth).
- The code requires a dedicated `package.json`, environment variables, or build step.
- You want to provide a runnable playground that users can clone and experiment with.

## Interactive Examples

Improve developer conversion by providing interactive playgrounds.

- **CodeSandbox**: Best for frontend components and React/Vue/Svelte libraries.
- **StackBlitz**: Ideal for Node.js, CLI tools, and full-stack frameworks.
- **GitHub Codespaces**: Perfect for complex systems that require specific environments or Docker containers.
- **Try-it-now buttons**: Use clear call-to-action buttons in the README to link to these environments.

## Testing Documentation Examples

Broken examples damage the credibility of a library and frustrate users.

### CI Validation
Integrate example testing into your GitHub Actions workflow.
- Use `ts-node` to run TypeScript examples directly.
- Implement `jest` or `vitest` to assert that examples produce the expected output.

### Documentation Extractors
Use tools like `markdown-doctest` or `mdsh` that extract code blocks from Markdown files and run them as tests. This ensures that what the user sees in the docs is exactly what was tested in CI.

### Version Alignment
When releasing a new version, verify that all examples in the README still work with the latest changes. Use automated scripts to update version strings in examples if necessary to prevent "copy-paste failures" due to outdated version numbers.

## Documentation Anti-Patterns

Avoid these common mistakes that frustrate developers and increase support overhead.

- **Incomplete Snippets**: Missing imports or variables that are defined "somewhere else."
- **Toy Data**: Using `foo` and `bar` instead of contextually relevant data.
- **Unexplained Magic Values**: Hardcoded numbers or strings without a comment explaining their significance.
- **Outdated Syntax**: Using `var` in 2024 or ignoring modern async/await patterns in favor of nested callbacks.
- **Missing Peer Dependencies**: Failing to mention that an example requires `react` or `lodash` to be installed.
- **Excessive Abstraction**: Wrapping simple logic in unnecessary design patterns or custom utilities for the sake of "cleanliness."
- **No Response Schema**: Showing a request but leaving the user guessing about the shape of the data returned by the API.
- **Inconsistent Formatting**: Mixing tabs and spaces, or varying naming conventions (camelCase vs snake_case) between different examples.
- **Wall of Code**: Providing a 50-line snippet without any break or intermediate explanation.
- **Hidden Prerequisites**: Assuming the user has a database running or a specific port open without stating it.
