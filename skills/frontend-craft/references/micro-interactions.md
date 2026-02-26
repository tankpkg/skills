# Micro-Interactions and Animation

Sources: Saffer (Microinteractions), Nabors (Animation at Work), Framer Motion documentation

Covers: animation timing, spring physics, Framer Motion patterns, gesture interactions, CSS transitions, reduced motion accessibility.

## Animation Timing Principles

Animation in UI design should be functional, not just decorative. The primary goal is to provide feedback, guide focus, and maintain spatial relationships during state changes.

### The Doherty Threshold
Interactions must happen within 400ms to keep the user's attention. For high-performance "premium" feel, aim for sub-100ms response times for triggers (Feedback loop).

### Duration Guidelines
Standardize durations to maintain consistency across the application.

| Interaction Type | Duration | Easing/Transition |
|------------------|----------|-------------------|
| Hover/Tap Feedback | 100ms - 150ms | ease-out or spring |
| Small element entry | 200ms - 250ms | ease-out |
| Large element entry | 300ms - 400ms | ease-out |
| Exit animations | 150ms - 200ms | ease-in (Exit faster than Enter) |
| Page transitions | 400ms - 500ms | layout / smooth spring |

### Easing Functions
- **ease-out**: Use for elements entering the screen. They start fast and slow down, mimicking physical objects coming to a stop.
- **ease-in**: Use for elements leaving the screen. They start slow and accelerate as they exit.
- **ease-in-out**: Use for elements moving from one point on screen to another.
- **Linear**: Avoid for visual movement. Only use for property changes like opacity or color if duration is extremely short.

## Spring Physics Configuration

Spring physics provide a more natural, "physical" feel than duration-based easing. They allow for momentum and overshoot, which creates a sense of tactile weight.

| Config Name | Stiffness | Damping | Mass | Use Case |
|-------------|-----------|---------|------|----------|
| **Snappy** | 400 | 30 | 1 | Buttons, toggles, instant feedback |
| **Bouncy** | 300 | 12 | 1 | Playful UI, notifications, "pop" effects |
| **Smooth** | 200 | 20 | 1 | Dialogs, drawers, dropdowns |
| **Gentle** | 120 | 14 | 1 | Subtle fades, background shifts |
| **Stiff** | 600 | 45 | 1 | Dragging constraints, high-tension UI |

### Implementation Example (Framer Motion)
```tsx
const transition = {
  type: "spring",
  stiffness: 400,
  damping: 30,
  mass: 1
};

<motion.div animate={{ scale: 1 }} transition={transition} />
```

## Framer Motion Core Patterns

Framer Motion is the industry standard for complex React animations. Use these patterns for premium interaction design.

### Hover and Tap Gestures
Always provide immediate feedback for interactive elements.

```tsx
<motion.button
  whileHover={{ scale: 1.02, backgroundColor: "var(--hover-bg)" }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 30 }}
  className="btn-primary"
>
  Click Me
</motion.button>
```

### AnimatePresence and Exit Animations
Required for animating components as they are removed from the React tree. Use `mode="wait"` to ensure the exiting component finishes before the new one enters.

```tsx
import { AnimatePresence, motion } from "framer-motion";

const Modal = ({ isOpen }: { isOpen: boolean }) => (
  <AnimatePresence mode="wait">
    {isOpen && (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className="modal"
      >
        Content
      </motion.div>
    )}
  </AnimatePresence>
);
```

### Layout and LayoutId (Shared Elements)
The `layout` prop automatically animates changes in the bounding box. `layoutId` allows for shared element transitions between different components.

```tsx
// Shared underline for tabs
{tabs.map((tab) => (
  <button key={tab} onClick={() => setActive(tab)} style={{ position: "relative" }}>
    {tab}
    {active === tab && (
      <motion.div
        layoutId="underline"
        className="absolute bottom-0 h-1 bg-blue-500 w-full"
      />
    )}
  </button>
))}
```

### Staggered List Entrance
Use variants to orchestrate child animations.

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map(i => <motion.li key={i} variants={item} />)}
</motion.ul>
```

## Gesture Interactions

Gestures add a layer of direct manipulation that feels modern and responsive.

### Drag and Swipe-to-Dismiss
Essential for mobile-friendly or high-touch interfaces.

```tsx
<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 0 }}
  onDragEnd={(_, info) => {
    if (info.offset.x > 100) handleDismiss();
  }}
  whileDrag={{ scale: 1.05 }}
  className="swipeable-card"
>
  Drag right to dismiss
</motion.div>
```

### Scroll-Triggered Animations
Use `whileInView` for simple triggers and `useScroll` for complex parallax or progress bars.

```tsx
// Simple reveal
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}
/>

// Scroll progress
const { scrollYProgress } = useScroll();
const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });

<motion.div className="progress-bar" style={{ scaleX }} />
```

## Premium Component Recipes

Applying micro-interaction principles to common UI components for a polished feel.

### Animated Toggle (Switch)
A standard toggle should feel tactile. Use `layout` for the internal handle.

```tsx
const [isOn, setIsOn] = useState(false);

