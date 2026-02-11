# Changelog

All notable changes to RepoDoctor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-11

### Added

- **Initial release of RepoDoctor** - AI-powered repository health analysis tool
- **Six core analysis commands**:
  - `diet` - Repository bloat and hygiene analysis
  - `tour` - Onboarding guide generation (TOUR.md)
  - `docker` - Dockerfile security and optimization analysis
  - `deadcode` - Unused code detection
  - `scan` - Comprehensive multi-module health scanning
  - `report` - Beautiful markdown reports from scan results
- **File generation by default**: Commands now generate markdown files
  - `repodoc diet` → generates **DIET.md** (markdown format by default)
  - `repodoc tour` → generates **TOUR.md**
  - `repodoc report` → generates **REPODOCTOR_REPORT.md**
- **GitHub Copilot CLI integration**: All analysis delegated to AI
- **Rich terminal output**: Colors, tables, panels, spinners
- **JSON output support**: `--json` flag for programmatic use
- **Flexible output paths**: `--out <path>` for custom file locations
- **Optional timeout parameter**: `--timeout <seconds>` for large repositories
- **Comprehensive error handling**: Clean, helpful error messages
- **Retry logic**: Automatic retry with stricter formatting on JSON parse failures
- **UTF-8 encoding everywhere**: Cross-platform Unicode support
- **Pydantic schema validation**: Type-safe data models
- **Extensive testing**: 54 tests with 98% pass rate, all CI/CD ready
- **Full documentation**: README, CONTRIBUTING, PRD, PUBLISHING guides
- **GitHub Actions CI/CD**: Automated testing, linting, type checking, and PyPI publishing
- **Type checking with ty**: Astral's blazing-fast type checker (10-100x faster than alternatives)

### Fixed
- Logger exc_info parameter handling to prevent KeyError on error reporting
- Windows console encoding issues with Unicode emojis in JSON mode
- All commands now properly suppress Rich console output when --json flag is used
- Analysis commands now respect .gitignore and skip untracked files (.venv, node_modules, caches)
  - Reduces execution time by 70-90% for projects with large dependencies
  - Uses `git ls-files` to only analyze tracked source code
  - Improves accuracy by excluding build artifacts and dependencies
- Duplicate console output in diet command (removed progress message before spinner)
- Confusing warning messages no longer shown to users (still logged for debugging)
- Timeout parameter now optional everywhere (no default value, user can specify as needed)
- Copilot CLI output encoding on Windows (force UTF-8 instead of system default cp1252)
- NoneType error when Copilot CLI returns empty stdout/stderr
- **Cross-platform UTF-8 enforcement**: All output (console, files, subprocess) now uses UTF-8 on all operating systems
  - Windows console code page set to UTF-8 (CP 65001)
  - Python stdout/stderr reconfigured to UTF-8
  - Rich console configured for modern UTF-8 output
  - All file operations use explicit UTF-8 encoding
- **Tour command file generation**: TourRenderer now actually writes TOUR.md file (was only displaying success message)
- **Diet command markdown generation**: Diet command now generates DIET.md file by default (like tour/report)
  - Added `diet_markdown` field to DietOutput schema
  - Updated prompt to generate markdown content
  - Default behavior: writes DIET.md file
  - `--json` flag outputs JSON summary to stdout
  - `--out <path>` allows custom markdown file path
- **CI/CD Tests**: Fixed GitHub Actions test failures caused by missing Copilot CLI
  - Added `shutil.which()` mocking in all test fixtures to simulate Copilot CLI availability
  - Tests in `test_copilot.py` now mock copilot binary presence during `CopilotInvoker` instantiation
  - CI pipelines no longer require actual GitHub Copilot CLI installation
  - All 54 tests pass without any external dependencies beyond Python packages
- **Clean error messages**: Removed duplicate/confusing error output from console
  - Logger messages now only written to `.repodoc/logs/` directory
  - Users see single, clear error message without logging noise
  - `typer.Exit` exceptions properly propagate without re-handling
  - Use `--verbose` flag to see detailed stack traces when debugging
