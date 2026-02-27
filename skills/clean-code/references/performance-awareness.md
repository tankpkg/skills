# Performance Awareness

Sources: Knuth (The Art of Computer Programming), Fowler (Refactoring), practical engineering patterns
Covers: data structure selection, N+1 detection, unnecessary computation, memory patterns, caching decisions, algorithmic awareness, profiling workflow.

## 1. The "Profile First" Rule
Optimization is a trade-off between speed and maintainability. Premature optimization makes code harder to read and debug for gains that might not matter.

**When to Optimize:**
- Performance is measurably below SLA or user expectations.
- You have a baseline measurement and a specific bottleneck identified.
- The bottleneck is in a critical user path (the "3%" that matters).
- The gain significantly outweighs the increase in code complexity.

**When NOT to Optimize:**
- You are guessing where the slowness is without measurement.
- The code is "fast enough" for current and near-future requirements.
- The optimization requires an architecture that prevents future refactoring.

**Profiling Workflow:**
1. **Reproduce:** Mirror the performance issue using realistic production data in a staging environment.
2. **Baseline:** Measure current performance (p50, p95, p99 latency or memory peak).
3. **Characterize:** Write a performance test (automated benchmark) that consistently fails. This prevents regressions after the fix.
4. **Trace:** Use a profiler (CPU/Memory) to find the top 1-3 hotspots where execution time is concentrated.
5. **Target:** Apply a targeted fix to the largest bottleneck first.
6. **Verify:** Re-measure to verify the fix and check for memory leaks or CPU regressions.

## 2. Data Structure Selection
Choosing the right structure is the highest-leverage design decision for performance.

| Operation | Array / List | Hash Map / Set | Sorted Tree |
| --- | --- | --- | --- |
| Access by index | O(1) | N/A | N/A |
| Search (unsorted) | O(n) | O(1) | O(log n) |
| Search (sorted) | O(log n) | O(1) | O(log n) |
| Insert / Delete | O(n)* | O(1) | O(log n) |
| Find Min/Max | O(n)** | O(n) | O(log n) |
| Order preservation | Insertion order | No order | Sorted order |
| Memory Overhead | Low | Medium | High |

\* Amortized O(1) for appending to dynamic arrays; O(n) for middle insertion.
\** O(1) if the list is maintained in a sorted state.

**Complexity Quick Reference:**
| Complexity | Name | Example Operation | Max Input Size (approx) |
| --- | --- | --- | --- |
| O(1) | Constant | Hash lookup, array indexing | Infinite |
| O(log n) | Logarithmic | Binary search, tree lookup | Millions |
| O(n) | Linear | Single loop, linear search | Millions |
| O(n log n) | Linearithmic | Merge sort, Quick sort | 100k - 1M |
| O(n²) | Quadratic | Nested loops (bubble sort) | 1k - 10k |
| O(2ⁿ) | Exponential | Recursive Fibonacci, TSP | < 50 |

## 3. Algorithmic Red Flags
Before deep profiling, look for architectural patterns that guarantee poor performance.

**Detection Checklist:**
- **Nested Loops:** Two loops over the same data set (O(n²)) usually indicate a Hash Map lookup could reduce it to O(n).
- **Linear Search in Sorted Data:** If data is already sorted, use binary search (O(log n)) instead of a linear scan.
- **Sorting for Min/Max:** Don't sort an entire list (`O(n log n)`) just to get the top element (`O(n)`).
- **Repeated Conversion:** Converting a list to a set inside a loop instead of once before the loop.
- **Recursion without Memoization:** Pure recursive functions on overlapping subproblems lead to exponential complexity.

**Example: Repeated Linear Search (O(n²))**
```ts
// Before: O(users * posts)
function getUserPosts(users: User[], posts: Post[]) {
  return users.map(user => ({
    ...user,
    posts: posts.filter(p => p.authorId === user.id) // O(posts) scan inside loop
  }));
}

// After: O(users + posts)
function getUserPosts(users: User[], posts: Post[]) {
  const postsByAuthor = groupBy(posts, p => p.authorId); // O(posts) map construction
  return users.map(user => ({
    ...user,
    posts: postsByAuthor.get(user.id) || [] // O(1) lookup
  }));
}
```

