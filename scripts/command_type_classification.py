import json
from typing import Dict, List, Optional

def load_commands(filepath: str) -> List[Dict]:
    """Load the combined.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_numeric_string(value: str) -> bool:
    """Check if a string represents a number"""
    if not value:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_integer_string(value: str) -> bool:
    """Check if a string represents an integer"""
    if not value:
        return False
    try:
        val = float(value)
        return val.is_integer()
    except ValueError:
        return False

def classify_command_type(command: Dict) -> Optional[str]:
    """
    Classify a command, return type or None if needs manual review
    """
    default_val = command['consoleData']['defaultValue']
    
    # Rule 1: null defaultValue means it's an action
    if default_val is None:
        return 'action'
    
    # Rule 2: "true" or "false" are booleans
    if default_val in ['true', 'false']:
        return 'bool'
    
    # Rule 3: Decimal numbers are floats
    if is_numeric_string(default_val) and not is_integer_string(default_val):
        return 'float'
    
    # Everything else needs manual classification
    return None

def add_type_classification(commands: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """Add type classification to each command"""
    classified_commands = []
    manual_review_commands = []
    
    for cmd in commands:
        cmd_type = classify_command_type(cmd)
        
        if cmd_type is not None:
            # Add the type to uiData
            cmd['uiData'] = {'type': cmd_type}
            classified_commands.append(cmd)
        else:
            # Needs manual review
            manual_review_commands.append(cmd)
    
    return classified_commands, manual_review_commands

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    input_file = "data/parsed_commands.json"
    classified_output = "data/commands_with_types.json"
    manual_review_output = "data/manual_review.json"
    
    print("Loading commands...")
    commands = load_commands(input_file)
    
    print("Classifying command types...")
    classified_commands, manual_review_commands = add_type_classification(commands)
    
    print("Saving files...")
    save_json(classified_commands, classified_output)
    save_json(manual_review_commands, manual_review_output)
    
    # Print results
    total = len(commands)
    auto_classified = len(classified_commands)
    manual_needed = len(manual_review_commands)
    
    print(f"\nResults:")
    print(f"Total commands: {total}")
    print(f"Auto-classified: {auto_classified} ({auto_classified/total*100:.1f}%)")
    print(f"Need manual review: {manual_needed} ({manual_needed/total*100:.1f}%)")
    
    # Count by type
    type_counts = {}
    for cmd in classified_commands:
        cmd_type = cmd['uiData']['type']
        type_counts[cmd_type] = type_counts.get(cmd_type, 0) + 1
    
    print(f"\nAuto-classified breakdown:")
    for cmd_type, count in type_counts.items():
        print(f"  {cmd_type}: {count}")
    
    print(f"\nFiles created:")
    print(f"  {classified_output}")
    print(f"  {manual_review_output}")

if __name__ == "__main__":
    main()