import unittest
import os
import sys

# Add the script's directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/splitting')))

from split import classify_command, classify_commands

class TestSplit(unittest.TestCase):

    def setUp(self):
        self.rules = {
            "by_flag": {
                "shared": [{"requires": ["rep"]}],
                "server": [{"requires": ["sv"]}],
                "player": [{"requires": ["cl"]}]
            },
            "by_prefix": {
                "player": ["cl_"],
                "server": ["sv_"],
                "shared": ["ai_"]
            }
        }

        self.commands = [
            {"command": "sv_gravity", "consoleData": {"flags": ["sv"]}},
            {"command": "cl_showfps", "consoleData": {"flags": ["cl"]}},
            {"command": "rep_test", "consoleData": {"flags": ["rep"]}},
            {"command": "ai_test", "consoleData": {"flags": []}},
            {"command": "uncategorized_cmd", "consoleData": {"flags": []}}
        ]

    def test_classify_command_by_flag(self):
        self.assertEqual(classify_command(self.commands[0], self.rules), "server")
        self.assertEqual(classify_command(self.commands[1], self.rules), "player")
        self.assertEqual(classify_command(self.commands[2], self.rules), "shared")

    def test_classify_command_by_prefix(self):
        self.assertEqual(classify_command({"command": "cl_dummy", "consoleData": {"flags": []}}, self.rules), "player")
        self.assertEqual(classify_command({"command": "sv_dummy", "consoleData": {"flags": []}}, self.rules), "server")
        self.assertEqual(classify_command({"command": "ai_dummy", "consoleData": {"flags": []}}, self.rules), "shared")

    def test_classify_command_uncategorized(self):
        self.assertEqual(classify_command(self.commands[4], self.rules), "uncategorized")

    def test_classify_commands(self):
        classified = classify_commands(self.commands, self.rules)

        self.assertEqual(len(classified["server"]), 1)
        self.assertEqual(classified["server"][0]["command"], "sv_gravity")

        self.assertEqual(len(classified["player"]), 1)
        self.assertEqual(classified["player"][0]["command"], "cl_showfps")

        self.assertEqual(len(classified["shared"]), 2)
        self.assertIn("rep_test", [c["command"] for c in classified["shared"]])
        self.assertIn("ai_test", [c["command"] for c in classified["shared"]])

        self.assertEqual(len(classified["uncategorized"]), 1)
        self.assertEqual(classified["uncategorized"][0]["command"], "uncategorized_cmd")

if __name__ == '__main__':
    unittest.main()
