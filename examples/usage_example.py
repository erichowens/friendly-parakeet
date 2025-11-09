#!/usr/bin/env python3
"""
Example usage of Friendly Parakeet.

This demonstrates how to use the Parakeet API programmatically.
"""

from parakeet.parakeet import Parakeet
from parakeet.config import Config

def main():
    # Initialize Parakeet with default config
    parakeet = Parakeet()
    
    # Scan and update projects
    print("Scanning projects...")
    projects = parakeet.scan_and_update()
    
    print(f"\nFound {len(projects)} projects:")
    for project in projects:
        print(f"  - {project['name']} ({project.get('type', 'unknown')})")
    
    # Get dashboard data
    print("\nDashboard data:")
    data = parakeet.get_dashboard_data()
    
    print(f"  Total projects: {data['stats']['total_projects']}")
    print(f"  Active projects: {data['stats']['active_projects']}")
    print(f"  Total breadcrumbs: {data['stats']['total_breadcrumbs']}")
    
    # Check for projects with breadcrumbs
    if data['breadcrumbs']:
        print("\nProjects with breadcrumbs:")
        for project_path, breadcrumbs in data['breadcrumbs'].items():
            print(f"  {project_path}: {len(breadcrumbs)} breadcrumb(s)")
            
            # Show latest breadcrumb prompts
            if breadcrumbs:
                latest = breadcrumbs[-1]
                print(f"    Latest prompts:")
                for i, prompt in enumerate(latest['prompt_suggestions'][:2], 1):
                    print(f"      {i}. {prompt}")
    
    # Get detailed info for a specific project
    if projects:
        project_path = projects[0]['path']
        details = parakeet.get_project_details(project_path)
        print(f"\nDetails for {details['name']}:")
        print(f"  Velocity trend: {details['velocity']['trend']}")
        print(f"  Active days: {details['velocity']['active_days']}")
        print(f"  Inactivity: {details['inactivity_days']} days")

if __name__ == '__main__':
    main()
