'use strict';
/*
 * Candidate search: given a name, return real artists (painters, sculptors,
 * draftsmen, engravers/printmakers) whose preferred name or a variant matches,
 * with life dates and birthplace. Sources: Wikidata + Getty ULAN.
 */
const { getJSON, qs, sparqlWD, sparqlGetty, v, qid, safe, norm, wdDate, wdYear, uniqBy, sparqlStr } = require('./util');

// Wikidata occupation roots (subclasses are matched via P279*)
const ROOTS = {
  Q1028181: 'painter',
  Q1281618: 'sculptor',
  Q15296811: 'draftsperson',
  Q329439: 'engraver',
  Q11569986: 'printmaker',
};
const ROOT_VALUES = Object.keys(ROOTS).map((k) => 'wd:' + k).join(' ');
const ULAN_ROLE_RX =
  /paint|sculpt|draftsm|draughtsm|drafts|engrav|printmak|etcher|miniaturist|watercolo|medal(l)?ist|carver|woodcut/i;
const LANGS = 'en,mul,fr,de,it,nl,es,pt,sv,da,pl,ru,ja,zh';

/* A slow Getty ULAN must never hold up a name search (John approved this
 * design Nov 17, 2026): Getty calls in the search path get a hard 5-second
 * cap. If Getty answers in time, its candidates enrich the results exactly
 * as before; if it stalls, the search returns the Wikidata candidates and
 * the errors list carries an honest note. The underlying request is left to
 * finish in the background — a late success still lands in the getJSON cache,
 * so a reload can pick it up. */
const GETTY_CAP_MS = 5000;
function withCap(promise, ms, label) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(
      () => reject(new Error(`${label} did not respond within ${Math.round(ms / 1000)} seconds`)),
      ms
    );
    promise.then(
      (val) => { clearTimeout(t); resolve(val); },
      (err) => { clearTimeout(t); reject(err); }
    );
  });
}

async function wdTextSearch(text, limit = 50) {
  const url =
    'https://www.wikidata.org/w/api.php?' +
    qs({ action: 'query', list: 'search', srsearch: text, srlimit: String(limit), srnamespace: '0', format: 'json' });
  const d = await getJSON(url, { timeout: 15000 });
  return (d.query?.search || []).map((x) => x.title).filter((t) => /^Q\d+$/.test(t));
}

