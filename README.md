# WW-Tag-Sorter

## Build Instructions for Windows Executable

This document outlines the steps required to convert the Python GUI application into a Windows executable using PyInstaller.

### Prerequisites
Before you start, you need to have the following installed:
- Python 3.x  
- Pip (Python package installer)  
- PyInstaller  

### Installation Steps
1. **Install Python**  
   Download and install Python from the [official website](https://www.python.org/downloads/).

2. **Install PyInstaller**  
   Open a command prompt and run the following command:
   ```bash
   pip install pyinstaller
   ```

### Building the Executable
1. Open the command prompt and navigate to the directory where your `main.py` file is located:
   ```bash
   cd path\to\your\project
   ```

2. Run PyInstaller with the following command:
   ```bash
   pyinstaller --onefile main.py
   ```
   This will create a single executable file. The generated executable will be found in the `dist` folder.

### Usage Instructions
- Navigate to the `dist` folder and locate the `main.exe` file.
- Double-click `main.exe` to run the application.

Ensure you meet all prerequisites and follow the instructions carefully to build your executable successfully.