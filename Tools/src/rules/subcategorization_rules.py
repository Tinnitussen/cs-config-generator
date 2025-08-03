"""
Subcategorization rules for command classification.
"""

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def get_player_subcategory(command: dict) -> str:
    """
    Determines the subcategory of a player command based on rules.

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
    ui_type = command.get('uiData', {}).get('type')
    flags = command.get('consoleData', {}).get('flags', [])

    # Apply prefix-based rules
    if prefix == "crosshair_":
        return "crosshair"
    elif prefix == "viewmodel_":
        return "viewmodel"
    elif prefix == "hud_":
        return "hud"
    elif prefix == "radar_":
        return "radar"
    elif prefix in ["input_", "m_", "joy_"]:
        return "input"
    elif prefix in ["gameplay_", "option_"]:
        return "gameplay"
    elif prefix in ["snd_", "sound_", "voice_"]:
        return "audio"
    elif prefix in ["comm_", "chat_"]:
        return "communication"
    elif prefix == "net_":
        return "network"
    elif "cheat" in flags:
        return "cheats"
    elif ui_type == "action":
        return "actions"
    elif prefix == "r_":
        return "developer/rendering"
    elif prefix in ["debug_", "dev_"]:
        return "developer/debugging"
    elif prefix == "spec_":
        return "developer/spectator"
    else:
        return "misc"

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

def get_shared_subcategory(command: dict) -> str:
    """
    Determines the subcategory of a shared command based on rules.

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

    # For now, all shared commands go to "tbd" (to be determined)
    # This maintains the current behavior exactly
    return "tbd"
