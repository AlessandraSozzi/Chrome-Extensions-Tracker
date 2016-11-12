# -*- coding: utf-8 -*-

import re
import numpy as np
from selenium import webdriver

from scrapy.http import Request
from scrapy.spiders import Spider
from scraper.items import ScraperItem
from scrapy.selector import HtmlXPathSelector


class WebstorescraperSpider(Spider):
    name = "webstoreScraper"
    allowed_domains = ["chrome.google.com"]
    start_urls = (
        'https://chrome.google.com/webstore/category/ext/28-photos',
    )

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome('/Users/Alessandra/Documents/WebDriver/chromedriver')
        super(webstoreScraper, self).__init__(*args, **kwargs)

    def parse(self, response):
    	
    	self.driver.get(response.url)

    	time.sleep(10)

    	# Scroll page until end
    	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")           
		
		while True:
		    lastCount = lenOfPage
		    time.sleep(5)
		    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
		    if (lastCount == lenOfPage):
		        break

		


