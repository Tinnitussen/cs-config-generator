#!/usr/bin/env python3
"""
Apply Type Improvements Script

This script applies type improvements to commands.json using:
1. Manual type overrides (highest priority)
2. Scraped types from scraped_types.json (for 'unknown' types)

Usage:
  python apply_type_improvements.py [--dry-run]
"""

import json
import os
import argparse

# Type normalization map (from compare_commands.py)
TYPE_NORMALIZATION = {
    'float32': 'float',
    'int32': 'int',
    'uint32': 'uint',
    'uint64': 'uint',
}

def normalize_type(type_str):
    """Normalize type strings to canonical forms."""
    if not type_str:
        return type_str
    return TYPE_NORMALIZATION.get(type_str, type_str)

def create_manual_overrides_file(data_dir):
    """Create the manual_type_overrides.json file if it doesn't exist."""
    overrides_path = os.path.join(data_dir, 'manual_type_overrides.json')

    if os.path.exists(overrides_path):
        print(f"Manual overrides file already exists: {overrides_path}")
        return overrides_path

    manual_overrides = {
        "_comment": "Manual type overrides for commands where automated classification needs correction. Takes precedence over all other sources.",
        "ai_debug_scripted_sequence": "bool",
        "demo_pauseatservertick": "command",
        "skill": "int",
        "fog_color": "vector3",
        "fog_colorskybox": "color",
        "hidehud": "int",
        "mat_overdraw_color": "color",
        "mat_shading_complexity_color": "color",
        "r_light_probe_volume_debug_colors": "bool",
        "r_light_probe_volume_debug_grid_albedo": "color"
    }

    with open(overrides_path, 'w', encoding='utf-8') as f:
        json.dump(manual_overrides, f, indent=2)

    print(f"Created manual overrides file: {overrides_path}")
    return overrides_path

def load_manual_overrides(data_dir):
    """Load manual type overrides."""
    overrides_path = os.path.join(data_dir, 'manual_type_overrides.json')

    if not os.path.exists(overrides_path):
        print("No manual overrides file found, creating one...")
        create_manual_overrides_file(data_dir)

    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)

    # Remove metadata keys
    return {k: v for k, v in overrides.items() if not k.startswith('_')}

def load_scraped_types(data_dir):
    """Load scraped types and normalize them."""
    scraped_path = os.path.join(data_dir, 'scraped_types.json')

    if not os.path.exists(scraped_path):
        print(f"Warning: Scraped types file not found: {scraped_path}")
        return {}

    with open(scraped_path, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    # Normalize types
    return {cmd: normalize_type(data.get('type')) for cmd, data in scraped_data.items()}

def apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=False):
    """
    Apply type improvements to commands.

    Priority order:
    1. Manual overrides (always applied)
    2. Scraped types (only for 'unknown' types)
    """
    stats = {
        'total': len(commands),
        'manual_overrides_applied': 0,
        'scraped_types_applied': 0,
        'unknown_remaining': 0,
        'skipped_no_uidata': 0
    }

    for cmd in commands:
        cmd_name = cmd.get('command')

        # Skip if no uiData
        if 'uiData' not in cmd:
            stats['skipped_no_uidata'] += 1
            continue

        current_type = cmd['uiData'].get('type')
        new_type = None
        source = None

        # Priority 1: Manual overrides (always applied)
        if cmd_name in manual_overrides:
            new_type = manual_overrides[cmd_name]
            source = 'manual_override'
            stats['manual_overrides_applied'] += 1

        # Priority 2: Scraped types (only if current type is 'unknown')
        elif current_type == 'unknown' and cmd_name in scraped_types:
            new_type = scraped_types[cmd_name]
            source = 'scraped_type'
            stats['scraped_types_applied'] += 1

        # Apply the new type if found
        if new_type and not dry_run:
            old_type = current_type
            cmd['uiData']['type'] = new_type
            print(f"  {cmd_name}: {old_type} -> {new_type} (source: {source})")
        elif new_type and dry_run:
            print(f"  [DRY RUN] {cmd_name}: {current_type} -> {new_type} (source: {source})")

        # Count remaining unknowns
        final_type = new_type if new_type else current_type
        if final_type == 'unknown':
            stats['unknown_remaining'] += 1

    return commands, stats

def export_unknown_overrides(data_dir, commands):
    """Append unknown uiData.type commands to manual_type_overrides.json with value 'unknown'."""
    overrides_path = os.path.join(data_dir, 'manual_type_overrides.json')
    if not os.path.exists(overrides_path):
        create_manual_overrides_file(data_dir)
    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
    # Collect existing (excluding meta keys)
    existing_keys = {k for k in overrides.keys() if not k.startswith('_')}
    unknown_cmds = [c['command'] for c in commands if c.get('uiData', {}).get('type') == 'unknown']
    added = []
    for cmd in unknown_cmds:
        if cmd not in existing_keys:
            overrides[cmd] = 'unknown'
            added.append(cmd)
    if added:
        with open(overrides_path, 'w', encoding='utf-8') as f:
            json.dump(overrides, f, indent=2)
    print(f"Export unknown overrides: {len(added)} added, {len(unknown_cmds)} unknown total.")
    if added:
        print("Added unknown placeholders:")
        for a in added:
            print(f"  - {a}")
    else:
        print("No new unknown commands to add.")

def main():
    parser = argparse.ArgumentParser(description="Apply type improvements to commands.json")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be changed without modifying files")
    parser.add_argument('--export-unknown', action='store_true', help="Append remaining unknown commands to manual_type_overrides.json with REVIEW placeholders")
    args = parser.parse_args()

    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(tools_dir, 'data')
    commands_path = os.path.join(data_dir, 'commands.json')

    print("=" * 60)
    print("Apply Type Improvements")
    print("=" * 60)

    if args.dry_run:
        print("\n[!] DRY RUN MODE - No files will be modified (except export of unknown overrides, which always writes)\n")

    # Load data
    print("\n1. Loading data files...")
    manual_overrides = load_manual_overrides(data_dir)
    print(f"   Loaded {len(manual_overrides)} manual overrides")
    scraped_types = load_scraped_types(data_dir)
    print(f"   Loaded {len(scraped_types)} scraped types")
    with open(commands_path, 'r', encoding='utf-8') as f:
        commands = json.load(f)
    print(f"   Loaded {len(commands)} commands")

    if args.export_unknown:
        print("\n[EXPORT] Appending unknown commands to manual_type_overrides.json ...")
        export_unknown_overrides(data_dir, commands)

    # Apply improvements
    print("\n2. Applying type improvements...")
    updated_commands, stats = apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=args.dry_run)

    # Save results
    if not args.dry_run:
        print("\n3. Saving updated commands.json...")
        with open(commands_path, 'w', encoding='utf-8') as f:
            json.dump(updated_commands, f, indent=2)
        print(f"   Saved to: {commands_path}")
    else:
        print("\n3. Skipping save (dry run mode)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total commands: {stats['total']}")
    print(f"Manual overrides applied: {stats['manual_overrides_applied']}")
    print(f"Scraped types applied: {stats['scraped_types_applied']}")
    print(f"Unknown types remaining: {stats['unknown_remaining']}")
    print(f"Commands without uiData: {stats['skipped_no_uidata']}")
    if stats['unknown_remaining'] > 0:
        print(f"\n[!] {stats['unknown_remaining']} commands still have 'unknown' type")
    if args.dry_run:
        print("\n[OK] Dry run complete - run without --dry-run to apply changes")
    else:
        print("\n[OK] Type improvements applied successfully!")

if __name__ == "__main__":
    main()
