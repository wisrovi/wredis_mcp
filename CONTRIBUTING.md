# Contributing to wredis-mcp

Thank you for your interest in contributing to wredis-mcp!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/wredis_mcp.git
   cd wredis_mcp
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wredis_mcp --cov-report=html
```

### Code Quality

```bash
# Lint with ruff
ruff check src/wredis_mcp/

# Type checking with mypy
mypy src/wredis_mcp/

# Format code with black
black src/wredis_mcp/
```

### Running All Quality Checks

```bash
ruff check src/wredis_mcp/ && mypy src/wredis_mcp/ && pytest
```

## Project Structure

```
wredis_mcp/
├── src/wredis_mcp/
│   ├── server.py       # MCP server, tools and CLI
│   ├── catalog.py      # Pattern catalog synchronization
│   └── templates.py    # Professional boilerplate definitions
├── examples/           # Sample implementations
└── .github/            # CI/CD workflows
```

## Writing Tests

- All new features should include tests
- Use descriptive test names: `test_<feature>_<behavior>`

## Pull Request Guidelines

1. Ensure all tests pass
2. Run linting: `ruff check src/wredis_mcp/`
3. Run type checking: `mypy src/wredis_mcp/`
4. Update documentation if needed
5. Keep changes focused and atomic

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to public functions
- Keep functions small and focused

## Reporting Issues

- Use the GitHub issue tracker
- Include a minimal reproducible example
- Specify your Python version and OS
