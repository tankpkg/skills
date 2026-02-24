# Text & Typography

Sources: Official Figma Plugin API - Working with Text, Working with Rich Text

Working with text in Figma is fundamentally different from other nodes because of the dependency on font files. This reference covers the lifecycle of text nodes, from font loading to complex rich-text manipulations.

## 1. CRITICAL: The Font Loading Lifecycle

The most common error in Figma plugin development is attempting to modify a text property without the required font being loaded. Text properties are not just data; they require the actual font engine to be active for that specific font family and style.

### The Golden Rule
**You must await font loading before changing any text content or typography property.**

```typescript
// Pattern A: Loading a specific font for a new node
const textNode = figma.createText()
const font = { family: 'Inter', style: 'Regular' }
await figma.loadFontAsync(font)
textNode.fontName = font
textNode.characters = 'Loaded and safe'

// Pattern B: Loading all fonts used in an existing mixed-style node
const allFonts = node.getRangeAllFontNames(0, node.characters.length)
await Promise.all(allFonts.map(font => figma.loadFontAsync(font)))

// Pattern C: Checking for missing fonts (Critical for production)
// If a user doesn't have the font installed on their system, 
// hasMissingFont will be true. Plugins CANNOT load fonts the user doesn't have.
if (textNode.hasMissingFont) {
  figma.notify('Cannot edit: font is missing from your system', { error: true })
  return
}
```

## 2. Property Dependency Matrix

Not all properties on a `TextNode` require a font load. Understanding this distinction prevents unnecessary `await` calls and clarifies why some edits fail while others succeed.

| Requires Font Load | Does NOT Require Font Load |
| :--- | :--- |
| `characters` (content) | `fills`, `fillStyleId` |
| `fontSize` | `strokes`, `strokeWeight`, `strokeAlign` |
| `fontName` | `strokeStyleId`, `dashPattern` |
| `textStyleId` | `opacity`, `blendMode` |
| `textCase` | `visible`, `locked` |
| `textDecoration` | `name` |
| `letterSpacing` | `effects`, `effectStyleId` |
| `lineHeight` | `layoutAlign`, `layoutGrow` |
| `leadingTrim` | `constraints` |
| `paragraphIndent` | `exportSettings` |
| `paragraphSpacing` | `relativeTransform`, `x`, `y` |

## 3. Creating Text Nodes

When creating text, the node is initialized with a default font (usually Inter Regular). However, it is best practice to explicitly load and set your desired font immediately.

```typescript
async function createHeading(content: string) {
  const text = figma.createText()
  
  // 1. Load font
  const font: FontName = { family: 'Roboto', style: 'Bold' }
  await figma.loadFontAsync(font)
  
  // 2. Set properties
  text.fontName = font
  text.characters = content
  text.fontSize = 32
  text.textAlignHorizontal = 'CENTER'
  
  return text
}
```

## 4. Comprehensive Property Reference

| Property | Type | Values / Notes |
| :--- | :--- | :--- |
| `characters` | `string` | The raw text content. |
| `fontSize` | `number \| figma.mixed` | Size in pixels. |
| `fontName` | `FontName \| figma.mixed` | `{ family: string, style: string }` |
| `fontWeight` | `number \| figma.mixed` | Numeric weight (100-900). |
| `textCase` | `string \| figma.mixed` | `'ORIGINAL'`, `'UPPER'`, `'LOWER'`, `'TITLE'`, `'SMALL_CAPS'`, `'SMALL_CAPS_FORCED'` |
| `textDecoration` | `string \| figma.mixed` | `'NONE'`, `'UNDERLINE'`, `'STRIKETHROUGH'` |
| `letterSpacing` | `LetterSpacing \| figma.mixed` | `{ value: number, unit: 'PIXELS' \| 'PERCENT' }` |
| `lineHeight` | `LineHeight \| figma.mixed` | `{ value: number, unit: 'PIXELS' \| 'PERCENT' }` or `{ unit: 'AUTO' }` |
| `paragraphIndent` | `number` | Indentation of the first line of paragraphs. |
| `paragraphSpacing` | `number` | Space between paragraphs. |
| `textAlignHorizontal`| `string` | `'LEFT'`, `'CENTER'`, `'RIGHT'`, `'JUSTIFIED'` |
| `textAlignVertical` | `string` | `'TOP'`, `'CENTER'`, `'BOTTOM'` |
| `textAutoResize` | `string` | `'NONE'`, `'WIDTH_AND_HEIGHT'`, `'HEIGHT'`, `'TRUNCATE'` |
| `leadingTrim` | `string` | `'NONE'`, `'CAP_HEIGHT'` |
| `openTypeFeatures` | `Object` | Key-value pairs of feature tags (e.g., `{ 'ss01': 1 }`). |

