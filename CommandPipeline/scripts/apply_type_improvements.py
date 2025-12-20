#!/usr/bin/env python3
"""
Apply Type Improvements Script

This script applies type improvements to commands.json using:
1. Manual type overrides (highest priority)
2. Vector heuristics: Detects vector2/vector3 by splitting default values (splits into 2 or 3 numbers)

Note: Scraped types have been removed from the pipeline due to reliability concerns.
All type classifications now come from either:
- Deterministic heuristics (bool, command, bitmask, float literal, vector)
- Numeric detection from config files
- Manual overrides (human-verified classifications)

Usage:
  python apply_type_improvements.py [--dry-run]
"""

import json
import os
import argparse
from typing import Optional


# Type normalization map (kept for manual overrides compatibility)
TYPE_NORMALIZATION = {
    'float32': 'float',
    'int32': 'int',
    'uint32': 'uint32',
    'uint64': 'uint64',
    'bool': 'bool',
    'action': 'command',
    'enum': 'int',
    'string': 'string',
    'vector': 'vector3',
    'vector2': 'vector2',
    'vector3': 'vector3',
    'color': 'color'
}


def normalize_type(type_str):
    """Normalize type strings to canonical forms (case-insensitive)."""
    if not type_str:
        return type_str
    key = str(type_str).strip().lower()
    return TYPE_NORMALIZATION.get(key, key)


def detect_vector_type(val) -> Optional[str]:
    """
    Detect if a value is a vector2 or vector3 based on splitting the string.
    Returns 'vector2', 'vector3', or None.
    """
    if not isinstance(val, str):
        return None

    parts = val.strip().split()
    if len(parts) not in (2, 3):
        return None

    # Verify all parts are numbers
    try:
        for p in parts:
            float(p)
    except ValueError:
        return None

    return 'vector3' if len(parts) == 3 else 'vector2'


def load_manual_overrides(data_dir):
    """Load manual type overrides."""
    overrides_path = os.path.join(data_dir, 'manual_type_overrides.json')
    if not os.path.exists(overrides_path):
        return {}
    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
    return {k: v for k, v in overrides.items() if not k.startswith('_')}


def apply_type_improvements(commands, manual_overrides, dry_run=False):
    """
    Apply type improvements using manual overrides and vector heuristics.
    
    Scraped types have been removed from the pipeline.
    """
    stats = {
        'total': len(commands),
        'manual_overrides_applied': 0,
        'heuristic_vectors_applied': 0,
        'unknown_remaining': 0,
        'skipped_no_typeinfo': 0,
    }

    for cmd in commands:
        cmd_name = cmd.get('command')
        if 'typeInfo' not in cmd:
            stats['skipped_no_typeinfo'] += 1
            continue

        current_type = cmd['typeInfo'].get('type')

        # Get raw default value from consoleData (source of truth)
        raw_default = cmd.get('consoleData', {}).get('defaultValue')

        new_type = None
        source = None

        # 1. Manual Overrides (highest priority)
        if cmd_name in manual_overrides:
            new_type = normalize_type(manual_overrides[cmd_name])
            source = 'manual_override'
            stats['manual_overrides_applied'] += 1

        # 2. Vector Heuristics (for string/unknown types)
        candidate_type = new_type if new_type else current_type

        if candidate_type in ('string', 'unknown'):
            vector_type = detect_vector_type(raw_default)

            if vector_type:
                new_type = vector_type
                source = 'heuristic_vector'
                stats['heuristic_vectors_applied'] += 1

        # Apply changes
        if new_type and new_type != current_type:
            if not dry_run:
                old_type_val = cmd['typeInfo']['type']
                cmd['typeInfo']['type'] = new_type
                print(f"  {cmd_name}: {old_type_val} -> {new_type} (source: {source})")
            else:
                print(f"  [DRY RUN] {cmd_name}: {current_type} -> {new_type} (source: {source})")

        final_type = new_type if new_type else current_type
        if final_type == 'unknown':
            stats['unknown_remaining'] += 1

    return commands, stats


def main():
    parser = argparse.ArgumentParser(description="Apply type improvements to commands.json")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be changed without modifying files")
    args = parser.parse_args()

    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(tools_dir, 'data')
    commands_path = os.path.join(data_dir, 'commands.json')

    print("=" * 60)
    print("Apply Type Improvements")
    print("=" * 60)

    # Load data
    print("\n1. Loading data files...")
    manual_overrides = load_manual_overrides(data_dir)

    try:
        with open(commands_path, 'r', encoding='utf-8') as f:
            commands = json.load(f)
    except FileNotFoundError:
        print(f"Error: commands.json not found at {commands_path}")
        return

    print(f"   Loaded {len(commands)} commands")
    print(f"   Loaded {len(manual_overrides)} manual overrides")

    # Apply improvements
    print("\n2. Applying type improvements...")
    updated_commands, stats = apply_type_improvements(commands, manual_overrides, dry_run=args.dry_run)

    # Save results
    if not args.dry_run:
        print("\n3. Saving updated commands.json...")
        with open(commands_path, 'w', encoding='utf-8') as f:
            json.dump(updated_commands, f, indent=2)
        print(f"   Saved to: {commands_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total commands: {stats['total']}")
    print(f"Manual overrides applied: {stats['manual_overrides_applied']}")
    print(f"Heuristic vectors applied: {stats['heuristic_vectors_applied']}")
    print(f"Unknown types remaining: {stats['unknown_remaining']}")


if __name__ == "__main__":
    main()
