import os, os.path
import json
import subprocess

def workflow(depth, master_path, processes, csv_file, total_attributes, first_attribute, first_index, second_attribute, 
            second_index, email_flag, email, folder_name):

    dicom_images_path = master_path+str(folder_name)+'/cold_extraction_accession_number/'
    os.makedirs(dicom_images_path, exist_ok=False)
    subprocess.call('chmod -R 777 {}'.format(dicom_images_path))

    logs_path = master_path+'logs/'
    os.makedirs(logs_path, exist_ok=False)
    subprocess.call('chmod -R 777 {}'.format(logs_path))

    # cold extraction
    subprocess.call('chmod 777 {}'.format(csv_file))
    subprocess.call('nohup python3 ../cold-extraction/ColdDataRetriver.py --StorageFolder {} --CsvFile {} \
        --NumberOfQueryAttributes {} --FirstAttr {} --FirstIndex {} --SecondAttr {} --SecondIndex {} --SendEmail {} \
        --YourEmail {} > {}'.format(dicom_images_path, csv_file, total_attributes, first_attribute, first_index, 
        second_attribute, second_index, email_flag, email,logs_path+'cold_extraction_'+folder_name+'.out'))

    # png extraction
    png_path = master_path+folder_name+'/png_images/'
    os.makedirs(png_path, exist_ok=False)
    subprocess.call('chmod 777 {}'.format(png_path))

    subprocess.call('nohup python3 ../png-extraction/ImageExtractor.py --DICOMHome {} --OutputDirectory {}, --Depth {} \
        --PrintImage {} --CommonHeadersOnly {} --UseProcesses {} --FlattenedToLevel {} --is16Bit {} --SendEmail {} \
        -- YourEmail {} > {}'.format(dicom_images_path, png_path, depth, False, True, processes, 
        'series', True, email_flag, 'aredd30@emory.edu', logs_path+'png_extraction_'+folder_name+'.out'))

    # dicom anonymization
    dicom_anon_path = master_path+folder_name+'/dicom_anon/'
    os.makedirs(dicom_anon_path, exist_ok=False)
    subprocess.call('chmod -R 777 {}'.format(dicom_anon_path))

    subprocess.call('nohup python3 ../dicom-anonymization/DicomAnonymizer.py {} {} > {}'.format(dicom_images_path, 
            dicom_anon_path, logs_path+'dicom_anon_'+folder_name+'.out'))

    # metadata anonymization
    metadata_path = png_path+'meta/'
    metadata_anon_path = master_path+folder_name+'/metadata_anon/'
    os.makedirs(metadata_anon_path, exist_ok=False)
    subprocess.call('chmod -R 777 {}'.format(metadata_anon_path))

    subprocess.call('nohup python3 metadata_anonymization.py {} {} > \
        {}'.format(metadata_path, metadata_anon_path, logs_path+'metadata_anonymization_'+folder_name+'.out'))

if __name__ == "__main__":

    with open('config.json', 'r') as f:
        config = json.load(f)

    depth = int(config['Depth'])
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
        os.makedirs(master_path)
        subprocess.call('chmod -R 777 {}'.format(master_path))

    workflow(depth, master_path, processes, csv_file, total_attributes, first_attribute, first_index, second_attribute, 
            second_index, email_flag, email, folder_name)



