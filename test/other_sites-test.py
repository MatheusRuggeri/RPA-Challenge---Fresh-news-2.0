# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 14:14:28 2024

@author: JoaoMurdiga
"""

    def scrape_news_reuters(self):
        try:
            articles = self.browser.find_elements("//li[@class='search-results__item__2oqiX']")
            results = []
            
            for article in articles:
                title_element = self.browser.find_element("class:header", parent=article)
                description_element = ''
                date_element = self.browser.find_element("xpath:.//time", parent=article)
                image_element = self.browser.find_element("xpath:.//img", parent=article)
                          
                title = self.browser.get_text(title_element)
                
                # Get the URL of the image from the 'src' attribute
                image_url = self.browser.get_element_attribute(image_element, 'src')
                
                # Extract the image name from the URL
                image_name = image_url.split('/')[-1]
                
                # Download the image and save in the path
                urllib.request.urlretrieve(image_url, f'../images/{image_name}')
                
                
                results.append({
                    "Title": title,
                    "Date": date,
                    "Description": description,
                    "Picture filename": image_name,
                    "Count of search phrases in the title and description": count_search,
                    "Title or description contains any amount of money": flag_contains_money
                })
                
            logging.info("Scraped news articles successfully")
            return results
        except Exception as e:
            logging.error(f"Failed to scrape news articles: {e}")
            raise


    def scrape_news_ap_news(self):
        try:
            # Find the select element
            select_element = self.browser.find_elements("//select[@class='Select-input']")
            
            # Select the option with the text "Newest"
            self.browser.select_from_list_by_label(select_element, "Newest")
            
            articles = self.browser.find_elements("//div[@class='SearchResultsModule-results']")
            results = []
            
            for article in articles:
                title_element = self.browser.find_element("//div[@class='PagePromo-title']/a/span", parent=article)
                description_element = self.browser.find_element("//div[@class='PagePromo-description']/a/span", parent=article)
                date_element = self.browser.find_element("//span[@class='Timestamp-template']", parent=article)
                
                page_images = self.browser.find_element("//div[@class='PagePromo-media']", parent=article) 
                image_element = self.browser.find_element("//img[@class='Image']", parent=page_images)
                          
                title = self.browser.get_text(title_element)
                description = self.browser.get_text(description_element)
                date = self.browser.get_text(date_element)
                
                # Get the URL of the image from the 'src' attribute
                image_url = self.browser.get_element_attribute(image_element, 'src')
                
                # Extract the image name from the URL
                image_name = image_url.split('/')[-1]
                
                # Download the image and save in the path
                urllib.request.urlretrieve(image_url, f'../images/{image_name}')
                
                
                results.append({
                    "Title": title,
                    "Date": date,
                    "Description": description,
                    "Picture filename": image_name,
                    "Count of search phrases in the title and description": count_search,
                    "Title or description contains any amount of money": flag_contains_money
                })
                
            logging.info("Scraped news articles successfully")
            return results
        except Exception as e:
            logging.error(f"Failed to scrape news articles: {e}")
            raise
