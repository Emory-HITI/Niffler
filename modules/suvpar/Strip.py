import pandas
import logging
import json

logging.basicConfig(level=logging.INFO)
df = {}
output_csv = {}


def initialize_config_and_execute():
    global df, output_csv
    with open('config.json', 'r') as f:
        config = json.load(f)

    feature_file = config['FeaturesetFile']
    filename = config['InputFile']
    output_csv = config['OutputFile']

    text_file = open(feature_file, "r")
    feature_list = text_file.read().split('\n')

    filtered_csv = pandas.read_csv(filename, usecols=lambda x: x in feature_list, sep=',')
    df = pandas.DataFrame(filtered_csv)


def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize_config_and_execute()
    write()
