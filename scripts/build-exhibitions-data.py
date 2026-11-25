#!/usr/bin/env python3
"""Build the Atlas site's Record of Exhibitions data files from the
parsed exhibition catalogues in ~/workspace/record-of-exhibitions/data/.

Outputs under public/data/exhibitions/:
  index.json          — array of exhibition summaries, in slate order
                        (grouped by series, chronological within each
                        series — see "Slate order" after the registry;
                        id, title, venue, dates, year, organiser, works
                        count, sections with counts, source note, and
                        the exhibition's honest "notes" text, which the
                        site shows in its About notice)
  <id>.json           — that exhibition's records, as parsed (for the
                        field-standard parses, whose sources are objects
                        {exhibition, records, apparatus}: an object
                        {records, apparatus}, the apparatus carried from
                        the source file; the site's loader accepts both
                        shapes)
  all.json            — {"works": [...]}: every record across
                        exhibitions, each tagged with its exhibition
                        id and short label (the cross-exhibition
                        search index)

Record fields (as parsed, printed forms kept): no, artist, title,
medium, size, lender, section, note.

Each exhibition in the registry below carries its own verify rules
(expected total, section counts, and whichever numbering/lender checks
apply to it). The build fails loudly rather than shipping numbers
that do not match them.
"""
import json, os
from collections import Counter

SRC_DIR = os.path.expanduser('~/workspace/record-of-exhibitions/data')
OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'exhibitions')

