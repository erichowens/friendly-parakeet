"""Command-line interface for Friendly Parakeet."""

import click
import json
import os
from pathlib import Path

from .parakeet import Parakeet
from .dashboard import create_app
from .sounds import play_sound


@click.group()
@click.version_option(version='0.1.0')
def main():
    """🦜 Friendly Parakeet - Your coding progress companion."""
    pass


@main.command()
@click.option('--config', '-c', help='Path to config file')
def scan(config):
    """Scan projects and update tracking data."""
    parakeet = Parakeet(config)
    projects = parakeet.scan_and_update()

    # Play chirp sound for scan completion
    play_sound("chirp")

    click.echo(f"\n✅ Scanned {len(projects)} project(s)")

    # Show summary
    for project in projects:
        velocity = parakeet.tracker.get_velocity(project['path'])
        inactivity = parakeet.tracker.get_inactivity_days(project['path'])

        status_icon = "🟢" if inactivity < 7 else "🟡" if inactivity < 30 else "🔴"
        click.echo(f"{status_icon} {project['name']}: "
                   f"{velocity['active_days']} active days, "
                   f"trend: {velocity['trend']}")


@main.command()
@click.argument('project_path', required=False)
@click.option('--config', '-c', help='Path to config file')
def breadcrumb(project_path, config):
    """View breadcrumbs for a project or all projects."""
    parakeet = Parakeet(config)

    if project_path:
        # Show breadcrumbs for specific project
        breadcrumbs = parakeet.breadcrumbs.get_breadcrumbs(project_path)
        if not breadcrumbs:
            click.echo(f"No breadcrumbs found for {project_path}")
            return

        # Play chirp sound when showing breadcrumbs
        play_sound("chirp")

        click.echo(f"\n📍 Breadcrumbs for {Path(project_path).name}:\n")
        for crumb in breadcrumbs:
            click.echo(f"Timestamp: {crumb['timestamp']}")
            click.echo(f"Status: {crumb['status']}")
            click.echo(f"Inactive days: {crumb['inactivity_days']}")
            click.echo("\nPrompt suggestions:")
            for i, suggestion in enumerate(crumb['prompt_suggestions'], 1):
                click.echo(f"  {i}. {suggestion}")
            click.echo("\n" + "-" * 60 + "\n")
    else:
        # Show all breadcrumbs
        all_breadcrumbs = parakeet.breadcrumbs.get_all_breadcrumbs()
        if not all_breadcrumbs:
            click.echo("No breadcrumbs found. Run 'parakeet scan' first.")
            return

        # Play chirp sound
        play_sound("chirp")

        click.echo(f"\n📍 All Breadcrumbs:\n")
        for path, crumbs in all_breadcrumbs.items():
            click.echo(f"{Path(path).name}: {len(crumbs)} breadcrumb(s)")


@main.command()
@click.option('--config', '-c', help='Path to config file')
@click.option('--port', '-p', default=5000, help='Port to run dashboard on')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind to')
def dashboard(config, port, host):
    """Start the dashboard web interface."""
    parakeet = Parakeet(config)
    app = create_app(parakeet)

    # Play hello sound when starting dashboard
    play_sound("hello")

    click.echo(f"\n🦜 Starting Friendly Parakeet Dashboard...")
    click.echo(f"🌐 Open http://{host}:{port} in your browser\n")

    app.run(host=host, port=port, debug=False)


@main.command()
@click.option('--config', '-c', help='Path to config file')
def status(config):
    """Show overall status and statistics."""
    parakeet = Parakeet(config)
    data = parakeet.get_dashboard_data()
    
    click.echo("\n🦜 Friendly Parakeet Status\n")
    click.echo(f"Total projects: {data['stats']['total_projects']}")
    click.echo(f"Active projects: {data['stats']['active_projects']}")
    click.echo(f"Total breadcrumbs: {data['stats']['total_breadcrumbs']}")
    
    click.echo("\n📊 Recent Activity:\n")
    for activity in data['activity_log'][:10]:
        icon = "📍" if activity['type'] == 'breadcrumb' else "✏️"
        click.echo(f"{icon} {activity['timestamp'][:10]} - {activity['details']}")


