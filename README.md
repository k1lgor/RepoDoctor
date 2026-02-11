# 🏥 RepoDoctor

> AI-Powered Repository Health Analysis Using GitHub Copilot CLI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: pyright](https://img.shields.io/badge/type%20checked-pyright-blue.svg)](https://github.com/microsoft/pyright)
[![codecov](https://codecov.io/gh/k1lgor/RepoDoctor/branch/main/graph/badge.svg)](https://codecov.io/gh/k1lgor/RepoDoctor)
[![PyPI version](https://badge.fury.io/py/repodoc.svg)](https://badge.fury.io/py/repodoc)

RepoDoctor is a **Copilot-first** CLI tool that analyzes your repository's health by delegating all analysis logic to GitHub Copilot CLI. Instead of hardcoded rules, RepoDoctor acts as a prompt library and workflow orchestrator, letting AI provide contextual, intelligent insights about your codebase.

## ✨ Features

- 🍔 **Diet Analysis** - Identify bloat, large files, and missing hygiene files
- 🌎 **Tour Generation** - Create onboarding guides (TOUR.md) for new contributors
- 🐳 **Dockerfile Analysis** - Security and optimization recommendations
- 💀 **Dead Code Detection** - Find unused code with confidence levels
- 🔬 **Health Scanning** - Comprehensive multi-module analysis with scoring
- 📋 **Report Generation** - Beautiful Markdown reports from scan results

## 🎯 Why RepoDoctor?

**Traditional static analysis tools** use hardcoded rules that can't understand context.

**RepoDoctor is different:**

- ✅ Uses AI (GitHub Copilot) for contextual understanding
- ✅ Provides actionable recommendations, not just lint errors
- ✅ Understands your specific tech stack and patterns
- ✅ Generates human-readable reports and documentation
- ✅ Easy to extend with new prompt templates

## 📋 Prerequisites

Before using RepoDoctor, you need:

1. **Python 3.11 or higher**
2. **GitHub Copilot CLI** - RepoDoctor depends on this for all analysis
   ```bash
   npm install -g @github/copilot
   ```
3. **Authenticated Copilot** - Make sure you're authenticated:
   ```bash
   copilot -> /login
   ```

> **Note:** RepoDoctor delegates all analysis to Copilot CLI. Without it, RepoDoctor cannot function.

## 🚀 Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install RepoDoctor
uv tool install repodoc

# Or install from source
git clone https://github.com/k1lgor/RepoDoctor.git
cd RepoDoctor
uv pip install -e .
```

### Using pip

```bash
pip install repodoc

# Or from source
git clone https://github.com/k1lgor/RepoDoctor.git
cd RepoDoctor
pip install -e .
```

## 🎓 Quick Start

### Run a Full Health Scan

```bash
cd your-repository
repodoc scan
```

This will analyze your repository across multiple dimensions and provide an overall health score.

### Analyze Repository Bloat

```bash
repodoc diet
```

Identifies large files, build artifacts, and missing hygiene files like `.gitignore` or `LICENSE`.

### Generate an Onboarding Guide

```bash
repodoc tour
```

Creates a `TOUR.md` file with a comprehensive overview of your repository structure and architecture.

### Analyze Dockerfiles

```bash
repodoc docker
```

Provides security and optimization recommendations for your Dockerfiles.

### Detect Dead Code

```bash
repodoc deadcode
```

Finds potentially unused code with confidence levels (high/medium/low).

### Generate a Report

```bash
repodoc report
```

Creates a detailed Markdown report from your latest scan results.

## 📚 Command Reference

### `repodoc scan`

Run a comprehensive repository health scan across all analysis modules.

```bash
repodoc scan                     # Run full scan
repodoc scan --skip-docker       # Skip Dockerfile analysis
repodoc scan --json              # Output JSON instead of formatted text
repodoc scan --out results.json  # Save results to file
repodoc scan --timeout 600       # Increase timeout for large repos
```

**What it analyzes:**

- Repository bloat and hygiene (diet module)
- Onboarding documentation quality (tour module)
- Dockerfile security and optimization (docker module)
- Dead code detection (deadcode module)
- Overall repository health score

### `repodoc diet`

Analyze repository bloat and missing hygiene files.

```bash
repodoc diet                     # Run analysis (outputs Markdown to DIET.md)
repodoc diet --out report.md     # Save to custom file
repodoc diet --json              # Output JSON format
repodoc diet --timeout 300       # Optional: Custom timeout for large repos
```

**Identifies:**

- Largest files and directories
- Suspected build artifacts
- Missing hygiene files (.gitignore, LICENSE, etc.)
- Repository size breakdown

### `repodoc tour`

Generate a comprehensive onboarding guide.

```bash
repodoc tour                     # Generate TOUR.md
repodoc tour --out GUIDE.md      # Custom output file
repodoc tour --json              # Output structured data
```

**Creates:**

- Project overview and architecture
- Tech stack identification
- Entry points and key directories
- Development setup instructions

### `repodoc docker`

Analyze Dockerfiles for security and optimization.

```bash
repodoc docker                   # Analyze Dockerfiles
repodoc docker --fix             # Generate Dockerfile.repodoc with fixes
repodoc docker --in-place        # Apply fixes directly (⚠️ overwrites!)
```

**Checks for:**

- Security vulnerabilities
- Best practices violations
- Optimization opportunities
- Multi-stage build recommendations

### `repodoc deadcode`

Detect potentially unused code.

```bash
repodoc deadcode                 # Detect dead code
repodoc deadcode --json          # Output JSON
```

**Detects:**

- Unused functions and classes
- Unreachable code
- Confidence levels (high/medium/low)
- Reasoning for each finding

### `repodoc report`

Generate a Markdown report from scan results.

```bash
repodoc report                   # Generate REPODOCTOR_REPORT.md
repodoc report --out custom.md   # Custom output file
```

## 🎨 Output Formats

RepoDoctor supports multiple output formats:

### Terminal (Default)

Rich, colored terminal output with tables, panels, and progress indicators.

```bash
repodoc scan
```

### JSON

Structured JSON output for programmatic consumption.

```bash
repodoc scan --json
```

### File Output

Save results to a file for later analysis.

```bash
repodoc scan --out results.json
```

## 🏗️ Architecture

RepoDoctor follows a **Copilot-first architecture**:

```
┌─────────────┐
│   repodoc   │  CLI Interface
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Prompt Templates│  Structured prompts for each analysis type
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Copilot Invoker  │  Subprocess management & retry logic
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ GitHub Copilot   │  AI-powered analysis
│      CLI         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Output Parser    │  JSON extraction & schema validation
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Renderers      │  Terminal, JSON, or Markdown output
└──────────────────┘
```

### Key Design Principles

1. **No Hardcoded Rules** - All analysis is performed by Copilot CLI
2. **Schema-Driven** - Pydantic schemas ensure consistent output
3. **Retry Logic** - Automatic retry with stricter formatting on JSON parse failure
4. **Safe by Default** - Never overwrites files without explicit `--in-place` flag
5. **Extensible** - Add new analysis types by creating prompt templates

## 🔧 Configuration

RepoDoctor uses prompt templates stored in `src/repodoc/prompts/v1/`.

### Custom Timeout

For large repositories, increase the timeout:

```bash
repodoc scan --timeout 600  # 10 minutes
```

### Skip Modules

Skip specific analysis modules:

```bash
repodoc scan --skip-docker --skip-deadcode
```

## 🐛 Troubleshooting

### "Copilot CLI not found"

**Solution:** Install GitHub Copilot CLI:

```bash
npm install -g @github/copilot
```

### "Authentication failed"

**Solution:** Authenticate with Copilot:

```bash
copilot -> /login
```

### "Timeout error"

**Solution:** Increase timeout for large repositories:

```bash
repodoc scan --timeout 600
```

### "Empty repository" error

**Solution:** Make sure you're in a directory with code files. RepoDoctor validates that the directory contains analyzable content.

### JSON parsing failures

RepoDoctor automatically retries with stricter formatting instructions. If both attempts fail, check `.repodoc/logs/` for raw output.

## 📊 Output Files

RepoDoctor creates the following in your repository:

- `.repodoc/` - Cache directory for results and logs
- `.repodoc/logs/` - Raw Copilot CLI outputs for debugging
- `.repodoc/last_scan.json` - Latest scan results cache
- `DIET.md` - Diet analysis output (default for `diet` command)
- `TOUR.md` - Generated onboarding guide (default for `tour` command)
- `REPODOCTOR_REPORT.md` - Generated report (default for `report` command)
- `Dockerfile.repodoc` - Fixed Dockerfile (if you run `docker --fix`)

**Note:** Consider adding `.repodoc/` to your `.gitignore` to avoid committing cache files.

## 🧪 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/repodoc.git
cd repodoc

# Install with development dependencies using uv
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_copilot.py

# Run with verbose output
uv run pytest -v

# Run only unit tests
uv run pytest -m unit
```

### Code Quality

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type check
uv run pyright src/

# Run all quality checks
uv run ruff check src/ && uv run pyright src/
```

### Project Structure

```
repodoc/
├── src/repodoc/           # Main package
│   ├── cli.py             # CLI entry point
│   ├── commands/          # Command implementations
│   ├── core/              # Core functionality
│   │   ├── copilot.py     # Copilot CLI invocation
│   │   ├── parser.py      # Output parsing
│   │   ├── logger.py      # Logging utilities
│   │   └── exceptions.py  # Custom exceptions
│   ├── prompts/           # Prompt templates
│   │   └── v1/            # Version 1 templates
│   ├── renderers/         # Output formatting
│   ├── schemas/           # Pydantic schemas
│   └── __init__.py
├── tests/                 # Test suite
├── docs/                  # Documentation
├── pyproject.toml         # Project metadata
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs and issues
- 💡 Suggest new features or analysis types
- 📝 Improve documentation
- 🔧 Submit pull requests
- 📋 Add new prompt templates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by [GitHub Copilot CLI](https://github.com/features/copilot/cli) for AI analysis
- Schema validation with [Pydantic](https://docs.pydantic.dev/)

## 📮 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/k1lgor/RepoDoctor/issues)
- **Discussions:** [GitHub Discussions](https://github.com/k1lgor/RepoDoctor/discussions)
- **Author:** Plamen Ivanov

---

<p align="center">
  Made with ❤️ by developers, for developers
</p>
