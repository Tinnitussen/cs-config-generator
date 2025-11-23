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
                'uiData': {'type': 'unknown', 'defaultValue': 0}
            }
        ]
        manual_overrides = {'example_cmd_text': 'string'}
        scraped_types = {'example_cmd_text': 'string'}  # should be ignored for unknown due to exclusion
        updated, stats = apply_type_improvements(commands, manual_overrides, scraped_types, dry_run=False)
        self.assertEqual(updated[0]['uiData']['type'], 'string')
        # defaultValue should be coerced to string '0' because type is string
        self.assertEqual(updated[0]['uiData']['defaultValue'], '0')
        self.assertEqual(stats['manual_overrides_applied'], 1)
        self.assertEqual(stats['scraped_types_applied'], 0)

if __name__ == '__main__':
    unittest.main()
