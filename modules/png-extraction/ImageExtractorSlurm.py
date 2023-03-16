#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time 
import pdb 
import numpy as np
import pandas as pd
import pydicom as dicom #pydicom is most recent form of dicom python interface. see https://pydicom.github.io/
import png, os, glob
import PIL as pil
from pprint import pprint
import hashlib
from shutil import copyfile
import logging
import json
import pickle 
from multiprocessing import Pool
from pydicom import config
from pydicom import datadict
from pydicom import values

#things needed for the slurm task array 
task_id = int(os.environ['SLURM_ARRAY_TASK_ID'] )
num_task = int(os.environ['SLURM_ARRAY_TASK_COUNT'])

with open('config.json', 'r') as f:
    niffler = json.load(f)

#Get variables for StoreScp from config.json.
print_images = niffler['PrintImages'] 
print_only_common_headers = niffler['CommonHeadersOnly'] 
dicom_home = niffler['DICOMHome'] #the folder containing your dicom files
output_directory = niffler['OutputDirectory']
depth = niffler['Depth']
half_mode = niffler['UseHalfOfTheProcessorsOnly'] #use only half of the available processors.
email = niffler['YourEmail']
send_email = niffler['SendEmail']

png_destination = output_directory + '/extracted-images/' 
failed = output_directory +'/failed-dicom/'

csv_destination = output_directory + '/metadata_'+str(task_id)+'.csv'
mappings= output_directory + '/mapping_'+str(task_id)+'.csv'
LOG_FILENAME = output_directory + '/ImageExtractor_'+str(task_id)+'.out'
pickle_file = output_directory +'/ImageExtractor.pickle'

# record the start time
t_start = time.time()

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

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
            if type(value) is dicom.sequence.Sequence:
                for nn, ss in enumerate(list(value)):
                    newkey = "_".join([key,("%d"%nn),aa]) if len(key) else "_".join([("%d"%nn),aa])
                    outlist.extend(get_tuples(ss, outlist = None, key = newkey))
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
    kv.append(('file',filelist[nn])) #adds my custom field with the original filepath
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
        ID=filedata.iloc[i].loc['PatientID'] #get patientID ex: BAC_00040
        folderName = hashlib.sha224(ID.encode('utf-8')).hexdigest()
    
        imName=os.path.split(filedata.iloc[i].loc['file'])[1][:-4] #get file name ex: IM-0107-0022
        #check for existence of patient folder, create if needed
        if not (os.path.exists(png_destination + folderName)): # it is completely possible for multiple proceses to run this check at this time. 
            os.mkdir(png_destination+folderName)              # TODO: ADD TRY STATEMENT TO FAIL GRACEFULY
    
        shape = ds.pixel_array.shape

        # Convert to float to avoid overflow or underflow losses.
        image_2d = ds.pixel_array.astype(float)

        # Rescaling grey scale between 0-255
        image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0

        # Convert to uint
        image_2d_scaled = np.uint8(image_2d_scaled)

        pngfile = png_destination+folderName+'/' +imName +'.png'

        # Write the PNG file
        with open(pngfile , 'wb') as png_file:
            w = png.Writer(shape[1], shape[0], greyscale=True)
            w.write(png_file, image_2d_scaled)
            
        filemapping = filedata.iloc[i].loc['file'] + ', ' + pngfile + '\n'
    except AttributeError as error:
        found_err = error
        fail_path = filedata.iloc[i].loc['file'], failed + '1/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except ValueError as error:
        found_err = error
        fail_path = filedata.iloc[i].loc['file'], failed + '2/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except BaseException as error: 
        found_err = error
        fail_path = filedata.iloc[i].loc['file'], failed + '3/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except:
        found_err = error
        fail_path = filedata.iloc[i].loc['file'], failed + '4/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    return (filemapping,fail_path,found_err)


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
                break  # i want to exit immediately after change is applied 
    return raw_elem


