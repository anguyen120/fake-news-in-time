# -*- coding: utf-8 -*-
import heapq
import re
from itertools import count

import scrapy
from archive.items import ArchiveItem
from pymongo import MongoClient
from scrapy.linkextractors import LinkExtractor


class CdxSpider(scrapy.Spider):
    name = 'cdx'
    allowed_domains = ['web.archive.org']

    CLIENT = MongoClient()
    DATABASE = CLIENT.data
    URLS = DATABASE.urls

    REAL_LIST = 'real.txt'
    FAKE_LIST = 'fake.txt'

    def start_requests(self):
        # Read in the sites from the list
        real = set()
        fake = set()

        with open(self.REAL_LIST, 'r') as file:
            for line in file:
                real.add(line.strip())

        with open(self.FAKE_LIST, 'r') as file:
            for line in file:
                fake.add(line.strip())

        # We combine and distribute the real and fake lists in a round robin fashion
        sites = set([x[1] for x in heapq.merge(zip(count(0, len(fake)), real), zip(count(0, len(real)), fake))])

        for site in sites:
            for year in range(2015, 2020):
                data = ArchiveItem()
                data['domain'] = site
                data['year'] = year
                data['fake'] = site in fake

                # We ONLY collect url of working snapshots (status code of 200)
                url = 'http://web.archive.org/cdx/search/cdx?url={}&from={}&to={}&filter=statuscode:200'.format(site,
                                                                                                                year,
                                                                                                                year)
                yield scrapy.Request(url=url, callback=self.parse_cdx, meta={'data': data})

    def parse_cdx(self, response):
        data = response.meta['data']

        # Filter out for latest timestamp of the day
        timestamps = re.findall(r'\d{14}', response.body.decode("utf-8"))
        timestamps = list(set([timestamp[:8] for timestamp in timestamps]))

        # Grab article urls based off of timestamp snapshot of site
        for timestamp in timestamps:
            url = 'https://web.archive.org/web/{}/{}'.format(timestamp, data.get('domain_url'))
            yield scrapy.Request(url, callback=self.extract_links, meta={'data': data})

    def extract_links(self, response):
        data = response.meta['data']
        timestamp = re.search(r'\d{14}', response.url).group()

        # List of the link objects from the homepage
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        urls = [link.url for link in links]

        urls_data = {
            'domain': data.get('domain'),
            'timestamp': timestamp,
            'year': data.get('year'),
            'urls': urls,
            'response': response.url,
            'fake': data.get('fake')
        }

        # Dump raw link urls into mongodb
        self.URLS.update_one({'response': response.url}, {'$set': urls_data}, upsert=True)
