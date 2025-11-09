"""Breadcrumb generation and management."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import git


class BreadcrumbGenerator:
    """Generates context breadcrumbs for projects."""
    
    def __init__(self, data_dir: Path):
        """Initialize breadcrumb generator.
        
        Args:
            data_dir: Directory to store breadcrumbs
        """
        self.data_dir = data_dir
        self.breadcrumbs_file = data_dir / 'breadcrumbs.json'
        self.breadcrumbs = self._load_breadcrumbs()
    
    def _load_breadcrumbs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load breadcrumbs from file.
        
        Returns:
            Breadcrumbs dictionary keyed by project path
        """
        if self.breadcrumbs_file.exists():
            with open(self.breadcrumbs_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_breadcrumbs(self):
        """Save breadcrumbs to file."""
        with open(self.breadcrumbs_file, 'w') as f:
            json.dump(self.breadcrumbs, f, indent=2)
    
    def generate_breadcrumb(self, project: Dict[str, Any], 
                           inactivity_days: int) -> Optional[Dict[str, Any]]:
        """Generate breadcrumb for a project.
        
        Args:
            project: Project information
            inactivity_days: Days since last activity
            
        Returns:
            Breadcrumb dictionary or None if not needed
        """
        project_path = project['path']
        
        # Gather context from git
        git_context = self._get_git_context(Path(project_path))
        
        # Get recent file changes
        recent_files = self._get_recent_files(Path(project_path))
        
        # Generate AI-friendly prompt suggestions
        prompt_suggestions = self._generate_prompt_suggestions(
            project, git_context, recent_files
        )
        
        breadcrumb = {
            'timestamp': datetime.now().isoformat(),
            'inactivity_days': inactivity_days,
            'project_name': project['name'],
            'project_type': project.get('type', 'unknown'),
            'git_context': git_context,
            'recent_files': recent_files,
            'prompt_suggestions': prompt_suggestions,
            'status': 'active' if inactivity_days < 7 else 'slowing',
        }
        
        return breadcrumb
    
    def _get_git_context(self, project_path: Path) -> Dict[str, Any]:
        """Get git context from project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Git context dictionary
        """
        try:
            repo = git.Repo(project_path)
            
            # Get recent commits
            commits = []
            for commit in list(repo.iter_commits(max_count=10)):
                commits.append({
                    'sha': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                })
            
            # Get current branch
            branch = repo.active_branch.name if not repo.head.is_detached else 'detached'
            
            # Get uncommitted changes
            modified_files = [item.a_path for item in repo.index.diff(None)]
            untracked_files = repo.untracked_files
            
            return {
                'branch': branch,
                'recent_commits': commits,
                'modified_files': modified_files,
                'untracked_files': untracked_files,
            }
        except (git.InvalidGitRepositoryError, git.GitCommandError):
            return {}
    
    def _get_recent_files(self, project_path: Path, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently modified files.
        
        Args:
            project_path: Path to project
            limit: Maximum number of files to return
            
        Returns:
            List of file information
        """
        files = []
        
        try:
            for item in project_path.rglob('*'):
                if item.is_file():
                    # Skip common excludes
                    if any(ex in str(item) for ex in ['.git', 'node_modules', '__pycache__']):
                        continue
                    
                    try:
                        stat = item.stat()
                        files.append({
                            'path': str(item.relative_to(project_path)),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'size': stat.st_size,
                        })
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        
        # Sort by modification time and limit
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files[:limit]
    
    def _generate_prompt_suggestions(self, project: Dict[str, Any],
                                    git_context: Dict[str, Any],
                                    recent_files: List[Dict[str, Any]]) -> List[str]:
        """Generate helpful prompt suggestions for AI coding agents.
        
        Args:
            project: Project information
            git_context: Git context
            recent_files: Recently modified files
            
        Returns:
            List of prompt suggestions
        """
        suggestions = []
        
        # Basic project context
        suggestions.append(
            f"I'm working on a {project.get('type', 'coding')} project called "
            f"'{project['name']}'. Here's where I left off..."
        )
        
        # Git context
        if git_context and git_context.get('recent_commits'):
            last_commit = git_context['recent_commits'][0]
            suggestions.append(
                f"My last commit was: \"{last_commit['message']}\". "
                f"Help me continue from here."
            )
        
        # Modified files
        if git_context and git_context.get('modified_files'):
            files_list = ', '.join(git_context['modified_files'][:5])
            suggestions.append(
                f"I have uncommitted changes in: {files_list}. "
                f"Can you help me review and complete these changes?"
            )
        
        # Recent activity
        if recent_files:
            top_file = recent_files[0]['path']
            suggestions.append(
                f"I was recently working on {top_file}. "
                f"What would be the next logical step?"
            )
        
        # General continuation
        suggestions.append(
            "Summarize the current state of this project and suggest next steps."
        )
        
        return suggestions
    
    def add_breadcrumb(self, project_path: str, breadcrumb: Dict[str, Any]):
        """Add breadcrumb for a project.
        
        Args:
            project_path: Path to project
            breadcrumb: Breadcrumb data
        """
        if project_path not in self.breadcrumbs:
            self.breadcrumbs[project_path] = []
        
        self.breadcrumbs[project_path].append(breadcrumb)
        self._save_breadcrumbs()
    
    def get_breadcrumbs(self, project_path: str) -> List[Dict[str, Any]]:
        """Get breadcrumbs for a project.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of breadcrumbs
        """
        return self.breadcrumbs.get(project_path, [])
    
    def get_all_breadcrumbs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all breadcrumbs.
        
        Returns:
            All breadcrumbs dictionary
        """
        return self.breadcrumbs
