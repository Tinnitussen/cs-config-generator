
import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'scripts' / 'scraping'))

from scrape_types import scrape_types

class TestScraping(unittest.TestCase):

    def setUp(self):
        # Create a temporary HTML file for test input
        self.temp_html_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.html')
        self.temp_html_file.write("""
        <html>
            <body>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>sv_cheats</td>
                            <td><span>Bool</span></td>
                            <td>Enables cheats on the server.</td>
                        </tr>
                        <tr>
                            <td>version</td>
                            <td><span data-tip="Action: No value, just does something">Action</span></td>
                            <td>Print version info string.</td>
                        </tr>
                        <tr>
                            <td>cl_showfps</td>
                            <td><span data-tip="Enum: 0 = off, 1 = fps, 2 = smooth, 3 = server, 4 = all">Enum</span></td>
                            <td>Draws framerate in corner of screen.</td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """)
        self.temp_html_file.close()

        # Create a temporary file for the JSON output
        self.temp_json_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.json')
        self.temp_json_file.close()

    def tearDown(self):
        # Clean up the temporary files
        os.remove(self.temp_html_file.name)
        os.remove(self.temp_json_file.name)

    def test_scrape_types(self):
        scrape_types(self.temp_html_file.name, self.temp_json_file.name)

        with open(self.temp_json_file.name, 'r') as f:
            data = json.load(f)

        self.assertEqual(data, {
            "sv_cheats": "Bool",
            "version": "Action",
            "cl_showfps": "Enum"
        })

if __name__ == '__main__':
    unittest.main()
