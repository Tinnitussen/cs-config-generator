import json
import os
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_classification_rules(filepath: str) -> Dict:
    """Load the classification rules from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_numeric_string(value: Any) -> bool:
    """Check if a string-like value represents a number."""
    try:
        float(value)
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
        "hideFromDefaultView": True
    }

def classify_command_type(command: Dict, rules: Dict) -> str:
    """Classify a single command based on the provided rules."""
    console_default = command['consoleData']['defaultValue']
    description = command['consoleData']['description'].lower()

    for rule in rules['rules']:
        key = rule.get('key')

        if key == 'defaultValue':
            value = rule.get('value')
            if value is None and console_default is None:
                return rule['type']
            if isinstance(value, list) and str(console_default).lower() in value:
                return rule['type']
            if rule.get('is_numeric') and is_numeric_string(console_default):
                if rule.get('contains_decimal') and '.' in str(console_default):
                    return rule['type']
                if not rule.get('contains_decimal') and '.' not in str(console_default):
                    return rule['type']

        elif key == 'description':
            if rule.get('contains') and rule['contains'] in description:
                return rule['type']

    return rules['default_type']

def add_type_classification(commands: List[Dict], rules: Dict) -> tuple[List[Dict], Dict, int, int]:
    """
    Adds a uiData skeleton to each command and classifies its type using
    a conservative and reliable set of rules. Only updates commands that
    don't already have type classification.
    """
    processed_commands = []
    type_counts = {}
    updated_count = 0
    skipped_count = 0
    
    for cmd in commands:
        if 'uiData' not in cmd:
            cmd['uiData'] = create_ui_data_skeleton(cmd)
        
        existing_type = cmd['uiData'].get('type')
        if existing_type != 'unknown':
            skipped_count += 1
            type_counts[existing_type] = type_counts.get(existing_type, 0) + 1
            processed_commands.append(cmd)
            continue
        
        cmd_type = classify_command_type(cmd, rules)

        console_default = cmd['consoleData']['defaultValue']
        ui_default: Any = console_default

        if cmd_type == 'action':
            ui_default = None
        elif cmd_type == 'bool':
            default_str = str(console_default).lower()
            ui_default = default_str == 'true' or default_str == '1'
        elif cmd_type == 'bitmask':
            ui_default = int(console_default) if is_numeric_string(console_default) else 0
        elif cmd_type == 'float':
            ui_default = float(console_default)
        elif cmd_type == 'unknown_numeric':
            ui_default = int(float(console_default))

        cmd['uiData']['type'] = cmd_type
        cmd['uiData']['defaultValue'] = ui_default

        if cmd_type == 'float' and 'range' not in cmd['uiData']:
            cmd['uiData']['range'] = {"minValue": -1, "maxValue": -1, "step": -1}
        elif cmd_type == 'bitmask' and 'options' not in cmd['uiData']:
            cmd['uiData']['options'] = {}
        elif cmd_type == 'action' and 'arguments' not in cmd['uiData']:
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "..", "data", "commands.json")
    output_file = os.path.join(script_dir, "..", "data", "commands.json")
    rules_file = os.path.join(script_dir, "config", "type_classification_rules.json")
    
    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)
    
    print(f"Loading classification rules from '{rules_file}'...")
    rules = load_classification_rules(rules_file)

    print("Classifying command types and building schema skeleton...")
    processed_commands, type_counts, updated_count, skipped_count = add_type_classification(commands, rules)
    
    print(f"Saving updated file to '{output_file}'...")
    save_json(processed_commands, output_file)
    
    total = len(commands)
    auto_classified = sum(v for k, v in type_counts.items() if 'unknown' not in k)
    unknown_total = type_counts.get('unknown', 0) + type_counts.get('unknown_numeric', 0)

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