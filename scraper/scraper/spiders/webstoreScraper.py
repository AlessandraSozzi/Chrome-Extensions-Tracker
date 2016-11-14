# -*- coding: utf-8 -*-

import re
import time
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver

from scrapy.http import Request
from scrapy.spiders import Spider
from scraper.items import ScraperItem
from scrapy.selector import HtmlXPathSelector


class WebstorescraperSpider(Spider):
    name = "webstoreScraper"
    allowed_domains = ["chrome.google.com"]
    start_urls = ["https://chrome.google.com/webstore/category/extensions"]

    def __init__(self, category = None, *args, **kwargs):
        super(WebstorescraperSpider, self).__init__(*args, **kwargs)
        if category:
            self.category = category
        else:
            self.category = "Photos"


    def parse_item(self, response):
        """Process Extension and extract fieds
        -   Name                :   name of the extension
        -   Google ID           :   string ID used by Google, found on the permalink of the extension
        -   Average Rating      :   Average rating, in decimal point
        -   Number of raters    :   Number of users who rated the extension
        -   Users               :   Number of users using the extension
        -   Version             :   Version as shown in the description
        -   Group               :   Whether the extension was featured in a group (eg: 'Our Top Picks') otherwise None
        -   Rank                :   Smart Rank given by Google (order of display) see here: https://developer.chrome.com/webstore/faq#faq-gen-24
        -   Short description   :   Short description of the extension
        -   Long description    :   Long description of the extension

        """
    	soup = BeautifulSoup(response.text, "lxml")

    	item = ScraperItem()

    	item_scope = soup.find('div', attrs={'class':'e-f'})

    	header = item_scope.find('div', attrs={'class':'e-f-w-Va'})

    	# Name
    	item["name"] = header.find('h1', attrs={'class':'e-f-w'}).text

    	# Google ID
    	item["google_id"] = header.find('div', attrs={'class':'rsw-stars'})['g:url'].split("id=")[1]

    	# Average Rating
    	rating = header.find('span', attrs={'class':'q-N-nd'})
    	avg_rating = rating["aria-label"]
    	m = re.search("Average rating\s(.+?)\s", avg_rating)
    	if m:
    		item["avg_rating"] = float(m.group(1))

    	# Number of Raters
    	item["raters"] = int(re.sub("\(|\)","", rating.text))

    	# Users
    	users = header.find('span', attrs = {'class':'e-f-ih'})["title"]
    	if users:
    		item["users"] = int(re.sub(',|users','',users).strip())
    	else:
    		item["users"] = 0

    	# Version
    	item["version"] = item_scope.find('span', attrs = {'class':'C-b-p-D-Xe h-C-b-p-D-md'}).text

        # Group
        item["group"] = response.meta.get('group', None)

        # Rank
        item["rank"] = response.meta.get('rank', None)

        # Short and long description
        description = item_scope.find('div', attrs = {'class':'C-b-p-j-D Ka-Ia-j C-b-p-j-D-gi'})
        if description:
            short_text = description.find('div', attrs = {'itemprop':'description'})
            long_text = description.find('pre')
        if short_text:
            item["short_text"] = short_text.text
        if long_text:
            item["long_text"] = long_text.text


    	return item

    
    def parse_group(self, response):
        """Process the Featured group page:
        1. Scroll the page until the end
        2. Extract all URLs which lead to the extension details page
        3. Yield a new requests for each extracted extension URL to be parsed by parse_item()

        """
        driver = webdriver.Chrome("/Users/Alessandra/Documents/WebDriver/chromedriver")
        
        driver.get(response.url)

        time.sleep(10)

        self.log("I'm in the current category page: %s with group name: %s" % (driver.current_url, response.meta.get('group', None)))

        # Scroll page until end
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")           

        while True:
            lastCount = lenOfPage
            self.log('lenOfPage %d' % lenOfPage)
            time.sleep(5)
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
            if (lastCount == lenOfPage):
                break


        # Extract extensions URLs and yield new Requests with parse_item callback
        extensions = driver.find_elements_by_xpath("//a[@class='a-u']")
        self.log("Extensions extracted %d" % len(extensions))

        for rank, extension in enumerate(extensions):
            url = extension.get_attribute("href")
            request = Request(url = url, callback = self.parse_item)
            request.meta.update(rank = rank)
            request.meta.update(group = response.meta.get('group', None))
            yield request

        driver.close()


    def parse(self, response):
        """Process the first page:
        1. Click on the menu
        2. Choose the category specified as argument when running the scraper ( eg: scrapy crawl webstoreScraper -a category="By Google" -o extensions.json )
            or use "Photos" as default
        3. Click the category and wait for the new page to be loaded
        4. Find groups in the page and extract URLs
        4. Yield a new requests for each extracted group URL to be parsed by parse_group()
        5. Send the current page to parse_group() (so that also the extensions in this page are parsed)

        """
    	driver = webdriver.Chrome("/Users/Alessandra/Documents/WebDriver/chromedriver")
    	driver.get(response.url)

    	time.sleep(10)

        # Click menu
        menu = driver.find_element_by_xpath("//span[@class='h-n-j-Z-ea-aa ga-dd-Va g-aa-ca']")
        menu.click()

        # Find category
        options = driver.find_element_by_xpath("//div[@role='listbox']").find_elements_by_xpath("//div[@role='option']")

        for option in options:
            option_id = option.get_attribute("id")
            option_text = option.text
            self.log("Option found: %s with id %s" % (option_text, option_id))
            if(option_text == self.category): 
                driver.find_element_by_xpath("//div[@role='listbox']").find_element_by_xpath("//div[@id='" + option_id + "']").click()
                time.sleep(10)
                current_url = driver.current_url
                break
        
        time.sleep(10)
        
        
        # Find extensions groups
        groups = driver.find_elements_by_xpath("//a[@class='a-K-o-y a-d-zc a-hn-K-o']")
        groups = [(group.get_attribute("href"), group.find_element_by_xpath("//div[@class='a-K-o-w']").text) for group in groups]
        driver.close()
        
        for (group, group_name) in groups:
            request = Request(url = group, callback = self.parse_group)
            request.meta.update(group = group_name)
            yield request

        # Send the current page 
        yield Request(url = current_url, callback = self.parse_group)







