import scrapy
from scrapy import Spider, Request
import re
import json
from collections import OrderedDict
from datetime import datetime
import re
import logging

from autotrader_scraper.database import *


class AutotraderSpider(Spider):
    name = 'autotrader'
    allowed_domains = ['autotrader.com.au']
    count = 0

    def start_requests(self):
        yield Request('https://script.google.com/macros/s/AKfycbymudzI8MqH0BhF2WmYpLIXhwUyjTiTDF-ygOeRlG32thVqvO6vzDc3nOlhWU2ZV5iA-A/exec', callback=self.parse_dealer_links)

    def make_request(self, page, dealer_id):
        return f'https://listings.platform.autotrader.com.au/api/v3/search?page={page}&dealer_id={dealer_id}&ipLookup=1&sorting_variation=smart_sort_2&paginate=13'

    def parse_dealer_links(self, response):
        dealer_list = response.json()
        for n, dealer in enumerate(dealer_list):
            dealer_id = re.search(r'dealerId=(\d+?)$', dealer.get('Url')).group(1)
            req_dealer = Request(self.make_request(1, dealer_id), callback=self.parse_dealer)
            req_dealer.meta['dealer_id'] = dealer_id
            req_dealer.meta['last'] = True if (n == len(dealer_list) - 1) else False
            yield req_dealer
        print(f'here we can call existing url: {self.old_unsold}')
        # for item in self.existing:
        #     url = item['url']
        #     print(url)
        #     yield Request(url, callback=self.parse_car2)

    def parse_dealer(self, response):
        car_data = response.json().get('data')

        for data in car_data:

            car_listing_id = data['_source']['id']
            x_list = [x['listingId'] for x in self.existing]

            if car_listing_id not in x_list:
                url = data['_source'].get('url')
                print(url)
                yield Request(f'https://www.{self.allowed_domains[0]}/{url}', callback=self.parse_car)
            else:
                print(len(self.old_unsold))

                for item in self.existing:
                    if item['listingId'] == car_listing_id:
                        self.old_unsold.append(item)
            #     dtm_now = datetime.now()
            #     item = list(filter(lambda item: item.get('listingId') == car_listing_id, self.existing))[0]
            #     new_price = data['_source']['price'].get('advertised_price')
            #     prev_price = int(item['price'])
            #     # prev_price = item['productDetails']['price'][-1]['value']
            #     if new_price != prev_price:
            #         item['productDetails']['price'].append({'date': dtm_now.date(), 'value': new_price})
            #         item['price'].append({'date': dtm_now.date(), 'value': new_price})
            #     item['lastUpdated'] = dtm_now
            #     yield item

        # go to the next page
        if car_data:
            page = response.meta.get('page', 1) + 1
            dealer_id = response.meta.get('dealer_id')
            req_dealer_page = Request(self.make_request(page, dealer_id), callback=self.parse_dealer)
            req_dealer_page.meta['page'] = page
            req_dealer_page.meta['dealer_id'] = dealer_id
            req_dealer_page.meta['last'] = response.meta['last']
            yield req_dealer_page

    def parse_car(self, response):
        try:
            url = response.url
            dl = dict()
            for di in response.xpath('//script[contains(text(), "dataLayer.push(")]/text()').re(r'dataLayer\.push\((.+?)\);'):
                dl.update(json.loads(di))

            schema = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').extract_first())
            dtm_now = datetime.now()
            item = OrderedDict()

            seller_location = {'Address': None, 'Dealer': None}
            product_details = {'Condition': None, 'Fuel type': None, 'Seller type': None, 'Vehicle Type': None,
                               'Engine': None, 'suburb': None, 'state': None, 'Dealer Name': None}
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

            specs['Exterior Color'], specs['Interior Color'] = tuple(
                x.strip() if x.strip() not in ('', '-') else None for x in
                re.split(r'\s/\s', specs.get('Colour ext / int', '/')))
            del specs['Colour ext / int']

            for key in ['year', 'make', 'model']:
                product_details[key] = dl['a']['attr'].get(key)

            product_details['price'] = [{'date': dtm_now.date(), 'value': dl['a']['attr'].get('price')}]

            product_details['title'] = schema['name']
            # product_details['kilometers'] = response.xpath('//body/*[contains(text(), "odometer:")]').re_first(r'odometer:(\d+),')

            dealer_details_text = response.xpath('//div/p/span[2]/text()').get()

            if dealer_details_text is not None:
                product_details['Dealer Licence'] = dealer_details_text.split(',')[0].strip()
                product_details['Dealer Name'] = dealer_details_text.split(',')[1].strip()
                product_details['suburb'] = dealer_details_text.split(',')[-2].strip()
                dealer_state = dealer_details_text.split(',')[-1].strip()
                product_details['state'] = dealer_state.split(' ')[-1].strip('.')

            vehicle_details_element = response.xpath('//div[contains(@class, "vehicleDetails--details")]').get()
            vehicle_details_text = scrapy.Selector(text=vehicle_details_element).css('.vehicleDetails--detail::text')
            product_details['kilometers'] = vehicle_details_text[0].get()
            product_details['Vehicle Type'] = vehicle_details_text[1].get()
            # seller_location_ = vehicle_details_text[5].get()
            # product_details['suburb'] = seller_location_.split(',')[-2].strip()
            # product_details['state'] = seller_location_.split(',')[-1].strip()
            product_details['Condition'] = dl.get('condition')
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
            item['isSold'] = True if dl.get('sold') == 1 else False
            item['soldDate'] = str(dtm_now.date()) if dl.get('sold') == 1 else None
            self.count += 1
            insert_autotrader(self.count, listingId= item['listingId'], title=product_details['title'], year=product_details["year"], price=product_details["price"][0]["value"],
                              kilometers=product_details["kilometers"], vehicle_type=product_details['Vehicle Type'],
                              gearbox=specs["Transmission"], fuel_type=specs["Fuel type"], seller_type=product_details["Seller type"],
                              condition=product_details["Condition"], suburb=product_details["suburb"], state=product_details["state"],
                              transmission=specs["Transmission"], body_type=specs["Body type"], drive_type=specs["Drive type"],
                              engine=product_details["Engine"], fuel_consumption=specs["Fuel consumption"], colour_ext=specs['Exterior Color'],
                              colour_int=specs['Interior Color'], registration=specs["Registration"], vin=specs["VIN"],
                              stock_no=specs["Stock No"], dealer=product_details['Dealer Name'], make=general["Make"],
                              model=general["Model"], variant=general["Variant"], serie=general["Series"],
                              is_sold=item['isSold'], sold_date=item['soldDate'], url=url)
            return item

        except Exception as e:
            print(e)
            logging.error(e)
            item = list(filter(lambda item: item.get('url') == response.url, self.existing))[0]
            if item:
                return item

    def parse_car2(self, response):
        try:
            url = response.url
            dl = dict()
            for di in response.xpath('//script[contains(text(), "dataLayer.push(")]/text()').re(r'dataLayer\.push\((.+?)\);'):
                dl.update(json.loads(di))

            schema = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').extract_first())
            dtm_now = datetime.now()
            item = OrderedDict()

            seller_location = {'Address': None, 'Dealer': None}
            product_details = {'Condition': None, 'Fuel type': None, 'Seller type': None, 'Vehicle Type': None,
                               'Engine': None, 'suburb': None, 'state': None, 'Dealer Name': None}
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

            specs['Exterior Color'], specs['Interior Color'] = tuple(
                x.strip() if x.strip() not in ('', '-') else None for x in
                re.split(r'\s/\s', specs.get('Colour ext / int', '/')))
            del specs['Colour ext / int']

            for key in ['year', 'make', 'model']:
                product_details[key] = dl['a']['attr'].get(key)

            product_details['price'] = [{'date': dtm_now.date(), 'value': dl['a']['attr'].get('price')}]

            product_details['title'] = schema['name']
            # product_details['kilometers'] = response.xpath('//body/*[contains(text(), "odometer:")]').re_first(r'odometer:(\d+),')

            dealer_details_text = response.xpath('//div/p/span[2]/text()').get()

            if dealer_details_text is not None:
                product_details['Dealer Licence'] = dealer_details_text.split(',')[0].strip()
                product_details['Dealer Name'] = dealer_details_text.split(',')[1].strip()
                product_details['suburb'] = dealer_details_text.split(',')[-2].strip()
                dealer_state = dealer_details_text.split(',')[-1].strip()
                product_details['state'] = dealer_state.split(' ')[-1].strip('.')

            vehicle_details_element = response.xpath('//div[contains(@class, "vehicleDetails--details")]').get()
            vehicle_details_text = scrapy.Selector(text=vehicle_details_element).css('.vehicleDetails--detail::text')
            product_details['kilometers'] = vehicle_details_text[0].get()
            product_details['Vehicle Type'] = vehicle_details_text[1].get()
            # seller_location_ = vehicle_details_text[5].get()
            # product_details['suburb'] = seller_location_.split(',')[-2].strip()
            # product_details['state'] = seller_location_.split(',')[-1].strip()
            product_details['Condition'] = dl.get('condition')
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
            item['isSold'] = True if dl.get('sold') == 1 else False
            item['soldDate'] = str(dtm_now.date()) if dl.get('sold') == 1 else None
            self.count += 1
            update_sold(self.count, item['listingId'], is_sold=item['isSold'])
            return item

        except Exception as e:
            print(e)
            logging.error(e)
            item = list(filter(lambda item: item.get('url') == response.url, self.existing))[0]
            if item:
                return item