@main.command()
@click.argument('key')
@click.argument('value')
@click.option('--config', '-c', help='Path to config file')
def config_set(key, value, config):
    """Set a configuration value."""
    from .config import Config
    cfg = Config(config)
    
    # Try to parse value as JSON for lists/dicts
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value
    
    cfg.set(key, parsed_value)
    click.echo(f"✅ Set {key} = {parsed_value}")


@main.command()
@click.option('--config', '-c', help='Path to config file')
def config_show(config):
    """Show current configuration."""
    from .config import Config
    cfg = Config(config)
    
    click.echo("\n⚙️  Current Configuration:\n")
    click.echo(json.dumps(cfg.config, indent=2))


@main.command()
@click.argument('project_path')
@click.option('--config', '-c', help='Path to config file')
def maintain(project_path, config):
    """Perform git maintenance on a project (auto-commit, push)."""
    parakeet = Parakeet(config)

    click.echo(f"\n🔧 Running git maintenance on {Path(project_path).name}...\n")

    result = parakeet.git_maintainer.perform_maintenance(project_path)

    if result['success']:
        # Play happy sound for successful maintenance
        play_sound("happy")
        click.echo("✅ Maintenance completed successfully:")
        for action in result['actions']:
            click.echo(f"  • {action}")
    else:
        # Play alert sound for failure
        play_sound("alert")
        click.echo(f"❌ Maintenance failed: {result['error']}")


@main.command()
@click.argument('project_path')
@click.option('--enabled/--disabled', default=True, help='Enable or disable auto-commit')
@click.option('--config', '-c', help='Path to config file')
def auto_commit(project_path, enabled, config):
    """Enable or disable auto-commit for a project."""
    parakeet = Parakeet(config)
    parakeet.git_maintainer.set_auto_commit(project_path, enabled)
    
    status = "enabled" if enabled else "disabled"
    click.echo(f"✅ Auto-commit {status} for {Path(project_path).name}")


@main.command()
@click.argument('project_path')
@click.option('--enabled/--disabled', default=True, help='Enable or disable auto-push')
@click.option('--config', '-c', help='Path to config file')
def auto_push(project_path, enabled, config):
    """Enable or disable auto-push for a project."""
    parakeet = Parakeet(config)
    parakeet.git_maintainer.set_auto_push(project_path, enabled)
    
    status = "enabled" if enabled else "disabled"
    click.echo(f"✅ Auto-push {status} for {Path(project_path).name}")


@main.command()
@click.argument('project_path')
@click.option('--config', '-c', help='Path to config file')
def changelog(project_path, config):
    """View changelog for a project."""
    parakeet = Parakeet(config)
    
    md = parakeet.changelog.generate_changelog_markdown(project_path)
    click.echo(md)


@main.command()
@click.argument('project_path')
@click.option('--config', '-c', help='Path to config file')
def time_report(project_path, config):
    """View time tracking report for a project."""
    parakeet = Parakeet(config)

    md = parakeet.changelog.generate_time_report(project_path)
    click.echo(md)


@main.command()
@click.argument('path')
@click.option('--config', '-c', help='Path to config file')
def add_path(path, config):
    """Add a directory to watch paths."""
    from .config import Config
    cfg = Config(config)

    path = os.path.expanduser(path)
    if not os.path.exists(path):
        play_sound("alert")
        click.echo(f"❌ Path does not exist: {path}")
        return

    watch_paths = cfg.get('watch_paths', [])
    if path in watch_paths or os.path.expanduser(path) in [os.path.expanduser(p) for p in watch_paths]:
        click.echo(f"ℹ️  Path already in watch list: {path}")
        return

    watch_paths.append(path)
    cfg.set('watch_paths', watch_paths)

    play_sound("happy")
    click.echo(f"✅ Added to watch paths: {path}")
    click.echo(f"   Total watch paths: {len(watch_paths)}")


