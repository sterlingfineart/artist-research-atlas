# The Wire — feeding artist reports from the Atlas's own databases

**Status:** built and verified locally, 24 Nov 2026. **Not pushed** — release is a
separate joint decision with John. Pilot/acceptance artist: Walter Frederick
Osborne (1859–1903).

## What it does

An artist report (`#/artist?wd=…&ulan=…`) previously drew only on external
sources (Wikidata, ULAN, OpenAlex, museum APIs), so it showed "0 exhibitions"
and "0 recorded transactions" for artists the Atlas itself documents richly.
The wire connects the report's **Exhibition record** and **Auction & art
sales** sections to the Atlas's own databases through an identity layer:

- Record of Exhibitions (84 exhibitions, 28,714 works wired)
- Loan Exhibitions (UK) — Graves (42,727 works)
- Royal Academy database (161,019 works)
- Paris Salon database (188,028 works)
- Historic Art Sales — Graves vols I–III, Redford vol II, modern landmarks
  (66,689 sales)

487,177 records in total. Source databases are **never edited**; records stay
exactly as printed, including known errors (Graves prints Osborne's birth
year as 1860; that error stays inside the loan data and does not contaminate
the report's identity).

## Data flow

```
public/data/** (the site's own published files)
        │  scripts/build-wire-index.py  (offline build, ~2.5 min)
        ▼
data/wire/groups.json        exhibition metadata (title, venue, dates, URL)
data/wire/shard-<l>.json     27 letter files (shard-a.json … shard-z.json plus
                             shard-0.json), each an object keyed by the two-
                             letter shard key (554 shards by first two letters
                             of the normalised surname; '00' for anything else,
                             filed in shard-0.json); each shard holds the
                             printed artist headings ("identities") of that
                             surname with their records, unchanged
data/wire/meta.json          build stats
        │  lib/wire.js  lookup({ name, by, dy, variants }) — synchronous,
        │  loads only the needed surname letter file, selects the
        │  two-letter shard inside it, memoised
        ▼
lib/report.js  wireFor() — resolves the profile (Wikidata/ULAN name, life
        dates, and the report's full variant set) when a Wikidata id is
        present, else uses the request's name/by/dy; adds inverted name
        forms. exhibitions() returns `atlas`; market() returns `atlasSales`,
        `atlasSalesTotal`, `atlasWithheld`.
        ▼
public/app.js  renderExhibitions (Atlas block first, plates via the existing
        exhPlateHtml, source labels + links, withheld line), renderMarket
        (Atlas sales table first, prices as printed), renderTimeline (Atlas
        exhibitions on the spine), section counts, Sources & method text.
```

Cold lookup measured at 5–92 ms; the report is not noticeably slower. The
shard layout follows the Browse precedent of server-side disk data under
repo-root `data/` (cf. `data/cache/browse-results.json`).

The letter-file packaging (Nov 24, 2026) changes storage only, not
content: the index is deployed by browser web upload, which grants files
individually, so 554 two-letter shard files — the cost recurring at every
rebuild — were repackaged into 27 letter files keyed by shard key, with
each shard's content byte-for-byte the same data. The largest letter
file (shard-b.json) is ~7.7 MB and parses in ~0.37 s on the build
machine (shard-s.json, 5.3 MB, in ~0.12 s); cold lookups stayed in the
same range as before (Osborne ~65–105 ms across runs on a shared CPU;
warm lookups under 1 ms). The
build script emits the letter layout directly; the original two-letter
shard files are kept in `data/wire-v1-shards-backup/`.

Rebuild after any source-database update:

```
python3 scripts/build-wire-index.py --verify
```

## Identity and matching rules

An **identity** is one printed artist heading, parsed to (surname, given
names/initials, printed life dates, activity span per source). The build
keeps every distinct heading separate — "OSBORNE, Walter Frederick, R.H.A.
1860-1903." and "OSBORNE, Walter" are different identities that the query
layer may both attribute to the same artist.

Matching a report artist (name + Wikidata/ULAN variants + life dates) to
identities applies, in order:

1. **Surname gate.** Whole normalised surname must be equal. Hyphens fold to
   spaces ("Alma-Tadema" = "alma tadema" on both sides). **Mc/Mac are never
   folded**, and matching is never on surname alone except for a bare-surname
   identity, which is used only when no given-carrying identity of that
   surname matched (the mononym rule — Rembrandt's sales).
2. **Given-name gate.** A full given name must equal the target's, be a
   cross-language equivalent (Laurent = Lawrence = Lourens; Jean = John;
   Guillaume = William; …), a prefix of it (≥4 chars), or within one OCR
   edit (names ≥5 chars). An identity that prints a full given name is
   **never** matched through an initials-only alias of the target — that is
   the Walter/William Osborne trap. A clear second-given conflict vetoes
   (John Raphael Smith ≠ John Rubens Smith); a short garbled token cannot
   veto.
3. **Date gate.** Printed life dates on a heading must agree with the
   artist's verified dates within ±3 years (Graves's 1860 for Osborne
   passes against 1859; the same heading is rejected for William Osborne,
   1823–1901). Floruit headings skip the gate.
4. **Record-year gate (annual exhibitions only).** RA, Salon, and annual
   exhibitions inside the Record (AWS, NAD) are contemporary exhibitions:
   records dated after death +3 or before birth −2 are withheld, with the
   reason shown. Loan exhibitions are retrospective and deliberately not
   gated — a work of 1752 can hang in a loan show of 1906.
5. **Ambiguity gate.** An identity whose printed heading does not fully
   discriminate it (initials only, no given name, or fewer given names than
   the artist's fullest name form) has each record tested against **rivals**:
   identities of the same surname that (a) carry a full given name — an
   initials-only heading is another abbreviation, not evidence of a second
   person; (b) are a genuinely different person from the target (same-person
   test uses the tolerant equality of rule 2, so OCR garbles and French
   forms of the target are not rivals); (c) are name-compatible with what
   the heading actually prints; and (d) were active **in the same source**
   in the record's year (±3). A covered record is withheld and the reason is
   returned and displayed, never silently dropped.

## Cross-source dedupe (decided)

Where the Loan database and the Record of Exhibitions record the **same
exhibition** (same year, loan venue named in the Record exhibition, and at
least one shared catalogue number for this artist), the two groups are
merged and shown **once**, works merged by catalogue number, Record fields
preferred, missing size/lender filled from Loan, and both sources cited.
Osborne's Guildhall 1904 is the type case: 14 works, sources "Record of
Exhibitions · Loan Exhibitions (UK) — Graves", catalogue plates from the
Record. Loan exhibitions with no Record counterpart stand alone.

## Probable work links

Across different exhibitions, a later work is linked **Probable** to an
earlier one when dimensions agree within 0.6 in per side (either
orientation, after repairing the Graves fraction garble "354" → 35½),
lender surnames agree, and titles share a distinctive word. The link and its
basis are printed on the page. Type case: RA 1909 no. 288 "Feeding Poultry"
(G. McCulloch, 35½×27½ as repaired) → Guildhall 1904 no. 39 "Feeding
Chickens" (George McCulloch, 36×28).

## What is withheld, and why (all shown on the page with reasons)

- Records under initials/underspecified headings where a different artist of
  the same name was active in the same source and years (e.g. "John R.
  Smith" records that could be John Rubens Smith's).
- Annual-exhibition records dated outside the artist's lifetime (e.g. a
  20th-century American namesake's AWS watercolours on John Raphael Smith's
  page).
- Known conservative losses, accepted rather than loosened: Laura
  Alma-Tadema's "Lady" heading (33 records, no given name) renders on
  neither her page nor Lawrence's, because a no-given identity is used only
  when no given-carrying identity of the surname matches; a few extreme OCR
  garbles stay unmatched (Bouguereau: "williah", "Willum-Adolphe" — 3 of his
  50 Salon records).

## Verification (24 Nov 2026, local server, real API)

| Artist | Before (Atlas data on report) | After |
|---|---|---|
| **Walter Osborne** | 0 exhibitions · 0 sales | **20 exhibition groups, 59 works** (Guildhall 1904 merged, 14 works, nos. 26, 39, 45, 66, 130, 143, 155, 161, 171, 182, 183, 185, 223, 224, plates on 45 & 185; RA 1909 loan "Feeding Poultry" with Probable link to no. 39; 44 RA annual works 1886–1903); **0 sales — an honest zero** (he appears in the sales data only as buyer/owner) |
| William Osborne (negative test) | — | 0 — Walter's loan heading (printed 1860–1903) date-rejected |
| Bouguereau (Salon-heavy) | 0 | 48 of 50 Salon works, 56 works total, 54 sales |
| Lawrence Alma-Tadema (RA-heavy) | 0 | 251 works (RA 65, Grosvenor 1883 retrospective 119, Salon, loan), **185 sales** (Graves "Laurence" + Redford "L. Alma-Tadema, R.A."); Laura's and Anna's works excluded |
| John Raphael Smith (ambiguity) | 0 | 70 RA works + 11 posthumous loan works + 13 sales; John Rubens's 43 RA works never appear; ambiguous initials records withheld with reasons; 1910s AWS namesake records withheld by the lifetime gate |

## Plugging in future databases

- **Art Prices Current** (after its 16-volume merge): add a `build_apc()`
  source in the build script emitting the same compact record shape
  (`s: 'sales'`, `sid`, `sl`, price pre-formatted as the sales tab prints
  it); no change needed in `lib/wire.js` or the renderers.
- **Newly inventoried catalogues** (the 27 exhibitions received 24 Nov 2026,
  NAD annuals as parsed): they enter through the Record of Exhibitions'
  own build into `public/data/exhibitions/`, which the wire build already
  reads — one rebuild wires them into every artist report.
- Any new source: give its records `s`, `g`, `y`, `no`, `t` and the fields
  it has (`d`, `l`, `m`, `sec`, `img`, `pl`); add its groups to
  `groups.json` via the build; decide whether it is an *annual* source for
  the lifetime gate (its group titles containing "Annual Exhibition" are
  detected automatically for the Record; other sources are gated by source
  id in `lib/wire.js`).

## Files

- `scripts/build-wire-index.py` — offline index build (parser mirrors
  `lib/wire.js`'s `parseName`; keep the two in step).
- `data/wire/` — generated index (groups.json, 27 letter files holding the
  554 surname shards, meta.json).
- `lib/wire.js` — query-time identity layer (`lookup`, `parseName`).
- `lib/report.js` — `wireFor()` + `atlas` / `atlasSales` response fields.
- `public/app.js` — rendering in the Exhibitions, Market and Timeline
  sections; Sources & method text.
