# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайта superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через
# input или аргументы). Получившийся список должен содержать в себе минимум:
#
# *Наименование вакансии
# *Предлагаемую зарплату (отдельно мин. и и отдельно макс.)
# *Ссылку на саму вакансию
# *Сайт откуда собрана вакансия
#
# По своему желанию можно добавить еще работодателя и расположение.
# Данная структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести
# с помощью dataFrame через pandas.

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd


def _parser_hh(vacancy):
    vacancy_date = []

    params = {'L_is_autosearch': 'false', 'clusters': 'true', 'enable_snippets': 'true', 'text': vacancy, 'page': 0}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.101 Yowser/2.5 Safari/537.36'}

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
                    vacancy_date.append(_parser_item_hh(item))

    return vacancy_date


def _parser_item_hh(item):
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
    salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.getText() \
            .replace(u'\xa0', u'')

        salary = re.split(r'\s|-', salary)

        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
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


def parser_vacancy(vacancy):
    vacancy_date = []
    vacancy_date.extend(_parser_hh(vacancy))
    df = pd.DataFrame(vacancy_date)
    df.to_csv('result_hh.csv', index=True)

    return df


vacancy = input('Введите название вакансии для парсинга - ')
df = parser_vacancy(vacancy)
print(df[:2])
print(df[-2:])
