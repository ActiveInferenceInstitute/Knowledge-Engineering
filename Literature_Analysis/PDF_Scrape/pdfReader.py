# -*- coding: utf-8 -*-

from PyPDF2 import PdfFileReader

# extractPDFtext extracts the full text of a pdf
def extractPDFtext(filePath):
    reader = PdfFileReader(filePath)
    text = ""
    for page in reader.pages:
        text+= page.extractText()
    return text
        
# test 
# x = extractPDFtext("resc/pdfList/00048.pdf")