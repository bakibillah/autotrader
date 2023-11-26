import json

import requests
from bs4 import BeautifulSoup
from lxml import html
import re


session = requests.session()
proxies = {
    'http': '127.0.0.1:8080',
    'https': '127.0.0.1:8080',
}
all_listing = []
for index in range(13):
    index += 1
    burp0_url = f"https://listings.platform.autotrader.com.au/api/v3/search?page={index}&dealer_id=12751&ipLookup=1&sorting_variation=smart_sort_2&paginate=13"
    burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"117\", \"Not;A=Brand\";v=\"8\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Linux\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9", "Connection": "close"}
    res = session.get(burp0_url, headers=burp0_headers)
    data = res.json()
    for item in data['data']:
        listing_id = item['_source']['id']
        all_listing.append(listing_id)

print(len(all_listing))
print(len(set(all_listing)))
print(set(all_listing))


