# Electron Development Guide

Sources: Electron v40 documentation (2026), electron-forge docs, electron-vite docs, Electron Fiddle examples

Covers: architecture, project setup, IPC patterns, preload scripts, main/renderer processes, electron-forge, electron-vite, BrowserWindow configuration, security best practices.

## Architecture

Electron runs two types of processes:

- **Main process**: Node.js runtime with full OS access. Manages app lifecycle,
  creates BrowserWindows, handles native APIs. One per app.
- **Renderer process**: Chromium instance running your web UI. Sandboxed by
  default. One per window.
- **Preload script**: Runs in renderer context but with access to Node.js APIs.
  Uses `contextBridge` to safely expose functions to the web page.

```
┌─────────────────────┐     IPC      ┌────────────────────────┐
│    Main Process      │◄────────────►│   Renderer Process     │
│    (Node.js)         │              │   (Chromium)           │
│                      │              │                        │
│  - app lifecycle     │   preload.js │  - Your web UI         │
│  - BrowserWindow     │──────────────│  - HTML/CSS/JS         │
│  - native APIs       │ contextBridge│  - React/Vue/Svelte    │
│  - file system       │              │  - Sandboxed           │
└─────────────────────┘              └────────────────────────┘
```

## Project Setup

### Option 1: electron-vite (Recommended for New Projects)

```bash
npm create electron-vite@latest my-app
cd my-app
npm install
npm run dev
```

Project structure:

```
my-app/
├── electron.vite.config.ts
├── package.json
├── src/
│   ├── main/           # Main process
│   │   └── index.ts
│   ├── preload/        # Preload scripts
│   │   └── index.ts
│   └── renderer/       # Web UI (React/Vue/etc.)
│       ├── index.html
│       └── src/
```

### Option 2: electron-forge (Official)

```bash
npm init electron-app@latest my-app -- --template=vite-typescript
cd my-app
npm start
```

### electron-vite vs electron-forge

| Aspect | electron-vite | electron-forge |
|--------|--------------|----------------|
| Maintainer | Community (alex.wei) | Electron team |
| Vite support | Native, stable | Plugin, "experimental" |
| HMR speed | Fast | Fast |
| Configuration | Minimal | More boilerplate |
| Maker ecosystem | Use electron-builder | Built-in makers |
| Recommendation | New projects | Need forge-specific makers |

### Adding Electron to an Existing Web Project

```bash
npm install --save-dev electron electron-vite
```

Create `electron.vite.config.ts`, `src/main/index.ts`, and `src/preload/index.ts`.
Point the main process to load your existing frontend.

## IPC Patterns

IPC (Inter-Process Communication) is how main and renderer exchange data.
All IPC must go through the preload script for security.

### Pattern 1: Renderer → Main (Request-Response)

Use `ipcRenderer.invoke` / `ipcMain.handle` for async request-response:

```typescript
// src/preload/index.ts
import { contextBridge, ipcRenderer } from 'electron';
contextBridge.exposeInMainWorld('api', {
  readFile: (path: string) => ipcRenderer.invoke('read-file', path),
  saveFile: (path: string, data: string) => ipcRenderer.invoke('save-file', path, data),
});

// src/main/index.ts
import { ipcMain } from 'electron';
import { readFile, writeFile } from 'fs/promises';
ipcMain.handle('read-file', async (_event, path: string) => {
  return readFile(path, 'utf-8');
});
ipcMain.handle('save-file', async (_event, path: string, data: string) => {
  await writeFile(path, data, 'utf-8');
});

// src/renderer (your web app)
const content = await window.api.readFile('/path/to/file');
await window.api.saveFile('/path/to/file', 'new content');
```

### Pattern 2: Main → Renderer (Push Notifications)

Use `webContents.send` / `ipcRenderer.on` for main-initiated messages:

```typescript
// src/main/index.ts
mainWindow.webContents.send('download-progress', { percent: 75 });

// src/preload/index.ts
contextBridge.exposeInMainWorld('api', {
  onDownloadProgress: (callback: (data: any) => void) => {
    ipcRenderer.on('download-progress', (_event, data) => callback(data));
  },
});

// src/renderer
window.api.onDownloadProgress((data) => {
  console.log(`Download: ${data.percent}%`);
});
```

### Pattern 3: Two-Way Channel

For streams or ongoing communication, combine both patterns.

### IPC Best Practices

| Do | Don't |
|----|-------|
| Use `invoke`/`handle` for request-response | Use `send`/`on` for request-response |
| Validate all inputs in main process handlers | Trust data from renderer |
| Type the exposed API with TypeScript interfaces | Expose raw `ipcRenderer` |
| Use descriptive channel names (`file:read`) | Use generic names (`data`) |
| Return serializable data only | Return functions or class instances |

## Preload Script

The preload script is the security boundary between main and renderer.

### Rules

1. Always use `contextBridge.exposeInMainWorld`
2. Never expose `ipcRenderer` directly to the renderer
3. Never expose Node.js APIs directly (`require`, `fs`, `path`)
4. Validate and sanitize all data crossing the bridge
5. Expose minimal API surface — only what the renderer needs

