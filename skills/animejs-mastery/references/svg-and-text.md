# SVG and Text Animations

Sources: Anime.js v4 official documentation (animejs.com)

Covers: SVG morphTo(), createDrawable(), createMotionPath(), text splitText(),
and production patterns for both.

## SVG Utilities

```js
import { svg } from 'animejs';
// or individual imports
import { morphTo, createDrawable, createMotionPath } from 'animejs';
// or subpath
import { morphTo, createDrawable, createMotionPath } from 'animejs/svg';
```

## morphTo() — Shape Morphing

Morph one SVG path into another. Handles mismatched point counts automatically.

```js
import { animate, svg } from 'animejs';

animate('#path-start', {
  d: svg.morphTo('#path-end'),
  duration: 1000,
  ease: 'inOut(3)'
});
```

### How It Works

1. Takes a target path element (CSS selector or DOM reference)
2. Reads the `d` attribute from both source and target
3. Interpolates between path data, adding points as needed
4. Animate the `d` attribute of the source path

### Morphing Between Multiple Shapes

```js
import { createTimeline, svg } from 'animejs';

const tl = createTimeline({ loop: true, alternate: true });
tl.add('#shape', { d: svg.morphTo('#circle') })
  .add('#shape', { d: svg.morphTo('#star') })
  .add('#shape', { d: svg.morphTo('#heart') });
```

### Tips

- Both paths should be in the same SVG container
- Hide target paths with CSS: `#path-end { display: none; }`
- More similar point counts = smoother morph
- Use same path direction (CW/CCW) for best results

## createDrawable() — Line Drawing

Create a drawable representation of an SVG stroke element for line drawing
animations.

```js
import { animate, svg } from 'animejs';

const drawable = svg.createDrawable('path.logo-outline');

animate(drawable, {
  draw: '0 1',          // Draw from 0% to 100%
  duration: 2000,
  ease: 'inOut(3)'
});
```

### Supported Elements

Works with any SVG element that has a stroke:
`path`, `line`, `polyline`, `polygon`, `circle`, `ellipse`, `rect`

### Draw Property Values

| Value | Meaning |
|-------|---------|
| `'0 1'` | Draw full path (0% to 100%) |
| `'0 0.5'` | Draw first half |
| `'0.5 1'` | Draw second half |
| `'1 0'` | Undraw (erase) |
| `[0, 1]` | Array shorthand |

### Draw-In Then Hold

```js
const drawable = svg.createDrawable('#logo path');

animate(drawable, {
  draw: ['0 0', '0 1'],  // From nothing to full
  duration: 2000,
  ease: 'out(3)'
});
```

### Multi-Path Sequential Drawing

```js
import { createTimeline, svg } from 'animejs';

const paths = document.querySelectorAll('#logo path');
const tl = createTimeline({ defaults: { ease: 'out(3)' } });

paths.forEach((path, i) => {
  const drawable = svg.createDrawable(path);
  tl.add(drawable, { draw: '0 1', duration: 800 }, i * 200);
});
```

### Setup CSS

```css
/* Required: set stroke, remove fill */
.drawable-path {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
}
```

## createMotionPath() — Path Following

Animate elements along an SVG path trajectory.

```js
import { animate, svg } from 'animejs';

const motionPath = svg.createMotionPath('#curved-path');

animate('.dot', {
  x: motionPath('x'),
  y: motionPath('y'),
  rotate: motionPath('angle'),  // Follow path tangent
  duration: 3000,
  ease: 'inOut(2)'
});
```

### Available Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `motionPath('x')` | function | X position along path |
| `motionPath('y')` | function | Y position along path |
| `motionPath('angle')` | function | Rotation angle (tangent) |

### Without Rotation

```js
animate('.element', {
  x: motionPath('x'),
  y: motionPath('y'),
  duration: 2000
});
```

### Looping Path Animation

```js
animate('.satellite', {
  x: motionPath('x'),
  y: motionPath('y'),
  rotate: motionPath('angle'),
  duration: 4000,
  loop: true,
  ease: 'linear'
});
```

## splitText() — Text Splitting

Split text elements into individually animatable lines, words, and characters.