@main.command()
@click.argument('path')
@click.option('--config', '-c', help='Path to config file')
def remove_path(path, config):
    """Remove a directory from watch paths."""
    from .config import Config
    cfg = Config(config)

    path = os.path.expanduser(path)
    watch_paths = cfg.get('watch_paths', [])
    expanded_paths = [os.path.expanduser(p) for p in watch_paths]

    if path not in expanded_paths:
        play_sound("alert")
        click.echo(f"❌ Path not in watch list: {path}")
        click.echo(f"\nCurrent watch paths:")
        for wp in watch_paths:
            click.echo(f"  • {wp}")
        return

    # Remove by expanded path
    idx = expanded_paths.index(path)
    removed = watch_paths.pop(idx)
    cfg.set('watch_paths', watch_paths)

    play_sound("chirp")
    click.echo(f"✅ Removed from watch paths: {removed}")
    click.echo(f"   Total watch paths: {len(watch_paths)}")


@main.command()
@click.option('--config', '-c', help='Path to config file')
def list_paths(config):
    """List all watch paths."""
    from .config import Config
    cfg = Config(config)

    watch_paths = cfg.get('watch_paths', [])
    recursive = cfg.get('scan_recursive', True)
    max_depth = cfg.get('scan_max_depth', 3)

    play_sound("chirp")
    click.echo("\n📂 Watch Paths Configuration\n")
    click.echo(f"Scan mode: {'Recursive' if recursive else 'Immediate subdirectories only'}")
    if recursive:
        click.echo(f"Max depth: {max_depth} levels")
    click.echo(f"\nWatch paths ({len(watch_paths)}):")

    for path in watch_paths:
        expanded = os.path.expanduser(path)
        exists = os.path.exists(expanded)
        status = "✅" if exists else "❌"
        click.echo(f"  {status} {path}")
        if not exists:
            click.echo(f"      (Path does not exist: {expanded})")


@main.command()
@click.option('--config', '-c', help='Path to config file')
def setup(config):
    """Interactive setup wizard for first-time configuration."""
    from .config import Config
    import os

    play_sound("hello")
    click.echo("\n🦜 Welcome to Friendly Parakeet Setup!\n")
    click.echo("Let's configure where to look for your coding projects.\n")

    cfg = Config(config)
    current_paths = cfg.get('watch_paths', [])

    click.echo("Current watch paths:")
    for path in current_paths:
        click.echo(f"  • {path}")

    click.echo("\n")
    if click.confirm("Would you like to modify watch paths?"):
        # Suggest common directories
        suggestions = [
            os.path.expanduser("~/coding"),
            os.path.expanduser("~/projects"),
            os.path.expanduser("~/dev"),
            os.path.expanduser("~/work"),
            os.path.expanduser("~/Documents/code"),
        ]

        existing_suggestions = [s for s in suggestions if os.path.exists(s)]

        if existing_suggestions:
            click.echo("\n📁 Found these directories on your system:")
            for path in existing_suggestions:
                click.echo(f"  • {path}")

            if click.confirm("\nAdd all found directories to watch paths?"):
                watch_paths = list(set(current_paths + existing_suggestions))
                cfg.set('watch_paths', watch_paths)
                click.echo(f"\n✅ Added {len(existing_suggestions)} directories")
            else:
                click.echo("\nAdd directories one by one? (enter blank to finish)")
                watch_paths = current_paths.copy()
                while True:
                    path = click.prompt("Path to add (or press Enter to finish)", default="", show_default=False)
                    if not path:
                        break
                    path = os.path.expanduser(path)
                    if os.path.exists(path):
                        watch_paths.append(path)
                        click.echo(f"  ✅ Added: {path}")
                    else:
                        click.echo(f"  ❌ Path does not exist: {path}")
                cfg.set('watch_paths', list(set(watch_paths)))
        else:
            click.echo("\nEnter paths to watch (one per line, blank to finish):")
            watch_paths = current_paths.copy()
            while True:
                path = click.prompt("Path", default="", show_default=False)
                if not path:
                    break
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    watch_paths.append(path)
                    click.echo(f"  ✅ Added: {path}")
                else:
                    click.echo(f"  ❌ Path does not exist: {path}")
            cfg.set('watch_paths', list(set(watch_paths)))

    # Configure scanning behavior
    click.echo("\n")
    if click.confirm("Would you like to configure scanning depth?"):
        recursive = click.confirm("Scan recursively into subdirectories?", default=True)
        cfg.set('scan_recursive', recursive)

        if recursive:
            max_depth = click.prompt(
                "Maximum depth for recursive scanning",
                type=int,
                default=3,
                show_default=True
            )
            cfg.set('scan_max_depth', max_depth)
            click.echo(f"\n✅ Will scan up to {max_depth} levels deep")
        else:
            click.echo("\n✅ Will scan immediate subdirectories only")

    # Summary
    final_paths = cfg.get('watch_paths', [])
    play_sound("happy")
    click.echo("\n" + "="*60)
    click.echo("🎉 Setup Complete!")
    click.echo("="*60)
    click.echo(f"\nWatching {len(final_paths)} directories:")
    for path in final_paths:
        click.echo(f"  • {path}")

    if cfg.get('scan_recursive', True):
        click.echo(f"\nRecursive scanning: {cfg.get('scan_max_depth', 3)} levels deep")
    else:
        click.echo("\nScanning: Immediate subdirectories only")

    click.echo("\nNext steps:")
    click.echo("  1. Run 'parakeet scan' to discover your projects")
    click.echo("  2. Run 'parakeet dashboard' to see your progress")
    click.echo("  3. Run 'parakeet menubar' to launch the Mac app")
    click.echo("\n")


