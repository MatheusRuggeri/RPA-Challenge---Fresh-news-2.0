# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:25:46 2024

@author: JoaoMurdiga
"""

import unittest
from scraper import NewsScraper
from utils import load_config

class TestNewsScraper(unittest.TestCase):
    def setUp(self):
        self.config = load_config('../config/formats.json')
        self.scraper = NewsScraper(self.config)

    def test_scrape_news(self):
        results = self.scraper.scrape_news("Schott")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn("title", result)
            self.assertIn("description", result)
            self.assertIn("date", result)
            self.assertIn("image_url", result)

if __name__ == "__main__":
    unittest.main()
