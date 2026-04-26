#!/usr/bin/env python3
"""
Build script to create an executable using PyInstaller.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def main():
    """Build executable using PyInstaller."""
    # Project configuration
    script_name = "main.py"
    app_name = "photo-sorter"

    # Clean previous builds
    build_dirs = ["build", "dist"]
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name",
        app_name,
        "--onefile",  # Create a single executable file
        "--clean",  # Clean PyInstaller cache
        script_name
    ]

    # Optional: Add console window (remove --noconsole if you want a GUI app)
    # cmd.append("--noconsole")  # Uncomment for GUI apps

    # Optional: Add icon (if you have one)
    # cmd.extend(["--icon", "icon.ico"])

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"  Executable location: dist/{app_name}")
        if sys.platform == "darwin":
            print(f"  On macOS: dist/{app_name}")
        elif sys.platform == "win32":
            print(f"  On Windows: dist/{app_name}.exe")
        else:
            print(f"  On Linux: dist/{app_name}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        return 1
    except FileNotFoundError:
        print("\nPyInstaller not found. Install it with:")
        print("  pip install pyinstaller")
        return 1


if __name__ == "__main__":
    sys.exit(main())
