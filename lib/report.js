'use strict';
/*
 * Report engine. Each exported function produces one section of the artist
 * report from open, citable sources. Every item carries a `cite` string
 * (Chicago style) and a URL so the user can verify it.
 */
const { getJSON, qs, sparqlWD, sparqlGetty, v, qid, safe, norm, wdDate, wdYear, uniqBy, cite, sparqlStr } = require('./util');
const { invertName } = require('./search');

const LANGS = 'en,mul,fr,de,it,nl,es,pt,sv,da,nb,fi,pl,cs,hu,ru,ja,zh';
const NOW_YEAR = new Date().getFullYear();

/* ------------------------------------------------------------------ helpers */
async function mapLimit(items, limit, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: Math.min(limit, items.length) }, async () => {
      while (i < items.length) {
        const idx = i++;
        try {
          out[idx] = await fn(items[idx], idx);
        } catch (e) {
          out[idx] = null;
        }
      }
    })
  );
  return out;
}

const memo = new Map();
function memoize(key, fn) {
  const hit = memo.get(key);
  if (hit && hit.exp > Date.now()) return hit.p;
  const p = fn().catch((e) => {
    memo.delete(key);
    throw e;
  });
  memo.set(key, { p, exp: Date.now() + 3 * 3600e3 });
  if (memo.size > 500) memo.delete(memo.keys().next().value);
  return p;
}

const surnameOf = (name) => {
  const parts = norm(name).split(' ').filter((p) => p.length > 1 && !['van', 'von', 'de', 'der', 'den', 'la', 'le', 'du', 'da', 'di', 'del', 'jr', 'sr'].includes(p));
  return parts[parts.length - 1] || norm(name);
};
const mentions = (text, name) => norm(text).includes(surnameOf(name));
/**
 * External metadata sometimes records the artist with wrong life dates
 * (e.g. an Internet Archive creator listed as "Rembrandt ..., 1608–1669").
 * When an author string names our artist and carries a year range that
 * contradicts the verified birth/death years, correct the range.
 */
function fixArtistLifeDates(str, name, by, dy) {
  if (!str || !by || !dy) return str;
  if (!norm(str).includes(surnameOf(name))) return str;
  return String(str).replace(/\b(\d{4})\s*[–-]\s*(\d{4})\b/, (m, a, b) => (+a === by && +b === dy ? m : `${by}–${dy}`));
}
/**
 * Does a museum's artist string refer to OUR artist (not a namesake)?
 * Requires the surname and, when the record carries life dates, a birth or death year within ±3 years.
 */
function sameArtist(display, name, by, dy, extraYears = []) {
  const n = norm(display);
  if (!n.includes(surnameOf(name))) return false;
  // reject namesakes whose recorded name has a different given/extra name (e.g. "Rembrandt Peale" vs "Rembrandt")
  const years = [...String(display || '').matchAll(/\b(1[0-9]{3}|[5-9][0-9]{2}|20[0-2][0-9])\b/g)].map((m) => +m[1]).concat(extraYears.filter(Boolean).map(Number));
  if (!years.length || (!by && !dy)) return true;
  return years.some((y) => (by && Math.abs(y - by) <= 3) || (dy && Math.abs(y - dy) <= 3));
}
const wikiUrl = (lang, title, project = 'wikipedia') => `https://${lang}.${project}.org/wiki/${encodeURIComponent(title.replace(/ /g, '_'))}`;
const wdUrl = (q) => `https://www.wikidata.org/wiki/${q}`;
const ulanUrl = (id) => `https://vocab.getty.edu/page/ulan/${id}`;
const stripHtml = (s) => String(s || '').replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\s+/g, ' ').trim();

/**
 * Verify a work's candidate museum identifiers against the institution's
 * own open API and return the verified institutional link — or null.
 * A constructed URL is not a verified link, and the museum websites
 * themselves block automated page checks (the Met answers 429 and the Art
 * Institute 403 to every request, a real object page and a bogus one
 * alike), so existence is confirmed through the institution's open API
 * instead: the Met API returns the museum's canonical objectURL for the
 * object, and the Art Institute API confirms the artwork exists under
 * that ID, its public page following the canonical
 * https://www.artic.edu/artworks/{id} pattern. An identifier the API
 * does not confirm is never emitted.
 * Wikidata "described at URL" (P973) is deliberately NOT resolved: its
 * targets are arbitrary third-party pages that cannot be verified from
 * this server, so those works keep their Wikidata link.
 */
async function verifyMetObject(id) {
  const r = await safe('The Met', () => getJSON(`https://collectionapi.metmuseum.org/public/collection/v1/objects/${id}`, { timeout: 10000 }));
  if (r.ok && r.data && +r.data.objectID === +id && r.data.objectURL) return { url: r.data.objectURL, institution: 'The Metropolitan Museum of Art' };
  return null;
}
async function verifyArticObject(id) {
  const r = await safe('Art Institute of Chicago', () => getJSON(`https://api.artic.edu/api/v1/artworks/${id}`, { headers: { 'AIC-User-Agent': 'ArtistResearchAtlas' }, timeout: 10000 }));
  if (r.ok && r.data && r.data.data && +r.data.data.id === +id) return { url: `https://www.artic.edu/artworks/${id}`, institution: 'Art Institute of Chicago' };
  return null;
}
/** Resolve a work's candidate museum identifiers to a verified institutional link (Met first, then Art Institute). */
async function verifyWorkLink(w) {
  if (w.metId) {
    const hit = await verifyMetObject(w.metId);
    if (hit) return hit;
  }
  if (w.articId) {
    const hit = await verifyArticObject(w.articId);
    if (hit) return hit;
  }
  return null;
}

/* ------------------------------------------------------------- resolution */
async function resolveIds({ wd, ulan }) {
  if (wd && !ulan) {
    const r = await safe('Wikidata', () => sparqlWD(`SELECT ?u WHERE { wd:${wd} wdt:P245 ?u } LIMIT 1`));
    if (r.ok && r.data[0]) ulan = v(r.data[0], 'u');
  }
  if (!wd && ulan) {
    const r = await safe('Wikidata', () => sparqlWD(`SELECT ?p WHERE { ?p wdt:P245 ${sparqlStr(ulan)} } LIMIT 1`));
    if (r.ok && r.data[0]) wd = qid(v(r.data[0], 'p'));
  }
  return { wd: wd || null, ulan: ulan || null };
}

/* ------------------------------------------------------------- Wikidata */
const PROPS = {
  P19: 'Place of birth', P20: 'Place of death', P27: 'Country of citizenship', P1412: 'Languages',
  P106: 'Occupation', P101: 'Field of work', P135: 'Movement / school', P136: 'Genre', P2348: 'Period',
  P69: 'Educated at', P1066: 'Student of (teachers)', P802: 'Teacher of (students)', P737: 'Influenced by',
  P463: 'Member of', P108: 'Employer', P39: 'Positions held', P166: 'Awards & honours', P551: 'Residence',
  P937: 'Work locations', P26: 'Spouse', P22: 'Father', P25: 'Mother', P3373: 'Siblings', P40: 'Children',
  P1038: 'Relatives', P140: 'Religion', P119: 'Place of burial', P509: 'Cause of death', P800: 'Notable works',
  P6379: 'Has works in the collection of', P1344: 'Participant in', P485: 'Archives held at', P1830: 'Owner of',
};

async function wdFacts(wd) {
  const pairs = Object.keys(PROPS).map((p) => `(p:${p} ps:${p} "${p}")`).join(' ');
  const rows = await sparqlWD(`SELECT ?pid ?val ?valLabel ?s ?e ?t WHERE {
    VALUES (?p ?ps ?pid) { ${pairs} }
    wd:${wd} ?p ?st . ?st ?ps ?val .
    OPTIONAL { ?st pq:P580 ?s } OPTIONAL { ?st pq:P582 ?e } OPTIONAL { ?st pq:P585 ?t }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } }`);
  const facts = {};
  for (const b of rows) {
    const pid = v(b, 'pid');
    const val = v(b, 'val');
    let label = v(b, 'valLabel');
    if (!label || /^https?:\/\/www\.wikidata\.org\/\.well-known/.test(label)) continue;
    const isItem = /entity\/Q\d+$/.test(val);
    const yrs = [wdYear(v(b, 's')), wdYear(v(b, 'e'))].filter(Boolean);
    const t = wdYear(v(b, 't'));
    let when = yrs.length ? yrs.join('–') : t ? String(t) : '';
    (facts[pid] ||= { label: PROPS[pid], values: [] }).values.push({ label, id: isItem ? qid(val) : null, when });
  }
  for (const f of Object.values(facts)) f.values = uniqBy(f.values, (x) => x.label + x.when);
  return facts;
}

