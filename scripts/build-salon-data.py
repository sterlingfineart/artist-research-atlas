#!/usr/bin/env python3
"""Build the Salon Time Machine's static data files.

Reads the combined Salon database (~/workspace/salon-database/data/salon-all.json,
144,081 records across 100 Paris Salon years, 1673-1881) and writes compact
per-year JSON files plus an index into the Atlas's public/ tree, where the
static file server serves them as-is (no API route needed):

  public/data/salon/index.json     — per-year counts, totals, range
  public/data/salon/<year>.json    — one file per year with data

Year-file format:
  {"year":1874,"salon":"Paris Salon",
   "sections":["PEINTURE","SCULPTURE","GRAVURE","ARCHITECTURE"],
   "works":[[sectionIndex, catalogueNoOrNull, surname, given, birthplace,
              teacher, title, medium, note, flags], ...]}
  flags is a bitmask: 1 = catalogue number suspect, 2 = number inferred.
  Works are in catalogue-number order within each section (numbers as
  printed; null when the livret gives none). All strings are copied exactly
  as in the source — no cleanup, no OCR correction.

Grouping is by each record's own `year` field, not by source filename:
the 1673 volume is a scholarly reprint holding records dated 1673, 1699
and 1704, and separate 1699/1704 volumes exist too.

Run:  python3 scripts/build-salon-data.py [--verify]
--verify re-reads the written files and checks them against the source.
"""
import json
import os
import sys

