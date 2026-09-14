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

   ```shell
   # Option 1: Clone dev branch directly
   git clone -b dev https://github.com/nirsimetri/onvif-python.git
   cd onvif-python
   
   # Option 2: Clone then switch to dev
   git clone https://github.com/nirsimetri/onvif-python.git
   cd onvif-python
   git checkout dev
   ```
### Install locally

   ```shell
   # Install the package in development mode
   pip install -e .
   
   # Install development dependencies
   # (pytest, pytest-cov, pylint, mypy, isort, docformatter, black)
   pip install -e ".[dev]"
   ```
   Or use `pyproject.toml` with your preferred tool (e.g., Poetry, pip).

### Run tests

   ```shell
   python -m pytest
   ```
   Make sure all tests pass before submitting your changes.

### Generate coverage report

   Coverage is optional for local development. To generate an XML coverage report:
   ```shell
   pytest --cov=. --cov-report=xml
   ```
   This generates `coverage.xml`, which can be used by coverage analysis tools such as Codacy.

### Lint and format code

   ```shell
   # Check code linting with pylint
   pylint .

   # Check error with pylint
   pylint . --errors-only --score=n

   # Static type checking
   mypy .

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

For the PR title, you **do not need** to include a title type prefix; omitting it improves readability when the release notes are generated (e.g., "Refactor CLI for better modularity"). Also, ensure the first letter of the PR title is capitalized.

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

The documentation is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and [mkdocstrings](https://mkdocstrings.github.io/) to generate API documentation directly from the Python source code.

### Setup

Install the project together with the documentation dependencies:

```shell
pip install -e ".[docs]"
```

This installs the documentation tooling defined in `pyproject.toml`, including:

* `mkdocs-material` — MkDocs theme and Material extensions
* `mkdocstrings[python]` — API documentation generated from Python source code
* `mkdocs-git-authors-plugin` — contributor information for documentation pages

### Run Locally

Start the MkDocs development server from the project root:

```shell
mkdocs serve
```

By default, the documentation will be available at:

```text
http://127.0.0.1:8000/
```

MkDocs automatically rebuilds the documentation when source files are changed.

### Build

Before submitting documentation changes, verify that the site can be built successfully:

```shell
mkdocs build --strict
```

Using `--strict` is recommended because it treats warnings as errors and helps catch broken links, invalid configuration, missing pages, and other documentation issues before they reach the deployed site.

### Structure

The documentation source is located in the [`docs/`](https://github.com/nirsimetri/onvif-python/tree/dev/docs) directory. The navigation and page structure are defined in `mkdocs.yml`.

```text
docs/
├── assets/
├── javascripts/
├── stylesheets/
├── overrides/
├── api/
├── core/
├── references/
├── utilities/
├── legal/
├── index.md
├── installation.md
├── quick_start.md
├── philosophy.md
├── contributing.md
├── roadmap.md
├── used_by.md
├── external.md
└── releases.md
```

API reference pages under [`docs/api/`](https://github.com/nirsimetri/onvif-python/tree/dev/docs/api) use `mkdocstrings` to generate documentation from the corresponding Python modules and classes.

For example:

```markdown
::: onvif.services.ptz
```

When modifying a public API, update the corresponding Python docstrings and documentation page where appropriate.

### Guidelines

* Update the [`docs/`](https://github.com/nirsimetri/onvif-python/tree/dev/docs) source when changes affect usage, installation, configuration, or public APIs.
* Add or update Python docstrings when introducing or changing public classes, methods, or functions.
* Keep examples accurate and executable where possible.
* Use clear headings and concise explanations.
* For device-specific behavior or compatibility information, contribute test results to the [`device-test/`](https://github.com/nirsimetri/onvif-products/tree/main/device-test) repository.
* Run `mkdocs build --strict` before submitting documentation-related changes.

### Pull Requests

Documentation-only changes should use the `docs` commit type:

```text
docs: Improve PTZ API documentation
```

If a code change also requires documentation updates, include the documentation changes in the same pull request when practical.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](https://github.com/nirsimetri/onvif-python/blob/main/CODE_OF_CONDUCT.md), which is based on the [CNCF Foundation Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md). Please treat everyone with respect and foster a welcoming, inclusive environment.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](../legal/license.md).

---

Thank you for making ONVIF Python better!

We appreciate your time, expertise, and enthusiasm.