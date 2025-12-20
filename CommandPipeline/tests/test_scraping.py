"""
Tests for the scraping functionality.

Note: Scraping has been deprecated and archived. These tests are skipped
but kept for reference in case scraping is re-enabled in the future.
"""

import unittest


class TestScraping(unittest.TestCase):

    @unittest.skip("Scraping functionality has been archived - see CommandPipeline/data/archive/")
    def test_scrape_types(self):
        """Test that scraping extracts types from HTML."""
        pass


if __name__ == '__main__':
    unittest.main()
