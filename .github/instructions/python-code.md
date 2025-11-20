---
applyTo: "src/parakeet/**/*.py"
---

# Python Code Guidelines for Parakeet

## Code Structure

### Module Organization
- Each major feature is encapsulated in its own module
- Follow the orchestrator pattern: `Parakeet` class coordinates component managers
- Component managers: scanner, tracker, breadcrumbs, git_maintainer, changelog

### Error Handling
- Use appropriate exception handling for file I/O operations
- GitPython operations should handle repository errors gracefully
- Provide helpful error messages to users

### State Management
- All state persists to `~/.parakeet/` directory
- Use JSON for data files (project_history.json, breadcrumbs.json)
- Use YAML for configuration (config.yaml)
- Ensure atomic writes to prevent data corruption

## Key Implementation Patterns

### Git Operations
- Always use GitPython library, never shell out to git commands
- Handle both local and remote operations
- Check repository state before operations
- Provide clear feedback on git operations

### CLI Commands
- Use Click for all CLI commands
- Provide helpful help text and examples
- Use consistent parameter naming
- Validate user input before processing

### File System Operations
- Use Path objects from pathlib when possible
- Handle missing directories gracefully
- Respect exclude patterns in configuration
- Check file existence before operations

### Dashboard/API
- Flask endpoints should return JSON for API calls
- Template-based rendering with Jinja2
- Keep business logic in component managers, not in routes
- Provide clear API responses with status codes

## Testing Guidelines

- Write unit tests for new functionality
- Use pytest fixtures for common setup
- Mock file system and git operations when appropriate
- Test edge cases and error conditions

## Dependencies

When adding new dependencies:
- Check if existing dependencies can handle the requirement
- Prefer well-maintained, widely-used packages
- Update requirements.txt and setup.py
- Document new dependencies in docstrings

## Common Pitfalls to Avoid

- Don't modify user's git repositories without explicit permission/configuration
- Don't assume directories exist; create them if needed
- Don't hardcode paths; use configuration
- Don't block on long-running operations; provide feedback
- Don't ignore git errors; handle them appropriately

## Performance Considerations

- Scanner should efficiently handle large directory trees
- Avoid repeated file system scans; cache when appropriate
- Git operations can be slow; show progress when needed
- Dashboard should load quickly; minimize blocking operations