return (
  <div 
    className={`w-12 h-6 rounded-full p-1 cursor-pointer flex ${isOn ? 'bg-green-500' : 'bg-gray-300'}`}
    onClick={() => setIsOn(!isOn)}
  >
    <motion.div
      layout
      transition={{ type: "spring", stiffness: 700, damping: 30 }}
      className="w-4 h-4 bg-white rounded-full shadow-md"
      style={{ alignSelf: 'center', marginLeft: isOn ? 'auto' : '0' }}
    />
  </div>
);
```

### Navigation Drawer
Drawer entry should include an overlay fade and a transform.

```tsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      <motion.aside
        initial={{ x: "-100%" }}
        animate={{ x: 0 }}
        exit={{ x: "-100%" }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="fixed left-0 top-0 bottom-0 w-64 bg-white z-50 p-6"
      >
        <nav>...</nav>
      </motion.aside>
    </>
  )}
</AnimatePresence>
```

### Form Input Polish: Shake on Error
Visual feedback for invalid data should be immediate and clear.

```tsx
const controls = useAnimation();

const handleError = async () => {
  await controls.start({
    x: [-10, 10, -10, 10, 0],
    transition: { duration: 0.4 }
  });
};

<motion.input
  animate={controls}
  className="border p-2 rounded"
  placeholder="Enter code..."
/>
```

### Button State Transitions (Loading to Success)
Maintain the button's spatial presence while changing its internal state.

```tsx
const [status, setStatus] = useState<'idle' | 'loading' | 'success'>('idle');

return (
  <button className="relative overflow-hidden px-6 py-2 bg-indigo-600 text-white rounded-lg">
    <AnimatePresence mode="wait">
      {status === 'idle' && (
        <motion.span key="idle" initial={{ y: 20 }} animate={{ y: 0 }} exit={{ y: -20 }}>
          Submit
        </motion.span>
      )}
      {status === 'loading' && (
        <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <Spinner />
        </motion.div>
      )}
      {status === 'success' && (
        <motion.span key="success" initial={{ scale: 0 }} animate={{ scale: 1 }}>
          <CheckIcon />
        </motion.span>
      )}
    </AnimatePresence>
  </button>
);
```

## CSS Transition Patterns

For simple interactions where Framer Motion is overkill, use CSS transitions with Tailwind utility patterns.

### The "Subtle Hover" Pattern
Combine scale, shadow, and border transitions for cards.

```html
<div class="transition-all duration-200 ease-out hover:-translate-y-1 hover:shadow-lg hover:border-slate-300 border border-transparent rounded-xl p-4 cursor-pointer">
  <h3 class="font-medium">Premium Card</h3>
  <p class="text-slate-500 text-sm">Hover to see the subtle lift and shadow shift.</p>
</div>
```

### Skeleton Shimmer Effect
Use a linear gradient with a repeated keyframe animation.

```css
@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.skeleton::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transform: translateX(-100%);
  background-image: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0,
    rgba(255, 255, 255, 0.2) 20%,
    rgba(255, 255, 255, 0.5) 60%,
    rgba(255, 255, 255, 0)
  );
  animation: shimmer 2s infinite;
}
```

## Reduced Motion Accessibility

Users may have "Reduce Motion" enabled in their OS. Respecting this is a legal requirement (WCAG) and a UX imperative.

### The useReducedMotion Hook
In Framer Motion, use the provided hook to conditionally disable or simplify animations.

```tsx
import { useReducedMotion } from "framer-motion";

function MyComponent() {
  const shouldReduceMotion = useReducedMotion();

  const animation = shouldReduceMotion 
    ? { opacity: 1 } // No movement
    : { opacity: 1, y: 0, scale: 1 };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={animation}
    />
  );
}
```

### CSS Media Query
For pure CSS transitions, wrap animations in the `prefers-reduced-motion` query.

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Anti-Patterns

Avoid these common mistakes to prevent "motion sickness" or a cheap-feeling UI.

| Anti-Pattern | Reason | Correction |
|--------------|--------|------------|
| **Over-animating** | Too many moving parts cause cognitive overload. | Only animate the primary focus or state change. |
| **Linear movement** | Feels robotic and unnatural. | Always use ease-out or spring physics for motion. |
| **Slow exits** | Users want to move fast; waiting for a modal to fade out is frustrating. | Make exit animations 50% faster than entry animations. |
| **Layout thrashing** | Animating properties like `height`, `top`, or `margin` triggers reflow. | Use `transform` (scale, translate) and `opacity` only. |
| **Excessive bounce** | High-oscillation springs feel unprofessional and distracting. | Keep damping values above 20 for standard UI elements. |
| **Animation loops** | Constant movement drains battery and distracts. | Use loops only for loading states or high-priority alerts. |

### Implementation Check: Performance
Always add `will-change: transform` or `will-change: opacity` to elements with complex or long-running animations to ensure GPU acceleration.

```tsx
<motion.div 
  style={{ willChange: "transform" }}
  animate={{ rotate: 360 }}
/>
```

### Hierarchy of Motion
1. **Feedback**: Primary importance (button clicks, toggle shifts).
2. **Context**: Explaining where things go (shared element transitions).
3. **Focus**: Directing eye to new info (notifications, entry animations).
4. **Delight**: Secondary polish (subtle parallax, playful icons).
