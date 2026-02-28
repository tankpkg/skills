# Interactive Features

Sources: Anime.js v4 official documentation (animejs.com)

Covers: createDraggable(), createLayout(), createAnimatable() — three v4 APIs
for building interactive, physics-based, and layout-aware animations.

## createDraggable()

Make elements draggable with physics-based release, snapping, and containers.

```js
import { createDraggable } from 'animejs';

const draggable = createDraggable('.card', {
  container: '.card-area',
  releaseEase: spring({ bounce: 0.5 })
});
```

### Axes Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | number/array/bool | X-axis bounds: `[-100, 100]`, `true` (free), `false` (locked) |
| `y` | number/array/bool | Y-axis bounds: `[-100, 100]`, `true` (free), `false` (locked) |
| `snap` | number/array | Snap to grid: `50` (every 50px) or `[0, 100, 200]` (specific values) |
| `modifier` | function | Transform position: `(value) => Math.round(value / 10) * 10` |
| `mapTo` | string/element | Map drag movement to another element |

```js
// Horizontal slider
createDraggable('.slider-thumb', {
  x: [0, 300],
  y: false,
  snap: 10
});

// Grid snapping
createDraggable('.tile', {
  snap: 80,
  releaseEase: spring({ stiffness: 300 })
});

// Map drag to another element
createDraggable('.handle', {
  mapTo: '.controlled-element'
});
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `trigger` | string/element | target | Drag handle element |
| `container` | string/element/array | — | Containment boundary |
| `containerPadding` | number/array | `0` | Inner padding of container |
| `containerFriction` | number | `0.85` | Resistance at container edge |
| `releaseContainerFriction` | number | `0.65` | Edge resistance on release |
| `releaseMass` | number | `1` | Physics mass on release |
| `releaseStiffness` | number | `100` | Spring stiffness on snap |
| `releaseDamping` | number | `20` | Spring damping on release |
| `velocityMultiplier` | number | `1` | Throw velocity scale |
| `minVelocity` | number | `0` | Minimum throw velocity |
| `maxVelocity` | number | `Infinity` | Maximum throw velocity |
| `releaseEase` | string/fn | — | Release animation easing |
| `dragSpeed` | number | `1` | Drag sensitivity |
| `dragThreshold` | number | `0` | Pixels before drag starts |
| `scrollThreshold` | number | `30` | Scroll vs drag threshold |
| `scrollSpeed` | number | `1.5` | Auto-scroll speed |
| `cursor` | bool | `true` | Change cursor on drag |

### Callbacks

| Callback | Fires When |
|----------|-----------|
| `onGrab` | Pointer down on target |
| `onDrag` | During drag movement |
| `onUpdate` | Every animation tick |
| `onRelease` | Pointer up |
| `onSnap` | Snaps to position |
| `onSettle` | Release animation completes |
| `onResize` | Container resizes |
| `onAfterResize` | After resize recalculation |

```js
createDraggable('.card', {
  onGrab: (draggable) => console.log('grabbed'),
  onDrag: (draggable) => {
    console.log('x:', draggable.x, 'y:', draggable.y);
  },
  onRelease: (draggable) => console.log('released'),
  onSnap: (draggable) => console.log('snapped to', draggable.x)
});
```

### Methods

| Method | Description |
|--------|-------------|
| `disable()` | Disable dragging |
| `enable()` | Re-enable dragging |
| `setX(value)` | Programmatically set X position |
| `setY(value)` | Programmatically set Y position |
| `animateInView()` | Animate element into visible area |
| `scrollInView()` | Scroll to show element |
| `stop()` | Stop current release animation |
| `reset()` | Reset to initial position |
| `revert()` | Remove draggable and clean up |
| `refresh()` | Recalculate bounds |

## createLayout()

Animate CSS layout changes automatically using FLIP (First, Last, Invert, Play).
New in v4.

```js
import { createLayout } from 'animejs';

const layout = createLayout('.grid', {
  duration: 500,
  ease: 'out(3)'
});
```

### How FLIP Works

1. **Record** current positions of children
2. **Apply** DOM/CSS changes
3. **Animate** from old positions to new positions automatically

### Basic Usage Pattern

```js
const layout = createLayout('.container', {
  duration: 400,
  ease: 'out(3)'
});

