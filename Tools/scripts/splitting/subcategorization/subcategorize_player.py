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

def subcategorize_player():
    """Subcategorizes the player commands."""
    commands = load_commands('Tools/data/classified_commands/player_commands.json')

    subcategories = {
        "crosshair": [],
        "viewmodel": [],
        "hud": [],
        "radar": [],
        "input": [],
        "gameplay": [],
        "audio": [],
        "communication": [],
        "network": [],
        "cheats": [],
        "actions": [],
        "misc": [],
        "developer/rendering": [],
        "developer/debugging": [],
        "developer/spectator": []
    }

    for command in commands:
        manual_category = command.get('uiData', {}).get('manual_category')
        if manual_category:
            _, subcategory = manual_category.split('/')
            subcategories[subcategory].append(command)
            continue

        prefix = get_prefix(command['command'])
        ui_type = command.get('uiData', {}).get('type')

        if prefix == "crosshair_":
            subcategories["crosshair"].append(command)
        elif prefix == "viewmodel_":
            subcategories["viewmodel"].append(command)
        elif prefix == "hud_":
            subcategories["hud"].append(command)
        elif prefix == "radar_":
            subcategories["radar"].append(command)
        elif prefix in ["input_", "m_", "joy_"]:
            subcategories["input"].append(command)
        elif prefix in ["gameplay_", "option_"]:
            subcategories["gameplay"].append(command)
        elif prefix in ["snd_", "sound_", "voice_"]:
            subcategories["audio"].append(command)
        elif prefix in ["comm_", "chat_"]:
            subcategories["communication"].append(command)
        elif prefix == "net_":
            subcategories["network"].append(command)
        elif command.get('consoleData', {}).get('flags') and "cheat" in command.get('consoleData', {}).get('flags', []):
            subcategories["cheats"].append(command)
        elif ui_type == "action":
            subcategories["actions"].append(command)
        elif prefix == "r_":
            subcategories["developer/rendering"].append(command)
        elif prefix in ["debug_", "dev_"]:
            subcategories["developer/debugging"].append(command)
        elif prefix == "spec_":
            subcategories["developer/spectator"].append(command)
        else:
            subcategories["misc"].append(command)

    output_dir = "CSConfigGenerator/wwwroot/data/commandschema/player"
    for category, command_list in subcategories.items():
        output_file = os.path.join(output_dir, f"{category}.json")
        print(f"Saving {len(command_list)} commands to '{output_file}'...")
        save_json(command_list, output_file)

if __name__ == "__main__":
    subcategorize_player()
