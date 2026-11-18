#!/usr/bin/env python3
"""Build the Atlas site's Record of Exhibitions data files from the
parsed exhibition catalogues in ~/workspace/record-of-exhibitions/data/.

Outputs under public/data/exhibitions/:
  index.json          — array of exhibition summaries (id, title, venue,
                        dates, year, organiser, works count, sections
                        with counts, source note)
  <id>.json           — that exhibition's records, as parsed
  all.json            — every record across exhibitions, each tagged
                        with its exhibition id and short label
                        (the cross-exhibition search index)

Record fields (as parsed, printed forms kept): no, artist, title,
medium, size, lender, section, note.
"""
import json, os
from collections import Counter

SRC_DIR = os.path.expanduser('~/workspace/record-of-exhibitions/data')
OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'exhibitions')

EXHIBITIONS = [
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
        # Expected values from the verified parse — the build fails
        # loudly rather than shipping numbers that do not match them.
        'expect': {
            'total': 466,
            'sections': {'Gallery I': 72, 'Gallery II': 58,
                         'Gallery III': 64, 'Gallery IV (Water Colours)': 272},
            'absent_numbers': [258],
        },
    },
]


def verify(ex, recs):
    exp = ex['expect']
    problems = []
    if len(recs) != exp['total']:
        problems.append(f"total {len(recs)} != expected {exp['total']}")
    sections = Counter(r['section'] for r in recs)
    if dict(sections) != exp['sections']:
        problems.append(f"sections {dict(sections)} != expected {exp['sections']}")
    present = {str(r['no']) for r in recs}
    for n in exp['absent_numbers']:
        if str(n) in present:
            problems.append(f"catalogue no. {n} present but should not exist")
    if problems:
        raise SystemExit(f"VERIFY FAILED for {ex['id']}: " + '; '.join(problems))
    return sections


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