// Record current state
layout.record();

// Make DOM/CSS changes
someElement.classList.toggle('expanded');
// or: container.appendChild(newChild);
// or: children.sort() and re-append

// Animate to new state
layout.animate();
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `children` | string | `'*'` | CSS selector for animated children |
| `delay` | number/fn | `0` | Animation delay |
| `duration` | number | `500` | Animation duration |
| `ease` | string | `'out(3)'` | Animation easing |
| `properties` | array | all | Which properties to animate |

### States — Enter and Exit

```js
const layout = createLayout('.list', {
  duration: 400,
  ease: 'out(3)',
  enterFrom: {
    opacity: 0,
    scale: 0.5
  },
  leaveTo: {
    opacity: 0,
    scale: 0.5,
    x: -100
  }
});
```

| State | Description |
|-------|-------------|
| `enterFrom` | Initial state for new elements entering |
| `leaveTo` | Final state for elements being removed |
| `swapAt` | Transition state when swapping parents |

### Layout Methods

| Method | Description |
|--------|-------------|
| `record()` | Capture current positions |
| `animate()` | Animate from recorded to current |
| `update()` | Re-record without animation |
| `revert()` | Clean up layout observer |

### Usage Patterns

**Toggle CSS display:**
```js
layout.record();
element.style.display = element.style.display === 'none' ? 'block' : 'none';
layout.animate();
```

**Reorder items:**
```js
layout.record();
const sorted = [...items].sort((a, b) => a.dataset.order - b.dataset.order);
sorted.forEach(item => container.appendChild(item));
layout.animate();
```

**Filter items:**
```js
layout.record();
items.forEach(item => {
  item.style.display = item.matches(filter) ? 'block' : 'none';
});
layout.animate();
```

### Layout ID Attribute

Track elements across parent changes with `data-layout-id`:

```html
<div class="list-a"><div data-layout-id="item-1">Item</div></div>
<div class="list-b"></div>
```

```js
layout.record();
listB.appendChild(document.querySelector('[data-layout-id="item-1"]'));
layout.animate(); // Smoothly animates between parents
```

### Common Gotchas

- Set explicit width/height before layout animations to prevent flicker
- `position: relative` or `absolute` on children works best
- Layout animations affect all children — use `children` selector to limit scope

## createAnimatable()

Create reactive animated properties. Values animate smoothly when set.

```js
import { createAnimatable } from 'animejs';

const anim = createAnimatable('.cursor', {
  x: { unit: 'px', duration: 200, ease: 'out(3)' },
  y: { unit: 'px', duration: 200, ease: 'out(3)' },
  scale: { duration: 300, ease: 'out(4)' }
});
```

### Settings Per Property

| Setting | Type | Description |
|---------|------|-------------|
| `unit` | string | CSS unit (`'px'`, `'%'`, `'rem'`) |
| `duration` | number | Transition duration |
| `ease` | string | Transition easing |
| `modifier` | function | Transform value |

### Getters and Setters

```js
// Get current value
const currentX = anim.x();

// Set value — automatically animates
anim.x(200);
anim.y(150);
anim.scale(1.5);
```

### Cursor Follower

```js
const cursor = createAnimatable('.cursor-dot', {
  x: { unit: 'px', duration: 150, ease: 'out(3)' },
  y: { unit: 'px', duration: 150, ease: 'out(3)' }
});

document.addEventListener('mousemove', (e) => {
  cursor.x(e.clientX);
  cursor.y(e.clientY);
});
```

### Interactive Slider

```js
const slider = createAnimatable('.slider-value', {
  width: { unit: '%', duration: 300, ease: 'out(3)' }
});

rangeInput.addEventListener('input', (e) => {
  slider.width(e.target.value);
});
```

### Responsive Animation

```js
const panel = createAnimatable('.sidebar', {
  x: { unit: 'px', duration: 400, ease: 'out(4)' },
  opacity: { duration: 300 }
});

// Open
panel.x(0);
panel.opacity(1);

// Close
panel.x(-300);
panel.opacity(0);
```

### Methods

| Method | Description |
|--------|-------------|
| `revert()` | Remove all animated properties and clean up |
