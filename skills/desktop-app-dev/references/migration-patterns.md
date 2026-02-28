# Migration and Conversion Patterns

Sources: Tauri migration guide (v2.tauri.app), Electron-to-Tauri community experiences (2025-2026), web-to-desktop conversion patterns

Covers: converting existing web apps to desktop, migrating Electron apps to Tauri, IPC mapping between frameworks, handling Node.js dependencies in Tauri, incremental migration strategies.

## Web App to Desktop: Decision Framework

### When to Convert

| Signal | Conversion Makes Sense |
|--------|----------------------|
| Users need offline access | Yes |
| Need native file system access | Yes |
| Need system tray / background operation | Yes |
| Need OS-level notifications | Yes |
| Need deep links (custom protocol) | Yes |
| Need auto-update mechanism | Yes |
| App needs local database | Yes |
| Distribution outside browser | Yes |

### When NOT to Convert

| Signal | Stay Web |
|--------|----------|
| Web app works fine in browser | No conversion needed |
| No native feature requirements | Use PWA instead |
| Mobile is primary target | PWA or native mobile |
| Users only need it occasionally | PWA with install prompt |
| Content-only site | Definitely not |

## Web App to Electron

Electron is the easiest path for web-to-desktop conversion because it runs
Node.js and Chromium — your web app runs nearly unchanged.

### Step-by-Step: Static SPA

1. Install dependencies:
   ```bash
   npm install --save-dev electron electron-vite
   ```

2. Create main process entry (`src/main/index.ts`):
   ```typescript
   import { app, BrowserWindow } from 'electron';
   import { join } from 'path';

   function createWindow() {
     const win = new BrowserWindow({
       width: 1200,
       height: 800,
       webPreferences: {
         preload: join(__dirname, '../preload/index.js'),
       },
     });
     // Production: load built files
     if (process.env.NODE_ENV === 'production') {
       win.loadFile(join(__dirname, '../renderer/index.html'));
     } else {
       // Dev: load dev server
       win.loadURL('http://localhost:5173');
     }
   }

   app.whenReady().then(createWindow);
   app.on('window-all-closed', () => {
     if (process.platform !== 'darwin') app.quit();
   });
   ```

3. Create minimal preload script (`src/preload/index.ts`):
   ```typescript
   import { contextBridge } from 'electron';
   contextBridge.exposeInMainWorld('desktop', { isDesktop: true });
   ```

4. Configure electron-vite to point at your existing frontend.

5. Add npm scripts:
   ```json
   { "dev:desktop": "electron-vite dev", "build:desktop": "electron-vite build" }
   ```

6. Test: `npm run dev:desktop`

### Step-by-Step: SPA with Backend API

If your web app calls a REST API:

| Approach | Pros | Cons |
|----------|------|------|
| Bundle API server as child process | Full compatibility | Larger bundle, port conflicts |
| Run API server in main process | Simpler | Shares main process resources |
| Keep API remote (cloud) | No changes to backend | Requires internet |
| Rewrite API calls as IPC | True desktop app | Most work |

**Recommended**: Start with remote API (no backend changes), then incrementally
move critical endpoints to IPC if offline support is needed.

### Step-by-Step: Next.js / SSR App

Next.js with Electron requires special handling:

```bash
# Option 1: Static export (simplest)
next build && next export
# Load the exported files in Electron

# Option 2: Custom server in main process
# Run Next.js server inside Electron's main process
# More complex but preserves SSR
```

For Tauri/Wails, only static export works (no Node.js server available).

## Web App to Tauri

Tauri requires no backend runtime — your frontend connects to a Rust backend
for native features.

### Step-by-Step

1. Initialize Tauri in your project:
   ```bash
   cd my-web-app
   npm install --save-dev @tauri-apps/cli
   npx tauri init
   ```

2. Answer prompts:
   - App name: your app name
   - Window title: your window title
   - Dev server URL: `http://localhost:5173` (or your dev server)
   - Frontend dist: `../dist` (or your build output directory)

3. Install Tauri API:
   ```bash
   npm install @tauri-apps/api
   ```

4. Replace browser-only APIs with Tauri plugins:

   | Browser API | Tauri Replacement |
   |-------------|------------------|
   | `localStorage` | `@tauri-apps/plugin-store` |
   | `fetch` (CORS issues) | `@tauri-apps/plugin-http` |
   | `Notification` | `@tauri-apps/plugin-notification` |
   | File input element | `@tauri-apps/plugin-dialog` + `@tauri-apps/plugin-fs` |
   | `navigator.clipboard` | `@tauri-apps/plugin-clipboard-manager` |

5. Add capabilities for required permissions:
   ```json
   // src-tauri/capabilities/default.json
   { "permissions": ["core:default", "store:default", "dialog:default"] }
   ```

6. Test: `npm run tauri dev`

### Key Constraint: No Node.js

Tauri does not run Node.js. If your web app imports Node.js modules
(`fs`, `path`, `crypto`, `child_process`), those imports must be:

- Removed (if only used server-side)
- Replaced with Tauri plugins
- Moved to Rust commands

This is the biggest conversion effort for complex apps.

## Web App to Wails

### Step-by-Step

1. Install Wails CLI:
   ```bash
   go install github.com/wailsapp/wails/v2/cmd/wails@latest
   ```

2. Initialize project around existing frontend:
   ```bash
   wails init -n my-app
   ```

3. Point `wails.json` to your frontend:
   ```json
   {
     "frontend:install": "npm install",
     "frontend:build": "npm run build",
     "frontend:dev:watcher": "npm run dev",
     "frontend:dev:serverUrl": "auto"
   }
   ```

