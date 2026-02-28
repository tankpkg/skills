# Framework Selection Guide

Sources: Electron v40 docs (2026), Tauri v2 docs (2026), Wails v2/v3 docs, 2025-2026 ecosystem research

Covers: framework comparison, project detection, decision matrices, team skill assessment, architecture overview, ecosystem maturity, frontend compatibility.

## Project Detection

Before recommending a framework, detect what is already in use.

### Detection Procedure

1. Check `package.json` for framework dependencies
2. Look for framework-specific config files
3. Inspect directory structure for framework markers

### Detection Signals

| Signal | Framework | Confidence |
|--------|-----------|------------|
| `electron` in package.json devDependencies | Electron | High |
| `@electron-forge/cli` in devDependencies | Electron (Forge) | High |
| `electron-vite` in devDependencies | Electron (Vite) | High |
| `electron-builder` in devDependencies | Electron | High |
| `electron-builder.yml` in project root | Electron | High |
| `main.js` + `preload.js` pattern | Electron | Medium |
| `src-tauri/` directory exists | Tauri | High |
| `tauri.conf.json` exists | Tauri | High |
| `@tauri-apps/api` in package.json | Tauri | High |
| `@tauri-apps/cli` in devDependencies | Tauri | High |
| `src-tauri/Cargo.toml` exists | Tauri | High |
| `wails.json` in project root | Wails | High |
| `go.mod` with `wails` import | Wails | High |
| `main.go` with wails imports | Wails | Medium |
| `frontend/wailsjs/` directory | Wails | High |

### When Nothing Is Detected

If no framework signals are found, the project is a plain web app. Ask the user
which framework they prefer and recommend based on the decision matrix below.

Default recommendation for most teams: **Tauri v2** (smallest bundles, best
performance, mobile support). Fall back to **Electron** if the team cannot
use Rust at all.

## Framework Comparison (February 2026)

| Aspect | Electron | Tauri v2 | Wails |
|--------|----------|----------|-------|
| Current version | v40.0 | v2.6+ | v2.11 (v3 alpha) |
| Backend language | Node.js (JavaScript/TypeScript) | Rust | Go |
| Rendering engine | Bundled Chromium | OS WebView | OS WebView |
| Bundle size (hello world) | 80-150 MB | 3-8 MB | 10-15 MB |
| Memory usage (idle) | ~150 MB | ~30-60 MB | ~40-80 MB |
| Startup time | 1-3 seconds | 200-500 ms | 300-800 ms |
| GitHub stars | 120K | 103K | 33K |
| npm downloads/month | ~10M | ~1.7M | N/A (Go) |
| Mobile support | No | Yes (iOS/Android) | No |
| Auto-update | Built-in (electron-updater) | Plugin (updater) | Manual |
| Code signing support | Mature (electron-builder) | Built-in (bundler) | Manual |
| Platforms | Windows, macOS, Linux | Windows, macOS, Linux, iOS, Android | Windows, macOS, Linux |

## Architecture Overview

### Electron

Two-process model with Chromium:

```
Main Process (Node.js) ←─ IPC ─→ Renderer Process (Chromium)
     │                              │
     ├── App lifecycle              ├── Your web UI
     ├── Native APIs                ├── HTML/CSS/JS
     ├── File system                └── Sandboxed by default
     └── Window management
              │
         Preload Script
         (contextBridge)
```

The main process has full Node.js and OS access. The renderer runs web content
in a sandboxed Chromium instance. Preload scripts bridge them via `contextBridge`.

### Tauri v2

Rust core with OS-native WebView:

```
Rust Core Process ←─ Commands/Events ─→ WebView (OS Native)
     │                                       │
     ├── App lifecycle                       ├── Your web UI
     ├── Commands (#[tauri::command])        ├── HTML/CSS/JS
     ├── Plugin system                       └── @tauri-apps/api
     ├── Capabilities (permissions)
     └── State management
```

The Rust backend defines commands that the frontend calls via `invoke()`. Each
window has a capability file that explicitly permits which APIs it can access.
Native features are modular plugins.

### Wails

Go backend with OS-native WebView:

```
Go Backend ←─ Method Binding ─→ WebView (OS Native)
     │                               │
     ├── App lifecycle                ├── Your web UI
     ├── Bound struct methods         ├── HTML/CSS/JS
     ├── Runtime APIs                 └── Auto-generated TS bindings
     └── Event system
```

Go struct methods are automatically bound to the frontend with auto-generated
TypeScript definitions. No manual IPC serialization needed.

## Decision Matrix

### Primary Decision: Which Framework?

| Your Situation | Recommendation | Reason |
|----------------|---------------|--------|
| Web dev team, no Rust/Go experience | **Electron** | Lowest learning curve, JS/TS only |
| Bundle size and memory matter | **Tauri** | 96% smaller, 58% less memory |
| Go team building internal tool | **Wails** | Natural Go integration |
| Need mobile + desktop | **Tauri v2** | Only framework with mobile support |
| Wrapping Node.js/Express backend | **Electron** | Run server in main process |
| Maximum security requirements | **Tauri** | Rust memory safety, capability permissions |
| Pixel-perfect cross-platform rendering | **Electron** | Bundled Chromium = identical everywhere |
| Greenfield project, team can learn | **Tauri** | Best performance, growing ecosystem |
| Existing Electron app | **Stay Electron** | Migration cost often not worth it |
| Simple desktop wrapper, minimal native | **Tauri** | Smallest footprint |
| Complex native module integration | **Electron** | Mature native module ecosystem |
| Need extensive community support | **Electron** | Largest ecosystem, most SO answers |

