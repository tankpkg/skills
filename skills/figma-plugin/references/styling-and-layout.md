# Styling & Layout Properties

Sources: Official Figma Plugin API Reference, @figma/plugin-typings

This reference covers the manipulation of visual properties (fills, strokes, effects) and spatial organization (Auto-Layout, Constraints) for Figma nodes.

## 1. CRITICAL: Immutable Array Pattern

In the Figma Plugin API, properties that return arrays (like `fills`, `strokes`, and `effects`) are **immutable by reference**. You cannot modify an element within the array directly and expect the UI to update.

```typescript
// ❌ WRONG - This will not work
node.fills[0].color.r = 0.5

// ✅ CORRECT - Clone, modify, and reassign the entire array
function clone(val: any) {
  return JSON.parse(JSON.stringify(val))
}

const fills = clone(node.fills)
fills[0] = { ...fills[0], color: { r: 0.5, g: 0, b: 1 } }
node.fills = fills

// RECOMMENDED: Utility Helpers
// Set a single solid color quickly
node.fills = [figma.util.solidPaint('#FF00FF')]

// Set solid color with alpha (8-digit hex)
node.fills = [figma.util.solidPaint('#FF00FF88')]
```

## 2. Paint Types & Color Formats

A "Paint" in Figma can be a solid color, a gradient, an image, or a video.

### Color Format: RGB vs RGBA
Figma uses a 0 to 1 scale for color channels, not 0 to 255.
- `RGB`: `{ r: number, g: number, b: number }` (all 0-1)
- `RGBA`: `{ r: number, g: number, b: number, a: number }` (all 0-1)

#### Hex to RGB Helper
```typescript
function hexToRgb(hex: string): RGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16) / 255,
    g: parseInt(result[2], 16) / 255,
    b: parseInt(result[3], 16) / 255
  } : { r: 0, g: 0, b: 0 }
}
```

### Type Definitions
- **SolidPaint**: `{ type: 'SOLID', color: RGB, opacity?: number, visible?: boolean, blendMode?: BlendMode }`
- **GradientPaint**: 
  - `type`: `'GRADIENT_LINEAR' | 'GRADIENT_RADIAL' | 'GRADIENT_ANGULAR' | 'GRADIENT_DIAMOND'`
  - `gradientTransform`: `Transform` (2x3 matrix)
  - `gradientStops`: `readonly ColorStop[]` where `ColorStop` is `{ position: number, color: RGBA }`
- **ImagePaint**: 
  - `type`: `'IMAGE'`
  - `scaleMode`: `'FILL' | 'FIT' | 'CROP' | 'TILE'`
  - `imageHash`: `string`
  - `imageTransform?`: `Transform`
  - `scalingFactor?`: `number`
  - `rotation?`: `number`
  - `filters?`: `ImageFilters`
- **VideoPaint**: `{ type: 'VIDEO', videoHash: string, scaleMode: 'FILL' | 'FIT' | 'CROP' | 'TILE', ... }`

## 3. Working with Images

Images are stored in Figma as `Image` objects, and applied to nodes via the `imageHash` property in an `ImagePaint`.

### Creating an Image
```typescript
// Main thread: Create image from Uint8Array
const image = figma.createImage(bytes)
const imageHash = image.hash

// Apply to node
node.fills = [{
  type: 'IMAGE',
  scaleMode: 'FILL',
  imageHash: imageHash
}]
```

### Fetching from URL (UI → Main Workflow)
Since the main plugin thread cannot use `fetch()`, you must perform network requests in the UI (iframe).

**In UI (ui.html/js):**
```javascript
async function uploadImage(url) {
  const response = await fetch(url)
  const buffer = await response.arrayBuffer()
  window.parent.postMessage({ pluginMessage: { type: 'upload-image', bytes: new Uint8Array(buffer) } }, '*')
}
```

