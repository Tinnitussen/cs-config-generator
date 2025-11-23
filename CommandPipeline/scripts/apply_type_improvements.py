#!/usr/bin/env python3
"""
Apply Type Improvements Script

This script applies type improvements to commands.json using:
1. Manual type overrides (highest priority)
2. Scraped types from scraped_types.json (for 'unknown' types), excluding 'string' classifications

Bool overrides are only applied if the existing defaultValue is an allowed boolean token: 1,0,true,false (case-insensitive).
Command/Action types are rejected if a default value exists (implying it's a variable).

Usage:
  python apply_type_improvements.py [--dry-run]
"""

import json
import os
import argparse

# Type normalization map (from compare_commands.py) plus scraped-type canonicalizations
TYPE_NORMALIZATION = {
    'float32': 'float',
    'int32': 'int',
    'uint32': 'uint32',
    'uint64': 'uint64',
    'bool': 'bool',
    'action': 'command',
    'command': 'command',
    'enum': 'int',  # Map enum to int per strict validation rules
    'string': 'string',
}

def normalize_type(type_str):
    """Normalize type strings to canonical forms (case-insensitive)."""
    if not type_str:
        return type_str
    key = str(type_str).strip().lower()
    return TYPE_NORMALIZATION.get(key, key)

ALLOWED_BOOL_STRINGS = {"1", "0", "true", "false"}

def is_valid_bool_value(val) -> bool:
    """Return True if val is an allowed boolean representation."""
    if isinstance(val, bool):
        return True
    if isinstance(val, (int, float)):
        return val in (0, 1)
    if isinstance(val, str):
        return val.strip().lower() in ALLOWED_BOOL_STRINGS
    return False

# --- Default value coercion helpers ---

