# 🚀 Friendly Parakeet Distribution Guide

## Overview

This guide explains how to distribute Friendly Parakeet as a Mac app WITHOUT exposing your source code. We'll use py2app to create a compiled binary, sign it for distribution, and set up secure update mechanisms.

## 🔒 Source Code Protection

### What Gets Protected

When you build with py2app:
- Python source gets compiled to `.pyc` bytecode
- All code bundled inside the `.app` package
- API keys and secrets stored in Keychain (never in code)
- Backend server code remains completely separate

### What Users Get

- A signed `.app` bundle they can drag to Applications
- No access to original Python source code
- No ability to modify core functionality
- Professional Mac app experience

## 📦 Building for Distribution

### Step 1: Prepare Your Environment

```bash
# Create clean virtual environment
python3 -m venv dist_env
source dist_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install py2app pyinstaller
```

### Step 2: Create py2app Setup

Create `setup.py`:

```python
"""
Friendly Parakeet Mac App Builder
"""
from setuptools import setup
import os

APP = ['src/parakeet/menubar_app.py']
DATA_FILES = [
    ('assets', ['assets/parakeet_icon.png', 'assets/parakeet.icns']),
    ('sounds', ['sounds/chirp.mp3', 'sounds/alert.mp3', 'sounds/idea.mp3']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/parakeet.icns',
    'plist': {
        'LSUIElement': True,  # Hide from dock (menu bar only)
        'CFBundleName': 'Friendly Parakeet',
        'CFBundleDisplayName': 'Friendly Parakeet',
        'CFBundleIdentifier': 'com.yourcompany.friendlyparakeet',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2024 Your Company. All rights reserved.',
        'LSMinimumSystemVersion': '10.15.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': [
        'rumps', 'keyring', 'requests', 'openai',
        'psutil', 'git', 'watchdog', 'httpx'
    ],
    'includes': [
        'parakeet.scanner', 'parakeet.tracker',
        'parakeet.breadcrumbs', 'parakeet.brilliant_budgies',
        'parakeet.ide_watcher', 'parakeet.subscription_manager'
    ],
    'excludes': [
        'matplotlib', 'numpy', 'pandas', 'scipy',  # Exclude unused heavy packages
        'test', 'unittest', 'pytest'  # Exclude test code
    ],
    'optimize': 2,  # Optimize bytecode
}

setup(
    app=APP,
    name='Friendly Parakeet',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Step 3: Build the App

```bash
# Clean previous builds
rm -rf build dist

# Build in alias mode for testing
python setup.py py2app -A

# Test the app
./dist/Friendly\ Parakeet.app/Contents/MacOS/Friendly\ Parakeet

# Build for distribution (compiled)
python setup.py py2app

# The app is now in dist/Friendly Parakeet.app
```

## 🔏 Code Signing & Notarization

### Step 1: Get Apple Developer Certificate

1. Join Apple Developer Program ($99/year)
2. Create Developer ID Application certificate
3. Download and install in Keychain

### Step 2: Sign the App

```bash
# Find your certificate
security find-identity -v -p codesigning

# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  --options runtime \
  --entitlements entitlements.plist \
  "dist/Friendly Parakeet.app"

# Verify signature
codesign --verify --verbose "dist/Friendly Parakeet.app"
spctl --assess --verbose "dist/Friendly Parakeet.app"
```

Create `entitlements.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

### Step 3: Notarize with Apple

```bash
# Create ZIP for notarization
ditto -c -k --keepParent "dist/Friendly Parakeet.app" "FriendlyParakeet.zip"

# Submit for notarization
xcrun notarytool submit FriendlyParakeet.zip \
  --apple-id "your-apple-id@example.com" \
  --password "app-specific-password" \
  --team-id "TEAMID" \
  --wait

# Staple the ticket
xcrun stapler staple "dist/Friendly Parakeet.app"
```

## 💿 Creating DMG Installer

### Step 1: Install create-dmg

```bash
brew install create-dmg
```

### Step 2: Create DMG

