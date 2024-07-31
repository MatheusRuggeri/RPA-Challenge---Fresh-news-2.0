# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:25:46 2024

@author: JoaoMurdiga
"""

import logging
from scraper import scrape_news
from robocorp.tasks import task

def setup_logging():
    log_path = './output/rpa_news_scraper.log'
    
    logging.basicConfig(
        filename = log_path,
        level = logging.INFO,
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@task
def main():
    setup_logging()
    logging.info("RPA News Scraper started")
    
    try:
        logging.debug("Starting scrape_news()")
        scrape_news()
    except Exception as e:
        logging.error(f"An error occurred during the scraping process: {e}")
    
    logging.info("RPA News Scraper finished")
    
if __name__ == "__main__":
    main()
