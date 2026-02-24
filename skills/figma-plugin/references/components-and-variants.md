# Components & Variants

Sources line: Official Figma Plugin API Reference, Tokens Studio patterns

Components are the fundamental building blocks of Figma design systems. In the Figma Plugin API, they are represented by `ComponentNode`, while their usage in the canvas is represented by `InstanceNode`. Variants are managed through `ComponentSetNode`.

## 1. Creating Components

Components can be created from scratch or converted from existing nodes.

### Creating from Scratch
When creating a new component, it starts empty and defaults to a 100x100 size unless resized.

```typescript
// Create a fresh component
const component = figma.createComponent()
component.name = 'Button'
component.resize(200, 48)

// Add content to the component
const text = figma.createText()
text.characters = 'Label'
component.appendChild(text)
```

### Converting Existing Nodes
A common pattern is converting an existing Frame or Group into a component.

```typescript
// Convert existing frame to component
const existingFrame = figma.currentPage.selection[0]
if (existingFrame && existingFrame.type === 'FRAME') {
  const component = figma.createComponentFromNode(existingFrame)
  component.name = 'Converted Component'
}
```

## 2. Component Properties

Every `ComponentNode` has metadata that defines its identity within a library and its documentation.

- **name**: The display name in the assets panel. For variants, this follows the `Property=Value` syntax.
- **key**: A unique, persistent identifier used to import this component into other files.
- **remote**: A boolean indicating if the component is from an external library. If `true`, the node is **READ-ONLY**.
- **description**: A string that appears in the Figma UI when hovering over the component.
- **documentationLinks**: An array of `DocumentationLink` objects ({ uri: string }).

```typescript
component.description = 'Primary action button for forms'
component.documentationLinks = [{ uri: 'https://design-system.com/button' }]
```

## 3. Creating Instances

Instances are clones of components that stay synced with the main component's changes while allowing specific overrides.

### Creation
```typescript
const instance = component.createInstance()
instance.x = 100
instance.y = 100
figma.currentPage.appendChild(instance)
```

### Finding Instances
Because instances can exist anywhere in the document, finding them can be an expensive operation. Use the asynchronous method for performance.

```typescript
// Get all instances of a component across the entire document
const instances = await component.getInstancesAsync()
console.log(`Component has ${instances.length} instances`)
```

## 4. Instance Operations

Instances allow for swapping, detaching, and managing overrides.

### Swapping Main Components
You can change the underlying component of an instance.

```typescript
// Swap main component
instance.mainComponent = otherComponent
```

### Detaching Instances
Detaching converts the instance into a regular `FrameNode`, breaking the link to the main component.

```typescript
// Detach (converts to frame, loses connection)
const frame = instance.detach()
```

### Managing Overrides
Overrides are the differences between an instance and its main component.

```typescript
// Reset all overrides to match the main component exactly
instance.resetOverrides()

// Check if a node was originally part of an instance that was detached
if (node.detachedInfo) {
  console.log('Original Component Key:', node.detachedInfo.componentKey)
}

// Access nested instances that have been "exposed" via Component Properties
const exposed = instance.exposedInstances
```

## 5. Component Sets (Variants)

Variants are grouped into a `ComponentSetNode`. This allows users to switch between different states or types using a single property panel.

### Creating Variants
To create a variant set, you must combine multiple components.

```typescript
// Create variants from existing components
const componentSet = figma.combineAsVariants([comp1, comp2, comp3], parent)
componentSet.name = 'Button'

// Components inside a set must follow the naming convention:
// "Property1=Value1, Property2=Value2"
comp1.name = 'Size=Small, State=Default'
comp2.name = 'Size=Large, State=Default'
comp3.name = 'Size=Large, State=Hover'
```

### Accessing Variant Schema
```typescript
// Read the available properties and values
const props = componentSet.variantGroupProperties
// Output: { "Size": { values: ["Small", "Large"] }, "State": { values: ["Default", "Hover"] } }
```

## 6. Component Properties (Modern API)

Figma introduced a specific API for "Component Properties" (Boolean, Text, Instance Swap, and Variant) that allow for a more structured way to handle overrides.

### Defining Properties on a Component
These definitions tell Figma which parts of the component are customizable.

```typescript
// Define properties on the Main Component
component.addComponentProperty('showIcon', 'BOOLEAN', true)
component.addComponentProperty('label', 'TEXT', 'Button')
component.addComponentProperty('icon', 'INSTANCE_SWAP', defaultIconId)
component.addComponentProperty('variant', 'VARIANT', 'primary')

// Read existing definitions
const defs = component.componentPropertyDefinitions
```

### Setting Property Overrides on Instances
Instead of manually traversing the layer tree, you can use the `setProperties` method.

