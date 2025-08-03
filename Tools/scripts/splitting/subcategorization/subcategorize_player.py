import sys
from pathlib import Path
from collections import defaultdict

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).parent
utils_dir = script_dir.parent.parent.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import (
    PLAYER_COMMANDS, PLAYER_SCHEMA_DIR, setup_rules_import,
    load_json, save_json, ensure_output_dirs
)

# Setup rules import
setup_rules_import()
from player_subcategorization_rules import get_player_subcategory

def subcategorize_player():
    """Subcategorizes the player commands using external rules."""

    if not PLAYER_COMMANDS.exists():
        print(f"Error: Player commands file not found at {PLAYER_COMMANDS}")
        print("Make sure you've run the command splitting step first.")
        return 1

    print(f"Loading player commands from {PLAYER_COMMANDS}...")
    commands = load_json(PLAYER_COMMANDS)
    print(f"Loaded {len(commands)} player commands")

    subcategories = {
        "crosshair": [],
        "viewmodel": [],
        "hud": [],
        "radar": [],
        "input": [],
        "gameplay": [],
        "audio": [],
        "communication": [],
        "network": [],
        "cheats": [],
        "actions": [],
        "misc": [],
        "developer/rendering": [],
        "developer/debugging": [],
        "developer/spectator": []
    }

    for command in commands:
        subcategory = get_player_subcategory(command)
        if subcategory in subcategories:
            subcategories[subcategory].append(command)
        else:
            print(f"Warning: Unknown subcategory '{subcategory}' for command {command['command']}")
            subcategories["misc"].append(command)

    # Ensure output directory exists
    ensure_output_dirs()

    print(f"\nSaving subcategorized player commands to {PLAYER_SCHEMA_DIR}:")
    for category, command_list in subcategories.items():
        if command_list:  # Only save non-empty categories
            # Handle nested categories (e.g., "developer/rendering")
            if '/' in category:
                category_dir = PLAYER_SCHEMA_DIR / category.split('/')[0]
                category_dir.mkdir(parents=True, exist_ok=True)
                output_file = category_dir / f"{category.split('/')[1]}.json"
            else:
                output_file = PLAYER_SCHEMA_DIR / f"{category}.json"

            print(f"  - {category}: {len(command_list)} commands -> {output_file.name}")
            save_json(command_list, output_file)

    # Print summary
    print(f"\n--- PLAYER SUBCATEGORIZATION SUMMARY ---")
    total_commands = len(commands)
    print(f"Total player commands processed: {total_commands}")

    non_empty_categories = {k: v for k, v in subcategories.items() if v}
    for category, command_list in sorted(non_empty_categories.items()):
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category}: {count} commands ({percentage:.1f}%)")

    return 0

if __name__ == "__main__":
    try:
        exit_code = subcategorize_player()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
