import json
import os

def compare_files():
    # Construct absolute paths to the data files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    commands_json_path = os.path.join(project_root, 'data', 'commands.json')
    scraped_types_json_path = os.path.join(project_root, 'data', 'scraped_types.json')

    # Load the JSON files
    with open(commands_json_path, 'r') as f:
        commands_data = json.load(f)
    with open(scraped_types_json_path, 'r') as f:
        scraped_data = json.load(f)

    # Convert commands_data to a dictionary for easier lookup
    commands_dict = {cmd['command']: cmd for cmd in commands_data}

    # Initialize statistics counters
    total_commands = len(commands_dict)
    scraped_commands_count = len(scraped_data)
    commands_in_scraped = 0
    commands_not_in_scraped = 0
    type_matches = 0
    type_mismatches = 0
    unknown_and_in_scraped = 0
    unknown_and_not_in_scraped = 0

    mismatched_commands = []
    not_in_scraped_list = []

    # --- Coverage and type matching ---
    for name, command_details in commands_dict.items():
        if name in scraped_data:
            commands_in_scraped += 1
            original_type = command_details.get('uiData', {}).get('type')
            scraped_type = scraped_data[name].get('type')

            if original_type == scraped_type:
                type_matches += 1
            else:
                type_mismatches += 1
                mismatched_commands.append({
                    'command': name,
                    'original_type': original_type,
                    'scraped_type': scraped_type
                })
        else:
            commands_not_in_scraped += 1
            not_in_scraped_list.append(name)

    # --- "Unknown" type analysis ---
    for name, command_details in commands_dict.items():
        if command_details.get('uiData', {}).get('type') == 'unknown':
            if name in scraped_data:
                unknown_and_in_scraped += 1
            else:
                unknown_and_not_in_scraped += 1

    # --- Analysis of scraped_types.json ---
    commands_in_json = set(commands_dict.keys())
    scraped_commands_keys = set(scraped_data.keys())

    extra_in_scraped = scraped_commands_keys - commands_in_json

    # --- Print out the statistics ---
    print(f"Total commands in commands.json: {total_commands}")
    print(f"Total commands in scraped_types.json: {scraped_commands_count}")
    print("-" * 30)

    if total_commands > 0:
        print(f"Commands from commands.json found in scraped_types.json: {commands_in_scraped} ({commands_in_scraped/total_commands:.2%})")
        print(f"Commands from commands.json NOT found in scraped_types.json: {commands_not_in_scraped} ({commands_not_in_scraped/total_commands:.2%})")
    else:
        print("commands.json is empty, skipping coverage statistics.")
    print(f"Extra commands in scraped_types.json not in commands.json: {len(extra_in_scraped)}")
    print("-" * 30)

    print(f"Type matches: {type_matches}")
    print(f"Type mismatches: {type_mismatches}")
    if type_mismatches > 0:
        print("Mismatched commands:")
        for item in mismatched_commands:
            print(f"  - {item['command']}: commands.json has '{item['original_type']}', scraped_types.json has '{item['scraped_type']}'")
    print("-" * 30)

    total_unknown = unknown_and_in_scraped + unknown_and_not_in_scraped
    if total_unknown > 0:
        print(f"Analysis of 'unknown' type in commands.json:")
        print(f"  - Total 'unknown' commands: {total_unknown}")
        print(f"  - 'unknown' commands found in scraped_types.json: {unknown_and_in_scraped} ({unknown_and_in_scraped/total_unknown:.2%})")
        print(f"  - 'unknown' commands NOT in scraped_types.json: {unknown_and_not_in_scraped} ({unknown_and_not_in_scraped/total_unknown:.2%})")
        print("-" * 30)

    if extra_in_scraped:
        print(f"Commands in scraped_types.json but not in commands.json ({len(extra_in_scraped)}):")
        for cmd in sorted(list(extra_in_scraped)):
            print(f"  - {cmd}")
        print("-" * 30)

    if not_in_scraped_list:
        print(f"Commands in commands.json but not in scraped_types.json ({len(not_in_scraped_list)}):")
        for cmd in sorted(not_in_scraped_list):
            print(f"  - {cmd}")
        print("-" * 30)

if __name__ == "__main__":
    compare_files()
