# Premium Component Patterns

Sources: TanStack Table documentation, cmdk documentation, React Hook Form documentation, Sonner documentation, Radix UI documentation

Covers: data tables (TanStack Table), command palettes (cmdk), forms (React Hook Form + Zod), modals/sheets/drawers (Radix), toast notifications (Sonner).

## Data Tables (TanStack Table)

Data tables are the backbone of data-dense applications. Use TanStack Table (v8) for headless logic, providing full control over the markup and styling while handling complex state management.

### TanStack Table Setup

Initialize the table using the `useReactTable` hook. Define columns with clear accessors and headers.

```tsx
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  ColumnDef
} from '@tanstack/react-table';

const columns: ColumnDef<User>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
  },
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'email',
    header: 'Email',
  },
];

const table = useReactTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
});
```

### Virtual Scrolling with TanStack Virtual

For datasets exceeding 1,000 rows, implement virtual scrolling to maintain 60 FPS. Use `@tanstack/react-virtual` to render only the visible rows.

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

const tableContainerRef = useRef<HTMLDivElement>(null);
const { rows } = table.getRowModel();

const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => 45, // Estimated row height
  overscan: 10, // Render 10 rows outside the viewport to prevent flickering
});

const virtualRows = rowVirtualizer.getVirtualItems();
const totalSize = rowVirtualizer.getTotalSize();

// In JSX
<div ref={tableContainerRef} style={{ height: '600px', overflow: 'auto' }}>
  <div style={{ height: `${totalSize}px`, position: 'relative' }}>
    {virtualRows.map((virtualRow) => {
      const row = rows[virtualRow.index];
      return (
        <div
          key={virtualRow.key}
          style={{
            position: 'absolute',
            top: 0,
            transform: `translateY(${virtualRow.start}px)`,
            height: `${virtualRow.size}px`,
          }}
        >
          {row.getVisibleCells().map(cell => (
             flexRender(cell.column.columnDef.cell, cell.getContext())
          ))}
        </div>
      );
    })}
  </div>
</div>
```

### Column Resizing

Set `columnResizeMode: "onChange"` for immediate feedback during resize.

```tsx
const table = useReactTable({
  columnResizeMode: 'onChange',
  defaultColumn: {
    minSize: 50,
    size: 150,
    maxSize: 500,
  },
  // ...other options
});

// Resizer handle in header
<div
  onMouseDown={header.getResizeHandler()}
  onTouchStart={header.getResizeHandler()}
  className={`resizer ${header.column.getIsResizing() ? 'isResizing' : ''}`}
/>
```

### Faceted Filtering

Faceted filters allow users to see the distribution of values within the dataset.

```tsx
const table = useReactTable({
  getFacetedUniqueValues: getFacetedUniqueValues(),
  // ...
});

// Accessing unique values for a column filter
const uniqueValues = Array.from(column.getFacetedUniqueValues().keys());
```

### Sorting

Enable sorting to allow users to organize data quickly.

```tsx
const [sorting, setSorting] = useState<SortingState>([]);

const table = useReactTable({
  state: {
    sorting,
  },
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
  // ...
});

// In header cell
<div
  className={header.column.getCanSort() ? 'cursor-pointer select-none' : ''}
  onClick={header.column.getToggleSortingHandler()}
>
  {flexRender(header.column.columnDef.header, header.getContext())}
  {{
    asc: ' [ASC]',
    desc: ' [DESC]',
  }[header.column.getIsSorted() as string] ?? null}
</div>
```

### Inline Editing

Implement inline editing by tracking row/cell state and rendering an input on click.

```tsx
const [editingId, setEditingId] = useState<string | null>(null);

