"""Test suite for AuthorshipTracker - tracking code authorship metadata.

This module tests the ability to infer and track metadata about how code was written:
- Which agent (Claude, Copilot, ChatGPT, human, etc.)
- Which IDE (VS Code, Cursor, Windsurf, etc.)
- Which environment (local, cloud, container, SSH, etc.)
- What tools and orchestration were used
- What skills and capabilities were involved
"""
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import git

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from parakeet.authorship_tracker import AuthorshipTracker, AuthorshipMetadata


class TestAuthorshipMetadata:
    """Tests for AuthorshipMetadata data structure."""

    def test_metadata_initialization_with_defaults(self):
        """Test metadata initializes with default values."""
        metadata = AuthorshipMetadata()
        
        assert metadata.agent == "unknown"
        assert metadata.ide == "unknown"
        assert metadata.environment == "unknown"
        assert metadata.tools == []
        assert metadata.skills == []
        assert metadata.orchestration == "unknown"
        assert isinstance(metadata.timestamp, str)
        assert metadata.confidence == 0.0

    def test_metadata_initialization_with_values(self):
        """Test metadata initializes with provided values."""
        metadata = AuthorshipMetadata(
            agent="claude",
            ide="cursor",
            environment="local",
            tools=["git", "pytest"],
            skills=["python", "tdd"],
            orchestration="github_copilot",
            confidence=0.95
        )
        
        assert metadata.agent == "claude"
        assert metadata.ide == "cursor"
        assert metadata.environment == "local"
        assert metadata.tools == ["git", "pytest"]
        assert metadata.skills == ["python", "tdd"]
        assert metadata.orchestration == "github_copilot"
        assert metadata.confidence == 0.95

    def test_metadata_to_dict(self):
        """Test metadata can be serialized to dictionary."""
        metadata = AuthorshipMetadata(
            agent="claude",
            ide="vscode",
            environment="local"
        )
        
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert data["agent"] == "claude"
        assert data["ide"] == "vscode"
        assert data["environment"] == "local"
        assert "timestamp" in data

    def test_metadata_from_dict(self):
        """Test metadata can be deserialized from dictionary."""
        data = {
            "agent": "copilot",
            "ide": "vscode",
            "environment": "cloud",
            "tools": ["docker", "kubernetes"],
            "skills": ["javascript", "testing"],
            "orchestration": "jenkins",
            "timestamp": "2024-01-01T00:00:00",
            "confidence": 0.8
        }
        
        metadata = AuthorshipMetadata.from_dict(data)
        
        assert metadata.agent == "copilot"
        assert metadata.ide == "vscode"
        assert metadata.environment == "cloud"
        assert metadata.tools == ["docker", "kubernetes"]
        assert metadata.skills == ["javascript", "testing"]
        assert metadata.orchestration == "jenkins"
        assert metadata.confidence == 0.8


