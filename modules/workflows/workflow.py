from genericpath import exists
import os, os.path
import json
import subprocess

def workflow(depth, file_path, master_path, processes, csv_file, total_attributes, first_attribute, first_index, second_attribute, 
            second_index, email_flag, email, folder_name):

    dicom_images_path = master_path+str(folder_name)+'/cold_extraction_accession_number/'
    os.makedirs(dicom_images_path, exist_ok=True)

    logs_path = master_path+'logs/'
    os.makedirs(logs_path, exist_ok=True)

    print (dicom_images_path, csv_file)

    # cold extraction
    subprocess.call("python3 ../cold-extraction/ColdDataRetriever.py --NifflerSystem {0} --StorageFolder {1} "
        "--FilePath {2} --CsvFile {3} --NumberOfQueryAttributes {4} --FirstAttr {5} --FirstIndex {6} --SecondAttr {7} "
        "--SecondIndex {8} --ThirdAttr {9} --ThirdIndex {10} --DateFormat {11} --SendEmail {12} --YourEmail {13}"
        .format('../cold-extraction/system.json', dicom_images_path, file_path, csv_file, total_attributes, 
        first_attribute, first_index, second_attribute, second_index, 'StudyDate', 3, '%Y%m%d', email_flag, email), shell=True)

    # # png extraction
    # png_path = master_path+folder_name+'/png_images/'
    # os.makedirs(png_path, exist_ok=True)

    # subprocess.call("python3 ../png-extraction/ImageExtractor.py --DICOMHome {} --OutputDirectory {}, --Depth {} "
    #     "--PrintImage {} --CommonHeadersOnly {} --UseProcesses {} --FlattenedToLevel {} --is16Bit {} --SendEmail {} "
    #     "-- YourEmail {} > {}".format(dicom_images_path, png_path, depth, False, True, processes, 
    #     'series', True, email_flag, 'aredd30@emory.edu', logs_path+'png_extraction_'+folder_name+'.out'), shell=True)

    # # dicom anonymization
    # dicom_anon_path = master_path+folder_name+'/dicom_anon/'
    # os.makedirs(dicom_anon_path, exist_ok=True)

    # subprocess.call("python3 ../dicom-anonymization/DicomAnonymizer.py {} {} > {}".format(dicom_images_path, 
    #         dicom_anon_path, logs_path+'dicom_anon_'+folder_name+'.out'), shell=True)

    # # metadata anonymization
    # metadata_path = png_path+'meta/'
    # metadata_anon_path = master_path+folder_name+'/metadata_anon/'
    # os.makedirs(metadata_path, exist_ok=True)
    # os.makedirs(metadata_anon_path, exist_ok=True)

    # for i, file in enumerate(metadata_path):
    #     metadata_filename = 'metadata_{}.csv'.format(i)
    #     metadata_filepath = metadata_path+metadata_filename

    #     anon_metadata_filename = 'metadata_anon_{}.csv'.format(i)
    #     anon_metadata_filepath = metadata_anon_path+anon_metadata_filename

    #     subprocess.call("python3 metadata_anonymization.py {} {} > "
    #         "{}".format(metadata_filepath, anon_metadata_filepath, 
    #         logs_path+'metadata_anonymization_'+folder_name+'.out'), shell=True)

if __name__ == "__main__":

    with open('config.json', 'r') as f:
        config = json.load(f)

    depth = int(config['Depth'])
    file_path = config['FilePath']
    master_path = config['MasterPath']
    processes = int(config['UseProcesses'])
    csv_file = config['CsvFile']
    total_attributes = int(config['NumberOfQueryAttributes'])
    first_attribute = config['FirstAttr']
    first_index = config['FirstIndex']
    second_attribute = config['SecondAttr']
    second_index = config['SecondIndex']
    email_flag = config['SendEmail']
    email = config['YourEmail']
    folder_name = config['FolderName']

    if not os.path.exists(master_path):
        os.makedirs(master_path, exist_ok=True)

    workflow(depth, file_path, master_path, processes, csv_file, total_attributes, first_attribute, first_index, second_attribute, 
            second_index, email_flag, email, folder_name)



