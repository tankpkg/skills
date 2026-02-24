# UI Development

Sources: Official Figma Plugin Docs - Creating UI, CSS Variables, Tokens Studio patterns, figma/plugin-samples

UI development in Figma plugins is unique because the plugin runs in two separate environments: the **Main Thread** (sandbox with access to Figma's internal Scene Graph) and the **UI Thread** (an iframe running standard browser HTML/JS). This reference covers how to build, communicate with, and style these interfaces.

## 1. Basic UI Setup

Figma plugins host their UI inside a `<dialog>`-like iframe. You define the source for this UI in your `manifest.json` and initialize it via the `figma` global.

### Manifest Configuration
You can specify a single entry point or multiple named files if your plugin has different views (e.g., a main interface and a settings panel).

```json
// manifest.json
{
  "name": "My Plugin",
  "id": "12345",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html" 
}

// Alternative: Multiple files
{
  "ui": {
    "main": "ui.html",
    "settings": "settings.html"
  }
}
```

### Initializing the UI
In your `code.ts` (Main Thread), call `figma.showUI` to render the interface.

```typescript
// Simple initialization
figma.showUI(__html__);

// Initialization with options
figma.showUI(__html__, {
  width: 400,
  height: 600,
  title: 'Advanced Plugin UI',
  visible: true,
  position: { x: 0, y: 0 },
  themeColors: true // CRITICAL: Always enable to inherit Figma's color scheme
});

// Accessing specific UI files if defined in manifest
figma.showUI(__uiFiles__.main, { width: 300, height: 400 });
// Later, switch to settings
// figma.showUI(__uiFiles__.settings);
```

## 2. Message Passing (CRITICAL PATTERN)

Because the Main Thread and UI Thread are isolated, they communicate via an asynchronous message-passing API.

### Main Thread → UI Thread
Use `figma.ui.postMessage` to send data to the iframe.

```typescript
// code.ts
figma.ui.postMessage({ 
  type: 'selection-change', 
  count: figma.currentPage.selection.length 
});
```

### UI Thread → Main Thread
Use `parent.postMessage` to send data back to the plugin core. 
**Note:** You must wrap the payload in a `pluginMessage` object and pass `'*'` as the target origin.

```javascript
// ui.html or ui.tsx
function notifyPlugin(action) {
  parent.postMessage({ 
    pluginMessage: { type: 'run-action', action } 
  }, '*');
}
```

### Receiving Messages
Both environments use event listeners to catch incoming data.

```typescript
// Receiving in Main Thread (code.ts)
figma.ui.onmessage = (msg) => {
  // msg is the payload inside 'pluginMessage'
  console.log('Received from UI:', msg.type);
  if (msg.type === 'create-rect') {
    const rect = figma.createRectangle();
    figma.currentPage.appendChild(rect);
  }
};

// Receiving in UI Thread (ui.html)
window.onmessage = (event) => {
  const msg = event.data.pluginMessage;
  // Handle the message from the main thread
  if (msg.type === 'selection-change') {
    document.getElementById('count').innerText = msg.count;
  }
};
```

## 3. Type-Safe Message Pattern

For production plugins (like Tokens Studio), using TypeScript unions ensures that messages are consistent across threads.

```typescript
// shared/messages.ts
export type MessageToUI =
  | { type: 'selection-changed'; nodes: string[] }
  | { type: 'theme-changed'; theme: 'light' | 'dark' }
  | { type: 'error'; message: string };

export type MessageToPlugin =
  | { type: 'create-nodes'; count: number; name: string }
  | { type: 'export'; format: 'svg' | 'png' }
  | { type: 'resize'; width: number; height: number };

// In code.ts
function sendToUI(msg: MessageToUI) {
  figma.ui.postMessage(msg);
}

// In ui.tsx
function sendToPlugin(msg: MessageToPlugin) {
  parent.postMessage({ pluginMessage: msg }, '*');
}
```

## 4. Serialization Constraints

The message-passing bridge uses the Structured Clone Algorithm, which has specific limitations in the Figma environment.

### Supported Types
- Primitive values (strings, numbers, booleans, null, undefined).
- Plain Objects and Arrays.
- `Date` objects.
- `Uint8Array` (Efficient for binary data like images).

### Unsupported Types
- **Node References:** You cannot send a `SceneNode` directly to the UI. You must extract the properties you need (ID, name, geometry) into a plain object.
- **Functions:** Passing callbacks across the bridge is impossible.
- **Classes:** Method definitions and prototypes are lost during cloning.
- **Blobs/Files:** Standard Browser Blobs are often unsupported in the bridge; use `Uint8Array` instead.

```typescript
// CORRECT: Serialize node data before sending
const selection = figma.currentPage.selection.map(node => ({
  id: node.id,
  name: node.name,
  type: node.type
}));
figma.ui.postMessage({ type: 'nodes', selection });
```

## 5. CSS Theming Variables

Figma provides a robust set of CSS variables that automatically update when the user switches between Light and Dark mode. To use these, ensure `themeColors: true` is set in `showUI`.

### Basic Implementation
Always use these variables for backgrounds and text to ensure your plugin feels native.

```css
body {
  margin: 0;
  padding: 16px;
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  background-color: var(--figma-color-bg);
  color: var(--figma-color-text);
}

button {
  background-color: var(--figma-color-bg-brand);
  color: var(--figma-color-text-onbrand);
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
}
```

### Essential Theme Variables
| Variable | Usage |
| :--- | :--- |
| `--figma-color-bg` | Main workspace background |
| `--figma-color-bg-secondary` | Sidebars or nested containers |
| `--figma-color-bg-brand` | Primary buttons, active states (Blue/Purple) |
| `--figma-color-bg-hover` | Standard hover overlay |
| `--figma-color-bg-pressed` | Clicked/Active state |
| `--figma-color-bg-selected` | Item selection highlight |
| `--figma-color-text` | Primary body and heading text |
| `--figma-color-text-secondary` | Labels and hints |
| `--figma-color-text-onbrand` | High contrast text for brand backgrounds |
| `--figma-color-border` | Dividers and input borders |
| `--figma-color-icon` | Standard icon tint |

## 6. React UI Setup

Using a framework like React is recommended for complex UIs. The standard architecture involves a `ui.tsx` file that builds to `ui.html`.

```tsx
// ui.tsx
import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [count, setCount] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleCreate = () => {
    setLoading(true);
    parent.postMessage({ 
      pluginMessage: { type: 'create-shapes', count } 
    }, '*');
  };

  useEffect(() => {
    // Listener for messages from Main Thread
    const handleMessage = (event: MessageEvent) => {
      const { type, success } = event.data.pluginMessage;
      if (type === 'shapes-created') {
        setLoading(false);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="p-4 flex flex-col gap-4">
      <h1 className="text-lg font-bold">Shape Generator</h1>
      <input 
        type="number" 
        value={count} 
        onChange={e => setCount(parseInt(e.target.value))}
        className="border p-2 rounded"
      />
      <button 
        disabled={loading}
        onClick={handleCreate}
        className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
      >
        {loading ? 'Creating...' : 'Generate'}
      </button>
    </div>
  );
}

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(<App />);
```

## 7. CRITICAL: Inlining JS in HTML

Figma serves the UI as a single string. This means your build tool must bundle all JavaScript and CSS directly into the `ui.html` file using `<script>` and `<style>` tags.

### Tooling Solutions
- **Vite:** Use `vite-plugin-singlefile`.
- **Webpack:** Use `HtmlWebpackPlugin` combined with `HtmlInlineScriptPlugin`.
- **Esbuild:** Requires a custom build script to read the JS output and inject it into an HTML template string.

### Why Inlining?
Security policies in the Figma sandbox prevent the iframe from loading external scripts or stylesheets (except for a very limited whitelist of fonts). Local relative paths like `<script src="./bundle.js">` will fail because there is no traditional server hosting the files.

## 8. Non-null Origin iframes

If you need to host your UI on a remote server (e.g., for faster updates or to use heavy libraries), you can navigate the iframe to an external URL.

```typescript
// code.ts
// Use a small local script to redirect the iframe
figma.showUI(`
  <script>
    window.location.href = "https://your-app.com/figma-plugin";
  </script>
`);
```

### Communicating from External UI
When hosted externally, the iframe has a non-null origin. You must include your `pluginId` in the `postMessage` call so Figma knows which plugin to route the message to.

```javascript
// External UI Code
parent.postMessage({
  pluginMessage: { type: 'fetch-data' },
  pluginId: 'YOUR_PLUGIN_ID_FROM_MANIFEST' // Or '*' if you don't care
}, 'https://www.figma.com');
```

## 9. Drag and Drop from UI

Figma allows users to drag items from your plugin UI and drop them directly onto the canvas.

### UI Implementation
When the user finishes a drag, send a `pluginDrop` message.

```javascript
// UI Thread
const onDragEnd = (event) => {
  parent.postMessage({
    pluginDrop: {
      clientX: event.clientX,
      clientY: event.clientY,
      items: [
        { 
          type: 'image/svg+xml', 
          data: '<svg>...</svg>' 
        }
      ],
      dropMetadata: { templateId: 'hero-section' }
    }
  }, '*');
};
```

### Main Thread Implementation
Listen for the `drop` event to handle the placement and creation of nodes.

```typescript
// code.ts
figma.on('drop', (event: DropEvent) => {
  const { items, x, y, dropMetadata } = event;
  
  if (items.length > 0 && items[0].type === 'image/svg+xml') {
    const newNode = figma.createNodeFromSvg(items[0].data);
    newNode.x = x;
    newNode.y = y;
    figma.currentPage.appendChild(newNode);
    figma.notify('Dropped SVG successfully');
    
    return false; // Return false to prevent Figma from handling the drop
  }
  return true;
});
```

## 10. UI Resize & Position

The UI window is not static. You can programmatically control its dimensions and visibility.

```typescript
// Resize the window based on UI content
figma.ui.resize(500, 400);

// Move the window
figma.ui.reposition(100, 100);

// Hide/Show without destroying the instance
figma.ui.hide();
figma.ui.show();

// Query current state
const position = figma.ui.getPosition(); 
// Returns { x, y, windowSpace: 'PLATFORM' | 'VIEWPORT' }
```

### Best Practice: Auto-Resize
A common pattern is to have the UI send its `scrollHeight` to the Main Thread on load so the window perfectly fits the content.

```javascript
// UI Thread
window.onload = () => {
  sendToPlugin({ 
    type: 'init-resize', 
    height: document.body.scrollHeight 
  });
};
```

## 11. Common UI Libraries

Creating a UI that feels "at home" in Figma is crucial for user adoption.

- **figma-plugin-ds:** A lightweight CSS/JS library that provides classes mimicking Figma's internal UI (buttons, checkboxes, inputs).
- **@create-figma-plugin/ui:** A comprehensive set of Preact components designed specifically for plugins. It handles theming, layout, and common widgets out of the box.
- **Tailwind CSS:** Highly popular for custom UIs. Requires careful configuration to work with the inlining constraints.

## 12. Notifications

You can communicate with the user without opening a full UI window using `figma.notify`.

```typescript
// Basic toast
figma.notify('Changes saved.');

// Error message
figma.notify('Selection is empty', { error: true });

// Message with duration
figma.notify('Working...', { timeout: 5000 });

// Persistent message with a button
const notification = figma.notify('Background task running', {
  timeout: Infinity,
  button: {
    text: 'Cancel',
    action: () => {
      console.log('User cancelled');
      return true; // Dismiss notification
    }
  }
});

// Programmatic dismissal
// notification.cancel();
```

## 13. UI Performance Best Practices

1. **Avoid Frequent PostMessage:** Sending data across the bridge 60 times a second (e.g., on mouse move) will degrade performance. Debounce or throttle UI updates.
2. **Lazy Load Components:** If your plugin is large, only render what the user sees.
3. **Asset Management:** Encode small icons as Base64 strings or SVG constants. External images should be fetched once and cached.
4. **Main Thread Logic:** Keep heavy calculations in the Main Thread to avoid freezing the UI iframe.
5. **Initial State:** Send the current Figma selection/state immediately after `showUI` to prevent "flicker" where the UI shows stale or empty data.

## 14. Responsive Layouts

Since users can resize the plugin window (if allowed), use flexible layouts.

```css
#root {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

main {
  flex: 1;
  overflow-y: auto;
}

footer {
  border-top: 1px solid var(--figma-color-border);
  padding: 8px;
}
```

By following these patterns, you ensure your plugin is performant, visually consistent with Figma, and robust across different user configurations.
