# SVG Optimization

Sources: SVGO documentation, SVG specification, web performance guides (2025-2026)

Covers: Cleaning AI-generated SVGs, SVGO configuration, manual cleanup patterns, file size targets, accessibility, dark mode preparation, animation preparation, and validation.

## 1. AI SVG Common Problems

AI image generators produce SVGs with predictable defects. Identify these before running any optimizer.

| Problem | Detection | Impact |
|---------|-----------|--------|
| Too many paths | `grep -c '<path' file.svg` — icons >20, illustrations >200 | Slow render, large file |
| Poor grouping | All paths at root level, no `<g>` structure | Blocks animation, no inheritance |
| Missing viewBox | `grep viewBox file.svg` returns nothing | Cannot scale responsively |
| Embedded rasters | `grep 'data:image/' file.svg` finds matches | Defeats vector purpose, huge size |
| Excessive precision | Coordinates like `123.456789` | Inflated file, no visual benefit |
| Redundant transforms | `transform="translate(0,0) scale(1,1)"` | Wasted bytes, animation confusion |

**Embedded rasters** are the most critical: if `data:image/png;base64` appears, the file is not truly vector. Re-generate with explicit vector-only prompts or remove the `<image>` element.

**Too many paths** for simple shapes means the generator traced a raster internally. SVGO's `mergePaths` reduces count; if still above 50 for a simple icon, redraw manually.

---

## 2. SVGO Configuration

Save as `svgo.config.js`. This configuration targets AI-generated SVGs specifically.

```javascript
// svgo.config.js
module.exports = {
  multipass: true,           // Run until no further reduction — critical for AI output
  js2svg: { pretty: false },
  plugins: [
    // Strip editor metadata
    { name: 'removeDoctype' },
    { name: 'removeXMLProcInst' },
    { name: 'removeComments' },
    { name: 'removeMetadata' },
    { name: 'removeEditorsNSData' },  // Removes Sketch, Illustrator, Inkscape namespaces

    // NEVER remove viewBox
    { name: 'removeViewBox', active: false },

    // Structure cleanup
    { name: 'removeEmptyAttrs' },
    { name: 'removeEmptyContainers' },
    { name: 'removeUnusedNS' },
    { name: 'removeUselessDefs' },
    { name: 'cleanupIds', params: { minify: true } },

    // Numeric precision — 1 for icons, 2 for illustrations
    { name: 'cleanupNumericValues', params: { floatPrecision: 2 } },
    { name: 'convertPathData', params: { floatPrecision: 2, transformPrecision: 2 } },

    // Transform and attribute optimization
    { name: 'convertTransform' },
    { name: 'removeUselessStrokeAndFill' },
    { name: 'convertColors', params: { shorthex: true, shortname: true } },
    { name: 'sortAttrs' },                // Improves gzip compression

    // Path and group merging
    { name: 'mergePaths' },
    { name: 'collapseGroups' },
    { name: 'moveElemsAttrsToGroup' },
    { name: 'moveGroupAttrsToElems' },

    // Shape simplification
    { name: 'convertShapeToPath' },
    { name: 'convertEllipseToCircle' },
    { name: 'mergePaths' },              // Second pass after shape conversion
  ],
};
```

### CLI Commands

```bash
# Single file
npx svgo --config svgo.config.js input.svg -o output.svg

# Batch directory
npx svgo --config svgo.config.js -f ./raw/ -o ./optimized/

# Dry run — show reduction without writing
npx svgo --config svgo.config.js input.svg --dry-run
```

### Precision by Use Case

| Use Case | floatPrecision |
|----------|---------------|
| Icon (16-48px) | 1 |
| Logo / Illustration | 2 |
| Data visualization | 3 |

---

## 3. Manual Cleanup Patterns

Run SVGO first. Apply these patterns to problems SVGO cannot fix automatically.

### Fix Missing viewBox

