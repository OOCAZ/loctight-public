# LOCTight Tests

This directory contains the unit tests for the LOCTight application.

## Running Tests

### Local Testing

To run the tests locally:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_core_logic.py -v
```

### CI/CD Testing

Tests are automatically run on every push and pull request via GitHub Actions across multiple platforms:

- Ubuntu (Linux)
- Windows
- macOS

And multiple Python versions:

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Test Structure

### test_core_logic.py

Tests the core timer and control logic without requiring GUI components:

- **TestTimerFunctions**: Tests for jiggle, countdown, pause/resume, and start/cancel logic
- **TestInputValidation**: Tests for custom timer input validation
- **TestPlatformLocking**: Tests for platform-specific workstation locking
- **TestButtonStateManagement**: Tests for UI state management logic

## Test Coverage

The tests focus on:

- Timer countdown logic
- Mouse jiggle functionality
- Pause and resume behavior
- Input validation
- Platform-specific locking mechanisms
- Button state management

## Continuous Integration

The project uses GitHub Actions for automated testing:

- **tests.yml**: Runs the full test suite on multiple platforms and Python versions
- **lint.yml**: Checks code quality with flake8, black, and isort

See `.github/workflows/` for the full CI configuration.
