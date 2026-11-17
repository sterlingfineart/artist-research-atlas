#!/usr/bin/env python3
"""Build the Atlas site's Loan Exhibitions data files from the parsed
Graves database (~/workspace/graves-loan/data/loan-all.json).

Outputs under public/data/loan/:
  index.json   — totals + per-letter artist/work counts
  <letter>.json — that letter's artists and their works (browse)
  all.json     — every work with full strings (search by artist/title/owner)

Work row: [artistIdx, year|null, no, noSuspect, title, size, owner,
           venue, ownerUncertain]  (letter files)
          [artist, year|null, no, noSuspect, title, size, owner,
           venue, ownerUncertain]  (all.json)
"""
import json, os, re
from collections import defaultdict

SRC = os.path.expanduser('~/workspace/graves-loan/data/loan-all.json')
OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'loan')

recs = json.load(open(SRC))

def letter_of(artist):
    m = re.search(r'[A-Za-z]', artist or '')
    return m.group(0).upper() if m else '#'

by_artist = {}
for r in recs:
    by_artist.setdefault(r['artist'], []).append(r)
artists_sorted = sorted(by_artist.keys(), key=lambda a: a.lower())

letters = defaultdict(list)
for a in artists_sorted:
    letters[letter_of(a)].append(a)

os.makedirs(OUT, exist_ok=True)
index = {'totalWorks': len(recs), 'totalArtists': len(artists_sorted), 'letters': []}
for letter in sorted(letters):
    names = letters[letter]
    works = []
    artist_rows = []
    for ai, name in enumerate(names):
        rs = by_artist[name]
        yrs = [r['year'] for r in rs if r['year']]
        artist_rows.append([name, len(rs), min(yrs) if yrs else None, max(yrs) if yrs else None])
        for r in rs:
            works.append([ai, r['year'], r['no'], 1 if r['noSuspect'] else 0,
                          r['title'], r['size'], r['owner'], r['venue'],
                          1 if r['ownerUncertain'] else 0])
    with open(os.path.join(OUT, f'{letter}.json'), 'w') as f:
        json.dump({'artists': artist_rows, 'works': works}, f, ensure_ascii=False)
    index['letters'].append({'letter': letter, 'artists': len(names), 'works': len(works)})

with open(os.path.join(OUT, 'index.json'), 'w') as f:
    json.dump(index, f, ensure_ascii=False)

all_works = []
for r in recs:
    all_works.append([r['artist'], r['year'], r['no'], 1 if r['noSuspect'] else 0,
                      r['title'], r['size'], r['owner'], r['venue'],
                      1 if r['ownerUncertain'] else 0])
with open(os.path.join(OUT, 'all.json'), 'w') as f:
    json.dump({'works': all_works}, f, ensure_ascii=False)

print(f"wrote {index['totalWorks']} works / {index['totalArtists']} artists, "
      f"{len(index['letters'])} letter files + all.json to {OUT}")
