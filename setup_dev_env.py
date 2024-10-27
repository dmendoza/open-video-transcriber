#!/usr/bin/env python3
# setup_dev_env.py

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version meets the minimum requirements."""
    min_version = (3, 12)
    current = sys.version_info[:2]
    
    if current < min_version:
        raise SystemError(
            f"Python {min_version[0]}.{min_version[1]} or higher is required. "
            f"You are using Python {current[0]}.{current[1]}"
        )

def create_virtual_environment():
    """Create a virtual environment for the project."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("Virtual environment already exists.")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

def install_dependencies():
    """Install project dependencies in the virtual environment."""
    # Determine the pip path based on OS
    pip_path = "venv/Scripts/pip" if sys.platform == "win32" else "venv/bin/pip"
    
    print("Upgrading pip...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    
    print("Installing development dependencies...")
    subprocess.run([pip_path, "install", "-e", ".[dev]"], check=True)

def main():
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