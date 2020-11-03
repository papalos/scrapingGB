# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def int_price(value):
    return int(value.replace(' ', ''))


def f_preproc(value):
    #print(value.xpath('./div'))
    f_dict = {}
    for f in value.xpath('./div'):
        #print(f.xpath('.//dt/text()').extract_first())
        #print(f.xpath('.//dd/text()').extract_first())
        key = f.xpath('.//dt/text()').extract_first()
        value = f.xpath('.//dd/text()').extract_first().replace('\n', '').replace(' ', '')

        f_dict[key] = value
    return f_dict


class LeruaItem(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(int_price))
    photo_links = scrapy.Field()
    feature = scrapy.Field(input_processor=MapCompose(f_preproc))