function cleanName(q) {
  return String(q || '')
    .replace(/["“”'’`*?~^:\\/(){}\[\]!|&+=<>-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120);
}

/** Getty ULAN full-text search, restricted to artist roles. */
async function ulanSearch(name) {
  const terms = name.split(' ').filter((t) => t.length > 0);
  if (!terms.length) return [];
  const luc = terms.map((t) => (t.length > 2 ? t + '*' : t)).join(' AND ');
  const q = `
SELECT ?s ?id ?name ?desc ?start ?end ?bpName ?bpParent ?dpName ?dpParent WHERE {
  ?s a gvp:PersonConcept; luc:term ${sparqlStr(luc)}; dc:identifier ?id;
     gvp:prefLabelGVP/xl:literalForm ?name; foaf:focus/gvp:biographyPreferred ?bio .
  ?bio schema:description ?desc .
  FILTER(regex(?desc, "paint|sculpt|draftsm|draughtsm|engrav|printmak|etcher|miniaturist|watercolo|medal", "i"))
  OPTIONAL { ?bio gvp:estStart ?start }
  OPTIONAL { ?bio gvp:estEnd ?end }
  OPTIONAL { ?bio schema:birthPlace ?bpf . ?bpc foaf:focus ?bpf; gvp:prefLabelGVP/xl:literalForm ?bpName . OPTIONAL { ?bpc gvp:parentString ?bpParent } }
  OPTIONAL { ?bio schema:deathPlace ?dpf . ?dpc foaf:focus ?dpf; gvp:prefLabelGVP/xl:literalForm ?dpName . OPTIONAL { ?dpc gvp:parentString ?dpParent } }
} LIMIT 60`;
  const rows = await sparqlGetty(q);
  const yr = (val, desc) => {
    if (!val) return null;
    const n = parseInt(val, 10);
    if (!Number.isFinite(n) || n > new Date().getFullYear()) return null;
    return String(desc || '').includes(String(Math.abs(n))) ? n : null; // only trust years ULAN actually states
  };
  return uniqBy(
    rows.map((b) => ({
      ulan: v(b, 'id'),
      name: v(b, 'name'),
      desc: (v(b, 'desc') || '').trim(),
      start: yr(v(b, 'start'), v(b, 'desc')),
      end: yr(v(b, 'end'), v(b, 'desc')),
      birthPlace: placeWithParent(v(b, 'bpName'), v(b, 'bpParent')),
      deathPlace: placeWithParent(v(b, 'dpName'), v(b, 'dpParent')),
    })),
    (x) => x.ulan
  );
}

function placeWithParent(name, parent) {
  if (!name) return null;
  if (!parent) return name;
  const parts = parent.split(',').map((s) => s.trim()).filter((p) => !/^(World|Europe|Asia|Africa|North and Central America|South America|Oceania)$/i.test(p));
  const country = parts.slice(-1)[0];
  return country && country !== name ? `${name}, ${country}` : name;
}

async function ulanVariants(ids) {
  if (!ids.length) return {};
  const q = `SELECT ?id ?l WHERE { VALUES ?id { ${ids.map(sparqlStr).join(' ')} } ?s dc:identifier ?id; a gvp:PersonConcept; xl:altLabel/xl:literalForm ?l . }`;
  const rows = await sparqlGetty(q);
  const out = {};
  for (const b of rows) (out[v(b, 'id')] ||= []).push(v(b, 'l'));
  return out;
}

/** Normalise ULAN "Rijn, Rembrandt van" → "Rembrandt van Rijn" for display/matching. */
function invertName(n) {
  const m = String(n || '').match(/^([^,]+),\s*([^,]+)$/);
  return m ? `${m[2]} ${m[1]}` : n;
}

function matchInfo(query, names) {
  const nq = norm(query);
  const tokens = nq.split(' ').filter(Boolean);
  let best = { type: 'partial', name: names[0] };
  for (const n of names) {
    const nn = norm(n);
    const ni = norm(invertName(n));
    if (nn === nq || ni === nq) return { type: 'exact', name: n };
    const words = new Set([...nn.split(' '), ...ni.split(' ')]);
    if (tokens.every((t) => words.has(t))) {
      if (n === names[0]) best = { type: 'all', name: n };
      else if (best.type === 'partial') best = { type: 'variant', name: n };
    }
  }
  if (best.type === 'partial') {
    const n = names.find((x) => tokens.some((t) => norm(x).split(' ').includes(t)));
    if (n) best.name = n;
  }
  return best;
}

async function search(rawQuery) {
  const name = cleanName(rawQuery);
  if (name.length < 2) return { query: rawQuery, candidates: [], errors: [] };
  const occFilter = 'haswbstatement:' + Object.keys(ROOTS).map((k) => 'P106=' + k).join('|');

  const [wdOcc, wdUlan, wdHuman, ulan] = await Promise.all([
    safe('Wikidata search', () => wdTextSearch(`${name} ${occFilter}`)),
    safe('Wikidata search', () => wdTextSearch(`${name} haswbstatement:P245`)),
    safe('Wikidata search', () => wdTextSearch(`${name} haswbstatement:P31=Q5`)),
    safe('Getty ULAN', () => withCap(ulanSearch(name), GETTY_CAP_MS, 'Getty ULAN')),
  ]);
  const errors = [wdOcc, wdUlan, wdHuman, ulan].filter((r) => !r.ok).map((r) => r.error);
  const ulanRecs = ulan.ok ? ulan.data : [];
  const searchIds = [...new Set([...(wdOcc.data || []), ...(wdUlan.data || []), ...(wdHuman.data || [])])].slice(0, 140);

  // Map ULAN ids → Wikidata
  let ulanToQ = {};
  if (ulanRecs.length) {
    const r = await safe('Wikidata', () =>
      sparqlWD(`SELECT ?p ?u WHERE { VALUES ?u { ${ulanRecs.map((x) => sparqlStr(x.ulan)).join(' ')} } ?p wdt:P245 ?u }`)
    );
    if (r.ok) for (const b of r.data) ulanToQ[v(b, 'u')] = qid(v(b, 'p'));
    else errors.push(r.error);
  }
  const allIds = [...new Set([...searchIds, ...Object.values(ulanToQ)])];
  const values = allIds.map((q) => 'wd:' + q).join(' ');

  let occByQ = {};
  let core = [];
  let alias = [];
  if (allIds.length) {
    const [occ, coreR, aliasR] = await Promise.all([
      safe('Wikidata', () =>
        sparqlWD(`SELECT ?p ?root ?oLabel WHERE { VALUES ?p { ${values} } VALUES ?root { ${ROOT_VALUES} }
          ?p wdt:P106 ?o . ?o wdt:P279* ?root .
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en,mul". } }`)
      ),
      safe('Wikidata', () =>
        sparqlWD(`SELECT ?p ?pLabel ?pDescription ?b ?bp ?d ?dp ?bplLabel ?bplcLabel ?dplLabel ?dplcLabel ?ulan ?img ?links ?cLabel WHERE {
          VALUES ?p { ${values} }
          OPTIONAL { ?p p:P569/psv:P569 [ wikibase:timeValue ?b; wikibase:timePrecision ?bp ] }
          OPTIONAL { ?p p:P570/psv:P570 [ wikibase:timeValue ?d; wikibase:timePrecision ?dp ] }
          OPTIONAL { ?p wdt:P19 ?bpl . OPTIONAL { ?bpl wdt:P17 ?bplc } }
          OPTIONAL { ?p wdt:P20 ?dpl . OPTIONAL { ?dpl wdt:P17 ?dplc } }
          OPTIONAL { ?p wdt:P245 ?ulan } OPTIONAL { ?p wdt:P18 ?img } OPTIONAL { ?p wikibase:sitelinks ?links }
          OPTIONAL { ?p wdt:P27 ?c }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } }`)
      ),
      safe('Wikidata', () =>
        sparqlWD(`SELECT ?p ?a WHERE { VALUES ?p { ${values} }
          { ?p skos:altLabel ?a } UNION { ?p rdfs:label ?a } UNION { ?p wdt:P1477|wdt:P742|wdt:P1559|wdt:P1449 ?a }
          FILTER(lang(?a) IN ("en","mul","fr","de","it","nl","es","pt","") ) }`)
      ),
    ]);
    for (const r of [occ, coreR, aliasR]) if (!r.ok) errors.push(r.error);
    for (const b of occ.data || []) {
      const q = qid(v(b, 'p'));
      (occByQ[q] ||= new Set()).add(v(b, 'oLabel'));
    }
    core = coreR.data || [];
    alias = aliasR.data || [];
  }

  const ulanById = Object.fromEntries(ulanRecs.map((u) => [u.ulan, u]));
  const ulanLinkedQs = new Set(Object.values(ulanToQ));
  const aliasByQ = {};
  for (const b of alias) (aliasByQ[qid(v(b, 'p'))] ||= new Set()).add(v(b, 'a'));

  // Build Wikidata candidates
  const byQ = {};
  for (const b of core) {
    const q = qid(v(b, 'p'));
    const uid = v(b, 'ulan');
    const eligible = occByQ[q] || (uid && ulanById[uid]) || ulanLinkedQs.has(q);
    if (!eligible) continue;
    let c = byQ[q];
    if (!c) {
      c = byQ[q] = {
        id: q,
        wikidata: q,
        ulan: uid || null,
        name: v(b, 'pLabel'),
        description: v(b, 'pDescription') || '',
        birth: wdDate(v(b, 'b'), v(b, 'bp')),
        death: wdDate(v(b, 'd'), v(b, 'dp')),
        floruit: null,
        birthYear: wdYear(v(b, 'b')),
        deathYear: wdYear(v(b, 'd')),
        birthPlace: joinPlace(v(b, 'bplLabel'), v(b, 'bplcLabel')),
        deathPlace: joinPlace(v(b, 'dplLabel'), v(b, 'dplcLabel')),
        image: v(b, 'img') ? v(b, 'img').replace(/^http:/, 'https:') + '?width=160' : null,
        sitelinks: parseInt(v(b, 'links') || '0', 10),
        citizenship: new Set(),
        altBirth: new Set(),
        altDeath: new Set(),
        roles: [...(occByQ[q] || [])].filter((r) => r && !/old master/i.test(r)),
        sources: ['Wikidata'],
      };
    }
    if (v(b, 'cLabel')) c.citizenship.add(v(b, 'cLabel'));
    const bd = wdDate(v(b, 'b'), v(b, 'bp'));
    const dd = wdDate(v(b, 'd'), v(b, 'dp'));
    if (bd && bd !== c.birth) c.altBirth.add(bd);
    if (dd && dd !== c.death) c.altDeath.add(dd);
    if (!c.ulan && uid) c.ulan = uid;
  }

  const ulanIdsAll = [...new Set([...ulanRecs.map((u) => u.ulan), ...Object.values(byQ).map((c) => c.ulan).filter(Boolean)])];
  const uv = await safe('Getty ULAN', () => withCap(ulanVariants(ulanIdsAll.slice(0, 60)), GETTY_CAP_MS, 'Getty ULAN'));
  if (!uv.ok) errors.push(uv.error);
  const ulanVar = uv.ok ? uv.data : {};

  const candidates = [];
  for (const c of Object.values(byQ)) {
    const u = c.ulan ? ulanById[c.ulan] : null;
    if (u) {
      c.sources.push('Getty ULAN');
      if (!c.birthPlace && u.birthPlace) c.birthPlace = u.birthPlace;
      if (!c.birth && u.start) c.birth = String(u.start);
      if (!c.death && u.end && u.end < 9000) c.death = String(u.end);
      c.ulanDescription = u.desc;
      c.floruit = floruit(u.desc);
    }
    const variants = new Set([...(aliasByQ[c.id] || []), ...(ulanVar[c.ulan] || [])]);
    if (u) variants.add(u.name);
    variants.delete(c.name);
    c.variants = [...variants].filter(Boolean);
    c.citizenship = [...c.citizenship];
    const precise = (main) => (x) => !(main && main.endsWith(' ' + x)) && !(x.endsWith(' ' + main));
    c.altBirth = [...c.altBirth].filter(precise(c.birth));
    c.altDeath = [...c.altDeath].filter(precise(c.death));
    if (!c.roles.length && u) c.roles = rolesFromUlan(u.desc);
    candidates.push(c);
  }
  // ULAN-only candidates (not in Wikidata)
  for (const u of ulanRecs) {
    if (ulanToQ[u.ulan] && byQ[ulanToQ[u.ulan]]) continue;
    if (!ULAN_ROLE_RX.test(u.desc)) continue;
    candidates.push({
      id: 'ulan:' + u.ulan,
      wikidata: null,
      ulan: u.ulan,
      name: invertName(u.name),
      description: u.desc,
      ulanDescription: u.desc,
      birth: u.start ? String(u.start) : null,
      death: u.end && u.end < 9000 ? String(u.end) : null,
      floruit: floruit(u.desc),
      birthYear: u.start,
      deathYear: u.end && u.end < 9000 ? u.end : null,
      birthPlace: u.birthPlace,
      deathPlace: u.deathPlace,
      image: null,
      sitelinks: 0,
      citizenship: [],
      altBirth: [],
      altDeath: [],
      roles: rolesFromUlan(u.desc),
      variants: [u.name, ...(ulanVar[u.ulan] || [])].filter((x) => x !== invertName(u.name)),
      sources: ['Getty ULAN'],
    });
  }

  for (const c of candidates) {
    const m = matchInfo(name, [c.name, ...c.variants]);
    c.match = m.type;
    c.matchedName = m.name;
  }
  const rank = { exact: 0, all: 1, variant: 2, partial: 3 };
  candidates.sort((a, b) => rank[a.match] - rank[b.match] || b.sitelinks - a.sitelinks || (a.birthYear || 0) - (b.birthYear || 0));
  for (const c of candidates) c.variants = c.variants.slice(0, 40);
  return { query: rawQuery, normalized: name, candidates: candidates.slice(0, 40), errors: [...new Set(errors)] };
}

function joinPlace(place, country) {
  if (!place || /^https?:/.test(place)) return null;
  if (country && /^https?:/.test(country)) country = null;
  return country && country !== place ? `${place}, ${country}` : place;
}

function floruit(desc) {
  const m = String(desc || '').match(/\b(active|fl\.?|flourished)\s[^,;)]*/i);
  return m ? m[0].trim() : null;
}

function rolesFromUlan(desc) {
  const out = [];
  const d = String(desc || '').toLowerCase();
  for (const [rx, label] of [
    [/paint/, 'painter'],
    [/sculpt/, 'sculptor'],
    [/draftsm|draughtsm|drafts/, 'draftsman'],
    [/engrav/, 'engraver'],
    [/printmak/, 'printmaker'],
    [/etcher/, 'etcher'],
    [/medal/, 'medalist'],
    [/miniaturist/, 'miniaturist'],
    [/watercolo/, 'watercolorist'],
  ])
    if (rx.test(d)) out.push(label);
  return out;
}

module.exports = { search, invertName, ROOTS };
