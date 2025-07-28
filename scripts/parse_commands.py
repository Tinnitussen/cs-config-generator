import json
import re

input_file = "data/all_commands.txt"
output_file = "data/combined.json"

pattern = re.compile(r"^\[Console\]\s+([^\s]+)\s+:\s+([^\s]+)\s+:\s+([^:]*)(?::\s*(.*))?")

entries = []

with open(input_file, encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line)
        if not match:
            continue

        command, default_value, flags_raw, description = match.groups()
        flags = [f.strip() for f in flags_raw.split(',') if f.strip()]

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
