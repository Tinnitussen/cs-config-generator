import json
import os
from collections import defaultdict

def load_commands(filepath: str):
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: list, filepath: str):
    """Save data to JSON file"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def subcategorize_server():
    """Subcategorizes the server commands."""
    commands = load_commands('Tools/data/classified_commands/server_commands.json')

    subcategories = {
        "setup": [],
        "teams": [],
        "rounds": [],
        "objectives": [],
        "spawning": [],
        "rules": [],
        "economy": [],
        "bots": [],
        "gotv": []
    }

    for command in commands:
        manual_category = command.get('uiData', {}).get('manual_category')
        if manual_category:
            _, subcategory = manual_category.split('/')
            subcategories[subcategory].append(command)
            continue

        prefix = get_prefix(command['command'])

        if prefix in ["hostname_", "log_", "rcon_"]:
            subcategories["setup"].append(command)
        elif prefix == "mp_":
            if "team" in command['command']:
                subcategories["teams"].append(command)
            elif "round" in command['command']:
                subcategories["rounds"].append(command)
            elif "bomb" in command['command'] or "hostage" in command['command']:
                subcategories["objectives"].append(command)
            elif "spawn" in command['command']:
                subcategories["spawning"].append(command)
            elif "friendlyfire" in command['command'] or "damage" in command['command']:
                subcategories["rules"].append(command)
            elif "money" in command['command'] or "cash" in command['command'] or "econ" in command['command']:
                subcategories["economy"].append(command)
            else:
                subcategories["rules"].append(command)
        elif prefix == "bot_":
            subcategories["bots"].append(command)
        elif prefix == "tv_":
            subcategories["gotv"].append(command)
        else:
            subcategories["setup"].append(command)

    output_dir = "CSConfigGenerator/wwwroot/data/commandschema/server"
    for category, command_list in subcategories.items():
        output_file = os.path.join(output_dir, f"{category}.json")
        print(f"Saving {len(command_list)} commands to '{output_file}'...")
        save_json(command_list, output_file)

if __name__ == "__main__":
    subcategorize_server()
