'use strict';
/*
 * Browse: find artists by century, country, movement or role, through live
 * Wikidata queries. The result is a finding aid only — each artist links
 * into the existing report flow, where works are linked to the holding
 * institution's verified page. Every curated QID was verified against
 * Wikidata (2026-11-16); no identifier here is guessed. Counts of eligible
 * artists per movement were checked the same day (8–703 each).
 *
 * Query shape (two steps, both live): (1) rank the best-documented artists
 * for the facet by sitelinks; (2) fetch their details. Occupation
 * eligibility is the same as search — P106 a subclass of one of the five
 * roots — but the subclass closure is resolved once (a cheap query, cached
 * in-process) and passed as VALUES: the P279* join inside the ranking
 * query times out on Wikidata (tested 2026-11-16), while the VALUES form
 * answers in ~15s for the heaviest facet (19th century).
 *
 * Country is by citizenship (P27), modern country plus the historical
 * states whose artists belong under it: citizenship in Wikidata records
 * the polity of the time — Rembrandt and Vermeer are "Dutch Republic",
 * Van Gogh and Mondrian "Kingdom of the Netherlands", Leonardo
 * "Republic of Florence" — so a modern-country P27 query returns no
 * Dutch masters at all and misses the whole Italian Renaissance. The
 * country query therefore matches P27 against a curated polity list
 * (verified QIDs, see COUNTRIES) with the P279* occupation join: that
 * form answers in ~18–30s for the big countries and finds the masters,
 * where the VALUES occupation form times out for the Kingdom of the
 * Netherlands at every threshold. Birthplace was tried first and ruled
 * out — both the P131* chain and the birthplace-country (P17) forms time
 * out on Wikidata for every country tested.
 */
const { sparqlWD, v, qid, safe, wdYear } = require('./util');
const { ROOTS } = require('./search');

const LANGS = 'en,mul';
const ROOT_VALUES = Object.keys(ROOTS).map((k) => 'wd:' + k).join(' ');

const CENTURIES = [12, 13, 14, 15, 16, 17, 18, 19, 20];
const centuryLabel = (c) => {
  const suffix = c % 10 === 1 && c % 100 !== 11 ? 'st' : c % 10 === 2 && c % 100 !== 12 ? 'nd' : c % 10 === 3 && c % 100 !== 13 ? 'rd' : 'th';
  return `${c}${suffix} century`;
};

