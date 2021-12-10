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
    # Drop entries without an ImageType, AcquisitionTime, AcquisitionDate, AccessionNumber, or DeviceSerialNumber entry.
    df.dropna(subset=["ImageType"], inplace=True)
    df.dropna(subset=["AccessionNumber"], inplace=True)
    df.dropna(subset=["AcquisitionTime"], inplace=True)
    df.dropna(subset=["AcquisitionDate"], inplace=True)
    df.dropna(subset=["DeviceSerialNumber"], inplace=True)
    # Consider only the ImageType that are ORIGINAL.
    df = df[df['ImageType'].str.contains("ORIGINAL")]
    # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
    df = df[df.Modality == "MR"]
    # Ignore milliseconds
    df['AcquisitionTime'] = df['AcquisitionDate'].astype(int).astype(str) + \
                            df['AcquisitionTime'].astype(int).astype(str)
    df['AcquisitionTime'] = pandas.to_datetime(df['AcquisitionTime'], format='%Y%m%d%H%M%S')
    df = df.join(
        df.groupby('AccessionNumber')['AcquisitionTime'].aggregate(['min', 'max']),
        on='AccessionNumber')
    df.rename(columns={'AcquisitionTime': 'AcquisitionDateTime'}, inplace=True)
    df.rename(columns={'min': 'MinAcquisitionDateTime'}, inplace=True)
    df.rename(columns={'max': 'MaxAcquisitionDateTime'}, inplace=True)
    df = df.drop_duplicates('AccessionNumber')
    df = df.drop(columns=['AcquisitionDate'])


def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize()
    strip()
    write()
