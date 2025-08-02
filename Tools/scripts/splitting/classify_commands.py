import json
import os
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    if command_name.startswith('+'):
        return '+'
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def classify_commands(commands: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify commands into server, player, shared, and uncategorized.
    """
    classified_commands = {
        "server": [],
        "player": [],
        "shared": [],
        "uncategorized": []
    }

    player_prefixes = ["cl_", "ui_", "joy_", "cam_", "c_", "+", "snd_", "r_", "mat_", "demo_"]
    server_prefixes = ["sv_", "mp_", "bot_", "nav_", "ent_", "script_", "logaddress_", "rr_", "cast_", "navspace_", "markup_", "spawn_", "vis_", "telemetry_", "test_", "soundscape_", "scene_", "particle_", "shatterglass_", "create_", "debugoverlay_", "prop_", "g_", "ff_", "cash_", "contributionscore_"]
    shared_prefixes = ["ai_", "weapon_", "ragdoll_", "ik_", "skeleton_"]

    for command in commands:
        manual_category = command.get('uiData', {}).get('manual_category')
        if manual_category:
            category, _ = manual_category.split('/')
            classified_commands[category].append(command)
            continue

        flags = command.get('consoleData', {}).get('flags', [])
        is_server = 'sv' in flags
        is_client = 'cl' in flags
        is_replicated = 'rep' in flags
        is_archived = 'a' in flags
        is_user = 'user' in flags
        command_name = command['command']
        prefix = get_prefix(command_name)

        if is_replicated or (is_server and is_client):
            classified_commands["shared"].append(command)
        elif is_server:
            classified_commands["server"].append(command)
        elif is_client:
            classified_commands["player"].append(command)
        elif prefix in player_prefixes:
            classified_commands["player"].append(command)
        elif prefix in server_prefixes:
            classified_commands["server"].append(command)
        elif prefix in shared_prefixes:
            classified_commands["shared"].append(command)
        elif is_archived or is_user:
            classified_commands["player"].append(command)
        else:
            classified_commands["uncategorized"].append(command)

    return classified_commands

def main():
    input_file = "Tools/data/commands.json"
    output_dir = "Tools/data/classified_commands"

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)

    print("Classifying commands with new logic...")
    classified_commands = classify_commands(commands)

    # Save the classified commands into separate files
    for category, command_list in classified_commands.items():
        output_file = os.path.join(output_dir, f"{category}_commands.json")
        print(f"Saving {len(command_list)} {category} commands to '{output_file}'...")
        save_json(command_list, output_file)

    print("\n--- CLASSIFICATION SUMMARY ---")
    total_commands = len(commands)
    print(f"Total commands processed: {total_commands}")
    for category, command_list in classified_commands.items():
        count = len(command_list)
        percentage = (count / total_commands * 100) if total_commands > 0 else 0
        print(f"- {category.capitalize()}: {count} commands ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
