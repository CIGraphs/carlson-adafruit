# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WebfocusedcrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    infourl = scrapy.Field() 
    entity = scrapy.Field()
    entitytype = scrapy.Field()
    text = scrapy.Field()
    attributeinfo = scrapy.Field()

