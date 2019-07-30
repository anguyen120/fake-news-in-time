from pymongo import MongoClient

'''
==========
MongoDB settings
==========
'''
client = MongoClient()
database = client.data
urls_collection = database.urls
articles_collection = database.articles

# If filter_on is True, articles that don't pass article word counter will be insert into filter collection
filter_on = True

if filter_on:
    filter_collection = database.filter

# allowDiskUse for pipeline aggregation from MongoDB
allowDiskUse = True

'''
==========
File name of curated sites text file
==========
'''
# To modify, it is assumed these files will be located in /fake-news-in-time/scrapy_archive/archive since scrapers
# are called from there
real_list = 'real.txt'
fake_list = 'fake.txt'

# Read in the sites from the list
real = []
fake = []

with open(real_list, 'r') as file:
    for line in file:
        real.append(line.strip())

with open(fake_list, 'r') as file:
    for line in file:
        fake.append(line.strip())

'''
==========
Collect articles based of these range
==========
'''
# The ranges are inclusive and are specified in the same 1 to 14 digit format used for wayback captures: yyyyMMddhhmmss
start_date = 2015
end_date = 2019

'''
==========
Minimum word count for article text body
==========
'''
min_word_count = 50
