import pandas
import logging
import json
import numpy
import hashlib

logging.basicConfig(level=logging.INFO)
df = {}
sta = {}
statistics_csv = {}
output_csv = {}


def initialize():
    global output_csv, df, device_SN, scanner_filter, statistics_csv, isStatistics, final_csv, isAnonymized, ris_df, is_merge_with_ris
    with open('config.json', 'r') as f:
        config = json.load(f)

    feature_file = config['FeaturesetFile']
    filename = config['InputFile']
    output_csv = config['OutputFile']
    scanner_file = config['ScannerDetails']
    scanner_filter = bool(config['ScannerFilter'])
    statistics_csv = config['Statistics_File']
    isStatistics = bool(config['IsStatistics'])
    ris_csv = config['RIS_File']
    is_merge_with_ris = bool(config['IsMergeWithRis'])
    final_csv = bool(config['IsFinalCSV'])
    isAnonymized = bool(config['IsAnonymized'])
    text_file = open(feature_file, "r")
    feature_list = text_file.read().split('\n')
    # Consider some Device Serial Number and remove other.
    scanner_file = open(scanner_file, "r")
    device_SN = scanner_file.read().split('\n')
    df = pandas.read_csv(filename, usecols=lambda x: x in feature_list, sep=',')
    ris_df = pandas.read_csv(ris_csv)


