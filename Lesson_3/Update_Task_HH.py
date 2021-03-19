from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from pymongo import MongoClient


def parser_hh(vacancy):
    vacancy_date = []

    params = {'L_is_autosearch': 'false', 'clusters': 'true', 'enable_snippets': 'true', 'text': vacancy, 'page': 0}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'}

    link = 'https://hh.ru/search/vacancy'

    html = requests.get(link, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')

        page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = 1
            print(last_page)
        else:
            last_page = int(page_block.find_all('a', {'class': 'HH-Pager-Control'})[
                                -2].getText())  # получаем последнюю страцу выдачи
        print(f'Количество страниц парсинга {last_page}')
        for page in range(last_page):
            params['page'] = page
            html = requests.get(link, params=params, headers=headers)

            if html.ok:
                parsed_html = bs(html.text, 'html.parser')

                vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                    .find_all('div', {'class': 'vacancy-serp-item'})

                for item in vacancy_items:
                    vacancy_date.append(parser_item_hh(item))

    return vacancy_date


def parser_item_hh(item):
    vacancy_date = {}

    # vacancy_name
    vacancy_name = item.find('span', {'class': 'resume-search-item__name'}) \
        .getText() \
        .replace(u'\xa0', u' ')

    vacancy_date['vacancy_name'] = vacancy_name

    # company_name
    try:
        company_name = item.find('a', {'class': 'bloko-link_secondary'}) \
            .getText()
        vacancy_date['company_name'] = company_name
    except:
        print('')

    # city
    city = item.find('span', {'class': 'vacancy-serp-item__meta-info'}) \
        .getText() \
        .split(', ')[0]

    vacancy_date['city'] = city

    # metro station
    metro_station = item.find('span', {'class': 'vacancy-serp-item__meta-info'}).findChild()

    if not metro_station:
        metro_station = None
    else:
        metro_station = metro_station.getText()

    vacancy_date['metro_station'] = metro_station

    # salary
    salary_min = None
    salary_max = None
    salary_currency = None
    salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary:
        salary = salary.getText() \
            .replace(u'\xa0', u'')

        salary = re.split(r'\s|-', salary)

        if salary[0] == 'до':
            salary_max = int(salary[1])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
        else:
            salary_min = int(salary[0])
            salary_max = int(salary[1])

        salary_currency = salary[2]

    vacancy_date['salary_min'] = salary_min
    vacancy_date['salary_max'] = salary_max
    vacancy_date['salary_currency'] = salary_currency

    # link
    vacancy_link = item.find('a')['href']
    vacancy_date['vacancy_link'] = vacancy_link

    # site
    vacancy_date['site'] = 'hh.ru'

    return vacancy_date


def parser_vacancy(vacancy, db_name, client):
    vacancy_date = []
    vacancy_date.extend(parser_hh(vacancy))
    df = pd.DataFrame(vacancy_date)
    df.to_csv('result_hh.csv', index=True)
    db = client[db_name]
    choice = int(input('Нажмите 1 для сохранения в БД MongoDB \n'
                       'Нажмите 2 для сохранения новых вакансий в БД MongoDB '))
    if choice == 1:
        db.hh_db.insert_many(vacancy_date)
    elif choice == 2:
        save_counter = 0
        for elem in vacancy_date:
            is_exists = db.hh_db.find_one({'vacancy_link': elem['vacancy_link']})
            if not is_exists:
                db.hh_db.insert_one(elem)
                save_counter += 1
    return df


def find_mongo(db_name, client):
    db = client[db_name]
    choice = input('Хотите осуществить поиск по БД MongoDB(y/n)?: ').lower()
    if choice == 'y':
        choice = int(input('1. Найти вакансии с заработной платой больше введённой суммы. \n'
                           '2. Найти вакансии без указания заработанной платы. '))
        if choice == 1:
            salary = input('Введите сумму: ')
            result = db.hh_db.find({
                'salary_min': {'$gt': f'{salary}'},
                'salary_max': {'$gt': f'{salary}'}
            })
            for elem in result:
                print(elem)
        if choice == 2:
            result = db.hh_db.find({'salary_min': None, 'salary_max': None})
            for elem in result:
                print(elem)
    if choice == 'n':
        print('Ok')


choice = int(input('Нажмите 1 для парсинга вакансий с сайта HH.RU \n'
                   'Нажмите 2 для работы с БД MongoDB '))
db_name = 'hh_db'
client = MongoClient('mongodb://127.0.0.1:27017')
if choice == 1:
    vacancy = input('Введите название вакансии для парсинга - ')
    df = parser_vacancy(vacancy, db_name, client)
elif choice == 2:
    find_mongo(db_name, client)
