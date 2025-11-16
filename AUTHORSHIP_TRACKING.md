# Code Authorship Tracking

Friendly Parakeet can now infer and track metadata about how your code was written! This feature provides deep insights into your development workflow.

## What Does It Track?

The authorship tracker automatically detects and records:

- **🤖 AI Agent**: Which coding assistant helped write the code
  - Claude / Claude Code
  - GitHub Copilot
  - ChatGPT / GPT-4
  - Cursor AI
  - Windsurf / Codeium
  - TabNine
  - AWS CodeWhisperer
  - Human (no AI assistance detected)

- **💻 IDE / Editor**: What development environment was used
  - VS Code
  - Cursor
  - Windsurf
  - PyCharm / IntelliJ IDEA
  - Vim / Neovim
  - Emacs
  - Sublime Text
  - Xcode
  - And more...

- **🌍 Environment**: Where the code was written
  - Local development machine
  - GitHub Actions
  - GitLab CI
  - CircleCI
  - Jenkins
  - Docker container
  - Kubernetes pod
  - SSH remote session
  - AWS CodeBuild
  - Azure Pipelines

- **🔧 Tools**: What development tools were detected
  - Version control: git
  - Testing frameworks: pytest, jest, etc.
  - Build tools: make, webpack, vite
  - Package managers: pip, npm, yarn, poetry
  - Containerization: docker, docker-compose, kubernetes

- **🎯 Skills / Languages**: Programming languages used
  - Python, JavaScript, TypeScript
  - Go, Rust, Java, Kotlin
  - Ruby, PHP, Swift, C/C++
  - And more...

- **⚙️ Orchestration**: CI/CD system detected
  - GitHub Actions
  - GitLab CI
  - Jenkins
  - CircleCI
  - Travis CI
  - Azure Pipelines

## How It Works

### Automatic Detection

The authorship tracker uses multiple detection methods:

1. **Commit Message Analysis**: Looks for patterns like:
   - `[Claude]` or `feat: add feature using Claude`
   - `[Copilot]` or `GitHub Copilot: implement function`
   - `Co-authored-by: GitHub Copilot`

2. **Environment Variables**: Checks for API keys and tool-specific variables:
   - `ANTHROPIC_API_KEY` → Claude
   - `OPENAI_API_KEY` → ChatGPT
   - `GITHUB_COPILOT` → GitHub Copilot

3. **Running Processes**: Detects active IDEs and AI assistants

4. **Git Configuration**: Reads IDE settings from git config

5. **Project Structure**: Analyzes files to detect tools and languages

6. **Environment Detection**: Identifies CI/CD and runtime environments

## Usage

### Enable Authorship Tracking

Authorship tracking is enabled by default. To disable:

```bash
parakeet config-set track_authorship false
```

To enable embedding metadata in git notes (experimental):

```bash
parakeet config-set embed_authorship_in_notes true
```

### Scan Projects

Run a scan to start collecting authorship data:

```bash
parakeet scan
```

This will track authorship for recent commits in all detected projects.

### View Authorship Information

Show all tracked commits with authorship metadata:

```bash
parakeet authorship
```

Filter by specific agent:

```bash
parakeet authorship --agent claude
parakeet authorship --agent github_copilot
```

Filter by IDE:

```bash
parakeet authorship --ide cursor
parakeet authorship --ide vscode
```

Limit results:

```bash
parakeet authorship --limit 50
```

### View Statistics

Get comprehensive statistics about authorship:

```bash
parakeet authorship-stats
```

Output in JSON format:

```bash
parakeet authorship-stats --format json
```

Example output:
```
📊 Authorship Statistics

==================================================

Total commits tracked: 156

🤖 By Agent:
  claude                 89 commits ( 57.1%) █████████████████
  human                  45 commits ( 28.8%) █████████
  github_copilot         22 commits ( 14.1%) ████

💻 By IDE:
  cursor                 89 commits ( 57.1%)
  vscode                 45 commits ( 28.8%)
  vim                    22 commits ( 14.1%)

🌍 By Environment:
  local                 134 commits ( 85.9%)
  github_actions         22 commits ( 14.1%)

🔧 Top Tools:
  git                   156 commits
  pytest                120 commits
  docker                 89 commits
  npm                    67 commits

🎯 Top Skills/Languages:
  python                156 commits
  javascript             67 commits
  typescript             45 commits
```

### Analyze a Specific Project

Get detailed authorship analysis for a project:

```bash
parakeet analyze-authorship /path/to/project
```