```typescript
// Apply overrides to an instance
instance.setProperties({
  'showIcon': false,
  'label': 'Submit',
  'icon': otherIconComponent.id
})

// Read the current property values of an instance
const currentProps = instance.componentProperties
```

## 7. Library Operations

Working with components from external files (Team Libraries) requires using keys and asynchronous loading.

### Importing Remote Nodes
```typescript
// Import a component by its unique key
const component = await figma.importComponentByKeyAsync('abc123_key')
const instance = component.createInstance()

// Import a variant set (ComponentSet)
const componentSet = await figma.importComponentSetByKeyAsync('def456_key')

// Import a shared style
const style = await figma.importStyleByKeyAsync('ghi789_key')
```

### Team Library Access
Accessing library metadata requires the `teamlibrary` permission in `manifest.json`.

```typescript
// Get available variable collections in the user's team libraries
const collections = await figma.teamLibrary.getAvailableLibraryVariableCollectionsAsync()
```

## 8. Styles (Paint, Text, Effect, Grid)

Styles are global definitions for visual properties.

### Creating Styles
```typescript
// Paint Style (Colors/Gradients)
const paintStyle = figma.createPaintStyle()
paintStyle.name = 'Colors/Primary'
paintStyle.paints = [{ type: 'SOLID', color: { r: 0, g: 0.4, b: 1 } }]

// Effect Style (Shadows/Blurs)
const effectStyle = figma.createEffectStyle()
effectStyle.name = 'Elevation/Small'
effectStyle.effects = [{
  type: 'DROP_SHADOW',
  color: { r: 0, g: 0, b: 0, a: 0.25 },
  offset: { x: 0, y: 4 },
  radius: 4,
  visible: true,
  blendMode: 'NORMAL'
}]
```

### Applying Styles
Instead of setting raw values, assign the style's ID to the node's style property.

```typescript
node.fillStyleId = paintStyle.id
node.effectStyleId = effectStyle.id
node.strokeStyleId = strokeStyle.id
```

### Retrieving Local Styles
```typescript
const paintStyles = await figma.getLocalPaintStylesAsync()
const textStyles = await figma.getLocalTextStylesAsync()
const effectStyles = await figma.getLocalEffectStylesAsync()
const gridStyles = await figma.getLocalGridStylesAsync()
```

## 9. Working with Remote Components

Remote components are those that exist in a library file, not the current file.

### Identification
Always check the `remote` property before attempting modifications.

```typescript
if (component.remote) {
  // READ-ONLY: Cannot change name, layout, or children
  console.log(`Remote Component: ${component.name} (${component.key})`)
}
```

### Finding the Main Component
An instance might point to a remote component. Use the async version to ensure it is loaded.

```typescript
// Safe way to get the main component of any instance
const main = await instance.getMainComponentAsync()
if (main) {
  console.log(`Instance is linked to: ${main.name}`)
}
```

## 10. Anti-Patterns & Best Practices

To ensure plugin stability and performance, avoid these common pitfalls.

### ❌ Modification of Remote Components
Attempting to set properties (like `name` or `resize`) on a component where `remote === true` will throw an error. Only local components can be modified.

### ❌ Synchronous `mainComponent` Access
The `instance.mainComponent` property can be `null` if the component is remote and hasn't been loaded. **Always prefer `instance.getMainComponentAsync()`**.

### ❌ Unnecessary `resetOverrides()`
Calling `resetOverrides()` on every instance update can be visually jarring for users and may destroy intentional customizations. Only use it when a "full reset" is explicitly intended.

### ❌ Forgetting to append to Canvas
`figma.createComponent()` creates the node in memory. It will not appear in the file until you use `appendChild()` on a page or a frame.

### ❌ Infinite Propagation
Remember that editing a Main Component immediately propagates changes to all instances. If you are modifying a component used thousands of times, the plugin may hang while Figma calculates the updates.

### ❌ Zombie Components
Always verify a component still exists before creating an instance. If a component was deleted but your plugin still holds a reference to it, `createInstance()` will fail.

```typescript
if (!component.removed) {
  component.createInstance()
}
```

### ❌ Hardcoding IDs
Never hardcode `node.id`. IDs are unique to a specific file instance. If you need a persistent reference across files, use `node.key` (for components/styles) or `setPluginData`.

## Summary Checklist for Component Ops

1. Check if node is a `ComponentNode` or `InstanceNode`.
2. Verify `remote` status before editing.
3. Use `Async` methods for finding instances or main components.
4. Follow the `Prop=Value` naming convention for Variants if not using the modern Component Properties API.
5. Use `importComponentByKeyAsync` for library components.
6. Handle potential `null` returns when importing or finding components.
