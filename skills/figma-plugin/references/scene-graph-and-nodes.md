# Scene Graph & Node Types
Sources: Official Figma Plugin API Reference, @figma/plugin-typings

The Figma Scene Graph is the hierarchical representation of every element in a document. Understanding its structure, how nodes are typed, and the optimal ways to traverse it is fundamental to building high-performance plugins.

## 1. Document Structure Hierarchy

Figma files follow a strict ownership tree. At the top level is the document root, which contains pages, which in turn contain the layers (SceneNodes) visible on the canvas.

```
DocumentNode (figma.root)
└── PageNode (figma.currentPage)
    └── SceneNode (Layers on canvas)
        ├── FrameNode
        │   └── RectangleNode
        ├── GroupNode
        │   └── TextNode
        └── ComponentNode
            └── InstanceNode
```

- **figma.root**: The entry point for the entire document. It contains the list of pages and metadata.
- **figma.currentPage**: The page the user is currently viewing/editing. Switching this changes the editor's view.
- **SceneNode**: A union type representing any object that can exist on the canvas. These are the "layers" in Figma.

## 2. Complete SceneNode Union Type

The `SceneNode` type is a union of over 30 distinct node types. Plugins must often narrow this type to access specific properties like `characters` for text or `fills` for shapes.

- **BooleanOperationNode**: Result of union, subtract, intersect, or exclude operations.
- **CodeBlockNode**: Syntax-highlighted code blocks used in FigJam.
- **ComponentNode**: The main component definition, containing the source of truth for its instances.
- **ComponentSetNode**: A container for component variants (e.g., different button states).
- **ConnectorNode**: Lines connecting objects, typically used in FigJam or diagramming.
- **EllipseNode**: Circles and ovals.
- **EmbedNode**: External content embeds like YouTube or Spotify.
- **FrameNode**: The primary container for layout, organization, and constraints.
- **GroupNode**: A logical grouping of nodes without its own layout or background properties.
- **HighlightNode**: Marker-style drawings often found in FigJam.
- **InstanceNode**: A copy of a component that stays linked to the main component.
- **InteractiveSlideElementNode**: Specialized elements for interactive Figma Slides.
- **LineNode**: Single line segments.
- **LinkUnfurlNode**: Visual representation of a URL link with a preview image.
- **MediaNode**: Video or GIF elements.
- **PolygonNode**: Regular polygons like triangles, hexagons, and pentagons.
- **RectangleNode**: Standard rectangles and squares, often used for buttons and backgrounds.
- **SectionNode**: Large-scale organizational containers for grouping frames on the canvas.
- **ShapeWithTextNode**: Common shapes containing text, primary building blocks in FigJam.
- **SliceNode**: Defines specific areas of the canvas for specialized export settings.
- **SlideGridNode**: Grid-based layouts for Figma Slides.
- **SlideNode**: Individual slides within a Figma Slides presentation.
- **SlideRowNode**: Row-based layouts for Figma Slides.
- **StampNode**: Reusable decorative markers or stickers in FigJam.
- **StarNode**: Star shapes with adjustable points, inner radius, and corner radius.
- **StickyNode**: Sticky notes used for feedback and brainstorming in FigJam.
- **TableNode**: Structured data tables with rows and columns.
- **TextNode**: Standard text elements for headings, body copy, and labels.
- **TextPathNode**: Text that follows the path of a vector object.
- **TransformGroupNode**: Grouping for complex 3D or perspective transforms.
- **VectorNode**: Complex paths composed of multiple points, segments, and regions.
- **WashiTapeNode**: Decorative tape elements found in FigJam.
- **WidgetNode**: Instances of Figma Widgets, which are interactive, stateful plugins.

## 3. Node Type Categories Table

| Category | Types | Has Children | Editor |
| :--- | :--- | :--- | :--- |
| **Containers** | FrameNode, GroupNode, SectionNode, ComponentNode, ComponentSetNode, InstanceNode | Yes | Figma |
| **Shapes** | RectangleNode, EllipseNode, PolygonNode, StarNode, LineNode, VectorNode, BooleanOperationNode | No | Figma |
| **Text** | TextNode, TextPathNode, CodeBlockNode | No | Figma/FigJam |
| **FigJam** | StickyNode, ShapeWithTextNode, ConnectorNode, StampNode, HighlightNode, WashiTapeNode | Varies | FigJam |
| **Slides** | SlideNode, SlideRowNode, SlideGridNode, InteractiveSlideElementNode | Yes | Slides |
| **Other** | EmbedNode, LinkUnfurlNode, MediaNode, SliceNode, WidgetNode, TableNode, TransformGroupNode | Varies | Various |