EXHIBITIONS = [
    # ——— National Academy of Design, 1826–1860 ———
    # From the published COMPILED record (printed for the New-York
    # Historical Society, 1943), not from original catalogues; each
    # entry's source and About notes say so plainly. The compiled
    # record's numbers are not a single complete sequence (gaps and
    # repetitions stand as printed), so these entries deliberately
    # carry no plain_range/lettered checks: totals, section and field
    # counts are the verification. Original-catalogue parses have
    # superseded the compiled entries for 1846 and 1859 (see those
    # entries below); 1858 stays on the compiled record — its only
    # scan is missing a gathering, and the library routes were left
    # unpursued by decision of 24 November 2026. Original-catalogue
    # entries continue the series past 1860 to 1923 (below).
    {
        'id': 'nad-1826',
        'file': 'nad-1826.json',
        'title': '1st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1826',
        'year': 1826,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1826',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 1st annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 143 "
         "works here, 5 carry the owner's name as the book prints it, carried in these "
         'records as the lender, and 0 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 57 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 19 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 143,
            'sections': {'Catalogue': 143},
            'no_lender': 138,
            'no_medium': 143,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1827',
        'file': 'nad-1827.json',
        'title': '2nd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1827',
        'year': 1827,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1827',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 2nd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 119 "
         "works here, 8 carry the owner's name as the book prints it, carried in these "
         'records as the lender, and 2 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 46 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 5 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 119,
            'sections': {'Catalogue': 119},
            'no_lender': 111,
            'no_medium': 119,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1828',
        'file': 'nad-1828.json',
        'title': '3rd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1828',
        'year': 1828,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1828',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 3rd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 175 "
         "works here, 33 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 26 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 58 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 3 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 175,
            'sections': {'Catalogue': 175},
            'no_lender': 142,
            'no_medium': 175,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1829',
        'file': 'nad-1829.json',
        'title': '4th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1829',
        'year': 1829,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1829',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 4th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 181 "
         "works here, 92 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 18 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 64 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 5 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 181,
            'sections': {'Catalogue': 181},
            'no_lender': 89,
            'no_medium': 181,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1830',
        'file': 'nad-1830.json',
        'title': '5th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1830',
        'year': 1830,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1830',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 5th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 173 "
         "works here, 57 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 23 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 61 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 5 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 173,
            'sections': {'Catalogue': 173},
            'no_lender': 116,
            'no_medium': 173,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1831',
        'file': 'nad-1831.json',
        'title': '6th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1831',
        'year': 1831,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1831',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 6th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 199 "
         "works here, 71 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 16 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 49 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 172 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 199,
            'sections': {'Catalogue': 199},
            'no_lender': 128,
            'no_medium': 199,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1832',
        'file': 'nad-1832.json',
        'title': '7th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1832',
        'year': 1832,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1832',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 7th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 229 "
         "works here, 77 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 20 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 58 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 4 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 229,
            'sections': {'Catalogue': 229},
            'no_lender': 152,
            'no_medium': 229,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1833',
        'file': 'nad-1833.json',
        'title': '8th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1833',
        'year': 1833,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1833',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 8th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 216 "
         "works here, 56 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 26 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 71 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 4 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 216,
            'sections': {'Catalogue': 216},
            'no_lender': 160,
            'no_medium': 216,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1834',
        'file': 'nad-1834.json',
        'title': '9th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1834',
        'year': 1834,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1834',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 9th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 177 "
         "works here, 40 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 16 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 59 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 2 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 5 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 177,
            'sections': {'Catalogue': 177},
            'no_lender': 137,
            'no_medium': 177,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1835',
        'file': 'nad-1835.json',
        'title': '10th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1835',
        'year': 1835,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1835',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 10th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 241 "
         "works here, 67 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 12 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 89 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 14 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 241,
            'sections': {'Catalogue': 241},
            'no_lender': 174,
            'no_medium': 241,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1836',
        'file': 'nad-1836.json',
        'title': '11th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1836',
        'year': 1836,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1836',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 11th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 237 "
         "works here, 73 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 28 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 77 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 13 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 237,
            'sections': {'Catalogue': 237},
            'no_lender': 164,
            'no_medium': 237,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1837',
        'file': 'nad-1837.json',
        'title': '12th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1837',
        'year': 1837,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1837',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 12th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 308 "
         "works here, 70 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 46 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 105 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 2 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 26 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 308,
            'sections': {'Catalogue': 308},
            'no_lender': 238,
            'no_medium': 308,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1838',
        'file': 'nad-1838.json',
        'title': '13th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1838',
        'year': 1838,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1838',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 13th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 341 "
         "works here, 99 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 38 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 114 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 3 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 17 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 341,
            'sections': {'Catalogue': 341},
            'no_lender': 242,
            'no_medium': 341,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1839',
        'file': 'nad-1839.json',
        'title': '14th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1839',
        'year': 1839,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1839',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 14th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 307 "
         "works here, 128 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 54 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 103 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 10 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 307,
            'sections': {'Catalogue': 307},
            'no_lender': 179,
            'no_medium': 307,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1840',
        'file': 'nad-1840.json',
        'title': '15th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1840',
        'year': 1840,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1840',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 15th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 308 "
         "works here, 120 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 42 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 107 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 11 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 308,
            'sections': {'Catalogue': 308},
            'no_lender': 188,
            'no_medium': 308,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1841',
        'file': 'nad-1841.json',
        'title': '16th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1841',
        'year': 1841,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1841',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 16th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 355 "
         "works here, 134 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 29 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 121 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 225 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 355,
            'sections': {'Catalogue': 355},
            'no_lender': 221,
            'no_medium': 355,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1842',
        'file': 'nad-1842.json',
        'title': '17th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1842',
        'year': 1842,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1842',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 17th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 363 "
         "works here, 112 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 41 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 116 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 2 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 3 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 363,
            'sections': {'Catalogue': 363},
            'no_lender': 251,
            'no_medium': 363,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1843',
        'file': 'nad-1843.json',
        'title': '18th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1843',
        'year': 1843,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1843',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 18th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 404 "
         "works here, 142 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 48 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 136 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 6 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 404,
            'sections': {'Catalogue': 404},
            'no_lender': 262,
            'no_medium': 404,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1844',
        'file': 'nad-1844.json',
        'title': '19th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1844',
        'year': 1844,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1844',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 19th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 401 "
         "works here, 151 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 97 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 130 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 2 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 3 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 401,
            'sections': {'Catalogue': 401},
            'no_lender': 250,
            'no_medium': 401,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1845',
        'file': 'nad-1845.json',
        'title': '20th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1845',
        'year': 1845,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1845',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 20th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 361 "
         "works here, 189 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 0 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 90 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 6 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 361,
            'sections': {'Catalogue': 361},
            'no_lender': 172,
            'no_medium': 361,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1846',
        'file': 'nad-1846.json',
        'title': '21st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1846)',
        'venue': 'National Academy of Design, New York',
        'dates': '1846',
        'year': 1846,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1846',
        'source': 'Original catalogue: Catalogue of the Twenty-First Annual Exhibition of the National Academy of Design (New-York: Israel Sackett, 1846); Internet Archive item catalogueofannua00nati_0 — parsed from the catalogue itself',
        'notes': ('The 21st annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Twenty-First Annual Exhibition (New-York: Israel Sackett, '
         '1846), read from the Internet Archive scan (item catalogueofannua00nati_0) '
         "— and they stand as the catalogue prints them, in the catalogue's own "
         'numbered order under its three saloon sections: Large Saloon (nos. 1–116), '
         'Smaller Saloon (nos. 117–236) and Drawing-Room (nos. 237–346). Of the 346 '
         "works here, 232 carry the possessor's name as the catalogue prints it, "
         'carried in these records as the lender. The catalogue prints no medium and '
         'no dimensions, and no per-entry for-sale marks — a sale list was held by '
         'the Curator, per the notice at the head of the catalogue. No. 129 prints '
         'no subject, and its record carries no title. The parse read the '
         "catalogue's pages by image OCR and cross-checked every catalogue number "
         "against the scan's text layer: the two readings of the number lists differ "
         'on 5 of the 16 catalogue pages; 10 records carry a flag in their note '
         'where the number rests on the image reading; and 7 numbers garbled in the '
         "OCR were restored from the sequence and the catalogue's own exhibitor "
         'index, both readings preserved — among them no. 327, which the page itself '
         'appears to print as 227. This entry supersedes the compiled-record entry '
         'for 1846 released on 24 November 2026, which was taken from the National '
         'Academy of Design Exhibition Record 1826–1860 (printed for the New-York '
         "Historical Society, 1943) and carried 344 records: the compiled record's "
         'numbering duplicates two numbers, omits others and adds a spurious no. '
         '354. Nothing was imported from the compiled record into this parse; where '
         'the two differ, the catalogue itself governs.'),
        'expect': {
            'total': 346,
            'sections': {'LARGE SALOON.': 116, 'SMALLER SALOON.': 120, 'DRAWING-ROOM': 110},
            'no_lender': 114,
            'no_medium': 346,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1847',
        'file': 'nad-1847.json',
        'title': '22nd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1847',
        'year': 1847,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1847',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 22nd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 398 "
         "works here, 234 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 4 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 99 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 2 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 398,
            'sections': {'Catalogue': 398},
            'no_lender': 164,
            'no_medium': 398,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1848',
        'file': 'nad-1848.json',
        'title': '23rd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1848',
        'year': 1848,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1848',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 23rd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 369 "
         "works here, 132 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 81 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 81 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 4 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 369,
            'sections': {'Catalogue': 369},
            'no_lender': 237,
            'no_medium': 369,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1849',
        'file': 'nad-1849.json',
        'title': '24th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1849',
        'year': 1849,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1849',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 24th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 345 "
         "works here, 114 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 88 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 77 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 3 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 345,
            'sections': {'Catalogue': 345},
            'no_lender': 231,
            'no_medium': 345,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1850',
        'file': 'nad-1850.json',
        'title': '25th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1850',
        'year': 1850,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1850',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 25th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 380 "
         "works here, 150 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 113 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 94 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them. '
         'Owner names are the least-verified field: the book prints them in italics '
         'after the title, the italics survive in neither OCR source, and they were '
         'separated from the titles typographically. No original catalogue for this '
         'year is in hand; if one is acquired, a parse from the catalogue itself will '
         'supersede this compiled-record entry.'),
        'expect': {
            'total': 380,
            'sections': {'Catalogue': 380},
            'no_lender': 230,
            'no_medium': 380,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1851',
        'file': 'nad-1851.json',
        'title': '26th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1851',
        'year': 1851,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1851',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 26th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 414 "
         "works here, 170 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 78 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 99 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 2 '
         'numbers on which the two readings disagree are marked uncertain in their '
         "records; and 317 of this year's records carry a year that rests on the image "
         "reading and the sequence of the book's year blocks, the text layer losing "
         'the year line. Owner names are the least-verified field: the book prints '
         'them in italics after the title, the italics survive in neither OCR source, '
         'and they were separated from the titles typographically. No original '
         'catalogue for this year is in hand; if one is acquired, a parse from the '
         'catalogue itself will supersede this compiled-record entry.'),
        'expect': {
            'total': 414,
            'sections': {'Catalogue': 414},
            'no_lender': 244,
            'no_medium': 414,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1852',
        'file': 'nad-1852.json',
        'title': '27th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1852',
        'year': 1852,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1852',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 27th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 473 "
         "works here, 167 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 120 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 121 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; '
         "and 7 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 473,
            'sections': {'Catalogue': 473},
            'no_lender': 306,
            'no_medium': 473,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1853',
        'file': 'nad-1853.json',
        'title': '28th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1853',
        'year': 1853,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1853',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 28th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 443 "
         "works here, 225 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 112 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 108 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 2 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 443,
            'sections': {'Catalogue': 443},
            'no_lender': 218,
            'no_medium': 443,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1854',
        'file': 'nad-1854.json',
        'title': '29th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1854',
        'year': 1854,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1854',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 29th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 398 "
         "works here, 182 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 60 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 102 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 3 '
         'numbers on which the two readings disagree are marked uncertain in their '
         'records. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 398,
            'sections': {'Catalogue': 398},
            'no_lender': 216,
            'no_medium': 398,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1855',
        'file': 'nad-1855.json',
        'title': '30th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1855',
        'year': 1855,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1855',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 30th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 267 "
         "works here, 123 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 46 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 47 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record; '
         "and 2 of this year's records carry a year that rests on the image reading "
         "and the sequence of the book's year blocks, the text layer losing the year "
         'line. Owner names are the least-verified field: the book prints them in '
         'italics after the title, the italics survive in neither OCR source, and they '
         'were separated from the titles typographically. No original catalogue for '
         'this year is in hand; if one is acquired, a parse from the catalogue itself '
         'will supersede this compiled-record entry.'),
        'expect': {
            'total': 267,
            'sections': {'Catalogue': 267},
            'no_lender': 144,
            'no_medium': 267,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1856',
        'file': 'nad-1856.json',
        'title': '31st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1856',
        'year': 1856,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1856',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 31st annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 284 "
         "works here, 146 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 36 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 45 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record. '
         'Owner names are the least-verified field: the book prints them in italics '
         'after the title, the italics survive in neither OCR source, and they were '
         'separated from the titles typographically. No original catalogue for this '
         'year is in hand; if one is acquired, a parse from the catalogue itself will '
         'supersede this compiled-record entry.'),
        'expect': {
            'total': 284,
            'sections': {'Catalogue': 284},
            'no_lender': 138,
            'no_medium': 284,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1857',
        'file': 'nad-1857.json',
        'title': '32nd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1857',
        'year': 1857,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1857',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 32nd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 566 "
         "works here, 243 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 73 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 24 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them. '
         'Owner names are the least-verified field: the book prints them in italics '
         'after the title, the italics survive in neither OCR source, and they were '
         'separated from the titles typographically. No original catalogue for this '
         'year is in hand; if one is acquired, a parse from the catalogue itself will '
         'supersede this compiled-record entry.'),
        'expect': {
            'total': 566,
            'sections': {'Catalogue': 566},
            'no_lender': 323,
            'no_medium': 566,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1858',
        'file': 'nad-1858.json',
        'title': '33rd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1858',
        'year': 1858,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1858',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 33rd annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 620 "
         "works here, 269 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 126 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 45 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them. '
         'Owner names are the least-verified field: the book prints them in italics '
         'after the title, the italics survive in neither OCR source, and they were '
         'separated from the titles typographically. The original 1858 catalogue has '
         'since been acquired and is being parsed from the catalogue itself; that '
         'parse will supersede this compiled-record entry.'),
        'expect': {
            'total': 620,
            'sections': {'Catalogue': 620},
            'no_lender': 351,
            'no_medium': 620,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1859',
        'file': 'nad-1859.json',
        'title': '34th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1859)',
        'venue': 'National Academy of Design, New York',
        'dates': '1859',
        'year': 1859,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1859',
        'source': 'Original catalogue: Catalogue of the Thirty-Fourth Annual Exhibition of the National Academy of Design (New-York: Sackett & Cobb, 1859); Internet Archive item catalogueofannua00nati — parsed from the catalogue itself',
        'notes': ('The 34th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Thirty-Fourth Annual Exhibition (New-York: Sackett & '
         'Cobb, 1859), read from the Internet Archive scan (item '
         'catalogueofannua00nati) — and they stand as the catalogue prints them, in '
         "the catalogue's own numbered order under its gallery sections: First "
         'Gallery (nos. 1–243), Second Gallery (nos. 244–342), Third Gallery (nos. '
         '343–505), Fourth Gallery (nos. 506–614), Fifth Gallery (nos. 615–720), '
         'Sixth Gallery (nos. 721–807) and Corridor (nos. 808–815). Of the 815 works '
         "here, 359 carry the possessor's name as the catalogue prints it, carried "
         'in these records as the lender, and 229 are marked “For Sale,” in the '
         'catalogue. The catalogue prints no medium and no dimensions. No. 296 '
         'prints no subject — dots only — and its record carries no title. The parse '
         "read the catalogue's pages by image OCR and cross-checked every catalogue "
         "number against the scan's text layer: the two readings of the number lists "
         'differ on 23 of the 35 catalogue pages; 117 records carry a flag in their '
         'note where the two readings disagree, both readings preserved; and the '
         'catalogue itself misprints four numbers — the entries in sequence 80, 81 '
         'and 82 are printed 30, 31 and 32, and no. 777 is printed 477 — each '
         'flagged in its record. This entry supersedes the compiled-record entry for '
         '1859 released on 24 November 2026, which was taken from the National '
         'Academy of Design Exhibition Record 1826–1860 (printed for the New-York '
         'Historical Society, 1943) and carried 828 records over 803 distinct '
         'numbers: the compiled record duplicates 25 catalogue numbers and omits 12 '
         'that the catalogue prints. Nothing was imported from the compiled record '
         'into this parse; where the two differ, the catalogue itself governs.'),
        'expect': {
            'total': 815,
            'sections': {'FIRST GALLERY.': 243, 'SECOND GALLERY.': 99, 'THIRD GALLERY.': 163, 'FOURTH GALLERY.': 109, 'FIFTH GALLERY.': 106, 'SIXTH GALLERY.': 87, 'CORRIDOR.': 8},
            'no_lender': 456,
            'no_medium': 815,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1860',
        'file': 'nad-1860.json',
        'title': '35th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As recorded in the compiled National Academy of Design Exhibition Record 1826–1860 (1943)',
        'venue': 'National Academy of Design, New York',
        'dates': '1860',
        'year': 1860,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1860',
        'source': 'Compiled record: National Academy of Design Exhibition Record 1826–1860, printed for the New-York Historical Society, 1943 (Internet Archive items nationalacademyo741nati and nationalacademyo752nati) — not the original exhibition catalogue',
        'notes': ('The 35th annual exhibition of the National Academy of Design. These records '
         'are taken from the published compiled record — the National Academy of '
         'Design Exhibition Record 1826–1860, printed for the New-York Historical '
         'Society in 1943 — not from the original exhibition catalogue, and they stand '
         "as that book prints them, gathered under each artist's heading. Of the 654 "
         "works here, 268 carry the owner's name as the book prints it, carried in "
         'these records as the lender, and 185 are marked “For sale.” in the book. The '
         "artist's address, as the book prints it for the year, stands in each "
         "record's note, and every record's note closes with its page in the compiled "
         "record. The book's catalogue numbers are not a single complete sequence — "
         'they carry gaps and repetitions — and they stand exactly as printed. The '
         "parse read the book's pages by image OCR and cross-checked every catalogue "
         "number and year against the scan's text layer: 43 of this year's numbers "
         'rest on the image reading alone, the text layer dropping or garbling them; 1 '
         'number on which the two readings disagree is marked uncertain in its record. '
         'Owner names are the least-verified field: the book prints them in italics '
         'after the title, the italics survive in neither OCR source, and they were '
         'separated from the titles typographically. No original catalogue for this '
         'year is in hand; if one is acquired, a parse from the catalogue itself will '
         'supersede this compiled-record entry.'),
        'expect': {
            'total': 654,
            'sections': {'Catalogue': 654},
            'no_lender': 386,
            'no_medium': 654,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    # ——— National Academy of Design, original annual
    # catalogues 1870–1923 ———
    # Parsed from the original annual catalogues themselves
    # (Internet Archive scans), on the same pattern as the
    # 1846 and 1859 entries above: the About text cites the
    # original catalogue as the source. Years whose scans are
    # defective (1877, 1897, 1898, 1905, 1915) and years with
    # no scan in hand (1871, 1878, 1891–1893, 1899, 1910–1911,
    # 1914, 1916–1919) have no entry. Audit trail:
    # ~/workspace/national-academy/RUN_LOG.md.
    {
        'id': 'nad-1870',
        'file': 'nad-1870.json',
        'title': '45th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1870)',
        'venue': 'National Academy of Design, New York',
        'dates': '1870',
        'year': 1870,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1870',
        'source': 'Original catalogue: Catalogue of the Forty-Fifth Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett, 1870); Internet Archive item annualexhibition45nati — parsed from the catalogue itself',
        'notes': (
         'The 45th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Forty-Fifth Annual Exhibition (New-York: E. Wells '
         'Sackett, 1870), read from the Internet Archive scan (item '
         'annualexhibition45nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–162), NORTH ROOM. (nos. 163–221), EAST ROOM. (nos. 222–307), '
         'SOUTH ROOM. (nos. 308–379), WEST ROOM. (nos. 380–460), SCULPTURE ROOM. '
         '(nos. 461–477). Of the 477 works here, 276 carry the possessor’s name as '
         'the catalogue prints it, carried in these records as the lender, and 144 '
         'are marked “For Sale,” in the catalogue. The catalogue prints no medium '
         'and no dimensions. The catalogue prints no illustrations. Two entries '
         'the OCR missed (nos. 16 and 198) were restored from the page images, and '
         'no. 477 prints its number with an asterisk, its footnote — “Died April '
         '10th, 1870” — carried as its catalogue text. Printed misprints stand as '
         'printed. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 477,
            'sections': {'CORRIDOR.': 162, 'NORTH ROOM.': 59, 'EAST ROOM.': 86, 'SOUTH ROOM.': 72, 'WEST ROOM.': 81, 'SCULPTURE ROOM.': 17},
            'plain_range': (1, 477),
            'lettered': set(),
            'no_lender': 201,
            'no_medium': 477,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1872',
        'file': 'nad-1872.json',
        'title': '47th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1872)',
        'venue': 'National Academy of Design, New York',
        'dates': '1872',
        'year': 1872,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1872',
        'source': 'Original catalogue: Catalogue of the Forty-Seventh Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett & Bro., 1872); Internet Archive item annualexhibition47nati — parsed from the catalogue itself',
        'notes': (
         'The 47th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Forty-Seventh Annual Exhibition (New-York: E. Wells '
         'Sackett & Bro., 1872), read from the Internet Archive scan (item '
         'annualexhibition47nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–107), NORTH ROOM. (nos. 108–190), EAST ROOM. (nos. 191–253), '
         'SOUTH ROOM. (nos. 254–316), WEST ROOM. (nos. 317–371), SCULPTURE ROOM. '
         '(nos. 372–385). Of the 385 works here, 192 carry the possessor’s name as '
         'the catalogue prints it, carried in these records as the lender, and 138 '
         'are marked “For Sale,” in the catalogue. The catalogue prints no medium '
         'and no dimensions. The catalogue prints no illustrations. Two entries '
         'the OCR missed (nos. 254 and 349) were restored from the page images. '
         'The parse read the catalogue’s pages by image OCR and cross-checked '
         'every catalogue number against the scan’s text layer; where the two '
         'readings disagree, the record is flagged and both readings are preserved '
         'in the parse’s audit file.'),
        'expect': {
            'total': 385,
            'sections': {'CORRIDOR.': 107, 'NORTH ROOM.': 83, 'EAST ROOM.': 63, 'SOUTH ROOM.': 63, 'WEST ROOM.': 55, 'SCULPTURE ROOM.': 14},
            'plain_range': (1, 385),
            'lettered': set(),
            'no_lender': 193,
            'no_medium': 385,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1873',
        'file': 'nad-1873.json',
        'title': '48th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1873)',
        'venue': 'National Academy of Design, New York',
        'dates': '1873',
        'year': 1873,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1873',
        'source': 'Original catalogue: Catalogue of the Forty-Eighth Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett & Bro., 1873); Internet Archive item annualexhibition4852nati (bound volume holding the 1873–1877 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 48th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Forty-Eighth Annual Exhibition (New-York: E. Wells '
         'Sackett & Bro., 1873), read from the Internet Archive scan (item '
         'annualexhibition4852nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–95), NORTH ROOM. (nos. 96–139), EAST ROOM. (nos. 140–190), SOUTH '
         'ROOM. (nos. 191–269), WEST ROOM. (nos. 270–323), SCULPTURE ROOM. (nos. '
         '324–337). Of the 337 works here, 120 carry the possessor’s name as the '
         'catalogue prints it, carried in these records as the lender, and 137 are '
         'marked “For Sale,” in the catalogue. The catalogue prints no medium and '
         'no dimensions. The catalogue prints no illustrations. Entries the raw '
         'parse dropped were restored from the page images and are flagged in '
         'their records. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 337,
            'sections': {'CORRIDOR.': 95, 'NORTH ROOM.': 44, 'EAST ROOM.': 51, 'SOUTH ROOM.': 79, 'WEST ROOM.': 54, 'SCULPTURE ROOM.': 14},
            'plain_range': (1, 337),
            'lettered': set(),
            'no_lender': 217,
            'no_medium': 337,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1874',
        'file': 'nad-1874.json',
        'title': '49th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1874)',
        'venue': 'National Academy of Design, New York',
        'dates': '1874',
        'year': 1874,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1874',
        'source': 'Original catalogue: Catalogue of the Forty-Ninth Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett & Bro., 1874); Internet Archive item annualexhibition4852nati (bound volume holding the 1873–1877 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 49th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Forty-Ninth Annual Exhibition (New-York: E. Wells '
         'Sackett & Bro., 1874), read from the Internet Archive scan (item '
         'annualexhibition4852nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–134), NORTH ROOM. (nos. 135–192), EAST ROOM. (nos. 193–254), '
         'SOUTH ROOM. (nos. 255–338), WEST ROOM. (nos. 339–393), SCULPTURE ROOM. '
         '(nos. 394–418). Of the 418 works here, 137 carry the possessor’s name as '
         'the catalogue prints it, carried in these records as the lender, and 213 '
         'are marked “For Sale,” in the catalogue. The catalogue prints no medium '
         'and no dimensions. The catalogue prints no illustrations. The catalogue '
         'itself misprints one number — the entry in sequence 88 is printed “38” — '
         'restored from the sequence and flagged in its record. The parse read the '
         'catalogue’s pages by image OCR and cross-checked every catalogue number '
         'against the scan’s text layer; where the two readings disagree, the '
         'record is flagged and both readings are preserved in the parse’s audit '
         'file.'),
        'expect': {
            'total': 418,
            'sections': {'CORRIDOR.': 134, 'NORTH ROOM.': 58, 'EAST ROOM.': 62, 'SOUTH ROOM.': 84, 'WEST ROOM.': 55, 'SCULPTURE ROOM.': 25},
            'plain_range': (1, 418),
            'lettered': set(),
            'no_lender': 281,
            'no_medium': 418,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1875',
        'file': 'nad-1875.json',
        'title': '50th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1875)',
        'venue': 'National Academy of Design, New York',
        'dates': '1875',
        'year': 1875,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1875',
        'source': 'Original catalogue: Catalogue of the Fiftieth Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett & Bro., 1875); Internet Archive item annualexhibition4852nati (bound volume holding the 1873–1877 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 50th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fiftieth Annual Exhibition (New-York: E. Wells Sackett '
         '& Bro., 1875), read from the Internet Archive scan (item '
         'annualexhibition4852nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–173), NORTH ROOM. (nos. 174–255), EAST ROOM. (nos. 256–318), '
         'SOUTH ROOM. (nos. 319–425), WEST ROOM. (nos. 426–491), NORTH-WEST ROOM. '
         '(nos. 492–533). Of the 533 works here, 111 carry the possessor’s name as '
         'the catalogue prints it, carried in these records as the lender, 346 are '
         'marked “For Sale,” in the catalogue, and the catalogue’s own printed '
         'Price List gives a price for 347 works, carried in those records’ notes. '
         'The catalogue prints no medium and no dimensions. The catalogue prints '
         'no illustrations. There is no Sculpture Room this year; the sculpture '
         'stands in the North-West Room. The parse read the catalogue’s pages by '
         'image OCR and cross-checked every catalogue number against the scan’s '
         'text layer; where the two readings disagree, the record is flagged and '
         'both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 533,
            'sections': {'CORRIDOR.': 173, 'NORTH ROOM.': 82, 'EAST ROOM.': 63, 'SOUTH ROOM.': 107, 'WEST ROOM.': 66, 'NORTH-WEST ROOM.': 42},
            'plain_range': (1, 533),
            'lettered': set(),
            'no_lender': 422,
            'no_medium': 533,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1876',
        'file': 'nad-1876.json',
        'title': '51st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1876)',
        'venue': 'National Academy of Design, New York',
        'dates': '1876',
        'year': 1876,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1876',
        'source': 'Original catalogue: Catalogue of the Fifty-First Annual Exhibition of the National Academy of Design (New-York: E. Wells Sackett & Bro., 1876); Internet Archive item annualexhibition4852nati (bound volume holding the 1873–1877 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 51st annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-First Annual Exhibition (New-York: E. Wells '
         'Sackett & Bro., 1876), read from the Internet Archive scan (item '
         'annualexhibition4852nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–175), NORTH ROOM. (nos. 176–262), EAST ROOM. (nos. 263–347), '
         'SOUTH ROOM. (nos. 348–442), WEST ROOM. (nos. 443–513), SCULPTURE ROOM. '
         '(nos. 514–568). Of the 568 works here, 70 carry the owner’s name as the '
         'catalogue prints it, carried in these records as the lender, and 414 '
         'carry a price as printed in the catalogue’s OWNER OR PRICE column, '
         'carried in the record’s note. The catalogue prints no medium and no '
         'dimensions. The catalogue prints no illustrations. Two catalogue numbers '
         'are misprinted in the catalogue itself and stand flagged in their '
         'records. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 568,
            'sections': {'CORRIDOR.': 175, 'NORTH ROOM.': 87, 'EAST ROOM.': 85, 'SOUTH ROOM.': 95, 'WEST ROOM.': 71, 'SCULPTURE ROOM.': 55},
            'plain_range': (1, 568),
            'lettered': set(),
            'no_lender': 498,
            'no_medium': 568,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1879',
        'file': 'nad-1879.json',
        'title': '54th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1879)',
        'venue': 'National Academy of Design, New York',
        'dates': '1879',
        'year': 1879,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1879',
        'source': 'Original catalogue: Catalogue of the Fifty-Fourth Annual Exhibition of the National Academy of Design (New York: E. Wells Sackett & Bro., 1879); Internet Archive item annualexhibition54nati — parsed from the catalogue itself',
        'notes': (
         'The 54th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Fourth Annual Exhibition (New York: E. Wells '
         'Sackett & Bro., 1879), read from the Internet Archive scan (item '
         'annualexhibition54nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 7 sections: CENTRAL '
         'GALLERY. (nos. 1–128), NORTH ROOM. (nos. 129–220), EAST ROOM. (nos. '
         '221–308), SOUTH ROOM. (nos. 309–399), WEST ROOM. (nos. 400–479), '
         'NORTH-WEST ROOM. (nos. 480–534), SCULPTURE ROOM. (nos. 535–615). Of the '
         '610 works here, 91 carry the owner’s name as the catalogue prints it, '
         'carried in these records as the lender, 332 carry a price as printed in '
         'the catalogue’s OWNER OR PRICE column, carried in the record’s note, and '
         '2 are marked “For Sale,” there. The catalogue prints no medium and no '
         'dimensions. The catalogue prints no illustrations. Nos. 75–79 have no '
         'records of their own: entry no. 74 is the catalogue’s own range entry, '
         '“74 to 79”, covering six Grand Manan studies by J. G. Brown, and it '
         'stands as the single record no. 74. The parse read the catalogue’s pages '
         'by image OCR and cross-checked every catalogue number against the scan’s '
         'text layer; where the two readings disagree, the record is flagged and '
         'both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 610,
            'sections': {'CENTRAL GALLERY.': 123, 'NORTH ROOM.': 92, 'EAST ROOM.': 88, 'SOUTH ROOM.': 91, 'WEST ROOM.': 80, 'NORTH-WEST ROOM.': 55, 'SCULPTURE ROOM.': 81},
            'plain_range': (1, 615),
            'absent_numbers': [75, 76, 77, 78, 79],
            'lettered': set(),
            'no_lender': 519,
            'no_medium': 610,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1880',
        'file': 'nad-1880.json',
        'title': '55th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1880)',
        'venue': 'National Academy of Design, New York',
        'dates': '1880',
        'year': 1880,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1880',
        'source': 'Original catalogue: Catalogue of the Fifty-Fifth Annual Exhibition of the National Academy of Design (New York, 1880); Internet Archive item annualexhibition5559nati (bound volume holding the 1880–1884 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 55th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Fifth Annual Exhibition (New York, 1880), read '
         'from the Internet Archive scan (item annualexhibition5559nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 7 sections: CENTRAL GALLERY. (nos. 1–143), NORTH ROOM. '
         '(nos. 144–238), EAST ROOM. (nos. 239–334), SOUTH ROOM. (nos. 335–462), '
         'WEST ROOM. (nos. 463–553), NORTH-WEST ROOM. (nos. 554–625), DRAWING AND '
         'SCULPTURE ROOM. (nos. 626–740). Of the 740 works here, 82 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender, 532 carry a price as printed in the catalogue’s OWNER OR PRICE '
         'column, carried in the record’s note, and 1 is marked “For Sale” there. '
         'The catalogue prints no medium and no dimensions. The catalogue prints '
         'no illustrations. Three entries the raw parse had absorbed into their '
         'neighbours (nos. 160, 638 and 669) were restored from the page images. '
         'The parse read the catalogue’s pages by image OCR and cross-checked '
         'every catalogue number against the scan’s text layer; where the two '
         'readings disagree, the record is flagged and both readings are preserved '
         'in the parse’s audit file.'),
        'expect': {
            'total': 740,
            'sections': {'CENTRAL GALLERY.': 143, 'NORTH ROOM.': 95, 'EAST ROOM.': 96, 'SOUTH ROOM.': 128, 'WEST ROOM.': 91, 'NORTH-WEST ROOM.': 72, 'DRAWING AND SCULPTURE ROOM.': 115},
            'plain_range': (1, 740),
            'lettered': set(),
            'no_lender': 658,
            'no_medium': 740,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1881',
        'file': 'nad-1881.json',
        'title': '56th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1881)',
        'venue': 'National Academy of Design, New York',
        'dates': '1881',
        'year': 1881,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1881',
        'source': 'Original catalogue: Catalogue of the Fifty-Sixth Annual Exhibition of the National Academy of Design (New York, 1881); Internet Archive item annualexhibition5559nati (bound volume holding the 1880–1884 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 56th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Sixth Annual Exhibition (New York, 1881), read '
         'from the Internet Archive scan (item annualexhibition5559nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 7 sections: CORRIDOR. (nos. 1–125), NORTH GALLERY. (nos. '
         '126–271), EAST GALLERY. (nos. 272–381), SOUTH GALLERY. (nos. 382–499), '
         'WEST GALLERY. (nos. 500–610), NORTH-WEST GALLERY. (nos. 611–668), '
         'PARLORS. (nos. 669–752). Of the 752 works here, 72 carry the owner’s '
         'name as the catalogue prints it, carried in these records as the lender, '
         'and 601 carry a price as printed in the catalogue’s OWNER OR PRICE '
         'column, carried in the record’s note. The catalogue prints no medium and '
         'no dimensions. The catalogue prints no illustrations. Entries the raw '
         'parse had absorbed into their neighbours were restored from the page '
         'images and are flagged in their records. The parse read the catalogue’s '
         'pages by image OCR and cross-checked every catalogue number against the '
         'scan’s text layer; where the two readings disagree, the record is '
         'flagged and both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 752,
            'sections': {'CORRIDOR.': 125, 'NORTH GALLERY.': 146, 'EAST GALLERY.': 110, 'SOUTH GALLERY.': 118, 'WEST GALLERY.': 111, 'NORTH-WEST GALLERY.': 58, 'PARLORS.': 84},
            'plain_range': (1, 752),
            'lettered': set(),
            'no_lender': 680,
            'no_medium': 752,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1882',
        'file': 'nad-1882.json',
        'title': '57th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1882)',
        'venue': 'National Academy of Design, New York',
        'dates': '1882',
        'year': 1882,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1882',
        'source': 'Original catalogue: Catalogue of the Fifty-Seventh Annual Exhibition of the National Academy of Design (New York, 1882); Internet Archive item annualexhibition5559nati (bound volume holding the 1880–1884 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 57th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Seventh Annual Exhibition (New York, 1882), read '
         'from the Internet Archive scan (item annualexhibition5559nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 7 sections: NORTH GALLERY. (nos. 1–135), EAST GALLERY. '
         '(nos. 136–260), SOUTH GALLERY. (nos. 261–416), WEST GALLERY. (nos. '
         '417–499), NORTH-WEST GALLERY. (nos. 500–579), CORRIDOR. (nos. 580–705), '
         'LIBRARY. (nos. 706–839). Of the 839 works here, 62 carry the owner’s '
         'name as the catalogue prints it, carried in these records as the lender, '
         'and 690 carry a price as printed in the catalogue’s OWNER OR PRICE '
         'column, carried in the record’s note. The catalogue prints no medium and '
         'no dimensions. The catalogue prints no illustrations. The parse read the '
         'catalogue’s pages by image OCR and cross-checked every catalogue number '
         'against the scan’s text layer; where the two readings disagree, the '
         'record is flagged and both readings are preserved in the parse’s audit '
         'file.'),
        'expect': {
            'total': 839,
            'sections': {'NORTH GALLERY.': 135, 'EAST GALLERY.': 125, 'SOUTH GALLERY.': 156, 'WEST GALLERY.': 83, 'NORTH-WEST GALLERY.': 80, 'CORRIDOR.': 126, 'LIBRARY.': 134},
            'plain_range': (1, 839),
            'lettered': set(),
            'no_lender': 777,
            'no_medium': 839,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1883',
        'file': 'nad-1883.json',
        'title': '58th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1883)',
        'venue': 'National Academy of Design, New York',
        'dates': '1883',
        'year': 1883,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1883',
        'source': 'Original catalogue: Catalogue of the Fifty-Eighth Annual Exhibition of the National Academy of Design (New York, 1883); Internet Archive item annualexhibition5559nati (bound volume holding the 1880–1884 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 58th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Eighth Annual Exhibition (New York, 1883), read '
         'from the Internet Archive scan (item annualexhibition5559nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 7 sections: NORTH GALLERY. (nos. 1–125), EAST GALLERY. '
         '(nos. 126–217), SOUTH GALLERY. (nos. 218–387), WEST GALLERY. (nos. '
         '388–446), NORTH-WEST GALLERY. (nos. 447–527), CORRIDOR. (nos. 528–634), '
         'LIBRARY. (nos. 635–746). Of the 746 works here, 40 carry the owner’s '
         'name as the catalogue prints it, carried in these records as the lender, '
         'and 646 carry a price as printed in the catalogue’s OWNER OR PRICE '
         'column, carried in the record’s note. The catalogue prints no medium and '
         'no dimensions. The catalogue prints no illustrations. The parse read the '
         'catalogue’s pages by image OCR and cross-checked every catalogue number '
         'against the scan’s text layer; where the two readings disagree, the '
         'record is flagged and both readings are preserved in the parse’s audit '
         'file.'),
        'expect': {
            'total': 746,
            'sections': {'NORTH GALLERY.': 125, 'EAST GALLERY.': 92, 'SOUTH GALLERY.': 170, 'WEST GALLERY.': 59, 'NORTH-WEST GALLERY.': 81, 'CORRIDOR.': 107, 'LIBRARY.': 112},
            'plain_range': (1, 746),
            'lettered': set(),
            'no_lender': 706,
            'no_medium': 746,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1884',
        'file': 'nad-1884.json',
        'title': '59th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1884)',
        'venue': 'National Academy of Design, New York',
        'dates': '1884',
        'year': 1884,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1884',
        'source': 'Original catalogue: Catalogue of the Fifty-Ninth Annual Exhibition of the National Academy of Design (New York, 1884); Internet Archive item annualexhibition5559nati (bound volume holding the 1880–1884 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 59th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Fifty-Ninth Annual Exhibition (New York, 1884), read '
         'from the Internet Archive scan (item annualexhibition5559nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: NORTH GALLERY. (nos. 1–110), EAST GALLERY. '
         '(nos. 111–202), SOUTH GALLERY. (nos. 203–395), WEST GALLERY. (nos. '
         '396–470), NORTH-WEST GALLERY. (nos. 471–534), CORRIDOR. (nos. 535–709). '
         'Of the 709 works here, 65 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender, and 583 carry a price as '
         'printed in the catalogue’s OWNER OR PRICE column, carried in the '
         'record’s note. The catalogue prints no medium and no dimensions. The '
         'catalogue prints no illustrations. The printed cover is this catalogue’s '
         'only title page; there is no separate letterpress title page. The parse '
         'read the catalogue’s pages by image OCR and cross-checked every '
         'catalogue number against the scan’s text layer; where the two readings '
         'disagree, the record is flagged and both readings are preserved in the '
         'parse’s audit file.'),
        'expect': {
            'total': 709,
            'sections': {'NORTH GALLERY.': 110, 'EAST GALLERY.': 92, 'SOUTH GALLERY.': 193, 'WEST GALLERY.': 75, 'NORTH-WEST GALLERY.': 64, 'CORRIDOR.': 175},
            'plain_range': (1, 709),
            'lettered': set(),
            'no_lender': 644,
            'no_medium': 709,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1885',
        'file': 'nad-1885.json',
        'title': '60th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1885)',
        'venue': 'National Academy of Design, New York',
        'dates': '1885',
        'year': 1885,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1885',
        'source': 'Original catalogue: Catalogue of the Sixtieth Annual Exhibition of the National Academy of Design (New York, 1885); Internet Archive item annualexhibition6061nati (bound volume holding the 1885 and 1886 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 60th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixtieth Annual Exhibition (New York, 1885), read from '
         'the Internet Archive scan (item annualexhibition6061nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: CORRIDOR. (nos. 1–114), NORTH GALLERY. (nos. '
         '115–237), EAST GALLERY. (nos. 238–358), SOUTH GALLERY. (nos. 359–501), '
         'WEST GALLERY. (nos. 502–581), NORTH-WEST GALLERY. (nos. 582–665). Of the '
         '665 works here, 35 carry the owner’s name as the catalogue prints it, '
         'carried in these records as the lender, and 576 carry a price as printed '
         'in the catalogue’s OWNER OR PRICE column, carried in the record’s note. '
         'The catalogue prints no medium and no dimensions. The catalogue prints '
         'no illustrations. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 665,
            'sections': {'CORRIDOR.': 114, 'NORTH GALLERY.': 123, 'EAST GALLERY.': 121, 'SOUTH GALLERY.': 143, 'WEST GALLERY.': 80, 'NORTH-WEST GALLERY.': 84},
            'plain_range': (1, 665),
            'lettered': set(),
            'no_lender': 630,
            'no_medium': 665,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1886',
        'file': 'nad-1886.json',
        'title': '61st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1886)',
        'venue': 'National Academy of Design, New York',
        'dates': '1886',
        'year': 1886,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1886',
        'source': 'Original catalogue: Catalogue of the Sixty-First Annual Exhibition of the National Academy of Design (New York: John C. Rankin, Jr., 1886); Internet Archive item annualexhibition6061nati (bound volume holding the 1885 and 1886 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 61st annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixty-First Annual Exhibition (New York: John C. '
         'Rankin, Jr., 1886), read from the Internet Archive scan (item '
         'annualexhibition6061nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: CORRIDOR. '
         '(nos. 1–165), NORTH GALLERY. (nos. 166–312), EAST GALLERY. (nos. '
         '313–467), SOUTH GALLERY. (nos. 468–615), WEST GALLERY. (nos. 616–735), '
         'NORTH-WEST GALLERY. (nos. 736–843). Of the 843 works here, 60 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender, and 711 carry a price as printed in the catalogue’s OWNER OR '
         'PRICE column, carried in the record’s note. The catalogue prints no '
         'medium and no dimensions. The catalogue prints no illustrations. The '
         'cover prints the exhibition dates, April 5th to May 15th, 1886. The '
         'parse read the catalogue’s pages by image OCR and cross-checked every '
         'catalogue number against the scan’s text layer; where the two readings '
         'disagree, the record is flagged and both readings are preserved in the '
         'parse’s audit file.'),
        'expect': {
            'total': 843,
            'sections': {'CORRIDOR.': 165, 'NORTH GALLERY.': 147, 'EAST GALLERY.': 155, 'SOUTH GALLERY.': 148, 'WEST GALLERY.': 120, 'NORTH-WEST GALLERY.': 108},
            'plain_range': (1, 843),
            'lettered': set(),
            'no_lender': 783,
            'no_medium': 843,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1887',
        'file': 'nad-1887.json',
        'title': '62nd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1887)',
        'venue': 'National Academy of Design, New York',
        'dates': '1887',
        'year': 1887,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1887',
        'source': 'Original catalogue: National Academy Notes and Complete Catalogue, Sixty-second Spring Exhibition of the National Academy of Design, edited by Charles M. Kurtz (New York: Cassell & Co., Limited, 1887); Internet Archive item annualexhibition62nati — parsed from the catalogue itself',
        'notes': (
         'The 62nd annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'National Academy Notes and Complete Catalogue (New York: Cassell & Co., '
         'Limited, 1887), read from the Internet Archive scan (item '
         'annualexhibition62nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 5 sections: THE '
         'CORRIDOR. (nos. 1–132), THE NORTH GALLERY. (nos. 133–204), THE EAST '
         'GALLERY. (nos. 205–286), THE SOUTH GALLERY. (nos. 287–411), THE WEST '
         'GALLERY. (nos. 412–503). Of the 503 works here, 37 carry the owner’s '
         'name as the catalogue prints it, carried in these records as the lender, '
         'and 427 carry a price as printed in the entry itself, carried in the '
         'record’s note. The catalogue prints no medium and no dimensions, except '
         'that the dimensions printed in the catalogue’s illustration captions are '
         'carried into the size of 59 records. The catalogue is illustrated: 62 of '
         'its plates are reproduced here, each cropped from the catalogue’s own '
         'pages and attached to the record its caption names — the catalogue is '
         'the evidence, so no external identity matching is involved. This is not '
         'the Academy’s letterpress catalogue alone: it is Charles M. Kurtz’s '
         '“National Academy Notes and Complete Catalogue” (Cassell & Co.), which '
         'contains all the matter of the official catalogue with notes and '
         'illustrations added. The entries run as a list — title, then the price '
         'if for sale, then the artist — with no table and no owner-or-price '
         'column; 84 entries carry the prize star in the title as printed. The '
         'parse read the catalogue’s pages by image OCR and cross-checked every '
         'catalogue number against the scan’s text layer; where the two readings '
         'disagree, the record is flagged and both readings are preserved in the '
         'parse’s audit file.'),
        'expect': {
            'total': 503,
            'sections': {'THE CORRIDOR.': 132, 'THE NORTH GALLERY.': 72, 'THE EAST GALLERY.': 82, 'THE SOUTH GALLERY.': 125, 'THE WEST GALLERY.': 92},
            'plain_range': (1, 503),
            'lettered': set(),
            'no_lender': 466,
            'no_medium': 503,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1888',
        'file': 'nad-1888.json',
        'title': '63rd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1888)',
        'venue': 'National Academy of Design, New York',
        'dates': '1888',
        'year': 1888,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1888',
        'source': 'Original catalogue: Catalogue of the Sixty-Third Annual Exhibition of the National Academy of Design (New York: John C. Rankin, Jr., 1888); Internet Archive item annualexhibition6364nati (bound volume holding the 1888 and 1889 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 63rd annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixty-Third Annual Exhibition (New York: John C. '
         'Rankin, Jr., 1888), read from the Internet Archive scan (item '
         'annualexhibition6364nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 5 sections: CORRIDOR. '
         '(nos. 1–121), NORTH GALLERY. (nos. 122–234), EAST GALLERY. (nos. '
         '235–323), SOUTH GALLERY. (nos. 324–466), WEST GALLERY. (nos. 467–598). '
         'Of the 598 works here, 57 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender, and 493 carry a price as '
         'printed in the catalogue’s OWNER OR PRICE column, carried in the '
         'record’s note. The catalogue prints no medium and no dimensions. The '
         'catalogue prints no illustrations. The prize device this year is a '
         'system of seven marks for the Clarke, Hallgarten and Dodge prizes, '
         'printed before the subject and explained in each marked record’s note; '
         '120 records carry one. No. 589’s number is misprinted “539” in the '
         'catalogue itself; the record stands in sequence, flagged. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 598,
            'sections': {'CORRIDOR.': 121, 'NORTH GALLERY.': 113, 'EAST GALLERY.': 89, 'SOUTH GALLERY.': 143, 'WEST GALLERY.': 132},
            'plain_range': (1, 598),
            'lettered': set(),
            'no_lender': 541,
            'no_medium': 598,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1889',
        'file': 'nad-1889.json',
        'title': '64th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1889)',
        'venue': 'National Academy of Design, New York',
        'dates': '1889',
        'year': 1889,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1889',
        'source': 'Original catalogue: Catalogue of the Sixty-Fourth Annual Exhibition of the National Academy of Design (New York: John C. Rankin, Jr., 1889); Internet Archive item annualexhibition6364nati (bound volume holding the 1888 and 1889 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 64th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixty-Fourth Annual Exhibition (New York: John C. '
         'Rankin, Jr., 1889), read from the Internet Archive scan (item '
         'annualexhibition6364nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 5 sections: CORRIDOR. '
         '(nos. 1–135), NORTH GALLERY. (nos. 136–241), EAST GALLERY. (nos. '
         '242–307), SOUTH GALLERY. (nos. 308–436), WEST GALLERY. (nos. 437–547). '
         'Of the 547 works here, 49 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender, and 432 carry a price as '
         'printed in the catalogue’s OWNER OR PRICE column, carried in the '
         'record’s note. The catalogue prints no medium and no dimensions. The '
         'catalogue prints no illustrations. The prize glyphs of 1888 give way to '
         'parenthesised prize letters — (C) Clarke, (H) Hallgarten, (D) Dodge — '
         'standing in the title as printed; 128 records carry one. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 547,
            'sections': {'CORRIDOR.': 135, 'NORTH GALLERY.': 106, 'EAST GALLERY.': 66, 'SOUTH GALLERY.': 129, 'WEST GALLERY.': 111},
            'plain_range': (1, 547),
            'lettered': set(),
            'no_lender': 498,
            'no_medium': 547,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1890',
        'file': 'nad-1890.json',
        'title': '65th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1890)',
        'venue': 'National Academy of Design, New York',
        'dates': '1890',
        'year': 1890,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1890',
        'source': 'Original catalogue: Catalogue of the Sixty-Fifth Annual Exhibition of the National Academy of Design (New York: John C. Rankin, Jr., 1890); Internet Archive item annualexhibition65nati — parsed from the catalogue itself',
        'notes': (
         'The 65th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixty-Fifth Annual Exhibition (New York: John C. '
         'Rankin, Jr., 1890), read from the Internet Archive scan (item '
         'annualexhibition65nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 5 sections: CORRIDOR. '
         '(nos. 1–165), NORTH GALLERY. (nos. 166–277), EAST GALLERY. (nos. '
         '278–389), SOUTH GALLERY. (nos. 390–537), WEST GALLERY. (nos. 538–671). '
         'Of the 671 works here, 38 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender, and 556 carry a price as '
         'printed in the catalogue’s OWNER OR PRICE column, carried in the '
         'record’s note. The catalogue prints no medium and no dimensions. The '
         'catalogue prints no illustrations. The parenthesised prize letters of '
         '1889 continue; 102 records carry one. The parse read the catalogue’s '
         'pages by image OCR and cross-checked every catalogue number against the '
         'scan’s text layer; where the two readings disagree, the record is '
         'flagged and both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 671,
            'sections': {'CORRIDOR.': 165, 'NORTH GALLERY.': 112, 'EAST GALLERY.': 112, 'SOUTH GALLERY.': 148, 'WEST GALLERY.': 134},
            'plain_range': (1, 671),
            'lettered': set(),
            'no_lender': 633,
            'no_medium': 671,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1894',
        'file': 'nad-1894.json',
        'title': '69th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1894)',
        'venue': 'National Academy of Design, New York',
        'dates': '1894',
        'year': 1894,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1894',
        'source': 'Original catalogue: Catalogue of the Sixty-Ninth Annual Exhibition of the National Academy of Design (New York, 1894); Internet Archive item annualexhibition69nati — parsed from the catalogue itself',
        'notes': (
         'The 69th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Sixty-Ninth Annual Exhibition (New York, 1894), read '
         'from the Internet Archive scan (item annualexhibition69nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: Corridor. (nos. 1–69), North Gallery. (nos. '
         '70–143), East Gallery. (nos. 144–197), South Gallery. (nos. 198–337), '
         'West Gallery. (nos. 338–413). Of the 413 works here, 23 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender, and 356 carry a price as printed in the catalogue entry, carried '
         'in the record’s note. The catalogue prints no medium and no dimensions, '
         'except that the dimensions printed in the catalogue’s illustration '
         'captions are carried into the size of 64 records. The catalogue is '
         'illustrated: 64 of its plates are reproduced here, each cropped from the '
         'catalogue’s own pages and attached to the record its caption names — the '
         'catalogue is the evidence, so no external identity matching is involved. '
         'Prize marks stand before the subject as printed and are explained in the '
         'records’ notes. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 413,
            'sections': {'Corridor.': 69, 'North Gallery.': 74, 'East Gallery.': 54, 'South Gallery.': 140, 'West Gallery.': 76},
            'plain_range': (1, 413),
            'lettered': set(),
            'no_lender': 390,
            'no_medium': 413,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1895',
        'file': 'nad-1895.json',
        'title': '70th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1895)',
        'venue': 'National Academy of Design, New York',
        'dates': '1895',
        'year': 1895,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1895',
        'source': 'Original catalogue: Catalogue of the Seventieth Annual Exhibition of the National Academy of Design (New York: The Knickerbocker Press, 1895); Internet Archive item annualexhibition70nati — parsed from the catalogue itself',
        'notes': (
         'The 70th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventieth Annual Exhibition (New York: The '
         'Knickerbocker Press, 1895), read from the Internet Archive scan (item '
         'annualexhibition70nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 5 sections: Corridor. '
         '(nos. 1–90), North Gallery. (nos. 91–169), East Gallery. (nos. 170–270), '
         'South Gallery. (nos. 271–377), West Gallery. (nos. 378–473). Of the 473 '
         'works here, 35 carry the owner’s name as the catalogue prints it, '
         'carried in these records as the lender, and 387 carry a price as printed '
         'in the catalogue entry, carried in the record’s note. The catalogue '
         'prints no medium and no dimensions, except that the dimensions printed '
         'in the catalogue’s illustration captions are carried into the size of 64 '
         'records. The catalogue is illustrated: 64 of its plates are reproduced '
         'here, each cropped from the catalogue’s own pages and attached to the '
         'record its caption names — the catalogue is the evidence, so no external '
         'identity matching is involved. 98 records carry a prize mark, standing '
         'before the subject as printed. The parse read the catalogue’s pages by '
         'image OCR and cross-checked every catalogue number against the scan’s '
         'text layer; where the two readings disagree, the record is flagged and '
         'both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 473,
            'sections': {'Corridor.': 90, 'North Gallery.': 79, 'East Gallery.': 101, 'South Gallery.': 107, 'West Gallery.': 96},
            'plain_range': (1, 473),
            'lettered': set(),
            'no_lender': 438,
            'no_medium': 473,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1896',
        'file': 'nad-1896.json',
        'title': '71st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1896)',
        'venue': 'National Academy of Design, New York',
        'dates': '1896',
        'year': 1896,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1896',
        'source': 'Original catalogue: Catalogue of the Seventy-First Annual Exhibition of the National Academy of Design (New York, 1896); Internet Archive item annualexhibition8182nati — parsed from the catalogue itself',
        'notes': (
         'The 71st annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-First Annual Exhibition (New York, 1896), read '
         'from the Internet Archive scan (item annualexhibition8182nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: Along the Staircase. (nos. 1–6), Corridor. '
         '(nos. 7–79), North Gallery. (nos. 80–150), East Gallery. (nos. 151–226), '
         'South Gallery. (nos. 227–334), West Gallery. (nos. 335–408). Of the 409 '
         'works here, 23 carry the owner’s name as the catalogue prints it, '
         'carried in these records as the lender, and 339 carry a price as printed '
         'in the catalogue entry, carried in the record’s note. The catalogue '
         'prints no medium and no dimensions, except that the dimensions printed '
         'in the catalogue’s illustration captions are carried into the size of 60 '
         'records. The catalogue is illustrated: 62 of its plates are reproduced '
         'here, each cropped from the catalogue’s own pages and attached to the '
         'record its caption names — the catalogue is the evidence, so no external '
         'identity matching is involved. 72 records carry a prize mark. No. 259 '
         'does not exist: the printed catalogue itself skips it (258 is followed '
         'by 260, verified on the page image), and no record has been fabricated '
         'for it. The lettered sub-numbers 32a and 36a stand as printed. The '
         'Internet Archive item is named for the 81st–82nd exhibitions, but the '
         'file holds the 71st (1896) catalogue only; the catalogue’s own title '
         'page governs. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 409,
            'sections': {'Along the Staircase.': 6, 'Corridor.': 75, 'North Gallery.': 71, 'East Gallery.': 76, 'South Gallery.': 107, 'West Gallery.': 74},
            'plain_range': (1, 408),
            'absent_numbers': [259],
            'lettered': {'32a', '36a'},
            'no_lender': 386,
            'no_medium': 409,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1900',
        'file': 'nad-1900.json',
        'title': '75th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1900)',
        'venue': 'National Academy of Design, New York',
        'dates': '1900',
        'year': 1900,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1900',
        'source': 'Original catalogue: Catalogue of the Seventy-Fifth Annual Exhibition of the National Academy of Design (New York, 1900); Internet Archive item annualexhibition7576nati (bound volume holding the 1900 and 1901 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 75th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-Fifth Annual Exhibition (New York, 1900), read '
         'from the Internet Archive scan (item annualexhibition7576nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: Vanderbilt Gallery. (nos. 1–120), South '
         'Gallery. (nos. 121–235), Middle Gallery. (nos. 236–273), East Gallery. '
         '(nos. 274–298), Statuary and Miniatures. (nos. 299–314). Of the 315 '
         'works here, 22 carry the owner’s name as the catalogue prints it, '
         'carried in these records as the lender. The catalogue prints no prices. '
         'The catalogue prints no medium and no dimensions. The catalogue is '
         'illustrated: 46 of its plates are reproduced here, each cropped from the '
         'catalogue’s own pages and attached to the record its caption names — the '
         'catalogue is the evidence, so no external identity matching is involved. '
         'The lettered sub-number 60a stands as printed. The catalogue’s printed '
         'Index to Illustrations lists 46 works, and exactly 46 plates are '
         'printed. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 315,
            'sections': {'Vanderbilt Gallery.': 121, 'South Gallery.': 115, 'Middle Gallery.': 38, 'East Gallery.': 25, 'Statuary and Miniatures.': 16},
            'plain_range': (1, 314),
            'lettered': {'60a'},
            'no_lender': 293,
            'no_medium': 315,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1901',
        'file': 'nad-1901.json',
        'title': '76th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1901)',
        'venue': 'National Academy of Design, New York',
        'dates': '1901',
        'year': 1901,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1901',
        'source': 'Original catalogue: Catalogue of the Seventy-Sixth Annual Exhibition of the National Academy of Design (New York, 1901); Internet Archive item annualexhibition7576nati (bound volume holding the 1900 and 1901 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 76th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-Sixth Annual Exhibition (New York, 1901), read '
         'from the Internet Archive scan (item annualexhibition7576nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: South Gallery. (nos. 1–82), Middle Gallery. '
         '(nos. 83–101), East Gallery. (nos. 102–140), West Gallery. (nos. '
         '141–184), Vanderbilt Gallery. (nos. 185–272), Sculpture. (nos. 273–285). '
         'Of the 286 works here, 23 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender. The catalogue prints no '
         'prices. The catalogue prints no medium and no dimensions. The catalogue '
         'is illustrated: 45 of its plates are reproduced here, each cropped from '
         'the catalogue’s own pages and attached to the record its caption names — '
         'the catalogue is the evidence, so no external identity matching is '
         'involved. The lettered sub-number 55A stands as printed. The printed '
         'Index to Illustrations lists 45 works, and exactly 45 plates are '
         'printed. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 286,
            'sections': {'South Gallery.': 83, 'Middle Gallery.': 19, 'East Gallery.': 39, 'West Gallery.': 44, 'Vanderbilt Gallery.': 88, 'Sculpture.': 13},
            'plain_range': (1, 285),
            'lettered': {'55A'},
            'no_lender': 263,
            'no_medium': 286,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1902',
        'file': 'nad-1902.json',
        'title': '77th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1902)',
        'venue': 'National Academy of Design, New York',
        'dates': '1902',
        'year': 1902,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1902',
        'source': 'Original catalogue: Catalogue of the Seventy-Seventh Annual Exhibition of the National Academy of Design (New York, 1902); Internet Archive item annualexhibition7778nati (bound volume holding the 1902 and 1903 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 77th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-Seventh Annual Exhibition (New York, 1902), '
         'read from the Internet Archive scan (item annualexhibition7778nati) — '
         'and they stand as the catalogue prints them, in the catalogue’s own '
         'numbered order under its 6 sections: South Gallery. (nos. 1–104), Middle '
         'Gallery. (nos. 105–156), East Gallery. (nos. 157–207), West Gallery. '
         '(nos. 208–260), Vanderbilt Gallery. (nos. 261–389), Sculpture. (nos. '
         '390–405). Of the 405 works here, 26 carry the owner’s name as the '
         'catalogue prints it, carried in these records as the lender. The '
         'catalogue prints no prices. The catalogue prints no medium and no '
         'dimensions. The catalogue is illustrated: 30 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 405,
            'sections': {'South Gallery.': 104, 'Middle Gallery.': 52, 'East Gallery.': 51, 'West Gallery.': 53, 'Vanderbilt Gallery.': 129, 'Sculpture.': 16},
            'plain_range': (1, 405),
            'lettered': set(),
            'no_lender': 379,
            'no_medium': 405,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1903',
        'file': 'nad-1903.json',
        'title': '78th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1903)',
        'venue': 'National Academy of Design, New York',
        'dates': '1903',
        'year': 1903,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1903',
        'source': 'Original catalogue: Catalogue of the Seventy-Eighth Annual Exhibition of the National Academy of Design (New York, 1903); Internet Archive item annualexhibition7778nati (bound volume holding the 1902 and 1903 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 78th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-Eighth Annual Exhibition (New York, 1903), read '
         'from the Internet Archive scan (item annualexhibition7778nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: South Gallery. (nos. 1–113), Middle Gallery. '
         '(nos. 114–170), East Gallery. (nos. 171–217), West Gallery. (nos. '
         '218–264), Vanderbilt Gallery. (nos. 265–393), Sculpture. (nos. 394–398). '
         'Of the 398 works here, 29 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender. The catalogue prints no '
         'prices. The catalogue prints no medium and no dimensions. The catalogue '
         'is illustrated: 28 of its plates are reproduced here, each cropped from '
         'the catalogue’s own pages and attached to the record its caption names — '
         'the catalogue is the evidence, so no external identity matching is '
         'involved. Nos. 169 and 276 are printed with no title at all; their '
         'records carry none. The parse read the catalogue’s pages by image OCR '
         'and cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 398,
            'sections': {'South Gallery.': 113, 'Middle Gallery.': 57, 'East Gallery.': 47, 'West Gallery.': 47, 'Vanderbilt Gallery.': 129, 'Sculpture.': 5},
            'plain_range': (1, 398),
            'lettered': set(),
            'no_lender': 369,
            'no_medium': 398,
            'no_title': 2,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1904',
        'file': 'nad-1904.json',
        'title': '79th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1904)',
        'venue': 'National Academy of Design, New York',
        'dates': '1904',
        'year': 1904,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1904',
        'source': 'Original catalogue: Catalogue of the Seventy-Ninth Annual Exhibition of the National Academy of Design (New York: The Knickerbocker Press, 1904); Internet Archive item annualexhibition7980nati (bound volume also holding the 1905 catalogue) — parsed from the catalogue itself',
        'notes': (
         'The 79th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Seventy-Ninth Annual Exhibition (New York: The '
         'Knickerbocker Press, 1904), read from the Internet Archive scan (item '
         'annualexhibition7980nati) — and they stand as the catalogue prints them, '
         'in the catalogue’s own numbered order under its 6 sections: South '
         'Gallery. (nos. 1–101), Middle Gallery. (nos. 102–141), East Gallery. '
         '(nos. 142–187), West Gallery. (nos. 188–244), Vanderbilt Gallery. (nos. '
         '245–348), Sculpture. (nos. 349–351). Of the 354 works here, 32 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender. The catalogue prints no prices. The catalogue prints no medium '
         'and no dimensions. The catalogue is illustrated: 23 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. Nos. 224, 265 '
         'and 293 are printed with no title at all; their records carry none. The '
         'lettered sub-numbers 263a, 263b and 263c stand as printed. One plate — '
         'captioned “NO. 2. THE LETTER. BY ARTHUR M. HAZARD.” — matches neither '
         'no. 2 nor Hazard’s only other entry, and is archived unattached rather '
         'than forced onto a record; six works the printed Index to Illustrations '
         'lists (nos. 31, 51, 75, 85, 89 and 183) have no plate printed anywhere '
         'in the catalogue, and their records carry no image. The parse read the '
         'catalogue’s pages by image OCR and cross-checked every catalogue number '
         'against the scan’s text layer; where the two readings disagree, the '
         'record is flagged and both readings are preserved in the parse’s audit '
         'file.'),
        'expect': {
            'total': 354,
            'sections': {'South Gallery.': 101, 'Middle Gallery.': 40, 'East Gallery.': 46, 'West Gallery.': 57, 'Vanderbilt Gallery.': 107, 'Sculpture.': 3},
            'plain_range': (1, 351),
            'lettered': {'263c', '263b', '263a'},
            'no_lender': 322,
            'no_medium': 354,
            'no_title': 3,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1906',
        'file': 'nad-1906.json',
        'title': '81st Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1906)',
        'venue': 'National Academy of Design, New York',
        'dates': '1906',
        'year': 1906,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1906',
        'source': 'Original catalogue: Catalogue of the Eighty-First Annual Exhibition of the National Academy of Design (New York, 1906); Internet Archive item annualexhibition71nati (bound volume holding the 1906 and 1907 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 81st annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-First Annual Exhibition (New York, 1906), read '
         'from the Internet Archive scan (item annualexhibition71nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 6 sections: South Gallery. (nos. 1–108), Centre Gallery. '
         '(nos. 109–137), East Gallery. (nos. 138–171), West Gallery. (nos. '
         '172–224), Vanderbilt Gallery. (nos. 225–340), Sculpture. (nos. 341–350). '
         'Of the 350 works here, 29 carry the owner’s name as the catalogue prints '
         'it, carried in these records as the lender. The catalogue prints no '
         'prices. The catalogue prints no medium and no dimensions. The catalogue '
         'is illustrated: 17 of its plates are reproduced here, each cropped from '
         'the catalogue’s own pages and attached to the record its caption names — '
         'the catalogue is the evidence, so no external identity matching is '
         'involved. The Internet Archive item is named for the 71st exhibition, '
         'but the volume holds the 81st (1906) and 82nd (1907) catalogues; only '
         'the 1906 catalogue is parsed here. The parse read the catalogue’s pages '
         'by image OCR and cross-checked every catalogue number against the scan’s '
         'text layer; where the two readings disagree, the record is flagged and '
         'both readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 350,
            'sections': {'South Gallery.': 108, 'Centre Gallery.': 29, 'East Gallery.': 34, 'West Gallery.': 53, 'Vanderbilt Gallery.': 116, 'Sculpture.': 10},
            'plain_range': (1, 350),
            'lettered': set(),
            'no_lender': 321,
            'no_medium': 350,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1907',
        'file': 'nad-1907.json',
        'title': '82nd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1907)',
        'venue': 'National Academy of Design, New York',
        'dates': '1907',
        'year': 1907,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1907',
        'source': 'Original catalogue: Catalogue of the Eighty-Second Annual Exhibition of the National Academy of Design (New York, 1907); Internet Archive item annualexhibition71nati (bound volume holding the 1906 and 1907 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 82nd annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-Second Annual Exhibition (New York, 1907), read '
         'from the Internet Archive scan (item annualexhibition71nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 7 sections: South Gallery. (nos. 1–94), Centre Gallery. '
         '(nos. 95–116), East Gallery. (nos. 117–164), West Gallery. (nos. '
         '165–213), Vanderbilt Gallery. (nos. 214–345), Academy Room. (nos. '
         '346–378), Sculpture (nos. 379–429). Of the 429 works here, 39 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender. The catalogue prints no prices. The catalogue prints no medium '
         'and no dimensions. The catalogue is illustrated: 16 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. This scan has no '
         'title page — the front-matter foliation is unbroken, so the catalogue '
         'proper is complete and nothing is missing from it. The Internet Archive '
         'item is named for the 71st exhibition, but the volume holds the 81st '
         '(1906) and 82nd (1907) catalogues; only the 1907 catalogue is parsed '
         'here. The parse read the catalogue’s pages by image OCR and '
         'cross-checked every catalogue number against the scan’s text layer; '
         'where the two readings disagree, the record is flagged and both readings '
         'are preserved in the parse’s audit file.'),
        'expect': {
            'total': 429,
            'sections': {'South Gallery.': 94, 'Centre Gallery.': 22, 'East Gallery.': 48, 'West Gallery.': 49, 'Vanderbilt Gallery.': 132, 'Academy Room.': 33, 'Sculpture': 51},
            'plain_range': (1, 429),
            'lettered': set(),
            'no_lender': 390,
            'no_medium': 429,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1908',
        'file': 'nad-1908.json',
        'title': '83rd Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1908)',
        'venue': 'National Academy of Design, New York',
        'dates': '1908',
        'year': 1908,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1908',
        'source': 'Original catalogue: Catalogue of the Eighty-Third Annual Exhibition of the National Academy of Design (New York, 1908); Internet Archive item annualexhibition8384nati (bound volume holding the 1908 and 1909 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 83rd annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-Third Annual Exhibition (New York, 1908), read '
         'from the Internet Archive scan (item annualexhibition8384nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 4 sections: South Gallery. (nos. 1–109), Centre Gallery. '
         '(nos. 110–208), Vanderbilt Gallery. (nos. 209–345), Sculpture (nos. '
         '346–389). Of the 389 works here, 42 carry the owner’s name as the '
         'catalogue prints it, carried in these records as the lender. The '
         'catalogue prints no prices. The catalogue prints no medium and no '
         'dimensions. The catalogue is illustrated: 17 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. Nos. 371 and 376 '
         'print no artist, and their records carry none. The parse read the '
         'catalogue’s pages by image OCR and cross-checked every catalogue number '
         'against the scan’s text layer; where the two readings disagree, the '
         'record is flagged and both readings are preserved in the parse’s audit '
         'file.'),
        'expect': {
            'total': 389,
            'sections': {'South Gallery.': 109, 'Centre Gallery.': 99, 'Vanderbilt Gallery.': 137, 'Sculpture': 44},
            'plain_range': (1, 389),
            'lettered': set(),
            'no_lender': 347,
            'no_medium': 389,
            'no_title': 0,
            'no_artist': 2,
        },
    },
    {
        'id': 'nad-1909',
        'file': 'nad-1909.json',
        'title': '84th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1909)',
        'venue': 'National Academy of Design, New York',
        'dates': '1909',
        'year': 1909,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1909',
        'source': 'Original catalogue: Catalogue of the Eighty-Fourth Annual Exhibition of the National Academy of Design (New York, 1909); Internet Archive item annualexhibition8384nati (bound volume holding the 1908 and 1909 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 84th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-Fourth Annual Exhibition (New York, 1909), read '
         'from the Internet Archive scan (item annualexhibition8384nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 4 sections: South Gallery. (nos. 1–94), Centre Gallery. '
         '(nos. 95–179), Vanderbilt Gallery. (nos. 180–275), Sculpture (nos. '
         '276–306). Of the 306 works here, 34 carry the owner’s name as the '
         'catalogue prints it, carried in these records as the lender. The '
         'catalogue prints no prices. The catalogue prints no medium and no '
         'dimensions. The catalogue is illustrated: 16 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 306,
            'sections': {'South Gallery.': 94, 'Centre Gallery.': 85, 'Vanderbilt Gallery.': 96, 'Sculpture': 31},
            'plain_range': (1, 306),
            'lettered': set(),
            'no_lender': 272,
            'no_medium': 306,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1912',
        'file': 'nad-1912.json',
        'title': '87th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1912)',
        'venue': 'National Academy of Design, New York',
        'dates': '1912',
        'year': 1912,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1912',
        'source': 'Original catalogue: Catalogue of the Eighty-Seventh Annual Exhibition of the National Academy of Design (New York, 1912); Internet Archive item annualexhibition8788nati (bound volume holding the 1912 and 1913 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 87th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-Seventh Annual Exhibition (New York, 1912), read '
         'from the Internet Archive scan (item annualexhibition8788nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: South Gallery. (nos. 1–85), Centre Gallery. '
         '(nos. 86–163), Vanderbilt Gallery. (nos. 164–260), Academy Room. (nos. '
         '261–296), Sculpture. (nos. 297–322). Of the 322 works here, 22 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender. The catalogue prints no prices. The catalogue prints no medium '
         'and no dimensions. The catalogue is illustrated: 18 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 322,
            'sections': {'South Gallery.': 85, 'Centre Gallery.': 78, 'Vanderbilt Gallery.': 97, 'Academy Room.': 36, 'Sculpture.': 26},
            'plain_range': (1, 322),
            'lettered': set(),
            'no_lender': 300,
            'no_medium': 322,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1913',
        'file': 'nad-1913.json',
        'title': '88th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1913)',
        'venue': 'National Academy of Design, New York',
        'dates': '1913',
        'year': 1913,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1913',
        'source': 'Original catalogue: Catalogue of the Eighty-Eighth Annual Exhibition of the National Academy of Design (New York, 1913); Internet Archive item annualexhibition8788nati (bound volume holding the 1912 and 1913 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 88th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Eighty-Eighth Annual Exhibition (New York, 1913), read '
         'from the Internet Archive scan (item annualexhibition8788nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: South Gallery. (nos. 1–88), Center Gallery. '
         '(nos. 89–179), Vanderbilt Gallery. (nos. 180–246), Academy Room. (nos. '
         '247–300), Sculpture. (nos. 301–315). Of the 315 works here, 22 carry the '
         'owner’s name as the catalogue prints it, carried in these records as the '
         'lender. The catalogue prints no prices. The catalogue prints no medium '
         'and no dimensions. The catalogue is illustrated: 16 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 315,
            'sections': {'South Gallery.': 88, 'Center Gallery.': 91, 'Vanderbilt Gallery.': 67, 'Academy Room.': 54, 'Sculpture.': 15},
            'plain_range': (1, 315),
            'lettered': set(),
            'no_lender': 293,
            'no_medium': 315,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1920',
        'file': 'nad-1920.json',
        'title': '95th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1920)',
        'venue': 'National Academy of Design, New York',
        'dates': '1920',
        'year': 1920,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1920',
        'source': 'Original catalogue: Catalogue of the Ninety-Fifth Annual Exhibition of the National Academy of Design (New York, 1920); Internet Archive items annualexhibition00nati (bound volume holding the 1920 and 1921 catalogues; the parse scan) and annualexhibition95nati (cross-check) — parsed from the catalogue itself',
        'notes': (
         'The 95th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Ninety-Fifth Annual Exhibition (New York, 1920), read '
         'from the Internet Archive scan (item annualexhibition00nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 3 sections: Paintings (nos. 1–654), Drawings, '
         'Engravings, Etchings and Prints (nos. 655–858), Sculpture (nos. '
         '859–936). No work here carries an owner’s name — the catalogue prints '
         'none. The catalogue prints no prices. The catalogue prints no medium and '
         'no dimensions. The catalogue is illustrated: 14 of its plates are '
         'reproduced here, each cropped from the catalogue’s own pages and '
         'attached to the record its caption names — the catalogue is the '
         'evidence, so no external identity matching is involved. Two scans of '
         'this edition were audited; the parse is made from the higher-resolution '
         'scan in the BYU bound volume, which holds all 14 plates, with the '
         'standalone scan (item annualexhibition95nati) as cross-check. No. 330 '
         'does not exist in print — 329 is followed by 331 — and 23 lettered '
         'sub-numbers stand as printed. Four of the 14 plates attach on their '
         'captions’ artist and title against a conflicting printed caption number, '
         'flagged in their records. The parse read the catalogue’s pages by image '
         'OCR and cross-checked every catalogue number against the scan’s text '
         'layer; where the two readings disagree, the record is flagged and both '
         'readings are preserved in the parse’s audit file.'),
        'expect': {
            'total': 958,
            'sections': {'Paintings': 655, 'Drawings, Engravings, Etchings and Prints': 208, 'Sculpture': 95},
            'plain_range': (1, 936),
            'absent_numbers': [330],
            'lettered': {'868a', '887a', '928a', '924a', '889a', '910a', '911a', '865a', '883b', '883a', '884c', '121a', '747d', '94a', '890a', '747b', '897a', '897b', '891a', '747a', '747c', '863a', '863b'},
            'no_lender': 958,
            'no_medium': 958,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1921',
        'file': 'nad-1921.json',
        'title': '96th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1921)',
        'venue': 'National Academy of Design, New York',
        'dates': '1921',
        'year': 1921,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1921',
        'source': 'Original catalogue: Catalogue of the Ninety-Sixth Annual Exhibition of the National Academy of Design (New York, 1921); Internet Archive item annualexhibition00nati (bound volume holding the 1920 and 1921 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 96th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Ninety-Sixth Annual Exhibition (New York, 1921), read '
         'from the Internet Archive scan (item annualexhibition00nati) — and they '
         'stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: Paintings (nos. 1–84), Center Gallery (nos. '
         '85–166), Vanderbilt Gallery (nos. 167–254), Academy Room (nos. 255–412), '
         'Sculpture (nos. 413–475). Of the 475 works here, 4 carry the owner’s '
         'name as the catalogue prints it, carried in these records as the lender. '
         'The catalogue prints no medium and no dimensions. The catalogue is '
         'illustrated: 16 of its plates are reproduced here, each cropped from the '
         'catalogue’s own pages and attached to the record its caption names — the '
         'catalogue is the evidence, so no external identity matching is involved. '
         'No Index to Illustrations and no illustration marks are printed; the '
         'plates attach on their captions alone, checked both ways. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 475,
            'sections': {'Paintings': 84, 'Center Gallery': 82, 'Vanderbilt Gallery': 88, 'Academy Room': 158, 'Sculpture': 63},
            'plain_range': (1, 475),
            'lettered': set(),
            'no_lender': 471,
            'no_medium': 475,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1922',
        'file': 'nad-1922.json',
        'title': '97th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1922)',
        'venue': 'National Academy of Design, New York',
        'dates': '1922',
        'year': 1922,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1922',
        'source': 'Original catalogue: Catalogue of the Ninety-Seventh Annual Exhibition of the National Academy of Design (New York, 1922); Internet Archive item annualexhibition9798nati (bound volume holding the 1922 and 1923 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 97th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Ninety-Seventh Annual Exhibition (New York, 1922), read '
         'from the Internet Archive scan (item annualexhibition9798nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: Paintings (88 works), Sculpture (65 works), '
         'Center Gallery (75 works), Vanderbilt Gallery (64 works), Academy Room '
         '(130 works). Of the 422 works here, 1 carry the owner’s name as the '
         'catalogue prints it, carried in these records as the lender. The '
         'catalogue prints no medium and no dimensions. The catalogue is '
         'illustrated: 16 of its plates are reproduced here, each cropped from the '
         'catalogue’s own pages and attached to the record its caption names — the '
         'catalogue is the evidence, so no external identity matching is involved. '
         'No Index to Illustrations and no illustration marks are printed; the '
         'plates attach on their captions alone, checked both ways. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 422,
            'sections': {'Paintings': 88, 'Sculpture': 65, 'Center Gallery': 75, 'Vanderbilt Gallery': 64, 'Academy Room': 130},
            'plain_range': (1, 422),
            'lettered': set(),
            'no_lender': 421,
            'no_medium': 422,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'nad-1923',
        'file': 'nad-1923.json',
        'title': '98th Annual Exhibition of the National Academy of Design',
        'subtitle': 'As printed in the original exhibition catalogue (1923)',
        'venue': 'National Academy of Design, New York',
        'dates': '1923',
        'year': 1923,
        'organiser': 'National Academy of Design',
        'label': 'National Academy of Design 1923',
        'source': 'Original catalogue: Catalogue of the Ninety-Eighth Annual Exhibition of the National Academy of Design (New York, 1923); Internet Archive item annualexhibition9798nati (bound volume holding the 1922 and 1923 catalogues) — parsed from the catalogue itself',
        'notes': (
         'The 98th annual exhibition of the National Academy of Design. These '
         'records are taken from the original exhibition catalogue itself — the '
         'Catalogue of the Ninety-Eighth Annual Exhibition (New York, 1923), read '
         'from the Internet Archive scan (item annualexhibition9798nati) — and '
         'they stand as the catalogue prints them, in the catalogue’s own numbered '
         'order under its 5 sections: Paintings (106 works), Sculpture (29 works), '
         'Center Gallery (77 works), Vanderbilt Gallery (95 works), Academy Room '
         '(146 works). No work here carries an owner’s name — the catalogue prints '
         'none. The catalogue prints no medium and no dimensions. The catalogue is '
         'illustrated: 18 of its plates are reproduced here, each cropped from the '
         'catalogue’s own pages and attached to the record its caption names — the '
         'catalogue is the evidence, so no external identity matching is involved. '
         'No Index to Illustrations and no illustration marks are printed; the '
         'plates attach on their captions alone, checked both ways. The parse read '
         'the catalogue’s pages by image OCR and cross-checked every catalogue '
         'number against the scan’s text layer; where the two readings disagree, '
         'the record is flagged and both readings are preserved in the parse’s '
         'audit file.'),
        'expect': {
            'total': 453,
            'sections': {'Paintings': 106, 'Sculpture': 29, 'Center Gallery': 77, 'Vanderbilt Gallery': 95, 'Academy Room': 146},
            'plain_range': (1, 453),
            'lettered': set(),
            'no_lender': 453,
            'no_medium': 453,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1891',
        'file': 'aws-1891.json',
        'title': 'Illustrated Catalogue of the Twenty-Fourth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '2 – 28 February 1891',
        'year': 1891,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1891',
        'source': 'Printed catalogue (New York, 1891); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-fourth annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '617 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 20 works name an '
                  'owner, who is recorded as the lender; three are marked “For sale” with '
                  'neither price nor owner given; and 21 leave the column blank. Fifty '
                  'works are illustrated in the catalogue, each flagged in its record’s '
                  'note. The scan’s text layer displaces the price and artist columns, so '
                  'every one of the catalogue’s 29 pages was read against the page images '
                  'during the parse. A handful of artist names stand exactly as the scan '
                  'reads them — the garbles are the scan’s, not the catalogue’s — and have '
                  'not been corrected. The Society offered the Wm. T. Evans Prize of $300 '
                  'for the most meritorious picture in the exhibition.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 661,
            'sections': {'North Gallery': 155, 'East Gallery': 137,
                         'South Gallery': 181, 'West Gallery': 188},
            # Plain catalogue numbers run 1–661 complete, in four
            # contiguous gallery blocks (North 1–155, East 156–292,
            # South 293–473, West 474–661), with no gaps, no lettered
            # inserts and none restored. Only 20 records name a
            # lender (the catalogue's owners); no record prints a
            # medium or a size; every record has an artist and a title.
            'plain_range': (1, 661),
            'lettered': set(),
            'no_lender': 641,
            'no_medium': 661,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1892',
        'file': 'aws-1892.json',
        'title': 'Illustrated Catalogue of the Twenty-Fifth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '1 – 27 February 1892',
        'year': 1892,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1892',
        'source': 'Printed catalogue (New York, 1892); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-fifth annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '647 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 10 works name an '
                  'owner, who is recorded as the lender; and 19 leave the column blank. '
                  'Twenty-seven works are illustrated in the catalogue, each flagged in '
                  'its record’s note — in this catalogue an asterisk marks illustrations '
                  'from the artists’ own drawings. The dearest work in the catalogue is '
                  'John La Farge’s “The Peak of Maona Roa Morea, Society Islands” '
                  '(no. 178), priced at $4,200. One entry — no. 232, by Louis C. '
                  'Tiffany — is printed with no title at all, and its record says so. '
                  'Two catalogue numbers (378 and 672) were lost or garbled in the scan '
                  'and have been restored from their sequence position, each flagged in '
                  'its record’s note. The scan’s text layer displaces the price and '
                  'artist columns, so every catalogue page was read against the page '
                  'images during the parse, as with the 1891 catalogue. A handful of '
                  'artist names stand exactly as the scan reads them — the garbles are '
                  'the scan’s, not the catalogue’s — and have not been corrected.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 676,
            'sections': {'North Gallery': 175, 'East Gallery': 147,
                         'South Gallery': 203, 'West Gallery': 151},
            # Plain catalogue numbers run 1–676 complete, in four
            # contiguous gallery blocks (North 1–175, East 176–322,
            # South 323–525, West 526–676), with no gaps and no
            # lettered inserts; two numbers (378 and 672) were
            # restored from their sequence position and are flagged
            # in their records' notes. Only 10 records name a
            # lender (the catalogue's owners); no record prints a
            # medium; every record has an artist; exactly one
            # record has no title (no. 232, Louis C. Tiffany — the
            # catalogue prints none).
            'plain_range': (1, 676),
            'lettered': set(),
            'no_lender': 666,
            'no_medium': 676,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'rose-croix-1892',
        'file': 'rose-croix-1892.json',
        'title': 'Premier Salon de la Rose+Croix (Ier Geste esthétique)',
        'printed_title': 'Catalogue du Salon de la Rose+Croix : Geste esthétique',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Galeries Durand-Ruel, Paris',
        'dates': '10 March – 10 April 1892',
        'year': 1892,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1892',
        'source': ('Printed catalogue (Paris: Librairie Nilsson, 1892), digitised by the '
                   'Bibliothèque nationale de France — Gallica, ark:/12148/bpt6k5470406r; '
                   'parsed from Gallica’s OCR text (no page images), recovered via the '
                   'user’s browser because Gallica blocks direct access.'),
        'notes': ('The first Salon de la Rose+Croix — Péladan’s first Geste esthétique. '
                  'These records come from the illustrated catalogue’s works list, which '
                  'is headed “Dessins” and prints no catalogue numbers, so no number is '
                  'recorded for any work here; the book’s own note at the head of the list '
                  'says that many drawings sent in late could not be included. Two entries '
                  'print no title, and none has been supplied. The parse '
                  'rests on Gallica’s OCR text of the Bibliothèque nationale de France '
                  'digitisation, not on page images, so names and titles carry that text’s '
                  'noise, and readings that had to be interpreted are flagged in the '
                  'individual records. The Règle printed in the book says the salon closed '
                  'on 9 April, though the Bibliothèque nationale de France dates the run '
                  'to 10 April. John Finnegan’s compilation of these salons held only two '
                  'Aman-Jean stub rows for 1892, with no works; the catalogue’s works list '
                  'contains no Aman-Jean entry.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 53,
            'sections': {'Dessins': 53},
            # The illustrated catalogue prints no catalogue numbers
            # at all: every record's number stands empty, and the
            # build must fail if any record carries one. No record
            # has a lender or a medium, and every record has an
            # artist; exactly two records have no title (De
            # Egusquiza's entry, for which the catalogue gives none,
            # and Sonnier's, whose name heads a page of verse) —
            # each flagged in its record's note.
            'no_numbers': True,
            'lettered': set(),
            'no_lender': 53,
            'no_medium': 53,
            'no_title': 2,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1892',
        'file': 'guildhall-1892.json',
        'title': 'Descriptive Catalogue of the Loan Collection of Pictures',
        'subtitle': 'Prepared by the authority of the Library Committee of the Corporation of the City of London',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '28 March – 30 June 1892',
        'year': 1892,
        'organiser': 'Library Committee of the Corporation of London; catalogued by A. G. Temple',
        'label': 'Guildhall 1892',
        'source': 'Internet Archive item descriptivecatal00artg_0 (Getty scan)',
        'notes': ('The scan of this catalogue is rough, and its ‘Lent by’ lines are the worst-read part of it: '
                  '167 of the 180 lenders have been supplied from the catalogue’s own Index of Contributors, '
                  'each flagged in its record’s note; two lenders could not be recovered at all. '
                  'Ten catalogue numbers were illegible and restored from their sequence position, each flagged; '
                  'one title (no. 171) is lost from the scan. Graves’s Century of Loan Exhibitions digests this '
                  'exhibition but covers only 154 of its 180 works — the printed catalogue is the authority here. '
                  'Names and titles are as printed and carry the scan’s OCR noise. No images in this first version.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 180,
            'sections': {'Room I': 37, 'Room II': 86, 'Room III': 57},
            # Plain catalogue numbers run 1–178 with no gaps; the only
            # lettered inserts are 122A and 132A; exactly two records
            # have no lender (nos. 83 and 104 — neither the scan nor
            # the catalogue's Index of Contributors yielded one).
            'plain_range': (1, 178),
            'lettered': {'122A', '132A'},
            'no_lender': 2,
        },
    },
    {
        'id': 'aws-1893',
        'file': 'aws-1893.json',
        'title': 'Illustrated Catalogue of the Twenty-Sixth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '30 January – 25 February 1893',
        'year': 1893,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1893',
        'source': 'Printed catalogue (New York, 1893); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-sixth annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '608 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 8 works name an '
                  'owner, who is recorded as the lender — among them Charles L. Freer, '
                  'at no. 64; and 30 leave the column blank. Twenty-one works are '
                  'illustrated in the catalogue, each flagged in its record’s note — '
                  'this catalogue prints no illustration marks in the body, so the '
                  'illustrated works are identified from the captions of the plates '
                  'themselves. The dearest works in the catalogue are five pictures '
                  'priced at $1,000 each, among them H. F. Farney’s “A Mountain '
                  'Trail—Crow Indians” (no. 256) and John La Farge’s portrait of Faase '
                  'of Samoa (no. 309). Two catalogue numbers (110 and 111) were lost or '
                  'garbled in the scan and have been restored from their sequence '
                  'position, each flagged in its record’s note. The scan’s text layer '
                  'displaces the price and artist columns, so every catalogue page was '
                  'read against the page images during the parse, as with the 1891 and '
                  '1892 catalogues. A handful of artist names stand exactly as the scan '
                  'reads them — the garbles are the scan’s, not the catalogue’s — and '
                  'have not been corrected. The Wm. T. Evans Prize rose to $500 this '
                  'year.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 646,
            'sections': {'North Gallery': 163, 'East Gallery': 108,
                         'South Gallery': 209, 'West Gallery': 166},
            # Plain catalogue numbers run 1–646 complete, in four
            # contiguous gallery blocks (North 1–163, East 164–271,
            # South 272–480, West 481–646), with no gaps and no
            # lettered inserts; two numbers (110 and 111) were
            # restored from their sequence position and are flagged
            # in their records' notes. Only 8 records name a lender
            # (the catalogue's owners); no record prints a medium;
            # every record has an artist and a title.
            'plain_range': (1, 646),
            'lettered': set(),
            'no_lender': 638,
            'no_medium': 646,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'rose-croix-1893',
        'file': 'rose-croix-1893.json',
        'title': 'Deuxième Salon de la Rose+Croix (IIe Geste esthétique)',
        'printed_title': 'Catalogue officiel illustré du second Salon de la Rose+Croix (IIe Geste esthétique)',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Palais du Champ-de-Mars, Paris',
        'dates': '28 March – 30 April 1893',
        'year': 1893,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1893',
        'source': 'Printed catalogue, in a compilation by John Finnegan (supplied November 2026)',
        'notes': ('The second Salon de la Rose+Croix — Péladan’s second Geste esthétique. '
                  'These records come from John Finnegan’s compilation of the printed catalogue '
                  'and stand as compiled: nothing has been corrected or completed. Titles are '
                  'as catalogued, with the medium often given in parentheses within the title; '
                  'these salons print no sizes and no lenders. Each artist’s address, as the '
                  'catalogue prints it, is carried in the record’s note. The numbers run to '
                  '275, but nos. 249–253 do not appear in the compilation; they are left '
                  'absent, not filled.'),
        # Expected values from the converted compilation — the build
        # fails loudly rather than shipping numbers that do not
        # match them.
        'expect': {
            'total': 270,
            'sections': {'Catalogue': 270},
            # Plain catalogue numbers run 1–275, but nos. 249–253 do
            # not appear in the compilation; there are no lettered
            # inserts; no record has a lender or a medium (both stand
            # empty throughout — the medium is in the title), and
            # every record has a title and an artist.
            'plain_range': (1, 275),
            'absent_numbers': [249, 250, 251, 252, 253],
            'lettered': set(),
            'no_lender': 270,
            'no_medium': 270,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1894',
        'file': 'aws-1894.json',
        'title': 'Illustrated Catalogue of the Twenty-Seventh Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '5 February – 3 March 1894',
        'year': 1894,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1894',
        'source': 'Printed catalogue (New York, 1894); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-seventh annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '577 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 5 works name an '
                  'owner, who is recorded as the lender; and 25 leave the column blank. '
                  'One work — no. 47, James D. Smillie’s “Well, Capuchin Monastery, '
                  'Italy” — is marked “Not for sale”, the catalogue’s only sale mark. '
                  'Twenty-one works are illustrated in the catalogue, each flagged in '
                  'its record’s note — nineteen are marked “(Illustration.)” in the '
                  'body, and two more (no. 60, Willard L. Metcalf’s “Beatrix”, and '
                  'no. 458, Harry Fenn’s “Street Venders in Cairo”) are identified from '
                  'the captions of the plates themselves; the plate of no. 347, Horatio '
                  'Walker’s “Morning”, is the catalogue’s frontispiece. The dearest '
                  'work in the catalogue is Wm. Magrath’s “Trafalgar Square, London” '
                  '(no. 160), priced at $1,500. Three catalogue numbers (110, 111 and '
                  '295) were lost or garbled in the scan and have been restored from '
                  'their sequence position, each flagged in its record’s note — '
                  'no. 295’s number was glued to its title in the scan; the printed '
                  'title is “Ænid”. The scan’s text layer displaces the price and '
                  'artist columns, so every catalogue page was read against the page '
                  'images during the parse, as with the earlier catalogues. A handful '
                  'of artist names stand exactly as the scan reads them — the garbles '
                  'are the scan’s, not the catalogue’s — and have not been corrected. '
                  'The Wm. T. Evans Prize was $500 this year.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 607,
            'sections': {'North Gallery': 127, 'East Gallery': 141,
                         'South Gallery': 190, 'West Gallery': 149},
            # Plain catalogue numbers run 1–607 complete, in four
            # contiguous gallery blocks (North 1–127, East 128–268,
            # South 269–458, West 459–607), with no gaps and no
            # lettered inserts; three numbers (110, 111 and 295) were
            # restored from their sequence position and are flagged
            # in their records' notes. Only 5 records name a lender
            # (the catalogue's owners); no record prints a medium;
            # every record has an artist and a title.
            'plain_range': (1, 607),
            'lettered': set(),
            'no_lender': 602,
            'no_medium': 607,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1894',
        'file': 'guildhall-1894.json',
        'title': 'Descriptive Catalogue of the Loan Collection of Pictures',
        'subtitle': 'Prepared by A. G. Temple, F.S.A., Director of the Art Gallery of the Corporation of London',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '2 April – 30 June 1894',
        'year': 1894,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1894',
        'source': 'Internet Archive item descriptivecatal00temp (Getty scan)',
        'notes': ('Thirty-nine catalogue numbers were illegible or garbled in the scan and have been restored '
                  'from their sequence position, each flagged in its record’s note; two lenders were supplied '
                  'from the catalogue’s own Index of Contributors, each flagged, and two could not be recovered '
                  'at all. Three sizes are lost from damaged scan lines and one title (no. 125) is absent from '
                  'the scan. Names and titles keep the scan’s reading, garbles included. Graves’s Century of '
                  'Loan Exhibitions digests this exhibition but covers only 143 of its 154 works — the printed '
                  'catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 154,
            'sections': {'Gallery I': 41, 'Gallery II': 60, 'Gallery III': 53},
            # Plain catalogue numbers run 1–152 with no gaps; the only
            # lettered inserts are 43A and 108A; exactly two records
            # have no lender (nos. 99 and 116 — neither the scan nor
            # the catalogue's Index of Contributors yielded one); and
            # exactly one record has no title (no. 125, absent from
            # the scan).
            'plain_range': (1, 152),
            'lettered': {'43A', '108A'},
            'no_lender': 2,
            'no_title': 1,
        },
    },
    {
        'id': 'rose-croix-1894',
        'file': 'rose-croix-1894.json',
        'title': 'Troisième Salon de la Rose+Croix (IIIe Geste esthétique)',
        'printed_title': 'Catalogue du Salon de la Rose+Croix (IIIe Geste esthétique)',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Galerie des Artistes Contemporains, rue de la Paix, Paris',
        'dates': 'May 1894',
        'year': 1894,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1894',
        'source': 'Printed catalogue, in a compilation by John Finnegan (supplied November 2026)',
        'notes': ('The third Salon de la Rose+Croix — Péladan’s third Geste esthétique. '
                  'The small room at the Galerie des Artistes Contemporains, rue de la Paix, '
                  'limited the hang to 83 works; the 84 records here are those 83 plus the '
                  'inserted no. 73A. These records come from John Finnegan’s compilation of '
                  'the printed catalogue and stand as compiled: nothing has been corrected '
                  'or completed. Titles are as catalogued, with the medium often given in '
                  'parentheses within the title; these salons print no sizes and no lenders. '
                  'Each artist’s address, as the catalogue prints it, is carried in the '
                  'record’s note.'),
        'expect': {
            'total': 84,
            'sections': {'Catalogue': 84},
            # Plain catalogue numbers run 1–83 with no gaps; the only
            # lettered insert is 73A; no record has a lender or a
            # medium, and every record has a title and an artist.
            'plain_range': (1, 83),
            'lettered': {'73A'},
            'no_lender': 84,
            'no_medium': 84,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1895',
        'file': 'aws-1895.json',
        'title': 'Illustrated Catalogue of the Twenty-Eighth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '4 February – 2 March 1895',
        'year': 1895,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1895',
        'source': 'Printed catalogue (New York, 1895); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-eighth annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '475 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 5 works name an '
                  'owner, who is recorded as the lender — at no. 288 the book prints the '
                  'word “Artist” itself in the owner column; and 29 leave the column '
                  'blank. One work — no. 347, Beatrice C. Wilcox’s “Roses” — is marked '
                  '“Not for sale”, the catalogue’s only sale mark. Nineteen works are '
                  'illustrated in the catalogue, each flagged in its record’s note — '
                  'sixteen are marked “(Illustration.)” in the body, and three more '
                  '(no. 14, L. E. Van Gorder’s “Old Fishing Town”, no. 264, Jules '
                  'Guerin’s “A Fagot Gatherer of Holland”, and no. 308, Carleton '
                  'Wiggins’s “A Holstein Cow”) are identified from the captions of '
                  'the plates themselves; the plate of no. 302, J. G. Brown’s “Echoes '
                  'from Town”, is the catalogue’s frontispiece. The dearest works in '
                  'the catalogue are two pictures priced at $1,000 each: Henry '
                  'Farrer’s “When leaves are brown, and the year is old” (no. 312) '
                  'and Frank Russell Green’s “A Pastoral” (no. 324). No. 446 stands '
                  'in the book as a bare printed number, with no artist, title or '
                  'price against it — presumably a work withdrawn after the '
                  'numbering was set — and its record stands empty, with a note '
                  'saying so. One catalogue number (111) was garbled in the scan and '
                  'has been restored from its sequence position, flagged in its '
                  'record’s note. Forty-seven prices are read through the scan’s '
                  'letter-for-figure garble and are flagged in their notes with the '
                  'form read; five more (nos. 332, 360, 412, 473 and 476) were '
                  'settled from the printed page where the garble could not be '
                  'resolved, no. 89’s price is lost to the scan entirely and read '
                  'from the printed page, and the prices of nos. 447–450 were '
                  'settled from the printed page as a block, their notes stating the '
                  'prices plainly. The scan’s text layer displaces the price and '
                  'artist columns, so every catalogue page was read against the '
                  'page images during the parse, as with the earlier catalogues. A '
                  'handful of artist names stand exactly as the scan reads them — '
                  'the garbles are the scan’s, not the catalogue’s — and have not '
                  'been corrected. The Wm. T. Evans Prize fell to $300 this year, '
                  'from $500 in 1893 and 1894.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 510,
            'sections': {'North Gallery': 106, 'East Gallery': 92,
                         'South Gallery': 160, 'West Gallery': 152},
            # Plain catalogue numbers run 1–510 complete, in four
            # contiguous gallery blocks (North 1–106, East 107–198,
            # South 199–358, West 359–510), with no gaps and no
            # lettered inserts; one number (111) was restored from
            # its sequence position and is flagged in its record's
            # note. Only 5 records name a lender (the catalogue's
            # owners); no record prints a medium; exactly one record
            # has no title and no artist (no. 446, which the book
            # itself prints as a bare number).
            'plain_range': (1, 510),
            'lettered': set(),
            'no_lender': 505,
            'no_medium': 510,
            'no_title': 1,
            'no_artist': 1,
        },
    },
    {
        'id': 'rose-croix-1895',
        'file': 'rose-croix-1895.json',
        'title': 'Quatrième Salon de la Rose+Croix (IVe Geste esthétique)',
        'printed_title': 'Catalogue du Salon de la Rose+Croix (IVe Geste esthétique)',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Galerie des Artistes Contemporains, rue de la Paix, Paris',
        'dates': '20 March – 20 April 1895',
        'year': 1895,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1895',
        'source': 'Printed catalogue, in a compilation by John Finnegan (supplied November 2026)',
        'notes': ('The fourth Salon de la Rose+Croix — Péladan’s fourth Geste esthétique. '
                  'These records come from John Finnegan’s compilation of the printed catalogue '
                  'and stand as compiled: nothing has been corrected or completed. Titles are '
                  'as catalogued, with the medium often given in parentheses within the title; '
                  'these salons print no sizes and no lenders. Each artist’s address, as the '
                  'catalogue prints it, is carried in the record’s note. The numbering is the '
                  'catalogue’s own tangle, kept as compiled: two notices for Louis Hawkins '
                  'state in terms that the catalogue gives neither number nor title for his '
                  'entry, three entries stand under no. 48 — the third of them, Léon '
                  'Jacques’s, with no title at all — and no. 99 is shared by two works.'),
        'expect': {
            'total': 109,
            'sections': {'Catalogue': 109},
            # Plain catalogue numbers cover 1–106 (the set check is
            # on distinct numbers: no. 48 stands three times and
            # no. 99 twice, as compiled); there are no lettered
            # inserts; no record has a lender or a medium; exactly
            # one record has no title (Léon Jacques, no. 48).
            'plain_range': (1, 106),
            'lettered': set(),
            'no_lender': 109,
            'no_medium': 109,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1895',
        'file': 'guildhall-1895.json',
        'title': 'Catalogue of the Loan Collection of Pictures',
        'subtitle': 'Prepared by A. G. Temple, F.S.A., Director of the Art Gallery of the Corporation of London',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '23 April – 21 July 1895',
        'year': 1895,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1895',
        'source': 'Internet Archive item catalogueofloanc00guil (Getty scan)',
        'notes': ('This scan’s OCR drops most of the printed catalogue numbers: 71 have been restored '
                  'from their sequence position, each flagged in its record’s note and corroborated by '
                  'the catalogue’s Index of Artists. Three entries (nos. 71, 101, 133) have lost their '
                  'headings in the scan — their artist and lender come from the catalogue’s own indexes '
                  'and their titles are left empty; no. 116 prints no artist at all. Three sizes are '
                  'illegible. Graves’s Century of Loan Exhibitions digests this exhibition and omits no '
                  'work outright, but keys only 127 of its 138 numbers correctly, merging or misnumbering '
                  'the rest — the printed catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 138,
            'sections': {'Gallery I': 40, 'Gallery II': 53, 'Gallery III': 45},
            # Plain catalogue numbers run 1–138 with no gaps and no
            # lettered inserts; every record has a lender; exactly
            # three records have no title (nos. 71, 101 and 133, whose
            # headings are lost from the scan); and exactly one record
            # has no artist (no. 116, which prints none).
            'plain_range': (1, 138),
            'lettered': set(),
            'no_lender': 0,
            'no_title': 3,
            'no_artist': 1,
        },
    },
    {
        'id': 'aws-1896',
        'file': 'aws-1896.json',
        'title': 'Illustrated Catalogue of the Twenty-Ninth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '3 – 29 February 1896',
        'year': 1896,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1896',
        'source': 'Printed catalogue (New York, 1896); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The twenty-ninth annual exhibition of the American Water Color Society. '
                  'The catalogue’s “Owner or Price” column is carried into these records: '
                  '588 works are priced for sale in the catalogue — the prices include '
                  'frames — and the price stands in each record’s note; 9 works name an '
                  'owner, who is recorded as the lender; and 9 leave the column blank. '
                  'Two works — nos. 115 and 170 — are marked “Not for sale”, the '
                  'catalogue’s only sale marks, and no price in the book reaches $1,000. '
                  'This year the hang gains a fifth section, the Corridor, beyond the '
                  'four galleries of the earlier volumes, and one sub-numbered entry — '
                  'no. 530a, Ethelyn Knowles Fenner’s “Water Lilies”, priced at $30.00 — '
                  'stands between nos. 530 and 531, cited in the book’s own index as '
                  '“530 a”. Nineteen works are illustrated in the catalogue, each '
                  'flagged in its record’s note — all nineteen on the evidence of the '
                  'body’s own “(Illustration),” mark, which this year prints a comma '
                  'where the 1894 and 1895 catalogues print a full stop; eighteen '
                  'captioned plates are bound in, every one naming a body-marked work, '
                  'and no. 231 carries the mark but no plate of it is bound in this '
                  'copy. The dearest work in the catalogue is W. Louis Sonntag, Jr.’s '
                  '“Coup de Grace” (no. 462) — the book prints no accent — priced at '
                  '$750.00. Two entries — nos. 535 and 590, both by Miss Holgate, at '
                  '$45.00 each — are printed with no title at all, and their records say '
                  'so. Four catalogue numbers (105, 110, 113 and 115) were lost or '
                  'garbled in the scan and have been restored from their sequence '
                  'position, each flagged in its record’s note — no. 105’s number was '
                  'lost to the scan altogether. Forty-one prices are read through the '
                  'scan’s letter-for-figure garble and are flagged in their notes with '
                  'the form read; four of them were settled from the printed page where '
                  'the garble could not be resolved, and one more — no. 200’s $75.00 — '
                  'is lost to the scan’s text layer entirely and read from the printed '
                  'page, its note stating the price plainly. The scan’s text layer '
                  'displaces the price and artist columns, so every catalogue page was '
                  'read against the page images during the parse, as with the earlier '
                  'catalogues. A handful of artist names stand exactly as the scan '
                  'reads them — the garbles are the scan’s, not the catalogue’s — and '
                  'have not been corrected; the book’s own spelling variants between '
                  'its body and its index likewise stand as printed in each place. The '
                  'Wm. T. Evans Prize was $300 this year, as in 1895.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 608,
            'sections': {'North Gallery': 116, 'East Gallery': 93,
                         'South Gallery': 174, 'West Gallery': 125,
                         'Corridor': 100},
            # Plain catalogue numbers run 1–607 complete, in five
            # contiguous blocks (North 1–116, East 117–209, South
            # 210–383, West 384–508, Corridor 509–607), with no gaps;
            # the only lettered insert is 530a; four numbers (105,
            # 110, 113 and 115) were restored from their sequence
            # position and are flagged in their records' notes. Only
            # 9 records name a lender (the catalogue's owners); no
            # record prints a medium; exactly two records have no
            # title (nos. 535 and 590, which the book itself prints
            # with no subject); every record has an artist.
            'plain_range': (1, 607),
            'lettered': {'530a'},
            'no_lender': 599,
            'no_medium': 608,
            'no_title': 2,
            'no_artist': 0,
        },
    },
    {
        'id': 'rose-croix-1896',
        'file': 'rose-croix-1896.json',
        'title': 'Cinquième Salon de la Rose+Croix (Ve Geste esthétique)',
        'printed_title': 'Salon de la Rose+Croix (Ve Geste esthétique)',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Galerie des Arts Réunis, avenue de l’Opéra, Paris',
        'dates': '20 March – 20 April 1896',
        'year': 1896,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1896',
        'source': 'Printed catalogue, in a compilation by John Finnegan (supplied November 2026)',
        'notes': ('The fifth Salon de la Rose+Croix — Péladan’s fifth Geste esthétique. '
                  'These records come from John Finnegan’s compilation of the printed catalogue '
                  'and stand as compiled: nothing has been corrected or completed. Titles are '
                  'as catalogued, with the medium often given in parentheses within the title; '
                  'these salons print no sizes and no lenders. Each artist’s address, as the '
                  'catalogue prints it, is carried in the record’s note. The numbering is '
                  'complete, 1–110.'),
        'expect': {
            'total': 110,
            'sections': {'Catalogue': 110},
            # Plain catalogue numbers run 1–110 with no gaps and no
            # duplicates; there are no lettered inserts; no record
            # has a lender or a medium, and every record has a title
            # and an artist.
            'plain_range': (1, 110),
            'lettered': set(),
            'no_lender': 110,
            'no_medium': 110,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1897',
        'file': 'aws-1897.json',
        'title': 'Illustrated Catalogue of the Thirtieth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '1 – 27 February 1897',
        'year': 1897,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1897',
        'source': 'Printed catalogue (New York, 1897); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirtieth annual exhibition of the American Water Color Society. '
                  'This catalogue departs from every earlier volume in the run: its '
                  'body has no “Owner or Price” column at all — number, subject and '
                  'artist only — so no price and no owner is printed for any work, '
                  'and no record here carries a price note or a lender; the book’s '
                  'notices still say that prices include frames, and prices were '
                  'evidently to be had at the desk in the gallery. The hang keeps '
                  'the five sections of 1896 — the four galleries and the Corridor. '
                  'Twenty works are illustrated in the catalogue, each flagged in '
                  'its record’s note on the evidence of the body’s own '
                  '“(Illustration).” mark — with the full stop again, where 1896 '
                  'prints a comma — and twenty captioned plates are bound in, every '
                  'one naming a body-marked work; one plate, of no. 322, L. C. '
                  'Earle’s “The Pensioner”, is captioned “22.” in the book’s own '
                  'error. Four catalogue numbers (7, 111, 317 and 371) were lost or '
                  'garbled in the scan and have been restored from their sequence '
                  'position, each flagged in its record’s note — no. 317 is printed '
                  '“417” in the book itself, a misprint the sequence and the book’s '
                  'own index both correct. Every catalogue page was read against '
                  'the page images during the parse, as with the earlier '
                  'catalogues. A handful of artist names and titles stand exactly '
                  'as the scan reads them — the garbles are the scan’s, not the '
                  'catalogue’s — and have not been corrected; the book’s own '
                  'spellings likewise stand as printed. The Wm. T. Evans Prize was '
                  '$300 this year, as in 1895 and 1896.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 509,
            'sections': {'North Gallery': 97, 'East Gallery': 81,
                         'South Gallery': 152, 'West Gallery': 97,
                         'Corridor': 82},
            # Plain catalogue numbers run 1–509 complete, in five
            # contiguous blocks (North 1–97, East 98–178, South
            # 179–330, West 331–427, Corridor 428–509), with no gaps
            # and no lettered inserts; four numbers (7, 111, 317 and
            # 371) were restored from their sequence position and are
            # flagged in their records' notes. The catalogue prints
            # no prices and no owners at all this year, so no record
            # names a lender; no record prints a medium; every record
            # has an artist and a title.
            'plain_range': (1, 509),
            'lettered': set(),
            'no_lender': 509,
            'no_medium': 509,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'rose-croix-1897',
        'file': 'rose-croix-1897.json',
        'title': 'Sixième Salon de la Rose+Croix (VIe Geste esthétique)',
        'printed_title': 'VIe Geste esthétique — Sixième Salon de la Rose+Croix',
        'subtitle': 'By Joséphin Péladan, for the Ordre de la Rose-Croix Catholique du Temple et du Graal',
        'venue': 'Galerie Georges Petit, Paris',
        'dates': '5 – 31 March 1897',
        'year': 1897,
        'organiser': 'Joséphin Péladan',
        'label': 'Rose+Croix 1897',
        'source': 'Printed catalogue, in a compilation by John Finnegan (supplied November 2026)',
        'notes': ('The sixth and last Salon de la Rose+Croix — Péladan’s sixth Geste '
                  'esthétique. These records come from John Finnegan’s compilation of the '
                  'printed catalogue and stand as compiled: nothing has been corrected or '
                  'completed. Titles are as catalogued, with the medium often given in '
                  'parentheses within the title; these salons print no sizes and no lenders. '
                  'Each artist’s address, as the catalogue prints it, is carried in the '
                  'record’s note. The numbering is complete, 1–217.'),
        'expect': {
            'total': 217,
            'sections': {'Catalogue': 217},
            # Plain catalogue numbers run 1–217 with no gaps and no
            # duplicates; there are no lettered inserts; no record
            # has a lender or a medium, and every record has a title
            # and an artist.
            'plain_range': (1, 217),
            'lettered': set(),
            'no_lender': 217,
            'no_medium': 217,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1897',
        'file': 'guildhall-1897.json',
        'title': 'Catalogue of the Loan Collection of Pictures',
        'subtitle': 'By Painters of the British School who have flourished during Her Majesty’s Reign',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '7 April – 14 July 1897',
        'year': 1897,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1897',
        'source': 'Internet Archive item catalogueofloanc00temp (Getty scan)',
        'notes': ('This scan drops the printed margin numbers wholesale: 73 have been restored from '
                  'their sequence position, each flagged in its record’s note and corroborated by the '
                  'catalogue’s Index of Artists. Two sizes are illegible in the scan. Two unnumbered '
                  'Jubilee exhibits shown with the exhibition — a marble bust and a miniature of Queen '
                  'Victoria — stand outside the catalogue’s numbering and are not recorded here. '
                  'Graves’s Century of Loan Exhibitions digests this exhibition but keys only 139 of '
                  'its 167 works, folding several pictures into merged records and missing the lettered '
                  'inserts — the printed catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 167,
            'sections': {'Gallery I': 58, 'Gallery II': 50, 'Gallery III': 59},
            # Plain catalogue numbers run 1–161 with no gaps; the
            # lettered inserts are 36A, 45A, 54A, 54B, 89A and 120A;
            # every record has a lender, a title and an artist.
            'plain_range': (1, 161),
            'lettered': {'36A', '45A', '54A', '54B', '89A', '120A'},
            'no_lender': 0,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1898',
        'file': 'aws-1898.json',
        'title': 'Illustrated Catalogue of the Thirty-First Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '31 January – 26 February 1898',
        'year': 1898,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1898',
        'source': 'Printed catalogue (New York, 1898); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-first annual exhibition of the American Water Color Society. '
                  'This catalogue keeps the form of 1897: its body has no “Owner or '
                  'Price” column at all — number, subject and artist only — so no '
                  'price and no owner is printed for any work, and no record here '
                  'carries a price note or a lender; the book’s notices still say '
                  'that prices include frames, and prices were evidently to be had '
                  'at the desk in the gallery. The hang keeps the five sections of '
                  '1896 and 1897 — the four galleries and the Corridor. Sixteen '
                  'works are illustrated in the catalogue, each flagged in its '
                  'record’s note — fourteen on the evidence of the body’s own '
                  '“(Illustration).” mark, with the full stop as in 1897, and two '
                  'more (no. 143, James Symington’s “Hypatia”, and no. 163, George '
                  'Wharton Edwards’s “Breakfast at the Blue Grape”) on the captions '
                  'of their plates alone, the body printing no mark against them; '
                  'eight captioned plates are bound in. One catalogue number (12) '
                  'was lost in the scan — an ink blot in this copy obscures its '
                  'printed figures — and has been restored from its sequence '
                  'position, flagged in its record’s note and corroborated by the '
                  'book’s own index. This copy is a former owner’s annotated copy: '
                  'pencil ticks, strokes and notes stand throughout it, and they '
                  'corrupt the text layer of the book’s index, though no body '
                  'reading. Every catalogue page was read against the page images '
                  'during the parse, as with the earlier catalogues. A handful of '
                  'artist names and titles stand exactly as the scan reads them — '
                  'the garbles are the scan’s, not the catalogue’s — and have not '
                  'been corrected; the book’s own spellings likewise stand as '
                  'printed — it prints both “F. K. M. Rehm” and “F. K. M. Rehn”, '
                  'and both “E. J. Hoklag” and “E. J. Holgate”. The Wm. T. Evans '
                  'Prize was $300 this year, as in 1895, 1896 and 1897.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 517,
            'sections': {'North Gallery': 98, 'East Gallery': 81,
                         'South Gallery': 140, 'West Gallery': 109,
                         'Corridor': 89},
            # Plain catalogue numbers run 1–517 complete, in five
            # contiguous blocks (North 1–98, East 99–179, South
            # 180–319, West 320–428, Corridor 429–517), with no gaps
            # and no lettered inserts; one number (12) was restored
            # from its sequence position and is flagged in its
            # record's note. The catalogue prints no prices and no
            # owners at all this year, so no record names a lender;
            # no record prints a medium; every record has an artist
            # and a title.
            'plain_range': (1, 517),
            'lettered': set(),
            'no_lender': 517,
            'no_medium': 517,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1898',
        'file': 'guildhall-1898.json',
        'title': 'Catalogue of the Loan Collection of Pictures by Painters of the French School',
        'subtitle': 'With Descriptive and Biographical Notes',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '6 June – 31 August 1898',
        'year': 1898,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1898',
        'source': 'Internet Archive item catalogueofloanc00guil_0 (Getty scan)',
        'notes': ('This copy of the catalogue is the pre-opening issue, marked “UNDER REVISION” on its '
                  'cover; the records are taken from that text. 46 catalogue numbers have been restored '
                  'from their sequence position, each flagged in its record’s note. Four sizes are '
                  'incomplete in the scan. A separately numbered section of medals and objects of art '
                  '(nos. 155–162) is not pictures and is not recorded here. Graves’s Century of Loan '
                  'Exhibitions covers 143 of these 156 works in substance — the printed catalogue is '
                  'the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 156,
            'sections': {'Gallery I': 49, 'Gallery II': 73, 'Gallery III': 34},
            # Plain catalogue numbers run 1–154 with no gaps; the
            # lettered inserts are 43A and 45A; every record has a
            # lender, a title and an artist.
            'plain_range': (1, 154),
            'lettered': {'43A', '45A'},
            'no_lender': 0,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1899',
        'file': 'aws-1899.json',
        'title': 'Illustrated Catalogue of the Thirty-Second Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '13 February – 11 March 1899',
        'year': 1899,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1899',
        'source': 'Printed catalogue (New York, 1899); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-second annual exhibition of the American Water Color Society. '
                  'This catalogue keeps the form of 1897 and 1898: its body has no '
                  '“Owner or Price” column at all — number, subject and artist only '
                  '— so no price and no owner is printed for any work, and no record '
                  'here carries a price note or a lender; the book’s notices still '
                  'say that prices include frames, and prices were evidently to be '
                  'had at the desk in the gallery. The hang keeps the five sections '
                  'of 1896–1898 — the four galleries and the Corridor — but the '
                  'Corridor shrinks to nineteen works this year. Twenty-one works '
                  'are illustrated in the catalogue, each flagged in its record’s '
                  'note — twenty on the evidence of the body’s own '
                  '“(Illustration).” mark, with the full stop as in 1897 and 1898, '
                  'and one more (no. 340, L. C. Earle’s “Nimrod and his '
                  'Granddaughter”) on the caption of its plate alone, the body '
                  'printing no mark against it; twenty captioned plates are bound '
                  'in, the plate of no. 84 serving as the frontispiece, and no. 341 '
                  'carries the mark but no plate of it is bound in this copy. Ten '
                  'of the plates are landscape plates whose captions stand '
                  'vertically along the plate’s edge and appear nowhere in the '
                  'scan’s text layer. Twenty-two catalogue numbers were lost or '
                  'garbled in the scan and have been restored from their sequence '
                  'position, each flagged in its record’s note — eighteen whose '
                  'printed figures the scan loses or garbles beyond reading, and '
                  'four seated where the scan reads a different figure (no. 119 '
                  'read as 11, no. 143 as 43, no. 153 as 1, no. 482 as 0); the '
                  'book’s own index corroborates the restored numbers, among them '
                  'nos. 316 and 482, though the index carries faults of its own — '
                  'from no. 471 to no. 490 it cites every number one lower than '
                  'the body, leaving no. 491 cited by nobody, and it cites Sydney '
                  'K. Hartman at an impossible “572”. Every catalogue page was '
                  'read against the page images during the parse, as with the '
                  'earlier catalogues. A handful of artist names and titles stand '
                  'exactly as the scan reads them — the garbles are the scan’s, '
                  'not the catalogue’s — and have not been corrected; the book’s '
                  'own spellings likewise stand as printed — it prints “A '
                  'Venician” (no. 144), and no. 84’s title, “Memories of the Red '
                  'Ear”, stands in both the body and its plate caption, though '
                  'the picture shows a man husking corn. The Wm. T. Evans Prize '
                  'was $300 this year, as in 1895, 1896, 1897 and 1898.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 491,
            'sections': {'North Gallery': 118, 'East Gallery': 99,
                         'South Gallery': 143, 'West Gallery': 112,
                         'Corridor': 19},
            # Plain catalogue numbers run 1–491 complete, in five
            # contiguous blocks (North 1–118, East 119–217, South
            # 218–360, West 361–472, Corridor 473–491), with no gaps
            # and no lettered inserts; twenty-two numbers were
            # restored from their sequence position and are flagged
            # in their records' notes. The catalogue prints no
            # prices and no owners at all this year, so no record
            # names a lender; no record prints a medium; every
            # record has an artist and a title.
            'plain_range': (1, 491),
            'lettered': set(),
            'no_lender': 491,
            'no_medium': 491,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1899',
        'file': 'guildhall-1899.json',
        'title': 'Catalogue of the Loan Collection of Pictures and Drawings by J. M. W. Turner, R.A.',
        'subtitle': 'And of a Selection of Pictures by some of his Contemporaries. With Descriptive and Biographical Notes',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '11 April – 11 July 1899',
        'year': 1899,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1899',
        'source': 'Internet Archive item catalogueloanco00gallgoog (Harvard scan)',
        'notes': ('Turner entries in Galleries I and II print no by-line; the artist is supplied from '
                  'the catalogue’s title and flagged in each record. Gallery II prints no medium word '
                  '— the works are the water colour drawings of its heading. Nos. 66–69 do not exist '
                  'in the printed catalogue — the Liber Studiorum list passes from 65 to 70. '
                  '26 numbers have been restored from their sequence position, each flagged, and '
                  'seven sizes are illegible in the scan. Graves’s Century of Loan Exhibitions keys '
                  'only 119 of these 195 works, omitting the Liber Studiorum impressions and folding '
                  'whole runs into unnumbered digests — the printed catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 195,
            'sections': {'Gallery I': 81, 'Gallery II': 79, 'Gallery III': 35},
            # Plain catalogue numbers run 1–196, but nos. 66–69 do not
            # exist in the printed catalogue (the Liber Studiorum list
            # passes from 65 to 70); the lettered inserts are 82A, 82B
            # and 82C; every record has a lender, a title and an artist.
            'plain_range': (1, 196),
            'absent_numbers': [66, 67, 68, 69],
            'lettered': {'82A', '82B', '82C'},
            'no_lender': 0,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1900',
        'file': 'aws-1900.json',
        'title': 'Illustrated Catalogue of the Thirty-Third Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the Waldorf-Astoria, New York',
        'venue': 'Waldorf-Astoria, New York',
        'dates': '5 – 17 February 1900',
        'year': 1900,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1900',
        'source': 'Printed catalogue (New York, 1900); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-third annual exhibition of the American Water Color Society. '
                  'This year the exhibition leaves the National Academy of Design, its '
                  'home throughout the earlier volumes in this run, for the Galleries '
                  'of the Waldorf-Astoria, New York, entered from Main 33rd Street. '
                  'This catalogue keeps the form of 1897, 1898 and 1899 for a fourth '
                  'year: its body has no “Owner or Price” column at all — number, '
                  'subject and artist only — so no price and no owner is printed for '
                  'any work, and no record here carries a price note or a lender; the '
                  'book’s notices still say that prices include frames, and prices '
                  'were evidently to be had at the desk in the gallery. The hang is '
                  'arranged not by gallery but by room, in one continuous numbering: '
                  'the Large Room holds nos. 1–169, with four lettered inserts — '
                  '143a and 143b after no. 143, 169a and 169b after no. 169 — and the '
                  'Small Room nos. 170–256. Nineteen works are illustrated in the '
                  'catalogue, each flagged in its record’s note on the evidence of '
                  'the captions of the plates alone — a change from 1897–1899, for '
                  'this book prints no “(Illustration).” mark against any entry in '
                  'its body at all; nineteen captioned plates are bound in, the '
                  'plate of no. 16, J. G. Brown’s “Dreamers”, serving as the '
                  'frontispiece. Twelve catalogue numbers were lost or garbled in '
                  'the scan and have been restored from their sequence position, '
                  'each flagged in its record’s note — nos. 11–21, whose tens figures '
                  'the scan drops wholesale on the first catalogue page, and '
                  'no. 111; the book’s own index corroborates the restored numbers '
                  'and is the cleanest index of the ten volumes, agreeing with the '
                  'body on every point the scan lets it be read, and citing all four '
                  'lettered inserts. Every catalogue page was read against the page '
                  'images during the parse, as with the earlier catalogues. A handful '
                  'of artist names and titles stand exactly as the scan reads them — '
                  'the garbles are the scan’s, not the catalogue’s — and have not '
                  'been corrected; the book’s own spellings likewise stand as '
                  'printed — it prints “Venice, from the San Giorgia” (no. 14), '
                  '“Puetra del Patro Machuca, Alhambra” (no. 149) and “Campodoglio, '
                  'from Roman Forum” (no. 148), and McCord’s name in full, “George '
                  'H. McCord”, at nos. 172 and 181, “Geo. H. McCord” elsewhere. The '
                  'Wm. T. Evans Prize was $300 this year, as in 1895–1899.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 260,
            'sections': {'Large Room': 173, 'Small Room': 87},
            # Plain catalogue numbers run 1–256 complete, in two
            # contiguous room blocks (Large Room 1–169 with its four
            # lettered inserts, Small Room 170–256), with no gaps;
            # the lettered inserts are 143a, 143b, 169a and 169b;
            # twelve numbers (11–21 and 111) were restored from
            # their sequence position and are flagged in their
            # records' notes. The catalogue prints no prices and no
            # owners at all this year, so no record names a lender;
            # no record prints a medium; every record has an artist
            # and a title.
            'plain_range': (1, 256),
            'lettered': {'143a', '143b', '169a', '169b'},
            'no_lender': 260,
            'no_medium': 260,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1901',
        'file': 'aws-1901.json',
        'title': 'Illustrated Catalogue of the Thirty-Fourth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the Building, formerly National Academy of Design, New York',
        'venue': 'National Academy of Design, New York',
        'dates': '11 February – 28 March 1901',
        'year': 1901,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1901',
        'source': 'Printed catalogue (New York, 1901); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-fourth annual exhibition of the American Water Color Society. '
                  'This year the exhibition returns to its old home — the galleries '
                  'of the building formerly the National Academy of Design, at '
                  'Twenty-Third Street and Fourth Avenue — after 1900’s single '
                  'year at the Waldorf-Astoria. This catalogue keeps the form of '
                  '1897, 1898, 1899 and 1900 for a fifth year: its body has no '
                  '“Owner or Price” column at all — number, subject and artist '
                  'only — so no price and no owner is printed for any work, and '
                  'no record here carries a price note or a lender; the book’s '
                  'notices still say that prices include frames, and inquiries in '
                  'regard to works for sale were to be made at the desk in the '
                  'gallery. The hang is arranged by gallery again — 1900’s two '
                  'rooms are gone — in one continuous numbering with no lettered '
                  'inserts: the North Gallery holds nos. 1–96, the East Gallery '
                  'nos. 97–172, the South Gallery nos. 173–321, the West Gallery '
                  'nos. 322–427 and the Corridor nos. 428–500. Twenty-two works '
                  'are illustrated in the catalogue, each flagged in its record’s '
                  'note on the evidence of the captions of the plates alone — as '
                  'in 1900, this book prints no “(Illustration).” mark against '
                  'any entry in its body at all; twenty-two captioned plates are '
                  'bound in, the plate of no. 131 serving as the frontispiece, '
                  'and sixteen of them are landscape plates whose captions stand '
                  'vertically along the plate’s edge and appear nowhere in the '
                  'scan’s text layer. Six catalogue numbers were lost or garbled '
                  'in the scan and have been restored from their sequence '
                  'position, each flagged in its record’s note — nos. 111 and '
                  '390, whose printed figures the scan loses outright, and nos. '
                  '113, 115 and 313, of which it reads only the last figure; '
                  'no. 141’s record carries a second note besides: the East '
                  'Gallery leaf is bound into this scan twice, in two different '
                  'print states — the copy parsed here omits no. 141 in print, '
                  'while the second copy prints it but omits nos. 142–144 — and '
                  'no. 141’s artist and title are read from the second copy’s '
                  'printed page, the book’s own index citing all four numbers. '
                  'No. 105’s number was reunited with its displaced printed '
                  'figures and carries no flag. The scan’s last leaf is a '
                  'frontispiece from another year’s catalogue — “35. '
                  'Puppies.—J. G. Brown” — and is given no record here; no. 35 '
                  'in this catalogue is Charles Warren Eaton’s “Evening in '
                  'Holland”. Every catalogue page was read against the page '
                  'images during the parse, as with the earlier catalogues, and '
                  'the book’s own index of artists was parsed as a cross-check; '
                  'the index carries faults of its own — it prints “Walter, '
                  'Horatio” for Walker at nos. 227 and 242, cites Otto Stark’s '
                  'no. 369 as “309” and Clark G. Voorhees’s no. 58 as “68”, and '
                  'files no. 342 under Moser where the body prints Moses — and '
                  'the body governs throughout. A handful of artist names and '
                  'titles stand exactly as the scan reads them — the garbles '
                  'are the scan’s, not the catalogue’s — and have not been '
                  'corrected: Léon Moran stands as “L£on Moran” at nos. 202, '
                  '391 and 396, as “L6on Moran” at no. 208 and unaccented at '
                  'no. 165. The book’s own spellings likewise stand as printed '
                  '— it prints “Rio St. Fraraco, Venice” (no. 212), “Canonicut” '
                  '(no. 294), “SS. Giovanni Paolo” (no. 425) and “Cadennabbia” '
                  '(no. 439), and the artist of nos. 133 and 272 under both '
                  '“Ohlefeld” and “Ihlefeld”. The Wm. T. Evans Prize was $300 '
                  'this year, as in 1895–1900.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 500,
            'sections': {'North Gallery': 96, 'East Gallery': 76,
                         'South Gallery': 149, 'West Gallery': 106,
                         'Corridor': 73},
            # Plain catalogue numbers run 1–500 complete, in five
            # contiguous blocks (North 1–96, East 97–172, South
            # 173–321, West 322–427, Corridor 428–500), with no gaps
            # and no lettered inserts; six numbers (111, 113, 115,
            # 141, 313 and 390) were restored from their sequence
            # position and are flagged in their records' notes. The
            # catalogue prints no prices and no owners at all this
            # year, so no record names a lender; no record prints a
            # medium; every record has an artist and a title.
            'plain_range': (1, 500),
            'lettered': set(),
            'no_lender': 500,
            'no_medium': 500,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1901',
        'file': 'guildhall-1901.json',
        'title': 'Descriptive and Biographical Catalogue of the Exhibition of the Works of Spanish Painters',
        'subtitle': 'By A. G. Temple, F.S.A., Director of the Art Gallery',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '30 April – 31 July 1901',
        'year': 1901,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1901',
        'source': 'Internet Archive item descriptivebiogr00guil_0 (Getty scan)',
        'notes': ('Gallery III is given over to Velasquez, with a life of the painter; Gallery IV '
                  'opens with a life of Fortuny. This copy is the pre-opening issue, marked '
                  '“Under revision” on its cover; the records stand as that text prints them. '
                  'Three numbers have been restored from their sequence position, each flagged; '
                  'no. 91 is entered under “Painter unknown”, as printed; seven entries at the end '
                  'are etchings and lithographs entered by heading only, with no medium or size '
                  'printed. Graves’s Century of Loan Exhibitions mixes this exhibition with another '
                  'Guildhall show of 1901; he keys 197 of these 209 numbers and covers 200 in '
                  'substance — the printed catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 209,
            'sections': {'Gallery I': 48, 'Gallery II': 50, 'Gallery III': 39, 'Gallery IV': 72},
            # Plain catalogue numbers run 1–208 with no gaps; the only
            # lettered insert is 73A; every record has a lender and a
            # title; exactly one record has no artist (no. 91, entered
            # under "Painter unknown").
            'plain_range': (1, 208),
            'lettered': {'73A'},
            'no_lender': 0,
            'no_title': 0,
            'no_artist': 1,
        },
    },
    {
        'id': 'aws-1902',
        'file': 'aws-1902.json',
        'title': 'Illustrated Catalogue of the Thirty-Fifth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Art Galleries, Madison Square South, New York',
        'venue': 'American Art Galleries, Madison Square South, New York',
        'dates': '21 April – 4 May 1902',
        'year': 1902,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1902',
        'source': 'Printed catalogue (New York, 1902); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-fifth annual exhibition of the American Water Color Society. '
                  'This year the exhibition is held at the American Art Galleries, '
                  'Madison Square South, New York, under the management of the '
                  'American Art Association. This catalogue changes the form of '
                  'the earlier volumes entirely: the galleries of 1891–1901 are '
                  'gone, and the body is arranged alphabetically by artist — each '
                  'artist’s heading, surname first, with the artist’s address '
                  'printed beneath it (the addresses are not carried into these '
                  'records), followed by that artist’s works, the works numbered '
                  'continuously 1–479 down the alphabet, all standing in the '
                  'single section the book itself heads “CATALOGUE”; the 479 '
                  'works stand under 222 artists’ headings as printed. The book '
                  'keeps the price-less form of 1897–1901 for a sixth year: there '
                  'is no “Owner or Price” column at all, so no price and no owner '
                  'is printed for any work, and no record here carries a price '
                  'note or a lender; the book’s notices still say that prices '
                  'include frames, and inquiries in regard to works for sale were '
                  'to be made at the desk in the gallery. Twenty-one works are '
                  'illustrated in the catalogue, each flagged in its record’s '
                  'note — the illustration evidence returns to the body this '
                  'year, each illustrated work carrying a bracketed '
                  '“[Illustration]” mark after its title — and the twenty-one '
                  'agree exactly with the book’s own List of Illustrations; '
                  'twenty plate leaves are bound in, but the plate for no. 35, '
                  'J. G. Brown’s “Puppies”, named in the List and marked in the '
                  'body, is not bound in this copy. Three catalogue numbers were '
                  'lost or garbled in the scan and have been restored from their '
                  'sequence position, each flagged in its record’s note — no. 1, '
                  'and nos. 110 and 111, whose printed lines the scan fuses into '
                  'two lines of interleaved type, so that neither title can be '
                  'read from the scan in its own order; those two titles are read '
                  'from the printed page — no. 110 is “Woodside, Maine” and '
                  'no. 111 “The Old Road”, the reverse of the order in which the '
                  'scan’s fragments stand — and each of those two records '
                  'carries a second note recording the fusion. The book prints '
                  'no artist index this year, so no index cross-check was '
                  'possible; its member lists were used only to corroborate name '
                  'forms. Every catalogue page was read against the page images '
                  'during the parse, as with the earlier catalogues. One heading '
                  'stands truncated in the book itself — “Of, George F., Jr.” '
                  '(nos. 298–299), the surname cut off in print, with no letters '
                  'before the “OF” — and one heading prints “Deceased” in place '
                  'of the artist’s address: C. Harry Eaton (nos. 107–109), whose '
                  'three records carry a note. A handful of artist names and '
                  'titles stand exactly as the scan reads them — the garbles are '
                  'the scan’s, not the catalogue’s — and have not been '
                  'corrected: the scan drops the printed accent in “Gruyere” '
                  '(no. 73), in Léon Moran’s name (nos. 246–252) and in '
                  '“Sandor, Mathias” (no. 375). The book’s own spellings '
                  'likewise stand as printed — it prints “Guidecca Canal, '
                  'Venice” (no. 415), “Guenn” (no. 314), “Lowery Day, Grand '
                  'Manan” (no. 25), “The Mosque of Tezzir Pasha Akka” (no. 132) '
                  'and “Caskel, Glen Columbkille” (no. 44). The Wm. T. Evans '
                  'Prize was $300 this year, as in 1895–1901; the book’s list '
                  'of past winners ends with the 1901 winner, Edward H. '
                  'Potthast’s “A Reverie”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 479,
            'sections': {'Catalogue': 479},
            # Plain catalogue numbers run 1–479 complete down the
            # alphabet, in the single section "Catalogue", with no
            # gaps and no lettered inserts; three numbers (1, 110
            # and 111) were restored from their sequence position
            # and are flagged in their records' notes. The catalogue
            # prints no prices and no owners at all this year, so no
            # record names a lender; no record prints a medium;
            # every record has an artist and a title.
            'plain_range': (1, 479),
            'lettered': set(),
            'no_lender': 479,
            'no_medium': 479,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1902',
        'file': 'guildhall-1902.json',
        'title': 'Catalogue of the Exhibition of a Selection of Works by French and English Painters of the Eighteenth Century',
        'subtitle': 'With Descriptive and Biographical Notes',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '22 April – 26 July 1902',
        'year': 1902,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1902',
        'source': 'Internet Archive item catalogueofexhib00guil (Getty scan)',
        'notes': ('One number has been restored from its sequence position, flagged in its record; '
                  'five sizes are not printed or are illegible in the scan, and six more are read '
                  'with Graves’s corroboration, each flagged. Two entries are headed “French School” '
                  'in place of a by-line, as printed. Graves’s Century of Loan Exhibitions keys 124 '
                  'of these 153 numbers and covers 136 in substance, folding eleven Gainsboroughs '
                  'into one digest record and missing all seven Lancrets — the printed catalogue is '
                  'the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 153,
            'sections': {'Gallery I': 52, 'Gallery II': 37, 'Gallery III': 14, 'Gallery IV': 50},
            # Plain catalogue numbers run 1–151 with no gaps; the
            # lettered inserts are 13A and 126A; every record has a
            # lender, a title, an artist and a medium.
            'plain_range': (1, 151),
            'lettered': {'13A', '126A'},
            'no_lender': 0,
            'no_title': 0,
            'no_artist': 0,
            'no_medium': 0,
        },
    },
    {
        'id': 'aws-1903',
        'file': 'aws-1903.json',
        'title': 'Illustrated Catalogue of the Thirty-Sixth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Art Galleries, Madison Square South, New York',
        'venue': 'American Art Galleries, Madison Square South, New York',
        'dates': '20 – 30 April 1903',
        'year': 1903,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1903',
        'source': 'Internet Archive item 1903AWS (Philadelphia Museum of Art copy)',
        'notes': ('The thirty-sixth annual exhibition of the American Water Color Society. '
                  'This year the exhibition is held at the American Art Galleries, '
                  'Madison Square South, New York, under the management of the '
                  'American Art Association, as in 1902; the copy recorded here is '
                  'the Internet Archive’s digitisation of the Philadelphia Museum '
                  'of Art’s copy (item 1903AWS), not one of the Frick Library scans '
                  'the rest of the run comes from. The catalogue keeps the form of '
                  '1902 entire: the galleries are gone, and the body is arranged '
                  'alphabetically by artist — each artist’s heading, surname '
                  'first, with the artist’s address printed beneath it (the '
                  'addresses are not carried into these records), followed by that '
                  'artist’s works, the works numbered continuously 1–299 down the '
                  'alphabet, all standing in the single section the book itself '
                  'heads “CATALOGUE”; the 299 works stand under 158 artists’ '
                  'headings as printed. The book keeps the price-less form of '
                  '1897–1902 for a seventh year: there is no “Owner or Price” '
                  'column at all, so no price and no owner is printed for any '
                  'work, and no record here carries a price note or a lender; the '
                  'book’s notices still direct buyers to the desk, payments to the '
                  'order of the American Art Association, and state that prices '
                  'include frames. Sixteen works are illustrated in the '
                  'catalogue, each flagged in its record’s note — each illustrated '
                  'work carrying a bracketed “[Illustration]” mark after its '
                  'title — and the sixteen agree exactly with the book’s own List '
                  'of Illustrations; all sixteen plates are bound in, no. 26 '
                  'serving as the frontispiece, and seven of the plate captions '
                  'print vertically at the leaf’s right side and never reach the '
                  'scan’s text layer, so every caption was read from its rendered '
                  'leaf. Two catalogue numbers were lost or garbled in the scan '
                  'and have been restored from their sequence position, each '
                  'flagged in its record’s note — no. 118, whose figure the scan '
                  'reads “lIS.”, the same garble it makes of no. 115’s figure, and '
                  'no. 206, read “zoo.”, the same garble as no. 200’s; both stand '
                  'correctly in print. The book prints no artist index this year, '
                  'so no index cross-check was possible; its member lists were '
                  'cross-checked against the headings’ marks instead — every '
                  'artist whose heading carries the Society’s mark stands in the '
                  'member lists, and three members’ headings print no mark at '
                  'all, the book’s own inconsistencies, the records standing as '
                  'printed: Geo. H. Smillie (nos. 257–261), F. Hopkinson Smith '
                  '(nos. 262–264) and Wm. J. Whittemore (no. 288). One heading '
                  'prints “Deceased” in place of the artist’s address: Henry '
                  'Farrer (nos. 75–91), whose seventeen records carry a note. '
                  'Every catalogue page was read against the page images during '
                  'the parse, as with the earlier catalogues. A handful of titles '
                  'stand exactly as the scan reads them — the garbles are the '
                  'scan’s, not the catalogue’s — and have not been corrected: '
                  '“The Wauderer” (no. 15), “Sheep on the Dnnes” (no. 48), '
                  '“Suuset Glow” (no. 97) and “The Damascns Blade” (no. 239) '
                  'among them. The book’s own spellings likewise stand as '
                  'printed — it prints “Over High Haith” (no. 56), “Innsbrook” '
                  '(no. 259), “Girl in Kimona” (no. 298) and “Fujiyama on a '
                  'Winters Eve” (no. 299); and one heading, “Hilderbrandt, Howard '
                  'L.”, is print-accurate with the R and stands uncorrected. The '
                  'Wm. T. Evans Prize was $300 this year, as in 1895–1902; the '
                  'book’s list of past winners ends with the 1902 winner, Arthur '
                  'I. Keller’s “The Finishing Touches”, and the 1903 award is not '
                  'recorded in this book.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 299,
            'sections': {'Catalogue': 299},
            # Plain catalogue numbers run 1–299 complete down the
            # alphabet, in the single section "Catalogue", with no
            # gaps and no lettered inserts; two numbers (118 and
            # 206) were restored from their sequence position and
            # are flagged in their records' notes. The catalogue
            # prints no prices and no owners at all this year, so
            # no record names a lender; no record prints a medium;
            # every record has an artist and a title.
            'plain_range': (1, 299),
            'lettered': set(),
            'no_lender': 299,
            'no_medium': 299,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1903',
        'file': 'guildhall-1903.json',
        'title': 'Catalogue of the Exhibition of a Selection of Works by Early and Modern Painters of the Dutch School. With Descriptive and Biographical Notes',
        'subtitle': 'By A. G. Temple, F.S.A., Director of the Art Gallery',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '28 April – 25 July 1903',
        'year': 1903,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1903',
        'source': 'Internet Archive item catalogueofexhib00guil_5 (Getty scan)',
        'notes': ('The Twelfth Exhibition of the Guildhall series. Gallery I held the Gassiot '
                  'bequest as part of the exhibition, but the catalogue prints no list of it, so '
                  'those works are not recorded here. Eight catalogue numbers have been restored '
                  'from their sequence position, each flagged in its record’s note. No. 100’s '
                  'heading is lost in the scan — its artist and lender come from the catalogue’s '
                  'own indexes, and its title, medium and size are not recorded. A printed notice '
                  'in the catalogue records that nos. 137, 162 and 187 were returned to their '
                  'owners in early June. Graves’s Century of Loan Exhibitions keys 144 of these '
                  '196 numbers and covers 158 in substance, lacking 38 outright — the printed '
                  'catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 196,
            'sections': {'Galleries II and III': 133, 'Gallery IV': 63},
            # Plain catalogue numbers run 1–195 with no gaps and no
            # absent numbers; the only lettered insert is 187A; every
            # record has an artist and a lender; exactly one record
            # has no title (no. 100, whose heading is lost in the
            # scan); 33 records print no medium.
            'plain_range': (1, 195),
            'lettered': {'187A'},
            'no_lender': 0,
            'no_title': 1,
            'no_artist': 0,
            'no_medium': 33,
        },
    },
    {
        'id': 'aws-1904',
        'file': 'aws-1904.json',
        'title': 'Illustrated Catalogue of the Thirty-Seventh Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Art Galleries, Madison Square South, New York',
        'venue': 'American Art Galleries, Madison Square South, New York',
        'dates': '29 April – 13 May 1904',
        'year': 1904,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1904',
        'source': 'Internet Archive item 1904AWS (Philadelphia Museum of Art copy)',
        'notes': ('The thirty-seventh annual exhibition of the American Water Color Society. '
                  'This year the exhibition is held at the American Art Galleries, '
                  'Madison Square South, New York, under the management of the '
                  'American Art Association, as in 1902 and 1903; the copy '
                  'recorded here is the Internet Archive’s digitisation of the '
                  'Philadelphia Museum of Art’s copy (item 1904AWS), not one of '
                  'the Frick Library scans the rest of the run comes from — this '
                  'copy carries the owner’s stamp of the exhibiting artist '
                  'J. C. Nicoll and a pencilled “May 1911”. The catalogue keeps '
                  'the form of 1902 and 1903 entire: the body is arranged '
                  'alphabetically by artist — each artist’s heading, surname '
                  'first, with the artist’s address printed beneath it (the '
                  'addresses are not carried into these records), followed by '
                  'that artist’s works, the works numbered 1–345 down the '
                  'alphabet with four lettered inserts the book prints with a '
                  'capital letter after the figure — no. 167A, Percival '
                  'De Luce’s “Solid Comfort”; nos. 270A and 270B, Alexander '
                  'Schilling’s “Spring” and “Hay Stacks”; and no. 321A, Horatio '
                  'Walker’s “Shepherdess and Sheep” — 349 works in all, standing '
                  'in the single section the book itself heads “CATALOGUE”, '
                  'under 184 artists’ headings as printed. The book keeps the '
                  'price-less form of 1897–1903 for an eighth year: there is no '
                  '“Owner or Price” column at all, so no price and no owner is '
                  'printed for any work, and no record here carries a price '
                  'note or a lender; no size or medium is printed for any entry '
                  'either — the absence was verified directly, a sweep of the '
                  'catalogue body’s text finding no “$”, “price”, “loaned”, '
                  '“owner” or “for sale” token anywhere in it. The book’s '
                  'notices still direct buyers to the desk, payments “to the '
                  'order of the American Art Association, Managers”, and state '
                  'that prices include frames. Sixteen works are illustrated '
                  'in the catalogue, each flagged in its record’s note — each '
                  'illustrated work carrying a bracketed “[Illustration]” mark '
                  'after its title — and the sixteen agree exactly with the '
                  'book’s own List of Illustrations; all sixteen plates are '
                  'bound in, no. 16, J. G. Brown’s “Making a Soaker”, serving '
                  'as the frontispiece, and five of the plate captions print '
                  'vertically at the leaf’s right side and never reach the '
                  'scan’s text layer, so every caption was read from its '
                  'rendered leaf. Two entries stand transposed in print: Harry '
                  'Fenn’s no. 91, “Mill Street, Warwick”, is printed above his '
                  'no. 90, “A Surrey Garden” — the records stand in the printed '
                  'order, each under its printed number, each carrying a note. '
                  'Three catalogue numbers were lost or garbled in the scan '
                  'and have been restored from their sequence position, each '
                  'flagged in its record’s note — no. 8, whose printed figure '
                  'the scan reads as the letter “K”, and nos. 98 and 180, whose '
                  'figures it reads “gS.” and “ISo.”, the 5/8 confusion of 1903 '
                  'in both; all three stand correctly in print. One entry '
                  'carries a printed designation after its title: no. 318, '
                  'T. De Thulstrup’s “Three Generals”, whose bracketed '
                  '“[A Sketch]” stands in the record’s note, not its title. '
                  'The book prints no artist index this year, so no index '
                  'cross-check was possible; its member lists were '
                  'cross-checked against the headings’ marks instead — every '
                  'artist whose heading carries the Society’s mark stands in '
                  'the member lists (52 distinct marked artists, 150 records '
                  'under marked headings), and no heading prints “Deceased” in '
                  'place of an address this year. Every catalogue page was '
                  'read against the page images during the parse, as with the '
                  'earlier catalogues. The book’s own spellings stand as '
                  'printed — it prints “Dusk of River Launs” (no. 214), '
                  '“Cyklamen” (no. 254) and “Mohigan Bluffs” (no. 259), not '
                  'Mohegan; the body prints no. 222’s title with a comma, '
                  '“Night, before Rain”, where the List of Illustrations and '
                  'the plate caption print it without, and the record follows '
                  'the body; and the List prints “Chicadees” for no. 13 where '
                  'the body and the record print “Chickadees”. The Wm. T. '
                  'Evans Prize was $300 this year, as in 1895–1903; the book’s '
                  'list of past winners runs 1888–1903 and ends with the 1903 '
                  'winner, Colin Campbell Cooper’s “Sky Scrapers, Broad St., '
                  'New York” — so the 1903 award, unrecorded in the 1903 book, '
                  'is recorded here; the 1904 award is not recorded in this '
                  'book.'),
        # The parse stores the plain catalogue numbers as integers
        # and the lettered inserts as strings; the built file
        # carries them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 349,
            'sections': {'Catalogue': 349},
            # Plain catalogue numbers run 1–345 complete down the
            # alphabet, in the single section "Catalogue"; the
            # lettered inserts are 167A, 270A, 270B and 321A; three
            # numbers (8, 98 and 180) were restored from their
            # sequence position and are flagged in their records'
            # notes. The catalogue prints no prices and no owners
            # at all this year, so no record names a lender; no
            # record prints a medium; every record has an artist
            # and a title.
            'plain_range': (1, 345),
            'lettered': {'167A', '270A', '270B', '321A'},
            'no_lender': 349,
            'no_medium': 349,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1904',
        'file': 'guildhall-1904.json',
        'title': 'Catalogue of The Exhibition of Works by Irish Painters',
        'subtitle': 'With Descriptive and Biographical Notes',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '31 May – 23 July 1904',
        'year': 1904,
        'organiser': 'Hugh P. Lane',
        'label': 'Guildhall 1904',
        'source': 'Internet Archive item catalogueofexhib00guil_7 (Getty scan)',
        'notes': ('Catalogue no. 258 does not exist in the printed catalogue — a gap in the original numbering, '
                  'not a lost record. 27 catalogue numbers were illegible in the scan and have been restored from '
                  'their sequence position; each is flagged in its record’s note, shown under the title. '
                  'Some entries print no size, medium or lender, and none has been inferred. '
                  'The catalogue’s text carries ordinary OCR noise, so the odd title or name is garbled. '
                  'The catalogue illustrates 47 of the works on unnumbered plate leaves; each plate is '
                  'shown beside its record, cropped from the catalogue’s own pages — the caption printed '
                  'with the plate is the evidence for the match. One further plate (a portrait captioned '
                  '“John Lavery, No. 170”) is not shown: the catalogue’s own entry no. 170 is Norman '
                  'Garstin’s “Moulin de la Ville”, so the plate cannot be assigned without guessing.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 466,
            'sections': {'Gallery I': 72, 'Gallery II': 58,
                         'Gallery III': 64, 'Gallery IV (Water Colours)': 272},
            'absent_numbers': [258],
        },
    },
    {
        'id': 'aws-1905',
        'file': 'aws-1905.json',
        'title': 'Catalogue of the Thirty-Eighth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the National Arts Club, New York',
        'venue': 'National Arts Club, New York',
        'dates': '10 – 27 March 1905',
        'year': 1905,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1905',
        'source': 'Internet Archive item 1905AWS (Metropolitan Museum Library copy)',
        'notes': ('The thirty-eighth annual exhibition of the American Water Color Society — '
                  'a much smaller show than the years around it, held at the National '
                  'Arts Club, 37–39 West Thirty-Fourth Street, New York, by courtesy '
                  'of the National Arts Club; the copy recorded here is the Internet '
                  'Archive’s digitisation of the Metropolitan Museum Library’s copy '
                  '(item 1905AWS), not one of the Frick Library scans the rest of the '
                  'run comes from. The catalogue keeps the alphabetical arrangement '
                  'of 1902–1904 for a last year: the body is arranged alphabetically '
                  'by artist — each artist’s heading, surname first, with the '
                  'artist’s address printed beneath it (the addresses are not '
                  'carried into these records), followed by that artist’s works, '
                  'the works numbered 1–69 down the alphabet with four lettered '
                  'inserts the book prints — no. 5A, J. G. Brown’s “Puzzling It '
                  'Out”; no. 26A, Winslow Homer’s “Pulling in the Anchor”, which '
                  'stands at the foot of its page and was missed by the search '
                  'that first located this book, which reported 72 entries; and '
                  'nos. 66A and 66B, Ross Turner’s “Summer” and “The Ship of '
                  'Parsus” — 73 works in all, standing in the single section the '
                  'book itself heads “Catalogue”, under 47 artists’ headings as '
                  'printed. The book keeps the price-less form of the years since '
                  '1897 for a ninth year: no price is printed against any entry '
                  'and no owner or lender is named for any entry, so no record '
                  'here carries a price note or a lender; no size or medium is '
                  'printed for any entry either. The book’s notices still direct '
                  'buyers to inquire at the desk, payments to be made before the '
                  'close of the exhibition “to the order of James Symington, '
                  'Treasurer”, under the standing line “PRICES INCLUDE FRAMES”. '
                  'Unlike 1902–1904, no heading carries the Society’s “A.W.C.S.” '
                  'mark this year, and the notices do not explain one: no artist '
                  'string carries it. The book is not styled “Illustrated”, '
                  'prints no List of Illustrations and carries no illustration '
                  'mark against any entry, and there are no plates: no work is '
                  'illustrated in the catalogue. One catalogue number was lost '
                  'or garbled in the scan and has been restored from its '
                  'sequence position, flagged in its record’s note — no. 33, '
                  'Léon Moran’s “ Day Dreams ”, whose printed figure the scan '
                  'garbles beyond reading; the figure stands correctly in '
                  'print. The book prints no artist index, so the member rolls '
                  'were cross-checked against the body instead: all 47 body '
                  'surnames stand in the rolls. Every catalogue page was read '
                  'against the page images during the parse, as with the '
                  'earlier catalogues. Three titles stand exactly as the scan '
                  'reads them, their punctuation the scan’s, not the '
                  'catalogue’s — “The Norman Staircase. Canterburv” (no. 13), '
                  '“The Silversmith’s Bazaar. Damascus” (no. 21) and “Along the '
                  'Canal, Muiden. Holland” (no. 23) — and have not been '
                  'corrected; no. 5’s “A Bit ot Beach” is the book’s own '
                  'misprint, print and scan agreeing, and “The Ship of Parsus” '
                  '(no. 66B) stands as printed. The Wm. T. Evans Prize was $300 '
                  'this year, as in 1895–1904; the book’s list of winners runs '
                  '1888–1905 complete, and its latest line is this year’s award '
                  'itself: 1905, W. Granville Smith, “The Bay” — which hangs in '
                  'this body as no. 63; the same list’s 1904 line names Charles '
                  'Menté’s “The Old Mill Dam in Winter”.'),
        # The parse stores the plain catalogue numbers as integers
        # and the lettered inserts as strings; the built file
        # carries them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 73,
            'sections': {'Catalogue': 73},
            # Plain catalogue numbers run 1–69 complete down the
            # alphabet, in the single section "Catalogue"; the
            # lettered inserts are 5A, 26A, 66A and 66B; one number
            # (33) was restored from its sequence position and is
            # flagged in its record's note. The catalogue prints no
            # prices and no owners at all this year, so no record
            # names a lender; no record prints a medium; every
            # record has an artist and a title.
            'plain_range': (1, 69),
            'lettered': {'5A', '26A', '66A', '66B'},
            'no_lender': 73,
            'no_medium': 73,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1906',
        'file': 'aws-1906.json',
        'title': 'Illustrated Catalogue of the Thirty-Ninth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '3 – 26 May 1906',
        'year': 1906,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1906',
        'source': 'Printed catalogue (New York, 1906); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The thirty-ninth annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. After the alphabetical catalogues of 1902–1905 the book '
                  'returns to the hanging order of 1891–1901: the works are numbered '
                  'continuously 1–593 through five galleries — the South Gallery '
                  '(nos. 1–128), the Central Gallery (nos. 129–242, sub-headed '
                  '“ETCHINGS”), the East Gallery (nos. 243–328) and the West Gallery '
                  '(nos. 329–416), both sub-headed “DRAWINGS FOR ILLUSTRATION IN '
                  'BLACK AND WHITE, AND COLOR”, and the Vanderbilt Gallery '
                  '(nos. 417–593), the largest of the five — 594 records in all, '
                  'standing under 227 artists’ headings, 208 of the records carrying '
                  'the Society’s “A.W.C.S.” mark. The price element returns with the '
                  'galleries, after the nine price-less years 1897–1905: under each '
                  'title stands a price, or a lender line (“Loaned by …”, three of '
                  'them in the form “Owner,”), or nothing — 427 works are priced '
                  'for sale in the catalogue, the price standing in each record’s '
                  'note and the prices including frames, 75 name a lender and 92 '
                  'have neither; the dearest work is Horatio Walker’s “The First '
                  'Snow” (no. 437), priced at $1,200. One number is printed twice: '
                  'no. 368, Arthur I. Keller’s “Illustration, Bret Harte’s ‘Her '
                  'Letter’”, stands twice in succession in the West Gallery, the '
                  'same number, title and price repeated — a duplication in the '
                  'book, not in the scan — and both printings are recorded, each '
                  'flagged in its note, so the West Gallery’s 88 numbers carry 89 '
                  'records. Eighteen works are illustrated in the catalogue, each '
                  'flagged in its record’s note; the body prints no illustration '
                  'marks, so the illustrated works are named by the book’s List of '
                  'Illustrations, and all eighteen plates are bound in this copy. '
                  'Three catalogue numbers were lost or garbled in the scan and '
                  'have been restored from their sequence position, each flagged '
                  'in its record’s note: nos. 110 and 111, whose number lines reach '
                  'the scan only as debris, and no. 584 — the book’s own misprint, '
                  'which prints “548.” for F. Luis Mora’s “The Keeper of the Bulls” '
                  'where the sequence and the book’s own index prove 584. The '
                  'artists’ addresses, which stood under the headings in 1891–1902, '
                  'stand only in the book’s artist index this year and are not '
                  'carried into these records; the index was cross-checked against '
                  'the body during the parse and the body governs every '
                  'disagreement between them. No medium and no size are printed '
                  'for any entry. A handful of names and titles stand exactly as '
                  'the scan reads them — “Hardenberqh” and “The Cenitury Company” '
                  'among them — and have not been corrected. The Wm. T. Evans Prize '
                  'was $300 this year, as in 1895–1902; the book’s list of past '
                  'winners runs 1888–1905, its latest line the 1905 award, '
                  'W. Granville Smith’s “The Bay”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 594,
            'sections': {'South Gallery': 128, 'Central Gallery': 114,
                         'East Gallery': 86, 'West Gallery': 89,
                         'Vanderbilt Gallery': 177},
            # Plain catalogue numbers run 1–593 complete through the
            # five galleries in the order hung (South 1–128, Central
            # 129–242, East 243–328, West 329–416, Vanderbilt
            # 417–593), with no gaps and no lettered inserts; ONE
            # number is printed twice in the book — no. 368 (Arthur
            # I. Keller, West Gallery), the same entry typeset twice
            # in succession — and both printings are recorded, so
            # 593 numbers carry 594 records. Three numbers (110, 111
            # and 584) were restored from their sequence position and
            # are flagged in their records' notes. 427 records carry
            # a price in the note, 75 name a lender and 92 have
            # neither; no record prints a medium or a size; every
            # record has an artist and a title.
            'plain_range': (1, 593),
            'lettered': set(),
            'duplicated': {'368': 2},
            'no_lender': 519,
            'no_medium': 594,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'guildhall-1906',
        'file': 'guildhall-1906.json',
        'title': 'Catalogue of the Exhibition of Works by Flemish and Modern Belgian Painters',
        'subtitle': 'By A. G. Temple, F.S.A., Director of the Art Gallery of the Corporation of London',
        'venue': 'Art Gallery of the Corporation of London (Guildhall Art Gallery)',
        'dates': '3 May – 28 July 1906',
        'year': 1906,
        'organiser': 'A. G. Temple',
        'label': 'Guildhall 1906',
        'source': 'Internet Archive item catalogueofexhib00temp_1 (Getty scan)',
        'notes': ('The Fourteenth Exhibition of the Guildhall series. This copy of the catalogue '
                  'is the pre-opening issue, marked “UNDER REVISION” on its cover; the records '
                  'stand as that text prints them. Twenty-seven catalogue numbers have been '
                  'restored from their sequence position, each flagged in its record’s note. '
                  'No lender has been taken from the book’s indexes. Graves’s Century of Loan '
                  'Exhibitions keys 191 of these 221 numbers and, counting his unnumbered '
                  'records, covers 194 of the 221 works, lacking 27 outright — the printed '
                  'catalogue is the authority here.'),
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 221,
            'sections': {'Gallery I': 81, 'Gallery II': 42, 'Gallery III': 47, 'Gallery IV': 51},
            # Plain catalogue numbers run 1–218 with no gaps and no
            # absent numbers; the lettered inserts are 59A, 140A and
            # 143A; exactly five records have no lender, one has no
            # title, two have no artist, and four print no medium.
            'plain_range': (1, 218),
            'lettered': {'59A', '140A', '143A'},
            'no_lender': 5,
            'no_title': 1,
            'no_artist': 2,
            'no_medium': 4,
        },
    },
    {
        'id': 'aws-1907',
        'file': 'aws-1907.json',
        'title': 'Illustrated Catalogue of the Fortieth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '2 – 26 May 1907',
        'year': 1907,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1907',
        'source': 'Printed catalogue (New York, 1907); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The fortieth annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The form of 1906 continues unchanged: the works are '
                  'numbered continuously 1–561 through five galleries — the South '
                  'Gallery (nos. 1–143), the Central Gallery (nos. 144–238, '
                  'sub-headed “ETCHINGS”), the East Gallery (nos. 239–302) and the '
                  'West Gallery (nos. 303–383), both sub-headed “DRAWINGS FOR '
                  'ILLUSTRATION IN BLACK AND WHITE, AND COLOR”, and the Vanderbilt '
                  'Gallery (nos. 384–561), the largest of the five — 561 records in '
                  'all, standing under 250 artists’ headings, 153 of the records '
                  'carrying the Society’s “A.W.C.S.” mark, one heading carrying it '
                  'qualified, “A.W.C.S. (Elect)”. Under each title stands a price, '
                  'or a lender line (“Loaned by …”, one of them in the form '
                  '“Owner,”), or nothing — 451 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note and the '
                  'prices including frames, 44 name a lender and 66 have neither; '
                  'the dearest work is Alphonse Mucha’s “Beatitudes” (no. 339), '
                  'priced at $5,000.00 — the highest price in any of the Society’s '
                  'catalogues parsed so far — followed by Childe Hassam’s '
                  '“Aphrodite” (no. 467) at $1,500. One entry stands under two '
                  'numbers in a single printed line: “295. 296. Two Decorations”, '
                  'by Will H. Bradley, loaned by Collier’s Weekly — both numbers '
                  'are recorded, each carrying the entry with a reciprocal note; '
                  'no. 296 is no placeholder and is not flagged restored, and the '
                  'book’s own index cites Bradley at both numbers. One catalogue '
                  'number was lost in the scan and has been restored from its '
                  'sequence position, flagged in its record’s note: no. 110, '
                  'Aloysius O’Kelly’s “A Canal Driver and Donkey Boy, Cairo”. '
                  'Nine works are illustrated in the catalogue, each flagged in '
                  'its record’s note; the body prints no illustration marks, so '
                  'the illustrated works are named by the book’s List of '
                  'Illustrations — no. 512, Arthur I. Keller’s “The Golden '
                  'Wedding”, is the frontispiece, and the plate of no. 111, '
                  'Charles P. Gruppé’s “November Evening”, is not bound in this '
                  'copy, that record resting on the List’s authority alone. '
                  'Medium words printed over whole blocks stand in the records’ '
                  'notes — Rufus Sheldon’s seven monotypes (nos. 305–311) and '
                  'George Senseney’s etchings in color among them — the Medium '
                  'field standing empty, as everywhere in this book; no medium '
                  'and no size are printed for any entry. The artists’ addresses '
                  'stand only in the book’s artist index and are not carried into '
                  'these records; the index was cross-checked against the body '
                  'during the parse and the body governs every disagreement '
                  'between them — the index’s own errors include sweeping Ernest '
                  'D. Ross’s five etchings (nos. 153–157) into its Roth entry and '
                  'Addison T. Millar’s six works (nos. 225–230) into Charles '
                  'Henry White’s. The book’s own errors stand as printed: the '
                  'heading “AETON, CHARLES WARREN” for Eaton at no. 393, a full '
                  'stop for the comma in “EATON. CHARLES WARREN” at no. 394 and '
                  'in “NICOLL. J. C.” at no. 550, the doubled comma in '
                  '“LABOURER,, J. E.” at no. 302, “The Yungfrau” twice over, the '
                  'comma-less heading “BALLIN HUGO”, and the etcher filed both '
                  'as “OLSON-NORDFELDT, BROR J.” and as “NORDFELDT, B. J. '
                  'OLSSON”. A handful of names and titles stand exactly as the '
                  'scan reads them — “Brigher, A. T.” for Bricher at no. 416 and '
                  'the lender “The Cehtury Company” at no. 315 among them — and '
                  'the scan’s dropping of the book’s accents stands throughout '
                  '(“Gruppe” for Gruppé, “Moran, Leon” for Léon Moran). The Wm. '
                  'T. Evans Prize was $300 this year, as in 1895–1906; the '
                  'book’s list of past winners runs 1888–1906, its latest line '
                  'the 1906 award, H. L. Hildebrandt’s “Sally”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 561,
            'sections': {'South Gallery': 143, 'Central Gallery': 95,
                         'East Gallery': 64, 'West Gallery': 81,
                         'Vanderbilt Gallery': 178},
            # Plain catalogue numbers run 1–561 complete through the
            # five galleries in the order hung (South 1–143, Central
            # 144–238, East 239–302, West 303–383, Vanderbilt
            # 384–561), with no gaps and no lettered inserts; no
            # number is printed twice — but one entry, Will H.
            # Bradley's "Two Decorations", is printed under two
            # numbers in a single line, "295. 296.", and both numbers
            # carry the entry, each with a reciprocal note. One
            # number (110) was restored from its sequence position
            # and is flagged in its record's note. 451 records carry
            # a price in the note, 44 name a lender and 66 have
            # neither; no record prints a medium or a size; every
            # record has an artist and a title.
            'plain_range': (1, 561),
            'lettered': set(),
            'no_lender': 517,
            'no_medium': 561,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1908',
        'file': 'aws-1908.json',
        'title': 'Illustrated Catalogue of the Forty-first Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '30 April – 24 May 1908',
        'year': 1908,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1908',
        'source': 'Printed catalogue (New York, 1908); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-first annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The format changes again: the five galleries of 1906–1907 '
                  'shrink to three, and the printed sub-headings disappear altogether — '
                  'the works are numbered continuously 1–610 through the South Gallery '
                  '(nos. 1–181), the Central Gallery (nos. 182–437) and the Vanderbilt '
                  'Gallery (nos. 438–610) — 610 records in all, standing under 291 '
                  'artists’ headings, 180 of the records carrying the Society’s '
                  '“A.W.C.S.” mark. Under each title stands a price, or a lender line '
                  '(“Loaned by …”), or nothing — 507 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note and the prices '
                  'including frames, 52 name a lender and 47 have neither — and four '
                  'entries carry a fourth form in the element’s place, “Made for the '
                  'Century Magazine.” (Jules Guerin’s nos. 376, 378, 381 and 413), '
                  'carried in the records’ notes with the lender standing empty. No '
                  'price in the book reaches $1,000 — after 1907’s $5,000 Mucha, the '
                  'ceiling falls back below four figures: the dearest work is Childe '
                  'Hassam’s “The Green Jade Gown” (no. 508), priced at $850.00, '
                  'followed by three works at $750.00 — Wm. H. Lippincott’s '
                  '“Helena—Pastel” (no. 9), Hugo Ballin’s “The Wood Nymph” (no. 549) '
                  'and C. Y. Turner’s “Heirlooms” (no. 568). Two lender lines are '
                  'printed in block form beneath a heading, over entries that carry no '
                  'individual element line — “Numbers 272 to 283 loaned by the Century '
                  'Company” under Timothy Cole and “423-426 loaned by Charles '
                  'Scribner’s Sons” under Edward Penfield — the lender applied to '
                  'every record of each block, each record’s note quoting the block '
                  'line; and one lender, at no. 422, is genuinely just “Mr. W.” in '
                  'print, and stands as printed. The numbering runs 1–610 complete, '
                  'with no gaps, no lettered inserts, no joint entries and no number '
                  'printed twice; three numbers were restored, each settled from the '
                  'printed page: no. 11, F. K. M. Rehn’s “The Moonlit Sea—Pastel”, '
                  'stands in the book without a printed number at all, between nos. 10 '
                  'and 12, its number restored from the sequence and flagged in its '
                  'record’s note; no. 111’s figures reach the scan only as letter '
                  'debris; and no. 246’s number is glued to its title by a dash, the '
                  'book’s own. Nine works are illustrated in the catalogue, each '
                  'flagged in its record’s note; the body prints no illustration '
                  'marks, so the illustrated works are named by the book’s List of '
                  'Illustrations, and all nine plates are bound in this copy — '
                  'no. 600, Colin Campbell Cooper’s “Grande Place, Antwerp”, is the '
                  'frontispiece. Medium words stand inside the titles as printed '
                  '(“The Hemlock Woods—Pastel”, “Charleston—Dry point”); no medium is '
                  'printed as a field and no size is printed for any entry, so Medium '
                  'and Size stand empty throughout. The artists’ addresses stand only '
                  'in the book’s artist index and are not carried into these records; '
                  'the index is incomplete in this copy — two of its leaves, carrying '
                  'the surnames Nicholls to Smith, are wanting — and was cross-checked '
                  'against the body on its surviving leaves during the parse, the body '
                  'governing every disagreement; its conflicts with the body are all '
                  'classified in the parse log, among them the index’s own spellings '
                  '“Chamberlin” for Chamberlain (no. 172) and “Andresen” for Andersen '
                  '(no. 450). The book’s own errors stand as printed: the doubled '
                  'comma in “CRAWFORD,, EARL STETSON” at no. 377, the word “Brush” '
                  'printed twice across a line break in no. 545’s title (“A Summer '
                  'Shower in the Sage Brush Brush Country”), “Nicholas Biddle, Esd.” '
                  'for Esq. in no. 32’s lender, the spellings “Poinsetta” (no. 95), '
                  '“Juffrow Knitting” (no. 603), “Mt. Magunticook” (no. 465), '
                  '“Caudebec” (no. 164) and “The Jinneeyeh” (no. 410), and Arthur '
                  'Keller filed as “Arthur L.” at no. 338 and as “Arthur I.” at '
                  'no. 346 — the book prints both, and both stand. Entries the book '
                  'itself prints twice under two numbers stand twice — Ruth Sypherd '
                  'Clements’s “Enfant au Luxembourg” at nos. 368 and 391 among them — '
                  'each printing with its own element line. A handful of names and '
                  'titles stand exactly as the scan reads them — “E.oth, Ernest D.” '
                  'for Roth at nos. 296–300, “Squbre, Maud Hunt” for Squire at '
                  'no. 243, “Watehing Leopards” (no. 439) and “Sfunset in the Alps” '
                  '(no. 605) among them — and the scan’s dropping of the book’s '
                  'accents stands throughout (“Vigee” for Vigée, “Cafe” for Café). '
                  'The Wm. T. Evans Prize was $300 this year, as in 1895–1907; the '
                  'book’s list of past winners runs 1888–1907, its latest line the '
                  '1907 award, W. H. Drake’s “The Lion’s Lair”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 610,
            'sections': {'South Gallery': 181, 'Central Gallery': 256,
                         'Vanderbilt Gallery': 173},
            # Plain catalogue numbers run 1–610 complete through the
            # three galleries in the order hung (South 1–181, Central
            # 182–437, Vanderbilt 438–610), with no gaps, no lettered
            # inserts, no joint entries and no number printed twice.
            # Three numbers were restored from the printed page:
            # no. 11, which the book prints without a number at all
            # (flagged in its record's note), no. 111 (its figures
            # reach the scan only as debris) and no. 246 (its number
            # glued to its title). 507 records carry a price in the
            # note, 52 name a lender, 47 have neither and four carry
            # "Made for the Century Magazine" in the element's place;
            # no record prints a medium or a size; every record has
            # an artist and a title.
            'plain_range': (1, 610),
            'lettered': set(),
            'no_lender': 558,
            'no_medium': 610,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1909',
        'file': 'aws-1909.json',
        'title': 'Illustrated Catalogue of the Forty-second Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '29 April – 23 May 1909',
        'year': 1909,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1909',
        'source': 'Printed catalogue (New York, 1909); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-second annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The three galleries of 1908 stand again — the South '
                  'Gallery (nos. 1–178), the Central Gallery (nos. 179–430) and the '
                  'Vanderbilt Gallery (nos. 431–598), the works numbered '
                  'continuously 1–598 — but the entry form changes entirely: the '
                  'galleries are headed in roman capitals (1908’s blackletter is '
                  'gone), there are no printed sub-headings anywhere, and each '
                  'entry stands on one line, its element on the same line as its '
                  'number and title — a price in whole dollars, or “Owned by …”, '
                  'or “Courtesy of …”, or nothing: 598 records in all, standing '
                  'under 248 artists’ headings, 216 of the records carrying the '
                  'Society’s “A.W.C.S.” mark; 466 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note and the '
                  'prices including frames, 54 name a lender (36 “Owned by”, 17 '
                  '“Courtesy of”, and one permission credit) and 78 have neither. '
                  'The dearest work in the book is Clara T. MacChesney’s “Still '
                  'Life” (no. 57), priced at $1,000.00 — the only four-figure '
                  'price in the book — followed by Ernest Albert’s “Moonrise” '
                  '(no. 475) at $800.00, Albert Sterner’s “The Visitor” (no. 112) '
                  'at $750.00 and three works at $600.00 (nos. 492, 500 and 559); '
                  'the cheapest are two works by Frank Melville at $5.00 (nos. 204 '
                  'and 266). One permission credit stands in the element’s place: '
                  'no. 308, William Levy’s “Dr. William B. Guthrie”, “By permission '
                  'of Dr. Guthrie.” — the lender standing as “Dr. Guthrie.” with '
                  'the credit quoted in the record’s note, the book’s only '
                  'instance. The numbering runs 1–598 complete, with no gaps, no '
                  'lettered inserts, no joint entries and no number printed '
                  'twice; three numbers were restored from the sequence, each '
                  'flagged in its record’s note: no. 110, whose printed figures '
                  'the scan’s text layer reads as the word “no.”; no. 111, whose '
                  'figures reach the layer as the debris “HI.”; and no. 519, '
                  'whose figures are fused to its title as “5i9i”, read on the '
                  'printed page. Twenty-three works are illustrated in the '
                  'catalogue, each flagged in its record’s note; the body prints '
                  'no illustration marks, so the illustrated works are named by '
                  'the book’s List of Illustrations, and all 23 plates are bound '
                  'in this copy, one or two to a leaf — no. 578 is the '
                  'frontispiece; the caption to no. 553 misprints its artist as '
                  '“HARRY PENN” (the plate is signed Fenn; the body and the List '
                  'read Fenn, the List spelling him “Hary Fenn”), and the plates '
                  'of nos. 543 and 559 carry copyright lines beneath their '
                  'captions. One medium line stands beneath a title — “Original '
                  'Engraving.” under no. 288, carried in the record’s note — and '
                  'no dimensions are printed for any entry, so Medium and Size '
                  'stand empty throughout, medium words standing inside very many '
                  'titles as printed. The artists’ addresses stand only in the '
                  'book’s artist index and are not carried into these records; '
                  'the index is complete in this copy (Abbatt to Zogbaum — a '
                  'contrast with the 1908 copy’s two wanting leaves) and was '
                  'cross-checked against the body during the parse, the body '
                  'governing every disagreement; its 14 conflicts with the body '
                  'are all classified in the parse log, among them the printed '
                  'index’s own errors — it cites no. 48 under Chatterton (the '
                  'body’s 46; 48 is Grant Gordon’s) and no. 594 under Needham '
                  '(the body’s 591) — and its outright omissions of nos. 577 '
                  '(Hirst) and 579 (Bicknell). The book’s own errors stand as '
                  'printed: “Deirlbiss, Ida E.” at no. 47 (the book’s own '
                  'misprint; the index prints Devilbiss), “Moonlinght” in '
                  'no. 167’s title, “Gallilee” in no. 449’s, “ALPHONE” for '
                  'Alphonse in Mucha’s heading at no. 430, the comma-less '
                  'headings “TURNER ROSS” (no. 547; no. 131 carries the comma) '
                  'and “GRANT GORDON” (nos. 48 and 446), and the stray printed '
                  'closing quote in no. 353’s lender (“Scribner’s '
                  'Magazine.””). A handful of names stand exactly as the scan '
                  'reads them — “Kobbfi” for Kobbé (no. 133), “Wialter” for '
                  'Walter (Palmer, no. 163), “Ruzigka” for Ruzicka (no. 283; '
                  'the heading at no. 288 is clean), “Charjles” for Charles '
                  '(Mielatz), “Emjma” for Emma (Maass, no. 454), “Carllton” for '
                  'Carlton (Chapman) and “Wihittemore” for Whittemore (no. 130) '
                  'among them — and the scan’s dropping of the book’s accents '
                  'stands throughout (“Lave” for Lavé, no. 191; “Cafe” for '
                  'Café, no. 337). The Wm. T. Evans Prize was $300 this year, as '
                  'in 1895–1908; the book’s list of past winners runs 1888–1908, '
                  'its latest line the 1908 award, Ross Turner’s “The Dawn”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 598,
            'sections': {'South Gallery': 178, 'Central Gallery': 252,
                         'Vanderbilt Gallery': 168},
            # Plain catalogue numbers run 1–598 complete through the
            # three galleries in the order hung (South 1–178, Central
            # 179–430, Vanderbilt 431–598), with no gaps, no lettered
            # inserts, no joint entries and no number printed twice.
            # Three numbers were restored from the sequence and are
            # flagged in their records' notes: no. 110 (its printed
            # figures read by the scan's text layer as the word
            # "no."), no. 111 (its figures reach the layer as the
            # debris "HI.") and no. 519 (its figures fused to its
            # title as "5i9i"). 466 records carry a price in the
            # note, 54 name a lender (36 "Owned by", 17 "Courtesy
            # of", and one permission credit, no. 308) and 78 have
            # neither; no record prints a medium or a size; every
            # record has an artist and a title.
            'plain_range': (1, 598),
            'lettered': set(),
            'no_lender': 544,
            'no_medium': 598,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1910',
        'file': 'aws-1910.json',
        'title': 'Illustrated Catalogue of the Forty-third Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '28 April – 22 May 1910',
        'year': 1910,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1910',
        'source': 'Printed catalogue (New York, 1910); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-third annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The three galleries of 1908–1909 stand again — the South '
                  'Gallery (nos. 1–171), the Central Gallery (nos. 172–416) and the '
                  'Vanderbilt Gallery (nos. 417–556), the works numbered '
                  'continuously 1–556 — and 1909’s one-line entry form stands with '
                  'them: the galleries are headed in display capitals, there are no '
                  'printed sub-headings anywhere, and each entry stands on one line, '
                  'its element on the same line as its number and title — a price in '
                  'whole dollars, or “Owned by …”, or “Courtesy of …”, or nothing: '
                  '556 records in all, standing under 231 artists’ headings, 230 of '
                  'the records carrying the Society’s “A.W.C.S.” mark; 455 works are '
                  'priced for sale in the catalogue, the price standing in each '
                  'record’s note and the prices including frames, 26 name a lender '
                  '(20 “Owned by” and 6 “Courtesy of” — Collier’s Weekly at nos. 349, '
                  '379, 407 and 411, and the New York Herald at nos. 415 and 416) '
                  'and 75 have neither. The dearest work in the book is E. Irving '
                  'Couse’s “The Magic Flute” (no. 526), priced at $1,000.00 — the '
                  'only four-figure price in the book — followed by two works at '
                  '$800.00 (no. 47, Charles Austin Needham’s “The Golden Hour”, and '
                  'no. 554, Charles P. Gruppe’s “Banks of the Genesee”), no. 456 at '
                  '$700.00 and no. 29 at $600.00; the cheapest is J. Andre Smith’s '
                  '“Doorway, Frauenkirche” (no. 262) at $6.00, then four works at '
                  '$8.00 (nos. 174, 205, 211 and 265). The numbering runs 1–556 '
                  'complete — no gaps, no lettered inserts, no joint entries, no '
                  'number printed twice and no number needing restoration, the '
                  'cleanest numbering of the run so far; many numbers are printed '
                  'without their stop (nos. 19, 36, 42 and 81 among them), the '
                  'figures themselves reaching the record in every case. The '
                  'artists’ headings are printed in both orders — surname-first '
                  '(“ABBATT, EDITH”) and natural order (“EUGENE HIGGINS”, “J. F. '
                  'BURNS”) — each standing as printed; and three headings carry a '
                  'parenthetical “(Deceased)” — J. Wells Champney (no. 28), James '
                  'D. Smillie and Frederick Remington — the mark carried into the '
                  'artist string in the usual form and recorded in the notes of 44 '
                  'records in all. Twenty-three works are illustrated in the '
                  'catalogue, each flagged in its record’s note; the body prints '
                  'no illustration marks, so the illustrated works are named by '
                  'the book’s List of Illustrations — whose own heading the book '
                  'misprints “List ot Illustrations” — and all 23 plates are bound '
                  'in this copy, one or two to a leaf, no. 159 standing before the '
                  'title page; two captions differ from their body entries: '
                  'no. 438’s caption reads “MOONLIGHT ON THE FRENCH RIVIERA” where '
                  'the body reads “Moonlight on the Riviera” (the List agrees with '
                  'the caption), and no. 520’s caption hyphenates “OLD-FASHIONED '
                  'ROSES” where the body prints “Old Fashioned Roses”. No medium '
                  'line stands beneath any entry’s title — a contrast with 1909’s '
                  'single “Original Engraving.” — and no dimensions are printed '
                  'for any entry, so Medium and Size stand empty throughout, '
                  'medium words standing inside very many titles as printed. The '
                  'artists’ addresses stand only in the book’s artist index and '
                  'are not carried into these records; the index is complete in '
                  'this copy (Abbatt to Zeigler) and was cross-checked against '
                  'the body during the parse, the body governing every '
                  'disagreement; the only body number the index does not cite is '
                  'the illustrated no. 466, Mente’s “Stray Sheep”, and its own '
                  'spellings stand against the body’s page forms at a handful of '
                  'points, all classified in the parse log. The book’s own name '
                  'forms vary from page to page and every form stands — “PERCIVAL '
                  'DE DUCE” against “PERCIVAL De LUCE”, “CHARLES F. W. MIELANTZ” '
                  'against MIELATZ, “CLARA T. Mac CHESNEY” spaced against '
                  '“MacCHESNEY” closed, “ANNA MERRIMAN PECK” against “ANNE '
                  'MERRIMAN PECK”, “W. MERRITT T. POST” with its extra initial — '
                  'and its own title spellings stand: “In Brittainy” (no. 54), '
                  '“Jerzual” (nos. 72, 250 and 535), “Mahonay” (no. 288), '
                  '“Morroco” (no. 453), “Katwyjk” (no. 448), “Hereditary '
                  'Assasins” (no. 370), “Edinburg” (no. 499), “Navaho Shepherd” '
                  '(no. 532) and “Cuernavacca” throughout. A handful of readings '
                  'were settled on the printed page where the scan’s text layer '
                  'garbles them — fifteen headings, five prices and seventeen '
                  'titles among them, each recorded with its evidence in the '
                  'parse log; one price is settled by its figures’ only sensible '
                  'form and is flagged in its record’s note: no. 52 at $50.00, '
                  'the layer reading “$5C”, the printed glyph itself C-shaped in '
                  'the scan. The Wm. T. Evans Prize was $300 this year, as in '
                  '1895–1909; the book’s list of past winners runs 1888–1909, '
                  'its latest line the 1909 award, Edward Dufner’s “Reflections”.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 556,
            'sections': {'South Gallery': 171, 'Central Gallery': 245,
                         'Vanderbilt Gallery': 140},
            # Plain catalogue numbers run 1–556 complete through the
            # three galleries in the order hung (South 1–171, Central
            # 172–416, Vanderbilt 417–556), with no gaps, no lettered
            # inserts, no joint entries, no number printed twice and
            # no number needing restoration — the cleanest numbering
            # of the run so far. 455 records carry a price in the
            # note, 26 name a lender (20 "Owned by", 6 "Courtesy
            # of") and 75 have neither; no record prints a medium or
            # a size; every record has an artist and a title.
            'plain_range': (1, 556),
            'lettered': set(),
            'no_lender': 530,
            'no_medium': 556,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1911',
        'file': 'aws-1911.json',
        'title': 'Illustrated Catalogue of the Forty-fourth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '27 April – 21 May 1911',
        'year': 1911,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1911',
        'source': 'Printed catalogue (New York, 1911); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-fourth annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The book shrinks back to two galleries only — the South '
                  'Gallery (nos. 1–109) and the Second Gallery (nos. 110–192), '
                  '1910’s Central and Vanderbilt Galleries gone — the works numbered '
                  'continuously 1–192 across the two, the galleries headed in display '
                  'capitals with no sub-headings; the Second Gallery’s heading carries '
                  'one line of gallery furniture, “Fountain Figure by Eli Harvey.”, '
                  'which is no part of the catalogue and stands in no record. The '
                  'one-line entry form of 1909–1910 stands: each entry on one line, '
                  'its element a price in whole dollars, or “Lent by …” standing on '
                  'its own line beneath the title, or nothing: 191 records in all, '
                  'standing under 118 artists’ headings; 169 works are priced for '
                  'sale in the catalogue, the price standing in each record’s note '
                  'and the prices including frames, 9 name a lender — “Lent by” is '
                  'this book’s only lender form, there being no “Owned by”, '
                  '“Courtesy of” or permission lines anywhere in the body — and 13 '
                  'have neither. The dearest work in the book is Mary Cassatt’s '
                  '“A Cup of Tea—Pastel” (no. 102), priced at $1,600.00 — the prices '
                  'print without a thousands comma (“$1600”), the records’ notes '
                  'supplying it, as throughout the run — followed by Winslow Homer’s '
                  '“Negro on Boat, Nassau” (no. 170) at $1,000.00 and Childe Hassam’s '
                  '“The Thunderstorm” (no. 142) at $850.00; five works stand at '
                  '$750.00, all of them Homer’s (nos. 164, 167, 168, 172 and 175); '
                  'the cheapest is Jerome Myers’s “Rivington Street Gossip” (no. 22) '
                  'at $40.00, then three works at $50.00 (nos. 11, 21 and 34); the '
                  'priced works total $37,525. The numbering runs 1–192 with no '
                  'no. 14: on the printed page the sequence passes directly from '
                  'no. 13 (I. A. Josephi’s “The Pasture”) to no. 15 (Everett Shinn’s '
                  '“Ballet Girl”) — the book prints no entry 14, and no placeholder '
                  'stands in these records; the book’s own artist index cites '
                  'Arthur B. Davies at “14, 37, 39, 41”, the 14 being the index’s '
                  'own error. There are no lettered inserts, no number printed '
                  'twice, no joint entries and no unnumbered entries. One number '
                  'is restored from the sequence: no. 172 (Winslow Homer’s “Channel '
                  'Bass, Florida”, $750.00), whose figures the scan’s text layer '
                  'reduces to debris — a crop of the printed page shows “172.” — '
                  'and the record’s note carries the standard restoration flag; it '
                  'is the book’s only restored number. The artists’ headings are '
                  'printed in both orders — surname-first and natural order '
                  '(“Everett Shinn”, “Katharine N. Rhoades”) — each standing as '
                  'printed; one heading carries a parenthetical “(Deceased)”: '
                  'Winslow Homer, whose twelve works (nos. 164–175) run under the '
                  'one heading, the mark recorded in each of the twelve records’ '
                  'notes. Sixteen works are illustrated in the catalogue, each '
                  'flagged in its record’s note; the body prints no illustration '
                  'marks, so the illustrated works are named by the book’s List of '
                  'Illustrations (nos. 16, 25, 40, 42, 45, 49, 57, 66, 101, 102, '
                  '108, 116, 119, 149, 150 and 190), and all sixteen plates are '
                  'bound in this copy, no. 25 (Gifford Beal’s “The Freight Yards”) '
                  'standing as frontispiece before the title page; three captions '
                  'diverge from their body entries, the body governing in each '
                  'case: no. 45’s caption reads “WEDNESDAY’S MARKET” against the '
                  'body’s “Wednesday Market, Bruges”, no. 119’s “BETSEY” against '
                  '“Betsy”, and no. 149’s caption and the List both read “THE '
                  'CALICO MART” against the body’s “Calico Market”. No medium line '
                  'stands beneath any entry’s title and no dimensions are printed '
                  'for any entry, so Medium and Size stand empty throughout, '
                  'medium words standing inside very many titles as printed. The '
                  'artists’ addresses stand only in the book’s artist index and '
                  'are not carried into these records; the index is complete in '
                  'this copy (Abbatt to Young) and was cross-checked against the '
                  'body during the parse, the body governing every disagreement; '
                  'its only other apparent conflict is the scan’s garble at no. 137, '
                  'the print reading “Platt, Alethea Hill”. The book’s own name '
                  'forms stand: the headings’ “Macrae” against the index’s '
                  '“MacRae”, the particle forms “Alexander T. van Laer” and '
                  '“E. van R. M. Heard” against the index’s capitalised “Van”, '
                  '“HAROLD CAMP” at no. 121 against “HAROLD M. CAMP” at no. 97 '
                  '(the index files both under the one entry), the mixed-case '
                  '“Percival DeLuce” the book itself prints, and “Edward McDowell” '
                  'with its lowercase c; and one price stands exactly as the book '
                  'prints it — no. 68’s “A Palace—175”, its price printed without '
                  'the dollar sign, flagged in the record’s note. A handful of '
                  'readings were settled on the printed page where the scan’s text '
                  'layer garbles them — nine headings and three prices among them, '
                  'and the titles’ printed accents restored (“Street Café, '
                  'Algeria” at no. 30, “The Cañon Road” at no. 117) — each recorded '
                  'with its evidence in the parse log. The Wm. T. Evans Prize was '
                  '$300 this year, on the standing terms; the book’s list of past '
                  'winners ends with the 1910 award, R. M. Shurtleff’s “June” — '
                  'the 1911 award is not recorded in this book.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 191,
            'sections': {'South Gallery': 108, 'Second Gallery': 83},
            # Plain catalogue numbers run 1–192 through the two
            # galleries in the order hung (South 1–109, Second
            # 110–192), the book itself printing no no. 14 — the
            # sequence passes from 13 to 15 on the page — with no
            # lettered inserts, no joint entries, no number printed
            # twice and one number restored (172). 169 records carry
            # a price in the note, 9 name a lender (all "Lent by")
            # and 13 have neither; no record prints a medium or a
            # size; every record has an artist and a title.
            'plain_range': (1, 192),
            'absent_numbers': [14],
            'lettered': set(),
            'no_lender': 182,
            'no_medium': 191,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1912',
        'file': 'aws-1912.json',
        'title': 'Illustrated Catalogue of the Forty-fifth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the American Fine Arts Galleries, 215 West 57th Street, New York',
        'venue': 'American Fine Arts Galleries, 215 West 57th Street, New York',
        'dates': '25 April – 12 May 1912',
        'year': 1912,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1912',
        'source': 'Printed catalogue (New York, 1912); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-fifth annual exhibition of the American Water Color Society, '
                  'held at the American Fine Arts Galleries, 215 West 57th Street, '
                  'New York. The exhibition grows again after 1911’s small hang: two '
                  'galleries — the First Gallery (nos. 1–130) and the Second Gallery '
                  '(nos. 131–272) — the works numbered continuously 1–272 across the '
                  'two, the galleries headed in display capitals with no sub-headings '
                  'and no gallery-furniture line under either heading (contrast '
                  '1911’s “Fountain Figure”). The one-line entry form of 1909–1911 '
                  'stands: each entry on one line, its element a price in whole '
                  'dollars, or “Owned by …” standing on its own line beneath the '
                  'title, or nothing: 272 records in all, standing under 163 '
                  'artists’ headings; 244 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note and the '
                  'prices including frames, 9 name a lender — “Owned by” is this '
                  'book’s only lender form, there being no “Lent by”, “Courtesy of” '
                  'or permission lines anywhere in the body — and 19 have neither. '
                  'The dearest works are two at $1,000.00: F. Hopkinson Smith’s “The '
                  'Rug Market” (no. 59) and Leonard Ochtman’s “The Brook in the '
                  'Winter” (no. 166) — this book prints the thousands comma '
                  '(“$1,000”), where 1911’s did not — followed by Bernard Johannes '
                  'Blommers’s “November at Scheveningen” (no. 7) at $800.00 and '
                  'William J. Whittemore’s “Bacchante” (no. 47) at $750.00; the '
                  'cheapest price is $50.00, carried by 46 records, nothing in the '
                  'book priced below it; the priced works total $37,890. The '
                  'numbering runs 1–272 complete — the cleanest of the 1906–1912 '
                  'volumes: no number is restored, none is printed twice, there are '
                  'no lettered inserts, no joint entries and no absent numbers; '
                  'two numbers carry the book’s own trailing punctuation — no. 141 '
                  'prints “141,” and no. 147 “147:” — read as their numbers without '
                  'remark. The artists’ headings are printed in natural order '
                  'throughout, members carrying the printed suffix “A.W.C.S.” '
                  'where it stands; two headings on one page carry a parenthetical '
                  '“(DECEASED)” in capitals: Howard Pyle, whose two works (nos. 203 '
                  'and 204) are both lent by Mrs. Pyle, the mark recorded in each '
                  'record’s note. Eight works are illustrated in the catalogue, '
                  'each flagged in its record’s note; the body prints no '
                  'illustration marks, so the illustrated works are named by the '
                  'book’s List of Illustrations (nos. 3, 7, 11, 65, 77, 100, 142 '
                  'and 196), and all eight plates are bound in this copy, no. 100 '
                  'standing as frontispiece; no caption differs from its body '
                  'entry. No medium line stands beneath any entry’s title and no '
                  'dimensions are printed for any entry, so Medium and Size stand '
                  'empty throughout, medium words standing inside very many titles '
                  'as printed. The artists’ addresses stand only in the book’s '
                  'artist index and are not carried into these records; the index '
                  'is complete in this copy (Abbatt to Wigand) and was '
                  'cross-checked against the body during the parse, the body '
                  'governing every disagreement — the index cites Forsyth at '
                  '“151, 249”, its 249 being its own figure error (the body’s '
                  'no. 249 is Beauley’s, and no. 240, W. Forsyth’s “A Winter '
                  'Brook”, goes uncited), and it prints Howard Pyle’s two numbers '
                  'under the entry for “Pyle, Mrs. Howard”, the lender. The '
                  'book’s own name forms stand: the secretary’s name printed '
                  '“MERRITT” at no. 23’s heading and “MERRIT” at no. 39’s; Robert '
                  'David Gauley’s surname “GAULEY” at no. 165 and “GAULY” at nos. '
                  '208 and 216; Clara T. MacChesney’s surname spaced, “MAC '
                  'CHESNEY”, at no. 176 and closed, “MacCHESNEY”, at no. 250; '
                  'Norwood Mac Gilvary’s surname spaced at no. 105; no. 150’s '
                  'heading carrying a compositor’s stray stop, “FIDELIA. '
                  'BRIDGES”; no. 199’s title standing as printed, “The Cleremont”, '
                  'no. 262’s as “Behind the Grootakirk”, and no. 188’s title '
                  'ending “XIII.,” as printed. A handful of readings were settled '
                  'on the printed page where the scan’s text layer garbles them — '
                  'no. 189’s price, $150.00, the page’s folio clustering into the '
                  'price segment in the layer; no. 41’s title, “Breezy Morning, '
                  'Paris”, a reader’s ink stroke over “Paris” reducing the word '
                  'to debris in the layer; and eight headings among them, '
                  'including the Glintenkamp heading at no. 97, garbled entire '
                  'behind an ink rule struck through it in this copy — each '
                  'recorded with its evidence in the parse log. The Wm. T. Evans '
                  'Prize was $300 this year, on the standing terms; the book’s '
                  'list of past winners ends with the 1911 award, Charles H. '
                  'Woodbury’s “Evening” — the 1912 award is not recorded in this '
                  'book.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 272,
            'sections': {'First Gallery': 130, 'Second Gallery': 142},
            # Plain catalogue numbers run 1–272 complete through the
            # two galleries in the order hung (First 1–130, Second
            # 131–272) — the cleanest of the 1906–1912 volumes: no
            # number restored, none printed twice, no lettered
            # inserts, no joint entries and no absent numbers. 244
            # records carry a price in the note, 9 name a lender (all
            # "Owned by") and 19 have neither; no record prints a
            # medium or a size; every record has an artist and a
            # title.
            'plain_range': (1, 272),
            'lettered': set(),
            'no_lender': 263,
            'no_medium': 272,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1913',
        'file': 'aws-1913.json',
        'title': 'Catalogue of the Forty-sixth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of M. Knoedler & Co., 556 and 558 Fifth Avenue, New York',
        'venue': 'Galleries of M. Knoedler & Co., 556 and 558 Fifth Avenue, New York',
        'dates': '3 – 15 March 1913',
        'year': 1913,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1913',
        'source': 'Printed catalogue (New York, 1913); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-sixth annual exhibition of the American Water Color Society, '
                  'held at the Galleries of M. Knoedler & Co., Five Fifty-six and '
                  'Five Fifty-eight Fifth Avenue, New York — the exhibition leaves '
                  'the American Fine Arts Galleries, where it had hung since 1906, '
                  'for Knoedler’s, and shrinks sharply: 143 catalogue numbers in a '
                  'single alphabetical run by artist, as in 1902 and unlike every '
                  'volume since, against 272 in two galleries in 1912. The works '
                  'stand under 108 artists’ headings, printed surname-first '
                  'throughout, members carrying the suffix “A.W.C.S.” where it '
                  'stands — 56 of the 108 headings carry the mark; beneath each '
                  'heading stands the artist’s address in small type, which is '
                  'not carried into these records, and the book prints no artist '
                  'index, the addresses standing in the body instead. There is '
                  'no price, lender or any other element in this book: no price '
                  'column, no “Owned by”, “Lent by” or “Courtesy of” lines and '
                  'no sale marks — all 143 records stand with neither price nor '
                  'lender, and there is no notices page, there being no prices '
                  'to notice. No dimensions and no medium lines are printed for '
                  'any entry, so Medium and Size stand empty throughout. The '
                  'book is not styled “Illustrated”: it prints no plates and no '
                  'List of Illustrations, and no work is illustrated. The '
                  'numbering runs 1–143 complete — no number is printed twice '
                  'for two works, there are no lettered inserts, no joint '
                  'entries, no unnumbered entries and no absent numbers — but '
                  'five numbers are restored from the sequence, each flagged in '
                  'its record’s note: three the scan’s text layer garbles while '
                  'the printed page is legible (nos. 11, 110 and 111), and two '
                  'the book itself misprints, the compositor dropping a figure '
                  '— no. 87 (Perrie, “An Old Vessel”) printed “7.” and no. 137 '
                  '(Ward, “Horses Ploughing”) printed “17.”, each verified on '
                  'the printed page (the 1906 treatment of no. 584, printed '
                  '“548”). One listing-order curiosity stands: the entries run '
                  'alphabetically by artist, but Post (no. 93) is listed before '
                  'Potthast (nos. 91, 92) — “Post” precedes “Potthast” in the '
                  'alphabet; the numbers simply follow the hang, and the '
                  'records are keyed and ordered by number as usual. A handful '
                  'of title readings were settled on the printed page where '
                  'the scan’s text layer garbles them — no. 66’s “The Sketch '
                  'Book”, no. 74’s “1860” (the title is the printed year), no. '
                  '119’s “Cloudy Sky” and no. 124’s “Dolomites, Cortina” — and '
                  'the book’s own misspellings stand as printed: no. 120’s '
                  '“Glouscester Harbor”, no. 129’s “Edinboro” and no. 133’s '
                  '“Assuan”. The book’s spaced surname forms stand as printed: '
                  '“Mac Chesney, Clara T.” (as in 1910 and 1912) and “Mc '
                  'Cormick, Katherine H.” Every catalogue page was read '
                  'against the page images during the parse. The Wm. T. Evans '
                  'Prize was $300 this year, on the standing terms; the '
                  'book’s printed list of past winners (1888–1912) ends with '
                  'the 1912 award, Childe Hassam’s “The Minuet” — the 1913 '
                  'award is not recorded in this book. This is the prize’s '
                  'last year: the Evans Prize was discontinued after 1913.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 143,
            'sections': {'Catalogue': 143},
            # Plain catalogue numbers run 1–143 complete in the single
            # alphabetical sequence: no number printed twice, no
            # lettered inserts, no joint entries, no unnumbered entries
            # and no absent numbers (five numbers are restored from the
            # sequence — nos. 11, 110 and 111 garbled in the scan's text
            # layer, nos. 87 and 137 misprinted by the book itself —
            # and stand in the records under their restored numbers).
            # The book prints no price, lender or any other element:
            # all 143 records stand with no lender and no medium; every
            # record has an artist and a title.
            'plain_range': (1, 143),
            'lettered': set(),
            'no_lender': 143,
            'no_medium': 143,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1914',
        'file': 'aws-1914.json',
        'title': 'Catalogue of the Forty-seventh Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of M. Knoedler & Co., 556 and 558 Fifth Avenue, New York',
        'venue': 'Galleries of M. Knoedler & Co., 556 and 558 Fifth Avenue, New York',
        'dates': '16 – 28 February 1914',
        'year': 1914,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1914',
        'source': 'Printed catalogue (New York, 1914); Frick Library scan supplied by John Finnegan (Google Drive)',
        'notes': ('The forty-seventh annual exhibition of the American Water Color Society, '
                  'held at the Galleries of M. Knoedler & Co., Five Fifty-six and '
                  'Five Fifty-eight Fifth Avenue, New York, where the exhibition '
                  'had moved in 1913: 113 catalogue numbers in a single '
                  'alphabetical run by artist, as in 1902 and 1913, the works '
                  'standing under 89 artists’ headings, printed surname-first '
                  'throughout, members carrying the suffix “A.W.C.S.” where it '
                  'stands — 39 of the 89 headings carry the mark; beneath each '
                  'heading stands the artist’s address in small type, which is '
                  'not carried into these records, and the book prints no artist '
                  'index, the addresses standing in the body instead. There are '
                  'no prices in this book: no price column, no price lines and '
                  'no sale marks, and there is no notices page — but the element '
                  'stands in exactly one form, an “Owned by …” line beneath the '
                  'title, on seven records: no. 35, whose owner is printed in '
                  'quotation marks — Owned by “The Delineator.”, the lender '
                  'field carrying the name and the record’s note quoting the '
                  'printed form — no. 62 (Mrs. Charles H. Parker), no. 63 (Mrs. '
                  'Herbert Scoville), no. 68 (Mrs. William R. Mercer), no. 93 '
                  '(Mrs. J. D. Heard) and nos. 110 and 111 (Mrs. W. M. Ivins, '
                  'Jr.); there are no “Lent by”, “Courtesy of” or permission '
                  'lines, and the remaining 106 records stand with neither price '
                  'nor lender. No dimensions and no medium lines are printed '
                  'for any entry, so Medium and Size stand empty throughout. '
                  'The book IS illustrated (contrast 1913): its List of '
                  'Illustrations names eight works by catalogue number — nos. '
                  '4, 20, 21, 65, 71, 88, 91 and 94 — and all eight plates are '
                  'bound in, one to a leaf, every List entry agreeing with its '
                  'plate caption and with the body entry of that number; the '
                  'eight carry the note “Illustrated in the catalogue.”, the '
                  'body itself printing no illustration marks. The numbering '
                  'runs 1–112 with one lettered insert standing in the book as '
                  'printed: G. Glenn Newell’s “A Bleak Day in the Pasture” is '
                  'numbered “55A.” between Needham’s 55 and Hugh Newell’s 56, '
                  'and its record’s number stands as the string “55A”. One '
                  'number is restored from the sequence and flagged in its '
                  'record’s note: no. 111 (Wyman, “The Market Place”), whose '
                  'printed figures the scan’s text layer reads as the debris '
                  '“HI” — the print reads “111.” cleanly, the same debris form '
                  'as 1913’s no. 111. No number is printed twice for two '
                  'works, there are no joint entries, no unnumbered entries '
                  'and no absent numbers; exactly one title wraps to a second '
                  'line (no. 74, “The Sea from the Shore, Magnolia, Mass.”). '
                  'The book’s spaced surname forms stand as printed: “Mac '
                  'Chesney, Clara T.”, “Mac Gilvary, Norwood”, “Mc Comas, '
                  'Francis” and “Mc Millan, Mary Lane”; “Menzler (Peyton), '
                  'Bertha S.” keeps the book’s parenthetical form, and “De '
                  'Thulstrup, T.” follows the 1902 precedent. Every catalogue '
                  'page was read against the page images during the parse. '
                  'This is the hinge year for the Society’s prizes. The prize '
                  'page announces the new Hudnut Prize: the Society is '
                  'indebted to Mr. Alexander M. Hudnut for a prize of $200, to '
                  'be awarded for the most meritorious water colour in the '
                  'exhibition, painted in this country by an American artist, '
                  'without limit as to age, the recipient to be thereafter '
                  'ineligible — no winner is named in this book (the 1915 '
                  'catalogue records the 1914 award: Edward H. Potthast’s “A '
                  'Holiday”, no. 71 here, and illustrated). Below the '
                  'announcement the book prints the list of recipients of the '
                  'Wm. T. Evans Prize, 1888–1913, ending with the 1913 award, '
                  'Arthur Schneider’s “A Morning Walk”, and then states: '
                  '“This Prize has been discontinued.” The Evans Prize of '
                  '$300 thus ends with this book, and no Evans amount is '
                  'offered for this exhibition.'),
        # The parse stores the plain catalogue numbers as integers
        # (the lettered insert as a string); the built file carries
        # them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 113,
            'sections': {'Catalogue': 113},
            # Plain catalogue numbers run 1–112 complete in the single
            # alphabetical sequence, with one lettered insert standing
            # as printed (55A, between 55 and 56): no number printed
            # twice, no joint entries, no unnumbered entries and no
            # absent numbers (one number is restored from the sequence
            # — no. 111, read as debris in the scan's text layer — and
            # stands in the records under its restored number). The
            # book prints no prices at all; the element stands only as
            # "Owned by" on 7 records, so 106 records have no lender;
            # no record prints a medium; every record has an artist
            # and a title.
            'plain_range': (1, 112),
            'lettered': {'55A'},
            'no_lender': 106,
            'no_medium': 113,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1915',
        'file': 'aws-1915.json',
        'title': 'Catalogue of the Forty-eighth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '4 – 25 February 1915',
        'year': 1915,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1915',
        'source': 'Printed catalogue (New York, 1915); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-eighth annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition leaves '
                  'Knoedler’s after two years, and grows again: 267 catalogue '
                  'numbers in a single alphabetical run by artist, as in 1902, '
                  '1913 and 1914, the works standing under 150 artists’ '
                  'headings, printed surname-first throughout, members carrying '
                  'the suffix “A.W.C.S.” where it stands — 35 of the 150 '
                  'headings carry the mark; beneath each heading stands the '
                  'artist’s address in small type, which is not carried into '
                  'these records, and the book prints no artist index, the '
                  'addresses standing in the body instead. There are no prices '
                  'in this book: no price column, no price lines and no sale '
                  'marks, and there is no notices page — but the element stands '
                  'in exactly one form, an “Owned by …” line beneath the title, '
                  'on five records: no. 4 (Samuel T. Shaw, Esq.), nos. 84 and '
                  '89 (Mrs. W. F. Powers), no. 222 (W. D. Edwards, Esq.) and '
                  'no. 261 (Mrs. Pascal Moore); there are no “Lent by”, '
                  '“Courtesy of” or permission lines, and the remaining 262 '
                  'records stand with neither price nor lender. No dimensions '
                  'and no medium lines are printed for any entry, so Medium '
                  'and Size stand empty throughout. The book IS illustrated '
                  '(as in 1914, and contrast 1913): its List of Illustrations '
                  'names ten works by title and artist, without numbers — no. '
                  '13 (Belcher, “Winifred Hunt”), no. 67 (Couse, “A Papoose”), '
                  'no. 75 (Dufner, “Springtime, Taormina”), no. 160 (Nicholls, '
                  '“A Dancer”), no. 172 (Platt, “An Old Man’s Workshop”), no. '
                  '179 (Potthast, “An Impression”), no. 190 (Ritschel, '
                  '“Morning Breeze, California”), no. 192 (Robinson, “Rocky '
                  'Pasture”), no. 197 (Schilling, “Autumn Ploughing”) and no. '
                  '267 (Yates, “Landscape in Blue and Gold”) — and all ten '
                  'plates are bound in, one to a leaf, each matched to its '
                  'body entry on artist and title, every match unique in the '
                  'body; the ten carry the note “Illustrated in the '
                  'catalogue.” One caption defect stands: no. 267’s plate '
                  'caption prints “LANDSCAPE IN BLUE AND COLD” — the book’s '
                  'misprint; the body and the List both read “Gold”, and the '
                  'record stands under the body reading. The numbering runs '
                  '1–267 complete and clean — no number is printed twice for '
                  'two works, there are no lettered inserts, no joint '
                  'entries, no unnumbered entries, no absent numbers and no '
                  'numbers restored from the sequence: the cleanest numbering '
                  'since 1912. Two headings stand out of alphabetical order '
                  'in print, and stand as printed: Aylward (no. 4) follows '
                  'Arms (no. 3), and De Haas (no. 95) stands between Gruppe '
                  '(no. 94) and Hartman (no. 96). The book’s own '
                  'inconsistencies stand as printed: the body heading '
                  '“Nichols, Rhoda Holmes” (single L) against the List’s and '
                  'the plate caption’s “Nicholls”; the List’s “Alethea Hill '
                  'Platt” against the members list’s “Piatt”, the body '
                  'reading “Platt”; no. 25’s title “Magnali, Tuscany” (the '
                  'place is Magliano; the book prints Magnali); no. 206’s '
                  '“Poincettas”; no. 210’s “Church of The Vera Crux”; the '
                  'headings printed without their comma, “Penman Edith” and '
                  '“O’ Leary Angela”; and “Scott Mrs. E. M.” without a comma '
                  'after the surname. A handful of readings were settled on '
                  'the printed page where the scan’s text layer garbles '
                  'them — a perforated Frick stamp falls across two body '
                  'pages, garbling the Stoner and Straus headings, the Van '
                  'Laer heading and no. 231’s title “Nymph” among them. '
                  'Every catalogue page was read against the page images '
                  'during the parse. The prize page carries the Society’s '
                  'change of prizes. It prints the list of recipients of '
                  'the Wm. T. Evans Prize, 1888–1913, ending with the 1913 '
                  'award, Arthur Schneider’s “A Morning Walk”, and then '
                  'states: “This Prize has been discontinued.” In its place '
                  'the page announces the Hudnut Prize: “In 1914 Alexander '
                  'M. Hudnut gave to the American Water Color Society a '
                  'prize of $200, to be known as the Hudnut Prize, ‘for the '
                  'most meritorious Water Color in the exhibition and to be '
                  'free from any restriction whatever’”, and the page '
                  'records the prize’s first award — in 1914, to Edward H. '
                  'Potthast, for his picture entitled “A Holiday”. No Evans '
                  'Prize amount is offered for this exhibition.'),
        # The parse stores the catalogue numbers as integers; the
        # built file carries them as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 267,
            'sections': {'Catalogue': 267},
            # Plain catalogue numbers run 1–267 complete and clean in
            # the single alphabetical sequence: no number printed
            # twice, no lettered inserts, no joint entries, no
            # unnumbered entries, no absent numbers and no numbers
            # restored from the sequence. The book prints no prices at
            # all; the element stands only as "Owned by" on 5 records,
            # so 262 records have no lender; no record prints a
            # medium; every record has an artist and a title.
            'plain_range': (1, 267),
            'lettered': set(),
            'no_lender': 262,
            'no_medium': 267,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1916',
        'file': 'aws-1916.json',
        'title': 'Catalogue of the Forty-ninth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '3 – 27 February 1916',
        'year': 1916,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1916',
        'source': 'Printed catalogue (New York, 1916); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The forty-ninth annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, and grows again: 358 catalogue '
                  'numbers in a single alphabetical run by artist, as in 1902, '
                  '1913, 1914 and 1915, the works standing under 175 artists’ '
                  'headings. The headings change their order this year: they '
                  'are printed in natural order — given names first — in '
                  'capitals, with the membership suffix set in lowercase, '
                  '“A. w. c. s.,”, after the name, where it stands — 52 of the '
                  '175 headings carry the mark; at the right of each heading '
                  'line, or beneath it at the right when the heading fills '
                  'the line, stands the artist’s address, which is not '
                  'carried into these records, and the book prints no artist '
                  'index, the addresses standing in the body instead. Prices '
                  'are back (absent in 1913 and 1915): each entry is one line '
                  '— number, title, and the price in whole dollars at the end '
                  'of the line — and 328 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note; the '
                  'lender element stands in exactly one form, an “Owned by '
                  '…” line beneath the title, on four records: no. 19 (James '
                  'Porter, Esq.), no. 70 (Miss Mary Shepard), no. 174 (Norman '
                  'Davis, Esq.) and no. 232 (Mrs. Harry Payne Whitney); there '
                  'are no “Lent by”, “Courtesy of” or permission lines, and '
                  'the remaining 26 records stand with neither price nor '
                  'lender. The dearest work is F. Hopkinson Smith’s “Rio '
                  'Fontega, Venice” (no. 297) at $1,000.00 — the book’s only '
                  'four-figure price, the book printing the thousands comma '
                  '(“$1,000”) — followed by Childe Hassam’s “The Poppies” '
                  '(no. 138) at $650.00 and seven works at $600.00; the '
                  'cheapest price is $20.00, carried by two records, both J. '
                  'H. Litchfield’s (nos. 185 and 187), and the prices run '
                  'from $20 to $1,000 with a median of $100. One price is '
                  'printed without its dollar sign — no. 131’s “Elefantasy. '
                  '150” — and carries the bare-price note, in the form used '
                  'for 1911; no. 22’s price follows a comma in its line, the '
                  'comma being the price’s separator and not part of the '
                  'title, and nos. 235 and 236 set the price after an '
                  'em-dash. No dimensions and no medium lines are printed '
                  'for any entry, so Medium and Size stand empty throughout. '
                  'The book IS illustrated (as in 1914 and 1915): its List '
                  'of Illustrations names eleven works by title and artist '
                  'only, without numbers — no. 38 (Browne, “Return from the '
                  'Weirs”), no. 73 (Crisp, “Along the River”), no. 76 '
                  '(Curran, “Elizabeth”), no. 86 (Dufner, “Evening in '
                  'June”), no. 88 (Eaton, “The Quai Verte, Bruges”), no. '
                  '249 (Peterson, “A Busy Street”), no. 257 (Potthast, “A '
                  'Day at the Seashore”), no. 269 (Robinson, “In the North '
                  'Woods”), no. 271 (Ryder, “Little White House in '
                  'Winter”), no. 326 (Volkert, “Summer Morning”) and no. '
                  '328 (Warner, “West Street, New York”) — ten plates are '
                  'bound in, one to a leaf, and the eleventh, no. 73, '
                  'stands on the catalogue’s own printed cover, which '
                  'survives inside this copy’s binding; each was matched to '
                  'its body entry on artist and title, every match unique '
                  'in the body, and the eleven carry the note “Illustrated '
                  'in the catalogue.” No. 88’s plate caption styles its '
                  'artist “C. Warren Eaton, A.W.C.S.” where the body '
                  'heading prints no suffix; the record follows the body '
                  'heading. The numbering runs 1–352 with six lettered '
                  'inserts standing as printed — 90a (Edwards, after '
                  'Eaton’s nos. 88–90), 116a (Granville-Smith), 178a (Lamb) '
                  'and 233a, 233b and 233c (Newell’s, after Nelson’s no. '
                  '233) — 358 records in all: no number is printed twice, '
                  'there are no joint entries, and no number in 1–352 is '
                  'absent. Six numbers are restored, each flagged in its '
                  'record’s note: four — nos. 86, 88, 89 and 98 — stand '
                  'plainly in the printed page but are dropped entire by '
                  'the scan’s text layer; no. 158 is read by the layer as '
                  '“15b”, its printed 8 imperfectly inked; and no. 177 is '
                  'printed without a number at all — the entry stands '
                  'numberless between nos. 176 and 178 — and is restored in '
                  'the form used for 1908’s unnumbered no. 11. One '
                  'collective heading stands in the body: the unnumbered, '
                  'indented line “Sketches at Panama-Pacific Exposition” '
                  'stands over Donna Schuster’s four sketches (nos. '
                  '282–285); it is not a record, and the four records carry '
                  'the group note. One heading carries a parenthetical '
                  '“(Deceased)”: F. Hopkinson Smith, whose five works (nos. '
                  '297–301) each record the mark in their note. The book’s '
                  'own spellings stand as printed: no. 210’s “The Poylar.”, '
                  'no. 274’s “Fountain, Bobuli Gardens, Florence.”, nos. '
                  '300 and 301’s “Dortrecht”, no. 121’s “A Street in Acama, '
                  'N. M.”, no. 131’s title “Elefantasy” — the print’s own '
                  'fanciful word — and no. 7’s “Campo Marguita, Venice”; '
                  'and the headings “Rokno Arai”, “Evelin Bodfish”, “C. F. '
                  'Solian Schmitt”, “Euphanie Mallison” and “Mary '
                  'Nicholena MacCord” stand exactly as the book prints '
                  'them, each checked on its page render. Nine heading '
                  'readings were settled on the printed page where the '
                  'scan’s text layer garbles them — among them Edwards’s '
                  '“WHARTON” (the layer inserts an “i”), Josephi’s first '
                  'initial “I.” (the layer reads “R.”) and Whittemore’s '
                  '“WILLIAM” (the layer reads “WILUAM”). Every body page '
                  'was verified entry by entry against its page image '
                  'during the parse. The prize page stands as in 1915. It '
                  'prints the list of recipients of the Wm. T. Evans Prize, '
                  '1888–1913, ending with the 1913 award, Arthur '
                  'Schneider’s “A Morning Walk”, and then states: “This '
                  'Prize has been discontinued.” The Hudnut Prize stands '
                  'at $200, the gift of Alexander M. Hudnut, “for the most '
                  'meritorious Water Color in the exhibition and to be free '
                  'from any restriction whatever”, and the page now '
                  'records two awards — in 1914, to Edward H. Potthast, for '
                  '“A Holiday”, and in 1915, to Hilda Belcher, for '
                  '“Winifred Hunt”. No Evans Prize amount is offered for '
                  'this exhibition, and the 1916 Hudnut award is not '
                  'recorded in this book.'),
        # The parse stores the plain catalogue numbers as integers
        # (the lettered inserts as strings); the built file carries
        # them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 358,
            'sections': {'Catalogue': 358},
            # Plain catalogue numbers run 1–352 complete in the single
            # alphabetical sequence, with six lettered inserts standing
            # as printed (90a, 116a, 178a, 233a, 233b, 233c): no number
            # printed twice, no joint entries and no number in 1–352
            # absent (six numbers are restored — nos. 86, 88, 89 and
            # 98 dropped entire by the scan's text layer, no. 158 read
            # as letter debris, and no. 177 printed without a number —
            # and stand in the records under their restored numbers).
            # Prices are back: 328 records carry a price in the note,
            # 4 name a lender (all "Owned by") and 26 have neither, so
            # 354 records have no lender; no record prints a medium;
            # every record has an artist and a title.
            'plain_range': (1, 352),
            'lettered': {'90a', '116a', '178a', '233a', '233b', '233c'},
            'no_lender': 354,
            'no_medium': 358,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1917',
        'file': 'aws-1917.json',
        'title': 'Catalogue of the Fiftieth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '1 – 24 February 1917',
        'year': 1917,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1917',
        'source': 'Printed catalogue (New York, 1917); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The fiftieth annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, and the Society reaches its fiftieth '
                  'annual: 330 records in a single alphabetical run by artist, '
                  'as in 1902, 1913, 1915 and 1916, the works standing under 189 '
                  'artists’ headings. The headings return to surname-first order '
                  'this year (contrast 1916’s natural order), in capitals, '
                  'members carrying the printed suffix “A. W. C. S.” set in '
                  'spaced capitals where it stands — 67 of the 189 headings '
                  'carry the mark; beneath each heading, or at its right, stands '
                  'the artist’s address, which is not carried into these '
                  'records, and the book prints no artist index, the addresses '
                  'standing in the body instead. Each entry stands on one line '
                  '— number, title and element together. Prices stand at the '
                  'end of the entry line in whole dollars, and 293 works are '
                  'priced for sale in the catalogue, the price standing in each '
                  'record’s note; the dearest work is Horatio Walker’s “Swine '
                  'and Swineherd” (no. 314) at $2,000.00 — three four-figure '
                  'prices in all: no. 314 at $2,000.00, no. 124 (Hassam, “Old '
                  'Fifth Avenue, 1898”) at $1,200.00 and no. 323 (Woodbury, '
                  '“Porpoises”) at $1,000.00; eleven records stand at $600.00 or '
                  'more, the cheapest price is $20.00, and the prices run from '
                  '$20 to $2,000 with a median of $125. The lender stands in two '
                  'forms: an “Owned by …” line beneath the title, on two '
                  'records (nos. 127 and 128), and a parenthetical “(owned by '
                  '…)” or “(Owned by …)” credit appended to the title line or '
                  'standing on its own line beneath it, on twelve records (nos. '
                  '14, 25, 100, 103, 167, 180, 190, 191, 230, 277, 292 and 295) '
                  '— the named party stands in the lender field and the printed '
                  'form is quoted in the record’s note; there are no “Lent by”, '
                  '“Courtesy of” or “Made for” lines and no sale marks, and 23 '
                  'records stand with no element at all. No dimensions are '
                  'printed for any entry, so Size stands empty throughout; a '
                  'medium line, “(Miniature.)”, is printed beneath the title on '
                  'two records (nos. 305 and 306) and stands in the note, '
                  '“(Miniature)” inside a title line standing in the title as '
                  'printed (nos. 21, 100, 167, 178 and 185), and the dimensions '
                  'stand in the titles of Ortlip’s three entries (nos. 215–217) '
                  'as printed, so Medium stands empty throughout. The book IS '
                  'illustrated (as in 1914, 1915 and 1916): its List of '
                  'Illustrations names nine works by title and artist only, '
                  'without numbers, and nine plates are bound in — no. 127 '
                  '(Henry, “Lord Howe’s Headquarters, Germantown, 1777”) as the '
                  'frontispiece, its caption printed vertically at the side of '
                  'the leaf, and eight interleaved, one to a leaf: no. 11 '
                  '(Aylward, “The Irish Emigrants”), no. 68 (Cooper, “Pan '
                  'Fountain—San Diego Exposition”), no. 90 (Dunsmore, “A '
                  'Perplexing Point”), no. 96 (Edwards, “Fair Amalfi”), no. 142 '
                  '(Howell, “The Public Library, Washington”), no. 260 '
                  '(Ritschel, “Waiting”) and no. 300 (Snell, “Twilight at '
                  'Newcastle”) — eight plates matched to body entries on artist '
                  'and title, every match unique in the body, and the eight '
                  'carry the note “Illustrated in the catalogue.” The ninth '
                  'plate has NO entry in the body: Albert Sterner’s “Nude in '
                  'Studio” stands in the List and among the plates, but the '
                  'body passes from Steele (no. 307) to Stoner (no. 308) with '
                  'the numbering unbroken, and Sterner stands only in the List '
                  'and in the members list. The List gives Aylward’s title in '
                  'the singular, “The Irish Emigrant”, where the body and the '
                  'caption read the plural; it spells Ritschel “Ritschell” '
                  'where the body heading and the caption read “Ritschel”; and '
                  'Henry’s caption gives his title in the fuller form “Lord '
                  'Howe’s Headquarters, Germantown, October 4, 1777” against '
                  'the body’s “…, 1777”. The numbering runs 1–327 with two '
                  'lettered inserts standing as printed — 24a (Beckwith, '
                  '“Movement for Decoration”, after Beal’s nos. 22–24) and 108a '
                  '(Gruppe, “It Sure is Jan.”, after Granville-Smith’s nos. '
                  '107–108) — and ONE ENTRY PRINTED WITHOUT A NUMBER: Grace H. '
                  'Fletcher’s “A Winter Morn in Venice”, between nos. 101 and '
                  '102, the sequence passing directly from 101 to 102 with no '
                  'number left for it; it is recorded with its number empty and '
                  'a note saying so, no number being supplied, because the book '
                  'leaves no number unused — to restore one would be to invent '
                  'a “101a” the book does not print. The book misprints one '
                  'number: Kleen’s “Tic-Tac” is numbered “150.” in print, '
                  'duplicating Klaw’s genuine no. 150; the record stands under '
                  '153, restored from the sequence and flagged in its note. '
                  'Three further numbers are restored from the sequence and '
                  'flagged — nos. 1, 15 and 47, whose printed figures stand '
                  'plainly in the printed page but are garbled in the scan’s '
                  'text layer (read “i”, “IS.” and “4/.”); no. 55 prints no '
                  'stop after its number; and no. 156’s price is settled at '
                  '$300.00 on the printed page, its dollar sign so faintly '
                  'inked that the layer reads “T300”. One record lacks a '
                  'title: no. 170 (Lever), for whose title the book prints a '
                  'rule; its price, $250.00, stands in the record. Peggy '
                  'Bacon’s nos. 12 and 13 both print “The Yellow Jacket” at '
                  '$50.00 — the book’s own duplication, recorded as printed. '
                  'Two readings stand as read: Loven’s no. 177 title “The '
                  'Hill’Top”, the apostrophe being the scan layer’s (the print '
                  'reads “The Hill Top.”), and Lever’s no. 172 “Five Master, '
                  'Gloucester.”, the “l” of Gloucester being a battered sort in '
                  'the print. Every catalogue page was read against the page '
                  'images during the parse. The prize page stands as in 1915 '
                  'and 1916. It prints the list of recipients of the Wm. T. '
                  'Evans Prize, 1888–1913, ending with the 1913 award, Arthur '
                  'Schneider’s “A Morning Walk”, and then states: “This Prize '
                  'has been discontinued.” The Hudnut Prize stands at $200, '
                  'the gift of Alexander M. Hudnut, “for the most meritorious '
                  'Water Color in the exhibition and to be free from any '
                  'restriction whatever”, and the page now records three awards '
                  '— in 1914, to Edward H. Potthast, for “A Holiday”; in 1915, '
                  'to Hilda Belcher, for “Winifred Hunt”; and in 1916, to W. '
                  'Granville-Smith, for “Old Philadelphia”. No Evans Prize '
                  'amount is offered for this exhibition, and the 1917 Hudnut '
                  'award is not recorded in this book.'),
        # The parse stores the plain catalogue numbers as integers,
        # the lettered inserts as strings and one entry's number as
        # the empty string, as printed; the built file carries them
        # all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 330,
            'sections': {'Catalogue': 330},
            # Plain catalogue numbers run 1–327 complete in the single
            # alphabetical sequence, each exactly once, with two
            # lettered inserts standing as printed (24a, 108a) and one
            # entry printed without a number, its number standing
            # empty in the records (Fletcher's, between nos. 101 and
            # 102). The book's misprinted "150." for Kleen's "Tic-Tac"
            # stands in the records under its restored number, 153, so
            # no plain number is duplicated. Prices stand on 293
            # records and a lender is named on 14, so 316 records have
            # no lender; no record prints a medium; one record has no
            # title (no. 170, whose title is a printed rule) and every
            # record has an artist.
            'plain_range': (1, 327),
            'lettered': {'24a', '108a'},
            'no_lender': 316,
            'no_medium': 330,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1918',
        'file': 'aws-1918.json',
        'title': 'Catalogue of the Fifty-First Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '7 February – 1 March 1918',
        'year': 1918,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1918',
        'source': 'Printed catalogue (New York, 1918); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The fifty-first annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, as in 1915, 1916 and 1917: 309 '
                  'records in a single alphabetical run by artist, as in 1902, '
                  '1913, 1915, 1916 and 1917, the works standing under 171 '
                  'artists’ headings. The headings stand surname-first, as in '
                  '1917, in capitals, members carrying the printed suffix '
                  '“A.W.C.S.” set in lowercase type where it stands — 55 of '
                  'the 171 headings carry the mark; beneath each heading, or '
                  'at its right, stands the artist’s address, which is not '
                  'carried into these records, and the book prints no artist '
                  'index. Three headings print a full stop in place of the '
                  'comma after the surname — “HUMPHREY. STETSON,”, '
                  '“MENZLER-PEYTON. BERTHA S.,” and “OCHTMAN. MINA FONDA,” — '
                  'and stand in these records in the comma form; one heading '
                  'keeps a comma between its given names (“Couper, Richard, '
                  'H.”). Each entry stands on one line — number, title and '
                  'element together; no title wraps. Prices stand at the end '
                  'of the entry line in whole dollars, and 294 works are '
                  'priced for sale in the catalogue, the price standing in '
                  'each record’s note; the dearest work is Edward Dufner’s '
                  '“Summer Evening” (no. 71) at $800.00, itself one of the '
                  'eight illustrated works — followed by Herman T. '
                  'Schladermundt’s “Palazzo, Contarini” (no. 260) at $750.00, '
                  'with two records at $600.00 (nos. 5 and 6, A. E. '
                  'Albright’s “The Sister” and “The Dooryard”); four records '
                  'in all stand at $600.00 or more, the cheapest price is '
                  '$25.00 (no. 145, Stetson Humphrey’s “Early Winter”), and '
                  'the prices run from $25 to $800 with a median of $100. '
                  'The lender stands in one form only: a parenthetical '
                  '“(Owned by …)” credit appended to the title line, on four '
                  'records (nos. 9, 29, 272 and 300) — the named party '
                  'stands in the lender field and the printed form is quoted '
                  'in the record’s note; there are no own-line “Owned by” '
                  'credits, no “Lent by”, “Courtesy of” or “Made for” lines '
                  'and no sale marks, and 11 records stand with no element at '
                  'all (nos. 10, 11, 18, 66, 115, 117, 130, 147, 160, 170 '
                  'and 302), those 11 being exactly the records without a '
                  'note. No medium line is printed for any entry this year '
                  'and no dimensions are printed, so Medium and Size stand '
                  'empty throughout. The book IS illustrated: its List of '
                  'Illustrations names eight works by title and artist only, '
                  'without numbers, and eight plates are bound in, '
                  'interleaved one to a leaf — no. 31 (Belcher, “The '
                  'Bouncing Baby”), no. 50 (Chapman, “Westward Ho!”), no. 52 '
                  '(Clark, “Sunset on the Hudson”), no. 71 (Dufner, “Summer '
                  'Evening”), no. 98 (Griffin, “Old Roman Church—Boigneville”), '
                  'no. 151 (Keller, “The Two Helmets”), no. 228 (Peterson, '
                  '“Ballet Girls”) and no. 245 (Robinson, “Colored '
                  'Sails—Venice”) — all eight matched to body entries on '
                  'artist and title, every match unique, and the eight carry '
                  'the note “Illustrated in the catalogue.” There is no '
                  'frontispiece this year and no unmatched plate (contrast '
                  '1917’s Sterner). The List gives Griffin’s title in the '
                  'fuller form “Old Roman Church—Boigneville, France” against '
                  'the body’s shorter form, gives Griffin a dash in place of '
                  'the membership suffix, and names “Alexander Robinson” '
                  'where his plate caption styles him “ALEX ROBINSON”. The '
                  'numbering runs 1–310 with ONE ABSENCE: NO. 118 IS NOT '
                  'PRINTED — the sequence passes from Hartman’s no. 117 '
                  '(“Arctic Grip in Manhattan”) directly to Hasler’s no. 119 '
                  '(“The Landing Place”), with no entry, numbered or '
                  'unnumbered, between them; 118 is a gap in the book’s '
                  'numbering, not an entry without a number, and no record '
                  'is supplied for it. There are no lettered inserts, no '
                  'duplicated numbers, no misprinted figures, no joint '
                  'entries and no unnumbered entries, and nothing is '
                  'restored: every printed figure stands in the scan’s text '
                  'layer reading exactly the number the sequence assigns. '
                  'Two records lack a title: nos. 82 (Edwards) and 84 '
                  '(Emerson), for whose titles the book prints a rule; their '
                  'prices, $125.00 and $50.00, stand in the records. The '
                  'book’s own misprints stand as printed: no. 302’s title '
                  '“Stll Life”, its “i” never printed; no. 18’s “Market '
                  'Day—Lower Pyranees”; no. 113’s “Mayaquez”; no. 49’s “The '
                  'Mangio Tower—Sienna”; no. 309’s “A Bowl of Zenias”; no. '
                  '154’s “Tuluca”; no. 146’s “A Fancy Danse”; and the heading '
                  '“Qackenbush, Ethel H.”, printed without the U. No. 125’s '
                  'title stands as printed, “L’Imitation de Jesus '
                  'Christ—1670.” — the capital I of “L’Imitation” is plain '
                  'on the page, though the scan’s text layer reads it as a '
                  'lowercase l. Every catalogue page was read against the '
                  'page images during the parse. The prize page stands as in '
                  '1915, 1916 and 1917. It prints the list of recipients of '
                  'the Wm. T. Evans Prize, 1888–1913, ending with the 1913 '
                  'award, Arthur Schneider’s “A Morning Walk”, and then '
                  'states: “This Prize has been discontinued.” The Hudnut '
                  'Prize stands at $200, the gift of Alexander M. Hudnut, '
                  '“for the most meritorious Water Color in the exhibition '
                  'and to be free from any restriction whatever”, and the '
                  'page now records four awards — in 1914, to Edward H. '
                  'Potthast, for “A Holiday”; in 1915, to Hilda Belcher, for '
                  '“Winifred Hunt”; in 1916, to W. Granville-Smith, for “Old '
                  'Philadelphia”; and in 1917, to Sidney Dale Shaw, for '
                  '“Snowy Roofs”. No Evans Prize amount is offered for this '
                  'exhibition, and the 1918 Hudnut award is not recorded in '
                  'this book.'),
        # The parse stores the plain catalogue numbers as integers;
        # the built file carries them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 309,
            'sections': {'Catalogue': 309},
            # Plain catalogue numbers run 1–310 in the single
            # alphabetical sequence, the book itself printing no
            # no. 118 — the sequence passes from 117 to 119 on the
            # page — with no lettered inserts, no duplicated
            # numbers, no unnumbered entries and nothing restored.
            # Prices stand on 294 records and a lender is named on
            # 4 (all parenthetical "(Owned by …)" credits), so 305
            # records have no lender; no record prints a medium;
            # two records have no title (nos. 82 and 84, whose
            # titles are printed rules) and every record has an
            # artist.
            'plain_range': (1, 310),
            'absent_numbers': [118],
            'lettered': set(),
            'no_lender': 305,
            'no_medium': 309,
            'no_title': 2,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1919',
        'file': 'aws-1919.json',
        'title': 'Catalogue of the Fifty-Second Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '6 – 28 February 1919',
        'year': 1919,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1919',
        'source': 'Printed catalogue (New York, 1919); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The fifty-second annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, as in 1915, 1916, 1917 and 1918: 360 '
                  'records in a single alphabetical run by artist, as in 1902, '
                  '1913, 1915, 1916, 1917 and 1918, the works standing under 184 '
                  'artists’ headings. The headings stand surname-first, as in '
                  '1917 and 1918, in letter-spaced capitals, members carrying '
                  'the printed suffix “A.W.C.S.” set in lowercase type where it '
                  'stands; beneath each heading, or at its right, stands the '
                  'artist’s address, which is not carried into these records, '
                  'and the book prints no artist index. Two headings print no '
                  'comma after the surname — “KLAW ALONZO,” and “STARR SIDNEY,” '
                  '— and stand surname-first in these records; one heading '
                  'gives the surname only — “GRAHAM,” — his four entries '
                  'standing under it; and the book prints two Albert headings, '
                  '“ALBERT, ERNEST, A.W.C.S.,” (nos. 4–5) and “ALBERT, ERNEST, '
                  'Jr.,” (no. 6), father and son, recorded as the two distinct '
                  'artist strings the book prints. Three headings (Drake, '
                  'Dufner and Leigh) print the membership suffix on a line of '
                  'its own between the heading and the first entry, and it '
                  'stands reattached in these records; the book prints both '
                  'Nelson forms — “NELSON, W. H. de B.,” at no. 256’s heading '
                  'and “NELSON, W. H. deB.,” at no. 257’s — the stop of the '
                  'second standing restored. The scan’s text layer twice '
                  'garbles the membership suffix — “A.WX.S.-” for Beal Reynolds '
                  'and “A.W.C|S.,” for Peterson — and reads Kobbé’s heading as '
                  '“KOBB6”; each stands in these records as the printed page '
                  'shows it. Each entry stands on one line — number, title and '
                  'element together; no title wraps. Prices stand at the end '
                  'of the entry line in whole dollars, and 326 works are '
                  'priced for sale in the catalogue, the price standing in '
                  'each record’s note; the dearest works are Childe Hassam’s '
                  'six pictures, nos. 146–151, at $1,500.00 each — followed by '
                  'two records at $1,000.00 (no. 161, Pearl L. Hill’s “Portrait '
                  'of a Chinese Lady”, and no. 261, G. Glenn Newell’s “Adventure '
                  'Afoot”, itself one of the eight illustrated works), with the '
                  'lettered insert no. 111a next at $800.00; eight records in '
                  'all stand at $1,000.00 or more, the cheapest price is '
                  '$50.00, and the prices run from $50 to $1,500 with a median '
                  'of $80. The lender stands in one form only: a “, owner …” '
                  'credit appended to the title line, on two records (no. 301, '
                  '“Mist and Smoke”, owner Mrs. A. D. Wolf; and no. 312, '
                  '“Summer”, owner R. S. Codman, Boston) — the named party '
                  'stands in the lender field and the printed form is quoted '
                  'in the record’s note; there are no own-line “Owned by” '
                  'credits, no parenthetical credits, no “Lent by”, “Courtesy '
                  'of” or “Made for” lines and no sale marks, and 32 records '
                  'stand with no element at all. One designation stands after '
                  'a title on the entry line: “A Poster.” on F. Luis Mora’s two '
                  'war posters (nos. 240 and 241), carried in those records’ '
                  'notes; no other medium is printed for any entry this year '
                  'and no dimensions are printed, so Medium and Size stand '
                  'empty throughout. The book IS illustrated: eight plates are '
                  'bound in, each captioned at the foot of its leaf, and all '
                  'eight match body entries on artist and title, every match '
                  'unique — no. 5 (Albert, “December”), no. 15 (Basing, “The '
                  'Old Billop House”), no. 126 (Giles, “Maine Shore”), no. 149 '
                  '(Hassam, “Mount Beacon—From Broadway, Newburgh”), no. 206 '
                  '(Leigh, “Resting”), no. 232 (Menzler-Peyton, “Butterflies”), '
                  'no. 261 (Newell, “Adventure Afoot”) and no. 280 (Robinson, '
                  '“Coast of Holland”) — and the eight carry the note '
                  '“Illustrated in the catalogue.” The book prints NO List of '
                  'Illustrations this year (contrast 1918), so the plate '
                  'captions are its only illustration evidence; there is no '
                  'frontispiece and no unmatched plate, and no printed cover '
                  'is preserved in this copy. The numbering runs 1–359 with '
                  'ONE LETTERED INSERT: no. 111a (Edwards, “Sunshine and '
                  'Mist”, $800.00), standing between nos. 111 and 112. No '
                  'number is absent, none is printed twice, none is '
                  'misprinted, there are no joint entries and no unnumbered '
                  'entries, and nothing is restored: every printed figure '
                  'stands in the scan’s text layer reading exactly the number '
                  'the sequence assigns. Some numbers print with a comma after '
                  'them (229, 306, 308–312) — punctuation, not carried into '
                  'these records. One record lacks a title: no. 310 (Sonn), '
                  'for whose title the book prints a rule; its price, $100.00, '
                  'stands in the record. The book’s own spellings stand as '
                  'printed: the headings “LITSHFIELD, J. HOMER,” (printed '
                  'without the C), “CRISE, STEWART S.,”, “BERMATH, SANDER,”, '
                  '“GUISHAIN, J. M.,” and “IMLOCH, W. B.,”; and the titles “The '
                  'Thangerts of Youth” (no. 219), “Street in Emness” (no. 14), '
                  '“Exprestation” (no. 303), “St. Gean du Doigt” (no. 308), '
                  '“Chasyord” (no. 309), “The Skinerdas” (no. 255), “Mt. '
                  'Chocoaua” (no. 339), “The Glacin Cave” (no. 294), “An Old '
                  'South Act” (no. 83), “An Old Poys Kuni” (no. 117), '
                  '“-Challenge”, with its leading dash (no. 350), and “Trad '
                  'Street, Charleston” (no. 333, for Tradd Street). No. 211’s '
                  'title stands as “Ducks” — the book prints “Ducks, $55.”, the '
                  'comma being its price separator. Every catalogue page was '
                  'read against the page images during the parse. The prize '
                  'page stands as in 1915, 1916, 1917 and 1918. It prints the '
                  'list of recipients of the Wm. T. Evans Prize, 1888–1913, '
                  'ending with the 1913 award, Arthur Schneider’s “A Morning '
                  'Walk”, and then states: “This Prize has been discontinued.” '
                  'The Hudnut Prize stands at $200, the gift of Alexander M. '
                  'Hudnut, “awarded for the most meritorious Water Color in the '
                  'exhibition and to be free from any restrictions, whatever”, '
                  'and the page now records five awards — in 1914, to Edward H. '
                  'Potthast, for “A Holiday”; in 1915, to Hilda Belcher, for '
                  '“Winifred Hunt”; in 1916, to W. Granville-Smith, for “Old '
                  'Philadelphia”; in 1917, to Sidney Dale Shaw, for “Snowy '
                  'Roofs”; and in 1918, to Hilda Belcher, for “The Bouncing '
                  'Baby”. No Evans Prize amount is offered for this exhibition, '
                  'and the 1919 Hudnut award is not recorded in this book.'),
        # The parse stores the plain catalogue numbers as integers;
        # the built file carries them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 360,
            'sections': {'Catalogue': 360},
            # Plain catalogue numbers run 1–359 in the single
            # alphabetical sequence, with one lettered insert (111a),
            # no absent numbers, no duplicated numbers, no unnumbered
            # entries and nothing restored. Prices stand on 326
            # records and a lender is named on 2 (both in the
            # ", owner …" form), so 358 records have no lender; no
            # record prints a medium; one record has no title
            # (no. 310, whose title is a printed rule) and every
            # record has an artist.
            'plain_range': (1, 359),
            'lettered': {'111a'},
            'no_lender': 358,
            'no_medium': 360,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1920',
        'file': 'aws-1920.json',
        'title': 'Catalogue of the Fifty-Third Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '5 – 27 February 1920',
        'year': 1920,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1920',
        'source': 'Printed catalogue (New York, 1920); Internet Archive scan (Philadelphia Museum of Art collection)',
        'notes': ('The fifty-third annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, as in 1915, 1916, 1917, 1918 and '
                  '1919: 326 records in a single alphabetical run by artist, as '
                  'in 1902, 1913, 1915, 1916, 1917, 1918 and 1919, the works '
                  'standing under 165 artists’ headings. The headings stand '
                  'surname-first, as in 1917, 1918 and 1919, in letter-spaced '
                  'capitals, members carrying the printed suffix “A.W.C.S.” '
                  'set in lowercase type where it stands; beneath each '
                  'heading, or at its right, stands the artist’s address, '
                  'which is not carried into these records. The book prints '
                  'NO artist index — its back matter is the lists of members '
                  'only, and they carry no catalogue numbers — so no index '
                  'cross-check is possible. One heading line is a '
                  'cross-reference only: “DE HAAS, ALICT TUCKER PREBLE,” — '
                  'the book misprints the given name, ALICE read as ALICT — '
                  'followed by “(See Nos. 109-110.)”; it creates no records, '
                  'and her entries stand under her own correctly spelled '
                  'heading (nos. 109 and 110). Each entry stands on one line '
                  '— number, title and element together. Prices stand at the '
                  'end of the entry line in whole dollars, and 294 works are '
                  'priced for sale in the catalogue, the price standing in '
                  'each record’s note; the dearest work is John S. Eland’s '
                  '“Hail! Mary” (no. 87) at $3,500.00 — followed by Horatio '
                  'Walker’s “A Pastoral—Sow and Pigs” (no. 287) at $3,000.00; '
                  'fifteen records in all stand at $1,000.00 or more, the '
                  'cheapest price is $50.00, and the prices run from $50 to '
                  '$3,500 with a median of $100. One price is printed WITHOUT '
                  'its dollar sign: no. 78c (Dougherty, “Mullion Cove”), '
                  'tabled at 250 — the omission is the book’s, and the bare '
                  'form is quoted in the record’s note. One price is '
                  'misprinted by the book itself: no. 291 prints “$2.000.”, a '
                  'full stop standing for the thousands comma (no. 290 '
                  'directly above prints “$2,500.”); the price stands at '
                  '$2,000.00 and the printed form is quoted in the record’s '
                  'note. The lender stands in one form only: a “, owner …” '
                  'credit appended to the title line itself, on ONE record '
                  '(no. 272, Tiffany, “Village of Field, B. C”, owner Mrs. '
                  'Robert De Forest) — the named party stands in the lender '
                  'field and the printed form is quoted in the record’s note; '
                  'there are no “Owned by” lines, no parenthetical credits, '
                  'no “Lent by”, “Courtesy of” or “Made for” lines and no '
                  'sale marks. No designation is printed after any title, no '
                  'medium is printed for any entry and no dimensions are '
                  'printed, so Medium and Size stand empty throughout. The '
                  'book IS illustrated: its List of Illustrations names eight '
                  'works, and eight plates are bound in, each captioned at '
                  'the foot of its leaf. SEVEN plates match body entries — '
                  'no. 22 (Beal, “Path of Gold”), no. 40 (Berneker, '
                  '“Summer”), no. 50 (Browne, “Street to the Market—Le '
                  'Puy”), no. 97 (Fisher, “The Canton Tea Jar”), no. 136 '
                  '(Howell, “St. Thomas Church”), no. 243 (Ryder, “The Old '
                  'Saw Mill”) and no. 275 (Volkert, “The Quiet Hour”) — and '
                  'carry the note “Illustrated in the catalogue.”; the '
                  'eighth — Charles W. Hawthorne’s “Interior”, standing in '
                  'frontispiece position — matches NO body entry '
                  '(Hawthorne’s body entries are nos. 123–127). Three '
                  'captions differ from their body titles: no. 50’s reads '
                  '“Street to the Market, Le Puy, France” against the body’s '
                  '“Street to the Market—Le Puy”; no. 97’s reads “The Canton '
                  'Crackled Tea Jar” against the body’s “The Canton Tea '
                  'Jar”; and no. 136’s reads “Saint Thomas’ Church, New '
                  'York” against the body’s “St. Thomas Church”. The '
                  'Berneker plate leaf is cropped at its foot in this scan — '
                  'only the word “SUMMER” of its caption survives — and the '
                  'attribution to no. 40 rests on the List of Illustrations '
                  'and on Berneker’s signature within the image. The '
                  'numbering runs 1–315 with ELEVEN LETTERED INSERTS the book '
                  'prints: 78a–78f (Dougherty), 188a–188d (McComas) and 274a '
                  '(Tuttle) — 326 records in all. No number is absent, none '
                  'is printed twice, none is misprinted as another number, '
                  'there are no joint entries and no unnumbered entries, and '
                  'NOTHING is restored: every printed figure stands in the '
                  'scan’s text layer reading exactly the number the sequence '
                  'assigns (contrast 1917 and 1919). A few numbers print '
                  'with a comma after them instead of a stop — punctuation '
                  'only, not carried into these records. The book’s own '
                  'spellings stand as printed, among them the heading '
                  '“HOWELL, FELECIE WALDO” (so also in the List of '
                  'Illustrations) and the titles “Old Mission Near Tuckson” '
                  '(no. 228), “Gate at Endosearch” (no. 284), “Ponciana '
                  'Trees—Honolulu” (no. 189), “Misty Afternoon, Point Lobon” '
                  '(no. 78e) and “Chicken Vender” (no. 117). Every catalogue '
                  'page was read against the page images during the parse. '
                  'The prize page stands as in 1915, 1916, 1917, 1918 and '
                  '1919. It prints the list of recipients of the Wm. T. Evans '
                  'Prize, 1888–1913, ending with the 1913 award, Arthur '
                  'Schneider’s “A Morning Walk”, and then states: “This Prize '
                  'has been discontinued.” The Hudnut Prize stands at $200, '
                  'the gift of Alexander M. Hudnut, “awarded for the most '
                  'meritorious Water Color in the exhibition and to be free '
                  'from any restrictions whatever”, and the page now records '
                  'six awards — in 1914, to Edward H. Potthast, for “A '
                  'Holiday”; in 1915, to Hilda Belcher, for “Winifred Hunt”; '
                  'in 1916, to W. Granville-Smith, for “Old Philadelphia”; in '
                  '1917, to Sidney Dale Shaw, for “Snowy Roofs”; in 1918, to '
                  'Hilda Belcher, for “The Bouncing Baby”; and in 1919, to '
                  'Childe Hassam, for “Mount Beacon—From Broadway, '
                  'Newburgh”. No Evans Prize amount is offered for this '
                  'exhibition, and this book names NO winner for the 1920 '
                  'exhibition itself: Horatio Walker’s Hudnut award belongs '
                  'to this exhibition — his “A Pastoral—Sow and Pigs” stands '
                  'at no. 287 in these records — but it is first printed in '
                  'the 1921 volume’s list.'),
        # The parse stores the plain catalogue numbers as integers;
        # the built file carries them all as strings.
        'no_as_string': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 326,
            'sections': {'Catalogue': 326},
            # Plain catalogue numbers run 1–315 in the single
            # alphabetical sequence, with eleven lettered inserts
            # (78a–78f, 188a–188d and 274a), no absent numbers, no
            # duplicated numbers, no unnumbered entries and nothing
            # restored. Prices stand on 294 records and a lender is
            # named on 1 (no. 272, in the ", owner …" form), so 325
            # records have no lender; no record prints a medium or a
            # title-less entry exists; every record has an artist.
            'plain_range': (1, 315),
            'lettered': {'78a', '78b', '78c', '78d', '78e', '78f',
                         '188a', '188b', '188c', '188d', '274a'},
            'no_lender': 325,
            'no_medium': 326,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-1921',
        'file': 'aws-1921.json',
        'title': 'Catalogue of the Fifty-Fourth Annual Exhibition of the American Water Color Society',
        'subtitle': 'Held at the Galleries of the National Arts Club, 119 East 19th Street, New York',
        'venue': 'Galleries of the National Arts Club, 119 East 19th Street, New York',
        'dates': '3 – 24 February 1921',
        'year': 1921,
        'organiser': 'American Water Color Society',
        'label': 'American Water Color Society 1921',
        'source': 'Printed catalogue (New York, 1921); Internet Archive scan (Philadelphia Museum of Art collection)',
        'notes': ('The fifty-fourth annual exhibition of the American Water Color Society, '
                  'held at the Galleries of the National Arts Club, One Nineteen '
                  'East Nineteenth Street, New York — the exhibition stays at '
                  'the National Arts Club, as in 1915, 1916, 1917, 1918, 1919 '
                  'and 1920: 257 records in a single section, “Catalogue”. The '
                  'book CHANGES ITS FORMAT this year, a change from 1920 and '
                  'from every earlier volume in this run: the entries are no '
                  'longer grouped under artists’ headings in an alphabetical '
                  'run, but stand in HANGING ORDER — each entry a title line, '
                  'the number token “N.” at its left margin and the price, '
                  'when any, at the right end of the same line, followed by '
                  'the artist’s name on the line beneath, indented and '
                  'given-name-first. The artist strings stand given-name-first '
                  'exactly as printed — the convention the 1922 dataset '
                  'already follows — and the 257 records stand under 160 '
                  'artists’ names as printed. UNLIKE the 1920 book, this book '
                  'HAS an index — “Names and Addresses of Exhibitors”, citing '
                  'catalogue numbers — so a full index cross-check was '
                  'possible and was done: 252 of the 257 numbers are cited '
                  'under the right artist. THE INDEX CONFLICTS WITH THE BODY '
                  'in six places, and the body governs in every case: no. 168 '
                  'stands under “John F. Lane” in the body, though the index '
                  'cites the number under Carlson, John F.; the Eaton entry’s '
                  'citation of 152 is an index error (no. 152 is George Elmer '
                  'Browne’s, and the index’s own Browne entry cites it too); '
                  'the Kaelin entry cites 405, 406, 407 and 409 — numbers '
                  'beyond the catalogue’s range — while Kaelin’s body entries, '
                  '30, 31, 34 and 35, are nowhere cited; a Lamb, F. M. entry '
                  'cites 235, though there is no Lamb in the body and no. 235 '
                  'is Sophie M. Brannan’s; the Leeper entry cites 90, which is '
                  'Arthur I. Kellar’s, while Vera Leeper’s body entry, no. 70, '
                  'is nowhere cited; and the Spiers entry cites 241, 245 and '
                  '249, of which only 241 is his. A dozen INDEX NAME FORMS '
                  'differ from the body’s — Bernath for the body’s Bernaph, '
                  'Custis, Eleanor Parks for the body’s Eleanor Parke Curtis, '
                  'Hutchins for Hutchens, McGillivray for MacGilvary, Penman '
                  'for Pennan, Stroud for Sproud among them — and every record '
                  'stands as the body prints it; the body itself prints '
                  '“Matilda Browne” at no. 22 and “Mathilda Browne” at nos. 52 '
                  'and 53, and the records keep both. Prices stand at the end '
                  'of the title line, printed WITH CENTS, and 236 works are '
                  'priced for sale in the catalogue, the price standing in '
                  'each record’s note; the dearest works are Francis '
                  'McComas’s “Storm Clouds” (no. 79) and “Arizona Cliffs” '
                  '(no. 81) at $2,000.00 each — followed by Childe Hassam’s '
                  'three pictures (nos. 147, 149 and 150) at $1,500.00 each '
                  'and two works at $1,200.00, Edward Penfield’s “The Temple '
                  'of Truth” (no. 24) and McComas’s “The Painted Desert” (no. '
                  '83); seven records in all stand at $1,000.00 or more, the '
                  'cheapest price is $50.00, and the prices run from $50 to '
                  '$2,000 with a median of $125. TWO PRICES ARE PRINTED '
                  'WITHOUT THEIR DOLLAR SIGNS — no. 76 (Groll, “A Coming '
                  'Storm”), tabled at 275.00, and no. 123 (Baxter, “Street '
                  'Corner, Grammercy Park”), tabled at 100.00 — printer’s '
                  'slips; the records carry the standard price note. There are '
                  'no lenders in any form — no “Owned by” lines, no '
                  'parenthetical credits, no “, owner …” credits — no medium '
                  'is printed for any entry and no dimensions are printed, so '
                  'Lender, Medium and Size stand empty throughout. The book '
                  'IS illustrated: its List of Illustrations names seven '
                  'works, and seven plates are bound in. SIX plates match '
                  'body entries — no. 72 (Anna Fisher, “Chinese Rose-hips”), '
                  'no. 94 (Harry L. Hoffman, “Song of the Reef”), no. 100 '
                  '(Norwood MacGilvary, “Autumnal”), no. 167 (Edward H. '
                  'Potthast, “Study of a Head”), no. 176 (Roy Brown, “Wet Day, '
                  'New York”) and no. 221 (George Laurence Nelson, “Lady with '
                  'a Rose Tam”) — and carry the note “Illustrated in the '
                  'catalogue.”; three captions differ from their body titles '
                  '— no. 72’s reads “Chinese Rose-Hips”, no. 176’s “A Wet '
                  'Day—New York” and no. 221’s “Lady in a Rose Tam” — and the '
                  'differences stand in the records’ notes. THE SEVENTH PLATE '
                  'MATCHES NO BODY ENTRY: “Hopi Adobes”, by Francis McComas, '
                  'its caption standing vertically on its leaf; McComas’s '
                  'three body entries are “Storm Clouds” (no. 79), “Arizona '
                  'Cliffs” (no. 81) and “The Painted Desert” (no. 83), the '
                  'book gives no way to assign the plate, and no McComas '
                  'record carries an illustrated note. The numbering runs '
                  'plain 1–256, COMPLETE, with ONE LETTERED INSERT the book '
                  'prints: 120A — Evelyn Cohen’s second “A Swiss Interior”, '
                  'between 120 and 121 (the index cites her “115, 120 A”) — '
                  '257 records in all. No number is absent, none is printed '
                  'twice and there are no joint entries; “(Deceased)” prints '
                  'after the artist’s name on the artist line at nos. 14 (W. '
                  'H. deB. Nelson) and 36 (A. T. van Laer), and stands in '
                  'those records’ notes — the index also marks Nelson '
                  '“Deceased” at no. 121, where the body prints nothing, and '
                  'the record follows the body. THE SCAN’S TEXT LAYER IS MUCH '
                  'POORER THAN 1920’S: whole lines drop out (no. 26’s title '
                  'line, no. 79’s title line, the artist lines of nos. 146 '
                  'and 222), number tokens drop or garble (“§6.” for 36, '
                  '“Kid.” for 100), and price tokens drop, split and garble; '
                  'in this typeface the hundreds digits 3 and 5 are '
                  'confusable in BOTH directions — the layer reads several '
                  'printed $350.00 prices as “$550.00”, while no. 72’s '
                  'printed $550.00 is genuine. Every price, and every '
                  'doubtful artist or title reading, was therefore settled on '
                  'the printed page during the parse — a full '
                  'record-by-record visual pass over all fifteen body pages, '
                  'with closer crops of the readings most at risk — and the '
                  'settlements stand in the records. The prize page stands '
                  'as in 1915, 1916, 1917, 1918, 1919 and 1920. It prints the '
                  'list of recipients of the Wm. T. Evans Prize, 1888–1913, '
                  'ending with the 1913 award, Arthur Schneider’s “A Morning '
                  'Walk”, and then states: “This Prize has been '
                  'discontinued.” The Hudnut Prize stands at $200, the gift '
                  'of Alexander M. Hudnut, “awarded for the most meritorious '
                  'Water Color in the exhibition and to be free from any '
                  'restrictions whatever”, and the page now records SEVEN '
                  'awards — in 1914, to Edward H. Potthast, for “A Holiday”; '
                  'in 1915, to Hilda Belcher, for “Winifred Hunt”; in 1916, to '
                  'W. Granville-Smith, for “Old Philadelphia”; in 1917, to '
                  'Sidney Dale Shaw, for “Snowy Roofs”; in 1918, to Hilda '
                  'Belcher, for “The Bouncing Baby”; in 1919, to Childe '
                  'Hassam, for “Mount Beacon—From Broadway, Newburgh”; and in '
                  '1920, to Horatio Walker, for “Pastoral—Sow and Pigs”. '
                  'Walker’s 1920 award — for the picture that stands at no. '
                  '287 in the 1920 records — is FIRST PRINTED IN THIS BOOK: '
                  'the 1920 volume named no winner for its own exhibition. No '
                  'Evans Prize amount is offered for this exhibition, and '
                  'this book names NO winner for the 1921 exhibition itself: '
                  'Francis McComas’s 1921 award, for “The Storm Cloud”, is '
                  'first printed in the 1922 volume (his body entry no. 79 in '
                  'this book is “Storm Clouds”, priced $2,000.00).'),
        # The parse stores the plain catalogue numbers as strings
        # already; the built file carries them all as strings.
        'no_as_string': True,
        # The 1921 parse stores each record's note under 'notes' and
        # carries working 'price' and 'page' fields; the build loop
        # normalises its records to the standard eight fields.
        'notes_plural': True,
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 257,
            'sections': {'Catalogue': 257},
            # Plain catalogue numbers run 1–256 complete in the single
            # section, with one lettered insert (120A), no absent
            # numbers, no duplicated numbers and no unnumbered entries.
            # Prices stand on 236 records; no record names a lender or
            # prints a medium; every record has an artist and a title.
            'plain_range': (1, 256),
            'lettered': {'120A'},
            'no_lender': 257,
            'no_medium': 257,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'aws-nywcc-1922',
        'file': 'aws-1922.json',
        'title': 'Combined Annual Exhibition of the American Water Color Society and the New York Water Color Club, 1922',
        'subtitle': 'Held at the American Fine Arts Building, 215 West Fifty-Seventh Street, New York',
        'venue': 'American Fine Arts Building, 215 West Fifty-Seventh Street, New York',
        'dates': '22 December 1922 – 9 January 1923',
        'year': 1922,
        'organiser': 'American Water Color Society and New York Water Color Club',
        'label': 'American Water Color Society & New York Water Color Club 1922',
        'source': 'Printed catalogue (New York, 1922); Frick Library scan supplied by John Finnegan (Internet Archive digitisation)',
        'notes': ('The combined annual exhibition of the American Water '
                  'Color Society and the New York Water Color Club, held at '
                  'the American Fine Arts Building, 215 West Fifty-Seventh '
                  'Street, New York — the two societies exhibiting together: '
                  '609 records in FOUR sections under one continuous '
                  'numbering — the South Gallery (nos. 1–167), the Centre '
                  'Gallery (nos. 168–372), the Vanderbilt Gallery (nos. '
                  '373–565) and Sculpture (nos. 566–609). The book’s title '
                  'page prints “COMBINED ANNUAL EXHIBITION / AMERICAN WATER '
                  'COLOR SOCIETY / AND / NEW YORK WATER COLOR CLUB” and NO '
                  'ordinal and NO annual number for either society; the '
                  'foreword (signed “HANNAH PIMERTON”) calls the previous '
                  'year’s show the “First Combined Exhibition”, so this is '
                  'the SECOND combined exhibition by inference — the book '
                  'itself numbers nothing. The show stands in this Record '
                  'as ONE exhibition, not one record per society. The '
                  'arrangement breaks with the alphabetical order of '
                  '1913–1919 and with the hanging order of 1921: the works '
                  'are hung and listed BY GALLERY. The body opens under the '
                  'head “Catalogue / Water Colors and Pastels” and the line '
                  '“Information Regarding Prices of Work for Sale May Be '
                  'Obtained at the Desk.”; the Sculpture section stands '
                  'under its own head and the notice that, “by invitation '
                  'of the Exhibition Committee, the National Sculpture '
                  'Society has selected the following works”, with its own '
                  'desk line for pictures and bronzes. The entry form is '
                  'uniform: the number at the left margin; the TITLE in '
                  'letter-spaced small capitals (normalised to title case '
                  'in these records, by the standing convention of the '
                  'gallery volumes); a dotted leader; the artist in '
                  'NATURAL ORDER, title case — there are no artist '
                  'headings, no addresses and no membership suffixes '
                  'anywhere in the body; and at the right the price in '
                  'whole dollars (the “$” sign stands on a page’s first '
                  'price as a column convention) or a printed DASH where '
                  'no price stands. Prices stand at the right of the entry '
                  'line, and 550 works are priced for sale in the '
                  'catalogue, the price standing in each record’s note; '
                  'the printed dash stands on 56 records, and three '
                  'Sculpture entries (nos. 586, 588 and 589) print “On '
                  'application” in place of a price. The dearest work in '
                  'the book is Max. Wieczorek’s “Ruth St. Denis” (no. 420, '
                  'Vanderbilt Gallery) at $3,500.00; next stand $1,500.00 '
                  '(no. 583, Emil Fuchs, “Forbes Robertson”, Sculpture) '
                  'and $1,000.00 (no. 524, Wm. T. L. Armstrong, “The '
                  'Birthday Bouquet”); the dearest work in the South '
                  'Gallery stands at $600.00 (no. 10, Mary Russell Ferrell '
                  'Colton, “Out on the Reservation”) and in the Centre '
                  'Gallery at $500.00 (no. 226, Alphaeus P. Cole, “Lady in '
                  'Green”). NO lender is named for any entry, and no '
                  'medium or size is printed for any entry, so Lender, '
                  'Medium and Size stand empty throughout. The book IS '
                  'illustrated: fifteen plates stand on twelve leaves. '
                  'There is NO List of Illustrations, and the plates are '
                  'identified from their leaf captions — title and artist '
                  'in capitals at the leaf’s foot, no catalogue number — '
                  'matched to the body on artist and title. FOURTEEN match '
                  'a body entry (nos. 2, 32, 37, 40, 50, 66, 96, 221, 381, '
                  '404, 439, 478, 538 and 548) and are flagged on their '
                  'records; six captions differ from their body titles, '
                  'and the difference is quoted in the record’s note — no. '
                  '2’s reads “San Juan Road” (the body “San Jaun Road”), '
                  'no. 32’s “Girl in a Boat” (the body “Girl in Boat”), '
                  'no. 66’s “The Yoke” (the body “The Yorke”), no. 439’s '
                  '“Payne Bingham” (the body “Portrait of Payne Bingham”), '
                  'no. 478’s “Winters End” (the body “Winter’s End”) and '
                  'no. 538’s “A Foggy Day, East Gloucester” (the body '
                  '“Foggy Morning, East Gloucester,”). The FRONTISPIECE is '
                  'captioned with the artist’s name only — “HILDA BELCHER '
                  '/ ENGRAVED BY H. C. MERRILL” — and Belcher has five '
                  'entries in the body (nos. 444, 445, 447, 448 and 449), '
                  'three of them portraits of children by title, so the '
                  'plate cannot be tied to one entry and NO record is '
                  'flagged for it. The numbering is continuous, 1–609, '
                  'across all four sections: no lettered inserts, no '
                  'duplicated numbers, no unnumbered entries and no '
                  'absent numbers. ONE number is the BOOK’s own misprint: '
                  'the entry between 279 and 281 (Egbert Cadmus, “Jagged '
                  'Rocks, Maine”) is printed “200” — a number the book '
                  'also prints correctly at no. 200; the record stands at '
                  '280, restored from the sequence and flagged in its '
                  'note, and the book’s own index cites Cadmus at 277, '
                  '278, 280 and 281, corroborating the restoration. Three '
                  'further numbers are lost to the scan’s TEXT LAYER only '
                  '— they ARE printed in the book: no. 599’s number token, '
                  'and nos. 608–609 entire, are supplied from the page '
                  'render in sequence position, and no. 607 anchors on '
                  'its garbled number sort “an1”, with its title supplied. '
                  'One entry is printed with NO title at all: no. 511 '
                  'stands as number, dotted leader, artist (Joseph '
                  'Rayner) and a dash, and nothing else; the record keeps '
                  'an empty title and a note saying so, and the index '
                  'lists Rayner at 511, agreeing. This book HAS an Index '
                  'of Contributors, WITH catalogue numbers, cross-checked '
                  'entry by entry against the body: it contains NO entry '
                  'for any artist of the Sculpture section — the National '
                  'Sculpture Society exhibitors are not indexed at all — '
                  'and is otherwise in substantial agreement with the '
                  'body. The disagreements are the BOOK’s, and the body '
                  'stands in every case: the index cites Chapman at 437, '
                  '438 for the body’s 537, 538; Dunbar at 536 for 556; W. '
                  'C. L. White at 560 for 550; Patterson at 239 for 238; '
                  'Victor Julius at 185 for 186 (185 is Heuston’s, and is '
                  'also cited under Heuston); Lenski at 355 for 353; and '
                  'the Willson entry is printed TWICE — “Willson, James '
                  'Mallery … 196, 331” and again “Willson, James Mallery … '
                  '322” — the body’s 331 being Jane Mallery Willson’s, who '
                  'has no index entry. The index’s own spelling variants '
                  'against the body (Allen for Allan, Hazell throughout, '
                  'Ochtonan for Ochtman, Wurtz for Wurts among them) stand '
                  'logged, not followed. The BOOK’s own spellings stand as '
                  'printed: no. 2 “San Jaun Road”; no. 25 “Lief Neandross” '
                  '(the members list has LEIF); no. 66 “The Yorke”; no. '
                  '114 “Calendulum”; no. 116 “Eliza D. Gardnier”; no. 218 '
                  '“Lake Taho”; no. 322 “James Mallesy Willson” against '
                  'no. 331 “Jane Mallery Willson”; no. 327 “Frank Hazel” '
                  '(one l) against “Frank Hazell” at 323, 330, 332; no. '
                  '341 “Chas. H. Caseau”; no. 343 “Hydrangias”; no. 392 '
                  '“W. Emerton Heitland”; no. 393 “Catherine Wharton '
                  'Moris” against no. 140 “Catharine Wharton Morris”; the '
                  'surname printed “Kat” (nos. 395, 397, 400 — the index '
                  'agrees); no. 431 “Kate Man Franklin” (the index gives '
                  '“Kate Mann”); no. 435 “Tropic Tapistry” and “Nelly '
                  'Littlehale Murphy” against no. 208 “Nelly Littledale '
                  'Murphy”; no. 477 “Grand Casca Pedia”; no. 538 “Foggy '
                  'Morning, East Gloucester,” with its printed trailing '
                  'comma; no. 573 “Abastina St. L. Eberle”; no. 574 '
                  '“Tergament”; no. 576 “(Insence Burner)”; and the same '
                  'artist spelled differently at different entries '
                  'throughout (Josef/Joseph Lenhard, Hoftrup/Hofstrup, '
                  'S./J. Olaf Olson, Katharine/Katherine Breen, Carle/Carl '
                  'Michel Boog) — each record carries its own entry’s '
                  'printed form. The scan’s text layer is an OCR layer '
                  'whose lines split each printed line into sub-rows by '
                  'type size, and its headline defects were each settled '
                  'from the page renders: on one body page the layer drops '
                  'the ENTIRE price column — the printed prices of nos. '
                  '215–265 are image-only, and all 51 elements were read '
                  'from the 300-dpi page render, read twice; on another it '
                  'drops the artist’s name on 27 entries, all supplied '
                  'from the render; on the Sculpture page it line-merges '
                  'entries 568/569 and 580/581 and seats no. 600’s price '
                  'token in no. 598’s band (no. 598’s printed price is '
                  '$700, no. 600’s is $60). A reader’s pencil stands in '
                  'this copy — a pencilled “$350” against entries at the '
                  'head of one body page, check marks in two margins — '
                  'none of it is print, and none of it is carried. Every '
                  'body page was verified RECORD BY RECORD against its '
                  'render before the parse was signed off — number, '
                  'artist, title and price element — and the parser’s '
                  'per-page token checks (multiset) agree exactly on all '
                  'thirteen body pages. Both societies’ prize pages are '
                  'printed, and NEITHER names a winner for this '
                  'exhibition. The AWS page prints the Hudnut Prize at '
                  '$200, its awards now running through 1921 — in 1919, to '
                  'Childe Hassam, for “Mount Beacon”; in 1920, to Horatio '
                  'Walker, for “Pastoral—Sow and Pigs”; and in 1921, to '
                  'Francis McComas, for “The Storm Cloud”, McComas’s award '
                  'being FIRST PRINTED IN THIS BOOK — and the William T. '
                  'Evans Prize recipients, 1889–1913, followed by “This '
                  'prize has been discontinued.” The NYWCC page prints two '
                  'prizes of the Club’s own: the Beal Prize, $200, '
                  '“instituted in 1904 by William R. Beal”, its printed '
                  'list of awards running 1904–1911 only; and the Club’s '
                  'Hudnut Prize, $100, first awarded 1916, its printed '
                  'list running 1916 (George Luks), 1917 (Hilda Belcher), '
                  '1918 (Colin Campbell Cooper) and 1919 (Edward C. '
                  'Volkert).'),
        # The parse stores the catalogue numbers as strings already;
        # the built file carries them all as strings.
        'no_as_string': True,
        # The parse dataset is named aws-1922.json, but the built
        # file (which the site fetches by exhibition id) is named
        # for the joint exhibition's registry id.
        'out_file': 'aws-nywcc-1922.json',
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 609,
            'sections': {'South Gallery': 167, 'Centre Gallery': 205,
                         'Vanderbilt Gallery': 193, 'Sculpture': 44},
            # Plain catalogue numbers run 1–609 complete across the
            # four contiguous gallery blocks (South 1–167, Centre
            # 168–372, Vanderbilt 373–565, Sculpture 566–609), with no
            # gaps, no lettered inserts, no duplicated numbers and no
            # unnumbered entries. Prices stand on 550 records; no
            # record names a lender or prints a medium; one record
            # (no. 511) prints no title.
            'plain_range': (1, 609),
            'lettered': set(),
            'no_lender': 609,
            'no_medium': 609,
            'no_title': 1,
            'no_artist': 0,
        },
    },
    # ——— Detroit Institute of Arts, 1942–1945 ———
    # The first parses under the unified field standard
    # (FIELD-STANDARD.md, confirmed 25 November 2026): the source
    # files are objects {exhibition, records, apparatus}, not bare
    # record lists. The build takes the records, applies the display
    # adaptation in adapt_object_records (lettered suffixes fold into
    # the catalogue number; the printed lines with no column of their
    # own are appended to the record's note), and carries the
    # apparatus block into the built file beside the records — the
    # site does not yet render the apparatus, but it is not dropped.
    {
        'id': 'detroit-1942',
        'file': 'detroit-1942.json',
        'title': 'Annual Exhibition for Michigan Artists',
        'subtitle': 'As printed in the original exhibition catalogue (1942)',
        'venue': 'Detroit Institute of Arts, Detroit',
        'dates': '17 November – 14 December 1942',
        'year': 1942,
        'organiser': 'Detroit Institute of Arts',
        'label': 'Detroit Institute of Arts 1942',
        'source': 'Original catalogue: Annual Exhibition for Michigan Artists (Detroit Institute of Arts, 1942); HathiTrust item mdp.39015091048705 (University of Michigan copy) — parsed from the catalogue itself',
        'notes': ('The annual juried exhibition for Michigan artists at the Detroit '
         'Institute of Arts — begun in 1910, held under the joint auspices of the '
         'Institute and the Scarab Club until 1928, and judged thereafter by an '
         'out-of-town jury. These records are taken from the original exhibition '
         'catalogue itself (printed pp. 1–16) and stand as the catalogue prints '
         'them: 231 works in the catalogue’s own numbered order — Pictures '
         '(nos. 1–206) and Sculpture (nos. 207–231). The catalogue prints no '
         'medium, dimensions or lender for any work (the works were for sale at '
         'studio prices, enquired of at the desk), and none has been inferred. '
         'Sixteen prizes were awarded; the prize each work won stands in its '
         'record and is shown in its note, as are the asterisked entries the '
         'catalogue marks as not in competition. The foreword counts 143 '
         'painters; the catalogue’s own headings number 142 — the discrepancy '
         'stands as printed. The catalogue’s apparatus — the jury of award, the '
         'prize table, the list of awards and the Founders Society purchase-'
         'prize roll 1926–1942 (which names no winner for 1934) — is carried '
         'in the built file’s apparatus block; the page does not yet display it.'),
        'object_file': True,
        'expect': {
            'total': 231,
            'sections': {'Pictures': 206, 'Sculpture': 25},
            'plain_range': (1, 231),
            'no_lender': 231,
            'no_medium': 231,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'detroit-1944-early-dutch',
        'file': 'detroit-1944-early-dutch.json',
        'title': 'Loan Exhibition of Early Dutch Paintings 1460–1540',
        'subtitle': 'The Twenty-Fifth Loan Exhibition · As printed in the original exhibition catalogue (1944)',
        'venue': 'Detroit Institute of Arts, Detroit',
        'dates': 'February 1944',
        'year': 1944,
        'organiser': 'Detroit Institute of Arts',
        'label': 'Detroit Institute of Arts 1944',
        'source': 'Original catalogue: Loan Exhibition of Early Dutch Paintings 1460–1540 (Detroit Institute of Arts, 1944), catalogue by W. R. Valentiner; HathiTrust item mdp.39015091048713 (University of Michigan copy) — parsed from the catalogue itself',
        'notes': ('The Institute’s Twenty-Fifth Loan Exhibition, a scholarly loan '
         'exhibition of early Dutch paintings catalogued by the Institute’s '
         'director, W. R. Valentiner. These records are taken from the original '
         'catalogue itself and stand as it prints them: 27 works under its six '
         'school sections (Haarlem, Amsterdam, Leiden, Delft, ’s-Hertogenbosch, '
         'Utrecht), each entry carrying its lender and, where the catalogue '
         'prints them, its COLLECTIONS provenance, EXHIBITED history and '
         'DESCRIBED bibliography — those lines stand in each record and are '
         'shown in its note. Sixteen lenders are named, New York dealers among '
         'them. The catalogue prints no prices and names no buyers — it is a '
         'loan exhibition — and the records’ price and buyer fields stand '
         'empty, as printed. Twelve works are illustrated on the catalogue’s '
         'plate leaves; each plate is shown beside its record, cropped from '
         'the catalogue’s own pages. This copy has no closing checklist; the '
         'numbered run was reconciled against the catalogue body itself. The '
         'catalogue’s introduction, lenders list and artist essays are carried '
         'in the built file’s apparatus block; the page does not yet display it.'),
        'object_file': True,
        # February 1944 precedes the December 1944 loan exhibition
        # below; both carry year 1944, so the slate tiebreak is stated.
        'slate_sort': 'detroit-1944-a',
        'expect': {
            'total': 27,
            'sections': {'School of Haarlem': 6, 'School of Amsterdam': 4,
                         'School of Leiden': 5, 'School of Delft': 1,
                         'School of Hertogenbosch': 2, 'School of Utrecht': 9},
            'plain_range': (1, 27),
            'no_lender': 0,
            'no_medium': 0,
            'no_title': 0,
            'no_artist': 0,
        },
    },
    {
        'id': 'detroit-1944-45-romantic',
        'file': 'detroit-1944-45-romantic.json',
        'title': 'The World of the Romantic Artist — A Survey of American Culture from 1800 to 1875',
        'subtitle': 'The Twenty-Sixth Loan Exhibition · As printed in the original exhibition catalogue (1944–45)',
        'venue': 'Detroit Institute of Arts, Detroit',
        'dates': '28 December 1944 – 28 January 1945',
        'year': 1944,
        'organiser': 'Detroit Institute of Arts',
        'label': 'Detroit Institute of Arts 1944–45',
        'source': 'Original catalogue: The World of the Romantic Artist — A Survey of American Culture from 1800 to 1875 (Detroit Institute of Arts, 1944), catalogue by E. P. Richardson; HathiTrust item mdp.39015091048754 (University of Michigan copy) — parsed from the catalogue itself',
        'notes': ('The Institute’s Twenty-Sixth Loan Exhibition, a survey of American '
         'culture from 1800 to 1875 through its painting, catalogued by '
         'E. P. Richardson. These records are taken from the original catalogue '
         'itself and stand as it prints them: 99 works — nos. 1–97 with the '
         'catalogue’s two lettered insertions, 13a and 44a — under its fifteen '
         'parts, from National Leaders to the Exotic Landscape. The catalogue '
         'prints no dimensions and no medium for any work, and none has been '
         'inferred; each work’s printed date, where the catalogue gives one, '
         'stands in its record and is shown in its note. Thirty-nine lenders '
         'are named, American museums and private collectors among them; two '
         'works (nos. 84 and 94) are anonymous loans. Twenty-eight works are '
         'illustrated in the text, each captioned with its number, title and '
         'artist; each illustration is shown beside its record, cropped from '
         'the catalogue’s own pages. The catalogue’s closing index of artists '
         'assigns no. 19 to William Page, where the body gives it to Stanley — '
         'the error stands as printed, and the index is carried whole in the '
         'built file’s apparatus block; the page does not yet display it.'),
        'object_file': True,
        'slate_sort': 'detroit-1944-b',
        'expect': {
            'total': 99,
            'sections': {'The People — I. National Leaders': 4,
                         'The People — II. Elegance and Romantic Beauty': 4,
                         'The People — III. Talent': 6,
                         'The People — IV. Character': 5,
                         'National Life': 8,
                         'Poetic Revery, Fantasy, The Idyll': 6,
                         'Religion': 4,
                         'Animals and Birds': 3,
                         'Still Life': 2,
                         'Landscape — I. The Wilderness Continent': 7,
                         'Landscape — II. The Seas and Ships': 2,
                         'Landscape — III. The Cities of America': 4,
                         'Landscape — IV. The Pastoral or Inhabited Landscape': 7,
                         'Landscape — V. The Exotic Landscape': 14,
                         'Life, Manners, The Variety of the Human Scene, The Humors and Flavors of Life': 23},
            'plain_range': (1, 97),
            'lettered': {'13a', '44a'},
            'no_lender': 0,
            'no_medium': 99,
            'no_title': 0,
            'no_artist': 0,
        },
    },
]


# ——— Slate order ———
# The Record of Exhibitions index (and all.json, which follows it)
# lists the exhibitions grouped by series, chronological within each
# series. The registry above is kept in the order the catalogues were
# parsed and is NOT the display order; the sort below enforces the
# slate on every build, wherever in the registry an entry sits.
# Series are ordered by the year of their first exhibition — National
# Academy of Design 1826, American Water Color Society 1891, then the
# two series beginning in 1892 alphabetically (Guildhall before the
# Salon de la Rose+Croix). When a new series is first recorded, add it
# to SERIES in first-year order. A series missing from SERIES sorts
# after the listed ones, by its first year and then its prefix, so
# the output stays deterministic.
SERIES = [
    ('nad-', 'National Academy of Design'),
    ('aws-', 'American Water Color Society'),
    ('guildhall-', 'Guildhall'),
    ('rose-croix-', 'Salon de la Rose+Croix'),
    ('detroit-', 'Detroit Institute of Arts'),
]

# Display heading for each series, shown as the group heading on the
# Record of Exhibitions page; the summaries carry it as 'series'.
SERIES_HEADINGS = {
    'nad-': 'National Academy of Design — Annual Exhibitions · New York',
    'aws-': 'American Water Color Society — Annual Exhibitions · New York',
    'guildhall-': 'Guildhall Art Gallery — Loan Exhibitions · London',
    'rose-croix-': 'Salons de la Rose+Croix · Paris',
    'detroit-': 'Detroit Institute of Arts — Annual and Loan Exhibitions · Detroit',
}


def _series_heading(ex):
    for prefix, heading in SERIES_HEADINGS.items():
        if ex['id'].startswith(prefix):
            return heading
    return ex['id'].split('-')[0]


def _series_rank(ex):
    for rank, (prefix, _name) in enumerate(SERIES):
        if ex['id'].startswith(prefix):
            return rank
    return len(SERIES)


_unlisted_first_year = {}
for _ex in EXHIBITIONS:
    if _series_rank(_ex) == len(SERIES):
        _prefix = _ex['id'].split('-')[0]
        _unlisted_first_year[_prefix] = min(
            _unlisted_first_year.get(_prefix, _ex['year']), _ex['year'])


def _slate_key(ex):
    # An entry may carry 'slate_sort' to state its place among
    # same-year exhibitions of its series (the two Detroit loan
    # exhibitions both opened in 1944, February before December);
    # it defaults to the exhibition id.
    rank = _series_rank(ex)
    if rank < len(SERIES):
        return (rank, 0, '', ex['year'], ex.get('slate_sort', ex['id']))
    prefix = ex['id'].split('-')[0]
    return (rank, _unlisted_first_year[prefix], prefix,
            ex['year'], ex.get('slate_sort', ex['id']))


EXHIBITIONS.sort(key=_slate_key)


def _is_plain(no):
    """A plain catalogue number: an int, or a string of digits."""
    return isinstance(no, int) or (isinstance(no, str) and no.isdigit())


def verify(ex, recs):
    exp = ex['expect']
    problems = []
    if len(recs) != exp['total']:
        problems.append(f"total {len(recs)} != expected {exp['total']}")
    sections = Counter(r['section'] for r in recs)
    if dict(sections) != exp['sections']:
        problems.append(f"sections {dict(sections)} != expected {exp['sections']}")
    present = {str(r['no']) for r in recs}
    for n in exp.get('absent_numbers', []):
        if str(n) in present:
            problems.append(f"catalogue no. {n} present but should not exist")
    if 'plain_range' in exp:
        lo, hi = exp['plain_range']
        plain = {int(r['no']) for r in recs if _is_plain(r['no'])}
        # Numbers the printed catalogue itself skips (listed under
        # absent_numbers) are not expected in the range.
        expected = set(range(lo, hi + 1)) - set(exp.get('absent_numbers', []))
        if plain != expected:
            missing = sorted(expected - plain)
            extra = sorted(plain - expected)
            problems.append(f"plain numbers != {lo}–{hi} exactly "
                            f"(missing {missing}, extra {extra})")
    if 'duplicated' in exp:
        # Plain numbers the printed catalogue itself repeats, with
        # their exact occurrence counts (the set check above cannot
        # see repetitions). Any other repetition fails the build.
        counts = Counter(str(r['no']) for r in recs if _is_plain(r['no']))
        dups = {n: c for n, c in counts.items() if c > 1}
        if dups != exp['duplicated']:
            problems.append(f"duplicated numbers {dups} != "
                            f"expected {exp['duplicated']}")
    if exp.get('no_numbers'):
        numbered = [r for r in recs if str(r.get('no') or '') != '']
        if numbered:
            problems.append(f"{len(numbered)} records carry a catalogue number "
                            f"but the catalogue prints none")
    if 'lettered' in exp:
        lettered = {str(r['no']) for r in recs
                    if str(r.get('no') or '') != '' and not _is_plain(r['no'])}
        if lettered != exp['lettered']:
            problems.append(f"lettered inserts {sorted(lettered)} != "
                            f"expected {sorted(exp['lettered'])}")
    if 'no_lender' in exp:
        n = sum(1 for r in recs if not r.get('lender'))
        if n != exp['no_lender']:
            problems.append(f"{n} records with no lender != expected {exp['no_lender']}")
    if 'no_title' in exp:
        n = sum(1 for r in recs if not r.get('title'))
        if n != exp['no_title']:
            problems.append(f"{n} records with no title != expected {exp['no_title']}")
    if 'no_artist' in exp:
        n = sum(1 for r in recs if not r.get('artist'))
        if n != exp['no_artist']:
            problems.append(f"{n} records with no artist != expected {exp['no_artist']}")
    if 'no_medium' in exp:
        n = sum(1 for r in recs if not r.get('medium'))
        if n != exp['no_medium']:
            problems.append(f"{n} records with no medium != expected {exp['no_medium']}")
    if problems:
        raise SystemExit(f"VERIFY FAILED for {ex['id']}: " + '; '.join(problems))
    # Section order for the summary: the registry's expected order.
    ordered = Counter()
    for name in exp['sections']:
        ordered[name] = sections[name]
    return ordered


os.makedirs(OUT, exist_ok=True)

# Catalogue-plate images: where a catalogue itself prints an
# illustration with a caption attributing artist and title, the plate
# is cropped from the catalogue's own pages and attached to the record
# (the catalogue is the evidence — no external identity matching).
# The archive of record (full-resolution crops, full plate pages and
# the caption index) lives in the record-of-exhibitions workspace at
# data/plate-archive/<exhibition-id>/index.json; the site carries the
# web-sized crops under public/images/exhibitions/<exhibition-id>/.
PLATE_ARCHIVE_DIR = os.path.expanduser(
    '~/workspace/record-of-exhibitions/data/plate-archive')


def apply_plates(ex, recs):
    path = os.path.join(PLATE_ARCHIVE_DIR, ex['id'], 'index.json')
    if not os.path.exists(path):
        return
    index = json.load(open(path))
    plates = {str(e['no']): e for e in index}
    matched = 0
    for r in recs:
        e = plates.get(str(r['no']))
        if e:
            web = e['web']
            if web.startswith('web/'):
                # The Detroit archives record the web copy's place
                # inside the archive ('web/2.jpg'); the site carries
                # it under /images/exhibitions/<id>/ — the form the
                # earlier archives record directly in their own ways
                # (with or without the leading slash), and those stand
                # exactly as recorded.
                web = f"/images/exhibitions/{ex['id']}/{os.path.basename(web)}"
            r['image'] = web
            r['plate'] = e['plate']
            matched += 1
    if matched != len(plates):
        raise SystemExit(f"PLATES FAILED for {ex['id']}: matched "
                         f"{matched} of {len(plates)} archived plates")
    print(f"{ex['id']}: attached {matched} catalogue plates")


def adapt_object_records(recs):
    """Display adaptation for the field-standard source shape
    ({exhibition, records, apparatus} — the Detroit parses first).
    Formatting-level only: every source field stays on the built
    record; two things change for display.

    * A lettered insert's suffix folds into the catalogue number
      (no 13 with no_suffix 'a' becomes '13a'), the form the other
      catalogues' lettered numbers already take.
    * The printed lines that have no column of their own — the work's
      printed date, COLLECTIONS / EXHIBITED / DESCRIBED lines, a shared
      group heading, prize awards and the not-in-competition flag —
      are appended to the record's note, where the exhibition page
      shows them under the title (the same home the owner and price
      lines take in the American Water Color Society records).
    """
    out = []
    for r in recs:
        r = dict(r)
        if r.get('no_suffix'):
            r['no'] = f"{r['no']}{r['no_suffix']}"
        extra = []
        if r.get('work_date'):
            extra.append(f"Dated {r['work_date']}.")
        if r.get('collections'):
            extra.append(f"{r.get('collections_label') or 'COLLECTIONS'}: "
                         f"{r['collections']}")
        if r.get('exhibited'):
            extra.append(f"EXHIBITED: {r['exhibited']}")
        if r.get('described'):
            extra.append(f"DESCRIBED: {r['described']}")
        if r.get('group'):
            extra.append(f"Shown in the group “{r['group']}”.")
        for a in r.get('award') or []:
            extra.append(f"Award: {a}.")
        if r.get('not_in_competition'):
            extra.append('Not in competition.')
        if extra:
            base = (r.get('note') or '').strip()
            r['note'] = (base + ' ' if base else '') + ' '.join(extra)
        out.append(r)
    return out


summaries = []
all_works = []
for ex in EXHIBITIONS:
    raw = json.load(open(os.path.join(SRC_DIR, ex['file'])))
    apparatus = None
    if isinstance(raw, dict) and 'records' in raw:
        # The field-standard source shape: the records are adapted
        # for display and the apparatus block is carried into the
        # built file beside them (see the output write below).
        recs = adapt_object_records(raw['records'])
        apparatus = raw.get('apparatus')
    else:
        recs = raw
    if ex.get('notes_plural'):
        # This parse stores the record note under 'notes' and carries
        # working 'price' and 'page' fields; the built file carries
        # the standard eight fields, in the standard order.
        recs = [{'no': r['no'], 'artist': r['artist'], 'title': r['title'],
                 'medium': r['medium'], 'size': r['size'],
                 'lender': r['lender'], 'section': r['section'],
                 'note': r['notes']} for r in recs]
    if ex.get('no_as_string'):
        for r in recs:
            r['no'] = str(r['no'])
    sections = verify(ex, recs)
    apply_plates(ex, recs)
    with open(os.path.join(OUT, ex.get('out_file', ex['file'])), 'w') as f:
        if apparatus is not None:
            json.dump({'records': recs, 'apparatus': apparatus}, f,
                      ensure_ascii=False)
        else:
            json.dump(recs, f, ensure_ascii=False)
    summaries.append({
        'id': ex['id'],
        'title': ex['title'],
        'subtitle': ex['subtitle'],
        'venue': ex['venue'],
        'dates': ex['dates'],
        'year': ex['year'],
        'organiser': ex['organiser'],
        'label': ex['label'],
        'series': _series_heading(ex),
        'works': len(recs),
        'sections': [{'name': name, 'works': n} for name, n in sections.items()],
        'source': ex['source'],
        'notes': ex['notes'] + (f" The catalogue’s own title is "
                                f"«{ex['printed_title']}»."
                                if ex.get('printed_title') else ''),
    })
    for r in recs:
        row = dict(r)
        row['exhibition'] = ex['id']
        row['label'] = ex['label']
        all_works.append(row)
    print(f"{ex['id']}: verified {len(recs)} works, "
          f"sections {dict(sections)}")

with open(os.path.join(OUT, 'index.json'), 'w') as f:
    json.dump(summaries, f, ensure_ascii=False)
with open(os.path.join(OUT, 'all.json'), 'w') as f:
    json.dump({'works': all_works}, f, ensure_ascii=False)

print(f"wrote index.json ({len(summaries)} exhibitions), "
      f"all.json ({len(all_works)} works) to {OUT}")
