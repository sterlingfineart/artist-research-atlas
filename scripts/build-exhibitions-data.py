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
summaries = []
all_works = []
for ex in EXHIBITIONS:
    recs = json.load(open(os.path.join(SRC_DIR, ex['file'])))
    if ex.get('no_as_string'):
        for r in recs:
            r['no'] = str(r['no'])
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
