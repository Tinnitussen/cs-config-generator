import json
import os
import os
import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CommandStats:
    """Statistics for a command's values"""
    command: str
    total: int
    float_count: int
    int_count: int
    values: List[str]
    current_type: str

    @property
    def float_ratio(self) -> float:
        return self.float_count / self.total if self.total > 0 else 0

    @property
    def is_all_int(self) -> bool:
        return self.int_count == self.total

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_value(val: str) -> str:
    """Remove quotes from value"""
    return val.strip('"\'')

def is_float(val: str) -> bool:
    """Check if value is a float"""
    val = clean_value(val)
    return bool(re.match(r"^-?\d+\.\d+$|^-?\d+e-?\d+$", val, re.IGNORECASE))

def is_int(val: str) -> bool:
    """Check if value is an integer"""
    val = clean_value(val)
    return bool(re.match(r"^-?\d+$", val))

def load_json(filepath: str) -> Any:
    """Load JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data: Any, filepath: str) -> None:
    """Save JSON file"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_command_values(cfg_path: str) -> Dict[str, List[str]]:
    """Extract command values from a single config file"""
    cmd_values = defaultdict(list)

    with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("//", "#")):
                continue

            parts = line.split()
            if len(parts) >= 2:
                cmd, val = parts[0], clean_value(parts[1])
                cmd_values[cmd].append(val)

    return cmd_values

def gather_all_values(configs_dir: str, known_commands: set) -> Dict[str, List[str]]:
    """Gather all command values from all config files"""
    all_values = defaultdict(list)

    cfg_files = [f for f in os.listdir(configs_dir) if f.endswith(".cfg")]

    for cfg_file in cfg_files:
        cfg_path = os.path.join(configs_dir, cfg_file)
        cmd_values = extract_command_values(cfg_path)

        for cmd, values in cmd_values.items():
            if cmd in known_commands:
                all_values[cmd].extend(values)

    return all_values

def create_command_stats(cmd: str, values: List[str], current_type: str) -> CommandStats:
    """Create CommandStats from raw values"""
    float_count = sum(1 for v in values if is_float(v))
    int_count = sum(1 for v in values if is_int(v))

    return CommandStats(
        command=cmd,
        total=len(values),
        float_count=float_count,
        int_count=int_count,
        values=sorted(set(values)),
        current_type=current_type
    )

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

def classify_command_from_pro_configs(stats: CommandStats, rules: Dict) -> str:
    """Determine the appropriate type for a command based on its stats"""
    numeric_rules = rules['numeric_detection_rules']

    if stats.current_type in numeric_rules['protected_types']:
        return stats.current_type

    if stats.float_ratio > numeric_rules['float_ratio']:
        return "float"

    if (stats.total >= numeric_rules['min_int_occurrences'] and
        stats.is_all_int and
        stats.current_type not in ("int", "unknown_integer")):
        return "unknown_integer"

    return stats.current_type

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "..", "data", "commands.json")
    output_file = os.path.join(script_dir, "..", "data", "commands.json")
    rules_file = os.path.join(script_dir, "config", "type_classification_rules.json")
    configs_dir = os.path.join(script_dir, "..", "data", "pro-player-configs", "unzipped-configs")
    
    print(f"Loading commands from '{input_file}'...")
    commands_data = load_json(input_file)
    known_commands = {entry["command"]: entry for entry in commands_data if "command" in entry}
    
    print(f"Loading classification rules from '{rules_file}'...")
    rules = load_json(rules_file)

    print("Classifying command types and building schema skeleton...")
    commands_data, type_counts, updated_count, skipped_count = add_type_classification(commands_data, rules)

    # --- Numeric Detection ---
    print("\n--- Analyzing Pro Player Configs for Numeric Types ---")
    all_values = gather_all_values(configs_dir, set(known_commands.keys()))
    
    all_stats = []
    for cmd, values in all_values.items():
        if len(values) >= rules['numeric_detection_rules']['min_occurrences']:
            current_type = known_commands[cmd].get("uiData", {}).get("type", "unknown")
            stats = create_command_stats(cmd, values, current_type)
            all_stats.append(stats)

    updated_float = 0
    updated_integer = 0
    for stats in all_stats:
        new_type = classify_command_from_pro_configs(stats, rules)
        entry = known_commands[stats.command]

        if new_type != stats.current_type:
            entry.setdefault("uiData", {})["type"] = new_type
            if new_type == "float":
                updated_float += 1
            elif new_type == "unknown_integer":
                updated_integer += 1
    
    print(f"Updated {updated_float} commands to type 'float'.")
    print(f"Updated {updated_integer} commands to type 'unknown_integer'.")

    # --- Command Popularity ---
    print("\n--- Analyzing Pro Player Configs for Command Popularity ---")
    cfg_files = [os.path.join(configs_dir, f) for f in os.listdir(configs_dir) if f.endswith(".cfg")]
    total_cfgs = len(cfg_files)
    command_counter = Counter()

    for cfg_path in cfg_files:
        cmds_in_cfg = extract_command_values(cfg_path)
        for cmd in cmds_in_cfg.keys():
            if cmd in known_commands:
                command_counter[cmd] += 1

    flagged_count = 0
    for entry in commands_data:
        cmd = entry.get("command")
        if not cmd:
            continue
        count = command_counter.get(cmd, 0)
        if total_cfgs > 0 and (count / total_cfgs) > rules['popularity_rules']['popularity_threshold']:
            if "uiData" in entry and entry["uiData"].get("hideFromDefaultView", True):
                entry["uiData"]["hideFromDefaultView"] = False
                flagged_count += 1
    
    print(f"Processed {total_cfgs} configs.")
    print(f"Commands flagged as hideFromDefaultView = False: {flagged_count}")

    print(f"\nSaving updated file to '{output_file}'...")
    save_json(commands_data, output_file)
    
    print(f"\nOutput file updated: {output_file}")


if __name__ == "__main__":
    main()