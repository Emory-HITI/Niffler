import os, glob
import sys
import logging
import pydicom as pyd
import shutil

def modality_split(cold_extraction_path, modality_split_path):
    # iterating through all the files in cold extraction
    for root, dirs, files in os.walk(cold_extraction_path):
        for file in files:
            if file.endswith('.dcm'):
                dcm_filename = root+'/'+file
                dcm_path = '/'.join(dcm_filename.split('/')[5:])
                dcm_only_folder = '/'.join(dcm_path.split('/')[:-1])
                dcm_file = pyd.dcmread(dcm_filename)
                dcm_modality = dcm_file.Modality

                # print (dcm_modality, dcm_only_folder)
                isExist = os.path.exists(modality_split_path+str(dcm_modality)+'/'+str(dcm_only_folder))
                if not isExist:
                    os.makedirs(modality_split_path+str(dcm_modality)+'/'+str(dcm_only_folder))
                print (cold_extraction_path+str(dcm_path), modality_split_path+str(dcm_modality)+'/'+str(dcm_only_folder)+'/'+str(dcm_path.split('/')[-1]))
                shutil.copy2(src=cold_extraction_path+str(dcm_path), dst=modality_split_path+str(dcm_modality)+'/'+str(dcm_only_folder)+'/'+str(dcm_path.split('/')[-1]))

if __name__ == "__main__":
    cold_extraction_path = sys.argv[1]
    modality_split_path = sys.argv[2]
    print ('Starting Modality Grouping')
    modality_split(cold_extraction_path, modality_split_path)
