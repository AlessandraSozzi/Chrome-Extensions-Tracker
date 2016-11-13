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
    start_urls = ["https://chrome.google.com/webstore/category/ext/28-photos"]

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome("/Users/Alessandra/Documents/WebDriver/chromedriver")
        super(WebstorescraperSpider, self).__init__(*args, **kwargs)


    def parse_item(self, response):

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
    	else:
    		item["avg_rating"] = np.nan

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


    	return item

    	


    def parse(self, response):
    	
    	self.driver.get(response.url)

    	time.sleep(10)

    	# Scroll page until end
    	lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")           

    	while True:
    		lastCount = lenOfPage
    		self.log('lenOfPage %d' % lenOfPage)
    		time.sleep(5)
    		lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
    		if (lastCount == lenOfPage):
    			break

    	# Extract extensions URLs and yield new Requests with parse_item callback
    	extensions = self.driver.find_elements_by_xpath("//a[@class='a-u']")
    	self.log("Extensions extracted %d" % len(extensions))

    	for extension in extensions:
    		url = extension.get_attribute("href")
    		yield Request(url = url, callback = self.parse_item)

    	# Second call
    	yield Request(url = "https://chrome.google.com/webstore/category/collection/top_picks_photos", callback = self.parse)

    def closed(self):
    	self.driver.close()







