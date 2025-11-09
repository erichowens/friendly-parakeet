"""Project scanner and file system crawler."""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import git


class ProjectScanner:
    """Scans and identifies coding projects in watch paths."""
    
    PROJECT_INDICATORS = [
        # Python
        'setup.py', 'pyproject.toml', 'requirements.txt', 'Pipfile',
        # JavaScript/Node
        'package.json', 'yarn.lock', 'package-lock.json',
        # Ruby
        'Gemfile', 'Rakefile',
        # Go
        'go.mod', 'go.sum',
        # Java
        'pom.xml', 'build.gradle', 'build.gradle.kts',
        # Rust
        'Cargo.toml',
        # C/C++
        'Makefile', 'CMakeLists.txt',
        # .NET
        '*.csproj', '*.fsproj', '*.sln',
        # General
        '.git',
    ]
    
    def __init__(self, watch_paths: List[str], exclude_patterns: List[str]):
        """Initialize project scanner.
        
        Args:
            watch_paths: List of paths to scan for projects
            exclude_patterns: Patterns to exclude from scanning
        """
        self.watch_paths = watch_paths
        self.exclude_patterns = exclude_patterns
    
    def scan_projects(self) -> List[Dict[str, Any]]:
        """Scan all watch paths and identify projects.
        
        Returns:
            List of project information dictionaries
        """
        projects = []
        
        for watch_path in self.watch_paths:
            path = Path(watch_path)
            if not path.exists():
                continue
            
            # Scan subdirectories
            for item in path.iterdir():
                if item.is_dir() and not self._should_exclude(item.name):
                    project_info = self._analyze_directory(item)
                    if project_info:
                        projects.append(project_info)
        
        return projects
    
    def _should_exclude(self, name: str) -> bool:
        """Check if directory should be excluded.
        
        Args:
            name: Directory name
            
        Returns:
            True if should be excluded
        """
        return any(pattern in name for pattern in self.exclude_patterns)
    
    def _analyze_directory(self, path: Path) -> Optional[Dict[str, Any]]:
        """Analyze directory to determine if it's a project.
        
        Args:
            path: Directory path to analyze
            
        Returns:
            Project information dict or None if not a project
        """
        # Check for project indicators
        is_project = False
        project_type = 'unknown'
        
        for indicator in self.PROJECT_INDICATORS:
            if indicator.startswith('*'):
                # Glob pattern
                if list(path.glob(indicator)):
                    is_project = True
                    break
            else:
                if (path / indicator).exists():
                    is_project = True
                    project_type = self._detect_project_type(indicator)
                    break
        
        if not is_project:
            return None
        
        # Get git information if available
        git_info = self._get_git_info(path)
        
        # Get file statistics
        stats = self._get_directory_stats(path)
        
        return {
            'name': path.name,
            'path': str(path.absolute()),
            'type': project_type,
            'git': git_info,
            'stats': stats,
            'last_scanned': datetime.now().isoformat(),
        }
    
    def _detect_project_type(self, indicator: str) -> str:
        """Detect project type from indicator file.
        
        Args:
            indicator: Indicator filename
            
        Returns:
            Project type string
        """
        type_map = {
            'setup.py': 'python',
            'pyproject.toml': 'python',
            'requirements.txt': 'python',
            'package.json': 'javascript',
            'Gemfile': 'ruby',
            'go.mod': 'go',
            'pom.xml': 'java',
            'Cargo.toml': 'rust',
            'Makefile': 'c/c++',
            '*.csproj': 'dotnet',
        }
        return type_map.get(indicator, 'unknown')
    
    def _get_git_info(self, path: Path) -> Optional[Dict[str, Any]]:
        """Get git repository information.
        
        Args:
            path: Project path
            
        Returns:
            Git info dict or None if not a git repo
        """
        try:
            repo = git.Repo(path)
            
            # Get last commit info
            last_commit = repo.head.commit
            
            # Get current branch
            branch = repo.active_branch.name if not repo.head.is_detached else 'detached'
            
            # Get uncommitted changes
            is_dirty = repo.is_dirty()
            
            return {
                'branch': branch,
                'last_commit': {
                    'sha': last_commit.hexsha[:8],
                    'message': last_commit.message.strip(),
                    'author': str(last_commit.author),
                    'date': datetime.fromtimestamp(last_commit.committed_date).isoformat(),
                },
                'is_dirty': is_dirty,
                'remote_url': self._get_remote_url(repo),
            }
        except (git.InvalidGitRepositoryError, git.GitCommandError):
            return None
    
    def _get_remote_url(self, repo: git.Repo) -> Optional[str]:
        """Get remote URL from git repo.
        
        Args:
            repo: Git repository object
            
        Returns:
            Remote URL or None
        """
        try:
            if repo.remotes:
                return repo.remotes.origin.url
        except AttributeError:
            pass
        return None
    
    def _get_directory_stats(self, path: Path) -> Dict[str, Any]:
        """Get directory statistics.
        
        Args:
            path: Directory path
            
        Returns:
            Statistics dictionary
        """
        file_count = 0
        total_size = 0
        last_modified = None
        
        try:
            for item in path.rglob('*'):
                if item.is_file() and not any(ex in str(item) for ex in self.exclude_patterns):
                    file_count += 1
                    try:
                        stat = item.stat()
                        total_size += stat.st_size
                        mtime = datetime.fromtimestamp(stat.st_mtime)
                        if last_modified is None or mtime > last_modified:
                            last_modified = mtime
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        
        return {
            'file_count': file_count,
            'total_size': total_size,
            'last_modified': last_modified.isoformat() if last_modified else None,
        }
