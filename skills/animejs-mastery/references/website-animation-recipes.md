# Website Animation Recipes

Sources: Anime.js v4 official documentation, production website patterns

Copy-paste-ready animation recipes for common website scenarios. All use
anime.js v4 API. Combine recipes for complex page animations.

## Hero Section Animations

### Staggered Text Reveal

```js
import { animate, stagger, splitText } from 'animejs';

const { chars } = splitText('.hero-title', { chars: true });
animate(chars, {
  opacity: [0, 1],
  y: [40, 0],
  delay: stagger(25),
  duration: 600,
  ease: 'out(4)'
});
```

### Hero Headline + Subtitle + CTA Sequence

```js
import { createTimeline } from 'animejs';

const tl = createTimeline({ defaults: { ease: 'out(3)' } });
tl.add('h1', { opacity: [0, 1], y: [40, 0], duration: 800 })
  .add('.subtitle', { opacity: [0, 1], y: [20, 0], duration: 600 }, '-=500')
  .add('.cta-button', { opacity: [0, 1], scale: [0.8, 1], duration: 500 }, '-=300');
```

### Hero Image Scale-In

```js
animate('.hero-image', {
  scale: [1.1, 1],
  opacity: [0, 1],
  duration: 1200,
  ease: 'out(4)'
});
```

### Background Gradient Shift

```js
const bg = { hue: 0 };
animate(bg, {
  hue: 360,
  duration: 10000,
  loop: true,
  ease: 'linear',
  onUpdate: () => {
    document.querySelector('.hero').style.background =
      `linear-gradient(135deg, hsl(${bg.hue}, 70%, 60%), hsl(${bg.hue + 60}, 70%, 40%))`;
  }
});
```

## Scroll-Triggered Reveals

### Fade-Up Cards

```js
import { animate, stagger, onScroll } from 'animejs';

animate('.card', {
  opacity: [0, 1],
  y: [60, 0],
  delay: stagger(100),
  duration: 700,
  ease: 'out(3)',
  autoplay: onScroll({ target: '.cards-section', repeat: false })
});
```

### Staggered Grid Reveal from Center

```js
animate('.grid-item', {
  opacity: [0, 1],
  scale: [0.6, 1],
  delay: stagger(60, { grid: [4, 3], from: 'center' }),
  duration: 500,
  ease: 'out(3)',
  autoplay: onScroll({ target: '.grid-section' })
});
```

### Animated Counter

```js
const counter = { value: 0 };
const el = document.querySelector('.stat-number');

animate(counter, {
  value: 12500,
  duration: 2000,
  ease: 'out(3)',
  onUpdate: () => {
    el.textContent = Math.round(counter.value).toLocaleString();
  },
  autoplay: onScroll({ target: el, repeat: false })
});
```

### Parallax Background

```js
animate('.parallax-layer', {
  y: [0, -150],
  ease: 'linear',
  autoplay: onScroll({
    target: '.parallax-section',
    enter: 'top bottom',
    leave: 'bottom top',
    sync: 'smooth'
  })
});
```

## Navigation and UI

### Hamburger to X Morph

```js
import { createTimeline } from 'animejs';

function openMenu() {
  const tl = createTimeline({ defaults: { duration: 300, ease: 'out(3)' } });
  tl.add('.line-top', { rotate: 45, y: 8 })
    .add('.line-mid', { opacity: 0, duration: 100 }, 0)
    .add('.line-bot', { rotate: -45, y: -8 }, 0);
  return tl;
}
```

### Mobile Menu Slide-In

```js
import { createTimeline, stagger, spring } from 'animejs';

function showMenu() {
  const tl = createTimeline({ defaults: { ease: 'out(4)' } });
  tl.add('.mobile-menu', { x: ['-100%', '0%'], duration: 400 })
    .add('.menu-link', {
      opacity: [0, 1],
      x: [-30, 0],
      delay: stagger(60),
      duration: 400
    }, '-=200');
  return tl;
}
```

### Tab Content Switch

```js
import { animate } from 'animejs';

async function switchTab(newContent) {
  await animate('.tab-content', { opacity: 0, y: -10, duration: 200 }).then();
  // Swap content here
  document.querySelector('.tab-content').innerHTML = newContent;
  animate('.tab-content', { opacity: [0, 1], y: [10, 0], duration: 300, ease: 'out(3)' });
}
```

### Tooltip Entrance

```js
animate('.tooltip', {
  opacity: [0, 1],
  scale: [0.8, 1],
  y: [8, 0],
  duration: 200,
  ease: 'out(3)'
});
```

## Micro-Interactions

### Button Hover Scale

```js
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('mouseenter', () => {
    animate(btn, { scale: 1.05, duration: 200, ease: 'out(3)' });
  });
  btn.addEventListener('mouseleave', () => {
    animate(btn, { scale: 1, duration: 300, ease: 'out(3)' });
  });
});
```

### Card Hover Lift

```js
card.addEventListener('mouseenter', () => {
  animate(card, {
    y: -8,
    boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
    duration: 300,
    ease: 'out(3)'
  });
});
```

### Like Heart Animation

