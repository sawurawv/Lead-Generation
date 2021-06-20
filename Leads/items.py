# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LeadsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    business_name = scrapy.Field()
    owner = scrapy.Field()
    phone= scrapy.Field()
    email= scrapy.Field()
    website= scrapy.Field()
    state= scrapy.Field()
    street_address= scrapy.Field()
    city = scrapy.Field()
    zip_code= scrapy.Field()
    directory= scrapy.Field()
    keyword= scrapy.Field()
    directory_business_link = scrapy.Field()

    pass
