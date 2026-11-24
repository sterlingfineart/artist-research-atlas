'use strict';
/*
 * lib/wire.js — the identity layer ("the wire") between an artist report and
 * the Atlas's own databases (Record of Exhibitions, Graves Loan Exhibitions,
 * Royal Academy, Paris Salon, Graves/Redford historic sales).
 *
 * The index (data/wire/, built by scripts/build-wire-index.py) stores every
 * printed artist heading as its own identity with the records filed under it,
 * exactly as printed. This module decides, at query time, which identities
 * are the report's artist — and which records must be withheld because the
 * printed name does not distinguish two people. Source databases are never
 * edited. See WIRE-DESIGN.md for the full rule set.
 */
const fs = require('fs');
const path = require('path');

const WIRE_DIR = path.join(__dirname, '..', 'data', 'wire');
let GROUPS = null;
function loadGroups() {
  if (!GROUPS) GROUPS = JSON.parse(fs.readFileSync(path.join(WIRE_DIR, 'groups.json'), 'utf8'));
  return GROUPS;
}
/* The index is stored in letter files: shard-<a-z>.json, each an object
 * keyed by the two-letter surname shard key, plus shard-0.json holding
 * the '00' bucket (surnames that do not start with two [a-z0-9]
 * characters — the build script's shard_of rule). Loading a letter file
 * and selecting the shard key inside it replaces the old one-file-per-
 * shard layout; the shard contents are unchanged. */
const letterCache = new Map();
function shardKeyOf(surname) {
  const k = (surname || '').slice(0, 2);
  return /^[a-z][a-z0-9]$/.test(k) ? k : '00';
}
function loadLetterFile(key) {
  const letter = key === '00' ? '0' : key[0];
  if (!letterCache.has(letter)) {
    try {
      letterCache.set(letter, JSON.parse(fs.readFileSync(path.join(WIRE_DIR, 'shard-' + letter + '.json'), 'utf8')));
    } catch (e) { letterCache.set(letter, null); }
  }
  return letterCache.get(letter);
}
function shardByKey(key) {
  const file = loadLetterFile(key);
  return file ? (file[key] || null) : null;
}
function loadShard(surname) {
  return shardByKey(shardKeyOf(surname));
}

/* ---------------- name parsing (mirror of build-wire-index.py) ---------------- */
const TITLES = new Set(['sir', 'dame', 'lord', 'lady', 'rev', 'reverend', 'dr', 'mr', 'mrs', 'miss', 'ms',
  'mme', 'mlle', 'm', 'monsieur', 'madame', 'mademoiselle', 'herr', 'frau', 'signor', 'signora',
  'senor', 'senora', 'don', 'dona', 'fr', 'father', 'brother', 'capt', 'col', 'gen', 'major',
  'prof', 'professor', 'hon', 'rt', 'ven', 'canon', 'the']);
const DEGREES = new Set(['ra', 'ara', 'pra', 'rha', 'ara.', 'rsa', 'arsa', 'prsa', 'rca', 'ri', 'roi',
  'rba', 'rms', 'rbs', 'neac', 'sws', 'owa', 'om', 'kcb', 'kcvo', 'cvo', 'obe', 'mbe', 'fsa', 'frs',
  'mp', 'dso', 'mc', 'vc', 'bt', 'bart', 'esq', 'jr', 'sr', 'phd', 'md', 'dd', 'littd', 'kc', 'qc']);
