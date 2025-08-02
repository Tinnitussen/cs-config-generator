"""
Pipeline Step 4: Sub-categorize all primary command groups.

This single, rule-driven script replaces the previous three separate
scripts. It reads a rules file and processes the primary command
categories (player, server, shared) to sort them into the final
fine-grained sub-category JSON files for the UI.
"""
import json
import os
from collections import defaultdict

def _get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    if command_name.startswith('+'):
        return '+'
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def _get_subcategory(command: dict, rules: dict):
    """Determines the subcategory for a single command based on the rules."""
    default_category = None

    for cat_name, cat_rules in rules.items():
        if cat_rules.get("default", False):
            default_category = cat_name

        prefix = _get_prefix(command['command'])
        ui_type = command.get('uiData', {}).get('type')
        flags = command.get('consoleData', {}).get('flags', [])
        cmd_name = command['command']

        if "prefixes" in cat_rules and prefix in cat_rules["prefixes"]:
            return cat_name
        if "ui_type" in cat_rules and ui_type == cat_rules["ui_type"]:
            return cat_name
        if "flags" in cat_rules and any(f in cat_rules["flags"] for f in flags):
            return cat_name
        if "keywords" in cat_rules and any(kw in cmd_name for kw in cat_rules["keywords"]):
            return cat_name

    return default_category

def subcategorize(classified_dir: str, schema_dir: str, rules_file: str):
    """
    Subcategorizes all primary command groups based on a rules file.

    Args:
        classified_dir (str): The directory containing the output of step 3 (e.g., player_commands.json).
        schema_dir (str): The root directory to save the final schema files.
        rules_file (str): Path to the JSON file containing subcategorization rules.
    """
    with open(rules_file, 'r', encoding='utf-8') as f:
        all_rules = json.load(f)

    print("--- Sub-categorization Step ---")

    for primary_category, category_rules in all_rules.items():
        input_file = os.path.join(classified_dir, f"{primary_category}_commands.json")
        output_dir = os.path.join(schema_dir, primary_category)

        if not os.path.exists(input_file):
            print(f"Skipping {primary_category}: file not found at {input_file}")
            continue

        with open(input_file, 'r', encoding='utf-8') as f:
            commands = json.load(f)

        print(f"\nProcessing {len(commands)} commands for '{primary_category}' category...")

        # Initialize subcategory lists
        subcategories = defaultdict(list)

        # Process each command
        for command in commands:
            manual_cat_path = command.get('uiData', {}).get('manual_category')
            if manual_cat_path:
                manual_primary, manual_sub = manual_cat_path.split('/')
                if manual_primary == primary_category:
                    subcategories[manual_sub].append(command)
                    continue

            subcategory = _get_subcategory(command, category_rules["subcategories"])
            if subcategory:
                subcategories[subcategory].append(command)
            else:
                print(f"Warning: Command '{command['command']}' did not match any subcategory rule for '{primary_category}'.")

        # Save the output files
        os.makedirs(output_dir, exist_ok=True)
        for sub_name, command_list in subcategories.items():
            category_path = os.path.join(output_dir, sub_name)
            os.makedirs(os.path.dirname(category_path), exist_ok=True)

            output_file = f"{category_path}.json"
            print(f"  - Saving {len(command_list)} commands to '{output_file}'")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(command_list, f, indent=2)

def main():
    """For testing this step independently."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    classified_dir = os.path.join(repo_root, 'Tools', 'data', 'classified_commands')
    schema_dir = os.path.join(repo_root, 'CSConfigGenerator', 'wwwroot', 'data', 'commandschema')
    rules_file = os.path.join(repo_root, 'Tools', 'pipeline', 'subcategorization_rules.json')

    if not os.path.exists(classified_dir):
        print(f"Error: Classified commands directory not found at '{classified_dir}'.")
        print("Please run up to Step 3 first.")
        return

    subcategorize(classified_dir, schema_dir, rules_file)

if __name__ == "__main__":
    main()
