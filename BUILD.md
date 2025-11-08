# Building Standalone Executables

This guide explains how to build standalone executables for pwick using PyInstaller.

## Requirements

- Python 3.9 or later
- pip (Python package manager)
- Internet connection (for downloading dependencies)

## Platform-Specific Instructions

### Linux / macOS

1. Open a terminal in the pwick directory
2. Run the build script:
   ```bash
   ./build_exe.sh
   ```
3. The executable will be created at: `dist/pwick`
4. Test the executable:
   ```bash
   ./dist/pwick
   ```

**Optional: Install System-Wide**
```bash
sudo cp dist/pwick /usr/local/bin/
```

### Windows

1. Open Command Prompt or PowerShell in the pwick directory
2. Run the build script:
   ```cmd
   build_exe.bat
   ```
3. The executable will be created at: `dist\pwick.exe`
4. Test the executable:
   ```cmd
   dist\pwick.exe
   ```

**Optional: Create Installer**

You can use installer creation tools like:
- [Inno Setup](https://jrsoftware.org/isinfo.php) (free, open source)
- [NSIS](https://nsis.sourceforge.io/) (free, open source)

## Build Process Details

The build scripts perform the following steps:

1. **Create Build Environment**: Creates an isolated Python virtual environment for building
2. **Install Dependencies**: Installs PyInstaller and all pwick dependencies
3. **Clean Previous Builds**: Removes old build artifacts
4. **Build Executable**: Uses PyInstaller with the `pwick.spec` configuration
5. **Report Results**: Shows build status and executable location

## Build Configuration

The build is configured through `pwick.spec` which includes:

- **Single-file executable**: All dependencies bundled into one file
- **Hidden imports**: Ensures all required modules are included
- **Data files**: Bundles VERSION, README.md, and LICENSE
- **Excluded modules**: Removes unnecessary dependencies (matplotlib, numpy, etc.)
- **UPX compression**: Reduces executable size
- **Platform-specific settings**:
  - **Windows**: Windowed mode (no console window)
  - **Linux/macOS**: Console mode (for better error reporting)

## Customization

### Adding an Application Icon

To add a custom icon:

1. Create or obtain an icon file:
   - **Windows**: `.ico` file
   - **macOS**: `.icns` file
   - **Linux**: `.png` file (at least 256x256)

2. Edit `pwick.spec` and change:
   ```python
   icon=None,  # Change to: icon='path/to/icon.ico'
   ```

3. Rebuild the executable

### Adjusting Executable Size

The build uses UPX compression by default. To disable it:

1. Edit `pwick.spec` and change:
   ```python
   upx=True,  # Change to: upx=False
   ```

2. Rebuild the executable

Note: Disabling UPX will increase executable size but may improve startup time.

## Troubleshooting

### Build Fails with "ModuleNotFoundError"

- **Solution**: Add the missing module to `hiddenimports` in `pwick.spec`

### Executable Won't Start

- **Check**: Run from terminal/command prompt to see error messages
- **Solution**: Ensure all data files are included in `datas` section of `pwick.spec`

### Executable Size Too Large

- **Check**: Current size and what's included
- **Solutions**:
  - Enable UPX compression in `pwick.spec`
  - Add more modules to `excludes` list
  - Consider using one-folder mode instead of one-file

### Permission Denied (Linux/macOS)

- **Solution**: Make scripts executable:
  ```bash
  chmod +x build_exe.sh
  ```

### Antivirus False Positive (Windows)

PyInstaller executables sometimes trigger antivirus warnings. This is a known issue with PyInstaller.

- **Solutions**:
  - Add exception in your antivirus software
  - Submit executable to antivirus vendor for whitelisting
  - Consider code signing the executable (requires certificate)

## Distribution

After building:

1. **Test thoroughly** on the target platform
2. **Create checksums** for verification:
   ```bash
   # Linux/macOS
   sha256sum dist/pwick > pwick.sha256

   # Windows PowerShell
   Get-FileHash dist\pwick.exe -Algorithm SHA256 > pwick.sha256
   ```
3. **Package with documentation**:
   - Include README.md
   - Include LICENSE
   - Include platform-specific installation instructions

## Automated Builds

For continuous integration, you can use GitHub Actions or similar CI/CD platforms:

```yaml
# Example GitHub Actions workflow
name: Build Executables

on: [push, pull_request]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Build
        run: ./build_exe.sh
      - uses: actions/upload-artifact@v2
        with:
          name: pwick-linux
          path: dist/pwick

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Build
        run: build_exe.bat
      - uses: actions/upload-artifact@v2
        with:
          name: pwick-windows
          path: dist/pwick.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Build
        run: ./build_exe.sh
      - uses: actions/upload-artifact@v2
        with:
          name: pwick-macos
          path: dist/pwick
```

## Support

For issues with building executables, please:

1. Check this document's troubleshooting section
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Open an issue at: https://github.com/orpheus497/pwick/issues
