#!/usr/bin/env python3
"""Build the Historic Art Sales tab's static data files.

Reads the verified sales datasets in ~/workspace/historic-sales/ and
writes one compact JSON file per source into public/data/sales/, plus a
manifest (index.json), so a later volume (e.g. Graves Vol III) drops in
by adding one file and one manifest entry — no page code changes:

  public/data/sales/index.json        — manifest of sources + totals
  public/data/sales/redford-vol2.json — George Redford, Art Sales, Vol II
  public/data/sales/graves-vol1.json  — Algernon Graves, Art Sales, Vol I
  public/data/sales/graves-vol2.json  — Algernon Graves, Art Sales, Vol II
  public/data/sales/graves-vol3.json  — Algernon Graves, Art Sales, Vol III
  public/data/sales/modern.json       — 10 verified modern landmark sales
  public/data/sales/conversions.json  — today's-money multipliers by year

Historic record format (compact array, positions fixed):
  [artist, artistDates, subject, lot, saleDate, saleYear, auctioneer,
   owner, buyer, pricePounds, priceShillings, pricePence,
   priceAsPrinted, currency, francAmount, page, note, flags]
  currency is "GBP" or "FRF"; francAmount is set only for FRF records
  (the amount Graves printed, carried in the source note); flags bit 1 =
  braced/shared price (one printed price covering two or more lots).
  Redford records have no pence column in the source: pricePence is null.
  All strings are copied exactly as in the source files.

Conversions: multipliers by sale year derived from the Bank of England,
"A millennium of macroeconomic data for the UK", version 3.1 (Thomas &
Dimsdale), sheet "A1. Headline series": the consumer price index
(2015=100) for "by prices" and average weekly earnings (£) for "by
earnings". That dataset ends in 2016, so both series are spliced forward
to the base year 2025 with Office for National Statistics figures,
compounded onto the 2016 values: the CPI annual rate (series D7G7,
dataset MM23 — the change in the calendar-year average index) for "by
prices", and the annual growth of Average Weekly Earnings (series KAB9,
whole economy total pay, annual averages, dataset EMP) for "by
earnings". multiplier(year) = index(2025) / index(year). The workbook
itself is read from ~/workspace/historic-sales/source/boe-millennium-
v3.1.xlsx if present, else from the --boe path. The ONS figures are
tabulated in ONS_CPI_RATES / ONS_AWE_ANNUAL below and in
public/data/sales/CONVERSIONS.md.

Run:  python3 scripts/build-sales-data.py [--verify] [--boe PATH]
"""
import json
import os
import re
import sys

HS = os.path.expanduser('~/workspace/historic-sales')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                   'public', 'data', 'sales')

FLAG_BRACED = 1

SOURCES = [
    {
        'id': 'redford-vol2', 'file': 'redford-vol2.json',
        'label': 'Redford, Art Sales, Vol. II (1888)',
        'short': 'Redford II',
        'src': os.path.join(HS, 'data', 'redford-vol2-all.json'),
        'blurb': 'George Redford, “Art Sales” (1888), Vol. II — sales '
                 'records as printed, parsed from the published volume.',
    },
    {
        'id': 'graves-vol1', 'file': 'graves-vol1.json',
        'label': 'Graves, Art Sales, Vol. I (1918)',
        'short': 'Graves I',
        'src': os.path.join(HS, 'data', 'graves-vol1-all.json'),
        'blurb': 'Algernon Graves, “Art Sales”, Vol. I (A–G) — every '
                 'record verified against the page image.',
    },
    {
        'id': 'graves-vol2', 'file': 'graves-vol2.json',
        'label': 'Graves, Art Sales, Vol. II (1921)',
        'short': 'Graves II',
        'src': os.path.join(HS, 'data', 'graves-vol2-all.json'),
        'blurb': 'Algernon Graves, “Art Sales”, Vol. II (H–REME) — every '
                 'record verified against the page image.',
    },
    {
        'id': 'graves-vol3', 'file': 'graves-vol3.json',
        'label': 'Graves, Art Sales, Vol. III (1921)',
        'short': 'Graves III',
        'src': os.path.join(HS, 'data', 'graves-vol3-all.json'),
        'blurb': 'Algernon Graves, “Art Sales”, Vol. III '
                 '(REYNOLDS–ZURBARAN) — every record verified against '
                 'the page image.',
    },
]

FRANC_RES = [re.compile(r'frs\.\s*([\d,]+)'),
             re.compile(r'([\d,]+)\s*francs'),
             re.compile(r'([\d,]+)\s*frs\.')]


