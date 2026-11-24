#!/usr/bin/env python3
"""Build the Atlas "wire" index: the identity layer that feeds the artist
report's Exhibition record and Auction & art sales sections from the
Atlas's OWN databases.

Reads the site's published data files (the same files the specialist
pages serve — the source databases are never modified):

  public/data/exhibitions/all.json + index.json   Record of Exhibitions
  public/data/loan/all.json                       Graves, Loan Exhibitions
  public/data/ra/<year>.json                      Royal Academy dictionary
  public/data/salon/<year>.json                   Paris Salon livrets
  public/data/sales/graves-vol{1,2,3}.json        Graves, Art Sales
  public/data/sales/redford-vol2.json             Redford, Art Sales
  public/data/sales/modern.json                   verified modern sales

Writes a server-side index under data/wire/ (not public/, like the
Browse result cache):

  data/wire/shard-<l>.json   letter files (shard-a.json … shard-z.json
                             plus shard-0.json): each an object keyed by
                             the two-letter surname prefix (first two
                             normalised surname characters, '00' for
                             anything else) holding that shard's artists
                             + slim records unchanged. ~28 files instead
                             of ~554 keeps web-upload rebuilds practical.
  data/wire/groups.json      exhibition group metadata by group key
  data/wire/meta.json        build stamp, source labels, totals

An "identity" in this index is one artist heading exactly as a source
prints it (e.g. "OSBORNE, Walter Frederick, R.H.A. 1860-1903."), parsed
into surname / given names / printed life dates. Records stay as
printed; identity resolution happens at query time in lib/wire.js
against the report artist's authority-file name variants and life
dates, under the rules in WIRE-DESIGN.md. This script never merges
identities and never edits a source record.

Run:  python3 scripts/build-wire-index.py [--verify]
"""
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
PUB = os.path.join(ROOT, 'public', 'data')
OUT = os.path.join(ROOT, 'data', 'wire')

