from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from pymongo import MongoClient


def _parser_superjob(vacancy):
    vacancy_date = []

    params = {'keywords': vacancy, 'noGeo': 1}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'
    }

    link = 'https://russia.superjob.ru/vacancy/search/'

    html = requests.get(link, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')

        page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
        if not page_block:
            last_page = 1
        else:
            page_block = page_block.findParent()
            last_page = int(page_block.find_all('a')[-2].getText())
            print(f'Количество страниц парсинга {last_page}')

        for page in range(0, last_page + 1):
            params['page'] = page
            html = requests.get(link, params=params, headers=headers)

        if html.ok:
            parsed_html = bs(html.text, 'html.parser')
            vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})

            for item in vacancy_items:
                vacancy_date.append(_parser_item_superjob(item))

    return vacancy_date


def _parser_item_superjob(item):
    vacancy_date = {}

    # vacancy_name
    vacancy_name = item.find_all('a')
    if len(vacancy_name) > 1:
        vacancy_name = vacancy_name[-2].getText()
    else:
        vacancy_name = vacancy_name[0].getText()
    vacancy_date['vacancy_name'] = vacancy_name

    # company_name
    company_name = item.find('span', {'class': 'f-test-text-vacancy-item-company-name'})

    if not company_name:
        company_name = item.findParent() \
            .find('span', {'class': 'f-test-text-vacancy-item-company-name'}) \
            .getText()
    else:
        company_name = company_name.getText()

    vacancy_date['company_name'] = company_name

    # city
    company_location = item.find('span', {'class': 'f-test-text-company-item-location'}) \
        .findChildren()[2] \
        .getText() \
        .split(',')

    vacancy_date['city'] = company_location[0]

    # metro station
    if len(company_location) > 1:
        metro_station = company_location[1]
    else:
        metro_station = None

    vacancy_date['metro_station'] = metro_station

    # salary
    salary = item.find('span', {'class': 'f-test-text-company-item-salary'}) \
        .findChildren()
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary_currency = salary[-1].getText()
        is_check_salary = item.find('span', {'class': 'f-test-text-company-item-salary'}) \
            .getText() \
            .replace(u'\xa0', u' ') \
            .split(' ', 1)[0]

        if is_check_salary == 'до' or len(salary) == 2:
            salary_min = None
            salary_max = int(salary[0].getText() \
                             .replace(u'\xa0', u''))
        elif is_check_salary == 'от':
            salary_min = salary[0].getText() \
                .replace(u'\xa0', u'') \
                .strip('отруб.')

            salary_max = None
        else:
            salary_min = salary[0].getText() \
                .replace(u'\xa0', u'')

            salary_max = salary[-1].getText() \
                .replace(u'\xa0', u'')

    vacancy_date['salary_min'] = salary_min
    vacancy_date['salary_max'] = salary_max
    vacancy_date['salary_currency'] = salary_currency

    # link
    vacancy_link = item.find_all('a')

    if len(vacancy_link) > 1:
        vacancy_link = vacancy_link[-2]['href']
    else:
        vacancy_link = vacancy_link[0]['href']

    vacancy_date['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

    # site
    vacancy_date['site'] = 'superjob.ru'

    return vacancy_date


def parser_vacancy(vacancy):
    vacancy_date = []
    vacancy_date.extend(_parser_superjob(vacancy))
    df = pd.DataFrame(vacancy_date)
    df.to_csv('result_sj.csv', index=True)
    db_name = 'sj_db'
    client = MongoClient('mongodb://127.0.0.1:27017')
    db = client[db_name]
    #db.sj_db.insert_many(vacancy_date)
    choice = int(input('Нажмите 1 для сохранения в БД MongoDB \n'
                       'Нажмите 2 для сохранения новых вакансий в БД MongoDB'))
    if choice == 1:
        db.sj_db.insert_many(vacancy_date)
    elif choice == 2:
        save_counter = 0
        for elem in vacancy_date:
            is_exists = db.sj_db.find_one({'vacancy_link': elem['vacancy_link']})
            if not is_exists:
                db.sj_db.insert_one(elem)
                save_counter += 1

    choice = input('Хотите осуществить поиск по БД MongoDB(y/n)?: ').lower()
    if choice == 'y':
        choice = int(input('1. Найти вакансии с заработной платой больше введённой суммы. \n'
                           '2. Найти вакансии без указания заработанной платы.'))
        if choice == 1:
            salary = input('Введите сумму: ')
            result = db.sj_db.find({
                'salary_min': {'$gt': f'{salary}'},
                'salary_max': {'$gt': f'{salary}'}
            })
            for elem in result:
                print(elem)
        if choice == 2:
            result = db.sj_db.find({'salary_min': None, 'salary_max': None})
            for elem in result:
                print(elem)
    if choice == 'n':
        print('Ok')

    return df


vacancy = input('Введите название вакансии для парсинга - ')
df = parser_vacancy(vacancy)
