# Image-to-SVG Conversion
Sources: fal.ai documentation (2025-2026), Recraft vectorization docs, Potrace documentation

This reference covers raster-to-SVG conversion methods for existing images. It assumes fal.ai client setup is already configured elsewhere.

## 1. When to Convert vs Generate Native

Decision table for choosing conversion rather than native vector generation.

| Situation | Convert Raster to SVG | Generate Native Vector | Why |
| --- | --- | --- | --- |
| You already have a raster asset (logo, scan, screenshot) | Yes | No | Preserve existing visual identity |
| You need pixel-accurate reproduction of a bitmap | Yes | No | Vectorization can simplify or distort |
| You need editable shapes for icon systems | Maybe | Yes | Native vectors reduce path noise |
| Input is a photo or complex texture | Maybe | No | Results are heavy and noisy |
| You need quick budget conversion | Yes | No | image2svg is cheapest |
| You need highest quality conversion | Yes | No | Prefer Recraft Vectorize or StarVector |
| You are designing new artwork | No | Yes | Avoid conversion artifacts |

Guidance:
- Convert if the asset already exists and must be preserved.
- Generate native if you can control style, palette, and shape complexity from scratch.

## 2. fal-ai/recraft/vectorize

Endpoint for high quality raster-to-SVG conversion.

Key constraints:
- Input formats: PNG, JPG, WEBP
- File size: < 5 MB
- Resolution: < 16 MP total, max dimension 4096 px, min dimension 256 px
- Output: SVG (`image/svg+xml`)
- Pricing: $0.01 per image

JavaScript (fal client):
```javascript
// Assumes fal client already configured
const result = await fal.subscribe("fal-ai/recraft/vectorize", {
  input: {
    image_url: "https://example.com/assets/logo.png"
  }
});

// result.data contains output URL(s)
console.log(result.data);
```

REST (curl):
```bash
curl -X POST "https://queue.fal.run/fal-ai/recraft/vectorize" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/assets/logo.png"}'
```

## 3. fal-ai/image2svg

Lower-cost vectorization with detail control.

Key constraints:
- Input formats: JPG, JPEG, PNG, WEBP, GIF
- Output: SVG (`image/svg+xml`)
- Pricing: $0.005 per image
- Detail control: use `detail` or model-specific parameter to trade fidelity vs simplicity

JavaScript (fal client):
```javascript
// Assumes fal client already configured
const result = await fal.subscribe("fal-ai/image2svg", {
  input: {
    image_url: "https://example.com/assets/icon.png",
    detail: 0.6
  }
});

console.log(result.data);
```

REST (curl):
```bash
curl -X POST "https://queue.fal.run/fal-ai/image2svg" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/assets/icon.png","detail":0.6}'
```

## 4. fal-ai/star-vector

AI vectorization model for complex shapes and cleaner output on illustrations.

Capabilities:
- Strong at illustration-style conversion
- Handles multi-color shapes better than classical trace
- Useful when Potrace yields too many jagged paths

JavaScript (fal client):
```javascript
// Assumes fal client already configured
const result = await fal.subscribe("fal-ai/star-vector", {
  input: {
    image_url: "https://example.com/assets/illustration.png"
  }
});

console.log(result.data);
```

REST (curl):
```bash
curl -X POST "https://queue.fal.run/fal-ai/star-vector" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/assets/illustration.png"}'
```

## 5. Two-Step Pipeline: Generate Raster then Vectorize

Use when you need custom style control but still want SVG output. The raster step produces a clean, flat image that vectorizes well.

Runnable Node.js example (uses fal client and storage upload):
```javascript
import fs from "node:fs";
import { fal } from "@fal-ai/client";

// Expects FAL_KEY in the environment and fal client already configured

async function generateRaster() {
  const result = await fal.subscribe("fal-ai/recraft/v3/text-to-image", {
    input: {
      prompt: "minimal flat icon of a delivery truck, solid colors, no gradients",
      style: "vector_illustration",
      image_size: "square_hd"
    }
  });
  return result.data.images[0].url;
}

async function vectorize(imageUrl) {
  const result = await fal.subscribe("fal-ai/recraft/vectorize", {
    input: {
      image_url: imageUrl
    }
  });
  return result.data;
}

async function main() {
  const rasterUrl = await generateRaster();
  const svgResult = await vectorize(rasterUrl);
  console.log({ rasterUrl, svgResult });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

Notes:
- The vectorization step works best when the raster has flat fills, limited colors, and crisp edges.
- If the generated raster is too detailed, reduce complexity in the prompt before vectorizing.

## 6. Local Conversion: Potrace CLI

Potrace is a classic bitmap-to-vector tracer. It is deterministic and works well for black-and-white or high-contrast inputs.

Install:
```bash
# macOS
brew install potrace

# Ubuntu
sudo apt-get install potrace
```

Usage (basic):
```bash
# Convert PNG to SVG (Potrace expects a bitmap, so convert first)
potrace input.pbm -s -o output.svg
```

Common workflow with ImageMagick:
```bash
# 1) Convert to grayscale
magick input.png -colorspace Gray gray.png

# 2) Increase contrast and binarize
magick gray.png -threshold 55% bw.pbm

