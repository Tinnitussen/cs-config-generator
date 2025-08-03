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
    SHARED_COMMANDS, SHARED_SCHEMA_DIR, setup_rules_import,
    load_json, save_json, ensure_output_dirs
)

# Setup rules import
setup_rules_import()
from shared_subcategorization_rules import get_shared_subcategory

def subcategorize_shared():
    """Subcategorizes the shared commands using external rules."""

    if not SHARED_COMMANDS.exists():
        print(f"Error: Shared commands file not found at {SHARED_COMMANDS}")
        print("Make sure you've run the command splitting step first.")
        return 1

    print(f"Loading shared commands from {SHARED_COMMANDS}...")
    commands = load_json(SHARED_COMMANDS)
    print(f"Loaded {len(commands)} shared commands")

    subcategories = {
        "tbd": []
    }

    for command in commands:
        subcategory = get_shared_subcategory(command)
        if subcategory in subcategories:
            subcategories[subcategory].append(command)
        else:
            print(f"Warning: Unknown subcategory '{subcategory}' for command {command['command']}")
            subcategories["tbd"].append(command)  # Default to tbd for unknown

    # Ensure output directory exists
    ensure_output_dirs()

    print(f"\nSaving subcategorized shared commands to {SHARED_SCHEMA_DIR}:")
    for category, command_list in subcategories.items():
        if command_list:  # Only save non-empty categories
            output_file = SHARED_SCHEMA_DIR / f"{category}.json"
            print(f"  - {category}: {len(command_list)} commands -> {output_file.name}")
            save_json(command_list, output_file)

    # Print summary
    print(f"\n--- SHARED SUBCATEGORIZATION SUMMARY ---")
    total_commands = len(commands)
    print(f"Total shared commands processed: {total_commands}")

    non_empty_categories = {k: v for k, v in subcategories.items() if v}
    for category, command_list in sorted(non_empty_categories.items()):
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category}: {count} commands ({percentage:.1f}%)")

    return 0

if __name__ == "__main__":
    try:
        exit_code = subcategorize_shared()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
