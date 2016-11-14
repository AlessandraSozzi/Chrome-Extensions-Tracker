# -*- coding: utf-8 -*-

from scrapy.item import Item, Field


class ScraperItem(Item):
    name = Field()
    google_id = Field()
    avg_rating = Field()
    raters = Field()
    users = Field()
    version = Field()
    group = Field()
    rank = Field()
    short_text = Field()
    long_text = Field()