### Secondary Decision: Tooling

| If Electron | Recommended Tooling |
|-------------|-------------------|
| New project | electron-vite (community preferred, faster DX) |
| Need full maker ecosystem | electron-forge + vite plugin |
| Packaging | electron-builder (most popular) |
| TypeScript | Yes, always |

| If Tauri | Recommended Tooling |
|----------|-------------------|
| New project | `npm create tauri-app@latest` |
| Adding to existing | `npx tauri init` |
| Frontend | Any (React-ts, Vue-ts, Svelte-ts templates) |
| Plugins | Add as needed from official plugin list |

| If Wails | Recommended Tooling |
|----------|-------------------|
| New project | `wails init -n myapp -t react-ts` |
| Version | v2 for production, evaluate v3 for future |
| Frontend | Any (React, Vue, Svelte templates) |

## Team Skill Assessment

| Team Background | Framework | Learning Curve | Time to First Build |
|----------------|-----------|---------------|-------------------|
| Frontend/React/Vue/Node | Electron | Low (1-2 days) | Hours |
| Frontend + some Rust | Tauri | Medium (1-2 weeks) | Days |
| Frontend + some Go | Wails | Medium (1 week) | Days |
| Full-stack JavaScript | Electron | Low (1-2 days) | Hours |
| Full-stack Rust | Tauri | Low (2-3 days) | Hours |
| Full-stack Go | Wails | Low (2-3 days) | Hours |
| No desktop experience | Electron | Low | Hours |

## WebView Consistency Considerations

Electron bundles Chromium. Tauri and Wails use OS-provided WebViews.

| Platform | Electron Renderer | Tauri/Wails Renderer |
|----------|------------------|---------------------|
| macOS | Chromium (bundled) | WebKit (WKWebView) |
| Windows | Chromium (bundled) | WebView2 (Edge/Chromium) |
| Linux | Chromium (bundled) | WebKitGTK |

### Implications for Tauri/Wails

- CSS feature support varies between WebKit, WebView2, and WebKitGTK
- JavaScript engine differs (JavaScriptCore on macOS vs V8 on Windows)
- Must test on all target platforms, not just development machine
- Use CSS feature detection and progressive enhancement
- Avoid bleeding-edge CSS features without fallbacks
- WebView2 requires Edge runtime on Windows (usually pre-installed)
- WebKitGTK may lag behind Safari WebKit on macOS

### When Consistent Rendering Is Critical

If the app must look pixel-identical on all platforms (e.g., design tools,
visual editors), choose Electron. For most business and developer tools,
the WebView differences are negligible.

## When NOT to Use Each Framework

### Do Not Use Electron When

- Disk space matters (IoT, embedded, disk-constrained environments)
- Memory is constrained (< 512 MB available)
- Mobile support is needed
- Users complain about resource usage and you cannot mitigate it
- Bundle download size must be under 20 MB

### Do Not Use Tauri When

- Team absolutely cannot learn any Rust (even basic command definitions)
- App relies heavily on Node.js native modules (better-sqlite3, sharp, etc.)
- Need pixel-perfect cross-platform rendering (WebView differences matter)
- Need mature, battle-tested auto-update with complex rollback scenarios
- Building on top of an existing Electron codebase without clear ROI

### Do Not Use Wails When

- Need mobile support (not available)
- v3 stability is required now (still alpha as of Feb 2026)
- Community support is critical (smaller than Electron/Tauri)
- Need built-in auto-update mechanism
- Team has no Go experience and no interest in learning

## Ecosystem Maturity

| Dimension | Electron | Tauri v2 | Wails |
|-----------|----------|----------|-------|
| Documentation quality | Excellent | Good (improving) | Good |
| Plugin/extension ecosystem | Massive (npm) | Growing (official plugins) | Small |
| Community size | Very large | Large, growing fast | Medium |
| Stack Overflow answers | Thousands | Hundreds | Tens |
| Production app examples | VS Code, Slack, Discord, Notion | Agents UI, Hopp, Cody | Fewer known |
| Books/courses available | Several | Few | Very few |
| Third-party tooling | electron-builder, -forge, -vite | Official CLI + bundler | Built-in CLI |
| Maturity (years) | 10+ years | 2+ years (v2 since Oct 2024) | 3+ years |

## Frontend Framework Compatibility

All three frameworks support any frontend that compiles to HTML, CSS, and
JavaScript. The differences are in templates and integrations.

| Frontend | Electron | Tauri | Wails |
|----------|----------|-------|-------|
| React | Via electron-vite/forge | Official template (react-ts) | Official template (react-ts) |
| Vue | Via electron-vite/forge | Official template (vue-ts) | Official template (vue-ts) |
| Svelte | Via electron-vite/forge | Official template (svelte-ts) | Official template (svelte-ts) |
| Angular | Via electron-vite/forge | Community template | Community template |
| SolidJS | Via electron-vite/forge | Official template (solid-ts) | Community template |
| Next.js | electron-serve or custom | Static export only | Static export only |
| Nuxt | Custom integration | Static export only | Static export only |
| Vanilla | Via electron-vite/forge | Official template (vanilla-ts) | Official template (vanilla) |

### Framework-Specific Notes

- **Next.js / Nuxt SSR**: Only works natively with Electron (can run Node.js
  server in main process). For Tauri/Wails, use static export (`next export`).
- **Vite-based frameworks**: Best DX across all three desktop frameworks.
  HMR works out of the box.
- **Webpack-based frameworks**: Work but may need extra configuration for
  Tauri/Wails dev server URL setup.