# 3) Trace to SVG
potrace bw.pbm -s -o output.svg
```

Useful options:
- `-s`: SVG output
- `-o file.svg`: Output file
- `-t <n>`: Tolerance; higher reduces detail
- `-a <n>`: Corner threshold; higher keeps corners sharper
- `-O <n>`: Curve optimization; higher simplifies curves
- `--color <hex>`: Set output fill color for single-color traces

When to use Potrace:
- Simple logos, line art, and monochrome icons
- Need deterministic output in offline environments
- Need clean, minimal paths with strong contrast input

## 7. Input Preparation Checklist

Quality of the input image strongly affects vectorization results.

Preparation steps:
- Increase contrast between foreground and background
- Reduce noise and texture (blur or denoise, then sharpen edges)
- Flatten gradients into solid color bands
- Resize so the shortest side is at least 256 px
- Avoid photos with complex lighting or high-frequency detail

Practical tweaks:
- Use a white or solid background when possible
- Limit palette to 2-6 colors for icons or logos
- Remove drop shadows and glows before vectorization

## 8. Quality Comparison Table

| Input Type | Best Tool | Why | Notes |
| --- | --- | --- | --- |
| Simple monochrome logo | Potrace | Minimal paths, deterministic | Requires PBM/PGM input |
| Flat vector-style illustration | Recraft Vectorize | Handles multi-color flat fills | $0.01/image |
| Small icon (simple shapes) | image2svg | Cheapest, acceptable detail | Reduce detail to avoid noise |
| Hand-drawn sketch | Star Vector | Better curve interpretation | Still may need cleanup |
| Photo or textured art | None (avoid) | Vectorization bloats paths | Consider keeping raster |
| UI screenshot | Recraft Vectorize | Better at sharp edges | Expect heavy SVG |

## 9. Limitations and Gotchas

Common issues to watch:
- File size limits: Recraft Vectorize enforces <5 MB and <16 MP
- Color handling: Excessive colors inflate path count and file size
- Complex textures: Convert poorly and create bloated SVGs
- Embedded rasters: Some conversions may include image data rather than paths
- Over-detailing: Too high detail creates many small paths, hard to edit
- Small inputs: Under 256 px short side often produce jagged paths

Mitigations:
- Simplify before conversion (posterize, reduce colors)
- Target flat colors and strong edges
- Prefer higher resolution inputs for clean outlines
- Use Potrace for monochrome art instead of AI models

## 10. Troubleshooting Common Conversion Failures

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Photo produces thousands of paths | Too many colors and gradients | Posterize to 4-8 colors in ImageMagick before vectorizing |
| Text not converting cleanly | Low input resolution or anti-aliasing | Upscale to at least 2x, sharpen edges, then convert |
| Output SVG is 5+ MB | Complex input with fine detail | Reduce detail parameter (image2svg) or simplify input |
| Jagged curves on smooth shapes | Input resolution too low | Resize to at least 512 px on shortest side before tracing |
| Colors merge or bleed together | Low contrast between adjacent regions | Increase contrast and saturation before conversion |
| Recraft Vectorize returns 400 error | File exceeds 5 MB or 16 MP limit | Resize and compress input; check dimensions |
| SVG contains embedded raster data | Endpoint fell back to image embedding | Use a different endpoint; verify output content_type is `image/svg+xml` |
| Potrace output is all black | Input was not binarized | Run threshold step with ImageMagick before Potrace |
| Star Vector returns generic shapes | Input too abstract or low-contrast | Use Recraft Vectorize instead; provide cleaner input |
| Paths are editable but wrong color | Potrace default is black fill | Pass `--color #RRGGBB` to set fill color |

## 11. Pre-Processing Tips

Apply these transformations before sending an image to any vectorization endpoint. Pre-processing is the single highest-leverage step for improving output quality.

Resize to a clean working resolution:
```bash
# Resize so shortest side is 512 px, preserve aspect ratio
magick input.png -resize 512x512^ -gravity Center -extent 512x512 resized.png
```

Adjust contrast to separate foreground from background:
```bash
# Boost contrast and saturation
magick resized.png -modulate 100,150 -contrast-stretch 5%x5% contrast.png
```

Remove background before vectorizing (for logos on white):
```bash
# Flood-fill white background to transparent
magick contrast.png -fuzz 10% -transparent white nobg.png
```

Posterize to reduce color count:
```bash
# Reduce to 6 color levels — good for logos and icons
magick nobg.png -posterize 6 posterized.png
```

Sharpen edges after posterization:
```bash
# Unsharp mask to crisp up edges before tracing
magick posterized.png -unsharp 0x1+1.5+0.05 sharpened.png
```

Run all steps in sequence:
```bash
magick input.png \
  -resize 512x512^ -gravity Center -extent 512x512 \
  -modulate 100,150 -contrast-stretch 5%x5% \
  -posterize 6 \
  -unsharp 0x1+1.5+0.05 \
  ready-for-vectorize.png
```

## 12. Batch Conversion Pattern

Convert multiple images in a pipeline using the fal client. Use `Promise.allSettled` to handle partial failures without aborting the batch.

```javascript
import { fal } from "@fal-ai/client";
import fs from "node:fs/promises";

// Expects FAL_KEY in environment and fal client configured

async function vectorizeBatch(imageUrls, endpoint = "fal-ai/recraft/vectorize") {
  const tasks = imageUrls.map((url) =>
    fal.subscribe(endpoint, { input: { image_url: url } })
      .then((result) => ({ url, status: "ok", data: result.data }))
      .catch((err) => ({ url, status: "error", error: err.message }))
  );

  const results = await Promise.allSettled(tasks);
  return results.map((r) => (r.status === "fulfilled" ? r.value : r.reason));
}

async function main() {
  const urls = [
    "https://example.com/logo-a.png",
    "https://example.com/logo-b.png",
    "https://example.com/icon-c.png"
  ];

  const results = await vectorizeBatch(urls);

  for (const r of results) {
    if (r.status === "ok") {
      console.log("Converted:", r.url, "->", r.data);
    } else {
      console.error("Failed:", r.url, r.error);
    }
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

Rate limiting note: fal.ai enforces per-account concurrency limits. If batches exceed the limit, add a concurrency cap using a semaphore or process in chunks of 5-10 images at a time.