// Countries of citizenship (Wikidata QIDs). The value is the modern
// country's QID; `polities` adds the historical states whose artists
// belong under it — citizenship in Wikidata records the polity of the
// time, so without them the Dutch masters (Dutch Republic) and the whole
// Italian Renaissance (Republic of Florence, Papal States, …) would be
// missing. Every QID was verified against Wikidata (2026-11-16).
// Two judgment calls, both checked against real artists' records:
// the Holy Roman Empire sits under Germany AND Italy (Raphael's
// citizenship is the Empire, and Urbino was in it; Dürer's is the Duchy
// of Bavaria, also listed); the Kingdom of Travancore sits under India
// (Raja Ravi Varma's citizenship). Behzad has no citizenship recorded
// at all, so no polity list can find him — he is only in the curated
// homepage index below.
const COUNTRIES = [
  ['Netherlands', 'Q55', ['Q55', 'Q29999', 'Q170072', 'Q188553', 'Q212278', 'Q15864']],
  ['France', 'Q142', ['Q142', 'Q70972']],
  ['Italy', 'Q38', ['Q38', 'Q172579', 'Q148540', 'Q4948', 'Q170174', 'Q153529', 'Q173065', 'Q154849', 'Q165154', 'Q12548']],
  ['Germany', 'Q183', ['Q183', 'Q27306', 'Q43287', 'Q12548', 'Q47261']],
  ['Spain', 'Q29', ['Q29']],
  ['United Kingdom', 'Q145', ['Q145', 'Q179876', 'Q161885']],
  ['United States', 'Q30', ['Q30']],
  ['Austria', 'Q40', ['Q40', 'Q131964', 'Q153136']],
  ['Belgium', 'Q31', ['Q31', 'Q622783', 'Q700283', 'Q15864']],
  ['Russia', 'Q159', ['Q159', 'Q34266', 'Q15180']],
  ['China', 'Q148', ['Q148', 'Q8733', 'Q13426199']],
  ['Japan', 'Q17', ['Q17', 'Q188712']],
  ['India', 'Q668', ['Q668', 'Q129286', 'Q33296', 'Q150058']],
  ['Brazil', 'Q155', ['Q155', 'Q217230']],
  ['Indonesia', 'Q252', ['Q252', 'Q188161']],
  ['Mexico', 'Q96', ['Q96']],
  ['Nigeria', 'Q1033', ['Q1033']],
  ['Iran', 'Q794', ['Q794', 'Q189326', 'Q161205']],
  ['Turkey', 'Q43', ['Q43', 'Q12560']],
  ['Uruguay', 'Q77', ['Q77']],
  ['Switzerland', 'Q39', ['Q39', 'Q435583']],
  ['Denmark', 'Q35', ['Q35']],
  ['Norway', 'Q20', ['Q20', 'Q62651', 'Q62589']],
];
// Movements / schools (Wikidata QIDs).
const MOVEMENTS = [
  ['Q4692', 'Renaissance'], ['Q37853', 'Baroque'], ['Q131808', 'Mannerism'],
  ['Q610877', 'Northern Renaissance'], ['Q122960', 'Rococo'], ['Q14378', 'Neoclassicism'],
  ['Q37068', 'Romanticism'], ['Q10857409', 'Realism'], ['Q184814', 'Pre-Raphaelite Brotherhood'],
  ['Q40415', 'Impressionism'], ['Q166713', 'Post-Impressionism'], ['Q164800', 'Symbolism'],
  ['Q34636', 'Art Nouveau'], ['Q80113', 'Expressionism'], ['Q42934', 'Cubism'],
  ['Q131221', 'Futurism'], ['Q6034', 'Dada'], ['Q39427', 'Surrealism'],
  ['Q207103', 'Constructivism'], ['Q134147', 'Pop art'],
];
// Roles — the same five occupation roots as search (ROOTS in search.js).
const ROLES = [
  ['Q1028181', 'Painters'], ['Q1281618', 'Sculptors'], ['Q15296811', 'Draftspeople'],
  ['Q329439', 'Engravers'], ['Q11569986', 'Printmakers'],
];

const FACETS = [
  { id: 'century', label: 'By century', values: CENTURIES.map((c) => ({ id: String(c), label: centuryLabel(c) })) },
  { id: 'country', label: 'By country', values: COUNTRIES.map(([label, id]) => ({ id, label })) },
  { id: 'movement', label: 'By movement', values: MOVEMENTS.map(([id, label]) => ({ id, label })) },
  { id: 'role', label: 'By medium', values: ROLES.map(([id, label]) => ({ id, label })) },
];

function bad(msg) {
  throw Object.assign(new Error(msg), { status: 400 });
}

// Occupation subclasses per root (P279* closure), resolved once per process.
let occCache = null;
async function occValues() {
  if (occCache) return occCache;
  const rows = await sparqlWD(`SELECT ?root ?o WHERE {
    VALUES ?root { ${ROOT_VALUES} }
    ?o wdt:P279* ?root .
  }`);
  const map = {};
  for (const b of rows) {
    const root = qid(v(b, 'root'));
    (map[root] ||= new Set()).add(qid(v(b, 'o')));
  }
  occCache = map;
  return map;
}

function facetFilter(facet, value) {
  if (facet === 'century') {
    const c = parseInt(value, 10);
    const from = `${(c - 1) * 100 + 1}-01-01T00:00:00Z`;
    const to = `${c * 100 + 1}-01-01T00:00:00Z`;
    return `?p wdt:P569 ?bt . FILTER(?bt >= "${from}"^^xsd:dateTime && ?bt < "${to}"^^xsd:dateTime)`;
  }
  if (facet === 'movement') return `?p wdt:P135 wd:${value} .`;
  // role: the occupation VALUES list is already restricted to this root's
  // subclasses, so no extra pattern is needed. country: see rankArtists —
  // it uses its own query shape (P279* join, polity list).
  return '';
}

