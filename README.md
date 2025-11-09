# 🦜 Friendly Parakeet

Your little coding buddy who crawls through your projects and keeps track of your progress!

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

## Installation

```bash
# Clone the repository
git clone https://github.com/erichowens/friendly-parakeet.git
cd friendly-parakeet

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

### 1. Scan Your Projects

```bash
parakeet scan
```

This will crawl through your coding folders and discover all projects.

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

### 🔧 Git Maintenance & Hygiene (NEW!)

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
```

## Commands

### Core Commands
- `parakeet scan` - Scan and update project tracking
- `parakeet status` - Show overall status and statistics
- `parakeet dashboard` - Start the web dashboard
- `parakeet breadcrumb [PROJECT_PATH]` - View breadcrumbs

### Git Maintenance Commands (NEW!)
- `parakeet maintain PROJECT_PATH` - Run git maintenance (auto-commit + push)
- `parakeet auto-commit PROJECT_PATH --enabled/--disabled` - Toggle auto-commit
- `parakeet auto-push PROJECT_PATH --enabled/--disabled` - Toggle auto-push

### Documentation Commands (NEW!)
- `parakeet changelog PROJECT_PATH` - View project changelog
- `parakeet time-report PROJECT_PATH` - View time tracking report

### Configuration Commands
- `parakeet breadcrumb [PROJECT_PATH]` - View breadcrumbs
- `parakeet config-set KEY VALUE` - Set configuration value
- `parakeet config-show` - Show current configuration

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
