import json
import os
import sys
from collections import defaultdict

# --- Path setup ---
# Add the 'rules' directory to the Python path to import the classification rules.
script_dir = os.path.dirname(os.path.abspath(__file__))
rules_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), 'rules')
if rules_dir not in sys.path:
    sys.path.append(rules_dir)

from player_subcategorization_rules import get_player_subcategory

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

def subcategorize_player():
    """Subcategorizes the player commands using external rules."""
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
        subcategory = get_player_subcategory(command)
        subcategories[subcategory].append(command)

    output_dir = os.path.join("CSConfigGenerator", "wwwroot", "data", "commandschema", "player")
    for category, command_list in subcategories.items():
        output_file = os.path.join(output_dir, f"{category}.json")
        print(f"Saving {len(command_list)} commands to '{output_file}'...")
        save_json(command_list, output_file)

if __name__ == "__main__":
    subcategorize_player()
