"""
Rules for determining command popularity based on configuration file usage.
"""

# Configuration constants
POPULARITY_THRESHOLD = 0.10  # 10%

def extract_commands_from_cfg(filepath: str) -> set:
    """
    Extract command names from a single configuration file.

    Args:
        filepath: Path to the .cfg file

    Returns:
        Set of command names found in the file
    """
    commands = set()
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            # Extract the first word (the command)
            cmd = line.split()[0]
            commands.add(cmd)
    return commands

def should_mark_as_popular(command_count: int, total_configs: int) -> bool:
    """
    Determine if a command should be marked as popular based on usage frequency.

    Args:
        command_count: Number of configs containing this command
        total_configs: Total number of config files processed

    Returns:
        True if command should be marked as popular (visible), False otherwise
    """
    if total_configs == 0:
        return False

    usage_ratio = command_count / total_configs
    return usage_ratio > POPULARITY_THRESHOLD

def should_update_visibility(entry: dict, is_popular: bool) -> bool:
    """
    Determine if a command entry should have its visibility updated.

    Args:
        entry: Command entry dictionary
        is_popular: Whether the command is considered popular

    Returns:
        True if the entry should be updated, False otherwise
    """
    ui_data = entry.get("uiData", {})
    current_hidden = ui_data.get("hideFromDefaultView", True)

    # Only update if the command is popular and currently hidden
    return is_popular and current_hidden
