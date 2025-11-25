# 🦜 Friendly Parakeet

Your little coding buddy who crawls through your projects and keeps track of your progress!

**NEW: Mac Menu Bar App!** 🎉 Transform Friendly Parakeet into a delightful Mac menu bar companion with chirping notifications and "Brilliant Budgies" - AI-powered coding ideas generated during off-hours! [Learn more →](MAC_APP_README.md)

## What is Friendly Parakeet?

Friendly Parakeet is a project progress tracker and velocity monitor that:

- 🔍 **Crawls** through your coding folders (default: `~/coding` subdirectories)
- 📊 **Tracks** your progress and velocity across all projects
- 📍 **Generates breadcrumbs** automatically when projects slow down
- 📜 **Analyzes** change history via Git integration
- 💡 **Suggests prompts** to help you resume work with AI coding agents
- 🎨 **Beautiful dashboard** showing your work log, breadcrumbs, and artifacts
- 🔧 **Git maintenance** - Auto-commits uncommitted work with smart messages
- 🚀 **Auto-push** - Keeps your work synced to remote (configurable per-project)
- 📚 **Documentation** - Generates changelogs and time reports automatically
- ⏱️ **Time tracking** - Tracks how long work actually takes on each project
- 🤖 **Authorship tracking** (NEW!) - Infers which AI agent, IDE, and environment wrote your code
- 🖥️ **Mac Menu Bar App** - Native Mac app with chirping notifications
- 💡 **Brilliant Budgies** - AI generates helpful coding ideas during off-hours

## Installation

```bash
# Clone the repository
git clone https://github.com/erichowens/friendly-parakeet.git
cd friendly-parakeet

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# For Mac menu bar app (optional)
pip install -r requirements-mac.txt
```

## Quick Start

### 0. First-Time Setup (Recommended)

```bash
parakeet setup
```

Run the interactive setup wizard to:
- Configure which directories to watch for projects
- Choose between recursive scanning or immediate subdirectories only
- Set the maximum depth for recursive scanning

You can also manage watch paths with these commands:
```bash
# Add a directory to watch
parakeet add-path ~/projects

# Remove a directory from watch list
parakeet remove-path ~/old-projects

# List all watch paths and their status
parakeet list-paths
```

### 1. Scan Your Projects

```bash
parakeet scan
```

This will crawl through your coding folders and discover all projects.

**How scanning works:**
- Parakeet scans **subdirectories** of your watch paths, not the watch paths themselves
- For example, if you add `~/coding`, it will scan `~/coding/project1`, `~/coding/project2`, etc., but NOT `~/coding` itself
- Recursive scanning is enabled by default with a max depth of 3 levels
- Projects are automatically detected by looking for indicator files (`.git`, `package.json`, `setup.py`, etc.)

### 2. View Status

```bash
parakeet status
```

See an overview of all your projects and recent activity.

### 3. Launch the Dashboard

```bash
parakeet dashboard
```

Open your browser to `http://localhost:5000` to see the beautiful dashboard!

### 3b. Or Launch the Mac Menu Bar App (NEW!)

```bash
parakeet menubar
```

Look for the 🦜 icon in your menu bar for quick access to all features!

### 4. View Breadcrumbs

```bash
# View all breadcrumbs
parakeet breadcrumb

# View breadcrumbs for a specific project
parakeet breadcrumb /path/to/project
```

Get helpful prompts to resume work on projects that have slowed down.

### 5. Git Maintenance (NEW!)

```bash
# Run git maintenance on a project (auto-commit + push)
parakeet maintain /path/to/project

# Enable/disable auto-commit for a project
parakeet auto-commit /path/to/project --enabled
parakeet auto-commit /path/to/project --disabled

# Enable/disable auto-push for a project
parakeet auto-push /path/to/project --enabled
parakeet auto-push /path/to/project --disabled
```

Parakeet will automatically commit uncommitted changes with intelligent messages and optionally push them.

### 6. View Changelogs and Time Reports

