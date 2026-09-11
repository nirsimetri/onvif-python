## Contributors

<a href="https://github.com/nirsimetri/onvif-python/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nirsimetri/onvif-python" />
</a>

## Ways to Contribute

### Bug Reports
If you find a bug, please [open an issue](https://github.com/nirsimetri/onvif-python/issues) with clear steps to reproduce, expected behavior, and environment details.

### Feature Requests
Suggest new features or improvements by opening an issue and describing your use case and desired functionality.

### Code Contributions
Submit fixes, enhancements, or new features via Pull Requests. See [Development Setup](#development-setup) and [Pull Request Guidelines](#pull-request-guidelines).

### Documentation
Help improve the [`docs/`](https://github.com/nirsimetri/onvif-python/tree/dev/docs) source, usage examples, or API documentation.

Well-written docs are as valuable as code!

### Testing
Add or improve unit and integration tests to ensure reliability and compatibility.

### Device Testing
Share your experience with different ONVIF devices by contributing results to the [`device-test/`](https://github.com/nirsimetri/onvif-products/blob/main/device-test) list.

### Translations
If you can help translate documentation or error messages, let us know!

## Development Setup

### Clone the repository and switch to dev branch

   ```bash
   # Option 1: Clone dev branch directly
   git clone -b dev https://github.com/nirsimetri/onvif-python.git
   cd onvif-python
   
   # Option 2: Clone then switch to dev
   git clone https://github.com/nirsimetri/onvif-python.git
   cd onvif-python
   git checkout dev
   ```
### Install locally

   ```bash
   # Install the package in development mode
   pip install -e .
   
   # Install development dependencies (pytest, black, docformatter, mypy, isort, pylint)
   pip install -e ".[dev]"
   ```
   Or use `pyproject.toml` with your preferred tool (e.g., Poetry, pip).

### Run tests

   ```bash
   python -m pytest
   ```
   Make sure all tests pass before submitting your changes.

### Lint and format code

   ```bash
   # Check code linting with pylint
   pylint .

   # Check error with pylint
   pylint onvif --errors-only --score=n

   # Static type checking
   mypy onvif

   # Sort import order
   isort .

   # Format docstring with docformatter
   docformatter --recursive --black --in-place .
   
   # Format code with black
   black .
   ```
   Ensure your code follows PEP8 standards and is properly formatted.

### Try example scripts

   See the [`examples/`](https://github.com/nirsimetri/onvif-python/tree/dev/examples) folder for usage scenarios.

## Pull Request Guidelines

### PR Convention

For the PR title, you do not need to include a title type prefix; omitting it improves readability when the release notes are generated (e.g., "Refactor CLI for better modularity"). Also, ensure the first letter of the PR title is capitalized.

Make sure to write a comprehensive description for the PR you create to make it easier for maintainers to review the PR you have submitted to the project.

### Commit Convention

Use the following commit title types:

- **`feat`** → ✨ New feature
- **`fix`** → 🐛 Bug fix
- **`chore`** → 🔧 Non-code tasks such as updating dependencies, configs, or build tools
- **`docs`** → 📚 Documentation-only changes
- **`style`** → 🎨 Code style changes (formatting, spacing, etc. — without affecting logic)
- **`refactor`** → 🔨 Code refactoring without adding features or fixing bugs
- **`test`** → ✅ Adding or modifying tests (unit tests, integration tests, etc.)
- **`perf`** → 🚀 Performance improvements
- **`ci`** → ⚙️ Changes to CI/CD configuration or pipelines
- **`build`** → 📦 Changes to the build system or external dependencies (e.g., Dockerfile)
- **`revert`** → ⏪ Reverting a previous commit
- **`code`** → General code changes that support but are not core features (e.g., examples)

**Examples:**

- `feat: Add Media service auto path detection`  
- `fix: Handle empty response in GetServices`  
- `chore: Update zeep dependencies`

### General Guidelines

- **Describe your changes clearly** in the PR description.  
- **Reference related issues** by number (e.g., `Fixes #123`).  
- **Keep changes focused**—avoid mixing unrelated fixes or features in one PR.  
- **Include tests** for new features or bug fixes when possible.  
- **Follow the style guide** and ensure your code passes linting and tests.  
- **Be responsive to review feedback** and update your PR as needed.  
- **Squash commits** if requested, to keep history clean.  

## Reporting Issues

- Search existing issues before opening a new one to avoid duplicates.
- Provide as much detail as possible: environment, device model, ONVIF version, error messages, and steps to reproduce.
- Attach logs, screenshots, or code snippets if relevant.
- Be polite and constructive—remember, maintainers and contributors are volunteers.

## Style Guide

- **PEP8** is the standard for Python code style. Use tools like `pylint` and `black` to check and format your code.
- **Docstrings:** Use clear, concise docstrings for modules, classes, and functions. Use `docformatter` to format your docstring.
- **Type hints:** Add type annotations where appropriate for better readability and tooling support.
- **Comments:** Write helpful comments, especially for complex logic.
- **Naming:** Use descriptive variable, function, and class names.

## Documentation

- Update the [`docs/`](https://github.com/nirsimetri/onvif-python/tree/dev/docs) if your changes affect usage or installation.
- Add or update docstrings and inline comments.
- If you add new modules or services, document their usage and API.
- For device-specific notes, contribute to the [`device-test/`](https://github.com/nirsimetri/onvif-products/blob/main/device-test) list.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](https://github.com/nirsimetri/onvif-python/blob/main/CODE_OF_CONDUCT.md), which is based on the [CNCF Foundation Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md). Please treat everyone with respect and foster a welcoming, inclusive environment.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](legal/license.md).

---

Thank you for making ONVIF Python better! We appreciate your time, expertise, and enthusiasm. Happy coding!