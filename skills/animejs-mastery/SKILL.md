---
name: animejs-mastery
description: |
  Anime.js v4 animation expert for building stunning web animations.
  Covers the complete API: animate(), createTimeline(), createScope(),
  onScroll(), createDraggable(), createLayout(), createAnimatable(),
  SVG utilities (morphTo, createDrawable, createMotionPath), splitText(),
  stagger(), spring physics, WAAPI integration, and production-ready
  website animation recipes. Synthesizes official Anime.js v4 documentation
  and production animation patterns.

  Trigger phrases: "anime.js", "animejs", "animate()", "createTimeline",
  "stagger", "spring animation", "SVG morphing", "SVG line drawing",
  "scroll animation", "onScroll", "text animation", "splitText",
  "draggable", "layout animation", "FLIP animation", "web animation",
  "hero animation", "page transition", "scroll reveal", "micro-interaction",
  "WAAPI", "keyframes", "easing function", "motion path"
---

# Anime.js v4 Animation Mastery

Expert-level guidance for creating production-quality web animations using
Anime.js v4, the lightweight JavaScript animation engine.

## Core Principles

1. **Animate transforms and opacity first** — compositor-friendly properties
   (translate, scale, rotate, opacity) run on GPU. Avoid animating layout
   properties (width, height, top, left) unless using createLayout().
2. **Use WAAPI for simple, JS for complex** — `waapi.animate()` is 3KB and
   hardware-accelerated. Use full `animate()` (10KB) for JS objects, SVG
   attributes, function-based values, and advanced features.
3. **Always clean up** — Call `scope.revert()` in SPA teardown, `animation.revert()`
   on removal. Memory leaks from orphaned animations are the #1 bug.
4. **Stagger everything** — Single-element animations look flat. `stagger()`
   with easing transforms any list into a choreographed sequence.
5. **Spring > easing for interactions** — `spring({ bounce: 0.5 })` feels
   more natural than cubic beziers for user-triggered animations.

## Quick-Start Recipes

### "Animate elements on page load"

```js
import { animate, stagger } from 'animejs';

animate('.card', {
  opacity: [0, 1],
  y: [20, 0],
  delay: stagger(100),
  ease: 'out(3)',
  duration: 600
});
```

### "Create a sequenced timeline"

```js
import { createTimeline } from 'animejs';

const tl = createTimeline({ defaults: { duration: 600, ease: 'out(3)' } });
tl.add('h1', { opacity: [0, 1], y: [30, 0] })
  .add('p', { opacity: [0, 1], y: [20, 0] }, '-=400')
  .add('.cta', { opacity: [0, 1], scale: [0.9, 1] }, '-=300');
```

### "Trigger animation on scroll"

```js
import { animate, onScroll } from 'animejs';

animate('.section', {
  opacity: [0, 1],
  y: [50, 0],
  duration: 800,
  autoplay: onScroll({ target: '.section' })
});
```

### "Use with React"

```js
import { createScope, animate } from 'animejs';
import { useEffect, useRef } from 'react';

function Component() {
  const root = useRef(null);
  const scope = useRef(null);
  useEffect(() => {
    scope.current = createScope({ root }).add(() => {
      animate('.target', { opacity: [0, 1] });
    });
    return () => scope.current.revert();
  }, []);
  return <div ref={root}><div className="target">Hello</div></div>;
}
```

## Decision Trees

### Which API to Use

| Need | Use | Import |
|------|-----|--------|
| Basic CSS animation | `waapi.animate()` | `import { waapi } from 'animejs'` |
| JS objects, SVG attrs, callbacks | `animate()` | `import { animate } from 'animejs'` |
| Sequenced multi-element | `createTimeline()` | `import { createTimeline } from 'animejs'` |
| Scroll-triggered | `onScroll()` in autoplay | `import { onScroll } from 'animejs'` |
| Drag interactions | `createDraggable()` | `import { createDraggable } from 'animejs'` |
| Layout changes (FLIP) | `createLayout()` | `import { createLayout } from 'animejs'` |
| Reactive values | `createAnimatable()` | `import { createAnimatable } from 'animejs'` |
| Text splitting | `splitText()` | `import { splitText } from 'animejs'` |
| SVG morphing | `svg.morphTo()` | `import { svg } from 'animejs'` |
| SVG drawing | `svg.createDrawable()` | `import { svg } from 'animejs'` |
| SVG motion path | `svg.createMotionPath()` | `import { svg } from 'animejs'` |

