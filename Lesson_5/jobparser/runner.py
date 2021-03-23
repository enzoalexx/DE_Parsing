from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider


if __name__ == '__main__':
    vacancy = 'data+engineer'  # for hhru
    #vacancy = 'data-engineer'  # for sjru

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(HhruSpider, vacancy=vacancy)
    #process.crawl(SjruSpider, vacancy=vacancy)

    process.start()
