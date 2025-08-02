import unittest
import os
import sys

# Add the script's directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from command_classification import classify_type_by_rules, add_type_classification

class TestCommandClassification(unittest.TestCase):

    def setUp(self):
        self.rules = [
            {"type": "action", "conditions": [{"field": "consoleData.defaultValue", "operator": "is_null"}]},
            {"type": "bool", "conditions": [{"field": "consoleData.defaultValue", "operator": "is_in_lower", "value": ["true", "false"]}]},
            {"type": "bitmask", "conditions": [{"field": "consoleData.description", "operator": "contains_lower", "value": "bitmask"}]},
            {"type": "float", "conditions": [{"field": "consoleData.defaultValue", "operator": "is_numeric"}, {"field": "consoleData.defaultValue", "operator": "contains", "value": "."}]},
            {"type": "unknown_numeric", "conditions": [{"field": "consoleData.defaultValue", "operator": "is_numeric"}]},
            {"type": "string", "default": True}
        ]

    def test_classify_action(self):
        cmd = {"consoleData": {"defaultValue": None, "description": ""}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "action")

    def test_classify_bool(self):
        cmd = {"consoleData": {"defaultValue": "true", "description": ""}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "bool")

    def test_classify_bitmask(self):
        cmd = {"consoleData": {"defaultValue": "0", "description": "this is a bitmask"}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "bitmask")

    def test_classify_float(self):
        cmd = {"consoleData": {"defaultValue": "1.5", "description": ""}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "float")

    def test_classify_numeric(self):
        cmd = {"consoleData": {"defaultValue": "10", "description": ""}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "unknown_numeric")

    def test_classify_string(self):
        cmd = {"consoleData": {"defaultValue": "hello", "description": ""}}
        self.assertEqual(classify_type_by_rules(cmd, self.rules), "string")

    def test_add_type_classification(self):
        commands = [
            {"command": "cmd_action", "consoleData": {"defaultValue": None, "description": "", "flags": []}},
            {"command": "cmd_bool", "consoleData": {"defaultValue": "false", "description": "", "flags": []}},
            {"command": "cmd_string", "consoleData": {"defaultValue": "text", "description": "", "flags": []}}
        ]

        processed, _, _, _ = add_type_classification(commands, self.rules)

        self.assertEqual(processed[0]["uiData"]["type"], "action")
        self.assertEqual(processed[0]["uiData"]["defaultValue"], None)

        self.assertEqual(processed[1]["uiData"]["type"], "bool")
        self.assertEqual(processed[1]["uiData"]["defaultValue"], False)

        self.assertEqual(processed[2]["uiData"]["type"], "string")
        self.assertEqual(processed[2]["uiData"]["defaultValue"], "text")


if __name__ == '__main__':
    unittest.main()
