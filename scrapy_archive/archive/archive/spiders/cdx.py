# -*- coding: utf-8 -*-
import heapq
import re
from itertools import count

import scrapy_config as cfg
import scrapy
from archive.items import ArchiveItem
from scrapy.linkextractors import LinkExtractor


class CdxSpider(scrapy.Spider):
    name = 'cdx'
    allowed_domains = ['web.archive.org']

    def start_requests(self):
        fake = cfg.fake
        real = cfg.real

        # We combine and distribute the real and fake lists in a round robin fashion
        sites = set([x[1] for x in heapq.merge(zip(count(0, len(fake)), real), zip(count(0, len(real)), fake))])

        for site in sites:
            data = ArchiveItem()
            data['domain'] = site
            data['fake'] = site in fake

            # We ONLY collect url of working snapshots (status code of 200) by checking archive's cdx query
            url = 'http://web.archive.org/cdx/search/cdx?url={site}&from={start_date}&to={end_date}&filter=statuscode:200'.format(
                site=site, start_date=cfg.start_date, end_date=cfg.end_date)
            yield scrapy.Request(url=url, callback=self.parse_cdx, meta={'data': data})

    def parse_cdx(self, response):
        data = response.meta['data']

        # Filter out for latest timestamp of the day
        timestamps = re.findall(r'\d{14}', response.body.decode("utf-8"))
        timestamps = list(set([timestamp[:8] for timestamp in timestamps]))

        # Grab article urls based off of timestamp snapshot of site
        for timestamp in timestamps:
            url = 'https://web.archive.org/web/{timestamp}/{domain}'.format(timestamp=timestamp,
                                                                            domain=data.get('domain'))
            data['timestamp'] = timestamp
            yield scrapy.Request(url, callback=self.extract_links, meta={'data': data})

    @staticmethod
    def extract_links(response):
        data = response.meta['data']

        # List of the link objects from the homepage
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        urls = [link.url for link in links]

        urls_data = {
            'domain': data.get('domain'),
            'timestamp': data.get('timestamp'),
            'year': data.get('timestamp')[:4],
            'urls': urls,
            'response': response.url,
            'fake': data.get('fake')
        }

        # Dump raw link urls into mongodb
        cfg.urls_collection.update_one({'response': response.url}, {'$set': urls_data}, upsert=True)