class TestAuthorshipTrackerInitialization:
    """Tests for AuthorshipTracker initialization."""

    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            tracker = AuthorshipTracker(data_dir)
            
            assert tracker.data_dir == data_dir
            assert tracker.authorship_file == data_dir / 'authorship_data.json'
            assert isinstance(tracker.authorship_data, dict)

    def test_tracker_loads_existing_data(self):
        """Test tracker loads existing authorship data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            authorship_file = data_dir / 'authorship_data.json'
            
            # Create existing data
            existing_data = {
                "commits": [
                    {
                        "sha": "abc123",
                        "agent": "claude",
                        "ide": "cursor"
                    }
                ]
            }
            authorship_file.write_text(json.dumps(existing_data))
            
            tracker = AuthorshipTracker(data_dir)
            
            assert len(tracker.authorship_data["commits"]) == 1
            assert tracker.authorship_data["commits"][0]["agent"] == "claude"


class TestAgentDetection:
    """Tests for detecting which AI agent wrote the code."""

    def test_detect_claude_from_commit_message(self):
        """Test detecting Claude from commit message patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Claude-style commit messages
            messages = [
                "feat: add new feature using Claude",
                "Implemented by Claude Code",
                "[Claude] Update documentation",
                "claude: fix bug in parser"
            ]
            
            for msg in messages:
                agent = tracker.detect_agent_from_commit_message(msg)
                assert agent in ["claude", "claude_code"], f"Failed to detect Claude from: {msg}"

    def test_detect_copilot_from_commit_message(self):
        """Test detecting GitHub Copilot from commit message patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            messages = [
                "feat: add feature (Copilot assisted)",
                "GitHub Copilot: implement function",
                "[Copilot] refactor code",
                "Co-authored-by: GitHub Copilot"
            ]
            
            for msg in messages:
                agent = tracker.detect_agent_from_commit_message(msg)
                assert agent == "github_copilot", f"Failed to detect Copilot from: {msg}"

    def test_detect_human_from_commit_message(self):
        """Test detecting human author when no agent patterns found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            messages = [
                "fix: update dependencies",
                "refactor: clean up code",
                "feat: add new endpoint"
            ]
            
            for msg in messages:
                agent = tracker.detect_agent_from_commit_message(msg)
                assert agent == "human", f"Should detect human from: {msg}"

    def test_detect_agent_from_environment_variables(self):
        """Test detecting agent from environment variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Test Claude detection
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-123"}):
                agent = tracker.detect_agent_from_environment()
                assert "claude" in agent.lower()
            
            # Test OpenAI/ChatGPT detection
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-123"}):
                agent = tracker.detect_agent_from_environment()
                assert agent in ["chatgpt", "openai", "gpt"]

    def test_detect_agent_from_process_list(self):
        """Test detecting agent from running processes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Mock process detection
            mock_processes = [
                {"name": "Cursor", "cmdline": ["/Applications/Cursor.app"]},
                {"name": "Code", "cmdline": ["--enable-copilot"]},
            ]
            
            with patch.object(tracker, '_get_running_processes', return_value=mock_processes):
                agent = tracker.detect_agent_from_processes()
                assert agent in ["cursor_ai", "github_copilot", "vscode_copilot"]


class TestIDEDetection:
    """Tests for detecting which IDE was used."""

    def test_detect_ide_from_active_processes(self):
        """Test detecting IDE from active processes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Mock different IDE processes
            test_cases = [
                (["Code", "code"], "vscode"),
                (["Cursor"], "cursor"),
                (["Windsurf"], "windsurf"),
                (["PyCharm"], "pycharm"),
                (["vim"], "vim"),
            ]
            
            for processes, expected_ide in test_cases:
                mock_procs = [{"name": p} for p in processes]
                with patch.object(tracker, '_get_running_processes', return_value=mock_procs):
                    ide = tracker.detect_ide()
                    assert ide == expected_ide, f"Failed to detect {expected_ide} from {processes}"

    def test_detect_ide_from_git_config(self):
        """Test detecting IDE from git configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            git_config = {
                "core.editor": "code",
            }
            
            with patch.object(tracker, '_get_git_config', return_value=git_config):
                ide = tracker.detect_ide_from_git_config()
                assert ide in ["vscode", "code"]


class TestEnvironmentDetection:
    """Tests for detecting the development environment."""

    def test_detect_local_environment(self):
        """Test detecting local development environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            with patch.dict(os.environ, {}, clear=True):
                env = tracker.detect_environment()
                assert env in ["local", "workstation"]

    def test_detect_container_environment(self):
        """Test detecting container environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Docker detection - clear GitHub Actions env first
            with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}, clear=True):
                env = tracker.detect_environment()
                assert env in ["docker", "container"]
            
            # Check for dockerenv file
            with patch.dict(os.environ, {}, clear=True):
                with patch('os.path.exists', return_value=True) as mock_exists:
                    env = tracker.detect_environment()
                    # Should check for /.dockerenv
                    if any("dockerenv" in str(call) for call in mock_exists.call_args_list):
                        assert env in ["docker", "container"]

    def test_detect_cloud_environment(self):
        """Test detecting cloud environments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # GitHub Actions
            with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
                env = tracker.detect_environment()
                assert env == "github_actions"
            
            # GitLab CI
            with patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True):
                env = tracker.detect_environment()
                assert env == "gitlab_ci"
            
            # AWS CodeBuild
            with patch.dict(os.environ, {"CODEBUILD_BUILD_ID": "123"}, clear=True):
                env = tracker.detect_environment()
                assert env in ["aws_codebuild", "codebuild"]

    def test_detect_ssh_environment(self):
        """Test detecting SSH remote environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            with patch.dict(os.environ, {"SSH_CONNECTION": "1.2.3.4"}, clear=True):
                env = tracker.detect_environment()
                assert env in ["ssh", "remote"]


