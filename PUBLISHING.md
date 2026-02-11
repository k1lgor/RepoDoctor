# Publishing Guide

This document describes the process for building, testing, and publishing RepoDoctor to PyPI.

## Prerequisites

- `uv` package manager installed
- PyPI account with API token
- Write access to the repository

## Version Management

RepoDoctor follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backward-compatible)
- **PATCH** version: Bug fixes (backward-compatible)

### Version Locations

Update the version in the following files:

1. `pyproject.toml` - `[project] version = "x.y.z"`
2. `src/repodoc/__init__.py` - `__version__ = "x.y.z"`
3. `CHANGELOG.md` - Add new version entry

## Pre-Release Checklist

Before publishing a new release:

- [ ] All tests pass: `uv run pytest`
- [ ] No linting errors: `uv run ruff check`
- [ ] Code is formatted: `uv run ruff format --check`
- [ ] No type errors: `uv run ty check`
- [ ] Version bumped in all files
- [ ] CHANGELOG.md updated with changes
- [ ] README.md is up-to-date
- [ ] Git working directory is clean

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old distribution files
rm -rf dist/
```

### 2. Build Distribution Packages

```bash
# Build both wheel and source distribution
uv build
```

This creates:

- `dist/repodoc-{version}-py3-none-any.whl` - Wheel package
- `dist/repodoc-{version}.tar.gz` - Source distribution

### 3. Verify Package Contents

```bash
# List contents of the wheel
python -m zipfile -l dist/repodoc-{version}-py3-none-any.whl

# Check package metadata
uv pip show repodoc
```

### 4. Test Local Installation

```bash
# Install from wheel
uv pip install dist/repodoc-{version}-py3-none-any.whl

# Verify CLI works
repodoc --version
repodoc --help

# Run a test command
repodoc diet --help

# Uninstall after testing
uv pip uninstall repodoc
```

## Publishing to PyPI

### Test PyPI (Recommended First)

1. **Configure Test PyPI credentials:**

```bash
# Create/edit ~/.pypirc
[testpypi]
username = __token__
password = pypi-YOUR-TEST-PYPI-TOKEN
```

2. **Upload to Test PyPI:**

```bash
uv publish --repository testpypi dist/*
```

3. **Test installation from Test PyPI:**

```bash
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repodoc
```

### Production PyPI

1. **Configure PyPI credentials:**

```bash
# Create/edit ~/.pypirc
[pypi]
username = __token__
password = pypi-YOUR-PYPI-TOKEN
```

2. **Upload to PyPI:**

```bash
uv publish dist/*
```

3. **Verify on PyPI:**

- Check https://pypi.org/project/repodoc/
- Verify README renders correctly
- Check that all classifiers are correct

4. **Test installation:**

```bash
uv pip install repodoc
repodoc --version
```

## Creating a GitHub Release

After publishing to PyPI:

1. **Tag the release:**

```bash
git tag -a v{version} -m "Release version {version}"
git push origin v{version}
```

2. **Create GitHub Release:**

- Go to https://github.com/k1lgor/RepoDoctor/releases/new
- Select the tag you just created
- Title: `v{version}`
- Description: Copy from CHANGELOG.md
- Attach distribution files from `dist/`
- Mark as pre-release if version < 1.0.0

3. **Update CHANGELOG.md:**

```markdown
## [Unreleased]

## [{version}] - {date}

### Added

- Feature 1
- Feature 2

### Changed

- Change 1

### Fixed

- Bug fix 1
```

## Rollback Procedure

If you need to yank a release from PyPI:

```bash
# Yank a specific version (keeps it available but marks it as yanked)
uv publish --yank {version}
```

Note: You cannot delete a version from PyPI, only yank it.

## Automation (Future)

Consider setting up GitHub Actions for:

- Automated testing on PRs
- Automated building on tags
- Automated publishing to PyPI on release

## Troubleshooting

### Build Fails

- Check that all source files are included
- Verify `pyproject.toml` is valid
- Run `uv build --verbose` for detailed output

### Upload Fails

- Verify PyPI token is correct and has upload permissions
- Check that version doesn't already exist on PyPI
- Ensure package name is available (first-time publish)

### Installation Fails

- Check Python version compatibility (>=3.11)
- Verify all dependencies are available on PyPI
- Check for platform-specific issues

## Support

For issues with publishing:

- PyPI help: https://pypi.org/help/
- GitHub issues: https://github.com/k1lgor/RepoDoctor/issues
