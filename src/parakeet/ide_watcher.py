"""IDE activity monitoring and real-time coding insights."""

import json
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
import subprocess
import re


class IDEWatcher:
    """Monitors IDE activity and provides real-time coding insights."""

    def __init__(self, parakeet):
        """Initialize IDE watcher.

        Args:
            parakeet: Main Parakeet instance
        """
        self.parakeet = parakeet
        self.data_dir = parakeet.config.data_dir
        self.ide_data_file = self.data_dir / 'ide_activity.json'
        self.ide_data = self._load_ide_data()

        # Tracking state
        self.active_files = {}  # file_path -> last_activity_time
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'files_edited': set(),
            'total_keystrokes': 0,
            'active_time': 0,
            'stuck_moments': [],
            'flow_states': []
        }

        # IDE process patterns (including modern AI IDEs)
        self.ide_processes = {
            'vscode': ['Code', 'code', 'code-insiders', 'codium'],
            'cursor': ['Cursor', 'cursor', 'Cursor.app'],  # AI-powered IDE
            'windsurf': ['Windsurf', 'windsurf', 'WindSurf'],  # AI IDE
            'claude_code': ['claude', 'Claude', 'claude.ai'],  # Claude in browser/app
            'xcode': ['Xcode', 'xcode'],  # Apple IDE
            'warp': ['Warp', 'warp', 'WarpTerminal'],  # Modern terminal
            'iterm': ['iTerm', 'iTerm2', 'iterm'],  # Popular Mac terminal
            'terminal': ['Terminal', 'terminal.app'],  # Mac Terminal
            'alacritty': ['Alacritty', 'alacritty'],  # GPU-accelerated terminal
            'kitty': ['kitty', 'Kitty'],  # Modern terminal
            'intellij': ['idea', 'IntelliJ', 'idea64'],
            'sublime': ['sublime_text', 'Sublime Text'],
            'vim': ['vim', 'nvim', 'neovim'],
            'emacs': ['emacs', 'Emacs'],
            'pycharm': ['pycharm', 'PyCharm'],
            'webstorm': ['webstorm', 'WebStorm'],
            'atom': ['atom', 'Atom'],
            'zed': ['Zed', 'zed'],  # Collaborative IDE
            'nova': ['Nova', 'nova'],  # Mac native IDE
            'fleet': ['Fleet', 'fleet'],  # JetBrains lightweight IDE
        }

        # Terminal-based development patterns
        self.terminal_patterns = {
            'ssh_session': ['ssh', 'mosh'],
            'tmux_session': ['tmux'],
            'screen_session': ['screen'],
            'docker_exec': ['docker exec'],
            'kubectl_exec': ['kubectl exec'],
        }

        # Detection thresholds
        self.stuck_threshold = 300  # 5 minutes of no activity
        self.flow_threshold = 600   # 10 minutes of continuous activity
        self.context_switch_threshold = 30  # 30 seconds between file switches

        # Real-time monitoring
        self.monitoring = False
        self.monitor_thread = None

    def _load_ide_data(self) -> Dict[str, Any]:
        """Load saved IDE activity data.

        Returns:
            IDE activity history
        """
        if self.ide_data_file.exists():
            with open(self.ide_data_file, 'r') as f:
                return json.load(f)
        return {
            'sessions': [],
            'patterns': {},
            'insights': []
        }

    def _save_ide_data(self):
        """Save IDE activity data."""
        with open(self.ide_data_file, 'w') as f:
            json.dump(self.ide_data, f, indent=2)

    def start_monitoring(self):
        """Start monitoring IDE activity."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            return True
        return False

    def stop_monitoring(self):
        """Stop monitoring IDE activity."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

        # Save current session
        self._save_session()

    def _monitor_loop(self):
        """Main monitoring loop."""
        last_check = datetime.now()

        while self.monitoring:
            try:
                current_time = datetime.now()

                # Check active IDEs
                active_ides = self.detect_active_ides()

                if active_ides:
                    # Get active file from IDE (platform-specific)
                    active_file = self.get_active_file()

                    if active_file:
                        self._track_file_activity(active_file, current_time)

                    # Detect patterns
                    self._detect_coding_patterns(current_time)

                    # Check for stuck moments
                    self._check_stuck_detection(current_time)

                    # Check for flow state
                    self._check_flow_state(current_time)

                # Sleep for a short interval
                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"Error in IDE monitoring: {e}")
                time.sleep(10)

    def detect_active_ides(self) -> List[Dict[str, Any]]:
        """Detect currently running IDE processes.

        Returns:
            List of active IDE information
        """
        active_ides = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                process_name = proc.info['name']

                for ide_type, patterns in self.ide_processes.items():
                    if any(pattern.lower() in process_name.lower() for pattern in patterns):
                        active_ides.append({
                            'type': ide_type,
                            'name': process_name,
                            'pid': proc.info['pid'],
                            'cpu': proc.info.get('cpu_percent', 0),
                            'memory': proc.info.get('memory_info', {}).rss / 1024 / 1024  # MB
                        })
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return active_ides

    def get_active_file(self) -> Optional[str]:
        """Get the currently active file in the IDE.

        Returns:
            Path to active file or None
        """
        # Try VS Code/Cursor/Windsurf first (they use similar storage)
        vscode_file = self._get_vscode_active_file()
        if vscode_file:
            return vscode_file

        # Try terminal-based detection
        terminal_file = self._get_terminal_active_file()
        if terminal_file:
            return terminal_file

        # Try XCode detection
        xcode_file = self._get_xcode_active_file()
        if xcode_file:
            return xcode_file

        # Try other methods
        # This could be extended with IDE-specific APIs
        return self._get_active_file_from_recent_changes()

    def _get_vscode_active_file(self) -> Optional[str]:
        """Get active file from VS Code/Cursor/Windsurf using workspace state.

        Returns:
            Active file path or None
        """
        # Check for VS Code and similar editors' workspace files
        workspace_dirs = [
            # VS Code
            Path.home() / '.vscode' / 'workspaceStorage',
            Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'workspaceStorage',
            # Cursor
            Path.home() / '.cursor' / 'workspaceStorage',
            Path.home() / 'Library' / 'Application Support' / 'Cursor' / 'User' / 'workspaceStorage',
            # Windsurf
            Path.home() / '.windsurf' / 'workspaceStorage',
            Path.home() / 'Library' / 'Application Support' / 'Windsurf' / 'User' / 'workspaceStorage',
        ]

        for workspace_dir in workspace_dirs:
            if workspace_dir.exists():
                # Look for recent state files
                try:
                    state_files = list(workspace_dir.glob('*/state.vscdb'))
                    if state_files:
                        # Sort by modification time
                        latest = max(state_files, key=lambda f: f.stat().st_mtime)

                        # Parse state (simplified - actual implementation would need SQLite)
                        # For now, use recent file changes as proxy
                        return self._get_active_file_from_recent_changes()
                except Exception:
                    pass

        return None

    def _get_terminal_active_file(self) -> Optional[str]:
        """Detect active file from terminal sessions (vim, nvim, etc.).

        Returns:
            Active file path or None
        """
        # Check for vim/nvim swap files
        swap_locations = [
            Path.home() / '.vim' / 'swap',
            Path.home() / '.local' / 'share' / 'nvim' / 'swap',
            Path('/tmp'),
            Path('/var/tmp'),
        ]

        recent_swap = None
        recent_time = 0

        for swap_dir in swap_locations:
            if swap_dir.exists():
                try:
                    # Look for swap files (.swp, .swo, .swn)
                    for swap_file in swap_dir.glob('*.sw[ponm]'):
                        mtime = swap_file.stat().st_mtime
                        if mtime > recent_time and (datetime.now().timestamp() - mtime) < 300:
                            recent_time = mtime
                            recent_swap = swap_file
                except Exception:
                    pass

        if recent_swap:
            # Try to extract filename from swap file name
            # Vim swap files often contain the original filename
            try:
                # Read the swap file header (first 1024 bytes)
                with open(recent_swap, 'rb') as f:
                    header = f.read(1024)
                    # Look for path-like patterns in the header
                    import re
                    paths = re.findall(b'/[^\x00]+', header)
                    if paths:
                        # Return the most likely file path
                        for path in paths:
                            decoded_path = path.decode('utf-8', errors='ignore')
                            if Path(decoded_path).exists():
                                return decoded_path
            except Exception:
                pass

        # Check terminal process command lines for editor invocations
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                name = proc.info.get('name', '').lower()
                cmdline = proc.info.get('cmdline', [])

                # Check for editors in terminal
                if any(editor in name for editor in ['vim', 'nvim', 'nano', 'emacs']):
                    # Look for file paths in command line
                    for arg in cmdline[1:]:  # Skip the command itself
                        if arg and not arg.startswith('-'):
                            if Path(arg).exists() and Path(arg).is_file():
                                return arg
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return None

    def _get_xcode_active_file(self) -> Optional[str]:
        """Get active file from XCode.

        Returns:
            Active file path or None
        """
        # Check XCode derived data and workspace state
        xcode_dirs = [
            Path.home() / 'Library' / 'Developer' / 'Xcode' / 'DerivedData',
            Path.home() / 'Library' / 'Developer' / 'Xcode' / 'UserData',
        ]

        for xcode_dir in xcode_dirs:
            if xcode_dir.exists():
                try:
                    # Look for recent workspace state files
                    workspace_files = list(xcode_dir.glob('*/UserInterfaceState.xcuserstate'))
                    if workspace_files:
                        # Get most recent
                        latest = max(workspace_files, key=lambda f: f.stat().st_mtime)

                        # Check if recently modified (within last minute)
                        if (datetime.now().timestamp() - latest.stat().st_mtime) < 60:
                            # Try to find corresponding project
                            project_dir = latest.parent.parent

                            # Look for recently modified source files
                            for pattern in ['**/*.swift', '**/*.m', '**/*.mm', '**/*.h']:
                                for source_file in project_dir.glob(pattern):
                                    if (datetime.now().timestamp() - source_file.stat().st_mtime) < 60:
                                        return str(source_file)
                except Exception:
                    pass

        return None

    def _get_active_file_from_recent_changes(self) -> Optional[str]:
        """Get most recently modified file in watched projects.

        Returns:
            Path to most recently modified file or None
        """
        recent_files = []

        for watch_path in self.parakeet.config.watch_paths:
            watch_dir = Path(watch_path).expanduser()
            if watch_dir.exists():
                # Look for recently modified code files
                for pattern in ['**/*.py', '**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx',
                               '**/*.java', '**/*.go', '**/*.rb', '**/*.rs']:
                    for file_path in watch_dir.glob(pattern):
                        # Skip node_modules, venv, etc.
                        if any(exclude in str(file_path) for exclude in
                               ['node_modules', 'venv', '__pycache__', '.git']):
                            continue

                        try:
                            mtime = file_path.stat().st_mtime
                            if datetime.now().timestamp() - mtime < 60:  # Modified in last minute
                                recent_files.append((file_path, mtime))
                        except Exception:
                            pass

        if recent_files:
            recent_files.sort(key=lambda x: x[1], reverse=True)
            return str(recent_files[0][0])

        return None

    def _track_file_activity(self, file_path: str, current_time: datetime):
        """Track activity on a file.

        Args:
            file_path: Path to the file
            current_time: Current timestamp
        """
        # Update active files
        self.active_files[file_path] = current_time

        # Add to session
        if isinstance(self.current_session['files_edited'], set):
            self.current_session['files_edited'].add(file_path)

        # Update active time
        if hasattr(self, '_last_activity_time'):
            time_diff = (current_time - self._last_activity_time).total_seconds()
            if time_diff < 30:  # Active if less than 30 seconds between activities
                self.current_session['active_time'] += time_diff

        self._last_activity_time = current_time

    def _detect_coding_patterns(self, current_time: datetime):
        """Detect coding patterns from activity.

        Args:
            current_time: Current timestamp
        """
        # Detect rapid file switching (might indicate searching for something)
        recent_switches = []
        for file_path, last_time in self.active_files.items():
            if (current_time - last_time).total_seconds() < 60:
                recent_switches.append(file_path)

        if len(recent_switches) > 5:
            self._add_insight({
                'type': 'rapid_switching',
                'timestamp': current_time.isoformat(),
                'files': recent_switches,
                'suggestion': "You're switching between many files. Try using global search or creating a workspace bookmark."
            })

        # Detect long sessions
        session_duration = (current_time - datetime.fromisoformat(
            self.current_session['start_time'])).total_seconds() / 3600

        if session_duration > 4 and not getattr(self, '_long_session_warned', False):
            self._long_session_warned = True
            self._add_insight({
                'type': 'long_session',
                'timestamp': current_time.isoformat(),
                'duration_hours': session_duration,
                'suggestion': "You've been coding for over 4 hours. Consider taking a break to maintain productivity!"
            })

    def _check_stuck_detection(self, current_time: datetime):
        """Check if the developer might be stuck.

        Args:
            current_time: Current timestamp
        """
        if hasattr(self, '_last_activity_time'):
            inactive_time = (current_time - self._last_activity_time).total_seconds()

            if inactive_time > self.stuck_threshold and not getattr(self, '_stuck_detected', False):
                self._stuck_detected = True

                # Determine context
                active_file = self.get_active_file()

                stuck_moment = {
                    'timestamp': current_time.isoformat(),
                    'file': active_file,
                    'duration': inactive_time,
                    'context': self._get_file_context(active_file) if active_file else None
                }

                self.current_session['stuck_moments'].append(stuck_moment)

                # Generate help suggestion
                self._generate_stuck_help(stuck_moment)

            elif inactive_time < 30:
                self._stuck_detected = False

    def _check_flow_state(self, current_time: datetime):
        """Check if developer is in flow state.

        Args:
            current_time: Current timestamp
        """
        if hasattr(self, '_flow_start_time'):
            flow_duration = (current_time - self._flow_start_time).total_seconds()

            if flow_duration > self.flow_threshold and not getattr(self, '_flow_detected', False):
                self._flow_detected = True

                flow_state = {
                    'timestamp': self._flow_start_time.isoformat(),
                    'duration': flow_duration,
                    'files': list(self.active_files.keys())[-10:],  # Last 10 files
                }

                self.current_session['flow_states'].append(flow_state)

                self._add_insight({
                    'type': 'flow_state',
                    'timestamp': current_time.isoformat(),
                    'duration_minutes': flow_duration / 60,
                    'message': "🌊 You're in the flow! Keep going!"
                })
        else:
            self._flow_start_time = current_time

    def _get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get context about a file.

        Args:
            file_path: Path to the file

        Returns:
            File context information
        """
        if not file_path:
            return {}

        path = Path(file_path)

        context = {
            'name': path.name,
            'extension': path.suffix,
            'directory': str(path.parent),
            'size': 0,
            'type': self._determine_file_type(path.suffix)
        }

        try:
            stat = path.stat()
            context['size'] = stat.st_size
            context['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception:
            pass

        return context

    def _determine_file_type(self, extension: str) -> str:
        """Determine file type from extension.

        Args:
            extension: File extension

        Returns:
            File type category
        """
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.html': 'web',
            '.css': 'style',
            '.scss': 'style',
            '.json': 'config',
            '.yaml': 'config',
            '.yml': 'config',
            '.md': 'documentation',
            '.txt': 'text'
        }

        return type_map.get(extension.lower(), 'other')

    def _generate_stuck_help(self, stuck_moment: Dict[str, Any]):
        """Generate help suggestion for stuck moment.

        Args:
            stuck_moment: Stuck moment data
        """
        file_context = stuck_moment.get('context', {})
        file_type = file_context.get('type', 'unknown')

        # Generate contextual suggestions based on file type
        suggestions = {
            'python': [
                "Try using a debugger (pdb) to step through the code",
                "Check the Python documentation or use help()",
                "Consider breaking the problem into smaller functions"
            ],
            'javascript': [
                "Use console.log() to debug the issue",
                "Check the browser DevTools for errors",
                "Try isolating the problem in a simpler test case"
            ],
            'typescript': [
                "Check for type errors in your IDE",
                "Use the TypeScript playground to test ideas",
                "Review the TypeScript documentation"
            ],
            'config': [
                "Validate your configuration syntax",
                "Check the documentation for correct format",
                "Look for example configurations"
            ],
            'other': [
                "Take a short break and come back fresh",
                "Try explaining the problem out loud (rubber duck debugging)",
                "Search for similar issues online or ask for help"
            ]
        }

        help_suggestions = suggestions.get(file_type, suggestions['other'])

        # Create insight
        self._add_insight({
            'type': 'stuck_detected',
            'timestamp': stuck_moment['timestamp'],
            'file': stuck_moment.get('file'),
            'suggestions': help_suggestions,
            'message': f"Looks like you might be stuck. Here are some suggestions:"
        })

    def _add_insight(self, insight: Dict[str, Any]):
        """Add an insight to the current session.

        Args:
            insight: Insight data
        """
        self.ide_data['insights'].append(insight)

        # Notify via parakeet if available
        if hasattr(self.parakeet, 'notify_ide_insight'):
            self.parakeet.notify_ide_insight(insight)

    def _save_session(self):
        """Save the current session data."""
        # Convert sets to lists for JSON serialization
        session_data = dict(self.current_session)
        if isinstance(session_data.get('files_edited'), set):
            session_data['files_edited'] = list(session_data['files_edited'])

        session_data['end_time'] = datetime.now().isoformat()

        self.ide_data['sessions'].append(session_data)
        self._save_ide_data()

    def get_coding_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get coding statistics for the past N days.

        Args:
            days: Number of days to analyze

        Returns:
            Coding statistics
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_sessions = [
            s for s in self.ide_data.get('sessions', [])
            if datetime.fromisoformat(s['start_time']) > cutoff
        ]

        stats = {
            'total_sessions': len(recent_sessions),
            'total_active_time': sum(s.get('active_time', 0) for s in recent_sessions),
            'total_files_edited': len(set().union(
                *[set(s.get('files_edited', [])) for s in recent_sessions]
            )),
            'stuck_moments': sum(len(s.get('stuck_moments', [])) for s in recent_sessions),
            'flow_states': sum(len(s.get('flow_states', [])) for s in recent_sessions),
            'average_session_length': 0,
            'most_edited_files': [],
            'productivity_score': 0
        }

        if recent_sessions:
            stats['average_session_length'] = stats['total_active_time'] / len(recent_sessions)

            # Find most edited files
            file_counts = defaultdict(int)
            for session in recent_sessions:
                for file_path in session.get('files_edited', []):
                    file_counts[file_path] += 1

            stats['most_edited_files'] = sorted(
                file_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]

            # Calculate productivity score
            flow_time = sum(
                f.get('duration', 0) for s in recent_sessions
                for f in s.get('flow_states', [])
            )
            stuck_time = sum(
                m.get('duration', 0) for s in recent_sessions
                for m in s.get('stuck_moments', [])
            )

            if stats['total_active_time'] > 0:
                stats['productivity_score'] = min(100, max(0,
                    int((flow_time - stuck_time) / stats['total_active_time'] * 100)
                ))

        return stats

    def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent IDE insights.

        Args:
            limit: Maximum number of insights to return

        Returns:
            List of recent insights
        """
        insights = self.ide_data.get('insights', [])
        return sorted(insights, key=lambda x: x['timestamp'], reverse=True)[:limit]