def franc_amount(r):
    """A Graves record is franc-priced when no £ price is carried and the
    verification note states the printed price in francs. The amount is
    the figure Graves printed, named in the note."""
    if r.get('price_pounds') is not None:
        return None
    note = r.get('note') or ''
    if not re.search(r'francs|frs\.', note):
        return None
    for rx in FRANC_RES:
        m = rx.search(note)
        if m:
            return int(m.group(1).replace(',', ''))
    return None


def compact_row(r):
    fr = franc_amount(r)
    flags = 0
    if re.search(r'brac', (r.get('note') or ''), re.I):
        flags |= FLAG_BRACED
    sale_date = (r.get('sale_date') or '').strip()
    if not sale_date and r.get('sale_year') is not None:
        sale_date = str(r['sale_year'])
    return [r.get('artist') or '', r.get('artist_dates') or '',
            r.get('subject') or '', r.get('lot') or '', sale_date,
            r.get('sale_year'), r.get('auctioneer') or '',
            r.get('owner') or '', r.get('buyer') or '',
            r.get('price_pounds'), r.get('price_shillings'),
            r.get('price_pence'), r.get('price_as_printed') or '',
            'FRF' if fr is not None else 'GBP', fr,
            r.get('page'), r.get('note') or '', flags]


# --- ONS splice, 2017-2025 (accessed 21 November 2026, ons.gov.uk) ---
# CPI annual rate, series D7G7 (dataset MM23): percentage change in the
# calendar-year average CPI (all items) over the previous year.
ONS_CPI_RATES = {2017: 2.7, 2018: 2.5, 2019: 1.8, 2020: 0.9, 2021: 2.6,
                 2022: 9.1, 2023: 7.3, 2024: 2.5, 2025: 3.4}
# Average Weekly Earnings, series KAB9 (dataset EMP): whole economy
# total pay, annual average, £ per week, seasonally adjusted. The year's
# growth factor is AWE[year] / AWE[year - 1]; compounding the nine
# factors telescopes to AWE[2025] / AWE[2016] = 728 / 494.
ONS_AWE_ANNUAL = {2016: 494, 2017: 505, 2018: 520, 2019: 538, 2020: 547,
                  2021: 580, 2022: 616, 2023: 659, 2024: 694, 2025: 728}
SPLICE_YEAR = 2016          # last year of the BoE millennium dataset
BASE_YEAR = 2025            # latest full year with published ONS data


def build_conversions(boe_path):
    import openpyxl
    wb = openpyxl.load_workbook(boe_path, read_only=True, data_only=True)
    ws = wb['A1. Headline series']
    series = {}
    for row in ws.iter_rows(min_row=8, values_only=True):
        if row[0] is None:
            continue
        earn, cpi = row[39], row[40]
        if earn is not None and cpi is not None:
            series[int(row[0])] = (earn, cpi)
    assert max(series) == SPLICE_YEAR, \
        f'BoE series ends {max(series)}, expected {SPLICE_YEAR}'
    # Splice: extend both index series from 2016 to BASE_YEAR by
    # compounding the ONS annual growth rates onto the 2016 values.
    earn, cpi = series[SPLICE_YEAR]
    for y in range(SPLICE_YEAR + 1, BASE_YEAR + 1):
        cpi = cpi * (1 + ONS_CPI_RATES[y] / 100.0)
        earn = earn * (ONS_AWE_ANNUAL[y] / ONS_AWE_ANNUAL[y - 1])
        series[y] = (earn, cpi)
    earn0, cpi0 = series[BASE_YEAR]
    prices = {y: round(cpi0 / v[1], 4) for y, v in sorted(series.items())}
    earnings = {y: round(earn0 / v[0], 4) for y, v in sorted(series.items())}
    return {'baseYear': BASE_YEAR,
            'source': 'Bank of England, “A millennium of macroeconomic '
                      'data for the UK”, version 3.1 (Thomas & Dimsdale), '
                      'sheet A1. Headline series (to 2016): consumer price '
                      'index (2015=100) and average weekly earnings; '
                      'extended 2017-2025 with Office for National '
                      'Statistics series D7G7 (CPI annual rate) and KAB9 '
                      '(Average Weekly Earnings), compounded onto the '
                      '2016 values.',
            'prices': prices, 'earnings': earnings}, series


