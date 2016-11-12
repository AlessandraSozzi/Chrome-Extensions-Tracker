# -*- coding: utf-8 -*-
import scrapy


class WebstorescraperSpider(scrapy.Spider):
    name = "webstoreScraper"
    allowed_domains = ["chrome.google.com"]
    start_urls = (
        'https://chrome.google.com/webstore/category/ext/28-photos',
    )

    def parse(self, response):
        pass
