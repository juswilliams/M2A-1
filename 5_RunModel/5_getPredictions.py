#!/usr/bin/python

'''
Run CNN Regressor 

Requires:
python/3.6.5+
os
time
argparse
numpy
pandas
h5py
keras
tensorflow

Input Required:
1) H5 feature file.
2) model weights

Output:
1) tab delimited file of predictions and corresponding 
	promoter regions
'''
import os
import time
import argparse
import numpy as np
import pandas as pd
import h5py
# model modules
from keras.models import load_model

#------------------------------------------------------------------------------
def parseArguments(): 
	# Create argument parser
	parser = argparse.ArgumentParser()   
	# Positional mandatory arguments
	parser.add_argument("FeatureFilePath", 
		help="Full path to feature .h5 file.", type=str)
	parser.add_argument("ModelFilePath", 
		help="Full path to model .h5 file.", type=str)
	parser.add_argument("--outFileName", help="File name to use for output", type=str)
	parser.add_argument("--outDirectory", help="Directory to write output to", default="output", type=str)
	# Parse arguments
	args = parser.parse_args()
	return args

#------------------------------------------------------------------------------
def parseInput(InFile):
	# Read h5 feature input and meta data
	SampleDataHDF = h5py.File(InFile, mode="r")
	#----------------------------------------------------------------------
	# build DF
	Cols = ["Transcript", "Gene",  "GeneName", 
				"Chr", "Start", "End", "Strand"]
	IdxList = ["EnsmblID_T", "EnsmblID_G",  "Gene", 
				"Chr", "Start", "End", "Strand"]
	MetaDF = pd.DataFrame(columns=Cols)
	for Col, Idx in zip(Cols, IdxList):
		MetaDF[Col] = np.array(SampleDataHDF[Idx])
		MetaDF[Col] = MetaDF[Col].astype(str).str.replace("b'","",regex=True)
		MetaDF[Col] = MetaDF[Col].astype(str).str.replace("'","",regex=True)
	# Test data
	TestData = np.array(SampleDataHDF["FeatureInput"])[:,:,:,[0,1,3]]
	return MetaDF, TestData

#-------------------------------------------------------------------------#
def getPredictions(MetaDF, TestData, ModelFilePath):
	# load model weights
	FitModel = load_model(ModelFilePath)
	# Return regression predictions
	PredReg = FitModel.predict(TestData, 
								batch_size=512, 
								verbose=1)
	ModelName = ".".join(ModelFilePath.split("/")[-1].split(".")[:-1])
	PredictedColumnName = "Predicted_log2_ChipDivInput_"+ModelName
	MetaDF[PredictedColumnName] = PredReg.flatten()
	return MetaDF

#------------------------------------------------------------------------------
def main(LineArgs):
	T0 = time.time()
	# Commandline args and model params
	FeatureFilePath = LineArgs.FeatureFilePath
	ModelFilePath = LineArgs.ModelFilePath
	# determine path
	Sample = ".".join(FeatureFilePath.split("/")[-1].split(".")[:-1])
	OutputFilePath = LineArgs.outDirectory
	if not os.path.exists(LineArgs.outDirectory):
		os.mkdir(LineArgs.outDirectory)
	if not LineArgs.outFileName:
		OutputFilePath += "/" + Sample+".txt"
	else:
		OutputFilePath += "/" + LineArgs.outFileName
	# parse test data, meta data
	MetaDF, TestData = parseInput(FeatureFilePath)
	# caluclate predictions
	PredictionsDF = getPredictions(MetaDF, TestData, ModelFilePath)
	# print predictions to file with meta data (positional data)
	PredictionsDF.to_csv(OutputFilePath, sep="\t", header=True, index=False)
	T1 = time.time()
	TotalTime = T1 - T0
	print ("Total time to complete,",str(TotalTime)+"s")
# Parse line arguments
if __name__ == '__main__':
	# Parse args
	LineArgs = parseArguments()
	main(LineArgs)