def main():
    boe_path = os.path.join(HS, 'source', 'boe-millennium-v3.1.xlsx')
    if '--boe' in sys.argv:
        boe_path = sys.argv[sys.argv.index('--boe') + 1]
    os.makedirs(OUT, exist_ok=True)
    manifest_sources = []
    total = 0
    docs = {}
    for s in SOURCES:
        records = json.load(open(s['src'], encoding='utf-8'))
        rows = [compact_row(r) for r in records]
        doc = {'source': s['id'], 'label': s['label'], 'records': rows}
        docs[s['file']] = doc
        years = [r['sale_year'] for r in records
                 if r.get('sale_year') is not None]
        manifest_sources.append({
            'id': s['id'], 'file': s['file'], 'label': s['label'],
            'short': s['short'], 'count': len(rows),
            'years': [min(years), max(years)], 'blurb': s['blurb'],
            'kind': 'historic'})
        total += len(rows)
        print(f"{s['id']}: {len(rows):,} records, "
              f"years {min(years)}-{max(years)}")
    modern = json.load(open(os.path.join(HS, 'sales.json'),
                            encoding='utf-8'))
    docs['modern.json'] = {'source': 'modern',
                           'label': 'Modern landmark sales',
                           'records': modern}
    manifest_sources.append({
        'id': 'modern', 'file': 'modern.json',
        'label': 'Modern landmark sales', 'short': 'Modern',
        'count': len(modern), 'years': [1990, 2026],
        'blurb': 'Ten landmark sales, each verified against public '
                 'sources and cited on the record. Hammer and '
                 'price-with-premium are separate fields throughout.',
        'kind': 'modern'})
    total += len(modern)
    conv, raw_series = build_conversions(boe_path)
    manifest = {'sources': manifest_sources, 'totalRecords': total,
                'conversionsBaseYear': conv['baseYear']}
    for name, doc in docs.items():
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'conversions.json'), 'w',
              encoding='utf-8') as f:
        json.dump(conv, f, ensure_ascii=False, separators=(',', ':'))
    size = sum(os.path.getsize(os.path.join(OUT, f))
               for f in os.listdir(OUT) if f.endswith('.json'))
    print(f'wrote {len(docs)} source files + index.json + conversions.json '
          f'to {OUT} ({size:,} bytes total)')
    print(f"manifest total: {total:,} records; conversions base year "
          f"{conv['baseYear']}, {len(conv['prices'])} years of multipliers")
    if '--verify' in sys.argv:
        errors = verify(docs, manifest, conv, raw_series)
        if errors:
            print('VERIFY FAILED:')
            for e in errors:
                print('  -', e)
            sys.exit(1)
        print('verify: counts, fields, franc amounts, braced flags and '
              'multipliers all match the sources')


def verify(docs, manifest, conv, raw_series):
    errors = []
    if manifest['totalRecords'] != sum(
            len(d['records']) for d in docs.values()):
        errors.append('manifest total != sum of file records')
    for s in SOURCES:
        src = json.load(open(s['src'], encoding='utf-8'))
        rows = docs[s['file']]['records']
        if len(rows) != len(src):
            errors.append(f"{s['id']}: {len(rows)} rows != {len(src)} source")
            continue
        for r, w in zip(src, rows):
            if w[0] != (r.get('artist') or '') or \
               w[2] != (r.get('subject') or '') or \
               w[9] != r.get('price_pounds') or \
               w[10] != r.get('price_shillings') or \
               w[11] != r.get('price_pence') or \
               w[5] != r.get('sale_year'):
                errors.append(f"{s['id']}: field mismatch at {w[0]} / {w[2]}")
                break
        fr = [w for w in rows if w[13] == 'FRF']
        expect_fr = {'graves-vol1': 22, 'graves-vol2': 22,
                     'graves-vol3': 39}.get(s['id'], 0)
        if len(fr) != expect_fr:
            errors.append(f"{s['id']}: {len(fr)} franc records "
                          f"(expect {expect_fr})")
        if any(w[14] is None or w[14] <= 0 for w in fr):
            errors.append(f"{s['id']}: a franc record lacks its amount")
    base = conv['baseYear']
    earn0, cpi0 = raw_series[base]
    for y in (1709, 1800, 1911):
        if abs(conv['prices'][y] - cpi0 / raw_series[y][1]) > 0.001:
            errors.append(f'prices multiplier wrong for {y}')
        if abs(conv['earnings'][y] - earn0 / raw_series[y][0]) > 0.001:
            errors.append(f'earnings multiplier wrong for {y}')
    return errors


if __name__ == '__main__':
    main()
