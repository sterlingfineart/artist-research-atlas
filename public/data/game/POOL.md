# Who Painted It? — how the picture pool was built

The pool (`pool.json`, generated 2026-11-21) holds **283 works** by **149 artists**,
every one of them an open-access museum picture. It was built by
`scripts/build-game-pool.py`, which can be re-run to rebuild it.

## Sources — open access only

| Museum | Works | How obtained |
|---|---|---|
| The Metropolitan Museum of Art | 160 | Collection API; only objects flagged `isPublicDomain` with an image |
| Art Institute of Chicago | 80 | The museum's official public data dump (the same records its API serves); only `is_public_domain` works with an image |
| The Cleveland Museum of Art | 43 | Open Access API; only CC0 works with an image |

Two access notes, for honesty. The Met retired its v1 search endpoint on
2026-10-01, so the build uses the v1.1 search. And the Art Institute's live
API and image CDN refuse direct requests from the build server's network
(a bot wall), which is why the AIC records come from the museum's own
published data dump instead — identical records, bulk form. AIC image
addresses are the museum's canonical IIIF URLs, built from each record's
own image ID exactly as the AIC API prescribes.

## Attribution — the museum record, and nothing else

No image was ever attached to an artist or title by inference. Each pool
record's artist, title, date, museum, object-page URL and image URL are
copied from the holding museum's own record for that exact object.

On top of that, artist matching is deliberately strict:

- Records whose museum attribution carries a qualifier — *after,
  attributed to, follower of, circle of, workshop of, manner of, school
  of, studio of, unknown, anonymous* — are rejected outright.
- A museum name string must firmly name one roster artist. Full names
  match as token sets; a bare surname matches only when the record
  carries no other personal name. (This rule exists because a looser one
  mis-filed David Lucas's engravings under Jacques-Louis David, and Jan
  Peeters's drawings under Clara Peeters. Both errors were caught in
  review and the matcher fixed before the pool was finalised.)
- Only paintings, prints and drawings are used — no sculpture, no
  decorative objects. Records whose "title" is only a date range are
  dropped. Near-duplicate titles for the same artist (the same work or
  print impression catalogued slightly differently at two museums) are
  merged, preferring Met, then AIC, then Cleveland.
- At most 6 works per artist enter the pool.

## Levels — curatorial, by fame

Levels were assigned in three steps:

1. **A hand-built canonical list** (~60 patterns: artist + distinctive
   title fragment + level, sometimes pinned to one museum) places the
   textbook pictures at levels 1–3 — *A Sunday on La Grande Jatte*,
   *Paris Street; Rainy Day*, *The Card Players*, the *Great Wave*,
   *View of Toledo*, *Melencolia I*, *The Sleep of Reason*, and so on.
   Canonical works the per-artist harvest missed were rescued with a
   title search of the Met API, under the same public-domain and
   attribution rules.
2. **Everything else is banded by the artist's fame tier.** A curated
   roster of 198 artists carries a tier (1 = household name … 4 =
   specialist name); a work's level is drawn from its artist's band —
   tier 1: levels 3–5, tier 2: 4–6, tier 3: 6–8, tier 4: 8–10 — chosen
   deterministically from the work's title, with a one-level easement
   for works the Met flags as collection highlights. Levels are never
   filled by dragging arbitrary works into them: levels 1–3 hold
   canonical works only.
3. **A trim** caps each level (40 works at levels 1–3, 30 at levels
   4–10, at most 3 per artist per level), keeping canonical and
   highlight works first.

Per-level counts: **L1: 9 · L2: 30 · L3: 38 · L4: 30 · L5: 30 ·
L6: 29 · L7: 30 · L8: 29 · L9: 29 · L10: 29.**

Level 1 is small on purpose. The very top tier of icons that are also
open access at these three museums is genuinely short — and some famous
pictures fail the museums' own flags: the Met flags Monet's *Bridge over
a Pond of Water Lilies* as **not** public domain and serves no image for
it, so it cannot be used, while *The Starry Night*, *The Kiss* and *The
Night Watch* hang in museums outside this pool's sources. Nine honest
icons were preferred to a padded level. A few other wished-for works
could not be retrieved as public-domain records at all (among them
Vermeer's *Allegory of Faith* and Hiroshige's *Plum Park at Kameido*).

Works span the 15th to the 20th century and 26 movements. The roster's
metadata (era, movement, nationality, and a hand-defined "circle" — 20
circles in all) drives the wrong answers: at levels 1–2 the distractors
come from eras at least two centuries away; in the middle levels from
the same broad period or movement; at levels 9–10 from the artist's own
circle (for Monet: Sisley, Pissarro, Renoir).

## Image verification

Every Met and Cleveland image URL was requested during the build; any
that failed to load was dropped (exactly one record was lost this way).
AIC images cannot be requested from the build server (the bot wall
above), so they were verified through an independent fetching service:
**80 AIC images were confirmed live**, most of them in a final pass on
2026-11-21. Fourteen more AIC records passed every other test but their
images could not be confirmed (the fetching service was intermittently
rate-limited). Rather than carry unverified pictures, those fourteen
records were **removed from the pool on 2026-11-21** — the pool is
verified-only. The removed works were Dürer's *Melencolia I*, Monet's
*Arrival of the Normandy Train* and *Stacks of Wheat (End of Day,
Autumn)*, Toulouse-Lautrec's *At the Moulin Rouge: the Franco-Russian
Alliance*, three Rembrandt self-portrait etchings, Homer's *The Herring
Net*, Turner's *Aesacus and Hesperie*, Ingres's *Charles Gounod*,
Altdorfer's *Altarpiece with the Beautiful Virgin of Regensburg*,
Hassam's *Against the Light*, Cabanel's *Central Figure, study for The
Life of Saint Louis*, and a Salvator Rosa *Warrior* from the Figurine
series. The game in any case skips and re-rolls any picture that fails
to load for a visitor, so a dead image can never stall a round.

Object-page links were spot-checked live for all three museums during
testing (Cleveland and AIC pages resolve and match the pool records
exactly; the Met's object URLs are the canonical addresses its API
returns for each object — the museum's website rate-limits automated
checks from the build network, so those were verified by construction
rather than by fetching).

## Scoring (for reference)

Correct answer: **level × 100 points**, plus a streak bonus of
**50 × (streak − 1)**, capped at 250, from the second consecutive right
answer on. A perfect ladder (levels 1–10, all right, streak unbroken)
scores **7,250**. Ranks: Gallery Visitor (0) · Art Lover (1,000) ·
Docent (2,200) · Connoisseur (3,400) · Curator (4,600) · Chief Curator
(5,800). Scores live only for the session.
