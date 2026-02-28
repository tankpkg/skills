# Scroll-Linked Animations

Sources: Anime.js v4 official documentation (animejs.com)

Covers: onScroll() function, ScrollObserver settings, thresholds, synchronisation
modes, callbacks, methods, and production scroll patterns.

## onScroll() Function

```js
import { onScroll, animate } from 'animejs';

animate('.section', {
  opacity: [0, 1],
  y: [50, 0],
  autoplay: onScroll({ target: '.section' })
});
```

Subpath: `import { onScroll } from 'animejs/events'`

Pass `onScroll()` as the `autoplay` parameter. Returns a `ScrollObserver`.

### Standalone Usage

```js
const observer = onScroll({
  target: '.el',
  onEnter: () => console.log('entered viewport'),
  onLeave: () => console.log('left viewport')
});
```

## ScrollObserver Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `container` | Element | viewport | Scroll container |
| `target` | Element/string | animation targets | Observed element |
| `debug` | bool | `false` | Show visual debug markers |
| `axis` | `'y'`/`'x'` | `'y'` | Scroll direction |
| `repeat` | bool | `true` | Re-trigger on re-enter |

```js
animate('.el', {
  x: 200,
  autoplay: onScroll({
    container: document.querySelector('.scroll-wrapper'),
    target: '.el',
    axis: 'y',
    debug: true,  // Shows colored threshold markers
    repeat: false // Only trigger once
  })
});
```

## Thresholds

Thresholds define WHEN the scroll observer triggers, based on target
position relative to the viewport/container.

### Numeric Values

```js
onScroll({ enter: 100, leave: -100 }) // Pixel offsets
```

### Position Shorthands

| Shorthand | Meaning |
|-----------|---------|
| `'top'` | Top edge of viewport |
| `'center'` | Center of viewport |
| `'bottom'` | Bottom edge of viewport |
| `'left'` | Left edge (horizontal) |
| `'right'` | Right edge (horizontal) |

### Relative Position Values

Format: `'targetEdge viewportEdge'`

```js
onScroll({
  enter: 'top bottom',   // Target top hits viewport bottom (default)
  leave: 'bottom top'    // Target bottom passes viewport top
})
```

Common configurations:

| Enter | Leave | Behavior |
|-------|-------|----------|
| `'top bottom'` | `'bottom top'` | Visible while any part in viewport |
| `'top center'` | `'bottom center'` | Visible while crossing center |
| `'top top'` | `'bottom bottom'` | Visible while fully in viewport |
| `'center center'` | `'center center'` | Trigger at exact center |

### Min/Max

```js
onScroll({
  enter: { min: 'top bottom', max: 'top center' },
  leave: { min: 'bottom center', max: 'bottom top' }
})
```

## Synchronisation Modes

How the ScrollObserver syncs with the linked animation.

### 1. Method Names (Default)

Play/pause on enter/leave. Animation runs at its own pace.

```js
animate('.el', {
  x: 200,
  duration: 1000,
  autoplay: onScroll() // Plays on enter, pauses on leave
});
```

Custom method mapping:

```js
onScroll({
  enter: 'play',    // or 'restart', 'reverse', 'alternate'
  leave: 'pause'    // or 'reverse', 'complete', 'reset'
})
```

### 2. Playback Progress (Scrubbing)

Animation progress maps directly to scroll position.

```js
animate('.el', {
  x: 200,
  autoplay: onScroll({
    enter: 'top bottom',
    leave: 'bottom top',
    sync: true  // Enable scrubbing
  })
});
```

### 3. Smooth Scroll

Interpolated scrubbing for smoother motion.

```js
onScroll({
  sync: 'smooth',
  // or sync: { smooth: 200 } // Custom smoothing in ms
})
```

### 4. Eased Scroll

Custom easing applied to scroll synchronization.

```js
onScroll({
  sync: { ease: 'out(3)' }
})
```

## ScrollObserver Callbacks

