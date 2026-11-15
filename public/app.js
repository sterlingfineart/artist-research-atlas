/* Artist Research Atlas — client application (vanilla JS, no build step). */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const app = $('#app');
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const enc = encodeURIComponent;
  const link = (url, text) => (url ? `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(text ?? url)}</a>` : esc(text));
  const spinner = (t = 'Researching…') => `<div class="loading"><div class="spinner"></div><span>${esc(t)}</span></div>`;
  const plural = (n, w) => `${n.toLocaleString()} ${w}${n === 1 ? '' : 's'}`;
  /** Correct ordinal typos in source-supplied headings, e.g. Wikiquote's "21th century" -> "21st century". */
  const fixOrdinals = (s) =>
    String(s || '').replace(/\b(\d+)(st|nd|rd|th)\b/g, (m, n) => {
      const v = +n;
      const right = v % 10 === 1 && v % 100 !== 11 ? 'st' : v % 10 === 2 && v % 100 !== 12 ? 'nd' : v % 10 === 3 && v % 100 !== 13 ? 'rd' : 'th';
      return v + right;
    });
  let config = { ai: false };

  function toast(msg) {
    let t = $('.toast');
    if (!t) {
      t = document.createElement('div');
      t.className = 'toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._h);
    t._h = setTimeout(() => t.classList.remove('show'), 1800);
  }
  async function api(path, params = {}) {
    const url = path + '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== '')).toString();
    const r = await fetch(url);
    const d = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
    if (!r.ok) throw new Error(d.error || `HTTP ${r.status}`);
    return d;
  }
  const citeBtn = (c) => (c ? `<button class="cite-btn" data-cite="${esc(c)}" title="Copy citation">cite</button>` : '');
  document.addEventListener('click', (e) => {
    const b = e.target.closest('.cite-btn');
    if (b) {
      navigator.clipboard?.writeText(b.dataset.cite).then(() => toast('Citation copied'));
    }
  });
  /** Render a list showing the first n items, the rest inside <details> (expanded when printing). */
  function list(items, render, n = 10, cls = 'items') {
    if (!items?.length) return '';
    const head = items.slice(0, n).map(render).join('');
    const rest = items.slice(n);
    return `<ul class="${cls}">${head}</ul>${rest.length ? `<details class="more"><summary>Show ${rest.length} more</summary><ul class="${cls}">${rest.map(render).join('')}</ul></details>` : ''}`;
  }
  const errs = (arr) => (arr?.length ? `<div class="notice">Some sources could not be reached and may be incomplete: ${esc([...new Set(arr)].join('; '))}. Reload the report to retry.</div>` : '');
  const lifeStr = (c) => {
    const b = c.birth || (c.births || [])[0];
    const d = c.death || (c.deaths || [])[0];
    if (!b && !d) return c.floruit ? c.floruit : 'Life dates not recorded';
    return `${b || '?'} – ${d || (c.living ? 'living' : '?')}`;
  };

  /* ================================================================ router */
  function route() {
    const h = location.hash.replace(/^#/, '') || '/';
    const [path, q] = h.split('?');
    const p = Object.fromEntries(new URLSearchParams(q || ''));
    window.scrollTo(0, 0);
    if (path === '/search' && p.q) return viewSearch(p.q);
    if (path === '/artist' && (p.wd || p.ulan)) return viewReport(p);
    if (path === '/about') return viewAbout();
    return viewHome();
  }
  window.addEventListener('hashchange', route);

  function viewHome(prefill = '') {
    app.innerHTML = $('#tpl-home').innerHTML;
    const f = $('#search-form');
    $('#q').value = prefill;
    $('#q').focus();
    f.addEventListener('submit', (e) => {
      e.preventDefault();
      const q = $('#q').value.trim();
      if (q.length >= 2) location.hash = '#/search?q=' + enc(q);
    });
  }

  /* ========================================================== search view */
  const ROLE_FILTERS = [
    ['all', 'All', /./],
    ['painter', 'Painters', /paint|watercolo|miniatur|pastel|fresco/i],
    ['sculptor', 'Sculptors', /sculpt|medal|carver|statuar/i],
    ['draftsman', 'Draftsmen', /draft|draught|drawing|illustrat/i],
    ['engraver', 'Engravers & printmakers', /engrav|etch|print|mezzotint|woodcut|lithograph/i],
  ];
  async function viewSearch(q) {
    app.innerHTML = `<form class="search-form" id="search-form" role="search" style="margin-bottom:22px"><input id="q" type="search" value="${esc(q)}" minlength="2" required aria-label="Artist name"><button class="btn btn-primary">Search artists</button></form><div id="results">${spinner('Searching artist authority records (Wikidata and Getty ULAN)…')}</div>`;
    $('#search-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const v = $('#q').value.trim();
      if (v.length >= 2) location.hash = '#/search?q=' + enc(v);
    });
    let data;
    try {
      data = await api('/api/search', { q });
    } catch (e) {
      $('#results').innerHTML = `<div class="notice error">Search failed: ${esc(e.message)}</div>`;
      return;
    }
    const cands = data.candidates || [];
    const out = $('#results');
    if (!cands.length) {
      out.innerHTML = `${errs(data.errors)}<div class="notice">No painters, sculptors, draftsmen or engravers matching “${esc(q)}” were found. Try another spelling, the surname alone, or an inverted form (e.g. “Gogh, Vincent van”).</div>`;
      return;
    }
    const exact = cands.filter((c) => c.match === 'exact').length;
    let filter = 'all';
    const render = () => {
      const rx = ROLE_FILTERS.find((f) => f[0] === filter)[2];
      const shown = cands.filter((c) => filter === 'all' || rx.test((c.roles || []).join(' ') + ' ' + (c.description || '')));
      out.innerHTML = `
        <div class="results-head">
          <div><h2>${plural(cands.length, 'matching artist')}</h2><div class="meta">${exact ? `${exact} exact name match${exact > 1 ? 'es' : ''} · ` : ''}Select the correct person to generate the research report.</div></div>
          <div class="filters">${ROLE_FILTERS.map(([k, l]) => `<button class="chip ${k === filter ? 'active' : ''}" data-f="${k}">${l}</button>`).join('')}</div>
        </div>${errs(data.errors)}
        ${shown.map(cardHtml).join('') || '<div class="notice">No candidates in this category.</div>'}`;
      out.querySelectorAll('.chip').forEach((b) => b.addEventListener('click', () => ((filter = b.dataset.f), render())));
      out.querySelectorAll('[data-pick]').forEach((b) =>
        b.addEventListener('click', () => {
          const c = cands[+b.dataset.pick];
          sessionStorage.setItem('cand:' + (c.wikidata || c.ulan), JSON.stringify(c));
          location.hash = `#/artist?${c.wikidata ? 'wd=' + c.wikidata : ''}${c.ulan ? (c.wikidata ? '&' : '') + 'ulan=' + c.ulan : ''}`;
        })
      );
    };
    const cardHtml = (c) => {
      const i = cands.indexOf(c);
      const matchBadge =
        c.match === 'exact' ? `<span class="badge exact">Exact match${c.matchedName !== c.name ? ` on “${esc(c.matchedName)}”` : ''}</span>`
        : c.match === 'all' ? `<span class="badge">Name contains all search terms</span>`
        : c.match === 'variant' ? `<span class="badge variant">Matched variant “${esc(c.matchedName)}”</span>`
        : `<span class="badge variant">Partial match${c.matchedName && c.matchedName !== c.name ? ` — “${esc(c.matchedName)}”` : ''}</span>`;
      const alt = [c.altBirth?.length ? `other recorded birth dates: ${c.altBirth.join(', ')}` : '', c.altDeath?.length ? `other recorded death dates: ${c.altDeath.join(', ')}` : ''].filter(Boolean).join(' · ');
      return `<article class="cand">
        ${c.image ? `<img class="thumb" src="${esc(c.image)}" alt="" loading="lazy">` : `<div class="thumb">${esc((c.name || '?')[0])}</div>`}
        <div>
          <h3>${esc(c.name)}</h3>
          <div class="dates">${esc(lifeStr(c))}${c.floruit && (c.birth || c.death) ? ` <span class="meta">(${esc(c.floruit)})</span>` : ''}</div>
          <div class="meta">${c.birthPlace ? `Born: <b>${esc(c.birthPlace)}</b>` : 'Birthplace not recorded'}${c.deathPlace ? ` · Died: ${esc(c.deathPlace)}` : ''}${c.citizenship?.length ? ` · ${esc(c.citizenship.slice(0, 2).join(', '))}` : ''}</div>
          ${alt ? `<div class="meta" style="font-size:12.5px">Note: ${esc(alt)}</div>` : ''}
          <div class="badges">${matchBadge}${(c.roles || []).slice(0, 6).map((r) => `<span class="badge role">${esc(r)}</span>`).join('')}${c.sources.map((s) => `<span class="badge src">${esc(s)}</span>`).join('')}</div>
          <div class="meta">${esc(c.ulanDescription && c.ulanDescription !== c.description ? `${c.description}${c.description ? ' — ' : ''}ULAN: ${c.ulanDescription}` : c.description)}</div>
          ${c.variants?.length ? `<div class="variants"><b>Name variants:</b> ${esc(c.variants.slice(0, 10).join(' · '))}${c.variants.length > 10 ? ` <span>(+${c.variants.length - 10} more)</span>` : ''}</div>` : ''}
        </div>
        <div class="cand-actions">
          <button class="btn btn-primary" data-pick="${i}">Select this artist →</button>
          ${c.wikidata ? link(`https://www.wikidata.org/wiki/${c.wikidata}`, `Wikidata ${c.wikidata}`) : ''}
          ${c.ulan ? link(`https://vocab.getty.edu/page/ulan/${c.ulan}`, `ULAN ${c.ulan}`) : ''}
        </div></article>`;
    };
    render();
  }

  /* ========================================================== report view */
  const SECTIONS = [
    ['synthesis', 'Research synthesis (AI)'],
    ['identity', 'Identity & names'],
    ['biography', 'Biography'],
    ['exhibitions', 'Exhibition record'],
    ['academic', 'Academic & peer reviews'],
    ['critical', 'Critical analyses'],
    ['market', 'Auction & art sales'],
    ['collections', 'Works & collections'],
    ['references', 'References'],
  ];
  const REF_CATS = [
    ['bio', 'Biographical sources'],
    ['exh', 'Exhibitions & showings'],
    ['acad', 'Academic & scholarly literature'],
    ['life', 'Sources from the artist’s lifetime'],
    ['mkt', 'Market, sales & provenance'],
    ['db', 'Art databases, authority files & identifiers'],
  ];

  async function viewReport(p) {
    const cached = JSON.parse(sessionStorage.getItem('cand:' + (p.wd || p.ulan)) || 'null');
    const state = { p, refs: Object.fromEntries(REF_CATS.map(([k]) => [k, new Map()])), prof: null, data: {} };
    window.__report = state;
    const secs = SECTIONS.filter(([k]) => k !== 'synthesis' || config.ai);
    app.innerHTML = `<div class="report">
      <aside class="toc"><h4>Report contents</h4>${secs.map(([k, l], i) => `<a href="#sec-${k}" data-toc="${k}"><span>${k === 'synthesis' ? '★' : i + (config.ai ? 0 : 1)}. ${l}</span><span class="st loading-dot" id="st-${k}"></span></a>${k === 'references' ? REF_CATS.map(([rk, rl]) => `<a class="sub" href="#ref-${rk}"><span>${rl}</span><span class="st" id="rc-${rk}"></span></a>`).join('') : ''}`).join('')}</aside>
      <div>
        <div class="rep-head" id="rep-head">${cached ? headHtml({ name: cached.name, births: [cached.birth].filter(Boolean), deaths: [cached.death].filter(Boolean), birthPlace: cached.birthPlace, deathPlace: cached.deathPlace, description: cached.description, image: cached.image?.replace('?width=160', '?width=400') }, true) : spinner('Loading artist record…')}</div>
        ${secs.map(([k, l], i) => `<section class="rs" id="sec-${k}"><h2><span><span class="num">${k === 'synthesis' ? '★' : i + (config.ai ? 0 : 1)}</span>${l}</span><small id="sm-${k}"></small></h2><div id="body-${k}">${k === 'synthesis' ? '' : spinner()}</div></section>`).join('')}
      </div></div>`;
    // smooth in-page anchors without breaking the hash router
    app.querySelectorAll('.toc a').forEach((a) =>
      a.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById(a.getAttribute('href').slice(1))?.scrollIntoView({ behavior: 'smooth' });
      })
    );
    if (config.ai) renderSynthesisIntro(state);

    let prof;
    try {
      prof = await api('/api/report/profile', { wd: p.wd, ulan: p.ulan });
    } catch (e) {
      $('#rep-head').innerHTML = `<div class="notice error">Could not load the artist record: ${esc(e.message)}</div>`;
      return;
    }
    state.prof = prof;
    document.title = `${prof.name} — Artist Research Atlas`;
    $('#rep-head').innerHTML = headHtml(prof) + toolbarHtml();
    bindToolbar(state);
    renderIdentity(state);
    renderBiography(state);
    renderCriticalBase(state);
    addProfileRefs(state);
    renderRefs(state);
    done('identity');
    done('biography');

    const variants = prof.variants.filter((x) => ['en', 'mul', 'ULAN', 'fr', 'de', 'nl', 'it'].includes(x.lang)).map((x) => x.name);
    const common = { wd: prof.ids.wikidata, ulan: prof.ids.ulan, name: prof.name, by: prof.birthYear, dy: prof.deathYear };
    const jobs = {
      exhibitions: api('/api/report/exhibitions', common).then((d) => renderExhibitions(state, d)),
      academic: api('/api/report/academic', common).then((d) => renderAcademic(state, d)),
      market: api('/api/report/market', common).then((d) => renderMarket(state, d)),
      collections: api('/api/report/collections', common).then((d) => renderCollections(state, d)),
      lifetime: api('/api/report/lifetime', { ...common, variants: variants.slice(0, 8).join('|') }).then((d) => renderLifetime(state, d)),
    };
    for (const [k, pr] of Object.entries(jobs))
      pr.catch((e) => {
        const target = k === 'lifetime' ? 'references' : k;
        const el = $('#body-' + target);
        if (el && target !== 'references') el.innerHTML = `<div class="notice error">This section could not be loaded: ${esc(e.message)}</div>`;
        else state.lifetimeError = e.message;
        done(target, 'error');
      }).finally(() => renderRefs(state));
    await Promise.allSettled(Object.values(jobs));
    done('references');
    done('critical');
  }

  function done(k, status = 'ok') {
    const st = $('#st-' + k);
    if (st) {
      st.classList.remove('loading-dot');
      st.textContent = status === 'ok' ? '✓' : '!';
    }
  }

  function headHtml(pr, preliminary = false) {
    const life = `${(pr.births || []).join(' / ') || '?'} – ${(pr.deaths || []).join(' / ') || (pr.living ? 'living' : '?')}`;
    const roles = (pr.facts?.P106?.values.map((x) => x.label) || []).filter((r) => !/^(old master|visual artist|artist)$/i.test(r));
    return `${pr.image ? `<img class="portrait" src="${esc(pr.image.includes('?') ? pr.image : pr.image + '?width=400')}" alt="Portrait or image of ${esc(pr.name)}">` : '<div></div>'}
      <div>
        <div class="meta" style="text-transform:uppercase;letter-spacing:.12em;font-size:11.5px">Artist research report${preliminary ? ' — loading' : ''}</div>
        <h1>${esc(pr.name)}</h1>
        <div class="dates">${esc(life)}</div>
        <p class="meta" style="margin:.4em 0 0">${esc(pr.description || '')}${pr.ulanDescription && pr.ulanDescription !== pr.description ? ` · <i>ULAN:</i> ${esc(pr.ulanDescription)}` : ''}</p>
        <div class="facts-grid">
          <div><b>Born</b>${esc((pr.births || []).join(' / ') || 'not recorded')}${pr.birthPlace ? `, ${esc(pr.birthPlace)}` : ''}</div>
          <div><b>Died</b>${esc((pr.deaths || []).join(' / ') || (pr.living ? 'living' : 'not recorded'))}${pr.deathPlace ? `, ${esc(pr.deathPlace)}` : ''}</div>
          ${roles.length ? `<div><b>Roles</b>${esc(roles.slice(0, 8).join(', '))}</div>` : ''}
          ${pr.facts?.P135 ? `<div><b>Movement / school</b>${esc(pr.facts.P135.values.map((x) => x.label).join(', '))}</div>` : ''}
          ${pr.ids ? `<div><b>Identifiers</b>${pr.ids.wikidata ? link('https://www.wikidata.org/wiki/' + pr.ids.wikidata, 'Wikidata ' + pr.ids.wikidata) : ''}${pr.ids.ulan ? ' · ' + link('https://vocab.getty.edu/page/ulan/' + pr.ids.ulan, 'ULAN ' + pr.ids.ulan) : ''}</div>` : ''}
        </div>
        ${pr.signature ? `<img src="${esc(pr.signature)}?width=240" alt="Signature" style="max-height:48px;margin-top:10px;opacity:.85">` : ''}
      </div>`;
  }
  function toolbarHtml() {
    return `<div class="toolbar" style="grid-column:1/-1">
      <button class="btn" id="tb-print">🖨 Print / save as PDF</button>
      <button class="btn" id="tb-copy">Copy all references</button>
      <button class="btn" id="tb-txt">Download references (.txt)</button>
      <button class="btn" id="tb-json">Download research data (.json)</button>
      <button class="btn" onclick="history.back()">← Back to candidates</button></div>`;
  }
  function allRefsText(state) {
    const lines = [`${state.prof.name} — References`, `Generated by Artist Research Atlas on ${new Date().toLocaleDateString()}`, ''];
    for (const [k, l] of REF_CATS) {
      const items = [...state.refs[k].values()];
      if (!items.length) continue;
      lines.push(l.toUpperCase(), '');
      items.forEach((r, i) => lines.push(`${i + 1}. ${r.text}${r.lifetime ? '  [published in the artist’s lifetime]' : ''}`));
      lines.push('');
    }
    return lines.join('\n');
  }
  function download(name, text, type) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type }));
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }
  function bindToolbar(state) {
    const slug = state.prof.name.replace(/[^\p{L}\p{N}]+/gu, '_');
    $('#tb-print').onclick = () => {
      document.querySelectorAll('details').forEach((d) => (d.open = true));
      window.print();
    };
    $('#tb-copy').onclick = () => navigator.clipboard.writeText(allRefsText(state)).then(() => toast('All references copied'));
    $('#tb-txt').onclick = () => download(`${slug}_references.txt`, allRefsText(state), 'text/plain');
    $('#tb-json').onclick = () => download(`${slug}_research.json`, JSON.stringify({ profile: state.prof, ...state.data }, null, 2), 'application/json');
  }

  /* -------------------------------------------------------------- refs */
  function addRef(state, cat, text, { year, url } = {}) {
    if (!text) return;
    const key = text.replace(/\(accessed [^)]*\)/, '').trim().toLowerCase();
    const prof = state.prof;
    const by = prof?.birthYear;
    const dy = prof?.deathYear ?? new Date().getFullYear();
    const lifetime = Boolean(year && by && year >= by && year <= dy && (prof?.deathYear || year < new Date().getFullYear() - 1 || false));
    if (!state.refs[cat].has(key)) state.refs[cat].set(key, { text, url, year, lifetime });
  }
  function renderRefs(state) {
    const el = $('#body-references');
    if (!el || !state.prof) return;
    let total = 0;
    let lifeTotal = 0;
    const html = REF_CATS.map(([k, l]) => {
      let items = [...state.refs[k].values()];
      if (k !== 'db') items.sort((a, b) => (a.year || 9999) - (b.year || 9999));
      total += items.length;
      lifeTotal += items.filter((r) => r.lifetime).length;
      const rc = $('#rc-' + k);
      if (rc) rc.textContent = items.length || '';
      const extra = k === 'life' ? lifetimeIntro(state) : '';
      const body = items.length
        ? `<ol class="refs">${items.map((r) => `<li class="${r.lifetime ? 'lifetime' : ''}">${linkify(r.text)}${r.lifetime ? '<span class="tag-life">LIFETIME</span>' : ''}</li>`).join('')}</ol>`
        : `<p class="muted">${k === 'life' && !state.lifeLoaded ? 'Searching period archives…' : 'No sources found in the open datasets consulted.'}</p>`;
      return `<h3 id="ref-${k}">${l} <small class="muted" style="font:13px var(--sans)">(${items.length})</small></h3>${extra}${body}`;
    }).join('');
    $('#sm-references').textContent = `${total.toLocaleString()} references · ${lifeTotal} from the artist’s lifetime`;
    el.innerHTML = `<p class="source-line">References are grouped by type and ordered chronologically within each group. Items marked <span class="tag-life">LIFETIME</span> were published, recorded or dated during the artist’s lifetime. Citations follow Chicago notes-bibliography style; verify page-level details against the originals.</p>${html}`;
  }
  const linkify = (t) => esc(t).replace(/(https?:\/\/[^\s<]+?)(?=[.)]?(\s|$))/g, (u) => `<a href="${u}" target="_blank" rel="noopener">${u}</a>`);

  function lifetimeIntro(state) {
    const l = state.data.lifetime;
    if (state.lifetimeError) return `<div class="notice error">Period-source search failed: ${esc(state.lifetimeError)}</div>`;
    if (!l) return spinner('Searching books, newspapers and periodicals published during the artist’s lifetime (the Library of Congress can take up to a minute)…');
    if (!l.range) return `<div class="notice">${esc(l.note)}</div>`;
    return `<p class="source-line">Searched ${esc(l.range.start)}–${esc(l.range.end)} for: ${l.searchedNames.map((n) => `“${esc(n)}”`).join(', ')}. Sources: Wikidata “described by source” records, Internet Archive, Library of Congress Chronicling America${l.newspapersCovered ? '' : ' (not applicable — coverage 1756–1963)'}, Europeana and Open Library.</p>
      ${errs(l.errors)}
      ${l.newspapers?.length ? `<h4>Newspaper mentions — Chronicling America (${l.newspapers.length})</h4>${list(l.newspapers, (n) => `<li><span class="yr">${esc(n.date)}</span> ${link(n.url, n.newspaper)} <span class="sub">${esc(n.state || '')}</span>${citeBtn(n.cite)}</li>`, 8)}` : ''}
      <h4>Search further period archives (pre-filled with name and lifetime dates)</h4><div class="links">${l.links.map((x) => link(x.url, x.label)).join('')}</div>
      <h4>Citations</h4>`;
  }

  function addProfileRefs(state) {
    const pr = state.prof;
    if (pr.ulan) addRef(state, 'bio', pr.ulan.cite);
    if (pr.wikidataCite) addRef(state, 'bio', pr.wikidataCite);
    if (pr.wikipedia) addRef(state, 'bio', pr.wikipedia.cite);
    if (pr.wikiquote) addRef(state, 'bio', pr.wikiquote.cite);
    for (const d of pr.describedBy) {
      addRef(state, 'bio', d.cite, { year: d.year });
      if (d.year && pr.birthYear && d.year >= pr.birthYear && d.year <= (pr.deathYear || 9999)) addRef(state, 'life', d.cite, { year: d.year });
    }
    for (const s of pr.ulan?.sources || []) addRef(state, 'bio', s.cite, { year: parseInt((s.title.match(/\((\d{4})/) || [])[1], 10) || undefined });
    for (const x of pr.externalIds.filter((x) => x.url)) {
      const cat = x.group === 'market' ? 'mkt' : 'db';
      addRef(state, cat, `${x.label}: ${x.id}. ${x.url}`);
    }
  }

  /* -------------------------------------------------------- AI synthesis */
  function renderSynthesisIntro(state) {
    const el = $('#body-synthesis');
    $('#sec-synthesis').classList.add('ai-box');
    el.innerHTML = `<p>Generate a narrative research synthesis written by ${esc(config.aiModel || 'an AI model')} <b>strictly from the sources gathered in this report</b>. Every statement is cited back to a numbered source; unsupported claims are flagged as gaps.</p><button class="btn btn-primary" id="ai-go">Generate synthesis</button>`;
    done('synthesis');
    $('#ai-go').onclick = async () => {
      if (!state.prof) return toast('Please wait for the artist record to load');
      el.innerHTML = spinner('Reading the gathered sources and writing the synthesis (this can take a minute)…');
      try {
        const d = await api('/api/report/synthesis', { wd: state.prof.ids.wikidata, ulan: state.prof.ids.ulan, name: state.prof.name });
        state.data.synthesis = d;
        el.innerHTML = `<div class="ai-out prose">${md(d.markdown)}</div><details><summary>Sources supplied to the model (${d.sources.length})</summary><ol class="refs">${d.sources.map((s) => `<li><b>[S${s.n}] ${esc(s.label)}</b> — ${linkify(s.cite)}</li>`).join('')}</ol></details><p class="source-line">AI-generated text (${esc(d.model)}). Check each claim against the cited source before relying on it.</p>`;
      } catch (e) {
        el.innerHTML = `<div class="notice error">Synthesis failed: ${esc(e.message)}</div>`;
      }
    };
  }
  function md(s) {
    const lines = String(s || '').split('\n');
    let html = '';
    let inList = false;
    const inline = (t) => esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\*(.+?)\*/g, '<i>$1</i>').replace(/\[(S\d+(?:,\s*S\d+)*)\]/g, '<sup class="muted">[$1]</sup>');
    for (const l of lines) {
      const h = l.match(/^(#{1,4})\s+(.*)/);
      const li = l.match(/^\s*[-*]\s+(.*)/);
      if (!li && inList) {
        html += '</ul>';
        inList = false;
      }
      if (h) html += `<h${Math.min(h[1].length + 1, 4)}>${inline(h[2])}</h${Math.min(h[1].length + 1, 4)}>`;
      else if (li) {
        if (!inList) html += '<ul>';
        inList = true;
        html += `<li>${inline(li[1])}</li>`;
      } else if (l.trim()) html += `<p>${inline(l)}</p>`;
    }
    return html + (inList ? '</ul>' : '');
  }

  /* --------------------------------------------------- 1. Identity */
  function renderIdentity(state) {
    const pr = state.prof;
    const F = pr.facts || {};
    const row = (k) => (F[k] ? `<tr><th>${esc(F[k].label)}</th><td>${F[k].values.map((x) => esc(x.label) + (x.when ? ` <span class="muted">(${esc(x.when)})</span>` : '')).join('; ')}</td></tr>` : '');
    const byLang = {};
    for (const v of pr.variants) (byLang[v.lang || '—'] ||= []).push(v.name);
    const langLabel = (l) => ({ ULAN: 'Getty ULAN', en: 'English', mul: 'Multilingual', fr: 'French', de: 'German', it: 'Italian', nl: 'Dutch', es: 'Spanish', pt: 'Portuguese', '': 'Unspecified', '—': 'Other' }[l] || l);
    const ulanNames = byLang.ULAN || [];
    delete byLang.ULAN;
    $('#body-identity').innerHTML = `
      <table class="table">
        <tr><th style="width:220px">Preferred name</th><td>${esc(pr.name)}${pr.ulan?.name ? ` <span class="muted">(ULAN: ${esc(pr.ulan.name)})</span>` : ''}</td></tr>
        <tr><th>Birth</th><td>${esc(pr.births.join(' / ') || 'not recorded')}${pr.births.length > 1 ? ' <span class="muted">(sources disagree)</span>' : ''}${pr.birthPlace ? ' — ' + esc(pr.birthPlace) : ''}</td></tr>
        <tr><th>Death</th><td>${esc(pr.deaths.join(' / ') || (pr.living ? 'living' : 'not recorded'))}${pr.deaths.length > 1 ? ' <span class="muted">(sources disagree)</span>' : ''}${pr.deathPlace ? ' — ' + esc(pr.deathPlace) : ''}</td></tr>
        ${pr.floruit ? `<tr><th>Active / floruit</th><td>${esc(pr.floruit)}</td></tr>` : ''}
        ${pr.ulan?.nationalities?.length ? `<tr><th>Nationality (ULAN)</th><td>${esc(pr.ulan.nationalities.join(', '))}</td></tr>` : ''}
        ${['P27', 'P1412', 'P106', 'P101', 'P135', 'P136', 'P2348', 'P140'].map(row).join('')}
      </table>
      <h3>Name variants <small class="muted" style="font:13px var(--sans)">(${pr.variants.length})</small></h3>
      <p class="source-line">Historical spellings, inverted forms, pseudonyms and names in other languages, as recorded by Wikidata and the Getty ULAN. Use these when searching archives and catalogues.</p>
      ${(() => {
        const principal = [...new Set([...(byLang.en || []), ...(byLang.mul || []), ...ulanNames])];
        return principal.length ? `<h4>Principal variants (English & Getty ULAN forms — ${principal.length})</h4><ul class="variant-cloud">${principal.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>` : '';
      })()}
      ${Object.keys(byLang).filter((l) => !['en', 'mul'].includes(l)).length ? `<details><summary>Names in other languages and scripts (${Object.entries(byLang).filter(([l]) => !['en', 'mul'].includes(l)).reduce((a, [, n]) => a + n.length, 0)})</summary><table class="table">${Object.entries(byLang).filter(([l]) => !['en', 'mul'].includes(l)).map(([l, n]) => `<tr><th style="width:160px">${esc(langLabel(l))}</th><td>${n.map(esc).join(' · ')}</td></tr>`).join('')}</table></details>` : ''}
      ${errs(pr.errors)}`;
  }

  /* --------------------------------------------------- 2. Biography */
  function wikiSections(wp, cat, opts = {}) {
    if (!wp) return '';
    const secs = wp.sections.filter((s) => s.category === cat && s.paragraphs.length);
    if (!secs.length) return '';
    return secs.map((s) => `${s.heading !== 'Introduction' ? `<h${s.level >= 3 ? 4 : 3}>${esc(s.heading)}</h${s.level >= 3 ? 4 : 3}>` : ''}<div class="prose">${s.paragraphs.map((p) => `<p>${esc(p)}</p>`).join('')}</div>`).join('');
  }
  function wikiSource(wp) {
    return wp ? `<p class="source-line">Text: ${link(wp.url, `“${wp.title}”, ${wp.lang === 'en' ? 'English' : wp.lang.toUpperCase()} Wikipedia`)}${wp.lang !== 'en' ? ' (no English article exists; text shown in the original language)' : ''}, CC BY-SA 4.0. ${citeBtn(wp.cite)}</p>` : '';
  }
  function renderBiography(state) {
    const pr = state.prof;
    const F = pr.facts || {};
    const lifeRows = ['P69', 'P1066', 'P802', 'P737', 'P463', 'P108', 'P39', 'P551', 'P937', 'P166', 'P26', 'P22', 'P25', 'P3373', 'P40', 'P1038', 'P119', 'P509'].filter((k) => F[k]);
    const rels = pr.ulan?.relations || [];
    const relGroups = {};
    for (const r of rels) (relGroups[r.relation] ||= []).push(r);
    $('#body-biography').innerHTML = `
      ${pr.ulan?.notes?.length ? `<h3>Biographical note — Getty ULAN</h3><blockquote>${pr.ulan.notes.map(esc).join('<br><br>')}<span class="attr">${link(pr.ulan.url, 'Getty Union List of Artist Names')} ${citeBtn(pr.ulan.cite)}</span></blockquote>` : ''}
      ${pr.wikipedia ? `<h3>Life and career</h3>${wikiSource(pr.wikipedia)}${wikiSections(pr.wikipedia, 'biography')}` : '<p class="muted">No encyclopaedic biography is available in the open sources consulted. See the biographical references below.</p>'}
      ${lifeRows.length ? `<h3>Documented life facts</h3><p class="source-line">Structured statements from ${link('https://www.wikidata.org/wiki/' + pr.ids.wikidata, 'Wikidata')}${citeBtn(pr.wikidataCite)}</p><table class="table">${lifeRows.map((k) => `<tr><th style="width:220px">${esc(F[k].label)}</th><td>${F[k].values.map((x) => (x.id ? link('https://www.wikidata.org/wiki/' + x.id, x.label) : esc(x.label)) + (x.when ? ` <span class="muted">(${esc(x.when)})</span>` : '')).join('; ')}</td></tr>`).join('')}</table>` : ''}
      ${rels.length ? `<h3>Teachers, pupils, family & associates — Getty ULAN</h3><table class="table">${Object.entries(relGroups).map(([k, arr]) => `<tr><th style="width:220px">${esc(k)}</th><td>${arr.map((r) => link('https://vocab.getty.edu/page/ulan/' + r.ulan, r.name)).join('; ')}</td></tr>`).join('')}</table>` : ''}`;
  }

  /* --------------------------------------------------- 5. Critical (base) */
  function renderCriticalBase(state) {
    const pr = state.prof;
    const wp = pr.wikipedia;
    const body = wikiSections(wp, 'critical');
    state.criticalBase = `${body ? `<h3>Style, technique, reception & legacy</h3>${wikiSource(wp)}${body}` : '<p class="muted">No critical discussion was found in the encyclopaedic sources; see scholarly perspectives below.</p>'}`;
    $('#body-critical').innerHTML = state.criticalBase + `<div id="crit-scholarly">${spinner('Gathering scholarly interpretations…')}</div>`;
    // Wikiquote → academic & peer reviews section (rendered when academic data arrives, but prepare now)
  }

  /* --------------------------------------------------- 3. Exhibitions */
  function renderExhibitions(state, d) {
    state.data.exhibitions = d;
    const pr = state.prof;
    for (const e of d.wikidata) addRef(state, 'exh', e.cite, { year: e.start });
    for (const e of d.aic) addRef(state, 'exh', e.cite, { year: parseInt(e.date, 10) });
    for (const c of d.catalogues) addRef(state, 'exh', c.cite, { year: c.year });
    for (const o of d.objectHistories) addRef(state, 'exh', `${o.museum}. “${o.object}” (${o.date || 'n.d.'}), object record — exhibition history. ${o.url}`);
    const lifeEx = d.wikidata.filter((e) => e.start && pr.birthYear && e.start <= (pr.deathYear || 9999) && e.start >= pr.birthYear);
    $('#sm-exhibitions').textContent = `${d.wikidata.length + d.aic.length} exhibitions · ${d.catalogues.length} catalogues`;
    const wpEx = wikiSections(pr.wikipedia, 'exhibitions');
    $('#body-exhibitions').innerHTML = `
      ${errs(d.errors)}
      <p class="source-line">Exhibitions documented in open records. ${lifeEx.length ? `<b>${lifeEx.length}</b> took place during the artist’s lifetime.` : ''} Exhibition data in open sources is incomplete — use the specialist databases at the end of this section to extend the record.</p>
      ${d.wikidata.length ? `<h3>Exhibition chronology</h3>${list(d.wikidata, (e) => `<li><span class="yr">${esc(e.date || 'n.d.')}</span> ${link(e.url, /^Q\d+$/.test(e.title) ? `Untitled exhibition record (${e.title})` : e.title)}${e.start && pr.birthYear && e.start >= pr.birthYear && e.start <= (pr.deathYear || 9999) ? '<span class="tag-life">LIFETIME</span>' : ''}${citeBtn(e.cite)}<div class="sub">${esc([e.venues.join(', '), e.organizers.length ? 'organised by ' + e.organizers.join(', ') : ''].filter(Boolean).join(' · '))}${e.workCount ? ` · ${plural(e.workCount, 'work')} by the artist recorded${e.works.length ? ': ' + esc(e.works.slice(0, 5).join('; ')) + (e.works.length > 5 ? '…' : '') : ''}` : e.how.includes('participant') ? ' · artist recorded as participant' : ''}</div></li>`, 25)}` : ''}
      ${d.aic.length ? `<h3>Exhibitions at the Art Institute of Chicago</h3>${list(d.aic, (e) => `<li><span class="yr">${esc((e.date || '').slice(0, 4) || 'n.d.')}</span> ${link(e.url, e.title)}${citeBtn(e.cite)}<div class="sub">${esc(e.date)}${e.description ? ' — ' + esc(e.description.slice(0, 260)) : ''}</div></li>`, 8)}` : ''}
      ${wpEx ? `<h3>Exhibitions discussed in the literature</h3>${wikiSource(pr.wikipedia)}${wpEx}` : ''}
      ${d.objectHistories.length ? `<h3>Object-level exhibition histories (museum records)</h3><p class="source-line">Exhibition histories of individual works, as published by the holding museums.</p>${d.objectHistories.map((o) => `<details><summary>${esc(o.object)} ${o.date ? `(${esc(o.date)})` : ''} — ${esc(o.museum)} · ${plural(o.entries.length, 'showing')}</summary><ul class="items">${o.entries.map((x) => `<li class="sub">${esc(x)}</li>`).join('')}</ul><p class="source-line">${link(o.url, 'Museum object record')}</p></details>`).join('')}` : ''}
      ${d.catalogues.length ? `<h3>Exhibition catalogues & related publications</h3>${list(d.catalogues, (c) => `<li><span class="yr">${esc(c.year || 'n.d.')}</span> ${link(c.url, c.title)}${citeBtn(c.cite)}<div class="sub">${esc([c.authors.join(', '), c.place, c.publisher].filter(Boolean).join(' · '))}</div></li>`, 12)}` : ''}
      ${!d.wikidata.length && !d.aic.length && !d.catalogues.length && !wpEx ? '<div class="notice">No exhibition records were found in the open datasets. This is common for lesser-documented artists — consult the databases below and the period sources in the References.</div>' : ''}
      <h3>Search specialist exhibition databases</h3><div class="links">${d.databases.map((x) => link(x.url, x.label)).join('')}</div>`;
    done('exhibitions');
  }

  /* --------------------------------------------------- 4. Academic */
  function renderAcademic(state, d) {
    state.data.academic = d;
    const pr = state.prof;
    for (const w of d.subjectWorks) addRef(state, 'acad', w.cite, { year: w.year });
    for (const w of d.scholarly) addRef(state, 'acad', w.cite, { year: w.year });
    $('#sm-academic').textContent = `${d.subjectWorks.length + d.scholarly.length} publications`;
    const wq = pr.wikiquote;
    const isAttr = (p) => /^(quote[ds]? (of|by|from)|quoted|as cited|original|explanatory|translation|in original|source:|—|~|- )/i.test(p) || /^(Quote|Quoted)\b/.test(p);
    const quoteBlock = (paras) => {
      const out = [];
      for (const p of paras) {
        if (isAttr(p) && out.length) out[out.length - 1].attr.push(p);
        else out.push({ q: p, attr: [] });
      }
      return out;
    };
    const quoteHtml = wq
      ? `<h3>Peer & critical commentary — quotations about the artist</h3><p class="source-line">Statements by contemporaries, fellow artists, critics and historians, arranged chronologically as compiled on ${link(wq.url, 'Wikiquote')}, with the attribution given there. Sections marked <span class="tag-life">LIFETIME</span> were written during the artist’s life. ${citeBtn(wq.cite)}</p>
         ${wq.sections.filter((s) => s.paragraphs.length > 1 || !/sorted|chronolog/i.test(s.paragraphs[0] || '')).map((s, i) => {
           const qs = quoteBlock(s.paragraphs);
           const life = /contemporar|lifetime/i.test(s.heading) || ((s.heading.match(/\b(1\d{3})\b/g) || []).some((y) => pr.birthYear && +y >= pr.birthYear && +y <= (pr.deathYear || 9999)));
           const render = (x) => `<li style="border:0;padding:0"><blockquote style="font-size:16.5px">${esc(x.q)}${x.attr.map((a) => `<span class="attr">${esc(a)}</span>`).join('')}</blockquote></li>`;
           return `<details ${i < 2 ? 'open' : ''}><summary>${esc(fixOrdinals(s.heading))}${life ? ' <span class="tag-life">LIFETIME</span>' : ''} — ${plural(qs.length, 'quotation')}</summary>${list(qs, render, 4)}</details>`;
         }).join('')}`
      : '';
    const pub = (w) => `<li><span class="yr">${esc(w.year || 'n.d.')}</span> <span class="t">${link(w.doi ? 'https://doi.org/' + w.doi : w.url, w.title)}</span>${citeBtn(w.cite)}
      <div class="sub">${esc([w.authors?.slice(0, 4).join(', '), w.venue, w.type].filter(Boolean).join(' · '))}${w.citedBy != null ? ` · cited by ${w.citedBy}` : ''}${w.field ? ` · ${esc(w.field)}` : ''}${w.openAccess ? ' · ' + link(w.openAccess, 'open-access copy') : ''}</div>
      ${w.abstract ? `<details><summary>Abstract</summary><div class="abs">${esc(w.abstract)}</div></details>` : ''}</li>`;
    $('#body-academic').innerHTML = `
      ${errs(d.errors)}
      ${d.subjectWorks.length ? `<h3>Scholarship with the artist as principal subject (${d.subjectWorks.length})</h3><p class="source-line">Books, articles, catalogues raisonnés and theses catalogued in Wikidata with the artist as main subject — a curated, high-precision list, in chronological order.</p>${list(d.subjectWorks, pub, 15)}` : ''}
      ${d.scholarly.length ? `<h3>Most-cited scholarly literature (${d.scholarly.length})</h3><p class="source-line">Peer-reviewed articles, books and chapters mentioning “${esc(pr.name)}” in the title or abstract, ranked by citations (${esc(d.scholarlySource || 'OpenAlex')}). Restricted to Arts and Humanities, so namesake studies from other fields (medicine, the natural sciences, patent law) are excluded.</p>${list(d.scholarly, pub, 15)}` : ''}
      ${d.reviews.length ? `<h3>Reviews (${d.reviews.length})</h3>${list(d.reviews, pub, 8)}` : ''}
      ${quoteHtml}
      ${!d.subjectWorks.length && !d.scholarly.length && !wq ? '<div class="notice">No scholarly literature was found in the open indexes. Search the specialist databases below.</div>' : ''}
      <h3>Continue in research databases</h3><div class="links">${d.databases.map((x) => link(x.url, x.label)).join('')}</div>`;
    done('academic');

    // scholarly perspectives for Critical analyses
    const arts = d.scholarly.filter((w) => w.abstract && (!w.field || /arts|humanities|history|social/i.test(w.field))).slice(0, 8);
    const crit = $('#crit-scholarly');
    if (crit)
      crit.innerHTML = arts.length
        ? `<h3>Scholarly interpretations</h3><p class="source-line">Arguments advanced in the most-cited humanities scholarship (abstracts as published).</p>${arts.map((w) => `<blockquote style="font-size:16px">${esc(w.abstract)}<span class="attr">${esc(w.authors.slice(0, 3).join(', '))}, “${esc(w.title)}”, ${esc(w.venue || '')} ${esc(w.year || '')} ${citeBtn(w.cite)}</span></blockquote>`).join('')}`
        : '';
  }

  /* --------------------------------------------------- 6. Market */
  function renderMarket(state, d) {
    state.data.market = d;
    const pr = state.prof;
    for (const p of d.provenance) addRef(state, 'mkt', `${p.museum}. “${p.object}”, provenance record. ${p.url}`);
    for (const r of d.recorded) addRef(state, 'mkt', `“${r.work}” — ${r.event || 'price'}${r.year ? ', ' + r.year : ''}${r.amount ? `, ${r.amount.toLocaleString()} ${r.unit}` : ''}. Wikidata. ${r.workUrl}`, { year: r.year });
    $('#sm-market').textContent = `${d.recorded.length} recorded transactions · ${d.provenance.length} provenance records`;
    const priced = d.recorded.filter((r) => r.amount);
    const wpMkt = wikiSections(pr.wikipedia, 'market');
    $('#body-market').innerHTML = `
      <div class="notice">${esc(d.note)}</div>${errs(d.errors)}
      ${priced.length ? `<h3>Documented prices</h3><table class="table"><tr><th>Year</th><th>Work</th><th>Price</th><th>Context</th></tr>${priced.map((r) => `<tr><td>${esc(r.year || 'n.d.')}</td><td>${link(r.workUrl, r.work)}</td><td><b>${esc(r.amount.toLocaleString())} ${esc(r.unit)}</b></td><td>${esc([r.event, r.buyer && 'buyer: ' + r.buyer, r.seller && 'seller: ' + r.seller].filter(Boolean).join(' · '))}</td></tr>`).join('')}</table>` : ''}
      ${d.recorded.filter((r) => !r.amount).length ? `<h3>Sales, acquisitions & ownership events</h3>${list(d.recorded.filter((r) => !r.amount), (r) => `<li><span class="yr">${esc(r.year || 'n.d.')}</span> ${link(r.workUrl, r.work)} — ${esc(r.event)}${r.buyer ? ` · to ${esc(r.buyer)}` : ''}${r.seller ? ` · from ${esc(r.seller)}` : ''}${r.year && pr.birthYear && r.year >= pr.birthYear && r.year <= (pr.deathYear || 9999) ? '<span class="tag-life">LIFETIME</span>' : ''}</li>`, 15)}` : ''}
      ${d.wikipediaMentions.length ? `<h3>Sales and prices reported in the literature</h3>${d.wikipediaCite ? `<p class="source-line">Sentences from the encyclopaedic article that mention sales, auctions, commissions or prices. ${citeBtn(d.wikipediaCite)}</p>` : ''}${list(d.wikipediaMentions, (s) => `<li>${esc(s.text)} <span class="sub">— §${esc(s.section)}</span></li>`, 10)}` : ''}
      ${wpMkt ? `<h3>Art market</h3>${wpMkt}` : ''}
      ${d.provenance.length ? `<h3>Provenance histories (museum records)</h3><p class="source-line">Chains of ownership, sales and auctions for individual works, as published by the holding museums.</p>${d.provenance.map((p) => `<details><summary>${esc(p.object)} — ${esc(p.museum)}</summary><ol class="refs">${p.entries.map((x) => `<li>${esc(x)}</li>`).join('')}</ol><p class="source-line">${link(p.url, 'Museum object record')}${p.credit ? ' · ' + esc(p.credit) : ''}</p></details>`).join('')}` : ''}
      ${d.marketProfiles.length ? `<h3>The artist’s pages on market databases</h3><div class="links">${d.marketProfiles.map((x) => link(x.url, x.label.replace(/ (artist|person|creator) ID$/i, ''))).join('')}</div>` : ''}
      <h3>Search auction-results & price databases</h3><div class="links">${d.priceDatabases.map((x) => link(x.url, x.label)).join('')}</div>`;
    done('market');
  }

  /* --------------------------------------------------- 7. Collections */
  function renderCollections(state, d) {
    state.data.collections = d;
    const pr = state.prof;
    const inColl = pr.facts?.P6379?.values || [];
    $('#sm-collections').textContent = `${d.totalWorks.toLocaleString()} catalogued works · ${d.holdings.length} collections`;
    const fig = (o) => `<figure>${o.image ? `<a href="${esc(o.url)}" target="_blank" rel="noopener"><img src="${esc(o.image)}" alt="${esc(o.title)}" loading="lazy"></a>` : ''}<figcaption>${link(o.url, o.title)}<br><span class="muted">${esc([o.date || o.year, o.museum || (o.collections || []).join(', ')].filter(Boolean).join(' · '))}</span></figcaption></figure>`;
    $('#body-collections').innerHTML = `
      ${errs(d.errors)}
      ${d.holdings.length ? `<h3>Holdings by collection</h3><p class="source-line">${d.totalWorks.toLocaleString()} works by the artist are catalogued in Wikidata, ${d.works.filter((w) => w.collections.length).length ? '' : ''}distributed as follows (top 25 shown).</p>${list(d.holdings, (h) => `<li>${esc(h.collection)} <span class="sub">— ${plural(h.count, 'work')}</span></li>`, 25)}` : ''}
      ${inColl.length ? `<h4>Institutions recorded as holding works</h4><p>${inColl.map((x) => esc(x.label)).join(' · ')}</p>` : ''}
      ${d.works.filter((w) => w.image).length ? `<h3>Selected works</h3><div class="gallery">${d.works.filter((w) => w.image).slice(0, 24).map(fig).join('')}</div>` : ''}
      ${d.museumObjects.length ? `<h3>Museum open-access records</h3><p class="source-line">Objects from The Metropolitan Museum of Art, the Art Institute of Chicago and the Cleveland Museum of Art.</p><div class="gallery">${d.museumObjects.slice(0, 36).map(fig).join('')}</div>` : ''}
      ${d.europeana.length ? `<h3>European collections (Europeana)</h3>${list(d.europeana, (o) => `<li>${link(o.url, o.title)} <span class="sub">— ${esc([o.museum, o.country, o.date].filter(Boolean).join(' · '))}</span></li>`, 10)}` : ''}
      ${!d.totalWorks && !d.museumObjects.length ? '<div class="notice">No catalogued works were found in the open collection datasets.</div>' : ''}`;
    done('collections');
  }

  /* --------------------------------------------------- 8. Lifetime refs */
  function renderLifetime(state, d) {
    state.data.lifetime = d;
    state.lifeLoaded = true;
    for (const x of d.dictionaries || []) addRef(state, 'life', x.cite, { year: x.year });
    for (const x of d.ia || []) addRef(state, 'life', x.cite, { year: x.year });
    for (const x of d.newspapers || []) addRef(state, 'life', x.cite, { year: parseInt(x.date, 10) });
    for (const x of d.europeana || []) addRef(state, 'life', x.cite, { year: parseInt(x.year, 10) });
    for (const x of d.books || []) addRef(state, 'life', x.cite, { year: x.year });
  }

  /* ================================================================ about */
  function viewAbout() {
    app.innerHTML = `<section class="rs prose" style="max-width:900px;margin:0 auto">
      <h2>Sources & method</h2>
      <h3>1 · Finding the right artist</h3>
      <p>Your search is matched against two authority files: <b>Wikidata</b> (labels, aliases, birth names and pseudonyms in many languages) and the <b>Getty Union List of Artist Names (ULAN)</b>, the reference standard for artist names, which records historical spellings and inverted forms. Results are restricted to people whose recorded occupation is (a subclass of) <i>painter, sculptor, draftsperson, engraver</i> or <i>printmaker</i>. Each candidate shows life dates (with any conflicting dates), birthplace, roles, and the variant that matched.</p>
      <h3>2 · Building the report</h3>
      <ul>
        <li><b>Biography</b> — Getty ULAN biographical note and relationships (teachers, pupils, family), Wikipedia (English or the best available language), and structured Wikidata life facts.</li>
        <li><b>Exhibition record</b> — Wikidata exhibition items (including exhibitions at which individual works were shown), Art Institute of Chicago exhibitions, object-level exhibition histories from museum records, and exhibition catalogues from Open Library, plus links to DoME, Paris Salon, Royal Academy, RKD, MoMA and Artfacts.</li>
        <li><b>Academic & peer reviews</b> — curated scholarship with the artist as main subject (Wikidata), the most-cited literature in OpenAlex (250M+ scholarly works), reviews, and chronologically arranged quotations from contemporaries, fellow artists and critics (Wikiquote).</li>
        <li><b>Critical analyses</b> — encyclopaedic discussion of style, technique, reception and legacy, and arguments drawn from leading scholarship.</li>
        <li><b>Auction & art sales</b> — documented prices, sales and ownership events, provenance chains published by museums, the artist’s pages on Artnet, Artsy, MutualArt, Invaluable and others, and pre-filled searches of auction archives. Full auction records are in subscription databases and are linked rather than reproduced.</li>
        <li><b>References</b> — every source is captured as a Chicago-style citation, grouped as biographical, exhibitions, academic, lifetime, market and database/authority records. <span class="tag-life">LIFETIME</span> marks sources dated within the artist’s life, drawn from historic dictionaries, the Internet Archive, the Library of Congress’s Chronicling America newspapers, Europeana and Open Library.</li>
      </ul>
      <h3>3 · Optional AI synthesis</h3>
      <p>If the server operator configures an API key, a narrative synthesis can be generated <i>only</i> from the sources collected for the report, with numbered citations and explicit gaps.</p>
      <h3>Limitations</h3>
      <p>Open data is uneven: famous artists are richly documented, lesser-known ones may have few records. Name-based searches (academic literature, period sources) can include namesakes for common names — check each item. Always verify against the cited original.</p>
    </section>`;
  }

  fetch('/api/config').then((r) => r.json()).then((c) => (config = c)).catch(() => {}).finally(route);
})();