class TestToolsDetection:
    """Tests for detecting tools and orchestration."""

    def test_detect_version_control_tools(self):
        """Test detecting version control tools."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Create .git directory to simulate a git repo
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            
            tools = tracker.detect_tools(temp_dir)
            assert "git" in tools

    def test_detect_testing_frameworks(self):
        """Test detecting testing frameworks from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Create pytest.ini
            (Path(temp_dir) / "pytest.ini").write_text("[pytest]")
            tools = tracker.detect_tools(temp_dir)
            assert "pytest" in tools
            
            # Create package.json with jest
            (Path(temp_dir) / "package.json").write_text('{"devDependencies": {"jest": "^27.0.0"}}')
            tools = tracker.detect_tools(temp_dir)
            assert "jest" in tools or "npm" in tools

    def test_detect_containerization_tools(self):
        """Test detecting containerization tools."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Create Dockerfile
            (Path(temp_dir) / "Dockerfile").write_text("FROM python:3.9")
            tools = tracker.detect_tools(temp_dir)
            assert "docker" in tools
            
            # Create docker-compose.yml
            (Path(temp_dir) / "docker-compose.yml").write_text("version: '3'")
            tools = tracker.detect_tools(temp_dir)
            assert "docker-compose" in tools or "docker" in tools


class TestSkillsDetection:
    """Tests for detecting programming skills/languages used."""

    def test_detect_python_skills(self):
        """Test detecting Python as a skill."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            (Path(temp_dir) / "main.py").write_text("print('hello')")
            skills = tracker.detect_skills(temp_dir)
            assert "python" in skills

    def test_detect_javascript_skills(self):
        """Test detecting JavaScript/TypeScript skills."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            (Path(temp_dir) / "index.js").write_text("console.log('hello')")
            skills = tracker.detect_skills(temp_dir)
            assert "javascript" in skills
            
            (Path(temp_dir) / "app.ts").write_text("const x: number = 5")
            skills = tracker.detect_skills(temp_dir)
            assert "typescript" in skills

    def test_detect_multiple_skills(self):
        """Test detecting multiple programming languages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            (Path(temp_dir) / "main.py").write_text("# Python")
            (Path(temp_dir) / "index.js").write_text("// JavaScript")
            (Path(temp_dir) / "app.go").write_text("// Go")
            
            skills = tracker.detect_skills(temp_dir)
            assert "python" in skills
            assert "javascript" in skills
            assert "go" in skills


