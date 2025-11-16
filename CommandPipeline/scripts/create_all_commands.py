import sys
import shutil
from pathlib import Path

# --- Path setup ---
script_dir = Path(__file__).resolve().parent
utils_dir = script_dir.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import COMMANDS_JSON, ALL_SCHEMA_DIR, ensure_output_dirs

def main():
    """
    Copies the master commands.json file to the 'all' schema directory
    to be used by a future version of the UI.
    """
    print("--- Creating 'All Commands' Data File ---")

    # Ensure paths exist
    if not COMMANDS_JSON.exists():
        print(f"Error: Master commands file not found at {COMMANDS_JSON}")
        return 1

    ensure_output_dirs()

    # Define destination path
    destination_path = ALL_SCHEMA_DIR / "all_commands.json"

    try:
        print(f"Copying '{COMMANDS_JSON}' to '{destination_path}'...")
        shutil.copy(COMMANDS_JSON, destination_path)
        print("Successfully created all_commands.json.")
    except Exception as e:
        print(f"Error: Failed to copy file. {e}")
        return 1

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