const ABBREV = { w: 'william', wm: 'william', thos: 'thomas', chas: 'charles', jas: 'james', jno: 'john',
  jn: 'john', jonth: 'jonathan', alex: 'alexander', alexr: 'alexander', fredk: 'frederick',
  fred: 'frederick', edw: 'edward', edwd: 'edward', geo: 'george', robt: 'robert', richd: 'richard',
  saml: 'samuel', benj: 'benjamin', danl: 'daniel', natl: 'nathaniel', nathl: 'nathaniel',
  michl: 'michael', hen: 'henry', jos: 'joseph', josh: 'joshua', abrm: 'abraham', abra: 'abraham',
  isa: 'isaac', sol: 'solomon', timy: 'timothy', bart: 'bartholomew', bartw: 'bartholomew',
  margt: 'margaret', eliz: 'elizabeth', elizth: 'elizabeth', cath: 'catherine', cathn: 'catherine',
  kath: 'katherine', susa: 'susanna', reba: 'rebecca', hy: 'henry', anthy: 'anthony',
  anto: 'anthony', steph: 'stephen', theo: 'theodore', eug: 'eugene', maur: 'maurice' };
const PARTICLES = new Set(['van', 'von', 'de', 'der', 'den', 'ten', 'ter', 'het', 'le', 'la', 'di', 'du',
  'della', 'delle', 'degli', 'dei', 'lo', 'da', 'dos', 'das', 'do', 'st', 'ste', 'vander', 'vanden']);
const OCR_DIGITS = { o: '0', l: '1', i: '1', s: '5', b: '8', z: '2', g: '9', q: '0' };
const YEAR_RX = /(?:1[5-9]\d\d|20[0-2]\d)/g;
const RANGE_RX = /^\s*(\d{4})\s*[-–—]\s*(\d{4})\s*$/;

