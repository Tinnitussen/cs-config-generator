
#!/usr/bin/env python3
"""
CS Commands Processing Pipeline Runner

This script streamlines the entire pipeline process:
1. Parse commands from snapshot file
2. Classify command types
3. Split commands into categories
4. Subcategorize commands

Each step waits for user review before continuing.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_step(step_num, text):
    """Print a step header"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}Step {step_num}: {text}{Colors.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def wait_for_user_input(step_name):
    """
    Wait for user to review and continue or abort.
    Returns True to continue, False to abort.
    """
    # Non-interactive mode: always continue
    return True

def get_latest_command_file():
    """Find the most recent command snapshot file."""
    tools_dir = Path(__file__).parent
    data_dir = tools_dir / "data"

    pattern = str(data_dir / "all_commands-*.txt")
    files = glob.glob(pattern)

    if not files:
        print_error("No command snapshot files found in Tools/data/")
        print("Expected format: all_commands-YYYY-DD-MM.txt")
        return None

    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return Path(files[0])

def run_script(script_path, description, args=None):
    """
    Run a Python script and return success status.
    """
    if args is None:
        args = []

    cmd = [sys.executable, script_path] + args

    print(f"Running: {' '.join(cmd)}")
    print("-" * 40)

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=True)
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print_error(f"Script not found: {script_path}")
        return False

def main():
    """Main pipeline runner"""
    print_header("CS Commands Processing Pipeline")
    print("This will guide you through the complete command processing pipeline.")

    # Get the tools directory
    tools_dir = Path(__file__).parent
    scripts_dir = tools_dir / "scripts"
    splitting_dir = scripts_dir / "splitting"
    subcategorization_dir = splitting_dir / "subcategorization"
    data_dir = tools_dir / "data"

    # Step 0: Select input file
    print_step(0, "Finding latest command snapshot file")
    latest_file_path = get_latest_command_file()
    if not latest_file_path:
        return 1

    print_success(f"Using: {latest_file_path.name}")

    # Step 1: Parse commands
    print_step(1, "Parse Commands")
    parse_script = scripts_dir / "parse_commands.py"
    # Pass absolute path to the script
    if not run_script(str(parse_script), "Command parsing", args=[str(latest_file_path)]):
        return 1

    # Step 2: Classify command types
    print_step(2, "Classify Command Types")
    classification_script = scripts_dir / "command_classification.py"
    if not run_script(str(classification_script), "Command type classification"):
        return 1

    # Step 3: Split commands into categories
    print_step(3, "Split Commands into Categories")
    split_script = splitting_dir / "classify_commands.py"
    if not run_script(str(split_script), "Command category splitting"):
        return 1

    # Step 4: Subcategorize commands
    print_step(4, "Subcategorize Commands")

    subcategorization_scripts = [
        ("subcategorize_player.py", "Player subcategorization"),
        ("subcategorize_server.py", "Server subcategorization"),
        ("subcategorize_shared.py", "Shared subcategorization")
    ]

    for script_name, description in subcategorization_scripts:
        script_path = subcategorization_dir / script_name
        print(f"\n{Colors.OKCYAN}Running {description}...{Colors.ENDC}")
        if not run_script(str(script_path), description):
            return 1

    # Pipeline complete
    print_header("Pipeline Complete!")
    print_success("All steps completed successfully!")
    print(f"\n{Colors.OKGREEN}Commands have been processed and are ready for use.{Colors.ENDC}")
    print(f"\nOutput locations:")
    print(f"  • Main commands file: Tools/data/commands.json")
    print(f"  • Split commands: Tools/data/classified_commands/")
    print(f"  • Subcategorized commands: CSConfigGenerator/wwwroot/data/commandschema/")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Pipeline interrupted by user.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
