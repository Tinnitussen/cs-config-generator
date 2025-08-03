import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).parent
utils_dir = script_dir.parent.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import (
    COMMANDS_JSON, CLASSIFIED_DIR, setup_rules_import,
    load_json, save_json, ensure_output_dirs
)

# Setup rules import
setup_rules_import()
from splitting_rules import get_command_category

def classify_commands(commands: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify commands into server, player, shared, and uncategorized
    using rules from an external file.
    """
    classified_commands = defaultdict(list)

    for command in commands:
        category = get_command_category(command)
        classified_commands[category].append(command)

    return dict(classified_commands)

def verify_data_integrity(original: List[Dict], classified: Dict[str, List[Dict]]):
    """
    Verify that the split data maintains integrity with the original.
    """
    original_count = len(original)
    classified_count = sum(len(commands) for commands in classified.values())

    if original_count != classified_count:
        print(f"Error: Command count mismatch. Original: {original_count}, Classified: {classified_count}")
        return False

    original_commands = {cmd['command'] for cmd in original}
    classified_commands = {cmd['command'] for commands in classified.values() for cmd in commands}

    if original_commands != classified_commands:
        print("Error: Command set mismatch.")
        missing = original_commands - classified_commands
        extra = classified_commands - original_commands
        if missing:
            print(f"Missing commands: {missing}")
        if extra:
            print(f"Extra commands: {extra}")
        return False

    return True

def main():
    """Main function to split commands into categories."""

    # Check if input file exists
    if not COMMANDS_JSON.exists():
        print(f"Error: Input file '{COMMANDS_JSON}' not found.")
        return 1

    # Ensure output directory exists
    ensure_output_dirs()

    print(f"Loading commands from '{COMMANDS_JSON}'...")
    commands = load_json(COMMANDS_JSON)

    print("Classifying commands using external rules...")
    classified_commands = classify_commands(commands)

    # Save the classified commands into separate files
    for category, command_list in classified_commands.items():
        output_file = CLASSIFIED_DIR / f"{category}_commands.json"
        print(f"Saving {len(command_list)} {category} commands to '{output_file}'...")
        save_json(command_list, output_file)

    print("\n--- CLASSIFICATION SUMMARY ---")
    total_commands = len(commands)
    print(f"Total commands processed: {total_commands}")
    for category, command_list in classified_commands.items():
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category.capitalize()}: {count} commands ({percentage:.1f}%)")

    print("\nVerifying data integrity...")
    if not verify_data_integrity(commands, classified_commands):
        print("Data integrity check failed. Aborting.")
        return 1
    print("Data integrity check passed.")

    print(f"\nClassified commands saved to: {CLASSIFIED_DIR}")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
