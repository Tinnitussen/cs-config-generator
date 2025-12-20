import unittest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
scripts_dir = project_root / 'scripts'
sys.path.append(str(project_root))
sys.path.append(str(scripts_dir))

from apply_type_improvements import apply_type_improvements


class TestApplyTypeImprovements(unittest.TestCase):
    def test_manual_override_string_applied(self):
        """Test that manual overrides are applied correctly."""
        commands = [
            {
                'command': 'example_cmd_text',
                'consoleData': {'defaultValue': 'hello_world', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown'}
            }
        ]
        manual_overrides = {'example_cmd_text': 'string'}
        updated, stats = apply_type_improvements(commands, manual_overrides, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'string')
        self.assertEqual(stats['manual_overrides_applied'], 1)

    def test_unknown_remains_without_override(self):
        """Test that unknown types remain unknown without a manual override."""
        commands = [
            {
                'command': 'unclassified_cmd',
                'consoleData': {'defaultValue': '42', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown'}
            }
        ]
        manual_overrides = {}
        updated, stats = apply_type_improvements(commands, manual_overrides, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'unknown')
        self.assertEqual(stats['manual_overrides_applied'], 0)
        self.assertEqual(stats['unknown_remaining'], 1)

    def test_vector3_heuristic_detection(self):
        """Test that vector3 is detected from space-separated triple."""
        commands = [
            {
                'command': 'some_vector_cmd',
                'consoleData': {'defaultValue': '1.0 2.0 3.0', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown'}
            }
        ]
        manual_overrides = {}
        updated, stats = apply_type_improvements(commands, manual_overrides, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'vector3')
        self.assertEqual(stats['heuristic_vectors_applied'], 1)

    def test_vector2_heuristic_detection(self):
        """Test that vector2 is detected from space-separated pair."""
        commands = [
            {
                'command': 'some_vector2_cmd',
                'consoleData': {'defaultValue': '0.5 1.5', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown'}
            }
        ]
        manual_overrides = {}
        updated, stats = apply_type_improvements(commands, manual_overrides, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'vector2')
        self.assertEqual(stats['heuristic_vectors_applied'], 1)


    def test_manual_override_to_int_not_overridden_by_vector(self):
        """Test that manual override to int is not overridden by vector heuristic."""
        commands = [
            {
                'command': 'special_cmd',
                'consoleData': {'defaultValue': '1.0 2.0 3.0', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown'}
            }
        ]
        # Force it to be an int - vector heuristic only applies to string/unknown
        manual_overrides = {'special_cmd': 'int'}
        updated, stats = apply_type_improvements(commands, manual_overrides, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'int')
        self.assertEqual(stats['manual_overrides_applied'], 1)
        self.assertEqual(stats['heuristic_vectors_applied'], 0)


if __name__ == '__main__':
    unittest.main()
