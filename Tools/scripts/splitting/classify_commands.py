import json
import os
import sys
from typing import Dict, List, Any
from collections import defaultdict

# --- Path setup ---
# Add the 'rules' directory to the Python path to import the classification rules.
# This makes the script runnable from any directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
rules_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'rules')
if rules_dir not in sys.path:
    sys.path.append(rules_dir)

from splitting_rules import get_command_category

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def classify_commands(commands: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify commands into server, player, shared, and uncategorized
    by using rules from an external file.
    """
    classified_commands = defaultdict(list)

    for command in commands:
        category = get_command_category(command)
        classified_commands[category].append(command)

    return dict(classified_commands)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(tools_dir, "data", "commands.json")
    output_dir = os.path.join(tools_dir, "data", "classified_commands")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)

    print("Classifying commands with new logic...")
    classified_commands = classify_commands(commands)

    # Save the classified commands into separate files
    for category, command_list in classified_commands.items():
        output_file = os.path.join(output_dir, f"{category}_commands.json")
        print(f"Saving {len(command_list)} {category} commands to '{output_file}'...")
        save_json(command_list, output_file)

    print("\n--- CLASSIFICATION SUMMARY ---")
    total_commands = len(commands)
    print(f"Total commands processed: {total_commands}")
    for category, command_list in classified_commands.items():
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category.capitalize()}: {count} commands ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