const columnDef: ColumnDef<User> = {
  cell: ({ getValue, row, column, table }) => {
    const initialValue = getValue();
    const [value, setValue] = useState(initialValue);

    const onBlur = () => {
      table.options.meta?.updateData(row.index, column.id, value);
    };

    return (
      <input
        value={value as string}
        onChange={e => setValue(e.target.value)}
        onBlur={onBlur}
      />
    );
  }
}
```

## Command Palette (cmdk)

Command palettes provide a "keyboard-first" interface for power users. Use `cmdk` for its robust fuzzy search and nested navigation capabilities.

### Basic Setup with Keyboard Shortcut

Register a global `KeyDown` listener to toggle the palette.

```tsx
import { Command } from 'cmdk';

const [open, setOpen] = useState(false);

useEffect(() => {
  const down = (e: KeyboardEvent) => {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((open) => !open);
    }
  };
  document.addEventListener('keydown', down);
  return () => document.removeEventListener('keydown', down);
}, []);

return (
  <Command.Dialog open={open} onOpenChange={setOpen}>
    <Command.Input placeholder="Type a command or search..." />
    <Command.List>
      <Command.Empty>No results found.</Command.Empty>
      <Command.Group heading="Actions">
        <Command.Item onSelect={() => console.log('Action 1')}>Action 1</Command.Item>
        <Command.Item onSelect={() => console.log('Action 2')}>Action 2</Command.Item>
      </Command.Group>
    </Command.List>
  </Command.Dialog>
);
```

### Nested Pages Pattern

Simulate navigation within the palette to prevent information overload.

```tsx
const [pages, setPages] = useState<string[]>([]);
const page = pages[pages.length - 1];

return (
  <Command onKeyDown={(e) => {
    if (e.key === 'Backspace' && !search && pages.length > 0) {
      setPages(pages.slice(0, -1));
    }
  }}>
    {!page && (
      <>
        <Command.Item onSelect={() => setPages([...pages, 'projects'])}>
          Projects...
        </Command.Item>
        <Command.Item onSelect={() => setPages([...pages, 'settings'])}>
          Settings...
        </Command.Item>
      </>
    )}

    {page === 'projects' && (
      <Command.Group heading="Projects">
        <Command.Item>Project A</Command.Item>
        <Command.Item>Project B</Command.Item>
      </Command.Group>
    )}
  </Command>
);
```

## Forms That Feel Right (React Hook Form + Zod)

Premium forms provide immediate feedback and handle complex validation without performance lag.

### Validation Timing Strategy

The most user-friendly validation pattern is to validate on `onBlur` for the first time, and `onChange` after an error is detected.

```tsx
const form = useForm<Schema>({
  resolver: zodResolver(schema),
  mode: 'onBlur',
  reValidateMode: 'onChange',
});
```

### Multi-Step Forms with Per-Step Validation

Validate each step before allowing navigation. Use `form.trigger()` to manually validate specific fields.

```tsx
const stepSchemas = [stepOneSchema, stepTwoSchema];
const currentSchema = stepSchemas[currentStep];

const next = async () => {
  const fields = Object.keys(currentSchema.shape) as (keyof Schema)[];
  const isValid = await form.trigger(fields);
  if (isValid) setCurrentStep(prev => prev + 1);
};
```

### Autosave with Debounced Watch

Implement autosave by watching the form values and debouncing the save operation.

```tsx
const values = useWatch({ control: form.control });

useEffect(() => {
  const timer = setTimeout(() => {
    if (form.formState.isDirty && form.formState.isValid) {
      saveData(values);
    }
  }, 1000);
  return () => clearTimeout(timer);
}, [values]);
```

### Optimistic Submit with Sonner

Use `toast.promise` to provide immediate visual feedback while the server processes the request.

```tsx
const onSubmit = async (data: Schema) => {
  toast.promise(saveData(data), {
    loading: 'Saving changes...',
    success: (data) => `Saved successfully`,
    error: 'Failed to save',
  });
};
```

## Modals and Overlays (Radix UI)

Overlays provide focused interactions. Use the correct primitive for the appropriate context.

### Overlay Selection Decision Tree

| Component | Use Case | Implementation Tip |
|-----------|----------|-------------------|
| Dialog | General actions/info | Use for non-destructive, focused tasks. |
| Sheet | Contextual info/Editing | Use for settings or side-navigation. |
| Drawer | Mobile-first actions | Best for mobile screens (bottom-up). |
| AlertDialog | Destructive actions | Forces explicit confirmation (Delete, Logout). |

### Radix Dialog Pattern

Ensure focus trapping and accessibility by using Radix primitives.

```tsx
import * as Dialog from '@radix-ui/react-dialog';

