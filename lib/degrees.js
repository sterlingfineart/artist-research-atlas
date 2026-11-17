'use strict';
/*
 * Six Degrees: the shortest chain between two artists through recorded
 * teacher/pupil/influence links — Wikidata P802 (student, i.e. taught),
 * P1066 (student of, i.e. taught by) and P737 (influenced by, in both
 * directions). Breadth-first search to depth 6, one SPARQL query per
 * level for the whole frontier (VALUES), neighbor sets cached in-process
 * per QID. A chain exists only where Wikidata records the link: when
 * none is found within six steps the answer is an honest found:false,
 * never a fabricated link.
 *
 * Edge labels are from the perspective of the path direction, e.g.
 * Rembrandt —taught→ Fabritius —influenced→ Vermeer: the second edge
 * means Fabritius influenced Vermeer (Vermeer was influenced by him).
 * The graph is small — the best-connected artists have a few dozen
 * recorded links — so the caps below are safety valves, not the norm.
 */
const { sparqlWD, v, qid, wdYear } = require('./util');

const MAX_DEPTH = 6;
const MAX_EXPANDED = 300; // total artists expanded per search
const MAX_FRONTIER = 120; // max frontier per level, best-documented first
const MAX_SEARCH_CACHE = 200;
const REL_ORDER = { taught: 0, 'was taught by': 1, 'was influenced by': 2, influenced: 3 };

// Neighbor sets, cached in-process per QID (SPARQL responses are also
// cached by lib/util for 6h, so repeat searches are cheap either way).
const neighborCache = new Map();
// Completed searches, keyed "from|to", so a repeat search is instant.
const searchCache = new Map();

function bad(msg) {
  throw Object.assign(new Error(msg), { status: 400 });
}

// Neighbors of a set of artists, in one batched query: taught, taught by,
// influenced by, and influenced (other artists who list this artist as an
// influence). Only people with an English label are kept — the human check
// is a separate batched VALUES query (filterHumans), because joining P31
// inside this UNION times WDQS out (tested 2026-11-16: 65s, HTTP 504,
// while the query without it answers in ~1s).
async function fetchNeighbors(qids) {
  const missing = qids.filter((q) => !neighborCache.has(q));
  if (missing.length) {
    const rows = await sparqlWD(
      `SELECT ?a ?rel ?n ?nLabel ?b ?d ?links WHERE {
        VALUES ?a { ${missing.map((q) => 'wd:' + q).join(' ')} }
        { ?a wdt:P802 ?n . BIND("taught" AS ?rel) }
        UNION { ?a wdt:P1066 ?n . BIND("was taught by" AS ?rel) }
        UNION { ?a wdt:P737 ?n . BIND("was influenced by" AS ?rel) }
        UNION { ?n wdt:P737 ?a . BIND("influenced" AS ?rel) }
        OPTIONAL { ?n p:P569/psv:P569 [ wikibase:timeValue ?b ] }
        OPTIONAL { ?n p:P570/psv:P570 [ wikibase:timeValue ?d ] }
        OPTIONAL { ?n wikibase:sitelinks ?links }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
      }`,
      { timeout: 55000 }
    );
    const byQ = new Map(missing.map((q) => [q, []]));
    const seen = new Set();
    for (const b of rows) {
      const a = qid(v(b, 'a'));
      const n = qid(v(b, 'n'));
      const label = v(b, 'nLabel');
      const rel = v(b, 'rel');
      if (!a || !n || !label || !rel || /^https?:/.test(label)) continue;
      const key = a + '|' + rel + '|' + n;
      if (seen.has(key)) continue;
      seen.add(key);
      byQ.get(a).push({
        qid: n,
        label,
        rel,
        born: wdYear(v(b, 'b')),
        died: wdYear(v(b, 'd')),
        links: parseInt(v(b, 'links') || '0', 10),
      });
    }
    // Keep people only: P737 also points at groups, schools and works
    // (Art & Language, the Leonardeschi, a treatise) that must never
    // appear as a link in a chain. A VALUES-bound P31 check answers in
    // under a second even for hundreds of QIDs; neighbors with no P31
    // statement at all are dropped too — a chain link must be verifiably
    // a person.
    const all = [...new Set([...byQ.values()].flatMap((l) => l.map((x) => x.qid)))];
    const humans = await filterHumans(all);
    for (const [q, list] of byQ) {
      const kept = list.filter((x) => humans.has(x.qid));
      // Deterministic order: teacher links before influence links, then
      // best-documented, then QID — so a search is reproducible.
      kept.sort((x, y) => REL_ORDER[x.rel] - REL_ORDER[y.rel] || y.links - x.links || (x.qid < y.qid ? -1 : 1));
      neighborCache.set(q, kept);
    }
  }
  const out = new Map();
  for (const q of qids) out.set(q, neighborCache.get(q) || []);
  return out;
}

