# State Choreography

Sources: Saffer (Microinteractions), Tidwell (Designing Interfaces), Linear/Vercel/Notion UX patterns
Covers: loading-to-content transitions, error states, empty states, success feedback, page transitions, layout animations, skeleton-to-content reveals.

## The Five UI States
Every interface component must account for the five fundamental states to ensure a continuous and graceful user experience.

| State | Pattern | UX Goal |
|-------|---------|---------|
| **Loading** | Skeletons, progress bars, spinners | Maintain layout stability and reduce perceived wait. |
| **Content** | The "ideal" state with data | Clear hierarchy and functional interactive elements. |
| **Empty** | Illustration, guidance, primary CTA | Explain why there is no data and how to create it. |
| **Error** | Inline alerts, retry buttons, error boundaries | Provide clear recovery paths without dead-ending. |
| **Success** | Checkmarks, confetti, feedback toasts | Confirm action completion and reinforce positive behavior. |

## Skeleton-to-Content Reveal
The transition from a skeleton placeholder to actual content must be fluid to avoid jarring layout shifts. Use a combined opacity and scale transition.

### Staggered Reveal Pattern
When a list of items loads, reveal them one by one using a stagger effect to guide the eye.

```tsx
import { motion, AnimatePresence } from 'framer-motion';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 10, scale: 0.98 },
  show: { opacity: 1, y: 0, scale: 1 },
};

export const ContentReveal = ({ isLoading, data }: { isLoading: boolean, data: any[] }) => {
  return (
    <AnimatePresence mode="wait">
      {isLoading ? (
        <motion.div
          key="skeleton"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 0.98 }}
          transition={{ duration: 0.2 }}
        >
          {/* Skeleton placeholders matching content layout */}
          <SkeletonList count={3} />
        </motion.div>
      ) : (
        <motion.div
          key="content"
          variants={container}
          initial="hidden"
          animate="show"
        >
          {data.map((entry) => (
            <motion.div key={entry.id} variants={item}>
              <Card entry={entry} />
            </motion.div>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
};
```

### Matching Layout
Ensure the skeleton precisely matches the final layout's dimensions and typography to prevent "jumping" when the real data arrives.

## Error State Patterns
Errors should not be destructive to the user's workflow. Provide context and a clear way back.

### Inline Errors and Retry Logic
For data fetching errors, include an exponential backoff retry mechanism and a clear "Retry" action.

```tsx
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorState = ({ error, onRetry }: { error: string, onRetry: () => void }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 border border-red-100 bg-red-50 rounded-lg">
      <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
      <h3 className="text-lg font-semibold text-red-900">Failed to load data</h3>
      <p className="text-sm text-red-700 text-center mb-6 max-w-xs">
        {error || "An unexpected error occurred. Please try again."}
      </p>
      <button
        onClick={onRetry}
        className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
      >
        <RefreshCw className="w-4 h-4 mr-2" />
        Retry Now
      </button>
    </div>
  );
};
```

### Global Error Boundaries
Use Error Boundaries for catastrophic failures to prevent the entire application from crashing. Render a fallback UI that allows the user to report the bug or return to the dashboard.

## Empty State Patterns
An empty state is an opportunity to onboard or re-engage users.

### Contentful Empty States
Avoid "No results found." Instead, provide guidance based on why the state is empty.

| Type | Content | Action |
|------|---------|--------|
| **First-Use** | Educational copy about the feature. | "Create your first [Item]" |
| **No Results** | Filter summary + suggestion to broaden search. | "Clear all filters" |
| **Cleared** | Congratulatory message (e.g., Inbox Zero). | "View archived" |

### Contextual Guidance Example
```tsx
export const EmptyState = ({ type }: { type: 'initial' | 'search' }) => {
  const content = {
    initial: {
      title: "No projects yet",
      description: "Get started by creating your first project to organize your tasks.",
      button: "Create Project",
    },
    search: {
      title: "No matches found",
      description: "Try adjusting your filters or search terms to find what you're looking for.",
      button: "Clear Search",
    },
  };

  const { title, description, button } = content[type];

  return (
    <div className="flex flex-col items-center py-12 px-6 text-center">
      <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
        <PackageOpen className="text-slate-400 w-10 h-10" />
      </div>
      <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-500 mb-6 max-w-sm">{description}</p>
      <button className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-full shadow-lg hover:shadow-xl transition-all active:scale-95">
        {button}
      </button>
    </div>
  );
};
```