async function wdCore(wd) {
  const rows = await sparqlWD(`SELECT ?label ?desc ?b ?bp ?d ?dp ?img ?sig ?fl ?ws ?we ?enwiki WHERE {
    OPTIONAL { wd:${wd} rdfs:label ?le FILTER(lang(?le)="en") } OPTIONAL { wd:${wd} rdfs:label ?lm FILTER(lang(?lm)="mul") }
    BIND(COALESCE(?le, ?lm) AS ?label)
    OPTIONAL { wd:${wd} schema:description ?desc FILTER(lang(?desc)="en") }
    OPTIONAL { wd:${wd} p:P569/psv:P569 [ wikibase:timeValue ?b; wikibase:timePrecision ?bp ] }
    OPTIONAL { wd:${wd} p:P570/psv:P570 [ wikibase:timeValue ?d; wikibase:timePrecision ?dp ] }
    OPTIONAL { wd:${wd} wdt:P18 ?img } OPTIONAL { wd:${wd} wdt:P109 ?sig }
    OPTIONAL { wd:${wd} wdt:P1317 ?fl } OPTIONAL { wd:${wd} wdt:P2031 ?ws } OPTIONAL { wd:${wd} wdt:P2032 ?we }
  } LIMIT 20`);
  const b0 = rows[0] || {};
  const dedupe = (arr) => {
    const u = uniqBy(arr.filter(Boolean), (x) => x);
    return u.filter((x) => !u.some((y) => y !== x && y.endsWith(' ' + x))); // drop "1606" when "15 Jul 1606" exists
  };
  const births = dedupe(rows.map((b) => wdDate(v(b, 'b'), v(b, 'bp'))));
  const deaths = dedupe(rows.map((b) => wdDate(v(b, 'd'), v(b, 'dp'))));
  return {
    name: v(b0, 'label'),
    description: v(b0, 'desc'),
    births,
    deaths,
    birthYear: wdYear(v(b0, 'b')),
    deathYear: wdYear(v(b0, 'd')),
    image: v(b0, 'img') ? v(b0, 'img').replace(/^http:/, 'https:') : null,
    signature: v(b0, 'sig') ? v(b0, 'sig').replace(/^http:/, 'https:') : null,
    floruit: wdYear(v(b0, 'fl')),
    workPeriod: [wdYear(v(b0, 'ws')), wdYear(v(b0, 'we'))].filter(Boolean).join('–') || null,
  };
}

async function wdNames(wd) {
  const rows = await sparqlWD(`SELECT DISTINCT ?a (lang(?a) AS ?lang) WHERE {
    { wd:${wd} skos:altLabel ?a } UNION { wd:${wd} rdfs:label ?a } UNION { wd:${wd} wdt:P1477|wdt:P742|wdt:P1559|wdt:P1449|wdt:P2561 ?a } }`);
  return rows.map((b) => ({ name: v(b, 'a'), lang: v(b, 'lang') }));
}

async function wdSitelinks(wd) {
  const rows = await sparqlWD(`SELECT ?article ?lang ?site ?title WHERE { ?article schema:about wd:${wd}; schema:inLanguage ?lang; schema:isPartOf ?site; schema:name ?title }`);
  return rows.map((b) => ({ url: v(b, 'article'), lang: v(b, 'lang'), site: v(b, 'site'), title: v(b, 'title') }));
}

const AUTH_RX = /VIAF|Library of Congress|GND|BnF|Bibliothèque nationale|ISNI|national library|authority|NKC|NDL|NLA|SUDOC|IdRef|BNE|NUKAT|PLWABN|CiNii|NLP|J9U|LNB|NSK|Libris|BIBSYS|NTA|CANTIC|FAST|WorldCat|Open Library|ORCID/i;
const MARKET_RX = /artnet|mutualart|invaluable|askart|artprice|christie|sotheby|bonhams|phillips|auction|artsy|liveauctioneers|price|dorotheum|lempertz|artvalue|artfacts|saatchi/i;
const ART_RX = /art|museum|painter|artist|gallery|collection|bénézit|benezit|grove|rkd|ulan|sikart|exhibition|tate|louvre|prado|rijks|getty|smithsonian|metropolitan|sculpt|engrav|print|photograph|design|biograph|dictionary|encyclop|national portrait|academy|salon|biografisch|lexikon|treccani|oxford|who/i;

