# Variables & Storage

Sources: Official Figma Plugin Docs - Working with Variables, figma/plugin-samples/variables-import-export

This reference guide covers the programmatic management of Figma Variables (Design Tokens) and the various persistence mechanisms available to plugins.

## 1. Variables Overview

Figma Variables allow designers and developers to store reusable values that can be applied across a design. They are the foundation for building multi-mode design systems (e.g., Light/Dark themes, Mobile/Desktop densities).

- **Variable Types**:
  - `COLOR`: RGBA values.
  - `FLOAT`: Numeric values (pixels, opacity, etc.).
  - `STRING`: Text values.
  - `BOOLEAN`: True/False flags.
- **Organization Hierarchy**:
  - **VariableCollection**: A container for a group of variables.
  - **VariableMode**: A set of values for variables in a collection (e.g., "Light", "Dark").
  - **Variable**: The individual token containing values for each mode in its collection.
- **Binding**: Variables can be "bound" to node properties, creating a live link that updates when the variable value or active mode changes.

## 2. Reading Variables

Accessing variables and collections is primarily asynchronous. You can fetch local items or specific items by their ID.

```typescript
/**
 * FETCHING COLLECTIONS
 */

// Retrieve all local variable collections in the current file
const collections = await figma.variables.getLocalVariableCollectionsAsync();

// Get a specific collection by its ID
const collection = await figma.variables.getVariableCollectionByIdAsync(collectionId);


/**
 * FETCHING VARIABLES
 */

// Get all local variables. Optionally filter by type: 'COLOR' | 'FLOAT' | 'STRING' | 'BOOLEAN'
const colorVars = await figma.variables.getLocalVariablesAsync('COLOR');
const allVars = await figma.variables.getLocalVariablesAsync();

// Get a specific variable by its unique ID
const variable = await figma.variables.getVariableByIdAsync(variableId);
```

## 3. Creating Variables

Creating a variable requires a parent collection. Once created, you can define values for each mode defined in that collection.

```typescript
// 1. Create a new collection
const collection = figma.variables.createVariableCollection('Brand Tokens');

// 2. Manage modes within the collection
// Every collection starts with one default mode
const lightModeId = collection.modes[0].modeId;
collection.renameMode(lightModeId, 'Light');

// Add additional modes (e.g., Dark Mode)
const darkModeId = collection.addMode('Dark');

// 3. Create the variable within the collection
const colorVar = figma.variables.createVariable('surface-primary', collection, 'COLOR');
const spacingVar = figma.variables.createVariable('spacing-sm', collection, 'FLOAT');

// 4. Set values for each mode
// Color values use { r, g, b, a? } where components are 0-1
colorVar.setValueForMode(lightModeId, { r: 1, g: 1, b: 1 }); // White
colorVar.setValueForMode(darkModeId, { r: 0.1, g: 0.1, b: 0.1 }); // Dark Grey

// Float values are direct numbers
spacingVar.setValueForMode(lightModeId, 8);
spacingVar.setValueForMode(darkModeId, 8);
```

## 4. Binding Variables to Nodes

Binding creates the connection between the token and the UI element. While simple properties can be bound directly, complex properties like fills and effects require an immutable update pattern.

### Helper for Immutable Properties
Figma properties like `fills`, `effects`, and `layoutGrids` are immutable. You must clone the array, modify the copy, and re-assign it.

```typescript
function clone(val: any): any {
  const type = typeof val;
  if (val === null) return null;
  if (type === 'undefined' || type === 'number' || type === 'string' || type === 'boolean') return val;
  if (type === 'object') {
    if (val instanceof Array) return val.map(x => clone(x));
    if (val instanceof Uint8Array) return new Uint8Array(val);
    const obj: any = {};
    for (const key in val) obj[key] = clone(val[key]);
    return obj;
  }
  throw new Error('Unknown type');
}
```

### Binding Snippets
```typescript
/**
 * SIMPLE FIELDS
 * Works for width, height, opacity, cornerRadius, etc.
 */
node.setBoundVariable('width', widthVariable);
node.setBoundVariable('opacity', opacityVariable);

// To unbind, pass null
node.setBoundVariable('width', null);

// Inspect existing bindings
const bound = node.boundVariables;
// Returns: { width: { type: 'VARIABLE_ALIAS', id: 'VariableID:...' } }


/**
 * COMPLEX ARRAYS (Fills, Strokes, Effects)
 * Use the dedicated figma.variables utility methods
 */

// 1. Fills / Strokes
const fills = clone(node.fills);
fills[0] = figma.variables.setBoundVariableForPaint(fills[0], 'color', colorVar);
node.fills = fills;

// 2. Effects (Shadows, Blurs)
const effects = clone(node.effects);
effects[0] = figma.variables.setBoundVariableForEffect(effects[0], 'radius', radiusVar);
node.effects = effects;

// 3. Layout Grids
const grids = clone(node.layoutGrids);
grids[0] = figma.variables.setBoundVariableForLayoutGrid(grids[0], 'count', countVar);
node.layoutGrids = grids;
```

## 5. Resolving Variables

Resolution is the process of getting the actual value being applied to a node, taking into account the node's current mode.

```typescript
// Get the specific value applied to a consumer node based on its mode context
const resolved = variable.resolveForConsumer(node);
console.log(resolved.value); // e.g., { r: 1, g: 1, b: 1 }
console.log(resolved.resolvedType); // 'COLOR'

// Get all raw values defined for the variable across all modes
const values = variable.valuesByMode;
// { 'mode-123': { r: 1, g: 1, b: 1 }, 'mode-456': { r: 0, g: 0, b: 0 } }
```

## 6. Variable Aliases