**In Main (code.ts):**
```typescript
figma.ui.onmessage = (msg) => {
  if (msg.type === 'upload-image') {
    const image = figma.createImage(msg.bytes)
    const node = figma.currentPage.selection[0]
    if ('fills' in node) {
      node.fills = [{ type: 'IMAGE', scaleMode: 'FILL', imageHash: image.hash }]
    }
  }
}
```

## 4. Strokes

Strokes follow the same immutable pattern as fills.

- **Properties**:
  - `strokes`: `readonly Paint[]`
  - `strokeWeight`: `number`
  - `strokeAlign`: `'CENTER' | 'INSIDE' | 'OUTSIDE'`
  - `strokeCap`: `'NONE' | 'ROUND' | 'SQUARE' | 'ARROW_LINES' | 'ARROW_EQUILATERAL'`
  - `strokeJoin`: `'MITER' | 'BEVEL' | 'ROUND'`
  - `dashPattern`: `readonly number[]` (e.g., `[10, 5]` for 10px dash, 5px gap)

### Individual Side Weights
You can set weights for individual sides if the node supports it (mostly Frames and Rectangles):
- `strokeTopWeight`: `number`
- `strokeRightWeight`: `number`
- `strokeBottomWeight`: `number`
- `strokeLeftWeight`: `number`

## 5. Effects

Effects include shadows and blurs.

```typescript
type Effect = DropShadowEffect | InnerShadowEffect | LayerBlurEffect | BackgroundBlurEffect

interface DropShadowEffect {
  readonly type: 'DROP_SHADOW'
  readonly color: RGBA
  readonly offset: Vector // { x: number, y: number }
  readonly radius: number
  readonly spread?: number
  readonly visible: boolean
  readonly blendMode: BlendMode
  readonly showShadowBehindNode?: boolean
}

interface InnerShadowEffect {
  readonly type: 'INNER_SHADOW'
  readonly color: RGBA
  readonly offset: Vector
  readonly radius: number
  readonly spread?: number
  readonly visible: boolean
  readonly blendMode: BlendMode
}

interface LayerBlurEffect {
  readonly type: 'LAYER_BLUR'
  readonly radius: number
  readonly visible: boolean
}

interface BackgroundBlurEffect {
  readonly type: 'BACKGROUND_BLUR'
  readonly radius: number
  readonly visible: boolean
}
```

## 6. Auto-Layout (Flexbox Equivalent)

Auto-Layout is applied to `FrameNode` or `ComponentNode`.

```typescript
// 1. Enable Auto-Layout
frame.layoutMode = 'HORIZONTAL' // row
// frame.layoutMode = 'VERTICAL'   // column
// frame.layoutMode = 'NONE'       // absolute positioning for children

// 2. Padding
frame.paddingLeft = 16
frame.paddingRight = 16
frame.paddingTop = 16
frame.paddingBottom = 16

// 3. Spacing (Gap)
frame.itemSpacing = 8         // Space between items
frame.counterAxisSpacing = 8  // Space between rows/cols when wrapping

// 4. Alignment
// primaryAxis controls 'justify-content'
frame.primaryAxisAlignItems = 'MIN' | 'MAX' | 'CENTER' | 'SPACE_BETWEEN'

// counterAxis controls 'align-items'
frame.counterAxisAlignItems = 'MIN' | 'MAX' | 'CENTER' | 'BASELINE'

// 5. Sizing Mode
// FIXED: User defined size
// AUTO: Shrink wrap content (deprecated in favor of layoutSizing)
frame.primaryAxisSizingMode = 'FIXED' | 'AUTO'
frame.counterAxisSizingMode = 'FIXED' | 'AUTO'

// 6. Wrapping
frame.layoutWrap = 'NO_WRAP' | 'WRAP'
```

## 7. Auto-Layout → CSS Flexbox Mapping

