import os
import pprint
from random import randint
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from pymongo import MongoClient

DRIVER_PATH = 'D:/PyProjects/chromedriver.exe'
URL = 'https://vk.com/tokyofashion'
options = Options()
options.add_argument("--window-size=1700,700")


def get_value(elems):
    if elems:
        return elems[0]
    return None


def find_posts(driver):
    find_button = driver.find_element_by_xpath('//*[contains(@class,"ui_tab_plain ui_tab_search")]')
    find_button.click()
    sleep(randint(1, 5))
    search_field = driver.find_element_by_id('wall_search')
    search_request = input('Type your search request: ')
    search_field.send_keys(search_request)
    sleep(randint(1, 5))
    search_field.send_keys(Keys.ENTER)


def scroll_page(driver):
    for i in range(10):
        sleep(randint(3, 9))
        try:
            unauth_box = driver.find_element_by_class_name("UnauthActionBox__in")
            while unauth_box:
                notyet_btn = driver.find_element_by_class_name("JoinForm__notNow")
                notyet_btn.click()
        except:
            driver.find_element_by_tag_name("html").send_keys(Keys.END)


def parse_post(elem):
    post_summary = {}
    post = html.fromstring(elem.get_attribute("outerHTML"))
    post_summary['link'] = 'https://vk.com' + get_value(post.xpath('//*[@class="post_link"]//@href'))
    post_summary['date'] = get_value(post.xpath('//*[@class="rel_date"]/text()')).replace('\xa0', ' ')
    text = ''.join(post.xpath('//*[@class="wall_post_text"]//text()'))
    post_summary['text'] = text
    post_summary['likes_count'] = get_value(
        post.xpath('//*[contains(@class,"like_cont ")]//*[@title="Нравится"]/*[@class="like_button_count"]/text()'))
    post_summary['share_count'] = get_value(
        post.xpath('//*[contains(@class,"like_cont ")]//*[@title="Поделиться"]/*[@class="like_button_count"]/text()'))
    try:
        post_summary['views'] = get_value(post.xpath('//*[contains(@class,"like_views _views")]')).text
    except Exception as e:
        print(e)
        post_summary['views'] = None
    try:
        photos = post.xpath('//*[contains(@aria-label,"фотография")]/@data-photo-id')
        photos_links = ['https://vk.com/photo' + photo for photo in photos]
    except Exception as e:
        print(e)
        photos_links = None
    post_summary['photos_links'] = photos_links
    return post_summary


def save_to_mongo(object):
    mongo_client = MongoClient(host='localhost', port=27017)
    db = mongo_client['vk_posts']
    db.get_collection('tokyofashion').update_one({'link': object['link']}, {'$set': object}, upsert=True)


if __name__ == '__main__':
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(URL)
    driver.refresh()
    find_posts(driver)
    scroll_page(driver)
    posts = driver.find_elements_by_xpath('//*[@class="_post_content"]')
    for elem in posts:
        post_summary = parse_post(elem)
        save_to_mongo(post_summary)
