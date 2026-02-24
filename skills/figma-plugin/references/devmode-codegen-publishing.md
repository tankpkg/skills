# Dev Mode, Codegen & Publishing

Sources: Official Figma Plugin Docs, FigmaToCode patterns, Tokens Studio testing patterns

## 1. Dev Mode Plugin Overview
Dev Mode plugins provide a read-only surface specifically for developers who are inspecting designs. This environment differs from the standard editor in several key ways:
- **Read-only Surface**: You cannot create, delete, or modify nodes. Attempts to do so will fail or be ignored.
- **UI Constraints**: The plugin UI occupies the full Inspect panel. It should be responsive and handle a minimum width of 300px.
- **Pages Loading**: Pages are always dynamically loaded. Plugins must handle `figma.currentPage` changes and selection events gracefully.
- **Capabilities**:
  - Read selection and node properties.
  - Listen to document and selection events.
  - Make network requests (subject to `networkAccess` permissions).
  - Use `figma.ui` for custom interactive panels.
  - Set `pluginData` and `relaunchData` (these are metadata, not node structure).
  - Use `exportAsync` to generate assets (SVG, PNG, etc.).
- **Access Model**: Dev Mode plugins can see the same content as the user. If a user has "View" access, the plugin has "View" access.

## 2. Manifest for Dev Mode
To enable Dev Mode features, your `manifest.json` must specify the correct `editorType` and `capabilities`.

```json
{
  "name": "My Dev Plugin",
  "id": "1234567890",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["dev"],
  "capabilities": ["inspect"],
  "documentAccess": "dynamic-page"
}
```
- `editorType`: Use `["dev"]` for Dev Mode only, or `["figma", "dev"]` for both.
- `capabilities`: 
  - `inspect`: General inspection UI.
  - `codegen`: Specific for code generation plugins.
  - `vscode`: Required to enable the plugin within "Figma for VS Code".
- `documentAccess`: "dynamic-page" is required for Dev Mode to handle large files efficiently.

## 3. Inspection Plugins
Inspection plugins typically show a custom UI when a node is selected. Since they are read-only, they focus on data extraction.

```typescript
if (figma.editorType === 'dev') {
  // Read-only operations allowed
  figma.showUI(__html__, { width: 300, height: 600 });
  
  figma.on('selectionchange', async () => {
    const selection = figma.currentPage.selection;
    if (selection.length > 0) {
      const node = selection[0];
      // Note: In Dev Mode, some properties might require async loading
      // but usually simple props like name/width/height are available.
      figma.ui.postMessage({
        type: 'inspect',
        name: node.name,
        width: node.width,
        height: node.height,
        id: node.id
      });
    } else {
      figma.ui.postMessage({ type: 'no-selection' });
    }
  });
}
```

## 4. Codegen Plugins
Codegen plugins are specialized for generating code snippets directly in the Inspect panel. They appear in the "Code" section of Dev Mode.

### Manifest Configuration
```json
{
  "editorType": ["dev"],
  "capabilities": ["codegen"],
  "codegenLanguages": [
    { "label": "Tailwind", "value": "tailwind" },
    { "label": "CSS", "value": "css" }
  ],
  "codegenPreferences": [
    {
      "itemType": "unit",
      "scaledUnit": "Rem",
      "defaultScaleFactor": 16,
      "default": true
    },
    {
      "itemType": "select",
      "propertyName": "tabSize",
      "label": "Tab Size",
      "options": [
        { "label": "2", "value": "2", "isDefault": true },
        { "label": "4", "value": "4" }
      ]
    }
  ]
}
```

### Implementation Logic
The `codegen.on('generate')` event is the entry point. It has a strict 15-second timeout.

```typescript
figma.codegen.on('generate', async (event) => {
  const { node, language } = event;
  
  // Custom logic to parse node properties and map to code
  const code = generateCode(node, language);
  
  return [
    {
      title: 'Component Code',
      code: code,
      language: 'TYPESCRIPT' // Syntax highlighting
    }
  ];
});

function generateCode(node: SceneNode, language: string): string {
  // Implementation of your transpiler
  return `// ${node.name} generated in ${language}\nconst MyComp = () => {};`;
}
```

## 5. VS Code Integration
Figma for VS Code allows designers to bridge the gap between Figma and the IDE. Plugins can run inside VS Code if they declare the capability.

### Detection and Handling
```typescript
// Detect VS Code environment
if (figma.vscode) {
  // Enable VS Code specific features (e.g., deeper file system linking)
}

