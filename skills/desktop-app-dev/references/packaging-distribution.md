# Packaging and Distribution

Sources: electron-builder docs, Tauri bundler docs, Wails build docs, Apple Developer docs, Microsoft Authenticode docs, 2025-2026 distribution patterns

Covers: platform-specific installers, code signing (macOS/Windows), notarization, auto-update mechanisms, CI/CD build pipelines, distribution channels, bundle size optimization.

## Platform Installer Formats

| Platform | Formats | Notes |
|----------|---------|-------|
| macOS | `.dmg`, `.pkg`, `.app` (in zip) | DMG most common for direct distribution |
| Windows | `.exe` (NSIS), `.msi` (WiX) | NSIS for consumer, MSI for enterprise |
| Linux | `.AppImage`, `.deb`, `.rpm`, `.snap` | AppImage most portable, deb for Ubuntu/Debian |

## Electron Packaging

### electron-builder (Most Popular)

```json
// package.json
{
  "build": {
    "appId": "com.example.myapp",
    "productName": "My App",
    "directories": { "output": "release" },
    "mac": {
      "target": ["dmg", "zip"],
      "category": "public.app-category.developer-tools",
      "icon": "build/icon.icns",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "win": {
      "target": ["nsis"],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "perMachine": false
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "build/icons",
      "category": "Development"
    }
  }
}
```

Build commands:

```bash
npx electron-builder --mac     # macOS
npx electron-builder --win     # Windows
npx electron-builder --linux   # Linux
npx electron-builder -mwl      # All platforms (from macOS)
```

### electron-forge Makers

```json
// forge.config.ts
{
  "makers": [
    { "name": "@electron-forge/maker-dmg" },
    { "name": "@electron-forge/maker-squirrel" },
    { "name": "@electron-forge/maker-deb" }
  ]
}
```

```bash
npx electron-forge make
```

### electron-builder vs electron-forge for Packaging

| Aspect | electron-builder | electron-forge |
|--------|-----------------|----------------|
| Configuration | package.json or yml | forge.config.ts |
| Auto-update | electron-updater | Squirrel (Windows), native (macOS) |
| Platform targets | Extensive | Good |
| ASAR support | Built-in | Built-in |
| Code signing | Built-in | Via makers |
| Recommendation | Most projects | Forge-specific workflows |

## Tauri Packaging

Tauri bundles are configured in `tauri.conf.json`:

```jsonc
{
  "bundle": {
    "active": true,
    "targets": "all",  // Or: ["dmg", "nsis", "appimage", "deb"]
    "identifier": "com.example.myapp",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": [],   // Extra files to bundle
    "macOS": {
      "minimumSystemVersion": "10.13",
      "signingIdentity": null,  // Set for code signing
      "entitlements": null
    },
    "windows": {
      "wix": null,     // Use WiX for MSI
      "nsis": null     // Use NSIS for exe installer
    },
    "linux": {
      "deb": { "depends": [] },
      "appimage": { "bundleMediaFramework": false }
    }
  }
}
```

```bash
npx tauri build          # Build for current platform
npx tauri build --target universal-apple-darwin  # Universal macOS binary
```

## Wails Packaging

```bash
wails build              # Production build for current platform
wails build -platform darwin/universal  # Universal macOS binary
wails build -nsis        # Windows NSIS installer
```

For macOS `.dmg` or Windows `.msi`, use platform-specific tools post-build:

```bash
# macOS DMG (after wails build)
hdiutil create -volname "My App" -srcfolder build/bin -ov -format UDZO MyApp.dmg

# Windows MSI (use WiX manually)
```

## Code Signing

### macOS Code Signing

**Required for distribution** — unsigned apps trigger Gatekeeper warnings.

Prerequisites:
- Apple Developer account ($99/year)
- Developer ID Application certificate
- Developer ID Installer certificate (for .pkg)

#### Electron (via electron-builder)

Set environment variables:

```bash
export APPLE_ID="your@email.com"
export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export APPLE_TEAM_ID="XXXXXXXXXX"
export CSC_LINK="/path/to/cert.p12"  # Or base64 encoded
export CSC_KEY_PASSWORD="certificate-password"
```

electron-builder signs and notarizes automatically when these are set.

#### Tauri

```bash
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (XXXXXXXXXX)"
export APPLE_ID="your@email.com"
export APPLE_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export APPLE_TEAM_ID="XXXXXXXXXX"
```

Tauri signs during `tauri build` when identity is available.

#### Manual Signing (Any Framework)

```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  --options runtime \
  MyApp.app
```

### macOS Notarization

Required for apps distributed outside the Mac App Store (macOS 10.15+).

