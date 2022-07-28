import os
import sys
import argparse
script_dir = os.path.dirname( __file__ )
module_dir=os.path.join(script_dir,"..","..","..","png-extraction")
print("script_dir is:",module_dir)
sys.path.append( module_dir )
import ImageExtractor

ap = argparse.ArgumentParser()
ap.add_argument("--DICOMHome")
ap.add_argument("--OutputDirectory")
ap.add_argument("--Depth")
ap.add_argument("--SplitIntoChunks")
ap.add_argument("--PrintImages")
ap.add_argument("--CommonHeadersOnly")
ap.add_argument("--UseProcesses")
ap.add_argument("--FlattenedToLevel")
ap.add_argument("--is16Bit")
ap.add_argument("--SendEmail")
ap.add_argument("--YourEmail")
ap.add_argument("--PublicHeadersOnly")
ap.add_argument("--SpecificHeadersOnly")
args = vars(ap.parse_args())
ImageExtractor.initialize_config_and_execute(args)