// Opening links
// In VS Code, standard window.open fails. You must use the Figma API.
figma.ui.onmessage = (msg) => {
  if (msg.type === 'OPEN_IN_BROWSER') {
    figma.openExternal(msg.url);
  }
};
```

### Keyboard Shortcuts in Hosted UI
VS Code's hosted webviews often block standard clipboard shortcuts. You must implement listeners in your UI code to handle these manually.

```javascript
// Inside your HTML/JS (UI side)
document.addEventListener('keydown', (e) => {
  const ctrl = e.metaKey || e.ctrlKey;
  if (ctrl && e.key === 'c') document.execCommand('copy');
  if (ctrl && e.key === 'v') document.execCommand('paste');
  if (ctrl && e.key === 'x') document.execCommand('cut');
  if (ctrl && e.key === 'a') document.execCommand('selectAll');
  if (ctrl && e.key === 'z') {
    e.shiftKey ? document.execCommand('redo') : document.execCommand('undo');
  }
});
```

## 6. Events API
Plugins rely on events to react to user actions.

```typescript
// Selection changes: Trigger when user clicks a different node
figma.on('selectionchange', () => { /* selection changed */ });

// Page changes: Important for multi-page documents
figma.on('currentpagechange', () => { /* page changed */ });

// Document changes: Watch for edits in real-time
figma.on('documentchange', (event) => {
  for (const change of event.documentChanges) {
    // change.type: 'CREATE' | 'DELETE' | 'PROPERTY_CHANGE'
    console.log(change.type, change.id);
  }
});

// Lifecycle events
figma.on('run', (event) => { /* plugin started, event.command contains parameters */ });
figma.on('close', () => { /* cleanup logic */ });

// Drag and Drop: Handle nodes dropped from UI onto the canvas
figma.on('drop', (event) => { /* event.x, event.y, event.items */ });

// Timer events (for productivity plugins)
figma.on('timerstart', () => {});
figma.on('timerstop', () => {});
figma.on('timerpause', () => {});
figma.on('timerresume', () => {});
figma.on('timeradjust', () => {});
figma.on('timerdone', () => {});
```

## 7. Performance Patterns
Figma files can be massive. Efficient document traversal is critical.

### Best Practices
- **Find with Criteria**: `findAllWithCriteria` is significantly faster than `findAll` with a filter function because it's implemented natively.
```typescript
const frames = page.findAllWithCriteria({ types: ['FRAME'] });
```
- **Dynamic Page Loading**: Don't iterate over the entire document (`figma.root`). Only load pages as needed.
```typescript
const page = figma.root.children[2];
await page.loadAsync(); // Required for reading content of non-current pages
```
- **Invisible Children**: By default, `figma.skipInvisibleInstanceChildren` is true in Dev Mode. Keep it that way to avoid processing hidden nodes.
- **Batching**: Use `Promise.all` for parallel async operations.
```typescript
await Promise.all(nodes.map(async (node) => {
  const data = await processNode(node);
  figma.ui.postMessage({ type: 'node-data', data });
}));
```
- **Payload Limits**: Avoid sending massive base64 strings or complex objects through `postMessage`. Process data on the plugin side and send only what the UI needs.
- **Throttling**: The `selectionchange` event fires rapidly. Throttle your heavy calculations or data extraction.

## 8. Testing Strategies
Testing Figma plugins is tricky because they run in a proprietary sandbox.

### Unit Testing (Jest)
Mock the `figma` global object.
```typescript
// mocks/figma.js
export const figma = {
  currentPage: { selection: [], children: [] },
  createRectangle: jest.fn(),
  clientStorage: {
    getAsync: jest.fn(),
    setAsync: jest.fn(),
  },
  notify: jest.fn(),
  closePlugin: jest.fn(),
};