```bash
# Submit for notarization
xcrun notarytool submit MyApp.dmg \
  --apple-id "your@email.com" \
  --password "xxxx-xxxx-xxxx-xxxx" \
  --team-id "XXXXXXXXXX" \
  --wait

# Staple the ticket
xcrun stapler staple MyApp.dmg
```

electron-builder and Tauri handle notarization automatically when configured.

### Windows Code Signing

Prerequisites:
- Code signing certificate from CA (DigiCert, Sectigo, etc.)
- EV certificate recommended (SmartScreen reputation from day one)

#### Electron

```bash
export CSC_LINK="/path/to/cert.pfx"
export CSC_KEY_PASSWORD="password"
```

#### Tauri

Configure in `tauri.conf.json` or set `TAURI_SIGNING_PRIVATE_KEY`.

#### Manual Signing

```powershell
signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com /td sha256 MyApp.exe
```

### Linux

No mandatory code signing. Optional GPG signing for package repositories.

## Auto-Update Mechanisms

### Electron (electron-updater)

```typescript
// main process
import { autoUpdater } from 'electron-updater';

autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});

autoUpdater.on('update-available', (info) => {
  mainWindow.webContents.send('update-available', info.version);
});
autoUpdater.on('update-downloaded', () => {
  mainWindow.webContents.send('update-downloaded');
});
```

```json
// package.json
{
  "build": {
    "publish": [{
      "provider": "github",
      "owner": "your-org",
      "repo": "your-app"
    }]
  }
}
```

Supports: GitHub Releases, S3, generic HTTP server.

### Tauri (updater plugin)

```bash
cargo add tauri-plugin-updater
npm install @tauri-apps/plugin-updater
```

```jsonc
// tauri.conf.json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ],
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ..."  // Required: Ed25519 public key
    }
  }
}
```

Tauri requires cryptographic signature verification for updates (mandatory).

Generate signing keys:

```bash
npx tauri signer generate -w ~/.tauri/myapp.key
```

### Wails

No built-in auto-updater. Implement manually with Go packages:

```go
import "github.com/blang/semver"
// Check version endpoint, download new binary, replace and restart
```

Or use a third-party solution like `go-update`.

## CI/CD Build Pipelines

### GitHub Actions (Recommended)

#### Electron

```yaml
name: Build
on: push
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run build
      - name: Package
        run: npx electron-builder --publish never
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: release-${{ matrix.os }}
          path: release/*
```

#### Tauri

```yaml
name: Build
on: push
jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
          - os: macos-latest
            target: aarch64-apple-darwin
          - os: windows-latest
            target: x86_64-pc-windows-msvc
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - uses: dtolnay/rust-toolchain@stable
      - run: npm ci
      - run: npx tauri build
        env:
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
```

#### Release Workflow

1. Tag version (`v1.2.3`) triggers CI
2. Build on all three platforms (matrix strategy)
3. Sign and notarize (macOS/Windows)
4. Upload installers to GitHub Releases
5. Update manifest for auto-updater endpoint
6. Notify users (in-app or changelog)

## Distribution Channels

| Channel | Electron | Tauri | Wails |
|---------|----------|-------|-------|
| GitHub Releases | Yes | Yes | Yes |
| Website download | Yes | Yes | Yes |
| Mac App Store | Possible (complex) | Possible | No |
| Microsoft Store | Possible | Possible | No |
| Snap Store | Yes | Yes | No |
| Flathub | Yes | Possible | No |
| Homebrew Cask | Yes (custom tap) | Yes | Yes |
| WinGet | Yes | Yes | Yes |

## Bundle Size Optimization

### Electron

| Technique | Impact |
|-----------|--------|
| ASAR archive | Default, compresses resources |
| `npm prune --production` | Remove devDependencies |
| Tree-shaking (Vite/Webpack) | Remove unused code |
| Exclude unnecessary files | `.map`, test files, docs |
| Use `asarUnpack` sparingly | Only for native modules |
| Avoid large dependencies | Check with `npx cost-of-modules` |

Minimum realistic size: ~80 MB (Chromium is the floor).

### Tauri

Already small (3-8 MB). Further optimization:

```toml
# src-tauri/Cargo.toml
[profile.release]
strip = true          # Strip debug symbols
lto = true            # Link-time optimization
codegen-units = 1     # Better optimization
opt-level = "s"       # Optimize for size (or "z" for smallest)
panic = "abort"       # Smaller binary
```

### Wails

```bash
# Go build flags for smaller binary
wails build -ldflags "-s -w"
# Optional: UPX compression
upx --best build/bin/my-app
```
