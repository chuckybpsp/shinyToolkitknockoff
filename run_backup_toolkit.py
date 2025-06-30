#!/usr/bin/env python3
"""
Backup Toolkit Launcher
Ensures dependencies are installed and chooses the appropriate interface
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import schedule
        return True
    except ImportError:
        return False

def check_gui_support():
    """Check if GUI (tkinter) is available"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def main():
    print("Backup Toolkit Launcher")
    print("=" * 30)
    
    # Check GUI support
    gui_available = check_gui_support()
    
    if gui_available:
        print("GUI support detected. Launching GUI version...")
        # Check if dependencies are installed
        if not check_dependencies():
            print("Missing dependencies. Installing...")
            if not install_requirements():
                print("Failed to install dependencies. Please run: pip install -r requirements.txt")
                sys.exit(1)
        
        # Import and run the GUI backup toolkit
        try:
            from backup_toolkit import main as run_gui_toolkit
            run_gui_toolkit()
        except ImportError as e:
            print(f"Error importing GUI backup toolkit: {e}")
            print("Falling back to CLI version...")
            gui_available = False
    
    if not gui_available:
        print("No GUI support detected. Launching CLI version...")
        try:
            from backup_cli import main as run_cli_toolkit
            print("\nRunning in CLI mode. Use --help for available commands.")
            run_cli_toolkit()
        except ImportError as e:
            print(f"Error importing CLI backup toolkit: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()