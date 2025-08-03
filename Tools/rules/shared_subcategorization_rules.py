"""
Shared subcategorization rules for command classification.
"""

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
