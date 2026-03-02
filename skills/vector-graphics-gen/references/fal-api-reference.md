# fal.ai API Reference
Sources: fal.ai official documentation (2025-2026), @fal-ai/client npm package

## 1. Authentication

Use the FAL key via environment variables or explicit client configuration.
Prefer env vars for local development and CI; use programmatic config for
multi-tenant services.

### Environment variable

```bash
export FAL_KEY="YOUR_FAL_KEY"
```

### Programmatic config (JavaScript)

```javascript
import { fal } from "@fal-ai/client";

fal.config({
  credentials: process.env.FAL_KEY || "YOUR_FAL_KEY"
});
```

### Programmatic config (Python)

```python
from fal_client import FalClient

client = FalClient("YOUR_FAL_KEY")
```

## 2. Client Setup

### JavaScript: @fal-ai/client

Install the SDK, configure credentials, and call an endpoint with async
queue handling.

```bash
npm install @fal-ai/client
```

```javascript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });

const result = await fal.subscribe("fal-ai/recraft/v4/text-to-vector", {
  input: {
    prompt: "Minimal geometric badge for a coffee brand"
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  }
});

console.log(result.images[0].url);
```

### Python: fal-client

Install the SDK and use the client to subscribe to a model endpoint.

```bash
pip install fal-client
```

```python
from fal_client import FalClient

client = FalClient()

result = client.subscribe("fal-ai/recraft/v4/text-to-vector", {
    "prompt": "Minimal geometric badge for a coffee brand"
})

print(result["images"][0]["url"])
```

### REST: curl

Use the queue endpoint for language-agnostic calls. The queue domain accepts
direct POSTs and returns a request id you can poll for results.

```bash
curl -X POST "https://queue.fal.run/fal-ai/recraft/v4/text-to-vector" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Minimal geometric badge for a coffee brand"}'
```

## 3. Request Patterns

Use queue-based async by default. Only use sync when you need a single, quick
call and are willing to block the process. Use manual queue when you need
explicit request ids for tracking or external orchestration.

### Pattern comparison

| Pattern | When to use | Pros | Cons |
| --- | --- | --- | --- |
| subscribe (async) | Most production workflows | Logs + progress callbacks | Slightly more code |
| run (sync) | One-off scripts | Simple, linear | Can time out, blocks process |
| submit/status/result | Orchestrated pipelines | Explicit request id | Multiple network round trips |

### Async subscribe (recommended)

#### JavaScript

```javascript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });

const result = await fal.subscribe("fal-ai/recraft/v4/text-to-vector", {
  input: {
    prompt: "Flat icon set: cloud, sun, rain"
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  }
});

console.log(result.images.map((img) => img.url));
```

#### Python

```python
from fal_client import FalClient

client = FalClient()

def on_update(update):
    if update["status"] == "IN_PROGRESS":
        for log in update.get("logs", []):
            print(log.get("message"))

result = client.subscribe(
    "fal-ai/recraft/v4/text-to-vector",
    {"prompt": "Flat icon set: cloud, sun, rain"},
    on_queue_update=on_update,
    logs=True,
)

print([img["url"] for img in result["images"]])
```

### Sync run

#### JavaScript

```javascript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });

const result = await fal.run("fal-ai/recraft/v4/text-to-vector", {
  input: {
    prompt: "Simple monochrome SVG logo for a bike shop"
  }
});

console.log(result.images[0].url);
```

#### Python

```python
from fal_client import FalClient

client = FalClient()

result = client.run("fal-ai/recraft/v4/text-to-vector", {
    "prompt": "Simple monochrome SVG logo for a bike shop"
})

print(result["images"][0]["url"])
```

### Manual queue (submit/status/result)

#### JavaScript

```javascript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });

const { request_id } = await fal.queue.submit("fal-ai/recraft/v4/text-to-vector", {
  input: {
    prompt: "Minimal map pin icon with clean outline"
  }
});

let status = await fal.queue.status("fal-ai/recraft/v4/text-to-vector", {
  requestId: request_id
});

while (status.status !== "COMPLETED" && status.status !== "FAILED") {
  await new Promise((r) => setTimeout(r, 1000));
  status = await fal.queue.status("fal-ai/recraft/v4/text-to-vector", {
    requestId: request_id
  });
}

if (status.status === "FAILED") {
  throw new Error(status.error || "Fal queue failed");
}

const result = await fal.queue.result("fal-ai/recraft/v4/text-to-vector", {
  requestId: request_id
});

console.log(result.images[0].url);
```

#### curl

```bash
# Submit
curl -X POST "https://queue.fal.run/fal-ai/recraft/v4/text-to-vector" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Minimal map pin icon with clean outline"}'

# Check status
curl -X GET "https://queue.fal.run/fal-ai/recraft/v4/text-to-vector/status/{REQUEST_ID}" \
  -H "Authorization: Key $FAL_KEY"

# Fetch result
curl -X GET "https://queue.fal.run/fal-ai/recraft/v4/text-to-vector/result/{REQUEST_ID}" \
  -H "Authorization: Key $FAL_KEY"
```

