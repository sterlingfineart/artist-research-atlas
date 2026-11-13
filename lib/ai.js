'use strict';
/*
 * Optional AI synthesis. When an OpenAI-compatible API key is configured, the
 * server writes a narrative synthesis grounded ONLY in the sources already
 * gathered for the report, citing them as [S1], [S2] …
 *
 * Env: AI_API_KEY (or OPENAI_API_KEY), AI_BASE_URL (default https://api.openai.com/v1),
 *      AI_MODEL (default gpt-4o-mini)
 */
const { getJSON } = require('./util');
const report = require('./report');

const KEY = process.env.AI_API_KEY || process.env.OPENAI_API_KEY || '';
const BASE = (process.env.AI_BASE_URL || 'https://api.openai.com/v1').replace(/\/$/, '');
const MODEL = process.env.AI_MODEL || 'gpt-4o-mini';

const enabled = () => Boolean(KEY);

function clip(s, n) {
  s = String(s || '');
  return s.length > n ? s.slice(0, n) + ' […]' : s;
}

async function buildSourcePack({ wd, ulan, name }) {
  const prof = await report.profile({ wd, ulan });
  name = name || prof.name;
  const ids = prof.ids;
  const [ex, ac, mk] = await Promise.all([
    report.exhibitions({ wd: ids.wikidata, name, by: prof.birthYear, dy: prof.deathYear }).catch(() => null),
    report.academic({ wd: ids.wikidata, name }).catch(() => null),
    report.market({ wd: ids.wikidata, name, by: prof.birthYear, dy: prof.deathYear }).catch(() => null),
  ]);
  const S = [];
  const add = (label, cite, text) => {
    S.push({ n: S.length + 1, label, cite, text });
  };
  if (prof.wikidataCite) {
    const facts = Object.values(prof.facts).map((f) => `${f.label}: ${f.values.map((x) => x.label + (x.when ? ` (${x.when})` : '')).join('; ')}`).join('\n');
    add('Wikidata facts', prof.wikidataCite, `Born ${prof.births.join(' / ')} in ${prof.birthPlace}; died ${prof.deaths.join(' / ')} in ${prof.deathPlace}.\n${facts}`);
  }
  if (prof.ulan) add('Getty ULAN', prof.ulan.cite, `${prof.ulan.description}\n${prof.ulan.notes.join('\n')}\nRelations: ${prof.ulan.relations.map((r) => `${r.relation} ${r.name}`).join('; ')}`);
  if (prof.wikipedia) {
    const body = prof.wikipedia.sections.filter((s) => s.category !== 'skip').map((s) => `## ${s.heading}\n${s.paragraphs.join('\n')}`).join('\n');
    add('Wikipedia article', prof.wikipedia.cite, clip(body, 24000));
  }
  if (prof.wikiquote) add('Wikiquote — quotations about the artist', prof.wikiquote.cite, clip(prof.wikiquote.sections.map((s) => `## ${s.heading}\n${s.paragraphs.join('\n')}`).join('\n'), 9000));
  if (ex?.wikidata?.length) add('Exhibition records (Wikidata)', 'Wikidata exhibition items', ex.wikidata.slice(0, 80).map((e) => `${e.date} — ${e.title}${e.venues.length ? ', ' + e.venues.join(', ') : ''}`).join('\n'));
  for (const w of (ac?.scholarly || []).filter((x) => x.abstract).slice(0, 14)) add('Scholarly publication', w.cite, clip(w.abstract, 1500));
  if (mk?.recorded?.length) add('Recorded sales/prices (Wikidata)', 'Wikidata artwork statements', mk.recorded.slice(0, 60).map((r) => `${r.year || 'n.d.'}: ${r.work} — ${r.event || ''} ${r.amount ? r.amount + ' ' + r.unit : ''}`).join('\n'));
  for (const p of (mk?.provenance || []).slice(0, 6)) add(`Provenance — ${p.object} (${p.museum})`, `${p.museum}, “${p.object}”, ${p.url}`, clip(p.entries.join('; '), 1500));
  return { prof, sources: S };
}

async function synthesize({ wd, ulan, name }) {
  if (!enabled()) throw new Error('AI synthesis is not configured on this server (set AI_API_KEY).');
  const { prof, sources } = await buildSourcePack({ wd, ulan, name });
  const pack = sources.map((s) => `[S${s.n}] ${s.label}\nCitation: ${s.cite}\n${s.text}`).join('\n\n---\n\n');
  const sys =
    'You are an art historian writing a rigorous research dossier. Use ONLY the numbered sources supplied. ' +
    'Every factual sentence must end with one or more citations like [S3]. If the sources do not support a point, say so explicitly ' +
    '("The supplied sources do not document …"). Never invent exhibitions, prices, dates, publications or quotations. ' +
    'Distinguish clearly between facts, contemporary (lifetime) opinions, and later scholarly interpretation. Write in clear academic English using Markdown.';
  const user =
    `Artist: ${prof.name} (${prof.births.join('/') || '?'} – ${prof.deaths.join('/') || (prof.living ? 'living' : '?')}), born ${prof.birthPlace || 'unknown'}.\n\n` +
    'Write these sections with Markdown headings:\n' +
    '## Executive summary\n## Biographical narrative\n## Artistic development, style and technique\n## Exhibition history overview\n' +
    '## Contemporary reception (during the artist’s lifetime)\n## Later critical and scholarly assessment\n## Market history and sales\n' +
    '## Gaps in the record and suggested further research\n\nSOURCES:\n\n' + pack;
  const d = await getJSON(`${BASE}/chat/completions`, {
    method: 'POST',
    timeout: 120000,
    ttl: 24 * 3600e3,
    noRetry: true,
    headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: MODEL, temperature: 0.2, messages: [{ role: 'system', content: sys }, { role: 'user', content: user }] }),
  });
  return {
    model: MODEL,
    markdown: d.choices?.[0]?.message?.content || '',
    sources: sources.map(({ n, label, cite }) => ({ n, label, cite })),
  };
}

module.exports = { enabled, synthesize, model: MODEL };
