"""
Player subcategorization rules for command classification.
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