def get_path(depth):
    directory = dicom_home + '/'

    i = 0;
    while i < depth:
        directory += "*/"
        i += 1

    return directory + "*.dcm"


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

#%% get set up to create dataframe
dirs = os.listdir(dicom_home)

file_path = get_path(depth)

#gets all dicom files. if editing this code, get filelist into the format of a list of strings, 
#with each string as the file path to a different dicom file.
if os.path.isfile(pickle_file):
    f= open(pickle_file, 'rb')
    filelist = pickle.load(f)
else:
    filelist=glob.glob(file_path, recursive=True) #this searches the folders at the depth we request and finds all dicoms
    pickle.dump(filelist,open(pickle_file,'wb'))

logging.info('Number of dicom files: ' + str(len(filelist)))
file_split = np.array_split(filelist,num_task)
filelist = file_split[task_id]
ff = filelist[0] #load first file as a templat to look at all 
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
            

#set([ type(getattr(plan, field)) for field in plan.dir() if (hasattr(plan, field) and field!='PixelData')])
#print(plan)
fm = open(mappings, "w+")
filemapping = 'Original dicom file location, jpeg location \n'
fm.write(filemapping)
#%%step through whole file list, read in file, append fields to future dataframe of all files
headerlist = []
#start up a multi processing pool 
p = Pool(15)
stamp = time.time()
res= p.imap_unordered(extract_headers,enumerate(filelist))
for i,e in enumerate(res):
    if i %100 ==0: 
        print(stamp-time.time())
        stamp= time.time()
    headerlist.append(e)
p.close()
p.join()
#Assuming that the context manager handles closing for me 
#make dataframe containing all fields and all files
df = pd.DataFrame(headerlist)

#print(df.columns) #all fields
logging.info('Number of fields per file: ' + str(len(df.columns)))


#%%find common fields
mask_common_fields = df.isnull().mean() < 0.1 #find if less than 10% of the rows in df are missing this column field
common_fields = set(np.asarray(df.columns)[mask_common_fields]) #define the common fields as those with more than 90% filled


for nn,kv in enumerate(headerlist):
    #print(kv)                #all field,value tuples for this one in headerlist
    for kk in list(kv.keys()):
        #print(kk)            #field names
        if print_only_common_headers:
            if kk not in common_fields:  #run this and next line if need to see only common fields
                kv.pop(kk)        #remove field if not in common fields
        headerlist[nn] = kv   #return altered set of field,value pairs to headerlist

#make dataframe containing all fields and all files minus those removed in previous block
data=pd.DataFrame(headerlist)

#%%export csv file of final dataframe
export_csv = data.to_csv(csv_destination, index = None, header=True) 

fields=df.keys()

#current assumption is that processes will have acces to global variables 
#meaning that i can get away with ismple just call imap on the range of indices to idne 
#%% print images

#todo: in consumer loop add sgment that checks if an error has occured and updates error count 
if print_images:
    filedata=data
    count =0 
    other =0 
    total = len(filelist)
    stamp = time.time()
    p = Pool(15)
    res = p.imap_unordered(extract_images,range(len(filedata)) )
    for out in res: 
        if other %100 ==0:
            print(time.time()-stamp)
            stamp = time.time()
        (fmap,fail_path,err) = out 
        other +=1
        if err: 
            count +=1 
            copyfile(fail_path[0],fail_path[1]) 
            err_msg = str(count) + 'out of' + str(len(filelist)) + ' dicom images have failed extraction' 
            logging.error( err_msg)
        else: 
            fm.write(fmap)
    p.close()
    p.join()              
fm.close()
#insert multiprocessing call here     
#for i in range(len(filedata)):
# todo: for cases where erorr is not none 
# add this: error_msg = str(count) + ' out of ' + str(len(filelist)) + ' dicom images have failed extraction.')

if send_email:
    subprocess.call('echo "Niffler has successfully completed the png conversion" | mail -s "The image conversion has been complete" {0}'.format(email), shell=True)

# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')
