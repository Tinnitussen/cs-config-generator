#!/usr/bin/env python3
"""
Apply Type Improvements Script

This script applies type improvements to commands.json using:
1. Manual type overrides (highest priority)
2. Scraped types from scraped_types.json (for 'unknown' types), excluding 'string' classifications

Strict Validation Logic:
- Rejects scraped 'bool' if raw defaultValue is not boolean-compatible (0/1/true/false).
- Rejects scraped 'command' if raw defaultValue is not null (implies it's a variable).
- Maps 'enum' to 'int' or 'unknown'.

Usage:
  python apply_type_improvements.py [--dry-run]
"""

import json
import os
import argparse
from typing import Dict, Any, Optional

# Type normalization map
TYPE_NORMALIZATION = {
    'float32': 'float',
    'int32': 'int',
    'uint32': 'uint32',
    'uint64': 'uint64',
    'bool': 'bool',
    'action': 'command',
    'enum': 'int',  # Map enum to int since we dropped Enum support
    'string': 'string',
    'vector': 'vector3',
    'vector3': 'vector3',
    'color': 'color'
}

ALLOWED_BOOL_STRINGS = {"1", "0", "true", "false", "yes", "no", "on", "off"}

def normalize_type(type_str):
    """Normalize type strings to canonical forms (case-insensitive)."""
    if not type_str:
        return type_str
    key = str(type_str).strip().lower()
    return TYPE_NORMALIZATION.get(key, key)

def is_valid_bool_value(val) -> bool:
    """Return True if val is an allowed boolean representation."""
    if isinstance(val, bool):
        return True
    if isinstance(val, (int, float)):
        return val in (0, 1)
    if isinstance(val, str):
        return val.strip().lower() in ALLOWED_BOOL_STRINGS
    return False

def coerce_default_value(new_type: str, current_value):
    """Coerce a defaultValue to the JSON shape expected by the C# UiData subtype."""
    try:
        if new_type == 'bool':
            if isinstance(current_value, bool): return current_value
            if isinstance(current_value, (int, float)): return current_value != 0
            if isinstance(current_value, str):
                v = current_value.strip().lower()
                if v in ('1', 'true', 'yes', 'on'): return True
                return False
            return False

        if new_type in ('int', 'bitmask', 'uint32', 'uint64'):
            if isinstance(current_value, int): return current_value
            if isinstance(current_value, float): return int(current_value)
            if isinstance(current_value, bool): return 1 if current_value else 0
            if isinstance(current_value, str):
                # Try parsing float then int to handle "1.0000"
                try:
                    return int(float(current_value))
                except ValueError:
                    return 0
            return 0

        if new_type == 'float':
            if isinstance(current_value, (int, float)): return float(current_value)
            if isinstance(current_value, bool): return 1.0 if current_value else 0.0
            if isinstance(current_value, str):
                try:
                    return float(current_value)
                except ValueError:
                    return 0.0
            return 0.0

        if new_type in ('string', 'vector2', 'vector3', 'color', 'command'):
            if current_value is None: return ''
            return str(current_value)

        return current_value
    except Exception:
        if new_type == 'bool': return False
        if new_type in ('int', 'bitmask', 'uint32', 'uint64'): return 0
        if new_type == 'float': return 0.0
        return ''

def load_manual_overrides(data_dir):
    """Load manual type overrides."""
    overrides_path = os.path.join(data_dir, 'manual_type_overrides.json')
    if not os.path.exists(overrides_path):
        return {}
    with open(overrides_path, 'r', encoding='utf-8') as f:
        overrides = json.load(f)
    return {k: v for k, v in overrides.items() if not k.startswith('_')}