```bash
# View changelog for a project
parakeet changelog /path/to/project

# View time tracking report
parakeet time-report /path/to/project
```

## Features in Detail

### 🤖 Code Authorship Tracking (NEW!)

Friendly Parakeet can now infer and track metadata about how your code was written:

**What it tracks:**
- **AI Agent**: Claude, GitHub Copilot, ChatGPT, Cursor AI, Windsurf, and more
- **IDE**: VS Code, Cursor, Windsurf, PyCharm, Vim, and others
- **Environment**: Local, GitHub Actions, GitLab CI, Docker, SSH, etc.
- **Tools**: git, pytest, docker, npm, and other development tools
- **Skills**: Programming languages and frameworks detected in your code
- **Orchestration**: CI/CD systems like GitHub Actions, Jenkins, etc.

**Commands:**
```bash
# View authorship information
parakeet authorship

# Filter by agent
parakeet authorship --agent claude

# View statistics
parakeet authorship-stats

# Analyze a specific project
parakeet analyze-authorship /path/to/project
```

[📖 Read the full Authorship Tracking documentation →](AUTHORSHIP_TRACKING.md)

### 🔧 Git Maintenance & Hygiene

Parakeet helps keep your git repositories clean and up-to-date:

**Auto-Commit**:
- Automatically commits uncommitted work
- Generates intelligent commit messages based on file types
- Creates stacked commits when changes are large (>10 files by default)
- Categorizes changes: code, docs, config, tests

**Auto-Push**:
- Optionally pushes commits to remote
- Enabled by default for private repos
- Can be disabled per-project via CLI or dashboard

**Smart Commit Messages**:
- "Auto-commit: Update code (5 files), Update documentation (2 files)"
- "Auto-commit: Update code (part 1, 10 files)" (for stacked commits)

### 📚 Documentation Generation (NEW!)

Parakeet generates markdown documentation in `.parakeet/` directory for each project:

**CHANGELOG.md**:
- Chronological log of work done
- Grouped by date
- Time estimates for each entry

**TIME_REPORT.md**:
- Overall time statistics
- Milestone tracking
- Session history

**AGENT_INSTRUCTIONS.md**:
- Instructions for AI coding agents
- How to track time and log changes
- Best practices for the project

### ⏱️ Time Tracking (NEW!)

Track actual work time on projects:
- Estimates based on commit patterns
- Manual session tracking available via API
- Milestone-based time allocation
- Reports on how long features actually took

### 📊 Progress Tracking

Friendly Parakeet monitors:
- File modifications
- Git commits and history
- Active days per project
- Velocity trends (increasing, stable, decreasing)

### 📍 Smart Breadcrumbs

When a project becomes inactive (default: 7+ days), Friendly Parakeet automatically:
- Analyzes recent commits and changes
- Identifies modified files
- Generates context-aware prompts for AI coding agents
- Helps you quickly resume where you left off

### 💡 AI-Friendly Prompts

Breadcrumbs include helpful prompts like:
- "I'm working on a [type] project called '[name]'. Here's where I left off..."
- "My last commit was: '[message]'. Help me continue from here."
- "I have uncommitted changes in: [files]. Can you help me review and complete these changes?"

### 🎨 Beautiful Dashboard

The web dashboard shows:
- All your projects with activity status
- **NEW**: Toggle auto-commit and auto-push per project
- **NEW**: One-click "Maintain Now" button
- **NEW**: View changelogs directly in the dashboard
- Velocity trends and metrics
- Recent activity timeline
- Breadcrumbs with resumption prompts
- Real-time scanning capabilities

## Configuration

Configuration is stored in `~/.parakeet/config.yaml`. You can modify settings:

```bash
# Set watch paths
parakeet config-set watch_paths '["~/coding", "~/projects"]'

# Set breadcrumb threshold (days)
parakeet config-set breadcrumb_threshold 5

# View current configuration
parakeet config-show
```

### Default Configuration

