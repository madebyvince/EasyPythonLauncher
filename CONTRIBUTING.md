# Contributing to Easy Python Launcher

Thank you for your interest in contributing to Easy Python Launcher! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your operating system and Python version
- Screenshots if applicable

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- A clear description of the feature
- Why this feature would be useful
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, commented code
   - Follow the existing code style
   - Test your changes on your platform

3. **Test thoroughly**
   - Ensure the application runs without errors
   - Test both light and dark modes
   - Verify multi-script execution works correctly

4. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Explain why the change is needed

## Code Style

- Use clear, descriptive variable names
- Add comments for complex logic
- Follow PEP 8 style guidelines
- Keep functions focused and single-purpose
- Document new functions with docstrings

## Testing Guidelines

Before submitting a PR, please test:
- Script execution (single and multiple)
- Stop functionality for each running script
- Theme switching and persistence
- Cross-platform compatibility (if possible)
- File system navigation
- Edge cases (permission errors, missing files, etc.)

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the "question" label
- Reach out to the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
