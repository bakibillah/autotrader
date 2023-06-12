# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta


class AutotraderScraperPipeline:

    def open_spider(self, spider):
        target_date = datetime.now() - timedelta(days = 3)
        spider.existing = []
        # self.client = pymongo.MongoClient("mongodb+srv://production:F6WockUSJ68LWkqN@cluster0.glugo.mongodb.net/test?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
        # db = self.client.autotrader
        # spider.cars = db['cars']
        # spider.existing = [x['listingId'] for x in spider.cars.find({"lastUpdated": {"$lt": target_date}})]

    # def process_item(self, item, spider):

    #     spider.cars.update({"_id": item['listingId']}, {"$set" : dict(item)}, upsert=True)
    #     return item

    # def close_spider(self, spider):
    #     self.client.close()


    def process_item(self, item, spider):
        return item
