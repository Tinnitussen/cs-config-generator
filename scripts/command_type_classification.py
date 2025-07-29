import json
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the parsed_commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_numeric_string(value: Any) -> bool:
    """Check if a string-like value represents a number."""
    if value is None:
        return False
    value_str = str(value)
    if value_str.isspace() or value_str == "":
        return False
    if ' ' in value_str:
        return False
    try:
        float(value_str)
        return True
    except (ValueError, TypeError):
        return False

def create_ui_data_skeleton(command: Dict) -> Dict:
    """Creates a lean, base uiData object with default values."""
    return {
        "label": command["command"],
        "helperText": command["consoleData"]["description"],
        "type": "unknown",
        "defaultValue": 0, # Generic placeholder, always overwritten
        "requiresCheats": "cheat" in command["consoleData"]["flags"],
        "hideFromDefaultView": False
    }

def add_type_classification(commands: List[Dict]) -> tuple[List[Dict], Dict]:
    """
    Adds a uiData skeleton to each command and classifies its type using
    a conservative and reliable set of rules.
    """
    processed_commands = []
    type_counts = {}
    
    for cmd in commands:
        cmd['uiData'] = create_ui_data_skeleton(cmd)
        
        console_default = cmd['consoleData']['defaultValue']
        description = cmd['consoleData']['description'].lower()

        cmd_type = "unknown"
        ui_default: Any = None

        # Rule 1: Null default is an 'action'.
        if console_default is None:
            cmd_type = 'action'
            ui_default = None
        
        # Rule 2: 'true'/'false' or '0'/'1' with a boolean-like description are 'bool'.
        elif str(console_default).lower() in ['true', 'false']:
            cmd_type = 'bool'
            default_str = str(console_default).lower()
            ui_default = default_str == 'true' or default_str == '1'

        # Rule 3: Description contains "bitmask". This is a very strong indicator.
        elif 'bitmask' in description:
            cmd_type = 'bitmask'
            ui_default = int(console_default) if is_numeric_string(console_default) else 0

        # Rule 4 (REVISED): Numeric values.
        elif is_numeric_string(console_default):
            # If it contains a decimal, it's definitively a float.
            if '.' in str(console_default):
                cmd_type = 'float'
                ui_default = float(console_default)
            # Otherwise, it's an ambiguous number that needs review.
            else:
                cmd_type = 'unknown_numeric'
                ui_default = int(float(console_default))

        # Rule 5 (NEW): If it's not null, not boolean-like, and not numeric, it's a string.
        else:
            cmd_type = 'string'
            ui_default = console_default

        # Update uiData with classification results
        cmd['uiData']['type'] = cmd_type
        cmd['uiData']['defaultValue'] = ui_default

        # Conditionally add type-specific placeholders
        if cmd_type == 'float':
            cmd['uiData']['range'] = {"minValue": 0, "maxValue": 0, "step": 0}
        elif cmd_type == 'bitmask':
            cmd['uiData']['options'] = {}
        elif cmd_type == 'action':
            cmd['uiData']['arguments'] = []

        processed_commands.append(cmd)
        type_counts[cmd_type] = type_counts.get(cmd_type, 0) + 1
            
    return processed_commands, type_counts

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    input_file = "data/parsed_commands.json"
    output_file = "data/commands_with_types.json"
    
    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)
    
    print("Classifying command types and building schema skeleton...")
    processed_commands, type_counts = add_type_classification(commands)
    
    print(f"Saving file to '{output_file}'...")
    save_json(processed_commands, output_file)
    
    total = len(commands)
    auto_classified = sum(v for k, v in type_counts.items() if 'unknown' not in k)
    unknown_total = total - auto_classified

    print("\n--- SCRIPT EXECUTION SUMMARY ---")
    print(f"Total commands processed: {total}")
    print(f"Auto-classified: {auto_classified} ({auto_classified/total*100:.1f}%)")
    print(f"Marked as 'unknown' for manual review: {unknown_total} ({unknown_total/total*100:.1f}%)")
    
    print("\nClassification breakdown:")
    for cmd_type, count in sorted(type_counts.items()):
        print(f"  - {cmd_type.replace('_', ' ').capitalize()}: {count}")
    
    print(f"\nOutput file created: {output_file}")


if __name__ == "__main__":
    main()