from scrapy import Spider, Request
import re
import json
from collections import OrderedDict
from datetime import datetime
import re


class AutotraderSpider(Spider):
    name = 'autotrader'
    allowed_domains = ['autotrader.com.au']

    def start_requests(self):
        yield Request(
            'https://script.google.com/macros/s/AKfycbymudzI8MqH0BhF2WmYpLIXhwUyjTiTDF-ygOeRlG32thVqvO6vzDc3nOlhWU2ZV5iA-A/exec',
            callback=self.parse_dealer_links
        )


    def make_request(self, page, dealer_id):
        # function to generate request URL based on the page number (1-based) and dealer id
        return f'https://listings.platform.autotrader.com.au/api/v3/search?page={page}&dealer_id={dealer_id}&ipLookup=1&sorting_variation=smart_sort_2&paginate=13'
        

    def parse_dealer_links(self, response):
        for dealer in response.json():
            dealer_id = re.search(r'dealerId=(\d+?)$', dealer.get('Url')).group(1)
            req_dealer = Request(self.make_request(1, dealer_id), callback=self.parse_dealer)
            req_dealer.meta['dealer_id'] = dealer_id
            yield req_dealer


    def parse_dealer(self, response):
        car_data = response.json().get('data')
        for data in car_data:
            if data['_source']['id'] not in [x['listingId'] for x in self.existing]:
                url = data['_source'].get('url')
                yield Request(f'https://www.{self.allowed_domains[0]}/{url}', callback=self.parse_car)
            else:
                dtm_now = datetime.now()
                item = [e for e in self.existing if e['listingId'] == data['_source']['id']][0]
                new_price = data['_source']['price'].get('advertised_price')
                prev_price = item['productDetails']['price'][-1]['value']
                if new_price != prev_price:
                    item['productDetails']['price'].append({'date': dtm_now.date(), 'value': new_price})
                item['lastUpdated'] = dtm_now
                yield item

        # going to the next page
        if car_data:
            page = response.meta.get('page', 1) + 1
            dealer_id = response.meta.get('dealer_id')
            req_dealer_page = Request(self.make_request(page, dealer_id), callback=self.parse_dealer)
            req_dealer_page.meta['page'] = page
            req_dealer_page.meta['dealer_id'] = dealer_id
            yield req_dealer_page


    def parse_car(self, response):

        dl = dict()
        for di in response.xpath('//script[contains(text(), "dataLayer.push(")]/text()').re(r'dataLayer\.push\((.+?)\);'):
            dl.update(json.loads(di))

        schema = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').extract_first())
        dtm_now = datetime.now()
        item = OrderedDict()


        seller_location = {'Address': None, 'Dealer': None}
        product_details = {'Condition': None, 'Fuel type': None, 'Seller type': None}
        specs = {'Transmission': None, 'Body type': None, 'Drive type': None, 'Fuel type': None,
                 'Fuel consumption': None, 'Colour ext / int': None, 'Registration': None, 'Rego expiry': None,
                           'VIN': None, 'Stock No': None}
        comfort = {'Seating capacity': None}
        exterior_body_features = {'Doors': None, 'Front tyre size': None, 'Front rim size': None,
         'Rear tyre size': None, 'Rear rim size': None}
        performance = {
            'Injection / Carburation': None, 
            'CC': None,
            'Number of cylinders': None,
            'Front suspension': [],
            'Rear suspension': [],
            'Front brakes': None,
            'Rear brakes': None,
            'Fuel type': None,
            'Fuel tank capacity': None,
            'Fuel consumption': None,
            'Valve gear type': None,
            'Maximum torque': None,
            'Maximum power (kW)': None,
            'CO2 level (g/km)': None,
            'ANCAP Safety rating': None,
            'Green overall rating': None,
            'Green house rating': None
        }
        dimensions = {
            'Overall HxWxL': None,
            'Ground clearance unladen': None,
            'Wheelbase': None,
            'Kerb weight': None,
            'Turning circle': None,
            'Rear track': None,
            'Front track': None,
            'Gross trailer weight braked': None
        }
        general = {
            'Make': None,
            'Model': None,
            'Variant': None,
            'Series': None,
            'Warranty when new (months)': None,
            'Warranty when new (kms)': None,
            'Service interval (months)': None,
            'Service interval (kms)': None,
            'Country of origin': None,
            'Vehicle segment': None
        }


        for dict_in in [seller_location, product_details, specs, comfort, exterior_body_features, performance, dimensions, general]:
            for key in dict_in.keys():
                if key not in ['Green overall rating', 'ANCAP Safety rating', 'Green house rating']:
                    value = ' '.join(response.xpath(f'//tr/td[1][contains(text(), "{key}")]/../td[2]/text()').extract_first('').split())
                    value = value if dict_in[key] is None else value.split(';')
                    if value in ['', '-']:
                        value = None
                    elif value in [[''], ['-']]:
                        value = []
                    dict_in[key] = value
                else:
                    trs = response.xpath(f'//td[contains(text(), "{key}")]/..')
                    dict_in[key] = len(trs[0].xpath('./td[2]//*[contains(@class, "-full svgIcon")]/@class').extract())

        print( specs.get('Colour ext / int', '/')) 
        specs['Exterior Color'], specs['Interior Color'] = tuple(x.strip() if x.strip() not in ('', '-') else None for x in re.split(r'\s/\s', specs.get('Colour ext / int', '/')))
        del specs['Colour ext / int']

        for key in ['year', 'make', 'model']:
            product_details[key] = dl['a']['attr'].get(key)
        

        product_details['price'] = [{'date': dtm_now.date(), 'value': dl['a']['attr'].get('price')}]

        product_details['title'] = schema['name']
        product_details['kilometers'] = response.xpath('//body/*[contains(text(), "odometer:")]').re_first(r'odometer:(\d+),')
        product_details['condition'] = dl.get('condition')
        product_details['suburb'] = seller_location['Address'].split(',')[-2].strip()
        product_details['state'] = seller_location['Address'].split(',')[-1].strip()

        item['listingId'] = dl.get('listing_id')
        item['url'] = response.url
        item['lastUpdated'] = dtm_now
        item['productDetails'] = product_details
        item['specs'] = specs
        item['sellerLocation'] = seller_location
        item['exteriorBodyFeatures'] = exterior_body_features
        item['comfort'] = comfort
        item['performance'] = performance
        item['dimensions'] = dimensions
        item['general'] = general

        return item
