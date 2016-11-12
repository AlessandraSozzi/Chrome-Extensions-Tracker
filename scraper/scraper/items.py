# -*- coding: utf-8 -*-

from scrapy.item import Item, Field


class ScraperItem(scrapy.Item):
    
    name = Field()
	google_id = Field()
	avg_rating = Field()
	raters = Field()
	users = Field()
	version = Field()
