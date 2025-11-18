import json
import os

MARKER = "compare_commands_v5"  # marker for verification


def normalize_type(type_str):
    """Normalize type strings to canonical forms for comparison.

    Eliminates false positives from stylistic differences:
    - float32 → float
    - int32 → int
    - uint32 → uint
    - uint64 → uint

    Preserves semantic distinctions:
    - bool, string, vector3, color, bitmask, command, unknown unchanged
    """
    if not type_str:
        return type_str

    normalization_map = {
        'float32': 'float',
        'int32': 'int',
        'uint32': 'uint',
        'uint64': 'uint',
    }

    return normalization_map.get(type_str, type_str)


def compare_files():
    """Compare commands.json and scraped_types.json with refined output rules.

    Explicit Output Sections:
    SECTION: SUMMARY (delimited by END SUMMARY)
    SECTION: MISSING (Non-Command)
    SECTION: TYPE MISMATCHES (Excluding Unknown)
    Suppressed listings: command-type missing, unknown-type mismatches, extras only count.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    commands_json_path = os.path.join(project_root, 'data', 'commands.json')
    scraped_types_json_path = os.path.join(project_root, 'data', 'scraped_types.json')

    with open(commands_json_path, 'r') as f:
        commands_data = json.load(f)
    with open(scraped_types_json_path, 'r') as f:
        scraped_data = json.load(f)

    commands_dict = {cmd['command']: cmd for cmd in commands_data}

    total_commands = len(commands_dict)
    scraped_commands_count = len(scraped_data)
    commands_in_scraped = 0
    commands_not_in_scraped = 0
    type_matches = 0
    type_matches_alias = 0  # Matches after normalization (e.g., float vs float32)
    type_mismatches_raw = 0
    unknown_and_in_scraped = 0
    unknown_and_not_in_scraped = 0

    missing_non_command = []
    mismatched_commands_filtered = []

    suppressed_missing_command_type = 0
    suppressed_unknown_mismatches = 0

    for name, details in commands_dict.items():
        original_type = details.get('uiData', {}).get('type')
        if name in scraped_data:
            commands_in_scraped += 1
            scraped_type = scraped_data[name].get('type')

            # Normalize types for comparison
            normalized_original = normalize_type(original_type)
            normalized_scraped = normalize_type(scraped_type)

            if original_type == scraped_type:
                type_matches += 1
            elif normalized_original == normalized_scraped:
                # Types differ in string but are semantically equivalent (e.g., float vs float32)
                type_matches_alias += 1
            else:
                type_mismatches_raw += 1
                if original_type == 'unknown':
                    suppressed_unknown_mismatches += 1
                else:
                    mismatched_commands_filtered.append({
                        'command': name,
                        'original_type': original_type,
                        'scraped_type': scraped_type
                    })
        else:
            commands_not_in_scraped += 1
            if original_type == 'command':
                suppressed_missing_command_type += 1
            else:
                missing_non_command.append(name)

    for name, details in commands_dict.items():
        if details.get('uiData', {}).get('type') == 'unknown':
            if name in scraped_data:
                unknown_and_in_scraped += 1
            else:
                unknown_and_not_in_scraped += 1

    extra_in_scraped_count = len(set(scraped_data.keys()) - set(commands_dict.keys()))

    # Summary header (printed explicitly, flush to avoid being lost when piping)
    print("SECTION: SUMMARY", flush=True)
    print(f"Marker: {MARKER}")
    print(f"Total commands in commands.json: {total_commands}")
    print(f"Total commands in scraped_types.json: {scraped_commands_count}")
    if total_commands:
        print(f"Coverage: present in scraped_types.json: {commands_in_scraped} ({commands_in_scraped/total_commands:.2%})")
        print(f"Coverage: absent from scraped_types.json: {commands_not_in_scraped} ({commands_not_in_scraped/total_commands:.2%})")
    else:
        print("Coverage: commands.json is empty")
    print(f"Extra (only in scraped_types.json) COUNT ONLY (listing suppressed): {extra_in_scraped_count}")
    print(f"Type matches (exact): {type_matches}")
    print(f"Type matches (after normalization): {type_matches_alias}")
    total_matches = type_matches + type_matches_alias
    print(f"Type matches (total): {total_matches}")
    print(f"Type mismatches (raw): {type_mismatches_raw}")
    print(f"Type mismatches shown (excluding unknown original type): {len(mismatched_commands_filtered)}")
    print(f"Type mismatches suppressed (unknown original type): {suppressed_unknown_mismatches}")
    print(f"Missing commands shown (non-'command' type): {len(missing_non_command)}")
    print(f"Missing commands suppressed (uiData.type == 'command'): {suppressed_missing_command_type}")
    total_unknown = unknown_and_in_scraped + unknown_and_not_in_scraped
    print(f"Total 'unknown' original types: {total_unknown} (in scraped: {unknown_and_in_scraped}, not in scraped: {unknown_and_not_in_scraped})")
    print("END SUMMARY")
    print("-" * 50)

    if missing_non_command:
        print("SECTION: MISSING (Non-Command)")
        print("Criteria: Present in commands.json, absent in scraped_types.json, and uiData.type != 'command'.")
        print(f"Count: {len(missing_non_command)}")
        for cmd in sorted(missing_non_command):
            print(f"  - {cmd}")
        print("END MISSING")
        print("-" * 50)

    if mismatched_commands_filtered:
        print("SECTION: TYPE MISMATCHES (Excluding Unknown)")
        print("Criteria: Present in both, types differ, and commands.json uiData.type != 'unknown'.")
        print(f"Count: {len(mismatched_commands_filtered)}")
        for item in mismatched_commands_filtered:
            print(f"  - {item['command']}: commands.json='{item['original_type']}' scraped_types.json='{item['scraped_type']}'")
        print("END TYPE MISMATCHES")
        print("-" * 50)


if __name__ == "__main__":
    compare_files()
