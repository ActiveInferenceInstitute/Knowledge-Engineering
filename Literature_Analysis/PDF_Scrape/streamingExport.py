# -*- coding: utf-8 -*-
from csv import writer

from dataImport import outputFileHeader

# Export parameters are resolved lazily on first use so that importing this
# module (e.g. from manager.py) does not block on an interactive prompt.
ExportID = None
ResultsExportFile = None
LogExportFile = None


# setExportId configures the export files from a caller-supplied callsign
def setExportId(callsign):
    global ExportID, ResultsExportFile, LogExportFile
    if not callsign:
        raise ValueError("Export callsign or ID must not be empty")
    ExportID = callsign
    ResultsExportFile = ExportID + "-Results.csv"
    LogExportFile = ExportID + "-Log.csv"


# requestExportId prompts for a callsign and configures the export files
def requestExportId():
    setExportId(input("Insert a Callsign or ID for export files: "))


def _ensureConfigured():
    if ResultsExportFile is None:
        requestExportId()
    assert ResultsExportFile is not None and LogExportFile is not None


# instantiatefiles instantiates log and export files
def instantiateFiles():
    _ensureConfigured()
    with open(ResultsExportFile, "w", encoding="utf-8", newline="") as f:
        f.write(outputFileHeader)
    with open(LogExportFile, "w", encoding="utf-8", newline=""):
        pass


# appendToResultsCsv appends a row to results
def appendToResultsCsv(row):
    _ensureConfigured()
    with open(ResultsExportFile, "a", encoding="utf-8", newline="") as f:
        f.write(row)


# appendToLogCsv appends one structured failure record to the log.
def appendToLogCsv(row):
    _ensureConfigured()
    with open(LogExportFile, "a", encoding="utf-8", newline="") as f:
        writer(f).writerow(row)
