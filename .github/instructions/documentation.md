---
applyTo: "**/*.md"
excludeAgent: "coding-agent"
---

# Documentation Guidelines

## Writing Style

- Use clear, concise language
- Write for developers who are new to the project
- Include code examples where helpful
- Keep examples up-to-date with current API

## Documentation Structure

### README.md
- High-level project overview
- Quick start guide
- Installation instructions
- Common use cases
- Link to detailed documentation

### Technical Documentation
- Architecture overview in CLAUDE.md
- Deployment guides (DISTRIBUTION_GUIDE.md, MAC_APP_README.md)
- Feature-specific documentation (SUBSCRIPTION_GUIDE.md, etc.)

### Code Comments
- Document why, not what
- Explain complex algorithms or business logic
- Keep comments up-to-date with code changes
- Use docstrings for public APIs

## Formatting

### Markdown Conventions
- Use ATX-style headers (# Header)
- Use backticks for inline code
- Use triple backticks for code blocks with language identifier
- Use bullet points for lists
- Use numbered lists for sequential steps

### Code Examples
```bash
# Include comments in examples
parakeet scan  # Scan for projects
```

```python
# Show realistic usage
from parakeet import Parakeet

parakeet = Parakeet()
parakeet.scan()
```

### Links
- Use relative links for internal documentation
- Use descriptive link text
- Verify links are not broken

## Content Guidelines

### Installation Instructions
- Include all prerequisites
- Provide step-by-step commands
- Cover different platforms when relevant
- Include troubleshooting tips

### Configuration
- Document all configuration options
- Show default values
- Explain impact of each setting
- Provide configuration examples

### API Documentation
- Document all public functions and classes
- Include parameter types and descriptions
- Show return values
- Provide usage examples

### Changelog
- Keep CHANGELOG.md up-to-date
- Use semantic versioning
- Group changes by type (Added, Changed, Fixed, etc.)
- Include issue/PR references

## Maintenance

- Review documentation with each code change
- Update examples when API changes
- Remove outdated information
- Keep version numbers current
