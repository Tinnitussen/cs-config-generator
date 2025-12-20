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
        commands = [
            {
                'command': 'example_cmd_text',
                'consoleData': {'defaultValue': 'hello_world', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown', 'defaultValue': 0}
            }
        ]
        manual_overrides = {'example_cmd_text': 'string'}
        scraped_types = {'example_cmd_text': 'string'}  # should be ignored for unknown due to exclusion
        updated, stats, manifest = apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'string')
        # defaultValue is coerced to string in new logic
        self.assertEqual(updated[0]['typeInfo']['defaultValue'], "0")
        self.assertEqual(stats['manual_overrides_applied'], 1)
        self.assertEqual(stats['scraped_types_applied'], 0)

    def test_scraped_string_excluded(self):
        commands = [
            {
                'command': 'scraped_string_cmd',
                'consoleData': {'defaultValue': 'text', 'flags': [], 'description': ''},
                'typeInfo': {'type': 'unknown', 'defaultValue': 0}
            }
        ]
        manual_overrides = {}
        scraped_types = {'scraped_string_cmd': 'string'}  # ignored
        updated, stats, manifest = apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=False)
        self.assertEqual(updated[0]['typeInfo']['type'], 'unknown')
        self.assertEqual(stats['manual_overrides_applied'], 0)
        self.assertEqual(stats['scraped_types_applied'], 0)

if __name__ == '__main__':
    unittest.main()
