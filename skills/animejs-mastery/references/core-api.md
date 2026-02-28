# Core Animation API

Sources: Anime.js v4 official documentation (animejs.com), juliangarnier/anime GitHub

Covers: animate() function, targets, animatable properties, tween values, tween
parameters, keyframes, playback settings, callbacks, methods, and WAAPI variant.

## animate() Function

```js
import { animate } from 'animejs';
const animation = animate(targets, parameters);
```

Standalone subpath import: `import { animate } from 'animejs/animation'`

Returns a `JSAnimation` instance with methods, callbacks, and properties.

## Targets

| Type | Example | Notes |
|------|---------|-------|
| CSS Selector | `'.card'`, `'#hero h1'` | Queries all matching elements |
| DOM Element | `document.querySelector('.el')` | Single element |
| NodeList | `document.querySelectorAll('.items')` | Multiple elements |
| JS Object (JS) | `{ x: 0, y: 0 }` | Animate plain object properties |
| Array | `['.a', el, nodeList, obj]` | Mix of any target types |

```js
// CSS selector
animate('.card', { opacity: 1 });

// DOM element
const el = document.getElementById('hero');
animate(el, { x: 100 });

// JS object (JS engine only)
const pos = { x: 0, y: 0 };
animate(pos, { x: 100, y: 200, duration: 1000 });

// Mixed array
animate(['.cards', el, pos], { opacity: [0, 1] });
```

## Animatable Properties

### CSS Properties

Animate any CSS property with a numerical value:

```js
animate('.el', {
  opacity: 0.5,
  width: '200px',
  borderRadius: '50%',
  backgroundColor: '#ff0000'
});
```

### CSS Transforms (Shorthand)

| Shorthand | CSS Equivalent | Default Unit |
|-----------|---------------|--------------|
| `x` | `translateX` | `px` |
| `y` | `translateY` | `px` |
| `z` | `translateZ` | `px` |
| `rotate` | `rotate` | `deg` |
| `rotateX` | `rotateX` | `deg` |
| `rotateY` | `rotateY` | `deg` |
| `rotateZ` | `rotateZ` | `deg` |
| `scale` | `scale` | — |
| `scaleX` | `scaleX` | — |
| `scaleY` | `scaleY` | — |
| `skew` | `skew` | `deg` |
| `skewX` | `skewX` | `deg` |
| `skewY` | `skewY` | `deg` |

```js
animate('.el', { x: 250, rotate: '1turn', scale: 1.5 });
```

### CSS Variables (JS)

```js
animate('.el', { '--progress': '100%', duration: 2000 });
```

### JS Object Properties (JS)

```js
const data = { progress: 0 };
animate(data, { progress: 100, duration: 1000, onUpdate: () => console.log(data.progress) });
```

### HTML Attributes (JS)

```js
animate('input[type=range]', { value: 100, duration: 2000 });
```

### SVG Attributes (JS)

```js
animate('circle', { cx: 200, cy: 150, r: 50 });
animate('rect', { x: 100, width: 200 });
```

## Tween Value Types

| Type | Example | Notes |
|------|---------|-------|
| Numerical | `100` | Uses default unit for property |
| With unit | `'200px'`, `'50%'`, `'2rem'` | Explicit unit |
| Unit conversion | `'100%'` on el with px width | Auto-converts |
| Relative (JS) | `'+=100'`, `'-=50'`, `'*=2'` | Relative to current |
| Color | `'#ff0'`, `'rgb(255,0,0)'`, `'hsl(0,100%,50%)'` | Any CSS color format |
| CSS variable | `'var(--color)'` | Resolves at runtime |
| Function-based | `(el, i, total) => i * 50` | Per-target values |

### From/To Shorthand

```js
// Animate from 0 to 100
animate('.el', { x: [0, 100] });

// Function-based: stagger-like per element
animate('.item', {
  x: (el, i) => i * 100,
  delay: (el, i) => i * 50
});
```

## Tween Parameters

Per-property parameters allow individual control:

