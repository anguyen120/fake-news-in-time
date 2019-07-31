import multiprocessing

from pymongo import MongoClient


'''
==========
MongoDB settings
==========
'''
client = MongoClient()
database = client.data
articles_collection = database.articles


'''
==========
Parallel processing setting
==========
'''
parallel_on = True
# We set one core to avoid locking up the system and another for MongoDB then the rest goes to pool
if parallel_on:
    cores = multiprocessing.cpu_count() - 2


'''
==========
File name for extracted features of article
==========
'''
output_file = 'output.csv'
