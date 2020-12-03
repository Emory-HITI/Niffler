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

#%%CHANGE THESE FOR YOUR USE
print_images=True #do you want to print the images from these dicom files?
print_only_common_headers=False #do you want the resulting dataframe csv to contain only the common headers? See section 'find common fields'

root = '/opt/localdrive/'     #the root directory for yor project
dicomHome = root + 'dicom-files/' #the folder containing your dicom files

png_destination = root + 'extracted-images/' #where you want the extracted images to print
csvDestination = root + 'metadata.csv' #where you want the dataframe csv to print

mappings= root + 'mapping.csv'
failed = root +'failed-dicom/'

LOG_FILENAME = root + 'ImageExtractor.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

#%%Function for getting tuple for field,val pairs for this file
#plan is instance of dicom class, the data for single mammo file
def get_tuples(plan, outlist = None, key = ""):
    if len(key)>0:
        key =  key + "_"
    if not outlist:
        outlist = []
    for aa  in plan.dir():
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



#%% get set up to create dataframe
dirs = os.listdir( root )
#gets all dicom files. if editing this code, get filelist into the format of a list of strings, 
#with each string as the file path to a different dicom file.

filelist=glob.glob(dicomHome + '*/*/*.dcm', recursive=True) #this searches the folders at the depth we request and finds all dicoms

logging.info('Number of dicom files: ' + str(len(filelist)))

ff = filelist[0] #load first file as a templat to look at all 
plan = dicom.dcmread(ff, force=True) 

logging.debug('Loaded the first file successfully')
#print(type(plan)) #is recorded as pydicom class, has attributes numerated in keys
#print(plan.dir()) #lists class attributes
keys = [(aa) for aa in plan.dir() if (hasattr(plan, aa) and aa!='PixelData')]
#print(keys) keys are attributes in this instance of the dicom class from the source file

#%%checks for images in fields and prints where they are
for field in plan.dir():
    if (hasattr(plan, field) and field!='PixelData'):
        entry = getattr(plan, field)
        #print(field)        #prints header
        #print(str(entry))   #prints associated value
        if type(entry) is bytes:
            print(field)
            print(str(entry))
            

#set([ type(getattr(plan, field)) for field in plan.dir() if (hasattr(plan, field) and field!='PixelData')])
#print(plan)
fm = open(mappings, "w+")
filemapping = 'Original dicom file location, jpeg location \n'
fm.write(filemapping)
#%%step through whole file list, read in file, append fields to future dataframe of all files
headerlist = []
for nn, ff in enumerate(filelist):
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
    headerlist.append(dict(kv)) #appends all of the field,val pairs for the files to list of all files
    
#make dataframe containing all fields and all files
df = pd.DataFrame(headerlist)

#print(df.columns) #all fields
logging.info('Number of fields per file: ' + str(len(df.columns)))


#%%find common fields
mask_common_fields = df.isnull().mean() < 0.1 #find if less than 10% of the rows in df are missing this column field
common_fields = set(np.asarray(df.columns)[mask_common_fields]) #define the common fields as those with more than 90% filled


#print(headerlist) #list of all field,value arguments for all data
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
export_csv = data.to_csv (csvDestination, index = None, header=True) 

fields=df.keys()

count = 0;
#%% print images
if print_images:
    filedata=data
    
    for i in range(len(filedata)):
        ds = dicom.dcmread(filedata.iloc[i].loc['file'], force=True) #read file in
        try:
            im=ds.pixel_array #pull image from read dicom
            ID=filedata.iloc[i].loc['PatientID'] #get patientID ex: BAC_00040
            folderName = hashlib.sha224(ID.encode('utf-8')).hexdigest()
        
            imName=os.path.split(filedata.iloc[i].loc['file'])[1][:-4] #get file name ex: IM-0107-0022
            #check for existence of patient folder, create if needed
            if not (os.path.exists(png_destination + folderName)):
                os.mkdir(png_destination+folderName)
        
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
            fm.write(filemapping)
        except AttributeError as error:
            logging.error(error)
            count = count + 1
            logging.error(str(count) + ' out of ' + str(len(filelist)) + ' dicom images have failed extraction.')
            copyfile(filedata.iloc[i].loc['file'], failed + '1/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm')
        except ValueError as error:
            logging.error(error)
            count = count + 1
            logging.error(str(count) + ' out of ' + str(len(filelist)) + ' dicom images have failed extraction.')
            copyfile(filedata.iloc[i].loc['file'], failed + '2/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm')
        except:
            logging.error("Unexpected error occurred")
            count = count + 1
            logging.error(str(count) + ' out of ' + str(len(filelist)) + ' dicom images have failed extraction.')
            copyfile(filedata.iloc[i].loc['file'], failed + '3/' + os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm')
fm.close()
