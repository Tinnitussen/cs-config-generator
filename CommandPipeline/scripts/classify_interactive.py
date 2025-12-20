#!/usr/bin/env python3
"""
Interactive Command Classification Tool

This tool allows human review and classification of unknown command types.
Classifications are saved to manual_type_overrides.json.

Features:
- Progress tracking with save/resume
- Validation of incompatible classifications
- Filter by pattern (e.g., show all *_time commands)
- Batch skip functionality

Usage:
  python classify_interactive.py [--filter PATTERN] [--reset-progress]
"""

import json
import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- Path setup ---
script_dir = Path(__file__).resolve().parent
utils_dir = script_dir.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import COMMANDS_JSON

# --- Constants ---
VALID_TYPES = ['int', 'float', 'bool', 'string', 'command', 'bitmask', 'unknown', 
               'color', 'uint32', 'uint64', 'vector2', 'vector3']

TYPE_SHORTCUTS = {
    '1': 'int',
    '2': 'float',
    '3': 'bool',
    '4': 'string',
    '5': 'command',
    '6': 'bitmask',
    '7': 'unknown',
    '8': 'color',
    '9': 'uint32',
    '0': 'uint64',
    'v2': 'vector2',
    'v3': 'vector3',
}

ALLOWED_BOOL_VALUES = {'0', '1', 'true', 'false', 'yes', 'no', 'on', 'off'}


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_commands() -> List[Dict]:
    """Load commands from commands.json."""
    if not COMMANDS_JSON.exists():
        print(f"{Colors.RED}Error: commands.json not found at {COMMANDS_JSON}{Colors.ENDC}")
        sys.exit(1)
    
    with open(COMMANDS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_manual_overrides(data_dir: Path) -> Dict[str, str]:
    """Load existing manual overrides."""
    overrides_path = data_dir / 'manual_type_overrides.json'
    if not overrides_path.exists():
        return {}
    
    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
    
    # Filter out comment keys
    return {k: v for k, v in overrides.items() if not k.startswith('_')}


def save_manual_overrides(data_dir: Path, overrides: Dict[str, str]):
    """Save manual overrides to file."""
    overrides_path = data_dir / 'manual_type_overrides.json'
    
    # Preserve comment if it exists
    full_data = {"_comment": "Manual type overrides for commands where automated classification needs correction. Takes precedence over all other sources."}
    full_data.update(dict(sorted(overrides.items())))
    
    with open(overrides_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2)


def load_progress(data_dir: Path) -> set:
    """Load progress (which commands have been reviewed)."""
    progress_path = data_dir / '.classification_progress.json'
    if not progress_path.exists():
        return set()
    
    with open(progress_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return set(data.get('reviewed', []))


def save_progress(data_dir: Path, reviewed: set):
    """Save progress to file."""
    progress_path = data_dir / '.classification_progress.json'
    
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump({'reviewed': sorted(list(reviewed))}, f, indent=2)


def validate_classification(cmd_type: str, default_value: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that a classification is compatible with the command's default value.
    Returns (is_valid, error_message).
    """
    if default_value is None:
        # No default value - must be a command
        if cmd_type != 'command' and cmd_type != 'unknown':
            return False, f"No default value - only 'command' or 'unknown' is valid"
        return True, None
    
    # Has a default value - cannot be a command
    if cmd_type == 'command':
        return False, f"Has default value '{default_value}' - cannot be 'command'"
    
    # Bool validation
    if cmd_type == 'bool':
        if default_value.lower() not in ALLOWED_BOOL_VALUES:
            return False, f"Default '{default_value}' is not boolean-compatible"
    
    # Float/int validation for obviously non-numeric defaults
    if cmd_type in ('int', 'float', 'uint32', 'uint64'):
        # Check if default is clearly non-numeric (contains letters other than e for scientific notation)
        cleaned = default_value.replace('.', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '')
        if cleaned and not cleaned.isdigit():
            # Could be a space-separated list (vector) or a string
            parts = default_value.split()
            if not all(is_numeric(p) for p in parts):
                return False, f"Default '{default_value}' is not numeric"
    
    # Vector validation
    if cmd_type in ('vector2', 'vector3'):
        parts = default_value.split()
        expected_count = 2 if cmd_type == 'vector2' else 3
        if len(parts) != expected_count:
            return False, f"Default '{default_value}' doesn't have {expected_count} components"
        if not all(is_numeric(p) for p in parts):
            return False, f"Default '{default_value}' components are not all numeric"
    
    return True, None


def is_numeric(value: str) -> bool:
    """Check if a string is a valid number."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_unknown_commands(commands: List[Dict], overrides: Dict[str, str], 
                         reviewed: set, filter_pattern: Optional[str] = None) -> List[Dict]:
    """Get list of commands that are currently 'unknown' and not yet reviewed."""
    unknown = []
    
    for cmd in commands:
        cmd_name = cmd.get('command', '')
        type_info = cmd.get('typeInfo', {})
        current_type = type_info.get('type', 'unknown')
        
        # Skip if already has a manual override
        if cmd_name in overrides:
            continue
        
        # Skip if already reviewed (but not classified - user skipped)
        if cmd_name in reviewed:
            continue
        
        # Only include unknown types
        if current_type != 'unknown':
            continue
        
        # Apply filter if specified
        if filter_pattern:
            if not re.search(filter_pattern, cmd_name, re.IGNORECASE):
                continue
        
        unknown.append(cmd)
    
    return unknown


def display_command(cmd: Dict, index: int, total: int):
    """Display command details for classification."""
    cmd_name = cmd.get('command', '')
    console_data = cmd.get('consoleData', {})
    default_value = console_data.get('defaultValue')
    description = console_data.get('description', '')
    flags = console_data.get('flags', [])
    
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}Command Classification Tool{Colors.ENDC}")
    print(f"{Colors.CYAN}Progress: {index + 1}/{total} commands remaining{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Command:{Colors.ENDC} {Colors.GREEN}{cmd_name}{Colors.ENDC}")
    
    if default_value is not None:
        print(f"{Colors.BOLD}Default:{Colors.ENDC}  {Colors.YELLOW}\"{default_value}\"{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}Default:{Colors.ENDC}  {Colors.DIM}(null - this is a command, not a variable){Colors.ENDC}")
    
    if description:
        # Wrap long descriptions
        if len(description) > 65:
            print(f"{Colors.BOLD}Desc:{Colors.ENDC}     {description[:65]}...")
            print(f"          {description[65:]}")
        else:
            print(f"{Colors.BOLD}Desc:{Colors.ENDC}     {description}")
    else:
        print(f"{Colors.BOLD}Desc:{Colors.ENDC}     {Colors.DIM}(no description){Colors.ENDC}")
    
    if flags:
        print(f"{Colors.BOLD}Flags:{Colors.ENDC}    {', '.join(flags)}")
    
    print(f"\n{Colors.HEADER}{'-' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}Select type:{Colors.ENDC}")
    print(f"  [1] int       [2] float     [3] bool      [4] string")
    print(f"  [5] command   [6] bitmask   [7] unknown   [8] color")
    print(f"  [9] uint32    [0] uint64    [v2] vector2  [v3] vector3")
    print(f"\n{Colors.DIM}Commands: [s]kip  [b]ack  [q]uit & save{Colors.ENDC}")
    print(f"{Colors.HEADER}{'-' * 70}{Colors.ENDC}")


def get_user_input() -> str:
    """Get user input for classification."""
    try:
        return input(f"\n{Colors.CYAN}Your choice: {Colors.ENDC}").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return 'q'


def main():
    parser = argparse.ArgumentParser(description="Interactive command classification tool")
    parser.add_argument('--filter', '-f', type=str, help="Filter commands by regex pattern (e.g., '_time$')")
    parser.add_argument('--reset-progress', action='store_true', help="Reset progress and start from beginning")
    parser.add_argument('--list-only', action='store_true', help="Just list unknown commands, don't classify")
    args = parser.parse_args()
    
    # Setup paths
    data_dir = script_dir.parent / 'data'
    
    # Load data
    print(f"{Colors.CYAN}Loading commands...{Colors.ENDC}")
    commands = load_commands()
    overrides = load_manual_overrides(data_dir)
    
    if args.reset_progress:
        reviewed = set()
        print(f"{Colors.YELLOW}Progress reset.{Colors.ENDC}")
    else:
        reviewed = load_progress(data_dir)
    
    # Get unknown commands
    unknown_commands = get_unknown_commands(commands, overrides, reviewed, args.filter)
    
    if not unknown_commands:
        print(f"\n{Colors.GREEN}No unknown commands to classify!{Colors.ENDC}")
        if args.filter:
            print(f"(Filter: {args.filter})")
        return 0
    
    print(f"\n{Colors.CYAN}Found {len(unknown_commands)} unknown commands to classify.{Colors.ENDC}")
    
    if args.list_only:
        print(f"\n{Colors.BOLD}Unknown commands:{Colors.ENDC}")
        for cmd in unknown_commands:
            cmd_name = cmd.get('command', '')
            default_value = cmd.get('consoleData', {}).get('defaultValue')
            print(f"  {cmd_name}: default={default_value!r}")
        return 0
    
    # Interactive classification loop
    index = 0
    session_classified = 0
    session_skipped = 0
    history = []  # For back navigation
    
    while index < len(unknown_commands):
        cmd = unknown_commands[index]
        cmd_name = cmd.get('command', '')
        console_data = cmd.get('consoleData', {})
        default_value = console_data.get('defaultValue')
        
        clear_screen()
        display_command(cmd, index, len(unknown_commands))
        
        user_input = get_user_input()
        
        if user_input == 'q':
            # Quit and save
            break
        
        elif user_input == 's':
            # Skip this command
            reviewed.add(cmd_name)
            history.append(('skip', cmd_name, None))
            session_skipped += 1
            index += 1
        
        elif user_input == 'b':
            # Go back
            if history:
                action, prev_cmd, prev_type = history.pop()
                if action == 'classify':
                    # Remove the classification
                    if prev_cmd in overrides:
                        del overrides[prev_cmd]
                    session_classified -= 1
                elif action == 'skip':
                    reviewed.discard(prev_cmd)
                    session_skipped -= 1
                index = max(0, index - 1)
            else:
                print(f"{Colors.YELLOW}No history to go back to.{Colors.ENDC}")
                input("Press Enter to continue...")
        
        elif user_input in TYPE_SHORTCUTS:
            # Classification
            selected_type = TYPE_SHORTCUTS[user_input]
            
            # Validate
            is_valid, error_msg = validate_classification(selected_type, default_value)
            
            if not is_valid:
                print(f"\n{Colors.RED}Invalid classification: {error_msg}{Colors.ENDC}")
                print(f"{Colors.YELLOW}Press Enter to try again, or 's' to skip...{Colors.ENDC}")
                retry = input().strip().lower()
                if retry == 's':
                    reviewed.add(cmd_name)
                    history.append(('skip', cmd_name, None))
                    session_skipped += 1
                    index += 1
                continue
            
            # Apply classification
            overrides[cmd_name] = selected_type
            reviewed.add(cmd_name)
            history.append(('classify', cmd_name, selected_type))
            session_classified += 1
            index += 1
            
            print(f"\n{Colors.GREEN}Classified {cmd_name} as {selected_type}{Colors.ENDC}")
        
        elif user_input in VALID_TYPES:
            # Direct type name input
            selected_type = user_input
            
            # Validate
            is_valid, error_msg = validate_classification(selected_type, default_value)
            
            if not is_valid:
                print(f"\n{Colors.RED}Invalid classification: {error_msg}{Colors.ENDC}")
                input("Press Enter to continue...")
                continue
            
            # Apply classification
            overrides[cmd_name] = selected_type
            reviewed.add(cmd_name)
            history.append(('classify', cmd_name, selected_type))
            session_classified += 1
            index += 1
        
        else:
            print(f"\n{Colors.RED}Unknown input: '{user_input}'{Colors.ENDC}")
            input("Press Enter to continue...")
    
    # Save on exit
    print(f"\n{Colors.CYAN}Saving progress...{Colors.ENDC}")
    save_manual_overrides(data_dir, overrides)
    save_progress(data_dir, reviewed)
    
    # Summary
    print(f"\n{Colors.HEADER}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}Session Summary{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 50}{Colors.ENDC}")
    print(f"Commands classified: {Colors.GREEN}{session_classified}{Colors.ENDC}")
    print(f"Commands skipped:    {Colors.YELLOW}{session_skipped}{Colors.ENDC}")
    print(f"Total in overrides:  {len(overrides)}")
    print(f"Remaining unknown:   {len(unknown_commands) - index}")
    print(f"\n{Colors.GREEN}Progress saved. Run again to continue.{Colors.ENDC}")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Aborted.{Colors.ENDC}")
        sys.exit(1)

