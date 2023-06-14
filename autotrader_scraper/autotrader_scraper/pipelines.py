# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
import json


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

    def open_spider(self, spider):
        target_date = datetime.now() - timedelta(days = 3)
        spider.existing = []

        # JSON file read
        try:
            with open('autotrader.json', 'r') as autotrader_file:
                spider.cars = [car for car in json.load(autotrader_file) if car['lastUpdated'] < str(target_date.date())]
                print(spider.cars)
        except FileNotFoundError:
            spider.cars = []

    def process_item(self, item, spider):
        # Append to JSON file
        item['lastUpdated'] = str(item['lastUpdated'])
        for price in item['productDetails']['price']:
            price['date'] = str(price['date'])
        spider.cars.append(item)
        return item

    def close_spider(self, spider):
        # JSON file save
        with open('autotrader.json', 'w') as autotrader_file:
            json.dump(spider.cars, autotrader_file)