@main.command()
@click.option('--config', '-c', help='Path to config file')
def menubar(config):
    """Launch the Mac menu bar app (macOS only)."""
    try:
        from .menubar_app import ParakeetMenuBarApp

        # Play hello sound when starting menubar app
        play_sound("hello")

        click.echo("\n🦜 Starting Friendly Parakeet Menu Bar App...")
        click.echo("Look for the parakeet icon in your menu bar!")
        click.echo("Press Ctrl+C to quit\n")

        app = ParakeetMenuBarApp()
        app.run()
    except ImportError as e:
        play_sound("alert")
        click.echo(f"❌ Menu bar app requires macOS dependencies: {e}")
        click.echo("Install with: pip install -r requirements-mac.txt")
    except Exception as e:
        play_sound("alert")
        click.echo(f"❌ Error starting menu bar app: {e}")


@main.command()
@click.argument('project_path', required=False)
@click.option('--config', '-c', help='Path to config file')
@click.option('--agent', '-a', help='Filter by agent name')
@click.option('--ide', '-i', help='Filter by IDE name')
@click.option('--limit', '-l', default=20, help='Number of commits to show')
def authorship(project_path, config, agent, ide, limit):
    """Show authorship metadata for commits."""
    parakeet = Parakeet(config)
    
    # If specific filters provided, use them
    if agent:
        commits = parakeet.authorship_tracker.query_by_agent(agent)
        click.echo(f"\n🤖 Commits by agent '{agent}':\n")
    elif ide:
        commits = parakeet.authorship_tracker.query_by_ide(ide)
        click.echo(f"\n💻 Commits using IDE '{ide}':\n")
    else:
        # Show all commits
        commits = parakeet.authorship_tracker.authorship_data.get('commits', [])
        click.echo(f"\n📝 Authorship Information:\n")
    
    if not commits:
        click.echo("No authorship data found. Run 'parakeet scan' to collect data.")
        return
    
    # Show limited number of commits
    for commit in commits[:limit]:
        sha = commit.get('sha', 'unknown')[:8]
        agent_name = commit.get('agent', 'unknown')
        ide_name = commit.get('ide', 'unknown')
        env = commit.get('environment', 'unknown')
        tools = ', '.join(commit.get('tools', [])[:3]) or 'none'
        skills = ', '.join(commit.get('skills', [])[:3]) or 'none'
        confidence = commit.get('confidence', 0.0)
        
        # Color code by agent
        agent_icon = {
            'claude': '🧠',
            'claude_code': '🧠',
            'github_copilot': '🤖',
            'cursor_ai': '✨',
            'windsurf_ai': '🌊',
            'chatgpt': '💬',
            'human': '👤',
        }.get(agent_name, '❓')
        
        click.echo(f"{agent_icon} {sha} | Agent: {agent_name} | IDE: {ide_name}")
        click.echo(f"  Environment: {env} | Confidence: {confidence:.0%}")
        click.echo(f"  Tools: {tools} | Skills: {skills}")
        click.echo()
    
    if len(commits) > limit:
        click.echo(f"... and {len(commits) - limit} more commits")
        click.echo(f"Use --limit to see more results")


