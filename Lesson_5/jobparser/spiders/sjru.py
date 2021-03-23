import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['http://superjob.ru/']

    def __init__(self, vacancy=None):
        super(SjruSpider, self).__init__()
        self.start_urls = [f'https://russia.superjob.ru/vakansii/{vacancy}.html']

    def parse(self, response: HtmlResponse):
        # print(response.status)
        vacancy_links = response.xpath('//div[contains(@class, "vacancy-item")]//a[contains(@class, "6AfZ9")]/@href').extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.parse_vacancies)

        next_page = response.xpath('//a[@rel = "next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        # print()
        pass

    def parse_vacancies(self, response: HtmlResponse):
        # Не стоит обрабатывать данные здесь
        title = response.xpath("//h1//text()").get()
        salary = response.xpath("//div[@class='_3MVeX']//span[contains(@class,'PlM3e')]/text()").getall()
        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]

        yield JobparserItem(title=title, salary=salary, vacancy_link=vacancy_link, site_scraping=site_scraping)
