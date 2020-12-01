# The PNG Extractor

The PNG Extractor converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.

## Configuring the PNG Extractor

A few parameters should be set in the Python class:

root = '/opt/localdrive/'     #the root directory for yor project

dicomHome = root + 'dicom-files/' #the folder containing your dicom files

Make sure to have empty extracted-images, failed-dicom/1, failed-dicom/2, failed-dicom/3 folders 

ready in the root folder.

## The output files

### PNG files

The png destination denotes where the png outcomes are stored

png_destination = root + 'extracted-images/' #where you want the extracted images to print


### CSV file for Metadata

The csv destination file stores all the metadata upon the png conversion in a csv format.

csvDestination = root + 'metadata.csv' #where you want the dataframe csv to print

### Mappings CSV file

The mappings csv file produces the original dicom file -> png location

mappings= root + 'mapping.csv'


### Failed conversions

A failed files folder stores the DICOM files that fail the PNG conversion in a separate folder.

failed = root +'failed-dicom/'
