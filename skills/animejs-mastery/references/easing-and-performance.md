# Easing and Performance

Sources: Anime.js v4 official documentation (animejs.com)

Covers: built-in easings, spring physics, stagger utility, cubic bezier, steps,
WAAPI vs JS engine selection, engine configuration, and performance best practices.

## Built-in Easing Functions

### Power-Based (Recommended)

Shorthand format: `'in(power)'`, `'out(power)'`, `'inOut(power)'`

| Ease | Power | Character | Best For |
|------|-------|-----------|----------|
| `'out(2)'` | 2 | Gentle deceleration | Subtle entrances |
| `'out(3)'` | 3 | Medium deceleration | **Default choice for UI** |
| `'out(4)'` | 4 | Strong deceleration | Snappy entrances |
| `'in(3)'` | 3 | Slow start, fast end | Exits, removals |
| `'inOut(2)'` | 2 | Symmetric | Looping, ambient |
| `'inOut(3)'` | 3 | Pronounced symmetric | Transitions |

### Named Easings

| In | Out | InOut | Character |
|----|-----|-------|-----------|
| `'inQuad'` | `'outQuad'` | `'inOutQuad'` | Gentle (power 2) |
| `'inCubic'` | `'outCubic'` | `'inOutCubic'` | Medium (power 3) |
| `'inQuart'` | `'outQuart'` | `'inOutQuart'` | Strong (power 4) |
| `'inQuint'` | `'outQuint'` | `'inOutQuint'` | Very strong (power 5) |
| `'inExpo'` | `'outExpo'` | `'inOutExpo'` | Exponential |
| `'inSine'` | `'outSine'` | `'inOutSine'` | Very gentle |
| `'inCirc'` | `'outCirc'` | `'inOutCirc'` | Circular |
| `'inBack'` | `'outBack'` | `'inOutBack'` | Overshoot |
| `'inBounce'` | `'outBounce'` | `'inOutBounce'` | Bouncing |
| `'inElastic'` | `'outElastic'` | `'inOutElastic'` | Elastic/rubber |

### Linear

```js
animate('.el', { x: 200, ease: 'linear' }); // Constant speed
```

### Choosing the Right Easing

| Context | Recommendation |
|---------|---------------|
| UI element entrance | `'out(3)'` or `'outExpo'` |
| UI element exit | `'in(3)'` or `'inExpo'` |
| Hover/click feedback | `spring({ bounce: 0.5 })` |
| Toggle/switch | `'inOut(2)'` |
| Scroll scrubbing | `'linear'` |
| Playful/fun UI | `'outBounce'` or `'outElastic'` |
| Background/ambient | `'inOut(2)'` with loop |
| Data visualization | `'out(4)'` |
| Modal entrance | `'outBack'` (slight overshoot) |

## Cubic Bezier

CSS-compatible custom curves:

```js
animate('.el', { x: 200, ease: 'cubicBezier(0.25, 0.1, 0.25, 1.0)' });
```

Common presets:
| Name | Value | Notes |
|------|-------|-------|
| ease | `cubicBezier(0.25, 0.1, 0.25, 1.0)` | CSS default |
| ease-in | `cubicBezier(0.42, 0, 1.0, 1.0)` | |
| ease-out | `cubicBezier(0, 0, 0.58, 1.0)` | |
| ease-in-out | `cubicBezier(0.42, 0, 0.58, 1.0)` | |

## Linear with Stops

Custom linear easing with percentage control points:

```js
animate('.el', { x: 200, ease: 'linear(0, 0.5 25%, 1)' });
```

## Steps

Discrete stepping (frame-by-frame feel):

```js
animate('.sprite', { x: 500, ease: 'steps(10)', duration: 1000 });
```

## Spring Physics

```js
import { spring } from 'animejs';
```

### Bounce Shorthand (Recommended)

```js
animate('.el', { scale: [0, 1], ease: spring({ bounce: 0.7 }) });
```

`bounce` range: `0` (no bounce) to `1` (maximum bounce)

### Full Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mass` | number | `1` | Object mass |
| `stiffness` | number | `100` | Spring stiffness |
| `damping` | number | `10` | Friction/resistance |
| `velocity` | number | `0` | Initial velocity |
| `bounce` | number | — | Shorthand (overrides above) |

```js
// Custom physics
animate('.el', {
  x: 200,
  ease: spring({ mass: 1, stiffness: 200, damping: 15 })
});

// Quick snap
animate('.el', { scale: 1.2, ease: spring({ bounce: 0.3 }) });

// Bouncy entrance
animate('.el', { y: [100, 0], ease: spring({ bounce: 0.8 }) });
```

### When to Use Spring vs Easing

