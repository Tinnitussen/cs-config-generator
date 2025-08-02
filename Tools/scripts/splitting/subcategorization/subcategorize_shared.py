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

def subcategorize_shared():
    """Subcategorizes the shared commands."""
    commands = load_commands('Tools/data/classified_commands/shared_commands.json')

    subcategories = {
        "tbd": []
    }

    for command in commands:
        manual_category = command.get('uiData', {}).get('manual_category')
        if manual_category:
            _, subcategory = manual_category.split('/')
            subcategories[subcategory].append(command)
            continue

        subcategories["tbd"].append(command)

    output_dir = "CSConfigGenerator/wwwroot/data/commandschema/shared"
    for category, command_list in subcategories.items():
        output_file = os.path.join(output_dir, f"{category}.json")
        print(f"Saving {len(command_list)} commands to '{output_file}'...")
        save_json(command_list, output_file)

if __name__ == "__main__":
    subcategorize_shared()
