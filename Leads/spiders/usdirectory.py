# -*- coding: utf-8 -*-
from scrapy import Request

from Leads.spiders import BaseSpider


class UsdirectorySpider(BaseSpider):
    name = 'usdirectory'
    allowed_domains = ['usdirectory.com']
    search_url = 'https://usdirectory.com/Site/BusinessesResult?search=true&searchText={keyword}&location={state}%2C%20USA&latitude={latitude}&longitude={longitude}&radius=200'

    def __init__(self, keyword='physical therapy clinic', state='WA', **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.state = state

    def start_requests(self):
        for keyword in self.keywords:
            for state in self.states:
                state_name = self.states[state]['name']
                long = self.states[state]['long']
                lat = self.states[state]['lat']
                yield Request(self.search_url.format(keyword=keyword, state=state_name, latitude=lat, longitude=long), meta={'kw': keyword})

    def parse(self, response):
        keyword = response.meta.get('kw')
        for links in response.css('h4.businessTitle>a'):
            link = response.urljoin(links.css('::attr(href)').get())
            yield Request(link, callback=self.parse_detail, meta={'kw': keyword})

        next_page =response.css('li.PagedList-skipToNext>a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse, meta={'kw': keyword})

    def parse_detail(self,response):
        item = {}
        item['business_name'] = response.css('h1.busName>div#businessNameAndInfo::text').get()
        item['owner'] = ''
        item['phone'] = response.css('a.callMerchant span::text').get()
        item['email'] = response.css('div.publicMailHolder>a::text').get()
        item['website'] = response.css('div.linksHolder>a.webLink::attr(href)').get()
        item['state'] = response.css('div.addressHolder>a::text').get().split(',')[-2].strip()
        item['address'] = response.css('div.addressHolder>a::text').get()
        item['zip Code'] = response.css('div.addressHolder>a::text').get().split(',')[-1].strip()
        item['Directory Link'] = self.allowed_domains[0]
        item['keyword'] = response.meta.get('kw', '')
        yield item