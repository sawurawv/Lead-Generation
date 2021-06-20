# # -*- coding: utf-8 -*-
# import datetime
# import json
# from urllib.parse import unquote
#
# import pandas as pd
# import scrapy
# from scrapy import Request
#
# from YpLead.utils import set_proxy
#
#
# class YelpSpider(scrapy.Spider):
#     name = 'yelp'
#     use_proxy = False
#     custom_settings = {
#         'FEED_EXPORT_FIELDS': ['crawled_date', 'name', 'link', 'phone', 'street_address',
#                                'city', 'state', 'zipcode', 'website', 'source'],
#         'CONCURRENT_REQUESTS': 2,
#         'DOWNLOAD_DELAY': 10,
#         'AUTOTHROTTLE_ENABLED': True,
#         'AUTOTHROTTLE_START_DELAY': 10,
#         'AUTOTHROTTLE_MAX_DELAY': 200,
#         'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
#         'AUTOTHROTTLE_DEBUG': True
#     }
#     allowed_domains = ['yelp.com']
#     base_url = 'https://www.yelp.com/search?find_desc=physical+therapy+clinic&find_loc={location}&ns=1'
#
#     def __init__(self, file='city list.xlsx', state='WA', **kwargs):
#         super().__init__(**kwargs)
#         self.file = file
#         self.state = state
#
#     def start_requests(self):
#         df = pd.read_excel(self.file)
#         for index, row in list(df.iterrows()):
#             if row['state_id'] == self.state:
#                 location = '{}, {}'.format(row['city'], row['state_id'])
#                 url = self.base_url.format(location=location)
#                 yield set_proxy(Request(url, meta={'city': row['city'], 'state': row['state_id']}), self.use_proxy)
#
#     def parse(self, response):
#         for link in response.css('h3 a::attr(href)').extract():
#             link = link.rsplit('?', 1)[0]
#             yield set_proxy(Request(response.urljoin(link), callback=self.parse_detail))
#
#         next_page = response.css('a.next-link ::attr(href)').extract_first()
#         if next_page:
#             yield set_proxy(Request(response.urljoin(next_page)))
#
#     def parse_detail(self, response):
#         url = response.css('span.biz-website ::attr(href)').extract_first()
#         if url:
#             item = {}
#             item['crawled_date'] = datetime.date.today().strftime('%Y-%m-%d')
#             item['name'] = response.css('h1.biz-page-title ::text').extract_first().strip()
#             item['link'] = response.url.rsplit('?', 1)[0]
#             item['phone'] = (response.css('span.biz-phone ::text').extract_first() or '').strip()
#             json_data = json.loads(response.css('script[type="application/ld+json"] ::text').extract()[-1])
#             address = json_data.get('address', {})
#             item['street_address'] = address.get('streetAddress', '').replace('\n', ' ')
#             item['zipcode'] = address.get('postalCode')
#             item['city'] = address.get('addressLocality')
#             item['state'] = address.get('addressRegion')
#             item['source'] = self.allowed_domains[0]
#             item['website'] = unquote(url.split('?url=')[1].split('&')[0])
#             yield item
