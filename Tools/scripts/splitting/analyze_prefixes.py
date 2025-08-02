import json
from collections import defaultdict

def load_commands(filepath: str):
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return parts[0]
    return None

def analyze_prefixes():
    """Analyzes the prefixes of commands and their distribution across categories."""
    commands = load_commands('Tools/data/commands.json')

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

    print(f"{'Prefix':<20} {'Count':<10}")
    print("-" * 30)

    for prefix, count in sorted_prefixes:
        print(f"{prefix:<20} {count:<10}")

if __name__ == "__main__":
    analyze_prefixes()
