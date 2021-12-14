import pandas
import logging
import json

logging.basicConfig(level=logging.INFO)
df = {}
output_csv = {}
drop = True


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
    # Drop entries without an ImageType, AcquisitionTime, SeriesInstanceUID,
    # AcquisitionDate, AccessionNumber, or DeviceSerialNumber entry.
    df.dropna(subset=["ImageType"], inplace=True)
    df.dropna(subset=["AccessionNumber"], inplace=True)
    df.dropna(subset=["SeriesInstanceUID"], inplace=True)
    df.dropna(subset=["AcquisitionTime"], inplace=True)
    df.dropna(subset=["AcquisitionDate"], inplace=True)
    df.dropna(subset=["DeviceSerialNumber"], inplace=True)
    # Consider only the ImageType that are ORIGINAL.
    df = df[df['ImageType'].str.contains("ORIGINAL")]
    # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
    df = df[df.Modality == "MR"]
    df['AcquisitionDateTime'] = df['AcquisitionDate'].astype(int).astype(str) + \
                            df['AcquisitionTime'].astype(float).astype(str)
    df['AcquisitionDateTime'] = pandas.to_datetime(df['AcquisitionDateTime'], format='%Y%m%d%H%M%S.%f')
    df['AcquisitionDateTime'] = df['AcquisitionDateTime'].dt.strftime('%Y/%m/%d %H:%M:%S.%f')
    df = df.join(
        df.groupby('SeriesInstanceUID')['AcquisitionDateTime'].aggregate(['min', 'max']),
        on='SeriesInstanceUID')
    df.rename(columns={'min': 'SeriesStartTime'}, inplace=True)
    df.rename(columns={'max': 'SeriesEndTime'}, inplace=True)
    df['SeriesStartTime'] = pandas.to_datetime(df['SeriesStartTime'])
    df['SeriesEndTime'] = pandas.to_datetime(df['SeriesEndTime'])
    df['SeriesDurationInMins'] = (df.SeriesEndTime - df.SeriesStartTime).dt.seconds / 60.0

    if drop:
        # Keep only one instance per series. 322,866 rows drops to 3,656 in a tested sample, by this step.
        df = df.drop_duplicates('SeriesInstanceUID')
        df = df.drop(columns=['AcquisitionDate'])
        df = df.drop(columns=['AcquisitionTime'])

    df = df.join(df.groupby('AccessionNumber')['AcquisitionDateTime'].aggregate(['min', 'max']), on='AccessionNumber')
    df.rename(columns={'min': 'StudyStartTime'}, inplace=True)
    df.rename(columns={'max': 'StudyEndTime'}, inplace=True)
    df['StudyStartTime'] = pandas.to_datetime(df['StudyStartTime'])
    df['StudyEndTime'] = pandas.to_datetime(df['StudyEndTime'])
    df['StudyDurationInMins'] = (df.StudyEndTime - df.StudyStartTime).dt.seconds / 60.0

    df = df.join(df.groupby('PatientID')['AcquisitionDateTime'].aggregate(['min', 'max']), on='PatientID')
    df.rename(columns={'min': 'PatientStartTime'}, inplace=True)
    df.rename(columns={'max': 'PatientEndTime'}, inplace=True)
    df['PatientStartTime'] = pandas.to_datetime(df['StudyStartTime'])
    df['PatientEndTime'] = pandas.to_datetime(df['StudyEndTime'])
    df['PatientDurationInMins'] = (df.PatientEndTime - df.PatientStartTime).dt.seconds / 60.0

    df = df.join(df.groupby('DeviceSerialNumber')['AcquisitionDateTime'].aggregate(['min', 'max']),
                 on='DeviceSerialNumber')
    # Estimating the last scan as the scanner off.
    df.rename(columns={'min': 'ScannerOn'}, inplace=True)
    df.rename(columns={'max': 'ScannerOff'}, inplace=True)
    df['ScannerOn'] = pandas.to_datetime(df['ScannerOn'])
    df['ScannerOff'] = pandas.to_datetime(df['ScannerOff'])
    df['ScannerTotalOnTimeInMins'] = (df.ScannerOff - df.ScannerOn).dt.seconds / 60.0

    # Sort by "DeviceSerialNumber" and "SeriesStartTime"
    df = df.sort_values(["DeviceSerialNumber", "SeriesStartTime"])


def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize()
    strip()
    write()
