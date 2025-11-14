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
    
    def __init__(self, watch_paths: List[str], exclude_patterns: List[str],
                 max_depth: int = 3, recursive: bool = True):
        """Initialize project scanner.

        Args:
            watch_paths: List of paths to scan for projects
            exclude_patterns: Patterns to exclude from scanning
            max_depth: Maximum depth for recursive scanning (0 = immediate subdirs only)
            recursive: Whether to scan recursively or just immediate subdirectories
        """
        self.watch_paths = watch_paths
        self.exclude_patterns = exclude_patterns
        self.max_depth = max_depth
        self.recursive = recursive
    
    def scan_projects(self) -> List[Dict[str, Any]]:
        """Scan all watch paths and identify projects.

        Returns:
            List of project information dictionaries
        """
        projects = []
        seen_paths = set()  # Avoid duplicates from symlinks

        for watch_path in self.watch_paths:
            path = Path(watch_path)
            if not path.exists():
                continue

            # Scan directories (recursive or immediate subdirs)
            if self.recursive:
                self._scan_recursive(path, projects, seen_paths, depth=0)
            else:
                self._scan_immediate(path, projects, seen_paths)

        return projects

    def _scan_immediate(self, path: Path, projects: List[Dict[str, Any]],
                       seen_paths: set) -> None:
        """Scan immediate subdirectories only.

        Args:
            path: Path to scan
            projects: List to append found projects to
            seen_paths: Set of already-scanned paths to avoid duplicates
        """
        try:
            for item in path.iterdir():
                try:
                    if item.is_dir() and not self._should_exclude(item.name):
                        real_path = str(item.resolve())
                        if real_path not in seen_paths:
                            seen_paths.add(real_path)
                            project_info = self._analyze_directory(item)
                            if project_info:
                                projects.append(project_info)
                except (PermissionError, OSError):
                    # Skip directories we can't access
                    continue
        except (PermissionError, OSError):
            # Skip paths we can't read
            pass

    def _scan_recursive(self, path: Path, projects: List[Dict[str, Any]],
                       seen_paths: set, depth: int = 0) -> None:
        """Recursively scan directories up to max_depth.

        Args:
            path: Path to scan
            projects: List to append found projects to
            seen_paths: Set of already-scanned paths to avoid duplicates
            depth: Current recursion depth
        """
        # Check depth limit
        if depth > self.max_depth:
            return

        try:
            for item in path.iterdir():
                try:
                    if not item.is_dir() or self._should_exclude(item.name):
                        continue

                    # Avoid infinite loops from symlinks
                    real_path = str(item.resolve())
                    if real_path in seen_paths:
                        continue
                    seen_paths.add(real_path)

                    # Check if this directory is a project
                    project_info = self._analyze_directory(item)
                    if project_info:
                        projects.append(project_info)
                        # Don't recurse into identified projects
                        continue

                    # Recurse into non-project directories
                    self._scan_recursive(item, projects, seen_paths, depth + 1)

                except (PermissionError, OSError):
                    # Skip directories we can't access
                    continue
        except (PermissionError, OSError):
            # Skip paths we can't read
            pass
    
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
        try:
            # Check for project indicators
            is_project = False
            project_type = 'unknown'
            
            for indicator in self.PROJECT_INDICATORS:
                try:
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
                except (PermissionError, OSError):
                    continue
            
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
        except (PermissionError, OSError):
            return None
    
    
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

            # Initialize default values for safety
            last_commit_info = None
            branch = None
            is_dirty = False

            # Check if repository has any commits
            try:
                # This will raise ValueError if there are no commits
                last_commit = repo.head.commit
                last_commit_info = {
                    'sha': last_commit.hexsha[:8],
                    'message': last_commit.message.strip(),
                    'author': str(last_commit.author),
                    'date': datetime.fromtimestamp(last_commit.committed_date).isoformat(),
                }
            except (ValueError, TypeError):
                # Repository has no commits yet (empty repo)
                last_commit_info = None

            # Get current branch (handle empty repo and detached HEAD)
            try:
                if repo.head.is_detached:
                    branch = 'detached'
                else:
                    branch = repo.active_branch.name
            except (TypeError, ValueError):
                # Empty repository or other issue accessing branch
                # Try to get the symbolic reference
                try:
                    # For empty repos, HEAD might point to refs/heads/main or refs/heads/master
                    with open(path / '.git' / 'HEAD', 'r') as f:
                        head_content = f.read().strip()
                        if head_content.startswith('ref: refs/heads/'):
                            branch = head_content.replace('ref: refs/heads/', '')
                        else:
                            branch = 'unknown'
                except (IOError, OSError):
                    branch = 'unknown'

            # Check for uncommitted changes (safe for empty repos)
            try:
                is_dirty = repo.is_dirty()
            except Exception:
                # If we can't determine dirty state, assume clean
                is_dirty = False

            return {
                'branch': branch,
                'last_commit': last_commit_info,
                'is_dirty': is_dirty,
                'remote_url': self._get_remote_url(repo),
            }
        except (git.InvalidGitRepositoryError, git.GitCommandError) as e:
            # Not a git repository or corrupted repository
            return None
        except Exception as e:
            # Catch any other unexpected exceptions and return None
            # This ensures the scanner doesn't crash on unexpected git states
            import logging
            logging.debug(f"Error getting git info for {path}: {e}")
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
