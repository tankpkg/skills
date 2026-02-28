---
name: "@tank/desktop-app-dev"
description: |
  Build, convert, and ship cross-platform desktop applications from web
  projects using Electron, Tauri v2, or Wails. Covers framework selection
  and automatic project detection, architecture and IPC patterns, native
  desktop APIs (menus, tray, notifications, file system, dialogs, shortcuts,
  clipboard), packaging and distribution (installers, code signing,
  notarization, auto-update), migration patterns (web-to-desktop conversion,
  Electron-to-Tauri migration), and CI/CD build pipelines. Synthesizes
  Electron v40 docs, Tauri v2 docs, Wails v2/v3 docs, and 2025-2026
  ecosystem research.

  Trigger phrases: "Electron", "Tauri", "Wails", "desktop app",
  "desktop application", "web to desktop", "convert to desktop app",
  "cross-platform app", "native app", "electron-builder", "electron-forge",
  "electron-vite", "tauri command", "system tray", "auto-update",
  "code signing", "notarize", "DMG", "MSI", "AppImage",
  "package desktop app", "IPC", "main process", "preload script",
  "BrowserWindow", "wails build", "desktop wrapper",
  "ship desktop app", "distribute app", "Electron to Tauri",
  "migrate from Electron", "wrap web app"
---

# Desktop App Development

Build cross-platform desktop apps from web projects. Three production-ready
frameworks: Electron (Node.js), Tauri v2 (Rust), and Wails (Go). Each uses
a web frontend with a native backend for OS access.

## Core Philosophy

1. **Detect before recommending** -- Check the project for existing framework
   signals before suggesting one. Never assume.
2. **Web skills transfer** -- All three frameworks use HTML/CSS/JS frontends.
   The backend language (Node.js, Rust, Go) is the key differentiator.
3. **Size and performance matter** -- Users notice 150 MB downloads and 300 MB
   memory usage. Choose the lightest framework that meets requirements.
4. **Ship incrementally** -- Get a working desktop wrapper first, then add
   native features (tray, auto-update, deep links) one at a time.
5. **Test on all platforms** -- Tauri and Wails use OS WebViews that render
   differently. Electron bundles Chromium for consistency but at size cost.

## Quick-Start

### "I want to turn my web app into a desktop app"

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Detect existing framework (see detection below) | This file |
| 2 | If none detected, choose framework via decision matrix | `references/framework-selection.md` |
| 3 | Set up the chosen framework in the project | Framework-specific guide |
| 4 | Add native features as needed (menus, tray, dialogs) | `references/native-apis.md` |
| 5 | Package for distribution | `references/packaging-distribution.md` |

### "I already have an Electron app and want to migrate to Tauri"

| Step | Action |
|------|--------|
| 1 | Run feasibility assessment (score IPC complexity, Node.js usage, native modules) |
| 2 | Map Electron IPC handlers to Tauri commands |
| 3 | Replace Node.js dependencies with Rust equivalents |
| 4 | Port incrementally: both can coexist during migration |
-> See `references/migration-patterns.md`

### "I need to package and distribute my desktop app"

| Step | Action |
|------|--------|
| 1 | Configure platform-specific installer formats (DMG, MSI, AppImage) |
| 2 | Set up code signing (macOS: Apple Developer cert, Windows: Authenticode) |
| 3 | Configure auto-update mechanism |
| 4 | Set up CI/CD matrix build (Ubuntu, macOS, Windows) |
-> See `references/packaging-distribution.md`

## Project Detection

Before recommending a framework, check for existing signals:

| Signal | Framework | Files to Check |
|--------|-----------|----------------|
| `electron` in package.json deps | Electron | `package.json`, `main.js`, `preload.js` |
| `src-tauri/` directory exists | Tauri | `tauri.conf.json`, `src-tauri/Cargo.toml` |
| `wails.json` exists | Wails | `wails.json`, `go.mod` |
| `@tauri-apps/api` in deps | Tauri | `package.json` |
| `electron-builder.yml` exists | Electron | project root |
| `electron-forge` in deps | Electron | `package.json` |
| None of the above | No framework | -> Use decision matrix |

