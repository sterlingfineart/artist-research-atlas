#!/usr/bin/env python3
"""Cross-match the historic sales records (Graves I-II, Redford II)
against the verified open-access works in the Who Painted It? pool
(public/data/game/pool.json), to find sales records whose picture can
actually be shown in Guess the Price.

A match counts ONLY at the Atlas's Confirmed standard for identity
links (see the cross-reference design note):
  * artist is a gate — the sales heading and the museum record must
    name the same person (surname + compatible given names; a
    surname-only sales heading counts only when the surname belongs
    to exactly one pool artist);
  * title/subject essentially identical on the museum's own record
    (equality after normalisation and after stripping any dimensions
    printed in the sales subject — period sale descriptions that
    merely resemble a museum title do not count);
  * the sale must not predate the work (where the museum date parses);
  * dimensions, where the sales record prints them, must AGREE with
    the holding museum's own dimensions for that object (fetched from
    the museum API; either orientation, tolerance ~1.5 in / 5%);
  * a title the same artist sold under again and again (three or more
    records with the identical normalised title) denotes a class of
    pictures, not one picture — none of them can be confirmed;
  * anything surviving all of that is still subject to the documented
    human review below (REVIEW_REJECTED), because a bare title match
    on a much-repeated subject is the weakest evidence there is.

Output: public/data/sales/picture-matches.json — the matches the sales
page loads, plus the audit trail of rejected candidates and why.

Run:  python3 scripts/build-sales-picture-matches.py
"""
import json, re, sys, unicodedata, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SALES = ROOT / 'public' / 'data' / 'sales'
POOL = ROOT / 'public' / 'data' / 'game' / 'pool.json'
OUT = SALES / 'picture-matches.json'
SOURCES = ('graves-vol1', 'graves-vol2', 'redford-vol2')

# Human review, 2026-11-21. Keyed by (source, record index). These
# candidates passed every automated gate but are NOT the same work at
# Confirmed standard; the reason is the record of the review.
REVIEW_REJECTED = {
    ('graves-vol2', 3437):
        'The Met object is a small drawing (pen and brown ink, '
        '9 13/16 x 8 3/16 in., Rogers Fund 1966). The 1790 sale entry '
        'gives no medium, no dimensions, no price and no buyer, and '
        'Jordaens treated the Adoration of the Shepherds repeatedly, '
        'in paint and on paper. Nothing in either record ties this '
        'sheet to that sale.',
}

# ---------------------------------------------------------------- text
def norm_text(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^a-z0-9]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()

HONOR = {'sir', 'dame', 'mr', 'mrs', 'miss', 'dr', 'rev', 'lord', 'lady', 'st', 'saint'}

def pool_artist_key(name):
    toks = [t for t in norm_text(name).split() if t not in HONOR]
    return {'surname': toks[-1] if toks else '', 'given': toks[:-1]}

def sales_artist_key(raw):
    raw = (raw or '').strip()
    pre, _, post = raw.partition(',')
    pre_toks = [t for t in norm_text(pre).split() if t not in HONOR]
    post_toks = [t for t in norm_text(post).split() if t not in HONOR]
    return {'surname': pre_toks[-1] if pre_toks else '', 'given': post_toks}

def given_compatible(sg, pg):
    if not sg or not pg:
        return True
    for t in sg:
        if len(t) == 1:
            if not any(p == t or p.startswith(t) for p in pg):
                return False
        elif t not in pg and not any(s == t[0] for s in sg if len(s) == 1):
            return False
    for t in pg:
        if len(t) > 1 and t not in sg and not any(s == t[0] for s in sg if len(s) == 1):
            return False
    return True

DIM_RE = re.compile(r'(\d+(?:\s+\d+/\d+)?(?:\.\d+)?)\s*(?:in\.?|ins\.?|inches)?\s*[x×]\s*(\d+(?:\s+\d+/\d+)?(?:\.\d+)?)\s*(?:in\.?|ins\.?|inches)?')

def dimval(x):
    x = x.strip()
    m = re.match(r'^(?:(\d+)\s+)?(\d+)/(\d+)$', x)
    if m:
        return int(m.group(1) or 0) + int(m.group(2)) / int(m.group(3))
    return float(x)

def strip_dims(subject):
    m = DIM_RE.search(subject or '')
    if not m:
        return subject, None
    try:
        dims = (dimval(m.group(1)), dimval(m.group(2)))
    except Exception:
        return subject, None
    return subject[:m.start()] + subject[m.end():], dims

def norm_title(s):
    toks = norm_text(s).split()
    while toks and toks[0] in ('the', 'a', 'an'):
        toks = toks[1:]
    return ' '.join(toks)

def pool_year(date):
    years = re.findall(r'(\d{4})', str(date or ''))
    return int(years[-1]) if years else None

