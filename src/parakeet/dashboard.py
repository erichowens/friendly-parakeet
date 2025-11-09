"""Web dashboard for Friendly Parakeet."""

from flask import Flask, render_template, jsonify
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
