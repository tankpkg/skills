# Perceived Performance

Sources: Krug (Don't Make Me Think), Yablonski (Laws of UX), React/Next.js documentation

Covers: skeleton screens, optimistic updates, progressive image loading, prefetch strategies, stale-while-revalidate, loading timing thresholds.

Perceived performance is the user's subjective experience of a system's speed and responsiveness. It is often more critical than actual technical performance metrics (like Time to First Byte) because it directly impacts user frustration, cognitive load, and trust.

## Response Time Thresholds

Human perception of time follows predictable patterns. Designing for these thresholds ensures that the interface feels "live" even when background processes are slow.

| Duration | User Perception | Required UI Action |
|----------|-----------------|--------------------|
| < 100ms  | Instant         | No loading state needed. Provide immediate visual feedback (e.g., button press state). |
| 100-300ms| Sluggish        | Subtle animation or transition. A loading spinner here often feels like "noise." |
| 300-1000ms| Waiting         | Use a loading indicator or skeleton screen. Must respect the Doherty Threshold. |
| > 1000ms | Task Interrupted| Full skeleton screen or progress bar. Provide status updates or estimated time. |
| > 10s    | Abandonment     | Process must be asynchronous or backgrounded. Notify user upon completion. |

### The Doherty Threshold
The Doherty Threshold states that computer-human interaction is most productive when both parties respond to each other at a pace of less than 400ms. If the response takes longer, users lose focus. Providing an immediate visual acknowledgment (even a skeleton) keeps the user engaged within this window.

## Skeleton Screens

Skeleton screens (ghost elements) provide a mockup of the content that is currently loading. They reduce the perceived wait time by focusing the user's attention on the progress being made rather than the fact that they are waiting.

### Implementation Guidelines
1. **Match Layout Exactly**: The skeleton should mirror the final content's geometry (height, width, border-radius).
2. **Synchronized Shimmer**: Use a CSS linear gradient animation moving from left to right. Ensure all skeletons in a list share the same animation timing to avoid visual chaos.
3. **Fade-in Content**: Once data arrives, cross-fade the skeleton to the actual content using a 200-300ms transition.

### Synchronized vs. Independent Skeletons
When rendering a list of items, avoid "popcorning"—where items appear one by one at different times. This creates visual noise.
- **Synchronized**: Wait for all primary data to load before revealing the entire section.
- **Progressive Disclosure**: Reveal high-priority content (e.g., hero text) first, then lower-priority skeletons (e.g., recommended products).

### Shimmer Implementation (Tailwind/CSS)
```tsx
const SkeletonItem = () => (
  <div className="relative overflow-hidden rounded-md bg-slate-200 p-4">
    <div className="space-y-3">
      <div className="h-4 w-3/4 rounded bg-slate-300" />
      <div className="h-4 w-1/2 rounded bg-slate-300" />
    </div>
    {/* Shimmer Effect */}
    <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
  </div>
);

// tailwind.config.js
// extend: {
//   keyframes: {
//     shimmer: {
//       '100%': { transform: 'translateX(100%)' },
//     },
//   },
// }
```

## Optimistic Updates

Optimistic updates assume a successful server response and update the UI immediately. This pattern is essential for high-frequency actions like "Liking," "Saving," or "Reordering."

### React 19 useOptimistic
The `useOptimistic` hook allows you to show a different state while an async action is in progress.

```tsx
import { useOptimistic } from 'react';

function LikeButton({ initialLikes, likeAction }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (state, newLikeCount: number) => newLikeCount
  );

  const handleLike = async () => {
    addOptimisticLike(optimisticLikes + 1);
    await likeAction(); // Server call
  };

  return (
    <button onClick={handleLike}>
      Likes: {optimisticLikes}
    </button>
  );
}
```

### Complex State & Conflict Resolution
When multiple optimistic updates occur simultaneously (e.g., a user quickly toggling a switch multiple times), the UI must stay consistent.
- **Last Write Wins**: Ensure that the final UI state reflects the last user action, regardless of server response order.
- **Debouncing**: For high-frequency actions like text input or sliders, debounce the server call while keeping the UI local and instant.

### TanStack Query (onMutate)
For complex state (like adding an item to a list), use the `onMutate` pattern to update the cache and provide a rollback mechanism on failure.

```tsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['todos'] });
    
    // Snapshot the previous value
    const previousTodos = queryClient.getQueryData(['todos']);
    
    // Optimistically update to the new value
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo]);
    
    // Return context with snapshot for rollback
    return { previousTodos };
  },
  onError: (err, newTodo, context) => {
    // Rollback to previous state
    queryClient.setQueryData(['todos'], context.previousTodos);
  },
  onSettled: () => {
    // Always refetch to sync with server
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

## Resource Hints and Connectivity

Reducing the actual time to fetch resources indirectly improves perceived performance by starting the work earlier.

### Preconnect and DNS-Prefetch
Use these in the `<head>` for critical third-party domains (e.g., font providers, CDNs, API endpoints).

```html
<!-- Establish connection early -->
<link rel="preconnect" href="https://api.example.com" />
<link rel="dns-prefetch" href="https://api.example.com" />
```

### Adaptive Loading Strategies
Adjust the interface based on the user's connection quality using the Network Information API.
- **Slow 2G/3G**: Disable video autoplay, serve low-res images, and use basic spinners instead of complex skeletons.
- **Fast 4G/WiFi**: Enable high-res assets, prefetch aggressively, and use complex transitions.

```javascript
if (navigator.connection && navigator.connection.saveData) {
  // Use "Lite" version of the UI
}
```

## Progressive Image Loading

Large images are the primary cause of layout shift and perceived sluggishness. Use placeholders to preserve layout and provide visual continuity.

### Next.js Image Component
Next.js provides built-in support for "blur-up" placeholders.

```tsx
import Image from 'next/image';

export const ProductCard = ({ src, blurDataURL }) => (
  <Image
    src={src}
    alt="Product"
    width={400}
    height={300}
    placeholder="blur"
    blurDataURL={blurDataURL} // 10px base64 encoded image
    className="rounded-lg transition-opacity duration-500"
  />
);
```

### Custom LQIP (Low Quality Image Placeholder)
If not using Next.js Image, implement a custom wrapper that switches from a low-res blurred background to the full image.

```tsx
const ProgressiveImage = ({ lowResSrc, highResSrc, alt }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div className="relative overflow-hidden">
      <img
        src={lowResSrc}
        alt={alt}
        className="absolute inset-0 h-full w-full scale-110 blur-xl filter"
      />
      <img
        src={highResSrc}
        alt={alt}
        onLoad={() => setIsLoaded(true)}
        className={`relative h-full w-full transition-opacity duration-700 ${
          isLoaded ? 'opacity-100' : 'opacity-0'
        }`}
      />
    </div>
  );
};
```

## Instant Navigation

Navigation should feel like switching tabs, not loading a new document. Predictive prefetching moves data fetching from "on click" to "on intent."

### Prefetch on Hover
Start fetching resources as soon as the user hovers over a link, as there is typically a 200-300ms gap between hover and click.

```tsx
import { useRouter } from 'next/router';

