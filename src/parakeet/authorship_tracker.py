"""Authorship metadata tracking for code.

This module provides capabilities to infer and track metadata about how code was written:
- Which agent (Claude, GitHub Copilot, ChatGPT, human, etc.)
- Which IDE (VS Code, Cursor, Windsurf, etc.)
- Which environment (local, cloud, container, SSH, etc.)
- What tools and orchestration were used
- What skills and capabilities were involved
"""

import os
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import psutil

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class AuthorshipMetadata:
    """Metadata about code authorship."""
    
    agent: str = "unknown"
    ide: str = "unknown"
    environment: str = "unknown"
    tools: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    orchestration: str = "unknown"
    timestamp: Optional[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.tools is None:
            self.tools = []
        if self.skills is None:
            self.skills = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthorshipMetadata':
        """Create from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            AuthorshipMetadata instance
        """
        return cls(**data)


class AuthorshipTracker:
    """Tracks authorship metadata for code commits."""
    
    # Agent detection patterns - Comprehensive 2025 coverage
    AGENT_PATTERNS = {
        # Major AI Coding Assistants
        'claude': [
            r'claude',
            r'anthropic',
            r'\[claude\]',
            r'claude code',
            r'claude\.ai',
        ],
        'github_copilot': [
            r'copilot',
            r'github copilot',
            r'\[copilot\]',
            r'co-authored-by.*copilot',
        ],
        'chatgpt': [
            r'chatgpt',
            r'gpt-[34]',
            r'openai',
            r'\[gpt\]',
            r'gpt-4o',
            r'gpt-3\.5',
        ],
        'cursor_ai': [
            r'cursor ai',
            r'cursor assistant',
            r'\[cursor\]',
        ],
        'windsurf_ai': [
            r'windsurf',
            r'codeium',
            r'\[windsurf\]',
        ],
        'tabnine': [
            r'tabnine',
            r'\[tabnine\]',
        ],
        'codewhisperer': [
            r'codewhisperer',
            r'aws codewhisperer',
        ],
        # 2025 AI Assistants
        'amazon_q': [
            r'amazon q',
            r'amazon q developer',
            r'\[amazon.?q\]',
        ],
        'gemini': [
            r'gemini',
            r'bard',
            r'google gemini',
            r'gemini code assist',
            r'\[gemini\]',
        ],
        'sourcegraph_cody': [
            r'cody',
            r'sourcegraph',
            r'\[cody\]',
        ],
        'replit_ai': [
            r'replit',
            r'ghostwriter',
            r'\[replit\]',
        ],
        'phind': [
            r'phind',
            r'\[phind\]',
        ],
        'pieces': [
            r'pieces',
            r'pieces for developers',
            r'\[pieces\]',
        ],
        'blackbox_ai': [
            r'blackbox',
            r'blackbox ai',
            r'\[blackbox\]',
        ],
        'codegpt': [
            r'codegpt',
            r'\[codegpt\]',
        ],
        'deepseek': [
            r'deepseek',
            r'deepseek coder',
            r'\[deepseek\]',
        ],
        'codellama': [
            r'codellama',
            r'code llama',
            r'\[codellama\]',
        ],
        'aider': [
            r'aider',
            r'\[aider\]',
        ],
        'continue_dev': [
            r'continue',
            r'continue\.dev',
            r'\[continue\]',
        ],
        'ollama': [
            r'ollama',
            r'\[ollama\]',
        ],
        'jan_ai': [
            r'jan\.ai',
            r'jan ai',
            r'\[jan\]',
        ],
    }
    
    # IDE detection patterns - Comprehensive 2025 coverage
    IDE_PATTERNS = {
        # AI-Powered IDEs
        'cursor': ['cursor'],
        'windsurf': ['windsurf'],
        'warp': ['warp', 'warpterminal'],  # AI-powered terminal
        'replit': ['replit'],
        # Microsoft IDEs
        'vscode': ['code', 'vscode', 'visual studio code', 'code-insiders', 'codium', 'vscodium'],
        'visual_studio': ['devenv', 'visual studio'],
        # JetBrains Family
        'intellij': ['idea', 'intellij', 'idea64'],
        'pycharm': ['pycharm'],
        'webstorm': ['webstorm'],
        'phpstorm': ['phpstorm'],
        'rubymine': ['rubymine'],
        'goland': ['goland'],
        'clion': ['clion'],
        'rider': ['rider'],
        'datagrip': ['datagrip'],
        'rustrover': ['rustrover'],
        'aqua': ['aqua'],
        'fleet': ['fleet'],
        # Apple IDEs
        'xcode': ['xcode'],
        # Editors
        'vim': ['vim', 'nvim', 'neovim'],
        'emacs': ['emacs'],
        'sublime': ['sublime', 'sublime_text', 'subl'],
        'atom': ['atom'],
        'brackets': ['brackets'],
        'notepad++': ['notepad++', 'notepadplusplus'],
        'geany': ['geany'],
        'kate': ['kate'],
        # Modern Editors
        'zed': ['zed'],
        'nova': ['nova'],
        'lapce': ['lapce'],
        'helix': ['helix', 'hx'],
        'micro': ['micro'],
        'positron': ['positron'],
        # Other IDEs
        'eclipse': ['eclipse'],
        'netbeans': ['netbeans'],
        'android_studio': ['android studio', 'studio'],
        'codeblocks': ['codeblocks', 'code::blocks'],
        # Terminals
        'iterm': ['iterm', 'iterm2'],
        'terminal': ['terminal', 'terminal.app'],
        'alacritty': ['alacritty'],
        'kitty': ['kitty'],
        'hyper': ['hyper'],
        'konsole': ['konsole'],
        'gnome_terminal': ['gnome-terminal'],
        # Cloud IDEs
        'codespaces': ['codespaces'],
        'gitpod': ['gitpod'],
        'cloud9': ['cloud9'],
        'codesandbox': ['codesandbox'],
        'stackblitz': ['stackblitz'],
    }
    
    # Environment detection - Comprehensive 2025 coverage
    CI_ENVIRONMENTS = {
        # Major CI/CD Platforms
        'GITHUB_ACTIONS': 'github_actions',
        'GITLAB_CI': 'gitlab_ci',
        'CIRCLECI': 'circleci',
        'TRAVIS': 'travis_ci',
        'JENKINS_URL': 'jenkins',
        'JENKINS_HOME': 'jenkins',
        'CODEBUILD_BUILD_ID': 'aws_codebuild',
        'AZURE_PIPELINES': 'azure_pipelines',
        'TF_BUILD': 'azure_pipelines',
        # Additional CI/CD
        'BUILDKITE': 'buildkite',
        'DRONE': 'drone_ci',
        'SEMAPHORE': 'semaphore_ci',
        'BITBUCKET_PIPELINE_UUID': 'bitbucket_pipelines',
        'TEAMCITY_VERSION': 'teamcity',
        'bamboo_buildKey': 'bamboo',
        'GO_PIPELINE_NAME': 'gocd',
        'CONCOURSE_VERSION': 'concourse_ci',
        'HARNESS_PIPELINE_ID': 'harness',
        'SPINNAKER_EXECUTION_ID': 'spinnaker',
        # Cloud Development Environments
        'CODESPACES': 'github_codespaces',
        'GITPOD_WORKSPACE_ID': 'gitpod',
        'REPLIT': 'replit',
        'CODESANDBOX_SSE': 'codesandbox',
        'STACKBLITZ': 'stackblitz',
        # Container Orchestration
        'KUBERNETES_SERVICE_HOST': 'kubernetes',
        'NOMAD_ALLOC_ID': 'nomad',
        'OPENSHIFT_BUILD_NAME': 'openshift',
        'RANCHER_URL': 'rancher',
    }
    
    def __init__(self, data_dir: Path):
        """Initialize authorship tracker.
        
        Args:
            data_dir: Directory for storing authorship data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.authorship_file = self.data_dir / 'authorship_data.json'
        self.authorship_data = self._load_authorship_data()
    
    def _load_authorship_data(self) -> Dict[str, Any]:
        """Load authorship data from disk.
        
        Returns:
            Authorship data dictionary
        """
        if self.authorship_file.exists():
            with open(self.authorship_file, 'r') as f:
                return json.load(f)
        return {
            'commits': [],
            'sessions': [],
            'statistics': {}
        }
    
    def _save_authorship_data(self):
        """Save authorship data to disk."""
        with open(self.authorship_file, 'w') as f:
            json.dump(self.authorship_data, f, indent=2)
    
    def detect_agent_from_commit_message(self, message: str) -> str:
        """Detect AI agent from commit message.
        
        Args:
            message: Git commit message
            
        Returns:
            Agent name or 'human' if no agent detected
        """
        message_lower = message.lower()
        
        for agent, patterns in self.AGENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return agent
        
        return "human"
    
    def detect_agent_from_environment(self) -> str:
        """Detect agent from environment variables.
        
        Returns:
            Agent name or 'unknown'
        """
        env_vars = os.environ
        
        # Check for API keys or agent-specific environment variables
        if 'ANTHROPIC_API_KEY' in env_vars:
            return 'claude'
        elif 'OPENAI_API_KEY' in env_vars:
            return 'chatgpt'
        elif 'GITHUB_COPILOT' in env_vars or 'COPILOT_ENABLED' in env_vars:
            return 'github_copilot'
        elif 'CURSOR_API_KEY' in env_vars:
            return 'cursor_ai'
        elif 'CODEIUM_API_KEY' in env_vars:
            return 'windsurf_ai'
        elif 'TABNINE_API_KEY' in env_vars:
            return 'tabnine'
        elif 'AWS_CODEWHISPERER' in env_vars:
            return 'amazon_q'
        elif 'GOOGLE_AI_API_KEY' in env_vars or 'GEMINI_API_KEY' in env_vars:
            return 'gemini'
        elif 'SOURCEGRAPH_TOKEN' in env_vars:
            return 'sourcegraph_cody'
        elif 'REPLIT_DB_URL' in env_vars:
            return 'replit_ai'
        elif 'PIECES_API_KEY' in env_vars:
            return 'pieces'
        elif 'BLACKBOX_API_KEY' in env_vars:
            return 'blackbox_ai'
        elif 'CODEGPT_API_KEY' in env_vars:
            return 'codegpt'
        elif 'DEEPSEEK_API_KEY' in env_vars:
            return 'deepseek'
        elif 'OLLAMA_HOST' in env_vars:
            return 'ollama'
        
        return 'unknown'
    
    def _get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes.
        
        Returns:
            List of process information
        """
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                processes.append({
                    'name': proc.info.get('name', ''),
                    'cmdline': proc.info.get('cmdline', [])
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # These exceptions are expected if a process terminates or access is denied; skip such processes.
            pass
        return processes
    
    def detect_agent_from_processes(self) -> str:
        """Detect agent from running processes.
        
        Returns:
            Agent name or 'unknown'
        """
        processes = self._get_running_processes()
        
        for proc in processes:
            name_lower = proc['name'].lower()
            cmdline_list = proc.get('cmdline', []) or []
            cmdline = ' '.join(str(x) for x in cmdline_list if x).lower()
            
            # Check for Cursor (includes AI)
            if 'cursor' in name_lower:
                return 'cursor_ai'
            
            # Check for Copilot in VS Code
            if ('code' in name_lower or 'vscode' in name_lower) and \
               ('copilot' in cmdline or 'github.copilot' in cmdline):
                return 'github_copilot'
            
            # Check for Windsurf
            if 'windsurf' in name_lower:
                return 'windsurf_ai'
        
        return 'unknown'
    
    def detect_ide(self) -> str:
        """Detect IDE from running processes.
        
        Returns:
            IDE name or 'unknown'
        """
        processes = self._get_running_processes()
        
        for proc in processes:
            name_lower = proc['name'].lower()
            
            for ide, patterns in self.IDE_PATTERNS.items():
                if any(pattern in name_lower for pattern in patterns):
                    return ide
        
        return 'unknown'
    
    def _get_git_config(self) -> Dict[str, str]:
        """Get git configuration.
        
        Returns:
            Git config dictionary
        """
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            config = {}
            with repo.config_reader() as reader:
                for section in reader.sections():
                    for option in reader.options(section):
                        key = f"{section}.{option}"
                        config[key] = reader.get_value(section, option)
            return config
        except Exception:
            return {}
    
    def detect_ide_from_git_config(self) -> str:
        """Detect IDE from git configuration.
        
        Returns:
            IDE name or 'unknown'
        """
        config = self._get_git_config()
        editor = config.get('core.editor', '').lower()
        
        for ide, patterns in self.IDE_PATTERNS.items():
            if any(pattern in editor for pattern in patterns):
                return ide
        
        return 'unknown'
    
    def detect_environment(self) -> str:
        """Detect development environment.
        
        Returns:
            Environment type
        """
        # Check for CI/CD environments
        for env_var, env_name in self.CI_ENVIRONMENTS.items():
            if env_var in os.environ:
                return env_name
        
        # Check for containerization
        if os.path.exists('/.dockerenv') or 'DOCKER_CONTAINER' in os.environ:
            return 'docker'
        
        if 'PODMAN_SYSTEMD_UNIT' in os.environ or 'container' in os.environ.get('container', ''):
            return 'podman'
        
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            return 'kubernetes'
        
        # Check for LXC/LXD
        if os.path.exists('/run/lxc') or os.path.exists('/run/lxd'):
            return 'lxc'
        
        # Check for SSH
        if 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ:
            return 'ssh'
        
        # Check for cloud environments
        if 'AWS_EXECUTION_ENV' in os.environ or 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            return 'aws_lambda'
        
        if 'GOOGLE_CLOUD_PROJECT' in os.environ or 'GCP_PROJECT' in os.environ:
            return 'google_cloud'
        
        if 'AZURE_HTTP_USER_AGENT' in os.environ or 'AZURE_FUNCTIONS_ENVIRONMENT' in os.environ:
            return 'azure'
        
        # Check for remote development
        if 'REMOTE_CONTAINERS' in os.environ:
            return 'vscode_remote_containers'
        
        if 'CODESPACES' in os.environ:
            return 'github_codespaces'
        
        # Default to local
        return 'local'
    
    def detect_tools(self, project_path: Path) -> List[str]:
        """Detect tools used in the project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            List of detected tools
        """
        tools = []
        project_dir = Path(project_path)
        
        # Version control
        if (project_dir / '.git').exists():
            tools.append('git')
        
        # Python tools
        if (project_dir / 'pytest.ini').exists() or \
           ((project_dir / 'setup.cfg').exists() and 'pytest' in (project_dir / 'setup.cfg').read_text()):
            tools.append('pytest')
        
        if (project_dir / 'requirements.txt').exists():
            tools.append('pip')
        
        if (project_dir / 'Pipfile').exists():
            tools.append('pipenv')
        
        if (project_dir / 'pyproject.toml').exists():
            try:
                content = (project_dir / 'pyproject.toml').read_text()
                if 'poetry' in content:
                    tools.append('poetry')
                if 'ruff' in content:
                    tools.append('ruff')
                if 'black' in content:
                    tools.append('black')
                if 'mypy' in content:
                    tools.append('mypy')
            except (OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read
        
        # JavaScript/Node tools
        if (project_dir / 'package.json').exists():
            tools.append('npm')
            try:
                content = (project_dir / 'package.json').read_text()
                if 'jest' in content:
                    tools.append('jest')
                if 'vitest' in content:
                    tools.append('vitest')
                if 'playwright' in content:
                    tools.append('playwright')
                if 'cypress' in content:
                    tools.append('cypress')
                if 'mocha' in content:
                    tools.append('mocha')
                if 'webpack' in content:
                    tools.append('webpack')
                if 'vite' in content:
                    tools.append('vite')
                if 'next' in content:
                    tools.append('nextjs')
                if 'turbo' in content:
                    tools.append('turborepo')
                if '@nx/' in content:
                    tools.append('nx')
            except (OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read
        
        if (project_dir / 'yarn.lock').exists():
            tools.append('yarn')
        
        if (project_dir / 'pnpm-lock.yaml').exists():
            tools.append('pnpm')
        
        if (project_dir / 'bun.lockb').exists():
            tools.append('bun')
        
        if (project_dir / 'deno.json').exists() or (project_dir / 'deno.jsonc').exists():
            tools.append('deno')
        
        # Java/JVM tools
        if (project_dir / 'pom.xml').exists():
            tools.append('maven')
        
        if (project_dir / 'build.gradle').exists() or (project_dir / 'build.gradle.kts').exists():
            tools.append('gradle')
        
        # Rust
        if (project_dir / 'Cargo.toml').exists():
            tools.append('cargo')
        
        # Go
        if (project_dir / 'go.mod').exists():
            tools.append('go')
        
        # PHP
        if (project_dir / 'composer.json').exists():
            tools.append('composer')
        
        # Ruby
        if (project_dir / 'Gemfile').exists():
            tools.append('bundler')
        
        if (project_dir / 'Rakefile').exists():
            tools.append('rake')
        
        # Elixir
        if (project_dir / 'mix.exs').exists():
            tools.append('mix')
        
        # Haskell
        if (project_dir / 'stack.yaml').exists():
            tools.append('stack')
        
        # Clojure
        if (project_dir / 'project.clj').exists():
            tools.append('leiningen')
        
        # Containerization
        if (project_dir / 'Dockerfile').exists():
            tools.append('docker')
        
        if (project_dir / 'docker-compose.yml').exists() or \
           (project_dir / 'docker-compose.yaml').exists():
            tools.append('docker-compose')
        
        if (project_dir / 'Containerfile').exists():
            tools.append('podman')
        
        # Kubernetes
        k8s_dirs = [project_dir / 'k8s', project_dir / 'kubernetes', project_dir / '.k8s']
        if any(d.exists() for d in k8s_dirs) or \
           (project_dir / 'deployment.yaml').exists() or \
           (project_dir / 'kustomization.yaml').exists():
            tools.append('kubernetes')
        
        if list(project_dir.glob('**/Chart.yaml')):
            tools.append('helm')
        
        # Build tools
        if (project_dir / 'Makefile').exists():
            tools.append('make')
        
        if (project_dir / 'BUILD').exists() or (project_dir / 'WORKSPACE').exists():
            tools.append('bazel')
        
        if (project_dir / 'CMakeLists.txt').exists():
            tools.append('cmake')
        
        # Testing frameworks (additional)
        if (project_dir / 'phpunit.xml').exists():
            tools.append('phpunit')
        
        if (project_dir / '.rspec').exists():
            tools.append('rspec')
        
        if list(project_dir.glob('**/cucumber.yml')):
            tools.append('cucumber')
        
        return list(set(tools))  # Remove duplicates
    
    def detect_skills(self, project_path: Path) -> List[str]:
        """Detect programming languages/skills used.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            List of detected skills/languages
        """
        skills = []
        project_dir = Path(project_path)
        
        # Map file extensions to languages - Comprehensive 2025 coverage
        extension_map = {
            # Popular languages
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.kt': 'kotlin',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.sh': 'bash',
            '.sql': 'sql',
            '.r': 'r',
            # Modern/Emerging languages
            '.zig': 'zig',
            '.v': 'v',
            '.nim': 'nim',
            '.cr': 'crystal',
            '.ex': 'elixir',
            '.exs': 'elixir',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.fs': 'fsharp',
            '.fsx': 'fsharp',
            '.scala': 'scala',
            '.sc': 'scala',
            '.clj': 'clojure',
            '.cljs': 'clojure',
            '.erl': 'erlang',
            '.lua': 'lua',
            '.dart': 'dart',
            '.jl': 'julia',
            '.sol': 'solidity',
            '.move': 'move',
            '.cairo': 'cairo',
            # Web technologies
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.vue': 'vue',
            '.svelte': 'svelte',
            # Data & Config
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            # Assembly & Low-level
            '.asm': 'assembly',
            '.s': 'assembly',
        }
        
        # Scan for files
        excluded_dirs = {'node_modules', 'venv', '.venv', 'vendor', '.git', 'dist', 'build'}
        for ext, lang in extension_map.items():
            files = [f for f in project_dir.glob(f'**/*{ext}') 
                     if not any(excluded in f.parts for excluded in excluded_dirs)]
            if files:
                skills.append(lang)
        
        # Check for specific frameworks and technologies
        if (project_dir / 'package.json').exists():
            try:
                with open(project_dir / 'package.json', encoding='utf-8') as f:
                    pkg = json.load(f)
                    deps = {}
                    if isinstance(pkg.get('dependencies'), dict):
                        deps.update(pkg.get('dependencies', {}))
                    if isinstance(pkg.get('devDependencies'), dict):
                        deps.update(pkg.get('devDependencies', {}))
                    
                    # Check for frameworks in dependencies
                    if 'react' in deps:
                        skills.append('react')
                    if 'vue' in deps:
                        skills.append('vue')
                    if 'angular' in deps or '@angular/core' in deps:
                        skills.append('angular')
                    if 'svelte' in deps:
                        skills.append('svelte')
                    if 'next' in deps:
                        skills.append('nextjs')
                    if 'nuxt' in deps:
                        skills.append('nuxtjs')
                    if 'express' in deps:
                        skills.append('expressjs')
                    if 'fastify' in deps:
                        skills.append('fastify')
                    if 'nest' in deps or '@nestjs/core' in deps:
                        skills.append('nestjs')
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read or parsed
        
        if (project_dir / 'requirements.txt').exists():
            try:
                with open(project_dir / 'requirements.txt', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # Extract package name from line (handle ==, >=, <=, etc.)
                        pkg_name = re.split(r'[<=>!]', line)[0].strip().lower()
                        if pkg_name == 'django':
                            skills.append('django')
                        elif pkg_name == 'flask':
                            skills.append('flask')
                        elif pkg_name == 'fastapi':
                            skills.append('fastapi')
                        elif pkg_name == 'tornado':
                            skills.append('tornado')
                        elif pkg_name == 'numpy':
                            skills.append('numpy')
                        elif pkg_name == 'pandas':
                            skills.append('pandas')
                        elif pkg_name in ('tensorflow', 'torch', 'pytorch'):
                            skills.append('machine-learning')
            except (OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read
        
        if (project_dir / 'Cargo.toml').exists():
            try:
                content = (project_dir / 'Cargo.toml').read_text()
                if 'tokio' in content:
                    skills.append('tokio')
                if 'actix' in content:
                    skills.append('actix')
            except (OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read
        
        if (project_dir / 'go.mod').exists():
            try:
                content = (project_dir / 'go.mod').read_text()
                if 'gin' in content:
                    skills.append('gin')
                if 'echo' in content:
                    skills.append('echo')
                if 'fiber' in content:
                    skills.append('fiber')
            except (OSError, UnicodeDecodeError):
                pass  # Skip if file cannot be read
        
        return list(set(skills))  # Remove duplicates
    
    def detect_orchestration(self, project_path: Path) -> str:
        """Detect CI/CD orchestration system.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Orchestration system name
        """
        project_dir = Path(project_path)
        
        # GitHub Actions
        if (project_dir / '.github' / 'workflows').exists():
            return 'github_actions'
        
        # GitLab CI
        if (project_dir / '.gitlab-ci.yml').exists():
            return 'gitlab_ci'
        
        # Jenkins
        if (project_dir / 'Jenkinsfile').exists():
            return 'jenkins'
        
        # CircleCI
        if (project_dir / '.circleci' / 'config.yml').exists():
            return 'circleci'
        
        # Travis CI
        if (project_dir / '.travis.yml').exists():
            return 'travis_ci'
        
        # Azure Pipelines
        if (project_dir / 'azure-pipelines.yml').exists():
            return 'azure_pipelines'
        
        # Buildkite
        if (project_dir / '.buildkite').exists() or (project_dir / 'buildkite.yml').exists():
            return 'buildkite'
        
        # Drone CI
        if (project_dir / '.drone.yml').exists():
            return 'drone_ci'
        
        # Semaphore CI
        if (project_dir / '.semaphore').exists():
            return 'semaphore_ci'
        
        # Bitbucket Pipelines
        if (project_dir / 'bitbucket-pipelines.yml').exists():
            return 'bitbucket_pipelines'
        
        # TeamCity
        if (project_dir / '.teamcity').exists():
            return 'teamcity'
        
        # Bamboo
        if (project_dir / 'bamboo.yml').exists():
            return 'bamboo'
        
        # GoCD
        if (project_dir / '.gocd').exists():
            return 'gocd'
        
        # Concourse CI
        if (project_dir / 'concourse.yml').exists() or (project_dir / 'pipeline.yml').exists():
            return 'concourse_ci'
        
        # Argo Workflows
        if list(project_dir.glob('**/*workflow.yaml')) or list(project_dir.glob('**/*workflow.yml')):
            return 'argo_workflows'
        
        # Tekton
        if list(project_dir.glob('**/tekton/**/*.yaml')):
            return 'tekton'
        
        return 'none'
    
    def track_commit(self, commit_data: Dict[str, Any], project_path: Path) -> AuthorshipMetadata:
        """Track authorship for a commit.
        
        Args:
            commit_data: Commit information
            project_path: Path to project
            
        Returns:
            AuthorshipMetadata instance
        """
        # Detect all components
        agent = self.detect_agent_from_commit_message(commit_data.get('message', ''))
        
        # If not found in commit message, check environment
        if agent == 'human':
            env_agent = self.detect_agent_from_environment()
            if env_agent != 'unknown':
                agent = env_agent
        
        # Check processes
        if agent == 'human':
            proc_agent = self.detect_agent_from_processes()
            if proc_agent != 'unknown':
                agent = proc_agent
        
        ide = self.detect_ide()
        if ide == 'unknown':
            ide = self.detect_ide_from_git_config()
        
        environment = self.detect_environment()
        tools = self.detect_tools(project_path)
        skills = self.detect_skills(project_path)
        orchestration = self.detect_orchestration(project_path)
        
        # Calculate confidence based on number of detected components
        confidence = 0.0
        if agent != 'unknown' and agent != 'human':
            confidence += 0.4
        if ide != 'unknown':
            confidence += 0.2
        if environment != 'unknown':
            confidence += 0.1
        if tools:
            confidence += 0.15
        if skills:
            confidence += 0.15
        
        metadata = AuthorshipMetadata(
            agent=agent,
            ide=ide,
            environment=environment,
            tools=tools,
            skills=skills,
            orchestration=orchestration,
            timestamp=commit_data.get('timestamp', datetime.now().isoformat()),
            confidence=min(1.0, confidence)
        )
        
        return metadata
    
    def store_metadata(self, commit_sha: str, metadata: AuthorshipMetadata):
        """Store authorship metadata for a commit.
        
        Args:
            commit_sha: Git commit SHA
            metadata: Authorship metadata
        """
        commit_entry = {
            'sha': commit_sha,
            **metadata.to_dict()
        }
        
        self.authorship_data['commits'].append(commit_entry)
        self._save_authorship_data()
    
    def query_by_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Query commits by agent.
        
        Args:
            agent: Agent name to filter by
            
        Returns:
            List of matching commits
        """
        return [
            commit for commit in self.authorship_data['commits']
            if commit.get('agent') == agent
        ]
    
    def query_by_ide(self, ide: str) -> List[Dict[str, Any]]:
        """Query commits by IDE.
        
        Args:
            ide: IDE name to filter by
            
        Returns:
            List of matching commits
        """
        return [
            commit for commit in self.authorship_data['commits']
            if commit.get('ide') == ide
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get authorship statistics.
        
        Returns:
            Statistics dictionary
        """
        commits = self.authorship_data['commits']
        
        stats = {
            'total_commits': len(commits),
            'by_agent': {},
            'by_ide': {},
            'by_environment': {},
            'top_tools': {},
            'top_skills': {},
        }
        
        # Count by agent
        for commit in commits:
            agent = commit.get('agent', 'unknown')
            stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
        
        # Count by IDE
        for commit in commits:
            ide = commit.get('ide', 'unknown')
            stats['by_ide'][ide] = stats['by_ide'].get(ide, 0) + 1
        
        # Count by environment
        for commit in commits:
            env = commit.get('environment', 'unknown')
            stats['by_environment'][env] = stats['by_environment'].get(env, 0) + 1
        
        # Count tools
        for commit in commits:
            for tool in commit.get('tools', []):
                stats['top_tools'][tool] = stats['top_tools'].get(tool, 0) + 1
        
        # Count skills
        for commit in commits:
            for skill in commit.get('skills', []):
                stats['top_skills'][skill] = stats['top_skills'].get(skill, 0) + 1
        
        return stats
    
    def track_git_commit(self, repo_path: Path, commit_sha: str) -> AuthorshipMetadata:
        """Track authorship for a git commit.
        
        Args:
            repo_path: Path to git repository
            commit_sha: Commit SHA to track
            
        Returns:
            AuthorshipMetadata instance
        """
        import git
        
        repo = git.Repo(repo_path)
        commit = repo.commit(commit_sha)
        
        commit_data = {
            'sha': commit_sha,
            'message': commit.message,
            'author': str(commit.author),
            'timestamp': commit.committed_datetime.isoformat()
        }
        
        metadata = self.track_commit(commit_data, repo_path)
        self.store_metadata(commit_sha, metadata)
        
        return metadata
    
    def embed_in_git_notes(self, repo_path: Path, commit_sha: str, 
                           metadata: AuthorshipMetadata) -> bool:
        """Embed authorship metadata in git notes.
        
        Args:
            repo_path: Path to git repository
            commit_sha: Commit SHA
            metadata: Authorship metadata
            
        Returns:
            True if successful
        """
        try:
            import git
            
            repo = git.Repo(repo_path)
            
            # Create notes reference if it doesn't exist
            notes_ref = 'refs/notes/authorship'
            
            # Format metadata as JSON
            notes_content = json.dumps(metadata.to_dict(), indent=2)
            
            # Add git note
            repo.git.notes('--ref', notes_ref, 'add', '-f', '-m', notes_content, commit_sha)
            
            return True
        except Exception as e:
            logger.error(f"Error embedding git notes: {e}")
            return False
    
    def read_from_git_notes(self, repo_path: Path, commit_sha: str) -> Optional[Dict[str, Any]]:
        """Read authorship metadata from git notes.
        
        Args:
            repo_path: Path to git repository
            commit_sha: Commit SHA
            
        Returns:
            Metadata dictionary or None
        """
        try:
            import git
            
            repo = git.Repo(repo_path)
            notes_ref = 'refs/notes/authorship'
            
            # Read git note
            notes_content = repo.git.notes('--ref', notes_ref, 'show', commit_sha)
            
            return json.loads(notes_content)
        except Exception:
            return None