```yaml
watch_paths:
  - ~/coding
data_dir: ~/.parakeet
scan_interval: 300  # seconds
breadcrumb_threshold: 7  # days
velocity_window: 30  # days
exclude_patterns:
  - node_modules
  - .git
  - __pycache__
  - venv
  - dist
  - build
dashboard_port: 5000
git_maintenance_enabled: true  # Auto-commit and push features
generate_docs: true  # Generate changelogs and time reports
auto_commit_max_files: 10  # Max files before creating stacked commits
scan_recursive: true  # Scan recursively or just immediate subdirectories
scan_max_depth: 3  # Maximum depth for recursive scanning
track_authorship: true  # Track code authorship metadata (NEW!)
embed_authorship_in_notes: false  # Embed authorship in git notes (experimental)
```

## Commands

### Setup and Configuration Commands
- `parakeet setup` - Interactive setup wizard for first-time configuration
- `parakeet add-path PATH` - Add a directory to watch paths
- `parakeet remove-path PATH` - Remove a directory from watch paths
- `parakeet list-paths` - List all watch paths and their status
- `parakeet config-set KEY VALUE` - Set configuration value
- `parakeet config-show` - Show current configuration

### Core Commands
- `parakeet scan` - Scan and update project tracking
- `parakeet status` - Show overall status and statistics
- `parakeet dashboard` - Start the web dashboard
- `parakeet menubar` - Launch the Mac menu bar app (macOS only)
- `parakeet breadcrumb [PROJECT_PATH]` - View breadcrumbs

### Git Maintenance Commands (NEW!)
- `parakeet maintain PROJECT_PATH` - Run git maintenance (auto-commit + push)
- `parakeet auto-commit PROJECT_PATH --enabled/--disabled` - Toggle auto-commit
- `parakeet auto-push PROJECT_PATH --enabled/--disabled` - Toggle auto-push

### Documentation Commands (NEW!)
- `parakeet changelog PROJECT_PATH` - View project changelog
- `parakeet time-report PROJECT_PATH` - View time tracking report

### Authorship Tracking Commands (NEW!)
- `parakeet authorship [--agent AGENT] [--ide IDE] [--limit N]` - View authorship metadata
- `parakeet authorship-stats [--format text|json]` - View authorship statistics
- `parakeet analyze-authorship PROJECT_PATH` - Analyze authorship for a project

## Project Detection

Friendly Parakeet automatically detects projects by looking for:

- **Python**: `setup.py`, `pyproject.toml`, `requirements.txt`, `Pipfile`
- **JavaScript/Node**: `package.json`, `yarn.lock`
- **Ruby**: `Gemfile`, `Rakefile`
- **Go**: `go.mod`, `go.sum`
- **Java**: `pom.xml`, `build.gradle`
- **Rust**: `Cargo.toml`
- **C/C++**: `Makefile`, `CMakeLists.txt`
- **.NET**: `*.csproj`, `*.fsproj`, `*.sln`
- **Git repositories**: `.git`

## Use Cases

### 1. Context Switching

When you have multiple projects and need to switch between them, Friendly Parakeet helps you quickly understand:
- What you were working on
- What changes are pending
- What to do next

### 2. AI Coding Assistant Integration

Copy the generated prompts directly into your AI coding assistant (GitHub Copilot, ChatGPT, etc.) to quickly get back into context.

### 3. Project Health Monitoring

Keep track of which projects are active, slowing down, or stale. Perfect for managers or solo developers juggling multiple codebases.

### 4. Velocity Tracking

Understand your coding patterns and productivity trends across different projects.

## Development

```bash
# Install in development mode
pip install -e .

# Run tests (when available)
pytest

# Run the dashboard in debug mode
python -m parakeet.cli dashboard --port 5000
```

## Data Storage

All data is stored in `~/.parakeet/`:
- `config.yaml` - Configuration
- `project_history.json` - Project tracking data
- `breadcrumbs.json` - Breadcrumb data

## License

MIT License - feel free to use and modify!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ by a friendly parakeet 🦜
