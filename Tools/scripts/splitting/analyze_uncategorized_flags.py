import sys
from pathlib import Path
from collections import defaultdict

# --- Path setup ---
# Add the utils directory to path and import shared paths
script_dir = Path(__file__).parent
utils_dir = script_dir.parent.parent / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.append(str(utils_dir))

from paths import UNCATEGORIZED_COMMANDS, load_json

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return parts[0]
    return None

def analyze_flags():
    """Analyzes the flags of uncategorized commands."""

    if not UNCATEGORIZED_COMMANDS.exists():
        print(f"Error: Uncategorized commands file not found at {UNCATEGORIZED_COMMANDS}")
        print("Make sure you've run the command splitting step first.")
        return 1

    print(f"Loading uncategorized commands from {UNCATEGORIZED_COMMANDS}...")
    commands = load_json(UNCATEGORIZED_COMMANDS)

    print(f"Analyzing {len(commands)} uncategorized commands...")

    prefix_flags = defaultdict(lambda: defaultdict(int))

    for command in commands:
        prefix = get_prefix(command['command'])
        if prefix:
            for flag in command.get('consoleData', {}).get('flags', []):
                prefix_flags[prefix][flag] += 1

    # Sort prefixes by the number of commands
    sorted_prefixes = sorted(prefix_flags.items(), key=lambda item: sum(item[1].values()), reverse=True)

    print(f"\nFlag Analysis by Prefix (Uncategorized Commands):")
    print("=" * 50)

    for prefix, flags in sorted_prefixes:
        total_commands = sum(flags.values())
        print(f"\nPrefix: {prefix} ({total_commands} commands)")
        sorted_flags = sorted(flags.items(), key=lambda item: item[1], reverse=True)
        for flag, count in sorted_flags:
            print(f"  - {flag}: {count}")
        print("-" * 30)

    print(f"\nSummary:")
    print(f"- Total prefixes analyzed: {len(sorted_prefixes)}")
    print(f"- Total uncategorized commands: {len(commands)}")

    return 0

if __name__ == "__main__":
    try:
        exit_code = analyze_flags()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
