"""Comprehensive test suite for ProjectScanner class.

This module provides thorough testing of all ProjectScanner functionality
including project detection, file statistics, error handling, and edge cases.
"""
import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import pytest
import git

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from parakeet.scanner import ProjectScanner


class TestProjectScannerInitialization:
    """Tests for ProjectScanner initialization and configuration."""

    @pytest.mark.unit
    def test_scanner_initialization_with_valid_paths(self):
        """Test scanner initializes with valid watch paths."""
        watch_paths = ["/path/one", "/path/two"]
        exclude_patterns = ["node_modules", "__pycache__"]

        scanner = ProjectScanner(watch_paths, exclude_patterns)

        assert scanner.watch_paths == watch_paths
        assert scanner.exclude_patterns == exclude_patterns

    @pytest.mark.unit
    def test_scanner_initialization_with_empty_paths(self):
        """Test scanner initializes with empty watch paths."""
        scanner = ProjectScanner([], [])

        assert scanner.watch_paths == []
        assert scanner.exclude_patterns == []

    @pytest.mark.unit
    def test_project_indicators_are_properly_defined(self):
        """Test that PROJECT_INDICATORS contains expected project types."""
        scanner = ProjectScanner([], [])

        # Check for common project indicators
        assert 'setup.py' in scanner.PROJECT_INDICATORS
        assert 'package.json' in scanner.PROJECT_INDICATORS
        assert 'Gemfile' in scanner.PROJECT_INDICATORS
        assert 'go.mod' in scanner.PROJECT_INDICATORS
        assert '.git' in scanner.PROJECT_INDICATORS
        assert '*.csproj' in scanner.PROJECT_INDICATORS


