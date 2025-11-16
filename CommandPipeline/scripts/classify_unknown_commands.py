import json
import requests
from bs4 import BeautifulSoup
import re

def scrape_valve_developer_community():
    """
    Scrapes the Valve Developer Community wiki for command information.
    """
    # TODO: Implement scraping logic
    pass

def scrape_cs2_poggu():
    """
    Scrapes cs2.poggu.me for command information.
    """
    # TODO: Implement scraping logic
    pass

def classify_unknown_commands():
    """
    Classifies commands of type 'unknown' based on scraped data.
    """
    with open('CommandPipeline/data/commands.json', 'r') as f:
        commands = json.load(f)

import re

def is_integer(scraped_info):
    """
    Determines if a command is an integer type.
    """
    default_value = scraped_info.get("defaultValue", "")
    description = scraped_info.get("description", "")

    # Check if default value is an integer
    if default_value.isdigit():
        return True

    # Check for integer ranges in the description (e.g., "(0-5)", "0-1")
    if re.search(r'\(\d+-\d+\)', description) or re.search(r'\d+-\d+', description):
        return True

    return False

def is_float(scraped_info):
    """
    Determines if a command is a float type.
    """
    default_value = scraped_info.get("defaultValue", "")

    # Check if default value is a float
    try:
        float(default_value)
        return "." in default_value
    except (ValueError, TypeError):
        return False


def is_enum(scraped_info):
    """
    Determines if a command is an enum type.
    """
    description = scraped_info.get("description", "")

    # Check for key=value pairs in the description (e.g., "0=off, 1=on")
    if re.search(r'\d+=\w+', description):
        return True

    # Check for quoted values in the description (e.g., "'all', 'local', 'none'")
    if re.search(r"\'[^']+\'", description):
        return True

    return False

def is_bitmask(scraped_info):
    """
    Determines if a command is a bitmask type.
    """
    description = scraped_info.get("description", "")

    # Check for keywords like "bitmask", "flags", "bitwise"
    if "bitmask" in description.lower() or "flags" in description.lower() or "bitwise" in description.lower():
        return True

    return False

def classify_unknown_commands():
    """
    Classifies commands of type 'unknown' based on scraped data.
    """
    # TODO: Replace with actual scraped data
    scraped_data = {
        "sv_cheats": {"description": "Allow cheats on server", "defaultValue": "0"},
        "cl_interp": {"description": "Sets the interpolation amount (bounded on server).", "defaultValue": "0.02"},
        "cl_showfps": {"description": "Draw fps meter at top of screen (0-5)", "defaultValue": "0"},
        "r_drawdecals": {"description": "Render decals (0-1)", "defaultValue": "1"},
        "host_timescale": {"description": "Prescale the clock by this amount.", "defaultValue": "1.0"},
        "mp_solid_teammates": {"description": "Determines whether teammates are solid or not. 1=solid, 2=not solid", "defaultValue": "1"},
        "some_bitmask_command": {"description": "A bitmask of flags to control something.", "defaultValue": "0"}
    }

    with open('CommandPipeline/data/commands.json', 'r') as f:
        commands = json.load(f)

    for command in commands:
        if command.get('uiData', {}).get('type') == 'unknown':
            command_name = command.get('name')
            if command_name in scraped_data:
                scraped_info = scraped_data[command_name]
                if is_integer(scraped_info):
                    command['uiData']['type'] = 'integer'
                elif is_float(scraped_info):
                    command['uiData']['type'] = 'float'
                elif is_enum(scraped_info):
                    command['uiData']['type'] = 'enum'
                elif is_bitmask(scraped_info):
                    command['uiData']['type'] = 'bitmask'

    with open('CommandPipeline/data/commands.json', 'w') as f:
        json.dump(commands, f, indent=4)

if __name__ == "__main__":
    classify_unknown_commands()
