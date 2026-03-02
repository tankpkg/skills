# SVG Integration Patterns

Sources: React documentation, Vite plugin ecosystem, web component patterns (2025)

Covers: framework integration, sprite sheets, icon systems, dynamic theming, performance, caching.

## Integration Decision Table

| Method | Use When | Avoid When | Bundle Impact |
|--------|----------|------------|---------------|
| Inline SVG | Need JS access, dynamic props, animations | Many repeated icons, SSR-heavy apps | Increases HTML size |
| `<img src>` | Static decorative images, CDN-hosted assets | Need color control, accessibility labels | Zero JS bundle cost |
| CSS `background-image` | Decorative backgrounds, pseudo-elements | Need accessibility, dynamic colors | Zero JS bundle cost |
| React/Vue component | Icon systems, reusable UI elements, theming | One-off illustrations | Adds to JS bundle |
| Sprite sheet | 20+ icons used across app, icon libraries | Single-use illustrations | One HTTP request |
| Data URI | Tiny icons in CSS, email templates | Files over 2KB (base64 bloat) | Inlined in CSS |

Decision rule: use `<img>` for illustrations, components for icons, sprite sheets for icon libraries at scale.

## React Integration

### SVGR Setup with Vite

```bash
npm install --save-dev vite-plugin-svgr
```

Configure `vite.config.ts`:

```typescript
import svgr from 'vite-plugin-svgr'

export default defineConfig({
  plugins: [
    react(),
    svgr({
      svgrOptions: { exportType: 'named', ref: true, svgo: false, titleProp: true },
      include: '**/*.svg',
    }),
  ],
})
```

### TypeScript Declarations

Add to `src/vite-env.d.ts` to get both URL and component exports from `.svg` files:

```typescript
declare module '*.svg' {
  import * as React from 'react'
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement> & { title?: string }>
  const src: string
  export default src
}
```

### Importing and Using SVG Components

```typescript
import { ReactComponent as ArrowIcon } from './icons/arrow.svg'
import logoUrl from './logo.svg'  // URL for <img> usage

// As component
<ArrowIcon width={16} height={16} fill="currentColor" aria-hidden="true" />

// As image (URL export)
<img src={logoUrl} alt="Company logo" width={120} height={40} />
```

### Passing Props to SVG Components

AI-generated SVGs often hardcode fill colors. Override at import time:

```typescript
<StarIcon fill="#FFD700" width={24} height={24} />
<StarIcon fill="currentColor" style={{ color: 'var(--color-accent)' }} />
```

For SVGs with multiple colored paths, use CSS custom properties (see Dynamic SVG section).

## Vue Integration

### vite-svg-loader Setup

```bash
npm install --save-dev vite-svg-loader
```

```typescript
import svgLoader from 'vite-svg-loader'
export default defineConfig({ plugins: [vue(), svgLoader({ defaultImport: 'component' })] })
```

### Using SVGs as Vue Components

```vue
<script setup lang="ts">
import ArrowIcon from './icons/arrow.svg'   // component (defaultImport)
import LogoUrl from './logo.svg?url'        // force URL import
import LogoRaw from './logo.svg?raw'        // force raw string import

const props = defineProps<{ size: number; color: string }>()
</script>

<template>
  <ArrowIcon :width="props.size" :height="props.size" :fill="props.color" />
  <img :src="LogoUrl" alt="Logo" />
  <div v-html="LogoRaw" />  <!-- sanitize before use -->
</template>
```

## Vanilla/HTML Integration

### Inline SVG

Paste SVG markup directly into HTML. Enables CSS targeting and JS manipulation:

```html
<button class="btn-icon">
  <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
    <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor"/>
  </svg>
  Save
</button>
```

### img Tag

Best for illustrations and logos where color control is not needed:

```html
<img
  src="/assets/hero-illustration.svg"
  alt="Team collaborating on a project"
  width="600" height="400"
  loading="lazy"
/>
```

Always include `width` and `height` to prevent layout shift (CLS).

