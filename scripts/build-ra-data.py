#!/usr/bin/env python3
"""Build the Royal Academy Time Machine's static data files.

Reads the combined Royal Academy database
(~/workspace/ra-database/data/ra-all.json, 162,562 records compiled from
Algernon Graves, "The Royal Academy of Arts: A Complete Dictionary of
Contributors and Their Work", 1905-06, with 1905 recovered from the Paul
Mellon Centre's RA Chronicle catalogue transcription) and writes compact
per-year JSON files plus an index into the Atlas's public/ tree, where the
static file server serves them as-is (no API route needed):

  public/data/ra/index.json     — per-year counts, totals, range
  public/data/ra/<year>.json    — one file per year, 1769-1905

Records whose year could not be resolved (1,543) are skipped entirely:
they are in the full database but not in this browser.

Year-file format:
  {"year":1874,"exhibition":"Summer Exhibition",
   "works":[[catalogueNoOrNull, surname, given, occupation, address,
              title, medium, flags], ...]}
  flags is a bitmask: 1 = catalogue number suspect in the source.
  ("Number inferred?" is always false in this database — no catalogue
  number has ever been invented — so there is no inferred bit.)
  Works are in catalogue-number order (numbers as printed; null when the
  source gives none, sorted last). All strings are copied exactly as in
  the source — no cleanup, no OCR correction. The Salon name-corrections
  file is NOT applied: it is specific to the Paris Salon livrets.

Run:  python3 scripts/build-ra-data.py [--verify]
--verify re-reads the written files and checks them against the source.
"""
import json
import os
import sys

