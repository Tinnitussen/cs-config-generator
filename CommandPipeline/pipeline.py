#!/usr/bin/env python3
"""
CS Commands Processing Pipeline Runner

This script streamlines the entire pipeline process:
1. Parse commands from a snapshot file.
2. Classify command data types (bool, string, etc.).
3. Create a master data file for the 'All Commands' UI.

Each step waits for user review before continuing.
Can be run non-interactively with the --non-interactive flag.
"""

import sys
import subprocess
import argparse
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

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).resolve().parent
utils_dir = script_dir / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import find_snapshot_files

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

def wait_for_user_input(step_name, non_interactive=False):
    """
    Wait for user to review and continue or abort.
    Returns True to continue, False to abort.
    """
    if non_interactive:
        print(f"\n{Colors.OKCYAN}Non-interactive mode: skipping user input for {step_name}...{Colors.ENDC}")
        return True

    print(f"\n{Colors.OKCYAN}Please review the {step_name} output above.{Colors.ENDC}")
    print("Press ENTER to continue, or 'q' + ENTER to quit: ", end="")

    try:
        user_input = input().strip().lower()
        if user_input in ['q', 'quit', 'exit']:
            print(f"{Colors.WARNING}Pipeline aborted by user.{Colors.ENDC}")
            return False
        return True
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.WARNING}Aborted by user.{Colors.ENDC}")
        return False

def select_command_file(non_interactive=False):
    """Let user select a command snapshot file"""
    files = [p.name for p in find_snapshot_files()]

    if not files:
        print_error("No command snapshot files found in Tools/data/")
        print("Expected format: all_commands-YYYY-DD-MM.txt")
        return None

    if non_interactive:
        print_success(f"Non-interactive mode: auto-selecting newest file: {files[0]}")
        return files[0]

    print(f"\n{Colors.OKBLUE}Available command snapshot files:{Colors.ENDC}")
    for i, filename in enumerate(files, 1):
        print(f"  {i}. {filename}")

    while True:
        try:
            print(f"\nSelect file (1-{len(files)}) or enter filename: ", end="")
            choice = input().strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    return files[idx]
            elif choice in files:
                return choice

            print_error("Invalid selection. Try again.")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.WARNING}Aborted by user.{Colors.ENDC}")
            return None
        except ValueError:
            print_error("Invalid input. Please enter a number or filename.")

def run_script(script_path, description, args=None):
    """Run a Python script and return success status."""
    if args is None:
        args = []

    cmd = [sys.executable, str(script_path)] + args
    print(f"Running: {' '.join(cmd)}")
    print("-" * 40)

    try:
        subprocess.run(cmd, check=True, text=True)
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print_error(f"Script not found: {script_path}")
        return False

def main(args):
    """Main pipeline runner"""
    print_header("CS Commands Processing Pipeline")
    if args.non_interactive:
        print(f"{Colors.WARNING}Running in non-interactive mode.{Colors.ENDC}")

    tools_dir = Path(__file__).parent.resolve()
    scripts_dir = tools_dir / "scripts"

    # Step 0: Select input file
    print_step(0, "Select Command Snapshot File")
    selected_file = select_command_file(args.non_interactive)
    if not selected_file:
        return 1
    print_success(f"Selected: {selected_file}")
    if not wait_for_user_input("file selection", args.non_interactive):
        return 1

    # Step 1: Parse commands
    print_step(1, "Parse Commands from Snapshot")
    parse_script = scripts_dir / "parse_commands.py"
    if not run_script(parse_script, "Command parsing", [selected_file]):
        return 1
    if not wait_for_user_input("command parsing", args.non_interactive):
        return 1

    # Step 2: Classify command types
    print_step(2, "Classify Command Data Types")
    classification_script = scripts_dir / "command_classification.py"
    if not run_script(classification_script, "Command type classification"):
        return 1
    if not wait_for_user_input("command type classification", args.non_interactive):
        return 1

    # Step 3: Detect numeric types from configs
    print_step(3, "Detect Numeric Types from Configs")
    numeric_detection_script = scripts_dir / "numeric_detection.py"

    print(f"\n{Colors.OKCYAN}Running numeric detection for Player commands...{Colors.ENDC}")
    if not run_script(numeric_detection_script, "Player numeric type detection", ["--type", "player"]):
        return 1

    print(f"\n{Colors.OKCYAN}Running numeric detection for Server commands...{Colors.ENDC}")
    if not run_script(numeric_detection_script, "Server numeric type detection", ["--type", "server"]):
        return 1
    if not wait_for_user_input("numeric type detection", args.non_interactive):
        return 1


    # Step 3: Create All Commands Data for UI
    print_step(3, "Create 'All Commands' Data File")
    all_commands_script = scripts_dir / "create_all_commands.py"
    if not run_script(all_commands_script, "Create all_commands.json"):
        return 1
    if not wait_for_user_input("all commands data creation", args.non_interactive):
        return 1

    print_header("Pipeline Complete!")
    print_success("All steps completed successfully!")
    print(f"\n{Colors.OKGREEN}Commands have been processed and are ready for use.{Colors.ENDC}")
    print("\nOutput locations:")
    print("  • Main commands file: CommandPipeline/data/commands.json")
    print("  • UI command schema: CSConfigGenerator/wwwroot/data/commandschema/all/all_commands.json")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CS Commands Processing Pipeline Runner")
    parser.add_argument(
        '-n', '--non-interactive',
        action='store_true',
        help="Run the pipeline non-interactively, without user prompts."
    )
    args = parser.parse_args()

    try:
        exit_code = main(args)
        sys.exit(exit_code)
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        sys.exit(1)
