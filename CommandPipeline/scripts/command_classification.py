import json
import os
import sys
import argparse
from typing import Dict, List, Any

# --- Path setup ---
# Add the 'rules' directory to the Python path to import the classification rules.
# This makes the script runnable from any directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
rules_dir = os.path.join(os.path.dirname(script_dir), 'rules')
if rules_dir not in sys.path:
    sys.path.append(rules_dir)

from type_classification_rules import CLASSIFICATION_RULES

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_ui_data_skeleton(command: Dict) -> Dict:
    """Creates a lean, base uiData object with default values."""
    return {
        "label": command["command"],
        "helperText": command["consoleData"]["description"],
        "type": "unknown",
        "defaultValue": 0, # Generic placeholder, always overwritten
        "requiresCheats": "cheat" in command["consoleData"]["flags"],
    }

def add_type_classification(commands: List[Dict], reclassify_all: bool = False) -> tuple[List[Dict], Dict, int, int]:
    """
    Adds a uiData skeleton to each command and classifies its type using
    an ordered set of rules from an external file.
    By default, it skips commands that already have a 'uiData' field.
    """
    processed_commands = []
    type_counts = {}
    updated_count = 0
    skipped_count = 0

    for cmd in commands:
        # If reclassify_all is False, skip commands that are already classified.
        if not reclassify_all and 'uiData' in cmd:
            skipped_count += 1
            type_counts[cmd['uiData'].get('type', 'unknown')] = type_counts.get(cmd['uiData'].get('type', 'unknown'), 0) + 1
            processed_commands.append(cmd)
            continue

        # Create or reset uiData
        cmd['uiData'] = create_ui_data_skeleton(cmd)

        cmd_type = "unknown"
        ui_default: Any = None

        # Apply rules from the external file in order
        for rule in CLASSIFICATION_RULES:
            result = rule(cmd)
            if result:
                cmd_type, ui_default = result
                break

        # Update uiData with classification results
        cmd['uiData']['type'] = cmd_type
        cmd['uiData']['defaultValue'] = ui_default

        # Conditionally add type-specific placeholders
        if cmd_type == 'float' and 'range' not in cmd['uiData']:
            cmd['uiData']['range'] = {"minValue": -1, "maxValue": -1, "step": -1}
        elif cmd_type == 'bitmask' and 'options' not in cmd['uiData']:
            cmd['uiData']['options'] = {}
        elif cmd_type == 'command' and 'arguments' not in cmd['uiData']:
            # Provide empty arguments list for command-type items (previously 'action')
            cmd['uiData']['arguments'] = []

        processed_commands.append(cmd)
        type_counts[cmd_type] = type_counts.get(cmd_type, 0) + 1
        updated_count += 1

    return processed_commands, type_counts, updated_count, skipped_count

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Classify commands and generate UI schema skeletons.")
    parser.add_argument(
        '--reclassify-all',
        action='store_true',
        help="If set, the script will re-classify all commands, overwriting any existing classifications."
    )
    args = parser.parse_args()

    # --- Path setup ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(script_dir)

    input_file = os.path.join(tools_dir, "data", "commands.json")
    output_file = os.path.join(tools_dir, "data", "commands.json")

    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)

    if args.reclassify_all:
        print("Re-classifying all commands...")
    else:
        print("Classifying new commands and building schema skeleton...")

    processed_commands, type_counts, updated_count, skipped_count = add_type_classification(commands, args.reclassify_all)

    print(f"Saving updated file to '{output_file}'...")
    save_json(processed_commands, output_file)

    total = len(commands)
    auto_classified = sum(v for k, v in type_counts.items() if 'unknown' not in k)
    unknown_total = type_counts.get('unknown', 0)

    print("\n--- SCRIPT EXECUTION SUMMARY ---")
    print(f"Total commands processed: {total}")
    print(f"Commands updated in this run: {updated_count}")
    print(f"Commands skipped (already classified): {skipped_count}")
    print(f"Auto-classified: {auto_classified} ({auto_classified/total*100:.1f}%)")
    print(f"Marked as 'unknown' for manual review: {unknown_total} ({unknown_total/total*100:.1f}%)")

    print("\nClassification breakdown:")
    for cmd_type, count in sorted(type_counts.items()):
        print(f"  - {cmd_type.replace('_', ' ').capitalize()}: {count}")

    print(f"\nOutput file updated: {output_file}")


if __name__ == "__main__":
    main()
