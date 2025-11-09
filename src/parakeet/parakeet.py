"""Main orchestrator for Friendly Parakeet."""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .config import Config
from .scanner import ProjectScanner
from .tracker import ProjectTracker
from .breadcrumbs import BreadcrumbGenerator


class Parakeet:
    """Main orchestrator for project tracking and monitoring."""
    
    def __init__(self, config_path: str = None):
        """Initialize Parakeet.
        
        Args:
            config_path: Optional path to config file
        """
        self.config = Config(config_path)
        self.scanner = ProjectScanner(
            self.config.watch_paths,
            self.config.get('exclude_patterns', [])
        )
        self.tracker = ProjectTracker(self.config.data_dir)
        self.breadcrumbs = BreadcrumbGenerator(self.config.data_dir)
    
    def scan_and_update(self) -> List[Dict[str, Any]]:
        """Scan projects and update tracking data.
        
        Returns:
            List of updated projects
        """
        print("🦜 Friendly Parakeet is scanning your projects...")
        
        # Scan for projects
        projects = self.scanner.scan_projects()
        print(f"Found {len(projects)} project(s)")
        
        # Update tracking for each project
        for project in projects:
            self.tracker.update_project(project)
            
            # Check if breadcrumb needed
            inactivity_days = self.tracker.get_inactivity_days(project['path'])
            threshold = self.config.get('breadcrumb_threshold', 7)
            
            if inactivity_days >= threshold:
                # Generate breadcrumb
                breadcrumb = self.breadcrumbs.generate_breadcrumb(
                    project, inactivity_days
                )
                if breadcrumb:
                    self.breadcrumbs.add_breadcrumb(project['path'], breadcrumb)
                    print(f"  📍 Created breadcrumb for {project['name']} "
                          f"(inactive for {inactivity_days} days)")
        
        return projects
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display.
        
        Returns:
            Dashboard data dictionary
        """
        # Get project summaries
        summaries = self.tracker.get_all_projects_summary()
        
        # Sort by last activity
        summaries.sort(key=lambda x: x['last_activity'], reverse=True)
        
        # Get all breadcrumbs
        all_breadcrumbs = self.breadcrumbs.get_all_breadcrumbs()
        
        # Compile activity log
        activity_log = []
        for summary in summaries:
            activity_log.append({
                'timestamp': summary['last_activity'],
                'project': summary['name'],
                'type': 'activity',
                'details': f"Active in {summary['name']}"
            })
        
        # Add breadcrumb events
        for project_path, crumbs in all_breadcrumbs.items():
            for crumb in crumbs:
                activity_log.append({
                    'timestamp': crumb['timestamp'],
                    'project': crumb['project_name'],
                    'type': 'breadcrumb',
                    'details': f"Breadcrumb created (inactive {crumb['inactivity_days']} days)"
                })
        
        # Sort activity log by time
        activity_log.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'projects': summaries,
            'breadcrumbs': all_breadcrumbs,
            'activity_log': activity_log[:50],  # Last 50 activities
            'stats': {
                'total_projects': len(summaries),
                'active_projects': sum(1 for s in summaries if s['inactivity_days'] < 7),
                'total_breadcrumbs': sum(len(crumbs) for crumbs in all_breadcrumbs.values()),
            }
        }
    
    def get_project_details(self, project_path: str) -> Dict[str, Any]:
        """Get detailed information about a specific project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Detailed project information
        """
        velocity = self.tracker.get_velocity(project_path)
        breadcrumbs = self.breadcrumbs.get_breadcrumbs(project_path)
        inactivity_days = self.tracker.get_inactivity_days(project_path)
        
        return {
            'path': project_path,
            'name': Path(project_path).name,
            'velocity': velocity,
            'breadcrumbs': breadcrumbs,
            'inactivity_days': inactivity_days,
        }
