"""Shared pytest fixtures and configuration."""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
import git
from faker import Faker


# Initialize Faker for test data generation
fake = Faker()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.

    Yields:
        Path to temporary directory that is cleaned up after test.
    """
    temp_path = Path(tempfile.mkdtemp(prefix="parakeet_test_"))
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_home_dir(temp_dir: Path, monkeypatch) -> Path:
    """Mock the home directory for testing.

    Args:
        temp_dir: Temporary directory fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Path to mocked home directory
    """
    home_path = temp_dir / "home"
    home_path.mkdir(exist_ok=True)

    # Create .parakeet directory
    parakeet_dir = home_path / ".parakeet"
    parakeet_dir.mkdir(exist_ok=True)

    # Mock Path.home() and os.path.expanduser
    monkeypatch.setattr(Path, "home", lambda: home_path)
    monkeypatch.setenv("HOME", str(home_path))

    return home_path


@pytest.fixture
def empty_git_repo(temp_dir: Path) -> git.Repo:
    """Create an empty git repository (no commits).

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Empty git.Repo object
    """
    repo_path = temp_dir / "empty_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)
    return repo


@pytest.fixture
def git_repo_with_commits(temp_dir: Path) -> git.Repo:
    """Create a git repository with commit history.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        git.Repo object with commits
    """
    repo_path = temp_dir / "repo_with_commits"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    # Configure git user for commits
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Create some files and commits
    for i in range(3):
        file_path = repo_path / f"file_{i}.txt"
        file_path.write_text(f"Content {i}\n")
        repo.index.add([str(file_path)])
        repo.index.commit(f"Commit {i}")

    # Add a remote
    repo.create_remote("origin", "https://github.com/test/repo.git")

    return repo


@pytest.fixture
def detached_head_repo(git_repo_with_commits: git.Repo) -> git.Repo:
    """Create a git repository in detached HEAD state.

    Args:
        git_repo_with_commits: Repository with commits

    Returns:
        git.Repo in detached HEAD state
    """
    repo = git_repo_with_commits
    first_commit = list(repo.iter_commits())[-1]
    repo.head.reference = first_commit
    return repo


@pytest.fixture
def corrupted_git_repo(temp_dir: Path) -> Path:
    """Create a corrupted git repository.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to corrupted repository
    """
    repo_path = temp_dir / "corrupted_repo"
    repo_path.mkdir()

    # Create a .git directory but corrupt it
    git_dir = repo_path / ".git"
    git_dir.mkdir()

    # Create an invalid HEAD file
    head_file = git_dir / "HEAD"
    head_file.write_text("invalid content")

    return repo_path


@pytest.fixture
def sample_project_structure(temp_dir: Path) -> Dict[str, Path]:
    """Create a sample project structure with various project types.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Dictionary mapping project types to their paths
    """
    projects = {}

    # Python project
    python_proj = temp_dir / "python_project"
    python_proj.mkdir()
    (python_proj / "setup.py").write_text("# Setup file")
    (python_proj / "requirements.txt").write_text("pytest\nflask")
    (python_proj / "src").mkdir()
    (python_proj / "src" / "__init__.py").touch()
    projects["python"] = python_proj

    # JavaScript project
    js_proj = temp_dir / "js_project"
    js_proj.mkdir()
    (js_proj / "package.json").write_text('{"name": "test-project"}')
    (js_proj / "node_modules").mkdir()  # Should be excluded
    (js_proj / "src").mkdir()
    (js_proj / "src" / "index.js").write_text("console.log('hello');")
    projects["javascript"] = js_proj

    # Ruby project
    ruby_proj = temp_dir / "ruby_project"
    ruby_proj.mkdir()
    (ruby_proj / "Gemfile").write_text("source 'https://rubygems.org'")
    projects["ruby"] = ruby_proj

    # Go project
    go_proj = temp_dir / "go_project"
    go_proj.mkdir()
    (go_proj / "go.mod").write_text("module example.com/test")
    projects["go"] = go_proj

    # Non-project directory
    non_proj = temp_dir / "not_a_project"
    non_proj.mkdir()
    (non_proj / "random.txt").write_text("Just a file")
    projects["non_project"] = non_proj

    return projects


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock datetime class
    """
    mock_dt = Mock()
    mock_dt.now.return_value = datetime(2024, 1, 15, 10, 30, 0)
    mock_dt.fromtimestamp = datetime.fromtimestamp
    monkeypatch.setattr("parakeet.scanner.datetime", mock_dt)
    return mock_dt


@pytest.fixture
def config_data() -> Dict[str, Any]:
    """Sample configuration data.

    Returns:
        Dictionary with sample config
    """
    return {
        "watch_paths": ["/Users/test/projects"],
        "exclude_patterns": ["node_modules", "__pycache__", ".git"],
        "scan_interval": 3600,
        "breadcrumb_threshold": 7,
        "auto_commit": {
            "enabled": False,
            "max_files_per_commit": 10,
            "commit_message_template": "Auto-commit: {change_type} changes",
        },
        "auto_push": {
            "enabled": False,
            "branches": ["main", "develop"],
        },
        "dashboard": {
            "port": 5000,
            "host": "localhost",
            "debug": False,
        },
    }


@pytest.fixture
def mock_parakeet_data_dir(mock_home_dir: Path) -> Path:
    """Create mock Parakeet data directory with sample data.

    Args:
        mock_home_dir: Mocked home directory

    Returns:
        Path to .parakeet directory
    """
    data_dir = mock_home_dir / ".parakeet"

    # Create sample project history
    history_file = data_dir / "project_history.json"
    history_file.write_text("""
    {
        "/path/to/project1": [
            {
                "timestamp": "2024-01-10T10:00:00",
                "file_count": 50,
                "total_size": 100000,
                "last_commit": "abc123"
            }
        ]
    }
    """)

    # Create sample breadcrumbs
    breadcrumbs_file = data_dir / "breadcrumbs.json"
    breadcrumbs_file.write_text("""
    {
        "/path/to/project1": {
            "timestamp": "2024-01-08T15:00:00",
            "breadcrumb": "Continue implementing user authentication",
            "context": "Working on login flow"
        }
    }
    """)

    # Create config
    config_file = data_dir / "config.yaml"
    config_file.write_text("""
    watch_paths:
      - /Users/test/projects
    exclude_patterns:
      - node_modules
      - __pycache__
    """)

    return data_dir


@pytest.fixture(autouse=True)
def isolate_tests(monkeypatch):
    """Automatically isolate tests from system resources.

    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    # Prevent accidental writes to real home directory
    monkeypatch.setenv("PARAKEET_TEST_MODE", "1")

    # Mock git operations that might affect system
    # These will be selectively unmocked in integration tests
    pass


@pytest.fixture
def mock_git_operations(monkeypatch):
    """Mock git operations for unit testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Dictionary of mock objects
    """
    mocks = {}

    # Mock git.Repo
    mock_repo = Mock(spec=git.Repo)
    mock_repo.is_dirty.return_value = False
    mock_repo.head.is_detached = False
    mock_repo.active_branch.name = "main"
    mock_repo.remotes = [Mock(url="https://github.com/test/repo.git")]

    mock_commit = Mock()
    mock_commit.hexsha = "abc123def456"
    mock_commit.message = "Test commit message"
    mock_commit.author = "Test Author"
    mock_commit.committed_date = datetime.now().timestamp()
    mock_repo.head.commit = mock_commit

    mocks["repo"] = mock_repo
    mocks["commit"] = mock_commit

    # Patch git.Repo constructor
    monkeypatch.setattr("git.Repo", lambda path: mock_repo)

    return mocks