```js
import { splitText } from 'animejs';
// or subpath
import { splitText } from 'animejs/text';

const { lines, words, chars } = splitText('h1', {
  lines: true,
  words: true,
  chars: true
});
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `lines` | bool | `false` | Split into line elements |
| `words` | bool | `true` | Split into word elements |
| `chars` | bool | `false` | Split into character elements |
| `debug` | bool | `false` | Add colored backgrounds |
| `includeSpaces` | bool | `false` | Include space characters |
| `accessible` | bool | `true` | Add aria-label for screen readers |

### Split Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `class` | string | CSS class added to split elements |
| `wrap` | string | HTML tag wrapping each split element |
| `clone` | bool | Clone original element (preserves original) |

### Return Value

```js
const result = splitText('.heading', { chars: true, words: true, lines: true });
// result.chars  — array of character elements
// result.words  — array of word elements
// result.lines  — array of line elements
```

### TextSplitter Methods

| Method | Description |
|--------|-------------|
| `addEffect(fn)` | Add animation effect to split elements |
| `revert()` | Restore original text (remove splits) |
| `refresh()` | Re-split (after resize or content change) |

## Text Animation Patterns

### Character-by-Character Reveal

```js
import { animate, stagger, splitText } from 'animejs';

const { chars } = splitText('h1', { chars: true });

animate(chars, {
  opacity: [0, 1],
  y: [20, 0],
  delay: stagger(30),
  duration: 400,
  ease: 'out(3)'
});
```

### Word-by-Word Slide Up

```js
const { words } = splitText('.tagline', { words: true });

animate(words, {
  opacity: [0, 1],
  y: ['1em', 0],
  delay: stagger(80),
  duration: 600,
  ease: 'out(4)'
});
```

### Line-by-Line Fade In

```js
const { lines } = splitText('.paragraph', { lines: true });

animate(lines, {
  opacity: [0, 1],
  x: [-30, 0],
  delay: stagger(150),
  duration: 800,
  ease: 'out(3)'
});
```

### Bouncy Character Entrance

```js
import { animate, stagger, splitText, spring } from 'animejs';

const { chars } = splitText('h2', { chars: true });

animate(chars, {
  y: [
    { to: '-2.75rem', ease: 'outExpo', duration: 600 },
    { to: 0, ease: spring({ bounce: 0.7 }), delay: 100 }
  ],
  rotate: { from: '-1turn', delay: 0 },
  delay: stagger(50),
  ease: 'inOutCirc',
  loop: true,
  loopDelay: 1000
});
```

### Scramble/Decode Effect

```js
const { chars } = splitText('.code', { chars: true });

animate(chars, {
  opacity: [0, 1],
  scale: [0, 1],
  rotate: () => Math.random() * 360,
  delay: stagger(20, { from: 'random' }),
  duration: 300,
  ease: 'outExpo'
});
```

## SVG Animation Patterns

### Logo Line Drawing on Load

```js
import { createTimeline, svg } from 'animejs';

const paths = document.querySelectorAll('#logo path');
const tl = createTimeline();

paths.forEach((path, i) => {
  const drawable = svg.createDrawable(path);
  tl.add(drawable, {
    draw: '0 1',
    duration: 1000,
    ease: 'inOut(3)'
  }, i * 150);
});

// After drawing, fade in fill
tl.add('#logo', { fillOpacity: [0, 1], duration: 500 });
```

### Icon State Morphing

```js
const morphToClose = () => animate('#menu-icon', {
  d: svg.morphTo('#close-shape'),
  duration: 400,
  ease: 'out(3)'
});

const morphToMenu = () => animate('#menu-icon', {
  d: svg.morphTo('#menu-shape'),
  duration: 400,
  ease: 'out(3)'
});
```

### Element on Curved Path

```js
const path = svg.createMotionPath('#flight-path');

animate('.airplane', {
  x: path('x'),
  y: path('y'),
  rotate: path('angle'),
  duration: 5000,
  ease: 'inOut(2)',
  loop: true
});
```

### Combined Draw + Fill Sequence

```js
const tl = createTimeline();
const drawable = svg.createDrawable('#illustration path');

tl.add(drawable, { draw: '0 1', duration: 2000, ease: 'inOut(3)' })
  .add('#illustration', {
    fillOpacity: [0, 1],
    strokeOpacity: [1, 0],
    duration: 800,
    ease: 'out(3)'
  }, '-=400');
```
