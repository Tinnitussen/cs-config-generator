import sys
import argparse
from collections import Counter
from pathlib import Path

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).resolve().parent
utils_dir = script_dir.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import (
    COMMANDS_JSON, PRO_PLAYER_CONFIGS_DIR, SERVER_CONFIGS_DIR,
    CLASSIFIED_DIR, setup_rules_import, load_json, save_json,
    ensure_output_dirs
)

# Setup rules import for popularity_rules
setup_rules_import()
from popularity_rules import extract_commands_from_cfg, should_mark_as_popular

def get_config_paths(config_type: str):
    """
    Determines the input and output paths based on the config type.
    """
    if config_type == "player":
        return PRO_PLAYER_CONFIGS_DIR, CLASSIFIED_DIR / "player_commands.json"
    elif config_type == "server":
        return SERVER_CONFIGS_DIR, CLASSIFIED_DIR / "server_commands.json"
    else:
        raise ValueError(f"Invalid config type: {config_type}")

def main():
    """
    Main function to classify commands as 'player' or 'server' based on their
    popularity in a given set of configuration files.
    """
    parser = argparse.ArgumentParser(
        description="Classify commands based on usage popularity in config files."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["player", "server"],
        help="The type of configuration to process (e.g., 'player' or 'server')."
    )
    args = parser.parse_args()
    config_type = args.type

    # 1. Determine paths based on type
    configs_dir, output_path = get_config_paths(config_type)
    print(f"--- Processing {config_type.capitalize()} Commands ---")
    print(f"Input directory: {configs_dir}")
    print(f"Output file: {output_path}")

    # 2. Verify required paths exist
    if not COMMANDS_JSON.exists():
        print(f"Error: Master commands file not found at {COMMANDS_JSON}")
        return 1

    if not configs_dir.exists():
        configs_dir.mkdir(parents=True)
        print(f"Warning: Configs directory not found at {configs_dir}. An empty directory has been created.")

    ensure_output_dirs()

    # 3. Load all known commands from commands.json
    print(f"Loading all commands from {COMMANDS_JSON}...")
    all_commands_data = load_json(COMMANDS_JSON)
    known_commands = {entry["command"] for entry in all_commands_data if "command" in entry}
    print(f"Loaded {len(known_commands)} known commands.")

    # 4. Parse all configs and count command popularity
    cfg_files = list(configs_dir.glob("*.cfg"))
    total_cfgs = len(cfg_files)

    if total_cfgs == 0:
        print(f"Warning: No .cfg files found in {configs_dir}. Output will be empty.")
        save_json([], output_path)
        return 0

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

    # 5. Filter for popular commands
    popular_commands = []
    for entry in all_commands_data:
        cmd = entry.get("command")
        if not cmd:
            continue

        count = command_counter.get(cmd, 0)
        if should_mark_as_popular(count, total_cfgs):
            popular_commands.append(entry)

    # 6. Save the new list of popular commands
    print(f"Found {len(popular_commands)} popular {config_type} commands.")
    print(f"Saving to {output_path}...")
    save_json(popular_commands, output_path)

    # Summary
    print(f"\n--- {config_type.capitalize()} Processing Summary ---")
    print(f"  - Processed {total_cfgs} config files from {configs_dir}")
    print(f"  - Identified {len(popular_commands)} popular commands")
    print(f"  - Output saved to {output_path}")

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