# ------------------------------------------------------- museum dimensions
def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'atlas-picture-match/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def museum_dims_in(work):
    """(h, w) in inches from the holding museum's own API, or None."""
    url = work['objectUrl']
    try:
        if 'metmuseum.org' in url:
            oid = url.rstrip('/').split('/')[-1]
            d = fetch_json('https://collectionapi.metmuseum.org/public/collection/v1/objects/' + oid)
            for m in d.get('measurements') or []:
                em = m.get('elementMeasurements') or {}
                if 'Height' in em and 'Width' in em:
                    return (em['Height'] / 2.54, em['Width'] / 2.54)
        elif 'clevelandart.org' in url:
            acc = url.rstrip('/').split('/')[-1]
            d = fetch_json('https://openaccess-api.clevelandart.org/api/artworks/' + acc)
            dims = ((d.get('data') or {}).get('dimensions') or {}).get('unframed') or {}
            if 'height' in dims and 'width' in dims:
                return (dims['height'] / 2.54, dims['width'] / 2.54)
        elif 'artic.edu' in url:
            aid = url.rstrip('/').split('/')[-1]
            d = fetch_json('https://api.artic.edu/api/v1/artworks/' + aid)
            dims = ((d.get('data') or {}).get('dimensions') or '')
            m = re.match(r'([\d.]+)\s*[×x]\s*([\d.]+)\s*cm', dims)
            if m:
                return (float(m.group(1)) / 2.54, float(m.group(2)) / 2.54)
    except Exception as e:
        print('  dims fetch failed for %s: %s' % (url, e), file=sys.stderr)
    return None

def dims_agree(sales_dims, mus_dims):
    if mus_dims is None:
        return None  # unverifiable
    sh, sw = sales_dims
    mh, mw = mus_dims
    def close(a, b):
        return abs(a - b) <= max(1.5, 0.05 * b)
    return (close(sh, mh) and close(sw, mw)) or (close(sh, mw) and close(sw, mh))

# ------------------------------------------------------------------ main
def main():
    pool = json.loads(POOL.read_text())
    works = pool['works']
    by_surname = defaultdict(list)
    artists_by_surname = defaultdict(set)
    for w in works:
        k = pool_artist_key(w['artist'])
        by_surname[k['surname']].append((w, k))
        artists_by_surname[k['surname']].add(w['artist'])

    sources = {sid: json.loads((SALES / (sid + '.json')).read_text())['records']
               for sid in SOURCES}

    # swarm counts: identical (surname, normalised title) across all sales
    swarm = defaultdict(int)
    for recs in sources.values():
        for r in recs:
            subj, _ = strip_dims(r[2])
            swarm[(sales_artist_key(r[0])['surname'], norm_title(subj))] += 1

    candidates = []
    for sid, recs in sources.items():
        for idx, r in enumerate(recs):
            sk = sales_artist_key(r[0])
            if not sk['surname'] or sk['surname'] not in by_surname:
                continue
            subj, dims = strip_dims(r[2])
            nt = norm_title(subj)
            for w, pk in by_surname[sk['surname']]:
                if not given_compatible(sk['given'], pk['given']):
                    continue
                if not sk['given'] and len(artists_by_surname[sk['surname']]) > 1:
                    continue
                if nt != norm_title(w['title']):
                    continue
                candidates.append((sid, idx, r, dims, w))

    matches, rejected = [], []
    for sid, idx, r, dims, w in candidates:
        base = {
            'source': sid, 'artist': r[0], 'subject': r[2], 'saleDate': r[4],
            'lot': r[3], 'page': r[15],
            'poolArtist': w['artist'], 'poolTitle': w['title'],
            'museum': w['museum'], 'objectUrl': w['objectUrl'],
        }
        reason = None
        py = pool_year(w.get('date'))
        if py is not None and r[5] is not None and r[5] < py:
            reason = 'Sale year %d predates the work (%s).' % (r[5], w.get('date'))
        elif dims is not None:
            # A record that prints dimensions can be tested against this
            # specific object — that verdict is decisive for the record,
            # so it outranks the generic-title rule below.
            md = museum_dims_in(w)
            ok = dims_agree(dims, md)
            if ok is None:
                reason = ('Sales record prints dimensions %.4g x %.4g in. but the '
                          'museum dimensions could not be fetched to check them.'
                          % dims)
            elif not ok:
                reason = ('Dimensions disagree: sales record prints %.4g x %.4g in.; '
                          'the museum gives %.4g x %.4g in. for this object.'
                          % (dims + tuple(round(x, 2) for x in md)))
        elif swarm[(sales_artist_key(r[0])['surname'], norm_title(strip_dims(r[2])[0]))] >= 3:
            reason = ('Generic title: the same artist + title heads %d sales '
                      'records — it denotes a class of pictures, not this one.'
                      % swarm[(sales_artist_key(r[0])['surname'], norm_title(strip_dims(r[2])[0]))])
        if reason is None and (sid, idx) in REVIEW_REJECTED:
            reason = REVIEW_REJECTED[(sid, idx)]
        if reason is not None:
            rejected.append(dict(base, reason=reason))
            continue
        matches.append(dict(base, image=w['image']))

    doc = {
        'generated': '2026-11-21',
        'standard': ('Confirmed identity only: same artist, title identical on the '
                     'museum record, sale not before the work, printed dimensions '
                     'in agreement with the museum object, generic repeated titles '
                     'excluded. See scripts/build-sales-picture-matches.py.'),
        'matches': matches,
        'rejected': rejected,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    print('candidates: %d  matches: %d  rejected: %d' % (len(candidates), len(matches), len(rejected)))
    for m in matches:
        print('MATCH  ', m['source'], m['artist'], '—', m['subject'], '=>', m['poolTitle'], '(%s)' % m['museum'])
    for rj in rejected:
        print('REJECT ', rj['source'], rj['artist'], '—', rj['subject'], '=>', rj['poolTitle'])
        print('         ', rj['reason'][:150])

if __name__ == '__main__':
    main()