function normText(s) {
  return String(s || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[^\w\s'-]/g, ' ').replace(/['’]/g, '').replace(/\s+/g, ' ').trim();
}
function extractYears(text) {
  const found = [];
  let t = ' ' + String(text || '') + ' ';
  t = t.replace(/\(\s*b\.?\s*(\d{4})/i, (m, y) => { found.push(['b', parseInt(y, 10)]); return ' '; });
  t = t.replace(/\(\s*d\.?\s*(\d{4})/i, (m, y) => { found.push(['d', parseInt(y, 10)]); return ' '; });
  t = t.replace(/\b(died|d\.|b\.|born|ne|nee)\s*(\d{4})\b/gi, (m, w, y) => {
    found.push([/^(died|d\.)$/i.test(w) ? 'd' : 'b', parseInt(y, 10)]);
    return ' ';
  });
  let fl = null;
  t = t.replace(/\b(?:fl\.?|floruit)\s*(\d{4})(?:\s*[-–—]\s*(\d{4}))?/i, (m, a, b) => {
    fl = [parseInt(a, 10), b ? parseInt(b, 10) : null]; return ' ';
  });
  const rangeM = t.replace(/[()]/g, ' ').match(RANGE_RX);
  if (rangeM) { found.push(['b', parseInt(rangeM[1], 10)]); found.push(['d', parseInt(rangeM[2], 10)]); t = ' '; }
  const years = t.match(YEAR_RX) || [];
  return { rest: t, found, years: years.map(Number), fl };
}
function givenTokens(tokens) {
  const out = [];
  for (let tok of tokens) {
    tok = (tok || '').trim();
    if (!tok) continue;
    if (TITLES.has(tok) || DEGREES.has(tok)) continue;
    const cleaned = tok.replace(/\./g, '');
    if (/^[a-z]\.?$/.test(tok) || (/^[A-Z]\.?$/.test(tok))) { out.push([cleaned.toLowerCase(), 1]); continue; }
    const n = normText(tok);
    if (!n) continue;
    if (TITLES.has(n) || DEGREES.has(n)) continue;
    if (n.length === 1) { out.push([n, 1]); continue; }
    if (ABBREV[n]) { out.push([ABBREV[n], 0]); continue; }
    if (/^[a-z]+$/.test(n)) out.push([n, 0]);
  }
  return out;
}
function isHonorificTail(tail) {
  const toks = normText(tail).split(/\s+/).filter(Boolean);
  return toks.length > 0 && toks.every((t) => TITLES.has(t) || DEGREES.has(t) || /^[a-z]$/.test(t) || /^\d{4}$/.test(t));
}
/* Parse any name form into { surname, givens:[[token,isInitial]], by, dy, fl }.
 * Exported for tests; the build script carries the same logic in Python. */
function parseName(raw) {
  let s = String(raw || '').trim();
  const res = extractYears(s);
  s = res.rest;
  let by = null; let dy = null;
  for (const [kind, y] of res.found) { if (kind === 'b' && by === null) by = y; if (kind === 'd' && dy === null) dy = y; }
  if (by === null && dy === null && res.years.length === 1) { /* single bare year: ignore */ }
  s = s.replace(/\bpage\s+\d+\b/gi, ' ');
  s = s.replace(/;/g, ',');
  s = s.replace(/\.\s*$/, '');
  const firstComma = s.indexOf(',');
  if (firstComma >= 0 && isHonorificTail(s.slice(firstComma + 1))) s = s.slice(0, firstComma);
  let surname; let givens;
  if (s.includes(',')) {
    const idx = s.indexOf(',');
    surname = normText(s.slice(0, idx));
    givens = givenTokens(s.slice(idx + 1).replace(/,/g, ' ').split(/[\s-]+/).filter(Boolean));
  } else {
    const toks = s.replace(/,/g, ' ').split(/\s+/).filter(Boolean);
    const start = toks.length - 1;
    let i = Math.max(0, start);
    const snParts = [toks[i]];
    while (i - 1 >= 0 && PARTICLES.has(normText(toks[i - 1]))) { i -= 1; snParts.unshift(toks[i]); }
    surname = normText(snParts.join(' '));
    givens = givenTokens(toks.slice(0, i));
  }
  // Hyphens in surnames fold to spaces, exactly as the build script stores
  // them ("Alma-Tadema" is filed as "alma tadema" on both sides).
  surname = surname.replace(/-/g, ' ').replace(/\s+/g, ' ').trim();
  return { surname, givens, by, dy, fl: res.fl };
}

/* ---------------- matching ---------------- */
function levWithin(a, b, maxD) {
  if (a === b) return true;
  const la = a.length; const lb = b.length;
  if (Math.abs(la - lb) > maxD) return false;
  let prev = new Array(lb + 1); let cur = new Array(lb + 1);
  for (let j = 0; j <= lb; j++) prev[j] = j;
  for (let i = 1; i <= la; i++) {
    cur[0] = i;
    let rowMin = cur[0];
    for (let j = 1; j <= lb; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      rowMin = Math.min(rowMin, cur[j]);
    }
    if (rowMin > maxD) return false;
    [prev, cur] = [cur, prev];
  }
  return prev[lb] <= maxD;
}
/* Cross-language given-name equivalences (authority-file practice: the Salon
 * prints French forms of foreign artists' names, Graves English ones). */
const GIVEN_EQUIV_CLASSES = [
  ['lawrence', 'laurence', 'laurent', 'lorenzo', 'lourens'],
  ['william', 'wilhelm', 'guillaume', 'guglielmo'],
  ['john', 'jean', 'juan', 'giovanni', 'johann', 'hans', 'ivan'],
  ['charles', 'karl', 'carlo', 'carlos'],
  ['george', 'georg', 'georges', 'giorgio', 'jorge'],
  ['henry', 'heinrich', 'henri', 'enrico'],
  ['frederick', 'friedrich', 'frederic', 'federico'],
  ['joseph', 'giuseppe', 'josef'],
  ['james', 'jacques', 'giacomo', 'jaime'],
  ['peter', 'pietro', 'pierre', 'pedro'],
  ['paul', 'paolo', 'pablo'],
  ['anthony', 'antoine', 'antonio', 'anton'],
  ['nicholas', 'nicolas', 'niccolo'],
  ['francis', 'francois', 'francesco', 'franz'],
  ['louis', 'luigi', 'ludwig', 'luis'],
  ['edward', 'edouard', 'edoardo'],
  ['michael', 'michel', 'michele', 'miguel'],
  ['stephen', 'etienne', 'stefano'],
  ['andrew', 'andre', 'andrea', 'andres'],
  ['philip', 'philippe', 'filippo', 'felipe'],
  ['walter', 'gautier', 'gualtiero'],
  ['theodore', 'teodoro'],
  ['daniel', 'daniele'], ['samuel', 'samuele'], ['benjamin', 'beniamino'],
  ['matthew', 'matthieu', 'matteo'], ['luke', 'luc', 'luca'],
  ['mark', 'marc', 'marco'], ['hugh', 'hugo'],
  ['albert', 'alberto'], ['robert', 'roberto'], ['thomas', 'tomas', 'tommaso'],
];
const GIVEN_CLASS = new Map();
GIVEN_EQUIV_CLASSES.forEach((cls, i) => cls.forEach((n) => GIVEN_CLASS.set(n, i)));
function givenEquiv(a, b) {
  return GIVEN_CLASS.has(a) && GIVEN_CLASS.get(a) === GIVEN_CLASS.get(b);
}
/* Tolerant "same given name" test: exact, one OCR edit, cross-language
 * equivalent, a prefix of the other (>=4 chars), or two edits on long names. */
function sameGiven(a, b) {
  if (!a || !b) return false;
  if (a === b) return true;
  if (givenEquiv(a, b)) return true;
  if (Math.min(a.length, b.length) >= 4 && (a.startsWith(b) || b.startsWith(a))) return true;
  if (Math.min(a.length, b.length) >= 5 && levWithin(a, b, 1)) return true;
  if (Math.min(a.length, b.length) >= 7 && levWithin(a, b, 2)) return true;
  return false;
}
/* Strict test used for the identity→target match itself: exact, one OCR edit
 * on names of 5+ chars, or a cross-language equivalent. */
function givenMatch(a, b) {
  if (a === b) return 'exact';
  if (givenEquiv(a, b)) return 'fuzzy';
  if (Math.min(a.length, b.length) >= 5 && levWithin(a, b, 1)) return 'fuzzy';
  if (Math.min(a.length, b.length) >= 4 && (a.startsWith(b) || b.startsWith(a))) return 'fuzzy';
  return null;
}
function matchForm(ident, form) {
  const ig = ident.gv || [];
  const fg = form.givens || [];
  if (!ig.length) return fg.length ? 'surname' : 'surname';
  if (!fg.length) return null;
  const [i0, i0init] = ig[0];
  const [f0, f0init] = fg[0];
  if (i0init && f0init) return i0 === f0 ? 'initial' : null;
  if (i0init) return f0[0] === i0 ? 'initial' : null;
  if (f0init) return i0[0] === f0 ? 'initial' : null;
  const m = givenMatch(i0, f0);
  if (!m) return null;
  // second-given veto: a CLEAR conflict only (both full names of 4+ chars
  // that are not the same name) — a garbled short token cannot veto.
  if (ig.length > 1 && fg.length > 1) {
    const [i1, i1init] = ig[1];
    const [f1, f1init] = fg[1];
    if (!i1init && !f1init && i1.length >= 4 && f1.length >= 4 && !sameGiven(i1, f1)) return null;
  }
  return m === 'exact' ? 'full' : 'fuzzy';
}
function matchIdentity(ident, T) {
  let best = null;
  const rank = { full: 3, fuzzy: 2, initial: 1, surname: 0 };
  const identFull = (ident.gv || []).length && !ident.gv[0][1];
  for (const form of T.forms) {
    if (form.surname !== ident.sn) continue;
    const formFull = (form.givens || []).length && !form.givens[0][1];
    // A heading that prints a full given name is attributed on that name;
    // it is never matched through an initials-only alias of the target,
    // whose initial is shared with other people of the surname.
    if (identFull && !formFull && (form.givens || []).length) continue;
    const lvl = matchForm(ident, form);
    if (lvl && (best === null || rank[lvl] > rank[best])) best = lvl;
  }
  return best;
}
function dateGate(ident, T) {
  if (ident.fl) return true;
  const ranges = [];
  if (ident.by != null || ident.dy != null) ranges.push([ident.by, ident.dy]);
  for (const d of ident.dates || []) ranges.push(d);
  for (const [b, d] of ranges) {
    if (b != null && T.by != null && Math.abs(b - T.by) > 3) return false;
    if (d != null && T.dy != null && Math.abs(d - T.dy) > 3) return false;
  }
  return true;
}
/* Could rival R be the person that identity I's printed heading denotes,
 * given what I actually prints? */
function nameCompatible(R, I) {
  const rg = R.gv || [];
  const ig = I.gv || [];
  if (!ig.length) return true;
  if (!rg.length) return false;
  const compat1 = (a, aInit, b, bInit) => {
    if (!aInit && !bInit) return sameGiven(a, b);
    if (!aInit && bInit) return a[0] === b;
    if (aInit && !bInit) return b[0] === a;
    return a === b;
  };
  if (!compat1(ig[0][0], ig[0][1], rg[0][0], rg[0][1])) return false;
  if (ig.length > 1 && rg.length > 1 && !ig[1][1] && !rg[1][1]) {
    if (!sameGiven(ig[1][0], rg[1][0])) return false;
  }
  return true;
}
/* Is rival R the same person as the target (under any of the target's name
 * forms)? Then R is not a rival at all. */
function rivalIsTarget(R, T) {
  for (const form of T.forms) {
    if (form.surname !== R.sn) continue;
    const fg = form.givens || [];
    const rg = R.gv || [];
    if (!fg.length || !rg.length) continue;
    if (rg[0][1] || fg[0][1]) continue;
    if (!sameGiven(rg[0][0], fg[0][0])) continue;
    // Second givens separate two people only when both are substantial
    // printed names; a short garbled token ("am") cannot.
    if (rg.length > 1 && fg.length > 1 && !rg[1][1] && !fg[1][1]
      && rg[1][0].length >= 4 && fg[1][0].length >= 4 && !sameGiven(rg[1][0], fg[1][0])) continue;
    return true;
  }
  return false;
}
/* Was rival R active in the SAME source in year y? Only then can R claim
 * this record. */
function rivalCovers(R, y, source) {
  if (y == null) return false;
  const span = (R.srcY || {})[source];
  if (!span) return false;
  return y >= span[0] - 3 && y <= span[1] + 3;
}

const memo = new Map();

function buildTarget(opts) {
  const forms = [];
  const seen = new Set();
  const addForm = (raw) => {
    if (!raw) return;
    const p = parseName(raw);
    if (!p.surname) return;
    const key = p.surname + '|' + p.givens.map((g) => g.join('')).join('|');
    if (seen.has(key)) return;
    seen.add(key);
    forms.push(p);
  };
  addForm(opts.name);
  for (const v of opts.variants || []) addForm(v);
  // mononym fallback: a bare surname form, used only when no given-carrying
  // identity of that surname matched.
  const surnames = [...new Set(forms.map((f) => f.surname))];
  return { forms, surnames, by: opts.by ?? null, dy: opts.dy ?? null };
}

function lookup(opts) {
  const T = buildTarget(opts);
  const mkey = JSON.stringify([T.forms.map((f) => f.surname + ':' + f.givens.flat().join('.')), T.by, T.dy]);
  if (memo.has(mkey)) return memo.get(mkey);
  const groupsMeta = loadGroups();
  const byLocal = new Map(); // shardKey|local -> { ident, rec }
  const matched = []; // { ident, level, shardKey }
  const surnameHasFull = new Map(); // surname -> bool (a given-carrying identity matched)

  for (const surname of T.surnames) {
    const shard = loadShard(surname);
    if (!shard) continue;
    const shardKey = shardKeyOf(surname);
    for (const [local, ident] of Object.entries(shard.artists)) {
      if (ident.sn !== surname) continue;
      if (!dateGate(ident, T)) continue;
      const level = matchIdentity(ident, T);
      if (!level) continue;
      matched.push({ ident, level, shardKey, local: +local, shard });
      if ((ident.gv || []).length) surnameHasFull.set(surname, true);
    }
  }
  // bare-surname identities render only when nothing with a given name matched
  const usable = matched.filter((m) => {
    if (m.level === 'surname' && surnameHasFull.get(m.ident.sn)) return false;
    return true;
  });

  // ambiguity gate: an identity whose printed heading does not fully
  // discriminate it (initials only, no given name, or fewer given names than
  // the target's fullest form) has its records withheld wherever a genuinely
  // different, name-compatible artist was active in the same source and year.
  const fullestBySurname = new Map();
  for (const f of T.forms) {
    fullestBySurname.set(f.surname, Math.max(fullestBySurname.get(f.surname) || 0, (f.givens || []).length));
  }
  const withheldMap = new Map(); // reason -> { count, sources:Set }
  const addWithheld = (reason, source) => {
    const cur = withheldMap.get(reason) || { count: 0, sources: new Set() };
    cur.count += 1;
    if (source) cur.sources.add(source);
    withheldMap.set(reason, cur);
  };
  const withhold = (ident, rivalRaw, rec) => {
    addWithheld(`Records under “${ident.raw[0]}” were withheld where they could as well belong to “${rivalRaw}” — the printed name does not distinguish them.`, rec.s);
  };

  const groupMap = new Map(); // groupKey -> { meta, works: [] }
  const sales = [];
  const contributing = new Set();
  const shardArtists = (shardKey) => {
    const shard = shardByKey(shardKey);
    return shard ? shard.artists : {};
  };

  for (const m of usable) {
    const ig = m.ident.gv || [];
    const discriminating = m.level === 'full' && ig.length > 0 && ig.every((g) => !g[1])
      && ig.length >= (fullestBySurname.get(m.ident.sn) || 0);
    let rivals = null;
    if (!discriminating) {
      rivals = [];
      for (const [local2, R] of Object.entries(shardArtists(m.shardKey))) {
        if (+local2 === m.local || R.sn !== m.ident.sn) continue;
        // A rival must be a person: an identity carrying a full given name.
        // An initials-only heading is another abbreviation, not evidence of
        // a second person — it cannot make a full printed name ambiguous.
        if (!(R.gv || []).length || R.gv[0][1]) continue;
        if (rivalIsTarget(R, T)) continue;
        if (!nameCompatible(R, m.ident)) continue;
        rivals.push(R);
      }
    }
    const recs = m.shard.records.filter((r) => r.i === m.local);
    if (recs.length) contributing.add(m.ident.sn + '|' + (m.ident.raw || []).join('|'));
    for (const rec of recs) {
      if (rivals && rivals.length) {
        const hit = rivals.find((R) => rivalCovers(R, rec.y, rec.s));
        if (hit) { withhold(m.ident, hit.raw[0], rec); continue; }
      }
      // record-year gate for the annual sources: the RA and the Salon are
      // contemporary annual exhibitions, and so are the annual exhibitions
      // inside the Record (AWS, NAD) — a work cannot be shown there outside
      // the artist's lifetime. Loan exhibitions are retrospective and are
      // deliberately not gated.
      const annualRecord = rec.s === 'record'
        && /annual exhibition/i.test((groupsMeta[rec.g] || {}).title || '');
      if ((rec.s === 'ra' || rec.s === 'salon' || annualRecord) && rec.y != null) {
        if (T.dy != null && rec.y > T.dy + 3) {
          addWithheld(`Records under “${m.ident.raw[0]}” dated outside the artist's lifetime in an annual exhibition of contemporary work were withheld.`, rec.s);
          continue;
        }
        if (T.by != null && rec.y < T.by - 2) continue;
      }
      if (rec.s === 'sales') { sales.push({ rec, ident: m.ident }); continue; }
      const gk = rec.g;
      if (!groupMap.has(gk)) {
        const meta = groupsMeta[gk] || {};
        groupMap.set(gk, {
          key: gk, source: meta.source || rec.s, title: meta.title || gk, venue: meta.venue || '',
          dates: meta.dates || '', year: meta.year || rec.y || null, url: meta.url || '',
          works: [],
        });
      }
      groupMap.get(gk).works.push({ rec, ident: m.ident });
    }
  }

  /* ---- cross-source dedupe: merge a Loan group into a Record group ---- */
  const groups = [...groupMap.values()];
  const recordGroups = groups.filter((g) => g.source === 'record');
  const mergedAway = new Set();
  for (const lg of groups.filter((g) => g.source === 'loan')) {
    const cand = recordGroups.find((rg) => {
      if (rg.year !== lg.year) return false;
      const venueSlug = (lg.venue || '').toLowerCase().replace(/[^a-z0-9]+/g, '');
      const hay = ((rg.venue || '') + ' ' + (rg.title || '') + ' ' + rg.key).toLowerCase().replace(/[^a-z0-9]+/g, '');
      if (!venueSlug || !hay.includes(venueSlug)) return false;
      const rNos = new Set(rg.works.map((w) => String(w.rec.no)));
      return lg.works.some((w) => rNos.has(String(w.rec.no)));
    });
    if (!cand) continue;
    const byNo = new Map(cand.works.map((w) => [String(w.rec.no), w]));
    for (const w of lg.works) {
      const ex = byNo.get(String(w.rec.no));
      if (ex) {
        ex.fromLoan = w;
        if (!ex.rec.d && w.rec.d) ex.rec = { ...ex.rec, d: w.rec.d };
        if (!ex.rec.l && w.rec.l) ex.rec = { ...ex.rec, l: w.rec.l };
      } else {
        cand.works.push(w);
        byNo.set(String(w.rec.no), w);
      }
    }
    mergedAway.add(lg.key);
  }

  const SOURCE_LABELS = {
    record: 'Record of Exhibitions', loan: 'Loan Exhibitions (UK) — Graves',
    ra: 'Royal Academy database — Graves', salon: 'Paris Salon database',
  };
  const outGroups = [];
  for (const g of groups) {
    if (mergedAway.has(g.key)) continue;
    // Shard records use the build script's compact keys: t title, d size
    // (dimensions as printed), l lender, m medium, sec section, img/pl the
    // catalogue plate image/caption where the Record has one.
    const works = g.works.map(({ rec, ident, fromLoan }) => ({
      no: rec.no, title: rec.t || '', size: rec.d || '', lender: rec.l || '',
      medium: rec.m || '', section: rec.sec || '',
      image: rec.img || null, plate: rec.pl || null,
      sources: fromLoan ? [g.source === 'record' ? 'record' : g.source, 'loan'] : [g.source],
      asPrinted: ident.raw[0],
    }));
    works.sort((a, b) => (parseInt(a.no, 10) || 0) - (parseInt(b.no, 10) || 0));
    const srcSet = [];
    for (const w of g.works) { if (!srcSet.includes(w.rec.s)) srcSet.push(w.rec.s); }
    if (g.works.some((w) => w.fromLoan) && !srcSet.includes('loan')) srcSet.push('loan');
    outGroups.push({
      key: g.key, source: g.source, title: g.title, venue: g.venue, dates: g.dates,
      year: g.year, url: g.url,
      sources: srcSet.map((s) => ({ id: s, label: SOURCE_LABELS[s] || s })),
      works,
    });
  }
  outGroups.sort((a, b) => (a.year || 9999) - (b.year || 9999));

  /* ---- probable cross-source work links (same size + lender + title word) ---- */
  const titleTokens = (t) => new Set(normText(t).split(/\s+/).filter((w) => w.length >= 4
    && !['with', 'from', 'near', 'landscape', 'portrait', 'study', 'head', 'view'].includes(w)));
  const sizeDims = (s) => {
    if (!s) return null;
    let str = String(s).replace(/[×]/g, 'x');
    str = str.replace(/(\d)\s*([¼½¾])/g, (m, d, f) => d + '.' + ({ '¼': '25', '½': '5', '¾': '75' })[f]);
    str = str.replace(/([¼½¾])/g, (m, f) => '0.' + ({ '¼': '25', '½': '5', '¾': '75' })[f]);
    str = str.replace(/(\d{2,3})\s*x\s*(\d{2,3})(?!\d|\.)/g, (m, a, b) => {
      const fix = (v) => (v.length === 3 && v.endsWith('4') && +v.slice(0, 2) >= 10 ? String(+v.slice(0, 2)) + '.5' : v);
      return fix(a) + 'x' + fix(b);
    });
    const m = str.match(/(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)/);
    return m ? [parseFloat(m[1]), parseFloat(m[2])] : null;
  };
  const lenderKey = (l) => { const p = parseName(l || ''); return p.surname || normText(l); };
  const flat = [];
  for (const g of outGroups) for (const w of g.works) flat.push({ g, w });
  for (const a of flat) {
    const da = sizeDims(a.w.size);
    if (!da || !a.w.lender) continue;
    const ta = titleTokens(a.w.title);
    for (const b of flat) {
      if (b.g === a.g || (b.g.year || 0) >= (a.g.year || 0)) continue;
      const db = sizeDims(b.w.size);
      if (!db) continue;
      const close = (x, y) => Math.abs(x - y) <= 0.6;
      if (!((close(da[0], db[0]) && close(da[1], db[1])) || (close(da[0], db[1]) && close(da[1], db[0])))) continue;
      if (!b.w.lender || lenderKey(a.w.lender) !== lenderKey(b.w.lender)) continue;
      const shared = [...titleTokens(b.w.title)].filter((t) => ta.has(t));
      if (!shared.length) continue;
      a.w.link = {
        tier: 'Probable', toTitle: b.w.title, toNo: b.w.no, toGroup: b.g.title, toYear: b.g.year,
        basis: `Same size as printed (${b.w.size} / ${a.w.size}), the same lender (${lenderKey(a.w.lender)}) and a shared title word (“${shared[0]}”) — scored the same work at the Probable tier of the Atlas linking layer.`,
      };
      break;
    }
  }

  // Sales records: dt date, h house, p the price already formatted as the
  // sales tab prints it (£sd / francs / "No price printed"), pb buyer,
  // ow owner, sid/sl the source volume id and its short label.
  const outSales = sales.map(({ rec, ident }) => ({
    date: rec.dt || '', year: rec.y || null, house: rec.h || '', title: rec.t || '',
    lot: rec.lot || '', price: rec.p || '', buyer: rec.pb || '', owner: rec.ow || '',
    source: rec.sid || 'sales', sourceLabel: rec.sl || 'Historic Art Sales',
    asPrinted: ident.raw[0],
  }));
  outSales.sort((a, b) => (a.year || 9999) - (b.year || 9999) || String(a.date).localeCompare(String(b.date)));
  const salesTotal = outSales.length;

  const result = {
    groups: outGroups,
    sales: outSales.slice(0, 300),
    salesTotal,
    withheld: [...withheldMap.entries()].map(([reason, w]) => ({ reason, count: w.count, sources: [...w.sources] })),
    totals: {
      groups: outGroups.length,
      works: outGroups.reduce((c, g) => c + g.works.length, 0),
      sales: salesTotal,
      identities: contributing.size,
    },
  };
  if (memo.size > 300) memo.clear();
  memo.set(mkey, result);
  return result;
}

module.exports = { lookup, parseName };
