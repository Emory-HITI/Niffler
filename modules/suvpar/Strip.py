import pandas
import logging
import json

logging.basicConfig(level=logging.INFO)
df = {}
output_csv = {}


def initialize():
    global output_csv, df
    with open('config.json', 'r') as f:
        config = json.load(f)

    feature_file = config['FeaturesetFile']
    filename = config['InputFile']
    output_csv = config['OutputFile']

    text_file = open(feature_file, "r")
    feature_list = text_file.read().split('\n')

    df = pandas.read_csv(filename, usecols=lambda x: x in feature_list, sep=',')
    logging.info(df['ImageType'])


def strip():
    global df
    try:
        # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
        df = df[df.Modality == "MR"]
        # Consider only the ImageType that are true.
        df = df[df['ImageType'].str.contains("ORIGINAL")]
    except ValueError:
        logging.exception("Empty entry detected")

def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize()
    strip()
    write()