```bash
# Create DMG with drag-to-install UI
create-dmg \
  --volname "Friendly Parakeet" \
  --volicon "assets/parakeet.icns" \
  --background "assets/dmg_background.png" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Friendly Parakeet.app" 175 190 \
  --hide-extension "Friendly Parakeet.app" \
  --app-drop-link 425 190 \
  --no-internet-enable \
  "FriendlyParakeet-1.0.0.dmg" \
  "dist/"

# Sign the DMG
codesign --sign "Developer ID Application: Your Name (TEAMID)" \
  "FriendlyParakeet-1.0.0.dmg"

# Notarize the DMG
xcrun notarytool submit "FriendlyParakeet-1.0.0.dmg" \
  --apple-id "your-apple-id@example.com" \
  --password "app-specific-password" \
  --team-id "TEAMID" \
  --wait

# Staple the ticket
xcrun stapler staple "FriendlyParakeet-1.0.0.dmg"
```

## 🔄 Auto-Update System

### Sparkle Framework Integration

Add to `src/parakeet/updater.py`:

```python
"""
Auto-update system using Sparkle (or custom solution)
"""
import hashlib
import httpx
import tempfile
import subprocess
import json
from packaging import version

class ParakeetUpdater:
    def __init__(self):
        self.update_url = "https://api.friendlyparakeet.com/updates/mac"
        self.current_version = "1.0.0"

    async def check_for_updates(self):
        """Check if updates are available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.update_url}/latest",
                    params={"current": self.current_version}
                )
                data = response.json()

                if version.parse(data['version']) > version.parse(self.current_version):
                    return {
                        'available': True,
                        'version': data['version'],
                        'download_url': data['download_url'],
                        'release_notes': data['release_notes'],
                        'sha256': data['sha256']
                    }
        except:
            pass
        return {'available': False}

    async def download_and_install(self, update_info):
        """Download and install update"""
        # Download DMG
        async with httpx.AsyncClient() as client:
            response = await client.get(update_info['download_url'])

            # Verify checksum
            if hashlib.sha256(response.content).hexdigest() != update_info['sha256']:
                raise ValueError("Update verification failed!")

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.dmg', delete=False) as f:
                f.write(response.content)
                dmg_path = f.name

        # Mount DMG and copy app
        subprocess.run(['hdiutil', 'attach', dmg_path])
        subprocess.run([
            'cp', '-R',
            '/Volumes/Friendly Parakeet/Friendly Parakeet.app',
            '/Applications/'
        ])
        subprocess.run(['hdiutil', 'detach', '/Volumes/Friendly Parakeet'])

        # Restart app
        subprocess.run(['open', '/Applications/Friendly Parakeet.app'])
        sys.exit(0)
```

## 🌐 Distribution Channels

### Option 1: Direct Download (Recommended)

1. **Create Landing Page**:
   - Host on friendlyparakeet.com
   - Include screenshots and features
   - Direct download link to DMG
   - Auto-update server for versions

2. **CDN Setup**:
   ```bash
   # Upload to CDN (CloudFlare, AWS S3, etc)
   aws s3 cp FriendlyParakeet-1.0.0.dmg \
     s3://downloads.friendlyparakeet.com/ \
     --acl public-read
   ```

### Option 2: Mac App Store

1. Additional requirements:
   - Sandbox entitlements
   - App Store Connect account
   - Review process (1-2 weeks)
   - 30% revenue share on subscriptions

2. Modifications needed:
   - Use StoreKit for subscriptions
   - Sandbox file access
   - No direct keychain access

### Option 3: Homebrew Cask

Create `homebrew-cask/friendlyparakeet.rb`:

```ruby
cask "friendly-parakeet" do
  version "1.0.0"
  sha256 "YOUR_SHA256_HERE"

  url "https://downloads.friendlyparakeet.com/FriendlyParakeet-#{version}.dmg"
  name "Friendly Parakeet"
  desc "AI-powered coding companion for Mac"
  homepage "https://friendlyparakeet.com"

  app "Friendly Parakeet.app"

  zap trash: [
    "~/Library/Preferences/com.yourcompany.friendlyparakeet.plist",
    "~/Library/Application Support/Friendly Parakeet",
  ]
end
```