## 5. Mixed Styles (figma.mixed)

A `TextNode` can have different styles for different characters. When you query a property like `fontSize` on such a node, Figma returns the `figma.mixed` symbol.

### Detection
```typescript
if (textNode.fontSize === figma.mixed) {
  console.log("The node has multiple font sizes.")
}
```

### Range Methods
To get or set properties for specific substrings, use the Range API.

```typescript
const start = 0
const end = 5 // Exclusive

// GETTERS
const subFont = textNode.getRangeFontName(start, end)
const subFills = textNode.getRangeFills(start, end)

// SETTERS
// All setters require font loading for the range if modifying typography
textNode.setRangeFontSize(start, end, 24)
textNode.setRangeTextCase(start, end, 'UPPER')
textNode.setRangeLetterSpacing(start, end, { value: 1.2, unit: 'PIXELS' })
textNode.setRangeTextDecoration(start, end, 'STRIKETHROUGH')

// Non-typography range setters (don't require font load)
textNode.setRangeFills(start, end, [{ type: 'SOLID', color: { r: 1, g: 0, b: 0 } }])
```

## 6. Styled Text Segments

Iterating through a text node character-by-character is inefficient. `getStyledTextSegments` is the modern, performant way to parse a text node with mixed styling. It groups contiguous characters with identical properties.

```typescript
// Pass an array of properties you want to group by
const segments = textNode.getStyledTextSegments([
  'fontName', 
  'fontSize', 
  'fills', 
  'textDecoration'
])

for (const segment of segments) {
  console.log(`Text: "${segment.characters}"`)
  console.log(`Range: ${segment.start} to ${segment.end}`)
  console.log(`Font: ${segment.fontName.family} ${segment.fontName.style}`)
  
  if (segment.textDecoration === 'UNDERLINE') {
    // Perform logic for underlined text
  }
}
```

## 7. Content Manipulation

Modifying the `characters` property directly overwrites the entire node. For surgical edits, use insertion and deletion methods. Note that these methods also preserve styles as much as possible, but might require font loading if they cause text reflow.

```typescript
// Insert text at index 5
textNode.insertCharacters(5, "Inserted Content")

// Delete text from index 10 to 15
textNode.deleteCharacters(10, 15)

// Append text
textNode.insertCharacters(textNode.characters.length, " The End.")
```

## 8. OpenType Features

OpenType features allow access to advanced typographic capabilities like stylistic alternates, ligatures, and fractions.

```typescript
textNode.openTypeFeatures = {
  'ss01': 1, // Stylistic Set 01 (On)
  'ss02': 0, // Stylistic Set 02 (Off)
  'liga': 1, // Standard Ligatures
  'dlig': 1, // Discretionary Ligatures
  'frac': 1, // Fractions
  'smcp': 1, // Small Caps
  'onum': 1, // Oldstyle Figures
}
```
*Note: Support varies by font family. Setting a feature on a font that doesn't support it will have no visual effect.*

## 9. Text Styles

`TextStyle` objects represent reusable typographic definitions in the Figma document.

### Creating and Modifying Styles
```typescript
const h1Style = figma.createTextStyle()
h1Style.name = 'Typography/H1'
h1Style.fontSize = 48
h1Style.fontName = { family: 'Inter', style: 'Black' }
h1Style.lineHeight = { value: 120, unit: 'PERCENT' }
```

