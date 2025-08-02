import json
import os
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rules(filepath: str) -> List[Dict]:
    """Load type classification rules from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_numeric_string(value: Any) -> bool:
    """Check if a string-like value represents a number."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def get_value_from_path(data: Dict, path: str) -> Any:
    """Safely gets a value from a nested dict using a dot-separated path."""
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def check_condition(command: Dict, condition: Dict) -> bool:
    """Checks if a command satisfies a single condition."""
    field_value = get_value_from_path(command, condition["field"])
    operator = condition["operator"]
    condition_value = condition.get("value")

    if operator == "is_null":
        return field_value is None
    if operator == "is_in_lower":
        return str(field_value).lower() in condition_value
    if operator == "contains_lower":
        return condition_value in str(field_value).lower()
    if operator == "is_numeric":
        return is_numeric_string(field_value)
    if operator == "contains":
        return condition_value in str(field_value)
    if operator == "contains_not":
        return condition_value not in str(field_value)

    return False

def classify_type_by_rules(command: Dict, rules: List[Dict]) -> str:
    """Classifies the command type based on a list of rules."""
    for rule in rules:
        if rule.get("default"):
            return rule["type"]

        conditions = rule.get("conditions", [])
        if all(check_condition(command, cond) for cond in conditions):
            return rule["type"]

    return "unknown" # Fallback if no rules match

def create_ui_data_skeleton(command: Dict) -> Dict:
    """Creates a lean, base uiData object with default values."""
    return {
        "label": command["command"],
        "helperText": command["consoleData"]["description"],
        "type": "unknown",
        "defaultValue": 0, # Generic placeholder, always overwritten
        "requiresCheats": "cheat" in command["consoleData"]["flags"]
    }

def add_type_classification(commands: List[Dict], rules: List[Dict]) -> tuple:
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
        
        if cmd['uiData'].get('type') != 'unknown':
            skipped_count += 1
            type_counts[cmd['uiData']['type']] = type_counts.get(cmd['uiData']['type'], 0) + 1
            processed_commands.append(cmd)
            continue

        cmd_type = classify_type_by_rules(cmd, rules)
        cmd['uiData']['type'] = cmd_type
        
        # Determine default value based on new type
        console_default = cmd['consoleData']['defaultValue']
        if cmd_type == 'action':
            cmd['uiData']['defaultValue'] = None
        elif cmd_type == 'bool':
            cmd['uiData']['defaultValue'] = str(console_default).lower() == 'true' or str(console_default).lower() == '1'
        elif cmd_type in ['bitmask', 'unknown_numeric', 'unknown_integer']:
            cmd['uiData']['defaultValue'] = int(float(console_default)) if is_numeric_string(console_default) else 0
        elif cmd_type == 'float':
            cmd['uiData']['defaultValue'] = float(console_default) if is_numeric_string(console_default) else 0.0
        else: # string
            cmd['uiData']['defaultValue'] = console_default

        # Add type-specific placeholders
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
    input_file = os.path.join(script_dir, "../data/commands.json")
    output_file = os.path.join(script_dir, "../data/commands.json")
    rules_file = os.path.join(script_dir, "../rules/type_rules.json")

    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)
    
    print(f"Loading type classification rules from '{rules_file}'...")
    rules = load_rules(rules_file)

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