Users install with:
```bash
brew install --cask friendly-parakeet
```

## 🛡️ Additional Protection Measures

### 1. License Verification

Add to `subscription_manager.py`:

```python
def verify_license(self):
    """Verify app license on startup"""
    machine_id = subprocess.check_output(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice']).decode()
    # Hash machine ID with secret
    license_key = hashlib.sha256(f"{machine_id}{SECRET}".encode()).hexdigest()
    # Verify with server
    return self.api_client.verify_license(license_key)
```

### 2. Binary Obfuscation

```bash
# Use pyarmor for additional protection
pip install pyarmor
pyarmor obfuscate --recursive src/parakeet/

# Then build with py2app
python setup.py py2app
```

### 3. Anti-Tampering

```python
def verify_integrity(self):
    """Check app hasn't been modified"""
    app_path = os.path.dirname(os.path.dirname(sys.executable))

    # Verify code signature
    result = subprocess.run(
        ['codesign', '--verify', app_path],
        capture_output=True
    )

    if result.returncode != 0:
        sys.exit("App integrity check failed!")
```

## 📊 Analytics & Crash Reporting

### Sentry Integration

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    environment="production",
    release=f"friendly-parakeet@{VERSION}",
    traces_sample_rate=0.1,
)
```

## 🚀 Launch Checklist

- [ ] Source code compiled with py2app
- [ ] App signed with Developer ID
- [ ] App notarized with Apple
- [ ] DMG created and signed
- [ ] Auto-update server configured
- [ ] Landing page ready
- [ ] Download analytics setup
- [ ] Crash reporting configured
- [ ] License system activated
- [ ] CDN configured for downloads
- [ ] Homebrew cask submitted (optional)
- [ ] Product Hunt launch planned
- [ ] Documentation website ready

## 📈 Marketing Distribution

### Launch Strategy

1. **Soft Launch**:
   - Beta testers via TestFlight
   - Direct downloads for early adopters
   - Gather feedback, fix issues

2. **Public Launch**:
   - Product Hunt
   - Hacker News Show HN
   - Dev.to article
   - Twitter/X announcement
   - Reddit (r/macapps, r/programming)

3. **Ongoing**:
   - SEO-optimized landing page
   - YouTube demos
   - Blog posts about features
   - Developer testimonials

## 💰 Revenue Protection

### Subscription Verification

The app checks subscription status:
1. On startup
2. Before AI operations
3. Cached for offline use (24 hours)

Server-side protections:
- API rate limiting
- Usage tracking
- Fraud detection
- Payment verification

## 🔧 Troubleshooting Distribution

### Common Issues

1. **"App is damaged"**:
   - Not notarized properly
   - Solution: Re-notarize and staple

2. **"Can't be opened - unidentified developer"**:
   - Not signed properly
   - Solution: Sign with Developer ID

3. **Crashes on launch**:
   - Missing dependencies
   - Solution: Check py2app includes

4. **Update fails**:
   - Permissions issue
   - Solution: Request admin privileges

## 📝 Legal Requirements

1. **Privacy Policy**: Required for App Store
2. **Terms of Service**: Define usage limits
3. **EULA**: End user license agreement
4. **Export Compliance**: For encryption

---

## Quick Start Distribution

```bash
# 1. Build the app
python setup.py py2app

# 2. Sign it
codesign --deep --force --sign "Developer ID" "dist/Friendly Parakeet.app"

# 3. Create DMG
create-dmg "FriendlyParakeet.dmg" "dist/"

# 4. Upload to CDN
aws s3 cp FriendlyParakeet.dmg s3://downloads.friendlyparakeet.com/

# 5. Update website download link
echo "https://downloads.friendlyparakeet.com/FriendlyParakeet.dmg"
```

Your source code is now protected and ready for distribution! 🦜🚀