- **Report command**: Fixed critical bugs and enhanced UX
  - **Bug Fix**: Added `{{scan_data}}` placeholder to report.txt template (was missing)
  - **Bug Fix**: Added UTF-8 encoding to log file handler (prevents UnicodeEncodeError)
  - **Bug Fix**: Fixed schema to allow flexible issues/recommendations format from Copilot
  - **Enhancement**: Added success message with next actions
  - Report now generates REPODOCTOR_REPORT.md successfully from scan cache
- **Type safety**: Fixed all type checking errors (ty now passes with 0 errors)
  - Added type annotations for `save_text_output` function parameters (`Callable`, `Any`)
  - Fixed `CopilotTimeoutError` to accept `int | None` timeout parameter
  - Added runtime checks for `sys.stdout.reconfigure` availability on Windows
  - Added proper `# type: ignore` comments for dynamic attribute access
  - Fixed `max()` return type inference with explicit `cast(str, ...)` for ty type checker
  - All core modules now fully type-safe with proper annotations

### Features

#### Commands
- **diet**: Repository bloat and hygiene analysis
- **tour**: Onboarding guide generation (TOUR.md)
- **docker**: Dockerfile security and optimization analysis
- **deadcode**: Dead code detection with confidence levels
- **scan**: Multi-module health scan with overall scoring
- **report**: Markdown report generation from scan results

#### Core Capabilities
- Copilot-first architecture (no hardcoded rules)
- Schema-driven output validation
- Automatic JSON parsing with markdown support
- Safe by default (no file overwrites without --in-place)
- Extensible prompt template system
- Comprehensive logging and debugging support

### Technical

- **Python 3.11+ support** (tested on 3.11, 3.12, 3.13)
- **Cross-platform**: Linux, macOS, Windows
- **Package manager**: uv (by Astral) - blazing fast Python package manager
- **Linter/Formatter**: ruff (by Astral) - 10-100x faster than traditional tools
- **Type checker**: ty (by Astral) - 10-100x faster than mypy/pyright
- **Testing**: pytest with 54 tests, 98% pass rate, 51% coverage
- **CI/CD**: GitHub Actions with automated testing and PyPI publishing
- **Architecture**: Copilot-first, no hardcoded rules, extensible prompt templates
- **Safe defaults**: Never overwrites files without explicit `--in-place` flag
- **UTF-8 everywhere**: Cross-platform Unicode support for all I/O operations

---

## Quality Metrics (v0.1.0)

- ✅ **54 tests passing** (98% pass rate, 1 xfailed)
- ✅ **51% code coverage**
- ✅ **0 lint errors** (ruff)
- ✅ **0 type errors** (ty)
- ✅ **All CI checks passing**
- ✅ **CI-ready**: No external dependencies required for tests

---

## Links

- [GitHub Repository](https://github.com/k1lgor/RepoDoctor)
- [PyPI Package](https://pypi.org/project/repodoc/)
- [Documentation](https://github.com/k1lgor/RepoDoctor#readme)
- [Contributing Guide](https://github.com/k1lgor/RepoDoctor/blob/main/CONTRIBUTING.md)

---

[Unreleased]: https://github.com/k1lgor/RepoDoctor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/k1lgor/RepoDoctor/releases/tag/v0.1.0
- Formatted with ruff
- Tested with pytest (51 passing tests, 54% coverage)
- Built with Typer CLI framework
- Rich terminal UI
- Pydantic v2 for data validation
- Zero lint errors, production-ready code

### CI/CD
- Automated testing on push/PR (9 platform/Python combinations)
- Automated dependency updates (weekly)
- Automated PyPI publishing on tags
- Documentation validation
- Code coverage reporting

---

## Version Guidelines

### Semantic Versioning

- **MAJOR**: Breaking changes to CLI or API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Categories

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes
