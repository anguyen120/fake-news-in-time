# -*- coding: utf-8 -*-
import heapq
import re
import sys
from itertools import count

import scrapy_config as cfg
import scrapy
from archive.items import ArchiveItem
from newspaper import Article
from nltk.tokenize import sent_tokenize, word_tokenize
from scrapy.linkextractors import LinkExtractor


"""
==========
urls_filter function will receive in the list object string of url and the ArchiveItem object
It uses the site string to check if the documents' urls matches web.archive.org snapshot url format
This helps not processing articles from third party links 
==========
"""
def urls_filter(urls, data):
    date = data.get('timestamp')[:8]

    # We check if the urls follows the format of "https://web.archive.org/web/{date}(hhmmss)/{domain}/*"
    url_format = re.compile(
        r'https:\/\/web\.archive\.org\/web\/' + re.escape(
            date) + r'\d{6}\/(?:http(?:s)?:\/\/)?(?:w{3}.)?' + re.escape(
            data.get('domain')) + r'\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    return list(filter(url_format.search, urls))


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

    def extract_links(self, response):
        data = response.meta['data']

        # List of the link objects from the homepage
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)

        urls = [link.url for link in links]

        urls = urls_filter(urls, data)

        for url in urls:
            yield scrapy.Request(url, callback=self.parse_article, meta={'data': data})

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

            article_data = {
                'title': article.title,
                'author': article.authors,
                'publish_date': article.publish_date,
                'content': article_text,
                'domain': data.get('domain'),
                'timestamp': data.get('timestamp'),
                'year': data.get('domain')[:4],
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
