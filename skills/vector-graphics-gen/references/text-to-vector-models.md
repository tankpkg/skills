# Text-to-Vector Models

Sources: fal.ai documentation (2025-2026), Recraft API docs, model benchmarks

Covers: All text-to-vector and vector-style image endpoints on fal.ai — Recraft V4, V4 Pro, V3 — with complete parameter references, model comparison, code examples, and the two-step raster-to-SVG pipeline.

## Model Overview

Three primary paths to vector output via fal.ai:

1. **Native SVG** — Recraft V4 and V4 Pro produce true SVG files directly from text
2. **Vector-style raster** — Recraft V3 with `vector_illustration` style produces raster images optimized for vectorization
3. **Two-step pipeline** — Generate with V3 vector style, then convert to SVG via `fal-ai/recraft/vectorize`

For image-to-SVG conversion endpoints, see `references/image-to-svg-conversion.md`.

## Model Comparison Table

| Model | Endpoint | Output Format | Price | Quality | Speed | Best For |
|-------|----------|---------------|-------|---------|-------|----------|
| Recraft V4 | `fal-ai/recraft/v4/text-to-vector` | True SVG | $0.08/image | High | Medium | Logos, icons, brand assets |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro/text-to-vector` | True SVG | $0.30/image | Highest | Slow | Production assets, complex illustrations |
| Recraft V3 | `fal-ai/recraft/v3/text-to-image` | Raster PNG | $0.08/image (vector style) | High | Fast | Vector-style illustrations, two-step pipeline |
| Recraft V3 (raster) | `fal-ai/recraft/v3/text-to-image` | Raster PNG | $0.04/image | High | Fast | Non-vector styles, photorealistic |

**Default choice**: Recraft V4 for direct SVG output. Use V4 Pro when quality is critical and cost is secondary. Use V3 + vectorize pipeline when you need fine-grained style control from V3's 22 sub-styles.

---

## Recraft V4 Text-to-Vector

**Endpoint**: `fal-ai/recraft/v4/text-to-vector`
**Output**: True SVG (`content_type: "image/svg+xml"`)
**Price**: $0.08/image

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description of the desired vector graphic |
| `image_size` | string or object | No | `square_hd` | Output dimensions (see size options below) |
| `colors` | array | No | — | Brand palette as array of `{r, g, b}` objects |
| `background_color` | object | No | — | Background fill as `{r, g, b}` |
| `enable_safety_checker` | boolean | No | `true` | Enable content safety filtering |

### Image Size Options

| Value | Dimensions | Use Case |
|-------|-----------|----------|
| `square` | 512×512 | Icons, avatars |
| `square_hd` | 1024×1024 | Logos, general use (default) |
| `portrait_4_3` | 768×1024 | Tall illustrations |
| `portrait_16_9` | 576×1024 | Mobile-oriented |
| `landscape_4_3` | 1024×768 | Wide illustrations |
| `landscape_16_9` | 1024×576 | Banner graphics |
| `{width, height}` | Custom | Specify exact pixel dimensions |

### Response Format

```json
{
  "images": [
    {
      "url": "https://fal.media/files/...",
      "file_size": 24680,
      "file_name": "image.svg",
      "content_type": "image/svg+xml"
    }
  ]
}
```

### JavaScript Example

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/recraft/v4/text-to-vector", {
  input: {
    prompt: "A minimalist mountain logo with clean geometric shapes",
    image_size: "square_hd",
    colors: [
      { r: 59, g: 130, b: 246 },
      { r: 30, g: 64, b: 175 }
    ],
    background_color: { r: 255, g: 255, b: 255 }
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});

const svgUrl = result.data.images[0].url;
// Download SVG
const response = await fetch(svgUrl);
const svgContent = await response.text();
```

### Python Example

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/recraft/v4/text-to-vector",
    arguments={
        "prompt": "A minimalist mountain logo with clean geometric shapes",
        "image_size": "square_hd",
        "colors": [
            {"r": 59, "g": 130, "b": 246},
            {"r": 30, "g": 64, "b": 175}
        ],
        "background_color": {"r": 255, "g": 255, "b": 255}
    }
)

