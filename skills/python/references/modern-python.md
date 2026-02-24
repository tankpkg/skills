# Modern Python 3.10+ Reference

Sources:
- Python Documentation (3.10-3.13)
- Fluent Python, 2nd Edition (Ramalho)
- Robust Python (Viafore)

## Type Hints: TypeVar and Generic
```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

## Type Hints: Bounds and Constraints
```python
from typing import TypeVar

TNumber = TypeVar("TNumber", int, float)
TUserId = TypeVar("TUserId", bound=str)

def add(a: TNumber, b: TNumber) -> TNumber:
    return a + b

def normalize_user_id(raw: TUserId) -> TUserId:
    return raw.strip()
```

## Protocols: Structural Typing
```python
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ttl: int) -> None: ...

def warm_cache(cache: Cache) -> None:
    cache.set("status", "ok", ttl=60)
```

## ParamSpec and Concatenate
```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def inject_request(fn: Callable[Concatenate[str, P], R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn("req-123", *args, **kwargs)
    return wrapper
```

## Dataclasses: Frozen and Slots
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Money:
    currency: str
    amount: int

price = Money("USD", 1999)
```

## Dataclasses: Field Factories and Post Init
```python
from dataclasses import dataclass, field

@dataclass
class Order:
    id: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tags = [t.lower() for t in self.tags]
```

## Dataclasses: Init Only and Derived Fields
```python
from dataclasses import dataclass, field, InitVar

@dataclass
class Token:
    raw: InitVar[str]
    digest: str = field(init=False)

    def __post_init__(self, raw: str) -> None:
        self.digest = raw.encode().hex()
```

## match/case: Structural Patterns
```python
def render(event: dict) -> str:
    match event:
        case {"type": "created", "id": int(id)}:
            return f"created:{id}"
        case {"type": "error", "detail": str(detail)}:
            return f"error:{detail}"
        case _:
            return "unknown"
```

## match/case: Guards
```python
def classify(value: int) -> str:
    match value:
        case x if x < 0:
            return "negative"
        case x if 0 <= x < 10:
            return "small"
        case _:
            return "large"
```

## Walrus Operator (:=) Patterns
```python
def read_first_line(path: str) -> str | None:
    if (line := open(path).readline().strip()):
        return line
    return None

def take_while_even(values: list[int]) -> list[int]:
    out: list[int] = []
    while (value := values.pop(0)) % 2 == 0:
        out.append(value)
    return out
```

## StrEnum and IntEnum
```python
from enum import IntEnum, StrEnum

class Status(StrEnum):
    OPEN = "open"
    CLOSED = "closed"

class Priority(IntEnum):
    LOW = 1
    HIGH = 10

def is_open(status: Status) -> bool:
    return status == Status.OPEN
```

## TypeAlias and type Statement (3.12+)
```python
from typing import TypeAlias

UserId: TypeAlias = str

type OrderId = str
type JsonDict = dict[str, object]
```

## @override Decorator (3.12+)
```python
from typing import override

class Repo:
    def save(self, value: str) -> None: ...

class MemoryRepo(Repo):
    @override
    def save(self, value: str) -> None:
        self.value = value
```

## ExceptionGroup and except*
```python
def demo_groups() -> None:
    try:
        raise ExceptionGroup("batch", [ValueError("bad"), RuntimeError("fail")])
    except* ValueError as err:
        print("value", err.exceptions)
    except* RuntimeError as err:
        print("runtime", err.exceptions)
```

## Decorators: functools.wraps
```python
from functools import wraps

def traced(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("call", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper
```

## Decorators: Parametrized
```python
from functools import wraps

def retry(times: int):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    last = _
            raise RuntimeError(f"failed after {times}")
        return wrapper
    return decorator
```

## Decorators: Class Decorators
```python
def add_repr(cls):
    def __repr__(self) -> str:
        return f"{cls.__name__}({self.__dict__})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
```

## Context Managers: contextlib
```python
from contextlib import contextmanager

@contextmanager
def log_section(name: str):
    print("start", name)
    try:
        yield
    finally:
        print("end", name)
```

## Async Context Managers
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan():
    resource = await open_resource()
    try:
        yield resource
    finally:
        await resource.close()
```

## Pattern: __all__ for Public API
```python
__all__ = ["Client", "Config"]

class Client:
    ...

class Config:
    ...
```

## Pattern: pathlib and type-safe paths
```python
from pathlib import Path

def read_config(root: Path) -> str:
    return (root / "config.toml").read_text()
```

## Anti-Patterns
```python
def bad_default(items: list[str] = []):
    items.append("x")
    return items
```

| Anti-pattern | Why it fails | Prefer |
| --- | --- | --- |
| Mutable default args | Shared state across calls | `None` sentinel + create inside |
| Bare `except:` | Hides system exits | `except Exception` |
| `import *` | Namespace pollution | Explicit imports |
| `type: ignore` everywhere | Silences real errors | Narrow types or `cast` |
| Global mutable state | Hard to test | Dependency injection |
| Deep nesting | Cognitive load | Early returns |
| `eval` for parsing | Security risk | `json`, `ast.literal_eval` |
| `str` for enums | Invalid values | `StrEnum` |
| Catching `BaseException` | Hides `KeyboardInterrupt` | `Exception` |
| Unbounded recursion | Stack risk | Iterative or tail patterns |

## Quick Checklist
```python
def checklist() -> list[str]:
    return [
        "Use type hints on public APIs",
        "Prefer dataclasses with slots",
        "Use match/case for tagged unions",
        "Use ExceptionGroup for fan-out failures",
    ]
```