# ------------------------------------------------------------------ norm
# Mirror of lib/util.js norm(): NFD, strip combining marks, lowercase,
# keep a-z 0-9 and the Cyrillic/Hebrew/CJK ranges, collapse whitespace.
def norm(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if not (0x0300 <= ord(c) <= 0x036F))
    s = s.lower()
    s = re.sub(r'[^a-z0-9\u0400-\u04ff\u0590-\u06ff\u3040-\u9fff ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

# ------------------------------------------------------- name vocabulary
# Titles and degrees are not name parts. They are dropped from the given
# names (they stay in the raw form, which is preserved for display).
TITLES = {
    'sir', 'dame', 'lady', 'lord', 'miss', 'mrs', 'mr', 'dr', 'rev',
    'hon', 'rt', 'prof', 'capt', 'col', 'gen', 'major', 'mme', 'mlle',
    'm', 'st', 'saint', 'father', 'brother', 'sister', 'hrh', 'the',
    'late', 'esq', 'esquire', 'jr', 'sr', 'jun', 'sen',
}
DEGREES = {
    'ra', 'rha', 'pra', 'ara', 'rsa', 'rws', 'om', 'kc', 'kcb', 'mp',
    'dd', 'frs', 'llb', 'lld', 'ma', 'md', 'ara', 'hrha', 'ara',
    'cbe', 'obe', 'kbe', 'fsa', 'ria', 'roi', 'rba', 'neac', 'sws',
}
# Printed abbreviations of given names, expanded so "Wm." can meet
# "William". Conservative list of period-standard forms.
ABBREV = {
    'wm': 'william', 'thos': 'thomas', 'jas': 'james', 'chas': 'charles',
    'geo': 'george', 'robt': 'robert', 'edw': 'edward',
    'fredk': 'frederick', 'fred': 'frederick', 'alex': 'alexander',
    'alexr': 'alexander', 'benj': 'benjamin', 'saml': 'samuel',
    'sam': 'samuel', 'danl': 'daniel', 'dan': 'daniel',
    'jonth': 'jonathan', 'jon': 'jonathan', 'nath': 'nathaniel',
    'margt': 'margaret', 'eliz': 'elizabeth', 'cath': 'catherine',
    'jos': 'joseph', 'hy': 'henry', 'ant': 'anthony', 'anthy': 'anthony',
    'mich': 'michael', 'richd': 'richard', 'jno': 'john',
    'abrm': 'abraham', 'tim': 'timothy', 'gab': 'gabriel',
    'zach': 'zachary', 'bart': 'bartholomew', 'fredc': 'frederick',
    'hen': 'henry', 'isa': 'isaac', 'sol': 'solomon',
}
PARTICLES = {
    'van', 'von', 'de', 'der', 'den', 'del', 'della', 'di', 'du',
    'le', 'la', 'ter', 'ten', 'vanden', 'vander', 'van den', 'van der',
    'd', 'l', 'st', 'st.',
}

YEAR_RX = r'(?:1[0-9]{3}|[5-9][0-9]{2}|20[0-2][0-9])'

def _year_tok(tok):
    """A year token as printed, repairing the OCR digit confusions the
    sources are known for (o for 0, l/I for 1) inside date contexts."""
    t = tok.replace('o', '0').replace('l', '1').replace('I', '1')
    return int(t) if re.fullmatch(r'\d{4}', t) else None

def parse_artist(raw):
    """Parse one printed artist heading into an identity:
    {raw, surname, givens: [[token, isInitial], ...], by, dy, fl:[a,b]|None}
    Life dates printed in the heading are evidence, kept as printed
    (Graves's 1860 for Osborne stays 1860 here; the query-time gate
    tolerates ±3 years, it does not rewrite the source)."""
    s = str(raw or '').strip()
    by = dy = None
    fl = None
    # Parenthetical matter: pull dates out, then drop it (it holds
    # "(called)", "(18o1-1846)" and the like, never name parts).
    def _paren(m):
        nonlocal by, dy
        inner = m.group(1)
        rng = re.search(r'([0-9olI]{4})\s*[-\u2013\u2014]\s*([0-9olI]{4})', inner)
        if rng and by is None:
            a, b = _year_tok(rng.group(1)), _year_tok(rng.group(2))
            if a and b:
                by, dy = a, b
        return ' '
    s = re.sub(r'\(([^)]*)\)', _paren, s)
    # "Died 1909", "b. 1806", "d. 1881"
    m = re.search(r'\b[Dd]ied\s+(' + YEAR_RX + r')', s)
    if m:
        dy = int(m.group(1))
        s = s.replace(m.group(0), ' ')
    m = re.search(r'\bb\.\s*(' + YEAR_RX + r')', s)
    if m:
        by = int(m.group(1))
        s = s.replace(m.group(0), ' ')
    m = re.search(r'\bd\.\s*(' + YEAR_RX + r')', s)
    if m:
        dy = int(m.group(1))
        s = s.replace(m.group(0), ' ')
    # Floruit ranges are activity, not life: keep them separate.
    m = re.search(r'\bfl\.\s*(' + YEAR_RX + r')\s*[-\u2013\u2014]\s*(' + YEAR_RX + r')', s)
    if m:
        fl = [int(m.group(1)), int(m.group(2))]
        s = s.replace(m.group(0), ' ')
    else:
        m = re.search(r'\bfl\.\s*(' + YEAR_RX + r')', s)
        if m:
            fl = [int(m.group(1)), int(m.group(1))]
            s = s.replace(m.group(0), ' ')
    # A remaining bare year range is life dates as printed.
    m = re.search(r'(' + YEAR_RX + r')\s*[-\u2013\u2014]\s*(' + YEAR_RX + r')', s)
    if m and by is None:
        by, dy = int(m.group(1)), int(m.group(2))
        s = s.replace(m.group(0), ' ')
    elif m:
        s = s.replace(m.group(0), ' ')
    # Graves cross-reference tails ("Page 15") are not name parts.
    s = re.sub(r'\bPage\s+\d+\b.*$', ' ', s)
    s = s.replace(';', ',')
    # A comma does not always invert: "Walter F. Osborne, R.H.A." is
    # natural order with an honorific suffix. If everything after the
    # first comma is titles/degrees, drop it and parse natural order.
    if ',' in s:
        head, tail = s.split(',', 1)
        tail_toks = [t for t in re.split(r'[\s,]+', tail) if t]
        def _hon(t):
            return norm(t) in TITLES or norm(t) in DEGREES or \
                re.fullmatch(r'([A-Za-z]\.)+', t) is not None
        if tail_toks and all(_hon(t) for t in tail_toks):
            s = head
    # Split surname / givens.
    if ',' in s:
        surname_part, given_part = s.split(',', 1)
        given_part = given_part.replace(',', ' ')
    else:
        toks = s.split()
        if not toks:
            return {'raw': raw, 'surname': '', 'givens': [], 'by': by, 'dy': dy, 'fl': fl}
        i = len(toks) - 1
        start = i
        while start - 1 >= 1 and norm(toks[start - 1]) in PARTICLES:
            start -= 1
        surname_part = ' '.join(toks[start:])
        given_part = ' '.join(toks[:start])
    surname = norm(surname_part)
    givens = []
    for tok in re.split(r'[\s\-]+', given_part):
        t = norm(tok)
        if not t or t in TITLES or t in DEGREES:
            continue
        if re.fullmatch(r'([a-z]\.)+', tok.strip()) or len(t) == 1:
            givens.append([t[0], 1])
        elif t in ABBREV:
            givens.append([ABBREV[t], 0])
        elif re.fullmatch(r'[a-z]+', t):
            givens.append([t, 0])
        # anything else (digits, garble with symbols) is dropped
    return {'raw': raw, 'surname': surname, 'givens': givens,
            'by': by, 'dy': dy, 'fl': fl}

_parse_cache = {}

def parse_artist_cached(raw):
    p = _parse_cache.get(raw)
    if p is None:
        p = parse_artist(raw)
        _parse_cache[raw] = p
    return p

def signature(p):
    return ' '.join((t if not init else t + '.') for t, init in p['givens'])

def fmt_lsd(p, s, d):
    """Mirror of the sales tab's fmtLSD/salesPriceText in app.js."""
    if p is None:
        return 'No price printed'
    out = '£' + format(int(p), ',')
    if s is not None:
        out += f' {s}s'
    if d is not None:
        out += f' {d}d'
    return out

# ---------------------------------------------------------------- index
class Index:
    def __init__(self):
        self.identities = {}          # (surname, sig) -> identity dict
        self.records = []             # slim records, each with 'i'
        self.groups = {}              # group key -> metadata
        self.stats = defaultdict(int)

    def identity(self, raw):
        p = parse_artist_cached(raw)
        key = (p['surname'], signature(p))
        ident = self.identities.get(key)
        if ident is None:
            ident = {'raw': [], 'surname': p['surname'], 'givens': p['givens'],
                     'by': p['by'], 'dy': p['dy'], 'fl': p['fl'],
                     'dates': [], 'yMin': None, 'yMax': None, 'srcY': {}}
            self.identities[key] = ident
        if raw not in ident['raw']:
            ident['raw'].append(raw)
        if p['by'] is not None:
            ds = [p['by'], p['dy']]
            if ds not in ident['dates']:
                ident['dates'].append(ds)
            if ident['by'] is None:
                ident['by'], ident['dy'] = p['by'], p['dy']
        return key

    def add(self, ikey, rec):
        rec['i'] = ikey
        self.records.append(rec)
        y = rec.get('y')
        if y is not None:
            ident = self.identities[ikey]
            ident['yMin'] = y if ident['yMin'] is None else min(ident['yMin'], y)
            ident['yMax'] = y if ident['yMax'] is None else max(ident['yMax'], y)
            span = ident['srcY'].get(rec['s'])
            if span is None:
                ident['srcY'][rec['s']] = [y, y]
            else:
                span[0] = min(span[0], y)
                span[1] = max(span[1], y)

# ------------------------------------------------------------- sources
def build_record(idx):
    meta = {e['id']: e for e in json.load(open(os.path.join(PUB, 'exhibitions', 'index.json')))}
    for e in meta.values():
        idx.groups['record:' + e['id']] = {
            'title': e['title'], 'venue': e['venue'], 'dates': e['dates'],
            'year': e['year'], 'url': '#/exhibitions/' + e['id'],
            'source': 'record', 'sourceLabel': 'Record of Exhibitions',
        }
    data = json.load(open(os.path.join(PUB, 'exhibitions', 'all.json')))
    for w in data['works']:
        if not (w.get('artist') or '').strip():
            idx.stats['record_skipped_noname'] += 1
            continue
        ikey = idx.identity(w['artist'])
        e = meta[w['exhibition']]
        rec = {'s': 'record', 'g': 'record:' + w['exhibition'], 'y': e['year'],
               'no': w.get('no'), 't': w.get('title') or '', 'd': w.get('size') or '',
               'l': w.get('lender') or '', 'm': w.get('medium') or '',
               'sec': w.get('section') or ''}
        if w.get('image'):
            rec['img'] = w['image']
        if w.get('plate'):
            rec['pl'] = w['plate']
        idx.add(ikey, rec)
        idx.stats['record'] += 1

def build_loan(idx):
    data = json.load(open(os.path.join(PUB, 'loan', 'all.json')))
    for w in data['works']:
        artist, year, no, _sus, title, size, owner, venue, _unc = w
        if not (artist or '').strip():
            idx.stats['loan_skipped_noname'] += 1
            continue
        ikey = idx.identity(artist)
        gk = 'loan:' + norm(venue) + '|' + (str(year) if year else 'nd')
        if gk not in idx.groups:
            idx.groups[gk] = {
                'title': (venue or 'Loan exhibition') + (f', {year}' if year else ''),
                'venue': venue or '', 'dates': str(year) if year else '',
                'year': year, 'url': '#/loan',
                'source': 'loan', 'sourceLabel': 'Loan Exhibitions (UK) — Graves',
            }
        idx.add(ikey, {'s': 'loan', 'g': gk, 'y': year, 'no': no,
                       't': title or '', 'd': size or '', 'l': owner or ''})
        idx.stats['loan'] += 1

def build_ra(idx):
    years = [int(f[:-5]) for f in os.listdir(os.path.join(PUB, 'ra'))
             if f[:-5].isdigit()]
    for year in sorted(years):
        d = json.load(open(os.path.join(PUB, 'ra', f'{year}.json')))
        gk = f'ra:{year}'
        idx.groups[gk] = {
            'title': f"Royal Academy {d.get('exhibition') or 'Summer Exhibition'}",
            'venue': 'Royal Academy of Arts, London', 'dates': str(year),
            'year': year, 'url': '#/ra',
            'source': 'ra', 'sourceLabel': 'Royal Academy database — Graves',
        }
        for w in d['works']:
            no, surname, given, _occ, _addr, title, medium, _flags = w
            ikey = idx.identity(f'{surname}, {given}')
            idx.add(ikey, {'s': 'ra', 'g': gk, 'y': year, 'no': no,
                           't': title or '', 'm': medium or ''})
            idx.stats['ra'] += 1

def build_salon(idx):
    years = [int(f[:-5]) for f in os.listdir(os.path.join(PUB, 'salon'))
             if f[:-5].isdigit()]
    for year in sorted(years):
        d = json.load(open(os.path.join(PUB, 'salon', f'{year}.json')))
        gk = f'salon:{year}'
        idx.groups[gk] = {
            'title': d.get('salon') or 'Paris Salon', 'venue': 'Paris',
            'dates': str(year), 'year': year, 'url': '#/salon',
            'source': 'salon', 'sourceLabel': 'Paris Salon database',
        }
        sections = d.get('sections') or []
        for w in d['works']:
            sec_i, no, surname, given = w[0], w[1], w[2], w[3]
            title, medium = w[6], w[7]
            ikey = idx.identity(f'{surname}, {given}')
            idx.add(ikey, {'s': 'salon', 'g': gk, 'y': year, 'no': no,
                           't': title or '', 'm': medium or '',
                           'sec': sections[sec_i] if sec_i is not None and sec_i < len(sections) else ''})
            idx.stats['salon'] += 1

SALES_FILES = ['graves-vol1', 'graves-vol2', 'graves-vol3', 'redford-vol2']

def build_sales(idx):
    manifest = {s['id']: s for s in json.load(open(os.path.join(PUB, 'sales', 'index.json')))['sources']}
    for sid in SALES_FILES:
        d = json.load(open(os.path.join(PUB, 'sales', sid + '.json')))
        label = manifest.get(sid, {}).get('label') or d.get('label') or sid
        short = manifest.get(sid, {}).get('short') or label
        for r in d['records']:
            (artist, dates, subject, lot, sale_date, sale_year, house,
             owner, buyer, pp, ps, pd, _printed, currency, francs,
             _page, _note, _flags) = r
            if not (artist or '').strip():
                idx.stats['sales_skipped_noname'] += 1
                continue
            ikey = idx.identity(artist)
            # The sales files carry the artist's dates as their own
            # field; attach them to the identity as printed evidence.
            if dates:
                p = parse_artist_cached('X, Y ' + str(dates))
                ident = idx.identities[ikey]
                if p['by'] is not None and [p['by'], p['dy']] not in ident['dates']:
                    ident['dates'].append([p['by'], p['dy']])
                    if ident['by'] is None:
                        ident['by'], ident['dy'] = p['by'], p['dy']
            price = (f"{francs:,} francs" if francs is not None else 'No price printed') \
                if currency == 'FRF' else fmt_lsd(pp, ps, pd)
            idx.add(ikey, {'s': 'sales', 'sid': sid, 'sl': short,
                           'y': sale_year, 'dt': sale_date or '',
                           'h': house or '', 't': subject or '',
                           'lot': lot or '', 'p': price,
                           'pb': buyer or '', 'ow': owner or ''})
            idx.stats['sales'] += 1
    # Modern landmark sales (object records, natural-order names).
    d = json.load(open(os.path.join(PUB, 'sales', 'modern.json')))
    for r in d['records']:
        ikey = idx.identity(r.get('artist') or '')
        y = int(str(r.get('sale_date') or '')[:4]) or None
        idx.add(ikey, {'s': 'sales', 'sid': 'modern', 'sl': 'Modern sales',
                       'y': y, 'dt': r.get('sale_date') or '',
                       'h': r.get('house') or '', 't': r.get('title') or '',
                       'lot': r.get('lot') or '',
                       'p': r.get('price_as_reported') or '',
                       'pb': '', 'ow': ''})
        idx.stats['sales_modern'] += 1

# ---------------------------------------------------------------- main
def shard_of(surname):
    k = (surname or '')[:2]
    return k if re.fullmatch(r'[a-z][a-z0-9]', k or '') else '00'

def main():
    idx = Index()
    build_record(idx)
    build_loan(idx)
    build_ra(idx)
    build_salon(idx)
    build_sales(idx)

    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, 'shard-*.json')):
        os.remove(old)
    shards = defaultdict(lambda: {'artists': {}, 'records': []})
    keymap = {}
    for (surname, sig), ident in idx.identities.items():
        sh = shard_of(surname)
        local = len(shards[sh]['artists'])
        shards[sh]['artists'][local] = {
            'raw': ident['raw'], 'sn': surname, 'gv': ident['givens'],
            'by': ident['by'], 'dy': ident['dy'], 'fl': ident['fl'],
            'dates': ident['dates'], 'yMin': ident['yMin'], 'yMax': ident['yMax'],
            'srcY': ident['srcY'],
        }
        keymap[(surname, sig)] = (sh, local)
    for rec in idx.records:
        sh, local = keymap[rec['i']]
        rec = dict(rec)
        rec['i'] = local
        shards[sh]['records'].append(rec)
    letters = defaultdict(dict)
    for sh, data in shards.items():
        letter = sh[0] if re.fullmatch(r'[a-z]', sh[0]) else '0'
        letters[letter][sh] = data
    total_bytes = 0
    for letter, obj in sorted(letters.items()):
        path = os.path.join(OUT, f'shard-{letter}.json')
        with open(path, 'w') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
        total_bytes += os.path.getsize(path)
    with open(os.path.join(OUT, 'groups.json'), 'w') as f:
        json.dump(idx.groups, f, ensure_ascii=False)
    meta = {
        'builtFrom': 'public/data (Record of Exhibitions, Loan, RA, Salon, Graves/Redford sales)',
        'records': len(idx.records), 'identities': len(idx.identities),
        'groups': len(idx.groups), 'shards': len(shards),
        'shardFiles': len(letters),
        'shardBytes': total_bytes, 'stats': dict(idx.stats),
    }
    with open(os.path.join(OUT, 'meta.json'), 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(json.dumps(meta, indent=1))

    if '--verify' in sys.argv:
        # Re-read the written shards and check the Osborne ground truth
        # is present and correctly parsed.
        prob = []
        found = {}
        for sh in ('os',):
            d = json.load(open(os.path.join(OUT, 'shard-o.json')))[sh]
            for li, a in d['artists'].items():
                if a['sn'] == 'osborne':
                    n = sum(1 for r in d['records'] if r['i'] == int(li))
                    found[a['raw'][0]] = (a['by'], a['dy'], n)
        print('Osborne identities:', json.dumps(found, indent=1))
        loan = [v for k, v in found.items() if 'Walter Frederick' in k]
        if not loan or loan[0][2] != 15:
            prob.append(f'loan Osborne works != 15: {loan}')
        if loan and loan[0][:2] != (1860, 1903):
            prob.append(f'loan Osborne printed dates != 1860-1903: {loan}')
        if prob:
            print('VERIFY FAILED:', prob)
            sys.exit(1)
        print('verify OK')

if __name__ == '__main__':
    main()