## 4. Creating Nodes

Nodes are created via factory methods on the `figma` object. By default, new nodes are placed at (0, 0) on the `currentPage`.

### Core Creation Methods
```typescript
const rect = figma.createRectangle()
const ellipse = figma.createEllipse()
const line = figma.createLine()
const polygon = figma.createPolygon()
const star = figma.createStar()
const vector = figma.createVector()
const frame = figma.createFrame()
const component = figma.createComponent()
const text = figma.createText()
const boolOp = figma.createBooleanOperation()
```

### Specialized Creation
```typescript
// Create from external data
const nodesFromSvg = figma.createNodeFromSvg(svgString)

// Grouping and Variants
const group = figma.group(nodes, parent) // parent is optional
const compSet = figma.combineAsVariants(components, parent)

// FigJam Elements
const sticky = figma.createSticky()
const connector = figma.createConnector()
const shapeText = figma.createShapeWithText()
const highlight = figma.createHighlight()
const stamp = figma.createStamp()

// Figma Slides
const slide = figma.createSlide()
```

## 5. Traversal Patterns

Efficiently navigating the scene graph is critical for plugin performance, especially in large files with thousands of layers.

### Standard Methods
- **`figma.currentPage.children`**: Returns a flat array of top-level nodes on the current page.
- **`node.findAll(predicate)`**: Recursively searches all descendants. **Warning**: Extremely slow on complex pages; it iterates through every single nested child.
- **`node.findOne(predicate)`**: Returns the first descendant matching the criteria and stops searching, making it slightly more efficient than `findAll`.

### Performance-Optimized Traversal
- **`node.findAllWithCriteria({ types: ['FRAME', 'RECTANGLE'] })`**: Significantly faster than `findAll` because the engine filters nodes natively before passing them to the plugin.
- **`node.findChildren(predicate)`**: Only searches direct children (non-recursive). Use this for shallow operations to avoid unnecessary recursion.

### Manual Recursive Pattern
For complex logic where `findAllWithCriteria` isn't enough, use a manual depth-first search to maintain control:

```typescript
function traverse(node: BaseNode) {
  // Perform action on node
  console.log(node.name)

  if ("children" in node) {
    // Reverse loop or copy array if you are removing nodes during traversal
    for (const child of node.children) {
      traverse(child)
    }
  }
}

// Start from root or specific container
traverse(figma.currentPage)
```

## 6. Type Checking Patterns

Since `SceneNode` is a union, you must narrow the type before accessing specific properties. Typescript requires this for type safety.

### Using the .type Property
The most common and reliable way to check a node's type.
```typescript
if (node.type === 'TEXT') {
  // node is narrowed to TextNode
  console.log(node.characters)
}
```

### Type Predicate Functions
Encapsulate complex checks into reusable type guards.
```typescript
function isContainer(node: SceneNode): node is FrameNode | GroupNode | ComponentNode | InstanceNode {
  return 'children' in node
}

if (isContainer(node)) {
  console.log(`Node has ${node.children.length} children`)
}
```

### Safe Property Access (In-operator)
Check for the existence of a property when you don't care about the specific node type.
```typescript
if ('fills' in node) {
  // Access paint properties safely across different shape types
  const fills = node.fills
}
```

## 7. Node Hierarchy Operations

Manipulating the relationship between nodes allows for restructuring the document and organizing layers.

### Reparenting and Ordering
- **`container.appendChild(child)`**: Moves `child` to the end of `container`'s children list (top of the layer stack).
- **`container.insertChild(index, child)`**: Moves `child` to a specific position in the hierarchy.
- **`node.remove()`**: Deletes the node from the document permanently.

### Duplication
- **`node.clone()`**: Creates a deep copy of the node (and its children, if any). The clone is initially placed in the same parent as the original. Note that `id` values will be different.

### Selection and Viewport
- **`figma.currentPage.selection = [node1, node2]`**: Updates the user's current selection. Setting this to an empty array `[]` clears the selection.
- **`figma.viewport.scrollAndZoomIntoView([node])`**: Focuses the editor view on specific nodes, automatically adjusting the zoom level.

## 8. Common Properties

While each node type has unique features, many properties are shared across the `SceneNode` union.

