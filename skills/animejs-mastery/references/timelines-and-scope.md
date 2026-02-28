# Timelines and Scope

Sources: Anime.js v4 official documentation (animejs.com)

Covers: createTimeline(), time positions, timeline methods, createScope(),
React integration patterns, and cleanup.

## createTimeline()

```js
import { createTimeline } from 'animejs';
const tl = createTimeline(parameters);
```

Subpath: `import { createTimeline } from 'animejs/timeline'`

Returns a `Timeline` instance with chaining methods.

### Basic Usage

```js
const tl = createTimeline({ defaults: { duration: 600, ease: 'out(3)' } });

tl.add('h1', { opacity: [0, 1], y: [30, 0] })
  .add('.subtitle', { opacity: [0, 1], y: [20, 0] }, '-=400')
  .add('.cta', { scale: [0.8, 1], opacity: [0, 1] }, '-=300');
```

### Adding Content

| Method | What It Adds | Signature |
|--------|-------------|-----------|
| `add()` | Animation | `tl.add(targets, params, position)` |
| `add()` | Timer | `tl.add(timerParams, position)` |
| `sync()` | WAAPI animation | `tl.sync(wapiAnim, position)` |
| `sync()` | Another timeline | `tl.sync(otherTl, position)` |
| `call()` | Function | `tl.call(fn, position)` |
| `label()` | Named marker | `tl.label('name', position)` |
| `set()` | Instant property set | `tl.set(targets, props, position)` |

```js
// Add animation
tl.add('.box', { x: 200, rotate: '1turn' }, 500);

// Add timer
tl.add({ duration: 1000, onUpdate: (self) => console.log(self.progress) }, 0);

// Sync WAAPI animation
const wapiAnim = waapi.animate('.bg', { opacity: [0, 1] });
tl.sync(wapiAnim, 0);

// Call function at specific time
tl.call(() => console.log('halfway'), '50%');

// Set instant values
tl.set('.el', { opacity: 1 }, 0);
```

## Time Positions

The third argument to `add()`, `sync()`, `call()`, `label()` controls WHEN
in the timeline the child starts.

| Position | Meaning | Example |
|----------|---------|---------|
| Number | Absolute time (ms) | `500` = at 500ms |
| `'<'` | Start of previous child | Previous starts at 200ms, this too |
| `'<+=200'` | 200ms after previous starts | Overlap with offset |
| `'<-=100'` | 100ms before previous starts | Negative offset |
| `'<<'` | Start of child before previous | Two children back |
| `'-=500'` | 500ms before previous ends | Overlap end |
| `'+=500'` | 500ms after previous ends | Gap |
| `'labelName'` | At label position | Named anchor |
| `'labelName+=200'` | 200ms after label | Label with offset |

### Common Sequencing Patterns

```js
const tl = createTimeline({ defaults: { duration: 500 } });

// Sequential (default) - each after previous
tl.add('.a', { x: 100 })
  .add('.b', { x: 100 })
  .add('.c', { x: 100 });

// Overlapping - start 200ms before previous ends
tl.add('.a', { x: 100 })
  .add('.b', { x: 100 }, '-=200')
  .add('.c', { x: 100 }, '-=200');

// Simultaneous - all at same time
tl.add('.a', { x: 100 }, 0)
  .add('.b', { y: 100 }, 0)
  .add('.c', { rotate: '1turn' }, 0);

// Staggered from same point using label
tl.label('start')
  .add('.a', { x: 100 }, 'start')
  .add('.b', { x: 100 }, 'start+=100')
  .add('.c', { x: 100 }, 'start+=200');
```

## Timeline Playback Settings

| Setting | Type | Default | Notes |
|---------|------|---------|-------|
| `defaults` | object | `{}` | Default params for all child animations |
| `delay` | number | `0` | Delay before timeline starts |
| `loop` | bool/number | `false` | Loop entire timeline |
| `loopDelay` | number | `0` | Pause between loops |
| `alternate` | bool | `false` | Reverse on each loop |
| `reversed` | bool | `false` | Play backwards |
| `autoplay` | bool/ScrollObserver | `true` | Can use `onScroll()` |
| `frameRate` | number | engine fps | Target FPS |
| `playbackRate` | number | `1` | Speed multiplier |
| `playbackEase` | string | — | Ease overall timeline progress |

```js
const tl = createTimeline({
  defaults: { duration: 600, ease: 'out(3)' },
  loop: true,
  alternate: true,
  autoplay: onScroll({ target: '.section' })
});
```

## Timeline Callbacks

Same as animation callbacks: onBegin, onComplete, onBeforeUpdate, onUpdate,
onRender, onLoop, onPause, then().

```js
const tl = createTimeline({
  onComplete: () => console.log('Timeline finished'),
  onLoop: (self) => console.log('Loop', self.currentIteration)
});
```