**Example: Recursion vs Memoization**
```ts
// Before: O(2ⁿ) - Exponential time
function fib(n: number): number {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

// After: O(n) - Linear time
function fibMemo(n: number, memo: Map<number, number> = new Map()): number {
  if (n <= 1) return n;
  if (memo.has(n)) return memo.get(n)!;
  const result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
  memo.set(n, result);
  return result;
}
```

## 4. The N+1 Problem
The N+1 pattern occurs when one operation triggers N additional operations in a loop. It applies to databases, API calls, and file reads.

**Detection Signals:**
- Logs show dozens of nearly identical queries in a tight sequence.
- Response time degrades linearly as the number of items fetched increases.
- A "fetch", "query", or "load" call is located inside a `for` or `map` loop.

**Prevention Patterns:**
- **SQL Eager Loading:** Use `JOIN` to fetch related data in one query (e.g., `SELECT * FROM posts JOIN authors`).
- **ORM Optimization:** Use methods like `select_related` (JOIN) or `prefetch_related` (Batching) in Django/ActiveRecord.
- **API Batching:** Request a batch endpoint (e.g., `/users?ids=1,2,3`) instead of calling `/users/1` N times.
- **DataLoader:** Use the DataLoader pattern in GraphQL to automatically batch and de-duplicate requests.

**Example: Database N+1 (Pseudocode)**
```ts
// Before: N+1 Queries
const posts = db.query("SELECT * FROM posts");
for (const post of posts) {
  // Executes N times
  post.author = db.query("SELECT * FROM users WHERE id = ?", post.authorId);
}

// After: 1 Query (Eager Load)
const posts = db.query("SELECT posts.*, users.name FROM posts JOIN users ON posts.author_id = users.id");

// After: 2 Queries (Batch Load)
const posts = db.query("SELECT * FROM posts");
const authorIds = posts.map(p => p.authorId);
const authors = db.query("SELECT * FROM users WHERE id IN (?)", authorIds);
const authorMap = new Map(authors.map(a => [a.id, a]));
posts.forEach(p => p.author = authorMap.get(p.authorId));
```

## 5. Unnecessary Computation
Code often computes values that are never used, computed too early, or computed repeatedly.

**Common Anti-patterns:**
- **Computing Unused Results:** Fetching full objects from a database when only a single field is needed.
- **Eager computation:** Calculating an expensive value before checking an early-return condition.
- **Loop Invariants:** Recalculating a value inside a loop that never changes during the iterations.

**Example: Loop Invariant Hoisting**
```ts
// Before: Recalculates threshold N times
function filterItems(items: Item[], config: Config) {
  return items.filter(item => {
    const threshold = calculateComplexThreshold(config); // Invariant
    return item.value > threshold;
  });
}

// After: Hoisted computation
function filterItems(items: Item[], config: Config) {
  const threshold = calculateComplexThreshold(config);
  return items.filter(item => item.value > threshold);
}
```

**Pattern: Early Exit**
Avoid deep computation by checking simple, cheap conditions first.

```ts
// Before: Heavy work happens before validity check
function processRequest(req: Request) {
  const metadata = await db.fetchMetadata(req.id); // Expensive I/O
  const auth = await api.checkAuth(req.token); // Expensive Network
  
  if (!req.payload || req.payload.length === 0) {
    return { status: 400, error: "Empty payload" };
  }
  
  return process(req, metadata, auth);
}

// After: Cheap checks happen first
function processRequest(req: Request) {
  if (!req.payload || req.payload.length === 0) {
    return { status: 400, error: "Empty payload" }; // Fast fail
  }

  const metadata = await db.fetchMetadata(req.id);
  const auth = await api.checkAuth(req.token);
  
  return process(req, metadata, auth);
}
```

## 6. Memory and Allocation Awareness
Allocations involve heap management and eventually garbage collection (GC). In "hot paths" (code that runs thousands of times per second), excessive allocations create "GC pressure" that leads to unpredictable latency spikes.

