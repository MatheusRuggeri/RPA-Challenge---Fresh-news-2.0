# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:25:46 2024

@author: JoaoMurdiga
"""


import re
import os
import time
import json
import random
import urllib
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems


class SeleniumError(Exception):
    """
    Custom exception for Selenium-related errors.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
        
class NewsScraper:
    def __init__(self):
        """
        Initialize the NewsScraper class.
        """
        
        # Initialize instances
        self.browser = Selenium()
        self.excel = Files()
        self.work_items = WorkItems()
        
        logging.info("Instances initialized")
        
        # Output folder
        self.output_path = './output/'
        
        # Define accepted image formats and date formats
        self.images_formats = ["*.jpg", "*.jpeg", "*.webp", "*.png", "*.gif", "*.bmp", "*.tiff", "*.tif", "*.svg", "*.heic", "*.heif"]
        self.date_formats = ["%d/%m/%Y", "%d.%m.%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%Y.%m.%d", "%Y %b %d", "%Y %B %d", "%A, %d %B %Y", "%a, %d %b %Y", "%A, %B %d, %Y", "%a, %b %d, %Y", "%d/%m/%y", "%m/%d/%y", "%y-%m-%d", "%d-%m-%y", "%Y.%m.%d %H:%M:%S", "%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M", "%m-%d-%Y %H:%M", "%d %B %Y %H:%M", "%d %b %Y %H:%M", "%Y/%m/%d %H:%M:%S", "%Y %b %d %H:%M", "%d-%m-%Y %H:%M:%S", "%A, %d %B %Y %H:%M", "%a, %d %b %Y %H:%M", "%b. %d, %Y", "%b %d, %Y"]



    def load_config(self, config_file):
        """
        Load and parse the JSON configuration file.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            dict: Parsed configuration.

        Raises:
            FileNotFoundError: If the config file is not found.
            json.JSONDecodeError: If there is an error decoding the JSON.
        """
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
            return config
        except FileNotFoundError:
            logging.error("Config file not found: %s", config_file)
            raise
        except json.JSONDecodeError as e:
            logging.error("Error decoding JSON from file: %s", e)
            raise


    def get_workitem(self):
        """
        Load the input work item containing search parameters.

        Returns:
            tuple: Contains the search phrase, news category, and number of months.
        """
        logging.info("Loading work item")
        input_data = self.work_items.get_input_work_item()
        logging.info("Work Items Loaded Successfully")
        
        try:
            return (input_data.payload["search_phrase"], 
                    input_data.payload["months"], 
                    input_data.payload["news_category"])
        except KeyError:
            logging.error("Error retrieving parameters from Cloud Robocorp. Configure the Payload in Cloud Robocorp.")
            logging.error("Go to Unattendend -> Processes -> [PROCESS NAME] -> Configure -> Advanced Settings -> Start Process with input data -> Payload")

            raise
            

    def open_browser(self, url):
        """
        Open a browser and navigate to the specified URL.
        
        Args:
            url (str): The URL to open.
        
        Raises:
            Exception: If there is an error opening the browser.
        """
        try:
            self.browser.open_available_browser(url)
            logging.info(f"Opened browser with URL: {url}")
        except Exception as e:
            logging.error(f"Failed to open browser with URL {url}: {e}")
            raise


    def open_browser_avoiding_robot_detection(self, url):
        """
        Open a browser and navigate to the specified URL while avoiding robot detection.

        Args:
            url (str): The URL to open.

        Raises:
            Exception: If there is an error opening the browser.
        """
        try:
            options = {
                "arguments": [
                    "--disable-blink-features=AutomationControlled", 
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            }
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            self.browser.open_available_browser(url, options=options)
            
            # Add a random  delay to mimic human behavior
            self.browser.set_browser_implicit_wait(random.uniform(1, 2))
            self.browser.execute_javascript(f"Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}})")
            self.browser.execute_javascript(f"navigator.__defineGetter__('userAgent', () => '{user_agent}')")
            logging.info(f"Opened browser with URL: {url}")
            
        except Exception as e:
            logging.error(f"Failed to open browser with URL {url}: {e}")
            raise

                
    def count_string_in_text(self, text, search_string):
        """
        Count the number of occurrences of a specific string in a given text.

        Args:
            text (str): The text to search within.
            search_string (str): The string to count.

        Returns:
            int: The number of occurrences of the search string in the text.
        """
        # Compile a regular expression pattern with word boundaries and case insensitivity
        pattern = re.compile(r'\b' + re.escape(search_string) + r'\b', re.IGNORECASE)
        
        # Find all matches and return the count
        matches = pattern.findall(text)
        
        return len(matches)


    def make_valid_filename(self, filename):
        """
        Convert a given filename into a valid filename by replacing invalid characters.

        Args:
            filename (str): The original filename.

        Returns:
            str: The valid filename with invalid characters replaced by underscores.
        """
        return re.sub(r'[<>:"/\\|?*]', '_', filename)


    def has_money_in_text(self, text):
        """
        Check if the given text contains any money-related strings.
        
        Args:
            text (str): The text to search within.
        
        Returns:
            bool: True if the text contains money-related strings, otherwise False.
        """
        # Define regular expression patterns for different money formats
        patterns = [
            # $11.1 or $111,111.11 -> '$' + '1-3 digits' + ',' + '1-3 digits' + '.' + '1-2 digits'
            re.compile(r'\$\d{1,3}(,\d{3})*(\.\d{1,2})?', re.IGNORECASE),
            # 11 dollars
            re.compile(r'\d+ dollars', re.IGNORECASE),
            # 11 USD
            re.compile(r'\d+ USD', re.IGNORECASE)
        ]
        
        # Check if any pattern matches
        for pattern in patterns:
            if pattern.search(text):
                return True
        
        return False


    def add_extension(self, filename):
        """
        Add the .jpg extension to a filename if it doesn't already have a common image extension.
        As I saw, it is usually .JPG files in LA Times, but sometimes the URL doesn't show it.
        
        Args:
            filename (str): The original filename.
        
        Returns:
            str: The filename with the .jpg extension added if necessary.
        """
        
        # Check if the filename has a valid image extension using a regular expression, add if it is needed
        if not re.search(r'\.(?:jpg|jpeg|png|gif|webp|bmp|svg)$', filename, re.IGNORECASE):
            return f'{filename}.jpg'
        
        return filename


    def fix_date(self, date):
        """
        Fix common issues with date formats, including replacing "Sept" with "Sep" and converting relative times to the current date.
        
        Args:
            date (str): The original date string.
        
        Returns:
            str: The fixed date string.
        """
        # Replace 'Sept' with 'Sep' to standardize the month abbreviation
        date = date.replace('Sept', 'Sep')
        
        # Convert relative times like "X minutes ago" or "X hour ago" to the current date
        if ('minutes' in date or 'hour' in date):
            date = datetime.now().strftime('%Y-%m-%d')
            
        return date


    def parse_date(self, date_str):
        """
        Parse the date string using multiple formats.

        Args:
            date_str (str): The date string to parse.

        Returns:
            datetime: The parsed date.
        """
        
        date = None
        for date_format in self.date_formats:
            try:
                date = datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        if (date == None):
            logging.warning(f"Unable to parse date: {date_str}")
            date = datetime(1, 1, 1)
    
        else:
            date_str = date.strftime('%Y-%m-%d')
            logging.info(f"Parsed date: {date_str}")
    
        return date

    
    def open_la_times_and_search(self, search_phrase):
        self.open_browser_avoiding_robot_detection(f"https://www.latimes.com/")
        self.browser.maximize_browser_window()
        logging.info(f"Performing the search for {search_phrase}")

        # Wait to load the search button and click it
        try:
            self.browser.wait_until_element_is_visible("//button[@data-element='search-button']", timeout=60)
            self.browser.click_element_when_visible("//button[@data-element='search-button']")
        except AssertionError:
            logging.error("Could't find Search Button after 60 seconds")
            raise SeleniumError("Search Button not found")
            
        try:
            self.browser.wait_until_element_is_visible("//input[@data-element='search-form-input']", timeout=60)
            self.browser.input_text_when_element_is_visible("//input[@data-element='search-form-input']", search_phrase)
        except AssertionError:
            logging.error("Could't find Search Input after 60 seconds")
            raise SeleniumError("Search Input not found")
            
        try:
            self.browser.click_element_when_visible('//button[@data-element="search-submit-button"]')
        except AssertionError:
            logging.error("Could't submit the Search Form")
            raise SeleniumError("Search Form submission failed")
            
        logging.info(f"Search for {search_phrase} complete")


    def filter_la_times(self, news_category):
        
        if not(news_category == "" or news_category == None):
            logging.info(f"Selecting category: {news_category}")
            
            # Expand to see all topics
            try:
                self.browser.wait_until_element_is_visible('//span[@class="see-all-text"]', timeout=60)
                self.browser.click_element_when_visible('//span[@class="see-all-text"]')
            except AssertionError:
                logging.error("Could't find categories for this search")
                raise SeleniumError("Search categories failed")
            
            try:
                categories_xpath = "//ul[@class='search-filter-menu']/li"
                categories = self.browser.find_elements(categories_xpath + "//label/span")
                
                found_category = False
                for index, category in enumerate(categories):
                    # Check for a flag to avoid error when the category was already checked
                    if not(found_category):
                        if category.text.lower().strip() == news_category.lower().strip():
                            logging.info(f"Found category: {category}")
                            i = index + 1
                            self.browser.click_element_when_visible(f'{categories_xpath}[{i}]//label//input[@type="checkbox"]')
                            found_category = True

            except AssertionError:
                logging.error("Could't find this category for this search")
                raise SeleniumError("Category doesn't exists")  
                
        else:
            logging.info(f"No news category to select")
            
            
            
    def order_la_times(self):
        try:
            self.browser.wait_until_element_is_visible('//div[@class="search-results-module-no-results"]', timeout=10)
            logging.error("There is no results for the search")
            raise SeleniumError("No news available")
        except:
            pass
        
        try:
            self.browser.wait_until_element_is_visible('//select[@class="select-input"]', timeout=60)
            select_element = self.browser.find_elements("//select[@class='select-input']")
        except AssertionError:
            logging.error("Could't find the order selection box")
            raise SeleniumError("Order failed")
            
        try:
            self.browser.select_from_list_by_label(select_element, "Newest")
        except AssertionError:
            logging.error("Impossible to filter by the Newest")
            raise SeleniumError("Order failed")
            
        # When it changes the sorter, it will remove the page content and load again,
        # wait a little for the page to load
        time.sleep(5)


    def scrape_news_la_times(self, search_phrase, months):
        """
        Scrape news articles from the LA Times website.
        
        Returns:
            list: A list of dictionaries containing scraped news article data.
        """
        
        results = []
        try:
            if (months == "" or months == 0):
                start_date = datetime(1, 1, 1)
            else:
                start_date = datetime.now() - relativedelta(months=int(months))
            
            start_str = start_date.strftime('%Y-%m-%d')
            logging.info(f"Limit for the news: {start_str}")
            
            # Flag to indicate whether the start date has been reached
            reach_start_date = False 
            
            # A counter to help in the logging, it will tell me if there are no results for the search,
            # or it reached the last news without reaching the start_date, or it reached page 10 (limit for LATimes)
            count_pages = 1
            
            while not reach_start_date:
                # XPath to locate articles on the page
                articles_xpath = "//ul[@class='search-results-module-results-menu']/li"
                articles = self.browser.find_elements(articles_xpath)
                
                
                # Wait to load the first news
                try:
                    self.browser.wait_until_element_is_visible(f"{articles_xpath}[1]//h3[@class='promo-title']/a", timeout=60)
                except AssertionError:
                    logging.error("Could't load the news after 60 seconds")
                    raise SeleniumError("News didn't load")                
                
                for index, article in enumerate(articles):
                    try:
                        i = index + 1
                        
                        # Locate elements for title, description, date, and image within each article
                        title_element = self.browser.find_element(f"{articles_xpath}[{i}]//h3[@class='promo-title']/a")
                        description_element = self.browser.find_element(f"{articles_xpath}[{i}]//p[@class='promo-description']")
                        date_element = self.browser.find_element(f"{articles_xpath}[{i}]//p[@class='promo-timestamp']")
                        image_element = self.browser.find_element(f"{articles_xpath}[{i}]//div[@class='promo-media']//img[@class='image']") 
                        
                        # Extract text from the located elements
                        title = self.browser.get_text(title_element)
                        description = self.browser.get_text(description_element)
                        
                        # Fix the date format, parse it and format as string
                        date = self.browser.get_text(date_element)
                        date = self.fix_date(date)
                        date = self.parse_date(date)
                        date_str = date.strftime('%Y-%m-%d')
                        
                        # Get the URL of the image from the 'src' attribute
                        image_url = self.browser.get_element_attribute(image_element, 'src')
                        
                        # Extract the image name from the URL and make it a valid filename
                        image_name = self.make_valid_filename(image_url.split('%2F')[-1])
                        image_name = self.add_extension(image_name)
                        
                        # Count of search phrases in the title and description
                        count_in_title = self.count_string_in_text(title, search_phrase)
                        count_in_description = self.count_string_in_text(description, search_phrase)
                        total_count = count_in_title + count_in_description
                        
                        # Check if the title or description contains any money-related terms
                        money_in_title = self.has_money_in_text(title)
                        money_in_description = self.has_money_in_text(description)
                        money_in_text = money_in_title or money_in_description
                        
                        # If the article date is after the start date, add it to the results
                        if date > start_date:
                            
                            # Download the image and save it in the path
                            image_filepath = self.output_path + image_name
                            urllib.request.urlretrieve(image_url, image_filepath)
                            
                            # Append the results
                            results.append({
                                "Title": title,
                                "Date": date_str,
                                "Description": description,
                                "Picture filename": image_name,
                                "Count of search phrases in the title and description": total_count,
                                "Title or description contains any amount of money": money_in_text
                            })
                            logging.info(f"Scraped {title}")
                        else:
                            reach_start_date = True
                            logging.info(f"{title} is out of range, not scraped")
                    
                    except Exception as e:
                        logging.error(f"Failed to process article at index {index + 1}: {e}")
                        continue
                try:
                    # Interact with the button to change the page
                    # It would be easier to just change the URL, but for an RPA test, I choose to interact with the button 
                    self.browser.find_element("//div[@class='search-results-module-next-page']/a").click()                
                    count_pages += 1
                except:
                    logging.error(f"Can't load more news, reached page {count_pages}")
                    return results
            
            
            logging.info("Scraped all news articles that matches the constraints")
            return results
        except Exception as e:
            logging.error(f"Failed to scrape news articles: {e}")
            return results


    def save_news_data_to_excel(self, results):
        """
        Save the scraped news data to an Excel file.
        
        Args:
            results (list): A list of dictionaries containing scraped news data.
        """
        
        logging.info("Saving data to Excel")
        
        # Define the output file path
        output_file = os.path.join("output/", "News.xlsx")
        
        # Create a new workbook
        self.excel.create_workbook(output_file)
        
        # Define and append the header for the Excel sheet
        header = ["Title", "Date", "Description", "Picture filename", "Count of search", "Contains money"]
        self.excel.append_rows_to_worksheet([header], header=False)
        
        # Append each result to the worksheet
        for result in results:
            self.excel.append_rows_to_worksheet([result], header=False)
            
        # Save and close the workbook
        self.excel.save_workbook()
        self.excel.close_workbook()


    def close_browser(self):
        """
        Close the browser instance.
        """
        try:
            self.browser.close_browser()
            logging.info("Browser closed")
        except Exception as e:
            logging.error(f"Failed to close browser: {e}")
            raise


def scrape_news(Workitens = None):
    """
    Main function to scrape news articles based on a search term and configuration.

    Args:

    Returns:
        list: A list of dictionaries containing scraped news article data.
    """
        
    # Initialize the NewsScraper with the provided configuration
    logging.debug("Init NewsScraper")
    scraper = NewsScraper()
    results = []
    
    try:
        # Get all the variables: from the WorkItems, or from parameters
        logging.debug("Getting workitens")
        if Workitens == None:
            search_phrase, months, news_category = scraper.get_workitem() 
        else:
            search_phrase, months, news_category = Workitens 
            
        # Open, filter and order LA Times
        logging.info("Opening LA Times")
        scraper.open_la_times_and_search(search_phrase)
        
        logging.info("Filtering categories in LA Times")
        scraper.filter_la_times(news_category)
        
        logging.info("Ordering news in LA Times")
        scraper.order_la_times()
        
        # Scrape news articles from the LA Times
        results = scraper.scrape_news_la_times(search_phrase, months)
        
        # If there are no results, create an Excel file with only the header
        if len(results) == 0: 
            results.append({
                "Title": '',
                "Date": '',
                "Description": '',
                "Picture filename": '',
                "Count of search phrases in the title and description": '',
                "Title or description contains any amount of money": ''
            })
            
        # Save the scraped news data to an Excel file
        logging.debug("Saving Excel")
        scraper.save_news_data_to_excel(results)
        
    except SeleniumError as e:
        logging.error(f"Search operation failed: {e.message}")
        
    finally:
        # Ensure the browser is closed even if an error occurs
        scraper.close_browser()
        
    # Return the results of the scraping process
    return results


if __name__ == "__main__":
    
    log_path = './output/rpa_news_scraper.log'
    
    logging.basicConfig(
        filename = log_path,
        level = logging.INFO,
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scrape_news(['amazon', 1, 'Climate & Environment'])
