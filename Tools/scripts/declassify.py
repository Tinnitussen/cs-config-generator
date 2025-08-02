import json
import os

def declassify_commands(filepath):
    """
    Removes the 'uiData' field from each command in the commands.json file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        commands = json.load(f)

    for command in commands:
        if 'uiData' in command:
            del command['uiData']

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=2)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    commands_file = os.path.join(script_dir, "../data/commands.json")
    print(f"De-classifying commands in {commands_file}...")
    declassify_commands(commands_file)
    print("De-classification complete.")
