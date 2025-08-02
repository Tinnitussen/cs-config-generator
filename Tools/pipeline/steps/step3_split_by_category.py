"""
Pipeline Step 3: Split commands into primary categories.

This script reads the `commands.json` file and splits all the commands
into primary categories (player, server, shared, uncategorized) based
on a set of rules. It writes the output to separate JSON files for
each category.
"""
import json
import os
import sys
from collections import defaultdict

def split_commands_by_category(commands_file: str, output_dir: str):
    """
    Classifies commands into primary categories and saves them to separate files.

    Args:
        commands_file (str): Path to the input commands.json file.
        output_dir (str): Directory to save the categorized JSON files.
    """
    # --- Path setup for rules ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rules_dir = os.path.join(script_dir, '..', '..', 'rules')
    if rules_dir not in sys.path:
        sys.path.append(rules_dir)
    from splitting_rules import get_command_category

    # --- Load and Process ---
    with open(commands_file, 'r', encoding='utf-8') as f:
        commands = json.load(f)

    print("Splitting commands into primary categories...")
    classified_commands = defaultdict(list)
    for command in commands:
        category = get_command_category(command)
        classified_commands[category].append(command)

    classified_commands = dict(classified_commands)

    # --- Save and Summarize ---
    os.makedirs(output_dir, exist_ok=True)
    for category, command_list in classified_commands.items():
        output_file = os.path.join(output_dir, f"{category}_commands.json")
        print(f"Saving {len(command_list)} {category} commands to '{output_file}'...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(command_list, f, indent=2)

    print("\n--- Primary Category Split Summary ---")
    total_commands = len(commands)
    print(f"Total commands processed: {total_commands}")
    for category, command_list in classified_commands.items():
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category.capitalize()}: {count} commands ({percentage:.1f}%)")

def main():
    """For testing this step independently."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    commands_file = os.path.join(repo_root, 'Tools', 'data', 'commands.json')
    output_dir = os.path.join(repo_root, 'Tools', 'data', 'classified_commands')

    if not os.path.exists(commands_file):
        print(f"Error: Input file not found at '{commands_file}'.")
        print("Please run Steps 1 and 2 first or ensure you are in the repo root.")
        return

    split_commands_by_category(commands_file, output_dir)

if __name__ == "__main__":
    main()