If no framework is detected, ask the user their preference. Recommend based
on the decision matrix in `references/framework-selection.md`.

## Decision Trees

### Framework Selection (Quick)

| Signal | Recommendation |
|--------|---------------|
| Pure web dev team, no Rust/Go experience | Electron |
| Bundle size and memory are critical | Tauri |
| Team already uses Go | Wails |
| Need mobile + desktop from one codebase | Tauri v2 |
| Need pixel-perfect cross-platform rendering | Electron |
| Maximum security, minimal attack surface | Tauri |
| Wrapping existing Next.js / Node.js backend | Electron |
| Greenfield project, performance matters | Tauri |

### Framework Comparison (2026)

| Aspect | Electron | Tauri v2 | Wails |
|--------|----------|----------|-------|
| Bundle size | 80-150 MB | 3-8 MB | 10-15 MB |
| Memory (idle) | ~150 MB | ~30-60 MB | ~40-80 MB |
| Backend | Node.js | Rust | Go |
| Rendering | Bundled Chromium | OS WebView | OS WebView |
| GitHub stars | 120K | 103K | 33K |
| Mobile support | No | Yes (v2) | No |
| Auto-update | Built-in | Plugin | Manual |
| Learning curve | Low (JS/TS only) | Medium (Rust) | Medium (Go) |

### Architecture Pattern

| App Type | Approach |
|----------|----------|
| Static site / SPA | Load index.html directly |
| SPA with REST API | Bundle API server or use local HTTP |
| Next.js / SSR app | Electron + custom server, or export static |
| Real-time app (WebSocket) | Run WS server in backend process |
| Heavy computation | Offload to native backend (Rust/Go) |

## Anti-Patterns

| Don't | Do Instead | Why |
|-------|-----------|-----|
| Expose Node.js to renderer (Electron) | Use preload + contextBridge | Security: renderer is untrusted |
| Skip code signing | Sign and notarize for all platforms | Users get scary warnings otherwise |
| Bundle dev dependencies | Production build with tree-shaking | Bloats installer unnecessarily |
| Use localStorage for sensitive data | Use OS keychain or encrypted store | localStorage is plaintext |
| Ignore platform differences | Test on macOS, Windows, Linux | WebView rendering varies |
| Port everything at once (migration) | Migrate incrementally | Lower risk, faster feedback |

## Reference Files

| File | Contents |
|------|----------|
| `references/framework-selection.md` | Decision matrices, project detection details, team skill assessment, architecture overviews, ecosystem maturity comparison, frontend framework compatibility |
| `references/electron-guide.md` | Electron architecture (main/renderer/preload), project setup (electron-forge, electron-vite), IPC patterns, BrowserWindow configuration, security best practices, TypeScript setup |
| `references/tauri-guide.md` | Tauri v2 architecture, project setup, commands and events, plugin system, capabilities/permissions, tauri.conf.json, frontend integration, mobile support, Rust state management |
| `references/wails-guide.md` | Wails architecture, project setup, Go method binding with auto-generated TypeScript, events system, window management, v2 vs v3 comparison |
| `references/native-apis.md` | Cross-framework native APIs: menus, system tray, notifications, file system, dialogs, keyboard shortcuts, clipboard, deep links, multi-window, with code examples for each framework |
| `references/packaging-distribution.md` | Platform installers (DMG/MSI/AppImage), code signing (macOS/Windows), notarization, auto-update mechanisms, CI/CD build pipelines, distribution channels, bundle size optimization |
| `references/migration-patterns.md` | Web-to-desktop conversion (Electron/Tauri/Wails), Electron-to-Tauri migration (feasibility scoring, IPC mapping, Node.js-to-Rust equivalents), incremental migration strategy, common pitfalls |
