# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import sqlite3
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SqlitePipeline(object):
    def open_spider(self, spider):
        self.conn = sqlite3.connect('Leads.db')
        self.cursor = self.conn.cursor()

        create_source_table = 'CREATE TABLE IF NOT EXISTS data (' \
                              'business_name VARCHAR(255),' \
                              'owner VARCHAR(255),' \
                              'phone VARCHAR(255),' \
                              'email VARCHAR(255),' \
                              'website VARCHAR(255),' \
                              'state VARCHAR(255),' \
                              'address VARCHAR (255),' \
                              'zip_code VARCHAR (32),' \
                              'directory VARCHAR (255),' \
                              'directory_business_link VARCHAR (255),'\
                              'keyword VARCHAR (255))'
        self.cursor.execute(create_source_table)
        self.conn.commit()

    @staticmethod
    def clean_phone(phone):
        if not isinstance(phone, str):
            return ''

        cleaned_phone = phone.strip()
        if cleaned_phone.startswith('+1'):
            cleaned_phone = cleaned_phone.strip('+1')

        cleaned_phone = re.sub('[^\d]', '', cleaned_phone)
        return cleaned_phone

    @staticmethod
    def clean_website(website):
        if not isinstance(website, str):
            return ''
        return urlparse(website.strip()).netloc.strip('www.')

    def process_item(self, item, spider):
        table_name = 'data'

        # replace all \xa0 with space and strip text
        for key in item:
            if isinstance(item[key], str):
                item[key] = item[key].replace('\xa0', ' ').strip()

        item['phone'] = self.clean_phone(item.get('phone', ''))

        if 'website' in item:
            if isinstance(item['website'], (set, list)):
                cleaned_website_list = set()
                for website in item['website']:
                    cleaned_website = self.clean_website(website)
                    cleaned_website_list.add(cleaned_website)
                item['website'] = ','.join(cleaned_website_list)
            elif isinstance(item['website'], str):
                item['website'] = self.clean_website(item['website'])

        # insert into db
        try:
            placeholder = ', '.join(["?"] * len(item))
            statement = 'INSERT OR REPLACE INTO {table} ({columns}) VALUES ({values})'.format(
                table=table_name, columns=','.join(item.keys()), values=placeholder)

            logger.info('Item: {} inserted to {}'.format(item, table_name))
            self.cursor.execute(statement, list(item.values()))
            self.conn.commit()
        except Exception as e:
            logger.error('Error {}'.format(e))
        return item

    def close(self, spider):
        self.cursor.close()
        self.conn.close()
