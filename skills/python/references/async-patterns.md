# Async Patterns with asyncio

Sources:
- Python Documentation (asyncio)
- asyncio Official Documentation

## Event Loop Basics
```python
import asyncio

async def main() -> None:
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
```

## Coroutines and Tasks
```python
import asyncio

async def fetch(url: str) -> str:
    await asyncio.sleep(0.01)
    return f"ok:{url}"

async def main() -> None:
    task = asyncio.create_task(fetch("https://example.com"))
    result = await task
    print(result)
```

## Awaiting Multiple Coroutines
```python
import asyncio

async def job(n: int) -> int:
    await asyncio.sleep(0.01)
    return n * 2

async def main() -> None:
    results = await asyncio.gather(job(1), job(2), job(3))
    print(results)
```

## asyncio.gather vs TaskGroup (3.11+)
```python
import asyncio

async def job(n: int) -> int:
    await asyncio.sleep(0.01)
    return n

async def with_taskgroup() -> list[int]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(job(n)) for n in range(3)]
    return [t.result() for t in tasks]

async def with_gather() -> list[int]:
    return await asyncio.gather(*(job(n) for n in range(3)))
```

## Structured Concurrency: Timeouts
```python
import asyncio

async def slow() -> str:
    await asyncio.sleep(5)
    return "done"

async def main() -> None:
    try:
        async with asyncio.timeout(0.5):
            await slow()
    except TimeoutError:
        print("timed out")
```

## TaskGroup Error Handling
```python
import asyncio

async def fail() -> None:
    raise ValueError("bad")

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fail())
            tg.create_task(asyncio.sleep(0.1))
    except* ValueError as err:
        print("grouped", err.exceptions)
```

## Cancellation and Cleanup
```python
import asyncio

async def worker() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cancelled")
        raise

async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.1)
    task.cancel()
    with asyncio.suppress(asyncio.CancelledError):
        await task
```

## Async Generators
```python
import asyncio

async def ticker() -> asyncio.AsyncIterator[int]:
    for i in range(3):
        await asyncio.sleep(0.01)
        yield i

async def main() -> None:
    async for value in ticker():
        print(value)
```

## Async Comprehensions
```python
import asyncio

async def numbers() -> asyncio.AsyncIterator[int]:
    for i in range(3):
        await asyncio.sleep(0.01)
        yield i

async def main() -> None:
    values = [v async for v in numbers()]
    print(values)
```

## Async Context Managers (aiohttp)
```python
import aiohttp

async def fetch_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

## Async Context Managers (aiofiles)
```python
import aiofiles

async def read_text(path: str) -> str:
    async with aiofiles.open(path, "r") as f:
        return await f.read()
```

## Semaphore for Concurrency Limits
```python
import asyncio

async def bounded_fetch(sem: asyncio.Semaphore, url: str) -> str:
    async with sem:
        await asyncio.sleep(0.01)
        return url

async def main() -> None:
    sem = asyncio.Semaphore(5)
    results = await asyncio.gather(
        *(bounded_fetch(sem, f"https://example.com/{i}") for i in range(10))
    )
    print(len(results))
```

## Producer/Consumer with asyncio.Queue
```python
import asyncio

async def producer(q: asyncio.Queue[int]) -> None:
    for i in range(3):
        await q.put(i)
    await q.put(-1)

async def consumer(q: asyncio.Queue[int]) -> None:
    while True:
        value = await q.get()
        if value == -1:
            break
        print(value)

async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()
    await asyncio.gather(producer(q), consumer(q))
```

## Fan-Out/Fan-In Pattern
```python
import asyncio

async def work(n: int) -> int:
    await asyncio.sleep(0.01)
    return n * n

async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(work(n)) for n in range(5)]
    results = [t.result() for t in tasks]
    print(results)
```

## Shielding Critical Work
```python
import asyncio

async def save() -> None:
    await asyncio.sleep(0.1)

async def main() -> None:
    task = asyncio.create_task(save())
    await asyncio.shield(task)
```

## Common Pitfall: Blocking the Event Loop
```python
import time

async def bad() -> None:
    time.sleep(1)

async def good() -> None:
    await asyncio.sleep(1)
```

## Common Pitfall: Forgetting await
```python
async def do_work() -> None:
    await asyncio.sleep(0.01)

async def main() -> None:
    coro = do_work()
    await coro
```

## Common Pitfall: Fire-and-Forget Tasks
```python
import asyncio

async def work() -> None:
    await asyncio.sleep(0.01)

async def main() -> None:
    task = asyncio.create_task(work())
    await task
```

## Sync to Async Migration
```python
def load_sync(path: str) -> str:
    with open(path) as f:
        return f.read()

async def load_async(path: str) -> str:
    import aiofiles
    async with aiofiles.open(path) as f:
        return await f.read()
```

## Bridging with run_in_executor
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def cpu_bound(x: int) -> int:
    return x * x

async def main() -> None:
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_bound, 9)
    print(result)
```

## When NOT to Use Async
```python
def parse_small_file(path: str) -> str:
    with open(path) as f:
        return f.read()

def cpu_heavy(values: list[int]) -> int:
    return sum(v * v for v in values)
```

## Anti-Patterns
```python
import asyncio

async def bad_sleep() -> None:
    import time
    time.sleep(1)

async def bad_gather() -> None:
    tasks = [asyncio.create_task(asyncio.sleep(0.01)) for _ in range(3)]
    await asyncio.gather(*tasks)
```

| Anti-pattern | Why it fails | Prefer |
| --- | --- | --- |
| Blocking calls in async | Freezes event loop | Async I/O or executor |
| Creating tasks without await | Lost errors | Track and await tasks |
| Swallowing CancelledError | Leaks tasks | Re-raise cancellation |
| Unbounded concurrency | Resource exhaustion | Semaphore or TaskGroup |
| Long CPU work in event loop | Starvation | Thread or process pool |
| Using gather for critical failures | Mixed errors | TaskGroup + except* |
| Shared mutable globals | Race conditions | Message passing |
| Forgetting timeouts | Hanging tasks | `asyncio.timeout` |
| Heavy logging per await | Slowdowns | Sampled logging |
| Mixing sync and async clients | Deadlocks | Use async libs consistently |

## Checklist
```python
def checklist() -> list[str]:
    return [
        "Use asyncio.run at entry points",
        "Prefer TaskGroup for fan-out",
        "Add timeouts around I/O",
        "Limit concurrency with Semaphore",
    ]
```