```js
import { animate, spring } from 'animejs';

function animateLike(el) {
  animate(el, {
    scale: [1, 1.4, 1],
    duration: 500,
    ease: spring({ bounce: 0.6 })
  });
}
```

### Loading Spinner

```js
animate('.spinner', {
  rotate: '1turn',
  duration: 800,
  loop: true,
  ease: 'linear'
});
```

### Success Checkmark Draw

```js
import { animate, svg } from 'animejs';

const drawable = svg.createDrawable('.checkmark-path');
animate(drawable, { draw: '0 1', duration: 600, ease: 'out(3)' });
```

### Notification Bell Shake

```js
animate('.bell-icon', {
  rotate: [0, 15, -15, 10, -10, 5, 0],
  duration: 600,
  ease: 'out(3)'
});
```

### Ripple Effect on Click

```js
button.addEventListener('click', (e) => {
  const ripple = document.createElement('span');
  ripple.classList.add('ripple');
  button.appendChild(ripple);
  animate(ripple, {
    scale: [0, 4],
    opacity: [0.5, 0],
    duration: 600,
    ease: 'out(3)',
    onComplete: () => ripple.remove()
  });
});
```

## Page Transitions

### Fade Cross-Transition

```js
async function transitionTo(newPage) {
  await animate('.page-content', {
    opacity: 0,
    y: -20,
    duration: 300,
    ease: 'in(3)'
  }).then();

  // Load new content
  document.querySelector('.page-content').innerHTML = newPage;

  animate('.page-content', {
    opacity: [0, 1],
    y: [20, 0],
    duration: 400,
    ease: 'out(3)'
  });
}
```

### Slide Transition

```js
async function slideTransition(direction = 'left') {
  const offset = direction === 'left' ? -100 : 100;
  await animate('.current-page', {
    x: `${offset}%`,
    opacity: 0,
    duration: 400,
    ease: 'in(3)'
  }).then();

  // Swap content, then:
  animate('.current-page', {
    x: [`${-offset}%`, '0%'],
    opacity: [0, 1],
    duration: 400,
    ease: 'out(3)'
  });
}
```

## Data and Content

### Progress Bar Fill

```js
animate('.progress-fill', {
  width: ['0%', '75%'],
  duration: 1500,
  ease: 'out(3)',
  autoplay: onScroll({ target: '.progress-bar', repeat: false })
});
```

### Chart Bar Animation

```js
animate('.chart-bar', {
  height: (el) => el.dataset.value + '%',
  delay: stagger(80),
  duration: 800,
  ease: 'out(4)',
  autoplay: onScroll({ target: '.chart' })
});
```

### Typewriter Effect

```js
const text = 'Hello, World!';
const el = document.querySelector('.typewriter');
const counter = { i: 0 };

animate(counter, {
  i: text.length,
  duration: text.length * 80,
  ease: 'linear',
  onUpdate: () => {
    el.textContent = text.slice(0, Math.round(counter.i));
  }
});
```

### List Item Enter with Layout

```js
import { createLayout } from 'animejs';

const layout = createLayout('.todo-list', {
  duration: 400,
  ease: 'out(3)',
  enterFrom: { opacity: 0, scale: 0.8, y: -20 },
  leaveTo: { opacity: 0, scale: 0.8, x: -100 }
});

function addItem(html) {
  layout.record();
  list.insertAdjacentHTML('beforeend', html);
  layout.animate();
}

function removeItem(el) {
  layout.record();
  el.remove();
  layout.animate();
}
```

## SVG Animations for Web

### Logo Line Drawing on Load

```js
import { createTimeline, svg } from 'animejs';

const tl = createTimeline();
document.querySelectorAll('#logo path').forEach((path, i) => {
  const drawable = svg.createDrawable(path);
  tl.add(drawable, { draw: '0 1', duration: 800, ease: 'inOut(3)' }, i * 100);
});
tl.add('#logo', { fillOpacity: [0, 1], duration: 600 }, '-=200');
```

### Icon State Toggle

```js
import { animate, svg } from 'animejs';

let isOpen = false;
function toggleIcon() {
  const target = isOpen ? '#icon-closed' : '#icon-open';
  animate('#morphable-icon', { d: svg.morphTo(target), duration: 400, ease: 'out(3)' });
  isOpen = !isOpen;
}
```

## CMS / Website Builder Integration

### Animate Dynamic HTML (works with any CMS)

```js
// After CMS renders content, animate visible elements
function animateSection(sectionEl) {
  animate(sectionEl.querySelectorAll('[data-animate]'), {
    opacity: [0, 1],
    y: [30, 0],
    delay: stagger(80),
    duration: 600,
    ease: 'out(3)'
  });
}
```

### SPA Cleanup Pattern

```js
import { createScope, animate } from 'animejs';

let pageScope;
function initPage(rootEl) {
  pageScope = createScope({ root: rootEl });
  pageScope.add(() => {
    animate('.hero', { opacity: [0, 1], duration: 800 });
    animate('.content', { y: [30, 0], delay: 200, duration: 600 });
  });
}
function destroyPage() { if (pageScope) pageScope.revert(); }

// Router hooks: destroyPage() on leave, initPage() on enter
```
