# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Friendly Parakeet is a Python-based project progress tracker that monitors coding projects, tracks velocity, generates breadcrumbs for inactive projects, performs automated git maintenance, and provides a web dashboard. It crawls through coding folders to track progress across multiple projects simultaneously.

## Development Commands

### Installation and Setup
```bash
# Install in development mode with editable installation
pip install -e .

# Install dependencies only
pip install -r requirements.txt
```

### Running the Application
```bash
# Main CLI command
parakeet [COMMAND]

# Core commands
parakeet scan                    # Scan projects and update tracking
parakeet status                  # Show overall status and statistics
parakeet dashboard               # Start web dashboard on http://localhost:5000
parakeet breadcrumb [PROJECT]    # View breadcrumbs for project(s)

# Git maintenance commands
parakeet maintain PROJECT_PATH   # Run git auto-commit and push
parakeet auto-commit PROJECT_PATH --enabled/--disabled
parakeet auto-push PROJECT_PATH --enabled/--disabled

# Documentation commands
parakeet changelog PROJECT_PATH  # View project changelog
parakeet time-report PROJECT_PATH # View time tracking report

# Configuration commands
parakeet config-show             # Display current configuration
parakeet config-set KEY VALUE    # Set configuration value
```

### Development and Testing
```bash
# Run the dashboard in debug mode (direct module execution)
python -m parakeet.cli dashboard --port 5000

# Run example usage
python examples/usage_example.py

# Note: No test suite currently exists - pytest mentioned in README but no tests implemented yet
```

## Architecture and Code Structure

### Core Architecture Pattern
The codebase follows a modular architecture with a central orchestrator pattern:

1. **Parakeet Class** (`src/parakeet/parakeet.py`): Main orchestrator that coordinates all subsystems. It initializes and manages all component managers (scanner, tracker, breadcrumbs, git_maintainer, changelog).

2. **Component Managers**: Each major feature is encapsulated in its own manager class:
   - `ProjectScanner`: Discovers projects by looking for indicator files (.git, package.json, etc.)
   - `ProjectTracker`: Maintains history and calculates velocity metrics
   - `BreadcrumbGenerator`: Creates context-aware prompts for resuming work
   - `GitMaintainer`: Handles auto-commit and auto-push functionality
   - `ChangelogManager`: Generates documentation (changelogs, time reports)
   - `Config`: Manages all configuration with YAML persistence

3. **Data Flow**:
   - All data is persisted in `~/.parakeet/` directory as JSON files
   - `project_history.json`: Tracks all project activity over time
   - `breadcrumbs.json`: Stores generated breadcrumbs for inactive projects
   - Configuration uses YAML format in `config.yaml`

### Key Implementation Details

**Project Detection Logic** (`scanner.py`):
- Projects are identified by presence of specific indicator files (setup.py, package.json, .git, etc.)
- Supports Python, JavaScript, Ruby, Go, Java, Rust, C/C++, .NET project types
- Recursively scans subdirectories in watch paths, excluding patterns like node_modules

**Velocity Tracking** (`tracker.py`):
- Tracks file modifications, git commits, and activity patterns
- Calculates trends (increasing/stable/decreasing) based on activity over time windows
- Stores timestamped snapshots of project state for historical analysis

**Git Integration**:
- Uses GitPython library for all git operations
- Auto-commit groups changes by file type (code, docs, config, tests)
- Creates stacked commits when changes exceed threshold (default: 10 files)
- Smart commit message generation based on changed files

**Dashboard** (`dashboard.py`):
- Flask-based web interface with real-time project monitoring
- API endpoints for toggling settings and triggering maintenance
- Template-based rendering with Jinja2

### Critical Dependencies

- **GitPython**: All git operations depend on this - handles repos, commits, push/pull
- **Flask**: Web dashboard and API endpoints
- **Click**: CLI command structure and argument parsing
- **PyYAML**: Configuration management
- **python-dateutil**: Date/time calculations for velocity and inactivity tracking

### State Management

The application maintains state across runs through JSON files in `~/.parakeet/`:
- Project history accumulates over time (append-only for tracking)
- Breadcrumbs persist until manually cleared
- Per-project settings (auto-commit, auto-push) stored in git maintainer's data

### Entry Points

- CLI: `parakeet` command via console_scripts in setup.py → `parakeet.cli:main`
- Programmatic: Import `Parakeet` class from `parakeet.parakeet`
- Dashboard: Flask app created by `create_app()` in `dashboard.py`