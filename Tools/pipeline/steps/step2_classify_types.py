"""
Pipeline Step 2: Classify command types and add UI data.

This script reads the main `commands.json` file, and for each command,
it adds a `uiData` object and determines its data type (e.g., bool,
float, action) based on a set of ordered rules.
"""
import json
import os
import sys
import argparse
from typing import Dict, List, Any

def _create_ui_data_skeleton(command: Dict) -> Dict:
    """Creates a lean, base uiData object with default values."""
    return {
        "label": command["command"],
        "helperText": command["consoleData"]["description"],
        "type": "unknown",
        "defaultValue": 0,  # Generic placeholder, always overwritten
        "requiresCheats": "cheat" in command["consoleData"]["flags"],
        "hideFromDefaultView": True
    }

def classify_command_types(commands_file: str, reclassify_all: bool = False):
    """
    Adds a uiData skeleton to each command and classifies its type using
    an ordered set of rules from an external file. Modifies the file in-place.
    By default, this is non-destructive and will not overwrite existing uiData.

    Args:
        commands_file (str): Path to the commands.json file.
        reclassify_all (bool): If True, re-classify all commands, overwriting existing uiData types.
    """
    # --- Path setup for rules ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = os.path.join(script_dir, '..', '..', 'rules')
    if rules_dir not in sys.path:
        sys.path.append(rules_dir)
    from type_classification_rules import CLASSIFICATION_RULES

    # --- Load and Process ---
    with open(commands_file, 'r', encoding='utf-8') as f:
        commands = json.load(f)

    processed_commands = []
    type_counts = {}
    updated_count = 0
    skipped_count = 0

    for cmd in commands:
        # If not re-classifying, skip any command that already has a 'type' defined.
        if not reclassify_all and cmd.get('uiData', {}).get('type') not in [None, 'unknown']:
            skipped_count += 1
            type_counts[cmd['uiData']['type']] = type_counts.get(cmd['uiData']['type'], 0) + 1
            processed_commands.append(cmd)
            continue

        # Ensure uiData exists before modifying it
        if 'uiData' not in cmd:
            cmd['uiData'] = _create_ui_data_skeleton(cmd)

        cmd_type = "unknown"
        ui_default: Any = None

        for rule in CLASSIFICATION_RULES:
            result = rule(cmd)
            if result:
                cmd_type, ui_default = result
                break

        # Only update the type and default value, preserving other fields
        cmd['uiData']['type'] = cmd_type
        cmd['uiData']['defaultValue'] = ui_default

        # Conditionally add type-specific placeholders if they don't already exist
        if cmd_type == 'float' and 'range' not in cmd['uiData']:
            cmd['uiData']['range'] = {"minValue": -1, "maxValue": -1, "step": -1}
        elif cmd_type == 'bitmask' and 'options' not in cmd['uiData']:
            cmd['uiData']['options'] = {}
        elif cmd_type == 'action' and 'arguments' not in cmd['uiData']:
            cmd['uiData']['arguments'] = []

        processed_commands.append(cmd)
        type_counts[cmd_type] = type_counts.get(cmd_type, 0) + 1
        updated_count += 1

    # --- Save and Summarize ---
    with open(commands_file, 'w', encoding='utf-8') as f:
        json.dump(processed_commands, f, indent=2)

    total = len(commands)
    auto_classified = sum(v for k, v in type_counts.items() if k not in ['unknown', 'unknown_integer'])
    unknown_total = type_counts.get('unknown', 0) + type_counts.get('unknown_integer', 0)

    print("\n--- Type Classification Summary ---")
    print(f"Total commands processed: {total}")
    print(f"Commands updated/classified in this run: {updated_count}")
    print(f"Commands skipped (already classified): {skipped_count}")
    print(f"Auto-classified: {auto_classified} ({auto_classified/total*100:.1f}%)")
    print(f"Marked as 'unknown' for manual review: {unknown_total} ({unknown_total/total*100:.1f}%)")

    print("\nClassification breakdown:")
    for cmd_type, count in sorted(type_counts.items()):
        print(f"  - {cmd_type.replace('_', ' ').capitalize()}: {count}")

    print(f"\nOutput file updated: {commands_file}")

def main():
    """For testing this step independently."""
    parser = argparse.ArgumentParser(description="Classify command types and generate UI schema skeletons.")
    parser.add_argument(
        '--reclassify-all',
        action='store_true',
        help="If set, the script will re-classify all commands, overwriting any existing classifications."
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    commands_file = os.path.join(repo_root, 'Tools', 'data', 'commands.json')

    if not os.path.exists(commands_file):
        print(f"Error: Input file not found at '{commands_file}'.")
        print("Please run Step 1 (parse) first or ensure you are in the repo root.")
        return

    if args.reclassify_all:
        print("Re-classifying all commands...")
    else:
        print("Classifying new commands and building schema skeleton...")

    classify_command_types(commands_file, args.reclassify_all)

if __name__ == "__main__":
    main()