# Testing and Packaging Reference

Sources:
- pytest Documentation
- Python Packaging User Guide

## pytest Basics
```python
def add(a: int, b: int) -> int:
    return a + b

def test_add() -> None:
    assert add(1, 2) == 3
```

## Fixtures and conftest.py
```python
import pytest

@pytest.fixture
def config() -> dict[str, str]:
    return {"env": "test"}

def test_config(config: dict[str, str]) -> None:
    assert config["env"] == "test"
```

## Fixture Dependency Injection
```python
import pytest

@pytest.fixture
def db_url() -> str:
    return "sqlite:///:memory:"

@pytest.fixture
def client(db_url: str) -> str:
    return f"client({db_url})"

def test_client(client: str) -> None:
    assert "sqlite" in client
```

## Parametrize and Marks
```python
import pytest

@pytest.mark.parametrize("value,expected", [(1, 2), (2, 3)])
def test_increment(value: int, expected: int) -> None:
    assert value + 1 == expected

@pytest.mark.slow
def test_slow_path() -> None:
    assert True
```

## Mocking with unittest.mock
```python
from unittest.mock import Mock

def send_email(client, address: str) -> None:
    client.send(address)

def test_send_email() -> None:
    client = Mock()
    send_email(client, "a@example.com")
    client.send.assert_called_once_with("a@example.com")
```

## Mocking with pytest-mock
```python
def test_patch(mocker) -> None:
    fake = mocker.patch("time.time")
    fake.return_value = 123
    import time
    assert time.time() == 123
```

## Testing Async Code (pytest-asyncio)
```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_work() -> None:
    await asyncio.sleep(0.01)
    assert True
```

## pyproject.toml for a Library
```toml
[project]
name = "acme-lib"
version = "0.1.0"
description = "Reusable helpers"
requires-python = ">=3.10"
dependencies = ["pydantic>=2"]

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
addopts = "-q"
```

```python
from importlib.metadata import version

def lib_version() -> str:
    return version("acme-lib")
```

## pyproject.toml for an App
```toml
[project]
name = "acme-app"
version = "0.1.0"
description = "Production service"
requires-python = ">=3.11"
dependencies = ["httpx>=0.25", "pydantic>=2"]

[project.scripts]
acme = "acme_app.__main__:main"

[tool.ruff]
line-length = 100
```

```python
def main() -> int:
    print("acme-app")
    return 0
```

## uv Workflows
```python
import subprocess

def uv_install() -> None:
    subprocess.run(["uv", "pip", "install", "-e", "."], check=True)

def uv_lock() -> None:
    subprocess.run(["uv", "pip", "compile", "pyproject.toml"], check=True)
```

## src-layout vs Flat-layout
```python
from acme_app.api import ping

def test_import() -> None:
    assert ping() == "pong"
```

| Layout | Use when | Notes |
| --- | --- | --- |
| src-layout | Libraries, larger apps | Avoids import shadowing |
| flat-layout | Tiny scripts | Faster onboarding |

## Virtual Environments
```python
import venv
from pathlib import Path

def create_env(path: Path) -> None:
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(path)
```

## Publishing to PyPI
```python
import subprocess

def publish() -> None:
    subprocess.run(["python", "-m", "build"], check=True)
    subprocess.run(["python", "-m", "twine", "upload", "dist/*"], check=True)
```

## conftest.py Patterns
```python
import pytest

@pytest.fixture(autouse=True)
def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "test")
```

## Temporary Paths
```python
def write_tmp(tmp_path) -> str:
    file_path = tmp_path / "data.txt"
    file_path.write_text("ok")
    return file_path.read_text()
```

## Capturing Output
```python
def greet() -> None:
    print("hello")

def test_capsys(capsys) -> None:
    greet()
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
```

## Parametrized Fixtures
```python
import pytest

@pytest.fixture(params=["sqlite", "postgres"])
def backend(request) -> str:
    return request.param

def test_backend(backend: str) -> None:
    assert backend in {"sqlite", "postgres"}
```

## Marking Expected Failures
```python
import pytest

@pytest.mark.xfail(reason="feature pending")
def test_future() -> None:
    assert False
```

## Anti-Patterns
```python
def test_no_assert() -> None:
    pass
```

| Anti-pattern | Why it fails | Prefer |
| --- | --- | --- |
| No assertions | Test does nothing | Assert meaningful outcomes |
| Global state between tests | Flaky order | Use fixtures |
| Hitting real services | Slow and flaky | Mock or use test containers |
| Testing private internals | Brittle | Test public API |
| Monolithic test cases | Hard to debug | Small focused tests |
| Skipping cleanup | Leaks state | `yield` fixtures |
| Parametrize with huge data | Slow suite | Sample inputs |
| Ignoring warnings | Missed failures | Fail on warnings |
| Mixing unit/integration | Confusing results | Separate markers |

## Checklist
```python
def checklist() -> list[str]:
    return [
        "Keep tests isolated",
        "Use fixtures for setup",
        "Lock dependencies",
        "Publish with build + twine",
    ]
```
