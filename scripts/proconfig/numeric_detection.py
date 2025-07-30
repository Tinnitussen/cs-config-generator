import os
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any

# Configuration
COMMANDS_JSON = "data/commands_with_types.json"
CONFIGS_DIR = "data/pro-player-configs/unzipped-configs"
MIN_OCCURRENCES = 4
FLOAT_RATIO = 0.5
MIN_INT_OCCURRENCES = 15
UNKNOWN_TYPES = ("unknown", "unknown_numeric")
PROTECTED_TYPES = ("float", "bool", "bitmask", "action")

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

def classify_command(stats: CommandStats) -> str:
    """Determine the appropriate type for a command based on its stats"""
    # Don't reclassify protected types
    if stats.current_type in PROTECTED_TYPES:
        return stats.current_type
    
    # Classify as float if enough float usage
    if stats.float_ratio > FLOAT_RATIO:
        return "float"
    
    # Classify as unknown_integer if all values are integers and enough occurrences
    if (stats.total >= MIN_INT_OCCURRENCES and 
        stats.is_all_int and 
        stats.current_type not in ("int", "unknown_integer")):
        return "unknown_integer"
    
    return stats.current_type

def find_anomalies(all_stats: List[CommandStats]) -> List[CommandStats]:
    """Find commands classified as non-float but used as float"""
    return [
        stats for stats in all_stats
        if (stats.float_ratio > FLOAT_RATIO and 
            stats.current_type not in ("float",) + UNKNOWN_TYPES)
    ]

def print_sanity_check(all_stats: List[CommandStats], limit: int = 10) -> None:
    """Print sanity check information"""
    print("Sanity check: command stats (first 10 commands with enough occurrences):")
    
    count = 0
    for stats in all_stats:
        if count >= limit:
            break
        
        print(f"{stats.command}: total={stats.total}, float_count={stats.float_count}, "
              f"int_count={stats.int_count}, float_ratio={stats.float_ratio:.2f}, "
              f"sample_values={stats.values[:5]}")
        count += 1

def main():
    # Load existing data
    commands_data = load_json(COMMANDS_JSON)
    known_commands = {entry["command"]: entry for entry in commands_data if "command" in entry}
    
    # Gather all values
    all_values = gather_all_values(CONFIGS_DIR, set(known_commands.keys()))
    
    # Create stats for commands with enough occurrences
    all_stats = []
    for cmd, values in all_values.items():
        if len(values) >= MIN_OCCURRENCES:
            current_type = known_commands[cmd].get("uiData", {}).get("type", "unknown")
            stats = create_command_stats(cmd, values, current_type)
            all_stats.append(stats)
    
    # Print sanity check
    print_sanity_check(all_stats)
    
    # Classify commands and track changes
    results = {"floats": {}, "integers": {}, "updated_float": 0, "updated_integer": 0}
    anomalies = find_anomalies(all_stats)
    
    for stats in all_stats:
        new_type = classify_command(stats)
        entry = known_commands[stats.command]
        
        # Update type if it changed
        if new_type != stats.current_type:
            entry.setdefault("uiData", {})["type"] = new_type
            
            if new_type == "float":
                results["updated_float"] += 1
                results["floats"][stats.command] = {
                    "total": stats.total,
                    "float_count": stats.float_count,
                    "float_ratio": stats.float_ratio,
                    "values": stats.values,
                    "current_type": stats.current_type
                }
            elif new_type == "unknown_integer":
                results["updated_integer"] += 1
                results["integers"][stats.command] = {
                    "total": stats.total,
                    "values": stats.values,
                    "current_type": stats.current_type
                }
    
    # Save results
    save_json(commands_data, COMMANDS_JSON)
    save_json(results["integers"], "detected_unknown_integers.json")
    save_json(results["floats"], "detected_floats.json")
    
    # Print summary
    print(f"\nProcessed {len(all_stats)} commands with enough occurrences.")
    print(f"Updated {results['updated_float']} commands to type 'float'.")
    print(f"Updated {results['updated_integer']} commands to type 'unknown_integer'.")
    print("Saved int candidates to detected_unknown_integers.json")
    print("Saved float candidates to detected_floats.json")
    
    if anomalies:
        print("\nAnomalies found (classified as non-float but used as float in configs):")
        for stats in anomalies:
            print(f"  {stats.command}: type={stats.current_type}, "
                  f"float_ratio={stats.float_ratio:.2f}, occurrences={stats.total}")
    else:
        print("No anomalies found.")

if __name__ == "__main__":
    main()