// Ranking query shapes, tuned per facet against Wikidata (2026-11-16):
// - ORDER BY sitelinks in SPARQL is fast when the joined set is small
//   (century, movement, role) but times out for country, where the set is
//   huge — country uses per-polity thresholded windows and sorts in JS
//   (see rankArtists).
// - threshold: only artists with at least that many sitelinks are ranked.
//   A second pass at a lower threshold fills up thin facets.
// - limit: rows returned; several rows per artist (one per occupation), so
//   200 rows yield ~50–80 distinct artists.
const RANK = {
  century: [{ threshold: null, limit: 200, order: true }],
  movement: [{ threshold: null, limit: 200, order: true }],
  role: [
    { threshold: 40, limit: 200, order: true },
    { threshold: 10, limit: 200, order: true },
  ],
};

async function rankArtists(facet, value, occList) {
  // Country uses its own shape: citizenship (P27) over the country's
  // historical polities, with the P279* occupation join, one query PER
  // polity run in parallel and merged in JS. A single query over the
  // whole polity list returns an arbitrary 500-row window that can
  // crowd out a whole polity (the Holy Roman Empire's set hid Dürer,
  // Raphael and Hildegard from Germany, 2026-11-16); per-polity windows
  // are small and complete (HRE: 29 artists, Bavaria: 1). The VALUES
  // occupation form that works for century/movement/role times out for
  // the big polities (Kingdom of the Netherlands failed at every
  // threshold); the P279* form answers in ~1–30s per polity and finds
  // the masters. A polity query that fails is recorded in `errors` and
  // the rest still merge, so one slow polity cannot sink the list.
  if (facet === 'country') {
    const polities = (COUNTRIES.find(([, id]) => id === value) || [])[2] || [value];
    const settled = await Promise.allSettled(
      polities.map((p) =>
        safe('Wikidata', () =>
          sparqlWD(
            `SELECT ?p ?links WHERE {
              VALUES ?root { ${ROOT_VALUES} }
              ?p wdt:P27 wd:${p} .
              ?p wdt:P106 ?o . ?o wdt:P279* ?root .
              ?p wikibase:sitelinks ?links . FILTER(?links >= 20)
            } LIMIT 500`,
            { timeout: 55000 }
          )
        )
      )
    );
    const linksByQ = new Map();
    const errors = [];
    for (const s of settled) {
      if (s.status === 'fulfilled' && s.value.ok) {
        for (const b of s.value.data || []) {
          const id = qid(v(b, 'p'));
          if (!linksByQ.has(id)) linksByQ.set(id, parseInt(v(b, 'links') || '0', 10));
        }
      } else {
        errors.push(s.status === 'fulfilled' ? s.value.error : String(s.reason));
      }
    }
    const ranked = [...linksByQ.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
    return { ok: true, ranked, linksByQ, errors };
  }
  for (const cfg of RANK[facet]) {
    const thresh = cfg.threshold != null ? `FILTER(?links >= ${cfg.threshold})` : '';
    const order = cfg.order ? 'ORDER BY DESC(?links)' : '';
    const q = `SELECT ?p ?links WHERE {
      VALUES ?o { ${occList.join(' ')} }
      ${facetFilter(facet, value)}
      ?p wdt:P106 ?o .
      ?p wikibase:sitelinks ?links . ${thresh}
    } ${order} LIMIT ${cfg.limit}`;
    const r = await safe('Wikidata', () => sparqlWD(q, { timeout: 55000 }));
    if (!r.ok) return { ok: false, error: r.error };
    const linksByQ = new Map();
    for (const b of r.data || []) {
      const id = qid(v(b, 'p'));
      if (!linksByQ.has(id)) linksByQ.set(id, parseInt(v(b, 'links') || '0', 10));
    }
    const ranked = [...linksByQ.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
    if (ranked.length >= 50 || cfg === RANK[facet][RANK[facet].length - 1]) return { ok: true, ranked, linksByQ };
  }
  return { ok: true, ranked: [], linksByQ: new Map() };
}

/**
 * browse({facet, value})
 * No params -> {facets: [...]}. With facet+value -> {facet, value, label,
 * artists: [...up to 50...], errors: []}. Every artist passes the same
 * occupation eligibility as search (P106 a subclass of a search root).
 */
async function browse({ facet, value }) {
  if (!facet && !value) return { facets: FACETS };
  if (!facet || !value) bad('Browse needs both a facet and a value.');
  const f = FACETS.find((x) => x.id === facet);
  if (!f) bad(`Unknown facet: ${facet}`);
  const val = f.values.find((x) => x.id === value);
  if (!val) bad(`Unknown value for ${facet}: ${value}`);

  // Occupation subclasses are needed to show each card's roles (and, for
  // non-country facets, to rank). Country ranks by its own P279* query.
  const occ = await safe('Wikidata', occValues);
  if (!occ.ok) return { facet, value, label: val.label, artists: [], errors: [occ.error] };
  const occList =
    facet === 'role'
      ? [...(occ.data[value] || [])].map((q) => 'wd:' + q)
      : [...new Set(Object.values(occ.data).flatMap((s) => [...s]))].map((q) => 'wd:' + q);
  const allowedOcc = new Set(occList.map((s) => s.slice(3)));

  // Step 1: rank the best-documented artists for this facet by sitelinks.
  const r1 = await rankArtists(facet, value, occList);
  if (!r1.ok) return { facet, value, label: val.label, artists: [], errors: [r1.error] };
  const { ranked, linksByQ } = r1;
  const rankErrors = r1.errors || [];
  const topIds = ranked.slice(0, 50);
  if (!topIds.length) return { facet, value, label: val.label, artists: [], errors: rankErrors };

  // Step 2: details for the top 50 (same VALUES + OPTIONAL pattern as search).
  const r2 = await safe('Wikidata', () =>
    sparqlWD(`SELECT ?p ?pLabel ?b ?d ?bplLabel ?ulan ?img ?links ?o ?oLabel WHERE {
      VALUES ?p { ${topIds.map((id) => 'wd:' + id).join(' ')} }
      OPTIONAL { ?p p:P569/psv:P569 [ wikibase:timeValue ?b ] }
      OPTIONAL { ?p p:P570/psv:P570 [ wikibase:timeValue ?d ] }
      OPTIONAL { ?p wdt:P19 ?bpl }
      OPTIONAL { ?p wdt:P245 ?ulan }
      OPTIONAL { ?p wdt:P18 ?img }
      OPTIONAL { ?p wikibase:sitelinks ?links }
      OPTIONAL { ?p wdt:P106 ?o }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". }
    }`)
  );
  if (!r2.ok) return { facet, value, label: val.label, artists: [], errors: [r2.error] };

  const byQ = {};
  for (const b of r2.data || []) {
    const id = qid(v(b, 'p'));
    let a = byQ[id];
    if (!a) {
      const bp = v(b, 'bplLabel');
      a = byQ[id] = {
        id,
        name: v(b, 'pLabel'),
        birthYear: wdYear(v(b, 'b')),
        deathYear: wdYear(v(b, 'd')),
        birthPlace: bp && !/^https?:/.test(bp) ? bp : null,
        roles: new Set(),
        image: v(b, 'img') ? v(b, 'img').replace(/^http:/, 'https:') + '?width=160' : null,
        ulan: v(b, 'ulan') || null,
        sitelinks: linksByQ.get(id) || parseInt(v(b, 'links') || '0', 10),
      };
    }
    // Show only the occupations that make the artist eligible here.
    if (v(b, 'o') && allowedOcc.has(qid(v(b, 'o'))) && v(b, 'oLabel')) a.roles.add(v(b, 'oLabel'));
    if (!a.ulan && v(b, 'ulan')) a.ulan = v(b, 'ulan');
  }
  const artists = topIds
    .map((id) => byQ[id])
    .filter(Boolean)
    .map((a) => ({ ...a, roles: [...a.roles].filter((x) => x && !/old master/i.test(x)) }));
  // Best-documented first; ties broken by birth year (earliest first),
  // as the browse page states.
  artists.sort((a, b) => b.sitelinks - a.sitelinks || (a.birthYear ?? 9999) - (b.birthYear ?? 9999));
  return { facet, value, label: val.label, artists, errors: rankErrors };
}

module.exports = { browse, FACETS };