Aliases allow variables to point to other variables, enabling semantic layering (e.g., `button-bg` points to `blue-500`).

```typescript
// Create an alias from an existing variable object
const alias = figma.variables.createVariableAlias(baseVariable);

// Set the value of one variable to be the alias of another
semanticVariable.setValueForMode(modeId, alias);

// Async version: creating an alias from a variable ID
const aliasAsync = await figma.variables.createVariableAliasByIdAsync(baseVariableId);
```

## 7. Library Variables

To access variables from external team libraries, your plugin needs the `teamlibrary` permission in `manifest.json`.

```typescript
// Import a specific variable from a team library using its unique key
const importedVar = await figma.variables.importVariableByKeyAsync(variableKey);

// Browse available library collections (meta-data only)
const libCollections = await figma.teamLibrary.getAvailableLibraryVariableCollectionsAsync();
```

## 8. Extended Collections (Enterprise)

Theming features (Extended Collections) allow for advanced overrides and cross-file theme application, typically used in Figma Enterprise.

```typescript
/**
 * EXTENDING COLLECTIONS
 */

// Extend a local collection to create a themed variation
const extended = localCollection.extend('Brand Theme');

// Extend a library collection (requires key)
const extendedLib = await figma.variables.extendLibraryCollectionByKeyAsync(libKey, 'External Theme');


/**
 * OVERRIDES
 */

// Apply an override value within the extended collection's mode
const themeModeId = extended.modes[0].modeId;
variable.setValueForMode(themeModeId, { r: 1, g: 0, b: 0 });

// Retrieve values specifically for an extended collection
const themedValues = await variable.valuesByModeForCollectionAsync(extended);

// Inspect all overrides on a collection
const allOverrides = extended.variableOverrides;

// Remove an override to revert to the base collection's value
variable.removeOverrideForMode(themeModeId);
```

## 9. Typography Variables

Variables can be bound to specific text properties or ranges within a text node.

```typescript
// Bindable Text Fields: 
// fontFamily, fontStyle, fontWeight, lineHeight, letterSpacing, paragraphSpacing, paragraphIndent

// 1. Bind to a whole text node
textNode.setBoundVariable('fontFamily', fontFamilyVar);
textNode.setBoundVariable('lineHeight', lineHeightVar);

// 2. Bind to a specific range of characters
textNode.setRangeBoundVariable(0, 10, 'fontWeight', weightVar);

// 3. Bind properties within a Text Style
const textStyle = figma.getStyleById(styleId) as TextStyle;
textStyle.setBoundVariable('letterSpacing', letterSpacingVar);
```

## 10. Plugin Data (Document Storage)

Plugin data is stored directly in the Figma file (`.fig`). It is ideal for metadata that should travel with the design.

- **Storage Limit**: ~100KB per entry (Key + Value + PluginID overhead).
- **Scope**: By default, data is private to your plugin ID.

```typescript
/**
 * PRIVATE PLUGIN DATA
 */
node.setPluginData('version', '1.0.2');
const version = node.getPluginData('version'); // Returns '' if key doesn't exist

// List all keys stored on a node by your plugin
const keys = node.getPluginDataKeys();


/**
 * SHARED PLUGIN DATA
 * Visible to OTHER plugins if they know your namespace
 */
node.setSharedPluginData('my-design-system', 'token-id', '123-abc');
const sharedId = node.getSharedPluginData('my-design-system', 'token-id');


/**
 * DOCUMENT-LEVEL STORAGE
 * Store global settings on the root node
 */
const settings = { theme: 'glass', showIcons: true };
figma.root.setPluginData('config', JSON.stringify(settings));

const savedConfig = JSON.parse(figma.root.getPluginData('config') || '{}');
```

## 11. Client Storage (Local Machine)

`clientStorage` is an asynchronous key-value store that persists on the user's local machine. It is perfect for user preferences or caching.

- **Storage Limit**: 5MB total per plugin.
- **Scope**: Per user, per machine. Not synced via Figma servers.

```typescript
// Store data (objects are automatically serialized)
await figma.clientStorage.setAsync('user-prefs', {
  recentColors: ['#FF0000', '#00FF00'],
  notificationsEnabled: false
});

// Retrieve data
const prefs = await figma.clientStorage.getAsync('user-prefs');

// Check for existence of keys
const allKeys = await figma.clientStorage.keysAsync();

// Cleanup
await figma.clientStorage.deleteAsync('user-prefs');
```

## 12. Storage Decision Table

| Requirement | Preferred Mechanism | Lifecycle | Accessibility |
| :--- | :--- | :--- | :--- |
| **Node Metadata** | `pluginData` | Lives in File | Only your plugin |
| **Document Settings** | `figma.root.pluginData` | Lives in File | Only your plugin |
| **Inter-Plugin Comms** | `sharedPluginData` | Lives in File | Any plugin with Namespace |
| **User Preferences** | `clientStorage` | Lives on Machine | Local user only |
| **Large Assets** | `External API` | Server-defined | Cross-device / Cross-user |

### Quick Checklist for Data Handling:
1. **Always use Async/Await**: `clientStorage` and most variable methods are asynchronous.
2. **Handle Empty States**: `getPluginData` returns an empty string `""` if not found, while `clientStorage.getAsync` returns `undefined`.
3. **Immutable Updates**: Remember to `clone()` arrays like `fills` or `effects` before modifying them to trigger a node update.
4. **JSON Serialization**: Use `JSON.stringify/parse` for complex objects in `pluginData`, as it only accepts strings. `clientStorage` handles objects natively.
5. **Permissions**: Ensure `manifest.json` includes `teamlibrary` if importing external variables.