### CSS background-image

For decorative icons and patterns:

```css
.icon-search {
  width: 20px; height: 20px;
  background: url('/icons/search.svg') no-repeat center / contain;
}
/* Data URI for tiny icons (under 1KB) — encode # as %23, " as ' */
.icon-close {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24'%3E%3Cpath d='M18 6L6 18M6 6l12 12' stroke='%23333' stroke-width='2'/%3E%3C/svg%3E");
}
```

## Sprite Sheets

### vite-plugin-svg-spritemap Setup

```bash
npm install --save-dev vite-plugin-svg-spritemap
```

```typescript
// vite.config.ts
import svgSpritemap from 'vite-plugin-svg-spritemap'

export default defineConfig({
  plugins: [svgSpritemap({
    pattern: 'src/icons/*.svg',
    filename: 'icons/sprite.svg',
    prefix: 'icon-',
    svgo: { plugins: [{ name: 'removeViewBox', active: false }] },
  })],
})
```

### Referencing Icons from the Sprite

```html
<svg width="24" height="24" aria-hidden="true"><use href="/icons/sprite.svg#icon-arrow" /></svg>
<svg width="24" height="24" aria-label="Search"><use href="/icons/sprite.svg#icon-search" /></svg>
```

### Inline Sprite for CSS Color Control

External `<use href="file.svg#id">` references cannot be styled with CSS `fill`. Inject the sprite inline to enable color overrides:

```typescript
const text = await fetch('/icons/sprite.svg').then(r => r.text())
const div = Object.assign(document.createElement('div'), { style: 'display:none', innerHTML: text })
document.body.insertBefore(div, document.body.firstChild)
// Then reference as: <use href="#icon-arrow" />
```

## Icon Systems

### Building a Lazy Icon Component (React)

```typescript
// src/components/Icon.tsx
import { lazy, Suspense } from 'react'

type IconName = 'arrow' | 'search' | 'close' | 'star' | 'menu'
interface IconProps {
  name: IconName; size?: number | string; color?: string
  className?: string; 'aria-label'?: string; 'aria-hidden'?: boolean
}

const iconMap = {
  arrow: lazy(() => import('../icons/arrow.svg?react')),
  search: lazy(() => import('../icons/search.svg?react')),
  close: lazy(() => import('../icons/close.svg?react')),
  star: lazy(() => import('../icons/star.svg?react')),
  menu: lazy(() => import('../icons/menu.svg?react')),
} satisfies Record<IconName, ReturnType<typeof lazy>>

export function Icon({ name, size = 24, color = 'currentColor', className, ...aria }: IconProps) {
  const C = iconMap[name]
  return (
    <Suspense fallback={<span style={{ width: size, height: size, display: 'inline-block' }} />}>
      <C width={size} height={size} fill={color} className={className} {...aria} />
    </Suspense>
  )
}
```

### Icon Component Usage

```tsx
<Icon name="arrow" size={16} aria-hidden />                  // decorative
<Icon name="search" size={20} aria-label="Search" />         // meaningful
<Icon name="star" size={24} color="var(--color-warning)" />  // themed
<Icon name="menu" size="1.5rem" />                           // responsive
```

## Dynamic SVG

### CSS Custom Properties for Runtime Color Changes

Replace hardcoded fill values in AI-generated SVGs with CSS variables:

```svg
<!-- Before -->
<circle cx="12" cy="12" r="10" fill="#3B82F6"/>

<!-- After -->
<circle cx="12" cy="12" r="10" fill="var(--icon-bg, #3B82F6)"/>
```

Apply themes via CSS — no JavaScript re-render needed:

```css
:root          { --icon-bg: #3B82F6; --icon-fg: #FFFFFF; }
[data-theme="dark"] { --icon-bg: #60A5FA; --icon-fg: #1E293B; }
.btn-danger .icon   { --icon-bg: #EF4444; }
```

Switch themes with a single attribute:

```typescript
document.documentElement.setAttribute('data-theme', 'dark')
```

