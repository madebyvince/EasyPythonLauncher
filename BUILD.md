# Building Easy Python Launcher

This guide explains how to build standalone executables of Easy Python Launcher using PyInstaller.

## Prerequisites

- Python 3.6 or higher installed
- PyInstaller package

## Installation

Install PyInstaller:
```bash
pip install pyinstaller
```

## Building the Executable

### Windows

For a single-file executable with no console window:
```bash
pyinstaller --onefile --windowed --name EasyPythonLauncher EasyPythonLauncher.py
```

The executable will be created in `dist/EasyPythonLauncher.exe`

### Linux

```bash
pyinstaller --onefile --name EasyPythonLauncher EasyPythonLauncher.py
```

The executable will be created in `dist/EasyPythonLauncher`

### macOS

```bash
pyinstaller --onefile --windowed --name EasyPythonLauncher EasyPythonLauncher.py
```

For a proper macOS app bundle:
```bash
pyinstaller --onefile --windowed --name EasyPythonLauncher --osx-bundle-identifier com.yourname.easypythonlauncher EasyPythonLauncher.py
```

The app will be created in `dist/EasyPythonLauncher.app`

## Build Options Explained

- `--onefile`: Bundles everything into a single executable file
- `--windowed`: Suppresses the console window (GUI only)
- `--name`: Sets the name of the output executable
- `--icon=icon.ico`: Adds a custom icon (if you have one)

## Advanced Options

### Adding an Icon

If you have a custom icon file:
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name EasyPythonLauncher EasyPythonLauncher.py
```

### Optimizing File Size

To reduce the executable size:
```bash
pyinstaller --onefile --windowed --name EasyPythonLauncher --strip EasyPythonLauncher.py
```

### Creating a Spec File for Customization

Generate a spec file for advanced customization:
```bash
pyi-makespec --onefile --windowed --name EasyPythonLauncher EasyPythonLauncher.py
```

Then edit `EasyPythonLauncher.spec` and build with:
```bash
pyinstaller EasyPythonLauncher.spec
```

## Testing the Executable

After building:

1. Navigate to the `dist/` folder
2. Run the executable
3. Test all features:
   - File browsing
   - Script execution
   - Multiple script management
   - Theme switching
   - Stop functionality

## Distribution

The executable in the `dist/` folder is standalone and can be:
- Copied to other computers (same OS)
- Distributed via GitHub Releases
- Shared directly with users

**Note**: The executable is platform-specific. You need to build separately for Windows, Linux, and macOS.

## Troubleshooting

### "Failed to execute script"
- Ensure all imports are available
- Check that tkinter is properly bundled
- Try building without `--windowed` to see error messages

### Large File Size
- This is normal; PyInstaller bundles Python and all dependencies
- Typical size: 10-20 MB for this application

### Antivirus False Positives
- Some antivirus software may flag PyInstaller executables
- This is a known issue with PyInstaller
- You can submit the file to antivirus vendors for whitelisting

## Clean Build

To clean previous builds:
```bash
# Remove build artifacts
rm -rf build/ dist/
rm *.spec
```

Then rebuild from scratch.

## Continuous Integration

For automated builds, see `.github/workflows/` for CI/CD examples (if configured).
