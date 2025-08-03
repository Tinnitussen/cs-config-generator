"""
Server subcategorization rules for command classification.
"""

# Order matters: more specific categories should come first.
SUBCATEGORY_RULES = {
    "economy": ["econ", "economy", "money", "cash", "price", "cost", "buy", "contributionscore"],
    "teams": ["_team", "scramble", "swap"],
    "rounds": ["_round", "warmup", "endmatch", "halftime", "overtime", "endround"],
    "objectives": ["_bomb", "hostage", "plant", "defuse"],
    "spawning": ["_spawn", "respawn"],
    "rules": ["friendlyfire", "_damage", "_c4", "_tk", "_kick", "_vote", "cheat", "_pause", "unpause", "limitteams", "autokick", "alltalk", "allchat", "pausable"],
}

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
        try:
            _, subcategory = manual_category.split('/')
            return subcategory
        except ValueError:
            # Handle cases where manual_category might not be in the expected format
            pass

    command_name = command['command'].lower()

    if command_name == 'rr_forceconcept':
        return 'setup'

    # --- Prefix-based rules (highest priority) ---
    if command_name.startswith(("bot_", "sv_bot_")):
        return "bots"
    if command_name.startswith(("tv_", "spec_")):
        return "gotv"
    if command_name.startswith("nav_"):
        return "setup"

    # --- Keyword-based rules ---
    for category, keywords in SUBCATEGORY_RULES.items():
        if any(keyword in command_name for keyword in keywords):
            return category

    # --- Fallback for mp_ commands ---
    if command_name.startswith("mp_"):
        return "rules"

    # --- Default category ---
    return "setup"