<Dialog.Root>
  <Dialog.Trigger asChild>
    <button>Open</button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="dialog-overlay" />
    <Dialog.Content className="dialog-content">
      <Dialog.Title>Dialog Title</Dialog.Title>
      <Dialog.Description>Brief description here.</Dialog.Description>
      {/* Content */}
      <Dialog.Close asChild>
        <button>Close</button>
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### Confirmation Pattern

For `AlertDialog`, always clearly distinguish the primary action (e.g., Delete) from the cancel action.

```tsx
import * as AlertDialog from '@radix-ui/react-alert-dialog';

<AlertDialog.Root>
  <AlertDialog.Content>
    <AlertDialog.Title>Are you absolutely sure?</AlertDialog.Title>
    <AlertDialog.Description>This action cannot be undone.</AlertDialog.Description>
    <div className="flex gap-2">
      <AlertDialog.Cancel>Cancel</AlertDialog.Cancel>
      <AlertDialog.Action className="bg-red-500">Delete Account</AlertDialog.Action>
    </div>
  </AlertDialog.Content>
</AlertDialog.Root>
```

## Toast Notifications (Sonner)

Toasts should be informative but non-disruptive. Use `Sonner` for its stacked appearance and promise-based API.

### Undo Pattern

Provide a way to revert actions directly from the toast.

```tsx
import { toast } from 'sonner';

const deleteItem = (id: string) => {
  const previousData = currentData;
  setData(data.filter(i => i.id !== id));

  toast('Item deleted', {
    action: {
      label: 'Undo',
      onClick: () => setData(previousData),
    },
  });
};
```

### Max Stacking and Auto-Dismiss

Prevent "toast fatigue" by limiting the number of visible toasts.

```tsx
<Toaster visibleToasts={3} expand={false} richColors />
```

### Progress Toast

Use for long-running operations like file uploads.

```tsx
const toastId = toast.loading('Uploading file...');

const onProgress = (percent: number) => {
  if (percent === 100) {
    toast.success('Upload complete', { id: toastId });
  } else {
    toast.loading(`Uploading: ${percent}%`, { id: toastId });
  }
};
```

## Component Selection Decision Tree

| Requirement | Preferred Component | Key Logic |
|-------------|---------------------|-----------|
| Viewing 1k+ items | Data Table | Virtualization + Faceted Filter |
| Rapid navigation | Command Palette | Nested Pages + `cmdk` |
| 5+ input fields | Form | React Hook Form + Zod |
| Side context | Sheet | Radix UI Portal |
| Mobile action list | Drawer | Vaul (Drawer primitive) |
| Feedback on action | Toast | Sonner `toast.promise` |
| Destructive action | Alert Dialog | Explicit confirmation focus |
| Multi-step data entry| Stepper Form | Schema-per-step validation |

## Implementation Checklist

1. **Accessibility**: Ensure every modal and dialog has a `Title` and `Description`.
2. **Keyboard**: Verify all components are navigable via `Tab`, `Enter`, and `Esc`.
3. **Performance**: Use virtualization for tables and `memo` for expensive cell renders.
4. **Resilience**: Handle error states in `toast.promise` and show descriptive errors in forms.
5. **State**: Keep form state local until submission; avoid lifting intermediate form state to global stores.
6. **Interaction**: Use `asChild` in Radix primitives to prevent redundant DOM nodes.
7. **Testing**: Test form validation logic independently of the UI using Zod schema tests.