def load_scraped_types(data_dir):
    """Load scraped types."""
    scraped_path = os.path.join(data_dir, 'scraped_types.json')
    if not os.path.exists(scraped_path):
        print(f"Warning: Scraped types file not found: {scraped_path}")
        return {}

    with open(scraped_path, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    cleaned = {}
    for cmd, data in scraped_data.items():
        t = normalize_type(data.get('type'))
        if t == 'string': continue  # Skip scraped 'string' types
        cleaned[cmd] = t
    return cleaned

def apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=False):
    """
    Apply type improvements with strict validation.
    """
    stats = {
        'total': len(commands),
        'manual_overrides_applied': 0,
        'scraped_types_applied': 0,
        'scraped_rejected': 0,
        'unknown_remaining': 0,
        'skipped_no_uidata': 0,
    }

    manifest_entries = []

    for cmd in commands:
        cmd_name = cmd.get('command')
        if 'uiData' not in cmd:
            stats['skipped_no_uidata'] += 1
            continue

        current_type = cmd['uiData'].get('type')
        current_default = cmd['uiData'].get('defaultValue')

        # Determine raw default value (trust consoleData primarily if available)
        raw_default = None
        if 'consoleData' in cmd:
            raw_default = cmd['consoleData'].get('defaultValue')
        else:
            raw_default = current_default # Fallback if consoleData missing (unlikely)

        new_type = None
        source = None

        # 1. Manual Overrides
        if cmd_name in manual_overrides:
            new_type = normalize_type(manual_overrides[cmd_name])
            source = 'manual_override'
            stats['manual_overrides_applied'] += 1

        # 2. Scraped Types (only if currently unknown or explicitly re-evaluating)
        # We only upgrade 'unknown' types using scraped data
        elif current_type == 'unknown' and cmd_name in scraped_types:
            candidate_type = scraped_types[cmd_name]

            # --- Strict Validation Rules ---
            is_valid = True
            rejection_reason = ""

            # Rule: Reject 'bool' if raw default is not bool-compatible
            if candidate_type == 'bool':
                if not is_valid_bool_value(raw_default):
                    is_valid = False
                    rejection_reason = f"Raw value '{raw_default}' is not boolean-compatible"

            # Rule: Reject 'command' if raw default is not None/Null (implies variable)
            elif candidate_type == 'command':
                if raw_default is not None:
                    is_valid = False
                    rejection_reason = f"Raw value '{raw_default}' implies variable, not command"

            if is_valid:
                new_type = candidate_type
                source = 'scraped_type'
                stats['scraped_types_applied'] += 1

                manifest_entries.append({
                    "command": cmd_name,
                    "old_type": current_type,
                    "new_type": new_type,
                    "raw_default": raw_default,
                    "source": "scraped"
                })
            else:
                stats['scraped_rejected'] += 1
                if dry_run:
                    print(f"  [REJECT] {cmd_name}: scraped '{candidate_type}' rejected. {rejection_reason}")

        # Apply changes
        if new_type and new_type != current_type:
            if not dry_run:
                old_type_val = cmd['uiData']['type']
                cmd['uiData']['type'] = new_type
                # Coerce default value
                coerced = coerce_default_value(new_type, current_default)
                cmd['uiData']['defaultValue'] = coerced
                print(f"  {cmd_name}: {old_type_val} -> {new_type} (source: {source})")
            else:
                print(f"  [DRY RUN] {cmd_name}: {current_type} -> {new_type} (source: {source})")

        final_type = new_type if new_type else current_type
        if final_type == 'unknown':
            stats['unknown_remaining'] += 1

    return commands, stats, manifest_entries

def main():
    parser = argparse.ArgumentParser(description="Apply type improvements to commands.json")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be changed without modifying files")
    args = parser.parse_args()

    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(tools_dir, 'data')
    commands_path = os.path.join(data_dir, 'commands.json')
    manifest_path = os.path.join(data_dir, 'scraped_classification_manifest.json')

    print("=" * 60)
    print("Apply Type Improvements (Strict Mode)")
    print("=" * 60)

    # Load data
    print("\n1. Loading data files...")
    manual_overrides = load_manual_overrides(data_dir)
    scraped_types = load_scraped_types(data_dir)

    try:
        with open(commands_path, 'r', encoding='utf-8') as f:
            commands = json.load(f)
    except FileNotFoundError:
        print(f"Error: commands.json not found at {commands_path}")
        return

    print(f"   Loaded {len(commands)} commands")
    print(f"   Loaded {len(scraped_types)} scraped types")
    print(f"   Loaded {len(manual_overrides)} manual overrides")

    # Apply improvements
    print("\n2. Applying type improvements...")
    updated_commands, stats, manifest = apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=args.dry_run)

    # Save results
    if not args.dry_run:
        print("\n3. Saving updated commands.json...")
        with open(commands_path, 'w', encoding='utf-8') as f:
            json.dump(updated_commands, f, indent=2)
        print(f"   Saved to: {commands_path}")

        print(f"   Saving classification manifest...")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        print(f"   Saved to: {manifest_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total commands: {stats['total']}")
    print(f"Manual overrides applied: {stats['manual_overrides_applied']}")
    print(f"Scraped types applied: {stats['scraped_types_applied']}")
    print(f"Scraped types rejected: {stats['scraped_rejected']}")
    print(f"Unknown types remaining: {stats['unknown_remaining']}")

if __name__ == "__main__":
    main()
