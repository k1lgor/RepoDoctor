# Contributing to RepoDoctor

Thank you for your interest in contributing to RepoDoctor! This document provides guidelines and instructions for contributing to the project.

## 🌟 Ways to Contribute

- 🐛 **Report Bugs** - Found a bug? Open an issue with details
- 💡 **Suggest Features** - Have an idea? We'd love to hear it
- 📝 **Improve Documentation** - Help make the docs clearer
- 🔧 **Submit Code** - Fix bugs or implement features
- 📋 **Add Prompts** - Create new prompt templates for analysis types
- 🧪 **Write Tests** - Improve test coverage

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** - Required for development
- **uv** - Recommended package manager ([install](https://github.com/astral-sh/uv))
- **GitHub Copilot CLI** - Required for testing
- **Git** - For version control

### Development Setup

1. **Fork and Clone**

   ```bash
   # Fork the repository on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/RepoDoctor.git
   cd RepoDoctor
   ```

2. **Install Dependencies**

   ```bash
   # Using uv (recommended)
   uv pip install -e ".[dev]"

   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Verify Installation**

   ```bash
   # Run tests
   uv run pytest

   # Check types
   uv run pyright src/

   # Lint code
   uv run ruff check src/
   ```

## 📁 Project Structure

Understanding the codebase:

```
repodoc/
├── src/repodoc/
│   ├── cli.py                    # Main CLI entry point
│   ├── __init__.py               # Package initialization
│   │
│   ├── commands/                 # Command implementations
│   │   ├── base.py               # Shared utilities
│   │   ├── diet.py               # Diet command
│   │   ├── tour.py               # Tour command
│   │   ├── docker.py             # Docker command
│   │   ├── deadcode.py           # Dead code command
│   │   ├── scan.py               # Scan orchestrator
│   │   └── report.py             # Report generator
│   │
│   ├── core/                     # Core functionality
│   │   ├── copilot.py            # Copilot CLI invocation
│   │   ├── parser.py             # JSON parsing & validation
│   │   ├── logger.py             # Logging utilities
│   │   └── exceptions.py         # Custom exceptions
│   │
│   ├── prompts/                  # Prompt templates
│   │   ├── __init__.py           # Prompt loader
│   │   ├── templates.py          # Template management
│   │   └── v1/                   # Version 1 prompts
│   │       ├── diet.md
│   │       ├── tour.md
│   │       ├── docker.md
│   │       ├── deadcode.md
│   │       ├── scan.md
│   │       └── report.md
│   │
│   ├── renderers/                # Output formatting
│   │   ├── base.py               # Base renderer
│   │   ├── json_renderer.py      # JSON output
│   │   ├── terminal_renderer.py  # Rich terminal output
│   │   └── command_renderers.py  # Command-specific renderers
│   │
│   └── schemas/                  # Pydantic data models
│       ├── base.py               # Base schemas
│       ├── diet.py               # Diet output schema
│       ├── tour.py               # Tour output schema
│       ├── docker.py             # Docker output schema
│       ├── deadcode.py           # Deadcode output schema
│       ├── scan.py               # Scan result schema
│       └── report.py             # Report schema
│
├── tests/                        # Test suite
│   ├── conftest.py               # Shared fixtures
│   ├── test_copilot.py           # Copilot invoker tests
│   ├── test_parser.py            # Parser tests
│   ├── test_exceptions.py        # Exception tests
│   ├── test_schemas.py           # Schema validation tests
│   ├── test_prompts.py           # Prompt loader tests
│   └── test_*_command.py         # Command integration tests
│
├── docs/                         # Additional documentation
├── pyproject.toml                # Project configuration
├── pytest.ini                    # Test configuration
└── README.md                     # Main documentation
```

## 🔧 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Follow the code style guidelines (see below).

### 3. Write Tests

All new features and bug fixes should include tests:

```bash
# Add tests to appropriate test file
# Run tests to ensure they pass
uv run pytest

# Check coverage
uv run pytest --cov=repodoc
```

### 4. Run Quality Checks

Before committing, ensure code quality:

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run pyright src/

# Run all tests
uv run pytest
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new analysis module for dependencies"
# or
git commit -m "fix: handle empty repository gracefully"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting)
- `chore:` - Build/tooling changes

### 6. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues
- Screenshots for UI changes (terminal output)

## 📝 Code Style Guidelines

### Python Code Style

We use **ruff** for formatting and linting, **pyright** for type checking.

**Key Principles:**
- **Type hints everywhere** - All functions should have type annotations
- **Docstrings for public APIs** - Use Google-style docstrings
- **Line length: 100 characters** - Configured in pyproject.toml
- **No bare `except:`** - Always catch specific exceptions
- **Use Pydantic** - For all data validation

**Example:**

```python
def parse_output(raw: str, schema: type[BaseModel]) -> BaseModel:
    """
    Parse and validate Copilot CLI output.

    Args:
        raw: Raw output string from Copilot CLI
        schema: Pydantic model class to validate against

    Returns:
        Validated model instance

    Raises:
        OutputParseError: If JSON cannot be extracted
        SchemaValidationError: If validation fails
    """
    try:
        data = json.loads(raw)
        return schema.model_validate(data)
    except json.JSONDecodeError as e:
        raise OutputParseError(f"Invalid JSON: {e}", raw)
```

### Testing Guidelines

- **Use pytest** - All tests use pytest framework
- **Mock Copilot CLI** - Never call real Copilot in tests
- **Test edge cases** - Empty inputs, errors, timeouts
- **Use fixtures** - Defined in `conftest.py`
- **Mark tests** - Use `@pytest.mark.unit` or `@pytest.mark.integration`

**Example:**

```python
@pytest.mark.unit
def test_parse_valid_json(sample_response: dict) -> None:
    """Test parser handles valid JSON correctly."""
    parser = OutputParser()
    result = parser.parse_json(json.dumps(sample_response))
    assert result == sample_response
```

## 📋 Adding New Prompt Templates

Prompt templates are the heart of RepoDoctor. Here's how to add a new one:

### 1. Create the Template File

Add a new Markdown file to `src/repodoc/prompts/v1/`:

```markdown
# Your Analysis Name

Analyze the repository for [specific aspect].

## Output Format

Return your analysis as a JSON object with the following structure:

\`\`\`json
{
  "command": "yourcommand",
  "success": true,
  "analysis": {
    // Your specific fields
  },
  "issues": [
    {
      "title": "Issue title",
      "description": "Detailed description",
      "severity": "high|medium|low",
      "category": "category_name",
      "suggestion": "How to fix"
    }
  ],
  "recommendations": [
    {
      "action": "What to do",
      "reason": "Why it matters",
      "priority": "high|medium|low"
    }
  ]
}
\`\`\`

## Analysis Focus

- Specific aspect 1
- Specific aspect 2
- Consider context and tech stack
```

**Important Notes:**
- Use `{{variable}}` syntax in prompt templates for dynamic content substitution
- Always include `timeout` parameter (optional, no default) for flexibility
- Use `except typer.Exit: raise` to avoid re-handling clean exits
- All errors only go to `.repodoc/logs/` - console stays clean

### 2. Create the Schema

Add a new schema file to `src/repodoc/schemas/`:

```python
from pydantic import BaseModel, Field
from repodoc.schemas.base import BaseCommandOutput

class YourAnalysis(BaseModel):
    """Analysis-specific results."""
    field1: str = Field(..., description="...")
    field2: list[str] = Field(default_factory=list, description="...")

class YourOutput(BaseCommandOutput):
    """Output schema for 'repodoc yourcommand' command."""
    command: str = Field(default="yourcommand")
    analysis: YourAnalysis = Field(..., description="Analysis results")
```

### 3. Implement the Command

Add a new command file to `src/repodoc/commands/`:

```python
def yourcommand(
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    json_output: Annotated[bool, typer.Option("--json")] = False,
    out: Annotated[str | None, typer.Option("--out", "-o")] = None,
    timeout: Annotated[int | None, typer.Option("--timeout")] = None,
) -> None:
    """Your command description."""
    try:
        repo_root = get_repo_root()

        # Load prompt (use {{variable}} syntax for placeholders)
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt(
            "yourcommand",
            repo_path=str(repo_root),
            # Optional: Pass variables for template substitution
            # variable_name="value"  # becomes {{variable_name}} in template
        )

        # Invoke Copilot (timeout is optional)
        copilot = CopilotInvoker(timeout=timeout)
        with console.status("[bold blue]Analyzing...[/bold blue]"):
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, YourOutput)

        # Handle output
        if json_output or out:
            handle_json_flag(result.model_dump(), json_output, out)
            if json_output:
                return

        # Render terminal output (implement renderer)
        # ... render logic ...

    except typer.Exit:
        raise  # Let typer handle clean exits
    except Exception as e:
        handle_command_error(e, verbose)
```

### 4. Register the Command

Add to `src/repodoc/cli.py`:

```python
from repodoc.commands import yourcommand

app.command(name="yourcommand")(yourcommand)
```

### 5. Add Tests

Create `tests/test_yourcommand.py` with unit and integration tests.

### 6. Update Documentation

Add command documentation to README.md.

## 🧪 Testing Strategy

### Test Categories

**Unit Tests** (`@pytest.mark.unit`):
- Test individual functions/classes in isolation
- Mock all external dependencies (Copilot CLI, file system)
- Fast execution (< 1 second each)

**Integration Tests** (`@pytest.mark.integration`):
- Test command workflows end-to-end
- Mock only Copilot CLI, use real file system
- Test multiple components working together

### Running Specific Tests

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run tests for specific module
uv run pytest tests/test_copilot.py

# Run with coverage
uv run pytest --cov=repodoc --cov-report=html

# Run verbosely
uv run pytest -vv
```

### Coverage Goals

- **Core modules**: 90%+ coverage
- **Commands**: 80%+ coverage
- **Overall**: 70%+ coverage

## 🐛 Debugging

### Enable Verbose Logging

```bash
repodoc scan --verbose
```

### Check Raw Outputs

Copilot CLI outputs are saved in `.repodoc/logs/`:

```bash
# View latest output
ls -lt .repodoc/logs/ | head
cat .repodoc/logs/output_copilot_output_*.txt
```

### Run with Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use VS Code debugger
```

## 📚 Documentation Standards

### Docstring Format

Use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """
    Brief description of function.

    More detailed explanation if needed. Can span multiple lines
    and include examples.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When this specific error occurs
        RuntimeError: When that specific error occurs

    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### README Updates

When adding features, update:
- Features list
- Command reference
- Examples
- Troubleshooting (if applicable)

## 🚦 Pull Request Process

1. **Ensure all checks pass**
   - Tests pass (`pytest`)
   - Type checking passes (`pyright`)
   - Linting passes (`ruff`)

2. **Update documentation**
   - README.md for user-facing changes
   - Docstrings for code changes
   - CHANGELOG.md (if exists)

3. **Write clear PR description**
   - What problem does it solve?
   - How does it solve it?
   - Any breaking changes?
   - Screenshots for UI changes

4. **Request review**
   - Tag relevant maintainers
   - Respond to feedback promptly

5. **Squash commits** (if needed)
   - Keep history clean
   - One logical change per commit

## 🏷️ Release Process

Maintainers follow this process for releases:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions builds and publishes to PyPI

## 💬 Communication

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Pull Requests** - Code contributions

## ⚖️ Code of Conduct

Be respectful, inclusive, and professional. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions make RepoDoctor better for everyone. Thank you for being part of this project!

---

<p align="center">
  Questions? Open an issue or start a discussion!
</p>
