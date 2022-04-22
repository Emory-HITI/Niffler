pd=projectDir

process makedir{
	output:
		stdout into cold_ext_in
	script:
"""
#!/usr/bin/python3
import os
if not os.path.exists("$params.OutputDirectory"):
    os.makedirs("$params.OutputDirectory")
if not os.path.exists("$params.OutputDirectory/workflow_results"):
    os.makedirs("$params.OutputDirectory/workflow_results")
if not os.path.exists("$params.OutputDirectory/workflow_results/cold_extraction_results"):
    os.makedirs('$params.OutputDirectory/workflow_results/cold_extraction_results')
if not os.path.exists('$params.OutputDirectory/workflow_results/png_extraction_results'):
    os.makedirs('$params.OutputDirectory/workflow_results/png_extraction_results')
if not os.path.exists('$params.OutputDirectory/workflow_results/suvpar_resuts'):
        os.makedirs('$params.OutputDirectory/workflow_results/suvpar_resuts')
x=str("$params.FilePath")
depth=len(x.split("/"))-1
print(depth)
	"""
}

process cold_extraction{
	input:
		val depth from cold_ext_in
	output:
		val depth into png_ext_in

	script:

	"""
	    python3 $pd/Modules/cold_extraction.py --StorageFolder $params.OutputDirectory/workflow_results/cold_extraction_results --FilePath $params.FilePath --CsvFile $params.CsvFile --NumberOfQueryAttributes $params.NumberOfQueryAttributes --FirstAttr $params.FirstAttr --FirstIndex $params.FirstIndex --SecondAttr $params.SecondAttr --SecondIndex $params.SecondIndex --ThirdAttr $params.ThirdAttr --ThirdIndex $params.ThirdIndex --DateFormat $params.DateFormat --SendEmail $params.SendEmail  --YourEmail $params.YourEmail --DCM4CHEBin $params.DCM4CHEBin --SrcAet $params.SrcAet --QueryAet $params.QueryAet --DestAet $params.DestAet --NightlyOnly $params.NightlyOnly --StartHour $params.StartHour --EndHour $params.EndHour --NifflerID $params.NifflerID --MaxNifflerProcesses $params.MaxNifflerProcesses
	"""

}


process png_extraction{
	input:
		val depth from png_ext_in

	output:
		stdout into suvpar_in

	script:

	"""
python3 $pd/Modules/ImageExtractor_nextflow.py --DICOMHome $params.OutputDirectory/workflow_results/cold_extraction_results --OutputDirectory $params.OutputDirectory/workflow_results/png_extraction_results  --SplitIntoChunks $params.SplitIntoChunks --PrintImages $params.PrintImages --CommonHeadersOnly $params.CommonHeadersOnly --UseProcesses $params.UseProcesses --FlattenedToLevel $params.FlattenedToLevel --is16Bit $params.is16Bit --SendEmail $params.SendEmail --YourEmail $params.YourEmail --PublicHeadersOnly $params.PublicHeadersOnly --Depth $depth
	"""
}


process suvpar{

	input:

            val inp from suvpar_in

	script:

	"""
	    python3 $pd/Modules/suvpar.py --InputFile $params.OutputDirectory/workflow_results/png_extraction_results/metadata.csv --OutputFile $params.OutputDirectory/workflow_results/suvpar_resuts/output.csv --FeaturesetFile $params.Featureset_File_for_suvpar
	"""

}


