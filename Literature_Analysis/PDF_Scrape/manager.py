# -*- coding: utf-8 -*-

from dataclasses import dataclass
import sys

from dataImport import FileInfoList
from docResults import docResults
import streamingExport as export


@dataclass
class BatchTotals:
    attempted: int = 0
    succeeded: int = 0
    failed: int = 0
    log_failures: int = 0

    @property
    def exit_code(self):
        return 1 if self.failed or self.log_failures else 0


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
        totals = BatchTotals()
        for key in self.keyring:
            totals.attempted += 1
            print("---------------\n\n\nAttempting: "+key,"\n-------------\n")
            try:
                export.appendToResultsCsv(docResults(FileInfoList[key]).toCSV() + "\n")
            except Exception as exc:
                totals.failed += 1
                try:
                    export.appendToLogCsv([key, "failed", str(exc)])
                except Exception as log_exc:
                    totals.log_failures += 1
                    print(
                        f"Unable to log failure for {key}: {log_exc}; "
                        f"original error: {exc}",
                        file=sys.stderr,
                    )
                print("---------------\n\nFailed: "+key,"\n-------------\n")
            else:
                totals.succeeded += 1
                print("---------------\n\nSucceeded: "+key,"\n-------------\n")
        return totals

    def close(self):
        pass
        #Deprecated, but keeping in case there is a need to revert to previous version (without streaming export)
        #f = open("testrun.csv", "w", encoding="utf-8")
        #f.write(self.csvString)
        #f.close()


def main():
    m = mrManager()
    m.getKeys()
    totals = m.run()
    print(
        f"Batch complete: attempted={totals.attempted} "
        f"succeeded={totals.succeeded} failed={totals.failed} "
        f"log_failures={totals.log_failures}"
    )
    return totals.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
