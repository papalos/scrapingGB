# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    _id = scrapy.Field()
    item_name = scrapy.Field()
    item_url = scrapy.Field()
    item_salary = scrapy.Field()