"""Git maintenance and hygiene management."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import git
from git import Repo, InvalidGitRepositoryError


class GitMaintainer:
    """Manages git hygiene including auto-commits, stacked diffs, and auto-push."""
    
    def __init__(self, data_dir: Path):
        """Initialize git maintainer.
        
        Args:
            data_dir: Directory to store maintenance data
        """
        self.data_dir = data_dir
        self.maintenance_file = data_dir / 'git_maintenance.json'
        self.maintenance_data = self._load_maintenance_data()
    
    def _load_maintenance_data(self) -> Dict[str, Any]:
        """Load maintenance data from file.
        
        Returns:
            Maintenance data dictionary
        """
        if self.maintenance_file.exists():
            with open(self.maintenance_file, 'r') as f:
                return json.load(f)
        return {
            'auto_commit_enabled': {},
            'auto_push_enabled': {},
            'last_maintenance': {},
        }
    
    def _save_maintenance_data(self):
        """Save maintenance data to file."""
        with open(self.maintenance_file, 'w') as f:
            json.dump(self.maintenance_data, f, indent=2)
    
    def is_auto_commit_enabled(self, project_path: str) -> bool:
        """Check if auto-commit is enabled for project.
        
        Args:
            project_path: Path to project
            
        Returns:
            True if auto-commit is enabled
        """
        return self.maintenance_data['auto_commit_enabled'].get(project_path, True)
    
    def is_auto_push_enabled(self, project_path: str) -> bool:
        """Check if auto-push is enabled for project.
        
        Args:
            project_path: Path to project
            
        Returns:
            True if auto-push is enabled
        """
        return self.maintenance_data['auto_push_enabled'].get(project_path, True)
    
    def set_auto_commit(self, project_path: str, enabled: bool):
        """Enable or disable auto-commit for project.
        
        Args:
            project_path: Path to project
            enabled: Whether to enable auto-commit
        """
        self.maintenance_data['auto_commit_enabled'][project_path] = enabled
        self._save_maintenance_data()
    
    def set_auto_push(self, project_path: str, enabled: bool):
        """Enable or disable auto-push for project.
        
        Args:
            project_path: Path to project
            enabled: Whether to enable auto-push
        """
        self.maintenance_data['auto_push_enabled'][project_path] = enabled
        self._save_maintenance_data()
    
    def analyze_uncommitted_changes(self, repo: Repo) -> Tuple[List[str], List[str], int]:
        """Analyze uncommitted changes in repository.
        
        Args:
            repo: Git repository object
            
        Returns:
            Tuple of (modified files, untracked files, total changes)
        """
        modified = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files
        total_changes = len(modified) + len(untracked)
        
        return modified, untracked, total_changes
    
    def generate_commit_message(self, modified: List[str], untracked: List[str]) -> str:
        """Generate intelligent commit message based on changes.
        
        Args:
            modified: List of modified files
            untracked: List of untracked files
            
        Returns:
            Generated commit message
        """
        # Categorize changes
        categories = {
            'code': [],
            'docs': [],
            'config': [],
            'tests': [],
            'other': []
        }
        
        all_files = modified + untracked
        
        for file in all_files:
            file_lower = file.lower()
            if any(ext in file_lower for ext in ['.py', '.js', '.java', '.go', '.rs', '.cpp', '.c']):
                categories['code'].append(file)
            elif any(ext in file_lower for ext in ['.md', '.rst', '.txt', 'readme']):
                categories['docs'].append(file)
            elif any(ext in file_lower for ext in ['config', '.yml', '.yaml', '.json', '.toml', '.ini']):
                categories['config'].append(file)
            elif 'test' in file_lower or 'spec' in file_lower:
                categories['tests'].append(file)
            else:
                categories['other'].append(file)
        
        # Build commit message
        parts = []
        
        if categories['code']:
            parts.append(f"Update code ({len(categories['code'])} files)")
        if categories['docs']:
            parts.append(f"Update documentation ({len(categories['docs'])} files)")
        if categories['config']:
            parts.append(f"Update configuration ({len(categories['config'])} files)")
        if categories['tests']:
            parts.append(f"Update tests ({len(categories['tests'])} files)")
        if categories['other']:
            parts.append(f"Update other files ({len(categories['other'])} files)")
        
        if not parts:
            return "Auto-commit: General updates"
        
        if len(parts) == 1:
            return f"Auto-commit: {parts[0]}"
        else:
            return f"Auto-commit: {', '.join(parts)}"
    
    def create_stacked_commits(self, repo: Repo, modified: List[str], 
                               untracked: List[str], max_files_per_commit: int = 10) -> List[str]:
        """Create stacked commits if changes are too large.
        
        Args:
            repo: Git repository object
            modified: List of modified files
            untracked: List of untracked files
            max_files_per_commit: Maximum files per commit
            
        Returns:
            List of commit SHAs created
        """
        all_files = modified + untracked
        commits = []
        
        # Group files by category for better organization
        categories = {}
        for file in all_files:
            file_lower = file.lower()
            if any(ext in file_lower for ext in ['.py', '.js', '.java', '.go', '.rs']):
                category = 'code'
            elif any(ext in file_lower for ext in ['.md', '.rst', '.txt']):
                category = 'docs'
            elif 'test' in file_lower:
                category = 'tests'
            elif any(ext in file_lower for ext in ['.yml', '.yaml', '.json', '.toml']):
                category = 'config'
            else:
                category = 'other'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(file)
        
        # Create commits for each category
        for category, files in categories.items():
            # Split into chunks if needed
            for i in range(0, len(files), max_files_per_commit):
                chunk = files[i:i + max_files_per_commit]
                
                # Stage files
                repo.index.add(chunk)
                
                # Generate message
                if len(files) <= max_files_per_commit:
                    message = f"Auto-commit: Update {category} ({len(chunk)} files)"
                else:
                    message = f"Auto-commit: Update {category} (part {i//max_files_per_commit + 1}, {len(chunk)} files)"
                
                # Commit
                commit = repo.index.commit(message)
                commits.append(commit.hexsha[:8])
        
        return commits
    
    def perform_maintenance(self, project_path: str) -> Dict[str, Any]:
        """Perform git maintenance on a project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Maintenance result dictionary
        """
        result = {
            'project_path': project_path,
            'timestamp': datetime.now().isoformat(),
            'actions': [],
            'success': True,
            'error': None,
        }
        
        try:
            repo = Repo(project_path)
            
            # Check if auto-commit is enabled
            if not self.is_auto_commit_enabled(project_path):
                result['actions'].append('Auto-commit disabled, skipping')
                return result
            
            # Analyze changes
            modified, untracked, total_changes = self.analyze_uncommitted_changes(repo)
            
            if total_changes == 0:
                result['actions'].append('No uncommitted changes')
                return result
            
            # Create commits
            if total_changes > 10:
                # Use stacked commits for large changes
                commits = self.create_stacked_commits(repo, modified, untracked)
                result['actions'].append(f'Created {len(commits)} stacked commits: {", ".join(commits)}')
            else:
                # Single commit for small changes
                repo.index.add(modified + untracked)
                message = self.generate_commit_message(modified, untracked)
                commit = repo.index.commit(message)
                result['actions'].append(f'Created commit {commit.hexsha[:8]}: {message}')
            
            # Auto-push if enabled
            if self.is_auto_push_enabled(project_path):
                if self._is_private_repo(repo):
                    # Only auto-push for private repos by default
                    try:
                        origin = repo.remote('origin')
                        origin.push()
                        result['actions'].append('Pushed changes to remote')
                    except Exception as e:
                        result['actions'].append(f'Push failed: {str(e)}')
                        result['success'] = False
                else:
                    result['actions'].append('Skipped push (public repo, requires manual approval)')
            else:
                result['actions'].append('Auto-push disabled')
            
            # Update last maintenance time
            self.maintenance_data['last_maintenance'][project_path] = datetime.now().isoformat()
            self._save_maintenance_data()
            
        except InvalidGitRepositoryError:
            result['success'] = False
            result['error'] = 'Not a git repository'
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _is_private_repo(self, repo: Repo) -> bool:
        """Check if repository is private.
        
        Args:
            repo: Git repository object
            
        Returns:
            True if repository appears to be private
        """
        try:
            if repo.remotes:
                remote_url = repo.remotes.origin.url
                # Simple heuristic: check if URL contains common private repo indicators
                # In a real implementation, this would query the GitHub API
                return 'github.com' in remote_url or 'gitlab.com' in remote_url
        except:
            pass
        return False
