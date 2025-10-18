# Contributing to ONVIF Python

Thank you for your interest in contributing to the ONVIF Python project! We welcome contributions from everyone—whether you're a seasoned developer, a device integrator, or a first-time open source participant. Your feedback, code, documentation, and ideas help make this project better for the entire community.

## Contributors

<a href="https://github.com/nirsimetri/onvif-python/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=nirsimetri/onvif-python" />
</a>

## Table of Contents
- [How to Contribute](#how-to-contribute)
- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Issues](#reporting-issues)
- [Style Guide](#style-guide)
- [Documentation](#documentation)
- [Community & Support](#community--support)
- [License](#license)

## How to Contribute

1. **Fork the repository** on GitHub and clone your fork locally.
2. **Create a new branch** for your feature, fix, or documentation update.
3. **Make your changes** with clear, descriptive commit messages.
4. **Test your changes** to ensure they work as expected and do not break existing functionality.
5. **Push your branch** to your fork and open a Pull Request (PR) against the `main` branch of this repository.
6. **Participate in code review** by responding to feedback and making necessary updates.

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](./CODE_OF_CONDUCT.md), which is based on the [CNCF Foundation Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md). Please treat everyone with respect and foster a welcoming, inclusive environment.

## Ways to Contribute

- **Bug Reports:** If you find a bug, please [open an issue](https://github.com/nirsimetri/onvif-python/issues) with clear steps to reproduce, expected behavior, and environment details.
- **Feature Requests:** Suggest new features or improvements by opening an issue and describing your use case and desired functionality.
- **Code Contributions:** Submit fixes, enhancements, or new features via Pull Requests. See [Development Setup](#development-setup) and [Pull Request Guidelines](#pull-request-guidelines).
- **Documentation:** Help improve the README, usage examples, or API documentation. Well-written docs are as valuable as code!
- **Testing:** Add or improve unit and integration tests to ensure reliability and compatibility.
- **Device Testing:** Share your experience with different ONVIF devices by contributing results to the [device-test](https://github.com/nirsimetri/onvif-products/blob/main/device-test) list.
- **Translations:** If you can help translate documentation or error messages, let us know!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nirsimetri/onvif-python.git
   cd onvif-python
   ```
2. **Install locally:**
   ```bash
   pip install .
   ```
   Or use `pyproject.toml` with your preferred tool (e.g., Poetry, pip).
3. (Optional) **Run tests:**
   ```bash
   pytest
   ```
4. (Optional) **Lint and format code:**
   ```bash
   flake8 .
   black .
   ```
5. **Try example scripts:**
   See the [`examples/`](./examples/) folder for usage scenarios.

## Pull Request Guidelines

### PR Title Convention

Use the following commit/PR title types:

| Type       | Description                                                                  |
| ---------- | ---------------------------------------------------------------------------- |
| `feat`     | ✨ **New feature**                                                           |
| `fix`      | 🐛 **Bug fix**                                                               |
| `chore`    | 🔧 Non-code tasks such as updating dependencies, configs, or build tools     |
| `docs`     | 📚 Documentation-only changes                                                |
| `style`    | 🎨 Code style changes (formatting, spacing, etc. — without affecting logic)  |
| `refactor` | 🔨 Code refactoring without adding features or fixing bugs                   |
| `test`     | ✅ Adding or modifying tests (unit tests, integration tests, etc.)           |
| `perf`     | 🚀 Performance improvements                                                  |
| `ci`       | ⚙️ Changes to CI/CD configuration or pipelines                               |
| `build`    | 📦 Changes to the build system or external dependencies (e.g., Dockerfile)   |
| `revert`   | ⏪ Reverting a previous commit                                               |
| `code`     | General code changes that support but are not core features (e.g., examples) |

### Examples
- `feat: add Media service auto path detection`  
- `fix: handle empty response in GetServices`  
- `chore: update dependencies`  

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

- **PEP8** is the standard for Python code style. Use tools like `flake8` and `black` to check and format your code.
- **Docstrings:** Use clear, concise docstrings for modules, classes, and functions.
- **Type hints:** Add type annotations where appropriate for better readability and tooling support.
- **Comments:** Write helpful comments, especially for complex logic.
- **Naming:** Use descriptive variable, function, and class names.

## Documentation

- Update the README if your changes affect usage or installation.
- Add or update docstrings and inline comments.
- If you add new modules or services, document their usage and API.
- For device-specific notes, contribute to the [device-test](https://github.com/nirsimetri/onvif-products/blob/main/device-test) list.

## Community & Support

- Join discussions in the [GitHub Discussions](https://github.com/nirsimetri/onvif-python/discussions) tab.
- For real-time help, check if there is a chat or forum linked in the repository.
- Be respectful, patient, and helpful to others.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE.md).

---

Thank you for making ONVIF Python better! We appreciate your time, expertise, and enthusiasm. Happy coding!