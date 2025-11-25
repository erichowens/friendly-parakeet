# Code Authorship Tracking

Friendly Parakeet can now infer and track metadata about how your code was written! This feature provides deep insights into your development workflow with **exhaustive 2025 coverage**.

## What Does It Track?

The authorship tracker automatically detects and records:

- **🤖 AI Agent**: Which coding assistant helped write the code (21 agents)
  - **Major Platforms**: Claude / Claude Code, GitHub Copilot, ChatGPT / GPT-4, Cursor AI, Windsurf / Codeium
  - **2025 Additions**: Amazon Q Developer, Google Gemini Code Assist, Sourcegraph Cody, Replit AI (Ghostwriter), Phind
  - **Emerging Tools**: Pieces for Developers, Blackbox AI, CodeGPT, DeepSeek Coder, CodeLlama
  - **Local AI**: Aider, Continue.dev, Ollama, Jan.ai
  - **Legacy**: TabNine, AWS CodeWhisperer
  - **Human**: No AI assistance detected

- **💻 IDE / Editor**: What development environment was used (49 IDEs)
  - **AI-Powered**: Cursor, Windsurf, Warp Terminal, Replit
  - **Microsoft**: VS Code, Visual Studio, Codespaces
  - **JetBrains**: IntelliJ IDEA, PyCharm, WebStorm, PHPStorm, RubyMine, GoLand, CLion, Rider, DataGrip, RustRover, Aqua, Fleet
  - **Apple**: Xcode
  - **Classic Editors**: Vim/Neovim, Emacs, Sublime Text, Atom, Brackets, Notepad++
  - **Modern Editors**: Zed, Nova, Lapce, Helix, Micro, Positron
  - **Other IDEs**: Eclipse, NetBeans, Android Studio, Code::Blocks, Geany, Kate
  - **Terminals**: Warp, iTerm, Alacritty, Kitty, Hyper, Konsole, GNOME Terminal
  - **Cloud IDEs**: GitHub Codespaces, Gitpod, AWS Cloud9, CodeSandbox, StackBlitz
  - And more...

- **🌍 Environment**: Where the code was written (28+ environments)
  - **Local**: Development machine
  - **Major CI/CD**: GitHub Actions, GitLab CI, CircleCI, Jenkins, Travis CI, Azure Pipelines
  - **Modern CI/CD**: Buildkite, Drone CI, Semaphore CI, Bitbucket Pipelines, TeamCity, Bamboo, GoCD, Concourse CI, Harness, Spinnaker
  - **Cloud Dev**: GitHub Codespaces, Gitpod, Replit, CodeSandbox, StackBlitz
  - **Containers**: Docker, Podman, LXC/LXD, Kubernetes, Nomad, OpenShift, Rancher
  - **Cloud Platforms**: AWS Lambda, Google Cloud, Azure Functions
  - **Remote**: SSH, VS Code Remote Containers

- **🔧 Tools**: What development tools were detected (60+ tools)
  - **Version Control**: git
  - **Python**: pip, pipenv, poetry, pytest, ruff, black, mypy
  - **JavaScript/Node**: npm, yarn, pnpm, bun, deno, jest, vitest, playwright, cypress, mocha, webpack, vite, Next.js, Turborepo, Nx
  - **Java/JVM**: maven, gradle
  - **Build Systems**: make, bazel, cmake
  - **Rust**: cargo
  - **Go**: go modules
  - **PHP**: composer, PHPUnit
  - **Ruby**: bundler, rake, RSpec
  - **Elixir**: mix
  - **Haskell**: stack
  - **Clojure**: leiningen
  - **Containers**: docker, docker-compose, podman, kubernetes, helm
  - **Testing**: cucumber, Robot Framework
  - And more...

- **🎯 Skills / Languages**: Programming languages used (45+ languages)
  - **Popular**: Python, JavaScript, TypeScript, React, Go, Rust, Java, Kotlin, Ruby, PHP, C/C++, C#, Swift
  - **Modern/Emerging**: Zig, V, Nim, Crystal, Elixir, Haskell, OCaml, F#, Scala, Clojure, Erlang, Lua, Dart, Julia
  - **Blockchain**: Solidity, Move, Cairo
  - **Web**: HTML, CSS, SCSS, SASS, LESS, Vue, Svelte
  - **Data**: SQL, R, Markdown
  - **Frameworks**: Django, Flask, FastAPI, React, Vue, Angular, Svelte, Next.js, Express, NestJS, and more
  - And more...

- **⚙️ Orchestration**: CI/CD system detected (15+ platforms)
  - GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis CI, Azure Pipelines
  - Buildkite, Drone CI, Semaphore CI, Bitbucket Pipelines
  - TeamCity, Bamboo, GoCD, Concourse CI
  - Argo Workflows, Tekton

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

## 2025 Exhaustive Coverage

This implementation provides **exhaustive coverage** of all major development tools and platforms in 2025:

### Statistics
- **21 AI Coding Assistants**: From Claude and Copilot to emerging tools like Aider and Ollama
- **49 IDEs and Editors**: Including Warp terminal, all JetBrains products, cloud IDEs, and more
- **28+ CI/CD Platforms**: Major platforms plus emerging tools like Buildkite and Drone CI
- **60+ Development Tools**: Comprehensive coverage of build tools, package managers, and testing frameworks
- **45+ Programming Languages**: From Python and JavaScript to Zig, Solidity, and Cairo
- **15+ Container Platforms**: Docker, Kubernetes, Podman, and orchestration systems

### What's New in This Update
- ✅ **Warp Terminal** - AI-powered terminal detection
- ✅ **Amazon Q Developer** - AWS's AI coding assistant
- ✅ **Google Gemini Code Assist** - Google's AI platform
- ✅ **Sourcegraph Cody** - Enterprise code AI
- ✅ **Replit AI (Ghostwriter)** - Cloud IDE AI
- ✅ **Modern Languages**: Zig, V, Nim, Crystal, Move, Cairo
- ✅ **Modern Tools**: Bun, pnpm, Vitest, Playwright
- ✅ **Cloud Dev Environments**: Codespaces, Gitpod, StackBlitz
- ✅ **Emerging CI/CD**: Buildkite, Drone CI, Argo Workflows, Tekton
- ✅ **Local AI**: Ollama, Jan.ai, Continue.dev, Aider

### Coverage Philosophy
This implementation aims to detect **any possible authorship configuration** in 2025 by:
1. Monitoring all major AI coding assistants (commercial and open-source)
2. Detecting all popular IDEs and editors (traditional and cloud-based)
3. Identifying all CI/CD platforms (legacy and cutting-edge)
4. Recognizing all modern programming languages and frameworks
5. Supporting all containerization and orchestration technologies

The detection is **future-proof** with extensible pattern matching that can easily accommodate new tools as they emerge.

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
