import pandas
import logging

logging.basicConfig(level=logging.INFO)
feature_file = 'properties.txt'


def initialize_config_and_execute(filename):
    text_file = open(feature_file, "r")
    feature_list = text_file.read().split('\n')

    filtered_csv = pandas.read_csv(filename, usecols=lambda x: x in feature_list, sep=',')
    logging.info(filtered_csv)
    df = pandas.DataFrame(filtered_csv)
    df.to_csv()


if __name__ == "__main__":
    initialize_config_and_execute('sample.csv')
