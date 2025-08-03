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

def analyze_flags():
    """Analyzes the flags of uncategorized commands."""
    commands = load_commands('Tools/data/classified_commands/uncategorized_commands.json')

    prefix_flags = defaultdict(lambda: defaultdict(int))

    for command in commands:
        prefix = get_prefix(command['command'])
        if prefix:
            for flag in command.get('consoleData', {}).get('flags', []):
                prefix_flags[prefix][flag] += 1

    # Sort prefixes by the number of commands
    sorted_prefixes = sorted(prefix_flags.items(), key=lambda item: sum(item[1].values()), reverse=True)

    for prefix, flags in sorted_prefixes:
        print(f"Prefix: {prefix}")
        sorted_flags = sorted(flags.items(), key=lambda item: item[1], reverse=True)
        for flag, count in sorted_flags:
            print(f"  - {flag}: {count}")
        print("-" * 30)

if __name__ == "__main__":
    analyze_flags()
