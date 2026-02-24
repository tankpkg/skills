# Plugin Architecture & Setup

Sources: Official Figma Plugin Docs, figma/plugin-samples, Tokens Studio patterns

## Dual-Context Model

Figma plugins operate in two isolated environments that communicate via asynchronous message passing. This separation ensures that heavy UI operations don't block the main Figma thread.

```text
┌──────────────────────────────────────────┐      ┌──────────────────────────────────────────┐
│          Main Thread (Sandbox)           │      │            UI Thread (iframe)            │
├──────────────────────────────────────────┤      ├──────────────────────────────────────────┤
│ - Context: QuickJS (Fast, Secure)        │      │ - Context: Full Browser (Chrome)         │
│ - Access: figma.* API                    │◀────▶│ - Access: DOM, Web APIs, Network         │
│ - No DOM/CSS/Network access              │      │ - No figma.* API access                  │
│ - Global: `figma`, `__html__`            │      │ - Global: `window`, `parent`, `document` │
│ - Constraints: No `fetch`, no `alert`    │      │ - Constraints: No node access            │
│ - Role: Node manipulation, file logic    │      │ - Role: UI, heavy calc, network calls    │
└──────────────────────────────────────────┘      └──────────────────────────────────────────┘
             ▲                                                   ▲
             │          figma.ui.postMessage(data)               │
             └───────────────────────────────────────────────────┘
                    parent.postMessage({ pluginMessage: data }, '*')
```

### Type-Safe Communication Pattern
Using TypeScript to enforce message structures across contexts is a best practice.

```typescript
// types.ts
export type PluginMessage = 
  | { type: 'create-shapes'; count: number }
  | { type: 'notify'; message: string };

export type UIMessage = 
  | { type: 'selection-changed'; ids: string[] }
  | { type: 'error'; message: string };

// code.ts (Main)
figma.ui.onmessage = (msg: PluginMessage) => {
  if (msg.type === 'create-shapes') {
    const rect = figma.createRectangle();
    figma.ui.postMessage({ type: 'selection-changed', ids: [rect.id] } as UIMessage);
  }
};

// ui.ts (UI)
function sendMessage(msg: PluginMessage) {
  parent.postMessage({ pluginMessage: msg }, '*');
}

window.onmessage = (event: MessageEvent<{ pluginMessage: UIMessage }>) => {
  const msg = event.data.pluginMessage;
  if (msg.type === 'selection-changed') console.log(msg.ids);
};
```

## Plugin Lifecycle

- **Start:** Plugin code executes. `figma.showUI` is typically the first call if UI is needed.
- **Run:** The main thread stays alive as long as the UI is open.
- **Background Tasks:** Plugins can register for background events (like `document-change`) but usually close after their primary task.
- **Termination:**
  - **Programmatic:** `figma.closePlugin()` must be called to end execution and save undo history.
  - **Implicit:** If the user closes the UI window, the plugin is terminated.
  - **Relaunch:** When a user clicks a relaunch button on a node, the plugin starts with a specific `figma.command`.

## Manifest.json Complete Reference

The `manifest.json` defines how Figma loads and executes your plugin.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name displayed in the Figma UI. |
| `id` | string | Unique 18-digit ID assigned during the first development save. |
| `api` | string | Version of the plugin API (e.g., "1.0.0"). |
| `main` | string | Path to the compiled JS file for the main thread. |
| `ui` | string | Path to the HTML file for the UI thread. |
| `editorType` | string[] | Array containing `"figma"` and/or `"figjam"`. |
| `documentAccess` | string | `"none"` (default) or `"dynamic-page"` for Dev Mode plugins. |
| `networkAccess` | object | Config for external requests (see below). |
| `permissions` | string[] | List of requested user/file data access. |
| `capabilities` | string[] | Specific features like `"codegen"` or `"inspect"`. |
| `codegenLanguages` | object[] | For Dev Mode: `[{"label": "CSS", "value": "css"}]`. |
| `codegenPreferences` | object[] | Configurable settings for the code generator. |
| `menu` | object[] | Nested menu structure: `{"name": "Sub", "menu": [...]}` or `{"command": "id"}`. |
| `relaunchButtons` | object[] | `{"command": "id", "name": "Label"}` tied to node metadata. |
| `parameters` | object[] | Input schema for parameter-only or hybrid plugins. |
| `parameterOnly` | boolean | If `true`, the plugin runs solely via parameters without `figma.showUI`. |
| `enableProposedApi` | boolean | Allows usage of beta API features. |
| `enablePrivatePluginApi` | boolean | Internal/Private API access (Enterprise only). |
| `build` | string | Command executed by Figma's internal publishing tool. |

### Network Access Patterns
Figma enforces a strict Content Security Policy. Setting to `[]` or omitting denies all network access.
```json
"networkAccess": {
  "reasoning": "We need to fetch design tokens and log analytics.",
  "allowedDomains": [
    "none",
    "https://*.tokens.com",
    "https://api.mixpanel.com",
    "*"
  ],
  "devAllowedDomains": ["http://localhost:3000"]
}
```

### Permissions Breakdown
- `currentuser`: Access the logged-in user's name and ID.
- `activeusers`: Access details of users currently active in the file.
- `fileusers`: Access the list of all users with access to the file.
- `payments`: Required for plugins that use Figma's native monetization.
- `teamlibrary`: Access team-level components and styles.

## Full Manifest Examples

