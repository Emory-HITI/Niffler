import os
import sys
import argparse
import pandas
import logging
script_dir = os.path.dirname( __file__ )
module_dir=os.path.join(script_dir,"..","..","..","suvpar")
print("script_dir is:",module_dir)
sys.path.append( module_dir )
import Suvpar

ap = argparse.ArgumentParser()
ap.add_argument("--InputFile")
ap.add_argument("--OutputFile")
ap.add_argument("--FeaturesetFile")
ap.add_argument("--ScannerDetails")
ap.add_argument("--ScannerFilter")
ap.add_argument("--Statistics_File")
ap.add_argument("--IsStatistics")
ap.add_argument("--IsFinalCSV")
ap.add_argument("--IsAnonymized")

config = vars(ap.parse_args())
logging.basicConfig(level=logging.INFO)
Suvpar.df = {}
Suvpar.sta = {}
Suvpar.statistics_csv = {}
Suvpar.output_csv = {}


global output_csv, df,  device_SN, scanner_filter, statistics_csv, isStatistics, final_csv, isAnonymized
Suvpar.feature_file = config['FeaturesetFile']
Suvpar.filename = config['InputFile']
Suvpar.output_csv = config['OutputFile']
Suvpar.scanner_file = config['ScannerDetails']
Suvpar.scanner_filter = bool(config['ScannerFilter'])
Suvpar.statistics_csv = config['Statistics_File']
Suvpar.isStatistics = bool(config['IsStatistics'])
Suvpar.final_csv = bool(config['IsFinalCSV'])
Suvpar.isAnonymized = bool(config['IsAnonymized'])
Suvpar.text_file = open(Suvpar.feature_file, "r")
Suvpar.feature_list = Suvpar.text_file.read().split('\n')

Suvpar.df = pandas.read_csv(Suvpar.filename, usecols=lambda x: x in Suvpar.feature_list, sep=',')
Suvpar.suvpar()
Suvpar.write()
