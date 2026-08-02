# -*- coding: utf-8 -*-

"""Extract text from a PDF file.

The project was originally written against the legacy PyPDF2 API.  The
compatibility imports below support both the current ``pypdf`` package and
PyPDF2 releases that still expose the old names.
"""

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - depends on the user's installed package
    try:
        from PyPDF2 import PdfReader
    except ImportError:  # pragma: no cover - legacy fallback
        from PyPDF2 import PdfFileReader as PdfReader


def extractPDFtext(filePath):
    """Return all extractable page text from ``filePath``."""
    reader = PdfReader(filePath)
    text = ""
    for page in reader.pages:
        if hasattr(page, "extract_text"):
            text += page.extract_text() or ""
        else:  # PyPDF2 < 3.0 legacy page API
            text += page.extractText() or ""
    return text


# Example: extractPDFtext("resc/pdfList/00048.pdf")