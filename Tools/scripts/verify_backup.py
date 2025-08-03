import json
import os

def compare_json_files(file1_path, file2_path):
    """
    Compares two JSON files, ignoring the 'sourcedAt' key in consoleData.
    Returns True if they are the same, False otherwise.
    """
    with open(file1_path, 'r') as f1:
        data1 = json.load(f1)
    with open(file2_path, 'r') as f2:
        data2 = json.load(f2)

    # Function to recursively remove 'sourcedAt' from the data
    def clean_data(data):
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if key == 'consoleData':
                    if 'sourcedAt' in value:
                        del value['sourcedAt']
                else:
                    clean_data(value)
        elif isinstance(data, list):
            for item in data:
                clean_data(item)

    clean_data(data1)
    clean_data(data2)

    return data1 == data2

def main():
    """
    Compares the generated JSON files with their backups.
    """
    tools_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(tools_dir, 'data')
    backup_dir = os.path.join(data_dir, 'backup')
    classified_dir = os.path.join(data_dir, 'classified_commands')

    files_to_compare = {
        os.path.join(data_dir, 'commands.json'): os.path.join(backup_dir, 'commands.json'),
        os.path.join(classified_dir, 'player_commands.json'): os.path.join(backup_dir, 'player_commands.json'),
        os.path.join(classified_dir, 'server_commands.json'): os.path.join(backup_dir, 'server_commands.json'),
        os.path.join(classified_dir, 'shared_commands.json'): os.path.join(backup_dir, 'shared_commands.json'),
        os.path.join(classified_dir, 'uncategorized_commands.json'): os.path.join(backup_dir, 'uncategorized_commands.json'),
    }

    all_match = True
    for original_path, backup_path in files_to_compare.items():
        if os.path.exists(original_path) and os.path.exists(backup_path):
            if compare_json_files(original_path, backup_path):
                print(f"✅ {os.path.basename(original_path)} matches backup.")
            else:
                print(f"❌ {os.path.basename(original_path)} does NOT match backup.")
                all_match = False
        else:
            print(f"⚠️ Could not find one or both files: {original_path}, {backup_path}")
            all_match = False

    if all_match:
        print("\nAll files match their backups. No regressions found.")
    else:
        print("\nSome files do not match their backups. Regressions may have occurred.")

if __name__ == "__main__":
    main()
