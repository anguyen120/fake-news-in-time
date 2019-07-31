import multiprocessing
import pandas
import feature_config as cfg

from pandas import DataFrame
from psychological import *
from readability_index import *
from sentiment import *
from vocabulary_richness import *


def analytics(content):
    dictionary = {}

    content = ''.join(filter(lambda x: x in string.printable, content))

    dictionary.update(psy_features(content))
    dictionary.update(ri_features(content))
    dictionary.update(sentiment(content))
    dictionary.update(vr_features(content))

    return dictionary


def process(row):
    data = analytics(row['content'].strip())
    data['_id'] = row['_id']
    data['domain'] = row['domain']
    data['timestamp'] = pandas.to_datetime(row['timestamp'][:8])
    data['fake'] = row['fake']
    return data


def parallel_processing(cursor):
    pool = multiprocessing.Pool(cfg.cores)
    results = pool.map_async(process, [row for index, row in cursor.iterrows()]).get()

    # Close Pool and let all the processes complete
    pool.close()

    # Postpones the execution of next line of code until all processes in the queue are done.
    pool.join()

    return results


def main():
    cursor = pandas.DataFrame(list(cfg.article_collection.find()))

    if cfg.parallel_on:
        results = parallel_processing(cursor)
    else:
        results = [process(row) for index, row in cursor.iterrows()]

    # Create a DataFrame to put features into and later output in CSV
    df = DataFrame(results)
    output_file = df.to_csv(cfg.output_file, index=None, header=True)


main()

