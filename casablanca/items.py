# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CasablancaItem(scrapy.Item):
    Serial = scrapy.Field()
    PlatformURL = scrapy.Field()
    url = scrapy.Field()
    rent_buy = scrapy.Field()
    price = scrapy.Field()
    other_charges = scrapy.Field()
    other_charges1 = scrapy.Field()
    agency_fee = scrapy.Field()
    other_agency_fee = scrapy.Field()
    deposit = scrapy.Field()
