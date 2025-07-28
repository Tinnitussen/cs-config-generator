import json
import re

input_file = "data/all_commands.txt"
output_file = "data/combined.json"

# Regex to parse valid console lines
pattern = re.compile(r"^\[Console\]\s+([^\s]+)\s+:\s+([^\s]+)\s+:\s+([^:]*)(?::\s*(.*))?")

# Valid command name pattern
valid_command = re.compile(
    r"^[a-zA-Z0-9_\-\.\+]+$"      # Letters, numbers, underscore, dash, dot, plus
)

# Valid default value pattern
valid_default_value = re.compile(
    re.compile(r"^.{0,256}$")
)

# Valid flags set
valid_flags = set([
    "cl", "sv", "cheat", "a", "release", "rep", "user", "norecord",
    "clientcmd_can_execute", "server_can_execute", "execute_per_tick",
    "vconsole_fuzzy", "vconsole_set_focus", "nf", "nolog",
    "per_user", "disconnected", "demo", "prot", "server_cant_query"
])

entries = []

with open(input_file, encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line)
        if not match:
            print(f"Skipping invalid line: {line.strip()}")
            continue

        command, default_value, flags_raw, description = match.groups()

        flags = [f.strip() for f in flags_raw.split(',') if f.strip()]

        # Validate components
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

        entry = {
            "command": command.strip(),
            "consoleData": {
                "defaultValue": default_value.strip() if default_value != "cmd" else None,
                "flags": flags,
                "description": description.strip() if description else ""
            }
        }
        entries.append(entry)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2)