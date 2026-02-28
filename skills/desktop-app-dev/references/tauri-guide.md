# Tauri v2 Development Guide

Sources: Tauri v2 official documentation (2026), tauri.app guides, Tauri v2 plugin ecosystem, 2025-2026 migration experiences

Covers: architecture, project setup, commands and events, plugin system, capabilities and permissions, tauri.conf.json configuration, frontend integration, mobile support, Rust state management.

## Architecture

Tauri uses a Rust core with an OS-native WebView for rendering:

- **Rust core**: Manages app lifecycle, defines commands, runs plugins, enforces
  permissions. Full OS access through Rust standard library and crates.
- **WebView frontend**: OS-native rendering (WebKit on macOS, WebView2 on
  Windows, WebKitGTK on Linux). Runs your HTML/CSS/JS app.
- **IPC**: Frontend calls Rust functions via `invoke()`. Rust pushes data to
  frontend via events. Type-safe across the boundary.
- **Plugin system**: Native features (fs, dialog, shell, etc.) are modular
  plugins added individually. Nothing enabled by default.

```
┌───────────────────────┐  Commands   ┌──────────────────────┐
│   Rust Core Process   │◄───────────►│   WebView (OS)       │
│                       │   Events    │                      │
│  - #[tauri::command]  │────────────►│  - Your web UI       │
│  - Plugin system      │             │  - @tauri-apps/api   │
│  - State management   │             │  - invoke('cmd')     │
│  - Capabilities       │             │  - listen('event')   │
└───────────────────────┘             └──────────────────────┘
```

## Project Setup

### New Project

```bash
npm create tauri-app@latest my-app
cd my-app
npm install
npm run tauri dev
```

Choose a frontend template during setup: React-ts, Vue-ts, Svelte-ts,
SolidJS-ts, Angular, Vanilla-ts, or others.

### Add Tauri to Existing Web Project

```bash
cd my-existing-web-app
npm install --save-dev @tauri-apps/cli@latest
npx tauri init
```

Answer the prompts: app name, window title, dev server URL (e.g.,
`http://localhost:5173`), frontend build output (e.g., `../dist`).

### Project Structure

```
my-app/
├── src/                    # Frontend (React/Vue/Svelte/etc.)
│   ├── App.tsx
│   └── main.tsx
├── src-tauri/
│   ├── src/
│   │   ├── lib.rs          # App setup, command registrations
│   │   └── main.rs         # Entry point (don't edit usually)
│   ├── capabilities/
│   │   └── default.json    # Permission definitions
│   ├── icons/              # App icons (all sizes)
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri configuration
├── package.json
└── vite.config.ts          # Frontend build config
```

## Commands (Frontend to Backend IPC)

Commands are Rust functions callable from the frontend.

### Basic Command

```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! From Rust.", name)
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error running tauri application");
}
```

```typescript
// Frontend
import { invoke } from '@tauri-apps/api/core';
const greeting = await invoke<string>('greet', { name: 'World' });
```

### Async Command

```rust
#[tauri::command]
async fn fetch_url(url: String) -> Result<String, String> {
    reqwest::get(&url)
        .await.map_err(|e| e.to_string())?
        .text()
        .await.map_err(|e| e.to_string())
}
```

### Error Handling

Return `Result<T, E>` where E implements `Into<InvokeError>`:

```rust
use serde::Serialize;

#[derive(Debug, Serialize)]
enum AppError {
    FileNotFound(String),
    PermissionDenied,
}
impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::FileNotFound(p) => write!(f, "File not found: {}", p),
            AppError::PermissionDenied => write!(f, "Permission denied"),
        }
    }
}

#[tauri::command]
fn read_config() -> Result<String, AppError> {
    // ...
}
```

Frontend catches errors normally:

```typescript
try {
  const config = await invoke<string>('read_config');
} catch (error) {
  console.error('Rust error:', error);
}
```

### Registering Multiple Commands

```rust
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
        greet,
        read_config,
        save_config,
        fetch_url,
    ])
```

## Events (Backend to Frontend)

Events push data from Rust to the frontend asynchronously.

### Emit from Rust

```rust
use tauri::Emitter;

#[tauri::command]
async fn start_download(app: tauri::AppHandle, url: String) -> Result<(), String> {
    // ... download logic ...
    app.emit("download-progress", 75).map_err(|e| e.to_string())?;
    app.emit("download-complete", true).map_err(|e| e.to_string())?;
    Ok(())
}
```

### Listen in Frontend

```typescript
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen<number>('download-progress', (event) => {
  console.log(`Progress: ${event.payload}%`);
});
// Call unlisten() to stop listening
```

### Emit from Frontend to Backend

```typescript
import { emit } from '@tauri-apps/api/event';
await emit('user-action', { type: 'click', target: 'save' });
```

Listen in Rust with `app.listen(...)`.

## Plugin System

Tauri v2 uses a modular plugin architecture. Native features are opt-in.

### Official Plugins