async function wdExternalIds(wd) {
  const rows = await sparqlWD(`SELECT ?prop ?propLabel ?id ?fmt WHERE {
    wd:${wd} ?wdtp ?id . ?prop wikibase:directClaim ?wdtp; wikibase:propertyType wikibase:ExternalId .
    OPTIONAL { ?prop wdt:P1630 ?fmt }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }`);
  const out = uniqBy(
    rows.map((b) => {
      const label = v(b, 'propLabel');
      const fmt = v(b, 'fmt');
      const id = v(b, 'id');
      let url = fmt ? fmt.replace('$1', /^https?:/.test(fmt) && /\$1/.test(fmt) ? encodeURI(id).replace(/#/g, '%23') : id) : null;
      const group = MARKET_RX.test(label) ? 'market' : AUTH_RX.test(label) ? 'authority' : ART_RX.test(label) ? 'art' : 'other';
      return { property: qid(v(b, 'prop')), label, id, url, group };
    }),
    (x) => x.property + x.id
  );
  return out.sort((a, b) => a.label.localeCompare(b.label));
}

async function wdDescribedBy(wd) {
  const rows = await sparqlWD(`SELECT ?src ?srcLabel ?art ?artLabel ?d1 ?d2 ?url ?vol ?page ?named WHERE {
    wd:${wd} p:P1343 ?st . ?st ps:P1343 ?src .
    OPTIONAL { ?st pq:P805 ?art . OPTIONAL { ?art wdt:P577 ?d2 } }
    OPTIONAL { ?st pq:P2699 ?url } OPTIONAL { ?st pq:P478 ?vol } OPTIONAL { ?st pq:P304 ?page } OPTIONAL { ?st pq:P1932 ?named }
    OPTIONAL { ?src wdt:P577 ?d1 }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } } LIMIT 500`);
  const grouped = {};
  for (const b of rows) {
    const key = v(b, 'src') + '|' + (v(b, 'art') || '');
    const g = (grouped[key] ||= {
      source: v(b, 'srcLabel'),
      sourceId: qid(v(b, 'src')),
      article: v(b, 'artLabel') && !/^Q\d+$/.test(v(b, 'artLabel')) ? v(b, 'artLabel') : null,
      year: wdYear(v(b, 'd2') || v(b, 'd1')),
      url: v(b, 'url') || null,
      volume: v(b, 'vol') || null,
      page: v(b, 'page') || null,
      namedAs: v(b, 'named') || null,
      authors: new Set(),
      publisher: null,
    });
  }
  return Object.values(grouped)
    .map((g) => {
      const authors = [...g.authors];
      const extra = [g.volume && `vol. ${g.volume}`, g.page && `p. ${g.page}`, g.namedAs && `entry “${g.namedAs}”`].filter(Boolean).join(', ');
      return {
        ...g,
        authors,
        cite: g.article
          ? cite({ authors, title: g.article, container: g.source, date: g.year, url: g.url, kind: 'article', extra })
          : cite({ authors, title: g.source, publisher: g.publisher, date: g.year, url: g.url || wdUrl(g.sourceId), kind: 'book', extra }),
      };
    })
    .sort((a, b) => (a.year || 9999) - (b.year || 9999));
}

/* ------------------------------------------------------------- Getty ULAN */
async function ulanDetails(id) {
  const id_ = sparqlStr(id);
  const [main, names, notes, sources, rels, nats] = await Promise.all([
    sparqlGetty(`SELECT ?name ?desc ?start ?end ?bpName ?dpName WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; gvp:prefLabelGVP/xl:literalForm ?name; foaf:focus/gvp:biographyPreferred ?bio .
      OPTIONAL { ?bio schema:description ?desc } OPTIONAL { ?bio gvp:estStart ?start } OPTIONAL { ?bio gvp:estEnd ?end }
      OPTIONAL { ?bio schema:birthPlace ?bpf . ?bpc foaf:focus ?bpf; gvp:prefLabelGVP/xl:literalForm ?bpName }
      OPTIONAL { ?bio schema:deathPlace ?dpf . ?dpc foaf:focus ?dpf; gvp:prefLabelGVP/xl:literalForm ?dpName } } LIMIT 1`),
    sparqlGetty(`SELECT DISTINCT ?l WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; xl:altLabel|xl:prefLabel ?t . ?t xl:literalForm ?l }`),
    sparqlGetty(`SELECT ?note WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; skos:scopeNote ?n . ?n rdf:value ?note . OPTIONAL { ?n dct:language ?lg } FILTER(!bound(?lg) || ?lg = aat:300388277) }`),
    sparqlGetty(`SELECT DISTINCT ?src ?t WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; dct:source ?src . ?src bibo:shortTitle ?t }`),
    sparqlGetty(`SELECT DISTINCT ?relLabel ?oname ?oid WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; ?rel ?o .
      ?o a gvp:PersonConcept; gvp:prefLabelGVP/xl:literalForm ?oname; dc:identifier ?oid .
      FILTER(?rel NOT IN (skos:related, skos:exactMatch, skos:closeMatch, gvp:broader, skos:broader))
      OPTIONAL { ?rel rdfs:label ?relLabel } } LIMIT 150`),
    sparqlGetty(`SELECT DISTINCT ?nat WHERE { ?s dc:identifier ${id_}; a gvp:PersonConcept; foaf:focus/schema:nationality ?n . ?n gvp:prefLabelGVP/xl:literalForm ?nat }`),
  ]);
  const m = main[0] || {};
  return {
    id,
    url: ulanUrl(id),
    name: v(m, 'name'),
    displayName: invertName(v(m, 'name')),
    description: v(m, 'desc'),
    birthPlace: v(m, 'bpName') || null,
    deathPlace: v(m, 'dpName') || null,
    estStart: v(m, 'start') || null,
    estEnd: v(m, 'end') || null,
    names: names.map((b) => v(b, 'l')),
    notes: notes.map((b) => v(b, 'note')),
    nationalities: nats.map((b) => v(b, 'nat')),
    relations: rels.filter((b) => !/mapping relation/i.test(v(b, 'relLabel') || '')).map((b) => ({
      relation: (v(b, 'relLabel') || '').replace(/_/g, ' ').replace(/^(ulan)?\d+\s*/i, '').trim() || 'related to',
      name: invertName(v(b, 'oname')),
      ulan: v(b, 'oid'),
    })),
    sources: sources.map((b) => ({
      title: v(b, 't'),
      url: `https://www.getty.edu/vow/ULANSource?find=&role=&nation=&sourceid=${v(b, 'src').split('/').pop()}`,
      cite: cite({ title: v(b, 't'), kind: 'book', extra: 'Cited as a source by the Getty Union List of Artist Names' }),
    })),
    cite: cite({ authors: 'Getty Research Institute', title: `${invertName(v(m, 'name'))} (ULAN ${id})`, container: 'Union List of Artist Names Online', url: ulanUrl(id) }),
  };
}

/* ------------------------------------------------------------- Wikipedia */
const SECTION_RULES = [
  ['skip', /^(references|notes|footnotes|citations|sources|external links|see also|further reading|bibliography|literature|works cited|gallery|list of works|selected works|images|notes and references|explanatory notes)$/i],
  ['collections', /museum collections|public collections|collections|holdings/i],
  ['market', /market|auction|sale|price|forger|value|provenance|theft|stolen|record/i],
  ['exhibitions', /exhibit|retrospective|show|salon|exposition|biennale/i],
  ['critical', /legacy|reception|reputation|critic|assessment|influence|style|technique|method|analysis|theme|subject|iconograph|approach|attribution|controvers|evaluation|appraisal|art\b|artistic|painting style|posthum|honou?rs|recognition|in popular culture|academic|^works$|oeuvre|œuvre|materials|signature|catalogue raisonn|period|films?|music|literary|fiction|depictions|cultural|memorial|tribute|works about|about /i],
  ['biography', /.*/],
];
function classify(heading) {
  for (const [k, rx] of SECTION_RULES) if (rx.test(heading.trim())) return k;
  return 'biography';
}

async function wikiArticle(lang, title, project = 'wikipedia') {
  const url = `https://${lang}.${project}.org/w/api.php?` + qs({ action: 'query', prop: 'extracts|info|revisions', explaintext: '1', exsectionformat: 'wiki', inprop: 'url', rvprop: 'timestamp', titles: title, redirects: '1', format: 'json' });
  const d = await getJSON(url, { timeout: 20000 });
  const page = Object.values(d.query?.pages || {})[0];
  if (!page || page.missing !== undefined) return null;
  const text = page.extract || '';
  const sections = [];
  let cur = { heading: 'Introduction', level: 1, text: [] };
  for (const line of text.split('\n')) {
    const h = line.match(/^(={2,6})\s*(.*?)\s*\1\s*$/);
    if (h) {
      sections.push(cur);
      cur = { heading: h[2], level: h[1].length, text: [] };
    } else if (line.trim()) cur.text.push(line.trim());
  }
  sections.push(cur);
  // subsections inherit the nearest ancestor's category unless they have their own
  const stack = [];
  for (const s of sections) {
    const own = s.heading === 'Introduction' ? 'biography' : classify(s.heading);
    let parent = null;
    for (let l = s.level - 1; l >= 1; l--) if (stack[l]) { parent = stack[l]; break; }
    s.category = parent === 'skip' ? 'skip' : own === 'biography' && parent ? parent : own;
    stack[s.level] = s.category;
    stack.length = s.level + 1;
    s.paragraphs = s.text;
    delete s.text;
  }
  const lastRev = page.revisions?.[0]?.timestamp?.slice(0, 10);
  return {
    lang,
    title: page.title,
    url: page.fullurl || wikiUrl(lang, page.title, project),
    sections: sections.filter((s) => s.paragraphs.length || s.level <= 2),
    plain: text,
    cite: cite({ title: page.title, container: `${project === 'wikiquote' ? 'Wikiquote' : 'Wikipedia'} (${lang})`, date: lastRev ? `last revised ${lastRev}` : undefined, url: page.fullurl }),
  };
}

/* ======================================================= SECTION: PROFILE */
async function profile({ wd, ulan }) {
  ({ wd, ulan } = await resolveIds({ wd, ulan }));
  return memoize(`profile:${wd}:${ulan}`, async () => {
    const tasks = {
      core: wd ? safe('Wikidata', () => wdCore(wd)) : null,
      facts: wd ? safe('Wikidata', () => wdFacts(wd)) : null,
      names: wd ? safe('Wikidata', () => wdNames(wd)) : null,
      links: wd ? safe('Wikidata', () => wdSitelinks(wd)) : null,
      ids: wd ? safe('Wikidata', () => wdExternalIds(wd)) : null,
      described: wd ? safe('Wikidata', () => wdDescribedBy(wd)) : null,
      ulan: ulan ? safe('Getty ULAN', () => ulanDetails(ulan)) : null,
    };
    const res = {};
    await Promise.all(Object.entries(tasks).map(async ([k, p]) => (res[k] = p ? await p : null)));
    const errors = Object.values(res).filter((r) => r && !r.ok).map((r) => r.error);
    const core = res.core?.data || {};
    const u = res.ulan?.data || null;
    const links = res.links?.data || [];

    // Wikipedia: English first, else best available language
    const wp = links.filter((l) => /wikipedia\.org/.test(l.site));
    const order = ['en', 'fr', 'de', 'it', 'nl', 'es', 'pt', 'sv', 'da', 'pl', 'ru', 'ja'];
    wp.sort((a, b) => (order.indexOf(a.lang) + 99) % 99 - (order.indexOf(b.lang) + 99) % 99);
    const best = wp.find((l) => l.lang === 'en') || wp[0];
    const quote = links.find((l) => l.lang === 'en' && /wikiquote\.org/.test(l.site));
    const [wiki, wq] = await Promise.all([
      best ? safe('Wikipedia', () => wikiArticle(best.lang, best.title)) : null,
      quote ? safe('Wikiquote', () => wikiArticle('en', quote.title, 'wikiquote')) : null,
    ]);
    if (wiki && !wiki.ok) errors.push(wiki.error);
    if (wq && !wq.ok) errors.push(wq.error);

    const name = core.name || u?.displayName || 'Unknown artist';
    const variantSet = new Map();
    for (const n of [...(res.names?.data || []), ...(u?.names || []).map((x) => ({ name: x, lang: 'ULAN' }))]) {
      if (!n.name || n.name === name) continue;
      const k = norm(n.name);
      if (!variantSet.has(k)) variantSet.set(k, n);
    }
    const facts = res.facts?.data || {};
    const birthPlace = facts.P19?.values.map((x) => x.label).join(' / ') || u?.birthPlace || null;
    const deathPlace = facts.P20?.values.map((x) => x.label).join(' / ') || u?.deathPlace || null;
    const ulanYear = (x) => (x && parseInt(x, 10) <= NOW_YEAR && u?.description?.includes(String(parseInt(x, 10))) ? parseInt(x, 10) : null);
    const birthYear = core.birthYear ?? ulanYear(u?.estStart);
    const deathYear = core.deathYear ?? ulanYear(u?.estEnd);

    // Wikiquote: keep "Quotes about …" sections (assessments by peers & critics)
    let quotes = null;
    if (wq?.ok && wq.data) {
      const secs = wq.data.sections;
      const startIdx = secs.findIndex((s) => /quotes? about|about .*|sayings about|quotes on/i.test(s.heading));
      if (startIdx >= 0) {
        const lvl = secs[startIdx].level;
        const sub = [];
        for (let i = startIdx; i < secs.length; i++) {
          if (i > startIdx && secs[i].level <= lvl) break;
          if (secs[i].paragraphs.length) sub.push({ heading: secs[i].heading, paragraphs: secs[i].paragraphs.slice(0, 40) });
        }
        quotes = { url: wq.data.url, cite: wq.data.cite, sections: sub };
      }
    }

    return {
      ids: { wikidata: wd, ulan },
      name,
      description: core.description || u?.description || '',
      ulanDescription: u?.description || null,
      births: core.births?.length ? core.births : birthYear ? [String(birthYear)] : [],
      deaths: core.deaths?.length ? core.deaths : deathYear ? [String(deathYear)] : [],
      birthYear,
      deathYear,
      living: !deathYear && birthYear && birthYear > NOW_YEAR - 110,
      floruit: core.floruit || core.workPeriod || null,
      birthPlace,
      deathPlace,
      image: core.image,
      signature: core.signature,
      variants: [...variantSet.values()].slice(0, 150),
      facts,
      ulan: u,
      wikipedia: wiki?.ok ? wiki.data : null,
      wikiquote: quotes,
      sitelinks: links.filter((l) => /wikipedia\.org/.test(l.site)).map((l) => ({ lang: l.lang, title: l.title, url: l.url })),
      externalIds: res.ids?.data || [],
      describedBy: res.described?.data || [],
      wikidataCite: wd ? cite({ title: `${name} (${wd})`, container: 'Wikidata', url: wdUrl(wd) }) : null,
      errors: [...new Set(errors)],
    };
  });
}

/* ================================================ museum data (shared) */
function museumData(name, by, dy) {
  by = by ? +by : null;
  dy = dy ? +dy : null;
  return memoize(`museum:${norm(name)}:${by}:${dy}`, async () => {
    const sur = surnameOf(name);
    const [met, aic, cma, eu] = await Promise.all([
      safe('The Met', async () => {
        const s = await getJSON('https://collectionapi.metmuseum.org/public/collection/v1.1/search?' + qs({ q: name, artistOrCulture: 'true', limit: '40' }));
        const ids = (s.objectIDs || []).slice(0, 24);
        const objs = await mapLimit(ids, 12, (id) => getJSON(`https://collectionapi.metmuseum.org/public/collection/v1/objects/${id}`, { timeout: 12000 }));
        return objs
          .filter((o) => o && sameArtist(`${o.artistDisplayName} ${o.artistDisplayBio || ''}`, name, by, dy, [parseInt(o.artistBeginDate, 10), parseInt(o.artistEndDate, 10)]))
          .map((o) => ({
            museum: 'The Metropolitan Museum of Art',
            title: o.title,
            date: o.objectDate,
            medium: o.medium,
            artist: o.artistDisplayName,
            accession: o.accessionNumber,
            image: o.primaryImageSmall || null,
            url: o.objectURL,
            department: o.department,
          }));
      }),
      safe('Art Institute of Chicago', async () => {
        const d = await getJSON('https://api.artic.edu/api/v1/artworks/search?' + qs({ q: name, limit: '40', fields: 'id,title,artist_title,artist_display,date_display,medium_display,image_id,main_reference_number,exhibition_history,provenance_text,publication_history,credit_line' }), { headers: { 'AIC-User-Agent': 'ArtistResearchAtlas' } });
        return (d.data || [])
          .filter((o) => sameArtist(o.artist_display || o.artist_title, name, by, dy))
          .map((o) => ({
            museum: 'Art Institute of Chicago',
            title: o.title,
            date: o.date_display,
            medium: o.medium_display,
            artist: o.artist_title,
            accession: o.main_reference_number,
            image: o.image_id ? `https://www.artic.edu/iiif/2/${o.image_id}/full/400,/0/default.jpg` : null,
            url: `https://www.artic.edu/artworks/${o.id}`,
            exhibitionHistory: o.exhibition_history || null,
            provenance: o.provenance_text || null,
            publications: o.publication_history || null,
            credit: o.credit_line,
          }));
      }),
      safe('Cleveland Museum of Art', async () => {
        const d = await getJSON('https://openaccess-api.clevelandart.org/api/artworks/?' + qs({ q: name, limit: '40' }), { timeout: 25000 });
        return (d.data || [])
          .filter((o) => (o.creators || []).some((c) => sameArtist(`${c.description} ${c.birth_year || ''} ${c.death_year || ''}`, name, by, dy)))
          .map((o) => ({
            museum: 'Cleveland Museum of Art',
            title: o.title,
            date: o.creation_date,
            medium: o.technique,
            artist: (o.creators || []).map((c) => c.description).join('; '),
            accession: o.accession_number,
            image: o.images?.web?.url || null,
            url: o.url,
            exhibitions: [...(o.exhibitions?.current || []), ...(o.exhibitions?.legacy || [])].map((e) => ({ title: stripHtml(e.title || e.description), date: e.opening_date || null, venue: e.organizer || null, description: stripHtml(e.description) })),
            provenanceList: (o.provenance || []).map((p) => ({ description: stripHtml(p.description), date: p.date, citations: (p.citations || []).map((c) => stripHtml(c.citation)) })),
            citations: (o.citations || []).map((c) => ({ text: stripHtml(c.citation), page: c.page_number, url: c.url })),
          }));
      }),
      safe('Europeana', async () => {
        const d = await getJSON('https://api.europeana.eu/record/v2/search.json?' + qs({ wskey: process.env.EUROPEANA_KEY || 'api2demo', query: `who:"${name}"`, rows: '30', profile: 'standard' }));
        return (d.items || []).map((o) => ({
          museum: (o.dataProvider || [])[0] || 'Europeana',
          title: (o.title || [])[0],
          date: (o.year || [])[0] || '',
          medium: (o.type || ''),
          artist: (o.dcCreator || [])[0],
          image: (o.edmPreview || [])[0] || null,
          url: o.guid,
          country: (o.country || [])[0],
        }));
      }),
    ]);
    return { met, aic, cma, eu };
  });
}

async function wdWorks(wd) {
  return memoize('works:' + wd, async () => {
    // Museum identifiers are fetched with the work list, at the first query:
    // P3634 (The Met object ID) and P4610 (Art Institute of Chicago artwork
    // ID). They are candidates only — collections() verifies each one against
    // the institution's own API before the institutional link is emitted.
    const rows = await sparqlWD(`SELECT ?w ?wLabel ?inc ?collLabel ?inv ?img ?typeLabel ?met ?artic WHERE {
      ?w wdt:P170 wd:${wd} .
      OPTIONAL { ?w wdt:P571 ?inc } OPTIONAL { ?w wdt:P195 ?coll } OPTIONAL { ?w wdt:P217 ?inv } OPTIONAL { ?w wdt:P18 ?img }
      OPTIONAL { ?w wdt:P31 ?type } OPTIONAL { ?w wdt:P3634 ?met } OPTIONAL { ?w wdt:P4610 ?artic }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } } LIMIT 3000`);
    const by = {};
    for (const b of rows) {
      const id = qid(v(b, 'w'));
      const w = (by[id] ||= { id, title: v(b, 'wLabel'), year: wdYear(v(b, 'inc')), collections: new Set(), inventory: v(b, 'inv') || null, image: v(b, 'img') ? v(b, 'img').replace(/^http:/, 'https:') + '?width=300' : null, type: v(b, 'typeLabel') || null, url: wdUrl(id), wikidataUrl: wdUrl(id), metId: null, articId: null });
      if (v(b, 'collLabel')) w.collections.add(v(b, 'collLabel'));
      if (v(b, 'met')) w.metId = v(b, 'met');
      if (v(b, 'artic')) w.articId = v(b, 'artic');
    }
    return Object.values(by).map((w) => ({ ...w, collections: [...w.collections] }));
  });
}

/* ================================================== SECTION: COLLECTIONS */
async function collections({ wd, name, by, dy }) {
  const [works, museums] = await Promise.all([wd ? safe('Wikidata', () => wdWorks(wd)) : null, museumData(name, by, dy)]);
  const counts = {};
  for (const w of works?.data || []) for (const c of w.collections) counts[c] = (counts[c] || 0) + 1;
  const holdings = Object.entries(counts).map(([collection, count]) => ({ collection, count })).sort((a, b) => b.count - a.count);
  const all = works?.data || [];
  // A work dated before the artist was born cannot be theirs: the open
  // record is wrong (a misattribution or a bad inception date on Wikidata).
  // Keep such works out of the displayed list instead of showing
  // impossible dates. Totals and holdings still count the full record.
  const plausible = all.filter((w) => !(by && w.year && w.year < by));
  const sample = [...plausible].sort((a, b) => (b.image ? 1 : 0) - (a.image ? 1 : 0) || (a.year || 9999) - (b.year || 9999)).slice(0, 60);
  // Only a museum link the institution's own API confirms is emitted: check
  // each sampled work's candidate identifiers (from wdWorks) and replace its
  // Wikidata URL with the verified institutional page. Anything unverified
  // keeps the Wikidata link, and the Wikidata URL stays on the record as
  // the secondary link.
  await mapLimit(sample, 6, async (w) => {
    if (!w.metId && !w.articId) return;
    const hit = await verifyWorkLink(w);
    if (hit) {
      w.url = hit.url;
      w.institution = hit.institution;
    }
  });
  const errors = [works, museums.met, museums.aic, museums.cma, museums.eu].filter((r) => r && !r.ok).map((r) => r.error);
  return {
    totalWorks: all.length,
    holdings,
    works: sample,
    museumObjects: [...(museums.met.data || []), ...(museums.aic.data || []), ...(museums.cma.data || [])].map(({ exhibitionHistory, provenance, publications, exhibitions, provenanceList, citations, ...o }) => o),
    europeana: museums.eu.data || [],
    errors,
  };
}

/* ============================================ SECTION: CATALOGUE RAISONNÉ */
// The catalogue raisonné is the standard complete, authenticated listing
// of an artist's works. Volumes are shown in chronological order, including
// catalogues later superseded by newer ones — the history of cataloguing
// is part of the record.
const RAISONNE_RX = /catalogues?\s+raisonn/;
// Words (normalised) that mark a title as a catalogue of works even when
// it does not carry the phrase "catalogue raisonné". Open Library subject
// headings alone are too loose — general monographs carry them too — so a
// subject-only match also needs one of these words in the title.
const CATALOGUE_WORDS = ['catalog', 'complet', 'oeuvre', 'uvre', 'works', 'werk', 'opera', 'zeichnung', 'schilderijen', 'grave', 'eaux', 'corpus', 'katalog', 'cataleg'];
// The standard modern catalogue does not always carry the phrase in its
// title ("A Corpus of Rembrandt Paintings", de La Faille's "L'Oeuvre de
// Vincent van Gogh"), so a small curated list covers the famous cases the
// search cannot surface. Every entry was verified against Open Library /
// the Internet Archive. Keys are the artist's surname.
const CURATED_RAISONNES = {
  rembrandt: [
    { title: 'The Paintings of Rembrandt', authors: ['A. Bredius'], year: 1937, url: 'https://openlibrary.org/works/OL31607372W' },
    { title: 'Rembrandt Paintings', authors: ['Horst Gerson'], year: 1969, url: 'https://archive.org/details/rembrandtpaintin0000gers', iaUrl: 'https://archive.org/details/rembrandtpaintin0000gers' },
    { title: 'A Corpus of Rembrandt Paintings', authors: ['J. Bruyn', 'Ernst van de Wetering'], year: 1982, yearEnd: 2014, note: '6 vols.', url: 'https://openlibrary.org/works/OL18343091W' },
  ],
  gogh: [
    { title: "L'Oeuvre de Vincent van Gogh", authors: ['Jacob Baart de la Faille'], year: 1928, url: 'https://openlibrary.org/works/OL518169W' },
  ],
};

async function catalogue({ wd, name }) {
  const surname = surnameOf(name);
  // The surname must appear as its own word: "Rembrandtschüler" (a book
  // about a pupil) must not match "Rembrandt".
  const surnameRx = new RegExp(`(^|[^a-z])${surname.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}s?([^a-z]|$)`);
  const enc = encodeURIComponent;
  const [ol, wikidata] = await Promise.all([
    safe('Open Library', async () => {
      const d = await getJSON('https://openlibrary.org/search.json?' + qs({ q: `${name} catalogue raisonne`, fields: 'key,title,subtitle,author_name,first_publish_year,publisher,ia,subject', limit: '40' }), { timeout: 25000 });
      return (d.docs || [])
        .filter((b) => {
          const title = norm(`${b.title || ''} ${b.subtitle || ''}`);
          const subjects = (b.subject || []).map(norm);
          const hasWord = CATALOGUE_WORDS.some((w) => title.includes(w));
          return (RAISONNE_RX.test(title) || (subjects.some((s) => RAISONNE_RX.test(s)) && hasWord)) && surnameRx.test(title);
        })
        .map((b) => ({
          title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''),
          authors: (b.author_name || []).slice(0, 3),
          year: b.first_publish_year || null,
          publisher: (b.publisher || [])[0] || null,
          url: `https://openlibrary.org${b.key}`,
          iaUrl: (b.ia || [])[0] ? `https://archive.org/details/${b.ia[0]}` : null,
          source: 'Open Library',
        }));
    }),
    wd && /^[a-z]+$/.test(surname)
      ? safe('Wikidata', async () => {
          const rows = await sparqlWD(`SELECT ?cr ?crLabel ?date ?authorLabel WHERE {
            ?cr wdt:P31 wd:Q1050259 .
            ?cr rdfs:label ?crLabel .
            FILTER(REGEX(LCASE(?crLabel), "(^|[^a-z])${surname}s?([^a-z]|$)"))
            OPTIONAL { ?cr wdt:P577 ?date }
            OPTIONAL { ?cr wdt:P50 ?author }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } ORDER BY ?date ?crLabel LIMIT 200`);
          // One row per label language; keep one row per item, English first.
          const byQ = new Map();
          for (const b of rows) {
            const id = qid(v(b, 'cr'));
            const lang = b.crLabel?.['xml:lang'] || '';
            const prev = byQ.get(id);
            if (!prev || (lang === 'en' && prev.lang !== 'en')) byQ.set(id, { id, lang, label: v(b, 'crLabel'), date: v(b, 'date'), author: v(b, 'authorLabel') });
          }
          return [...byQ.values()].map((r) => ({
            title: r.label,
            authors: r.author ? [r.author] : [],
            year: wdYear(r.date),
            url: wdUrl(r.id),
            source: 'Wikidata',
          }));
        })
      : null,
  ]);
  // Merge, preferring curated entries, then dedupe (editions of the same
  // catalogue collapse to one row — the key is the first 50 characters of
  // the normalised title, and a title that extends another is the same
  // work) and order chronologically, earliest year winning on a collision.
  const merged = new Map();
  const dedupKey = (t) => norm(String(t || '').replace(/œ/gi, 'oe').replace(/æ/gi, 'ae')).slice(0, 50).replace(/[^a-z0-9]/g, '');
  const put = (x, curated) => {
    const nk = dedupKey(x.title);
    if (!nk) return;
    let key = nk;
    for (const k of merged.keys()) if (k.startsWith(nk) || nk.startsWith(k)) { key = k; break; }
    const prev = merged.get(key);
    if (!prev) { merged.set(key, { ...x, curated: !!curated }); return; }
    if (curated && !prev.curated) { merged.set(key, { ...x, curated: true }); return; }
    // A curated row is never overwritten by a discovered record that merely
    // shares its title prefix (e.g. a single Corpus volume must not replace
    // the 6-volume Corpus entry); only fill in gaps.
    if (prev.curated) {
      const nx = { ...prev };
      if (!prev.authors?.length && x.authors?.length) nx.authors = x.authors;
      if (!prev.iaUrl && x.iaUrl) nx.iaUrl = x.iaUrl;
      merged.set(key, nx);
      return;
    }
    const nx = { ...prev };
    if (x.year && (!prev.year || x.year < prev.year)) { nx.year = x.year; nx.yearEnd = x.yearEnd || null; nx.url = x.url; nx.source = x.source; nx.title = x.title; nx.note = x.note || prev.note; }
    if (!prev.authors?.length && x.authors?.length) nx.authors = x.authors;
    if (!prev.iaUrl && x.iaUrl) nx.iaUrl = x.iaUrl;
    merged.set(key, nx);
  };
  for (const x of CURATED_RAISONNES[surname] || []) put({ ...x, source: 'Curated' }, true);
  for (const x of ol.data || []) put(x, false);
  for (const x of wikidata?.data || []) put(x, false);
  // Curated entries are always shown. No backend cap: the report UI shows
  // the first 15 with a "Show more" control for the rest.
  const items = [...merged.values()]
    .map((x) => ({ ...x, cite: cite({ authors: x.authors, title: x.title, publisher: x.publisher, date: x.year, kind: 'book', url: x.url }) }))
    .sort((a, b) => (a.year || 9999) - (b.year || 9999));
  return {
    items,
    links: [
      ['Open Library — "NAME catalogue raisonné"', `https://openlibrary.org/search?q=${enc(`${name} catalogue raisonné`)}`],
      ['WorldCat — "NAME catalogue raisonné"', `https://search.worldcat.org/search?q=${enc(`"${name}" "catalogue raisonné"`)}`],
      ['Google Books — "NAME catalogue raisonné"', `https://www.google.com/search?tbm=bks&q=${enc(`"${name}" "catalogue raisonné"`)}`],
      ['Internet Archive — "NAME catalogue raisonné"', `https://archive.org/search?query=${enc(`"${name}" AND "catalogue raisonné"`)}`],
    ].map(([label, url]) => ({ label, url })),
    errors: [ol, wikidata].filter((r) => r && !r.ok).map((r) => r.error),
  };
}

/* ================================================== SECTION: EXHIBITIONS */
async function exhibitions({ wd, name, by, dy }) {
  const [wdEx, aicEx, catalogues, museums] = await Promise.all([
    wd
      ? safe('Wikidata', async () => {
          const rows = await sparqlWD(`SELECT ?e ?eLabel ?s ?f ?t ?locLabel ?orgLabel ?how ?w ?wLabel WHERE {
            { wd:${wd} wdt:P1344 ?e . BIND("participant" AS ?how) }
            UNION { ?e wdt:P710 wd:${wd} . BIND("participant" AS ?how) }
            UNION { ?w wdt:P170 wd:${wd}; wdt:P608 ?e . BIND("work exhibited" AS ?how) }
            ?e wdt:P31/wdt:P279* wd:Q464980 .
            OPTIONAL { ?e wdt:P580 ?s } OPTIONAL { ?e wdt:P582 ?f } OPTIONAL { ?e wdt:P585|wdt:P571 ?t }
            OPTIONAL { ?e wdt:P276 ?loc } OPTIONAL { ?e wdt:P664 ?org }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } } LIMIT 4000`);
          const by = {};
          for (const b of rows) {
            const id = qid(v(b, 'e'));
            const e = (by[id] ||= { id, title: v(b, 'eLabel'), start: wdYear(v(b, 's')) || wdYear(v(b, 't')), startRaw: v(b, 's') || v(b, 't') || null, end: wdYear(v(b, 'f')), venues: new Set(), organizers: new Set(), how: new Set(), works: new Map(), url: wdUrl(id) });
            if (v(b, 'locLabel')) e.venues.add(v(b, 'locLabel'));
            if (v(b, 'orgLabel')) e.organizers.add(v(b, 'orgLabel'));
            e.how.add(v(b, 'how'));
            if (v(b, 'w')) e.works.set(qid(v(b, 'w')), v(b, 'wLabel'));
          }
          return Object.values(by)
            .map((e) => ({
              ...e,
              venues: [...e.venues],
              organizers: [...e.organizers],
              how: [...e.how],
              workCount: e.works.size,
              works: [...e.works.values()].slice(0, 12),
              date: e.startRaw ? wdDate(e.startRaw, 9) + (e.end && e.end !== e.start ? `–${e.end}` : '') : '',
              cite: cite({ title: e.title, container: [...e.venues].join(', ') || [...e.organizers].join(', ') || undefined, date: e.start ? String(e.start) : undefined, url: e.url, extra: 'Exhibition record, Wikidata' }),
            }))
            .sort((a, b) => (a.start || 9999) - (b.start || 9999));
        })
      : null,
    safe('Art Institute of Chicago', async () => {
      const d = await getJSON('https://api.artic.edu/api/v1/exhibitions/search?' + qs({ q: name, limit: '30', fields: 'id,title,aic_start_at,aic_end_at,short_description,web_url,status,gallery_title' }), { headers: { 'AIC-User-Agent': 'ArtistResearchAtlas' } });
      return (d.data || [])
        .filter((e) => mentions(`${e.title} ${e.short_description || ''}`, name))
        .map((e) => ({
          title: e.title,
          venue: 'Art Institute of Chicago' + (e.gallery_title ? `, ${e.gallery_title}` : ''),
          date: [e.aic_start_at?.slice(0, 10), e.aic_end_at?.slice(0, 10)].filter(Boolean).join(' – '),
          description: stripHtml(e.short_description),
          url: e.web_url || `https://www.artic.edu/exhibitions/${e.id}`,
          cite: cite({ title: e.title, container: 'Art Institute of Chicago', date: e.aic_start_at?.slice(0, 4), url: e.web_url || `https://www.artic.edu/exhibitions/${e.id}`, extra: 'Exhibition' }),
        }));
    }),
    safe('Open Library', async () => {
      const q = `"${name}" AND (exhibition OR exposition OR retrospective OR catalogue OR ausstellung OR tentoonstelling OR mostra OR exposición OR salon)`;
      const d = await getJSON('https://openlibrary.org/search.json?' + qs({ q, fields: 'key,title,subtitle,author_name,first_publish_year,publisher,publish_place', limit: '60', sort: 'old' }), { timeout: 25000 });
      return (d.docs || [])
        .filter((b) => mentions(`${b.title} ${b.subtitle || ''} ${(b.author_name || []).join(' ')}`, name))
        .map((b) => ({
          title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''),
          year: b.first_publish_year || null,
          authors: (b.author_name || []).slice(0, 4),
          publisher: (b.publisher || [])[0] || null,
          place: (b.publish_place || [])[0] || null,
          url: `https://openlibrary.org${b.key}`,
          cite: cite({ authors: (b.author_name || []).slice(0, 3), title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''), place: (b.publish_place || [])[0], publisher: (b.publisher || [])[0], date: b.first_publish_year, kind: 'book', url: `https://openlibrary.org${b.key}` }),
        }));
    }),
    museumData(name, by, dy),
  ]);

  // object-level exhibition histories from museum records
  const objectHistories = [];
  for (const o of museums.aic.data || [])
    if (o.exhibitionHistory) objectHistories.push({ object: o.title, date: o.date, museum: o.museum, url: o.url, entries: o.exhibitionHistory.split(/\n+/).map((s) => s.trim()).filter(Boolean) });
  for (const o of museums.cma.data || [])
    if (o.exhibitions?.length) objectHistories.push({ object: o.title, date: o.date, museum: o.museum, url: o.url, entries: o.exhibitions.map((e) => e.description || e.title).filter(Boolean) });

  const enc = encodeURIComponent;
  const databases = [
    ['Artfacts — exhibition history & rankings', `https://artfacts.net/search?q=${enc(name)}`],
    ['Database of Modern Exhibitions (DoME), 1905–1915', `https://exhibitions.univie.ac.at/person/search?q=${enc(name)}`],
    ['Paris Salon catalogues (Musée d’Orsay base Salons)', `https://salons.musee-orsay.fr/index/resultats?q=${enc(name)}`],
    ['Royal Academy of Arts collection & exhibition catalogues', `https://www.royalacademy.org.uk/art-artists/search/search-the-collection?search=${enc(name)}`],
    ['MoMA exhibition history', `https://www.moma.org/artists?q=${enc(name)}`],
    ['RKD Research (Netherlands Institute for Art History)', `https://rkd.nl/en/search?query=${enc(name)}`],
    ['Artsy — shows & fairs', `https://www.artsy.net/search?term=${enc(name)}`],
    ['Smithsonian Archives of American Art', `https://www.aaa.si.edu/search/collections?edan_q=${enc(name)}`],
    ['Frick Art Reference Library (Arcade catalogue)', `https://arcade.nyarc.org/search~S7/?searchtype=X&searcharg=${enc(name)}`],
  ].map(([label, url]) => ({ label, url }));

  return {
    wikidata: wdEx?.data || [],
    aic: aicEx.data || [],
    catalogues: catalogues.data || [],
    objectHistories: objectHistories.slice(0, 30),
    databases,
    errors: [wdEx, aicEx, catalogues].filter((r) => r && !r.ok).map((r) => r.error),
  };
}

