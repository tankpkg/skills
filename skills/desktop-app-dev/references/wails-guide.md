# Wails Development Guide

Sources: Wails v2 documentation (2025), Wails v3 alpha docs, wails.io guides, Go community patterns

Covers: architecture, project setup, Go method binding, events system, frontend integration, window management, configuration, v2 vs v3 differences.

## Architecture

Wails uses a Go backend with an OS-native WebView:

- **Go backend**: Manages app lifecycle, exposes Go struct methods to the
  frontend via automatic binding. Full OS access through Go standard library.
- **WebView frontend**: WebView2 on Windows, WebKit on macOS and Linux.
  Runs your HTML/CSS/JS application.
- **Method binding**: Go struct methods are automatically exposed to the
  frontend. Wails generates TypeScript definitions for type safety.
- **Events**: Bidirectional event system between Go and frontend.

```
┌──────────────────────┐  Method Binding  ┌──────────────────────┐
│   Go Backend         │◄────────────────►│   WebView (OS)       │
│                      │  (auto-gen TS)   │                      │
│  - Struct methods    │                  │  - Your web UI       │
│  - runtime.* APIs    │   Events         │  - wailsjs/ bindings │
│  - App lifecycle     │◄────────────────►│  - runtime.* JS APIs │
│  - Full Go stdlib    │                  │                      │
└──────────────────────┘                  └──────────────────────┘
```

## Project Setup

### Prerequisites

- Go 1.21+ installed
- Node.js 18+ installed
- Platform dependencies (see gotchas section for Linux)

### Install Wails CLI

```bash
go install github.com/wailsapp/wails/v2/cmd/wails@latest
wails doctor  # Verify installation
```

### Create New Project

```bash
wails init -n my-app -t react-ts
cd my-app
wails dev    # Development with hot reload
wails build  # Production build
```

Available templates: `react-ts`, `vue-ts`, `svelte-ts`, `lit-ts`,
`preact-ts`, `vanilla-ts`, `react`, `vue`, `svelte`, `vanilla`.

### Project Structure

```
my-app/
├── app.go              # App struct with lifecycle methods
├── main.go             # Entry point, app configuration
├── wails.json          # Wails configuration
├── go.mod              # Go module definition
├── frontend/
│   ├── src/            # Your frontend code
│   ├── wailsjs/        # Auto-generated bindings
│   │   ├── go/         # Go method bindings (TypeScript)
│   │   └── runtime/    # Wails runtime API (TypeScript)
│   ├── package.json
│   └── vite.config.ts
└── build/              # Build output
```

## Method Binding (Go to JavaScript)

The core feature of Wails. Expose Go methods directly to the frontend.

### Define Methods on a Struct

```go
// app.go
package main

import "context"

type App struct {
    ctx context.Context
}

func NewApp() *App {
    return &App{}
}

func (a *App) startup(ctx context.Context) {
    a.ctx = ctx
}

// Exported methods (capitalized) are auto-bound to frontend
func (a *App) Greet(name string) string {
    return fmt.Sprintf("Hello %s, from Go!", name)
}

func (a *App) ReadFile(path string) (string, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return "", err
    }
    return string(data), nil
}
```

### Bind in Main

```go
// main.go
func main() {
    app := NewApp()
    err := wails.Run(&options.App{
        Title:  "My App",
        Width:  1024,
        Height: 768,
        OnStartup: app.startup,
        Bind: []interface{}{
            app,
        },
    })
    if err != nil {
        log.Fatal(err)
    }
}
```

### Call from Frontend (Auto-Generated TypeScript)

```typescript
// Auto-generated at frontend/wailsjs/go/main/App.ts
import { Greet, ReadFile } from '../wailsjs/go/main/App';

const greeting = await Greet("World");
console.log(greeting); // "Hello World, from Go!"

try {
    const content = await ReadFile("/path/to/file");
} catch (err) {
    console.error("Go error:", err);
}
```

Wails auto-generates TypeScript types from Go types. Structs become
interfaces, errors become rejected promises.

### Complex Types

```go
type FileInfo struct {
    Name string `json:"name"`
    Size int64  `json:"size"`
    IsDir bool  `json:"isDir"`
}

func (a *App) ListFiles(dir string) ([]FileInfo, error) {
    // ... returns typed data
}
```

Frontend receives properly typed objects:

```typescript
import { ListFiles } from '../wailsjs/go/main/App';
import { main } from '../wailsjs/go/models';

const files: main.FileInfo[] = await ListFiles("/home");
```

## Events System

Bidirectional event communication between Go and frontend.

### Go to Frontend

```go
import "github.com/wailsapp/wails/v2/pkg/runtime"

func (a *App) StartProcess() {
    for i := 0; i <= 100; i += 10 {
        runtime.EventsEmit(a.ctx, "progress", i)
        time.Sleep(500 * time.Millisecond)
    }
    runtime.EventsEmit(a.ctx, "complete", true)
}
```

### Frontend Listening

```typescript
import { EventsOn, EventsOff } from '../wailsjs/runtime/runtime';

EventsOn("progress", (value: number) => {
    console.log(`Progress: ${value}%`);
});

EventsOn("complete", () => {
    console.log("Done!");
    EventsOff("progress"); // Cleanup
});
```

