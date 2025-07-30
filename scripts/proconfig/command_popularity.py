import os
import json
from collections import Counter

COMMANDS_JSON = "data/commands.json"
CONFIGS_DIR = "data/pro-player-configs/unzipped-configs"
POPULARITY_THRESHOLD = 0.10  # 10%

def load_commands_with_types(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_commands_with_types(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_commands_from_cfg(filepath):
    commands = set()
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            # Extract the first word (the command)
            cmd = line.split()[0]
            commands.add(cmd)
    return commands

def main():
    # 1. Load all known commands from commands.json
    commands_data = load_commands_with_types(COMMANDS_JSON)
    known_commands = set()
    for entry in commands_data:
        if "command" in entry:
            known_commands.add(entry["command"])

    # 2. Parse all configs and count command popularity
    cfg_files = [
        os.path.join(CONFIGS_DIR, f)
        for f in os.listdir(CONFIGS_DIR)
        if f.endswith(".cfg")
    ]
    total_cfgs = len(cfg_files)
    command_counter = Counter()

    for cfg_path in cfg_files:
        cmds_in_cfg = extract_commands_from_cfg(cfg_path)
        # Only count commands that are known
        for cmd in cmds_in_cfg:
            if cmd in known_commands:
                command_counter[cmd] += 1

    # 3. Mark commands as popular if they appear in >10% of configs
    flagged_count = 0
    for entry in commands_data:
        cmd = entry.get("command")
        if not cmd:
            continue
        count = command_counter.get(cmd, 0)
        if total_cfgs > 0 and (count / total_cfgs) > POPULARITY_THRESHOLD:
            if "uiData" in entry and entry["uiData"].get("hideFromDefaultView", True):
                entry["uiData"]["hideFromDefaultView"] = False
                flagged_count += 1

    # 4. Save updated commands.json
    save_commands_with_types(commands_data, COMMANDS_JSON)
    print(f"Processed {total_cfgs} configs.")
    print(f"Updated {COMMANDS_JSON} with popular commands marked as visible.")
    print(f"Commands flagged as hideFromDefaultView = False: {flagged_count}")

if __name__ == "__main__":
    main()