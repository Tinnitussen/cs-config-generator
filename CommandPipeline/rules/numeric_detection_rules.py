from typing import Any

# --- Rule-based classification logic for numeric detection ---

# Configuration for numeric type classification
FLOAT_RATIO = 0.5
MIN_INT_OCCURRENCES = 15
PROTECTED_TYPES = ("float", "bool", "bitmask", "action")
UNKNOWN_TYPES = ("unknown",)

def classify_command_by_usage(stats: Any) -> str:
    """
    Determine the appropriate type for a command based on its usage stats.

    Args:
        stats: A CommandStats object with statistics about the command's usage.

    Returns:
        The classified type name as a string.
    """
    # Don't reclassify protected types that have been manually set
    if stats.current_type in PROTECTED_TYPES:
        return stats.current_type

    # Classify as float if a significant ratio of its values are floats
    if stats.float_ratio > FLOAT_RATIO:
        return "float"

    # Classify as unknown if all values are integers and it appears often
    if (stats.total >= MIN_INT_OCCURRENCES and
        stats.is_all_int and
        stats.current_type not in ("int", "unknown")):
        return "unknown"

    # If no specific rule matches, keep the existing type
    return stats.current_type