| Scenario | Use |
|----------|-----|
| User interaction response | Spring |
| Natural motion (drag release) | Spring |
| Timed sequences/timelines | Easing |
| Scroll-linked animation | Easing (linear) |
| CSS-compatible (WAAPI) | Easing or spring |
| Precise duration control | Easing (spring has dynamic duration) |

## stagger() Utility

Distribute values across multiple targets.

```js
import { stagger } from 'animejs';
```

### Time Staggering

```js
animate('.item', { x: 100, delay: stagger(100) }); // 0ms, 100ms, 200ms...
```

### Value Staggering

```js
animate('.item', { rotate: stagger([0, 360]) }); // Distributed 0-360
animate('.bar', { height: stagger([10, 200]) }); // Distributed heights
```

### Stagger Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | number | Starting value (default: 0) |
| `from` | string/number | Direction: `'first'`, `'last'`, `'center'`, index |
| `reversed` | bool | Reverse stagger order |
| `ease` | string | Ease the distribution |
| `grid` | `[rows, cols]` | 2D grid staggering |
| `axis` | `'x'`/`'y'` | Grid axis (with grid) |
| `modifier` | function | Transform each value |
| `use` | function | Custom per-element function |
| `total` | number | Override element count |

### Common Patterns

```js
// From center outward
animate('.item', { scale: [0, 1], delay: stagger(50, { from: 'center' }) });

// From last to first
animate('.item', { opacity: [0, 1], delay: stagger(50, { from: 'last' }) });

// With easing (non-linear spacing)
animate('.item', { x: 100, delay: stagger(200, { ease: 'out(3)' }) });

// Grid stagger (2D ripple)
animate('.cell', {
  scale: [0, 1],
  delay: stagger(50, { grid: [10, 10], from: 'center' })
});

// Grid with axis
animate('.cell', {
  y: [-20, 0],
  delay: stagger(40, { grid: [5, 8], from: 'first', axis: 'x' })
});
```

### Timeline Position Staggering

```js
const tl = createTimeline();
elements.forEach((el, i) => {
  tl.add(el, { x: 100 }, stagger(100)(el, i, elements.length));
});
```

## WAAPI vs JS Engine

### Decision Table

| Criteria | JS (`animate`) | WAAPI (`waapi.animate`) |
|----------|---------------|------------------------|
| Bundle size | ~10KB | ~3KB |
| Hardware accelerated | No | Yes (transform, opacity) |
| JS object animation | Yes | No |
| SVG attributes | Yes | No |
| Function-based values | Yes | Limited |
| Callbacks (onUpdate) | Yes | No |
| Modifier functions | Yes | No |
| Spring easing | Yes | Yes (converted) |
| Composition control | Yes | No |

### Using WAAPI

```js
import { waapi } from 'animejs';

const anim = waapi.animate('.el', {
  x: 250,
  opacity: [0, 1],
  duration: 600,
  ease: 'out(3)'
});
```

### Converting Easings for WAAPI

```js
import { waapi } from 'animejs';

const cssEasing = waapi.convertEase('outExpo');
// Returns CSS-compatible easing string
```

## Engine Configuration

```js
import { engine } from 'animejs';
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeUnit` | string | `'ms'` | `'ms'` or `'s'` |
| `speed` | number | `1` | Global speed multiplier |
| `fps` | number | `120` | Target frame rate |
| `precision` | number | `4` | Decimal precision |
| `pauseOnDocumentHidden` | bool | `true` | Pause in background tabs |

```js
// Global slow-motion
engine.speed = 0.5;

// Use seconds instead of ms
engine.timeUnit = 's';
animate('.el', { x: 200, duration: 0.6 }); // 0.6 seconds

// Limit FPS for performance
engine.fps = 60;

// Manual tick (for game loops)
engine.pause();
function gameLoop(time) {
  engine.update(time);
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

## Performance Best Practices

### Compositor-Friendly Properties

Animate these for 60fps:
- `transform` (x, y, z, rotate, scale, skew)
- `opacity`

Avoid animating (triggers layout):
- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`, `border-width`
- `font-size`

### Optimization Checklist

1. **Prefer transform/opacity** for smooth 60fps
2. **Use WAAPI** for simple transform/opacity animations
3. **Use `will-change: transform`** on elements that will animate (sparingly)
4. **Clean up with `revert()`** in SPAs to prevent memory leaks
5. **Limit concurrent animations** — 50+ simultaneous tweens can cause jank
6. **Use `stagger()`** instead of creating individual animations
7. **Avoid animating during scroll** without throttling (use `onScroll` sync)
8. **Use `frameRate`** to cap animation FPS on low-power devices
9. **Profile with DevTools** — Performance tab, paint flashing, layers panel
10. **Prefer `createLayout()`** over manual position animation for layout changes
