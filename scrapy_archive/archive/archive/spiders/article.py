# -*- coding: utf-8 -*-
import heapq
import itertools
import re
import sys
from itertools import count

import config as cfg
import scrapy
from archive.items import ArchiveItem
from newspaper import Article
from nltk.tokenize import sent_tokenize, word_tokenize

"""
==========
urls_filter function will receive in the list object of the aggregation from MongoDB and a string of the site
It uses the site string to check if the documents' urls matches web.archive.org snapshot url format
This helps not processing articles from third party links 
==========
"""


def urls_filter(aggregation, site):
    urls = []

    for document in aggregation:
        item_urls = list(itertools.chain(*document.get('urls')))
        date = document.get('_id').get('timestamp')[:8]

        # We check if the urls follows the format of "https://web.archive.org/web/{date}(hhmmss)/{domain}/*"
        filter_exp = re.compile(
            r'https:\/\/web\.archive\.org\/web\/' + re.escape(
                date) + r'\d{6}\/(?:http(?:s)?:\/\/)?(?:w{3}.)?' + re.escape(
                site) + r'\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        filter_urls = filter(filter_exp.search, item_urls)
        urls.extend(filter_urls)

    return urls


'''
==========
word_count function takes in a string of the article text
Using nltk's tokenizer, the function will return a bool based off of the word count against the configured min_word_count
==========
'''


def word_count(article_text):
    word_counter = 0
    article_sentences = sent_tokenize(article_text)

    for sentence in article_sentences:
        word_counter += len(word_tokenize(sentence))

    return word_counter >= cfg.min_word_count


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['web.archive.org']

    def start_requests(self):
        # Read in sites from list
        real = cfg.real
        fake = cfg.fake

        # We combine and distribute the real and fake lists in a round robin fashion
        sites = set([x[1] for x in heapq.merge(zip(count(0, len(fake)), real), zip(count(0, len(real)), fake))])

        for site in sites:
            data = ArchiveItem()
            data['domain'] = site
            data['fake'] = site in fake

            pipeline = [
                {'$match': {'domain': site, 'fake': data.get('fake')}},
                {'$project': {'_id': 0, 'year': 1, 'fake': 1, 'domain': 1, 'urls': 1, 'timestamp': 1}},
                {'$group': {'_id': {'year': '$year', 'timestamp': '$timestamp', 'fake': '$fake', 'domain': '$domain'},
                            'urls': {'$push': '$urls'}}}
            ]

            aggregation = list(cfg.urls_collection.aggregate(pipeline, allowDiskUse=cfg.allowDiskUse))

            # Access the objects' urls list and filter urls
            urls = urls_filter(aggregation, site)

            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_article, meta={'data': data})

    # Newspaper3k handles extracting article
    @staticmethod
    def parse_article(response):
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

            # If article has an image, it will gave (snip) in its body but we don't want to include the phrase
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
            if word_count(article_text):
                cfg.articles_collection.update_one({'url': response.url}, {'$set': article_data}, upsert=True)
            else:
                if cfg.filter_on:
                    cfg.filter_collection.update_one({'url': response.url}, {'$set': article_data}, upsert=True)
        except Exception as e:
            # If it is not an article, we move on
            pass
