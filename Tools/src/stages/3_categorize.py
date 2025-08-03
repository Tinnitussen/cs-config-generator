import json
import os
import sys
from typing import Dict, List, Any
from collections import defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from rules.categorization_rules import get_command_category

def load_commands(filepath: Path) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], filepath: Path):
    """Save data to JSON file"""
    # Create output directory if it doesn't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)
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
    tools_dir = Path(__file__).parent.parent.parent
    data_dir = tools_dir / "data"
    input_file = data_dir / "commands.json"
    output_dir = data_dir / "classified_commands"

    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)

    print("Classifying commands with new logic...")
    classified_commands = classify_commands(commands)

    # Save the classified commands into separate files
    for category, command_list in classified_commands.items():
        output_file = output_dir / f"{category}_commands.json"
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