SRC = os.path.expanduser('~/workspace/salon-database/data/salon-all.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                   'public', 'data', 'salon')

# Compact row positions: [section, number, surname, given, birthplace,
# teacher, title, medium, note, flags]
FLAG_SUSPECT = 1
FLAG_INFERRED = 2


def compact_row(r, section_index):
    flags = 0
    if r.get('number_suspect'):
        flags |= FLAG_SUSPECT
    if r.get('number_inferred'):
        flags |= FLAG_INFERRED
    return [section_index, r.get('catalogue_no'), r.get('artist_surname'),
            r.get('artist_given'), r.get('birthplace'), r.get('teacher'),
            r.get('title'), r.get('medium'), r.get('note'), flags]


def build(records):
    by_year = {}
    for r in records:
        by_year.setdefault(r['year'], []).append(r)
    years_out = []
    index_years = []
    total = 0
    for year in sorted(by_year):
        recs = by_year[year]
        # Sections in first-appearance order (the livret's own order).
        sections = []
        for r in recs:
            if r['section'] not in sections:
                sections.append(r['section'])
        sidx = {s: i for i, s in enumerate(sections)}
        rows = [compact_row(r, sidx[r['section']]) for r in recs]
        # Catalogue-number order within each section; null numbers last.
        # Stable sort keeps the printed order among equal keys.
        rows.sort(key=lambda w: (w[0], w[1] is None, w[1] if w[1] is not None else 0))
        salon = recs[0]['salon']
        assert all(r['salon'] == salon for r in recs), f'mixed salon in {year}'
        artists = len({(r.get('artist_surname') or '',
                        r.get('artist_given') or '') for r in recs})
        counts = {}
        for r in recs:
            counts[r['section']] = counts.get(r['section'], 0) + 1
        years_out.append((year, {'year': year, 'salon': salon,
                                 'sections': sections, 'works': rows}))
        index_years.append({'year': year, 'works': len(recs),
                            'artists': artists, 'sections': counts})
        total += len(recs)
    index = {'years': index_years, 'totalWorks': total,
             'totalYears': len(index_years),
             'range': [index_years[0]['year'], index_years[-1]['year']]}
    return years_out, index


def write(years_out, index):
    os.makedirs(OUT, exist_ok=True)
    for year, doc in years_out:
        with open(os.path.join(OUT, f'{year}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'index.json'), 'w',
              encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))


def verify(records):
    """Independent check: re-read the written files and compare with source."""
    errors = []
    index = json.load(open(os.path.join(OUT, 'index.json'), encoding='utf-8'))
    by_year = {}
    for r in records:
        by_year.setdefault(r['year'], []).append(r)
    if index['totalWorks'] != len(records):
        errors.append(f"index totalWorks {index['totalWorks']} != source {len(records)}")
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
        if len(doc['works']) != len(src):
            errors.append(f'{year}: {len(doc["works"])} works in file, {len(src)} in source')
        if entry['works'] != len(src):
            errors.append(f'{year}: index says {entry["works"]} works, source has {len(src)}')
        artists = len({(r.get('artist_surname') or '', r.get('artist_given') or '') for r in src})
        if entry['artists'] != artists:
            errors.append(f'{year}: index says {entry["artists"]} artists, source has {artists}')
        for s, n in entry['sections'].items():
            if sum(1 for r in src if r['section'] == s) != n:
                errors.append(f'{year}: section {s} count mismatch')
        seen_total += len(doc['works'])
        # Works must be in catalogue-number order within each section.
        for sec in doc['sections']:
            si = doc['sections'].index(sec)
            nums = [w[1] for w in doc['works'] if w[0] == si and w[1] is not None]
            if nums != sorted(nums):
                errors.append(f'{year}: section {sec} not in catalogue-number order')
    if seen_total != len(records):
        errors.append(f'year files total {seen_total} works != source {len(records)}')
    return errors


def spot_check(records):
    """Decode specific source records from the compact files and compare
    every field. Picks one record per section plus a flagged and a
    number-less one."""
    by_year = {}
    for r in records:
        by_year.setdefault(r['year'], []).append(r)
    picks = []
    for r in records:
        if r['year'] == 1874 and r['section'] == 'PEINTURE' and not r['number_suspect'] and not r['number_inferred']:
            picks.append(('1874 PEINTURE, clean', r))
            break
    for r in records:
        if r['year'] == 1874 and r['section'] == 'SCULPTURE':
            picks.append(('1874 SCULPTURE', r))
            break
    for r in records:
        if r['year'] == 1874 and r['section'] == 'GRAVURE':
            picks.append(('1874 GRAVURE', r))
            break
    for r in records:
        if r['year'] == 1874 and r['section'] == 'ARCHITECTURE':
            picks.append(('1874 ARCHITECTURE', r))
            break
    for r in records:
        if r['year'] == 1880 and r['number_inferred']:
            picks.append(('1880 inferred number', r))
            break
    for r in records:
        if r['year'] == 1673 and r['catalogue_no'] is None:
            picks.append(('1673 prose, no number', r))
            break
    results = []
    for label, src in picks:
        doc = json.load(open(os.path.join(OUT, f"{src['year']}.json"), encoding='utf-8'))
        si = doc['sections'].index(src['section'])
        match = None
        for w in doc['works']:
            if (w[0] == si and w[1] == src['catalogue_no']
                    and w[2] == src['artist_surname'] and w[6] == src['title']):
                match = w
                break
        if match is None:
            results.append((label, 'NOT FOUND in compact file'))
            continue
        expected_flags = (FLAG_SUSPECT if src['number_suspect'] else 0) | \
                         (FLAG_INFERRED if src['number_inferred'] else 0)
        expected = [si, src['catalogue_no'], src['artist_surname'],
                    src['artist_given'], src['birthplace'], src['teacher'],
                    src['title'], src['medium'], src['note'], expected_flags]
        results.append((label, 'OK' if match == expected else
                        f'MISMATCH: compact={match} expected={expected}'))
    return results


def main():
    records = json.load(open(SRC, encoding='utf-8'))
    print(f'source: {len(records)} records')
    years_out, index = build(records)
    write(years_out, index)
    size = sum(os.path.getsize(os.path.join(OUT, f))
               for f in os.listdir(OUT) if f.endswith('.json'))
    print(f'wrote {len(years_out)} year files + index.json to {OUT}')
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
            if res != 'OK':
                sys.exit(1)
        print('spot-checks: all fields match the original records exactly')


if __name__ == '__main__':
    main()
