import sys
from pathlib import Path
from collections import defaultdict

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).parent
utils_dir = script_dir.parent.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import COMMANDS_JSON, load_json

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return parts[0]
    return None

def analyze_prefixes():
    """Analyzes the prefixes of commands and their distribution across categories."""

    if not COMMANDS_JSON.exists():
        print(f"Error: Commands file not found at {COMMANDS_JSON}")
        return 1

    print(f"Loading commands from {COMMANDS_JSON}...")
    commands = load_json(COMMANDS_JSON)

    prefix_counts = defaultdict(int)

    for command in commands:
        flags = command.get('consoleData', {}).get('flags', [])
        is_server = 'sv' in flags
        is_client = 'cl' in flags

        if not is_server and not is_client:
            prefix = get_prefix(command['command'])
            if prefix:
                prefix_counts[prefix] += 1

    # Sort prefixes by total count
    sorted_prefixes = sorted(prefix_counts.items(), key=lambda item: item[1], reverse=True)

    print(f"\nPrefix Analysis (commands without 'sv' or 'cl' flags):")
    print(f"{'Prefix':<20} {'Count':<10}")
    print("-" * 30)

    for prefix, count in sorted_prefixes:
        print(f"{prefix:<20} {count:<10}")

    print(f"\nTotal prefixes analyzed: {len(sorted_prefixes)}")
    total_commands = sum(count for _, count in sorted_prefixes)
    print(f"Total commands with prefixes: {total_commands}")

    return 0

if __name__ == "__main__":
    try:
        exit_code = analyze_prefixes()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