def suvpar():
    global df, sta
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
    # Remove only the ImageType that are NA or NPR.
    df = df[(~df['ImageType'].str.contains('NA|NPR')) | (df['ImageType'].str.contains('ORIGINAL'))]
    # Consider only MR. Remove modalities such as PR and SR that are present in the original data.
    df = df[df.Modality == "MR"]
    # Dataset after removing unwanted Device Serial Number
    if scanner_filter:
        temp_sn = list()
        # sometimes DeviceSerialNumber are int data type
        for SN in device_SN:
            if SN.isdigit():
                temp_sn.append(int(SN))
        device_SN.extend(temp_sn)
        df = df.loc[df['DeviceSerialNumber'].isin(device_SN)]
    # Check for the AcquisitionTime > SeriesTime case, currently observed in Philips and FONAR scanners.
    df['AltCase'] = numpy.where(df['Manufacturer'].str.contains('Philips|FONAR'), True, False)

    #  Statistics of the dataset after drop some values
    sta = df.describe()
    if isAnonymized:
        # Apply hashing function to the column.
        df['AccessionNumber'] = df['AccessionNumber'].astype(str).apply(
            lambda x:
            hashlib.sha256(x.encode()).hexdigest()
        )

        df['InstitutionAddress'] = df['InstitutionAddress'].astype(str).apply(
            lambda x:
            hashlib.sha256(x.encode()).hexdigest()
        )

        df['PatientID'] = df['PatientID'].astype(str).apply(
            lambda x:
            hashlib.sha256(x.encode()).hexdigest()
        )

        df['SeriesInstanceUID'] = df['SeriesInstanceUID'].astype(str).apply(
            lambda x:
            hashlib.sha256(x.encode()).hexdigest()
        )

    # Statistics of the dataset after isAnonymized
    sta = df.describe()
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

        # if ContentDateTime available
        if 'ContentTime' and 'ContentDate' in df.columns:
            df.dropna(subset=["ContentTime"], inplace=True)
            df['ContentDateTime'] = df['ContentDate'].astype(int).astype(str) + \
                                    df['ContentTime'].astype(float).astype(str)
            df['ContentDateTime'] = pandas.to_datetime(df['ContentDateTime'], format='%Y%m%d%H%M%S.%f')
            df['ContentDateTime'] = df['ContentDateTime'].dt.strftime('%Y/%m/%d %H:%M:%S.%f')

            # (1) Series Level for ContentDateTime
            df = df.join(
                df.groupby('SeriesInstanceUID')['ContentDateTime'].aggregate(['min', 'max']),
                on='SeriesInstanceUID')
            df.rename(columns={'min': 'TContentStartTime'}, inplace=True)
            df.rename(columns={'max': 'TContentEndTime'}, inplace=True)

            df['SeriesStartTime'] = df['TSeriesStartTime'] * df['AltCase'] + df['TContentStartTime'] * ~df['AltCase']
            df['SeriesEndTime'] = df['TContentEndTime'] * df['AltCase'] + df['TSeriesEndTime'] * ~df['AltCase']

            df['SeriesStartTime'] = pandas.to_datetime(df['SeriesStartTime'])
            df['SeriesEndTime'] = pandas.to_datetime(df['SeriesEndTime'])

            # Compute series duration in minutes
            df['SeriesDurationInMins'] = (df.SeriesEndTime - df.SeriesStartTime).dt.seconds / 60.0

            # Keep only one instance per series. 322,866 rows drops to 3,656 in a tested sample, by this step.
            df = df.drop_duplicates('SeriesInstanceUID')
            df = df.drop(columns=['ContentDate'])
            df = df.drop(columns=['ContentTime'])

            # (2) Study/Accession Level for ContentDateTime
            df = df.join(
                df.groupby('AccessionNumber')['ContentDateTime'].aggregate(['min', 'max']),
                on='AccessionNumber')
            df.rename(columns={'min': 'TEContentStartTime'}, inplace=True)
            df.rename(columns={'max': 'TEContentEndTime'}, inplace=True)

            df['StudyStartTime'] = df['TESeriesStartTime'] * df['AltCase'] + df['TEContentStartTime'] * ~df['AltCase']
            df['StudyEndTime'] = df['TEContentEndTime'] * df['AltCase'] + df['TESeriesEndTime'] * ~df['AltCase']

            df['StudyStartTime'] = pandas.to_datetime(df['StudyStartTime'])
            df['StudyEndTime'] = pandas.to_datetime(df['StudyEndTime'])

            # Compute study duration in minutes
            df['StudyDurationInMins'] = (df.StudyEndTime - df.StudyStartTime).dt.seconds / 60.0

            df['NewAltCase'] = numpy.where((df['SeriesDurationInMins'] > (23 * 60)), ~df['AltCase'], df['AltCase'])
            df['AltCase'] = df['NewAltCase']
            df = df.drop(columns=['NewAltCase'])

            # Recompute study duration with the new AltCase value.
            df['StudyStartTime'] = df['TESeriesStartTime'] * df['AltCase'] + df['TEContentStartTime'] * ~df['AltCase']
            df['StudyEndTime'] = df['TEContentEndTime'] * df['AltCase'] + df['TESeriesEndTime'] * ~df['AltCase']

            df['StudyStartTime'] = pandas.to_datetime(df['StudyStartTime'])
            df['StudyEndTime'] = pandas.to_datetime(df['StudyEndTime'])

            df['StudyDurationInMins'] = (df.StudyEndTime - df.StudyStartTime).dt.seconds / 60.0

            # Recompute series duration with the new AltCase value.
            df['SeriesStartTime'] = df['TSeriesStartTime'] * df['AltCase'] + df['TEContentStartTime'] * ~df['AltCase']
            df['SeriesEndTime'] = df['TEContentEndTime'] * df['AltCase'] + df['TSeriesEndTime'] * ~df['AltCase']

            df['SeriesStartTime'] = pandas.to_datetime(df['SeriesStartTime'])
            df['SeriesEndTime'] = pandas.to_datetime(df['SeriesEndTime'])

            df['SeriesDurationInMins'] = (df.SeriesEndTime - df.SeriesStartTime).dt.seconds / 60.0

            # Drop study-level temp fields
            df = df.drop(columns=['TEContentStartTime'])
            df = df.drop(columns=['TEContentEndTime'])

            # Drop series-level temp fields
            df = df.drop(columns=['TContentStartTime'])
            df = df.drop(columns=['TContentEndTime'])

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

        df = df.drop(
            columns=['TCAcquisitionStartTime', 'TCAcquisitionEndTime', 'TCSeriesStartTime', 'TCSeriesEndTime', ])

        # (5) Study Level Scanner Utilization
        df_temp1 = df.groupby(['StudyDate', 'DeviceSerialNumber', 'AccessionNumber']).SeriesDurationInMins.agg(
            [sum]).reset_index()
        df_temp2 = df.groupby(['StudyDate', 'DeviceSerialNumber', 'AccessionNumber']).StudyDurationInMins.agg(
            "mean").reset_index().drop(columns=['StudyDate', 'DeviceSerialNumber'])

        df_study = pandas.merge(df_temp1, df_temp2, on='AccessionNumber')
        df_study.rename(columns={'StudyDurationInMins': 'TotalStudyDurationInMins', 'sum': 'SeriesDurationInMinsTotal'},
                        inplace=True)
        df_study = df_study.drop_duplicates('AccessionNumber')
        df_study['StudyLevelScannerUtilization'] = df_study['SeriesDurationInMinsTotal'] / df_study[
            'TotalStudyDurationInMins']
        df_temp = df[['AccessionNumber', 'PatientID']].drop_duplicates('AccessionNumber')
        df_study = pandas.merge(df_study, df_temp, on='AccessionNumber')
        df_study = df_study.drop(columns=['DeviceSerialNumber', 'PatientID'])
        # In df_study consist six columns ('StudyDate', 'DeviceSerialNumber', 'AccessionNumber',
        # 'StudyLevelScannerUtilization', 'SeriesDurationInMinsTotal','StudyDurationInMean','PatientID']

        # (6) Multi Study Duration Encounter
        df_multi = df[['DeviceSerialNumber', 'AccessionNumber', 'PatientID', 'StudyStartTime', 'StudyEndTime',
                       'StudyDurationInMins']]
        df_multi = df_multi.drop_duplicates('AccessionNumber')
        df_multi = df_multi.sort_values(["DeviceSerialNumber", 'StudyStartTime', 'PatientID'])

        m_pid = []  # PatientID come under the multi study duration
        n_m_pid = [df_multi.iloc[-1, 2]]  # PatientID come under the non-multi study duration
        for i in range(0, len(df_multi) - 1):
            if df_multi.iloc[i, 2] == df_multi.iloc[i + 1, 2]:
                if ((df_multi.iloc[i + 1, 3] - df_multi.iloc[i, 4]).total_seconds() / 60) < 20:
                    m_pid.append(df_multi.iloc[i, 2])
            else:
                n_m_pid.append(df_multi.iloc[i, 2])

        for i in m_pid:
            if i in n_m_pid:
                n_m_pid.remove(i)

        # row contain multi-study encounter
        df_multi_study = df_multi.loc[df['PatientID'].isin(m_pid)]
        # row contain non multi-study encounter
        df_non_multi_study = df_multi.loc[df['PatientID'].isin(n_m_pid)]

        df_multi_study = df_multi_study.join(
            df_multi_study.groupby('PatientID')['StudyStartTime'].aggregate(['min']),
            on='PatientID')
        df_multi_study = df_multi_study.join(
            df_multi_study.groupby('PatientID')['StudyEndTime'].aggregate(['max']),
            on='PatientID')
        df_multi_study['MultiStudyEncounter'] = True
        df_multi_study.rename(columns={'min': 'StudyStartTimeMin'}, inplace=True)
        df_multi_study.rename(columns={'max': 'StudyEndTimeMax'}, inplace=True)

        df_multi_study['StudyStartTimeMin'] = pandas.to_datetime(df_multi_study['StudyStartTimeMin'])
        df_multi_study['StudyEndTimeMax'] = pandas.to_datetime(df_multi_study['StudyEndTimeMax'])

        # Compute multi StudyDuration Time
        df_multi_study['StudyDurationInMins'] = (
                                                        df_multi_study.StudyEndTimeMax - df_multi_study.StudyStartTimeMin).dt.seconds / 60.0

        df_multi_study = df_multi_study.drop(
            columns=['StudyEndTimeMax', 'StudyStartTimeMin'])

        # connect both table df_multi_study and df_non_multi_study
        df_multi_study = pandas.concat([df_multi_study, df_non_multi_study])

        # Fill the other MultiStudyEncounter values with false
        df_multi_study["MultiStudyEncounter"].fillna(False, inplace=True)

        # Drope the duplicate AccessionNumbers
        df_multi_study = df_multi_study.drop_duplicates('AccessionNumber')
        df_study = pandas.merge(df_multi_study, df_study, on='AccessionNumber')

        # (7) scanner utilization
        df_temp = df.groupby(['StudyDate', 'DeviceSerialNumber']).ScannerTotalOnTimeInMins.agg(
            "mean").reset_index().drop(
            columns=['StudyDate'])
        # Now add the DeviceSerialNumber column in df_study
        df_study = pandas.merge(df_study, df_temp, on='DeviceSerialNumber')

        # adding the total StudyDuration by particular scanner and PatientID
        df_temp = df_study.groupby(['StudyDate', 'DeviceSerialNumber', 'PatientID']).StudyDurationInMins.agg(
            "mean").reset_index()
        df_temp = df_temp.groupby(['StudyDate', 'DeviceSerialNumber']).StudyDurationInMins.agg(
            [sum]).reset_index().drop(
            columns=['StudyDate'])

        # mean duration time of the that scanner
        df_temp1 = df_study.groupby(['StudyDate', 'DeviceSerialNumber']).ScannerTotalOnTimeInMins.agg(
            "mean").reset_index().drop(
            columns=['StudyDate'])
        df_scanner = pandas.merge(df_temp, df_temp1, on='DeviceSerialNumber')
        df_scanner.rename(
            columns={'sum': 'StudyDurationInMinsSum', 'ScannerTotalOnTimeInMins': 'ScannerTotalOnTimeInMinsMean'},
            inplace=True)

        df_scanner['ScannerUtilization'] = (df_scanner['StudyDurationInMinsSum'] / df_scanner[
            'ScannerTotalOnTimeInMinsMean']) * 100

        # merge df_study with df_scanner
        df_utilizer = pandas.merge(df_study, df_scanner, on='DeviceSerialNumber')

        # drop duplicate columns
        df_utilizer = df_utilizer.drop(columns={'StudyDate', 'DeviceSerialNumber', 'SeriesDurationInMinsTotal',
                                                'TotalStudyDurationInMins',
                                                'ScannerTotalOnTimeInMins', 'ScannerTotalOnTimeInMinsMean', 'PatientID',
                                                'StudyStartTime', 'StudyEndTime',
                                                'StudyDurationInMins', 'StudyDurationInMinsSum'})
        # merge with main dataset
        df = pandas.merge(df, df_utilizer, on='AccessionNumber')

        # Sort by "DeviceSerialNumber" and "SeriesStartTime"
        df = df.sort_values(["DeviceSerialNumber", "SeriesStartTime"])

        # it will fill the nan values as well as give the symbol for weird cases.
        df = df.fillna(-1)
        # Statistics of the dataset
        sta = df.describe()
        sta.loc['count', 'MultiStudyEncounter'] = df[df['MultiStudyEncounter'] == True]['InstanceNumber'].count()

    if is_merge_with_ris:
        df = pandas.merge(df, ris_df, on='PatientID')


def write():
    global isStatistics
    df.to_csv(output_csv)
    if isStatistics:
        sta.to_csv(statistics_csv)


if __name__ == "__main__":
    initialize()
    suvpar()
    write()
