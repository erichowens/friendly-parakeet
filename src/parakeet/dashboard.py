"""Web dashboard for Friendly Parakeet."""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pathlib import Path


def create_app(parakeet):
    """Create Flask application.
    
    Args:
        parakeet: Parakeet instance
        
    Returns:
        Flask application
    """
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Render main dashboard page."""
        data = parakeet.get_dashboard_data()
        return render_template('dashboard.html', **data)
    
    @app.route('/api/projects')
    def api_projects():
        """API endpoint for projects data."""
        data = parakeet.get_dashboard_data()
        return jsonify(data['projects'])
    
    @app.route('/api/breadcrumbs')
    def api_breadcrumbs():
        """API endpoint for breadcrumbs data."""
        data = parakeet.get_dashboard_data()
        return jsonify(data['breadcrumbs'])
    
    @app.route('/api/activity')
    def api_activity():
        """API endpoint for activity log."""
        data = parakeet.get_dashboard_data()
        return jsonify(data['activity_log'])
    
    @app.route('/api/project/<path:project_path>')
    def api_project_details(project_path):
        """API endpoint for detailed project information."""
        details = parakeet.get_project_details(project_path)
        return jsonify(details)
    
    @app.route('/api/scan', methods=['POST'])
    def api_scan():
        """API endpoint to trigger a scan."""
        projects = parakeet.scan_and_update()
        return jsonify({'status': 'success', 'projects_scanned': len(projects)})
    
    @app.route('/api/maintenance/<path:project_path>', methods=['POST'])
    def api_maintenance(project_path):
        """API endpoint to trigger git maintenance."""
        result = parakeet.git_maintainer.perform_maintenance(project_path)
        return jsonify(result)
    
    @app.route('/api/auto_commit/<path:project_path>', methods=['POST'])
    def api_auto_commit(project_path):
        """API endpoint to toggle auto-commit."""
        data = request.json
        enabled = data.get('enabled', True)
        parakeet.git_maintainer.set_auto_commit(project_path, enabled)
        return jsonify({'status': 'success', 'enabled': enabled})
    
    @app.route('/api/auto_push/<path:project_path>', methods=['POST'])
    def api_auto_push(project_path):
        """API endpoint to toggle auto-push."""
        data = request.json
        enabled = data.get('enabled', True)
        parakeet.git_maintainer.set_auto_push(project_path, enabled)
        return jsonify({'status': 'success', 'enabled': enabled})
    
    @app.route('/api/maintenance_status/<path:project_path>')
    def api_maintenance_status(project_path):
        """API endpoint to get maintenance status."""
        return jsonify({
            'auto_commit': parakeet.git_maintainer.is_auto_commit_enabled(project_path),
            'auto_push': parakeet.git_maintainer.is_auto_push_enabled(project_path),
        })
    
    @app.route('/api/changelog/<path:project_path>')
    def api_changelog(project_path):
        """API endpoint to get changelog."""
        md = parakeet.changelog.generate_changelog_markdown(project_path)
        return jsonify({'markdown': md})
    
    @app.route('/api/time_report/<path:project_path>')
    def api_time_report(project_path):
        """API endpoint to get time report."""
        md = parakeet.changelog.generate_time_report(project_path)
        return jsonify({'markdown': md})
    
    @app.template_filter('timeago')
    def timeago_filter(timestamp_str):
        """Convert timestamp to relative time."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            delta = datetime.now() - timestamp
            
            if delta.days > 365:
                return f"{delta.days // 365} year(s) ago"
            elif delta.days > 30:
                return f"{delta.days // 30} month(s) ago"
            elif delta.days > 0:
                return f"{delta.days} day(s) ago"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hour(s) ago"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60} minute(s) ago"
            else:
                return "just now"
        except:
            return timestamp_str
    
    return app
