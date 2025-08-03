"""
Server subcategorization rules for command classification.
"""

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def get_server_subcategory(command: dict) -> str:
    """
    Determines the subcategory of a server command based on rules.

    Args:
        command: A dictionary representing a command.

    Returns:
        A string indicating the subcategory.
    """
    # Check for manual category first
    manual_category = command.get('uiData', {}).get('manual_category')
    if manual_category:
        _, subcategory = manual_category.split('/')
        return subcategory

    prefix = get_prefix(command['command'])
    command_name = command['command']

    # Apply prefix-based rules
    if prefix in ["hostname_", "log_", "rcon_"]:
        return "setup"
    elif prefix == "mp_":
        if "team" in command_name:
            return "teams"
        elif "round" in command_name:
            return "rounds"
        elif "bomb" in command_name or "hostage" in command_name:
            return "objectives"
        elif "spawn" in command_name:
            return "spawning"
        elif "friendlyfire" in command_name or "damage" in command_name:
            return "rules"
        elif "money" in command_name or "cash" in command_name or "econ" in command_name:
            return "economy"
        else:
            return "rules"
    elif prefix == "bot_":
        return "bots"
    elif prefix == "tv_":
        return "gotv"
    else:
        return "setup"