### Easing Selection

| Context | Easing | Why |
|---------|--------|-----|
| UI entrance | `'out(3)'` to `'out(4)'` | Fast start, gentle stop |
| UI exit | `'in(3)'` | Slow start, quick exit |
| Hover/click feedback | `spring({ bounce: 0.5 })` | Natural rebound |
| Looping/ambient | `'inOut(2)'` | Symmetric, smooth |
| Scroll scrubbing | `'linear'` | Direct 1:1 mapping |
| Bouncy entrance | `'outBounce'` | Playful landing |
| Elastic snap | `'outElastic'` | Overshoot + settle |

### Animation Timing Guidelines

| Element Type | Duration | Delay Pattern |
|-------------|----------|---------------|
| Micro-interaction (hover, click) | 150-300ms | None |
| UI feedback (toggle, switch) | 200-400ms | None |
| Content entrance | 400-800ms | `stagger(50-150)` |
| Page transition | 300-600ms | Sequential |
| Hero reveal | 600-1200ms | `stagger(100-200)` |
| Scroll parallax | Match scroll | `'linear'` scrub |
| Loading/ambient | 1000-3000ms | Loop |

### v3 to v4 Migration

| v3 (Old) | v4 (New) |
|----------|----------|
| `anime({ targets, ... })` | `animate(targets, { ... })` |
| `anime.timeline()` | `createTimeline()` |
| `anime.stagger()` | `stagger()` |
| `direction: 'alternate'` | `alternate: true` |
| `direction: 'reverse'` | `reversed: true` |
| `easing: 'easeOutExpo'` | `ease: 'outExpo'` |
| `anime.remove()` | `animation.revert()` |

## Utilities Quick Reference

```js
import { utils } from 'animejs';
// or import individual utilities

utils.$('.selector')     // Query elements (returns array)
utils.get(el, 'prop')    // Get computed property value
utils.set(el, { x: 100 }) // Set properties immediately
utils.remove(animation)  // Remove animation
utils.sync(a, b)         // Sync two animations
utils.random(0, 100)     // Random number in range
utils.clamp(0, value, 100) // Clamp value
utils.mapRange(0, 1, 0, 100, 0.5) // Map value between ranges
utils.lerp(0, 100, 0.5)  // Linear interpolation
utils.snap(10, value)     // Snap to nearest increment
```

## Common Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| Animation not visible | Element has `opacity: 0` in CSS | Set initial state or use `from` parameter |
| Janky animation | Animating width/height/top/left | Use transform (x, y, scale) instead |
| Memory leak in SPA | Not cleaning up animations | `scope.revert()` in cleanup |
| React double-fire | StrictMode runs effects twice | `createScope()` + cleanup handles this |
| Animation stacks | Multiple triggers without cancel | Call `.revert()` before re-creating |
| WAAPI missing features | Using JS-only features with `waapi` | Switch to `animate()` for full API |
| Layout animation flicker | No explicit dimensions | Set CSS width/height before animating |

## Reference Files

| File | Contents |
|------|----------|
| `references/core-api.md` | animate() function, targets, properties, tweens, keyframes, playback, callbacks, methods, WAAPI variant |
| `references/timelines-and-scope.md` | createTimeline(), time positions, createScope(), React integration pattern |
| `references/scroll-and-events.md` | onScroll(), ScrollObserver settings, thresholds, sync modes, scroll patterns |
| `references/svg-and-text.md` | SVG morphTo/createDrawable/createMotionPath, splitText(), text animation patterns |
| `references/interactive-features.md` | createDraggable(), createLayout() (FLIP), createAnimatable(), interaction patterns |
| `references/easing-and-performance.md` | Easing functions, spring physics, stagger(), WAAPI vs JS, engine config, performance |
| `references/website-animation-recipes.md` | Production-ready recipes: hero, scroll reveals, nav, micro-interactions, page transitions |