```js
animate('.el', {
  x: { to: 250, duration: 800, ease: 'outExpo' },
  rotate: { from: '-1turn', delay: 0 },
  opacity: { to: 1, duration: 400 }
});
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `to` | value | End value |
| `from` | value | Start value (element's current value if omitted) |
| `delay` | number/fn | Delay before this property starts |
| `duration` | number/fn | Duration for this property |
| `ease` | string/fn | Easing for this property |
| `composition` (JS) | string | `'none'` / `'replace'` / `'blend'` |
| `modifier` (JS) | fn | Transform computed value: `v => Math.round(v)` |

## Keyframes

### Value Array Keyframes

```js
animate('.el', { x: [0, 100, 50, 200] }); // Steps through values
```

### Parameter Keyframes (JS)

```js
animate('.el', {
  y: [
    { to: -100, ease: 'outExpo', duration: 600 },
    { to: 0, ease: 'outBounce', duration: 800 }
  ]
});
```

### Duration-Based Keyframes (JS)

```js
animate('.el', {
  keyframes: [
    { x: 100, duration: 500 },
    { y: 50, duration: 300 },
    { rotate: '1turn', duration: 800 }
  ]
});
```

### Percentage-Based Keyframes (JS)

```js
animate('.el', {
  keyframes: {
    '0%': { x: 0, y: 0 },
    '50%': { x: 200, y: -100 },
    '100%': { x: 400, y: 0 }
  }
});
```

## Playback Settings

| Setting | Type | Default | Notes |
|---------|------|---------|-------|
| `delay` | number/fn | `0` | Before first play |
| `duration` | number/fn | `1000` | Animation duration in ms |
| `loop` | bool/number | `false` | `true` = infinite, number = count |
| `loopDelay` (JS) | number | `0` | Pause between loops |
| `alternate` | bool | `false` | Reverse on each loop (replaces v3 `direction`) |
| `reversed` | bool | `false` | Play backwards |
| `autoplay` | bool/ScrollObserver | `true` | `false` or `onScroll()` |
| `frameRate` (JS) | number | `engine.fps` | Target FPS |
| `playbackRate` | number | `1` | Speed multiplier |
| `playbackEase` (JS) | string | — | Ease the overall progress |
| `persist` (WAAPI) | bool | `true` | Keep final state |

```js
animate('.el', {
  x: 250,
  duration: 800,
  delay: 200,
  ease: 'outExpo',
  loop: 3,
  alternate: true,
  autoplay: false // manual control
});
```

## Callbacks

| Callback | Fires When | Signature |
|----------|-----------|-----------|
| `onBegin` (JS) | First frame | `(animation) => {}` |
| `onComplete` | Last frame | `(animation) => {}` |
| `onBeforeUpdate` (JS) | Before each tick | `(animation) => {}` |
| `onUpdate` (JS) | After each tick | `(animation) => {}` |
| `onRender` (JS) | After DOM update | `(animation) => {}` |
| `onLoop` (JS) | Each loop iteration | `(animation) => {}` |
| `onPause` (JS) | On pause | `(animation) => {}` |
| `then()` | On complete (promise) | `.then(anim => {})` |

```js
animate('.el', {
  x: 250,
  onBegin: (anim) => console.log('started'),
  onComplete: (anim) => console.log('done')
});

// Promise-style
animate('.el', { x: 250 }).then(() => {
  animate('.el', { y: 100 });
});
```

## Playback Methods

| Method | Description |
|--------|-------------|
| `play()` | Start/resume playback |
| `pause()` | Pause at current position |
| `reverse()` | Reverse direction |
| `restart()` | Reset and play from start |
| `alternate()` | Toggle direction |
| `resume()` | Resume from pause |
| `complete()` | Jump to end |
| `cancel()` | Stop without finishing |
| `revert()` | Stop and remove all inline styles |
| `reset()` (JS) | Reset to initial state without playing |
| `seek(time)` | Seek to time in ms |
| `stretch(dur)` (JS) | Change total duration |
| `refresh()` (JS) | Recalculate from DOM |

```js
const anim = animate('.el', { x: 250, autoplay: false });
anim.play();
anim.seek(500);    // Seek to 500ms
anim.reverse();
anim.pause();
anim.revert();     // Clean up completely
```

## Animation Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | number | Unique animation ID |
| `targets` | array | Animated target elements |
| `currentTime` | number | Current playback time |
| `duration` | number | Total duration |
| `progress` | number | Progress 0-1 |
| `paused` | bool | Whether paused |
| `began` | bool | Whether started |
| `completed` | bool | Whether finished |
| `reversed` | bool | Current direction |
| `currentIteration` | number | Current loop count |

## WAAPI Variant

Lightweight (3KB) hardware-accelerated alternative:

```js
import { waapi } from 'animejs';

const anim = waapi.animate('.el', {
  x: 250,
  opacity: [0, 1],
  duration: 600,
  ease: 'out(3)'
});
```

### JS vs WAAPI Feature Comparison

| Feature | JS (10KB) | WAAPI (3KB) |
|---------|-----------|-------------|
| CSS properties | Yes | Yes |
| CSS transforms | Yes | Yes |
| Colors | Yes | Yes |
| Keyframes | Yes | Yes |
| JS Object targets | Yes | No |
| SVG attributes | Yes | No |
| HTML attributes | Yes | No |
| CSS variables | Yes | No |
| Function-based values | Yes | Limited |
| Relative values | Yes | No |
| onUpdate/onRender | Yes | No |
| Modifier functions | Yes | No |
| Hardware acceleration | No | Yes (transform/opacity) |
| composition param | Yes | No |

Use WAAPI for: simple transform/opacity animations where performance matters.
Use JS for: complex animations, SVG, JS objects, callbacks, fine-grained control.
