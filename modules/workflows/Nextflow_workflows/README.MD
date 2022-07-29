# Mega-workflow: 
Mega-workflow chains Cold_extraction, Png_extraction, Suvpar, DicomAnonymization and MetaDataAnonymization together. Mega-workflow contains 8 different workflows. User can choose the workflow by changing the workflow parameter in nextflow.config as mentioned below:

* Cold_extraction->Png_extraction->Suvpar->DicomAnonymization->MetaDataAnonymization = 1

* Cold_extraction->Png_extraction->Suvpar = 2

* Cold_extraction->Png_extraction->DicomAnonymization = 3

* Cold_extraction->Png_extraction->MetaDataAnonymization = 4

* Png_extraction->Suvpar->DicomAnonymization->MetaDataAnonymization = 5

* Png_extraction->Suvpar = 6

* Png_extraction->DicomAnonymization = 7

* Png_extraction->MetaDataAnonymization = 8



Steps to use this workflow:
  1. ```pip install requirements.txt``` 
  2. Modify nextflow.config. DICOMHome and depth parameters are only needed for workflows 5,6,7,8.
  3. Run the command ``` nextflow run cold_png_suvpar.nf ```

Make sure that nextflow is installed. If you have run ./install.sh then nextflow would be installed on your computer if not run the following commands:
 ```
 wget -qO- https://get.nextflow.io | bash
 ```
 ```
 sudo mv nextflow /usr/local/bin
 ```
 If HITI_anon_internal is not installed, run ``` pip install -i https://test.pypi.org/simple/ HITI-anon-internal ```
