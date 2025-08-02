"""
Pipeline Step 1: Parse raw command data from a text file.

This script reads a text file containing a list of console commands,
parses them, and creates a structured JSON file. It also handles
detecting new, updated, and deprecated commands by comparing against
a previous version of the JSON file.
"""
import json
import re
from datetime import datetime
import os

def _extract_date_from_filename(filename):
    """Extract date from filename and convert to ISO 8601 timestamp."""
    date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(date_pattern, filename)
    if match:
        year, day, month = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.isoformat() + "Z"
        except ValueError as e:
            print(f"Warning: Invalid date extracted from filename: {year}-{month}-{day}")
    print(f"Warning: Could not extract date from filename: {filename}")
    return datetime.now().isoformat() + "Z"

def _has_data_changed(old_data, new_data):
    """Check if console data has changed between old and new entries."""
    return (
        old_data.get("defaultValue") != new_data.get("defaultValue") or
        set(old_data.get("flags", [])) != set(new_data.get("flags", [])) or
        old_data.get("description") != new_data.get("description")
    )

def _load_existing_data(output_file):
    """Load existing parsed commands if file exists."""
    if os.path.exists(output_file):
        try:
            with open(output_file, encoding="utf-8") as f:
                return {entry["command"]: entry for entry in json.load(f)}
        except (json.JSONDecodeError, KeyError):
            print(f"Warning: Could not load existing data from {output_file}. Starting fresh.")
    return {}

def _parse_input_file(input_file, rules_file):
    """Parse the input file and return a set of current commands and their data."""
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
    seen_entries = set()
    
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                continue
            
            command, default_value, flags_raw, description = match.groups()
            flags = [f.strip() for f in flags_raw.split(',') if f.strip()]
            
            if not (valid_command.match(command) and
                    (default_value == "cmd" or valid_default_value.match(default_value)) and
                    all(flag in valid_flags for flag in flags)):
                print(f"Skipping invalid entry for command: {command}")
                continue
            
            command = command.strip()
            current_commands.add(command)
            
            console_data = {
                "defaultValue": default_value.strip() if default_value != "cmd" else None,
                "flags": flags,
                "description": description.strip() if description else ""
            }
            
            entry_key = (command, console_data["defaultValue"], tuple(sorted(console_data["flags"])), console_data["description"])
            if entry_key in seen_entries:
                continue
            seen_entries.add(entry_key)
            parsed_commands[command] = console_data
    
    return current_commands, parsed_commands

def parse_raw_commands(input_file, output_file, rules_file):
    """
    Orchestrates the parsing of the raw command file.
    
    Args:
        input_file (str): Path to the raw command text file.
        output_file (str): Path to write the output JSON file.
        rules_file (str): Path to the parsing validation rules JSON.
    """
    sourced_at = _extract_date_from_filename(os.path.basename(input_file))
    print(f"Using timestamp: {sourced_at}")
    
    existing_commands = _load_existing_data(output_file)
    print(f"Loaded {len(existing_commands)} existing commands")
    
    current_commands, parsed_commands = _parse_input_file(input_file, rules_file)
    print(f"Found {len(current_commands)} valid commands in input file")
    
    # Unmark deprecated commands that are now back
    unmarked_count = 0
    for cmd_name in current_commands:
        if cmd_name in existing_commands and existing_commands[cmd_name].get("deprecated"):
            existing_commands[cmd_name].pop("deprecated", None)
            unmarked_count += 1
    
    entries = []
    updated_count = 0
    new_count = 0
    
    # Process current commands
    for command, new_console_data in parsed_commands.items():
        new_console_data["sourcedAt"] = sourced_at
        if command in existing_commands:
            existing_entry = existing_commands[command]
            if _has_data_changed(existing_entry["consoleData"], new_console_data):
                existing_entry["consoleData"] = new_console_data
                updated_count += 1
            else:
                existing_entry["consoleData"]["sourcedAt"] = sourced_at
            entries.append(existing_entry)
        else:
            entry = {"command": command, "consoleData": new_console_data}
            entries.append(entry)
            new_count += 1

    # Mark commands as deprecated
    deprecated_count = 0
    for cmd_name, existing_entry in existing_commands.items():
        if cmd_name not in current_commands:
            if not existing_entry.get("deprecated"):
                existing_entry["deprecated"] = True
                deprecated_count += 1
            entries.append(existing_entry)
    
    entries.sort(key=lambda x: x["command"])
    
    # Summary
    total_active = len(current_commands)
    total_deprecated = sum(1 for entry in entries if entry.get("deprecated", False))
    print("\nProcessing Summary:")
    print(f"- Total commands in dataset: {len(entries)}")
    print(f"- Current active commands: {total_active}")
    print(f"- Currently deprecated commands: {total_deprecated}")
    print(f"- Commands unmarked from deprecated: {unmarked_count}")
    print(f"- New commands added: {new_count}")
    print(f"- Existing commands updated: {updated_count}")
    print(f"- Commands newly marked as deprecated: {deprecated_count}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    
    print(f"\nOutput written to: {output_file}")

def main():
    """For testing this step independently."""
    # This assumes the script is run from the repo root.
    # In the pipeline, paths will be provided by the orchestrator.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    tools_dir = os.path.join(repo_root, 'Tools')

    input_file = os.path.join(tools_dir, "data", "all_commands-2025-30-07.txt")
    output_file = os.path.join(tools_dir, "data", "commands.json")
    rules_file = os.path.join(tools_dir, "rules", "parsing_validation_rules.json")

    if not all(os.path.exists(p) for p in [input_file, rules_file]):
        print("Error: Required files not found. Make sure you are running this from the repository root.")
        return

    parse_raw_commands(input_file, output_file, rules_file)

if __name__ == "__main__":
    main()