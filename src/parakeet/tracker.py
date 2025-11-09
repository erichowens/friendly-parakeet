"""Project tracking and velocity calculation."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class ProjectTracker:
    """Tracks project progress and calculates velocity metrics."""
    
    def __init__(self, data_dir: Path):
        """Initialize project tracker.
        
        Args:
            data_dir: Directory to store tracking data
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / 'project_history.json'
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load project history from file.
        
        Returns:
            History dictionary keyed by project path
        """
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_history(self):
        """Save project history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def update_project(self, project: Dict[str, Any]):
        """Update tracking data for a project.
        
        Args:
            project: Project information dictionary
        """
        project_path = project['path']
        
        # Initialize project history if needed
        if project_path not in self.history:
            self.history[project_path] = []
        
        # Create snapshot
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'stats': project.get('stats', {}),
            'git': project.get('git', {}),
        }
        
        self.history[project_path].append(snapshot)
        self._save_history()
    
    def get_velocity(self, project_path: str, window_days: int = 30) -> Dict[str, Any]:
        """Calculate project velocity over a time window.
        
        Args:
            project_path: Path to project
            window_days: Number of days to calculate velocity over
            
        Returns:
            Velocity metrics dictionary
        """
        if project_path not in self.history or len(self.history[project_path]) < 2:
            return {
                'commits_per_day': 0,
                'active_days': 0,
                'trend': 'unknown',
            }
        
        cutoff = datetime.now() - timedelta(days=window_days)
        recent_snapshots = [
            s for s in self.history[project_path]
            if datetime.fromisoformat(s['timestamp']) > cutoff
        ]
        
        if len(recent_snapshots) < 2:
            return {
                'commits_per_day': 0,
                'active_days': 0,
                'trend': 'stale',
            }
        
        # Calculate active days (days with changes)
        active_dates = set()
        for snapshot in recent_snapshots:
            date = datetime.fromisoformat(snapshot['timestamp']).date()
            active_dates.add(date)
        
        active_days = len(active_dates)
        
        # Estimate commits (based on git info changes)
        # This is simplified - in real usage we'd track actual commits
        commits_per_day = active_days / window_days if window_days > 0 else 0
        
        # Determine trend
        mid_point = len(recent_snapshots) // 2
        first_half_activity = mid_point
        second_half_activity = len(recent_snapshots) - mid_point
        
        if second_half_activity > first_half_activity * 1.2:
            trend = 'increasing'
        elif second_half_activity < first_half_activity * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'commits_per_day': round(commits_per_day, 2),
            'active_days': active_days,
            'trend': trend,
        }
    
    def get_inactivity_days(self, project_path: str) -> int:
        """Get number of days since last activity.
        
        Args:
            project_path: Path to project
            
        Returns:
            Days since last activity
        """
        if project_path not in self.history or not self.history[project_path]:
            return 0
        
        last_snapshot = self.history[project_path][-1]
        last_time = datetime.fromisoformat(last_snapshot['timestamp'])
        return (datetime.now() - last_time).days
    
    def get_all_projects_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all tracked projects.
        
        Returns:
            List of project summaries
        """
        summaries = []
        
        for project_path in self.history:
            if not self.history[project_path]:
                continue
            
            last_snapshot = self.history[project_path][-1]
            velocity = self.get_velocity(project_path)
            inactivity = self.get_inactivity_days(project_path)
            
            summaries.append({
                'path': project_path,
                'name': Path(project_path).name,
                'last_activity': last_snapshot['timestamp'],
                'inactivity_days': inactivity,
                'velocity': velocity,
                'stats': last_snapshot.get('stats', {}),
            })
        
        return summaries
