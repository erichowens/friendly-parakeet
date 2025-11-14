"""Test cases for scanner handling of empty git repositories (TDD - Red phase).

These tests are written BEFORE fixing the bug to demonstrate TDD approach.
They should FAIL initially, proving the bug exists.
"""
import pytest
import git
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from parakeet.scanner import ProjectScanner


class TestEmptyGitRepositoryHandling:
    """Test suite for empty git repository handling.

    This addresses the bug where scanner crashes with:
    ValueError: Reference at 'refs/heads/main' does not exist
    """

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_handles_empty_git_repo_no_commits(self, empty_git_repo, temp_dir):
        """Test that scanner gracefully handles git repo with no commits.

        This is the PRIMARY test for the reported bug.
        An empty git repo (git init but no commits) should not crash the scanner.
        """
        # Create a project indicator file so the project is detected
        (Path(empty_git_repo.working_dir) / "setup.py").write_text("# Empty setup.py")

        # Scanner looks for projects in subdirectories of watch_path
        scanner = ProjectScanner(
            watch_paths=[str(Path(empty_git_repo.working_dir).parent)],
            exclude_patterns=["node_modules", "__pycache__"]
        )

        # This should NOT raise an exception - the bug would cause ValueError here
        projects = scanner.scan_projects()

        # Verify the project is still detected
        assert len(projects) == 1
        project = projects[0]
        assert project["path"] == str(empty_git_repo.working_dir)

        # Git info should be present but indicate no commits
        assert "git" in project
        git_info = project["git"]

        # Should handle missing commit gracefully
        if git_info:
            assert git_info.get("branch") in [None, "main", "master", "unborn"]
            assert git_info.get("last_commit") is None or git_info["last_commit"].get("sha") is None
            assert "is_dirty" in git_info
            assert git_info.get("remote_url") is None  # No remote in empty repo

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_handles_empty_repo_with_unborn_branch(self, temp_dir):
        """Test scanner handles repository with unborn branch (no commits).

        Git repositories can have an 'unborn' branch state before first commit.
        """
        repo_path = temp_dir / "unborn_branch_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create a project indicator file so the project is detected
        (repo_path / "package.json").write_text('{"name": "test"}')

        # Verify repo is in unborn state
        with pytest.raises(ValueError) as exc_info:
            _ = repo.head.commit  # This should raise the exact error we're fixing
        assert "does not exist" in str(exc_info.value).lower()

        scanner = ProjectScanner(
            watch_paths=[str(repo_path.parent)],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )

        # Scanner should NOT crash
        projects = scanner.scan_projects()
        assert len(projects) == 1

        git_info = projects[0].get("git")
        assert git_info is None or git_info.get("last_commit") is None

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_handles_bare_repository(self, temp_dir):
        """Test scanner handles bare git repository (no working tree)."""
        bare_repo_path = temp_dir / "bare_repo.git"
        bare_repo_path.mkdir()

        # Create bare repository
        git.Repo.init(bare_repo_path, bare=True)

        scanner = ProjectScanner(
            watch_paths=[str(temp_dir)],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )

        # Should not crash when encountering bare repo
        projects = scanner.scan_projects()

        # Bare repos might not be detected as projects (no working files)
        # But scanner should not crash
        assert isinstance(projects, list)

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_handles_corrupted_git_repo(self, corrupted_git_repo):
        """Test scanner handles corrupted git repository gracefully."""
        scanner = ProjectScanner(
            watch_paths=[str(corrupted_git_repo.parent)],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )

        # Should not crash when encountering corrupted repo
        projects = scanner.scan_projects()

        # Project might still be detected (has .git dir) but git_info should be None
        matching_projects = [p for p in projects if Path(p["path"]) == corrupted_git_repo]
        if matching_projects:
            project = matching_projects[0]
            assert project.get("git") is None

    @pytest.mark.unit
    @pytest.mark.git
    def test_get_git_info_with_empty_repo(self, empty_git_repo):
        """Test _get_git_info method directly with empty repository."""
        scanner = ProjectScanner(
            watch_paths=[],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )

        # Call the problematic method directly
        git_info = scanner._get_git_info(Path(empty_git_repo.working_dir))

        # Should return None or valid info without crashing
        assert git_info is None or git_info.get("last_commit") is None

    @pytest.mark.unit
    @pytest.mark.git
    def test_get_git_info_returns_safe_defaults_for_empty_repo(self, empty_git_repo):
        """Test that _get_git_info returns safe defaults for empty repository."""
        scanner = ProjectScanner(
            watch_paths=[],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )
        git_info = scanner._get_git_info(Path(empty_git_repo.working_dir))

        if git_info is not None:
            # Verify safe defaults are returned
            assert isinstance(git_info, dict)
            assert "branch" in git_info
            assert "is_dirty" in git_info
            assert git_info.get("last_commit") is None or git_info["last_commit"] == {
                "sha": None,
                "message": "No commits yet",
                "author": None,
                "date": None
            }

    @pytest.mark.unit
    @pytest.mark.git
    @pytest.mark.parametrize("exception_type,exception_message", [
        (ValueError, "Reference at 'refs/heads/main' does not exist"),
        (git.exc.InvalidGitRepositoryError, "Invalid repository"),
        (git.exc.GitCommandError, "Git command failed"),
        (AttributeError, "'NoneType' object has no attribute"),
        (TypeError, "unsupported operand type"),
    ])
    def test_get_git_info_handles_various_git_exceptions(
        self, temp_dir, monkeypatch, exception_type, exception_message
    ):
        """Test that _get_git_info handles various git-related exceptions."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()

        # Mock git.Repo to raise various exceptions
        def mock_repo_init(path):
            mock_repo = Mock(spec=git.Repo)
            mock_repo.head.commit = Mock(side_effect=exception_type(exception_message))
            return mock_repo

        monkeypatch.setattr("parakeet.scanner.git.Repo", mock_repo_init)

        scanner = ProjectScanner(
            watch_paths=[],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )
        git_info = scanner._get_git_info(repo_path)

        # Should handle exception and return None
        assert git_info is None

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_performance_with_empty_repos(self, temp_dir):
        """Test scanner performance doesn't degrade with multiple empty repos."""
        import time

        # Create multiple empty repos
        for i in range(10):
            repo_path = temp_dir / f"empty_repo_{i}"
            repo_path.mkdir()
            git.Repo.init(repo_path)

        scanner = ProjectScanner(
            watch_paths=[str(temp_dir)],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )

        start_time = time.time()
        projects = scanner.scan_projects()
        elapsed_time = time.time() - start_time

        # Should complete quickly even with multiple empty repos
        assert elapsed_time < 5.0  # 5 seconds is generous
        assert len(projects) == 10

    @pytest.mark.unit
    @pytest.mark.git
    def test_scanner_mixed_repo_states(self, temp_dir, git_repo_with_commits, empty_git_repo):
        """Test scanner handles mix of empty and populated repositories."""
        # Create a watch path containing both repo types
        watch_path = temp_dir / "mixed_repos"
        watch_path.mkdir()

        # Move repos to watch path
        import shutil
        shutil.move(str(git_repo_with_commits.working_dir), str(watch_path / "with_commits"))
        shutil.move(str(empty_git_repo.working_dir), str(watch_path / "empty"))

        scanner = ProjectScanner(
            watch_paths=[str(watch_path)],
            exclude_patterns=["node_modules", "__pycache__", ".git"]
        )
        projects = scanner.scan_projects()

        # Should detect both projects
        assert len(projects) == 2

        # Verify each is handled correctly
        for project in projects:
            assert "git" in project
            if "with_commits" in project["path"]:
                # Should have commit info
                assert project["git"] is not None
                assert project["git"].get("last_commit") is not None
            else:
                # Empty repo - should handle gracefully
                git_info = project["git"]
                assert git_info is None or git_info.get("last_commit") is None