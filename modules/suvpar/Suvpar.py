import pandas
import logging
import json
import numpy

logging.basicConfig(level=logging.INFO)
df = {}
output_csv = {}
final_csv = True


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


def suvpar():
    global df
    # 0x0051100F
    # 0x0051100C
    # 0x00090010
    # 0x0019100B - SIEMENS, milliseconds (divide by 1000 for seconds)
    # 0x0019105A - GE, microseconds (divide 10^6 for seconds)
    # 0x00251011 -

    # Drop entries without an ImageType, AcquisitionTime, SeriesInstanceUID,
    # AcquisitionDate, AccessionNumber, or DeviceSerialNumber entry.
    df.dropna(subset=["ImageType"], inplace=True)
    df.dropna(subset=["AccessionNumber"], inplace=True)
    df.dropna(subset=["SeriesInstanceUID"], inplace=True)
    df.dropna(subset=["AcquisitionTime"], inplace=True)
    df.dropna(subset=["AcquisitionDate"], inplace=True)
    df.dropna(subset=["SeriesTime"], inplace=True)
    df.dropna(subset=["SeriesDate"], inplace=True)
    df.dropna(subset=["DeviceSerialNumber"], inplace=True)
    # Consider only the ImageType that are ORIGINAL.
    df = df[df['ImageType'].str.contains("ORIGINAL")]
    # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
    df = df[df.Modality == "MR"]

    # Check for the AcquisitionTime > SeriesTime case, currently observed in Philips and FONAR scanners.
    df['AltCase'] = numpy.where(df['Manufacturer'].str.contains('Philips|FONAR'), True, False)

    # Add computed non-DICOM fields and drop a few attributes, if we are producing a final_csv and not an intermediate.
    if final_csv:
        df['AcquisitionDateTime'] = df['AcquisitionDate'].astype(int).astype(str) + \
                                df['AcquisitionTime'].astype(float).astype(str)
        df['AcquisitionDateTime'] = pandas.to_datetime(df['AcquisitionDateTime'], format='%Y%m%d%H%M%S.%f')
        df['AcquisitionDateTime'] = df['AcquisitionDateTime'].dt.strftime('%Y/%m/%d %H:%M:%S.%f')

        df['SeriesDateTime'] = df['SeriesDate'].astype(int).astype(str) + df['SeriesTime'].astype(float).astype(str)
        df['SeriesDateTime'] = pandas.to_datetime(df['SeriesDateTime'], format='%Y%m%d%H%M%S.%f')
        df['SeriesDateTime'] = df['SeriesDateTime'].dt.strftime('%Y/%m/%d %H:%M:%S.%f')

        # Compute min and max times for the scan duration at various levels.
        # (1) Series Level
        df = df.join(
            df.groupby('SeriesInstanceUID')['SeriesDateTime'].aggregate(['min', 'max']),
            on='SeriesInstanceUID')
        df.rename(columns={'min': 'TSeriesStartTime'}, inplace=True)
        df.rename(columns={'max': 'TSeriesEndTime'}, inplace=True)

        df = df.join(
            df.groupby('SeriesInstanceUID')['AcquisitionDateTime'].aggregate(['min', 'max']),
            on='SeriesInstanceUID')
        df.rename(columns={'min': 'TAcquisitionStartTime'}, inplace=True)
        df.rename(columns={'max': 'TAcquisitionEndTime'}, inplace=True)

        df['SeriesStartTime'] = df['TSeriesStartTime'] * df['AltCase'] + df['TAcquisitionStartTime'] * ~df['AltCase']
        df['SeriesEndTime'] = df['TAcquisitionEndTime'] * df['AltCase'] + df['TSeriesEndTime'] * ~df['AltCase']

        df['SeriesStartTime'] = pandas.to_datetime(df['SeriesStartTime'])
        df['SeriesEndTime'] = pandas.to_datetime(df['SeriesEndTime'])

        # Compute series duration in minutes
        df['SeriesDurationInMins'] = (df.SeriesEndTime - df.SeriesStartTime).dt.seconds / 60.0

        # Keep only one instance per series. 322,866 rows drops to 3,656 in a tested sample, by this step.
        df = df.drop_duplicates('SeriesInstanceUID')
        df = df.drop(columns=['AcquisitionDate'])
        df = df.drop(columns=['AcquisitionTime'])

        # (2) Study/Accession Level
        df = df.join(
            df.groupby('AccessionNumber')['SeriesDateTime'].aggregate(['min', 'max']),
            on='AccessionNumber')
        df.rename(columns={'min': 'TESeriesStartTime'}, inplace=True)
        df.rename(columns={'max': 'TESeriesEndTime'}, inplace=True)

        df = df.join(
            df.groupby('AccessionNumber')['AcquisitionDateTime'].aggregate(['min', 'max']),
            on='AccessionNumber')
        df.rename(columns={'min': 'TEAcquisitionStartTime'}, inplace=True)
        df.rename(columns={'max': 'TEAcquisitionEndTime'}, inplace=True)

        df['StudyStartTime'] = df['TESeriesStartTime'] * df['AltCase'] + df['TEAcquisitionStartTime'] * ~df['AltCase']
        df['StudyEndTime'] = df['TEAcquisitionEndTime'] * df['AltCase'] + df['TESeriesEndTime'] * ~df['AltCase']

        df['StudyStartTime'] = pandas.to_datetime(df['StudyStartTime'])
        df['StudyEndTime'] = pandas.to_datetime(df['StudyEndTime'])

        # Compute study duration in minutes
        df['StudyDurationInMins'] = (df.StudyEndTime - df.StudyStartTime).dt.seconds / 60.0

        # Check for the AcquisitionTime = SeriesTime case. Mostly for GE scanners. In such cases, series duration will
        # likely be higher than study duration or both of them will be more than 23 hours.
        df['NewAltCase'] = numpy.where((df['SeriesDurationInMins'] > (23 * 60)), ~df['AltCase'], df['AltCase'])
        df['AltCase'] = df['NewAltCase']
        df = df.drop(columns=['NewAltCase'])

        # Recompute study duration with the new AltCase value.
        df['StudyStartTime'] = df['TESeriesStartTime'] * df['AltCase'] + df['TEAcquisitionStartTime'] * ~df['AltCase']
        df['StudyEndTime'] = df['TEAcquisitionEndTime'] * df['AltCase'] + df['TESeriesEndTime'] * ~df['AltCase']

        df['StudyStartTime'] = pandas.to_datetime(df['StudyStartTime'])
        df['StudyEndTime'] = pandas.to_datetime(df['StudyEndTime'])

        df['StudyDurationInMins'] = (df.StudyEndTime - df.StudyStartTime).dt.seconds / 60.0

        # Recompute series duration with the new AltCase value.
        df['SeriesStartTime'] = df['TSeriesStartTime'] * df['AltCase'] + df['TAcquisitionStartTime'] * ~df['AltCase']
        df['SeriesEndTime'] = df['TAcquisitionEndTime'] * df['AltCase'] + df['TSeriesEndTime'] * ~df['AltCase']

        df['SeriesStartTime'] = pandas.to_datetime(df['SeriesStartTime'])
        df['SeriesEndTime'] = pandas.to_datetime(df['SeriesEndTime'])

        df['SeriesDurationInMins'] = (df.SeriesEndTime - df.SeriesStartTime).dt.seconds / 60.0

        # Drop study-level temp fields
        df = df.drop(columns=['TEAcquisitionStartTime'])
        df = df.drop(columns=['TEAcquisitionEndTime'])
        df = df.drop(columns=['TESeriesStartTime'])
        df = df.drop(columns=['TESeriesEndTime'])

        # Drop series-level temp fields
        df = df.drop(columns=['TAcquisitionStartTime'])
        df = df.drop(columns=['TAcquisitionEndTime'])
        df = df.drop(columns=['TSeriesStartTime'])
        df = df.drop(columns=['TSeriesEndTime'])

        # (3) Patient Level
        df = df.join(
            df.groupby('PatientID')['SeriesDateTime'].aggregate(['min', 'max']),
            on='PatientID')
        df.rename(columns={'min': 'TPSeriesStartTime'}, inplace=True)
        df.rename(columns={'max': 'TPSeriesEndTime'}, inplace=True)

        df = df.join(
            df.groupby('PatientID')['AcquisitionDateTime'].aggregate(['min', 'max']),
            on='PatientID')
        df.rename(columns={'min': 'TPAcquisitionStartTime'}, inplace=True)
        df.rename(columns={'max': 'TPAcquisitionEndTime'}, inplace=True)

        df['PatientStartTime'] = df['TPSeriesStartTime'] * df['AltCase'] + df['TPAcquisitionStartTime'] * ~df['AltCase']
        df['PatientEndTime'] = df['TPAcquisitionEndTime'] * df['AltCase'] + df['TPSeriesEndTime'] * ~df['AltCase']

        df['PatientStartTime'] = pandas.to_datetime(df['StudyStartTime'])
        df['PatientEndTime'] = pandas.to_datetime(df['StudyEndTime'])

        # Compute patient duration in minutes
        df['PatientDurationInMins'] = (df.PatientEndTime - df.PatientStartTime).dt.seconds / 60.0

        df = df.drop(columns=['TPAcquisitionStartTime'])
        df = df.drop(columns=['TPAcquisitionEndTime'])
        df = df.drop(columns=['TPSeriesStartTime'])
        df = df.drop(columns=['TPSeriesEndTime'])

        # (4) Scanner Level
        df = df.join(
            df.groupby('DeviceSerialNumber')['SeriesDateTime'].aggregate(['min', 'max']),
            on='DeviceSerialNumber')
        df.rename(columns={'min': 'TCSeriesStartTime'}, inplace=True)
        df.rename(columns={'max': 'TCSeriesEndTime'}, inplace=True)

        df = df.join(
            df.groupby('DeviceSerialNumber')['AcquisitionDateTime'].aggregate(['min', 'max']),
            on='DeviceSerialNumber')
        df.rename(columns={'min': 'TCAcquisitionStartTime'}, inplace=True)
        df.rename(columns={'max': 'TCAcquisitionEndTime'}, inplace=True)

        df['ScannerOn'] = df['TCSeriesStartTime'] * df['AltCase'] + df['TCAcquisitionStartTime'] * ~df['AltCase']
        df['ScannerOff'] = df['TCAcquisitionEndTime'] * df['AltCase'] + df['TCSeriesEndTime'] * ~df['AltCase']

        df['ScannerOn'] = pandas.to_datetime(df['ScannerOn'])
        df['ScannerOff'] = pandas.to_datetime(df['ScannerOff'])

        # Compute scanner on duration in minutes
        df['ScannerTotalOnTimeInMins'] = (df.ScannerOff - df.ScannerOn).dt.seconds / 60.0

        df = df.drop(columns=['TCAcquisitionStartTime'])
        df = df.drop(columns=['TCAcquisitionEndTime'])
        df = df.drop(columns=['TCSeriesStartTime'])
        df = df.drop(columns=['TCSeriesEndTime'])

        # Sort by "DeviceSerialNumber" and "SeriesStartTime"
        df = df.sort_values(["DeviceSerialNumber", "SeriesStartTime"])


def write():
    df.to_csv(output_csv)


if __name__ == "__main__":
    initialize()
    suvpar()
    write()