// The QIDs in `qids` that are instance of human (P31 Q5), via VALUES-bound
// queries — fast, unlike joining P31 inside the neighbor UNION. Chunked
// (200 QIDs per query) because a single VALUES list of thousands of QIDs
// makes the request URI too long for WDQS (HTTP 431, 2026-11-16).
async function filterHumans(qids) {
  if (!qids.length) return new Set();
  const chunks = [];
  for (let i = 0; i < qids.length; i += 200) chunks.push(qids.slice(i, i + 200));
  const sets = await Promise.all(
    chunks.map(async (ch) => {
      const rows = await sparqlWD(
        `SELECT ?n WHERE { VALUES ?n { ${ch.map((q) => 'wd:' + q).join(' ')} } ?n wdt:P31 wd:Q5 . }`,
        { timeout: 25000 }
      );
      return new Set(rows.map((b) => qid(v(b, 'n'))).filter(Boolean));
    })
  );
  return new Set(sets.flatMap((s) => [...s]));
}

// Labels and life years for the two endpoints.
async function fetchDetails(qids) {
  const rows = await sparqlWD(
    `SELECT ?a ?aLabel ?b ?d WHERE {
      VALUES ?a { ${qids.map((q) => 'wd:' + q).join(' ')} }
      OPTIONAL { ?a p:P569/psv:P569 [ wikibase:timeValue ?b ] }
      OPTIONAL { ?a p:P570/psv:P570 [ wikibase:timeValue ?d ] }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }`,
    { timeout: 25000 }
  );
  const out = {};
  for (const b of rows) {
    const id = qid(v(b, 'a'));
    if (!id) continue;
    out[id] = { qid: id, label: v(b, 'aLabel'), born: wdYear(v(b, 'b')), died: wdYear(v(b, 'd')) };
  }
  return out;
}

/**
 * degrees(from, to) — shortest recorded chain, up to 6 steps.
 * Returns { from, to, fromLabel, toLabel, found, steps, path, explored, ms }
 * where path is [{ qid, label, born, died, edge }] and edge is the link
 * from the previous node (null for the first). found:false carries
 * steps:null, path:[] and the explored count — an honest no-path answer.
 */
async function degrees(from, to) {
  const t0 = Date.now();
  if (!/^Q\d+$/.test(from || '')) bad('degrees needs a from artist (Wikidata QID).');
  if (!/^Q\d+$/.test(to || '')) bad('degrees needs a to artist (Wikidata QID).');
  const key = from + '|' + to;
  if (searchCache.has(key)) return { ...searchCache.get(key), ms: Date.now() - t0, cached: true };
  const details = await fetchDetails([from, to]);
  const fromNode = details[from] || { qid: from, label: from, born: null, died: null };
  const toNode = details[to] || { qid: to, label: to, born: null, died: null };
  const done = (result) => {
    const out = { from, to, fromLabel: fromNode.label, toLabel: toNode.label, ...result, ms: Date.now() - t0 };
    if (searchCache.size > MAX_SEARCH_CACHE) searchCache.delete(searchCache.keys().next().value);
    searchCache.set(key, out);
    return out;
  };
  if (from === to) return done({ found: true, steps: 0, path: [{ ...fromNode, edge: null }], explored: 1 });

  // BFS: visited maps qid -> { prev, edge, node } for reconstruction.
  const visited = new Map([[from, { prev: null, edge: null, node: fromNode }]]);
  let frontier = [from];
  let expanded = 0;
  for (let depth = 1; depth <= MAX_DEPTH; depth++) {
    const byQ = await fetchNeighbors(frontier);
    expanded += frontier.length;
    const next = [];
    const nextSeen = new Set();
    for (const q of frontier) {
      for (const nb of byQ.get(q) || []) {
        if (visited.has(nb.qid)) continue;
        visited.set(nb.qid, { prev: q, edge: nb.rel, node: { qid: nb.qid, label: nb.label, born: nb.born, died: nb.died } });
        if (nb.qid === to) {
          const path = [];
          let cur = to;
          while (cur) {
            const rec = visited.get(cur);
            path.unshift({ ...rec.node, edge: rec.edge });
            cur = rec.prev;
          }
          return done({ found: true, steps: path.length - 1, path, explored: visited.size });
        }
        if (!nextSeen.has(nb.qid)) {
          nextSeen.add(nb.qid);
          next.push({ qid: nb.qid, links: nb.links });
        }
      }
    }
    if (!next.length || expanded >= MAX_EXPANDED) break;
    // Best-documented first, capped, so a search stays bounded.
    next.sort((a, b) => b.links - a.links || (a.qid < b.qid ? -1 : 1));
    frontier = next.slice(0, MAX_FRONTIER).map((x) => x.qid);
  }
  return done({ found: false, steps: null, path: [], explored: visited.size });
}

module.exports = { degrees };
