# -*- coding: utf-8 -*-
from dataImport import outputFileHeader

# Export Parameters
ExportID = input("Insert a Callsign or ID for export files: ")
ResultsExportFile = ExportID + "-Results.csv"
LogExportFile = ExportID + "-Log.csv"

# instantiatefiles instantiates log and export files
def instantiateFiles():
    f = open(ResultsExportFile,"w")
    f.write(outputFileHeader)
    f.close()
    f = open(LogExportFile,"w")
    f.close()
    
# appendToResultsCsv appends a row to results
def appendToResultsCsv(row):
    with open(ResultsExportFile,'a') as f:
        f.write(row)
        
# appendToLogCsv appends a row top log
def appendToLogCsv(row):
    with open(LogExportFile,'a') as f:
        f.write(row)
