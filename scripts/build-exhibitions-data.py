#!/usr/bin/env python3
"""Build the Atlas site's Record of Exhibitions data files from the
parsed exhibition catalogues in ~/workspace/record-of-exhibitions/data/.

Outputs under public/data/exhibitions/:
  index.json          — array of exhibition summaries, chronological
                        (id, title, venue, dates, year, organiser, works
                        count, sections with counts, source note, and
                        the exhibition's honest "notes" text, which the
                        site shows in its About notice)
  <id>.json           — that exhibition's records, as parsed
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
    {
        'id': 'rose-croix-1892',
        'file': 'rose-croix-1892.json',
        'title': 'Catalogue du Salon de la Rose+Croix : Geste esthétique',
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
        'id': 'rose-croix-1893',
        'file': 'rose-croix-1893.json',
        'title': 'Catalogue officiel illustré du second Salon de la Rose+Croix (IIe Geste esthétique)',
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
        'title': 'Catalogue du Salon de la Rose+Croix (IIIe Geste esthétique)',
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
        'id': 'rose-croix-1895',
        'file': 'rose-croix-1895.json',
        'title': 'Catalogue du Salon de la Rose+Croix (IVe Geste esthétique)',
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
        'id': 'rose-croix-1896',
        'file': 'rose-croix-1896.json',
        'title': 'Salon de la Rose+Croix (Ve Geste esthétique)',
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
        'id': 'rose-croix-1897',
        'file': 'rose-croix-1897.json',
        'title': 'VIe Geste esthétique — Sixième Salon de la Rose+Croix',
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
                  'No images in this first version.'),
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
]


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
summaries = []
all_works = []
for ex in EXHIBITIONS:
    recs = json.load(open(os.path.join(SRC_DIR, ex['file'])))
    sections = verify(ex, recs)
    with open(os.path.join(OUT, ex['file']), 'w') as f:
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
        'works': len(recs),
        'sections': [{'name': name, 'works': n} for name, n in sections.items()],
        'source': ex['source'],
        'notes': ex['notes'],
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
