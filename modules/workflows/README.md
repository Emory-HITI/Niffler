# A Workflow Module for Niffler

The workflow module in niffler combines other modules such as cold extraction, modality splitting, png extraction, dicom anonymization and metadata anonymization. This modules executes and the above mentioned modules in a serial manner. The module is intended to reduce the human intervention in the process and extracting and handling DICOM Images. 

The module currently do not offer felixbility to run all the above mentioned modules through a configuration file and requires editing the *workflow.py* file. Configuring the modules in *workflow.py* is same as configuring the configuration files in the indivudual modules and is not mentioned in this module. However, configuring *modality splitting* and *metadata anonymization* were mentioned as they were not documented in the Niffler repository.

# Configuring the Workflow File

* Configuring Cold Extraction - https://github.com/Emory-HITI/Niffler/blob/master/modules/cold-extraction/README.md
* Configuring Modality Splitting
```
**cold_extraction_path** : Set the path of the extracted DICOMs. These DICOMs are usually extracted using cold extraction module.
**modality_split_path** : Set the path of the resulting files. After the extraction, this folder will have mutiple sub-folders.
```
* Configuring PNG Extraction - https://github.com/Emory-HITI/Niffler/blob/master/modules/png-extraction/README.md
* Configuring DICOM Anonymization - https://github.com/Emory-HITI/Niffler/blob/master/modules/dicom-anonymization/README.md
* Configuring Metadata Anonymization
```
**metadata_path** : Set the complete path of the metadata file to be anonymized. The file should be in CSV format.
**anon_metadata_path** : Set the path of the resulting anonymized metadata file.
```

PS - Though the cold extraction module is integrated in the workflow module. It is currently causing issues by messing with the flow of other modules and is not being used in this module.
