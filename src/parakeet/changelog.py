"""Changelog and time tracking for projects."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import git


class ChangelogManager:
    """Manages changelogs and time tracking for projects."""
    
    def __init__(self, data_dir: Path):
        """Initialize changelog manager.
        
        Args:
            data_dir: Directory to store changelog data
        """
        self.data_dir = data_dir
        self.changelog_file = data_dir / 'changelogs.json'
        self.time_tracking_file = data_dir / 'time_tracking.json'
        self.changelogs = self._load_changelogs()
        self.time_tracking = self._load_time_tracking()
    
    def _load_changelogs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load changelogs from file.
        
        Returns:
            Changelogs dictionary keyed by project path
        """
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_time_tracking(self) -> Dict[str, Dict[str, Any]]:
        """Load time tracking data from file.
        
        Returns:
            Time tracking dictionary keyed by project path
        """
        if self.time_tracking_file.exists():
            with open(self.time_tracking_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_changelogs(self):
        """Save changelogs to file."""
        with open(self.changelog_file, 'w') as f:
            json.dump(self.changelogs, f, indent=2)
    
    def _save_time_tracking(self):
        """Save time tracking data to file."""
        with open(self.time_tracking_file, 'w') as f:
            json.dump(self.time_tracking, f, indent=2)
    
    def add_changelog_entry(self, project_path: str, entry: Dict[str, Any]):
        """Add a changelog entry for a project.
        
        Args:
            project_path: Path to project
            entry: Changelog entry dictionary
        """
        if project_path not in self.changelogs:
            self.changelogs[project_path] = []
        
        self.changelogs[project_path].append(entry)
        self._save_changelogs()
    
    def track_work_session(self, project_path: str, duration_minutes: int, 
                          description: str, milestone: Optional[str] = None):
        """Track a work session on a project.
        
        Args:
            project_path: Path to project
            duration_minutes: Duration of work session in minutes
            description: Description of work done
            milestone: Optional milestone name
        """
        if project_path not in self.time_tracking:
            self.time_tracking[project_path] = {
                'total_minutes': 0,
                'sessions': [],
                'milestones': {},
            }
        
        session = {
            'timestamp': datetime.now().isoformat(),
            'duration_minutes': duration_minutes,
            'description': description,
            'milestone': milestone,
        }
        
        self.time_tracking[project_path]['sessions'].append(session)
        self.time_tracking[project_path]['total_minutes'] += duration_minutes
        
        # Track milestone time
        if milestone:
            if milestone not in self.time_tracking[project_path]['milestones']:
                self.time_tracking[project_path]['milestones'][milestone] = {
                    'total_minutes': 0,
                    'start_time': datetime.now().isoformat(),
                    'sessions': 0,
                }
            
            self.time_tracking[project_path]['milestones'][milestone]['total_minutes'] += duration_minutes
            self.time_tracking[project_path]['milestones'][milestone]['sessions'] += 1
        
        self._save_time_tracking()
    
    def estimate_work_duration(self, project_path: str, 
                              start_time: datetime, end_time: datetime) -> int:
        """Estimate actual work duration based on commits.
        
        Args:
            project_path: Path to project
            start_time: Start of period
            end_time: End of period
            
        Returns:
            Estimated work duration in minutes
        """
        try:
            repo = git.Repo(project_path)
            commits = list(repo.iter_commits(
                after=start_time.isoformat(),
                before=end_time.isoformat()
            ))
            
            if not commits:
                return 0
            
            # Estimate based on commit frequency
            # Assume active work session between commits < 2 hours apart
            total_minutes = 0
            last_commit_time = None
            
            for commit in sorted(commits, key=lambda c: c.committed_date):
                commit_time = datetime.fromtimestamp(commit.committed_date)
                
                if last_commit_time:
                    gap = (commit_time - last_commit_time).total_seconds() / 60
                    if gap < 120:  # Less than 2 hours
                        total_minutes += gap
                    else:
                        # Add 30 minutes for the work that led to the commit
                        total_minutes += 30
                else:
                    # First commit, assume 30 minutes of work
                    total_minutes += 30
                
                last_commit_time = commit_time
            
            return int(total_minutes)
        
        except Exception:
            return 0
    
    def generate_changelog_markdown(self, project_path: str) -> str:
        """Generate changelog in markdown format.
        
        Args:
            project_path: Path to project
            
        Returns:
            Markdown formatted changelog
        """
        project_name = Path(project_path).name
        entries = self.changelogs.get(project_path, [])
        
        md = f"# Changelog for {project_name}\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if not entries:
            md += "_No changelog entries yet._\n"
            return md
        
        # Group by date
        by_date = {}
        for entry in entries:
            date = entry['timestamp'][:10]
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(entry)
        
        # Write entries by date
        for date in sorted(by_date.keys(), reverse=True):
            md += f"## {date}\n\n"
            for entry in by_date[date]:
                time = entry['timestamp'][11:16]
                md += f"- **{time}** - {entry['description']}"
                if entry.get('duration_estimate'):
                    md += f" _(~{entry['duration_estimate']} min)_"
                md += "\n"
            md += "\n"
        
        return md
    
    def generate_time_report(self, project_path: str) -> str:
        """Generate time tracking report.
        
        Args:
            project_path: Path to project
            
        Returns:
            Markdown formatted time report
        """
        project_name = Path(project_path).name
        tracking = self.time_tracking.get(project_path, {})
        
        md = f"# Time Report for {project_name}\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if not tracking:
            md += "_No time tracking data yet._\n"
            return md
        
        # Overall stats
        total_minutes = tracking.get('total_minutes', 0)
        total_hours = total_minutes / 60
        sessions = tracking.get('sessions', [])
        
        md += "## Overall Statistics\n\n"
        md += f"- **Total Time**: {total_hours:.1f} hours ({total_minutes} minutes)\n"
        md += f"- **Total Sessions**: {len(sessions)}\n"
        md += f"- **Average Session**: {total_minutes / len(sessions):.0f} minutes\n" if sessions else ""
        md += "\n"
        
        # Milestones
        milestones = tracking.get('milestones', {})
        if milestones:
            md += "## Milestones\n\n"
            for milestone, data in sorted(milestones.items()):
                hours = data['total_minutes'] / 60
                md += f"### {milestone}\n\n"
                md += f"- **Time Spent**: {hours:.1f} hours ({data['total_minutes']} minutes)\n"
                md += f"- **Sessions**: {data['sessions']}\n"
                md += f"- **Started**: {data['start_time'][:10]}\n"
                md += "\n"
        
        # Recent sessions
        if sessions:
            md += "## Recent Sessions (Last 10)\n\n"
            for session in sorted(sessions, key=lambda s: s['timestamp'], reverse=True)[:10]:
                timestamp = session['timestamp'][:16].replace('T', ' ')
                md += f"- **{timestamp}** - {session['duration_minutes']} min"
                if session.get('milestone'):
                    md += f" [{session['milestone']}]"
                md += f": {session['description']}\n"
            md += "\n"
        
        return md
    
    def generate_agent_instructions(self, project_path: str, 
                                   project_type: str = 'unknown') -> str:
        """Generate instructions for project agents.
        
        Args:
            project_path: Path to project
            project_type: Type of project (python, javascript, etc.)
            
        Returns:
            Markdown formatted instructions
        """
        project_name = Path(project_path).name
        
        md = f"# Agent Instructions for {project_name}\n\n"
        md += f"Project Type: {project_type}\n\n"
        
        md += "## Time Tracking\n\n"
        md += "When working on this project, please track your time:\n\n"
        md += "```python\n"
        md += "from parakeet.changelog import ChangelogManager\n"
        md += "from pathlib import Path\n\n"
        md += "manager = ChangelogManager(Path.home() / '.parakeet')\n"
        md += f"manager.track_work_session(\n"
        md += f"    '{project_path}',\n"
        md += "    duration_minutes=30,\n"
        md += "    description='Description of work',\n"
        md += "    milestone='Optional milestone name'\n"
        md += ")\n"
        md += "```\n\n"
        
        md += "## Changelog Updates\n\n"
        md += "Add changelog entries for significant changes:\n\n"
        md += "```python\n"
        md += "manager.add_changelog_entry(\n"
        md += f"    '{project_path}',\n"
        md += "    {\n"
        md += "        'timestamp': datetime.now().isoformat(),\n"
        md += "        'description': 'What was changed',\n"
        md += "        'duration_estimate': 45  # minutes\n"
        md += "    }\n"
        md += ")\n"
        md += "```\n\n"
        
        md += "## Best Practices\n\n"
        md += "- Make small, focused commits with descriptive messages\n"
        md += "- Track time for each work session\n"
        md += "- Document milestones and their completion times\n"
        md += "- Keep the changelog up to date\n"
        md += "- Let Parakeet auto-commit when you're done for the day\n\n"
        
        return md
    
    def write_project_docs(self, project_path: str, project_type: str = 'unknown'):
        """Write documentation files to project.
        
        Args:
            project_path: Path to project
            project_type: Type of project
        """
        project_dir = Path(project_path)
        docs_dir = project_dir / '.parakeet'
        docs_dir.mkdir(exist_ok=True)
        
        # Write changelog
        changelog_md = self.generate_changelog_markdown(project_path)
        (docs_dir / 'CHANGELOG.md').write_text(changelog_md)
        
        # Write time report
        time_report_md = self.generate_time_report(project_path)
        (docs_dir / 'TIME_REPORT.md').write_text(time_report_md)
        
        # Write agent instructions
        agent_instructions = self.generate_agent_instructions(project_path, project_type)
        (docs_dir / 'AGENT_INSTRUCTIONS.md').write_text(agent_instructions)