svg_url = result["images"][0]["url"]
```

---

## Recraft V4 Pro Text-to-Vector

**Endpoint**: `fal-ai/recraft/v4/pro/text-to-vector`
**Output**: True SVG (`content_type: "image/svg+xml"`)
**Price**: $0.30/image

The Pro variant uses an enhanced model with higher fidelity output, more complex path structures, and better adherence to detailed prompts. Use when the standard V4 output lacks sufficient detail or when the asset will be used at large scale.

Parameters are identical to Recraft V4 — replace the endpoint string with `fal-ai/recraft/v4/pro/text-to-vector`. All `prompt`, `image_size`, `colors`, `background_color`, and `enable_safety_checker` parameters apply unchanged.

### When to Use V4 Pro vs V4

| Scenario | Use |
|----------|-----|
| Prototyping, iteration, batch generation | V4 ($0.08) |
| Final production asset, client deliverable | V4 Pro ($0.30) |
| Complex illustration with fine detail | V4 Pro |
| Simple icon or logo | V4 |
| Budget-constrained project | V4 |
| Quality is the only constraint | V4 Pro |

---

## Recraft V3 Text-to-Image (Vector Style)

**Endpoint**: `fal-ai/recraft/v3/text-to-image`
**Output**: Raster PNG (NOT true SVG)
**Price**: $0.04/image (raster styles), $0.08/image (vector_illustration style)

V3 produces raster images but with 22 vector-optimized sub-styles that produce clean, flat artwork ideal for downstream vectorization. Use V3 when you need a specific illustration style not available in V4, or as the first step in the two-step pipeline.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description |
| `style` | string | No | `realistic_image` | Top-level style category |
| `style_id` | string | No | — | Sub-style within the category |
| `image_size` | string or object | No | `square_hd` | Output dimensions |
| `colors` | array | No | — | Brand palette as array of `{r, g, b}` objects |
| `enable_safety_checker` | boolean | No | `true` | Enable content safety filtering |

### Top-Level Style Values

| Value | Description | Price |
|-------|-------------|-------|
| `realistic_image` | Photorealistic output | $0.04 |
| `digital_illustration` | Digital art, painterly | $0.04 |
| `vector_illustration` | Flat, clean, vector-optimized | $0.08 |

Set `style: "vector_illustration"` to access all 22 vector sub-styles.

### Vector Illustration Sub-Styles (22 Total)

Set `style_id` to one of these values when `style` is `"vector_illustration"`:

| Sub-style | Visual Character | Best For |
|-----------|-----------------|----------|
| `bold_stroke` | Thick outlines, high contrast | Stickers, badges, bold branding |
| `chemistry` | Technical diagram aesthetic | Scientific, educational content |
| `colored_sticker` | Bright fills with outline | Sticker packs, emoji-style assets |
| `contour` | Outline-focused, minimal fill | Line art, coloring book style |
| `cosmetics` | Soft, elegant, beauty-adjacent | Beauty brands, lifestyle |
| `cutout` | Paper-cut layered look | Collage, editorial illustration |
| `engraving` | Cross-hatch, etched texture | Vintage, premium, certificates |
| `editorial` | Clean, publication-ready | Magazine, news, infographics |
| `ethnic` | Cultural pattern motifs | Decorative, cultural content |
| `line_art` | Pure line drawing, no fill | Sketches, technical illustration |
| `line_circuit` | Circuit board line patterns | Tech, electronics, data |
| `linocut` | Woodblock print texture | Artisan, handmade aesthetic |
| `marker` | Marker pen strokes | Casual, hand-drawn feel |
| `mosaic` | Tile/fragment composition | Decorative, abstract |
| `naiveart` | Childlike, folk art style | Playful, approachable brands |
| `outline` | Simple outline shapes | Icons, UI elements |
| `outline_details` | Outline with interior detail lines | Detailed icons, technical |
| `paper_cut_style` | Layered paper silhouettes | Craft aesthetic, depth |
| `pointilism` | Dot-based texture | Artistic, textured illustration |
| `pop_art` | Bold color, halftone influence | Retro, vibrant branding |
| `psychedelic` | Swirling, surreal patterns | Music, festival, creative |
| `seamless_pattern` | Tileable repeat pattern | Backgrounds, textiles, packaging |
| `thin` | Hairline strokes, delicate | Elegant, minimal, luxury |
| `watercolor` | Soft washes, organic edges | Lifestyle, organic brands |

### JavaScript Example

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/recraft/v3/text-to-image", {
  input: {
    prompt: "A coffee cup with steam rising, flat design",
    style: "vector_illustration",
    style_id: "bold_stroke",
    image_size: "square_hd",
    colors: [
      { r: 120, g: 53, b: 15 },
      { r: 254, g: 243, b: 199 }
    ]
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});

const imageUrl = result.data.images[0].url;
// This is a raster PNG — pass to vectorize endpoint to get SVG
```

### Python Example

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/recraft/v3/text-to-image",
    arguments={
        "prompt": "A coffee cup with steam rising, flat design",
        "style": "vector_illustration",
        "style_id": "bold_stroke",
        "image_size": "square_hd",
        "colors": [
            {"r": 120, "g": 53, "b": 15},
            {"r": 254, "g": 243, "b": 199}
        ]
    }
)

image_url = result["images"][0]["url"]
```

---

## Two-Step Pipeline: V3 Vector Style + Vectorize

Use this pipeline when you need a specific V3 sub-style (e.g., `engraving`, `linocut`, `seamless_pattern`) and require true SVG output. Total cost: $0.08 (V3) + $0.01 (vectorize) = $0.09/image.

### When to Use the Pipeline vs Direct V4

| Scenario | Approach |
|----------|----------|
| Need a specific V3 sub-style (e.g., linocut, engraving) | V3 + vectorize |
| Need true SVG, style doesn't matter | V4 direct ($0.08) |
| Need highest quality SVG | V4 Pro direct ($0.30) |
| Need seamless/tileable pattern as SVG | V3 seamless_pattern + vectorize |
| Iterating on style before committing to SVG | V3 raster first, vectorize when satisfied |

### Step 1: Generate Raster with V3 Vector Style

```javascript
import { fal } from "@fal-ai/client";

