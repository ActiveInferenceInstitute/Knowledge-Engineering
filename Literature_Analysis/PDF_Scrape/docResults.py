# -*- coding: utf-8 -*-

# separate body, abstract, and citations

from pdfReader import extractPDFtext
from dataImport import KwList, normalizeText

# kwResults is a container for results of keyword search of a doc
class kwResults:
    def __init__(self):
        self.FullTextCount = dict() # map for holding [kw]:count in full text
        self.AbstractCount = dict() # map for holding [kw]:count in abstract
        for kw in KwList.keys(): # instantiate each keyword with a count of 0
            self.FullTextCount[kw] = 0 # for kws in full text
            self.AbstractCount[kw] = 0 # for kws in abstract
    # update the total count of the kw found in abstract
    def addAbstractCount(self, kw, count):
        self.AbstractCount[kw] = count
    # update the total count of the kw found in full text
    def addFullTextCount(self, kw, count):
        self.FullTextCount[kw] = count
    # Push result to a csv row format
    def toCSV(self):
        row = ""
        for key in KwList.keys():
            row+= str(self.FullTextCount[key]) + ","
        for key in KwList.keys():
            row+= str(self.AbstractCount[key]) + ","
        return row

# docResults is a manager for handling keyword search within a doc
class docResults:
    def __init__(self,doc):
        self.doc = doc # doc  class - dataImport.docImport 
        self.kws = kwResults() # load up KwList
        # Flatten both sources once, using the same normalization as keywords.
        self.fulltext = normalizeText(extractPDFtext(self.doc.filePath))
        self.abstract = normalizeText(self.doc.abstract)
        self.countKws()
    def countKws(self):
        for kw in KwList.keys():
            self.kws.addFullTextCount(kw, self.fulltext.count(kw))
            self.kws.addAbstractCount(kw, self.abstract.count(kw))
    def toCSV(self):
        row = self.doc.fileId + ","
        row += self.kws.toCSV()
        return row

