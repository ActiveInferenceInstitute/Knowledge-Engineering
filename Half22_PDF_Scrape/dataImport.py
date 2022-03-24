# -*- coding: utf-8 -*-

from csv import reader

# addZeros adds zeros to match file nomenclature
def formatFileId(fileId):
    n = len(str(fileId))
    nFileId = ""
    for i in range(5-n):
        nFileId += "0"
    return nFileId+str(fileId)


# genOutPutHeader creates a header for output csv file
def genOutPutHeader(kwlist):
    row = "FileId,"
    for kw in kwlist.keys():
        row+= "ft_"+kw+","
    for kw in kwlist.keys():
        row+= "ab_"+kw+","
    return row


# getKws pulls keyword list from keywords.csv, and returns in list form
def getKws():
    kwlist = dict()
    with open("resc/params/keywords.csv", 'r',encoding="utf-8") as fileInfo:
        r = reader(fileInfo)
        next(r)
        for row in r:
            kwlist[row[0]]=""
    return kwlist

# getFileInfo pulls paper information from fileInfo.csv and returns a dict
# in the form [fileId]:docImport
def getFileInfo():
    tempDict = dict()
    with open("resc/params/fileInfo.csv", 'r',encoding="utf-8") as fileInfo:
        r = reader(fileInfo)
        next(r)
        for row in r:
            tempDict[formatFileId(row[0])] = docImport(row[0], row[1], row[2])
    return tempDict

# docImport is a container for paper information available prior to pdf
# extraction
class docImport:
    def __init__(self, fileId, title, abstract):
        fileId = formatFileId(fileId)
        self.fileId = fileId # already formatted
        self.title = title
        self.abstract = abstract
        self.filePath = ("resc/pdfList/" + fileId + ".pdf")
        
# constants for import
KwList = getKws()
FileInfoList = getFileInfo()
outputFileHeader = genOutPutHeader(KwList) + "\n"


