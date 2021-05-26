import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy=None):
        super(HhruSpider, self).__init__()
        self.start_urls = [f'https://ufa.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text={vacancy}&L_save_area=true&area=99&from=cluster_area&showClusters=true']

    def parse(self, response: HtmlResponse):
        # print(response.status)
        vacancy_links = response.xpath(
            '//div[contains(@class, "vacancy-serp-item")]//a[contains(@class, "HH-LinkModifier")]/@href'
        ).extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.parse_vacancies)

        next_page = response.xpath('//a[contains(@class, "-Pager-Controls-Next")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        # print()
        pass

    def parse_vacancies(self, response: HtmlResponse):
        # Не стоит обрабатывать данные здесь
        title = response.xpath("//h1//text()").get()
        salary = response.xpath("//p[contains(@class, 'vacancy-salary')]//span/text()").getall()
        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]

        yield JobparserItem(title=title, salary=salary, vacancy_link=vacancy_link, site_scraping=site_scraping)
