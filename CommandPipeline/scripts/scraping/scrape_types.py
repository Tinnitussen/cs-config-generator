
import json
from bs4 import BeautifulSoup
import os

def scrape_types(html_file_path, output_json_path):
    """
    Parses an HTML file to extract command names and their types, then saves them to a JSON file.

    Args:
        html_file_path (str): The path to the input HTML file.
        output_json_path (str): The path to the output JSON file.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{html_file_path}' was not found.")
        return

    soup = BeautifulSoup(html_content, 'lxml')
    table = soup.find('table')

    if not table:
        print("Error: No table found in the HTML file.")
        return

    headers = [th.text.strip() for th in table.find_all('th')]

    name_index = headers.index('Name') if 'Name' in headers else -1
    type_index = headers.index('Type') if 'Type' in headers else -1
    description_index = headers.index('Description') if 'Description' in headers else -1
    flags_index = headers.index('Flags') if 'Flags' in headers else -1

    if name_index == -1:
        print("Error: 'Name' column not found in the table.")
        return

    data = {}
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if not cols:
            continue

        # Extract command name, stripping any default value
        name_raw = cols[name_index].text.strip()
        name = name_raw.split(' ')[0]

        # Initialize data structure for the command
        command_info = {}

        # Extract type, description, and flags if they exist
        if type_index != -1 and len(cols) > type_index:
            type_tag = cols[type_index]
            type_value = type_tag.find('span', {'data-tip': True})
            if type_value:
                type_text = type_value['data-tip']
            else:
                type_text = type_tag.text.strip()
            if ':' in type_text:
                type_text = type_text.split(':', 1)[0].strip()
            command_info['type'] = type_text

        if description_index != -1 and len(cols) > description_index:
            command_info['description'] = cols[description_index].text.strip()

        if flags_index != -1 and len(cols) > flags_index:
            command_info['flags'] = cols[flags_index].text.strip().split()

        data[name] = command_info

    with open(output_json_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Scraped data saved to {output_json_path}")

def main():
    """
    Main function to run the scraping process with default file paths.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_html_path = os.path.join(script_dir, '../../data/ConVars _ CS2 Docs.html')
    default_json_path = os.path.join(script_dir, '../../data/scraped_types.json')
    scrape_types(default_html_path, default_json_path)

if __name__ == '__main__':
    main()
