#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code creates a dataframe of dicom headers based on dicom files in a filepath.
This code also extracts the images within those dicoms if requested. see section 'print images'
pip3 install image numpy pandas pydicom pillow pypng
Make sure to have empty extracted-images, failed-dicom/1, failed-dicom/2, failed-dicom/3 folders
ready in the root folder.
"""
import numpy as np
import pandas as pd
import pydicom as dicom #pydicom is most recent form of dicom python interface. see https://pydicom.github.io/
import png, os, glob
import PIL as pil
from pprint import pprint
import hashlib
from shutil import copyfile
import logging
from multiprocessing import Pool
import json
import sys
import subprocess
import pdb
import pickle
#pydicom imports needed to handle data errrors
from pydicom import config
from pydicom import datadict
from pydicom import values
from subprocess import Popen
import time

with open('config.json', 'r') as f:
    niffler = json.load(f)

#Get variables for StoreScp from config.json.
print_images = niffler['PrintImages']
print_only_common_headers = niffler['CommonHeadersOnly']
dicom_home = niffler['DICOMHome'] #the folder containing your dicom files
output_directory = niffler['OutputDirectory']
depth = niffler['Depth']
processes = niffler['UseProcesses'] #how many processes to use.
flattened_to_level = niffler['FlattenedToLevel']
email = niffler['YourEmail']
send_email = niffler['SendEmail']
no_splits = niffler['SplitIntoChunks']
is16Bit = niffler['is16Bit']

png_destination = output_directory + '/extracted-images/'
failed = output_directory +'/failed-dicom/'
maps_directory = output_directory + '/maps/'
meta_directory = output_directory + '/meta/'

LOG_FILENAME = output_directory + '/ImageExtractor.out'
pickle_file = output_directory + '/ImageExtractor.pickle'
# record the start time
t_start = time.time()

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

if not os.path.exists(maps_directory):
    os.makedirs(maps_directory)

if not os.path.exists(meta_directory):
    os.makedirs(meta_directory)

if not os.path.exists(png_destination):
    os.makedirs(png_destination)

if not os.path.exists(failed):
    os.makedirs(failed)

if not os.path.exists(failed + "/1"):
    os.makedirs(failed + "/1")

if not os.path.exists(failed + "/2"):
    os.makedirs(failed + "/2")

if not os.path.exists(failed + "/3"):
    os.makedirs(failed + "/3")

if not os.path.exists(failed + "/4"):
    os.makedirs(failed + "/4")

#%%Function for getting tuple for field,val pairs
def get_tuples(plan, outlist = None, key = ""):
    if len(key)>0:
        key =  key + "_"
    if not outlist:
        outlist = []
    for aa  in plan.dir():
        try:
            hasattr(plan,aa)
        except TypeError as e:
            logging.warning('Type Error encountered')
        if (hasattr(plan, aa) and aa!='PixelData'):
            value = getattr(plan, aa)
            start = len(outlist)
            #if dicom sequence extract tags from each element
            if type(value) is dicom.sequence.Sequence:
                for nn, ss in enumerate(list(value)):
                    newkey = "_".join([key,("%d"%nn),aa]) if len(key) else "_".join([("%d"%nn),aa])
                    candidate = get_tuples(ss,outlist=None,key=newkey)
                    #if extracted tuples are too big condense to a string
                    if len(candidate)>2000:
                        outlist.append((newkey,str(candidate)))
                    else:
                        outlist.extend(candidate)
            else:
                if type(value) is dicom.valuerep.DSfloat:
                    value = float(value)
                elif type(value) is dicom.valuerep.IS:
                    value = str(value)
                elif type(value) is dicom.valuerep.MultiValue:
                    value = tuple(value)
                elif type(value) is dicom.uid.UID:
                    value = str(value)
                outlist.append((key + aa, value)) #appends name, value pair for this file. these are later concatenated to the dataframe
    return outlist


def extract_headers(f_list_elem):
    nn,ff = f_list_elem # unpack enumerated list
    plan = dicom.dcmread(ff, force=True)  #reads in dicom file
    #checks if this file has an image
    c=True
    try:
        check=plan.pixel_array #throws error if dicom file has no image
    except:
        c = False
    kv = get_tuples(plan)       #gets tuple for field,val pairs for this file. function defined above
    # dicom images should not have more than 300
    if len(kv)>500:
        logging.debug(str(len(kv)) + " dicoms produced by " + ff)
    kv.append(('file',chunk[nn])) #adds my custom field with the original filepath
    kv.append(('has_pix_array',c))   #adds my custom field with if file has image
    if c:
        kv.append(('category','uncategorized')) #adds my custom category field - useful if classifying images before processing
    else:
        kv.append(('category','no image'))      #adds my custom category field, makes note as imageless
    return dict(kv)

#%%Function to extract pixel array information
#takes an integer used to index into the global filedata dataframe
#returns tuple of
# filemapping: dicom to png paths   (as str)
# fail_path: dicom to failed folder (as tuple)
# found_err: error code produced when processing
def extract_images(i):
    ds = dicom.dcmread(filedata.iloc[i].loc['file'], force=True) #read file in
    found_err=None
    filemapping = ""
    fail_path = ""
    try:
        im=ds.pixel_array #pull image from read dicom
        imName=os.path.split(filedata.iloc[i].loc['file'])[1][:-4] #get file name ex: IM-0107-0022

        if flattened_to_level == 'patient':
            ID=filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            folderName = hashlib.sha224(ID.encode('utf-8')).hexdigest()
            #check for existence of patient folder. Create if it does not exist.
            if not (os.path.exists(png_destination + folderName)): # it is completely possible for multiple proceses to run this check at same time.
                os.mkdir(png_destination + folderName)
        elif flattened_to_level == 'study':
            ID1=filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            try:
                ID2=filedata.iloc[i].loc['StudyInstanceUID']  # Unique identifier for the Study.
            except:
                ID2='ALL-STUDIES'
            folderName = hashlib.sha224(ID1.encode('utf-8')).hexdigest() + "/" + \
                         hashlib.sha224(ID2.encode('utf-8')).hexdigest()
            #check for existence of the folder tree patient/study/series. Create if it does not exist.
            if not (os.path.exists(png_destination + folderName)): # it is completely possible for multiple proceses to run this check at same time.
                os.makedirs(png_destination + folderName)
        else:
            ID1=filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            try:
                ID2=filedata.iloc[i].loc['StudyInstanceUID']  # Unique identifier for the Study.
                ID3=filedata.iloc[i].loc['SeriesInstanceUID']  # Unique identifier of the Series.
            except:
                ID2='ALL-STUDIES'
                ID3='ALL-SERIES'
            folderName = hashlib.sha224(ID1.encode('utf-8')).hexdigest() + "/" + \
                         hashlib.sha224(ID2.encode('utf-8')).hexdigest() + "/" + hashlib.sha224(ID3.encode('utf-8')).hexdigest()
            #check for existence of the folder tree patient/study/series. Create if it does not exist.
            if not (os.path.exists(png_destination + folderName)): # it is completely possible for multiple proceses to run this check at same time.
                os.makedirs(png_destination + folderName)


        pngfile = png_destination+folderName+'/' + hashlib.sha224(imName.encode('utf-8')).hexdigest() + '.png'
        dicom_path = filedata.iloc[i].loc['file']
        image_path = png_destination+folderName+'/' + hashlib.sha224(imName.encode('utf-8')).hexdigest() + '.png'
        if is16Bit: 
            # write the PNG file as a 16-bit greyscale 
            image_2d = ds.pixel_array.astype(np.double) 
            # # Rescaling grey scale between 0-255
            image_2d_scaled =  (np.maximum(image_2d,0) / image_2d.max()) * 65535.0  
            # # Convert to uint
            shape = ds.pixel_array.shape
            image_2d_scaled = np.uint16(image_2d_scaled) 
            with open(pngfile , 'wb') as png_file:
                    w = png.Writer(shape[1], shape[0], greyscale=True,bitdepth=16)
                    w.write(png_file, image_2d_scaled)
        else: 
            shape = ds.pixel_array.shape
            # # Convert to float to avoid overflow or underflow losses.
            image_2d = ds.pixel_array.astype(float)
            #
            # # Rescaling grey scale between 0-255
            image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
            #
            # # Convert to uint
            image_2d_scaled = np.uint8(image_2d_scaled)
        # # Write the PNG file
            with open(pngfile , 'wb') as png_file:
                    w = png.Writer(shape[1], shape[0], greyscale=True)
                    w.write(png_file, image_2d_scaled)
        filemapping = filedata.iloc[i].loc['file'] + ', ' + pngfile + '\n'
    except AttributeError as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '1/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except ValueError as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '2/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except BaseException as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '3/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except Exception as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '4/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    return (filemapping,fail_path,found_err)


#%%Function when pydicom fails to read a value attempt to read as
#other types.
def fix_mismatch_callback(raw_elem, **kwargs):
    try:
        values.convert_value(raw_elem.VR, raw_elem)
    except TypeError:
        for vr in kwargs['with_VRs']:
            try:
                values.convert_value(vr, raw_elem)
            except TypeError:
                pass
            else:
                raw_elem = raw_elem._replace(VR=vr)
                break  # I want to exit immediately after change is applied
    return raw_elem


def get_path(depth):
    directory = dicom_home + '/'
    i = 0
    while i < depth:
        directory += "*/"
        i += 1
    return directory + "*.dcm"

#%%Function used by pydicom.
def fix_mismatch(with_VRs=['PN', 'DS', 'IS']):
    """A callback function to check that RawDataElements are translatable
    with their provided VRs.  If not, re-attempt translation using
    some other translators.
    Parameters
    ----------
    with_VRs : list, [['PN', 'DS', 'IS']]
        A list of VR strings to attempt if the raw data element value cannot
        be translated with the raw data element's VR.
    Returns
    -------
    No return value.  The callback function will return either
    the original RawDataElement instance, or one with a fixed VR.
    """
    dicom.config.data_element_callback = fix_mismatch_callback
    config.data_element_callback_kwargs = {
        'with_VRs': with_VRs,
    }
    
fix_mismatch()
if processes == 0.5:  # use half the cores to avoid  high ram usage
    core_count = int(os.cpu_count()/2)
elif processes == 0:  # use all the cores
    core_count = int(os.cpu_count())
elif processes < os.cpu_count():  # use the specified number of cores to avoid high ram usage
    core_count = processes
else:
    core_count = int(os.cpu_count())
#%% get set up to create dataframe
dirs = os.listdir(dicom_home)
#gets all dicom files. if editing this code, get filelist into the format of a list of strings,
#with each string as the file path to a different dicom file.
file_path = get_path(depth)

if os.path.isfile(pickle_file):
    f=open(pickle_file,'rb')
    filelist=pickle.load(f)
else:
    filelist=glob.glob(file_path, recursive=True) #this searches the folders at the depth we request and finds all dicoms
    pickle.dump(filelist,open(pickle_file,'wb'))
file_chunks = np.array_split(filelist,no_splits)
logging.info('Number of dicom files: ' + str(len(filelist)))
logging.info('Number of chunks is 100 with size ' + str(len(file_chunks[0])) )

try:
    ff = filelist[0] #load first file as a template to look at all
except IndexError:
    logging.error("There is no file present in the given folder in " + file_path)
    sys.exit(1)

plan = dicom.dcmread(ff, force=True)
logging.debug('Loaded the first file successfully')

keys = [(aa) for aa in plan.dir() if (hasattr(plan, aa) and aa!='PixelData')]
#%%checks for images in fields and prints where they are
for field in plan.dir():
    if (hasattr(plan, field) and field!='PixelData'):
        entry = getattr(plan, field)
        if type(entry) is bytes:
            logging.debug(field)
            logging.debug(str(entry))
for i,chunk in enumerate(file_chunks):
    csv_destination = "{}/meta/metadata_{}.csv".format(output_directory,i)
    mappings ="{}/maps/mapping_{}.csv".format(output_directory,i)
    fm = open(mappings, "w+")
    filemapping = 'Original DICOM file location, PNG location \n'
    fm.write(filemapping)
    # add a check to see if the metadata has already been extracted
    #%%step through whole file list, read in file, append fields to future dataframe of all files
    headerlist = []
    #start up a multi processing pool
    #for every item in filelist send data to a subprocess and run extract_headers func
    #output is then added to headerlist as they are completed (no ordering is done)
    with Pool(core_count) as p:
        res= p.imap_unordered(extract_headers,enumerate(chunk))
        for i,e in enumerate(res):
            headerlist.append(e)
    data = pd.DataFrame(headerlist)
    logging.info('Chunk ' + str(i) + ' Number of fields per file : ' + str(len(data.columns)))
    #%%find common fields
    #make dataframe containing all fields and all files minus those removed in previous block
    #%%export csv file of final dataframe
    export_csv = data.to_csv (csv_destination, index = None, header=True)
    fields=data.keys()
    count = 0 #potential painpoint
    #writting of log handled by main process
    if print_images:
        logging.info("Start processing Images")
        filedata=data
        total = len(chunk)
        stamp = time.time()
        p = Pool(os.cpu_count()) 
        res = p.imap_unordered(extract_images,range(len(filedata)))
        for out in res:
            (fmap,fail_path,err) = out
            if err:
                count +=1
                copyfile(fail_path[0],fail_path[1])
                err_msg = str(count) + ' out of ' + str(len(chunk)) + ' dicom images have failed extraction'
                logging.error(err_msg)
            else:
                fm.write(fmap)
    fm.close()
    logging.info('Chunk run time: %s %s', time.time() - t_start, ' seconds!')


logging.info('Generating final metadata file')

#identify the 
col_names=  set()
metas = glob.glob( "{}*.csv".format(meta_directory))
#for each meta  file identify the columns that are not na's for 90% of data 
for meta in metas:
    m = pd.read_csv(meta,dtype='str')
    d_len = m.shape[0]
    interest_names = [e for e in m.columns  if  ( (m[e]. isna()==True).sum() /d_len ) <.9  ]  #count if percentage > .9 
    col_names.update(interest_names)
#load every metadata file using only valid columns 
meta_list = list()
for meta in metas:
    m = pd.read_csv(meta,dtype='str',usecols=col_names)
    meta_list.append(m)
merged_meta = pd.concat(meta_list,ignore_index=True)
merged_meta.to_csv('{}/metadata.csv'.format(output_directory),index=False)
#getting a single mapping file
logging.info('Generatign final mapping file')
mappings = glob.glob("{}/maps/*.csv".format(output_directory))
map_list = list()
for mapping in mappings:
    map_list.append(pd.read_csv(mapping,dtype='str'))
merged_maps = pd.concat(map_list,ignore_index=True)
if print_only_common_headers:
    mask_common_fields = merged_maps.isnull().mean() < 0.1
    common_fields = set(np.asarray(merged_maps.columns)[mask_common_fields])
    merged_maps = merged_maps[common_fields]
merged_maps.to_csv('{}/mapping.csv'.format(output_directory),index=False)


if send_email:
    subprocess.call('echo "Niffler has successfully completed the png conversion" | mail -s "The image conversion has been complete" {0}'.format(email), shell=True)
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')
