import json
from pathlib import Path
import sys
from collections import defaultdict
from typing import List, Dict, Callable

sys.path.append(str(Path(__file__).parent.parent))
from rules.subcategorization_rules import get_player_subcategory, get_server_subcategory, get_shared_subcategory

def load_commands(filepath: Path) -> List[Dict]:
    """Load a command JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: list, filepath: Path):
    """Save data to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def subcategorize(category_name: str, subcategory_func: Callable, default_subcategories: List[str]):
    """
    Subcategorizes commands for a given category using external rules.

    Args:
        category_name: The name of the category (e.g., "player", "server").
        subcategory_func: The function to call to get the subcategory for a command.
        default_subcategories: A list of default subcategory names to create empty files for.
    """
    tools_dir = Path(__file__).parent.parent.parent
    input_file = tools_dir / "data" / "classified_commands" / f"{category_name}_commands.json"

    if not input_file.exists():
        print(f"Skipping {category_name} subcategorization: {input_file} not found.")
        return

    commands = load_commands(input_file)
    print(f"Loaded {len(commands)} {category_name} commands from {input_file}")

    subcategories = defaultdict(list)
    for subcat in default_subcategories:
        subcategories[subcat] = []

    for command in commands:
        subcategory = subcategory_func(command)
        subcategories[subcategory].append(command)

    output_dir = tools_dir.parent / "CSConfigGenerator" / "wwwroot" / "data" / "commandschema" / category_name
    for subcat_name, command_list in subcategories.items():
        output_file = output_dir / f"{subcat_name}.json"
        print(f"Saving {len(command_list)} commands to '{output_file}'...")
        save_json(command_list, output_file)

def main():
    """Main function to run subcategorization for all categories."""
    player_subcategories = [
        "crosshair", "viewmodel", "hud", "radar", "input", "gameplay",
        "audio", "communication", "network", "cheats", "actions", "misc",
        "developer/rendering", "developer/debugging", "developer/spectator"
    ]
    server_subcategories = [
        "setup", "teams", "rounds", "objectives", "spawning",
        "rules", "economy", "bots", "gotv"
    ]
    shared_subcategories = ["tbd"]

    print("--- Subcategorizing Player Commands ---")
    subcategorize("player", get_player_subcategory, player_subcategories)

    print("\n--- Subcategorizing Server Commands ---")
    subcategorize("server", get_server_subcategory, server_subcategories)

    print("\n--- Subcategorizing Shared Commands ---")
    subcategorize("shared", get_shared_subcategory, shared_subcategories)

if __name__ == "__main__":
    main()
