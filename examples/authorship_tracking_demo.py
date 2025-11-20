#!/usr/bin/env python3
"""Demo script to showcase authorship tracking capabilities."""

import tempfile
from pathlib import Path
import git
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parakeet.authorship_tracker import AuthorshipTracker, AuthorshipMetadata


def create_demo_project():
    """Create a demo project with various commits."""
    print("🎬 Creating demo project...")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="parakeet_demo_"))
    project_dir = temp_dir / "demo-project"
    project_dir.mkdir()
    
    print(f"📁 Created project at: {project_dir}")
    
    # Initialize git repo
    repo = git.Repo.init(project_dir)
    
    # Configure git
    with repo.config_writer() as config:
        config.set_value("user", "name", "Demo User")
        config.set_value("user", "email", "demo@example.com")
    
    # Create commits with different authorship patterns
    commits_data = [
        {
            "file": "main.py",
            "content": "print('Hello, World!')\n",
            "message": "feat: initial Python script [Claude]"
        },
        {
            "file": "utils.py",
            "content": "def helper():\n    pass\n",
            "message": "Add utility functions (GitHub Copilot assisted)"
        },
        {
            "file": "test.py",
            "content": "import unittest\n\nclass TestMain(unittest.TestCase):\n    pass\n",
            "message": "Add tests [Cursor]"
        },
        {
            "file": "README.md",
            "content": "# Demo Project\n\nA sample project.\n",
            "message": "docs: add README"  # Human commit
        },
        {
            "file": "config.json",
            "content": '{"version": "1.0"}\n',
            "message": "chore: add config [ChatGPT]"
        },
        {
            "file": "Dockerfile",
            "content": "FROM python:3.9\nWORKDIR /app\n",
            "message": "Add Dockerfile"  # Human commit
        },
        {
            "file": "requirements.txt",
            "content": "requests>=2.28.0\npytest>=7.0.0\n",
            "message": "feat: add dependencies [Claude Code]"
        },
    ]
    
    print("\n📝 Creating commits with different authorship patterns...")
    
    for i, commit_data in enumerate(commits_data, 1):
        # Write file
        file_path = project_dir / commit_data["file"]
        file_path.write_text(commit_data["content"])
        
        # Add and commit
        repo.index.add([commit_data["file"]])
        commit = repo.index.commit(commit_data["message"])
        
        print(f"  {i}. {commit.hexsha[:8]} - {commit_data['message']}")
    
    print(f"\n✅ Created {len(commits_data)} commits")
    
    return project_dir