## Timeline Methods

All animation methods plus timeline-specific:

| Method | Description |
|--------|-------------|
| `add()` | Add animation or timer |
| `set()` | Set properties instantly |
| `sync()` | Sync WAAPI animation or timeline |
| `label()` | Add named time marker |
| `remove()` | Remove child by reference |
| `call()` | Add function callback |
| `init()` | Initialize without playing |
| `play()` | Start playback |
| `pause()` | Pause |
| `reverse()` | Reverse direction |
| `restart()` | Reset and play |
| `seek(time)` | Seek to time |
| `stretch(dur)` | Change total duration |
| `refresh()` | Recalculate from DOM |
| `revert()` | Stop and clean up |

## createScope()

Scopes all anime.js instances to a DOM subtree. Essential for component-based
frameworks (React, Vue) and cleanup.

```js
import { createScope } from 'animejs';

const scope = createScope({ root: document.querySelector('#app') });

scope.add(() => {
  // All animations here are scoped to #app
  animate('.card', { opacity: 1 });
  createTimeline().add('.item', { x: 100 });
});

// Clean up ALL animations in scope
scope.revert();
```

### Scope Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | Element/Ref | DOM element that scopes CSS selectors |
| `defaults` | object | Default animation parameters for scope |
| `mediaQueries` | object | Responsive breakpoint handlers |

### Scope Methods

| Method | Description |
|--------|-------------|
| `add(fn)` | Add constructor — runs immediately, registers for cleanup |
| `addOnce(fn)` | Add constructor — runs once, not on refresh |
| `keepTime()` | Preserve timeline positions across refresh |
| `revert()` | Destroy all animations and clean inline styles |
| `refresh()` | Re-run constructors (responsive/resize) |

### Registering Reusable Methods

```js
scope.add(self => {
  self.add('animateIn', () => {
    animate('.card', { opacity: [0, 1], y: [20, 0] });
  });

  self.add('animateOut', () => {
    animate('.card', { opacity: 0, y: -20 });
  });
});

// Use from outside scope
scope.methods.animateIn();
scope.methods.animateOut();
```

### Media Queries

```js
const scope = createScope({
  root: containerRef,
  mediaQueries: {
    small: '(max-width: 640px)',
    large: '(min-width: 641px)'
  }
});

scope.add((self, { small, large }) => {
  if (small) animate('.el', { x: 50 });
  if (large) animate('.el', { x: 200 });
});
```

## React Integration

### Standard Pattern

```js
import { createScope, animate, spring, createDraggable } from 'animejs';
import { useEffect, useRef, useState } from 'react';

function AnimatedComponent() {
  const root = useRef(null);
  const scope = useRef(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    scope.current = createScope({ root }).add(self => {
      // All animations scoped to root element
      animate('.item', {
        scale: [{ to: 1.25, ease: 'inOut(3)', duration: 200 },
                { to: 1, ease: spring({ bounce: 0.7 }) }],
        loop: true,
        loopDelay: 250
      });

      // Register methods callable from handlers
      self.add('highlight', () => {
        animate('.item', { rotate: '+=360', ease: 'out(4)' });
      });
    });

    // CRITICAL: cleanup on unmount
    return () => scope.current.revert();
  }, []);

  const handleClick = () => {
    setCount(prev => prev + 1);
    scope.current.methods.highlight();
  };

  return (
    <div ref={root}>
      <div className="item" onClick={handleClick}>
        Count: {count}
      </div>
    </div>
  );
}
```

### Key Rules for React

1. **Always use `createScope({ root })`** — scopes selectors to component
2. **Always `return () => scope.current.revert()`** — prevents memory leaks
3. **Use `self.add('name', fn)` for methods** — safely callable from handlers
4. **Access methods via `scope.current.methods.name()`** — not direct calls
5. **StrictMode safe** — scope handles double-mount cleanup automatically

### Multiple Animations with State

```js
useEffect(() => {
  scope.current = createScope({ root }).add(self => {
    self.add('updateProgress', (value) => {
      animate('.progress-bar', {
        width: `${value}%`,
        duration: 400,
        ease: 'out(3)'
      });
    });
  });
  return () => scope.current.revert();
}, []);

// Call when state changes
useEffect(() => {
  if (scope.current) {
    scope.current.methods.updateProgress(progress);
  }
}, [progress]);
```

## Cleanup Patterns

### Vanilla JS / SPA Router

```js
// Create
const scope = createScope({ root: document.querySelector('#page') });
scope.add(() => { /* animations */ });

// On page leave / component destroy
scope.revert(); // Removes ALL animations and inline styles
```

### Individual Animation Cleanup

```js
const anim = animate('.el', { x: 100 });
// Later...
anim.revert(); // Stops and removes inline styles from this animation
```
