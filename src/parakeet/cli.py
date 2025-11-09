"""Command-line interface for Friendly Parakeet."""

import click
import json
from pathlib import Path

from .parakeet import Parakeet
from .dashboard import create_app


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


if __name__ == '__main__':
    main()
