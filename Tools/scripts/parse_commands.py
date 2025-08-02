import json
import re
from datetime import datetime
import os

def extract_date_from_filename(filename):
    """Extract date from filename and convert to ISO 8601 timestamp."""
    # Extract date pattern like "2025-30-07" from filename
    date_pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(date_pattern, filename)
    
    if match:
        year, day, month = match.groups()
        # Create datetime object (assuming start of day UTC)
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.isoformat() + "Z"
        except ValueError as e:
            print(f"Warning: Invalid date extracted from filename: {year}-{month}-{day}")
            return datetime.now().isoformat() + "Z"
    else:
        print(f"Warning: Could not extract date from filename: {filename}")
        return datetime.now().isoformat() + "Z"

def has_data_changed(old_data, new_data):
    """Check if console data has changed between old and new entries."""
    return (
        old_data.get("defaultValue") != new_data.get("defaultValue") or
        set(old_data.get("flags", [])) != set(new_data.get("flags", [])) or
        old_data.get("description") != new_data.get("description")
    )

def load_existing_data(output_file):
    """Load existing parsed commands if file exists."""
    if os.path.exists(output_file):
        try:
            with open(output_file, encoding="utf-8") as f:
                return {entry["command"]: entry for entry in json.load(f)}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load existing data from {output_file}: {e}")
            print("Starting with empty dataset.")
    return {}

def parse_input_file(input_file):
    """Parse the input file and return a set of current commands and their data."""
    # Regex to parse valid console lines
    pattern = re.compile(
        r"^\[Console\]\s+"               # Literal prefix
        r"([^\s]+)\s+:\s+"               # Command name
        r"(.+?)\s+:\s+"                   # Default value: anything up to the next colon
        r"([^:]+?)\s*"                     # Flags (comma-separated)
        r"(?::\s*(.*))?$"                   # Optional description
    )
    
    valid_command = re.compile(r"^[a-zA-Z0-9_\-\.\+]+$")
    valid_default_value = re.compile(r"^.{0,256}$")
    valid_flags = set([
        "cl", "sv", "cheat", "a", "release", "rep", "user", "norecord",
        "clientcmd_can_execute", "server_can_execute", "execute_per_tick",
        "vconsole_fuzzy", "vconsole_set_focus", "nf", "nolog",
        "per_user", "disconnected", "demo", "prot", "server_cant_query",
        "linked"
    ])
    
    current_commands = set()
    parsed_commands = {}
    seen_entries = set()
    
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                print(f"Skipping invalid line: {line.strip()}")
                continue
            
            command, default_value, flags_raw, description = match.groups()
            flags = [f.strip() for f in flags_raw.split(',') if f.strip()]
            
            is_valid_command = valid_command.match(command)
            is_valid_value = default_value == "cmd" or valid_default_value.match(default_value)
            is_valid_flags = all(flag in valid_flags for flag in flags)
            
            if not is_valid_command:
                print(f"Invalid command: {command}")
                continue
            if not is_valid_value:
                print(f"Invalid default value for {command}: {default_value}")
                continue
            if not is_valid_flags:
                print(f"Invalid flags for {command}: {flags}")
                continue
            
            command = command.strip()
            current_commands.add(command)
            
            console_data = {
                "defaultValue": default_value.strip() if default_value != "cmd" else None,
                "flags": flags,
                "description": description.strip() if description else ""
            }
            
            # Check for duplicates in current processing
            entry_key = (
                command,
                console_data["defaultValue"],
                tuple(sorted(console_data["flags"])),
                console_data["description"]
            )
            
            if entry_key in seen_entries:
                print(f"Skipping duplicate entry in current file: {command}")
                continue
            seen_entries.add(entry_key)
            
            parsed_commands[command] = console_data
    
    return current_commands, parsed_commands

def unmark_deprecated_commands(existing_commands, current_commands, sourced_at):
    """
    Initial step: Unmark any deprecated commands that are now back in the current dataset.
    Returns count of commands unmarked.
    """
    unmarked_count = 0
    
    for cmd_name in current_commands:
        if cmd_name in existing_commands and existing_commands[cmd_name].get("deprecated"):
            print(f"Command {cmd_name} is back - removing deprecated flag")
            existing_commands[cmd_name].pop("deprecated", None)
            unmarked_count += 1
    
    return unmarked_count

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "..", "data", "all_commands-2025-30-07.txt")
    output_file = os.path.join(script_dir, "..", "data", "commands.json")
    
    # Extract timestamp from filename
    sourced_at = extract_date_from_filename(input_file)
    print(f"Using timestamp: {sourced_at}")
    
    # Load existing data
    existing_commands = load_existing_data(output_file)
    print(f"Loaded {len(existing_commands)} existing commands")
    
    # Parse input file to get current commands and their data
    print("Parsing input file...")
    current_commands, parsed_commands = parse_input_file(input_file)
    print(f"Found {len(current_commands)} valid commands in input file")
    
    # Step 1: Unmark deprecated commands that are now back
    print("Step 1: Unmarking deprecated commands that are back...")
    unmarked_count = unmark_deprecated_commands(existing_commands, current_commands, sourced_at)
    
    # Step 2: Process all current commands (new and existing)
    print("Step 2: Processing current commands...")
    entries = []
    updated_count = 0
    new_count = 0
    
    for command, new_console_data in parsed_commands.items():
        # Add timestamp to console data
        new_console_data["sourcedAt"] = sourced_at
        
        if command in existing_commands:
            # Existing command - check if data has changed
            existing_entry = existing_commands[command]
            old_console_data = existing_entry["consoleData"]
            
            if has_data_changed(old_console_data, new_console_data):
                print(f"Updating changed command: {command}")
                existing_entry["consoleData"] = new_console_data
                updated_count += 1
            else:
                # Data hasn't changed, but update sourcedAt to show we checked it
                existing_entry["consoleData"]["sourcedAt"] = sourced_at
            
            entries.append(existing_entry)
        else:
            # New command
            print(f"Adding new command: {command}")
            entry = {
                "command": command,
                "consoleData": new_console_data
            }
            entries.append(entry)
            new_count += 1
    
    # Step 3: Mark commands as deprecated if they're not in current file
    print("Step 3: Marking missing commands as deprecated...")
    deprecated_count = 0
    
    for cmd_name, existing_entry in existing_commands.items():
        if cmd_name not in current_commands:
            if not existing_entry.get("deprecated"):
                print(f"Marking command as deprecated: {cmd_name}")
                existing_entry["deprecated"] = True
                deprecated_count += 1
            entries.append(existing_entry)
    
    # Sort entries by command name for consistency
    entries.sort(key=lambda x: x["command"])
    
    # Count final stats directly from the processed data
    total_active = len(current_commands)
    total_deprecated = sum(1 for entry in entries if entry.get("deprecated", False))
    
    # Summary
    print(f"\nProcessing Summary:")
    print(f"- Total commands in dataset: {len(entries)}")
    print(f"- Current active commands: {total_active}")
    print(f"- Currently deprecated commands: {total_deprecated}")
    print(f"- Commands unmarked from deprecated: {unmarked_count}")
    print(f"- New commands added: {new_count}")
    print(f"- Existing commands updated: {updated_count}")
    print(f"- Commands newly marked as deprecated: {deprecated_count}")
    
    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    
    print(f"\nOutput written to: {output_file}")

if __name__ == "__main__":
    main()