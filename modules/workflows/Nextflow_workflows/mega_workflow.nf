pd=projectDir

process makedir{
	output:
		stdout into makedir_out
	script:
"""
#!/usr/bin/python3
import os
if not os.path.exists("$params.OutputDirectory"):
    os.makedirs("$params.OutputDirectory")
if not os.path.exists("$params.OutputDirectory/workflow_results"):
    os.makedirs("$params.OutputDirectory/workflow_results")
if not os.path.exists("$params.OutputDirectory/workflow_results/cold_extraction_results") and ($params.workflow==1 or $params.workflow==2 or $params.workflow==3 or $params.workflow==4) :
    os.makedirs('$params.OutputDirectory/workflow_results/cold_extraction_results')
if not os.path.exists('$params.OutputDirectory/workflow_results/png_extraction_results'):
    os.makedirs('$params.OutputDirectory/workflow_results/png_extraction_results')
if not os.path.exists('$params.OutputDirectory/workflow_results/suvpar_resuts') and ($params.workflow==1 or $params.workflow==2 or $params.workflow==5) :
        os.makedirs('$params.OutputDirectory/workflow_results/suvpar_resuts')
if not os.path.exists('$params.OutputDirectory/workflow_results/DicomAnon_resuts') and ($params.workflow==1 or $params.workflow==3 or $params.workflow==6):
        os.makedirs('$params.OutputDirectory/workflow_results/DicomAnon_resuts')
if not os.path.exists('$params.OutputDirectory/workflow_results/metaAnon_resuts') and ($params.workflow==1 or $params.workflow==4 or $params.workflow==7):
        os.makedirs('$params.OutputDirectory/workflow_results/metaAnon_resuts')
x=str("$params.FilePath")
depth=len(x.split("/"))-1
print(depth)
	"""
}

process cold_extraction{
	input:
		val dept from makedir_out
	output: 
		val dept into cold_extraction_out
	when:
		params.workflow==1 || params.workflow==2 || params.workflow==3 || params.workflow==4
	script:
	"""
	python3 $pd/src/cold_extraction.py --StorageFolder $params.OutputDirectory/workflow_results/cold_extraction_results --FilePath $params.FilePath --CsvFile $params.CsvFile --NumberOfQueryAttributes $params.NumberOfQueryAttributes --FirstAttr $params.FirstAttr --FirstIndex $params.FirstIndex --SecondAttr $params.SecondAttr --SecondIndex $params.SecondIndex --ThirdAttr $params.ThirdAttr --ThirdIndex $params.ThirdIndex --DateFormat $params.DateFormat --SendEmail $params.SendEmail  --YourEmail $params.YourEmail --DCM4CHEBin $params.DCM4CHEBin --SrcAet $params.SrcAet --QueryAet $params.QueryAet --DestAet $params.DestAet --NightlyOnly $params.NightlyOnly --StartHour $params.StartHour --EndHour $params.EndHour --NifflerID $params.NifflerID --MaxNifflerProcesses $params.MaxNifflerProcesses
	"""

}

if(params.workflow==1 || params.workflow==2 || params.workflow==3 || params.workflow==4){ 

	process png_extraction{
		input:
			val depth from cold_extraction_out
		output:
			val depth into png_ext_out
		script:
			"""
				python3 $pd/src/ImageExtractor_nextflow.py --DICOMHome $params.OutputDirectory/workflow_results/cold_extraction_results --OutputDirectory $params.OutputDirectory/workflow_results/png_extraction_results --SplitIntoChunks $params.SplitIntoChunks --PrintImages $params.PrintImages --CommonHeadersOnly $params.CommonHeadersOnly --UseProcesses $params.UseProcesses --FlattenedToLevel $params.FlattenedToLevel --is16Bit $params.is16Bit --SendEmail $params.SendEmail --YourEmail $params.YourEmail --PublicHeadersOnly $params.PublicHeadersOnly --Depth $depth
			"""
	}
}
else{
	process png_extraction2{
		input:
			val depth from makedir_out	
		output:
			val depth into png_ext_out
		script:
			"""
				python3 $pd/src/ImageExtractor_nextflow.py --DICOMHome $params.DICOMHome --OutputDirectory $params.OutputDirectory/workflow_results/png_extraction_results  --SplitIntoChunks $params.SplitIntoChunks --PrintImages $params.PrintImages --CommonHeadersOnly $params.CommonHeadersOnly --UseProcesses $params.UseProcesses --FlattenedToLevel $params.FlattenedToLevel --is16Bit $params.is16Bit --SendEmail $params.SendEmail --YourEmail $params.YourEmail --PublicHeadersOnly $params.PublicHeadersOnly --Depth $depth
			"""
	}

}


process suvpar{
	input:
		val depth from png_ext_out
	when:
		params.workflow==1 || params.workflow==2 || params.workflow==5 || params.workflow==6
	
	script:

	"""
	
	    python3 $pd/src/suvpar.py --InputFile $params.OutputDirectory/workflow_results/png_extraction_results/metadata.csv --OutputFile $params.OutputDirectory/workflow_results/suvpar_resuts/output.csv --FeaturesetFile $params.Featureset_File_for_suvpar
	
	"""

}
process dicomAnon{
	input:
		val depth from png_ext_out
	when:
		params.workflow==1 || params.workflow==3 || params.workflow==5 || params.workflow==7
	script:
	"""
		python3 $pd/../../dicom-anonymization/DicomAnonymizer2.py $params.OutputDirectory/workflow_results/cold_extraction_results $params.OutputDirectory/workflow_results/DicomAnon_resuts
	"""
}

process meta_anon{
	input:
		val depth from png_ext_out
	when:
		params.workflow==1 || params.workflow==4 || params.workflow==5 || params.workflow==8
	script:
	"""
		python3 $pd/src/metadata_anonymization.py $params.OutputDirectory/workflow_results/png_extraction_results/metadata.csv $params.OutputDirectory/workflow_results/metaAnon_resuts/output.csv
	"""
}

