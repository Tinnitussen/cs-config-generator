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

def main():
    input_file = "data/all_commands-2025-30-07.txt"
    output_file = "data/commands.json"
    
    # Extract timestamp from filename
    sourced_at = extract_date_from_filename(input_file)
    print(f"Using timestamp: {sourced_at}")
    
    # Load existing data
    existing_commands = load_existing_data(output_file)
    print(f"Loaded {len(existing_commands)} existing commands")
    
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
        "per_user", "disconnected", "demo", "prot", "server_cant_query"
    ])
    
    current_commands = set()
    entries = []
    seen_entries = set()
    updated_count = 0
    new_count = 0
    
    # Process input file
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
            
            current_commands.add(command.strip())
            
            new_console_data = {
                "sourcedAt": sourced_at,
                "defaultValue": default_value.strip() if default_value != "cmd" else None,
                "flags": flags,
                "description": description.strip() if description else ""
            }
            
            # Check for duplicates in current processing
            entry_key = (
                command.strip(),
                new_console_data["defaultValue"],
                tuple(sorted(new_console_data["flags"])),
                new_console_data["description"]
            )
            
            if entry_key in seen_entries:
                print(f"Skipping duplicate entry in current file: {command}")
                continue
            seen_entries.add(entry_key)
            
            # Check if command exists and needs updating
            if command.strip() in existing_commands:
                existing_entry = existing_commands[command.strip()]
                old_console_data = existing_entry["consoleData"]
                
                # Remove deprecated flag if it exists (command is back)
                if existing_entry.get("deprecated"):
                    print(f"Command {command} is no longer deprecated")
                    existing_entry.pop("deprecated", None)
                
                # Check if data has changed
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
                    "command": command.strip(),
                    "consoleData": new_console_data
                }
                entries.append(entry)
                new_count += 1
    
    # Mark deprecated commands (existed before but not in current file)
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
    
    # Summary
    print(f"\nProcessing Summary:")
    print(f"- Total commands processed: {len(entries)}")
    print(f"- New commands added: {new_count}")
    print(f"- Existing commands updated: {updated_count}")
    print(f"- Commands marked as deprecated: {deprecated_count}")
    print(f"- Current active commands: {len(current_commands)}")
    
    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    
    print(f"\nOutput written to: {output_file}")

if __name__ == "__main__":
    main()