@main.command()
@click.option('--config', '-c', help='Path to config file')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text')
def authorship_stats(config, format):
    """Show statistics about code authorship."""
    parakeet = Parakeet(config)
    
    stats = parakeet.authorship_tracker.get_statistics()
    
    if format == 'json':
        click.echo(json.dumps(stats, indent=2))
        return
    
    # Text format
    click.echo("\n📊 Authorship Statistics\n")
    click.echo("=" * 50)
    
    click.echo(f"\nTotal commits tracked: {stats['total_commits']}")
    
    if stats['by_agent']:
        click.echo("\n🤖 By Agent:")
        for agent, count in sorted(stats['by_agent'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_commits'] * 100) if stats['total_commits'] > 0 else 0
            bar = '█' * int(percentage / 5)
            click.echo(f"  {agent:20} {count:4} commits ({percentage:5.1f}%) {bar}")
    
    if stats['by_ide']:
        click.echo("\n💻 By IDE:")
        for ide, count in sorted(stats['by_ide'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_commits'] * 100) if stats['total_commits'] > 0 else 0
            bar = '█' * int(percentage / 5)
            click.echo(f"  {ide:20} {count:4} commits ({percentage:5.1f}%) {bar}")
    
    if stats['by_environment']:
        click.echo("\n🌍 By Environment:")
        for env, count in sorted(stats['by_environment'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_commits'] * 100) if stats['total_commits'] > 0 else 0
            click.echo(f"  {env:20} {count:4} commits ({percentage:5.1f}%)")
    
    if stats['top_tools']:
        click.echo("\n🔧 Top Tools:")
        for tool, count in sorted(stats['top_tools'].items(), key=lambda x: x[1], reverse=True)[:10]:
            click.echo(f"  {tool:20} {count:4} commits")
    
    if stats['top_skills']:
        click.echo("\n🎯 Top Skills/Languages:")
        for skill, count in sorted(stats['top_skills'].items(), key=lambda x: x[1], reverse=True)[:10]:
            click.echo(f"  {skill:20} {count:4} commits")
    
    click.echo()


@main.command()
@click.argument('project_path')
@click.option('--config', '-c', help='Path to config file')
def analyze_authorship(project_path, config):
    """Analyze authorship for a specific project."""
    parakeet = Parakeet(config)
    
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        click.echo(f"❌ Project path does not exist: {project_path}")
        return
    
    click.echo(f"\n🔍 Analyzing authorship for: {project_path.name}\n")
    
    # Detect current state
    agent = parakeet.authorship_tracker.detect_agent_from_environment()
    proc_agent = parakeet.authorship_tracker.detect_agent_from_processes()
    ide = parakeet.authorship_tracker.detect_ide()
    env = parakeet.authorship_tracker.detect_environment()
    tools = parakeet.authorship_tracker.detect_tools(project_path)
    skills = parakeet.authorship_tracker.detect_skills(project_path)
    orch = parakeet.authorship_tracker.detect_orchestration(project_path)
    
    click.echo("Current Detection:")
    click.echo(f"  Agent (env):       {agent}")
    click.echo(f"  Agent (process):   {proc_agent}")
    click.echo(f"  IDE:               {ide}")
    click.echo(f"  Environment:       {env}")
    click.echo(f"  Orchestration:     {orch}")
    click.echo(f"  Tools:             {', '.join(tools) if tools else 'none detected'}")
    click.echo(f"  Skills/Languages:  {', '.join(skills) if skills else 'none detected'}")
    
    # Analyze git commits if it's a git repo
    try:
        import git
        repo = git.Repo(project_path)
        
        click.echo(f"\n📚 Recent Commits (last 10):")
        
        for commit in list(repo.iter_commits(max_count=10)):
            sha = commit.hexsha[:8]
            message = commit.message.split('\n')[0][:50]
            agent = parakeet.authorship_tracker.detect_agent_from_commit_message(commit.message)
            
            agent_icon = {
                'claude': '🧠',
                'github_copilot': '🤖',
                'cursor_ai': '✨',
                'human': '👤',
            }.get(agent, '❓')
            
            click.echo(f"  {agent_icon} {sha} {agent:15} {message}")
    except Exception as e:
        click.echo(f"\n⚠️  Not a git repository or error reading commits")
    
    click.echo()


if __name__ == '__main__':
    main()