**Heuristics for Hot Paths:**
- **Pre-allocation:** If you know a collection will hold 10,000 items, initialize it with that capacity to avoid repeated resizing.
- **Reuse Objects:** Update fields of an existing object instead of creating a new temporary instance in every iteration.
- **String Builders:** Never use `+=` on strings in a loop. In many languages, each `+` creates a whole new string. Use a `StringBuilder` or join an array.
- **Avoid Intermediate Collections:** Avoid chains like `list.filter().map().sort()` on large data sets; they create new collections at every step. Use lazy iterators or generators.

**Example: Collection Pre-allocation**
```ts
// Before: Multiple resizes as array grows
const result = [];
for (let i = 0; i < 10000; i++) {
  result.push(compute(i));
}

// After: Allocated once
const result = new Array(10000);
for (let i = 0; i < 10000; i++) {
  result[i] = compute(i);
}
```

## 7. I/O Efficiency
I/O is orders of magnitude slower than memory access. Network and disk operations are almost always the primary bottleneck.

**I/O Design Principles:**
- **Batching:** Send multiple small items in one request rather than making many small requests.
- **Connection Pooling:** Reuse established connections (database, HTTP) to avoid the overhead of TCP/TLS handshakes.
- **Streaming:** Process large files or response bodies line-by-line or in chunks rather than loading the entire payload into memory.
- **Asynchronous I/O:** Use non-blocking I/O to handle other tasks while waiting for a response.

**Example: Streaming vs Buffering**
```ts
// Before: Loads 1GB file into memory
const data = fs.readFileSync("huge_log.txt", "utf-8");
const lines = data.split("\n");

// After: Memory usage remains constant
const reader = readline.createInterface({ input: fs.createReadStream("huge_log.txt") });
for await (const line of reader) {
  process(line);
}
```

## 8. Caching Decision Tree
Caching adds significant complexity (invalidation, memory usage, potential for stale data).

**When to Cache:**
1. **Frequency:** Is the data accessed frequently? If NO, don't cache.
2. **Cost:** Is the computation/fetch expensive (>100ms or high financial cost for API)? If NO, don't cache.
3. **Stability:** Is the data stable? If it changes multiple times per second, caching is risky.
4. **Consistency:** Can you tolerate stale data? If NO, you must implement reliable invalidation.
5. **Memory:** Is the cached data small enough for memory? If NO, consider partial caching or a distributed cache (Redis).
6. **Safety:** Does the data contain sensitive PII that requires specific expiration/security?

**Invalidation Strategies:**
| Strategy | Use Case | Pro | Con |
| --- | --- | --- | --- |
| **TTL (Time to Live)** | Slightly stale data is OK | Simple, zero logic needed | May serve old data |
| **Event-driven** | Real-time consistency | Always fresh | Complex to implement |
| **Write-through** | Strong consistency | Cache is always right | Slower writes |
| **Manual** | Admin-triggered updates | Full control | High risk of human error |

## 9. Per-Language Performance Traps

| Language | Primary Trap | Detection Signal |
| --- | --- | --- |
| **JavaScript** | Blocking the Event Loop | UI freeze or server-side "Event Loop Lag" spikes. |
| **Python** | Global Interpreter Lock (GIL) | CPU-bound multi-threaded code not scaling. Use `multiprocessing`. |
| **Java** | GC Pauses (Stop-the-World) | Spikes in p99 latency; high CPU usage during young gen GC. |
| **Go** | Goroutine Leaks | Memory usage climbing indefinitely; check `NumGoroutine` count. |
| **Rust** | Unnecessary `.clone()` | Profiler shows significant time spent in `memcpy` or cloning. |
| **C#** | Boxing/Unboxing | High GC pressure when using `object` or non-generic collections. |
| **Ruby** | Method Dispatch Overhead | Extremely deep inheritance trees or heavy use of `method_missing`. |

## 10. Performance Summary
1. **Clear Code First:** Write for readability. Optimize only when the data proves it's necessary.
2. **Profile, Don't Guess:** You will likely guess the wrong bottleneck. Use tools to see the truth.
3. **Batch over Chatty:** Minimize I/O round-trips. One big request beats 100 small ones.
4. **Mind the Hot Path:** Keep allocations, heavy I/O, and complexity out of frequently called loops.
5. **Know Your Big-O:** Using the wrong data structure is an architectural failure, not a micro-optimization.