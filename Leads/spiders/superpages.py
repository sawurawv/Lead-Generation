# -*- coding: utf-8 -*-
import csv
import datetime
import json
import re

import pandas as pd
import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse
from Leads.items import LeadsItem
from Leads.spiders import BaseSpider
import urllib.parse


class SuperpagesSpider(BaseSpider):
    name = 'superpages'
    use_proxy = True
    custom_settings = {
        'CONCURRENT_REQUESTS': 256,
        # 'DOWNLOAD_DELAY': 0.25
    }
    allowed_domains = ['superpages.com']
    # base_url = 'https://www.superpages.com/listings.jsp?&STYPE=S&C=physical%20therapy%20clinic%20{location}'
    base_url = 'https://www.superpages.com/listings.jsp?CS=L&search=Find%20It&C={keyword}%20in%20{zipcode}'

    def __init__(self, keyword='physical therapy clinic',
                 file='us_zip_state.csv', zip_code=10001, **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.file = file
        self.zip_code = zip_code

    def start_requests(self):
        with open('us_zip_state.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                zip_code = row['zipcode']
                for keyword in self.keywords:
                    yield Request(self.base_url.format(keyword=keyword, zipcode=zip_code),
                              meta={'keyword': keyword})

    def parse(self, response):
        item = LeadsItem()
        try:
            dr = re.findall('<script type="application/ld\+json">(.*?)</script>', response.text)[0]
            dr = json.loads(dr)
        except:
            dr = []
        for row in dr:
            url = row.get('url')
            # sometimes the urls come concatenated
            if url.startswith('https://www.superpages.com') and not url.startswith('https://www.superpages.com/'):
                url = url.replace('https://www.superpages.com', '', 1)
            item['directory_business_link'] = url
            item['phone'] = row.get('telephone')
            item['business_name'] = row.get('name')
            item['website'] = response.xpath(
                '//a[text()="' + item[
                    'business_name'] + '"]/../../../div[contains(@class, "web-addr")]/a/strong/text()').extract_first()
            address = row.get('address', {})
            item['zip_code'] = address.get('postalCode')
            item['state'] = address.get('addressRegion', '').upper()
            item['city'] = address.get('addressLocality', '').title()
            item['street_address'] = address.get('streetAddress')
            item['directory'] = self.allowed_domains[0]
            item['keyword'] = response.meta.get('keyword')
            yield item

        next_page = response.urljoin(
            response.xpath('//div[contains(@class, "pagebuttons")]/a[text()="Next"]/@href').extract_first())
        if next_page:
            yield Request(next_page, meta={'keyword': response.meta.get('keyword')})
