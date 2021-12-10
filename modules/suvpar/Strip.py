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


def strip():
    global df
    # Drop entries without an ImageType, AcquisitionTime, or an AccessionNumber entry.
    df.dropna(subset=["ImageType"], inplace=True)
    df.dropna(subset=["AccessionNumber"], inplace=True)
    df.dropna(subset=["AcquisitionTime"], inplace=True)
    # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
    df = df[df['ImageType'].str.contains("ORIGINAL")]
    df = df[df.Modality == "MR"]
    # Consider only the ImageType that are ORIGINAL.
    df['AcquisitionTime'] = pandas.to_datetime(df['AcquisitionTime'], format='%H%M%S')
    df = df.join(
        df.groupby('AccessionNumber')['AcquisitionTime'].aggregate(['min', 'max']),
        on='AccessionNumber')
    df = df.drop_duplicates('AccessionNumber')


def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize()
    strip()
    write()
