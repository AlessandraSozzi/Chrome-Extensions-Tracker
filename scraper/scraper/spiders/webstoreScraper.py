# -*- coding: utf-8 -*-
import scrapy


class WebstorescraperSpider(scrapy.Spider):
    name = "webstoreScraper"
    allowed_domains = ["chrome.google.com"]
    start_urls = (
        'http://www.chrome.google.com/',
    )

    def parse(self, response):
        pass