4. Move backend logic to Go methods and bind them.

5. Test: `wails dev`

## Electron to Tauri Migration

### Feasibility Assessment

Score your Electron app on each factor:

| Factor | Easy (1) | Medium (3) | Hard (5) |
|--------|---------|-----------|---------|
| IPC handler count | < 10 | 10-30 | 30+ |
| Node.js native modules | None | 1-2 | 3+ |
| Node.js API usage (fs, crypto, etc.) | Minimal | Moderate | Heavy |
| Main process complexity | Simple window management | Some business logic | Complex server |
| electron-specific APIs used | Basic (dialog, menu) | Moderate | Extensive (protocol, session, etc.) |

**Scoring**: 5-10 = straightforward migration; 11-17 = moderate effort; 18-25 = significant rewrite

### IPC Mapping: Electron to Tauri

| Electron | Tauri Equivalent |
|----------|-----------------|
| `ipcMain.handle('channel', handler)` | `#[tauri::command] fn handler()` |
| `ipcRenderer.invoke('channel', data)` | `invoke('handler', { data })` |
| `webContents.send('channel', data)` | `app.emit('channel', data)` |
| `ipcRenderer.on('channel', cb)` | `listen('channel', cb)` |
| `contextBridge.exposeInMainWorld` | Not needed (invoke is the bridge) |
| `ipcMain.on('channel', handler)` | `app.listen('channel', handler)` (Rust) |
| `ipcRenderer.send('channel', data)` | `emit('channel', data)` |

### Node.js to Rust Equivalents

| Node.js Module | Rust Equivalent | Crate |
|----------------|----------------|-------|
| `fs` (file system) | `std::fs` or `tokio::fs` | Standard library |
| `path` | `std::path::PathBuf` | Standard library |
| `child_process` | `std::process::Command` | Standard or `tauri-plugin-shell` |
| `crypto` | `ring` or `sha2` | ring, sha2 |
| `http`/`https` | `reqwest` | reqwest |
| `os` | `std::env`, `sysinfo` | sysinfo |
| `better-sqlite3` | `rusqlite` | rusqlite |
| `node-fetch` | `reqwest` | reqwest |
| `ws` (WebSocket) | `tokio-tungstenite` | tokio-tungstenite |
| `sharp` (images) | `image` | image |
| `electron-store` | `tauri-plugin-store` | Official plugin |
| `keytar` | `keyring` | keyring |

### Step-by-Step Migration

1. **Audit** — List all `ipcMain.handle` calls, Node.js imports, electron APIs
2. **Set up Tauri alongside Electron** — Both can coexist in the same project
3. **Port IPC handlers one by one** — Convert each to a Tauri command
4. **Replace electron APIs** — Map to Tauri plugins (dialog, menu, tray, etc.)
5. **Update frontend imports** — `@tauri-apps/api` instead of `electron`
6. **Conditional runtime detection** — Support both during migration:
   ```typescript
   const isElectron = typeof window.electron !== 'undefined';
   const isTauri = '__TAURI_INTERNALS__' in window;
   ```
7. **Test each ported feature** — Verify on all platforms
8. **Remove Electron** — Once all features are ported and tested

### Incremental Migration Strategy

```
Phase 1: Run both frameworks side by side
         ├── Frontend shared (same codebase)
         ├── Electron IPC still working
         └── Tauri commands added alongside

Phase 2: Feature-flag new commands
         ├── New features → Tauri commands only
         ├── Existing features → Electron IPC still
         └── Runtime detection picks the right backend

Phase 3: Port remaining Electron features
         ├── Convert Electron IPC → Tauri commands
         ├── Replace electron-store → tauri-plugin-store
         └── Replace native modules → Rust crates

Phase 4: Remove Electron
         ├── Remove electron dependencies
         ├── Remove preload scripts
         ├── Remove main process code
         └── Clean up runtime detection
```

## Handling Node.js Dependencies in Tauri

### Decision Framework

| Dependency Type | Action |
|----------------|--------|
| Pure JS library (lodash, date-fns) | Keep — works in WebView |
| Browser-compatible library (axios, zustand) | Keep — works in WebView |
| Node.js core module usage (fs, path) | Replace with Tauri plugin or Rust |
| Native module (better-sqlite3, sharp) | Rewrite in Rust |
| Electron-specific (electron-store, electron-log) | Replace with Tauri plugin |
| Server framework (Express, Fastify) | Remove — no server in Tauri |

### Common Replacements

```typescript
// BEFORE (Electron)
const fs = require('fs');
const data = fs.readFileSync('config.json', 'utf-8');

// AFTER (Tauri)
import { readTextFile, BaseDirectory } from '@tauri-apps/plugin-fs';
const data = await readTextFile('config.json', { baseDir: BaseDirectory.AppData });
```

## Common Migration Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|-----------|
| Migrating everything at once | Burnout, broken app | Incremental approach, feature flags |
| Assuming WebView = Chromium | Visual bugs, broken features | Test on all platforms from day one |
| Ignoring capability permissions | "Not allowed" errors everywhere | Set up capabilities early in migration |
| Fighting the Rust borrow checker | Slow progress | Learn Rust basics first, start with simple commands |
| Not testing on Windows | WebView2 vs WebKit differences | CI matrix build from the start |
| Keeping Node.js patterns in Rust | Unidiomatic, slow code | Learn Rust idioms (Result, Option, traits) |
| Underestimating native module ports | Timeline blowout | Audit native modules first, assess Rust alternatives |
| Skipping the feasibility assessment | Wasted effort | Score the migration before committing |