SRC = os.path.expanduser('~/workspace/ra-database/data/ra-all.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                   'public', 'data', 'ra')

# Compact row positions: [number, surname, given, occupation, address,
# title, medium, flags]
FLAG_SUSPECT = 1

# The occupations Graves's dictionary records, in display order. (About
# 19,000 records have no occupation recorded at all; those keep the empty
# string and appear in no occupation count.)
OCCUPATION_ORDER = ['Painter', 'Sculptor', 'Architect', 'Engraver',
                    'Etcher', 'Draughtsman', 'Modeller', 'Lithographer',
                    'Designer', 'Carver', 'Enameller']


def compact_row(r):
    flags = 0
    if r.get('Number suspect?'):
        flags |= FLAG_SUSPECT
    return [r.get('Catalogue No.'), r.get('Artist (surname)'),
            r.get('Artist (given names)'), r.get('Occupation'),
            r.get('Address'), r.get('Title'), r.get('Medium'), flags]


def build(records):
    by_year = {}
    skipped = 0
    for r in records:
        if r.get('Year') is None:
            skipped += 1
            continue
        by_year.setdefault(r['Year'], []).append(r)
    years_out = []
    index_years = []
    total = 0
    for year in sorted(by_year):
        recs = by_year[year]
        assert all(r['Exhibition'] == 'Summer Exhibition' for r in recs), \
            f'mixed exhibition in {year}'
        rows = [compact_row(r) for r in recs]
        # Catalogue-number order; null numbers last. Stable sort keeps the
        # source order among equal keys.
        rows.sort(key=lambda w: (w[0] is None, w[0] if w[0] is not None else 0))
        artists = len({(r.get('Artist (surname)') or '',
                        r.get('Artist (given names)') or '') for r in recs})
        raw_counts = {}
        for r in recs:
            occ = r.get('Occupation') or ''
            if occ:
                raw_counts[occ] = raw_counts.get(occ, 0) + 1
        counts = {o: raw_counts[o] for o in OCCUPATION_ORDER if o in raw_counts}
        for o, n in raw_counts.items():
            if o not in counts:
                counts[o] = n
        years_out.append((year, {'year': year,
                                 'exhibition': 'Summer Exhibition',
                                 'works': rows}))
        index_years.append({'year': year, 'works': len(recs),
                            'artists': artists, 'occupations': counts})
        total += len(recs)
    index = {'years': index_years, 'totalWorks': total,
             'totalYears': len(index_years),
             'range': [index_years[0]['year'], index_years[-1]['year']]}
    return years_out, index, skipped


def write(years_out, index):
    os.makedirs(OUT, exist_ok=True)
    for year, doc in years_out:
        with open(os.path.join(OUT, f'{year}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'index.json'), 'w',
              encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))


def dated_by_year(records):
    by_year = {}
    for r in records:
        if r.get('Year') is not None:
            by_year.setdefault(r['Year'], []).append(r)
    return by_year


def verify(records):
    """Independent check: re-read the written files and compare with source."""
    errors = []
    index = json.load(open(os.path.join(OUT, 'index.json'), encoding='utf-8'))
    by_year = dated_by_year(records)
    dated = sum(len(v) for v in by_year.values())
    if index['totalWorks'] != dated:
        errors.append(f"index totalWorks {index['totalWorks']} != dated source {dated}")
    if index['totalYears'] != len(by_year):
        errors.append(f"index totalYears {index['totalYears']} != {len(by_year)} years in source")
    if [y['year'] for y in index['years']] != sorted(by_year):
        errors.append('index years do not match source years')
    seen_total = 0
    for entry in index['years']:
        year = entry['year']
        doc = json.load(open(os.path.join(OUT, f'{year}.json'), encoding='utf-8'))
        src = by_year[year]
        if doc['year'] != year:
            errors.append(f'{year}.json: year field is {doc["year"]}')
        if doc['exhibition'] != 'Summer Exhibition':
            errors.append(f'{year}.json: exhibition is {doc["exhibition"]!r}')
        if len(doc['works']) != len(src):
            errors.append(f'{year}: {len(doc["works"])} works in file, {len(src)} in source')
        if entry['works'] != len(src):
            errors.append(f'{year}: index says {entry["works"]} works, source has {len(src)}')
        artists = len({(r.get('Artist (surname)') or '', r.get('Artist (given names)') or '') for r in src})
        if entry['artists'] != artists:
            errors.append(f'{year}: index says {entry["artists"]} artists, source has {artists}')
        for occ, n in entry['occupations'].items():
            if sum(1 for r in src if (r.get('Occupation') or '') == occ) != n:
                errors.append(f'{year}: occupation {occ} count mismatch')
        seen_total += len(doc['works'])
        # Works must be in catalogue-number order, nulls last.
        nums = [w[0] for w in doc['works'] if w[0] is not None]
        if nums != sorted(nums):
            errors.append(f'{year}: works not in catalogue-number order')
        if any(w[0] is None for w in doc['works'][:len(nums)]):
            errors.append(f'{year}: a null catalogue number is not sorted last')
    if seen_total != dated:
        errors.append(f'year files total {seen_total} works != dated source {dated}')
    return errors


def spot_check(records):
    """Decode specific source records from the compact files and compare
    every field: Leighton's 1855 no. 569, Sargent's six 1905 works, plus
    a suspect-numbered and a number-less record."""
    results = []

    def find_row(year, src):
        doc = json.load(open(os.path.join(OUT, f'{year}.json'), encoding='utf-8'))
        for w in doc['works']:
            if (w[0] == src.get('Catalogue No.')
                    and w[1] == src.get('Artist (surname)')
                    and w[5] == src.get('Title')):
                return w
        return None

    def check(label, src):
        if src is None:
            results.append((label, 'SOURCE RECORD NOT FOUND'))
            return
        match = find_row(src['Year'], src)
        if match is None:
            results.append((label, 'NOT FOUND in compact file'))
            return
        expected = compact_row(src)
        results.append((label, 'OK' if match == expected else
                        f'MISMATCH: compact={match} expected={expected}'))

    leighton = next((r for r in records
                     if r.get('Year') == 1855 and r.get('Catalogue No.') == 569
                     and (r.get('Artist (surname)') or '').upper().startswith('LEIGHTON')), None)
    check('1855 Leighton no. 569', leighton)
    doc1905 = json.load(open(os.path.join(OUT, '1905.json'), encoding='utf-8'))
    sargent = [w for w in doc1905['works'] if (w[1] or '').upper() == 'SARGENT']
    results.append(('1905 Sargent entries', f'{len(sargent)} (expect 6)'
                    if len(sargent) == 6 else f'{len(sargent)} — EXPECTED 6'))
    suspect = next((r for r in records
                    if r.get('Year') is not None and r.get('Number suspect?')
                    and r.get('Catalogue No.') is not None), None)
    check('a suspect-numbered record', suspect)
    numberless = next((r for r in records
                       if r.get('Year') is not None
                       and r.get('Catalogue No.') is None), None)
    check('a number-less record', numberless)
    return results


def main():
    records = json.load(open(SRC, encoding='utf-8'))
    print(f'source: {len(records)} records')
    years_out, index, skipped = build(records)
    write(years_out, index)
    size = sum(os.path.getsize(os.path.join(OUT, f))
               for f in os.listdir(OUT) if f.endswith('.json'))
    print(f'wrote {len(years_out)} year files + index.json to {OUT}')
    print(f'skipped {skipped} records with no resolved year')
    print(f'compact size on disk: {size:,} bytes ({size / 1048576:.2f} MB)')
    print(f"index: {index['totalWorks']:,} works, {index['totalYears']} years, "
          f"range {index['range'][0]}-{index['range'][1]}")
    if '--verify' in sys.argv:
        errors = verify(records)
        if errors:
            print('VERIFY FAILED:')
            for e in errors:
                print('  -', e)
            sys.exit(1)
        print('verify: all year files and index counts match the source')
        for label, res in spot_check(records):
            print(f'  spot-check {label}: {res}')
            if res != 'OK' and not res.endswith('(expect 6)'):
                sys.exit(1)
        print('spot-checks: all fields match the original records exactly')


if __name__ == '__main__':
    main()
