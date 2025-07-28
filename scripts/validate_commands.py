import json

def is_valid_command(entry):
    """Checks if a single entry is a valid command."""
    if not isinstance(entry, dict):
        return False

    command = entry.get("command")
    console_data = entry.get("consoleData")

    if not isinstance(command, str) or not command:
        return False

    if not isinstance(console_data, dict):
        return False

    default_value = console_data.get("defaultValue")
    if not (isinstance(default_value, str) or default_value is None):
        return False

    flags = console_data.get("flags")
    if not isinstance(flags, list) or not all(isinstance(f, str) and f for f in flags):
        return False

    return True

def validate_commands(file_path):
    """
    Loads a JSON file of commands and validates each entry.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Error: The root of the JSON file is not a list.")
            return

        invalid_commands = [
            entry for entry in data if not is_valid_command(entry)
        ]

        if not invalid_commands:
            print("All commands are valid.")
        else:
            print(f"Found {len(invalid_commands)} invalid commands:")
            for entry in invalid_commands:
                print(json.dumps(entry, indent=2))

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")


validate_commands('data/combined.json')