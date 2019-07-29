# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArchiveItem(scrapy.Item):
    domain = scrapy.Field()
    domain_url = scrapy.Field()
    fake = scrapy.Field()
    timestamp = scrapy.Field()
