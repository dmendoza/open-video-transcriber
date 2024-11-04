#!/usr/bin/env python3
"""
setup_dev_env.py
This script sets up the development environment for the project. It performs the following tasks:
1. Checks if the Python version meets the minimum requirements.
2. Creates a virtual environment for the project.
3. Installs the project dependencies in the virtual environment.

Usage:
    Run this script from the command line to set up the development environment:
        python setup_dev_env.py
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """
    Checks if the current Python version meets the minimum required version.
    This function compares the current Python version with the minimum required
    version (3.12). If the current version is lower than the minimum required
    version, it raises a SystemError with a message indicating the required
    version and the current version.

    Raises:
        SystemError: If the current Python version is lower than the minimum
                     required version.
    """
    min_version = (3, 12)
    current = sys.version_info[:2]
    
    if current < min_version:
        raise SystemError(
            f"Python {min_version[0]}.{min_version[1]} or higher is required. "
            f"You are using Python {current[0]}.{current[1]}"
        )

def create_virtual_environment():
    """
    Creates a virtual environment in the current directory.
    This function checks if a virtual environment already exists in the directory.
    If it does, it prints a message and exits. If it does not, it creates a new
    virtual environment using the `venv` module.
    """
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("Virtual environment already exists.")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

def install_dependencies():
    """
    Installs the necessary development dependencies for the project.
    This function performs the following steps:
    1. Determines the correct pip path based on the operating system.
       - For Windows, it uses "venv/Scripts/pip".
       - For other operating systems, it uses "venv/bin/pip".
    2. Upgrades pip to the latest version.
    3. Installs the development dependencies specified in the project's setup configuration.

    Raises:
        subprocess.CalledProcessError: If any of the subprocess commands fail.
    """
    # Determine the pip path based on OS
    pip_path = "venv/Scripts/pip" if sys.platform == "win32" else "venv/bin/pip"
    
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    
    print("Installing development dependencies...")
    subprocess.run([pip_path, "install", "-e", ".[dev]"], check=True)

def main():
    """
    Sets up the development environment by performing the following steps:
    1. Checks the Python version to ensure compatibility.
    2. Creates a virtual environment for the project.
    3. Installs the necessary dependencies within the virtual environment.
    4. Prints a success message and provides instructions for activating the virtual environment and starting development.
    If any step fails, an error message is printed to stderr and the program exits with a status code of 1.
    """
    try:
        # Check Python version
        check_python_version()
        
        # Create virtual environment
        create_virtual_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Print success message and next steps
        print("\nDevelopment environment setup complete!")
        print("\nNext steps:")
        print("1. Activate the virtual environment:")
        if sys.platform == "win32":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Start developing!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()