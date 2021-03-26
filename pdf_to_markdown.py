#!/usr/bin/env python3
#
# This script parses the book from a given pdf file.
# It creates a folder, where the daily quotes are being exported to individual .md files.
# It may or may not work on your edition of the book.

import slate3k
import pickle
import os

PDF = "the-daily-stoic.pdf"
JAN_01_PAGE = 15
DEC_31_PAGE = 394

PDF_PICKLE = PDF.replace(".pdf", ".doc.pickle")
MKDOWN_DIR = "markdown_pages"


# Stores the daily quotes and does some fine-tuning if needed
class Page:
    def __init__(self, date, title, quote, quote_src, comment, *extra):
        # The PDF reader module integrated to slate somehow mixes the date and the title up, this needs to be fixes
        date_spl = date.split()
        if len(date_spl) == 2 and date_spl[0].isalpha() and date_spl[1][0].isnumeric():
            self.date = date
            self.title = title
        else:
            self.date = title
            self.title = date

        self.title = self.title.title()
        self.date = self.date[:-2]
        self.quote = quote
        self.quote_src = quote_src[1:].title()
        self.comment = comment
        self.extra = extra if extra != () else ""  # Ideally should be empty

        # My edition of the book requires some extra love regarding one page
        if self.title == "July 16Th Progress Of The Soul":
            tmp_date = self.date
            tmp_quote_src = self.quote_src
            self.date, self.title = self.title.split("16Th ")
            self.date += "16"
            self.quote = tmp_date
            self.quote_src = ""
            self.comment = "T" + self.comment.replace("", "")


# Scan the document if no pickle file is present
if not os.path.isfile(PDF_PICKLE):
    with open(PDF, "rb") as f:
        doc = slate3k.PDF(f)
        doc = doc[JAN_01_PAGE - 1 : DEC_31_PAGE - 1]
        pickle.dump(doc, open(PDF_PICKLE, "wb"))
else:
    doc = pickle.load(open(PDF_PICKLE, "rb"))

doc = [page.replace("\t", " ").split("\n\n") for page in doc]

for page in doc:

    if len(page) == 3:  # Remove chapter pages (eg. ['MAY', 'RIGHT ACTION'])
        doc.remove(page)

    if len(page) >= 5:  # Move the intial first letter to the body
        page[5] = page[4] + page[5]
        del page[4]

doc = list(filter(lambda p: len(p) >= 4, doc))  # Filter out junk
# Replace newline chars and remove junk from the end of pages
doc = [[e.replace("\n", " ") for e in page if e != ""] for page in doc]

# Create Page objects from the doc list
pages = [Page(*p) for p in doc]

# Write markdown files ino the directory if no such directory is present
if not os.path.isfile(os.path.join(MKDOWN_DIR, "January 1")):
    for page in pages:
        with open(os.path.join(MKDOWN_DIR, page.date + ".md"), "w") as f:
            f.write(f"# {page.title}\n\n")
            f.write(f"> {page.quote}\n>\n")
            f.write(f"> {page.quote_src}\n\n")
            f.write(f" {page.comment}\n\n")
            f.write(f" {page.extra}")
