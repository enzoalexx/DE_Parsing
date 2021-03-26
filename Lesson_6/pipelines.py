# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from PIL import Image
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

MONGO_URL = "localhost:27017"


class LmparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client['leroymerlin']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.update_one(item, {"$set": item}, upsert=True)
        return item


class LmparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo_url in item['photos']:
                try:
                    yield scrapy.Request(photo_url, meta={'title': item['title']})
                except Exception as e:
                    print(e)

    #def file_path(self, request, response, info, *, item):
        #item_title = request.meta['title']
        #return f'{item_title}/{ImagesPipeline.file_path(self, request, response, info)}'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