## Success Feedback
Reinforce user actions with immediate, high-quality feedback.

### The Feedback Loop
1. **Trigger:** User clicks "Submit".
2. **Action:** Loading state (spinner inside button).
3. **Response:** Success animation (checkmark) and toast notification.
4. **Transition:** Redirect or clear form.

### Checkmark Animation
A crisp SVG checkmark animation is more satisfying than plain text.

```tsx
const checkVariants = {
  initial: { pathLength: 0, opacity: 0 },
  animate: { pathLength: 1, opacity: 1, transition: { duration: 0.4, ease: "easeInOut" } }
};

export const SuccessIcon = () => (
  <svg viewBox="0 0 52 52" className="w-12 h-12 text-green-500">
    <motion.path
      fill="none"
      strokeWidth="4"
      stroke="currentColor"
      d="M14 27l7.5 7.5L38 18"
      strokeLinecap="round"
      strokeLinejoin="round"
      variants={checkVariants}
      initial="initial"
      animate="animate"
    />
  </svg>
);
```

## Page Transitions
Transitions between pages should feel native. Use `AnimatePresence` with `mode="wait"` to ensure the outgoing page exits before the new one enters.

### Fade and Slide Pattern
```tsx
const pageVariants = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 10 },
};

export const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <motion.main
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    transition={{ type: "spring", stiffness: 260, damping: 20 }}
  >
    {children}
  </motion.main>
);
```

## Layout Animations
Framer Motion's `layout` prop automatically handles the transition between different DOM positions.

### Smooth Reflow on Filter/Sort
When reordering a list, use `layout` to animate items into their new positions instead of them snapping instantly.

```tsx
export const AnimatedList = ({ items }: { items: any[] }) => (
  <ul className="space-y-4">
    {items.map((item) => (
      <motion.li
        key={item.id}
        layout
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <ItemContent data={item} />
      </motion.li>
    ))}
  </ul>
);
```

### Shared Layout Transitions (layoutId)
Use `layoutId` to morph an element from one state to another (e.g., a card expanding into a full-page modal).

```tsx
// Grid Item
<motion.div layoutId={`card-${id}`} onClick={() => setSelected(id)}>
  <Thumbnail />
</motion.div>

// Full-screen View
<AnimatePresence>
  {selected && (
    <motion.div layoutId={`card-${selected}`} className="fixed inset-0 z-50">
      <LargeContent />
    </motion.div>
  )}
</AnimatePresence>
```

## Orchestration Patterns
Coordinate multiple animations to create a cohesive sequence.

### Parent-Child Coordination
Use the `variants` system to propagate animation states from parents to children.

### Exit Before Enter
Always ensure that context-switching animations (like tabs or step-based forms) follow the "Exit before Enter" rule to prevent overlapping content during the transition.

```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={activeTab}
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
  >
    {tabContent[activeTab]}
  </motion.div>
</AnimatePresence>
```

## Anti-Patterns
Avoid these common choreography mistakes that degrade the user experience.

- **Jarring State Switches:** Flipping from a loading spinner to content without any transition (fade/scale).
- **Missing Empty States:** Leaving a blank white screen when no data exists, confusing the user about whether the app is broken or just empty.
- **Dead-End Errors:** Showing an error message without a "Retry" or "Go Back" action.
- **Over-Animating:** Adding 500ms+ transitions to every minor interaction, making the app feel slow and sluggish.
- **Unstable Skeletons:** Skeletons that shift significantly when the content loads (e.g., image loading after the text skeleton has already disappeared).
- **Layout Snap:** Elements jumping to new positions when items are added or removed from a list without a `layout` animation.
- **Competing Toasts:** Bombarding the user with multiple success/info toasts that obscure critical UI elements.
- **Infinite Spinners:** Using a spinner for long-running processes without providing progress updates or a fallback.