class TestProjectDetection:
    """Tests for project detection logic."""

    @pytest.mark.unit
    def test_detect_python_project(self, temp_dir):
        """Test detection of Python projects."""
        project_dir = temp_dir / "python_project"
        project_dir.mkdir()
        (project_dir / "setup.py").touch()
        (project_dir / "requirements.txt").touch()

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        assert len(projects) == 1
        assert projects[0]["name"] == "python_project"
        assert projects[0]["type"] == "python"

    @pytest.mark.unit
    def test_detect_javascript_project(self, temp_dir):
        """Test detection of JavaScript/Node.js projects."""
        project_dir = temp_dir / "js_project"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test-project"}')

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        assert len(projects) == 1
        assert projects[0]["name"] == "js_project"
        assert projects[0]["type"] == "javascript"

    @pytest.mark.unit
    def test_detect_multiple_project_types(self, sample_project_structure):
        """Test detection of multiple project types simultaneously."""
        scanner = ProjectScanner(
            [str(Path(list(sample_project_structure.values())[0]).parent)],
            []
        )
        projects = scanner.scan_projects()

        # Should detect Python, JavaScript, Ruby, and Go projects
        project_names = {p["name"] for p in projects}
        assert "python_project" in project_names
        assert "js_project" in project_names
        assert "ruby_project" in project_names
        assert "go_project" in project_names

        # Non-project directory should not be detected
        assert "not_a_project" not in project_names

    @pytest.mark.unit
    def test_detect_project_with_glob_patterns(self, temp_dir):
        """Test project detection using glob patterns like *.csproj."""
        project_dir = temp_dir / "dotnet_project"
        project_dir.mkdir()
        (project_dir / "MyApp.csproj").touch()

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        assert len(projects) == 1
        assert projects[0]["type"] == "dotnet"

    @pytest.mark.unit
    def test_no_projects_in_empty_directory(self, temp_dir):
        """Test that empty directories are not detected as projects."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        assert len(projects) == 0

    @pytest.mark.unit
    def test_nested_projects_detection(self, temp_dir):
        """Test detection of nested projects (project within project)."""
        parent_project = temp_dir / "parent_project"
        parent_project.mkdir()
        (parent_project / "package.json").write_text('{"name": "parent"}')

        child_project = parent_project / "child_project"
        child_project.mkdir()
        (child_project / "setup.py").touch()

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        # Should detect parent but not scan inside it for children
        assert len(projects) == 1
        assert projects[0]["name"] == "parent_project"


class TestExcludePatterns:
    """Tests for exclude pattern functionality."""

    @pytest.mark.unit
    def test_exclude_patterns_filter_directories(self, temp_dir):
        """Test that excluded directories are not scanned."""
        # Create projects
        normal_project = temp_dir / "normal_project"
        normal_project.mkdir()
        (normal_project / "setup.py").touch()

        excluded_project = temp_dir / "node_modules"
        excluded_project.mkdir()
        (excluded_project / "package.json").touch()

        scanner = ProjectScanner([str(temp_dir)], ["node_modules"])
        projects = scanner.scan_projects()

        assert len(projects) == 1
        assert projects[0]["name"] == "normal_project"

    @pytest.mark.unit
    def test_exclude_patterns_with_partial_match(self, temp_dir):
        """Test exclude patterns with partial name matching."""
        test_dir = temp_dir / "test_cache"
        test_dir.mkdir()
        (test_dir / "setup.py").touch()

        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "setup.py").touch()

        scanner = ProjectScanner([str(temp_dir)], ["cache"])
        projects = scanner.scan_projects()

        # Both directories contain "cache" so both should be excluded
        assert len(projects) == 0

    @pytest.mark.unit
    def test_should_exclude_method(self):
        """Test the _should_exclude method directly."""
        scanner = ProjectScanner([], ["node_modules", "__pycache__", ".git"])

        assert scanner._should_exclude("node_modules") is True
        assert scanner._should_exclude("__pycache__") is True
        assert scanner._should_exclude(".git") is True
        assert scanner._should_exclude("my_project") is False
        assert scanner._should_exclude("git_project") is True  # Contains "git"


class TestGitInformation:
    """Tests for Git repository information extraction."""

    @pytest.mark.unit
    @pytest.mark.git
    def test_git_info_with_normal_repository(self, git_repo_with_commits):
        """Test git info extraction from normal repository."""
        scanner = ProjectScanner([], [])
        git_info = scanner._get_git_info(Path(git_repo_with_commits.working_dir))

        assert git_info is not None
        assert git_info["branch"] == "master"
        assert git_info["last_commit"] is not None
        assert git_info["last_commit"]["sha"] is not None
        assert git_info["last_commit"]["message"] == "Commit 2"
        assert git_info["is_dirty"] is False
        assert "github.com/test/repo.git" in git_info["remote_url"]

    @pytest.mark.unit
    @pytest.mark.git
    def test_git_info_with_dirty_repository(self, git_repo_with_commits):
        """Test git info shows dirty state correctly."""
        repo_path = Path(git_repo_with_commits.working_dir)

        # Make repository dirty
        (repo_path / "new_file.txt").write_text("uncommitted changes")

        scanner = ProjectScanner([], [])
        git_info = scanner._get_git_info(repo_path)

        assert git_info["is_dirty"] is True

    @pytest.mark.unit
    @pytest.mark.git
    def test_git_info_with_detached_head(self, detached_head_repo):
        """Test git info extraction with detached HEAD state."""
        scanner = ProjectScanner([], [])
        git_info = scanner._get_git_info(Path(detached_head_repo.working_dir))

        assert git_info is not None
        assert git_info["branch"] == "detached"

    @pytest.mark.unit
    def test_git_info_with_non_git_directory(self, temp_dir):
        """Test git info returns None for non-git directories."""
        normal_dir = temp_dir / "not_a_repo"
        normal_dir.mkdir()

        scanner = ProjectScanner([], [])
        git_info = scanner._get_git_info(normal_dir)

        assert git_info is None

    @pytest.mark.unit
    @pytest.mark.git
    def test_get_remote_url_without_remotes(self, temp_dir):
        """Test remote URL extraction when no remotes exist."""
        repo_path = temp_dir / "no_remote"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        scanner = ProjectScanner([], [])
        remote_url = scanner._get_remote_url(repo)

        assert remote_url is None


class TestDirectoryStatistics:
    """Tests for directory statistics calculation."""

    @pytest.mark.unit
    def test_directory_stats_calculation(self, temp_dir):
        """Test calculation of directory statistics."""
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Create some files
        (project_dir / "file1.py").write_text("print('hello')")
        (project_dir / "file2.txt").write_text("test content")

        subdir = project_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.js").write_text("console.log('test');")

        scanner = ProjectScanner([], [])
        stats = scanner._get_directory_stats(project_dir)

        assert stats["file_count"] == 3
        assert stats["total_size"] > 0
        assert stats["last_modified"] is not None

    @pytest.mark.unit
    def test_directory_stats_excludes_patterns(self, temp_dir):
        """Test that excluded patterns are not counted in stats."""
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        (project_dir / "main.py").write_text("code")

        cache_dir = project_dir / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "cached.pyc").write_text("cached")

        scanner = ProjectScanner([], ["__pycache__"])
        stats = scanner._get_directory_stats(project_dir)

        # Should only count main.py, not the cached file
        assert stats["file_count"] == 1

    @pytest.mark.unit
    def test_directory_stats_with_permission_errors(self, temp_dir, monkeypatch):
        """Test directory stats handles permission errors gracefully."""
        project_dir = temp_dir / "project"
        project_dir.mkdir()
        (project_dir / "file.txt").write_text("content")

        def mock_stat_error(*args, **kwargs):
            raise PermissionError("Access denied")

        scanner = ProjectScanner([], [])

        with monkeypatch.context() as m:
            m.setattr(Path, "stat", mock_stat_error)
            stats = scanner._get_directory_stats(project_dir)

        # Should handle error gracefully
        assert stats["file_count"] == 1  # File found but stat failed
        assert stats["total_size"] == 0
        assert stats["last_modified"] is None


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    @pytest.mark.unit
    def test_scan_with_nonexistent_watch_path(self):
        """Test scanning with non-existent watch paths."""
        scanner = ProjectScanner(["/nonexistent/path"], [])
        projects = scanner.scan_projects()

        # Should handle gracefully and return empty list
        assert projects == []

    @pytest.mark.unit
    def test_scan_with_permission_denied(self, temp_dir, monkeypatch):
        """Test scanning handles permission errors gracefully."""
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir()

        def mock_iterdir_error(*args, **kwargs):
            raise PermissionError("Permission denied")

        scanner = ProjectScanner([str(temp_dir)], [])

        with monkeypatch.context() as m:
            m.setattr(Path, "iterdir", mock_iterdir_error)
            projects = scanner.scan_projects()

        # Should handle error and return empty list
        assert projects == []

    @pytest.mark.unit
    def test_analyze_directory_with_os_error(self, temp_dir, monkeypatch):
        """Test _analyze_directory handles OS errors gracefully."""
        project_dir = temp_dir / "project"
        project_dir.mkdir()
        (project_dir / "setup.py").touch()

        def mock_exists_error(*args, **kwargs):
            raise OSError("Disk error")

        scanner = ProjectScanner([], [])

        with monkeypatch.context() as m:
            m.setattr(Path, "exists", mock_exists_error)
            result = scanner._analyze_directory(project_dir)

        assert result is None


class TestProjectTypeDetection:
    """Tests for project type detection logic."""

    @pytest.mark.unit
    def test_detect_project_type_python(self):
        """Test Python project type detection."""
        scanner = ProjectScanner([], [])

        assert scanner._detect_project_type("setup.py") == "python"
        assert scanner._detect_project_type("pyproject.toml") == "python"
        assert scanner._detect_project_type("requirements.txt") == "python"
        assert scanner._detect_project_type("Pipfile") == "python"

    @pytest.mark.unit
    def test_detect_project_type_javascript(self):
        """Test JavaScript project type detection."""
        scanner = ProjectScanner([], [])

        assert scanner._detect_project_type("package.json") == "javascript"
        assert scanner._detect_project_type("yarn.lock") == "javascript"

    @pytest.mark.unit
    def test_detect_project_type_other_languages(self):
        """Test project type detection for other languages."""
        scanner = ProjectScanner([], [])

        assert scanner._detect_project_type("Gemfile") == "ruby"
        assert scanner._detect_project_type("go.mod") == "go"
        assert scanner._detect_project_type("pom.xml") == "java"
        assert scanner._detect_project_type("Cargo.toml") == "rust"
        assert scanner._detect_project_type("Makefile") == "c/c++"

    @pytest.mark.unit
    def test_detect_project_type_unknown(self):
        """Test unknown project type detection."""
        scanner = ProjectScanner([], [])

        assert scanner._detect_project_type("unknown.file") == "unknown"
        assert scanner._detect_project_type(".git") == "unknown"


class TestIntegrationScenarios:
    """Integration tests for complex scanning scenarios."""

    @pytest.mark.integration
    def test_full_scan_workflow(self, temp_dir):
        """Test complete scan workflow with multiple projects."""
        # Create multiple projects
        for i in range(3):
            project = temp_dir / f"project_{i}"
            project.mkdir()

            if i == 0:
                (project / "setup.py").touch()
                git.Repo.init(project)
            elif i == 1:
                (project / "package.json").write_text('{"name": "proj"}')
            else:
                (project / "go.mod").touch()

        # Add an excluded directory
        excluded = temp_dir / "node_modules"
        excluded.mkdir()
        (excluded / "package.json").touch()

        scanner = ProjectScanner([str(temp_dir)], ["node_modules"])
        projects = scanner.scan_projects()

        assert len(projects) == 3
        project_types = {p["type"] for p in projects}
        assert "python" in project_types
        assert "javascript" in project_types
        assert "go" in project_types

    @pytest.mark.integration
    @pytest.mark.git
    def test_scan_with_various_git_states(self, temp_dir):
        """Test scanning projects with different git states."""
        # Normal repo with commits
        normal = temp_dir / "normal"
        normal.mkdir()
        (normal / "setup.py").touch()
        repo1 = git.Repo.init(normal)
        repo1.index.add(["setup.py"])
        repo1.index.commit("Initial commit")

        # Empty repo (no commits)
        empty = temp_dir / "empty"
        empty.mkdir()
        (empty / "package.json").touch()
        git.Repo.init(empty)

        # No git repo
        no_git = temp_dir / "no_git"
        no_git.mkdir()
        (no_git / "go.mod").touch()

        scanner = ProjectScanner([str(temp_dir)], [])
        projects = scanner.scan_projects()

        assert len(projects) == 3

        for project in projects:
            if project["name"] == "normal":
                assert project["git"]["last_commit"] is not None
            elif project["name"] == "empty":
                assert project["git"]["last_commit"] is None
            elif project["name"] == "no_git":
                assert project["git"] is None


class TestPerformance:
    """Tests for performance and scalability."""

    @pytest.mark.unit
    @pytest.mark.slow
    def test_scan_large_directory_tree(self, temp_dir):
        """Test scanning performance with large directory tree."""
        import time

        # Create a large directory tree
        for i in range(20):
            project = temp_dir / f"project_{i}"
            project.mkdir()
            (project / "package.json").touch()

            # Add subdirectories
            for j in range(10):
                subdir = project / f"subdir_{j}"
                subdir.mkdir()
                (subdir / f"file_{j}.txt").touch()

        scanner = ProjectScanner([str(temp_dir)], [])

        start_time = time.time()
        projects = scanner.scan_projects()
        elapsed = time.time() - start_time

        assert len(projects) == 20
        assert elapsed < 10.0  # Should complete within 10 seconds

    @pytest.mark.unit
    def test_scan_with_many_exclude_patterns(self, temp_dir):
        """Test scanning performance with many exclude patterns."""
        # Create projects
        for i in range(5):
            project = temp_dir / f"project_{i}"
            project.mkdir()
            (project / "setup.py").touch()

        # Many exclude patterns
        exclude_patterns = [f"pattern_{i}" for i in range(100)]

        scanner = ProjectScanner([str(temp_dir)], exclude_patterns)
        projects = scanner.scan_projects()

        assert len(projects) == 5  # All projects should be found