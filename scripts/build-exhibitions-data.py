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
