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
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import psutil


@dataclass
class AuthorshipMetadata:
    """Metadata about code authorship."""
    
    agent: str = "unknown"
    ide: str = "unknown"
    environment: str = "unknown"
    tools: List[str] = None
    skills: List[str] = None
    orchestration: str = "unknown"
    timestamp: str = None
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
    
    # Agent detection patterns
    AGENT_PATTERNS = {
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
    }
    
    # IDE detection patterns
    IDE_PATTERNS = {
        'vscode': ['code', 'vscode', 'visual studio code'],
        'cursor': ['cursor'],
        'windsurf': ['windsurf'],
        'pycharm': ['pycharm'],
        'intellij': ['idea', 'intellij'],
        'vim': ['vim', 'nvim', 'neovim'],
        'emacs': ['emacs'],
        'sublime': ['sublime', 'sublime_text'],
        'atom': ['atom'],
        'zed': ['zed'],
        'nova': ['nova'],
        'fleet': ['fleet'],
        'xcode': ['xcode'],
    }
    
    # Environment detection
    CI_ENVIRONMENTS = {
        'GITHUB_ACTIONS': 'github_actions',
        'GITLAB_CI': 'gitlab_ci',
        'CIRCLECI': 'circleci',
        'TRAVIS': 'travis_ci',
        'JENKINS_URL': 'jenkins',
        'CODEBUILD_BUILD_ID': 'aws_codebuild',
        'AZURE_PIPELINES': 'azure_pipelines',
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
            cmdline = ' '.join(proc['cmdline']).lower()
            
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
        
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            return 'kubernetes'
        
        # Check for SSH
        if 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ:
            return 'ssh'
        
        # Check for cloud environments
        if 'AWS_EXECUTION_ENV' in os.environ:
            return 'aws_lambda'
        
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            return 'google_cloud'
        
        if 'AZURE_HTTP_USER_AGENT' in os.environ:
            return 'azure'
        
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
           (project_dir / 'setup.cfg').exists() and 'pytest' in (project_dir / 'setup.cfg').read_text():
            tools.append('pytest')
        
        if (project_dir / 'requirements.txt').exists():
            tools.append('pip')
        
        if (project_dir / 'Pipfile').exists():
            tools.append('pipenv')
        
        if (project_dir / 'pyproject.toml').exists():
            content = (project_dir / 'pyproject.toml').read_text()
            if 'poetry' in content:
                tools.append('poetry')
        
        # JavaScript/Node tools
        if (project_dir / 'package.json').exists():
            tools.append('npm')
            content = (project_dir / 'package.json').read_text()
            if 'jest' in content:
                tools.append('jest')
            if 'webpack' in content:
                tools.append('webpack')
            if 'vite' in content:
                tools.append('vite')
        
        if (project_dir / 'yarn.lock').exists():
            tools.append('yarn')
        
        # Containerization
        if (project_dir / 'Dockerfile').exists():
            tools.append('docker')
        
        if (project_dir / 'docker-compose.yml').exists() or \
           (project_dir / 'docker-compose.yaml').exists():
            tools.append('docker-compose')
        
        # Kubernetes
        if (project_dir / 'k8s').exists() or \
           list(project_dir.glob('**/deployment.yaml')):
            tools.append('kubernetes')
        
        # Make
        if (project_dir / 'Makefile').exists():
            tools.append('make')
        
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
        
        # Map file extensions to languages
        extension_map = {
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
            '.cs': 'csharp',
            '.swift': 'swift',
            '.sh': 'bash',
            '.sql': 'sql',
            '.r': 'r',
        }
        
        # Scan for files
        for ext, lang in extension_map.items():
            if list(project_dir.glob(f'**/*{ext}')):
                skills.append(lang)
        
        # Check for specific frameworks
        if (project_dir / 'package.json').exists():
            content = (project_dir / 'package.json').read_text()
            if 'react' in content:
                skills.append('react')
            if 'vue' in content:
                skills.append('vue')
            if 'angular' in content:
                skills.append('angular')
        
        if (project_dir / 'requirements.txt').exists():
            content = (project_dir / 'requirements.txt').read_text()
            if 'django' in content:
                skills.append('django')
            if 'flask' in content:
                skills.append('flask')
        
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
            print(f"Error embedding git notes: {e}")
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
