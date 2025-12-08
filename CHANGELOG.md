# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-05

### Added
- **Python Interpreter Selection**: New menu option (Settings > Select Python Interpreter) to manually choose which Python installation to use
- **Python Path Auto-detection**: Automatically finds and saves the Python interpreter path for faster subsequent launches
- **Last Folder Restoration**: Application now remembers and reopens the last folder containing executed scripts
- **Improved PyInstaller Support**: Fixed issue where compiled executable would relaunch itself instead of running selected scripts
- **Smart Python Discovery**: Searches common Python installation locations on Windows
- **Python Path Persistence**: Saves selected Python interpreter location in configuration file

### Changed
- **Configuration File Location**: Now stored in the application directory instead of user profile to reduce antivirus false positives
  - Before: `C:\Users\Username\.easy_python_launcher_config.json`
  - After: `EasyPythonLauncher.config.json` (next to the executable/script)
- Enhanced configuration file to store Python interpreter path and last opened folder
- Improved error handling when Python interpreter is not found
- Better user feedback with dialog boxes for Python selection

### Fixed
- **Critical**: Resolved PyInstaller compilation issue where `sys.executable` pointed to the launcher instead of Python
- **Security**: Reduced antivirus false positive detections by moving config file from user profile to application directory
- Application now correctly launches Python scripts when compiled as standalone executable

### Technical Improvements
- Added `get_python_executable()` method with automatic detection and fallback to manual selection
- Implemented `expand_to_folder()` for automatic folder tree navigation
- Added configuration methods: `save_python_path()`, `load_python_path()`, `save_last_folder()`, `load_last_folder()`
- Enhanced search algorithm for Python installations across multiple common Windows locations
- Config file now uses application directory instead of user profile (reduces "UserProfileSelfRun" AV triggers)

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
