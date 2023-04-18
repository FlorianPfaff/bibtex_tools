import argparse
import warnings

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import author, convert_to_unicode

ENABLEEXTRAS = False

# create map between ids and table headers
NAMES = {
    "article": "Journals",
    "inproceedings": "Conferences",
    "inbook": "In Books",
    "incollection": "In Books",
    "book": "Editorship",
    "proceedings": "Editorship",
    "phdthesis": "Books and Theses",
}

PREPRINTS_STR = "Preprints"  # name of 'preprints' header
PREPRINTS_FILE_STR = (
    "Preprints"  # string that, if file name contains it, marks file as preprints
)
AUTHOR_STR = "Hanebeck, Uwe D."  # name that must be contained in authors field
MIN_YEAR = "1989"  # minimum year to display


# create list of table headers
class Lang:
    pass


TABLE_HEADERS = [
    "Conferences",
    "Journals",
    "In Books",
    "Editorship",
    "Books and Theses",
    "Preprints",
    "Other",
]
if ENABLEEXTRAS:
    special_headers = ["Fusion", "MFI"]
else:
    special_headers = []
FullHeaders = TABLE_HEADERS[0:1] + special_headers + TABLE_HEADERS[1:]

special_header_strings = {
    "Fusion": "International Conference on Information Fusion",
    "MFI": "International Conference on Multisensor Fusion",
}


####
en = {
    "TableHeaders": [
        '<div align="left"><div class="balken-inproceedings" '
        'style="align:left; width:10px; height:10px; display: inline-block;"></div> Conferences </div>',
        '<div align="left"><div class="balken-article" '
        'style="width:10px; height:10px; display: inline-block;"></div> Journals </div>',
        '<div align="left"><div class="balken-inbook" '
        'style="width:10px; height:10px; display: inline-block;"></div> In Books </div>',
        '<div align="left"><div class="balken-book" '
        'style="width:10px; height:10px; display: inline-block;"></div> Editorship </div>',
        '<div align="left"><div class="balken-phdthesis" '
        'style="width:10px; height:10px; display: inline-block;"></div> Books and Theses </div>',
        '<div align="left"><div class="balken-preprint" '
        'style="width:10px; height:10px; display: inline-block;"></div> Preprints </div>',
        '<div align="left"><div class="balken-other" '
        'style="width:10px; height:10px; display: inline-block;"></div> Other </div>',
    ],
    "SpecialHeaders": [
        '<div class="balken-fusion" style="width:10px; height:10px; display: inline-block;"></div> '
        '<div style="text-indent:20px;width:10px; height:10px; display: inline-block;">'
        '<span title="Fusion: International Conference on Information Fusion">Fusion</span></div>',
        '<div class="balken-mfi" style="width:10px; height:10px; display: inline-block;"></div> '
        '<div style="text-indent:20px;width:10px; height:10px; display: inline-block;">'
        '<span title="MFI: IEEE International Conference on Multisensor Fusion and Integration for Intelligent Systems">MFI</span></div>',
    ]
    if ENABLEEXTRAS
    else [],
    "TypeYear": (
        '<div style="width:125px; height:10px; display: inline-block;">Type / Year</div>'
    ),
    "Total": '<div align="left">Total</div>',
}
en["FullHeaders"] = (
    en["TableHeaders"][0:1] + en["SpecialHeaders"] + en["TableHeaders"][1:]
)

de = {
    "TableHeaders": [
        '<div align="left"><div class="balken-inproceedings" '
        'style="width:10px; height:10px; display: inline-block;"></div> Konferenzen </div>',
        '<div align="left"><div class="balken-article" '
        'style="width:10px; height:10px; display: inline-block;"></div> Zeitschriften </div>',
        '<div align="left"><div class="balken-inbook" '
        'style="width:10px; height:10px; display: inline-block;"></div> In Büchern </div>',
        '<div align="left"><div class="balken-book" '
        'style="width:10px; height:10px; display: inline-block;"></div> '
        "Editor von Büchern oder Zeitschriften </div>",
        '<div align="left"><div class="balken-phdthesis" '
        'style="width:10px; height:10px; display: inline-block;"></div> Bücher und Thesen </div>',
        '<div align="left"><div class="balken-preprint" '
        'style="width:10px; height:10px; display: inline-block;"></div> Preprints </div>',
        '<div align="left"><div class="balken-other" '
        'style="width:10px; height:10px; display: inline-block;"></div> Andere </div>',
    ],
    "SpecialHeaders": en["SpecialHeaders"],
    "TypeYear": "Typ / Jahr",
    "Total": "Gesamt",
}
de["FullHeaders"] = (
    de["TableHeaders"][0:1] + de["SpecialHeaders"] + de["TableHeaders"][1:]
)