def coerce_default_value(new_type: str, current_value):
    """Coerce a defaultValue to the JSON shape expected by the C# UiData subtype.

    Rules:
      bool    -> JSON boolean
      int/uint/bitmask -> JSON number (int)
      float   -> JSON number (float)
      command -> keep (usually None or empty); ensure string
      string/vector2/vector3/color -> JSON string
      unknown -> leave as-is (number or string acceptable)
    """
    try:
        if new_type == 'bool':
            # Accept numeric or string indicators
            if isinstance(current_value, bool):
                return current_value
            if isinstance(current_value, (int, float)):
                return current_value != 0
            if isinstance(current_value, str):
                v = current_value.strip().lower()
                if v in ('1', 'true'): return True
                if v in ('0', 'false'): return False
                # Fallback: any non-empty non-zero-ish string -> True
                return v not in ('', '0', 'false', 'no')
            # Fallback
            return False

        if new_type in ('int', 'bitmask', 'uint'):
            if isinstance(current_value, int):
                return current_value
            if isinstance(current_value, float):
                return int(current_value)
            if isinstance(current_value, bool):
                return 1 if current_value else 0
            if isinstance(current_value, str):
                try:
                    if '.' in current_value:
                        return int(float(current_value))
                    return int(current_value)
                except ValueError:
                    return 0
            return 0

        if new_type == 'float':
            if isinstance(current_value, (int, float)):
                return float(current_value)
            if isinstance(current_value, bool):
                return 1.0 if current_value else 0.0
            if isinstance(current_value, str):
                try:
                    return float(current_value)
                except ValueError:
                    return 0.0
            return 0.0

        if new_type in ('string', 'vector2', 'vector3', 'color', 'command'):
            # Ensure string representation
            if current_value is None:
                return ''
            return str(current_value)

        # unknown or any other
        return current_value
    except Exception:
        # Defensive fallback
        if new_type == 'bool':
            return False
        if new_type in ('int', 'bitmask', 'uint'):
            return 0
        if new_type == 'float':
            return 0.0
        return '' if new_type in ('string', 'vector2', 'vector3', 'color', 'command') else current_value

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
    """Load scraped types and normalize them, ignoring any 'string' classifications."""
    scraped_path = os.path.join(data_dir, 'scraped_types.json')

    if not os.path.exists(scraped_path):
        print(f"Warning: Scraped types file not found: {scraped_path}")
        return {}

    with open(scraped_path, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    cleaned = {}
    for cmd, data in scraped_data.items():
        t = normalize_type(data.get('type'))
        # Note: Filter here is redundant if we filter in the loop, but kept for consistency
        # However, to test redundancy, we rely on the loop filter mainly.
        if t == 'string':
             continue
        cleaned[cmd] = t
    return cleaned

def apply_type_improvements(commands, manual_overrides, scraped_types, data_dir=None, dry_run=False):
    """
    Apply type improvements to commands.

    Priority order:
    1. Manual overrides (always applied; may include 'string')
    2. Scraped types (only for 'unknown' types; never 'string')

    Ensures the defaultValue JSON shape matches the target type to avoid deserialization errors.
    Bool type changes are skipped if the existing defaultValue cannot be parsed as a bool.
    Command type changes are skipped if a default value exists (implying it's a variable).
    """
    stats = {
        'total': len(commands),
        'manual_overrides_applied': 0,
        'scraped_types_applied': 0,
        'unknown_remaining': 0,
        'skipped_no_uidata': 0,
        'coerced_defaults': 0,
        'bool_unparseable_skipped': 0,
        'command_with_value_skipped': 0,
        'string_scraped_skipped': 0
    }

    manifest_entries = []

    for cmd in commands:
        cmd_name = cmd.get('command')

        if 'uiData' not in cmd:
            stats['skipped_no_uidata'] += 1
            continue

        current_type = cmd['uiData'].get('type')
        current_default = cmd['uiData'].get('defaultValue')

        # Raw default value from console data (if available)
        raw_default = cmd.get('consoleData', {}).get('defaultValue')

        new_type = None
        source = None

        if cmd_name in manual_overrides:
            new_type = normalize_type(manual_overrides[cmd_name])
            source = 'manual_override'
            stats['manual_overrides_applied'] += 1
        elif current_type == 'unknown' and cmd_name in scraped_types:
            candidate_type = scraped_types[cmd_name]

            # Explicitly ignore 'string' from scraped data even if loader didn't filter it
            if candidate_type == 'string':
                if dry_run:
                    print(f"  [DRY RUN] {cmd_name}: skipped scraped 'string' type")
                stats['string_scraped_skipped'] += 1
                continue

            new_type = candidate_type
            source = 'scraped_type'
            stats['scraped_types_applied'] += 1

        # --- Strict Validations ---

        # 1. Validate bool applicability
        if new_type == 'bool' and not is_valid_bool_value(current_default):
            if dry_run:
                print(f"  [DRY RUN] {cmd_name}: skip bool override (unparseable defaultValue={current_default!r})")
            else:
                print(f"  {cmd_name}: skipped bool override (unparseable defaultValue={current_default!r})")
            new_type = None
            stats['bool_unparseable_skipped'] += 1

        # 2. Validate 'command' type applicability
        # If scraped as 'command' but has a raw default value (not None/empty), it's likely a variable.
        if new_type == 'command' and raw_default is not None and str(raw_default).strip() != "":
             if dry_run:
                print(f"  [DRY RUN] {cmd_name}: skip command override (has defaultValue={raw_default!r})")
             else:
                print(f"  {cmd_name}: skipped command override (has defaultValue={raw_default!r})")
             new_type = None
             stats['command_with_value_skipped'] += 1

        if new_type:
            old_type = current_type

            # Apply changes
            if not dry_run:
                cmd['uiData']['type'] = new_type
                # Coerce default if type actually changes or if bool target with numeric default
                if old_type != new_type:
                    coerced = coerce_default_value(new_type, current_default)
                    if coerced != current_default:
                        stats['coerced_defaults'] += 1
                        cmd['uiData']['defaultValue'] = coerced
                print(f"  {cmd_name}: {old_type} -> {new_type} (source: {source})")

                # Add to manifest
                manifest_entries.append({
                    "command": cmd_name,
                    "old_type": old_type,
                    "new_type": new_type,
                    "source": source
                })

            elif dry_run:
                potential_default = coerce_default_value(new_type, current_default)
                changed_marker = ' [coerced default]' if potential_default != current_default else ''
                print(f"  [DRY RUN] {cmd_name}: {current_type} -> {new_type}{changed_marker} (source: {source})")

        final_type = new_type if new_type else current_type
        if final_type == 'unknown':
            stats['unknown_remaining'] += 1

    # Write manifest if not dry run and data_dir provided
    if not dry_run and data_dir and manifest_entries:
        manifest_path = os.path.join(data_dir, 'scraped_classification_manifest.json')
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_entries, f, indent=2)
            print(f"  Generated manifest: {manifest_path}")
        except Exception as e:
            print(f"  Error writing manifest: {e}")

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
    updated_commands, stats = apply_type_improvements(commands, manual_overrides, scraped_types, data_dir=data_dir, dry_run=args.dry_run)

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
    print(f"Bool unparseable skipped: {stats['bool_unparseable_skipped']}")
    print(f"Command with value skipped: {stats['command_with_value_skipped']}")
    if stats['unknown_remaining'] > 0:
        print(f"\n[!] {stats['unknown_remaining']} commands still have 'unknown' type")
    if args.dry_run:
        print("\n[OK] Dry run complete - run without --dry-run to apply changes")
    else:
        print("\n[OK] Type improvements applied successfully!")

if __name__ == "__main__":
    main()
