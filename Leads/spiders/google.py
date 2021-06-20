# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class GoogleSpider(scrapy.Spider):
    name = 'google'
    allowed_domains = ['google.com']
    search_urls = 'https://www.google.com/search?q={business_name}+{address}'

    def start_requests(self):
        business_name = 'Brooklyn Burgers & Beer'
        address = '259 5th Ave 11215'
        yield Request(f'https://www.google.com/search?q={business_name} {address}')

    def parse(self, response):
        item = {}
        item['Business Name'] = response.css('div.kno-ecr-pt>span::text').get()
        item['Rating'] = response.css('span.rtng::text').get()
        item['Address'] = response.css('span.LrzXr::text').get()
        item['Street'] = response.css('span.LrzXr::text').get().split(',')[0]
        item['City'] = response.css('span.LrzXr::text').get().split(',')[1]
        item['State'] = response.css('span.LrzXr::text').get().split(',')[-1].split()[0]
        item['Zip Code'] = response.css('span.LrzXr::text').get().split(',')[-1].split()[-1]
        item['Website'] = response.css('div.QqG1Sd>a::attr(href)').get()
        item['Phone'] = response.css('span.zdqRlf>span>span::text').get()
        yield item