/* ===================================================== SECTION: ACADEMIC */
function openAlexUrl(params) {
  if (process.env.OPENALEX_API_KEY) params.api_key = process.env.OPENALEX_API_KEY;
  if (process.env.CONTACT_EMAIL) params.mailto = process.env.CONTACT_EMAIL;
  return 'https://api.openalex.org/works?' + qs(params);
}
function abstractFrom(inv) {
  if (!inv) return null;
  const words = [];
  for (const [w, pos] of Object.entries(inv)) for (const p of pos) words[p] = w;
  const s = words.filter(Boolean).join(' ');
  return s.length > 1200 ? s.slice(0, 1200) + '…' : s;
}
function mapOpenAlex(w) {
  const src = w.primary_location?.source?.display_name || null;
  const b = w.biblio || {};
  const pages = b.first_page ? `${b.first_page}${b.last_page ? '–' + b.last_page : ''}` : null;
  const container = src ? `${src}${b.volume ? ' ' + b.volume : ''}${b.issue ? ', no. ' + b.issue : ''}` : null;
  const authors = (w.authorships || []).map((a) => a.author?.display_name).filter(Boolean);
  const doi = w.doi ? w.doi.replace('https://doi.org/', '') : null;
  const kind = w.type === 'book' || w.type === 'book-chapter' ? (w.type === 'book' ? 'book' : 'article') : 'article';
  return {
    id: w.id,
    title: w.display_name || w.title,
    year: w.publication_year,
    type: w.type,
    venue: src,
    authors: authors.slice(0, 8),
    citedBy: w.cited_by_count || 0,
    field: w.primary_topic?.field?.display_name || null,
    doi,
    url: w.primary_location?.landing_page_url || w.doi || w.id,
    openAccess: w.open_access?.oa_url || null,
    abstract: abstractFrom(w.abstract_inverted_index),
    cite: cite({ authors, title: w.display_name || w.title, container, date: w.publication_year, pages, doi, url: w.id, kind }),
  };
}

