---
applyTo: "tests/**/*.py"
---

# Testing Guidelines for Friendly Parakeet

## Test Organization

### File Structure
- Mirror the src/parakeet structure in tests/
- Name test files as test_<module>.py
- Group related tests in classes when appropriate

### Test Naming
- Use descriptive test function names: test_<feature>_<scenario>
- Example: test_scanner_initialization_with_valid_paths
- Example: test_git_maintainer_handles_auto_commit

## Test Patterns

### Fixtures
- Use pytest fixtures for common setup and teardown
- Create temporary directories for file system tests
- Mock git repositories for git operation tests
- Clean up resources in fixtures

### Mocking
- Mock external dependencies (file system, git, network)
- Use pytest-mock or unittest.mock
- Don't mock internal component interfaces unless necessary
- Verify mock calls when testing integration points

### Assertions
- Use pytest-style assertions (assert ==, assert in, etc.)
- Provide clear assertion messages
- Test both success and failure cases
- Verify error messages when appropriate

## Test Coverage

### Unit Tests
- Test individual functions and methods in isolation
- Cover edge cases and boundary conditions
- Test error handling and validation

### Integration Tests
- Test component interactions
- Verify data flow between components
- Test CLI commands end-to-end
- Test dashboard endpoints

### Test Data
- Use realistic but minimal test data
- Create test fixtures for common scenarios
- Avoid hardcoded paths; use temporary directories
- Clean up test data after tests complete

## What to Test

### Critical Functionality
- Project detection and scanning
- Git operations (commit, push, status)
- Configuration management
- Data persistence (JSON, YAML)
- CLI command execution
- Dashboard routes and API endpoints

### Edge Cases
- Empty directories
- Missing configuration files
- Invalid git repositories
- Network failures (for push operations)
- File permission errors
- Malformed JSON/YAML data

## Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scanner.py

# Run with coverage
pytest --cov=parakeet

# Run with verbose output
pytest -v
```

## Continuous Integration

- All tests should pass before merging
- New features should include tests
- Bug fixes should include regression tests
- Maintain or improve code coverage
