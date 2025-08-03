import json
import sys
from collections import Counter
from pathlib import Path

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

# Setup rules import for popularity_rules
setup_rules_import()
from popularity_rules import extract_commands_from_cfg, should_mark_as_popular, should_update_visibility

def main():
    """Main function to process command popularity based on config usage."""

    # Verify required paths exist
    if not COMMANDS_JSON.exists():
        print(f"Error: Commands file not found at {COMMANDS_JSON}")
        return 1

    if not CONFIGS_DIR.exists():
        print(f"Error: Configs directory not found at {CONFIGS_DIR}")
        return 1

    # 1. Load all known commands from commands.json
    print(f"Loading commands from {COMMANDS_JSON}...")
    commands_data = load_json(COMMANDS_JSON)
    known_commands = set()
    for entry in commands_data:
        if "command" in entry:
            known_commands.add(entry["command"])

    print(f"Loaded {len(known_commands)} known commands")

    # 2. Parse all configs and count command popularity
    cfg_files = list(CONFIGS_DIR.glob("*.cfg"))
    total_cfgs = len(cfg_files)

    if total_cfgs == 0:
        print(f"Warning: No .cfg files found in {CONFIGS_DIR}")
        return 1

    print(f"Processing {total_cfgs} config files...")
    command_counter = Counter()

    for cfg_path in cfg_files:
        try:
            cmds_in_cfg = extract_commands_from_cfg(str(cfg_path))
            # Only count commands that are known
            for cmd in cmds_in_cfg:
                if cmd in known_commands:
                    command_counter[cmd] += 1
        except Exception as e:
            print(f"Warning: Failed to process {cfg_path.name}: {e}")
            continue

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
    print(f"Saving updated commands to {COMMANDS_JSON}...")
    save_json(commands_data, COMMANDS_JSON)

    # Summary
    print(f"\nProcessing Summary:")
    print(f"- Processed {total_cfgs} config files")
    print(f"- Commands flagged as visible (hideFromDefaultView=False): {flagged_count}")
    print(f"- Updated {COMMANDS_JSON}")

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