Langs = [en]


def parse_bib_files(file_list):
    """
    Parse the given list of BibTeX files and return a catalog with publication counts.

    Args:
        filelist (list): List of BibTeX file names to process.

    Returns:
        dict: A dictionary containing publication counts by year and type.
    """
    catalog = dict()

    # parse bibtex files
    for file_name in file_list:
        with open(file_name) as bibtex_file:
            parser = BibTexParser(common_strings=True)
            parser.customization = convert_to_unicode
            parser.customization = author

            bibdata = bibtexparser.load(bibtex_file, parser=parser)

        for entry in bibdata.entries:
            if "arXiv" in entry["ID"]:
                etype = PREPRINTS_STR
            else:
                bib_type = entry["ENTRYTYPE"]
                try:
                    etype = NAMES[bib_type]
                except KeyError:
                    etype = "Other"

            try:
                year = entry["year"]
            except KeyError:
                warnings.warn(f"Entry '{entry.key}' has no year!")
                continue

            if year < MIN_YEAR:
                continue

            if "author" in entry.keys():
                authors = entry["author"]
                if "editor" in entry.keys():
                    authors += entry["editor"]
            elif (
                "editor" in entry.keys()
            ):  # Use editor instead of author if no author is available
                authors = entry["editor"]
            else:  # Entry has neither author nor editor, this must not happen
                raise ValueError(
                    entry["ID"]
                    + " has neither author nor editor, this must not happen."
                )

            if (
                not any("Hanebeck" in name for name in authors)
                and "Hanebeck" not in authors
            ):
                warnings.warn(
                    f'Publication {entry["ID"]} is not by Hanebeck but by {authors}'
                )
                continue

            if year not in catalog:
                catalog[year] = dict()

            if etype not in catalog[year]:
                catalog[year][etype] = set()

            catalog[year][etype].add(entry["ID"])

            if entry["ENTRYTYPE"] == "inproceedings":
                try:
                    title = entry["booktitle"]
                except KeyError:
                    continue
            for conf in special_headers:
                conf_string = special_header_strings[conf]
                if conf_string in title:
                    if conf not in catalog[year]:
                        catalog[year][conf] = set()
                    catalog[year][conf].add(entry["ID"])
        return catalog


def create_counts_table(output_type, filelist):
    """
    Generate the table from the publication counts

    Args:
        output_type (str): Output type, either "full" or "simple".
        filelist (list): List of BibTeX file names to process.
    """
    catalog = parse_bib_files(filelist)
    num_full_headers = len(FullHeaders)

    years = sorted(catalog.keys(), reverse=True)
    numYears = len(years)

    data = [
        [
            (len(catalog[year][header]) if (header in catalog[year]) else 0)
            for year in years
        ]
        for header in TABLE_HEADERS
    ]
    headerTotals = [sum(row) for row in data]
    yearTotals = [sum(row[y] for row in data) for y in range(0, numYears)]

    fullData = [
        [
            (len(catalog[year][header]) if (header in catalog[year]) else 0)
            for year in years
        ]
        for header in FullHeaders
    ]
    fullHeaderTotals = [sum(row) for row in fullData]

    if output_type == "full":
        print(
            f"{en['TypeYear']},<b>Total</b>,"
            + ",".join((f'<a href="#{year}">{year}</a>') for year in years)
        )
        for h in range(0, num_full_headers):
            print(
                f"{','.join(lang['FullHeaders'][h] for lang in Langs)},<b>{fullHeaderTotals[h]}</b>,"
                + f"{','.join(str(yt) for yt in fullData[h])}"
            )
        print(
            f"{','.join(lang['Total'] for lang in Langs)},<b>{sum(yearTotals)}</b>,"
            + ",".join(str(yt) for yt in yearTotals)
        )
    elif output_type == "simple":
        print(f"{','.join(TABLE_HEADERS)},Total")
        print(f"{','.join(str(ht) for ht in headerTotals)},{sum(yearTotals)}")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Generate publication counts from BibTeX files."
    )
    arg_parser.add_argument(
        "--output_type",
        choices=["full", "simple"],
        default="full",
        help="Choose output type: full or simple.",
    )
    arg_parser.add_argument(
        "filelist", nargs="+", help="List of BibTeX files to process."
    )
    args = arg_parser.parse_args()

    output_type = args.output_type
    filelist = args.filelist

    create_counts_table(args.output_type, args.filelist)
