# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-05

### Added
- Initial release of Easy Python Launcher
- File explorer interface with tree view for folder navigation
- Python script (.py) file listing and selection
- One-click script execution with Run button
- Double-click to run scripts
- Integrated console with real-time output display
- Multi-process support - run multiple scripts simultaneously
- Selective process control - stop specific running scripts
- Dark/Light mode toggle with persistent settings
- Visual indicators for running scripts
- Cross-platform support (Windows, Linux, macOS)
- Automatic drive detection on Windows (C:\, D:\, etc.)
- Protection against launching duplicate scripts
- Configuration file for saving user preferences

### Features
- **User Interface**: Clean, modern interface built with tkinter
- **Theme System**: Complete dark/light mode with customized colors for all UI elements
- **Process Management**: Independent subprocess handling for each script
- **Smart Controls**: Context-aware button states based on selection and running status
- **Console Output**: Scrollable console with color-coded output (green on black for dark mode)
- **File System**: Full file system access with expandable folder tree
- **Settings Persistence**: Automatic saving of theme preference

### Technical Details
- Built with Python standard library (tkinter)
- No external dependencies required
- Platform-specific path handling
- Thread-based script execution for non-blocking UI
- Process dictionary for managing multiple concurrent scripts

[1.0.0]: https://github.com/yourusername/easy-python-launcher/releases/tag/v1.0.0
