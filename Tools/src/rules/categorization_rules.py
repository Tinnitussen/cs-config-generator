# --- Rule-based classification logic for splitting commands ---

PLAYER_PREFIXES = ["cl_", "ui_", "joy_", "cam_", "c_", "+", "snd_", "r_", "mat_", "demo_"]
SERVER_PREFIXES = ["sv_", "mp_", "bot_", "nav_", "ent_", "script_", "logaddress_", "rr_", "cast_", "navspace_", "markup_", "spawn_", "vis_", "telemetry_", "test_", "soundscape_", "scene_", "particle_", "shatterglass_", "create_", "debugoverlay_", "prop_", "g_", "ff_", "cash_", "contributionscore_"]
SHARED_PREFIXES = ["ai_", "weapon_", "ragdoll_", "ik_", "skeleton_"]

def get_prefix(command_name: str):
    """Extracts the prefix from a command name."""
    if command_name.startswith('+'):
        return '+'
    parts = command_name.split('_')
    if len(parts) > 1:
        return f"{parts[0]}_"
    return None

def get_command_category(command: dict) -> str:
    """
    Determines the category of a command based on a set of rules.

    Args:
        command: A dictionary representing a command.

    Returns:
        A string indicating the category: "server", "player", "shared", or "uncategorized".
    """
    manual_category = command.get('uiData', {}).get('manual_category')
    if manual_category:
        category, _ = manual_category.split('/')
        return category

    flags = command.get('consoleData', {}).get('flags', [])
    is_server = 'sv' in flags
    is_client = 'cl' in flags
    is_replicated = 'rep' in flags
    is_archived = 'a' in flags
    is_user = 'user' in flags
    command_name = command['command']
    prefix = get_prefix(command_name)

    if is_replicated or (is_server and is_client):
        return "shared"
    elif is_server:
        return "server"
    elif is_client:
        return "player"
    elif prefix in PLAYER_PREFIXES:
        return "player"
    elif prefix in SERVER_PREFIXES:
        return "server"
    elif prefix in SHARED_PREFIXES:
        return "shared"
    elif is_archived or is_user:
        return "player"
    else:
        return "uncategorized"
