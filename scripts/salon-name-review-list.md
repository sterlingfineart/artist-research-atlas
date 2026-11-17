# Salon artist-name cleanup — review list (phase 1)

These are the garbled artist names the automated pass (November 2026)
deliberately did **not** correct. The corrected names live in
`public/data/salon/name-corrections.json` (7,775 unambiguous mappings);
everything here stays as printed on the site until a human resolves it.

Counts: **40,232 distinct forms / 93,860 records** across the three
fields. Most of that bulk is names that are simply rare or already
correct — the actionable items are the **ambiguous** and
**fragment / plausible-surname** sections below. The full
machine-readable lists are in the working directory
(`~/workspace/salon-database/cleanup/`): `given_review.json`,
`surname_review.json`, `teacher_review.json`.

Years 1673 / 1699 / 1704 are excluded from the whole cleanup: their
records are prose fragments from a scholarly reprint, not real livret
name fields.

## How to use this list

- **Ambiguous** — one garbled string plausibly maps to two (or more)
  different people. A human who knows the artist (or can check the
  livret scan) can pick the right one and add it to
  `name-corrections.json`.
- **Fragment / plausible surname** — the string is either a word
  fragment (the tail of a longer name) or a real surname the authority
  data does not know. Do not "correct" these on a guess.
- **Unresolved** — a garbled form with no confident target. Mostly
  one-off OCR wreckage; the top entries by count are listed.
- **Real surname / compound / hyphen-split** — not errors. Real
  surnames are correct names that were considered and left alone;
  compound teacher lists and hyphen-split teacher values need hand
  work to split correctly, they are not single-name corrections.

## Given names — 16,206 forms / 44,694 records

### Ambiguous (a human can resolve these)

| garbled | candidates | records |
|---|---|---|
| `Carie` | Marie / Carle | 27 |
| `jan` / `jean` / `juan` forms (266 forms) | Jan / Jean / Juan | 768 |
| `emile` / `emili` forms (148 forms) | Émile / Émili | 546 |
| `M!k Màthilde-Isàbelle`, `M"V Cécile` … (70 forms) | Max / Mme | 243 |
| `Alexandrb`, `ALEXANDRK-AUGUSTIN-CÊLBgTIN` … (45 forms) | Alexandra / Alexandre | 141 |
| `Bernard-Léoh`, `Charles-Léox` … (31 forms) | Leo / Léon | 92 |
| `Joh an -Jacob`, `Ludovic- An ATOLB` … (17 forms) | Jan / Yan | 80 |

### Unresolved garbles (top by count)

- `M««.` and other honorific garbles — 8,786 records / 4,024 forms
  (e.g. `M" Adélaïde`, `M" Fiélicie`, `M" Harriet`). The honorific is
  unreadable (Mme vs Mlle); the name itself is usually fine.
- Initials-only — 6,095 records / 197 forms (e.g. `A`, `A -F.`).
  Nothing to correct to.
- Digit fragments — 1,625 records / 628 forms
  (e.g. `**0SFE*`, `*I1,e HÉLÈNE -JOSÉPHINE`).
- Comma fragments — 1,387 records / 444 forms (e.g. `!«,U`, `%P,e`).
- Alias constructions — 963 records / 488 forms
  (e.g. `ALBERT deJ, né à Beaulieu (Gantai`).
- The remaining 9,560 unresolved forms (23,223 records) are one-off
  OCR wreckage with no confident target (e.g. `!!"• honori!se`,
  `!**••.`, `!K!le .`).

## Surnames — 16,201 forms / 31,545 records

### Ambiguous (a human can resolve these)

| garbled | candidates | records |
|---|---|---|
| `MOBERT`, `COBERT`, `nOBERT` | Gobert / Robert | 8 |
| `BUQUET`, `BOÛUET` | Boquet / Bouquet | 6 |
| `rAURE`, `AURE`, `PAURE` | Faure / Laure | 6 |
| `UIBOT`, `hibot` | Cibot / Ribot | 6 |
| `ADAU`, `adah` | Adam / Adan | 5 |
| `AUDRY`, `AuDRY` | Aubry / Oudry | 5 |
| `LEREUX` | Leleux / Leroux | 5 |
| `AOBERT` was resolved to Robert by shared given name
  (Louis-Valentin-Élias); `JODY` was resolved to Jouy, not Joly,
  by shared given name (Joseph-Nicolas) and the 1873 livret's
  rewarded-artists list. |

### Fragment / plausible real surname (do not guess)

`COLON` (5, 1799–1801, no given name — a consistent three-year run,
probably a real person), `ment` (5, a word fragment), `ROTER`,
`LOZIER`, `RICHNER`, `BURE`, `PILLETTE`, `BOUCHU`, `PEAU`, `DAVE`,
`PATOU`, `FOUCHET`, `GIRAUDON`, `BRULE` / `BRÛLÉ`, `DUCHENNE`,
`DANJOU`. These are real surnames (or fragments) that the Wikidata
artist set does not know; correcting them on a guess would mislabel
a real exhibitor.

### Other surname categories

- **Real surname** — 9,201 records / 4,352 forms. Correct names that
  were considered and left alone (e.g. `ABADiE`, `ABATE`, `ABEILLE`).
  No action needed.
- **M-prefix, unattested remainder** — 98 records / 36 forms
  (e.g. `M A L A I N E`, `M A S S A R D`, `M A TET`). The remainder
  is not attested as a surname in the data, so the honorific cannot
  be stripped safely.
- **Descriptor** — 11 records / 9 forms (e.g. `Adam l'aîné`,
  `A d a m le jeune`, `FAUSSILLOIV dit LABOSB`). Left as-is.
- **Unresolved** — 22,006 records / 11,687 forms. Garbles with no
  confident target (e.g. `A CADÉMICIENS`, `A STRUG`, `AAPIXE`).
  Includes the `DESSINS` family (573 records): `DESSINS` is a
  section header parsed as a surname, not a name, and is never
  corrected.
- **Structural artifact** — `DESSINS` and its garbles, never
  corrected by design.

## Teachers — 7,825 forms / 17,621 records

- **Compound teacher lists** — 14,304 records / 6,174 forms
  (e.g. `MM. Gérôme et Lequien`, `A. Toussaint, Galmels et Munch`).
  These need hand splitting before any surname in them can be
  corrected; they are not single-name corrections.
- **Hyphen-split surnames** — 3,309 records / 1,645 forms
  (e.g. `M. Bogo- luboff`, `De- laroche et de M. L. Gogniet`).
  The surname is split across lines; the token is not whole.
- **Plausible surname** — 8 records / 6 forms (`Brevet`, `Gaudron`,
  `Glaude`, `Goret`, `Grot`, `Touillon`). Real surnames, left alone.
- Teacher values with an address (digits, `rue`, `n°`, `chez`, …) or
  longer than 40 characters were not considered at all — they are
  fragments of the livret's address lines, not names.

## What was deliberately NOT fixed (all fields)

- Titles, mediums, catalogue numbers, birthplaces, notes — out of
  scope for phase 1 (artist names only). Titles are the next phase.
- Years 1673 / 1699 / 1704 (prose records).
- Any name where the correction was not high-confidence. When in
  doubt it was left as printed and listed here.
- `DESSINS` (a section header, not a name) and its garbles.
- Descriptors (`dit …`, `l'aîné`, `le jeune`).
- Honorifics that are unreadable (`M««.`, `M^^.`) — Mme vs Mlle
  cannot be told apart from the OCR alone.
