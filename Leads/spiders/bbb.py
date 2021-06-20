# -*- coding: utf-8 -*-
import csv
import json

from scrapy import Request
from scrapy.utils.response import open_in_browser

from Leads.items import LeadsItem
from Leads.spiders import BaseSpider


class BbbSpider(BaseSpider):
    name = 'bbb'
    allowed_domains = ['bbb.org']
    search_url = 'https://www.bbb.org/search?find_country=USA&find_loc={city}%2C%20{state}&find_text={keyword}&page=1&sort=Relevance'

    def __init__(self, keyword, state, city, file='us_cities.csv', **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.file = file
        self.state = state
        self.city = city

    def start_requests(self):
        with open('us_cities.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            if self.city and self.state:
                yield Request(self.search_url.format(keyword=self.keyword, state=self.state, city=self.city),
                              meta={'kw': self.keyword})
            else:
                for row in csv_reader:
                    city = row['city']
                    state = row['code']
                    # if keyword is provided by -a
                    if self.keyword:
                        keyword = self.keyword
                        yield Request(self.search_url.format(keyword=keyword, state=state, city=city),
                                      meta={'kw': keyword})
                    else:
                        for keyword in self.keywords:
                            yield Request(self.search_url.format(keyword=keyword, state=state, city=city),
                                          meta={'kw': keyword})

    def parse(self, response):
        keyword = response.meta.get('kw')
        for links in response.css('div.MuiPaper-root h3.MuiTypography-root>a'):
            link = response.urljoin(links.css('::attr(href)').get())
            yield Request(link, callback=self.parse_detail, meta={'kw': keyword})

        next_page = response.css('section.dtm-search-pagination a.Next-sc-1kq0k7j-0::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse, meta={'kw': keyword})

    def parse_detail(self, response):
        item = LeadsItem()
        item['business_name'] = response.css('div.MuiGrid-root>h4::text').get()
        json_data = json.loads(response.css('script[type="application/ld+json"]::text').get().strip().strip(';'))
        owner_kw = ['owner', 'president', 'founder', 'manager']
        if 'employee' in json_data:
            for emp in json_data['employee']:
                for kw in owner_kw:
                    if kw in emp.get('jobTitle', '').lower():
                        item['owner'] = '{}{}{},{}'.format(emp.get('honorificPrefix'), emp.get('givenName'), emp.get(
                            'familyName'), emp.get('jobTitle'))
        item['phone'] = response.css('a.dtm-phone::text').get()
        item['email'] = ''

        websites = {response.urljoin(response.css('a.femZSp::attr(href)').get(''))}
        for website in response.css('a.dtm-url::attr(href)').extract():
            if website:
                websites.add(response.urljoin(website))

        item['website'] = websites
        item['state'] = response.css('div.dtm-address p.MuiTypography-root::text').extract()[-3].strip()
        item['address'] = response.css('div.dtm-address p.MuiTypography-root::text').get()
        item['zip_code'] = response.css('div.dtm-address p.MuiTypography-root::text').extract()[-1].strip()
        item['directory'] = self.allowed_domains[0]
        item['directory_business_link'] = response.url.split('?', 1)[0]
        item['keyword'] = response.meta.get('kw', '')
        yield item
