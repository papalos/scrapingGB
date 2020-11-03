import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from lerua.items import LeruaItem


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response):
        next_page = response.xpath("//a[@class='paginator-button next-paginator-button']/@href").extract_first()
        goods_links = response.xpath('//a[@class="plp-item__info__title"]')
        for link in goods_links:
            yield response.follow(link, callback=self.parse_goods)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaItem(), response=response)
        loader.add_xpath('title', '//h1[@class="header-2"]/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('photo_links', '//uc-pdp-media-carousel[@slot="media-content"]/picture/source[1]/@data-origin')
        loader.add_value('feature', response.xpath('//uc-pdp-section-vlimited/dl'))
        yield loader.load_item()
