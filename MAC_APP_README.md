# 🦜 Friendly Parakeet Mac App

Transform Friendly Parakeet into a delightful Mac menu bar companion that chirps, tracks your coding, and generates brilliant ideas!

## Features

### 🎯 Menu Bar Integration
- **Parakeet Icon**: Lives in your menu bar with a number badge showing important notifications
- **Quick Access**: All features available from the menu bar dropdown
- **Dark Mode Support**: Icon adapts to your system theme

### 🔊 Budgie Sounds
- **Chirps & Alerts**: Delightful budgie sounds for different events
- **Smart Notifications**: Audio alerts for important changes
- **Mutable**: Toggle sounds on/off from the menu

### 💡 Brilliant Budgies (NEW!)
Your parakeet now thinks during off-hours and generates helpful coding ideas:
- **Unit Test Suggestions**: Identifies modules lacking test coverage
- **Refactoring Ideas**: Suggests improvements for complex code
- **Performance Optimizations**: Spots potential bottlenecks
- **Documentation Gaps**: Finds undocumented code
- **Creative Features**: Proposes new tools and workflows

Ideas are generated during off-hours (late night/early morning) when your parakeet has time to think!

### 📊 Core Features
- **Auto-Scanning**: Continuously monitors your projects
- **Breadcrumb Alerts**: Notifications when projects need attention
- **Dashboard Access**: One-click to open the web dashboard
- **Git Maintenance**: Auto-commit and push from the menu

## Installation

### Prerequisites
- macOS 11.0 or later
- Python 3.8+
- Git

### Quick Start (Development)

1. **Install Mac-specific dependencies**:
```bash
pip install -r requirements-mac.txt
```

2. **Generate the parakeet icon**:
```bash
cd assets
python generate_icon.py
cd ..
```

3. **Run the menu bar app**:
```bash
parakeet menubar
# OR directly with Python:
python -m parakeet.cli menubar
```

### Building a Standalone Mac App

1. **Install py2app**:
```bash
pip install py2app
```

2. **Build the app**:
```bash
python setup_mac.py py2app
```

3. **Find your app**:
The built app will be in `dist/Friendly Parakeet.app`

4. **Install the app**:
```bash
# Copy to Applications
cp -r "dist/Friendly Parakeet.app" /Applications/

# Or drag the app to your Applications folder
```

### Creating a DMG for Distribution

```bash
# Create a DMG for easy distribution
hdiutil create -volname "Friendly Parakeet" -srcfolder dist -ov -format UDZO "Friendly Parakeet.dmg"
```

## Usage

### Starting the App

**From Command Line**:
```bash
parakeet menubar
```

**From Applications**:
Double-click "Friendly Parakeet" in your Applications folder

### Menu Bar Interface

Click the 🦜 icon in your menu bar to access:

- **📊 Dashboard**: Opens the web dashboard
- **🔍 Scan Projects**: Manually trigger a project scan
- **📍 Recent Breadcrumbs**: View and copy prompts for inactive projects
- **💡 Brilliant Budgies**: View AI-generated improvement ideas
- **🔊 Sounds**: Toggle sound effects
- **⚙️ Preferences**: Edit configuration

### Brilliant Budgies Ideas

When your parakeet has a new idea:
1. You'll hear a "eureka" sound
2. The badge count will increase
3. Click 💡 Brilliant Budgies to view ideas
4. Click an idea to see details
5. Choose "Yes, let's do it!" to create an implementation task

### Notifications

The parakeet will notify you about:
- **Inactive Projects**: Projects that haven't been touched in 7+ days
- **New Breadcrumbs**: Context for resuming work
- **Brilliant Ideas**: AI-generated improvements
- **Git Status**: Uncommitted changes that need attention

## Configuration

### Sound Files

Place custom sound files in `assets/sounds/`:
- `budgie_hello.wav` - Startup sound
- `budgie_alert.wav` - Important notifications
- `budgie_eureka.wav` - New ideas
- `budgie_chirp.wav` - General interactions
- `budgie_happy.wav` - Success events

### Settings

Edit `~/.parakeet/config.yaml`:

```yaml
# Brilliant Budgies settings
brilliant_budgies_enabled: true
brilliant_budgies_hours: [0, 1, 2, 3, 4, 5, 22, 23]  # Off-hours for idea generation
brilliant_budgies_frequency: 3600  # Check every hour

# Menu bar settings
menubar_sounds_enabled: true
menubar_auto_launch: false  # Launch at login
menubar_scan_interval: 300  # 5 minutes
```

## Development

### Project Structure
```
src/parakeet/
├── menubar_app.py        # Main menu bar application
├── brilliant_budgies.py  # AI idea generation system
├── parakeet.py          # Core orchestrator
├── scanner.py           # Project discovery
├── tracker.py           # Progress tracking
├── breadcrumbs.py       # Context generation
└── ...

assets/
├── parakeet_icon.png    # Menu bar icon
├── parakeet_icon.icns   # macOS icon file
└── sounds/              # Budgie sound effects
```

### Adding New Brilliant Budgie Ideas

Edit `brilliant_budgies.py` to add new idea templates:

```python
self.idea_templates['new_category'] = {
    'title_formats': ["Template {variable}"],
    'descriptions': ["Detailed description with {variable}"]
}
```

### Customizing Sounds

Create custom sounds using:
1. Text-to-speech: `say -v "Bells" "chirp" -o chirp.aiff`
2. Convert to WAV: `afconvert chirp.aiff chirp.wav`
3. Or use the Python script in `assets/sounds/README.md`

## Troubleshooting

### App Won't Start
- Check Python version: `python --version` (needs 3.8+)
- Install dependencies: `pip install -r requirements-mac.txt`
- Check for port conflicts if dashboard won't open

### No Sound
- Check system volume
- Verify sound files exist in `assets/sounds/`
- Toggle sounds off/on in menu
- Check macOS sound permissions

### Icon Not Showing
- Generate icon: `cd assets && python generate_icon.py`
- Restart the app
- Check menu bar space (might be hidden if too many icons)

### Brilliant Budgies Not Working
- Check if enabled in menu
- Verify it's during off-hours (late night/early morning)
- Check `~/.parakeet/brilliant_budgies.json` for saved ideas
- Look for errors in console output

## Uninstalling

1. Quit the app (menu → Quit)
2. Remove from Applications: `rm -rf "/Applications/Friendly Parakeet.app"`
3. Remove data (optional): `rm -rf ~/.parakeet`
4. Remove Python package: `pip uninstall friendly-parakeet`

## Future Enhancements

- **Voice Commands**: "Hey Parakeet, what should I work on?"
- **AI Integration**: Connect to OpenAI/Claude for smarter Brilliant Budgies
- **Team Sync**: Share breadcrumbs and ideas with your team
- **Focus Mode**: Pomodoro timer with chirp reminders
- **Code Review**: Automated PR checking and suggestions
- **Metric Dashboards**: Productivity analytics and insights

## License

MIT License - Your parakeet is free to fly! 🦜

---

Made with ❤️ and chirps by Friendly Parakeet