```javascript
function fixViewBox(svgString) {
  if (/viewBox=/.test(svgString)) return svgString;

  const w = parseFloat(svgString.match(/width="([^"]+)"/)?.[1]);
  const h = parseFloat(svgString.match(/height="([^"]+)"/)?.[1]);
  if (!w || !h) return svgString;

  return svgString
    .replace(/<svg/, `<svg viewBox="0 0 ${w} ${h}"`)
    .replace(/\s+width="[^"]*"/, '')
    .replace(/\s+height="[^"]*"/, '');
}
```

### Remove Embedded Raster Images

```javascript
function removeEmbeddedRasters(svgString) {
  return svgString
    .replace(/<image[^>]*data:image\/[^>]*\/>/g, '')
    .replace(/<image[^>]*data:image\/[\s\S]*?<\/image>/g, '');
}
```

### Convert Inline Styles to Presentation Attributes

Inline `style` attributes block CSS overrides and prevent `currentColor` inheritance.

```javascript
const PRESENTATION_PROPS = new Set([
  'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
  'opacity', 'fill-opacity', 'stroke-opacity', 'fill-rule', 'clip-rule',
]);

function inlineStyleToAttrs(svgString) {
  return svgString.replace(/style="([^"]*)"/g, (_, styleContent) => {
    const attrs = [];
    const remaining = [];
    styleContent.split(';').filter(Boolean).forEach(rule => {
      const [prop, val] = rule.split(':').map(s => s.trim());
      if (PRESENTATION_PROPS.has(prop)) {
        attrs.push(`${prop}="${val}"`);
      } else {
        remaining.push(`${prop}:${val}`);
      }
    });
    return remaining.length
      ? `${attrs.join(' ')} style="${remaining.join('; ')}"`
      : attrs.join(' ');
  });
}
```

---

## 4. File Size Targets

These targets apply after SVGO optimization. Exceeding the max indicates structural problems.

| Use Case | Target | Max | Path Count |
|----------|--------|-----|------------|
| UI icon (16-48px) | < 1 KB | 2 KB | 1-8 |
| Logo (simple) | < 3 KB | 5 KB | 5-20 |
| Logo (complex) | < 8 KB | 15 KB | 20-60 |
| Spot illustration | < 10 KB | 20 KB | 20-80 |
| Hero illustration | < 25 KB | 50 KB | 50-200 |
| Animated SVG | < 15 KB | 30 KB | 10-60 |

If a file exceeds the max after SVGO, diagnose in order:
1. `grep 'data:image/' file.svg` — embedded rasters
2. `grep -c '<path' file.svg` — excessive path count
3. `grep -c '<defs' file.svg` — duplicate definitions
4. Consider PNG/WebP if the design is inherently photographic

---

## 5. Accessibility

AI-generated SVGs have no accessibility metadata. Add before deploying.

### Semantic SVG

```svg
<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  role="img"
  aria-labelledby="svg-title svg-desc"
>
  <title id="svg-title">Shopping cart</title>
  <desc id="svg-desc">Icon showing a cart with two wheels</desc>
  <!-- paths -->
</svg>
```

### Decorative SVG (No Semantic Meaning)

```svg
<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24">
  <!-- decorative paths -->
</svg>
```

### Programmatic Addition

```javascript
function addAccessibility(svgString, title, description, isDecorative = false) {
  if (isDecorative) {
    return svgString.replace('<svg', '<svg aria-hidden="true" focusable="false"');
  }
  const ariaAttr = description
    ? 'role="img" aria-labelledby="svg-title svg-desc"'
    : 'role="img" aria-labelledby="svg-title"';
  const titleEl = `<title id="svg-title">${title}</title>`;
  const descEl = description ? `<desc id="svg-desc">${description}</desc>` : '';
  return svgString
    .replace('<svg', `<svg ${ariaAttr}`)
    .replace(/(<svg[^>]*>)/, `$1\n  ${titleEl}${descEl ? '\n  ' + descEl : ''}`);
}
```

---

## 6. Dark Mode Preparation

### currentColor Technique

Replace hardcoded fill/stroke values with `currentColor` to inherit the CSS `color` property. The parent element's color cascades into the SVG.