// Step 1: Generate vector-style raster
const rasterResult = await fal.subscribe("fal-ai/recraft/v3/text-to-image", {
  input: {
    prompt: "A vintage compass rose, engraving style",
    style: "vector_illustration",
    style_id: "engraving",
    image_size: "square_hd"
  }
});

const rasterUrl = rasterResult.data.images[0].url;
console.log("Raster generated:", rasterUrl);
```

### Step 2: Vectorize the Raster

```javascript
// Step 2: Convert raster to SVG
const svgResult = await fal.subscribe("fal-ai/recraft/vectorize", {
  input: {
    image_url: rasterUrl
  }
});

const svgUrl = svgResult.data.image.url;
console.log("SVG generated:", svgUrl);

// Download SVG content
const response = await fetch(svgUrl);
const svgContent = await response.text();
```

### Complete Pipeline (Python)

```python
import fal_client
import requests

def generate_vector_svg(prompt: str, style_id: str, colors: list = None) -> str:
    """
    Two-step pipeline: V3 vector style → vectorize → SVG string.
    Returns SVG content as string.
    """
    # Step 1: Generate vector-style raster
    raster_args = {
        "prompt": prompt,
        "style": "vector_illustration",
        "style_id": style_id,
        "image_size": "square_hd"
    }
    if colors:
        raster_args["colors"] = colors

    raster_result = fal_client.subscribe(
        "fal-ai/recraft/v3/text-to-image",
        arguments=raster_args
    )
    raster_url = raster_result["images"][0]["url"]

    # Step 2: Vectorize
    svg_result = fal_client.subscribe(
        "fal-ai/recraft/vectorize",
        arguments={"image_url": raster_url}
    )
    svg_url = svg_result["image"]["url"]

    # Download and return SVG content
    response = requests.get(svg_url)
    return response.text

# Usage
svg = generate_vector_svg(
    prompt="A vintage compass rose",
    style_id="engraving",
    colors=[{"r": 30, "g": 30, "b": 30}]
)
with open("compass.svg", "w") as f:
    f.write(svg)
```

---

## Colors Parameter Reference

All three endpoints accept a `colors` array to constrain the model's palette to brand colors. Pass up to 5 colors for best results.

```javascript
// Single brand color
colors: [{ r: 59, g: 130, b: 246 }]

// Full brand palette
colors: [
  { r: 59, g: 130, b: 246 },   // primary blue
  { r: 30, g: 64, b: 175 },    // dark blue
  { r: 255, g: 255, b: 255 },  // white
  { r: 15, g: 23, b: 42 }      // near-black
]
```

Convert hex to RGB for the API:

```javascript
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

// Usage
const brandColors = ["#3b82f6", "#1e40af", "#ffffff"].map(hexToRgb);
```

---

## Model Selection Guide

### By Output Requirement

| You need... | Use |
|-------------|-----|
| True SVG file, standard quality | `fal-ai/recraft/v4/text-to-vector` |
| True SVG file, maximum quality | `fal-ai/recraft/v4/pro/text-to-vector` |
| Raster with vector aesthetic | `fal-ai/recraft/v3/text-to-image` + `vector_illustration` |
| SVG with specific illustration style | V3 + `fal-ai/recraft/vectorize` pipeline |

### By Budget

| Budget per asset | Approach |
|-----------------|----------|
| Under $0.05 | V3 raster only ($0.04), no SVG |
| $0.08-0.09 | V4 direct SVG or V3 + vectorize pipeline |
| $0.30 | V4 Pro for highest quality SVG |

### By Style Need

| Style | Endpoint | style_id |
|-------|----------|----------|
| Clean logo/icon | V4 direct | — |
| Vintage/etched | V3 + vectorize | `engraving` or `linocut` |
| Sticker/badge | V3 + vectorize | `bold_stroke` or `colored_sticker` |
| Seamless pattern | V3 + vectorize | `seamless_pattern` |
| Technical diagram | V3 + vectorize | `line_circuit` or `chemistry` |
| Minimal line art | V3 + vectorize | `line_art` or `thin` |
| Pop/retro | V3 + vectorize | `pop_art` |
| Watercolor-style | V3 + vectorize | `watercolor` |

---

## Error Handling

| HTTP Status | Cause | Action |
|-------------|-------|--------|
| 401 | Invalid or missing FAL_KEY | Check `FAL_KEY` env var or `fal.config({credentials})` |
| 422 | Invalid parameter type or value | Check `style_id` spelling, `colors` format `{r,g,b}`, `image_size` value |
| 429 | Rate limit exceeded | Implement exponential backoff; use queue pattern for batch jobs |
| 500 | Model inference failure | Retry once; if persistent, simplify prompt or switch endpoint |

Wrap `fal.subscribe()` calls in try/catch and inspect `error.status` and `error.body` for validation details. The `422` body typically names the offending field.

For fal.ai client setup, authentication, and queue management patterns, see `references/fal-api-reference.md`.
For prompt engineering strategies specific to vector output, see `references/prompt-engineering.md`.