async function academic({ wd, name }) {
  const sel = 'id,doi,display_name,publication_year,type,cited_by_count,authorships,primary_location,biblio,abstract_inverted_index,open_access,primary_topic';
  const phrase = `"${name}"`;
  // OpenAlex is searched by the artist's name, which also matches namesakes
  // in other fields (the REMBRANDT brain-tumour trial, a Mercury impact
  // basin, a patents paper). All three queries are therefore restricted to
  // primary_topic.field.id:12 (Arts and Humanities) — the same filter the
  // most-cited query already used.
  const normTitle = (t) => String(t || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const [subjectWorks, oaCited, oaTitle, oaRecent, olBooks] = await Promise.all([
    wd
      ? safe('Wikidata', async () => {
          const rows = await sparqlWD(`SELECT ?w ?title ?wLabel ?date ?doi ?venueLabel ?authorLabel ?aname ?typeLabel WHERE {
            ?w wdt:P921 wd:${wd} .
            OPTIONAL { ?w wdt:P1476 ?title } OPTIONAL { ?w wdt:P577 ?date } OPTIONAL { ?w wdt:P356 ?doi }
            OPTIONAL { ?w wdt:P1433 ?venue } OPTIONAL { ?w wdt:P50 ?author } OPTIONAL { ?w wdt:P2093 ?aname } OPTIONAL { ?w wdt:P31 ?type }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } } LIMIT 3000`);
          const by = {};
          for (const b of rows) {
            const id = qid(v(b, 'w'));
            const x = (by[id] ||= { id, title: v(b, 'title') || v(b, 'wLabel'), year: wdYear(v(b, 'date')), doi: v(b, 'doi') || null, venue: v(b, 'venueLabel') || null, type: v(b, 'typeLabel') || null, authors: new Set(), url: wdUrl(id) });
            if (v(b, 'authorLabel')) x.authors.add(v(b, 'authorLabel'));
            if (v(b, 'aname')) x.authors.add(v(b, 'aname'));
          }
          return Object.values(by)
            .map((x) => {
              const authors = [...x.authors];
              const isBook = /book|catalog|monograph|edition/i.test(x.type || '');
              return { ...x, authors, cite: cite({ authors, title: x.title, container: x.venue, date: x.year, doi: x.doi, url: x.url, kind: isBook ? 'book' : 'article' }) };
            })
            .sort((a, b) => (a.year || 9999) - (b.year || 9999));
        })
      : null,
    safe('OpenAlex', async () => (await getJSON(openAlexUrl({ filter: `title_and_abstract.search:${phrase},primary_topic.field.id:12`, sort: 'cited_by_count:desc', 'per-page': '40', select: sel }))).results.map(mapOpenAlex)),
    safe('OpenAlex', async () => (await getJSON(openAlexUrl({ filter: `title.search:${phrase},primary_topic.field.id:12`, sort: 'cited_by_count:desc', 'per-page': '40', select: sel }))).results.map(mapOpenAlex)),
    safe('OpenAlex', async () => (await getJSON(openAlexUrl({ filter: `title_and_abstract.search:${phrase},primary_topic.field.id:12`, sort: 'publication_date:desc', 'per-page': '20', select: sel }))).results.map(mapOpenAlex)),
    // Key books & monographs: Open Library subject search. Ranked by edition
    // count below (a rough measure of how widely a book is held and read).
    // Fiction and children's books that happen to carry the artist as a
    // subject tag are filtered out by their own subject headings.
    safe('Open Library', async () => {
      const d = await getJSON('https://openlibrary.org/search.json?' + qs({ subject: name.toLowerCase(), fields: 'key,title,subtitle,author_name,first_publish_year,edition_count,publisher,publish_place,subject', limit: '40' }), { timeout: 25000 });
      const junk = /fiction|juvenile|children'?s|picture book|colouring|coloring|activity book/i;
      return (d.docs || [])
        .filter((b) => b.title && b.first_publish_year && !(b.subject || []).some((s) => junk.test(s)))
        .map((b) => ({
          title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''),
          year: b.first_publish_year,
          authors: (b.author_name || []).slice(0, 3),
          editions: b.edition_count || 1,
          publisher: (b.publisher || [])[0] || null,
          place: (b.publish_place || [])[0] || null,
          url: `https://openlibrary.org${b.key}`,
          cite: cite({ authors: (b.author_name || []).slice(0, 3), title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''), place: (b.publish_place || [])[0], publisher: (b.publisher || [])[0], date: b.first_publish_year, kind: 'book', url: `https://openlibrary.org${b.key}` }),
        }));
    }),
  ]);
  // Deduplicate the Open Library books against the curated Wikidata subject
  // list (same title + year, preferring the Wikidata record), then keep the
  // most widely held 15.
  const swKeys = new Set((subjectWorks?.data || []).map((x) => `${normTitle(x.title)}|${x.year || ''}`));
  const books = (olBooks?.data || [])
    .filter((b) => !swKeys.has(`${normTitle(b.title)}|${b.year || ''}`))
    .sort((a, b) => (b.editions || 1) - (a.editions || 1))
    .slice(0, 15);
  let scholarly = uniqBy([...(oaTitle.data || []), ...(oaCited.data || []), ...(oaRecent.data || [])], (x) => x.doi || x.id).sort((a, b) => b.citedBy - a.citedBy);
  let crossref = null;
  if (!scholarly.length) {
    // Fallback when OpenAlex is unavailable / rate-limited: Crossref (no key needed)
    crossref = await safe('Crossref', async () => {
      const params = { 'query.bibliographic': name, rows: '60', select: 'DOI,title,author,container-title,issued,type,volume,issue,page,is-referenced-by-count,abstract,URL' };
      if (process.env.CONTACT_EMAIL) params.mailto = process.env.CONTACT_EMAIL;
      const d = await getJSON('https://api.crossref.org/works?' + qs(params), { timeout: 25000 });
      return (d.message?.items || [])
        .filter((w) => mentions((w.title || []).join(' ') + ' ' + (w.abstract || ''), name))
        .map((w) => {
          const authors = (w.author || []).map((a) => [a.given, a.family].filter(Boolean).join(' ') || a.name).filter(Boolean);
          const year = w.issued?.['date-parts']?.[0]?.[0] || null;
          const venue = (w['container-title'] || [])[0] || null;
          const container = venue ? `${venue}${w.volume ? ' ' + w.volume : ''}${w.issue ? ', no. ' + w.issue : ''}` : null;
          const title = (w.title || [])[0];
          return { id: w.DOI, title, year, type: w.type, venue, authors: authors.slice(0, 8), citedBy: w['is-referenced-by-count'] || 0, doi: w.DOI, url: w.URL, openAccess: null, field: null,
            abstract: w.abstract ? stripHtml(w.abstract).slice(0, 1200) : null,
            cite: cite({ authors, title, container, date: year, pages: w.page, doi: w.DOI, kind: /book/.test(w.type) && w.type !== 'book-chapter' ? 'book' : 'article' }) };
        })
        .sort((a, b) => b.citedBy - a.citedBy);
    });
    scholarly = crossref.data || [];
  }
  const reviews = scholarly.filter((x) => x.type === 'review' || /\breview\b|rezension|compte rendu|recensione|besprechung/i.test(x.title || ''));
  const enc = encodeURIComponent;
  return {
    subjectWorks: subjectWorks?.data || [],
    scholarly,
    reviews,
    books,
    totals: { scholarly: scholarly.length, subjectWorks: subjectWorks?.data?.length || 0, books: books.length },
    databases: [
      ['JSTOR', `https://www.jstor.org/action/doBasicSearch?Query=${enc(phrase)}`],
      ['Google Scholar', `https://scholar.google.com/scholar?q=${enc(phrase)}`],
      ['Oxford Art Online (Grove / Benezit)', `https://www.oxfordartonline.com/search?q=${enc(name)}`],
      ['Bibliography of the History of Art (BHA) / RILA', `https://primo.getty.edu/primo-explore/search?query=any,contains,${enc(name)}&vid=GRI`],
      ['Getty Research Portal (digitised art literature)', `https://portal.getty.edu/?q=${enc(name)}`],
      ['WorldCat', `https://search.worldcat.org/search?q=${enc(phrase)}`],
      ['Art Full Text / Art Index (EBSCO, via library)', `https://www.ebsco.com/products/research-databases/art-full-text`],
      ['Semantic Scholar', `https://www.semanticscholar.org/search?q=${enc(phrase)}`],
    ].map(([label, url]) => ({ label, url })),
    scholarlySource: crossref ? 'Crossref' : 'OpenAlex',
    errors: crossref?.ok && scholarly.length ? [] : [subjectWorks, oaCited, oaTitle, oaRecent, crossref, olBooks].filter((r) => r && !r.ok).map((r) => r.error),
  };
}