### TypeScript Typing

```typescript
// src/preload/index.ts
const api = {
  readFile: (path: string): Promise<string> => ipcRenderer.invoke('read-file', path),
  getAppVersion: (): Promise<string> => ipcRenderer.invoke('get-app-version'),
};
contextBridge.exposeInMainWorld('api', api);

// src/preload/index.d.ts (or global declaration)
declare global {
  interface Window {
    api: {
      readFile: (path: string) => Promise<string>;
      getAppVersion: () => Promise<string>;
    };
  }
}
```

## BrowserWindow Configuration

```typescript
import { BrowserWindow } from 'electron';
const mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  minWidth: 800,
  minHeight: 600,
  webPreferences: {
    preload: join(__dirname, '../preload/index.js'),
    sandbox: true,           // Default: true (keep it)
    contextIsolation: true,  // Default: true (keep it)
    nodeIntegration: false,  // Default: false (keep it)
  },
  // macOS specific
  titleBarStyle: 'hiddenInset', // For custom title bar
  trafficLightPosition: { x: 15, y: 10 },
  // General
  show: false, // Show after ready-to-show to avoid flash
});
mainWindow.once('ready-to-show', () => mainWindow.show());
```

### Key webPreferences

| Option | Default | Keep Default? | Why |
|--------|---------|---------------|-----|
| `sandbox` | true | Yes | Restricts renderer capabilities |
| `contextIsolation` | true | Yes | Prevents prototype pollution |
| `nodeIntegration` | false | Yes | No Node.js in renderer |
| `webSecurity` | true | Yes | Enforces same-origin policy |
| `preload` | none | Set it | Required for safe IPC |

## Security Best Practices

### Content Security Policy

Add CSP to restrict what the renderer can load:

```typescript
// In main process, set CSP header
session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: {
      ...details.responseHeaders,
      'Content-Security-Policy': [
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
      ],
    },
  });
});
```

### Restrict Navigation

```typescript
mainWindow.webContents.on('will-navigate', (event, url) => {
  const allowed = ['http://localhost:5173']; // dev server
  if (!allowed.some((a) => url.startsWith(a))) event.preventDefault();
});
app.on('web-contents-created', (_event, contents) => {
  contents.setWindowOpenHandler(() => ({ action: 'deny' }));
});
```

### Session Permissions

```typescript
session.defaultSession.setPermissionRequestHandler((_webContents, permission, callback) => {
  const allowed = ['clipboard-read', 'clipboard-write'];
  callback(allowed.includes(permission));
});
```

## TypeScript Configuration

Use separate tsconfig for each process:

```jsonc
// tsconfig.node.json (main + preload)
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ESNext",
    "strict": true,
    "outDir": "./out"
  },
  "include": ["src/main/**/*", "src/preload/**/*"]
}

// tsconfig.web.json (renderer)
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ESNext",
    "strict": true,
    "jsx": "react-jsx",
    "lib": ["DOM", "ESNext"]
  },
  "include": ["src/renderer/**/*"]
}
```

## Hot Module Replacement

electron-vite and electron-forge+vite both support HMR:

- Frontend changes: Instant HMR in the renderer (same as web dev)
- Preload changes: Renderer reloads automatically
- Main process changes: App restarts automatically

No special configuration needed with electron-vite defaults.

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| White screen on startup | Incorrect preload path or build path | Check `join(__dirname, ...)` resolves correctly |
| Cannot use `require` in renderer | nodeIntegration disabled (correct) | Use IPC through preload instead |
| CSP blocking inline scripts | Missing or overly strict CSP | Add `'unsafe-inline'` for styles if needed |
| Large bundle size (200+ MB) | Dev dependencies in production | Use `npm prune --production` or electron-builder |
| Slow cold startup | Loading heavy modules synchronously | Lazy-load with dynamic `import()` |
| App crashes on macOS notarization | Missing entitlements | Add `entitlements.mac.plist` with hardened runtime |
| Window flashes white then loads | Creating visible window before content ready | Use `show: false` + `ready-to-show` event |
| IPC returns undefined | Forgetting to `return` in handle callback | Ensure handler returns value or Promise |
| `__dirname` is undefined | ESM mode without polyfill | Use `import.meta.url` or electron-vite auto-polyfill |
| Multiple windows share state | Using global variables | Use IPC or shared store (electron-store) |

## Debugging

```bash
# Open DevTools programmatically
mainWindow.webContents.openDevTools();

# Debug main process with VS Code
# .vscode/launch.json:
{
  "type": "node",
  "request": "launch",
  "name": "Debug Main",
  "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
  "args": ["."],
  "cwd": "${workspaceFolder}"
}
```

## App Lifecycle

```typescript
import { app, BrowserWindow } from 'electron';

app.whenReady().then(() => {
  createWindow();
  // macOS: re-create window when dock icon clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows closed (except macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Cleanup before quit
app.on('before-quit', () => {
  // Save state, close connections
});
```
