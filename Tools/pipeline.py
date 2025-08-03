
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
    print(f"\n{Colors.OKCYAN}Please review the {step_name} output above.{Colors.ENDC}")
    print("Press ENTER to continue, or 'q' + ENTER to quit: ", end="")

    user_input = input().strip().lower()
    if user_input in ['q', 'quit', 'exit']:
        print(f"{Colors.WARNING}Pipeline aborted by user.{Colors.ENDC}")
        return False
    return True

def find_command_files():
    """Find available command snapshot files"""
    tools_dir = Path(__file__).parent
    data_dir = tools_dir / "data"

    pattern = str(data_dir / "all_commands-*.txt")
    files = glob.glob(pattern)

    if not files:
        return []

    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return [Path(f).name for f in files]

def select_command_file():
    """Let user select a command snapshot file"""
    files = find_command_files()

    if not files:
        print_error("No command snapshot files found in Tools/data/")
        print("Expected format: all_commands-YYYY-DD-MM.txt")
        return None

    print(f"\n{Colors.OKBLUE}Available command snapshot files:{Colors.ENDC}")
    for i, filename in enumerate(files, 1):
        print(f"  {i}. {filename}")

    while True:
        try:
            print(f"\nSelect file (1-{len(files)}) or enter filename: ", end="")
            choice = input().strip()

            # Check if it's a number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    return files[idx]
                else:
                    print_error(f"Invalid selection. Please choose 1-{len(files)}")
                    continue

            # Check if it's a direct filename
            if choice in files:
                return choice

            # Check if the filename exists (with or without extension)
            if not choice.endswith('.txt'):
                choice += '.txt'
            if choice in files:
                return choice

            print_error("Invalid selection. Try again.")

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Aborted by user.{Colors.ENDC}")
            return None
        except ValueError:
            print_error("Invalid input. Please enter a number or filename.")

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

def update_script_input_file(script_path, new_filename):
    """
    Update the input filename in parse_commands.py
    """
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find and replace the input file line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'input_file = os.path.join(tools_dir, "data",' in line and 'all_commands-' in line:
                lines[i] = f'    input_file = os.path.join(tools_dir, "data", "{new_filename}")'
                break

        # Write back the modified content
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print_success(f"Updated {script_path} to use {new_filename}")
        return True

    except Exception as e:
        print_error(f"Failed to update script: {e}")
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

    # Step 0: Select input file
    print_step(0, "Select Command Snapshot File")
    selected_file = select_command_file()
    if not selected_file:
        return 1

    print_success(f"Selected: {selected_file}")

    # Update parse_commands.py with the selected file
    parse_script = scripts_dir / "parse_commands.py"
    if not update_script_input_file(parse_script, selected_file):
        return 1

    if not wait_for_user_input("file selection"):
        return 1

    # Step 1: Parse commands
    print_step(1, "Parse Commands")
    if not run_script(str(parse_script), "Command parsing"):
        return 1

    if not wait_for_user_input("command parsing"):
        return 1

    # Step 2: Classify command types
    print_step(2, "Classify Command Types")
    classification_script = scripts_dir / "command_classification.py"
    if not run_script(str(classification_script), "Command type classification"):
        return 1

    if not wait_for_user_input("command classification"):
        return 1

    # Step 3: Split commands into categories
    print_step(3, "Split Commands into Categories")
    split_script = splitting_dir / "classify_commands.py"
    if not run_script(str(split_script), "Command category splitting"):
        return 1

    if not wait_for_user_input("command splitting"):
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

    if not wait_for_user_input("subcategorization"):
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
