import unittest
import os
import json
import shutil
import sys

# Add the script's directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from parse_commands import load_parsing_rules, parse_input_file

class TestParseCommands(unittest.TestCase):

    def setUp(self):
        self.test_dir = "temp_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)

        self.rules_file = os.path.join(self.test_dir, "parsing_rules.json")
        self.input_file = os.path.join(self.test_dir, "test_input.txt")

        # Create dummy rules file
        self.rules = {
            "parse_pattern": "^\\[Test\\]\\s+([^\\s]+)\\s+(.*)$",
            "valid_command_pattern": "^[a-z_]+$",
            "valid_default_value_pattern": ".*",
            "valid_flags": ["test_flag"]
        }
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f)

        # Create dummy input file
        with open(self.input_file, 'w') as f:
            f.write("[Test] test_command value\n")
            f.write("[Test] another_command another_value\n")
            f.write("Invalid line\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_parsing_rules(self):
        loaded_rules = load_parsing_rules(self.rules_file)
        self.assertEqual(self.rules, loaded_rules)

    def test_parse_input_file(self):
        rules = load_parsing_rules(self.rules_file)
        # Modify parse_input_file to not require all the fields, just for this test
        # This is a bit of a hack, but it's easier than creating a full-blown command structure

        # Let's adapt the test to the actual structure of parse_input_file
        # We need to provide a file that matches the real parsing logic

        # Re-create dummy files for a more realistic test
        with open(self.rules_file, 'w') as f:
            json.dump({
                "parse_pattern": "^\\[Console\\]\\s+([^\\s]+)\\s+:\\s+(.+?)\\s+:\\s+([^:]+?)\\s*(?::\\s*(.*))?$",
                "valid_command_pattern": "^[a-z_]+$",
                "valid_default_value_pattern": ".+",
                "valid_flags": ["test_flag"]
            }, f)

        with open(self.input_file, 'w') as f:
            f.write("[Console] test_cmd : default_val : test_flag : description\n")
            f.write("[Console] another_cmd : another_val : test_flag : \n")

        current_commands, parsed_commands = parse_input_file(self.input_file, load_parsing_rules(self.rules_file))

        self.assertEqual(len(current_commands), 2)
        self.assertIn("test_cmd", current_commands)
        self.assertIn("another_cmd", current_commands)

        self.assertEqual(parsed_commands["test_cmd"]["defaultValue"], "default_val")
        self.assertEqual(parsed_commands["test_cmd"]["flags"], ["test_flag"])
        self.assertEqual(parsed_commands["test_cmd"]["description"], "description")

if __name__ == '__main__':
    unittest.main()