## 4. Response Format

Expect an `images` array. For vector endpoints, each image entry points to
an SVG file with `content_type` set to `image/svg+xml`.

```json
{
  "images": [
    {
      "url": "https://storage.fal.run/outputs/abc123/image.svg",
      "file_size": 24561,
      "file_name": "image.svg",
      "content_type": "image/svg+xml"
    }
  ]
}
```

## 5. File Upload

Use fal storage to upload local files (e.g., a raster image you want to
vectorize) and pass the resulting URL in model input.

### JavaScript upload

```javascript
import { fal } from "@fal-ai/client";
import fs from "node:fs";

fal.config({ credentials: process.env.FAL_KEY });

const buffer = fs.readFileSync("./input.png");
const file = new File([buffer], "input.png", { type: "image/png" });

const url = await fal.storage.upload(file);

const result = await fal.subscribe("fal-ai/recraft/vectorize", {
  input: { image_url: url }
});

console.log(result.images[0].url);
```

### Python upload

```python
from fal_client import FalClient

client = FalClient()

uploaded_url = client.upload_file("./input.png")

result = client.subscribe("fal-ai/recraft/vectorize", {
    "image_url": uploaded_url
})

print(result["images"][0]["url"])
```

## 6. Error Handling

Handle queue failures explicitly, and implement timeouts and retries for
network errors or 429 responses. Fail fast on invalid inputs.

### Queue statuses to handle

| Status | Meaning | Action |
| --- | --- | --- |
| IN_QUEUE | Waiting for worker | Keep polling |
| IN_PROGRESS | Running | Stream logs or wait |
| COMPLETED | Success | Fetch result |
| FAILED | Model or input error | Inspect error, do not retry blindly |
| CANCELED | Request canceled | Treat as failure |
| TIMEOUT | Worker exceeded limit | Retry with backoff or reduce workload |

### JavaScript retry pattern

```javascript
import { fal } from "@fal-ai/client";

fal.config({ credentials: process.env.FAL_KEY });

async function runWithRetry(endpoint, input, maxAttempts = 3) {
  let attempt = 0;
  let lastError;

  while (attempt < maxAttempts) {
    attempt += 1;
    try {
      return await fal.run(endpoint, { input });
    } catch (err) {
      lastError = err;
      const waitMs = 500 * attempt;
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }

  throw lastError;
}

const result = await runWithRetry(
  "fal-ai/recraft/v4/text-to-vector",
  { prompt: "Outlined badge with clean geometry" }
);

console.log(result.images[0].url);
```

### Python timeout and retry

```python
import time
from fal_client import FalClient

client = FalClient()

def run_with_retry(endpoint, payload, max_attempts=3):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            return client.run(endpoint, payload)
        except Exception as err:
            last_error = err
            time.sleep(0.5 * attempt)
    raise last_error

result = run_with_retry(
    "fal-ai/recraft/v4/text-to-vector",
    {"prompt": "Outlined badge with clean geometry"}
)

print(result["images"][0]["url"])
```

## 7. Downloading SVG Results

Download the SVG with a standard HTTP fetch once you have the image URL.
Verify `content_type` if the caller needs to enforce SVG output.

### JavaScript download

```javascript
import fs from "node:fs";

async function downloadSvg(url, outputPath) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Download failed: ${res.status}`);
  }
  const svg = await res.text();
  fs.writeFileSync(outputPath, svg, "utf8");
}

await downloadSvg(
  "https://storage.fal.run/outputs/abc123/image.svg",
  "./result.svg"
);
```

### Python download

```python
import requests

def download_svg(url, path):
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    with open(path, "w", encoding="utf-8") as f:
        f.write(res.text)

download_svg(
    "https://storage.fal.run/outputs/abc123/image.svg",
    "./result.svg"
)
```

## 8. Common Pitfalls Table

| Pitfall | Cause | Fix |
| --- | --- | --- |
| Using sync run for large batches | run blocks and can time out | Use subscribe or manual queue |
| Missing credentials in CI | FAL_KEY not set in environment | Export FAL_KEY in CI secret config |
| Treating vector-style raster as SVG | Some models return PNG | Check `content_type` and file extension |
| Ignoring queue failures | FAILED status not handled | Stop and surface error details |
| Hard-coding request ids | Reusing old request_id | Always capture from submit response |
| Uploading local paths directly | API expects URLs | Upload via fal storage and pass URL |
| Polling too aggressively | Rate limits or wasted requests | Poll every 1-2 seconds |
| Saving SVG as binary | Using response.arrayBuffer | Use res.text() and write UTF-8 |
