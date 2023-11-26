# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime, timedelta
import json
import os
import logging
import pymongo
import requests
from collections import OrderedDict
from autotrader_scraper.database import *
import re
import scrapy
from lxml import html
from scrapy import Spider, Request


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
            spider.old_unsold = []
            loaded_cars = get_all_carsdata()
            # loaded_cars = json.load(autotrader_file)
            spider.existing = [car for car in loaded_cars]
            spider.all_carsdict = {car['listingId']: car for car in loaded_cars}
            logging.debug(f'{len(spider.existing)} cars exist in the file')
        except FileNotFoundError:
            spider.existing = []
            spider.all_carsdict = {}

    def process_item(self, item, spider):
        # Append to JSON file
        item['lastUpdated'] = str(item['lastUpdated'])
        # for price in item['productDetails']['price']:
        #     price['date'] = str(price['date'])
        spider.all_carsdict[item['listingId']] = item
        return item

    def close_spider(self, spider):
        print('close')
        proxies = {
            'http': '127.0.0.1:8080',
            'https': '127.0.0.1:8080',
        }
        session = requests.session()
        session.proxies = proxies
        result = [item for item in spider.existing if item not in spider.old_unsold]
        count = 0
        for data in result:
            count += 1
            url = data['url']
            listingId = data['listingId']
            burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"117\", \"Not;A=Brand\";v=\"8\"", "Sec-Ch-Ua-Mobile": "?0",
                             "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36",
                             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                             "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1",
                             "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate, br",
                             "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}
            res = session.get(url, headers=burp0_headers, proxies=proxies)
            parsed_html = html.fromstring(res.content)
            paragraphs = parsed_html.xpath('//script[contains(text(), "dataLayer.push(")]/text()')
            match = re.search(r'dataLayer\.push\((.+?)\);', paragraphs[0]).group(1)
            json_data = json.loads(match)
            is_sold = json_data['sold']
            update_sold(count, listingId, is_sold)
