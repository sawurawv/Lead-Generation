# -*- coding: utf-8 -*-
import re

import pandas as pd
import scrapy
from scrapy import Request



class YpSpider(scrapy.Spider):
    name = 'yp'
    use_proxy = True
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['crawled_date', 'name', 'link', 'phone', 'street_address',
                               'city', 'state', 'zipcode', 'website', 'source'],
        'CONCURRENT_REQUESTS': 256,
        # 'DOWNLOAD_DELAY': 0.25
    }
    allowed_domains = ['yellowpages.com']
    base_url = 'https://www.yellowpages.com/search?search_terms={}&geo_location_terms={}'

    def __init__(self, keyword='physical therapy clinic',
                 file='us_cities.csv', state='WA', **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.file = file
        self.state = state

    def start_requests(self):
        keywords = ['Taxi', 'Cab', 'chauffeur', 'limo', 'shuttle', 'town car', 'Janitorial', 'Cleaning',
                    'Paving Services', 'Asphalt Services', 'Airport Shuttle Service', 'Town Car Service',
                    'Handyman Services', 'Awning Services', 'Psychic Reading', 'Hair Braiding Services', 'Salon', 'Spa',
                    'Movers', 'Home Remodeling', 'Kitchen Cabinets', 'Cabinets', ' Upholstery',
                    ' Carpet Cleaning Services', ' Window Tinting Services', 'Painting Services', 'Pool Services',
                    'Soda Blasting Services', 'Pressure Washer Services', 'Roofing', 'Tavern', 'Junk Removal',
                    'Takeaway', 'Day Care', 'Church', 'Tree Services', 'Tree Stumping Services', 'Landscape',
                    'Cell Phone Repair', 'Pet Care', 'Motel', 'Driving School', 'Cabinetry', 'Furniture', 'Kid store',
                    'Toy store', 'Pawn Brokers', 'Jewelry', 'Painting', 'Dental labs', 'Flower Shop', 'Garage Doors',
                    'Barber Shop', 'Meat shop', 'Electrical', 'Locksmith', 'Signs', 'Heating', 'Cooling',
                    'Messenger Service', 'Towing', 'Martial Arts', 'Takwondo', 'Travel', 'Tour', 'Lodge',
                    'Plumbing Services', 'Professional Coating', 'Flooring', 'Gutters', 'Collision', 'Collision',
                    'Paint', 'Transportation', 'Taxi', 'Cab Services', 'Taxidermy', 'Masonry', 'Home Improvement',
                    'Windows', 'Doors', 'Driveways', 'Sailing', 'Chimney Sweep', 'Catering', 'Party Planner',
                    'Home Daycare Provider', 'Vintage Clothing Reseller', 'Party Clown', 'Dance Instructor', 'Musician',
                    'Personal Trainer', 'Music Teacher', 'Jewelry Maker', 'Hot Air Balloon Operator',
                    'Massage Therapist', 'Hair Stylist', 'Interior Designer', 'Home Staging Professional',
                    'Dog Groomer', 'Dog Trainer', 'Pet Sitter', 'Personal Stylist', 'Photographer', 'Photography',
                    'Gift Basket Arranger', 'Furniture Upcycler', 'Bicycle Repair Professional', 'Baker', 'Jam Seller',
                    'Caterer', 'Florist', 'Landscape Designer']
        df = pd.read_csv(self.file)
        for index, row in list(df.iterrows()):
            # if row['state_id'] == self.state:
                self.location = '{}, {}'.format(row['city'], row['code'])
                for keyword in keywords:
                    url = self.base_url.format(keyword.strip(), self.location)
                    yield Request(url, meta={'city': row['city'], 'state': row['code'], 'kw':keyword})

    def parse(self, response):
        city = response.meta.get('city')
        state = response.meta.get('state')
        # if not city and not state:
        #     city, state = map(str.strip, self.location.split(','))
        for company in response.css('div.search-results.organic div.v-card'):
            item = {}
            item['link'] = response.urljoin(company.css('a.business-name::attr(href)').extract_first())
            item['name'] = company.css('a.business-name span ::text').extract_first()
            item['phone number'] = company.css('div.phones ::text').extract_first()
            item['street address'] = company.css('p.adr span.street-address::text').extract_first()
            item['city'] = (company.css('p.adr span.locality::text').extract_first() or '').strip().strip(',')
            item['Directory Link'] = self.allowed_domains[0]
            try:
                state = company.css('p.adr span::text').extract()[-2]
                item['state'] = state
            except:
                item['state'] = ''
            try:
                zipcode = company.css('p.adr span::text').extract()[-1]
                item['zipcode'] = zipcode if re.match('\d+', zipcode) else ''
            except:
                item['zipcode'] = ''
            item['website'] = company.css('a.track-visit-website ::attr(href)').extract_first()
            if item['website'] and item['state'] == state and item['city'] == city:
                if not item['website'].startswith('http'):
                    item['website'] = 'http://' + item['website']
                yield item

        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page:
            yield Request(response.urljoin(next_page), meta={'city': city, 'state': state})
