import os
import json
import sys
from collections import Counter

# --- Path setup ---
# Add the 'rules' directory to the Python path to import the classification rules.
script_dir = os.path.dirname(os.path.abspath(__file__))
rules_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'rules')
if rules_dir not in sys.path:
    sys.path.append(rules_dir)

from popularity_rules import extract_commands_from_cfg, should_mark_as_popular, should_update_visibility

COMMANDS_JSON = "data/commands.json"
CONFIGS_DIR = "data/pro-player-configs/unzipped-configs"

def load_commands_with_types(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_commands_with_types(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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
        is_popular = should_mark_as_popular(count, total_cfgs)

        if should_update_visibility(entry, is_popular):
            entry["uiData"]["hideFromDefaultView"] = False
            flagged_count += 1

    # 4. Save updated commands.json
    save_commands_with_types(commands_data, COMMANDS_JSON)
    print(f"Processed {total_cfgs} configs.")
    print(f"Updated {COMMANDS_JSON} with popular commands marked as visible.")
    print(f"Commands flagged as hideFromDefaultView = False: {flagged_count}")

if __name__ == "__main__":
    main()
