import os
import sys
import argparse
import pandas
script_dir = os.path.dirname( __file__ )
module_dir=os.path.join(script_dir,"..","..","..","suvpar")
print("script_dir is:",module_dir)
sys.path.append( module_dir )
import Suvpar

ap = argparse.ArgumentParser()
ap.add_argument("--InputFile")
ap.add_argument("--OutputFile")
ap.add_argument("--FeaturesetFile")
config = vars(ap.parse_args())
global output_csv, df
Suvpar.feature_file = config['FeaturesetFile']
Suvpar.filename = config['InputFile']
Suvpar.output_csv = config['OutputFile']

Suvpar.text_file = open(Suvpar.feature_file, "r")
Suvpar.feature_list = Suvpar.text_file.read().split('\n')

Suvpar.df = pandas.read_csv(Suvpar.filename, usecols=lambda x: x in Suvpar.feature_list, sep=',')
Suvpar.suvpar()
Suvpar.write()