### Hover and Focus States

```css
/* currentColor approach — simpler, inherits from parent element */
.btn svg { fill: currentColor; transition: color 150ms ease; }
.btn:hover { color: var(--color-primary-hover); }
.btn:focus-visible svg { outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }
```

## Performance

### Lazy Loading

Use native lazy loading for `<img>` SVGs:

```html
<img src="/illustrations/hero.svg" alt="Hero" width="600" height="400"
  loading="lazy" decoding="async" />
```

For inline SVGs below the fold, defer fetch with Intersection Observer (`rootMargin: '200px'` preloads before the element enters the viewport):

```typescript
const observer = new IntersectionObserver(([e]) => {
  if (e.isIntersecting) {
    fetch(src).then(r => r.text()).then(html => { container.innerHTML = html })
    observer.disconnect()
  }
}, { rootMargin: '200px' })
observer.observe(container)
```

### Code Splitting Icon Libraries

```typescript
// Avoid: imports entire icon set
import * as Icons from '../icons'

// Better: named imports (tree-shakeable with SVGR)
import { ReactComponent as ArrowIcon } from '../icons/arrow.svg'

// Best for large sets: dynamic import per name
const { default: C } = await import(`../icons/${name}.svg?react`)
```

### SSR Considerations

Inline SVG components (SVGR imports) render on the server without issues in Next.js and Remix. Avoid fetching SVG strings server-side and injecting via `dangerouslySetInnerHTML` — this causes hydration mismatches.

```typescript
// Next.js: next/image for file-based SVGs
import Image from 'next/image'
<Image src="/icons/logo.svg" alt="Logo" width={120} height={40} />

// SVGR import — renders correctly in SSR
import LogoIcon from './logo.svg'
<LogoIcon width={120} height={40} />
```

### Bundle Size Reference

| Approach | JS Bundle Cost | Notes |
|----------|---------------|-------|
| `<img src>` | 0 bytes | File fetched separately |
| CSS background | 0 bytes (file) | Data URI adds to CSS bundle |
| Inline SVG (static) | SVG file size | Included in HTML payload |
| React component (SVGR) | SVG size + ~200B | In JS bundle |
| Sprite sheet | 0 bytes | One SVG file, all icons |
| Lazy component | 0 bytes initial | Loaded on demand |

Target: icons under 1KB each, illustrations under 30KB. Audit with `vite-bundle-visualizer`.

## Caching Strategy

### Content-Hash Filenames

Vite generates content-hashed filenames for all imported assets (`arrow.a3f9b2c1.svg`). The hash changes only when file content changes, enabling aggressive long-term caching:

```
# Hashed assets (Vite build output)
Cache-Control: public, max-age=31536000, immutable

# SVGs in public/ (no hash)
Cache-Control: public, max-age=86400, stale-while-revalidate=604800
```

### Service Worker Caching (Workbox)

```typescript
import { registerRoute } from 'workbox-routing'
import { CacheFirst, StaleWhileRevalidate } from 'workbox-strategies'

// Hashed assets — cache forever
registerRoute(
  ({ url }) => url.pathname.match(/\.[a-f0-9]{8}\.svg$/),
  new CacheFirst({ cacheName: 'svg-hashed-v1' })
)
// Non-hashed SVGs — serve stale, update in background
registerRoute(
  ({ request }) => request.destination === 'image' && request.url.endsWith('.svg'),
  new StaleWhileRevalidate({ cacheName: 'svg-images-v1' })
)
```

### Preloading Critical SVGs

Preload above-the-fold SVGs in `<head>` to eliminate render-blocking fetches:

```html
<link rel="preload" href="/icons/sprite.svg" as="image" type="image/svg+xml" />
<link rel="preload" href="/illustrations/hero.svg" as="image" type="image/svg+xml" />
```

For SVG optimization before integration, see `references/svg-optimization.md`.
For AI generation and prompting strategies, see `references/ai-generation-workflow.md`.
