import json
import os
from typing import Dict, List, Any

def load_commands(filepath: str) -> List[Dict]:
    """Load the commands.json file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: List[Dict], filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def has_sv_flag(command: Dict) -> bool:
    """Check if a command has the 'sv' flag"""
    flags = command.get('consoleData', {}).get('flags', [])
    return 'sv' in flags



def split_commands_by_sv_flag(commands: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Split commands into server and player commands based on 'sv' flag.
    Returns (server_commands, player_commands)
    """
    server_commands = []
    player_commands = []
    
    for command in commands:
        if has_sv_flag(command):
            server_commands.append(command)
        else:
            player_commands.append(command)
    
    return server_commands, player_commands

def verify_data_integrity(original: List[Dict], server: List[Dict], player: List[Dict]) -> Dict[str, Any]:
    """
    Verify that the split data maintains integrity with the original.
    Returns verification results.
    """
    results = {
        'passed': True,
        'issues': [],
        'stats': {}
    }
    
    # Check total count
    original_count = len(original)
    combined_count = len(server) + len(player)
    results['stats']['original_count'] = original_count
    results['stats']['combined_count'] = combined_count
    
    if original_count != combined_count:
        results['passed'] = False
        results['issues'].append(f"Count mismatch: original={original_count}, combined={combined_count}")
    
    # Create sets of command names for comparison
    original_commands = {cmd['command'] for cmd in original}
    server_commands = {cmd['command'] for cmd in server}
    player_commands = {cmd['command'] for cmd in player}
    combined_commands = server_commands.union(player_commands)
    
    # Check for missing commands
    missing_from_split = original_commands - combined_commands
    if missing_from_split:
        results['passed'] = False
        results['issues'].append(f"Commands missing from split: {sorted(missing_from_split)}")
    
    # Check for extra commands
    extra_in_split = combined_commands - original_commands
    if extra_in_split:
        results['passed'] = False
        results['issues'].append(f"Extra commands in split: {sorted(extra_in_split)}")
    
    # Check for duplicates between server and player
    duplicates = server_commands.intersection(player_commands)
    if duplicates:
        results['passed'] = False
        results['issues'].append(f"Commands in both server and player: {sorted(duplicates)}")
    
    # Verify individual command data integrity
    original_by_name = {cmd['command']: cmd for cmd in original}
    all_split_commands = server + player
    
    for split_cmd in all_split_commands:
        cmd_name = split_cmd['command']
        if cmd_name in original_by_name:
            original_cmd = original_by_name[cmd_name]
            # Deep comparison of command data
            if json.dumps(original_cmd, sort_keys=True) != json.dumps(split_cmd, sort_keys=True):
                results['passed'] = False
                results['issues'].append(f"Data mismatch for command '{cmd_name}'")
    
    results['stats']['server_count'] = len(server)
    results['stats']['player_count'] = len(player)
    results['stats']['duplicates_count'] = len(duplicates)
    
    return results

def main():
    input_file = "data/commands.json"
    server_output = "data/server.json"
    player_output = "data/player.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    print(f"Loading commands from '{input_file}'...")
    commands = load_commands(input_file)
    
    print("Splitting commands by 'sv' flag...")
    server_commands, player_commands = split_commands_by_sv_flag(commands)
    
    print("Verifying data integrity...")
    integrity_check = verify_data_integrity(commands, server_commands, player_commands)
    
    # Print integrity check results
    print("\n--- DATA INTEGRITY VERIFICATION ---")
    if integrity_check['passed']:
        print("✓ Data integrity check PASSED")
        print("✓ All original data preserved in split")
        print("✓ No duplicates or missing commands")
    else:
        print("✗ Data integrity check FAILED")
        for issue in integrity_check['issues']:
            print(f"  - {issue}")
        print("\nAborting save due to integrity issues.")
        return
    
    # Only proceed with saving if integrity check passed
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(server_output), exist_ok=True)
    
    print(f"\nSaving server commands to '{server_output}'...")
    save_json(server_commands, server_output)
    
    print(f"Saving player commands to '{player_output}'...")
    save_json(player_commands, player_output)
    
    # Print summary
    stats = integrity_check['stats']
    total_commands = stats['original_count']
    server_count = stats['server_count']
    player_count = stats['player_count']
    
    print("\n--- SPLIT SUMMARY ---")
    print(f"Total commands processed: {total_commands}")
    print(f"Server commands (with 'sv' flag): {server_count} ({server_count/total_commands*100:.1f}%)")
    print(f"Player commands (without 'sv' flag): {player_count} ({player_count/total_commands*100:.1f}%)")
    print(f"Data integrity: {'✓ PASSED' if integrity_check['passed'] else '✗ FAILED'}")
    
    # Show some examples
    if server_commands:
        print(f"\nExample server commands:")
        for i, cmd in enumerate(server_commands[:5]):
            flags = cmd.get('consoleData', {}).get('flags', [])
            print(f"  - {cmd['command']} (flags: {', '.join(flags)})")
    
    if player_commands:
        print(f"\nExample player commands:")
        for i, cmd in enumerate(player_commands[:5]):
            flags = cmd.get('consoleData', {}).get('flags', [])
            flag_str = ', '.join(flags) if flags else 'none'
            print(f"  - {cmd['command']} (flags: {flag_str})")
    
    print(f"\nFiles created:")
    print(f"  - {server_output}")
    print(f"  - {player_output}")
    
    # Final verification summary
    print(f"\n--- VERIFICATION SUMMARY ---")
    print(f"Original commands: {stats['original_count']}")
    print(f"Combined split commands: {stats['combined_count']}")
    print(f"Duplicates between splits: {stats['duplicates_count']}")
    print(f"Integrity check: {'PASSED' if integrity_check['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()