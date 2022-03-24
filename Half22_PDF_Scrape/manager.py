# -*- coding: utf-8 -*-

from dataImport import FileInfoList
from docResults import docResults
import streamingExport as export


# mrManager is just a "manager" for allowing three-line implementation
class mrManager:
    def __init__(self):
        self.keyring = []
    # giveKeys provides the manager with a specific list of doc-keys to check
    def giveKeys(self, keys):
        self.keyring = keys
    # getKeys leaves the manager to retrieve all the doc-keys available
    def getKeys(self):
        self.keyring = FileInfoList.keys()
    def run(self):
        export.instantiateFiles()
        for key in self.keyring:
            print("---------------\n\n\nAttempting: "+key,"\n-------------\n")
            try:
                export.appendToResultsCsv(docResults(FileInfoList[key]).toCSV() + "\n")
                print("---------------\n\nSucceeded: "+key,"\n-------------\n")
            except:
                export.appendToLogCsv(key+", failed\n")
                print("---------------\n\nFailed: "+key,"\n-------------\n")
            
    def close(self):
        pass
        #f = open("testrun.csv", "w", encoding="utf-8")
        #f.write(self.csvString)
        #f.close()
            
        
m = mrManager()
m.getKeys()
m.run()