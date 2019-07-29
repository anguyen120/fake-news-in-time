# -*- coding: utf-8 -*-
import heapq
import itertools
import re
import sys
from collections import defaultdict
from itertools import chain, count

import scrapy
from newspaper import Article
from nltk.tokenize import sent_tokenize, word_tokenize
from pymongo import MongoClient

from archive.items import ArchiveItem


"""
Comment about a summary of this nice helper function
"""
def url_filter(aggregation, site):
    urls = defaultdict(list)

    for item in aggregation:
        item_urls = list(itertools.chain(*item.get('urls')))

        if len(urls[2015]) > 3000 and len(urls[2016]) > 3000 and len(urls[2017]) > 3000 and len(
                urls[2018]) > 3000 and len(urls[2019]) > 3000:
            break
        else:
            year = int(item.get('_id').get('timestamp')[:4])

            # We check if the url follows the format of "https://web.archive.org/web/(timestamp)/(domain)/*"
            filter_exp = re.compile(
                r'https:\/\/web\.archive\.org\/web\/' + re.escape(
                    item.get('_id').get('timestamp')) + r'\/(?:http(?:s)?:\/\/)?(?:w{3}.)?' + re.escape(
                    site) + r'\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            filter_urls = filter(filter_exp.search, item_urls)

            if len(urls[2015]) <= 3000 and year == 2015:
                urls[2015].extend(filter_urls)
            elif len(urls[2016]) <= 3000 and year == 2016:
                urls[2016].extend(filter_urls)
            elif len(urls[2017]) <= 3000 and year == 2017:
                urls[2017].extend(filter_urls)
            elif len(urls[2018]) <= 3000 and year == 2018:
                urls[2018].extend(filter_urls)
            elif len(urls[2019]) <= 3000 and year == 2019:
                urls[2019].extend(filter_urls)

    return [url for year, url in urls]


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['web.archive.org']

    # File name of curated sites
    REAL_LIST = 'real.txt'
    FAKE_LIST = 'fake.txt'

    # Minimum word count for article text
    MIN_WORD_COUNT = 50

    CLIENT = MongoClient()
    DATABASE = CLIENT.data
    ARTICLES = DATABASE.articles
    FILTER = DATABASE.filter
    URLS = DATABASE.urls

    def start_requests(self):
        # Read in sites from list
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
            data = ArchiveItem()
            data['domain'] = site
            data['fake'] = site in fake

            # Grab a sample from database for each site
            pipeline = [
                {'$match': {'domain': site, 'fake': data.get('fake')}},
                {'$project': {'_id': 0, 'year': 1, 'fake': 1, 'domain': 1, 'urls': 1, 'timestamp': 1}},
                {'$sample': {'size': 1000}},
                {'$group': {'_id': {'year': '$year', 'timestamp': '$timestamp', 'fake': '$fake', 'domain': '$domain'},
                            'urls': {'$push': '$urls'}}}
            ]

            aggregation = list(self.URLS.aggregate(pipeline, allowDiskUse=True))

            # Access the objects' urls list and filter urls then grab only 3000 urls for each year + domain
            urls = url_filter(aggregation, site)

            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_article, meta={'data': data})

    # Newspaper3k handles extracting article
    def parse_article(self, response):
        # Some links are not articles so we need to handle it
        try:
            article = Article(
                response.url,
                language='en',
                MAX_TITLE=sys.maxsize,
                MAX_TEXT=sys.maxsize,
                fetch_images=False,
            )

            # You must have called download() on an article before calling parse()
            article.download()
            article.parse()

            # If article has an image, it will gave (snip) in its body but we don't need it
            article_text = re.sub('(snip)', '', article.text)

            data = response.meta['data']
            timestamp = re.search(r'\d{14}', response.url).group()

            article_data = {
                'title': article.title,
                'author': article.authors,
                'publish_date': article.publish_date,
                'content': article_text,
                'domain': data.get('domain'),
                'timestamp': timestamp,
                'year': int(timestamp[:4]),
                'url': response.url,
                'fake': data.get('fake')
            }

            # Filter then store article data if it is not in the collection
            if self.word_count(article_text):
                self.ARTICLES.update_one({'url': response.url}, {'$set': article_data}, upsert=True)
            else:
                self.FILTER.update_one({'url': response.url}, {'$set': article_data}, upsert=True)
        except Exception as e:
            # If it is not an article, we move on
            pass

    def word_count(self, article_text):
        word_counter = 0
        article_sentences = sent_tokenize(article_text)

        for sentence in article_sentences:
            word_counter += len(word_tokenize(sentence))

        return word_counter >= self.MIN_WORD_COUNT