class TestOrchestrationDetection:
    """Tests for detecting orchestration and CI/CD systems."""

    def test_detect_github_actions(self):
        """Test detecting GitHub Actions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Create .github/workflows directory
            workflows_dir = Path(temp_dir) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)
            (workflows_dir / "ci.yml").write_text("name: CI")
            
            orchestration = tracker.detect_orchestration(temp_dir)
            assert orchestration == "github_actions"

    def test_detect_gitlab_ci(self):
        """Test detecting GitLab CI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            (Path(temp_dir) / ".gitlab-ci.yml").write_text("stages: [build]")
            orchestration = tracker.detect_orchestration(temp_dir)
            assert orchestration == "gitlab_ci"

    def test_detect_jenkins(self):
        """Test detecting Jenkins."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            (Path(temp_dir) / "Jenkinsfile").write_text("pipeline {}")
            orchestration = tracker.detect_orchestration(temp_dir)
            assert orchestration == "jenkins"


class TestAuthorshipTracking:
    """Tests for tracking and storing authorship metadata."""

    def test_track_commit_authorship(self):
        """Test tracking authorship for a git commit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            commit_data = {
                "sha": "abc123",
                "message": "feat: add feature [Claude]",
                "author": "John Doe",
                "timestamp": "2024-01-01T00:00:00"
            }
            
            metadata = tracker.track_commit(commit_data, Path(temp_dir))
            
            assert metadata.agent in ["claude", "claude_code"]
            assert metadata.timestamp is not None
            assert metadata.confidence > 0

    def test_store_authorship_metadata(self):
        """Test storing authorship metadata to disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            tracker = AuthorshipTracker(data_dir)
            
            metadata = AuthorshipMetadata(
                agent="claude",
                ide="cursor",
                environment="local"
            )
            
            tracker.store_metadata("abc123", metadata)
            
            # Verify data was saved
            assert (data_dir / "authorship_data.json").exists()
            
            # Verify data can be loaded
            new_tracker = AuthorshipTracker(data_dir)
            assert len(new_tracker.authorship_data["commits"]) > 0

    def test_query_authorship_by_agent(self):
        """Test querying commits by agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Store multiple commits
            tracker.store_metadata("sha1", AuthorshipMetadata(agent="claude"))
            tracker.store_metadata("sha2", AuthorshipMetadata(agent="copilot"))
            tracker.store_metadata("sha3", AuthorshipMetadata(agent="claude"))
            
            claude_commits = tracker.query_by_agent("claude")
            assert len(claude_commits) == 2

    def test_query_authorship_by_ide(self):
        """Test querying commits by IDE."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            tracker.store_metadata("sha1", AuthorshipMetadata(ide="cursor"))
            tracker.store_metadata("sha2", AuthorshipMetadata(ide="vscode"))
            tracker.store_metadata("sha3", AuthorshipMetadata(ide="cursor"))
            
            cursor_commits = tracker.query_by_ide("cursor")
            assert len(cursor_commits) == 2

    def test_get_authorship_statistics(self):
        """Test getting statistics about authorship."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = AuthorshipTracker(Path(temp_dir))
            
            # Add diverse authorship data
            tracker.store_metadata("sha1", AuthorshipMetadata(agent="claude", ide="cursor"))
            tracker.store_metadata("sha2", AuthorshipMetadata(agent="copilot", ide="vscode"))
            tracker.store_metadata("sha3", AuthorshipMetadata(agent="claude", ide="cursor"))
            tracker.store_metadata("sha4", AuthorshipMetadata(agent="human", ide="vim"))
            
            stats = tracker.get_statistics()
            
            assert stats["total_commits"] == 4
            assert "claude" in stats["by_agent"]
            assert stats["by_agent"]["claude"] == 2
            assert "cursor" in stats["by_ide"]
            assert stats["by_ide"]["cursor"] == 2


class TestIntegrationWithGit:
    """Tests for integrating authorship tracking with git operations."""

    def test_track_git_commit_with_metadata(self):
        """Test tracking authorship when git commit is made."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            repo_dir = Path(temp_dir) / "test_repo"
            repo_dir.mkdir()
            repo = git.Repo.init(repo_dir)
            
            # Configure git
            with repo.config_writer() as config:
                config.set_value("user", "name", "Test User")
                config.set_value("user", "email", "test@example.com")
            
            # Create a file and commit
            test_file = repo_dir / "test.py"
            test_file.write_text("print('hello')")
            repo.index.add(["test.py"])
            commit = repo.index.commit("feat: add test file [Claude]")
            
            # Track authorship
            tracker = AuthorshipTracker(Path(temp_dir))
            metadata = tracker.track_git_commit(repo_dir, commit.hexsha)
            
            assert metadata.agent in ["claude", "claude_code"]
            assert "python" in metadata.skills

    def test_embed_authorship_in_git_notes(self):
        """Test embedding authorship metadata in git notes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize git repo
            repo_dir = Path(temp_dir) / "test_repo"
            repo_dir.mkdir()
            repo = git.Repo.init(repo_dir)
            
            with repo.config_writer() as config:
                config.set_value("user", "name", "Test User")
                config.set_value("user", "email", "test@example.com")
            
            test_file = repo_dir / "test.py"
            test_file.write_text("print('hello')")
            repo.index.add(["test.py"])
            commit = repo.index.commit("test commit")
            
            # Track and embed authorship
            tracker = AuthorshipTracker(Path(temp_dir))
            metadata = AuthorshipMetadata(agent="claude", ide="cursor", environment="local")
            
            success = tracker.embed_in_git_notes(repo_dir, commit.hexsha, metadata)
            assert success is True
            
            # Verify git notes were added
            notes = tracker.read_from_git_notes(repo_dir, commit.hexsha)
            assert notes is not None
            assert notes["agent"] == "claude"