| Figma Property | CSS Equivalent |
| :--- | :--- |
| `layoutMode: 'HORIZONTAL'` | `flex-direction: row` |
| `layoutMode: 'VERTICAL'` | `flex-direction: column` |
| `primaryAxisAlignItems: 'MIN'` | `justify-content: flex-start` |
| `primaryAxisAlignItems: 'CENTER'` | `justify-content: center` |
| `primaryAxisAlignItems: 'MAX'` | `justify-content: flex-end` |
| `primaryAxisAlignItems: 'SPACE_BETWEEN'` | `justify-content: space-between` |
| `counterAxisAlignItems: 'MIN'` | `align-items: flex-start` |
| `counterAxisAlignItems: 'CENTER'` | `align-items: center` |
| `counterAxisAlignItems: 'MAX'` | `align-items: flex-end` |
| `itemSpacing` | `gap` |
| `layoutWrap: 'WRAP'` | `flex-wrap: wrap` |
| `child.layoutGrow = 1` | `flex-grow: 1` |
| `child.layoutAlign = 'STRETCH'` | `align-self: stretch` |

## 8. Grid Layout

Figma introduced native Grid support within the Auto-Layout system recently.

```typescript
frame.layoutMode = 'GRID'
frame.gridRowCount = 3
frame.gridColumnCount = 3
frame.gridRowGap = 8
frame.gridColumnGap = 8
```

## 9. Child Layout Properties

These properties are set on the **child node** inside an Auto-Layout parent.

- **layoutAlign**: `'INHERIT' | 'STRETCH' | 'MIN' | 'CENTER' | 'MAX'`
  - Determines if the child stretches to fill the counter axis.
- **layoutGrow**: `0` (Fixed) or `1` (Fill container)
  - Determines if the child grows to fill the primary axis.
- **layoutSizingHorizontal / layoutSizingVertical**:
  - `'FIXED'`: Set width/height explicitly.
  - `'HUG'`: Size based on child content.
  - `'FILL'`: Stretch to fill parent space.
- **layoutPositioning**: `'AUTO'` (Part of flow) or `'ABSOLUTE'` (Ignored by Auto-Layout flow)

## 10. Constraints

Constraints determine how a node responds when its parent frame is resized (only applicable when the parent is NOT using Auto-Layout).

```typescript
node.constraints = {
  horizontal: 'MIN' | 'CENTER' | 'MAX' | 'STRETCH' | 'SCALE',
  vertical: 'MIN' | 'CENTER' | 'MAX' | 'STRETCH' | 'SCALE'
}
```

## 11. Corner Radius & Smoothing

- **Uniform Radius**: `node.cornerRadius = 8`
- **Individual Radii**:
  - `node.topLeftRadius = 8`
  - `node.topRightRadius = 8`
  - `node.bottomRightRadius = 8`
  - `node.bottomLeftRadius = 8`
- **Corner Smoothing**: `node.cornerSmoothing = 0.6`
  - Range: `0` to `1`.
  - `0.6` approximates the "continuous" curve used in iOS (Squircle).

## 12. Blend Modes

Standard blend modes available for fills, strokes, and layers.

- `NORMAL`
- `DARKEN`
- `MULTIPLY`
- `COLOR_BURN`
- `LIGHTEN`
- `SCREEN`
- `COLOR_DODGE`
- `OVERLAY`
- `SOFT_LIGHT`
- `HARD_LIGHT`
- `DIFFERENCE`
- `EXCLUSION`
- `HUE`
- `SATURATION`
- `COLOR`
- `LUMINOSITY`

## Implementation Checklist
1. Did I clone the array before modifying `fills`/`strokes`/`effects`?
2. Are my color values between `0` and `1`?
3. If using `IMAGE`, did I create the image and use the `hash`?
4. Is `layoutMode` set before trying to adjust `itemSpacing` or padding?
5. For absolute positioning inside Auto-Layout, did I set `layoutPositioning = 'ABSOLUTE'`?
