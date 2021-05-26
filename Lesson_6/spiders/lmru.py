import scrapy
from leroymerlin.lmparser.items import LmparserItem
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']

    def __init__(self, search):
        super(LmruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        product_links = response.xpath('//a[contains(@class,"plp-item__info__title")]/@href').extract()
        for link in product_links:
            yield response.follow(link, callback=self.handle_producr_data)
        next_page = response.xpath('//a[@class = "paginator-button next-paginator-button"]').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def handle_producr_data(self, response: HtmlResponse):
        loader = ItemLoader(item=LmparserItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('title', '//h1[@slot="title"]/text()')
        loader.add_xpath('photos', '//img[@alt="product image"]/@src')
        loader.add_xpath('params', '//div[@class="def-list__group"]/*/text()')
        loader.add_xpath('price', '//meta[@itemprop="price"]/@content')
        yield loader.load_item()
