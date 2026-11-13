'use strict';
/* Shared helpers: cached JSON fetching, SPARQL clients, date formatting, citations. */

const UA = process.env.USER_AGENT ||
  'ArtistResearchAtlas/1.0 (open-source art research tool; contact: admin@example.org)';

const cache = new Map();
const MAX_CACHE = 2000;

async function getJSON(url, opts = {}) {
  try {
    return await getJSONOnce(url, opts);
  } catch (e) {
    if (opts.noRetry || !/HTTP (429|5\d\d)|timeout|fetch failed|ECONNRESET|socket/i.test(e.message)) throw e;
    await new Promise((r) => setTimeout(r, 1200));
    return getJSONOnce(url, { ...opts, timeout: Math.min((opts.timeout || 20000) * 1.5, 60000) });
  }
}

async function getJSONOnce(url, { timeout = 20000, headers = {}, ttl = 6 * 3600e3, method = 'GET', body } = {}) {
  const key = method + ' ' + url + (body ? ' ' + body : '');
  const hit = cache.get(key);
  if (hit && hit.exp > Date.now()) return hit.val;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeout);
  try {
    const res = await fetch(url, {
      method,
      body,
      headers: { 'User-Agent': UA, Accept: 'application/json', ...headers },
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} from ${new URL(url).host}`);
    const val = await res.json();
    if (cache.size > MAX_CACHE) cache.delete(cache.keys().next().value);
    cache.set(key, { val, exp: Date.now() + ttl });
    return val;
  } catch (e) {
    if (e.name === 'AbortError') throw new Error(`timeout from ${new URL(url).host}`);
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

const qs = (o) => new URLSearchParams(o).toString();

async function sparqlWD(query, opts = {}) {
  const url = 'https://query.wikidata.org/sparql?' + qs({ query, format: 'json' });
  const d = await getJSON(url, { timeout: 30000, ...opts, headers: { Accept: 'application/sparql-results+json' } });
  return d.results.bindings;
}

async function sparqlGetty(query, opts = {}) {
  const url = 'https://vocab.getty.edu/sparql.json?' + qs({ query });
  const d = await getJSON(url, { timeout: 25000, ...opts });
  return d.results.bindings;
}

const v = (b, k) => (b && b[k] ? b[k].value : undefined);
const qid = (uri) => (uri ? uri.replace(/^.*\/entity\//, '') : undefined);

/** Run a source; never throw — return {ok, data|error}. */
async function safe(name, fn) {
  try {
    return { ok: true, source: name, data: await fn() };
  } catch (e) {
    return { ok: false, source: name, error: e.message || String(e) };
  }
}

const norm = (s) =>
  String(s || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\u0400-\u04ff\u0590-\u06ff\u3040-\u9fff ]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

/** Wikidata time value + precision -> human readable string. */
function wdDate(value, precision) {
  if (!value || /^https?:/.test(value)) return null;
  const m = String(value).match(/^([+-]?)(\d+)-(\d\d)-(\d\d)/);
  if (!m) return null;
  const bce = m[1] === '-';
  const y = parseInt(m[2], 10);
  const p = parseInt(precision || 11, 10);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const era = bce ? ' BCE' : '';
  if (p >= 11) return `${parseInt(m[4], 10)} ${months[parseInt(m[3], 10) - 1]} ${y}${era}`;
  if (p === 10) return `${months[parseInt(m[3], 10) - 1]} ${y}${era}`;
  if (p === 9) return `${y}${era}`;
  if (p === 8) return `${Math.floor(y / 10) * 10}s${era}`;
  if (p === 7) return `${Math.ceil(y / 100)}th century${era}`;
  return `${y}${era}`;
}
function wdYear(value) {
  if (!value) return null;
  const m = String(value).match(/^([+-]?)(\d+)-/);
  if (!m) return null;
  return (m[1] === '-' ? -1 : 1) * parseInt(m[2], 10);
}

function uniqBy(arr, keyFn) {
  const seen = new Set();
  return arr.filter((x) => {
    const k = keyFn(x);
    if (k == null || seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

const accessed = () =>
  new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

/** Chicago-style (notes-bibliography) citation builder. */
function cite({ authors, title, container, publisher, place, date, url, doi, kind = 'web', pages, extra }) {
  const a = Array.isArray(authors) ? authors.filter(Boolean) : authors ? [authors] : [];
  let authorStr = '';
  if (a.length === 1) authorStr = a[0];
  else if (a.length === 2) authorStr = `${a[0]} and ${a[1]}`;
  else if (a.length > 2) authorStr = `${a[0]} et al.`;
  const parts = [];
  if (authorStr) parts.push(authorStr.replace(/\.$/, '') + '.');
  if (kind === 'book') {
    parts.push(`${title}.`);
    const pub = [place, publisher].filter(Boolean).join(': ');
    if (pub || date) parts.push([pub, date].filter(Boolean).join(', ') + '.');
  } else if (kind === 'article') {
    parts.push(`“${title}.”`);
    if (container) parts.push(`${container}${date ? ` (${date})` : ''}${pages ? `: ${pages}` : ''}.`);
    else if (date) parts.push(`${date}.`);
  } else {
    parts.push(`“${title}.”`);
    if (container) parts.push(`${container}.`);
    if (date) parts.push(`${date}.`);
  }
  if (extra) parts.push(extra.replace(/\.?$/, '.'));
  if (doi) parts.push(`https://doi.org/${doi.replace(/^https?:\/\/doi\.org\//, '')}.`);
  else if (url) parts.push(`${url} (accessed ${accessed()}).`);
  return parts.join(' ').replace(/\s+/g, ' ').trim();
}

function sparqlStr(s) {
  return '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
}

module.exports = { UA, getJSON, qs, sparqlWD, sparqlGetty, v, qid, safe, norm, wdDate, wdYear, uniqBy, cite, sparqlStr };
