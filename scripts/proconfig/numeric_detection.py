import os
import json
from collections import defaultdict
import re

COMMANDS_JSON = "data/commands_with_types.json"
CONFIGS_DIR = "data/pro-player-configs/unzipped-configs"
MIN_OCCURRENCES = 4
FLOAT_RATIO = 0.5
MIN_INT_OCCURRENCES = 15

UNKNOWN_TYPES = ("unknown", "unknown_numeric")

def clean_value(val):
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val

def is_float(val):
    val = clean_value(val)
    if re.match(r"^-?\d+\.\d+$", val):  # e.g. 2.0, -3.14
        return True
    if re.match(r"^-?\d+e-?\d+$", val, re.IGNORECASE):  # e.g. 1e-5
        return True
    return False

def is_int(val):
    val = clean_value(val)
    return re.match(r"^-?\d+$", val) is not None

def load_commands_with_types(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_commands_with_types(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_command_values_from_cfg(filepath):
    cmd_values = defaultdict(list)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            cmd, val = parts[0], clean_value(parts[1])
            cmd_values[cmd].append(val)
    return cmd_values

def main():
    commands_data = load_commands_with_types(COMMANDS_JSON)
    known_commands = {entry["command"]: entry for entry in commands_data if "command" in entry}

    # Gather all values for each command across all configs
    all_cmd_values = defaultdict(list)
    cfg_files = [
        os.path.join(CONFIGS_DIR, f)
        for f in os.listdir(CONFIGS_DIR)
        if f.endswith(".cfg")
    ]
    for cfg_path in cfg_files:
        cmd_vals = extract_command_values_from_cfg(cfg_path)
        for cmd, vals in cmd_vals.items():
            if cmd in known_commands:
                all_cmd_values[cmd].extend(vals)

    # Sanity check: print stats for each command with enough occurrences
    print("Sanity check: command stats (first 10 commands with enough occurrences):")
    sanity_count = 0
    for cmd, values in all_cmd_values.items():
        if len(values) < MIN_OCCURRENCES:
            continue
        float_count = sum(1 for v in values if is_float(v))
        int_count = sum(1 for v in values if is_int(v))
        print(
            f"{cmd}: total={len(values)}, float_count={float_count}, "
            f"int_count={int_count}, float_ratio={float_count/len(values):.2f}, "
            f"sample_values={values[:5]}"
        )
        sanity_count += 1
        if sanity_count >= 10:
            break

    updated_float = 0
    updated_unknown_int = 0
    anomalies = []
    classified = 0
    unknown_int_candidates = {}
    detected_floats = {}

    for cmd, values in all_cmd_values.items():
        if len(values) < MIN_OCCURRENCES:
            continue
        float_count = sum(1 for v in values if is_float(v))
        ratio = float_count / len(values)
        entry = known_commands[cmd]
        current_type = entry.get("uiData", {}).get("type", "unknown")
        # Detect anomaly: classified as non-float but used as float
        if ratio > FLOAT_RATIO and current_type not in ("float",) + UNKNOWN_TYPES:
            anomalies.append({
                "command": cmd,
                "current_type": current_type,
                "float_ratio": ratio,
                "occurrences": len(values)
            })
        # Classify as float if eligible
        if (
            ratio > FLOAT_RATIO
            and current_type not in ("float", "bool", "bitmask", "action")
        ):
            entry.setdefault("uiData", {})["type"] = "float"
            updated_float += 1
            detected_floats[cmd] = {
                "total": len(values),
                "float_count": float_count,
                "float_ratio": ratio,
                "values": list(sorted(set(values))),
                "current_type": current_type
            }
        # Classify as unknown_integer if eligible
        elif (
            len(values) >= MIN_INT_OCCURRENCES
            and all(is_int(v) for v in values)
            and current_type not in ("float", "int", "bool", "bitmask", "action", "unknown_integer")
        ):
            entry.setdefault("uiData", {})["type"] = "unknown_integer"
            updated_unknown_int += 1
            unknown_int_candidates[cmd] = {
                "total": len(values),
                "values": list(sorted(set(values))),
                "current_type": current_type
            }
        # Save all int candidates for debugging
        elif (
            len(values) >= MIN_INT_OCCURRENCES
            and all(is_int(v) for v in values)
        ):
            unknown_int_candidates[cmd] = {
                "total": len(values),
                "values": list(sorted(set(values))),
                "current_type": current_type,
                "skipped_reason": "type already set or not unknown"
            }
        classified += 1

    save_commands_with_types(commands_data, COMMANDS_JSON)
    # Save all int and float candidates for inspection
    with open("detected_unknown_integers.json", "w", encoding="utf-8") as f:
        json.dump(unknown_int_candidates, f, indent=2)
    with open("detected_floats.json", "w", encoding="utf-8") as f:
        json.dump(detected_floats, f, indent=2)

    print(f"Processed {classified} commands with enough occurrences.")
    print(f"Updated {updated_float} commands to type 'float'.")
    print(f"Updated {updated_unknown_int} commands to type 'unknown_integer'.")
    print(f"Saved int candidates to detected_unknown_integers.json")
    print(f"Saved float candidates to detected_floats.json")
    if anomalies:
        print("\nAnomalies found (classified as non-float but used as float in configs):")
        for a in anomalies:
            print(f"  {a['command']}: type={a['current_type']}, float_ratio={a['float_ratio']:.2f}, occurrences={a['occurrences']}")
    else:
        print("No anomalies found.")

if __name__ == "__main__":
    main()