"""Brilliant Budgies - AI-powered coding assistant that generates helpful ideas."""

import json
import random
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import git
import ast
import re


class BrilliantBudgies:
    """Generates helpful coding ideas and improvements during off-hours."""

    def __init__(self, parakeet):
        """Initialize Brilliant Budgies.

        Args:
            parakeet: Main Parakeet instance for accessing project data
        """
        self.parakeet = parakeet
        self.ideas_file = parakeet.config.data_dir / 'brilliant_budgies.json'
        self.ideas = self._load_ideas()

        # Idea templates for different project improvements
        self.idea_templates = {
            'unit_tests': {
                'title_formats': [
                    "Add unit tests for {module}",
                    "Improve test coverage for {feature}",
                    "Create integration tests for {component}"
                ],
                'descriptions': [
                    "I noticed {module} has no tests. Adding unit tests would prevent regressions and improve confidence in deployments.",
                    "The {feature} functionality could benefit from comprehensive test coverage, including edge cases and error handling.",
                    "Integration tests between {component} and its dependencies would catch interface issues early."
                ]
            },
            'refactoring': {
                'title_formats': [
                    "Refactor {file} to improve readability",
                    "Extract {concept} into a reusable module",
                    "Simplify {function} logic"
                ],
                'descriptions': [
                    "The {file} has grown complex. Breaking it into smaller, focused functions would improve maintainability.",
                    "The {concept} pattern appears in multiple places. Extracting it would follow DRY principles.",
                    "The {function} has nested conditionals that could be simplified using early returns or helper functions."
                ]
            },
            'performance': {
                'title_formats': [
                    "Optimize {operation} performance",
                    "Add caching for {resource}",
                    "Implement lazy loading for {component}"
                ],
                'descriptions': [
                    "The {operation} could be optimized using more efficient algorithms or data structures.",
                    "Caching {resource} would reduce redundant computations and improve response times.",
                    "Lazy loading {component} would improve initial load times and resource usage."
                ]
            },
            'documentation': {
                'title_formats': [
                    "Document {module} API",
                    "Add examples for {feature}",
                    "Create architecture diagram for {system}"
                ],
                'descriptions': [
                    "Adding comprehensive documentation for {module} would help new developers understand its purpose and usage.",
                    "Real-world examples for {feature} would make it easier for users to get started.",
                    "A visual architecture diagram of {system} would clarify component relationships and data flow."
                ]
            },
            'tooling': {
                'title_formats': [
                    "Add {tool} for better developer experience",
                    "Create {script} to automate {task}",
                    "Implement {workflow} for efficiency"
                ],
                'descriptions': [
                    "Adding {tool} would streamline the development process and reduce manual work.",
                    "A {script} could automate the repetitive {task}, saving time and reducing errors.",
                    "Implementing {workflow} would improve team collaboration and code quality."
                ]
            },
            'error_handling': {
                'title_formats': [
                    "Improve error handling in {module}",
                    "Add validation for {input}",
                    "Implement retry logic for {operation}"
                ],
                'descriptions': [
                    "Better error handling in {module} would provide clearer messages and graceful degradation.",
                    "Validating {input} would prevent downstream issues and improve security.",
                    "Adding retry logic for {operation} would improve resilience against transient failures."
                ]
            },
            'monitoring': {
                'title_formats': [
                    "Add logging for {component}",
                    "Implement metrics for {feature}",
                    "Create health checks for {service}"
                ],
                'descriptions': [
                    "Strategic logging in {component} would aid debugging and monitoring in production.",
                    "Tracking metrics for {feature} would provide insights into usage patterns and performance.",
                    "Health checks for {service} would enable proactive issue detection and automated recovery."
                ]
            }
        }

    def _load_ideas(self) -> List[Dict[str, Any]]:
        """Load saved Brilliant Budgie ideas.

        Returns:
            List of saved ideas
        """
        if self.ideas_file.exists():
            with open(self.ideas_file, 'r') as f:
                return json.load(f)
        return []

    def _save_ideas(self):
        """Save Brilliant Budgie ideas to file."""
        with open(self.ideas_file, 'w') as f:
            json.dump(self.ideas, f, indent=2)

    def generate_ideas(self) -> List[Dict[str, Any]]:
        """Generate new Brilliant Budgie ideas based on project analysis.

        Returns:
            List of newly generated ideas
        """
        new_ideas = []

        # Get all tracked projects
        projects = self.parakeet.scanner.scan_projects()

        for project in projects:
            # Analyze project and generate relevant ideas
            project_ideas = self._analyze_and_generate_ideas(project)
            new_ideas.extend(project_ideas)

        # Save new ideas
        for idea in new_ideas:
            idea['id'] = self._generate_idea_id(idea)
            idea['timestamp'] = datetime.now().isoformat()
            idea['status'] = 'pending'
            self.ideas.append(idea)

        self._save_ideas()
        return new_ideas

    def _analyze_and_generate_ideas(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a project and generate relevant improvement ideas.

        Args:
            project: Project information

        Returns:
            List of generated ideas for this project
        """
        ideas = []
        project_path = Path(project['path'])

        # Analyze project structure
        analysis = self._analyze_project_structure(project_path)

        # Generate ideas based on analysis
        if analysis['missing_tests']:
            ideas.append(self._generate_test_idea(project, analysis))

        if analysis['complex_files']:
            ideas.append(self._generate_refactoring_idea(project, analysis))

        if analysis['missing_docs']:
            ideas.append(self._generate_documentation_idea(project, analysis))

        if analysis['performance_opportunities']:
            ideas.append(self._generate_performance_idea(project, analysis))

        # Random creative idea (10% chance)
        if random.random() < 0.1:
            ideas.append(self._generate_creative_idea(project))

        return [idea for idea in ideas if idea]  # Filter out None values

    def _analyze_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure for improvement opportunities.

        Args:
            project_path: Path to project

        Returns:
            Analysis results
        """
        analysis = {
            'missing_tests': [],
            'complex_files': [],
            'missing_docs': [],
            'performance_opportunities': [],
            'file_stats': {}
        }

        # Check for test coverage
        src_files = list(project_path.glob('**/*.py'))
        test_files = list(project_path.glob('**/test_*.py')) + list(project_path.glob('**/*_test.py'))

        for src_file in src_files:
            # Skip test files and __pycache__
            if 'test' in src_file.name or '__pycache__' in str(src_file):
                continue

            # Check if corresponding test exists
            test_name = f"test_{src_file.stem}.py"
            has_test = any(test_name in str(t) for t in test_files)

            if not has_test:
                analysis['missing_tests'].append(src_file)

            # Check file complexity
            try:
                content = src_file.read_text()
                lines = content.splitlines()

                # Simple complexity heuristics
                if len(lines) > 300:
                    analysis['complex_files'].append(src_file)

                # Check for docstrings
                if '"""' not in content[:200] and "'''" not in content[:200]:
                    analysis['missing_docs'].append(src_file)

                # Look for performance patterns
                if 'for' in content and 'for' in content[content.index('for')+3:]:
                    # Nested loops
                    analysis['performance_opportunities'].append(src_file)

            except Exception:
                pass

        return analysis

    def _generate_test_idea(self, project: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate unit test idea.

        Args:
            project: Project information
            analysis: Project analysis results

        Returns:
            Generated idea or None
        """
        if not analysis['missing_tests']:
            return None

        # Pick a file that needs tests
        target_file = random.choice(analysis['missing_tests'])
        module_name = target_file.stem

        template = self.idea_templates['unit_tests']
        title = random.choice(template['title_formats']).format(module=module_name)
        description = random.choice(template['descriptions']).format(
            module=module_name,
            feature=module_name,
            component=module_name
        )

        return {
            'project_path': project['path'],
            'project_name': project['name'],
            'type': 'unit_tests',
            'title': title,
            'description': description,
            'target_file': str(target_file),
            'priority': 'high' if len(analysis['missing_tests']) > 5 else 'medium',
            'estimated_time': '2-4 hours',
            'implementation_hints': [
                f"Create test file: test_{module_name}.py",
                "Test main functions and edge cases",
                "Aim for >80% code coverage",
                "Use pytest or unittest framework"
            ]
        }

    def _generate_refactoring_idea(self, project: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate refactoring idea.

        Args:
            project: Project information
            analysis: Project analysis results

        Returns:
            Generated idea or None
        """
        if not analysis['complex_files']:
            return None

        target_file = random.choice(analysis['complex_files'])
        file_name = target_file.name

        template = self.idea_templates['refactoring']
        title = random.choice(template['title_formats']).format(
            file=file_name,
            concept="common logic",
            function="main processing"
        )
        description = random.choice(template['descriptions']).format(
            file=file_name,
            concept="repeated patterns",
            function="core logic"
        )

        return {
            'project_path': project['path'],
            'project_name': project['name'],
            'type': 'refactoring',
            'title': title,
            'description': description,
            'target_file': str(target_file),
            'priority': 'medium',
            'estimated_time': '1-3 hours',
            'implementation_hints': [
                "Break large functions into smaller ones",
                "Extract common patterns into utilities",
                "Improve naming for clarity",
                "Consider design patterns where appropriate"
            ]
        }

    def _generate_documentation_idea(self, project: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate documentation idea.

        Args:
            project: Project information
            analysis: Project analysis results

        Returns:
            Generated idea or None
        """
        if not analysis['missing_docs']:
            return None

        target_file = random.choice(analysis['missing_docs'])
        module_name = target_file.stem

        template = self.idea_templates['documentation']
        title = random.choice(template['title_formats']).format(
            module=module_name,
            feature=module_name,
            system=project['name']
        )
        description = random.choice(template['descriptions']).format(
            module=module_name,
            feature=module_name,
            system=project['name']
        )

        return {
            'project_path': project['path'],
            'project_name': project['name'],
            'type': 'documentation',
            'title': title,
            'description': description,
            'target_file': str(target_file),
            'priority': 'low',
            'estimated_time': '30-60 minutes',
            'implementation_hints': [
                "Add module-level docstring",
                "Document all public functions",
                "Include usage examples",
                "Explain complex logic with comments"
            ]
        }

    def _generate_performance_idea(self, project: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate performance improvement idea.

        Args:
            project: Project information
            analysis: Project analysis results

        Returns:
            Generated idea or None
        """
        if not analysis['performance_opportunities']:
            return None

        target_file = random.choice(analysis['performance_opportunities'])

        template = self.idea_templates['performance']
        title = random.choice(template['title_formats']).format(
            operation="data processing",
            resource="computed values",
            component=target_file.stem
        )
        description = random.choice(template['descriptions']).format(
            operation="loop operations",
            resource="frequently accessed data",
            component=target_file.stem
        )

        return {
            'project_path': project['path'],
            'project_name': project['name'],
            'type': 'performance',
            'title': title,
            'description': description,
            'target_file': str(target_file),
            'priority': 'medium',
            'estimated_time': '2-4 hours',
            'implementation_hints': [
                "Profile code to identify bottlenecks",
                "Consider caching repeated calculations",
                "Use more efficient data structures",
                "Optimize database queries if applicable"
            ]
        }

    def _generate_creative_idea(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a creative/innovative idea for the project.

        Args:
            project: Project information

        Returns:
            Generated creative idea
        """
        creative_ideas = [
            {
                'title': f"Add CLI tool for {project['name']}",
                'description': "Create a command-line interface to make common tasks easier for developers and users.",
                'hints': ["Use Click or argparse", "Add helpful commands", "Include --help documentation"]
            },
            {
                'title': f"Create Docker setup for {project['name']}",
                'description': "Containerize the application for easier deployment and consistent environments.",
                'hints': ["Create Dockerfile", "Add docker-compose.yml", "Document container usage"]
            },
            {
                'title': f"Add GitHub Actions CI/CD for {project['name']}",
                'description': "Automate testing and deployment with GitHub Actions workflows.",
                'hints': ["Create .github/workflows/", "Add test runner", "Consider deployment automation"]
            },
            {
                'title': f"Implement feature flags in {project['name']}",
                'description': "Add feature flag system for safer deployments and A/B testing.",
                'hints': ["Use environment variables", "Create toggle system", "Document flag usage"]
            },
            {
                'title': f"Add telemetry to {project['name']}",
                'description': "Implement anonymous usage tracking to understand how the tool is used.",
                'hints': ["Respect user privacy", "Make it opt-in", "Track only essential metrics"]
            }
        ]

        idea = random.choice(creative_ideas)

        return {
            'project_path': project['path'],
            'project_name': project['name'],
            'type': 'creative',
            'title': idea['title'],
            'description': idea['description'],
            'priority': 'low',
            'estimated_time': '4-8 hours',
            'implementation_hints': idea['hints']
        }

    def _generate_idea_id(self, idea: Dict[str, Any]) -> str:
        """Generate unique ID for an idea.

        Args:
            idea: Idea data

        Returns:
            Unique ID string
        """
        content = f"{idea['project_path']}{idea['title']}{idea['type']}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def get_recent_ideas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent Brilliant Budgie ideas.

        Args:
            limit: Maximum number of ideas to return

        Returns:
            List of recent ideas
        """
        # Sort by timestamp and return most recent
        sorted_ideas = sorted(self.ideas, key=lambda x: x['timestamp'], reverse=True)
        return sorted_ideas[:limit]

    def create_implementation_task(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Create an implementation task from a Brilliant Budgie idea.

        Args:
            idea: Idea to implement

        Returns:
            Task information
        """
        # Create a breadcrumb-like task for the idea
        task = {
            'id': idea['id'],
            'type': 'brilliant_budgie',
            'timestamp': datetime.now().isoformat(),
            'project_path': idea['project_path'],
            'title': idea['title'],
            'description': idea['description'],
            'implementation_hints': idea.get('implementation_hints', []),
            'estimated_time': idea.get('estimated_time', 'Unknown'),
            'priority': idea.get('priority', 'medium'),
            'status': 'assigned'
        }

        # Update idea status
        for saved_idea in self.ideas:
            if saved_idea['id'] == idea['id']:
                saved_idea['status'] = 'assigned'
                saved_idea['assigned_at'] = datetime.now().isoformat()
                break

        self._save_ideas()

        # Create implementation prompt
        prompt = self._create_implementation_prompt(task)
        task['prompt'] = prompt

        # Save to project breadcrumbs for easy access
        self.parakeet.breadcrumbs.add_breadcrumb(
            idea['project_path'],
            {
                'timestamp': datetime.now().isoformat(),
                'type': 'brilliant_budgie',
                'inactivity_days': 0,
                'project_name': idea['project_name'],
                'prompt_suggestions': [prompt],
                'status': 'brilliant_budgie'
            }
        )

        return task

    def _create_implementation_prompt(self, task: Dict[str, Any]) -> str:
        """Create an implementation prompt for AI coding assistants.

        Args:
            task: Task information

        Returns:
            Implementation prompt
        """
        hints = '\n'.join(f"- {hint}" for hint in task.get('implementation_hints', []))

        prompt = f"""
🦜💡 BRILLIANT BUDGIE TASK: {task['title']}

Your parakeet has been thinking and has a suggestion for improving the project!

Description: {task['description']}

Estimated Time: {task['estimated_time']}
Priority: {task['priority']}

Implementation Hints:
{hints}

Please implement this improvement following best practices and the existing code style.
"""
        return prompt.strip()