def demonstrate_tracking(project_dir: Path):
    """Demonstrate authorship tracking."""
    print("\n" + "="*70)
    print("🔍 AUTHORSHIP TRACKING DEMONSTRATION")
    print("="*70)
    
    # Create tracker
    tracker_dir = project_dir.parent / ".parakeet"
    tracker_dir.mkdir(exist_ok=True)
    tracker = AuthorshipTracker(tracker_dir)
    
    # Track all commits
    print("\n📊 Tracking authorship for all commits...")
    repo = git.Repo(project_dir)
    
    for commit in repo.iter_commits():
        metadata = tracker.track_git_commit(project_dir, commit.hexsha)
        
        # Show detection results
        agent_icon = {
            'claude': '🧠',
            'claude_code': '🧠',
            'github_copilot': '🤖',
            'cursor_ai': '✨',
            'chatgpt': '💬',
            'human': '👤',
        }.get(metadata.agent, '❓')
        
        print(f"\n{agent_icon} Commit: {commit.hexsha[:8]}")
        print(f"   Message: {commit.message.strip()}")
        print(f"   Agent: {metadata.agent}")
        print(f"   IDE: {metadata.ide}")
        print(f"   Environment: {metadata.environment}")
        print(f"   Tools: {', '.join(metadata.tools[:3]) if metadata.tools else 'none'}")
        print(f"   Skills: {', '.join(metadata.skills[:3]) if metadata.skills else 'none'}")
        print(f"   Confidence: {metadata.confidence:.0%}")
    
    # Show statistics
    print("\n" + "="*70)
    print("📈 AUTHORSHIP STATISTICS")
    print("="*70)
    
    stats = tracker.get_statistics()
    
    print(f"\nTotal commits tracked: {stats['total_commits']}")
    
    print("\n🤖 By Agent:")
    for agent, count in sorted(stats['by_agent'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['total_commits'] * 100) if stats['total_commits'] > 0 else 0
        bar = '█' * int(percentage / 5)
        print(f"  {agent:20} {count:2} commits ({percentage:5.1f}%) {bar}")
    
    print("\n🔧 Tools Detected:")
    for tool, count in sorted(stats['top_tools'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {tool:20} {count:2} commits")
    
    print("\n🎯 Skills/Languages:")
    for skill, count in sorted(stats['top_skills'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {skill:20} {count:2} commits")
    
    # Show AI vs Human ratio
    ai_commits = sum(count for agent, count in stats['by_agent'].items() if agent != 'human')
    human_commits = stats['by_agent'].get('human', 0)
    total = stats['total_commits']
    
    print("\n" + "="*70)
    print("🤖 AI vs Human Contribution")
    print("="*70)
    
    if total > 0:
        ai_percent = (ai_commits / total) * 100
        human_percent = (human_commits / total) * 100
        
        print(f"\n  AI-assisted:  {ai_commits:2} commits ({ai_percent:5.1f}%) {'█' * int(ai_percent / 5)}")
        print(f"  Human-only:   {human_commits:2} commits ({human_percent:5.1f}%) {'█' * int(human_percent / 5)}")
        
        if ai_commits > 0:
            print(f"\n  💡 {ai_percent:.0f}% of your commits involved AI assistance!")
        if human_commits > 0:
            print(f"  👤 {human_percent:.0f}% were human-only commits")
    
    return tracker_dir


def demonstrate_queries(tracker_dir: Path):
    """Demonstrate querying capabilities."""
    print("\n" + "="*70)
    print("🔎 QUERY DEMONSTRATIONS")
    print("="*70)
    
    tracker = AuthorshipTracker(tracker_dir)
    
    # Query by specific agent
    print("\n📋 Claude commits:")
    claude_commits = tracker.query_by_agent("claude")
    for commit in claude_commits:
        print(f"  • {commit['sha'][:8]}")
    
    print("\n📋 GitHub Copilot commits:")
    copilot_commits = tracker.query_by_agent("github_copilot")
    for commit in copilot_commits:
        print(f"  • {commit['sha'][:8]}")
    
    print("\n📋 Human-only commits:")
    human_commits = tracker.query_by_agent("human")
    for commit in human_commits:
        print(f"  • {commit['sha'][:8]}")


def demonstrate_git_notes(project_dir: Path, tracker_dir: Path):
    """Demonstrate git notes integration."""
    print("\n" + "="*70)
    print("📝 GIT NOTES INTEGRATION (Experimental)")
    print("="*70)
    
    tracker = AuthorshipTracker(tracker_dir)
    repo = git.Repo(project_dir)
    
    # Get first commit
    commits = list(repo.iter_commits())
    if commits:
        commit = commits[-1]  # First commit
        
        print(f"\n🔍 Embedding authorship metadata in git notes for {commit.hexsha[:8]}...")
        
        # Create metadata
        metadata = AuthorshipMetadata(
            agent="claude",
            ide="cursor",
            environment="local",
            tools=["git", "pytest"],
            skills=["python"],
            orchestration="github_actions",
            confidence=0.95
        )
        
        # Embed in git notes
        success = tracker.embed_in_git_notes(project_dir, commit.hexsha, metadata)
        
        if success:
            print("✅ Successfully embedded authorship metadata in git notes")
            
            # Read it back
            print("\n📖 Reading back from git notes:")
            notes_data = tracker.read_from_git_notes(project_dir, commit.hexsha)
            
            if notes_data:
                print(f"  Agent: {notes_data.get('agent')}")
                print(f"  IDE: {notes_data.get('ide')}")
                print(f"  Environment: {notes_data.get('environment')}")
                print(f"  Tools: {notes_data.get('tools')}")
                print(f"  Skills: {notes_data.get('skills')}")
                print(f"  Confidence: {notes_data.get('confidence'):.0%}")
                
                print("\n💡 You can view git notes manually with:")
                print(f"   git notes --ref=refs/notes/authorship show {commit.hexsha[:8]}")
            else:
                print("⚠️  Could not read notes back")
        else:
            print("❌ Failed to embed git notes")


def main():
    """Run the demo."""
    print("\n" + "="*70)
    print("🦜 FRIENDLY PARAKEET - AUTHORSHIP TRACKING DEMO")
    print("="*70)
    
    try:
        # Create demo project
        project_dir = create_demo_project()
        
        # Demonstrate tracking
        tracker_dir = demonstrate_tracking(project_dir)
        
        # Demonstrate queries
        demonstrate_queries(tracker_dir)
        
        # Demonstrate git notes
        demonstrate_git_notes(project_dir, tracker_dir)
        
        # Final summary
        print("\n" + "="*70)
        print("✨ DEMO COMPLETE!")
        print("="*70)
        
        print(f"\n📁 Demo project created at: {project_dir}")
        print(f"📊 Authorship data stored in: {tracker_dir}")
        print("\nYou can explore the demo project with:")
        print(f"  cd {project_dir}")
        print(f"  git log --oneline")
        print(f"  git notes --ref=refs/notes/authorship list")
        
        print("\n🧹 To clean up, remove:")
        print(f"  rm -rf {project_dir.parent}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