### Position and Size
- **`x, y`**: Position relative to the parent container's coordinate system.
- **`width, height`**: Dimensions of the node's bounding box.
- **`relativeTransform`**: A 2x3 matrix (Affine Transform) representing the node's transformation (position, rotation, scale) relative to its parent.
- **`absoluteTransform`**: A 2x3 matrix representing the global position and rotation relative to the page origin.
- **`absoluteBoundingBox`**: The coordinates and size in global document space, useful for spatial calculations across different containers.
- **`resize(w, h)`**: Resizes the node. If the node is a Frame, this may move child elements based on their constraints.
- **`resizeWithoutConstraints(w, h)`**: Resizes the node without triggering constraint-based movement of children.

### Display and State
- **`name`**: The layer name visible in the layers panel. Defaults to the node type if not set.
- **`visible`**: Boolean toggle for visibility. Hidden nodes still exist in the scene graph.
- **`locked`**: Boolean toggle for selection locking. Locked nodes cannot be selected by the user on the canvas.
- **`opacity`**: Value from 0 to 1, representing the overall layer transparency.
- **`blendMode`**: String identifying how the layer blends with layers below it (e.g., 'NORMAL', 'MULTIPLY', 'SCREEN').

### Plugin Data (Metadata)
- **`setPluginData(key, value)`**: Stores a private string on the node. This is persistent across sessions and only accessible by your plugin's ID.
- **`getPluginData(key)`**: Retrieves the stored private data.
- **`setSharedPluginData(namespace, key, value)`**: Stores data in a shared namespace that other plugins can also read/write.

### Persistence and Life Cycle
- **`id`**: A unique, persistent identifier for the node. This ID remains the same even after closing and reopening the file.
- **`removed`**: A read-only boolean. If your plugin keeps node references in memory (e.g., in an async callback), check this to ensure the node still exists before modification.

## 9. Page Operations

Pages are the top-level containers for all canvas content. A document can have multiple pages.

### Accessing and Modifying Pages
- **`figma.root.children`**: Returns an array of all `PageNode` objects.
- **`figma.currentPage`**: Get or set the active page. Switching pages will interrupt any active user interactions.
- **`figma.createPage()`**: Creates a new page and appends it to the document.
- **`page.name`**: Pages can be renamed just like scene nodes.

### Dynamic Loading
For large files, Figma may not load all pages into memory immediately to save resources.
- **`"documentAccess": "dynamic-page"`**: Manifest flag to enable granular page access.
- **`page.loadAsync()`**: Loads the content of a specific page on demand. Essential for plugins that process the entire document.
- **`figma.loadAllPagesAsync()`**: Loads every page in the document. **Caution**: This is a heavy operation and can lead to performance degradation or memory issues in massive files.

## 10. Anti-Patterns

Avoid these common mistakes to ensure your plugin is fast, stable, and user-friendly.

- **Iterating the entire document**: Never use `figma.root.findAll()` without a very specific reason. Most operations should be scoped to the `currentPage` or the user's current selection.
- **Using `findAll` by default**: Always prefer `findAllWithCriteria` for simple type or property searches. It offloads the work to Figma's native code, which is orders of magnitude faster.
- **Ignoring the `removed` property**: If your plugin performs asynchronous work (like `fetch` calls or `setTimeout`), always check `node.removed` before applying changes to node references.
- **Modifying Library Components**: Nodes within a library component are read-only when accessed via an instance or if the file is a consumer. Modifications will throw errors.
- **Blind Property Access**: Never assume a node has a property like `children`, `fills`, or `characters` without narrowing the type first. Use TypeScript to catch these errors at compile time.
- **Deep Nesting in Loops**: Avoid complex logic inside a `findAll` predicate. It's better to get a list of nodes first, then iterate over them with your logic.
- **Assuming Node Order**: The order of `children` represents the z-index (stacking order). Do not assume specific nodes are at specific indices, as users frequently reorder layers.
- **Hard-coding Node IDs**: While `id` is persistent, it is unique to the specific file. Do not hard-code IDs from your test files into your plugin code.
- **Massive Batch Operations without yields**: If modifying thousands of nodes, consider using `await new Promise(r => setTimeout(r, 0))` occasionally to keep the Figma UI responsive.
- **Overwriting Plugin Data**: Be careful with `setPluginData`. If multiple parts of your plugin use the same keys, they will overwrite each other. Use structured keys like `pluginName:featureName:key`.