| Plugin | Crate | JS Package | Purpose |
|--------|-------|-----------|---------|
| fs | `tauri-plugin-fs` | `@tauri-apps/plugin-fs` | File system read/write |
| dialog | `tauri-plugin-dialog` | `@tauri-apps/plugin-dialog` | Open/save file dialogs |
| shell | `tauri-plugin-shell` | `@tauri-apps/plugin-shell` | Run external commands |
| notification | `tauri-plugin-notification` | `@tauri-apps/plugin-notification` | System notifications |
| updater | `tauri-plugin-updater` | `@tauri-apps/plugin-updater` | Auto-updates |
| store | `tauri-plugin-store` | `@tauri-apps/plugin-store` | Persistent key-value store |
| clipboard | `tauri-plugin-clipboard-manager` | `@tauri-apps/plugin-clipboard-manager` | Clipboard access |
| http | `tauri-plugin-http` | `@tauri-apps/plugin-http` | HTTP client |
| os | `tauri-plugin-os` | `@tauri-apps/plugin-os` | OS information |
| process | `tauri-plugin-process` | `@tauri-apps/plugin-process` | Process management |
| global-shortcut | `tauri-plugin-global-shortcut` | `@tauri-apps/plugin-global-shortcut` | Keyboard shortcuts |
| deep-link | `tauri-plugin-deep-link` | `@tauri-apps/plugin-deep-link` | Custom protocol |

### Adding a Plugin

```bash
# 1. Add Rust crate
cargo add tauri-plugin-fs
# 2. Add JS bindings
npm install @tauri-apps/plugin-fs
```

```rust
// 3. Register in builder (src-tauri/src/lib.rs)
tauri::Builder::default()
    .plugin(tauri_plugin_fs::init())
    .invoke_handler(tauri::generate_handler![...])
```

```typescript
// 4. Use in frontend
import { readTextFile, writeTextFile } from '@tauri-apps/plugin-fs';
const content = await readTextFile('config.json', { baseDir: BaseDirectory.AppData });
```

## Capabilities and Permissions

Tauri v2 uses a capability-based security model. Nothing is allowed by default.

### Capability File

```json
// src-tauri/capabilities/default.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default permissions for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:default",
    "dialog:default",
    "notification:default"
  ]
}
```

### Permission Scopes

Restrict file system access to specific directories:

```json
{
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPDATA/**" }]
    }
  ]
}
```

### Security Principle

Grant minimum required permissions. Each window can have its own capability
file with different permission sets. A settings window needs different access
than the main editor window.

## tauri.conf.json Configuration

Key sections:

```jsonc
{
  "productName": "My App",
  "version": "1.0.0",
  "identifier": "com.example.myapp",
  "build": {
    "frontendDist": "../dist",       // Production frontend build path
    "devUrl": "http://localhost:5173" // Dev server URL
  },
  "app": {
    "windows": [{
      "title": "My App",
      "width": 1200,
      "height": 800,
      "minWidth": 800,
      "minHeight": 600,
      "decorations": true,       // Native title bar
      "resizable": true
    }]
  },
  "bundle": {
    "active": true,
    "targets": "all",            // Or ["dmg", "nsis", "appimage"]
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

## State Management in Rust

Share state across commands using `tauri::Manager::manage`:

```rust
use std::sync::Mutex;

struct AppState {
    counter: Mutex<i32>,
    db: Mutex<Option<Database>>,
}

#[tauri::command]
fn increment(state: tauri::State<'_, AppState>) -> i32 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}

pub fn run() {
    tauri::Builder::default()
        .manage(AppState {
            counter: Mutex::new(0),
            db: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![increment])
        .run(tauri::generate_context!())
        .expect("error running tauri application");
}
```

For async state, use `tokio::sync::Mutex` instead.

## Mobile Support (Tauri v2)

Tauri v2 supports iOS and Android from the same codebase.

```bash
# Initialize mobile targets
npx tauri android init
npx tauri ios init

# Run on device/emulator
npx tauri android dev
npx tauri ios dev

# Build for release
npx tauri android build
npx tauri ios build
```

The same Rust commands work on mobile. The WebView is WKWebView (iOS) or
Android System WebView. Mobile uses the same `tauri.conf.json` with
optional platform-specific overrides.

### Mobile Considerations

- File paths differ (use Tauri path API, not hardcoded paths)
- Some plugins have mobile-specific behavior
- Screen sizes require responsive frontend design
- Not all desktop plugins are available on mobile

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| "not allowed by permissions" | Missing capability | Add permission to `capabilities/default.json` |
| WebView looks different on Windows | WebView2 vs WebKit rendering | Test on all platforms, use CSS resets |
| Rust compilation very slow | Full rebuild | Use `cargo watch`, incremental compilation |
| Cannot access files | fs plugin not added or not permitted | Add `tauri-plugin-fs` + capability |
| Frontend cannot find Tauri API | Missing `@tauri-apps/api` | `npm install @tauri-apps/api` |
| Window blank on first load | Dev server not ready | Ensure dev server starts before Tauri |
| Build fails with schema error | Outdated capability schema | Run `npx tauri build` to regenerate schemas |
| Mobile build fails | Missing Android SDK / Xcode | Install platform toolchains per docs |
| State deadlock | Holding Mutex across await | Use `tokio::sync::Mutex` for async code |
