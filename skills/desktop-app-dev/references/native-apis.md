# Native Desktop APIs

Sources: Electron v40 API docs, Tauri v2 plugin docs, Wails v2 runtime docs, platform-specific guidelines

Covers: application menus, system tray, notifications, file system access, dialogs, keyboard shortcuts, clipboard, deep links, system information, multi-window management.

## Application Menus

### Electron

```typescript
import { Menu, MenuItem, app } from 'electron';

const template: Electron.MenuItemConstructorOptions[] = [
  {
    label: 'File',
    submenu: [
      { label: 'New', accelerator: 'CmdOrCtrl+N', click: () => createFile() },
      { label: 'Open', accelerator: 'CmdOrCtrl+O', click: () => openFile() },
      { type: 'separator' },
      { role: 'quit' },
    ],
  },
  { role: 'editMenu' },   // Built-in edit menu (undo, redo, cut, copy, paste)
  { role: 'viewMenu' },   // Built-in view menu (zoom, devtools, fullscreen)
];
const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
```

### Tauri

```rust
use tauri::menu::{Menu, MenuBuilder, SubmenuBuilder};

pub fn run() {
    tauri::Builder::default()
        .menu(|app| {
            MenuBuilder::new(app)
                .items(&[
                    &SubmenuBuilder::new(app, "File")
                        .text("new", "New")
                        .text("open", "Open")
                        .separator()
                        .quit()
                        .build()?,
                    &SubmenuBuilder::new(app, "Edit")
                        .undo().redo().separator()
                        .cut().copy().paste()
                        .build()?,
                ])
                .build()
        })
        .on_menu_event(|app, event| {
            match event.id().as_ref() {
                "new" => { /* handle new */ },
                "open" => { /* handle open */ },
                _ => {}
            }
        })
}
```

### Wails

```go
// main.go - configure in app options
appMenu := menu.NewMenu()
fileMenu := appMenu.AddSubmenu("File")
fileMenu.AddText("New", keys.CmdOrCtrl("n"), func(cd *menu.CallbackData) {
    // handle new
})
fileMenu.AddText("Open", keys.CmdOrCtrl("o"), func(cd *menu.CallbackData) {
    // handle open
})
fileMenu.AddSeparator()
fileMenu.AddText("Quit", keys.CmdOrCtrl("q"), func(cd *menu.CallbackData) {
    runtime.Quit(app.ctx)
})

wails.Run(&options.App{
    Menu: appMenu,
})
```

### Context Menus

| Framework | Approach |
|-----------|----------|
| Electron | `Menu.popup()` on `contextmenu` event |
| Tauri | `menu.popup()` from Rust or via event |
| Wails | No built-in context menu API; use frontend library |

## System Tray

### Electron

```typescript
import { Tray, Menu, nativeImage } from 'electron';

let tray: Tray;
app.whenReady().then(() => {
  const icon = nativeImage.createFromPath('icon.png');
  tray = new Tray(icon.resize({ width: 16, height: 16 }));
  tray.setToolTip('My App');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Show App', click: () => mainWindow.show() },
    { label: 'Quit', click: () => app.quit() },
  ]));
  tray.on('click', () => mainWindow.show());
});
```

### Tauri

```rust
use tauri::tray::{TrayIconBuilder, MouseButton, MouseButtonState};
use tauri::menu::{Menu, MenuItem};

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&quit])?;
            TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .on_menu_event(|app, event| {
                    if event.id() == "quit" { app.exit(0); }
                })
                .on_tray_icon_event(|tray, event| {
                    if let tauri::tray::TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up, ..
                    } = event {
                        let app = tray.app_handle();
                        if let Some(w) = app.get_webview_window("main") {
                            w.show().unwrap();
                            w.set_focus().unwrap();
                        }
                    }
                })
                .build(app)?;
            Ok(())
        })
}
```

### Wails

```go
wails.Run(&options.App{
    // v2: Limited system tray via platform-specific packages
    // v3: Enhanced tray support (in alpha)
})
```

For v2, use third-party packages like `getlantern/systray` alongside Wails.

## Notifications

### Electron

```typescript
// From renderer (Web Notification API works)
new Notification('Title', { body: 'Message body' });

// From main process
const { Notification } = require('electron');
new Notification({ title: 'Title', body: 'Message' }).show();
```

### Tauri

```bash
cargo add tauri-plugin-notification
npm install @tauri-apps/plugin-notification
```

```typescript
import { sendNotification, isPermissionGranted, requestPermission }
  from '@tauri-apps/plugin-notification';

let permitted = await isPermissionGranted();
if (!permitted) permitted = (await requestPermission()) === 'granted';
if (permitted) sendNotification({ title: 'Title', body: 'Message body' });
```

### Wails

No built-in notification API. Use Go libraries:

```go
import "github.com/gen2brain/beeep"

func (a *App) Notify(title, message string) error {
    return beeep.Notify(title, message, "")
}
```

## File Dialogs

### Electron

