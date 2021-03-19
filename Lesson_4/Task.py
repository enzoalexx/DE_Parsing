from lxml import html
import requests
from datetime import datetime
from pymongo import MongoClient


def get_news_lenta():
    news = []

    keys = ('title', 'date', 'link')
    date_format = ' %H:%M, %d %B %Y'
    link_lenta = 'https://lenta.ru/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'}

    request = requests.get(link_lenta, headers=headers)

    root = html.fromstring(request.text)
    root.make_links_absolute(link_lenta)

    news_links = root.xpath("(//div[@class='first-item']/h2 | //div[@class='item'])/a/@href")

    news_text = root.xpath("(//div[@class='first-item']/h2 | //div[@class='item'])/a/text()")

    for i in range(len(news_text)):
        news_text[i] = news_text[i].replace(u'\xa0', u' ')

    news_date = []

    for item in news_links:
        request = requests.get(item)
        root = html.fromstring(request.text)
        date = root.xpath("//time[@class='g-time']/@datetime")
        news_date.extend(date)

    for i in range(len(news_date)):
        date_temp = news_date[i]
        news_date[i] = date_temp.replace('марта', 'March')
        news_date[i] = datetime.strptime(news_date[i], date_format)

    for item in list(zip(news_text, news_date, news_links)):
        news_dict = {}
        for key, value in zip(keys, item):
            news_dict[key] = value

        news_dict['source'] = 'lenta.ru'
        news.append(news_dict)

    return news


def get_news_mail():
    news = []

    keys = ('title', 'date', 'link', 'source')
    date_format = '%Y-%m-%dT%H:%M:%S%z'
    link_mail = 'https://news.mail.ru/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'}

    request = requests.get(link_mail, headers=headers)

    root = html.fromstring(request.text)
    root.make_links_absolute(link_mail)

    news_links = root.xpath("(//div[contains(@class, 'daynews_')] | //li)/a/@href")

    news_text = root.xpath("(//span[@class='photo__captions']/span | //li/a)/text()")

    for i in range(len(news_text)):
        news_text[i] = news_text[i].replace(u'\xa0', u' ')

    news_date = []
    news_source = []

    for item in news_links:
        request = requests.get(item)
        root = html.fromstring(request.text)
        date = root.xpath("//span[contains(@class,'note__text')]/@datetime")
        source = root.xpath("//span[contains(@class,'note')]/a/@href")
        news_date.extend(date)
        news_source.extend(source)

    for i in range(len(news_date)):
        news_date[i] = datetime.strptime(news_date[i], date_format)

    for item in list(zip(news_text, news_date, news_links, news_source)):
        news_dict = {}
        for key, value in zip(keys, item):
            news_dict[key] = value

        news.append(news_dict)

    return news


def get_news_yandex():
    news = []

    keys = ('title', 'date', 'link', 'source')
    date_format = '%Y-%m-%d %H:%M'
    link_yandex = 'https://yandex.ru/news'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'}

    request = requests.get(link_yandex, headers=headers)

    root = html.fromstring(request.text)
    root.make_links_absolute(link_yandex)

    news_links = root.xpath("(//div[@class='mg-card__inner'] | //div[@class='mg-card__text'])/a/@href")

    news_text = root.xpath("(//div[@class='mg-card__inner'] | //div[@class='mg-card__text'])/a/h2/text()")

    news_date = root.xpath("(//div[contains(@class,'mg-card-footer')]//span[contains(@class,'time')])/text()")

    news_source = root.xpath("(//div[contains(@class,'mg-card-footer')]//a)/text()")

    for i in range(len(news_text)):
        news_text[i] = news_text[i].replace(u'\xa0', u' ')

    for i in range(len(news_date)):
        news_date[i] = f'{(datetime.now().date())} {(news_date[i])}'
        news_date[i] = datetime.strptime(news_date[i], date_format)

    for item in list(zip(news_text, news_date, news_links, news_source)):
        news_dict = {}
        for key, value in zip(keys, item):
            news_dict[key] = value

        news.append(news_dict)

    return news


def transfer_to_mongo(news, db_name, client):
    db = client[db_name]
    choice = int(input('Нажмите 1 для сохранения в БД MongoDB \n'
                       'Нажмите 2 для сохранения новых новостей в БД MongoDB '))
    if choice == 1:
        db.parsing_news.insert_many(news)
        print(f'Transfer completed.')
    elif choice == 2:
        save_counter = 0
        for elem in news:
            is_exists = db.parsing_news.find_one({'link': elem['link']})
            if not is_exists:
                db.parsing_news.insert_one(elem)
                save_counter += 1
                print(f'Updating completed.')


db_name = 'news_db'
client = MongoClient('mongodb://127.0.0.1:27017')

lenta = get_news_lenta()
transfer_to_mongo(lenta, db_name, client)

mail = get_news_mail()
transfer_to_mongo(mail, db_name, client)

yandex = get_news_yandex()
transfer_to_mongo(yandex, db_name, client)
