
# -*- coding: utf-8 -*-
# Author contact: Florian Pfaff pfaff@kit.edu
# Use Python 3.6 or later!

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from pathlib import Path

def create_publications_table():
    bibtex_file_path = Path('/localhome/isaswebwiki/ISASPublikationen/ISASFused.bib')
    output_file_path = Path('/localhome/isaswebwiki/isas.iar.kit.edu/publications.table')

    with bibtex_file_path.open() as bibtex_file:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    months_list = ["none", "December", "November", "October", "September", "August", "July", "June", "May", "April", "March", "February", "January"]
    supported_for_colored_boxes = ["preprint", "article", "inproceedings", "inbook", "incollection", "book", "proceedings", "phdthesis"]

    with output_file_path.open("w", encoding="utf-8") as outputFile:
        outputFile.write('<table id="qs_table" border="1"><tbody>\n')

        def writeEntry(entry):
            if "author" in entry.keys():
                authors = entry["author"]
            elif "editor" in entry.keys():  # Use editor instead of author if no author is available
                authors = entry["editor"] + " (Eds.)"
            else:  # Entry has neither author nor editor, this must not happen
                raise

            title = entry["title"]

            if "Hanebeck" in authors and not "Uwe D. Hanebeck" in authors:
                raise NameError(f"Name Hanebeck faulty in entry {title}")

            if not "booktitle" in entry.keys():
                if not "journal" in entry.keys():
                    booktitle = "none"
                else:
                    booktitle = entry["journal"]
            else:
                booktitle = entry["booktitle"]

            tmpwriter = BibTexWriter()
            tmpDatabase = BibDatabase()
            tmpDatabase.entries.append(entry)
            bibtex = tmpwriter.write(tmpDatabase)

            submissionType = entry["ENTRYTYPE"]
            pubid = entry["ID"]

            # Properly set en and em dashes
            title = title.replace("---", u"\u2014").replace("--", u"\u2013").replace("~", " ")
            booktitle = booktitle.replace("---", u"\u2014").replace("--", u"\u2013").replace("~", " ")

            authors = authors.replace(" and ", ", ")
            if not submissionType in supported_for_colored_boxes:
                submissionType = "other"
            elif "arXiv" in booktitle:
                submissionType = "preprint"
            
            outputFile.write(f'<tr id="{pubid}" class="entry">\n<td><div class="balken-{submissionType}"></div>\n</td>\n')
            outputFile.write(f'<td> <i>{authors}</i>,</br> <b>{title}</b>,</br>')

            if not booktitle == "none":
                outputFile.write(f'{booktitle}, ')

            pages = entry.get("pages", "")
            volume = entry.get("volume", "")
            number = entry.get("number", "")

            if pages and volume and number:
                outputFile.write('{}({}):{}, '.format(volume, number, pages.replace("--", u'\u2013').replace("-", u'\u2013')))
            elif pages and volume:
                outputFile.write('{}:{}, '.format(volume, pages.replace("--", u'\u2013').replace("-", u'\u2013')))
            elif pages:
                outputFile.write('pp. {}, '.format(pages.replace("--", u'\u2013').replace("-", u'\u2013')))

            if "publisher" in entry.keys():
                outputFile.write(f'{entry["publisher"]}, ')
            if "address" in entry.keys():
                outputFile.write(f'{entry["address"]}, ')

            if "series" in entry.keys():
                outputFile.write(f'{entry["series"]}, ')

            if not month == "none":
                outputFile.write(f'{month}, ')

            outputFile.write(f'{entry["year"]}.\n')
            outputFile.write('<p class="infolinks"> <a href="javascript:toggleInfo(\''+pubid+'\',\'bibtex\')"><img src="https://isas.iar.kit.edu/img/BibTeX.png" alt="BibTeX" /></a>')

            if "pdf" in entry.keys():
                outputFile.write(f' <a href="https://isas.iar.kit.edu/pdf/{entry["pdf"]}" target="_blank"><img src="https://isas.iar.kit.edu/img/PDF.png" alt="PDF" /></a>')
            if "url" in entry.keys() and (not "pdf" in entry.keys() or submissionType == "article"):
                outputFile.write(f' <a href="{entry["url"]}" target="_blank">URL</a>')
            if "annote" in entry.keys():
                outputFile.write(f' <font color="red">{entry["annote"]}</font>')
            outputFile.write('</p>\n</td>\n</tr>\n')
            outputFile.write(f'<tr id="bib_{pubid}" class="bibtex noshow"><td></td>\n<td><b>BibTeX</b>:\n<pre>\n')
            outputFile.write(bibtex)
            outputFile.write('\n</pre>\n</td>\n</tr>\n\n')
            # write_entry ends here
        # Determine relevant years
        allYears = set([entry["year"] for entry in bib_database.entries])
        for year in sorted(list(allYears), reverse=True):
            outputFile.write(f'<tr class="year"><td></td><td><a name="{year}"></a>{year}</td></tr>\n')

            entriesOfYear = [entry for entry in bib_database.entries if entry["year"] == str(year)]

            for month in months_list:
                for entry in entriesOfYear:
                    if not "month" in entry.keys():
                        monthOfEntry = "none"
                    else:
                        monthOfEntry = entry["month"]
                    if not monthOfEntry == month:
                        continue
                    writeEntry(entry)

        outputFile.write('</tbody></table>')

if __name__ == "__main__":
    create_publications_table()