// In your test file
import { figma } from './mocks/figma';
global.figma = figma;
```

### End-to-End Testing (Cypress)
Standard E2E tools can't easily access the Figma canvas. The pattern is to build the plugin for the browser environment and test the UI in isolation.
```json
// package.json
{
  "scripts": {
    "build:cy": "webpack --mode=development --env PREVIEW_ENV=browser"
  }
}
```

## 9. Error Handling Patterns
Figma plugins should be resilient. A crash in the plugin can affect the designer's perception of stability.

```typescript
async function safeExecute() {
  try {
    const result = await performOperation();
    figma.ui.postMessage({ type: 'success', result });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    console.error('Plugin error:', message);
    
    // Notify the user in the Figma UI
    figma.notify(message, { error: true });
    
    // Inform the plugin UI to show an error state
    figma.ui.postMessage({ type: 'error', error: message });
  }
}
```

## 10. Publishing Checklist
Before hitting "Publish", verify these scenarios:
- [ ] **No Selection**: What happens if the plugin is run with nothing selected?
- [ ] **Wrong Type**: What happens if a user selects a Slice or a Group when you expect a Frame?
- [ ] **Multiple Selection**: Can your plugin handle 100+ selected nodes?
- [ ] **Missing Fonts**: Are you checking `figma.loadFontAsync` before editing text?
- [ ] **Remote Components**: Components from libraries might have restricted access or require `importComponentByKeyAsync`.
- [ ] **Offline Mode**: Do your network requests have timeouts and error handling for no connectivity?
- [ ] **Deleted Nodes**: Check `node.removed` if you are holding references to nodes over time.
- [ ] **Multiplayer**: Other users might move or delete nodes while your plugin is open.
- [ ] **File Size**: Test against a file with 10,000+ nodes.
- [ ] **Scaling**: Position calculations must account for rotation and scale properties.
- [ ] **Bundle Size**: Use a production build (minification) to keep the plugin fast.
- [ ] **Network Access**: Declare `allowedDomains` in manifest. Wildcards are discouraged.
- [ ] **Support**: Provide a clear contact email or GitHub repo.
- [ ] **Assets**: Ensure you have high-quality screenshots and a clear icon.

## 11. Publishing Process
- **Initial Submission**: The first version of a plugin goes through a manual review process by Figma. This can take several business days. Reviewers check for security, UX consistency, and manifest correctness.
- **Updates**: Once approved, subsequent updates are published immediately. There is no second review.
- **No Versioning**: Figma does not expose versions to users. Everyone is always on the latest version.
- **No Rollback**: If you publish a bug, you cannot "revert" in the dashboard. You must publish a new update containing the previous working code.
- **Public vs Private**: You can publish to the Community (public) or specifically for your organization (Enterprise).

## 12. Monetization (Payment API)
Figma provides a native way to charge for plugins.

### Manifest Configuration
```json
{
  "permissions": ["payments"]
}
```

### Checking Status and Initiating Checkout
```typescript
async function checkAccess() {
  const status = figma.payments.status;
  
  if (status.type === 'UNPAID') {
    // Show a paywall or trial ended message
    await figma.payments.initiateCheckoutAsync({
      interstitial: 'TRIAL_ENDED'
    });
  }
}
```
- **Models**:
  - **One-time purchase**: User pays once for lifetime access.
  - **Subscription**: Time-based access (monthly/yearly).
  - **Trials**: You can implement time-based or usage-based trials by checking `firstRun` timestamps in `clientStorage`.
- **Processing**: Figma handles the billing, tax, and payout logic.
- **Usage tracking**: Use `figma.clientStorage` to store local usage metrics for trial logic.

## 13. Relaunch Buttons
Relaunch buttons are persistent shortcuts that appear in the right-hand sidebar when a specific node is selected.

### Manifest
```json
{
  "relaunchButtons": [
    { "command": "edit", "name": "Edit Component" },
    { "command": "open", "name": "View Documentation", "multipleSelection": true }
  ]
}
```

### Application
```typescript
// Attach relaunch data to a node
node.setRelaunchData({ 
  edit: 'Click to open the editor for this component',
  open: 'Open the technical documentation'
});

// To remove
node.setRelaunchData({});
```

## 14. OAuth Integration
Many plugins need to connect to external services (GitHub, Jira, Linear).

- **Implementation**: Use `figma.showUI` to render an `<iframe>`. The OAuth redirect URI must be the URL of your hosted UI.
- **Storage**: Store access tokens and refresh tokens in `figma.clientStorage`. This is persistent across sessions and unique to the user + plugin.
- **Security**: Never store client secrets in the plugin code. Always use a backend broker for the code-to-token exchange.
- **Flow**:
  1. User clicks "Login" in Plugin UI.
  2. UI opens a popup or redirects the iframe to the provider's OAuth page.
  3. Provider redirects back to your callback URL with an authorization code.
  4. Your backend exchanges the code for tokens.
  5. Backend communicates the token back to the UI (e.g., via postMessage or a polling mechanism).
  6. UI sends token to `main` plugin code.
  7. `main` code saves token to `figma.clientStorage`.

## 15. Advanced Developer Patterns
- **Library Imports**: Use `figma.importComponentByKeyAsync(key)` to pull components from external libraries into the current file.
- **Selection Persistence**: If your plugin UI needs to keep track of a "source" node while the user selects other things, store the `node.id` and use `figma.getNodeById(id)` to retrieve it later. Always check if it still exists.
- **Node Removal**: Listen to `documentchange` to detect when a node your plugin is currently displaying has been deleted by another user.
- **Image Processing**: Use `exportAsync` on a node to get a `Uint8Array`, then send it to the UI to be converted into a Blob/URL for display.
- **Performance - Layout**: Avoid frequent reads of `absoluteTransform` or `x/y` in a loop; if you need to calculate complex layouts, try to do it in a single pass.
- **Memory Management**: If your plugin creates many UI elements or holds onto many references, ensure you clean them up on `figma.on('close')`.

---

This reference covers the operational and lifecycle aspects of Figma plugin development. For node-specific manipulation or UI design patterns, refer to the respective specialized reference files in the skill directory.
