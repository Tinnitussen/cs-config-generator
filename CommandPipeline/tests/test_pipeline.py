
import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add the scripts and rules directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'scripts'))
sys.path.append(str(Path(__file__).resolve().parent.parent / 'rules'))

from parse_commands import parse_input_file
from command_classification import add_type_classification

class TestCommandPipeline(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for test input
        self.temp_input_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_input_file.write(
            """[Console] sv_cheats : 0 : a, sv, rep, nolog : Enables cheats on the server.
[Console] version : cmd : release, clientcmd_can_execute : Print version info string.
[Console] cl_showfps : 1 : a, cl : Draws framerate in corner of screen.
[Console] host_timescale : 1.0 : sv, cheat : Prescale the clock by this amount.
[Console] sv_gravity : 800.0 : sv, rep, nolog : World gravity.
[Console] an_invalid_command! : 1 : a : Invalid command.
[Console] another_valid_command : test : invalid_flag : Invalid flag.
"""
        )
        self.temp_input_file.close()

        # Path to the actual rules file
        self.rules_file = str(Path(__file__).resolve().parent.parent / 'rules' / 'parsing_validation_rules.json')

    def tearDown(self):
        # Clean up the temporary files
        os.remove(self.temp_input_file.name)

    def test_parse_input_file_with_actual_rules(self):
        current_commands, parsed_commands = parse_input_file(
            self.temp_input_file.name, self.rules_file
        )

        # Check that the valid commands were parsed correctly
        self.assertIn("sv_cheats", parsed_commands)
        self.assertEqual(parsed_commands["sv_cheats"]["defaultValue"], "0")
        self.assertEqual(parsed_commands["sv_cheats"]["flags"], ["a", "nolog", "rep", "sv"])
        self.assertEqual(parsed_commands["sv_cheats"]["description"], "Enables cheats on the server.")

        self.assertIn("version", parsed_commands)
        self.assertIsNone(parsed_commands["version"]["defaultValue"])
        self.assertEqual(parsed_commands["version"]["flags"], ["clientcmd_can_execute", "release"])
        self.assertEqual(parsed_commands["version"]["description"], "Print version info string.")

        # Check that invalid commands are skipped
        self.assertNotIn("an_invalid_command!", parsed_commands)
        self.assertNotIn("another_valid_command", parsed_commands)

        # Check the set of current commands
        self.assertEqual(current_commands, {"sv_cheats", "version", "cl_showfps", "host_timescale", "sv_gravity"})

    def test_add_type_classification(self):
        commands = [
            {"command": "sv_cheats", "consoleData": {"defaultValue": "0", "flags": ["sv"], "description": ""}},
            {"command": "version", "consoleData": {"defaultValue": None, "flags": ["release"], "description": ""}},
            {"command": "cl_showfps", "consoleData": {"defaultValue": "1", "flags": ["cl"], "description": ""}},
            {"command": "host_timescale", "consoleData": {"defaultValue": "1.0", "flags": ["sv", "cheat"], "description": ""}},
            {"command": "sv_gravity", "consoleData": {"defaultValue": "800.0", "flags": ["sv"], "description": ""}},
            {"command": "test_string", "consoleData": {"defaultValue": "hello", "flags": [], "description": ""}},
            {"command": "test_bool_true", "consoleData": {"defaultValue": "true", "flags": [], "description": ""}},
            {"command": "test_bool_false", "consoleData": {"defaultValue": "false", "flags": [], "description": ""}},
        ]

        processed_commands, _, _, _ = add_type_classification(commands, reclassify_all=True)

        self.assertEqual(processed_commands[0]['uiData']['type'], 'unknown') # 0 is numeric, but without context it's unknown
        self.assertEqual(processed_commands[1]['uiData']['type'], 'action')
        self.assertEqual(processed_commands[2]['uiData']['type'], 'unknown') # 1 is numeric, but without context it's unknown
        self.assertEqual(processed_commands[3]['uiData']['type'], 'float')
        self.assertEqual(processed_commands[4]['uiData']['type'], 'float')
        self.assertEqual(processed_commands[5]['uiData']['type'], 'string')
        self.assertEqual(processed_commands[6]['uiData']['type'], 'bool')
        self.assertEqual(processed_commands[6]['uiData']['defaultValue'], True)
        self.assertEqual(processed_commands[7]['uiData']['type'], 'bool')
        self.assertEqual(processed_commands[7]['uiData']['defaultValue'], False)

if __name__ == '__main__':
    unittest.main()
