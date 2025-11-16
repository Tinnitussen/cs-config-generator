"""
Shared path constants for the CS Commands Processing Pipeline.

This module provides standardized paths for all scripts in the pipeline,
ensuring consistency and preventing path-related issues when running
scripts from different directories.
"""

import os
import sys
from pathlib import Path
from typing import List

# Base directories - calculated dynamically from this file's location
UTILS_DIR = Path(__file__).parent.resolve()
PIPELINE_DIR = UTILS_DIR.parent
PROJECT_ROOT = PIPELINE_DIR.parent

# --- Input Directories ---
DATA_DIR = PIPELINE_DIR / "data"
RULES_DIR = PIPELINE_DIR / "rules"
SCRIPTS_DIR = PIPELINE_DIR / "scripts"

# Config source directories
PRO_PLAYER_CONFIGS_DIR = DATA_DIR / "pro-player-configs" / "unzipped-configs"
SERVER_CONFIGS_DIR = DATA_DIR / "server-configs"

# --- Main Data Files ---
COMMANDS_JSON = DATA_DIR / "commands.json"
PARSING_RULES_JSON = RULES_DIR / "parsing_validation_rules.json"

# --- File Patterns ---
SNAPSHOT_PATTERN = "all_commands-*.txt"
SNAPSHOT_GLOB = str(DATA_DIR / SNAPSHOT_PATTERN)

# --- Output Directories ---
SCHEMA_DIR = PROJECT_ROOT / "CSConfigGenerator" / "wwwroot" / "data" / "commandschema"

# Schema output directories
ALL_SCHEMA_DIR = SCHEMA_DIR / ""

def setup_rules_import():
    """
    Add the rules directory to sys.path for importing rule modules.
    This should be called by any script that needs to import from the rules directory.
    """
    rules_path = str(RULES_DIR)
    if rules_path not in sys.path:
        sys.path.append(rules_path)

def ensure_output_dirs():
    """
    Create all necessary output directories if they don't exist.
    """
    dirs_to_create = [
        DATA_DIR,
        SCHEMA_DIR,
        ALL_SCHEMA_DIR
    ]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

def find_snapshot_files() -> List[Path]:
    """
    Find all available command snapshot files, sorted by modification time (newest first).

    Returns:
        List of Path objects for snapshot files
    """
    import glob

    files = glob.glob(SNAPSHOT_GLOB)
    if not files:
        return []

    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return [Path(f) for f in files]

def get_latest_snapshot() -> Path:
    """
    Get the most recent snapshot file.

    Returns:
        Path to the latest snapshot file

    Raises:
        FileNotFoundError: If no snapshot files are found
    """
    files = find_snapshot_files()
    if not files:
        raise FileNotFoundError(f"No snapshot files found matching pattern: {SNAPSHOT_GLOB}")

    return files[0]

# Convenience functions for common operations
def load_json(filepath: Path):
    """Load JSON file with error handling"""
    import json

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load JSON from {filepath}: {e}")

def save_json(data, filepath: Path, create_dirs: bool = True):
    """Save data to JSON file with error handling"""
    import json

    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except (OSError, TypeError) as e:
        raise RuntimeError(f"Failed to save JSON to {filepath}: {e}")

# Debug function to verify paths
def verify_paths():
    """
    Verify that all expected paths exist and print diagnostic information.
    Useful for debugging path issues.
    """
    print("=== Path Verification ===")
    print(f"PIPELINE_DIR: {PIPELINE_DIR} (exists: {PIPELINE_DIR.exists()})")
    print(f"DATA_DIR: {DATA_DIR} (exists: {DATA_DIR.exists()})")
    print(f"RULES_DIR: {RULES_DIR} (exists: {RULES_DIR.exists()})")
    print(f"COMMANDS_JSON: {COMMANDS_JSON} (exists: {COMMANDS_JSON.exists()})")

    if PRO_PLAYER_CONFIGS_DIR.exists():
        cfg_count = len(list(PRO_PLAYER_CONFIGS_DIR.glob("*.cfg")))
        print(f"PRO_PLAYER_CONFIGS_DIR: {PRO_PLAYER_CONFIGS_DIR} (exists: True, .cfg files: {cfg_count})")
    else:
        print(f"PRO_PLAYER_CONFIGS_DIR: {PRO_PLAYER_CONFIGS_DIR} (exists: False)")

    if SERVER_CONFIGS_DIR.exists():
        cfg_count = len(list(SERVER_CONFIGS_DIR.glob("*.cfg")))
        print(f"SERVER_CONFIGS_DIR: {SERVER_CONFIGS_DIR} (exists: True, .cfg files: {cfg_count})")
    else:
        print(f"SERVER_CONFIGS_DIR: {SERVER_CONFIGS_DIR} (exists: False)")

    snapshot_files = find_snapshot_files()
    print(f"Snapshot files found: {len(snapshot_files)}")
    for i, snapshot in enumerate(snapshot_files[:3]):  # Show first 3
        print(f"  {i+1}. {snapshot.name}")

    print("========================")

if __name__ == "__main__":
    # When run directly, verify all paths
    verify_paths()
