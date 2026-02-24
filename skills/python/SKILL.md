---
name: "@tank/python"
description: "Modern Python (3.10+) patterns for production applications."
triggers:
  - python
  - type hint
  - typing
  - typevar
  - protocol
  - dataclass
  - attrs
  - async
  - asyncio
  - taskgroup
  - pytest
  - pydantic
  - match case
  - pyproject.toml
  - packaging
  - uv
  - pip
  - virtual environment
  - decorator
  - context manager
  - generator
  - comprehension
  - f-string
  - walrus operator
  - typealias
---

# Modern Python 3.10+ Skill

## Purpose
Provide production-grade Python guidance for 3.10+ with type hints, async patterns,
testing, and packaging. Emphasis is on clarity, maintainability, and runtime safety.

## Core Philosophy
- "Type hints are documentation that compiles."
- "Explicit over implicit."
- "Flat is better than nested."

## Python Version Features
| Version | Highlights | Notes |
| --- | --- | --- |
| 3.10 | `match/case`, `ParamSpec` | Structural patterns, better typing ergonomics |
| 3.11 | `ExceptionGroup`, `TaskGroup` | Structured concurrency and error grouping |
| 3.12 | `type` statement, f-string improvements | Cleaner aliases, faster formatting |
| 3.13 | latest | Track releases; prefer stable, tested usage |

## Project Structure (src-layout)
```text
repo/
  pyproject.toml
  README.md
  src/
    acme_app/
      __init__.py
      api.py
      config.py
      models.py
      services/
        __init__.py
        billing.py
      __main__.py
  tests/
    conftest.py
    test_api.py
  scripts/
    dev.py
```

## Type Hint Quick Reference
| Pattern | Prefer | Notes |
| --- | --- | --- |
| Optional | `X | None` | Use `None` explicitly, avoid `Optional[X]` in new code |
| Collections | `list[str]` | Use built-in generics (3.9+) |
| Dicts | `dict[str, int]` | Prefer immutable `Mapping` at boundaries |
| Callables | `Callable[[A, B], R]` | Use `ParamSpec` for wrappers |
| Protocols | `class Repo(Protocol): ...` | Structural typing over inheritance |
| Type aliases | `type UserId = str` | 3.12 `type` statement |
| Literal | `Literal["open", "closed"]` | Constrain state enums |
| Generics | `class Box[T]: ...` | Model reusable containers |

## Type Hint Patterns
```python
from typing import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class Runner(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

def time_it(fn: Runner[P, R]) -> Runner[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return wrapper
```

## Data Modeling
```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Invoice:
    id: str
    lines: list[str] = field(default_factory=list)
```

## Async Guidance
```python
import asyncio

async def fetch_all(urls: list[str]) -> list[str]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(u)) for u in urls]
    return [t.result() for t in tasks]
```

## Testing Guidance
```python
import pytest

@pytest.mark.parametrize("value,expected", [(1, 2), (2, 3)])
def test_increment(value: int, expected: int) -> None:
    assert increment(value) == expected
```

## Packaging Checklist
- Use `src/` layout for libraries and apps with multiple modules.
- Pin tool versions in `pyproject.toml` and lock with `uv`.
- Provide console entry points under `project.scripts`.
- Separate runtime and dev dependencies.

## Operating Guidance
- Use `pyproject.toml` as the single source of truth for build, lint, and tools.
- Prefer `pathlib.Path` over string paths; avoid `os.path` for new code.
- Validate external input with Pydantic v2 or dataclasses + explicit parsing.
- Prefer small, pure functions and explicit dependency injection.
- Keep modules flat; avoid deep nesting unless boundaries are clear.

## Error Handling Patterns
- Raise narrow, explicit exceptions; wrap third-party exceptions at the boundary.
- Use `ExceptionGroup` when fan-out tasks fail independently.
- Log with context keys, not string concatenation; keep tracebacks intact.

## Anti-Patterns
| Anti-pattern | Why it fails | Prefer |
| --- | --- | --- |
| Mutable default args | Shared state across calls | `None` sentinel + create inside |
| Bare `except:` | Hides `KeyboardInterrupt` and bugs | `except Exception` |
| `import *` | Namespace pollution | Explicit imports |
| Ignoring `await` | Silent failures | Always `await` coroutines |
| Global state singletons | Hidden coupling | Inject dependencies |
| Deep nesting | Hard to test and read | Early returns |
| `print` logging in prod | No context or levels | `logging` with adapters |
| Mixing sync/async I/O | Blocks event loop | Async libraries and `await` |
| `typing.Any` everywhere | Loses guarantees | Narrow types at edges |

## Reference File Index
- `skills/python/references/modern-python.md`
- `skills/python/references/async-patterns.md`
- `skills/python/references/testing-and-packaging.md`

## Response Style
- Provide concise answers with real Python examples.
- Keep code modern (3.10+), avoid legacy compatibility advice.
- Default to type hints, dataclasses, and `asyncio` when relevant.
