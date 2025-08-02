"""
This file defines the ordered rules for classifying command types.
Each rule is a function that takes a command dictionary and returns a
tuple of (type, default_value) if the command matches the rule,
otherwise it returns None.
"""

def is_numeric_string(value: any) -> bool:
    """Helper function to check if a string can be cast to a float."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False

# --- Classification Rules ---

def rule_action(cmd):
    """Rule 1: A command is an 'action' if its defaultValue is null."""
    if cmd['consoleData']['defaultValue'] is None:
        return 'action', None
    return None

def rule_bool(cmd):
    """Rule 2: A command is a 'bool' if its defaultValue is 'true' or 'false'."""
    console_default = cmd['consoleData']['defaultValue']
    if str(console_default).lower() in ['true', 'false']:
        default_str = str(console_default).lower()
        ui_default = default_str == 'true' or default_str == '1'
        return 'bool', ui_default
    return None

def rule_bitmask(cmd):
    """Rule 3: A command is a 'bitmask' if its description contains 'bitmask'."""
    description = cmd['consoleData']['description'].lower()
    if 'bitmask' in description:
        console_default = cmd['consoleData']['defaultValue']
        ui_default = int(console_default) if is_numeric_string(console_default) else 0
        return 'bitmask', ui_default
    return None

def rule_numeric(cmd):
    """Rule 4: A command is numeric if its defaultValue is a numeric string."""
    console_default = cmd['consoleData']['defaultValue']
    if is_numeric_string(console_default):
        if '.' in str(console_default):
            return 'float', float(console_default)
        else:
            return 'unknown_numeric', int(float(console_default))
    return None

def rule_string(cmd):
    """Rule 5: A command is a 'string' if no other rule matches."""
    # This rule is a catch-all for any non-null, non-bool, non-numeric value.
    console_default = cmd['consoleData']['defaultValue']
    if console_default is not None:
        return 'string', console_default
    return None

# The ordered list of rules to be applied.
# The first rule to match will determine the type.
CLASSIFICATION_RULES = [
    rule_action,
    rule_bool,
    rule_bitmask,
    rule_numeric,
    rule_string,
]