```typescript
import { dialog } from 'electron';

// Open file
const result = await dialog.showOpenDialog(mainWindow, {
  properties: ['openFile', 'multiSelections'],
  filters: [
    { name: 'Text', extensions: ['txt', 'md'] },
    { name: 'All Files', extensions: ['*'] },
  ],
});
// result.filePaths: string[]

// Save file
const saveResult = await dialog.showSaveDialog(mainWindow, {
  defaultPath: 'document.txt',
  filters: [{ name: 'Text', extensions: ['txt'] }],
});
// saveResult.filePath: string | undefined

// Select directory
const dirResult = await dialog.showOpenDialog(mainWindow, {
  properties: ['openDirectory'],
});
```

### Tauri

```typescript
import { open, save } from '@tauri-apps/plugin-dialog';

const file = await open({
  multiple: false,
  filters: [{ name: 'Text', extensions: ['txt', 'md'] }],
});
// file: string | null

const savePath = await save({
  defaultPath: 'document.txt',
  filters: [{ name: 'Text', extensions: ['txt'] }],
});

const dir = await open({ directory: true });
```

### Wails

```go
file, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
    Title:   "Open File",
    Filters: []runtime.FileFilter{
        {DisplayName: "Text Files", Pattern: "*.txt;*.md"},
    },
})
```

See `references/wails-guide.md` for full dialog examples.

## Keyboard Shortcuts

### Electron (Global Shortcuts)

```typescript
import { globalShortcut } from 'electron';

app.whenReady().then(() => {
  globalShortcut.register('CommandOrControl+Shift+I', () => {
    // Global shortcut (works even when app not focused)
  });
});
app.on('will-quit', () => globalShortcut.unregisterAll());
```

### Tauri

```bash
cargo add tauri-plugin-global-shortcut
npm install @tauri-apps/plugin-global-shortcut
```

```typescript
import { register } from '@tauri-apps/plugin-global-shortcut';

await register('CommandOrControl+Shift+C', (event) => {
  if (event.state === 'Pressed') { /* handle */ }
});
```

### Wails

No built-in global shortcut API. Use platform-specific Go libraries or
handle keyboard events in the frontend (local shortcuts only).

## Clipboard

### Electron

```typescript
import { clipboard } from 'electron';
clipboard.writeText('copied text');
const text = clipboard.readText();
```

### Tauri

```typescript
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';
await writeText('copied text');
const text = await readText();
```

### Wails

```go
import "github.com/atotto/clipboard"
clipboard.WriteAll("copied text")
text, _ := clipboard.ReadAll()
```

## Deep Links (Custom Protocol)

Register `myapp://` protocol for deep linking.

### Electron

```typescript
app.setAsDefaultProtocolClient('myapp');
// macOS
app.on('open-url', (event, url) => { handleDeepLink(url); });
// Windows/Linux
app.on('second-instance', (_event, argv) => {
  const url = argv.find(a => a.startsWith('myapp://'));
  if (url) handleDeepLink(url);
});
```

### Tauri

```bash
cargo add tauri-plugin-deep-link
npm install @tauri-apps/plugin-deep-link
```

Configure in `tauri.conf.json` under `plugins.deep-link.desktop.schemes`.

### Wails

No built-in deep link support. Register protocols manually per platform.

## Multi-Window Management

### Electron

```typescript
const secondWindow = new BrowserWindow({
  width: 600, height: 400,
  webPreferences: { preload: join(__dirname, 'preload.js') },
});
secondWindow.loadFile('settings.html');
// Communicate between windows via main process IPC
```

### Tauri

```rust
use tauri::WebviewWindowBuilder;

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    WebviewWindowBuilder::new(&app, "settings", tauri::WebviewUrl::App("/settings".into()))
        .title("Settings")
        .inner_size(600.0, 400.0)
        .build()
        .map_err(|e| e.to_string())?;
    Ok(())
}
```

### Wails

Multi-window is limited in v2 (workarounds exist). Full support in v3 (alpha).

## Feature Support Matrix

| Feature | Electron | Tauri v2 | Wails v2 |
|---------|----------|----------|----------|
| Application menus | Built-in | Built-in | Built-in |
| Context menus | Built-in | Built-in | Frontend only |
| System tray | Built-in | Built-in | Third-party |
| Notifications | Built-in | Plugin | Third-party |
| File dialogs | Built-in | Plugin | Built-in |
| Global shortcuts | Built-in | Plugin | Third-party |
| Clipboard | Built-in | Plugin | Third-party |
| Deep links | Built-in | Plugin | Manual |
| Multi-window | Full | Full | v3 only |
| Touch Bar (macOS) | Yes | No | No |
| Dock badge (macOS) | Yes | No | No |
| Drag and drop | Full | Via events | Via frontend |
| Spellcheck | Built-in (Chromium) | WebView-dependent | WebView-dependent |
| Print | Built-in | Via WebView | Via WebView |
| Screen capture | desktopCapturer | No built-in | No built-in |
