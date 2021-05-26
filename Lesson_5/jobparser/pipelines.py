# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
# в вашем случае
MONGO_URL = "localhost:27017"
# если нестандартный порт
#MONGO_URL = "localhost:27019"


class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client['vacancy']

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            if item['salary'][2] == ' до ':
                item['salary_min'] = item['salary'][1]
                item['salary_max'] = item['salary'][3]
                item['salary_currency'] = item['salary'][5]
            if item['salary'][0] == 'от ':
                item['salary_min'] = item['salary'][1]
                item['salary_max'] = None
                item['salary_currency'] = item['salary'][3]
            if item['salary'][0] == 'до ':
                item['salary_min'] = None
                item['salary_max'] = item['salary'][1]
                item['salary_currency'] = item['salary'][3]
            if item['salary'][0] == 'з/п не указана':
                item['salary_min'] = None
                item['salary_max'] = None
                item['salary_currency'] = None

        if spider.name == 'sjru':
            item['salary_min'] = None
            item['salary_max'] = None
            item['salary_currency'] = None
            if item['salary']:
                if item['salary'][0] == 'от':
                    num = str(item['salary'][2])
                    item['salary_min'] = num[:-4]
                    item['salary_currency'] = num[-4:]
                if item['salary'][0] == 'до':
                    num = str(item['salary'][2])
                    item['salary_max'] = num[:-4]
                    item['salary_currency'] = num[-4:]
                if item['salary'][2] == 'руб.':
                    item['salary_min'] = item['salary'][0]
                    item['salary_currency'] = item['salary'][2]
                if item['salary'][0] == 'По договорённости':
                    item['salary_min'] = None
                    item['salary_max'] = None
                    item['salary_currency'] = None
                if len(item['salary']) > 5:
                    item['salary_min'] = item['salary'][0]
                    item['salary_max'] = item['salary'][3]
                    item['salary_currency'] = item['salary'][4]

        #print(item)
            del item['salary']
        collection = self.db[spider.name]
        collection.update_one(item, {"$set": item}, upsert=True)
        return item
