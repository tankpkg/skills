---
name: "@tank/figma-plugin"
description: "Guidance for building Figma plugins. Covers architecture, Plugin API (nodes, styles, variables, components), UI development, Dev Mode codegen, widgets, publishing, and monetization. Triggers: figma plugin, figma API, plugin development, figma widget, Dev Mode, codegen, figma node, figma styles, figma variables, iframe, message passing, plugin UI, figma publish, figma marketplace."
---

# Figma Plugin Development

Expert guidance for building Figma plugins — from architecture and API usage
to UI development, publishing, and monetization.

Synthesized from: Official Figma Plugin API Documentation, @figma/plugin-typings,
figma/plugin-samples, Tokens Studio, FigmaToCode, Design Lint, Config talks,
Evil Martians guides.

## When to Use This Skill

Use when the task involves:
- Creating a new Figma plugin (design mode, FigJam, Dev Mode, Slides)
- Working with the Figma Plugin API (nodes, styles, variables, components)
- Building plugin UI (iframe, React, message passing)
- Generating code from Figma designs (codegen plugins)
- Publishing or monetizing a Figma plugin
- Debugging plugin issues (sandbox, font loading, network, performance)

## Core Concepts

### Dual-Context Architecture

```
┌──────────────────────┐     postMessage     ┌──────────────────────┐
│    MAIN THREAD       │ ◄──────────────────► │     UI THREAD        │
│    (Sandbox)         │                      │     (iframe)         │
│                      │                      │                      │
│  ✓ figma.* API       │                      │  ✓ DOM, fetch, canvas│
│  ✓ Read/write nodes  │                      │  ✓ React/HTML/CSS    │
│  ✗ No browser APIs   │                      │  ✗ No figma.* access │
└──────────────────────┘                      └──────────────────────┘
```

### Plugin Types

| Editor Type | Manifest Value | Read/Write | Key Capability |
|-------------|---------------|------------|----------------|
| Figma Design | `"figma"` | Read + Write | Full node manipulation |
| FigJam | `"figjam"` | Read + Write | Stickies, connectors, stamps |
| Dev Mode | `"dev"` | Read Only | Inspection, codegen |
| Slides | `"slides"` | Read + Write | Slide manipulation |
| Buzz | `"buzz"` | Read + Write | Buzz-specific features |

### Critical Patterns (Memorize These)

**1. Immutable arrays** — fills, strokes, effects MUST be cloned and reassigned:
```typescript
const fills = JSON.parse(JSON.stringify(node.fills))
fills[0] = { ...fills[0], color: { r: 1, g: 0, b: 0 } }
node.fills = fills
// OR use helper: node.fills = [figma.util.solidPaint('#FF0000')]
```

**2. Font loading** — MUST load before editing any text property:
```typescript
if (textNode.hasMissingFont) return // Always check first
const fonts = textNode.getRangeAllFontNames(0, textNode.characters.length)
await Promise.all(fonts.map(figma.loadFontAsync))
textNode.characters = 'New text'
```

**3. Message passing** — syntax differs between main thread and UI:
```typescript
// Main → UI:  figma.ui.postMessage(data)
// UI → Main:  parent.postMessage({ pluginMessage: data }, '*')
```

**4. Close plugin** — MUST call when done or plugin runs forever:
```typescript
figma.closePlugin()           // Silent close
figma.closePlugin('Done!')    // Close with notification
```

## Workflow

### Creating a New Plugin

1. **Choose editor type** → determines manifest `editorType` and capabilities
2. **Set up project** → TypeScript + bundler (Vite recommended)
3. **Design architecture** → decide if plugin needs UI or runs headless
4. **Implement** → use reference files below for API details
5. **Test edge cases** → no selection, wrong types, missing fonts, large docs
6. **Publish** → first publish requires review, updates are instant

### Decision: Plugin vs Widget

| Need | Choose |
|------|--------|
| One-time operation (export, transform, lint) | Plugin |
| Complex UI with forms/inputs | Plugin |
| External API integration | Plugin |
| Collaborative tool visible to all users | Widget |
| Persistent element on canvas | Widget |
| Real-time multiplayer features | Widget |

### Decision: Build Tool

| Situation | Recommended |
|-----------|------------|
| New project, modern stack | Vite + esbuild |
| Large codebase, many deps | Webpack + SWC |
| Simple plugin, no framework | esbuild alone |
| Want batteries-included | Create Figma Plugin (community) |
| Want hot reload dev server | Plugma (community) |

### Decision: Storage

| Data Type | Store In | Scope |
|-----------|----------|-------|
| Per-document metadata | `node.setPluginData()` | File (your plugin) |
| Cross-plugin document data | `node.setSharedPluginData()` | File (all plugins) |
| User preferences | `figma.clientStorage` | Local machine |
| Shared/synced data | External API via fetch | Server |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Modify `node.fills[0]` directly | Clone → modify → reassign entire array |
| Edit text without loading fonts | Always `await figma.loadFontAsync()` first |
| Use `findAll()` on huge docs | Use `findAllWithCriteria()` (faster) |
| Load all pages at startup | Use `"documentAccess": "dynamic-page"`, load on demand |
| Send Node objects to UI | Serialize to plain objects first |
| Forget `figma.closePlugin()` | Always close, even in error paths |
| Use `getMainComponent()` sync | Use `getMainComponentAsync()` for remote components |
| Hardcode component/style IDs | Use `.key` for imports, `.id` only within same session |
| Ignore `networkAccess` in manifest | Specify exact domains, not wildcards |
| Skip missing font checks | Always check `textNode.hasMissingFont` |

## Reference Files

| File | When to Load |
|------|-------------|
| @references/plugin-architecture.md | Setting up a new plugin, manifest questions, build tooling |
| @references/scene-graph-and-nodes.md | Working with nodes, traversal, creation, type checking |
| @references/styling-and-layout.md | Fills, strokes, effects, auto-layout, constraints |
| @references/text-and-typography.md | Text nodes, font loading, mixed styles, text manipulation |
| @references/components-and-variants.md | Components, variants, instances, library operations, styles |
| @references/ui-development.md | Plugin UI, message passing, React, theming, drag-and-drop |
| @references/variables-and-storage.md | Variables API, design tokens, pluginData, clientStorage |
| @references/devmode-codegen-publishing.md | Dev Mode, codegen, VS Code, testing, publishing, payments |

## Quick Reference: Common Operations

```typescript
// Selection
const sel = figma.currentPage.selection
figma.currentPage.selection = [node]

// Viewport
figma.viewport.scrollAndZoomIntoView([node])
figma.viewport.center = { x: 0, y: 0 }
figma.viewport.zoom = 1

// Notifications
figma.notify('Message')
figma.notify('Error!', { error: true })

// Events
figma.on('selectionchange', () => {})
figma.on('currentpagechange', () => {})
figma.on('documentchange', (e) => {})
figma.on('close', () => {})
figma.on('drop', (e) => {})

// Export
const bytes = await node.exportAsync({ format: 'PNG', constraint: { type: 'SCALE', value: 2 } })
const svg = await node.exportAsync({ format: 'SVG' })
```
