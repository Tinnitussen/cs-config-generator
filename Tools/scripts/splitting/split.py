import json
import os
from typing import Dict, List, Any

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

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    if command_name.startswith('+'):
        return '+'
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def load_rules(filepath: str) -> Dict:
    """Load categorization rules from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_command(command: Dict, rules: Dict) -> str:
    """Classify a single command based on the provided rules."""
    flags = set(command.get('consoleData', {}).get('flags', []))
    command_name = command['command']
    prefix = get_prefix(command_name)

    # Check flag-based rules first
    for category, conditions in rules["by_flag"].items():
        for condition in conditions:
            if set(condition["requires"]).issubset(flags):
                return category

    # Check prefix-based rules
    for category, prefixes in rules["by_prefix"].items():
        if prefix in prefixes:
            return category

    return "uncategorized"

def classify_commands(commands: List[Dict], rules: Dict) -> Dict[str, List[Dict]]:
    """
    Classify commands into server, player, shared, and uncategorized.
    """
    classified_commands = {
        "server": [],
        "player": [],
        "shared": [],
        "uncategorized": []
    }

    for command in commands:
        category = classify_command(command, rules)
        classified_commands[category].append(command)

    return classified_commands

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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "../../data/commands.json")
    output_dir = os.path.join(script_dir, "../../data/classified_commands")
    rules_file = os.path.join(script_dir, "../../rules/category_rules.json")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)

    print(f"Loading categorization rules from '{rules_file}'...")
    rules = load_rules(rules_file)
    
    print("Classifying commands with new logic...")
    classified_commands = classify_commands(commands, rules)
    
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

    print("\nVerifying data integrity...")
    if not verify_data_integrity(commands, classified_commands):
        print("Data integrity check failed. Aborting.")
        return
    print("Data integrity check passed.")

if __name__ == "__main__":
    main()