```svg
<!-- Before -->
<path fill="#1a1a1a" d="M12 2..."/>

<!-- After — inherits from CSS color property -->
<path fill="currentColor" d="M12 2..."/>
```

```css
.icon { color: #1a1a1a; }
@media (prefers-color-scheme: dark) { .icon { color: #f5f5f5; } }
```

### CSS Custom Properties for Multi-Color SVGs

```svg
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <style>
    :root { --c-primary: #1a1a1a; --c-accent: #3b82f6; }
    @media (prefers-color-scheme: dark) {
      :root { --c-primary: #f5f5f5; --c-accent: #60a5fa; }
    }
  </style>
  <path fill="var(--c-primary)" d="M..."/>
  <circle fill="var(--c-accent)" cx="24" cy="24" r="4"/>
</svg>
```

### Approach Selection

| Scenario | Approach |
|----------|----------|
| Single-color icon | `currentColor` |
| Multi-color illustration | CSS custom properties |
| SVG used as `<img>` tag | Embed `<style>` with media query inside SVG |
| Inline SVG in HTML | Either approach works |

---

## 7. Animation Preparation

Structure AI SVGs for animation before running SVGO. `collapseGroups` and `cleanupIds` destroy animation targets.

### Preserve Animation Target IDs

```javascript
// In svgo.config.js
{
  name: 'cleanupIds',
  params: {
    minify: false,
    preserve: ['body', 'arm-left', 'arm-right', 'wheel', 'shadow'],
  },
},
```

### Group Structure for Animation

```svg
<svg viewBox="0 0 200 200">
  <g id="shadow">
    <ellipse cx="100" cy="185" rx="40" ry="8" fill="#00000033"/>
  </g>
  <g id="body">
    <path d="M..."/>
  </g>
  <g id="arm-left" style="transform-box: fill-box; transform-origin: center">
    <path d="M..."/>
  </g>
</svg>
```

### transform-origin in SVG

SVG elements use the SVG coordinate system for `transform-origin`, not the element's bounding box. Always set `transform-box: fill-box` alongside `transform-origin: center` to get expected behavior:

```css
#spinner {
  transform-box: fill-box;
  transform-origin: center;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

### Path Simplification for Motion

CSS `offset-path` and morphing require smooth, low-node paths. Target under 12 nodes for motion paths, equal node count between morph states.

```bash
# Simplify paths with Inkscape CLI
inkscape --actions="select-all; path-simplify; export-filename:simplified.svg; export-plain-svg" input.svg
```

---

## 8. Validation

### Structural Checks

```bash
# XML validity
xmllint --noout input.svg

# Check for external references (breaks CSP and sandboxed contexts)
grep -oP '(href|src|xlink:href)="https?://[^"]*"' input.svg

# Check for embedded rasters
grep 'data:image/' input.svg

# Check for script elements (security risk)
grep '<script' input.svg
```

### Programmatic Validation

```javascript
function validateSVG(svgString) {
  const errors = [];
  if (!/<svg[^>]+viewBox/.test(svgString)) errors.push('Missing viewBox');
  if (/href="https?:\/\//.test(svgString)) errors.push('External href reference');
  if (/data:image\//.test(svgString)) errors.push('Embedded raster data');
  if (/<script/.test(svgString)) errors.push('Script element present');
  return { valid: errors.length === 0, errors };
}
```

### Common Validation Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Blank render | Missing viewBox | Add `viewBox="0 0 w h"` |
| Broken in `<img>` | External CSS reference | Inline all styles |
| CSP violation | External font or script | Remove or inline |
| Screen reader silent | Missing `role` and `title` | Add accessibility attributes |
| Animation not working | SVGO removed IDs | Preserve IDs in SVGO config |
| Wrong colors in dark mode | Hardcoded hex values | Convert to `currentColor` or CSS variables |
| Huge file after SVGO | Embedded raster | Remove `<image data:image>` elements |

For integration into React, Vue, or build pipelines, see `references/svg-integration-patterns.md`.
