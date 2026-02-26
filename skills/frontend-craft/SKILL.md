---
name: frontend-craft
description: |
  Expert frontend craft for building apps that make users go "wow, this is
  fast and easy." Covers micro-interactions, perceived performance, premium
  component patterns, visual polish, state choreography, and component
  architecture. Synthesizes Saffer (Microinteractions), Wathan/Schoger
  (Refactoring UI), Krug (Don't Make Me Think), Yablonski (Laws of UX),
  Nabors (Animation at Work), Tidwell (Designing Interfaces), plus
  production patterns from Linear, Vercel, and Notion.

  Trigger phrases: "micro-interaction", "make it feel fast", "loading state",
  "skeleton screen", "optimistic update", "framer motion", "animation",
  "command palette", "data table", "TanStack Table", "toast notification",
  "sonner", "cmdk", "shadcn", "UI polish", "wow factor", "delightful UI",
  "premium feel", "perceived performance", "empty state", "page transition",
  "error state", "form UX", "modal pattern", "visual polish", "spring animation"
---

# Frontend Craft

## Core Philosophy

1. **Speed is a feeling, not a metric** — Users judge speed by perceived
   responsiveness. Optimistic updates, skeleton screens, and instant feedback
   matter more than raw milliseconds.
2. **Every interaction deserves feedback** — Buttons press, toggles snap,
   lists stagger. Silent UI feels broken. Animated UI feels alive.
3. **Polish compounds** — One shadow system, one spacing scale, one motion
   language. Consistency across details creates the "premium" feeling.
4. **States are first-class UI** — Loading, empty, error, and success states
   are not afterthoughts. Design them with the same care as the happy path.
5. **Accessibility is not optional** — Reduced motion, focus management,
   keyboard navigation, screen readers. Premium means premium for everyone.

## Quick-Start: Make It Feel Fast

### Problem: "The app feels slow"

1. Add skeleton screens matching content layout for anything over 200ms.
   -> See `references/perceived-performance.md`
2. Implement optimistic updates for user-initiated mutations.
   -> See `references/perceived-performance.md`
3. Prefetch routes on hover with `router.prefetch(href)`.
   -> See `references/perceived-performance.md`

### Problem: "The UI feels dead"

1. Add `whileHover` scale 1.02 and `whileTap` scale 0.98 to buttons.
2. Use staggered entrance animations for lists (staggerChildren: 0.05).
3. Animate page transitions with `AnimatePresence mode="wait"`.
   -> See `references/micro-interactions.md`

### Problem: "I need a premium data table"

1. Use TanStack Table v8 (headless) with virtual scrolling for 100+ rows.
2. Add column resizing, faceted filtering, and inline editing.
3. Wrap in shadcn/ui DataTable component pattern.
   -> See `references/premium-components.md`

### Problem: "The design looks amateur"

1. Apply a 5-level shadow elevation system consistently.
2. Stick to 4px/8px spacing grid — no arbitrary values.
3. Use HSL-based design tokens with CSS custom properties.
   -> See `references/visual-polish.md`

## Decision Trees

### When to Animate

| Trigger | Animate? | Pattern |
|---------|----------|---------|
| User clicks/taps | Yes | Scale 0.98 + spring (400/30) |
| User hovers | Yes | Subtle lift + shadow increase |
| Content loads | Yes | Skeleton → fade-in with stagger |
| Page navigates | Yes | Fade + slide (150ms ease-out) |
| Error appears | Yes | Shake or red border pulse |
| Background data refresh | No | Silent update, no flash |
| Resize/reflow | No | Instant, no transition |

### Loading State Selection

| Wait Time | Pattern | Example |
|-----------|---------|---------|
| < 100ms | Nothing | Instant response |
| 100-300ms | Subtle spinner | Button loading state |
| 300ms-1s | Content placeholder | Inline skeleton |
| 1-3s | Full skeleton screen | Page-level loading |
| 3s+ | Progress indicator | File upload, export |

### Component Selection

| Need | Use | Library |
|------|-----|---------|
| Data display with sort/filter | TanStack Table | @tanstack/react-table |
| Global search / command menu | Command Palette | cmdk |
| User notifications | Toast | sonner |
| Form with validation | React Hook Form | react-hook-form + zod |
| Overlay requiring action | Dialog | @radix-ui/react-dialog |
| Contextual side panel | Sheet | @radix-ui/react-dialog (side) |
| Destructive confirmation | AlertDialog | @radix-ui/react-alert-dialog |
| Component variants | CVA | class-variance-authority |

### Visual Polish Priority

| Impact | Action | Effort |
|--------|--------|--------|
| Highest | Consistent spacing (4px grid) | Low |
| High | Shadow elevation system | Low |
| High | Focus-visible keyboard rings | Low |
| Medium | Skeleton loading states | Medium |
| Medium | Dark mode with smooth transition | Medium |
| Lower | Backdrop blur / glassmorphism | Low |
| Lower | Custom selection color | Trivial |

## The Premium Stack

```
Radix UI          → Accessible, unstyled primitives
  + shadcn/ui     → Styled component library (copy-paste)
  + CVA           → Type-safe variant system
  + Tailwind      → Utility CSS with design tokens
  + Framer Motion → Animation and gestures
  + TanStack      → Headless table, virtual scrolling
  + cmdk          → Command palette
  + Sonner        → Toast notifications
  + React Hook Form + Zod → Forms with schema validation
```

## Reference Files

| File | Contents |
|------|----------|
| `references/micro-interactions.md` | Framer Motion patterns, spring physics, gesture interactions, CSS transitions, timing, reduced motion |
| `references/perceived-performance.md` | Skeleton screens, optimistic updates, progressive loading, prefetch, SWR, loading thresholds |
| `references/premium-components.md` | TanStack Table, cmdk command palettes, React Hook Form + Zod, modals/sheets, Sonner toasts |
| `references/visual-polish.md` | Shadow systems, spacing scales, typography, gradients, backdrop blur, dark mode, focus states |
| `references/state-choreography.md` | Loading/error/empty/success states, page transitions, layout animations, skeleton reveals |
| `references/component-architecture.md` | shadcn/ui + Radix + CVA patterns, design tokens, variant systems, composition, accessibility |
