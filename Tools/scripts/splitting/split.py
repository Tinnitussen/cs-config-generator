import json
import os
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_splitting_rules(filepath: str) -> Dict:
    """Load the splitting rules from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
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

    player_prefixes = rules["player_prefixes"]
    server_prefixes = rules["server_prefixes"]
    shared_prefixes = rules["shared_prefixes"]
    
    for command in commands:
        flags = command.get('consoleData', {}).get('flags', [])
        is_server = 'sv' in flags
        is_client = 'cl' in flags
        is_replicated = 'rep' in flags
        is_archived = 'a' in flags
        is_user = 'user' in flags
        command_name = command['command']
        prefix = get_prefix(command_name)

        if is_replicated or (is_server and is_client):
            classified_commands["shared"].append(command)
        elif is_server:
            classified_commands["server"].append(command)
        elif is_client:
            classified_commands["player"].append(command)
        elif prefix in player_prefixes:
            classified_commands["player"].append(command)
        elif prefix in server_prefixes:
            classified_commands["server"].append(command)
        elif prefix in shared_prefixes:
            classified_commands["shared"].append(command)
        elif is_archived or is_user:
            classified_commands["player"].append(command)
        else:
            classified_commands["uncategorized"].append(command)

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
    input_file = os.path.join(script_dir, "..", "..", "data", "commands.json")
    output_dir = os.path.join(script_dir, "..", "..", "data", "classified_commands")
    rules_file = os.path.join(script_dir, "..", "config", "splitting_rules.json")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)
    
    print(f"Loading splitting rules from '{rules_file}'...")
    rules = load_splitting_rules(rules_file)

    print("Classifying commands with new logic...")
    classified_commands = classify_commands(commands, rules)
    
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
