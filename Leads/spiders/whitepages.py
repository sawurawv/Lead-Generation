# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from Leads.spiders import BaseSpider


class WhitepagesSpider(BaseSpider):
    name = 'whitepages'
    allowed_domains = ['whitepages.com']
    search_urls = ['https://www.whitepages.com/business/{state}/{keyword}']


    def start_requests(self):
        for keyword in self.keywords:
            for state in self.states:
                yield Request(self.search_url.format(keyword=keyword, state=self.states[state]))

    def parse(self, response):
        pass
