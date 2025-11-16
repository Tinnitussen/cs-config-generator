import json
import re
import argparse
from datetime import datetime
import os
from pathlib import Path

def extract_date_from_filename(filename):
    """Extract date from filename and convert to ISO 8601 timestamp."""
    date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(date_pattern, filename)

    if match:
        year, day, month = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.isoformat() + "Z"
        except ValueError:
            print(f"Warning: Invalid date in filename: {year}-{month}-{day}")

    print(f"Warning: Could not extract date from filename: {filename}")
    return datetime.now().isoformat() + "Z"

def has_data_changed(old_data, new_data):
    """Check if console data has changed."""
    return (
        old_data.get("defaultValue") != new_data.get("defaultValue") or
        set(old_data.get("flags", [])) != set(new_data.get("flags", [])) or
        old_data.get("description") != new_data.get("description")
    )

def load_existing_data(output_file):
    """Load existing parsed commands."""
    if output_file.exists():
        try:
            with open(output_file, encoding="utf-8") as f:
                return {entry["command"]: entry for entry in json.load(f)}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load {output_file}: {e}. Starting fresh.")
    return {}

def parse_input_file(input_file, rules_file):
    """Parse the input file and return current commands and their data."""
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    valid_command = re.compile(rules["valid_command_regex"])
    valid_default_value = re.compile(rules["valid_default_value_regex"])
    valid_flags = set(rules["valid_flags"])

    pattern = re.compile(
        r"^\[Console\]\s+"
        r"([^\s]+)\s+:\s+"
        r"(.+?)\s+:\s+"
        r"([^:]+?)\s*"
        r"(?::\s*(.*))?$"
    )

    current_commands = set()
    parsed_commands = {}

    with open(input_file, encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                continue

            command, default_value, flags_raw, description = match.groups()
            flags = [f.strip() for f in flags_raw.split(',') if f.strip()]

            if not valid_command.match(command) or \
               not (default_value == "cmd" or valid_default_value.match(default_value)) or \
               not all(flag in valid_flags for flag in flags):
                print(f"Skipping invalid entry for command: {command}")
                continue

            command = command.strip()

            console_data = {
                "defaultValue": default_value.strip() if default_value != "cmd" else None,
                "flags": sorted(list(set(flags))),
                "description": description.strip() if description else ""
            }

            if command in parsed_commands:
                print(f"Skipping duplicate command in source file: {command}")
                continue

            parsed_commands[command] = console_data
            current_commands.add(command)

    return current_commands, parsed_commands

def unmark_deprecated_commands(existing_commands, current_commands):
    """Unmark any deprecated commands that are now back."""
    unmarked_count = 0
    for cmd_name in current_commands:
        if cmd_name in existing_commands and existing_commands[cmd_name].get("deprecated"):
            print(f"Re-activating command: {cmd_name}")
            existing_commands[cmd_name].pop("deprecated", None)
            unmarked_count += 1
    return unmarked_count

def main():
    parser = argparse.ArgumentParser(description="Parse CS2 command dump file.")
    parser.add_argument("filename", help="The name of the command snapshot file (e.g., 'all_commands-2025-30-07.txt').")
    args = parser.parse_args()

    # --- Path setup ---
    tools_dir = Path(__file__).resolve().parent.parent
    data_dir = tools_dir / "data"
    rules_dir = tools_dir / "rules"

    input_file = data_dir / args.filename
    output_file = data_dir / "commands.json"
    rules_file = rules_dir / "parsing_validation_rules.json"

    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return 1

    sourced_at = extract_date_from_filename(input_file.name)
    print(f"Using timestamp: {sourced_at}")

    existing_commands = load_existing_data(output_file)
    print(f"Loaded {len(existing_commands)} existing commands.")

    print("Parsing input file...")
    current_commands, parsed_commands = parse_input_file(input_file, rules_file)
    print(f"Found {len(current_commands)} valid commands in input file.")

    unmarked_count = unmark_deprecated_commands(existing_commands, current_commands)

    entries = []
    updated_count = 0
    new_count = 0

    for command, new_console_data in parsed_commands.items():
        new_console_data["sourcedAt"] = sourced_at
        if command in existing_commands:
            existing_entry = existing_commands[command]
            if has_data_changed(existing_entry.get("consoleData", {}), new_console_data):
                print(f"Updating changed command: {command}")
                existing_entry["consoleData"] = new_console_data
                updated_count += 1
            else:
                existing_entry["consoleData"]["sourcedAt"] = sourced_at
            entries.append(existing_entry)
        else:
            print(f"Adding new command: {command}")
            entry = {"command": command, "consoleData": new_console_data}
            entries.append(entry)
            new_count += 1

    deprecated_count = 0
    # Add back commands that are now deprecated
    for cmd_name, existing_entry in existing_commands.items():
        if cmd_name not in current_commands:
            if not existing_entry.get("deprecated"):
                print(f"Marking command as deprecated: {cmd_name}")
                existing_entry["deprecated"] = True
                deprecated_count += 1
            entries.append(existing_entry)

    entries.sort(key=lambda x: x["command"])

    print("\n--- Processing Summary ---")
    print(f"Total commands in dataset: {len(entries)}")
    print(f"Active commands: {len(current_commands)}")
    print(f"Deprecated commands: {sum(1 for e in entries if e.get('deprecated'))}")
    print(f"Commands re-activated: {unmarked_count}")
    print(f"New commands added: {new_count}")
    print(f"Existing commands updated: {updated_count}")
    print(f"Commands newly deprecated: {deprecated_count}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)

    print(f"\nOutput written to: {output_file}")

if __name__ == "__main__":
    main()