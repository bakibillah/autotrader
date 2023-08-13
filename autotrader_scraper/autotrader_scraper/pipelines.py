# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
import json
import os
import logging


class AutotraderScraperMongoPipeline:

    def open_spider(self, spider):
        target_date = datetime.now() - timedelta(days = 3)
        self.client = pymongo.MongoClient("mongodb+srv://production:F6WockUSJ68LWkqN@cluster0.glugo.mongodb.net/test?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
        db = self.client.autotrader
        spider.cars = db['cars']
        spider.existing = [x['listingId'] for x in spider.cars.find({"lastUpdated": {"$lt": target_date}})]

    def process_item(self, item, spider):
        spider.cars.update({"_id": item['listingId']}, {"$set" : dict(item)}, upsert=True)
        return item

    def close_spider(self, spider):
        self.client.close()


class AutotraderScraperFilePipeline:

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        path = settings.get("OUT_FILE_PATH")
        return cls(path)

    def __init__(self, path):
        self.path = path

    def open_spider(self, spider):
        target_date = datetime.now() - timedelta(days = 3)

        # JSON file read
        try:
            with open(os.path.join(self.path, 'autotrader.json'), 'r') as autotrader_file:
                loaded_cars = json.load(autotrader_file)
                spider.existing = [car for car in loaded_cars if (car['lastUpdated'] > str(target_date.date()))]
                spider.all_carsdict = {car['listingId']: car for car in loaded_cars}
                logging.debug(f'{len(spider.existing)} cars exist in the file')

        except FileNotFoundError:
            spider.existing = []
            spider.all_carsdict = {}

    def process_item(self, item, spider):
        # Append to JSON file
        item['lastUpdated'] = str(item['lastUpdated'])
        for price in item['productDetails']['price']:
            price['date'] = str(price['date'])
        spider.all_carsdict[item['listingId']] = item
        return item

    def close_spider(self, spider):
        # JSON file save
        with open(os.path.join(self.path, 'autotrader.json'), 'w') as autotrader_file:
            json.dump(list(spider.all_carsdict.values()), autotrader_file, indent=4)
