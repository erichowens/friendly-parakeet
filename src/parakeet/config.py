"""Configuration management for Friendly Parakeet."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Configuration manager for Friendly Parakeet."""
    
    DEFAULT_CONFIG = {
        'watch_paths': ['~/coding'],
        'data_dir': '~/.parakeet',
        'scan_interval': 300,  # seconds
        'breadcrumb_threshold': 7,  # days of inactivity before creating breadcrumb
        'velocity_window': 30,  # days to calculate velocity
        'exclude_patterns': [
            'node_modules',
            '.git',
            '__pycache__',
            'venv',
            '.env',
            'dist',
            'build',
            '.pytest_cache',
            '.tox',
        ],
        'dashboard_port': 5000,
        'git_maintenance_enabled': True,  # Auto-commit and push features
        'generate_docs': True,  # Generate changelogs and time reports
        'auto_commit_max_files': 10,  # Max files before creating stacked commits
        'scan_max_depth': 3,  # Maximum depth for recursive scanning (0 = immediate subdirs only)
        'scan_recursive': True,  # Whether to scan recursively or just immediate subdirectories
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. Defaults to ~/.parakeet/config.yaml
        """
        if config_path is None:
            config_path = os.path.expanduser('~/.parakeet/config.yaml')
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
            # Merge with defaults
            config = {**self.DEFAULT_CONFIG, **user_config}
        else:
            config = self.DEFAULT_CONFIG.copy()
            # Create default config file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_config(config)
        
        return config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file.
        
        Args:
            config: Configuration dict to save. Uses current config if None.
        """
        if config is None:
            config = self.config
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save_config()
    
    @property
    def watch_paths(self) -> List[str]:
        """Get expanded watch paths."""
        return [os.path.expanduser(p) for p in self.config['watch_paths']]
    
    @property
    def data_dir(self) -> Path:
        """Get expanded data directory path."""
        return Path(os.path.expanduser(self.config['data_dir']))
