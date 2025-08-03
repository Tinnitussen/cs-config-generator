import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).parent
utils_dir = script_dir.parent.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import (
    COMMANDS_JSON, CONFIGS_DIR, setup_rules_import,
    load_json, save_json
)

# Setup rules import
setup_rules_import()
from numeric_detection_rules import classify_command_by_usage, UNKNOWN_TYPES, FLOAT_RATIO

# Configuration
MIN_OCCURRENCES = 4

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

def extract_command_values(cfg_path: Path) -> Dict[str, List[str]]:
    """Extract command values from a single config file"""
    cmd_values = defaultdict(list)

    try:
        with open(cfg_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("//", "#")):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    cmd, val = parts[0], clean_value(parts[1])
                    cmd_values[cmd].append(val)
    except Exception as e:
        print(f"Warning: Failed to process {cfg_path.name}: {e}")

    return cmd_values

def gather_all_values(configs_dir: Path, known_commands: set) -> Dict[str, List[str]]:
    """Gather all command values from all config files"""
    all_values = defaultdict(list)

    cfg_files = list(configs_dir.glob("*.cfg"))
    print(f"Processing {len(cfg_files)} config files...")

    for cfg_file in cfg_files:
        cmd_values = extract_command_values(cfg_file)

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

def find_anomalies(all_stats: List[CommandStats]) -> List[CommandStats]:
    """Find commands classified as non-float but used as float"""
    return [
        stats for stats in all_stats
        if (stats.float_ratio > FLOAT_RATIO and
            stats.current_type not in ("float",) + UNKNOWN_TYPES)
    ]

def print_sanity_check(all_stats: List[CommandStats]) -> None:
    """Print sanity check information for interesting classifications"""
    # Find commands that will be classified as float or unknown_integer
    float_candidates = []
    int_candidates = []

    for stats in all_stats:
        new_type = classify_command_by_usage(stats)
        if new_type == "float" and new_type != stats.current_type:
            float_candidates.append((stats, new_type))
        elif new_type == "unknown_integer" and new_type != stats.current_type:
            int_candidates.append((stats, new_type))

    print("Sanity check: Commands that will be reclassified")
    print(f"\nFloat candidates (showing up to 5):")
    for i, (stats, new_type) in enumerate(float_candidates[:5]):
        print(f"{stats.command}: {stats.current_type} -> {new_type}, "
              f"total={stats.total}, float_ratio={stats.float_ratio:.2f}, "
              f"sample_values={stats.values[:5]}")

    print(f"\nUnknown integer candidates (showing up to 5):")
    for i, (stats, new_type) in enumerate(int_candidates[:5]):
        print(f"{stats.command}: {stats.current_type} -> {new_type}, "
              f"total={stats.total}, all_int={stats.is_all_int}, "
              f"sample_values={stats.values[:5]}")

    print(f"\nSummary: {len(float_candidates)} float candidates, {len(int_candidates)} integer candidates")

def main():
    """Main function to detect and reclassify numeric command types."""

    # Verify required paths exist
    if not COMMANDS_JSON.exists():
        print(f"Error: Commands file not found at {COMMANDS_JSON}")
        return 1

    if not CONFIGS_DIR.exists():
        print(f"Error: Configs directory not found at {CONFIGS_DIR}")
        return 1

    # Load existing data
    print(f"Loading commands from {COMMANDS_JSON}...")
    commands_data = load_json(COMMANDS_JSON)
    known_commands = {entry["command"]: entry for entry in commands_data if "command" in entry}

    print(f"Loaded {len(known_commands)} commands")

    # Gather all values
    print("Gathering command values from config files...")
    all_values = gather_all_values(CONFIGS_DIR, set(known_commands.keys()))

    # Create stats for commands with enough occurrences
    all_stats = []
    for cmd, values in all_values.items():
        if len(values) >= MIN_OCCURRENCES:
            current_type = known_commands[cmd].get("uiData", {}).get("type", "unknown")
            stats = create_command_stats(cmd, values, current_type)
            all_stats.append(stats)

    print(f"Found {len(all_stats)} commands with >= {MIN_OCCURRENCES} occurrences")

    # Print sanity check
    print_sanity_check(all_stats)

    # Classify commands and track changes
    updated_float = 0
    updated_integer = 0
    anomalies = find_anomalies(all_stats)

    for stats in all_stats:
        new_type = classify_command_by_usage(stats)
        entry = known_commands[stats.command]

        # Update type if it changed
        if new_type != stats.current_type:
            entry.setdefault("uiData", {})["type"] = new_type

            if new_type == "float":
                updated_float += 1
            elif new_type == "unknown_integer":
                updated_integer += 1

    # Save updated commands
    print(f"Saving updated commands to {COMMANDS_JSON}...")
    save_json(commands_data, COMMANDS_JSON)

    # Print summary
    print(f"\nProcessing Summary:")
    print(f"- Processed {len(all_stats)} commands with enough occurrences")
    print(f"- Updated {updated_float} commands to type 'float'")
    print(f"- Updated {updated_integer} commands to type 'unknown_integer'")

    if anomalies:
        print(f"\nAnomalies found ({len(anomalies)} commands classified as non-float but used as float):")
        for stats in anomalies:
            print(f"  {stats.command}: type={stats.current_type}, "
                  f"float_ratio={stats.float_ratio:.2f}, occurrences={stats.total}")
    else:
        print("No anomalies found.")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