| Callback | Fires When |
|----------|-----------|
| `onEnter` | Target enters threshold |
| `onEnterForward` | Enters while scrolling down/right |
| `onEnterBackward` | Enters while scrolling up/left |
| `onLeave` | Target leaves threshold |
| `onLeaveForward` | Leaves while scrolling down/right |
| `onLeaveBackward` | Leaves while scrolling up/left |
| `onUpdate` | Every scroll tick while in range |
| `onSyncComplete` | Synced animation completes |
| `onResize` | Container resizes |

```js
animate('.el', {
  x: 200,
  autoplay: onScroll({
    onEnter: (observer) => console.log('visible'),
    onLeave: (observer) => console.log('hidden'),
    onUpdate: (observer) => {
      console.log('progress:', observer.progress);
      console.log('velocity:', observer.velocity);
    }
  })
});
```

## ScrollObserver Methods

| Method | Description |
|--------|-------------|
| `link(animation)` | Link additional animation to observer |
| `refresh()` | Recalculate positions (after layout change) |
| `revert()` | Remove observer and clean up |

```js
const observer = onScroll({ target: '.section' });

// Link multiple animations to same scroll observer
const anim1 = animate('.title', { y: [30, 0], autoplay: observer });
observer.link(animate('.body', { opacity: [0, 1] }));
```

## ScrollObserver Properties

| Property | Type | Description |
|----------|------|-------------|
| `progress` | number | Scroll progress 0-1 |
| `velocity` | number | Current scroll velocity |
| `isInView` | bool | Target currently in threshold |
| `scrollY` / `scrollX` | number | Current scroll position |

## Production Scroll Patterns

### Fade-In on Scroll Enter

```js
import { animate, stagger, onScroll } from 'animejs';

document.querySelectorAll('.reveal').forEach(el => {
  animate(el, {
    opacity: [0, 1],
    y: [40, 0],
    duration: 800,
    ease: 'out(3)',
    autoplay: onScroll({ target: el, repeat: false })
  });
});
```

### Staggered Grid Reveal

```js
animate('.grid-item', {
  opacity: [0, 1],
  scale: [0.8, 1],
  delay: stagger(80, { grid: [4, 4], from: 'center' }),
  duration: 600,
  autoplay: onScroll({ target: '.grid' })
});
```

### Parallax Scrub

```js
animate('.parallax-bg', {
  y: [0, -200],
  autoplay: onScroll({
    enter: 'top bottom',
    leave: 'bottom top',
    sync: 'smooth'
  })
});
```

### Scroll Progress Bar

```js
animate('.progress-bar', {
  scaleX: [0, 1],
  autoplay: onScroll({
    target: document.body,
    enter: 'top top',
    leave: 'bottom bottom',
    sync: true
  })
});
```

### Horizontal Scroll Section

```js
const container = document.querySelector('.horizontal-scroll');

animate('.horizontal-panels', {
  x: [0, -(container.scrollWidth - window.innerWidth)],
  ease: 'linear',
  autoplay: onScroll({
    container: container,
    axis: 'x',
    sync: true
  })
});
```

### Number Counter on Scroll

```js
const counter = { value: 0 };
const display = document.querySelector('.counter');

animate(counter, {
  value: 1000,
  duration: 2000,
  ease: 'out(3)',
  onUpdate: () => { display.textContent = Math.round(counter.value); },
  autoplay: onScroll({ target: display, repeat: false })
});
```

### Timeline Synced to Scroll

```js
import { createTimeline, onScroll } from 'animejs';

const tl = createTimeline({
  defaults: { duration: 500, ease: 'out(3)' },
  autoplay: onScroll({
    target: '.story-section',
    sync: 'smooth'
  })
});

tl.add('.step-1', { opacity: [0, 1], x: [-50, 0] })
  .add('.step-2', { opacity: [0, 1], x: [50, 0] }, '-=200')
  .add('.step-3', { opacity: [0, 1], scale: [0.5, 1] }, '-=200');
```