This shows:
- Current detection (what's running now)
- Recent commits with detected agents
- Project tools and languages

Example output:
```
🔍 Analyzing authorship for: friendly-parakeet

Current Detection:
  Agent (env):       claude
  Agent (process):   cursor_ai
  IDE:               cursor
  Environment:       local
  Orchestration:     github_actions
  Tools:             git, pytest, docker, npm
  Skills/Languages:  python, javascript, typescript

📚 Recent Commits (last 10):
  🧠 c346de2b claude           Add AuthorshipTracker with comprehensive TDD tests
  👤 b07eabea human            Initial plan
  🤖 a123b456 github_copilot   Implement new feature
```

## Data Storage

Authorship data is stored in `~/.parakeet/authorship_data.json` with the following structure:

```json
{
  "commits": [
    {
      "sha": "abc123...",
      "agent": "claude",
      "ide": "cursor",
      "environment": "local",
      "tools": ["git", "pytest", "docker"],
      "skills": ["python", "javascript"],
      "orchestration": "github_actions",
      "timestamp": "2024-01-15T10:30:00",
      "confidence": 0.85
    }
  ],
  "sessions": [],
  "statistics": {}
}
```

### Confidence Scoring

Each authorship record includes a confidence score (0.0 to 1.0) based on:
- Agent detection: +0.4
- IDE detection: +0.2
- Environment detection: +0.1
- Tools detected: +0.15
- Skills detected: +0.15

Higher confidence means more metadata was successfully detected.

## Git Notes Integration (Experimental)

You can optionally embed authorship metadata directly in git notes:

```bash
parakeet config-set embed_authorship_in_notes true
```

This adds a git note to each commit containing the full authorship metadata in JSON format. The notes are stored in `refs/notes/authorship`.

To view git notes for a commit:

```bash
git notes --ref=refs/notes/authorship show <commit-sha>
```

## Use Cases

### 1. Team Analytics

Understand how your team uses different tools:
- Which AI assistants are most popular?
- What IDEs do developers prefer?
- Are CI/CD systems being utilized effectively?

### 2. AI Assistance Tracking

Measure the impact of AI coding assistants:
- How many commits involve AI assistance?
- Which AI assistant is most productive?
- Are certain languages better suited for AI assistance?

### 3. Development Environment Optimization

Identify patterns:
- Which tools are used together most often?
- Are there bottlenecks in the development workflow?
- What skills are most frequently needed?

### 4. Documentation and Attribution

Automatically document:
- Which tools and technologies are used in the project
- Development workflow and practices
- Contributor patterns and preferences

### 5. Compliance and Auditing

Track:
- Where code is being written (local vs cloud)
- What tools have access to the codebase
- Security and compliance requirements

## API Usage

You can also use the authorship tracker programmatically:

```python
from parakeet.authorship_tracker import AuthorshipTracker
from pathlib import Path

# Initialize tracker
tracker = AuthorshipTracker(Path("~/.parakeet"))

# Track a git commit
metadata = tracker.track_git_commit(
    Path("/path/to/repo"),
    "abc123..."  # commit SHA
)

# Query commits by agent
claude_commits = tracker.query_by_agent("claude")

# Get statistics
stats = tracker.get_statistics()
print(f"Total commits: {stats['total_commits']}")
print(f"By agent: {stats['by_agent']}")
```

## Privacy and Security

- **Local Storage**: All authorship data is stored locally in `~/.parakeet/`
- **No Telemetry**: Data is never sent to external servers
- **Opt-out**: You can disable authorship tracking anytime with `parakeet config-set track_authorship false`
- **Git Notes**: Git notes are stored locally in your repository and only pushed if you explicitly push the notes ref

## Future Enhancements

Planned features:
- Real-time authorship tracking during active development
- Integration with IDE extensions for more accurate detection
- Machine learning-based agent detection from code patterns
- Time-series analysis of authorship trends
- Export to various formats (CSV, PDF reports)
- Dashboard visualization of authorship data

## Troubleshooting

### No commits are being tracked

Make sure:
1. Authorship tracking is enabled: `parakeet config-show`
2. Projects are being scanned: `parakeet scan`
3. Projects have git commits: `git log` in the project directory

### Agent detection is incorrect

The detector looks for patterns in commit messages. To improve detection:
- Include agent tags in commit messages: `[Claude]`, `[Copilot]`, etc.
- Use environment variables when working with AI assistants
- Ensure the AI assistant process is running when commits are made

### Low confidence scores

Confidence scores are low when minimal metadata is detected. To improve:
- Ensure git is configured correctly
- Have project files (package.json, requirements.txt, etc.) present
- Include CI/CD configuration files
- Use descriptive commit messages with agent tags

---

Made with ❤️ by a friendly parakeet 🦜 (and maybe some AI friends! 🤖)