const NavLink = ({ href, children }) => {
  const router = useRouter();

  const handleMouseEnter = () => {
    router.prefetch(href);
  };

  return (
    <Link href={href} onMouseEnter={handleMouseEnter}>
      {children}
    </Link>
  );
};
```

### Next.js Link Strategies
Next.js prefetches visible links in the viewport by default. However, for large sites, you can fine-tune this:
- `prefetch={false}`: Disables automatic viewport prefetching.
- `prefetch={true}`: Forces prefetching even for dynamic routes.

### Handling Prefetch Failures
Prefetching is a hint, not a guarantee. Ensure that if a prefetch fails, the user is not blocked.
- **Fail Silently**: If prefetching a route fails, the actual navigation should still attempt to fetch data normally.
- **Retry Logic**: Implement exponential backoff for critical resource prefetching (e.g., critical JS chunks).

## The Progress Bar Principle

For operations that take longer than 2 seconds, a progress bar provides more certainty than a spinner.

### Non-Linear Progress
Users perceive time differently based on the "speed" of the progress bar.
- **Fast Start**: Start the progress bar quickly (e.g., jump to 30% in 500ms). This gives the user immediate confirmation that the process has begun.
- **Slow End**: Slow down as it nears 90% if the task is still running. Never let a progress bar stop completely; keep a slow "creep" moving to indicate the system hasn't crashed.
- **Artificial Delay**: Ironically, if a task is "too fast" (e.g., 50ms), a progress bar that flashes instantly can be jarring. In these rare cases, adding a minimum display time (e.g., 500ms) can actually feel more stable to the user.

## Navigation Feedback Loops

Every user interaction should trigger a feedback loop within 100ms.

### Interaction States
- **Intent**: User hovers or focuses (Trigger prefetch).
- **Execution**: User clicks (Immediate visual change: button state, loading bar start).
- **In-Progress**: Waiting for server (Skeleton screen, progress indicator).
- **Completion**: Success or failure state (Content swap, toast notification).

### Avoiding "Zombie" Clicks
If a button click triggers a slow navigation, users often click it again, thinking the first click didn't register.
- **Solution**: Disable the button or show a "Loading" state inside it immediately upon the first click.

## Stale-While-Revalidate (SWR)

SWR allows the UI to show "old" data immediately while fetching fresh data in the background. This eliminates loading states entirely for previously visited content.

```tsx
// Pattern for instant data
const { data, isValidating } = useSWR('/api/user', fetcher, {
  revalidateOnFocus: false,
  revalidateIfStale: true,
});