### 1. Design & FigJam Plugin
```json
{
  "name": "Asset Exporter",
  "id": "123456789012345678",
  "api": "1.0.0",
  "main": "dist/code.js",
  "ui": "dist/ui.html",
  "editorType": ["figma", "figjam"],
  "networkAccess": { "allowedDomains": ["*"] }
}
```

### 2. Dev Mode Codegen Plugin
```json
{
  "name": "React Generator",
  "id": "234567890123456789",
  "api": "1.0.0",
  "main": "dist/code.js",
  "editorType": ["figma"],
  "capabilities": ["codegen"],
  "codegenLanguages": [
    { "label": "TypeScript", "value": "typescript" }
  ]
}
```

### 3. Parameter-Only Utility
```json
{
  "name": "Find and Replace",
  "id": "345678901234567890",
  "api": "1.0.0",
  "main": "dist/code.js",
  "editorType": ["figma"],
  "parameters": [
    { "name": "Find", "key": "find", "description": "Text to find" },
    { "name": "Replace", "key": "replace", "description": "Replacement text" }
  ]
}
```

## Project Setup (Quickstart)

1. **Scaffold:** Figma Desktop → Plugins → Development → New Plugin → Custom.
2. **Core Dependencies:**
   ```bash
   npm install --save-dev @figma/plugin-typings typescript concurrently
   ```
3. **Recommended `tsconfig.json`:**
   ```json
   {
     "compilerOptions": {
       "target": "es6",
       "lib": ["es6", "dom"],
       "module": "es6",
       "moduleResolution": "node",
       "typeRoots": ["./node_modules/@types", "./node_modules/@figma"],
       "strict": true,
       "noImplicitAny": true,
       "esModuleInterop": true
     }
   }
   ```
4. **Linting:** 
   Add `@figma/eslint-plugin-figma-plugins` to enforce sandbox-safe code patterns.

## Build Tooling Decision Table

| Tool | Speed | Complexity | Best For |
| :--- | :--- | :--- | :--- |
| **Webpack + ts-loader** | Moderate | High | Enterprise-grade, massive plugins, established teams. |
| **Webpack + SWC** | Fast | High | Projects needing Webpack plugins but SWC speed. |
| **Vite + esbuild** | Ultra Fast | Moderate | **Gold Standard.** Modern DX, instant feedback. |
| **esbuild CLI** | Instant | Low | Fast scripts, one-off tools, minimal setup. |
| **Create Figma Plugin** | Fast | Low | Quick starts using Preact or Vanilla JS. |
| **Plugma** | Fast | Low | Framework-agnostic Vite wrapper for Figma. |

## Webpack Config Pattern (The Inline Secret)

Figma requires UI code to be inlined because it doesn't host multiple files in the iframe sandbox.

```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const InlineChunkHtmlPlugin = require('react-dev-utils/InlineChunkHtmlPlugin');

module.exports = (env, argv) => ({
  mode: argv.mode === 'production' ? 'production' : 'development',
  devtool: argv.mode === 'production' ? false : 'inline-source-map',
  entry: {
    ui: './src/ui.tsx',
    code: './src/code.ts'
  },
  module: {
    rules: [
      { test: /\.tsx?$/, use: 'ts-loader', exclude: /node_modules/ },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.(png|jpg|gif|webp|svg)$/, use: 'url-loader' }
    ]
  },
  resolve: { extensions: ['.tsx', '.ts', '.jsx', '.js'] },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/ui.html',
      filename: 'ui.html',
      chunks: ['ui'],
      cache: false
    }),
    new InlineChunkHtmlPlugin(HtmlWebpackPlugin, [/ui/])
  ],
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist')
  }
});
```

## Vite + esbuild Config Pattern (Modern Best Practice)

This setup uses Vite for the UI (React/Vue/Svelte) and a simple esbuild script for the sandbox.

### 1. `vite.config.ts`
```typescript
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    target: 'esnext',
    assetsInlineLimit: 100000000,
    cssCodeSplit: false,
    outDir: 'dist',
    rollupOptions: {
      input: { ui: 'src/ui.html' }
    }
  }
});
```

### 2. `package.json` Scripts
```json
{
  "scripts": {
    "build:ui": "vite build",
    "build:main": "esbuild src/code.ts --bundle --outfile=dist/code.js --target=es6",
    "build": "npm run build:ui && npm run build:main",
    "watch": "concurrently \"vite build --watch\" \"npm run build:main -- --watch\""
  }
}
```

## Relaunch Buttons
Relaunch buttons allow nodes to persist plugin entry points in the right-hand panel.

```typescript
// Define in manifest.json
"relaunchButtons": [
  { "command": "open-editor", "name": "Open Editor" }
]

// In code.ts, attach to a node
node.setRelaunchData({ "open-editor": "Select this node to edit tokens." });

// Detect relaunch in code.ts
if (figma.command === 'open-editor') {
  figma.showUI(__html__);
}
```

## Hot Reload

- **Mechanism:** Figma monitors the files defined in your manifest. When `ui.html` changes, the iframe is re-instantiated.
- **Sandbox Limitation:** Changes to `code.js` (main thread) **do not** trigger a reload. You must re-run the plugin via `Cmd + Option + P`.
- **Troubleshooting:**
  - If Hot Reload fails, verify that your build tool is actually updating the `dist` folder.
  - Ensure **Plugins → Development → Hot reload** is checked in the Figma Desktop menu.
  - Using `vite --watch` or `webpack --watch` is mandatory for development.