### Applying Styles to Nodes
Applying a style ID is asynchronous because it may trigger a font load.

```typescript
await textNode.setTextStyleIdAsync(h1Style.id)

// To apply to a range
await textNode.setRangeTextStyleIdAsync(0, 5, h1Style.id)
```

### Fetching Local Styles
```typescript
const localStyles = figma.getLocalTextStyles()
const brandStyle = localStyles.find(s => s.name === 'Brand/Primary')
```

## 10. Rich Text (Metadata & Links)

Figma supports rich text in certain metadata fields, most notably `Component.description` and `ComponentSet.description`. This uses a different internal representation than `TextNode`.

### Hyperlinks in TextNodes
Text nodes can contain clickable links within their characters.

```typescript
// Set a link for a range
textNode.setRangeHyperlink(0, 10, { 
  type: 'URL', 
  value: 'https://figma.com' 
})

// Check for links
const link = textNode.getRangeHyperlink(0, 10)
if (link !== figma.mixed && link?.type === 'URL') {
  console.log(link.value)
}
```

## 11. Safe Text Edit Pattern

In production, user-installed fonts are unpredictable. Use a robust wrapper for all text edits to prevent plugin crashes.

```typescript
/**
 * Safely updates characters in a TextNode by handling missing 
 * fonts and loading existing ones.
 */
async function safeTextUpdate(node: TextNode, newText: string): Promise<boolean> {
  // 1. Check for missing fonts (Unrecoverable by plugin)
  if (node.hasMissingFont) {
    figma.notify('Update failed: Some fonts are missing from your system.', { error: true })
    return false
  }

  try {
    // 2. Load all fonts currently used in the node
    const fonts = node.getRangeAllFontNames(0, node.characters.length)
    await Promise.all(fonts.map(f => figma.loadFontAsync(f)))

    // 3. Perform the update
    node.characters = newText
    return true
  } catch (err) {
    console.error('Font loading failed', err)
    figma.notify('An error occurred while loading fonts.', { error: true })
    return false
  }
}
```

## 12. Typography Variables

Figma allows binding variables to specific typography properties. This enables "Themeable" typography.

### Supported Bindings
You can bind variables to:
- `fontFamily`
- `fontStyle`
- `fontWeight`
- `fontSize`
- `lineHeight`
- `letterSpacing`
- `paragraphSpacing`
- `paragraphIndent`

### Usage
```typescript
// Bind the font size to a variable
const fontSizeVar = await figma.variables.getVariableByIdAsync('VariableID:...')
if (fontSizeVar) {
  textNode.setBoundVariable('fontSize', fontSizeVar)
}

// Substring binding
textNode.setRangeBoundVariable(0, 5, 'fontWeight', weightVar)
```

## 13. Common Pitfalls & Tips

### Line Height Math
`LineHeight` units are critical.
- `unit: 'AUTO'`: Let the font decide.
- `unit: 'PERCENT'`: Often confusing as it is relative to font size (150% of 16px = 24px).
- `unit: 'PIXELS'`: Absolute value.

### Letter Spacing
Like line height, letter spacing can be `PIXELS` or `PERCENT`. When converting from CSS, remember that CSS `em` is often equivalent to Figma `PERCENT` (0.02em = 2%).

### Hidden Characters
`textNode.characters` returns exactly what is in the buffer. This includes:
- `\n`: Line feeds.
- `\u2028`: Line separators (often result of copy-pasting from other apps).
- Soft hyphens and other non-printing characters.

Always sanitize input if your plugin relies on exact string matching.

### Auto-Resize Behavior
If you set `textAutoResize = 'WIDTH_AND_HEIGHT'`, the `width` and `height` properties of the node become read-only results of the text layout. To force a specific width, set `textAutoResize = 'HEIGHT'` or `'NONE'`.

### Truncation
The `'TRUNCATE'` resize mode requires a fixed width. If the text exceeds the container, Figma will append an ellipsis (...). Note that the `.characters` property still returns the full, untruncated string.