/* ======================================================= SECTION: MARKET */
const MARKET_SENT_RX = /(auction|sold for|was sold|sale (?:at|of)|christie|sotheby|bonhams|phillips|drouot|dorotheum|hammer price|record (?:price|for)|purchased (?:by|for)|bought (?:by|for)|acquired (?:by|for)|guineas|francs|florins|guilders|commission(?:ed)? (?:for|of)|fetched|price of)/i;

async function market({ wd, name, by, dy }) {
  const prof = await profile({ wd, ulan: null }).catch(() => null);
  const [prices, museums] = await Promise.all([
    wd
      ? safe('Wikidata', async () => {
          const rows = await sparqlWD(`SELECT ?w ?wLabel ?amt ?unitLabel ?t ?evLabel ?evt ?buyerLabel ?sellerLabel ?met ?artic WHERE {
            ?w wdt:P170 wd:${wd} .
            { ?w p:P2284 ?ps . ?ps psv:P2284 [ wikibase:quantityAmount ?amt; wikibase:quantityUnit ?unit ] . OPTIONAL { ?ps pq:P585 ?t } OPTIONAL { ?ps pq:P1640|pq:P1327 ?buyer } }
            UNION { ?w p:P793 ?es . ?es ps:P793 ?ev . OPTIONAL { ?es pq:P585 ?evt } OPTIONAL { ?es pqv:P2284 [ wikibase:quantityAmount ?amt; wikibase:quantityUnit ?unit ] } OPTIONAL { ?es pq:P1327|pq:P1640 ?buyer } OPTIONAL { ?es pq:P1037|pq:P127 ?seller } }
            OPTIONAL { ?w wdt:P3634 ?met } OPTIONAL { ?w wdt:P4610 ?artic }
            SERVICE wikibase:label { bd:serviceParam wikibase:language "${LANGS}". } } LIMIT 1000`);
          const recorded = uniqBy(
            rows
              .map((b) => ({
                work: v(b, 'wLabel'),
                workUrl: wdUrl(qid(v(b, 'w'))),
                wikidataUrl: wdUrl(qid(v(b, 'w'))),
                metId: v(b, 'met') || null,
                articId: v(b, 'artic') || null,
                institution: null,
                amount: v(b, 'amt') ? Number(v(b, 'amt')) : null,
                unit: v(b, 'unitLabel') && v(b, 'unitLabel') !== '1' ? v(b, 'unitLabel') : '',
                year: wdYear(v(b, 't') || v(b, 'evt')),
                event: v(b, 'evLabel') || (v(b, 'amt') ? 'price' : null),
                buyer: v(b, 'buyerLabel') || null,
                seller: v(b, 'sellerLabel') || null,
              }))
              .filter((x) => x.amount || /auction|sale|sold|purchase|acquisition|theft|donation|bequest|commission/i.test(x.event || ''))
              // The same sale can be recorded twice on Wikidata — once as a
              // bare price (P2284) and once as a significant event (P793)
              // carrying the same amount. Keep one row, preferring the
              // event-labelled one, so a price is never listed twice.
              .sort((a, b) => (a.event === 'price' ? 1 : 0) - (b.event === 'price' ? 1 : 0)),
            (x) => (x.amount ? `${x.work}|${x.amount}|${x.unit}` : `${x.work}|${x.event}|${x.year}`)
          ).sort((a, b) => (a.year || 9999) - (b.year || 9999));
          // Verify each recorded work's candidate museum identifiers the
          // same way as the collections sample (see verifyWorkLink): only a
          // link the institution's own API confirms replaces the Wikidata
          // URL as the work's link.
          await mapLimit(recorded, 6, async (r) => {
            if (!r.metId && !r.articId) return;
            const hit = await verifyWorkLink(r);
            if (hit) {
              r.workUrl = hit.url;
              r.institution = hit.institution;
            }
          });
          return recorded;
        })
      : null,
    museumData(name, by, dy),
  ]);

  // sentences about sales from Wikipedia
  const sentences = [];
  for (const s of prof?.wikipedia?.sections || []) {
    if (s.category === 'skip') continue;
    for (const p of s.paragraphs)
      for (const sent of p.split(/(?<=[.!?])\s+(?=[A-Z“"(])/))
        if (MARKET_SENT_RX.test(sent) && /\d/.test(sent)) sentences.push({ section: s.heading, text: sent });
  }

  const provenance = [];
  for (const o of museums.aic.data || []) if (o.provenance) provenance.push({ object: o.title, museum: o.museum, url: o.url, credit: o.credit, entries: o.provenance.split(/;\s*|\n+/).map((x) => x.trim()).filter(Boolean) });
  for (const o of museums.cma.data || []) if (o.provenanceList?.length) provenance.push({ object: o.title, museum: o.museum, url: o.url, entries: o.provenanceList.map((p) => [p.description, p.date].filter(Boolean).join(' — ')) });

  const enc = encodeURIComponent;
  const priceDatabases = [
    ['Artnet Price Database', `https://www.artnet.com/search/artists/?q=${enc(name)}`],
    ['MutualArt — auction results', `https://www.mutualart.com/Search/${enc(name)}`],
    ['Artprice', `https://www.artprice.com/search?query=${enc(name)}`],
    ['Invaluable — past auction results', `https://www.invaluable.com/search?query=${enc(name)}&upcoming=false`],
    ['LiveAuctioneers — sold lots', `https://www.liveauctioneers.com/search/?keyword=${enc(name)}&status=archive`],
    ['Christie’s', `https://www.christies.com/en/search?entry=${enc(name)}&page=1&sortby=relevance&tab=sold_lots`],
    ['Sotheby’s', `https://www.sothebys.com/en/search?query=${enc(name)}&tab=objects`],
    ['Bonhams', `https://www.bonhams.com/search/?q=${enc(name)}`],
    ['Phillips', `https://www.phillips.com/search/${enc(name)}`],
    ['Heritage Auctions', `https://www.ha.com/c/search-results.zx?N=0&Ntt=${enc(name)}`],
    ['Dorotheum', `https://www.dorotheum.com/en/search/?q=${enc(name)}`],
    ['askART (American artists)', `https://www.askart.com/artist_search?q=${enc(name)}`],
    ['Getty Provenance Index (historic sales 1650–1945)', `https://www.getty.edu/research/tools/provenance/search.html`],
  ].map(([label, url]) => ({ label, url }));

  return {
    recorded: prices?.data || [],
    wikipediaMentions: uniqBy(sentences, (s) => s.text).slice(0, 40),
    wikipediaCite: prof?.wikipedia?.cite || null,
    provenance: provenance.slice(0, 25),
    marketProfiles: (prof?.externalIds || []).filter((x) => x.group === 'market' && x.url),
    priceDatabases,
    note:
      'Comprehensive auction records (hammer prices, lot-by-lot results) are held in subscription databases such as Artnet, Artprice and MutualArt; they are not openly licensed. This section reports openly documented sales, prices and provenance, and links directly to the artist’s pages in the commercial price databases.',
    errors: [prices, museums.aic, museums.cma].filter((r) => r && !r.ok).map((r) => r.error),
  };
}

/* ===================================== SECTION: LIFETIME / PERIOD SOURCES */
async function lifetime({ wd, name, by, dy, variants = [] }) {
  by = by ? parseInt(by, 10) : null;
  dy = dy ? parseInt(dy, 10) : null;
  if (!by && dy) by = dy - 70;
  if (!by) return { range: null, note: 'Life dates are unknown, so references cannot be restricted to the artist’s lifetime.', ia: [], newspapers: [], europeana: [], books: [], dictionaries: [], links: [], errors: [] };
  const start = Math.max(by, -3000);
  const end = Math.min(dy || NOW_YEAR, NOW_YEAR);
  // search names: preferred name + up to 3 Latin-script multi-word variants
  const names = uniqBy([name, ...variants.filter((x) => /^[\p{Script=Latin}\s.'’-]+$/u.test(x) && x.split(' ').length >= 2 && !x.includes(','))], (x) => norm(x)).slice(0, 4);
  const iaQ = '(' + names.map((n) => `"${n.replace(/"/g, '')}"`).join(' OR ') + `) AND mediatype:texts AND date:[${String(Math.max(start, 1)).padStart(4, '0')}-01-01 TO ${String(end).padStart(4, '0')}-12-31]`;
  const ca = start <= 1963 && end >= 1756;
  const prof = wd ? await profile({ wd, ulan: null }).catch(() => null) : null;

  const [ia, news, eu, ol] = await Promise.all([
    safe('Internet Archive', async () => {
      const d = await getJSON('https://archive.org/advancedsearch.php?' + qs({ q: iaQ, 'fl[]': 'identifier', rows: '80', sort: 'date asc', output: 'json' }) + '&fl[]=title&fl[]=creator&fl[]=date&fl[]=publisher&fl[]=description', { timeout: 25000 });
      return (d.response?.docs || []).map((x) => {
        const creator = (Array.isArray(x.creator) ? x.creator.slice(0, 3) : x.creator ? [x.creator] : []).map((a) => fixArtistLifeDates(a, name, by, dy));
        const year = x.date ? parseInt(String(x.date).slice(0, 4), 10) : null;
        const publisher = Array.isArray(x.publisher) ? x.publisher[0] : x.publisher;
        const url = `https://archive.org/details/${x.identifier}`;
        return { title: Array.isArray(x.title) ? x.title[0] : x.title, authors: creator, year, publisher: publisher || null, url, fulltextSearch: `https://archive.org/details/${x.identifier}?q=${encodeURIComponent('"' + name + '"')}`, cite: cite({ authors: creator, title: Array.isArray(x.title) ? x.title[0] : x.title, publisher, date: year, kind: 'book', url }) };
      });
    }),
    ca
      ? safe('Library of Congress — Chronicling America', async () => {
          const d = await getJSON('https://www.loc.gov/collections/chronicling-america/?' + qs({ q: `"${name}"`, dates: `${Math.max(start, 1756)}/${Math.min(end, 1963)}`, fo: 'json', c: '40', sb: 'date' }), { timeout: 55000, noRetry: true });
          return (d.results || []).map((r) => {
            const paper = (Array.isArray(r.partof_title) ? r.partof_title[0] : r.partof_title) || r.title;
            const paperName = String(paper || '').replace(/\b\w/g, (c) => c.toUpperCase());
            return { title: r.title, newspaper: paperName, date: r.date, state: (r.location_state || [])[0] || null, url: r.url || r.id, cite: cite({ title: r.title, container: paperName, date: r.date, url: r.url || r.id, extra: 'Chronicling America: Historic American Newspapers, Library of Congress' }) };
          });
        })
      : null,
    safe('Europeana', async () => {
      const d = await getJSON('https://api.europeana.eu/record/v2/search.json?' + qs({ wskey: process.env.EUROPEANA_KEY || 'api2demo', query: `"${name}"`, qf: `YEAR:[${start} TO ${end}]`, rows: '40', profile: 'standard' }) + '&qf=TYPE:TEXT');
      return (d.items || []).map((o) => ({ title: (o.title || [])[0], year: (o.year || [])[0], provider: (o.dataProvider || [])[0], authors: (o.dcCreator || []).slice(0, 2).map((a) => fixArtistLifeDates(a, name, by, dy)), url: o.guid, cite: cite({ authors: (o.dcCreator || []).slice(0, 2).map((a) => fixArtistLifeDates(a, name, by, dy)), title: (o.title || [])[0], container: (o.dataProvider || [])[0], date: (o.year || [])[0], url: o.guid, extra: 'via Europeana' }) }));
    }),
    safe('Open Library', async () => {
      const d = await getJSON('https://openlibrary.org/search.json?' + qs({ q: `"${name}" first_publish_year:[${start} TO ${end}]`, fields: 'key,title,subtitle,author_name,first_publish_year,publisher,publish_place', limit: '40', sort: 'old' }), { timeout: 25000 });
      return (d.docs || []).map((b) => ({ title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''), year: b.first_publish_year, authors: (b.author_name || []).slice(0, 3).map((a) => fixArtistLifeDates(a, name, by, dy)), publisher: (b.publisher || [])[0] || null, url: `https://openlibrary.org${b.key}`, cite: cite({ authors: (b.author_name || []).slice(0, 3).map((a) => fixArtistLifeDates(a, name, by, dy)), title: b.title + (b.subtitle ? `: ${b.subtitle}` : ''), place: (b.publish_place || [])[0], publisher: (b.publisher || [])[0], date: b.first_publish_year, kind: 'book', url: `https://openlibrary.org${b.key}` }) }));
    }),
  ]);

  const dictionaries = (prof?.describedBy || []).filter((d) => d.year && d.year >= start && d.year <= end);
  const enc = encodeURIComponent;
  const ph = `"${name}"`;
  const links = [
    ['Google Books (limited to lifetime)', `https://www.google.com/search?tbm=bks&q=${enc(ph)}&tbs=cdr:1,cd_min:${start},cd_max:${end}`],
    ['HathiTrust full-text search', `https://babel.hathitrust.org/cgi/ls?q1=${enc(name)};anyall1=phrase;lmt=all`],
    ['Internet Archive full-text (inside books)', `https://archive.org/search?query=${enc(ph)}&sin=TXT&and%5B%5D=year%3A%5B${start}+TO+${end}%5D`],
    ['Gallica (BnF) — French books & press', `https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=%28gallica%20all%20${enc(ph)}%29`],
    ['Delpher — Dutch newspapers & books', `https://www.delpher.nl/nl/kranten/results?query=${enc(ph)}`],
    ['British Newspaper Archive', `https://www.britishnewspaperarchive.co.uk/search/results/${start}-01-01/${end}-12-31?basicsearch=${enc(ph)}&exactsearch=true&retrievecountrycounts=false`],
    ['Trove — Australian newspapers', `https://trove.nla.gov.au/search/category/newspapers?keyword=${enc(ph)}&date.from=${start}-01-01&date.to=${end}-12-31`],
    ['Newspapers.com', `https://www.newspapers.com/search/?query=${enc(ph)}&dr_year=${start}-${end}`],
    ['ANNO — Austrian newspapers online', `https://anno.onb.ac.at/anno-suche#searchMode=simple&query=${enc(ph)}&from=${start}&to=${end}`],
    ['Deutsches Zeitungsportal', `https://www.deutsche-digitale-bibliothek.de/newspaper/search?query=${enc(ph)}&fromDay=1&fromMonth=1&fromYear=${start}&toDay=31&toMonth=12&toYear=${end}`],
    ['Chronicling America (all results)', `https://www.loc.gov/collections/chronicling-america/?q=${enc(ph)}&dates=${start}/${end}`],
  ].map(([label, url]) => ({ label, url }));

  return {
    range: { start, end, living: !dy },
    searchedNames: names,
    dictionaries,
    ia: ia.data || [],
    newspapers: news?.data || [],
    newspapersCovered: ca,
    europeana: eu.data || [],
    books: ol.data || [],
    links,
    errors: [ia, news, eu, ol].filter((r) => r && !r.ok).map((r) => r.error),
  };
}

module.exports = { profile, exhibitions, academic, market, collections, lifetime, catalogue, resolveIds };