return (
  <div>
    {/* Always show data if available, even if stale */}
    <h1>{data?.name || <Skeleton />}</h1>
    {/* Subtle indicator if background update is happening */}
    {isValidating && <small className="opacity-50">Syncing...</small>}
  </div>
);
```

### Background Refresh Management
- **Polling**: Use `refreshInterval` for real-time data (e.g., stock prices).
- **Focus Revalidation**: Re-fetch data when the user returns to the tab to ensure they aren't looking at very old data.
- **Mutation Sync**: After an optimistic update, trigger a revalidation to ensure the UI matches the truth on the server.

## Loading State Decision Tree

Use the following logic to determine which loading pattern to implement based on the context and expected duration.

1. **Is the operation triggered by a user action (e.g., Save button)?**
   - **Yes**: Use **Optimistic Update**. If it takes >1s, add a small spinner inside the button.
   - **No (Page load)**: Proceed to step 2.

2. **Is the layout of the incoming data predictable?**
   - **Yes**: Use **Skeleton Screen**.
   - **No**: Use a **Progress Bar** (top of page) or a centered **Spinner**.

3. **Is the data likely to change frequently?**
   - **Yes**: Use **SWR** (show stale data immediately).
   - **No**: Use a permanent **Skeleton** until data arrives.

4. **Is the operation critical for navigation?**
   - **Yes**: Use **Instant Navigation** (prefetching).
   - **No**: **Lazy Load** with a placeholder.

| Pattern | Best For | Cognitive Load |
|---------|----------|----------------|
| Skeleton| Page Loads, List Items | Low (maintains layout) |
| Spinner | Buttons, Small Widgets | Medium (indicates blockage) |
| Progress| Large File Uploads | Low (provides certainty) |
| Blur-up | Images, Galleries | Low (visual continuity) |

## Anti-Patterns

Avoid these common mistakes that increase the user's perception of "waiting."

### 1. Full-Page Spinners
Blocking the entire screen with a spinner for more than 500ms creates a "wall" that interrupts the user's flow. Always prefer partial loading states or skeletons.

### 2. Layout Thrashing (Layout Shift)
Never inject content without reserved space. If an image or text block pops in and moves other elements, the user feels the interface is unstable.
- **Fix**: Define fixed heights or aspect ratios for containers before content arrives.

### 3. Waterfall Data Fetching
Fetching data sequentially (Component A finishes, then B starts) causes a "stuttering" loading experience.
- **Fix**: Use Parallel Data Fetching or pre-fetch data at the route level.

### 4. Excessive Optimism
Optimistically updating UI for high-latency or high-failure operations (e.g., complex financial transactions) can lead to jarring "jump-back" rollbacks.
- **Fix**: Use a loading state for high-stakes actions.

### 5. Flash of Invisible Text (FOIT)
Hiding text until the custom font loads.
- **Fix**: Use `font-display: swap` to show a system font immediately, then swap to the brand font.

### 6. The "Dead" Button
A button that doesn't change state when clicked because the operation is fast (~150ms).
- **Fix**: Always provide an immediate active/pressed state, even if the result is nearly instant.

## Perceived Timing Guidelines

Follow these "Golden Rules" of interface timing to maintain a premium feel:

- **Input Feedback**: Sub-50ms (Button down/up, hover).
- **Page Transitions**: 200-400ms. Anything faster feels "broken," anything slower feels "heavy."
- **Scroll Response**: Instant (Synchronous).
- **Skeleton Duration**: Ideally visible for 500-1500ms. If < 300ms, the flash is distracting.
- **Progressive Blur**: Fade duration 400-600ms.

By prioritizing these techniques, you ensure the application feels faster than its network latency suggests, reducing user churn and improving overall satisfaction.