### Frontend to Go

```typescript
import { EventsEmit } from '../wailsjs/runtime/runtime';
EventsEmit("user-action", { type: "save" });
```

```go
runtime.EventsOn(a.ctx, "user-action", func(data ...interface{}) {
    // Handle event from frontend
})
```

## Application Lifecycle

```go
wails.Run(&options.App{
    OnStartup:     app.startup,     // App initialized, context available
    OnDomReady:    app.domReady,    // Frontend DOM loaded
    OnBeforeClose: app.beforeClose, // User tries to close (return true to prevent)
    OnShutdown:    app.shutdown,    // App closing, cleanup here
})
```

```go
func (a *App) beforeClose(ctx context.Context) (prevent bool) {
    dialog, err := runtime.MessageDialog(ctx, runtime.MessageDialogOptions{
        Type:    runtime.QuestionDialog,
        Title:   "Quit?",
        Message: "Are you sure you want to quit?",
    })
    return dialog == "No"
}
```

## Window Management

```go
import "github.com/wailsapp/wails/v2/pkg/runtime"

// Window controls
runtime.WindowSetTitle(a.ctx, "New Title")
runtime.WindowSetSize(a.ctx, 1280, 720)
runtime.WindowSetMinSize(a.ctx, 800, 600)
runtime.WindowCenter(a.ctx)
runtime.WindowMaximise(a.ctx)
runtime.WindowMinimise(a.ctx)
runtime.WindowToggleMaximise(a.ctx)
runtime.WindowFullscreen(a.ctx)
runtime.WindowUnfullscreen(a.ctx)
runtime.WindowShow(a.ctx)
runtime.WindowHide(a.ctx)

// Get position and size
x, y := runtime.WindowGetPosition(a.ctx)
w, h := runtime.WindowGetSize(a.ctx)
```

### Frameless Window

```go
wails.Run(&options.App{
    Frameless: true,  // No native title bar
})
```

Use CSS `-webkit-app-region: drag` for custom drag areas.

## Configuration (wails.json)

```json
{
  "name": "my-app",
  "outputfilename": "my-app",
  "frontend:install": "npm install",
  "frontend:build": "npm run build",
  "frontend:dev:watcher": "npm run dev",
  "frontend:dev:serverUrl": "auto",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "info": {
    "companyName": "My Company",
    "productVersion": "1.0.0",
    "copyright": "Copyright 2026",
    "comments": "Built with Wails"
  }
}
```

| Field | Purpose |
|-------|---------|
| `name` | Application name |
| `outputfilename` | Binary name after build |
| `frontend:install` | Command to install frontend deps |
| `frontend:build` | Command to build frontend for production |
| `frontend:dev:watcher` | Command to start frontend dev server |
| `frontend:dev:serverUrl` | Dev server URL (`auto` detects Vite) |

## Wails v2 vs v3

| Feature | v2 (Stable) | v3 (Alpha, Feb 2026) |
|---------|------------|---------------------|
| API style | Struct binding | Services + procedural |
| Multi-window | Limited (workarounds) | Full native support |
| System tray | Basic | Enhanced |
| Stability | Production-ready | Alpha, breaking changes |
| Go version | 1.21+ | 1.22+ |
| WebView | WebView2 (Win), WebKit | Same |
| Build system | Wails CLI | Wails CLI (redesigned) |

### Recommendation

Use **v2 for production** projects today. Evaluate **v3** for new projects
starting mid-2026 or later when it reaches stable. v3 adds proper
multi-window support and a cleaner API, but expect breaking changes.

## Dialogs

```go
// Open file dialog
file, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
    Title: "Select File",
    Filters: []runtime.FileFilter{
        {DisplayName: "Text Files", Pattern: "*.txt;*.md"},
        {DisplayName: "All Files", Pattern: "*.*"},
    },
})

// Save file dialog
path, err := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{
    Title:           "Save File",
    DefaultFilename: "document.txt",
})

// Select directory
dir, err := runtime.OpenDirectoryDialog(a.ctx, runtime.OpenDialogOptions{
    Title: "Select Directory",
})

// Message dialog
result, err := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
    Type:    runtime.InfoDialog,
    Title:   "Information",
    Message: "Operation complete!",
})
```

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| `wails: command not found` | Go bin not in PATH | Add `$GOPATH/bin` to PATH |
| Frontend changes not reflecting | Stale dev server | Restart `wails dev` |
| Bindings not generated | Method not exported (lowercase) | Capitalize method name |
| CGO errors on Linux | Missing build deps | `sudo apt install gcc pkg-config libgtk-3-dev libwebkit2gtk-4.0-dev` |
| WebView2 missing on Windows | Edge runtime not installed | Bundle WebView2 bootstrapper or use fixed version |
| Slow build | Full rebuild | Use `wails dev` for incremental |
| TypeScript types wrong | Stale generated bindings | Delete `frontend/wailsjs/` and rebuild |
| App icon not showing | Wrong icon format | Use 1024x1024 PNG, `wails generate icons` |
| Cross-compilation fails | CGO platform mismatch | Use CI matrix build per platform |
