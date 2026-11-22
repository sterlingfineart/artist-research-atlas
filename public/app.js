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
    if (path === '/browse') return viewBrowse(p);
    if (path === '/degrees') return viewDegrees(p);
    if (path === '/salon' || path.startsWith('/salon/')) return viewSalon(p, path);
    if (path === '/ra' || path.startsWith('/ra/')) return viewRA(p, path);
    if (path === '/loan' || path.startsWith('/loan/')) return viewLoan(p, path);
    if (path === '/exhibitions' || path.startsWith('/exhibitions/')) return viewExhibitions(p, path);
    if (path === '/sales') return viewSales(p);
    if (path === '/game') return viewGame(p);
    if (path === '/feedback') return viewFeedback();
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
        ${c.image ? `<img class="thumb" src="${esc(c.image)}" alt="">` : `<div class="thumb">${esc((c.name || '?')[0])}</div>`}
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

  /* ========================================================== browse view */
  /* The twenty homepage artists, grouped by the same four facets as Browse.
   * Centuries are by birth year, countries in their modern form, movements
   * the artist's best-known one. Every QID was verified against Wikidata. */
  const SHOWCASE_INDEX = [
    { name: 'Rembrandt', wd: 'Q5598', century: 17, country: 'Netherlands', movement: 'Baroque', roles: ['Painters', 'Engravers', 'Printmakers', 'Draftspeople'] },
    { name: 'Hokusai', wd: 'Q5586', century: 18, country: 'Japan', movement: 'Ukiyo-e', roles: ['Painters', 'Printmakers', 'Draftspeople'] },
    { name: 'Johannes Vermeer', wd: 'Q41264', century: 17, country: 'Netherlands', movement: 'Baroque', roles: ['Painters'] },
    { name: 'Xu Beihong', wd: 'Q714152', century: 19, country: 'China', movement: 'Realism', roles: ['Painters'] },
    { name: 'Artemisia Gentileschi', wd: 'Q212657', century: 16, country: 'Italy', movement: 'Baroque', roles: ['Painters'] },
    { name: 'Behzad', wd: 'Q334875', century: 15, country: 'Iran', movement: 'Persian miniature', roles: ['Painters'] },
    { name: 'Claude Monet', wd: 'Q296', century: 19, country: 'France', movement: 'Impressionism', roles: ['Painters'] },
    { name: 'Raden Saleh', wd: 'Q1375979', century: 19, country: 'Indonesia', movement: 'Romanticism', roles: ['Painters', 'Draftspeople'] },
    { name: 'Gustav Klimt', wd: 'Q34661', century: 19, country: 'Austria', movement: 'Art Nouveau', roles: ['Painters', 'Draftspeople'] },
    { name: 'Raja Ravi Varma', wd: 'Q333453', century: 19, country: 'India', movement: 'Realism', roles: ['Painters'] },
    { name: 'Albrecht Dürer', wd: 'Q5580', century: 15, country: 'Germany', movement: 'Northern Renaissance', roles: ['Painters', 'Engravers', 'Printmakers', 'Draftspeople'] },
    { name: 'Osman Hamdi Bey', wd: 'Q1190012', century: 19, country: 'Turkey', movement: 'Orientalism', roles: ['Painters'] },
    { name: 'Mary Cassatt', wd: 'Q173223', century: 19, country: 'United States', movement: 'Impressionism', roles: ['Painters', 'Printmakers'] },
    { name: 'Joaquín Torres García', wd: 'Q520713', century: 19, country: 'Uruguay', movement: 'Universal Constructivism', roles: ['Painters', 'Sculptors'] },
    { name: 'John Singer Sargent', wd: 'Q155626', century: 19, country: 'United States', movement: 'Impressionism', roles: ['Painters'] },
    { name: 'Olowe of Ise', wd: 'Q7088530', century: 19, country: 'Nigeria', movement: 'Yoruba art', roles: ['Sculptors'] },
    { name: 'Amrita Sher-Gil', wd: 'Q150312', century: 20, country: 'India', movement: 'Post-Impressionism', roles: ['Painters'] },
    { name: 'Francisco Goya', wd: 'Q5432', century: 18, country: 'Spain', movement: 'Romanticism', roles: ['Painters', 'Engravers', 'Printmakers', 'Draftspeople'] },
    { name: 'Pedro Américo', wd: 'Q540219', century: 19, country: 'Brazil', movement: 'Romanticism', roles: ['Painters'] },
    { name: 'Hildegard von Bingen', wd: 'Q70991', century: 11, country: 'Germany', movement: 'Romanesque art', roles: ['Illuminator'] },
  ];
  const centuryLabel = (c) => {
    const s = c % 10 === 1 && c % 100 !== 11 ? 'st' : c % 10 === 2 && c % 100 !== 12 ? 'nd' : c % 10 === 3 && c % 100 !== 13 ? 'rd' : 'th';
    return `${c}${s} century`;
  };
  function indexGroup(title, key, sort) {
    const groups = {};
    for (const a of SHOWCASE_INDEX) {
      const vals = Array.isArray(a[key]) ? a[key] : [a[key]];
      for (const v of vals) (groups[v] ||= []).push(a);
    }
    return `<h3>${esc(title)}</h3>${Object.keys(groups).sort(sort).map((g) => `<h4>${esc(key === 'century' ? centuryLabel(+g) : g)}</h4><p>${groups[g].map((a) => `<a href="#/search?q=${enc(a.name)}">${esc(a.name)}</a>`).join(' · ')}</p>`).join('')}`;
  }
  function renderShowcaseIndex() {
    const el = $('#browse-index');
    if (!el) return;
    el.innerHTML = `<h2>From the homepage</h2>
      <p class="source-line">The twenty artists on the homepage, grouped by the same four facets. Each name opens the usual name search, so you can pick the right person and read the report.</p>
      ${indexGroup('By century', 'century', (a, b) => +a - +b)}
      ${indexGroup('By country', 'country', (a, b) => a.localeCompare(b))}
      ${indexGroup('By movement', 'movement', (a, b) => a.localeCompare(b))}
      ${indexGroup('By medium', 'roles', (a, b) => a.localeCompare(b))}`;
  }
  function browseCard(a, i) {
    return `<article class="cand">
      ${a.image ? `<img class="thumb" src="${esc(a.image)}" alt="">` : `<div class="thumb">${esc((a.name || '?')[0])}</div>`}
      <div>
        <h3>${esc(a.name)}</h3>
        <div class="dates">${esc(lifeStr({ birth: a.birthYear ? String(a.birthYear) : null, death: a.deathYear ? String(a.deathYear) : null }))}</div>
        <div class="meta">${a.birthPlace ? `Born: <b>${esc(a.birthPlace)}</b>` : 'Birthplace not recorded'}</div>
        <div class="badges">${(a.roles || []).slice(0, 6).map((r) => `<span class="badge role">${esc(r)}</span>`).join('')}<span class="badge src">Wikidata</span></div>
      </div>
      <div class="cand-actions">
        <button class="btn btn-primary" data-pick="${i}">Select this artist →</button>
        ${a.id ? link(`https://www.wikidata.org/wiki/${a.id}`, `Wikidata ${a.id}`) : ''}
        ${a.ulan ? link(`https://vocab.getty.edu/page/ulan/${a.ulan}`, `ULAN ${a.ulan}`) : ''}
      </div></article>`;
  }
  /* The Atlas's own collections, with counts taken from each
     collection's index file, and a year browser across all of them:
     pick a year and see every catalogue the Atlas holds for it — the
     Paris Salon, the Royal Academy and the Record of Exhibitions. */
  async function browseCollectionData() {
    const [exh, salon, ra, loan] = await Promise.all([
      exhIndex ? Promise.resolve(exhIndex) : salonFetchJSON('/data/exhibitions/index.json').then((d) => (exhIndex = d)).catch(() => null),
      salonIndex ? Promise.resolve(salonIndex) : salonFetchJSON('/data/salon/index.json').then((d) => (salonIndex = d)).catch(() => null),
      raIndex ? Promise.resolve(raIndex) : salonFetchJSON('/data/ra/index.json').then((d) => (raIndex = d)).catch(() => null),
      loanIndex ? Promise.resolve(loanIndex) : salonFetchJSON('/data/loan/index.json').then((d) => (loanIndex = d)).catch(() => null),
    ]);
    return { exh, salon, ra, loan };
  }
  const sumWorks = (rows) => (rows || []).reduce((s, r) => s + (r.works || 0), 0);
  const yearSpan = (rows) => {
    const ys = (rows || []).map((r) => r.year).filter(Boolean);
    return ys.length ? `${Math.min(...ys)}–${Math.max(...ys)}` : '';
  };
  async function renderBrowseCollections() {
    const el = $('#browse-collections');
    if (!el) return;
    const { exh, salon, ra, loan } = await browseCollectionData();
    const card = (href, title, meta, desc) => `<h3><a href="${href}">${esc(title)}</a></h3><p>${meta ? `<span class="meta">${esc(meta)}</span><br>` : ''}${esc(desc)}</p>`;
    let html = `<h2>The collections</h2>
      <p class="source-line">The Atlas's own databases — exhibition catalogues and reference dictionaries digitised in full and verified against their sources. Everything below is counted from the collections themselves.</p>`;
    if (exh) html += card('#/exhibitions', 'Record of Exhibitions', `${exh.length} exhibitions · ${sumWorks(exh).toLocaleString()} works · ${yearSpan(exh)}`, 'Complete exhibition catalogues recorded work by work — the Guildhall exhibitions, the Salons de la Rose+Croix, the American Water Color Society annuals and more.');
    if (salon) html += card('#/salon', 'Paris Salon', `${salon.years.length} Salon years · ${sumWorks(salon.years).toLocaleString()} works · ${yearSpan(salon.years)}`, 'The Paris Salon livrets, browsable year by year — every work in every catalogue.');
    if (ra) html += card('#/ra', 'Royal Academy', `${ra.years.length} exhibition years · ${sumWorks(ra.years).toLocaleString()} works · ${yearSpan(ra.years)}`, 'The Royal Academy Summer Exhibitions, from Graves’s Complete Dictionary of Contributors and Their Work.');
    if (loan) html += card('#/loan', 'Loan Exhibitions (UK)', `${(loan.totalWorks || 0).toLocaleString()} works · ${(loan.totalArtists || 0).toLocaleString()} artists`, 'British loan exhibitions, from Graves’s dictionary of the exhibitions and their contributors.');
    el.innerHTML = html;
  }
  async function renderBrowseYears() {
    const el = $('#browse-years');
    if (!el) return;
    const { exh, salon, ra } = await browseCollectionData();
    const byYear = new Map();
    const add = (year, item) => {
      if (!byYear.has(year)) byYear.set(year, []);
      byYear.get(year).push(item);
    };
    for (const y of (salon && salon.years) || []) add(y.year, { label: `Paris Salon ${y.year}`, href: `#/salon/${y.year}`, meta: `${y.works.toLocaleString()} works` });
    for (const y of (ra && ra.years) || []) add(y.year, { label: `Royal Academy ${y.year}`, href: `#/ra/${y.year}`, meta: `${y.works.toLocaleString()} works` });
    for (const e of exh || []) add(e.year, { label: e.label, href: `#/exhibitions/${e.id}`, meta: `${e.works.toLocaleString()} works · ${e.venue}` });
    const years = [...byYear.keys()].sort((a, b) => b - a);
    if (!years.length) { el.innerHTML = ''; return; }
    const byDecade = new Map();
    for (const y of years) {
      const d = Math.floor(y / 10) * 10;
      if (!byDecade.has(d)) byDecade.set(d, []);
      byDecade.get(d).push(y);
    }
    el.innerHTML = `<h2>Exhibitions by year</h2>
      <p class="source-line">Pick a year and see every catalogue the Atlas holds for it, across Paris, London and New York.</p>
      <form class="browse-form" id="browse-year-form">
        <label>Year <select id="browse-year-select" aria-label="Year"><option value="">Choose a year…</option>${years.map((y) => `<option value="${y}">${y}</option>`).join('')}</select></label>
      </form>
      <div id="browse-year-results"></div>
      ${[...byDecade.entries()].sort((a, b) => b[0] - a[0]).map(([d, ys]) => `<h4>${d}s</h4><p>${ys.map((y) => `<a href="#" data-browse-year="${y}">${y}</a>`).join(' · ')}</p>`).join('')}`;
    const showYear = (y) => {
      const out = $('#browse-year-results');
      const sel = $('#browse-year-select');
      if (sel) sel.value = String(y);
      const items = byYear.get(y) || [];
      out.innerHTML = `<h3>${y}</h3>${items.map((it) => `<p><a href="${it.href}">${esc(it.label)}</a> <span class="meta">${esc(it.meta)}</span></p>`).join('')}`;
    };
    $('#browse-year-select').addEventListener('change', (e) => { if (e.target.value) showYear(+e.target.value); });
    el.querySelectorAll('[data-browse-year]').forEach((a) =>
      a.addEventListener('click', (e) => { e.preventDefault(); showYear(+a.dataset.browseYear); })
    );
  }
  async function viewBrowse(p) {
    app.innerHTML = `<h1 style="font-size:38px">Browse</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Two ways in: the Atlas’s own collections — the exhibition catalogues and dictionaries it has digitised and verified — browsed by collection or by year; or artists by century, country, movement or medium, drawn from Wikidata.</p>
      <section class="rs" id="browse-collections"></section>
      <section class="rs" id="browse-years"></section>
      <h2>Artists by facet</h2>
      <p class="source-line">Browse artists by century, country, movement or medium — pick any combination and press GO. Every list is drawn from Wikidata, restricted to painters, sculptors, draftsmen, engravers and printmakers — select an artist to generate the full research report.</p>
      <p class="source-line" id="browse-cache-note">Results cached — refreshed weekly.</p>
      <div id="browse-facets">${spinner('Loading browse lists…')}</div>
      <div id="browse-results"></div>
      <section class="rs" id="browse-index"></section>`;
    renderShowcaseIndex();
    renderBrowseCollections();
    renderBrowseYears();
    const showBrowseCacheNote = (cache) => {
      const note = $('#browse-cache-note');
      if (!note) return;
      note.textContent = cache?.cachedAt
        ? `Results cached — refreshed weekly. Cache updated ${new Date(cache.cachedAt).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit' })}.`
        : 'Results cached — refreshed weekly.';
    };
    let defs;
    try {
      defs = await api('/api/browse', {});
    } catch (e) {
      $('#browse-facets').innerHTML = `<div class="notice error">Browse lists could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    if (defs?.facets) {
      showBrowseCacheNote(defs.cache);
      const byId = Object.fromEntries(defs.facets.map((f) => [f.id, f]));
      // The current selection, from a combined URL (?century=19&country=Q96)
      // or a legacy single-facet URL (?facet=country&value=Q96).
      const selFor = (fid) => p[fid] || (p.facet === fid ? p.value : '');
      const opt = (f, v) => `<option value="${esc(v.id)}"${selFor(f.id) === v.id ? ' selected' : ''}>${esc(v.label)}${v.count != null ? ` (${v.count.toLocaleString()})` : ''}</option>`;
      const selectHtml = (f, placeholder) => {
        if (f.id === 'country' && f.values.some((v) => v.historical)) {
          const modern = f.values.filter((v) => !v.historical);
          const hist = f.values.filter((v) => v.historical);
          return `<select name="country" aria-label="Country"><option value="">${placeholder}</option><optgroup label="Countries">${modern.map((v) => opt(f, v)).join('')}</optgroup><optgroup label="Historical states &amp; regions">${hist.map((v) => opt(f, v)).join('')}</optgroup></select>`;
        }
        return `<select name="${f.id}" aria-label="${esc(f.label)}"><option value="">${placeholder}</option>${f.values.map((v) => opt(f, v)).join('')}</select>`;
      };
      $('#browse-facets').innerHTML = `<form id="browse-form" class="browse-form">
        <label>Century ${selectHtml(byId.century, 'Choose a century…')}</label>
        <label>Country ${selectHtml(byId.country, 'Choose a country…')}</label>
        <label>Movement ${selectHtml(byId.movement, 'Choose a movement…')}</label>
        <label>Medium ${selectHtml(byId.role, 'Choose a medium…')}</label>
        <button class="btn btn-primary" type="submit">GO</button>
      </form>${errs(defs.errors)}`;
      $('#browse-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const q = ['century', 'country', 'movement', 'role']
          .map((k) => (fd.get(k) ? `${k}=${enc(fd.get(k))}` : ''))
          .filter(Boolean)
          .join('&');
        if (!q) return;
        location.hash = '#/browse?' + q;
      });
    }
    const hasCombined = p.century || p.country || p.movement || p.role;
    if (!p.facet && !p.value && !hasCombined) return;
    const out = $('#browse-results');
    out.innerHTML = spinner('Finding artists…');
    let d;
    try {
      d = await api('/api/browse', hasCombined ? { century: p.century, country: p.country, movement: p.movement, role: p.role } : { facet: p.facet, value: p.value });
    } catch (e) {
      out.innerHTML = `<div class="notice error">Browse failed: ${esc(e.message)}</div>`;
      return;
    }
    showBrowseCacheNote(d.cache);
    const artists = d.artists || [];
    if (!artists.length) {
      out.innerHTML = `${errs(d.errors)}<div class="notice">No artists were found for “${esc(d.label || p.value || 'those filters')}”. Wikidata may not record that combination — try another value.</div>`;
      return;
    }
    out.innerHTML = `<div class="results-head"><div><h2>${plural(artists.length, 'artist')} — ${esc(d.label)}</h2><div class="meta">Showing up to 50 artists, best-documented first (by number of linked Wikimedia pages), then by birth year. Select an artist to generate the research report.</div></div></div>${errs(d.errors)}${artists.map((a, i) => browseCard(a, i)).join('')}`;
    out.querySelectorAll('[data-pick]').forEach((b) =>
      b.addEventListener('click', () => {
        const a = artists[+b.dataset.pick];
        const cand = { wikidata: a.id, ulan: a.ulan || null, name: a.name, birth: a.birthYear ? String(a.birthYear) : null, death: a.deathYear ? String(a.deathYear) : null, birthYear: a.birthYear, deathYear: a.deathYear, birthPlace: a.birthPlace, roles: a.roles, image: a.image, sources: ['Wikidata'], variants: [], citizenship: [] };
        sessionStorage.setItem('cand:' + (cand.wikidata || cand.ulan), JSON.stringify(cand));
        location.hash = `#/artist?wd=${cand.wikidata}${cand.ulan ? '&ulan=' + cand.ulan : ''}`;
      })
    );
  }

  /* ======================================================== six degrees view */
  /* Six Degrees of Rembrandt: the shortest chain between two artists
   * through recorded teacher/pupil/influence links (Wikidata P802/P1066/
   * P737). Each side is picked through the usual name search; a single
   * exact match is used directly, several candidates are offered as a
   * small list to choose from. The suggested pairs below were all verified
   * against the live endpoint (2026-11-16) — step counts are real, not
   * guessed. */
  const DEGREES_PAIRS = [
    { from: 'Rembrandt', to: 'Johannes Vermeer', steps: 2 },
    { from: 'Rembrandt', to: 'Claude Monet', steps: 2 },
    { from: 'Hokusai', to: 'Vincent van Gogh', steps: 1 },
    { from: 'Rembrandt', to: 'Pablo Picasso', steps: 3 },
  ];
  const degreesState = { from: null, to: null }; // each: { wd, ulan, name, birth, death }

  async function viewDegrees(p) {
    app.innerHTML = `<h1 style="font-size:38px">Six Degrees of Rembrandt</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Pick any two artists. The finder traces the shortest chain between them — up to six steps — through links Wikidata actually records: <b>taught</b>, <b>was taught by</b>, <b>influenced</b>, <b>was influenced by</b>. Every name in the chain links to that artist's Atlas report. If no chain is recorded within six steps, it says so — it never invents a link.</p>
      <div class="degrees-pickers">
        <div class="degrees-side" id="deg-from"></div>
        <div class="degrees-side" id="deg-to"></div>
      </div>
      <div class="degrees-pairs"><span class="meta">Try a pair:</span>${DEGREES_PAIRS.map((pr, i) => `<button class="chip" data-pair="${i}">${esc(pr.from)} → ${esc(pr.to)} · ${pr.steps} step${pr.steps === 1 ? '' : 's'}</button>`).join('')}</div>
      <div style="margin:14px 0"><button class="btn btn-primary" id="deg-find" disabled>Find the chain</button></div>
      <div id="deg-out"></div>`;
    renderDegreePicker('from', 'From');
    renderDegreePicker('to', 'To');
    document.querySelectorAll('[data-pair]').forEach((b) => b.addEventListener('click', () => runSuggestedPair(DEGREES_PAIRS[+b.dataset.pair])));
    $('#deg-find').addEventListener('click', () => runDegrees(degreesState.from.wd, degreesState.to.wd));
    // A shared link (#/degrees?from=Q5598&to=Q41264) runs the search
    // directly; the pickers are filled from the result's labels.
    if (/^Q\d+$/.test(p.from || '') && /^Q\d+$/.test(p.to || '')) {
      runDegrees(p.from, p.to).then((d) => {
        if (!d) return;
        degreesState.from = { wd: p.from, ulan: null, name: d.fromLabel };
        degreesState.to = { wd: p.to, ulan: null, name: d.toLabel };
        renderDegreePicker('from', 'From');
        renderDegreePicker('to', 'To');
        updateDegreeFind();
      });
    }
    // If both pickers are already filled (e.g. coming back from a chain
    // artist's report), enable Find without making the user re-pick.
    updateDegreeFind();
  }

  function renderDegreePicker(side, label) {
    const el = $('#deg-' + side);
    if (!el) return;
    const sel = degreesState[side];
    el.innerHTML = `<label>${label} artist</label>
      <div class="degrees-pick">
        <input id="deg-${side}-q" type="search" placeholder="e.g. Rembrandt" aria-label="${label} artist name" value="${esc(sel?.name || '')}">
        <button class="btn" id="deg-${side}-go">Look up</button>
      </div>
      ${sel ? `<div class="degrees-chosen">✓ <b>${esc(sel.name)}</b>${sel.birth || sel.death ? ` <span class="meta">(${esc(sel.birth || '?')}–${esc(sel.death || '?')})</span>` : ''} <button class="linkish" id="deg-${side}-clear">change</button></div>` : ''}
      <div id="deg-${side}-cands"></div>`;
    const input = $('#deg-' + side + '-q');
    const lookup = async () => {
      const q = input.value.trim();
      const box = $('#deg-' + side + '-cands');
      if (!box) return;
      if (q.length < 2) { box.innerHTML = '<div class="notice">Enter at least two characters.</div>'; return; }
      box.innerHTML = spinner('Looking up…');
      let d;
      try { d = await api('/api/search', { q }); }
      catch (e) { box.innerHTML = `<div class="notice error">Lookup failed: ${esc(e.message)}</div>`; return; }
      const cands = (d.candidates || []).slice(0, 5);
      if (!cands.length) { box.innerHTML = `<div class="notice">No artists matching “${esc(q)}” were found. Try another spelling, or the surname alone.</div>`; return; }
      const exact = cands.filter((c) => c.match === 'exact');
      if (exact.length === 1) { pickDegree(side, exact[0]); return; }
      box.innerHTML = `<div class="degrees-cands">${cands.map((c, i) => `<button class="degrees-cand" data-i="${i}"><b>${esc(c.name)}</b> <span class="meta">${esc(lifeStr(c))}${c.birthPlace ? ` · born ${esc(c.birthPlace)}` : ''}</span></button>`).join('')}</div>`;
      box.querySelectorAll('[data-i]').forEach((b) => b.addEventListener('click', () => pickDegree(side, cands[+b.dataset.i])));
    };
    $('#deg-' + side + '-go').addEventListener('click', lookup);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); lookup(); } });
    const clear = $('#deg-' + side + '-clear');
    if (clear) clear.addEventListener('click', () => {
      degreesState[side] = null;
      renderDegreePicker(side, label);
      updateDegreeFind();
    });
  }

  function pickDegree(side, c) {
    if (!c.wikidata) {
      const box = $('#deg-' + side + '-cands');
      if (box) box.innerHTML = `<div class="notice">“${esc(c.name)}” has no Wikidata record, so the chain search cannot use this candidate — pick another.</div>`;
      return;
    }
    degreesState[side] = { wd: c.wikidata, ulan: c.ulan || null, name: c.name, birth: c.birth || null, death: c.death || null };
    renderDegreePicker(side, side === 'from' ? 'From' : 'To');
    updateDegreeFind();
  }

  function updateDegreeFind() {
    const b = $('#deg-find');
    if (b) b.disabled = !(degreesState.from?.wd && degreesState.to?.wd);
  }

  async function runDegrees(fromQid, toQid) {
    const out = $('#deg-out');
    if (!out) return null;
    out.innerHTML = spinner('Searching the teacher, pupil and influence links…');
    const t0 = Date.now();
    const timer = setInterval(() => {
      const s = out.querySelector('.loading span');
      if (s) s.textContent = `Searching the teacher, pupil and influence links… ${Math.floor((Date.now() - t0) / 1000)}s — Wikidata can be slow for some pairs.`;
      else clearInterval(timer);
    }, 1000);
    let d;
    try { d = await api('/api/degrees', { from: fromQid, to: toQid }); }
    catch (e) {
      clearInterval(timer);
      out.innerHTML = `<div class="notice error">The chain search failed: ${esc(e.message)} — Wikidata is sometimes slow or unreachable; try again in a moment.</div>`;
      return null;
    }
    clearInterval(timer);
    renderDegreesResult(d);
    return d;
  }

  function renderDegreesResult(d) {
    const out = $('#deg-out');
    if (!out) return;
    const secs = ((d.ms || 0) / 1000).toFixed(1);
    if (d.steps === 0) {
      out.innerHTML = `<div class="notice">That is the same artist — <b>${esc(d.fromLabel)}</b>, 0 steps. Try two different artists.</div>`;
      return;
    }
    if (!d.found) {
      out.innerHTML = `<div class="notice">No chain found within six steps — ${plural(d.explored, 'artist')} explored in ${secs}s. Wikidata only records some teacher, pupil and influence links, so a missing chain means no chain is recorded, not that no connection existed in life.</div>`;
      return;
    }
    const node = (n) => `<a href="#/artist?wd=${esc(n.qid)}">${esc(n.label)}</a>${n.born || n.died ? ` <span class="meta">(${esc(n.born ?? '?')}–${esc(n.died ?? '?')})</span>` : ''}`;
    const steps = d.path.map((n, i) => (i === 0
      ? `<div class="chain-node">${node(n)}</div>`
      : `<div class="chain-edge"><span class="chain-arrow">↓</span><span class="chain-rel">${esc(n.edge)}</span></div><div class="chain-node">${node(n)}</div>`)).join('');
    out.innerHTML = `<div class="results-head"><div><h2>${plural(d.steps, 'step')} — ${esc(d.fromLabel)} to ${esc(d.toLabel)}</h2><div class="meta">${plural(d.explored, 'artist')} explored · ${secs}s${d.cached ? ' · from cache' : ''}</div></div></div>
      <div class="chain">${steps}</div>
      <p class="source-line">Each link is a Wikidata record: <i>student</i> (P802), <i>student of</i> (P1066) or <i>influenced by</i> (P737). “Taught” and “influenced” run from the artist above to the one below; “was taught by” and “was influenced by” run the other way. Click any name for the full Atlas report.</p>`;
  }

  async function runSuggestedPair(pair) {
    const out = $('#deg-out');
    const resolve = async (side, name) => {
      const d = await api('/api/search', { q: name });
      const exact = (d.candidates || []).filter((c) => c.match === 'exact');
      const c = exact[0] || (d.candidates || [])[0];
      if (!c || !c.wikidata) throw new Error(`Could not resolve “${name}” — pick the artists by hand instead.`);
      degreesState[side] = { wd: c.wikidata, ulan: c.ulan || null, name: c.name, birth: c.birth || null, death: c.death || null };
      renderDegreePicker(side, side === 'from' ? 'From' : 'To');
    };
    if (out) out.innerHTML = spinner('Resolving the pair…');
    try {
      await resolve('from', pair.from);
      await resolve('to', pair.to);
      updateDegreeFind();
      await runDegrees(degreesState.from.wd, degreesState.to.wd);
    } catch (e) {
      if (out) out.innerHTML = `<div class="notice error">${esc(e.message)}</div>`;
    }
  }

  /* ========================================================== salon view */
  const SALON_SECTION_LABELS = { PEINTURE: 'Painting', SCULPTURE: 'Sculpture', GRAVURE: 'Engraving', ARCHITECTURE: 'Architecture', 'MONUMENTS PUBLICS': 'Public monuments' };
  const SALON_SECTION_ORDER = ['PEINTURE', 'SCULPTURE', 'GRAVURE', 'ARCHITECTURE', 'MONUMENTS PUBLICS'];
  const SALON_FAMOUS = [
    { year: 1863, label: '1863 · the Refusés year' },
    { year: 1855, label: '1855 · Universal Exhibition' },
    { year: 1874, label: '1874' },
    { year: 1789, label: '1789' },
  ];
  const SALON_DEFAULT_YEAR = 1874;
  const SALON_PAGE_SIZE = 50;
  let salonIndex = null;
  const salonYearCache = new Map();
  const salonState = { year: SALON_DEFAULT_YEAR, section: 'all', query: '', page: 1, data: null, entry: null };
  async function salonFetchJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`Could not load ${url} (HTTP ${r.status})`);
    return r.json();
  }
  async function loadSalonIndex() {
    if (!salonIndex) salonIndex = await salonFetchJSON('/data/salon/index.json');
    return salonIndex;
  }
  /* OCR name corrections (public/data/salon/name-corrections.json), fetched
     once and cached. Applied in memory to a year's works right after the
     year file loads; the per-year files keep the spellings as printed.
     If the file cannot be loaded the page still works, uncorrected. */
  let salonNameCorrections = null;
  async function loadSalonNameCorrections() {
    if (!salonNameCorrections) salonNameCorrections = salonFetchJSON('/data/salon/name-corrections.json').catch(() => null);
    return salonNameCorrections;
  }
  function applySalonNameCorrections(data, year, corr) {
    if (!corr) return;
    // Prose years (1673, 1699, 1704) are not livret name fields: untouched.
    if (year === 1673 || year === 1699 || year === 1704) return;
    const { given, surname, teacher } = corr;
    for (const w of data.works) {
      if (w[2] && surname[w[2]]) w[2] = surname[w[2]];
      if (w[3] && given[w[3]]) w[3] = given[w[3]];
      if (w[5] && teacher[w[5]]) w[5] = teacher[w[5]];
    }
  }
  async function loadSalonYear(year) {
    if (!salonYearCache.has(year)) {
      salonYearCache.set(year, (async () => {
        const data = await salonFetchJSON(`/data/salon/${year}.json`);
        applySalonNameCorrections(data, year, await loadSalonNameCorrections());
        return data;
      })().catch((e) => { salonYearCache.delete(year); throw e; }));
    }
    return salonYearCache.get(year);
  }
  const salonSectionLabel = (s) => SALON_SECTION_LABELS[s] || s.charAt(0) + s.slice(1).toLowerCase();
  function salonOrderedSections(sections) {
    const known = SALON_SECTION_ORDER.filter((s) => sections.includes(s));
    const rest = sections.filter((s) => !SALON_SECTION_ORDER.includes(s));
    return [...known, ...rest];
  }
  /** Full name for the Atlas name search: given names + surname as printed. */
  function salonFullName(w) {
    return [w[3], w[2]].filter(Boolean).join(' ');
  }
  function salonNumCell(w) {
    if (w[1] == null) return '<span class="muted" title="No catalogue number in the livret — a prose entry, not a numbered work">—</span>';
    if (w[9] & 2) return `${esc(w[1])} <span class="flag-mark" title="Catalogue number inferred from the sequence — the printed livret does not give it clearly">~</span>`;
    if (w[9] & 1) return `${esc(w[1])} <span class="flag-mark" title="Catalogue number as printed, but it breaks the sequence — it may be an OCR misreading">~</span>`;
    return esc(w[1]);
  }
  function salonFiltered() {
    const { data, section, query } = salonState;
    if (!data) return [];
    const q = query.trim().toLowerCase();
    return data.works.filter((w) => {
      if (section !== 'all' && data.sections[w[0]] !== section) return false;
      if (!q) return true;
      return salonFullName(w).toLowerCase().includes(q) || (w[6] || '').toLowerCase().includes(q);
    });
  }
  function renderSalonTable() {
    const wrap = $('#salon-table-wrap');
    if (!wrap || !salonState.data) return;
    const rows = salonFiltered();
    const pages = Math.max(1, Math.ceil(rows.length / SALON_PAGE_SIZE));
    if (salonState.page > pages) salonState.page = pages;
    const start = (salonState.page - 1) * SALON_PAGE_SIZE;
    const pageRows = rows.slice(start, start + SALON_PAGE_SIZE);
    const noteHtml = (w) => {
      if (!w[8]) return '';
      const n = w[8];
      const short = n.length > 160 ? n.slice(0, 160) + '…' : n;
      return `<div class="meta" title="${esc(n)}">${esc(short)}</div>`;
    };
    if (!rows.length) {
      wrap.innerHTML = '<div class="notice">No works in this year match — try another spelling, a different section, or clear the search box.</div>';
      return;
    }
    wrap.innerHTML = `<div class="table-wrap"><table class="table salon-table">
      <thead><tr><th class="salon-num">No.</th><th>Title</th><th>Artist</th><th>Birthplace</th><th>Teacher</th><th>Medium</th></tr></thead>
      <tbody>${pageRows.map((w) => `<tr>
        <td class="salon-num">${salonNumCell(w)}</td>
        <td>${esc(w[6] || '')}${noteHtml(w)}</td>
        <td><a href="#/search?q=${enc(salonFullName(w))}">${esc(salonFullName(w))}</a></td>
        <td>${esc(w[4] || '')}</td>
        <td>${esc(w[5] || '')}</td>
        <td>${esc(w[7] || '')}</td>
      </tr>`).join('')}</tbody></table></div>
      <div class="pager">
        <button class="btn btn-sm" id="salon-prev-page" ${salonState.page <= 1 ? 'disabled' : ''}>← Previous</button>
        <span class="meta">Page ${salonState.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + SALON_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} work${rows.length === 1 ? '' : 's'}</span>
        <button class="btn btn-sm" id="salon-next-page" ${salonState.page >= pages ? 'disabled' : ''}>Next →</button>
      </div>`;
    const prev = $('#salon-prev-page');
    const next = $('#salon-next-page');
    if (prev) prev.addEventListener('click', () => { salonState.page--; renderSalonTable(); });
    if (next) next.addEventListener('click', () => { salonState.page++; renderSalonTable(); });
  }
  function renderSalonYear() {
    const el = $('#salon-year');
    const { data, entry, year } = salonState;
    if (!el || !data) return;
    const counts = salonOrderedSections(data.sections).map((s) => `${salonSectionLabel(s)} ${entry.sections[s].toLocaleString()}`).join(' · ');
    const tabs = [{ id: 'all', label: 'All sections', n: entry.works }, ...salonOrderedSections(data.sections).map((s) => ({ id: s, label: salonSectionLabel(s), n: entry.sections[s] }))];
    el.innerHTML = `<div class="results-head"><div><h2>${year} — ${esc(data.salon)}</h2><div class="meta">${plural(entry.works, 'work')} by ${plural(entry.artists, 'artist')} · ${counts}</div></div></div>
      <div class="filters">${tabs.map((t) => `<button class="chip ${salonState.section === t.id ? 'active' : ''}" data-sec="${esc(t.id)}">${esc(t.label)} (${t.n.toLocaleString()})</button>`).join('')}</div>
      <div class="salon-search"><input id="salon-q" type="search" placeholder="Filter this year by artist or title…" value="${esc(salonState.query)}" aria-label="Filter works by artist or title"></div>
      <div id="salon-table-wrap"></div>
      <div class="notice">About these records — transcribed from the printed Salon livrets (via the Internet Archive; the years to 1881 from the Garland reprints) and parsed from OCR, so some titles carry OCR noise and a few artist names are fragments. Coverage runs from 1673 to 1898: from 1882 the Salon was organised by the Société des Artistes Français, and those livrets were transcribed in the same way. Nine years between 1882 and 1900 are missing — 1883, 1887, 1888, 1889, 1892, 1894, 1896, 1899 and 1900 — because no digitised copy of those livrets is available to us. The 1898 records come from Baschet's Catalogue illustré, which prints only the Painting and Sculpture sections, so that year is partial: the Drawings section and everything after Sculpture in the official livret are not included. The 1886 volume survives only in a poor scan: most of its Architecture entries appear under Gravure, and its opening entries are lost. Artist names have been corrected where the OCR misread them, against authority records (Wikidata artist lists and the frequent clean spellings in the livrets themselves); only high-confidence corrections are applied, ambiguous names are left as printed, and the original printed spellings are preserved in the data files. A “~” after a catalogue number means the number was inferred from the sequence or looks suspect in the printed text. Every artist name links to the Atlas name search — pick the right person there to read the full research report. No images yet: most Salon works have no surviving image in the open sources, so this first version is the catalogue itself, browsable year by year.</div>`;
    el.querySelectorAll('[data-sec]').forEach((b) => b.addEventListener('click', () => {
      salonState.section = b.dataset.sec;
      salonState.page = 1;
      el.querySelectorAll('[data-sec]').forEach((x) => x.classList.toggle('active', x === b));
      renderSalonTable();
    }));
    const q = $('#salon-q');
    q.addEventListener('input', () => { salonState.query = q.value; salonState.page = 1; renderSalonTable(); });
    renderSalonTable();
  }
  function renderSalonControls(idx, year) {
    const el = $('#salon-controls');
    if (!el) return;
    const years = idx.years.map((y) => y.year);
    const i = years.indexOf(year);
    const prev = i > 0 ? years[i - 1] : null;
    const next = i >= 0 && i < years.length - 1 ? years[i + 1] : null;
    const inList = i >= 0;
    const opt = (y) => `<option value="${y.year}"${y.year === year ? ' selected' : ''}>${y.year} — ${y.works.toLocaleString()} works</option>`;
    el.innerHTML = `<form id="salon-form" class="browse-form">
        <button class="btn" type="button" id="salon-prev-year" ${prev == null ? 'disabled' : ''}>← ${prev ?? ''}</button>
        <label>Year <select id="salon-year-select" aria-label="Salon year">${inList ? '' : '<option value="" selected>Choose a year…</option>'}${idx.years.map(opt).join('')}</select></label>
        <button class="btn" type="button" id="salon-next-year" ${next == null ? 'disabled' : ''}>${next ?? ''} →</button>
      </form>
      <div class="salon-famous"><span class="meta">Famous years:</span>${SALON_FAMOUS.map((f) => `<a class="chip" href="#/salon/${f.year}">${esc(f.label)}</a>`).join('')}</div>`;
    $('#salon-year-select').addEventListener('change', (e) => { if (e.target.value) location.hash = '#/salon/' + e.target.value; });
    if (prev != null) $('#salon-prev-year').addEventListener('click', () => { location.hash = '#/salon/' + prev; });
    if (next != null) $('#salon-next-year').addEventListener('click', () => { location.hash = '#/salon/' + next; });
  }
  async function viewSalon(p, path) {
    const seg = (path.split('/')[2] || p.year || '').trim();
    let year = parseInt(seg || SALON_DEFAULT_YEAR, 10);
    if (!Number.isFinite(year)) year = SALON_DEFAULT_YEAR;
    salonState.year = year;
    salonState.section = 'all';
    salonState.query = '';
    salonState.page = 1;
    salonState.data = null;
    salonState.entry = null;
    app.innerHTML = `<h1 style="font-size:38px">Salon Time Machine</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Step into any Paris Salon, 1673–1898, as it was catalogued: every work, every exhibitor, in the sections the livret itself used. Pick a year — or walk year by year — and every artist name opens the Atlas name search, so a Salon exhibitor leads straight to the full research report.</p>
      <div id="salon-controls">${spinner('Loading Salon years…')}</div>
      <div id="salon-year"></div>`;
    let idx;
    try {
      idx = await loadSalonIndex();
    } catch (e) {
      $('#salon-controls').innerHTML = `<div class="notice error">The Salon catalogue could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderSalonControls(idx, year);
    const entry = idx.years.find((y) => y.year === year);
    if (!entry) {
      const years = idx.years.map((y) => y.year);
      const before = [...years].reverse().find((y) => y < year);
      const after = years.find((y) => y > year);
      $('#salon-year').innerHTML = `<div class="notice">There is no Salon catalogue for ${year} in this collection — either no Salon was held that year, or its livret has not survived.${before ? ` The previous Salon with a catalogue is <a href="#/salon/${before}">${before}</a>${after ? `, the next is <a href="#/salon/${after}">${after}</a>` : ''}.` : ''}</div>`;
      return;
    }
    salonState.entry = entry;
    $('#salon-year').innerHTML = spinner(`Loading the ${year} Salon…`);
    try {
      salonState.data = await loadSalonYear(year);
    } catch (e) {
      $('#salon-year').innerHTML = `<div class="notice error">The ${year} Salon catalogue could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderSalonYear();
  }

  /* ==================================================== royal academy view */
  const RA_OCCUPATION_ORDER = ['Painter', 'Sculptor', 'Architect', 'Engraver', 'Etcher', 'Draughtsman', 'Modeller', 'Lithographer', 'Designer', 'Carver', 'Enameller'];
  const RA_MAIN_OCCUPATIONS = ['Painter', 'Sculptor', 'Architect', 'Engraver'];
  const RA_OTHER_OCCUPATIONS = RA_OCCUPATION_ORDER.filter((o) => !RA_MAIN_OCCUPATIONS.includes(o));
  const RA_FAMOUS = [
    { year: 1769, label: '1769 · The first exhibition' },
    { year: 1821, label: '1821 · The Hay Wain' },
    { year: 1851, label: '1851' },
    { year: 1905, label: '1905 · The last year here' },
  ];
  const RA_DEFAULT_YEAR = 1769;
  const RA_PAGE_SIZE = 50;
  let raIndex = null;
  const raYearCache = new Map();
  const raState = { year: RA_DEFAULT_YEAR, occupation: 'all', query: '', page: 1, data: null, entry: null };
  /* Search-all-years state. all.json rows are the year-file rows with the
     year prepended: [year, catalogueNo, surname, given, occupation,
     address, title, medium, flags]. */
  let raAllWorks = null;
  const raSearchState = { mode: 'artist', query: '', result: null, selected: null, page: 1 };
  async function loadRAAll() {
    if (!raAllWorks) {
      raAllWorks = salonFetchJSON('/data/ra/all.json')
        .then((d) => d.works)
        .catch((e) => { raAllWorks = null; throw e; });
    }
    return raAllWorks;
  }
  function raAllName(w) {
    return [w[3], w[2]].filter(Boolean).join(' ');
  }
  function raAllNumCell(w) {
    if (w[1] == null) return '<span class="muted" title="No catalogue number could be read in the source — none has been invented">—</span>';
    if (w[8] & 1) return `${esc(w[1])} <span class="flag-mark" title="Catalogue number as printed in Graves’s dictionary, but uncertain — it may be an OCR misreading of the source scan">~</span>`;
    return esc(w[1]);
  }
  function raNorm(s) {
    return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  }
  function raWordsMatch(text, words) {
    const t = raNorm(text);
    return words.every((w) => t.includes(w));
  }
  async function loadRAIndex() {
    if (!raIndex) raIndex = await salonFetchJSON('/data/ra/index.json');
    return raIndex;
  }
  async function loadRAYear(year) {
    if (!raYearCache.has(year)) {
      raYearCache.set(year, salonFetchJSON(`/data/ra/${year}.json`)
        .catch((e) => { raYearCache.delete(year); throw e; }));
    }
    return raYearCache.get(year);
  }
  /** Full name for the Atlas name search: given names + surname as printed. */
  function raFullName(w) {
    return [w[2], w[1]].filter(Boolean).join(' ');
  }
  function raNumCell(w) {
    if (w[0] == null) return '<span class="muted" title="No catalogue number could be read in the source — none has been invented">—</span>';
    if (w[7] & 1) return `${esc(w[0])} <span class="flag-mark" title="Catalogue number as printed in Graves’s dictionary, but uncertain — it may be an OCR misreading of the source scan">~</span>`;
    return esc(w[0]);
  }
  function raFiltered() {
    const { data, occupation, query } = raState;
    if (!data) return [];
    const q = query.trim().toLowerCase();
    return data.works.filter((w) => {
      if (occupation === 'other' && !RA_OTHER_OCCUPATIONS.includes(w[3])) return false;
      if (occupation !== 'all' && occupation !== 'other' && w[3] !== occupation) return false;
      if (!q) return true;
      return raFullName(w).toLowerCase().includes(q) || (w[5] || '').toLowerCase().includes(q);
    });
  }
  function renderRATable() {
    const wrap = $('#ra-table-wrap');
    if (!wrap || !raState.data) return;
    const rows = raFiltered();
    const pages = Math.max(1, Math.ceil(rows.length / RA_PAGE_SIZE));
    if (raState.page > pages) raState.page = pages;
    const start = (raState.page - 1) * RA_PAGE_SIZE;
    const pageRows = rows.slice(start, start + RA_PAGE_SIZE);
    if (!rows.length) {
      wrap.innerHTML = '<div class="notice">No works in this year match — try another spelling, a different occupation, or clear the search box.</div>';
      return;
    }
    wrap.innerHTML = `<div class="table-wrap"><table class="table salon-table">
      <thead><tr><th class="salon-num">No.</th><th>Title</th><th>Artist</th><th>Address</th><th>Occupation</th><th>Medium</th></tr></thead>
      <tbody>${pageRows.map((w) => `<tr>
        <td class="salon-num">${raNumCell(w)}</td>
        <td>${esc(w[5] || '')}</td>
        <td><a href="#/search?q=${enc(raFullName(w))}">${esc(raFullName(w))}</a></td>
        <td>${esc(w[4] || '')}</td>
        <td>${esc(w[3] || '')}</td>
        <td>${esc(w[6] || '')}</td>
      </tr>`).join('')}</tbody></table></div>
      <div class="pager">
        <button class="btn btn-sm" id="ra-prev-page" ${raState.page <= 1 ? 'disabled' : ''}>← Previous</button>
        <span class="meta">Page ${raState.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + RA_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} work${rows.length === 1 ? '' : 's'}</span>
        <button class="btn btn-sm" id="ra-next-page" ${raState.page >= pages ? 'disabled' : ''}>Next →</button>
      </div>`;
    const prev = $('#ra-prev-page');
    const next = $('#ra-next-page');
    if (prev) prev.addEventListener('click', () => { raState.page--; renderRATable(); });
    if (next) next.addEventListener('click', () => { raState.page++; renderRATable(); });
  }
  function renderRAYear() {
    const el = $('#ra-year');
    const { data, entry, year } = raState;
    if (!el || !data) return;
    const occ = entry.occupations || {};
    const counts = RA_OCCUPATION_ORDER.filter((o) => occ[o]).map((o) => `${o} ${occ[o].toLocaleString()}`).join(' · ');
    const otherN = RA_OTHER_OCCUPATIONS.reduce((n, o) => n + (occ[o] || 0), 0);
    const tabs = [{ id: 'all', label: 'All', n: entry.works },
      ...RA_MAIN_OCCUPATIONS.filter((o) => occ[o]).map((o) => ({ id: o, label: o, n: occ[o] })),
      ...(otherN ? [{ id: 'other', label: 'Other crafts', n: otherN }] : [])];
    el.innerHTML = `<div class="results-head"><div><h2>${year} — ${esc(data.exhibition)}</h2><div class="meta">${plural(entry.works, 'work')} by ${plural(entry.artists, 'artist')}${counts ? ` · ${counts}` : ''}</div></div></div>
      <div class="filters">${tabs.map((t) => `<button class="chip ${raState.occupation === t.id ? 'active' : ''}" data-occ="${esc(t.id)}">${esc(t.label)} (${t.n.toLocaleString()})</button>`).join('')}</div>
      <div class="salon-search"><input id="ra-q" type="search" placeholder="Filter this year by artist or title…" value="${esc(raState.query)}" aria-label="Filter works by artist or title"></div>
      <div id="ra-table-wrap"></div>
      <div class="notice">About these records — compiled from Algernon Graves, “The Royal Academy of Arts: A Complete Dictionary of Contributors and Their Work” (1905–06), with the 1905 exhibition recovered from the Paul Mellon Centre’s RA Chronicle catalogue transcription. Names, addresses and titles are as printed, with the OCR noise of the source scans, so some titles carry garbled words and a few artist names are fragments. A “~” after a catalogue number means the number is uncertain in the source. About 12,200 records have no readable catalogue number and show “—” — no number has been invented for them. A further 1,543 records in the full database, whose year could not be resolved, are not in this browser. Every artist name links to the Atlas name search — pick the right person there to read the full research report. No images yet: this first version is the catalogue itself, browsable year by year.</div>`;
    el.querySelectorAll('[data-occ]').forEach((b) => b.addEventListener('click', () => {
      raState.occupation = b.dataset.occ;
      raState.page = 1;
      el.querySelectorAll('[data-occ]').forEach((x) => x.classList.toggle('active', x === b));
      renderRATable();
    }));
    const q = $('#ra-q');
    q.addEventListener('input', () => { raState.query = q.value; raState.page = 1; renderRATable(); });
    renderRATable();
  }
  function renderRAControls(idx, year) {
    const el = $('#ra-controls');
    if (!el) return;
    const years = idx.years.map((y) => y.year);
    const i = years.indexOf(year);
    const prev = i > 0 ? years[i - 1] : null;
    const next = i >= 0 && i < years.length - 1 ? years[i + 1] : null;
    const inList = i >= 0;
    const opt = (y) => `<option value="${y.year}"${y.year === year ? ' selected' : ''}>${y.year} — ${y.works.toLocaleString()} works</option>`;
    el.innerHTML = `<form id="ra-form" class="browse-form">
        <button class="btn" type="button" id="ra-prev-year" ${prev == null ? 'disabled' : ''}>← ${prev ?? ''}</button>
        <label>Year <select id="ra-year-select" aria-label="Royal Academy year">${inList ? '' : '<option value="" selected>Choose a year…</option>'}${idx.years.map(opt).join('')}</select></label>
        <button class="btn" type="button" id="ra-next-year" ${next == null ? 'disabled' : ''}>${next ?? ''} →</button>
      </form>
      <div class="salon-famous"><span class="meta">Famous years:</span>${RA_FAMOUS.map((f) => `<a class="chip" href="#/ra/${f.year}">${esc(f.label)}</a>`).join('')}</div>`;
    $('#ra-year-select').addEventListener('change', (e) => { if (e.target.value) location.hash = '#/ra/' + e.target.value; });
    if (prev != null) $('#ra-prev-year').addEventListener('click', () => { location.hash = '#/ra/' + prev; });
    if (next != null) $('#ra-next-year').addEventListener('click', () => { location.hash = '#/ra/' + next; });
  }
  function raArtistGroups(works, words) {
    const groups = new Map();
    for (const w of works) {
      const name = raAllName(w);
      if (!raWordsMatch(name, words)) continue;
      // Group on the case-insensitive name: Graves prints surnames in
      // capitals, the 1905 Mellon transcription in mixed case, and those
      // are the same people, not different artists. The display name is
      // the most frequent printed form. Genuinely different printed
      // forms (initials vs full names) still list separately.
      const key = `${raNorm(w[2])}|${raNorm(w[3])}`;
      if (!groups.has(key)) groups.set(key, { key, forms: new Map(), works: [] });
      const g = groups.get(key);
      g.forms.set(name, (g.forms.get(name) || 0) + 1);
      g.works.push(w);
    }
    return [...groups.values()].map((g) => ({
      key: g.key,
      name: [...g.forms.entries()].sort((a, b) => b[1] - a[1])[0][0],
      works: g.works,
    })).sort((a, b) => a.name.localeCompare(b.name));
  }
  function renderRASearch() {
    const el = $('#ra-search');
    if (!el) return;
    const s = raSearchState;
    const total = raIndex ? raIndex.totalWorks.toLocaleString() : '161,019';
    el.innerHTML = `<div class="results-head"><div><h2>Search all years, 1769–1905</h2>
      <div class="meta">An artist’s complete Royal Academy record in one view — or a title searched across every exhibition at once: all eight volumes of Graves at a keystroke. Covers the same ${total} dated records as the year browser below.</div></div></div>
      <div class="filters">
        <button class="chip ${s.mode === 'artist' ? 'active' : ''}" data-ra-mode="artist">By artist</button>
        <button class="chip ${s.mode === 'title' ? 'active' : ''}" data-ra-mode="title">By title</button>
      </div>
      <form id="ra-search-form" class="salon-search">
        <input id="ra-search-q" type="search" placeholder="${s.mode === 'artist' ? 'Artist’s name — e.g. Arthur Wardle' : 'A title, or its distinctive words — e.g. cimabue, trysting, muffet'}" value="${esc(s.query)}" aria-label="Search all Royal Academy years">
        <button class="btn" type="submit">Search</button>
      </form>
      <div class="meta" style="margin:6px 0 10px">${s.mode === 'artist' ? 'Capitalisation is ignored — Graves prints surnames in capitals, the 1905 transcription does not, and those are the same people. Genuinely different printed forms of a name (initials vs a full name) still list separately.' : 'Tip: one or two distinctive words beat a full exact title — titles were printed in full and the OCR garbles the odd word, so an exact phrase can miss a work that a single word finds.'}</div>
      <div id="ra-search-results"></div>`;
    el.querySelectorAll('[data-ra-mode]').forEach((b) => b.addEventListener('click', () => {
      raSearchState.mode = b.dataset.raMode;
      raSearchState.result = null;
      raSearchState.selected = null;
      raSearchState.page = 1;
      renderRASearch();
    }));
    $('#ra-search-form').addEventListener('submit', (e) => { e.preventDefault(); runRASearch(); });
    renderRASearchResults();
  }
  async function runRASearch() {
    const input = $('#ra-search-q');
    const q = (input ? input.value : '').trim();
    raSearchState.query = q;
    raSearchState.selected = null;
    raSearchState.page = 1;
    const wrap = $('#ra-search-results');
    if (!q) { raSearchState.result = null; renderRASearchResults(); return; }
    if (wrap) wrap.innerHTML = spinner(raAllWorks ? 'Searching every year, 1769–1905…' : 'Searching every year, 1769–1905 — the first search downloads the complete index (about 18 MB); after that, searches are instant…');
    let works;
    try {
      works = await loadRAAll();
    } catch (e) {
      if (wrap) wrap.innerHTML = `<div class="notice error">The all-years index could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    const words = raNorm(q).split(' ').filter(Boolean);
    if (raSearchState.mode === 'artist') {
      const artists = raArtistGroups(works, words);
      raSearchState.result = { type: 'artist', artists };
      if (artists.length === 1) raSearchState.selected = artists[0].key;
    } else {
      raSearchState.result = { type: 'title', rows: works.filter((w) => raWordsMatch(w[6], words)) };
    }
    renderRASearchResults();
  }
  function renderRASearchResults() {
    const wrap = $('#ra-search-results');
    if (!wrap) return;
    const s = raSearchState;
    const r = s.result;
    if (!r) { wrap.innerHTML = ''; return; }
    if (r.type === 'artist') {
      if (!r.artists.length) {
        wrap.innerHTML = `<div class="notice">No artist in Graves matches “${esc(s.query)}” — try the surname alone, or another spelling.</div>`;
        return;
      }
      const sel = r.artists.find((a) => a.key === s.selected);
      if (!sel) {
        wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(r.artists.length, 'artist')} in Graves match “${esc(s.query)}”:</div>
        <div class="table-wrap"><table class="table salon-table"><thead><tr><th>Artist</th><th>Works</th><th>Years exhibited</th><th></th></tr></thead>
        <tbody>${r.artists.map((a) => { const ys = a.works.map((w) => w[0]); return `<tr><td>${esc(a.name)}</td><td>${a.works.length.toLocaleString()}</td><td>${Math.min(...ys)}–${Math.max(...ys)}</td><td><button class="btn btn-sm" data-ra-artist="${esc(a.key)}">View works →</button></td></tr>`; }).join('')}</tbody></table></div>`;
        wrap.querySelectorAll('[data-ra-artist]').forEach((b) => b.addEventListener('click', () => { raSearchState.selected = b.dataset.raArtist; renderRASearchResults(); }));
        return;
      }
      const ys = sel.works.map((w) => w[0]);
      const occs = [...new Set(sel.works.map((w) => w[4]).filter(Boolean))].join(', ');
      wrap.innerHTML = `${r.artists.length > 1 ? '<button class="btn btn-sm" id="ra-search-back" style="margin-bottom:10px">← All matching artists</button>' : ''}
        <div class="results-head"><div><h2>${esc(sel.name)}</h2>
        <div class="meta">${plural(sel.works.length, 'work')} at the Royal Academy, ${Math.min(...ys)}–${Math.max(...ys)}${occs ? ` · ${esc(occs)}` : ''} · <a href="#/search?q=${enc(sel.name)}">Atlas research report →</a></div></div></div>
        <div class="table-wrap"><table class="table salon-table">
        <thead><tr><th>Year</th><th class="salon-num">No.</th><th>Title</th><th>Address</th><th>Occupation</th><th>Medium</th></tr></thead>
        <tbody>${sel.works.map((w) => `<tr>
          <td><a href="#/ra/${w[0]}">${w[0]}</a></td>
          <td class="salon-num">${raAllNumCell(w)}</td>
          <td>${esc(w[6] || '')}</td>
          <td>${esc(w[5] || '')}</td>
          <td>${esc(w[4] || '')}</td>
          <td>${esc(w[7] || '')}</td>
        </tr>`).join('')}</tbody></table></div>`;
      const back = $('#ra-search-back');
      if (back) back.addEventListener('click', () => { raSearchState.selected = null; renderRASearchResults(); });
      return;
    }
    const rows = r.rows;
    if (!rows.length) {
      wrap.innerHTML = `<div class="notice">No title in 1769–1905 matches “${esc(s.query)}” — try fewer or different distinctive words; the OCR garbles the odd word.</div>`;
      return;
    }
    const pages = Math.max(1, Math.ceil(rows.length / RA_PAGE_SIZE));
    if (s.page > pages) s.page = pages;
    const start = (s.page - 1) * RA_PAGE_SIZE;
    const pageRows = rows.slice(start, start + RA_PAGE_SIZE);
    wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(rows.length, 'work')} across 1769–1905 match “${esc(s.query)}”${rows.length > 1000 ? ' — a lot; add another distinctive word to narrow it down' : ''}:</div>
      <div class="table-wrap"><table class="table salon-table">
      <thead><tr><th>Year</th><th class="salon-num">No.</th><th>Title</th><th>Artist</th><th>Occupation</th></tr></thead>
      <tbody>${pageRows.map((w) => `<tr>
        <td><a href="#/ra/${w[0]}">${w[0]}</a></td>
        <td class="salon-num">${raAllNumCell(w)}</td>
        <td>${esc(w[6] || '')}</td>
        <td><a href="#/search?q=${enc(raAllName(w))}">${esc(raAllName(w))}</a></td>
        <td>${esc(w[4] || '')}</td>
      </tr>`).join('')}</tbody></table></div>
      <div class="pager">
        <button class="btn btn-sm" id="ra-s-prev" ${s.page <= 1 ? 'disabled' : ''}>← Previous</button>
        <span class="meta">Page ${s.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + RA_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} works</span>
        <button class="btn btn-sm" id="ra-s-next" ${s.page >= pages ? 'disabled' : ''}>Next →</button>
      </div>`;
    const prev = $('#ra-s-prev');
    const next = $('#ra-s-next');
    if (prev) prev.addEventListener('click', () => { s.page--; renderRASearchResults(); });
    if (next) next.addEventListener('click', () => { s.page++; renderRASearchResults(); });
  }
  async function viewRA(p, path) {
    const seg = (path.split('/')[2] || p.year || '').trim();
    let year = parseInt(seg || RA_DEFAULT_YEAR, 10);
    if (!Number.isFinite(year)) year = RA_DEFAULT_YEAR;
    raState.year = year;
    raState.occupation = 'all';
    raState.query = '';
    raState.page = 1;
    raState.data = null;
    raState.entry = null;
    app.innerHTML = `<h1 style="font-size:38px">Royal Academy Time Machine</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Step into any Royal Academy Summer Exhibition, 1769–1905, as Graves’s dictionary recorded it: every work, every contributor, with the address the catalogue itself printed. Pick a year — or walk year by year — and every artist name opens the Atlas name search, so an exhibitor leads straight to the full research report.</p>
      <div id="ra-controls">${spinner('Loading Royal Academy years…')}</div>
      <div id="ra-search"></div>
      <div id="ra-year"></div>`;
    let idx;
    try {
      idx = await loadRAIndex();
    } catch (e) {
      $('#ra-controls').innerHTML = `<div class="notice error">The Royal Academy catalogue could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderRAControls(idx, year);
    renderRASearch();
    const entry = idx.years.find((y) => y.year === year);
    if (!entry) {
      const years = idx.years.map((y) => y.year);
      const before = [...years].reverse().find((y) => y < year);
      const after = years.find((y) => y > year);
      $('#ra-year').innerHTML = `<div class="notice">There is no Royal Academy Summer Exhibition for ${year} in this collection — the browser covers every year from 1769 to 1905.${before ? ` The nearest year before is <a href="#/ra/${before}">${before}</a>${after ? `, the next is <a href="#/ra/${after}">${after}</a>` : ''}.` : ''}</div>`;
      return;
    }
    raState.entry = entry;
    $('#ra-year').innerHTML = spinner(`Loading the ${year} Summer Exhibition…`);
    try {
      raState.data = await loadRAYear(year);
    } catch (e) {
      $('#ra-year').innerHTML = `<div class="notice error">The ${year} Summer Exhibition could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderRAYear();
  }

  /* ================================================== loan exhibitions */
  const LOAN_PAGE_SIZE = 50;
  let loanIndex = null;
  const loanLetterCache = new Map();
  let loanAllWorks = null;
  const loanState = { letter: null, data: null, selected: null };
  const loanSearchState = { mode: 'artist', query: '', result: null, selected: null, page: 1 };
  async function loadLoanIndex() {
    if (!loanIndex) loanIndex = await salonFetchJSON('/data/loan/index.json');
    return loanIndex;
  }
  async function loadLoanLetter(letter) {
    if (!loanLetterCache.has(letter)) {
      loanLetterCache.set(letter, salonFetchJSON(`/data/loan/${letter}.json`)
        .catch((e) => { loanLetterCache.delete(letter); throw e; }));
    }
    return loanLetterCache.get(letter);
  }
  async function loadLoanAll() {
    if (!loanAllWorks) {
      loanAllWorks = salonFetchJSON('/data/loan/all.json')
        .then((d) => d.works)
        .catch((e) => { loanAllWorks = null; throw e; });
    }
    return loanAllWorks;
  }
  /* Work rows (letter files and all.json alike):
     [artist|artistIdx, year, no, noSuspect, title, size, owner, venue, ownerUncertain] */
  function loanNumCell(w) {
    if (!w[2]) return '<span class="muted" title="No catalogue number could be read in the source — none has been invented">—</span>';
    if (w[3]) return `${esc(w[2])} <span class="flag-mark" title="Catalogue number as printed in Graves, but the scan’s digits were ambiguous — the systematic OCR confusions (I/l for 1, O for 0, Q for 9) have been normalised">~</span>`;
    return esc(w[2]);
  }
  function loanOwnerCell(w) {
    if (!w[6]) return '<span class="muted">—</span>';
    return esc(w[6]) + (w[8] ? ' <span class="flag-mark" title="This owner was separated from the title by column position alone and may be mis-split">~</span>' : '');
  }
  function loanReportName(name) {
    return (name || '').replace(/\s*\d{3,4}\s*[-–]\s*\d{3,4}\.?$/, '').replace(/\.+$/, '').trim();
  }
  function loanWorkRow(w, artistName) {
    return `<tr>
      <td>${w[1] ?? '<span class="muted">—</span>'}</td>
      <td>${esc(w[7] || '')}</td>
      <td class="salon-num">${loanNumCell(w)}</td>
      <td>${esc(w[4] || '')}</td>
      <td>${esc(w[5] || '')}</td>
      ${artistName !== undefined ? `<td><a href="#/search?q=${enc(loanReportName(artistName))}">${esc(artistName)}</a></td>` : `<td>${loanOwnerCell(w)}</td>`}
    </tr>`;
  }
  function renderLoanSearch() {
    const el = $('#loan-search');
    if (!el) return;
    const s = loanSearchState;
    const total = loanIndex ? loanIndex.totalWorks.toLocaleString() : '42,727';
    const artists = loanIndex ? loanIndex.totalArtists.toLocaleString() : '3,435';
    el.innerHTML = `<div class="results-head"><div><h2>Search the whole book</h2>
      <div class="meta">Every work in Graves’s <i>Century of Loan Exhibitions</i> at a keystroke: ${total} works under ${artists} artist headings. By artist — that artist’s complete loan-exhibition record in one view. By title — a work traced across every exhibition. By owner — everything a collector or institution lent, which is a provenance record in itself.</div></div></div>
      <div class="filters">
        <button class="chip ${s.mode === 'artist' ? 'active' : ''}" data-loan-mode="artist">By artist</button>
        <button class="chip ${s.mode === 'title' ? 'active' : ''}" data-loan-mode="title">By title</button>
        <button class="chip ${s.mode === 'owner' ? 'active' : ''}" data-loan-mode="owner">By owner (lender)</button>
      </div>
      <form id="loan-search-form" class="salon-search">
        <input id="loan-search-q" type="search" placeholder="${s.mode === 'artist' ? 'Artist’s name — e.g. Turner, Gainsborough, Unknown Painters' : s.mode === 'title' ? 'A title, or its distinctive words — e.g. virgin child, shipwreck' : 'Owner’s name — e.g. Earl of Yarborough, Wynn Ellis, Royal Academy'}" value="${esc(s.query)}" aria-label="Search the loan exhibitions">
        <button class="btn" type="submit">Search</button>
      </form>
      <div class="meta" style="margin:6px 0 10px">${s.mode === 'title' ? 'Tip: one or two distinctive words beat a full exact title — titles were printed in full and the OCR garbles the odd word, so an exact phrase can miss a work that a single word finds.' : 'Names are as Graves printed them, so the same person may appear under more than one printed form (initials vs a full name); those list separately.'}</div>
      <div id="loan-search-results"></div>`;
    el.querySelectorAll('[data-loan-mode]').forEach((b) => b.addEventListener('click', () => {
      loanSearchState.mode = b.dataset.loanMode;
      loanSearchState.result = null;
      loanSearchState.selected = null;
      loanSearchState.page = 1;
      renderLoanSearch();
    }));
    $('#loan-search-form').addEventListener('submit', (e) => { e.preventDefault(); runLoanSearch(); });
    renderLoanSearchResults();
  }
  async function runLoanSearch() {
    const input = $('#loan-search-q');
    const q = (input ? input.value : '').trim();
    loanSearchState.query = q;
    loanSearchState.selected = null;
    loanSearchState.page = 1;
    const wrap = $('#loan-search-results');
    if (!q) { loanSearchState.result = null; renderLoanSearchResults(); return; }
    if (wrap) wrap.innerHTML = spinner(loanAllWorks ? 'Searching the whole book…' : 'Searching the whole book — the first search downloads the complete index (about 6 MB); after that, searches are instant…');
    let works;
    try {
      works = await loadLoanAll();
    } catch (e) {
      if (wrap) wrap.innerHTML = `<div class="notice error">The loan exhibitions index could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    const words = raNorm(q).split(' ').filter(Boolean);
    if (loanSearchState.mode === 'title') {
      loanSearchState.result = { type: 'title', rows: works.filter((w) => raWordsMatch(w[4], words)) };
    } else {
      const field = loanSearchState.mode === 'artist' ? 0 : 6;
      const groups = new Map();
      for (const w of works) {
        const name = w[field];
        if (!name || !raWordsMatch(name, words)) continue;
        if (!groups.has(name)) groups.set(name, []);
        groups.get(name).push(w);
      }
      const list = [...groups.entries()].map(([name, ws]) => ({ name, works: ws }))
        .sort((a, b) => a.name.localeCompare(b.name));
      loanSearchState.result = { type: loanSearchState.mode, groups: list };
      if (list.length === 1) loanSearchState.selected = list[0].name;
    }
    renderLoanSearchResults();
  }
  function renderLoanSearchResults() {
    const wrap = $('#loan-search-results');
    if (!wrap) return;
    const s = loanSearchState;
    const r = s.result;
    if (!r) { wrap.innerHTML = ''; return; }
    if (r.type === 'title') {
      const rows = r.rows;
      if (!rows.length) {
        wrap.innerHTML = `<div class="notice">No title in 1813–1912 matches “${esc(s.query)}” — try fewer or different distinctive words; the OCR garbles the odd word.</div>`;
        return;
      }
      const pages = Math.max(1, Math.ceil(rows.length / LOAN_PAGE_SIZE));
      if (s.page > pages) s.page = pages;
      const start = (s.page - 1) * LOAN_PAGE_SIZE;
      const pageRows = rows.slice(start, start + LOAN_PAGE_SIZE);
      wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(rows.length, 'work')} across 1813–1912 match “${esc(s.query)}”${rows.length > 1000 ? ' — a lot; add another distinctive word to narrow it down' : ''}:</div>
        <div class="table-wrap"><table class="table salon-table">
        <thead><tr><th>Year</th><th>Venue</th><th class="salon-num">No.</th><th>Title</th><th>Size</th><th>Artist</th></tr></thead>
        <tbody>${pageRows.map((w) => loanWorkRow(w, w[0])).join('')}</tbody></table></div>
        <div class="pager">
          <button class="btn btn-sm" id="loan-s-prev" ${s.page <= 1 ? 'disabled' : ''}>← Previous</button>
          <span class="meta">Page ${s.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + LOAN_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} works</span>
          <button class="btn btn-sm" id="loan-s-next" ${s.page >= pages ? 'disabled' : ''}>Next →</button>
        </div>`;
      const prev = $('#loan-s-prev');
      const next = $('#loan-s-next');
      if (prev) prev.addEventListener('click', () => { s.page--; renderLoanSearchResults(); });
      if (next) next.addEventListener('click', () => { s.page++; renderLoanSearchResults(); });
      return;
    }
    const groups = r.groups;
    const kind = r.type === 'artist' ? 'artist' : 'owner';
    if (!groups.length) {
      wrap.innerHTML = `<div class="notice">No ${kind} in Graves matches “${esc(s.query)}” — try the surname alone, or another spelling.</div>`;
      return;
    }
    const sel = groups.find((g) => g.name === s.selected);
    if (!sel) {
      wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(groups.length, kind)} in Graves match “${esc(s.query)}”:</div>
      <div class="table-wrap"><table class="table salon-table"><thead><tr><th>${kind === 'artist' ? 'Artist' : 'Owner (lender)'}</th><th>Works</th><th>Years</th><th></th></tr></thead>
      <tbody>${groups.map((g) => { const ys = g.works.map((w) => w[1]).filter((y) => y != null); return `<tr><td>${esc(g.name)}</td><td>${g.works.length.toLocaleString()}</td><td>${ys.length ? `${Math.min(...ys)}–${Math.max(...ys)}` : '—'}</td><td><button class="btn btn-sm" data-loan-group="${esc(g.name)}">View works →</button></td></tr>`; }).join('')}</tbody></table></div>`;
      wrap.querySelectorAll('[data-loan-group]').forEach((b) => b.addEventListener('click', () => { loanSearchState.selected = b.dataset.loanGroup; renderLoanSearchResults(); }));
      return;
    }
    const ys = sel.works.map((w) => w[1]).filter((y) => y != null);
    const head = kind === 'artist'
      ? `<h2>${esc(sel.name)}</h2><div class="meta">${plural(sel.works.length, 'work')} at loan exhibitions${ys.length ? `, ${Math.min(...ys)}–${Math.max(...ys)}` : ''} · <a href="#/search?q=${enc(loanReportName(sel.name))}">Atlas research report →</a></div>`
      : `<h2>${esc(sel.name)}</h2><div class="meta">${plural(sel.works.length, 'work')} lent to loan exhibitions${ys.length ? `, ${Math.min(...ys)}–${Math.max(...ys)}` : ''} · by ${plural(new Set(sel.works.map((w) => w[0])).size, 'artist')}</div>`;
    wrap.innerHTML = `${groups.length > 1 ? '<button class="btn btn-sm" id="loan-search-back" style="margin-bottom:10px">← All matching ' + (kind === 'artist' ? 'artists' : 'owners') + '</button>' : ''}
      <div class="results-head"><div>${head}</div></div>
      <div class="table-wrap"><table class="table salon-table">
      <thead><tr><th>Year</th><th>Venue</th><th class="salon-num">No.</th><th>Title</th><th>Size</th><th>${kind === 'artist' ? 'Owner (lender)' : 'Artist'}</th></tr></thead>
      <tbody>${sel.works.map((w) => kind === 'artist' ? loanWorkRow(w) : loanWorkRow(w, w[0])).join('')}</tbody></table></div>`;
    const back = $('#loan-search-back');
    if (back) back.addEventListener('click', () => { loanSearchState.selected = null; renderLoanSearchResults(); });
  }
  function renderLoanBrowse() {
    const el = $('#loan-browse');
    if (!el || !loanIndex) return;
    const chips = loanIndex.letters.map((l) =>
      `<a class="chip ${loanState.letter === l.letter ? 'active' : ''}" href="#/loan/${l.letter}">${l.letter} · ${l.works.toLocaleString()}</a>`).join('');
    let body = '';
    if (loanState.letter && loanState.data) {
      const d = loanState.data;
      const selIdx = d.artists.findIndex((a) => a[0] === loanState.selected);
      if (selIdx >= 0) {
        const a = d.artists[selIdx];
        const works = d.works.filter((w) => w[0] === selIdx);
        body = `<button class="btn btn-sm" id="loan-browse-back" style="margin:12px 0 10px">← All artists under ${esc(loanState.letter)}</button>
          <div class="results-head"><div><h2>${esc(a[0])}</h2>
          <div class="meta">${plural(a[1], 'work')} at loan exhibitions${a[2] != null ? `, ${a[2]}–${a[3]}` : ''} · <a href="#/search?q=${enc(loanReportName(a[0]))}">Atlas research report →</a></div></div></div>
          <div class="table-wrap"><table class="table salon-table">
          <thead><tr><th>Year</th><th>Venue</th><th class="salon-num">No.</th><th>Title</th><th>Size</th><th>Owner (lender)</th></tr></thead>
          <tbody>${works.map((w) => loanWorkRow(w)).join('')}</tbody></table></div>`;
      } else {
        body = `<div class="results-head" style="margin-top:14px"><div><h2>Artists under ${esc(loanState.letter)}</h2>
          <div class="meta">${plural(d.artists.length, 'artist heading')} as Graves printed them · ${plural(d.works.length, 'work')}</div></div></div>
          <div class="table-wrap"><table class="table salon-table"><thead><tr><th>Artist</th><th>Works</th><th>Years</th><th></th></tr></thead>
          <tbody>${d.artists.map((a) => `<tr><td>${esc(a[0])}</td><td>${a[1].toLocaleString()}</td><td>${a[2] != null ? `${a[2]}–${a[3]}` : '—'}</td><td><button class="btn btn-sm" data-loan-artist="${esc(a[0])}">View works →</button></td></tr>`).join('')}</tbody></table></div>`;
      }
    }
    el.innerHTML = `<div class="results-head"><div><h2>Browse by artist</h2>
      <div class="meta">The book is arranged by artist — pick a letter to walk its headings, exactly as printed.</div></div></div>
      <div class="filters">${chips}</div>
      <div id="loan-letter">${body}</div>`;
    el.querySelectorAll('[data-loan-artist]').forEach((b) => b.addEventListener('click', () => {
      loanState.selected = b.dataset.loanArtist;
      renderLoanBrowse();
    }));
    const back = $('#loan-browse-back');
    if (back) back.addEventListener('click', () => { loanState.selected = null; renderLoanBrowse(); });
  }
  async function viewLoan(p, path) {
    const seg = (path.split('/')[2] || '').trim().toUpperCase();
    const letter = /^[A-Z]$/.test(seg) ? seg : null;
    if (loanState.letter !== letter) { loanState.selected = null; loanState.data = null; }
    loanState.letter = letter;
    app.innerHTML = `<h1 style="font-size:38px">A Century of Loan Exhibitions, 1813–1912</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Algernon Graves spent thirty years recording every work lent to a century of British loan exhibitions — the Royal Academy’s winter exhibitions, the British Institution, Manchester’s Art Treasures, the Grosvenor and New Galleries and hundreds more. His book is arranged by artist, and each work carries the owner who lent it: a provenance goldmine. Search it by artist, by title, or by the lender — or browse the artists letter by letter. Every artist name opens the Atlas name search, so an exhibitor leads straight to the full research report.</p>
      <div id="loan-search">${spinner('Loading the loan exhibitions…')}</div>
      <div id="loan-browse"></div>
      <div class="notice" style="margin-top:22px">About these records — compiled from Algernon Graves, “A Century of Loan Exhibitions 1813–1912” (1913–15; Kingsmead reprint), parsed from the Internet Archive scan of the book. 42,727 works under 3,435 artist headings at 271 venues, all as printed, with the OCR noise of the source scan: some titles carry garbled words, and sizes in particular suffer — a printed fraction such as ¾ is often read as a plain digit. A “~” after a catalogue number means the printed digits were ambiguous in the scan (the systematic confusions — I/l for 1, O for 0, Q for 9 — have been normalised); about 1,790 records have no readable catalogue number and show “—” — no number has been invented for them. A “~” after an owner means the owner was separated from the title by column position alone and may be mis-split; about 9% of records have no owner read at all. Artist headings are as printed, so one person may appear under several forms; “Unknown Painters” is Graves’s own heading for unattributed works and alone holds 2,659 of them. The reprint’s third volume — Graves’s index of owners — is not included; the By owner search above is built from the work records themselves. No images in this first version.</div>`;
    try {
      await loadLoanIndex();
    } catch (e) {
      $('#loan-search').innerHTML = `<div class="notice error">The loan exhibitions index could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderLoanSearch();
    renderLoanBrowse();
    if (letter) {
      const wrap = $('#loan-letter');
      if (wrap) wrap.innerHTML = spinner(`Loading artists under ${letter}…`);
      try {
        loanState.data = await loadLoanLetter(letter);
      } catch (e) {
        if (wrap) wrap.innerHTML = `<div class="notice error">The artists under ${letter} could not be loaded: ${esc(e.message)}</div>`;
        return;
      }
      renderLoanBrowse();
    }
  }

  /* ============================================= record of exhibitions */
  const EXH_PAGE_SIZE = 50;
  let exhIndex = null;
  const exhDataCache = new Map();
  let exhAllWorks = null;
  const exhSearchState = { mode: 'artist', query: '', result: null, selected: null, page: 1 };
  const exhState = { id: null, entry: null, records: null, section: 'all', query: '', page: 1, letter: null, selected: null };
  async function loadExhIndex() {
    if (!exhIndex) exhIndex = await salonFetchJSON('/data/exhibitions/index.json');
    return exhIndex;
  }
  async function loadExhRecords(id) {
    if (!exhDataCache.has(id)) {
      exhDataCache.set(id, salonFetchJSON(`/data/exhibitions/${id}.json`)
        .catch((e) => { exhDataCache.delete(id); throw e; }));
    }
    return exhDataCache.get(id);
  }
  async function loadExhAll() {
    if (!exhAllWorks) {
      exhAllWorks = salonFetchJSON('/data/exhibitions/all.json')
        .then((d) => d.works)
        .catch((e) => { exhAllWorks = null; throw e; });
    }
    return exhAllWorks;
  }
  /* The name as printed, minus the post-nominal tail (", R.H.A." and the
     like) — used for the Atlas name search and to find the surname. */
  function exhNamePart(artist) {
    return String(artist || '')
      .split(/,\s*(?:P\.?R\.?H\.?A|A\.?R\.?H\.?A|R\.?H\.?A|R\.?S\.?A|A\.?R\.?A|R\.?A|Bart|Esq)\b/i)[0]
      .replace(/[\s.,]+$/, '').trim();
  }
  /* Surname initial for the letter browse. Natural-order names as
     printed ("Walter F. Osborne, R.H.A.") file under the last name-like
     word of the name part; surname-first headings ("AIKEN, Charles A.")
     file under the name before the comma — its last word, so "De Wint,
     Peter" files as W, matching the natural-order treatment. When the
     part before the comma holds no surname (a comma inside initials,
     "L. E, Van Gorder"), the whole name is scanned as before. Accented
     letters count and fold to their base letter ("Guérin" files as G).
     Trailing OCR debris (a leaked medium, dimensions) is skipped. */
  function exhSurnameInitial(artist) {
    const skip = new Set(['canvas', 'panel', 'millboard', 'inches', 'inehes', 'size']);
    /* Honorifics are skipped in the surname-first scan only, so "Sir J,
       E. Millais" falls through to the whole-name scan and files as M,
       while a genuine surname like Lord in natural order still counts. */
    const honorifics = new Set(['sir', 'dame', 'lord', 'lady', 'rev', 'hon', 'fra', 'mons', 'monsieur', 'madame', 'mademoiselle']);
    const namePart = exhNamePart(artist);
    const comma = namePart.indexOf(',');
    const parts = comma >= 0
      ? [[namePart.slice(0, comma), true], [namePart, false]]
      : [[namePart, false]];
    for (const [part, skipHonorifics] of parts) {
      const toks = part.split(/\s+/);
      for (let i = toks.length - 1; i >= 0; i--) {
        const t = toks[i].replace(/[.,]+$/, '');
        if (t.length < 2 || !/^[\p{L}][\p{L}'’-]*$/u.test(t)) continue;
        if (skip.has(t.toLowerCase())) continue;
        if (skipHonorifics && honorifics.has(t.toLowerCase())) continue;
        return t.normalize('NFD').replace(/\p{M}/gu, '').charAt(0).toUpperCase();
      }
    }
    return '#';
  }
  /* EXH-NICE:BEGIN */
  /* Display-only capitalisation for the Record of Exhibitions. The
     parsed records stay exactly as printed; these functions regularise
     case and typography at render time — names and titles only, never
     spelling, so OCR garbles (corox, MARSHA^, DUG) survive untouched
     apart from their case. Applied only where the exhibitions views
     render artist, title or lender. */
  const EXH_PARTICLES = new Set(['de', 'le', 'la', 'les', 'du', 'des', 'van', 'von', 'der', 'den', 'ten', 'y', 'e', 'di', 'da', 'and', 'of', 'the']);
  const EXH_HONORIFICS = { sir: 'Sir', lord: 'Lord', lady: 'Lady', mrs: 'Mrs.', mr: 'Mr.', miss: 'Miss', dr: 'Dr.', rev: 'Rev.', hon: 'Hon.', rt: 'Rt.', esq: 'Esq.', mons: 'Mons.', monsieur: 'Monsieur', madame: 'Madame', mademoiselle: 'Mademoiselle', messrs: 'Messrs.', dame: 'Dame', capt: 'Capt.', col: 'Col.' };
  const EXH_PAREN_SMALL = new Set(['called', 'dit', 'née', 'nee', 'formerly', 'known', 'as', 'after']);
  const EXH_SMALL_WORDS = new Set(['a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'and', 'or', 'by', 'for', 'with', 'from', 'de', 'la', 'le', 'les', 'du', 'des', 'et', 'au', 'aux', 'en', 'sur', 'un', 'une', 'à']);

  /* The letters of an initial-cluster token ("j.", "R.A.", "m.p"), or
     null when the token is not one. Multi-letter words with a trailing
     period ("Hon.", "Dr.") do not match: their letters are not
     separated by periods. */
  function exhInitialLetters(tok) {
    return /^[A-Za-z](\.[A-Za-z])*\.?$/.test(tok) ? tok.replace(/\./g, '').toUpperCase() : null;
  }
  /* The rendered form of a period-separated cluster token, or null.
     Covers single-letter initials ("R.A.") and degree-style clusters
     whose groups run to two letters and are all one case as printed
     ("ll.d" -> "LL.D.", the garbled "R.II.A." stays "R.II.A."). */
  function exhClusterForm(tok) {
    const letters = exhInitialLetters(tok);
    if (letters) return letters.split('').join('.') + '.';
    if (/^([A-Za-z]{1,2}\.)+[A-Za-z]{1,2}\.?$/.test(tok)) {
      const groups = tok.replace(/\.$/, '').split('.');
      const all = groups.join('');
      if (all.length >= 3 && groups.every((g) => g === g.toUpperCase() || g === g.toLowerCase())) return groups.map((g) => g.toUpperCase()).join('.') + '.';
    }
    return null;
  }
  /* Case one name word. isFirst is true only for the very first word of
     the whole name; inParen marks words inside a parenthetical group,
     whose descriptive openers ("called …", "after …") stay lowercase. */
  function exhCaseWord(tok, isFirst, inParen) {
    const bare = tok.toLowerCase().replace(/\.$/, '');
    if (/^[A-Za-z]+\.?$/.test(tok) && EXH_HONORIFICS[bare]) return EXH_HONORIFICS[bare];
    if (inParen && EXH_PAREN_SMALL.has(bare)) return bare;
    if (tok.includes('-')) {
      return tok.split('-').map((part, i) => (part ? exhCaseWord(part, isFirst && i === 0, inParen) : part)).join('-');
    }
    const lower = tok.toLowerCase();
    if (!isFirst && EXH_PARTICLES.has(lower)) return lower;
    const mc = tok.match(/^mc([a-z].*)$/i);
    if (mc) {
      if (/^Mc[A-Z]/.test(tok)) return tok; // already correctly cased
      return 'Mc' + mc[1].charAt(0).toUpperCase() + mc[1].slice(1).toLowerCase();
    }
    const apm = tok.match(/^([^'’]*)(['’])([\s\S]*)$/);
    if (apm && apm[1]) {
      const pre = apm[1];
      const rest = apm[3];
      const preLow = pre.toLowerCase();
      const preOut = preLow === 'd' || preLow === 'l' ? preLow : pre.charAt(0).toUpperCase() + pre.slice(1).toLowerCase();
      return preOut + apm[2] + (rest ? rest.charAt(0).toUpperCase() + rest.slice(1).toLowerCase() : '');
    }
    return tok.charAt(0).toUpperCase() + tok.slice(1).toLowerCase();
  }
  /* One comma-separated segment of a name. post segments (post-nominals,
     places — everything after the first comma) join runs of initials
     without spaces ("K. p" -> "K.P.", "U. S. A" -> "U.S.A."); in the
     name segment itself initials keep their spaced form ("J. C."). A
     cluster printed as one token ("R.A.") stays compact anywhere. */
  function exhNameSegment(seg, post, firstCap, inParen) {
    const units = seg.match(/\([^()]*\)|\S+/g) || [];
    const pieces = [];
    units.forEach((u, i) => {
      if (u.length > 1 && u.startsWith('(') && u.endsWith(')')) {
        pieces.push({ text: '(' + exhNameSegment(u.slice(1, -1), post, false, true) + ')', initial: false });
        return;
      }
      const bare = u.replace(/^["“”']+/, '');
      const form = /^[ye]$/i.test(u) ? null : exhClusterForm(bare); // a bare "y"/"e" is the Spanish/Portuguese conjunction, not an initial
      if (form) {
        pieces.push({ text: u.slice(0, u.length - bare.length) + form, initial: true });
        return;
      }
      pieces.push({ text: exhCaseWord(u, firstCap && i === 0, inParen), initial: false });
    });
    let out = '';
    pieces.forEach((p, i) => {
      if (i === 0) out = p.text;
      else if (post && p.initial && pieces[i - 1].initial) out += p.text;
      else out += ' ' + p.text;
    });
    return out;
  }
  function niceName(s) {
    if (s == null) return '';
    let str = String(s).trim().replace(/\s+/g, ' ');
    if (!str) return str;
    if (str.endsWith(',')) str = str.slice(0, -1).trim();
    if (!str) return str;
    const segs = [];
    let depth = 0;
    let cur = '';
    for (const ch of str) {
      if (ch === '(') depth++;
      else if (ch === ')') depth = Math.max(0, depth - 1);
      if (ch === ',' && depth === 0) { segs.push(cur); cur = ''; } else cur += ch;
    }
    segs.push(cur);
    return segs
      .map((seg, i) => exhNameSegment(seg.trim(), i > 0, i === 0, false))
      .filter((x) => x !== '')
      .join(', ');
  }
  /* Split a title token into leading punctuation, core and trailing
     punctuation, so the core can be cased on its own. */
  function exhPeel(tok) {
    const m = String(tok).match(/^([^A-Za-zÀ-ÖØ-öø-ÿ]*)([\s\S]*?)([^A-Za-zÀ-ÖØ-öø-ÿ]*)$/);
    return { lead: m[1], core: m[2], trail: m[3] };
  }
  /* A title is normalised only when its casing is shouting (>=70% of
     its letters uppercase), whispering (>=90% lowercase) or mangled —
     a word with a lowercase letter running into an uppercase one
     ("CiESAR"), or all-caps and all-lowercase words mixed in one title
     ("THE approaching STORM", "a mill in HOLLAND"). Mc/Mac tokens are
     not mangling. A clean mixed-case title is returned byte-identical. */
  function exhTitleNeedsFix(s) {
    const cased = [...String(s)].filter((c) => c.toLowerCase() !== c.toUpperCase());
    if (!cased.length) return false;
    const upper = cased.filter((c) => c === c.toUpperCase()).length;
    if (upper / cased.length >= 0.7) return true;
    if ((cased.length - upper) / cased.length >= 0.9) return true;
    let capsWords = 0;
    let words = 0;
    let hasLowerWord = false;
    for (const raw of String(s).split(/\s+/)) {
      const { core } = exhPeel(raw);
      if (!core) continue;
      if (/^ma?c[a-z]/i.test(core)) continue;
      if (/[a-zà-öø-ÿ][A-ZÀ-Ö]/.test(core)) return true;
      if (core.length < 2) continue;
      words++;
      if (/^[A-ZÀ-ÖØ-Þ]{2,}$/.test(core)) capsWords++;
      else if (/^[a-zà-öø-ÿ]{2,}$/.test(core)) hasLowerWord = true;
    }
    if (hasLowerWord && capsWords > 0) return true;
    /* A title whose words are half or more all-caps, with at least two
       of them, is shouting in its main words even when a clean
       parenthetical gloss ("L' AMOUR VAINQUEUR (Love Triumphant)")
       dilutes the letter count below the 70% line. */
    return capsWords >= 2 && capsWords * 2 >= words;
  }
  /* Title-case one word from the lowercased pass. origCore is the same
     word as printed, used only to protect roman numerals of length >=2
     that were printed in capitals ("VIII" stays "VIII"). */
  function exhTitleWord(core, origCore, first, afterTerm) {
    if (!core) return core;
    if (origCore && /^[IVXLCDM]{2,}$/.test(origCore)) return origCore;
    if (origCore) {
      const rm = origCore.match(/^([IVXLCDM]{2,})(st|nd|rd|th)$/i);
      if (rm && rm[1] === rm[1].toUpperCase()) return rm[1] + rm[2].toLowerCase(); // "XVth" stays "XVth"
    }
    if (core.includes('.') && exhClusterForm(core)) return exhClusterForm(core);
    if (core === 'i') return 'I';
    if (!first && !afterTerm && EXH_SMALL_WORDS.has(core)) return core;
    const pm = core.match(/^([dl])(['’])(.*)$/);
    if (pm) {
      const rest = pm[3] ? exhTitleWord(pm[3], null, true, true) : '';
      return (first ? pm[1].toUpperCase() : pm[1]) + pm[2] + rest;
    }
    const mc = core.match(/^mc([a-z].*)$/);
    if (mc) return 'Mc' + mc[1].charAt(0).toUpperCase() + mc[1].slice(1);
    if (core.includes('-')) {
      return core.split('-').map((part, j) => {
        if (!part) return part;
        if (j > 0 && !afterTerm && EXH_SMALL_WORDS.has(part)) return part;
        return exhTitleWord(part, null, first && j === 0, afterTerm);
      }).join('-');
    }
    return core.charAt(0).toUpperCase() + core.slice(1);
  }
  function niceTitle(s) {
    if (s == null) return '';
    const str = String(s).trim();
    if (!str || !exhTitleNeedsFix(str)) return String(s);
    const toks = str.toLowerCase().split(/\s+/);
    const origToks = str.split(/\s+/);
    const pieces = [];
    let seenCore = false;
    let pending = null; // a detached "d'"/"l'" token waiting for its word
    const flushPending = () => {
      if (pending) { pieces.push({ text: pending.lead + pending.ch + pending.apo, glue: true }); pending = null; }
    };
    toks.forEach((tok, i) => {
      const { lead, core, trail } = exhPeel(tok);
      if (!core) { flushPending(); pieces.push({ text: tok, glue: false }); return; }
      const first = !seenCore;
      seenCore = true;
      const prev = i > 0 ? toks[i - 1].replace(/[)\]}"”’»]+$/, '') : '';
      const afterTerm = /[.:!?]$/.test(prev);
      /* A word straight after an opening parenthesis starts a phrase of
         its own (usually the translated gloss), so small words there
         capitalise like a first word: "(The Break of Day)". */
      const wordFirst = first || lead.includes('(');
      if ((core === 'd' || core === 'l') && (trail === "'" || trail === '’')) {
        flushPending();
        pending = { ch: core, apo: trail, first: wordFirst, lead };
        pieces.push({ text: '', glue: false });
        return;
      }
      let useTrail = trail;
      if (useTrail.startsWith('.') && core.includes('.') && exhClusterForm(core)) useTrail = useTrail.slice(1);
      const origCore = exhPeel(origToks[i] || '').core;
      let word = exhTitleWord(core, origCore, pending ? pending.first : wordFirst, afterTerm);
      if (pending) {
        word = pending.lead + (pending.first ? pending.ch.toUpperCase() : pending.ch) + pending.apo + lead + word;
        pieces.push({ text: word + useTrail, glue: true });
        pending = null;
      } else {
        pieces.push({ text: lead + word + useTrail, glue: false });
      }
    });
    flushPending();
    let out = '';
    pieces.forEach((p, i) => { out += i === 0 || p.glue ? p.text : ' ' + p.text; });
    return out;
  }
  /* EXH-NICE:END */
  function exhNoteHtml(note) {
    if (!note) return '';
    const short = note.length > 160 ? note.slice(0, 160) + '…' : note;
    return `<div class="meta exh-note" title="${esc(note)}">${esc(short)}</div>`;
  }
  /* One works table for the Record of Exhibitions, global and local:
     Exhibition (global only) | No. | Artist | Title | Medium | Size |
     Lender. Artist names link to the Atlas name search, as on the Loan
     page. */
  function exhWorkRow(w, global) {
    return `<tr>
      ${global ? `<td><a href="#/exhibitions/${esc(w.exhibition)}">${esc(w.label)}</a></td>` : ''}
      <td class="salon-num">${esc(w.no)}</td>
      <td><a href="#/search?q=${enc(exhNamePart(w.artist))}">${esc(niceName(w.artist))}</a></td>
      <td>${esc(niceTitle(w.title || ''))}${exhNoteHtml(w.note)}</td>
      <td>${esc(w.medium || '')}</td>
      <td class="exh-size">${esc(w.size || '')}</td>
      <td>${esc(niceName(w.lender))}</td>
    </tr>`;
  }
  const EXH_TABLE_HEAD = (global) => `<thead><tr>${global ? '<th>Exhibition</th>' : ''}<th class="salon-num">No.</th><th>Artist</th><th>Title</th><th>Medium</th><th>Size</th><th>Lender</th></tr></thead>`;
  /* Group works by a name field (artist or lender). Grouping is
     case-insensitive — the catalogue's capitalisation varies from entry
     to entry for the same person — and the display name is the most
     frequent printed form. Genuinely different printed forms (initials
     vs a full name) still list separately. */
  function exhGroups(works, field, words) {
    const groups = new Map();
    for (const w of works) {
      const name = w[field];
      if (!name || !raWordsMatch(name, words)) continue;
      const key = raNorm(name);
      if (!groups.has(key)) groups.set(key, { key, forms: new Map(), works: [] });
      const g = groups.get(key);
      g.forms.set(name, (g.forms.get(name) || 0) + 1);
      g.works.push(w);
    }
    return [...groups.values()].map((g) => ({
      key: g.key,
      name: [...g.forms.entries()].sort((a, b) => b[1] - a[1])[0][0],
      works: g.works,
    })).sort((a, b) => a.name.localeCompare(b.name));
  }
  /* EXH-BROWSE-GROUP:BEGIN */
  /* Display-layer grouping for the Record of Exhibitions "Browse by
     artist" only. The records themselves stay exactly as printed; what
     changes is how the browse groups them. One artist could be split
     across several rows — and several letters — by OCR garbles, variant
     printed forms and appended section words. The grouping key below
     normalises those away deterministically: accents and case folded,
     post-nominal suffix segments dropped (R.A., E.A., Bakt., LL.A. and
     the like), catalogue section words dropped (Dessins, Études,
     Peintures), name abbreviations expanded (Chas. = Charles), and the
     known OCR confusion classes applied (6 for e, 0 for o, vv for w,
     final fl for ff, a skeleton that treats c/g/q/o, k/r, y/v and i/t
     as interchangeable, doubled letters collapsed, spaces ignored).
     Rows group ONLY where the normalised keys match exactly — there is
     no similarity scoring. Identity-bearing distinctions are never
     normalised away: "the Elder" / "the Younger" stay in the key, so
     the two Teniers never merge, and a bare "Carlos" never acquires
     the surname of "Schwabe, Carlos". The letter a group files under
     still comes from exhSurnameInitial applied to the group's display
     name — that rule is unchanged — except where the surname token
     itself is garbled, when its repaired form supplies the letter. */
  const EXH_SUFFIX_SEGMENTS = new Set(['ra', 'ara', 'rsa', 'rha', 'prha', 'arha', 'ea', 'ua', 'lla', 'lia', 'usa', 'bakt', 'bart', 'esq', 'mp', 'ri', 'ha', 'pa', 'ba', 'aha', 'ei', 'frs', 'awcs', 'na', 'ana']);
  const EXH_SECTION_WORDS = new Set(['dessins', 'etudes', 'peintures']);
  const EXH_NAME_ABBREV = { chas: 'charles', thos: 'thomas', wm: 'william', jno: 'john', geo: 'george' };
  const EXH_INITIAL_GARBLES = { it: 'h', rn: 'm' };
  const EXH_SURNAME_REPAIRS = { yelde: 'velde' };
  function exhFoldName(s) {
    return String(s || '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  }
  /* The name as comma-separated token segments (accents and case
     folded, punctuation split away), with post-nominal suffix segments
     and appended section words removed. Elder/Younger segments are
     protected: they distinguish two people, not a printing variant. */
  function exhBrowseSegments(artist) {
    const segs = exhFoldName(artist).split(',')
      .map((seg) => seg.split(/[^a-z0-9]+/).filter(Boolean))
      .filter((tokens) => tokens.length);
    while (segs.length > 1) {
      const last = segs[segs.length - 1];
      if (last.includes('elder') || last.includes('younger')) break;
      const isSuffix = EXH_SUFFIX_SEGMENTS.has(last.join('')) && (last.length === 1 || last.every((t) => t.length <= 3));
      if (!isSuffix) break;
      segs.pop();
    }
    if (segs.length) {
      const last = segs[segs.length - 1];
      while (last.length > 1 && EXH_SECTION_WORDS.has(last[last.length - 1])) last.pop();
    }
    return segs;
  }
  function exhKeyToken(tok) {
    let t = tok.replace(/6/g, 'e').replace(/0/g, 'o');
    if (EXH_NAME_ABBREV[t]) t = EXH_NAME_ABBREV[t];
    if (EXH_INITIAL_GARBLES[t]) t = EXH_INITIAL_GARBLES[t];
    if (t === 'tbe') t = 'the';
    t = t.replace(/vv/g, 'w');
    if (t.length >= 6 && t.startsWith('ay')) t = 'w' + t.slice(2); // "Ayilliam" for William
    if (/fl$/.test(t)) t = t.slice(0, -2) + 'ff'; // "Shurtlefl" for Shurtleff
    return t;
  }
  function exhSkeleton(str) {
    return str.replace(/[cgqo]/g, 'o').replace(/k/g, 'r').replace(/y/g, 'v').replace(/i/g, 't').replace(/(.)\1+/g, '$1');
  }
  /* The grouping key. Word tokens are skeletonised; single letters are
     kept literal — an initial is identity-bearing, so "Nicoll, J. C."
     and the garbled "Nicoll, J. G." stay apart — except a run of four
     or more single letters, which is a spaced-out word ("G e o r g e")
     and is skeletonised as one unit. Doubled letters collapse inside a
     word unit, and across a word/word boundary (a surname split in two
     by the OCR, "Far re r"), but never between an initial and the
     surname: "W. L. Lathrop" and "W. Lathrop" stay apart. */
  function exhBrowseKey(artist) {
    const tokens = exhBrowseSegments(artist).flat();
    const units = [];
    let run = [];
    const flushRun = () => {
      if (!run.length) return;
      if (run.length >= 4) units.push({ text: exhSkeleton(run.join('')), word: true });
      else for (const t of run) units.push({ text: t.replace(/6/g, 'e').replace(/0/g, 'o'), word: false });
      run = [];
    };
    for (const tok of tokens) {
      if (tok.length === 1) { run.push(tok); continue; }
      flushRun();
      units.push({ text: exhSkeleton(exhKeyToken(tok)), word: true });
    }
    flushRun();
    let key = '';
    let prevWord = false;
    for (const u of units) {
      if (key && u.word && prevWord && key.charAt(key.length - 1) === u.text.charAt(0)) {
        key += u.text.slice(1);
      } else {
        key += u.text;
      }
      prevWord = u.word;
    }
    return key;
  }
  /* The surname token of the cleaned name: the last word before the
     first comma for surname-first headings, otherwise the last word —
     with a split surname rejoined ("Go" + "yen") and garbled tokens
     repaired (digits, Yelde). Used for the group's letter (only where
     the printed surname is itself garbled) and for sorting. */
  function exhBrowseSurname(artist, repaired) {
    const segs = exhBrowseSegments(artist);
    if (!segs.length) return '';
    const honorifics = new Set(['sir', 'dame', 'lord', 'lady', 'rev', 'hon', 'fra', 'mons', 'monsieur', 'madame', 'mademoiselle', 'miss', 'mr', 'mrs', 'dr']);
    const first = segs[0].filter((t) => t.length >= 2 && !honorifics.has(t));
    let surname;
    if (String(artist).includes(',') && first.length) {
      surname = first[first.length - 1];
    } else {
      const all = segs.flat();
      surname = all[all.length - 1];
      const prev = all[all.length - 2];
      if (repaired && prev && prev.length === 2 && surname.length <= 3) surname = prev + surname;
    }
    if (repaired) {
      surname = surname.replace(/6/g, 'e').replace(/0/g, 'o').replace(/vv/g, 'w');
      if (EXH_SURNAME_REPAIRS[surname]) surname = EXH_SURNAME_REPAIRS[surname];
    }
    return surname;
  }
  /* The printed form a group is shown under: the printed name with any
     appended section word removed and stray trailing punctuation
     trimmed — nothing else about it is altered. */
  function exhBrowseDisplayForm(artist) {
    let s = String(artist || '').trim().replace(/\s+/g, ' ');
    const comma = s.lastIndexOf(',');
    const head = comma >= 0 ? s.slice(0, comma + 1) : '';
    const tail = comma >= 0 ? s.slice(comma + 1).trim() : s;
    const toks = tail.split(' ');
    while (toks.length > 1 && EXH_SECTION_WORDS.has(exhFoldName(toks[toks.length - 1]).replace(/[^a-z]/g, ''))) toks.pop();
    s = (head ? head + ' ' : '') + toks.join(' ');
    return s.replace(/[\s"“”']+$/, '').replace(/^[\s,]+/, '').replace(/[\s,]+$/, '').trim();
  }
  /* How garbled a printed form looks, for choosing which form a group
     is shown under: digits and stray symbols, the vv digraph, a q with
     no u after it, and the Ay- for W- garble. Clean forms beat garbled
     ones however often the garble was printed. */
  function exhGarbleScore(name) {
    let score = 0;
    for (const ch of String(name)) {
      if (/[0-9]/.test(ch)) score += 2;
      else if (!/[\p{L}\s,.'’()-]/u.test(ch)) score += 2;
    }
    for (const tok of exhFoldName(name).split(/[^a-z0-9]+/).filter(Boolean)) {
      if (tok.includes('vv')) score += 2;
      if (/q(?!u)/.test(tok)) score += 2;
      if (tok.length >= 6 && tok.startsWith('ay')) score += 2;
    }
    return score;
  }
  const EXH_BLANK_KEY = 'artist-not-given';
  /* Group one exhibition's works for the artist browse. Blank-artist
     entries form their own group so their works stay reachable. Each
     group carries its filing letter and a surname sort key. */
  function exhBrowseGroups(records) {
    const groups = new Map();
    for (const w of records) {
      const raw = (w.artist || '').trim();
      /* Mc/Mac surname prefixes are identity-bearing: "B. M. Guinness"
         and "B. McGuinness" skeletonise to the same key, but Guinness
         and McGuinness are different families, so a Mc/Mac surname
         never groups with the same surname shorn of its prefix. */
      const mcGuard = raw && /^(mc|mac)/.test(exhBrowseSurname(raw, false)) && exhBrowseSurname(raw, false).length >= 5;
      const key = raw ? exhBrowseKey(raw) + (mcGuard ? '|mc' : '') : EXH_BLANK_KEY;
      if (!groups.has(key)) groups.set(key, { key, blank: !raw, forms: new Map(), works: [] });
      const g = groups.get(key);
      if (raw) {
        const cand = exhBrowseDisplayForm(raw);
        g.forms.set(cand, (g.forms.get(cand) || 0) + 1);
      }
      g.works.push(w);
    }
    return [...groups.values()].map((g) => {
      if (g.blank) {
        return { key: g.key, blank: true, name: 'Artist not given in catalogue', works: g.works, letter: '#', sortKey: 'artistnotgiven' };
      }
      /* Display form: the cleanest printed form wins; among equally
         clean forms, the one whose name tokens are most usual across
         the group's forms (so a one-off garble of the surname loses
         to the spelling the catalogue used most), then the most
         frequent, then alphabetical. */
      const tokenFreq = new Map();
      for (const cand of g.forms.keys()) {
        for (const tok of new Set(exhBrowseSegments(cand).flat().map(exhKeyToken))) {
          tokenFreq.set(tok, (tokenFreq.get(tok) || 0) + 1);
        }
      }
      const centrality = (cand) => {
        const toks = exhBrowseSegments(cand).flat();
        if (!toks.length) return 0;
        return toks.reduce((n, tok) => n + (tokenFreq.get(exhKeyToken(tok)) || 0), 0) / toks.length;
      };
      const forms = [...g.forms.entries()]
        .sort((a, b) => exhGarbleScore(a[0]) - exhGarbleScore(b[0])
          || centrality(b[0]) - centrality(a[0])
          || b[1] - a[1]
          || a[0].localeCompare(b[0]));
      const name = forms[0][0];
      const surname = exhBrowseSurname(name, true);
      const rawSurname = exhBrowseSurname(name, false);
      let letter = exhSurnameInitial(name);
      if ((letter === '#' || surname !== rawSurname) && /^[a-z]/.test(surname)) {
        letter = surname.charAt(0).toUpperCase();
      }
      return { key: g.key, blank: false, name, works: g.works, letter, sortKey: exhSkeleton(surname) + '|' + g.key };
    });
  }
  /* EXH-BROWSE-GROUP:END */
  function renderExhSearch() {
    const el = $('#exh-search');
    if (!el) return;
    const s = exhSearchState;
    const total = exhIndex ? exhIndex.reduce((n, e) => n + e.works, 0).toLocaleString() : '466';
    el.innerHTML = `<div class="results-head"><div><h2>Search all recorded exhibitions</h2>
      <div class="meta">Every work in every catalogue recorded here at a keystroke: ${total} works. By artist — that artist’s record across all the exhibitions. By title — a work traced from catalogue to catalogue. By lender — everything a collector or institution lent, which is a provenance record in itself.</div></div></div>
      <div class="filters">
        <button class="chip ${s.mode === 'artist' ? 'active' : ''}" data-exh-mode="artist">By artist</button>
        <button class="chip ${s.mode === 'title' ? 'active' : ''}" data-exh-mode="title">By title</button>
        <button class="chip ${s.mode === 'lender' ? 'active' : ''}" data-exh-mode="lender">By lender</button>
      </div>
      <form id="exh-search-form" class="salon-search">
        <input id="exh-search-q" type="search" placeholder="${s.mode === 'artist' ? 'Artist’s name — e.g. Osborne, Lavery, Yeats' : s.mode === 'title' ? 'A title, or its distinctive words — e.g. fishmarket, octobre' : 'Lender’s name — e.g. Lane, McCulloch, National Gallery of Ireland'}" value="${esc(s.query)}" aria-label="Search all recorded exhibitions">
        <button class="btn" type="submit">Search</button>
      </form>
      <div class="meta" style="margin:6px 0 10px">${s.mode === 'title' ? 'Tip: one or two distinctive words beat a full exact title — titles were printed in full and the OCR garbles the odd word, so an exact phrase can miss a work that a single word finds.' : 'Capitalisation is ignored — the catalogue varies it from entry to entry for the same person, and those entries list together. Genuinely different printed forms of a name (initials vs a full name) still list separately.'}</div>
      <div id="exh-search-results"></div>`;
    el.querySelectorAll('[data-exh-mode]').forEach((b) => b.addEventListener('click', () => {
      exhSearchState.mode = b.dataset.exhMode;
      exhSearchState.result = null;
      exhSearchState.selected = null;
      exhSearchState.page = 1;
      renderExhSearch();
    }));
    $('#exh-search-form').addEventListener('submit', (e) => { e.preventDefault(); runExhSearch(); });
    renderExhSearchResults();
  }
  async function runExhSearch() {
    const input = $('#exh-search-q');
    const q = (input ? input.value : '').trim();
    exhSearchState.query = q;
    exhSearchState.selected = null;
    exhSearchState.page = 1;
    const wrap = $('#exh-search-results');
    if (!q) { exhSearchState.result = null; renderExhSearchResults(); return; }
    if (wrap) wrap.innerHTML = spinner(exhAllWorks ? 'Searching all recorded exhibitions…' : 'Searching all recorded exhibitions — the first search downloads the combined index; after that, searches are instant…');
    let works;
    try {
      works = await loadExhAll();
    } catch (e) {
      if (wrap) wrap.innerHTML = `<div class="notice error">The combined exhibitions index could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    const words = raNorm(q).split(' ').filter(Boolean);
    if (exhSearchState.mode === 'title') {
      exhSearchState.result = { type: 'title', rows: works.filter((w) => raWordsMatch(w.title, words)) };
    } else {
      const groups = exhGroups(works, exhSearchState.mode === 'artist' ? 'artist' : 'lender', words);
      exhSearchState.result = { type: exhSearchState.mode, groups };
      if (groups.length === 1) exhSearchState.selected = groups[0].key;
    }
    renderExhSearchResults();
  }
  function renderExhSearchResults() {
    const wrap = $('#exh-search-results');
    if (!wrap) return;
    const s = exhSearchState;
    const r = s.result;
    if (!r) { wrap.innerHTML = ''; return; }
    if (r.type === 'title') {
      const rows = r.rows;
      if (!rows.length) {
        wrap.innerHTML = `<div class="notice">No title in the recorded exhibitions matches “${esc(s.query)}” — try fewer or different distinctive words; the OCR garbles the odd word.</div>`;
        return;
      }
      const pages = Math.max(1, Math.ceil(rows.length / EXH_PAGE_SIZE));
      if (s.page > pages) s.page = pages;
      const start = (s.page - 1) * EXH_PAGE_SIZE;
      const pageRows = rows.slice(start, start + EXH_PAGE_SIZE);
      wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(rows.length, 'work')} in the recorded exhibitions match “${esc(s.query)}”${rows.length > 1000 ? ' — a lot; add another distinctive word to narrow it down' : ''}:</div>
        <div class="table-wrap"><table class="table salon-table">
        ${EXH_TABLE_HEAD(true)}
        <tbody>${pageRows.map((w) => exhWorkRow(w, true)).join('')}</tbody></table></div>
        <div class="pager">
          <button class="btn btn-sm" id="exh-s-prev" ${s.page <= 1 ? 'disabled' : ''}>← Previous</button>
          <span class="meta">Page ${s.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + EXH_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} works</span>
          <button class="btn btn-sm" id="exh-s-next" ${s.page >= pages ? 'disabled' : ''}>Next →</button>
        </div>`;
      const prev = $('#exh-s-prev');
      const next = $('#exh-s-next');
      if (prev) prev.addEventListener('click', () => { s.page--; renderExhSearchResults(); });
      if (next) next.addEventListener('click', () => { s.page++; renderExhSearchResults(); });
      return;
    }
    const groups = r.groups;
    const kind = r.type === 'artist' ? 'artist' : 'lender';
    if (!groups.length) {
      wrap.innerHTML = `<div class="notice">No ${kind} in the recorded exhibitions matches “${esc(s.query)}” — try the surname alone, or another spelling.</div>`;
      return;
    }
    const sel = groups.find((g) => g.key === s.selected);
    if (!sel) {
      wrap.innerHTML = `<div class="meta" style="margin-bottom:8px">${plural(groups.length, kind)} in the recorded exhibitions match “${esc(s.query)}”:</div>
      <div class="table-wrap"><table class="table salon-table"><thead><tr><th>${kind === 'artist' ? 'Artist' : 'Lender'}</th><th>Works</th><th>Exhibitions</th><th></th></tr></thead>
      <tbody>${groups.map((g) => `<tr><td>${esc(niceName(g.name))}</td><td>${g.works.length.toLocaleString()}</td><td>${esc([...new Set(g.works.map((w) => w.label))].join(', '))}</td><td><button class="btn btn-sm" data-exh-group="${esc(g.key)}">View works →</button></td></tr>`).join('')}</tbody></table></div>`;
      wrap.querySelectorAll('[data-exh-group]').forEach((b) => b.addEventListener('click', () => { exhSearchState.selected = b.dataset.exhGroup; renderExhSearchResults(); }));
      return;
    }
    const head = kind === 'artist'
      ? `<h2>${esc(niceName(sel.name))}</h2><div class="meta">${plural(sel.works.length, 'work')} in the recorded exhibitions · <a href="#/search?q=${enc(exhNamePart(sel.name))}">Atlas research report →</a></div>`
      : `<h2>${esc(niceName(sel.name))}</h2><div class="meta">${plural(sel.works.length, 'work')} lent to the recorded exhibitions · by ${plural(new Set(sel.works.map((w) => raNorm(w.artist))).size, 'artist')}</div>`;
    wrap.innerHTML = `${groups.length > 1 ? '<button class="btn btn-sm" id="exh-search-back" style="margin-bottom:10px">← All matching ' + (kind === 'artist' ? 'artists' : 'lenders') + '</button>' : ''}
      <div class="results-head"><div>${head}</div></div>
      <div class="table-wrap"><table class="table salon-table">
      ${EXH_TABLE_HEAD(true)}
      <tbody>${sel.works.map((w) => exhWorkRow(w, true)).join('')}</tbody></table></div>`;
    const back = $('#exh-search-back');
    if (back) back.addEventListener('click', () => { exhSearchState.selected = null; renderExhSearchResults(); });
  }
  function renderExhList(idx) {
    const el = $('#exh-list');
    if (!el) return;
    el.innerHTML = `<div class="results-head"><div><h2>Recorded exhibitions</h2>
      <div class="meta">${plural(idx.length, 'exhibition')} recorded so far — the collection grows catalogue by catalogue as scans surface.</div></div></div>
      ${idx.map((e) => `<div class="results-head"><div><h2 style="font-size:24px"><a href="#/exhibitions/${esc(e.id)}">${esc(e.title)}</a></h2>
      <div class="meta">${esc(e.subtitle)} · ${esc(e.venue)} · ${esc(e.dates)} · organised by ${esc(e.organiser)} · ${plural(e.works, 'work')} in ${e.sections.map((s) => `${esc(s.name)} ${s.works.toLocaleString()}`).join(' · ')}</div></div></div>`).join('')}`;
  }
  function exhFiltered() {
    const { records, section, query } = exhState;
    if (!records) return [];
    const q = query.trim().toLowerCase();
    return records.filter((w) => {
      if (section !== 'all' && w.section !== section) return false;
      if (!q) return true;
      return (w.artist || '').toLowerCase().includes(q) || (w.title || '').toLowerCase().includes(q) || (w.lender || '').toLowerCase().includes(q);
    });
  }
  function renderExhTable() {
    const wrap = $('#exh-table-wrap');
    if (!wrap || !exhState.records) return;
    const rows = exhFiltered();
    const pages = Math.max(1, Math.ceil(rows.length / EXH_PAGE_SIZE));
    if (exhState.page > pages) exhState.page = pages;
    const start = (exhState.page - 1) * EXH_PAGE_SIZE;
    const pageRows = rows.slice(start, start + EXH_PAGE_SIZE);
    if (!rows.length) {
      wrap.innerHTML = '<div class="notice">No works in this exhibition match — try another spelling, a different gallery, or clear the search box.</div>';
      return;
    }
    wrap.innerHTML = `<div class="table-wrap"><table class="table salon-table">
      ${EXH_TABLE_HEAD(false)}
      <tbody>${pageRows.map((w) => exhWorkRow(w, false)).join('')}</tbody></table></div>
      <div class="pager">
        <button class="btn btn-sm" id="exh-prev-page" ${exhState.page <= 1 ? 'disabled' : ''}>← Previous</button>
        <span class="meta">Page ${exhState.page} of ${pages.toLocaleString()} · showing ${(start + 1).toLocaleString()}–${Math.min(start + EXH_PAGE_SIZE, rows.length).toLocaleString()} of ${rows.length.toLocaleString()} work${rows.length === 1 ? '' : 's'}</span>
        <button class="btn btn-sm" id="exh-next-page" ${exhState.page >= pages ? 'disabled' : ''}>Next →</button>
      </div>`;
    const prev = $('#exh-prev-page');
    const next = $('#exh-next-page');
    if (prev) prev.addEventListener('click', () => { exhState.page--; renderExhTable(); });
    if (next) next.addEventListener('click', () => { exhState.page++; renderExhTable(); });
  }
  function renderExhMain() {
    const el = $('#exh-main');
    const { entry } = exhState;
    if (!el || !entry) return;
    const allLabel = entry.sections.length && /room/i.test(entry.sections[0].name) ? 'All rooms' : 'All galleries';
    const tabs = [{ id: 'all', label: allLabel, n: entry.works }, ...entry.sections.map((s) => ({ id: s.name, label: s.name, n: s.works }))];
    el.innerHTML = `<div class="filters">${tabs.map((t) => `<button class="chip ${exhState.section === t.id ? 'active' : ''}" data-exh-sec="${esc(t.id)}">${esc(t.label)} (${t.n.toLocaleString()})</button>`).join('')}</div>
      <div class="salon-search"><input id="exh-q" type="search" placeholder="Filter this exhibition by artist, title or lender…" value="${esc(exhState.query)}" aria-label="Filter works by artist, title or lender"></div>
      <div id="exh-table-wrap"></div>`;
    el.querySelectorAll('[data-exh-sec]').forEach((b) => b.addEventListener('click', () => {
      exhState.section = b.dataset.exhSec;
      exhState.page = 1;
      el.querySelectorAll('[data-exh-sec]').forEach((x) => x.classList.toggle('active', x === b));
      renderExhTable();
    }));
    const q = $('#exh-q');
    q.addEventListener('input', () => { exhState.query = q.value; exhState.page = 1; renderExhTable(); });
    renderExhTable();
  }
  function renderExhBrowse() {
    const el = $('#exh-browse');
    if (!el || !exhState.records) return;
    const records = exhState.records;
    /* Group first (display-layer normalisation), then file each group
       under its letter — a garbled variant no longer strands its works
       under the wrong letter or in "#". */
    const allGroups = exhBrowseGroups(records);
    const counts = new Map();
    for (const g of allGroups) {
      counts.set(g.letter, (counts.get(g.letter) || 0) + g.works.length);
    }
    const letters = [...counts.keys()].sort((a, b) => (a === '#' ? 1 : b === '#' ? -1 : a.localeCompare(b)));
    const chips = letters.map((L) =>
      `<button class="chip ${exhState.letter === L ? 'active' : ''}" data-exh-letter="${esc(L)}">${esc(L)} · ${counts.get(L).toLocaleString()}</button>`).join('');
    let body = '';
    if (exhState.letter) {
      const groups = allGroups.filter((g) => g.letter === exhState.letter)
        .sort((a, b) => a.sortKey.localeCompare(b.sortKey));
      const inLetter = groups.reduce((n, g) => n + g.works.length, 0);
      const sel = groups.find((g) => g.key === exhState.selected);
      if (sel) {
        body = `<button class="btn btn-sm" id="exh-browse-back" style="margin:12px 0 10px">← All artists under ${esc(exhState.letter)}</button>
          <div class="results-head"><div><h2>${esc(niceName(sel.name))}</h2>
          <div class="meta">${plural(sel.works.length, 'work')} in this exhibition${sel.blank ? '' : ` · <a href="#/search?q=${enc(exhNamePart(sel.name))}">Atlas research report →</a>`}</div></div></div>
          <div class="table-wrap"><table class="table salon-table">
          <thead><tr><th class="salon-num">No.</th><th>Title</th><th>Medium</th><th>Size</th><th>Lender</th><th>Gallery</th></tr></thead>
          <tbody>${sel.works.map((w) => `<tr>
            <td class="salon-num">${esc(w.no)}</td>
            <td>${esc(niceTitle(w.title || ''))}${exhNoteHtml(w.note)}</td>
            <td>${esc(w.medium || '')}</td>
            <td class="exh-size">${esc(w.size || '')}</td>
            <td>${esc(niceName(w.lender))}</td>
            <td>${esc(w.section || '')}</td>
          </tr>`).join('')}</tbody></table></div>`;
      } else {
        body = `<div class="results-head" style="margin-top:14px"><div><h2>Artists under ${esc(exhState.letter)}</h2>
          <div class="meta">${plural(groups.length, 'artist')} as the catalogue printed them · ${plural(inLetter, 'work')}</div></div></div>
          <div class="table-wrap"><table class="table salon-table"><thead><tr><th>Artist</th><th>Works</th><th></th></tr></thead>
          <tbody>${groups.map((g) => `<tr><td>${esc(niceName(g.name))}</td><td>${g.works.length.toLocaleString()}</td><td><button class="btn btn-sm" data-exh-artist="${esc(g.key)}">View works →</button></td></tr>`).join('')}</tbody></table></div>`;
      }
    }
    el.innerHTML = `<div class="results-head"><div><h2>Browse by artist</h2>
      <div class="meta">Pick a letter — the artists are filed under the initial of the surname as the catalogue printed it.</div></div></div>
      <div class="filters">${chips}</div>
      <div id="exh-letter">${body}</div>`;
    el.querySelectorAll('[data-exh-letter]').forEach((b) => b.addEventListener('click', () => {
      exhState.letter = exhState.letter === b.dataset.exhLetter ? null : b.dataset.exhLetter;
      exhState.selected = null;
      renderExhBrowse();
    }));
    el.querySelectorAll('[data-exh-artist]').forEach((b) => b.addEventListener('click', () => {
      exhState.selected = b.dataset.exhArtist;
      renderExhBrowse();
    }));
    const back = $('#exh-browse-back');
    if (back) back.addEventListener('click', () => { exhState.selected = null; renderExhBrowse(); });
  }
  async function viewExhibitions(p, path) {
    const seg = (path.split('/')[2] || '').trim();
    let idx;
    if (!seg) {
      app.innerHTML = `<h1 style="font-size:38px">Record of Exhibitions</h1>
        <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">A growing repository of original exhibition catalogues, digitised and parsed into searchable records — catalogue number, artist, title, medium, size and lender. These are the primary sources themselves, not a digest of them: what the catalogue printed is what is recorded here, uncertainties flagged and never smoothed over. Search across every exhibition recorded so far, or open one and browse it as its visitors did. Every artist name opens the Atlas name search, so an exhibitor leads straight to the full research report. Names and titles are shown in standard capitalisation for readability; the underlying records stand exactly as printed in each catalogue.</p>
        <div id="exh-search">${spinner('Loading the recorded exhibitions…')}</div>
        <div id="exh-list"></div>`;
      try {
        idx = await loadExhIndex();
      } catch (e) {
        $('#exh-search').innerHTML = `<div class="notice error">The recorded exhibitions could not be loaded: ${esc(e.message)}</div>`;
        return;
      }
      renderExhSearch();
      renderExhList(idx);
      return;
    }
    if (exhState.id !== seg) {
      exhState.id = seg;
      exhState.entry = null;
      exhState.records = null;
      exhState.section = 'all';
      exhState.query = '';
      exhState.page = 1;
      exhState.letter = null;
      exhState.selected = null;
    }
    app.innerHTML = `<div id="exh-head">${spinner('Loading the exhibition…')}</div>
      <div id="exh-main"></div>
      <div id="exh-browse"></div>
      <div id="exh-about"></div>`;
    try {
      idx = await loadExhIndex();
    } catch (e) {
      $('#exh-head').innerHTML = `<div class="notice error">The recorded exhibitions could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    const entry = idx.find((e) => e.id === seg);
    if (!entry) {
      $('#exh-head').innerHTML = `<div class="notice">No exhibition with the address “${esc(seg)}” has been recorded yet. See the <a href="#/exhibitions">Record of Exhibitions</a> for the catalogues that have.</div>`;
      return;
    }
    exhState.entry = entry;
    $('#exh-head').innerHTML = `<p class="meta" style="margin-bottom:6px"><a href="#/exhibitions">← Record of Exhibitions</a></p>
      <h1 style="font-size:38px">${esc(entry.title)}</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">${esc(entry.subtitle)} · ${esc(entry.venue)} · ${esc(entry.dates)} · organised by ${esc(entry.organiser)} · ${plural(entry.works, 'work')} in ${entry.sections.map((s) => `${esc(s.name)} ${s.works.toLocaleString()}`).join(' · ')}</p>`;
    $('#exh-about').innerHTML = `<div class="notice" style="margin-top:22px">About these records — the <i>${esc(entry.title)}</i> (${esc(entry.venue)}; ${esc(entry.dates)}; organised by ${esc(entry.organiser)}), parsed from the printed catalogue: ${esc(entry.source)}.${entry.notes ? ` ${esc(entry.notes)}` : ''} Names and titles are shown in standard capitalisation for readability; the underlying records stand exactly as printed in each catalogue.</div>`;
    try {
      exhState.records = await loadExhRecords(seg);
    } catch (e) {
      $('#exh-main').innerHTML = `<div class="notice error">This exhibition’s records could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderExhMain();
    renderExhBrowse();
  }

  /* ========================================================== report view */
  const SECTIONS = [
    ['synthesis', 'Research synthesis (AI)'],
    ['identity', 'Identity & names'],
    ['biography', 'Biography'],
    ['timeline', 'Timeline'],
    ['exhibitions', 'Exhibition record'],
    ['academic', 'Bibliography & scholarship'],
    ['critical', 'Critical analyses'],
    ['market', 'Auction & art sales'],
    ['collections', 'Works & collections'],
    ['catalogue', 'Catalogue raisonné'],
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

  /* ==================================================== art sales view */
  /* Historic record rows are compact arrays built by
     scripts/build-sales-data.py:
     [artist, artistDates, subject, lot, saleDate, saleYear, auctioneer,
      owner, buyer, pricePounds, priceShillings, pricePence,
      priceAsPrinted, currency, francAmount, page, note, flags]
     flags bit 1 = braced/shared price. currency "GBP" or "FRF". */
  const SALES_PAGE_SIZE = 50;
  let salesManifest = null;
  let salesConv = null;
  const salesData = new Map(); // source id -> records array
  let salesLoadPromise = null;
  const salesState = { equiv: 'off', query: '', source: 'all', page: 1, results: null, counts: null, today: null, gamePool: null, game: null, ended: false, score: { played: 0, correct: 0, streak: 0, best: 0 } };
  let salesPicDoc = null; // picture-matches.json — Confirmed sales↔pool-work links only

  async function loadSales() {
    if (!salesLoadPromise) {
      salesLoadPromise = (async () => {
        salesManifest = await salonFetchJSON('/data/sales/index.json');
        salesConv = await salonFetchJSON('/data/sales/conversions.json');
        await Promise.all(salesManifest.sources.map(async (s) => {
          const doc = await salonFetchJSON('/data/sales/' + s.file);
          salesData.set(s.id, doc.records);
        }));
        /* Picture matches are an enhancement, never a dependency: a
           missing file must not take the archive down with it. */
        try { salesPicDoc = await salonFetchJSON('/data/sales/picture-matches.json'); } catch (e) { salesPicDoc = null; }
        return salesManifest;
      })().catch((e) => { salesLoadPromise = null; throw e; });
    }
    return salesLoadPromise;
  }
  const salesSrcMeta = (id) => (salesManifest ? salesManifest.sources.find((s) => s.id === id) : null);
  function salesDec(w) {
    if (w[9] == null) return null;
    return w[9] + (w[10] || 0) / 20 + (w[11] || 0) / 240;
  }
  function fmtLSD(p, s, d) {
    let out = '£' + Number(p).toLocaleString('en-GB');
    if (s != null) out += ' ' + s + 's';
    if (d != null) out += ' ' + d + 'd';
    return out;
  }
  function salesPriceText(w) {
    if (w[13] === 'FRF') return (w[14] != null ? w[14].toLocaleString('en-GB') : '') + ' francs';
    if (w[9] == null) return 'No price printed';
    return fmtLSD(w[9], w[10], w[11]);
  }
  function round3sf(x) {
    if (!x || !isFinite(x)) return 0;
    const pow = Math.pow(10, Math.floor(Math.log10(x)) - 2);
    return Math.round(x / pow) * pow;
  }
  /* The equivalent for one historic sterling record under a mode
     ('prices' | 'earnings'); '' when it cannot be computed. */
  function salesEquivText(w, mode) {
    if (!mode || mode === 'off' || !salesConv) return '';
    if (w[13] !== 'GBP' || w[9] == null || w[5] == null) return '';
    const mult = (salesConv[mode] || {})[w[5]];
    if (!mult) return '';
    const val = round3sf(salesDec(w) * mult);
    return '≈ £' + val.toLocaleString('en-GB') + ' in ' + salesConv.baseYear + ' money (' + (mode === 'prices' ? 'by prices' : 'by earnings') + ')';
  }
  function salesPriceCell(w) {
    const eq = salesEquivText(w, salesState.equiv);
    let html = '<span class="sales-price">' + esc(salesPriceText(w)) + '</span>';
    if (w[17] & 1) html += ' <span class="badge variant" title="One printed price covers this lot and its braced companion — the price stands on both records">braced</span>';
    if (eq) html += '<div class="equiv">' + esc(eq) + '</div>';
    return html;
  }
  const SALES_NOTE_SHOW = /francs|brac|bought in|no price|dash|not put up|implausib|may fuse|garble|ocr/i;
  function salesNoteHtml(w) {
    const n = w[16] || '';
    if (!n || !SALES_NOTE_SHOW.test(n)) return '';
    const short = n.length > 160 ? n.slice(0, 160) + '…' : n;
    return '<div class="meta" title="' + esc(n) + '">' + esc(short) + '</div>';
  }
  const SALES_MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, sept: 9, oct: 10, nov: 11, dec: 12, january: 1, february: 2, march: 3, april: 4, june: 6, july: 7, august: 8, september: 9, october: 10, november: 11, december: 12 };
  const SALES_MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function parseSalesDate(sd) {
    const m = /^(\d{4}) ([A-Za-z]+)\.? (\d{1,2})$/.exec(String(sd || '').trim());
    if (!m) return null;
    const mo = SALES_MONTHS[m[2].toLowerCase()];
    return mo ? { y: +m[1], m: mo, d: +m[3] } : null;
  }
  function salesGravesRows() {
    const out = [];
    for (const id of ['graves-vol1', 'graves-vol2']) {
      const recs = salesData.get(id) || [];
      for (const w of recs) out.push({ id, w });
    }
    return out;
  }
  /* "Sold on this day": the highest-priced Graves sale whose full date
     matches today's month and day; if none matches, the nearest day
     that has one, labelled as such. Never invents a match. */
  function pickSalesToday(now) {
    const tm = now.getMonth() + 1;
    const td = now.getDate();
    const cum = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335];
    const doy = (m, d) => cum[m - 1] + d;
    const target = doy(tm, td);
    const byDay = new Map();
    for (const r of salesGravesRows()) {
      const p = parseSalesDate(r.w[4]);
      if (!p || r.w[9] == null) continue;
      const key = p.m + '-' + p.d;
      if (!byDay.has(key)) byDay.set(key, { m: p.m, d: p.d, rows: [] });
      byDay.get(key).rows.push(r);
    }
    const bestOf = (rows) => rows.reduce((a, b) => (salesDec(b.w) > salesDec(a.w) ? b : a));
    const exact = byDay.get(tm + '-' + td);
    if (exact) return { exact: true, m: tm, d: td, pick: bestOf(exact.rows), n: exact.rows.length };
    let best = null;
    for (const day of byDay.values()) {
      const dd = Math.abs(doy(day.m, day.d) - target);
      const dist = Math.min(dd, 366 - dd);
      const pick = bestOf(day.rows);
      if (!best || dist < best.dist || (dist === best.dist && salesDec(pick.w) > salesDec(best.pick.w))) {
        best = { exact: false, m: day.m, d: day.d, pick, n: day.rows.length, dist };
      }
    }
    return best;
  }
  function renderSalesToday() {
    const el = $('#sales-today');
    if (!el) return;
    const t = salesState.today;
    if (!t) { el.innerHTML = ''; return; }
    const w = t.pick.w;
    const meta = salesSrcMeta(t.pick.id);
    const when = t.exact
      ? 'Sold on this day — ' + t.d + ' ' + SALES_MONTH_NAMES[t.m - 1]
      : 'Sold on this day — no sale in Graves falls on ' + new Date().getDate() + ' ' + SALES_MONTH_NAMES[new Date().getMonth()] + '; the nearest recorded day is ' + t.d + ' ' + SALES_MONTH_NAMES[t.m - 1];
    el.innerHTML = '<div class="sales-feature"><div class="sales-feature-label">' + esc(when) + '</div>'
      + '<div class="sales-feature-main"><span class="sales-feature-artist">' + esc(w[0]) + '</span> '
      + '<span class="sales-feature-title">' + esc(w[2]) + '</span></div>'
      + '<div class="meta">' + esc(w[4]) + ' · ' + esc(w[6]) + (w[3] ? ' · lot ' + esc(w[3]) : '') + (w[7] ? ' · owner ' + esc(w[7]) : '') + (w[8] ? ' · buyer ' + esc(w[8]) : '') + '</div>'
      + '<div class="sales-feature-price">' + salesPriceCell(w) + '</div>'
      + '<div class="meta">As recorded by ' + esc(meta ? meta.label : t.pick.id) + ', p. ' + esc(w[15]) + (t.n > 1 ? ' · the highest-priced of ' + t.n + ' Graves sales on this date' : '') + '</div></div>';
  }
  /* -------------------------------------------------- guess the price */
  /* A picture for a sales record exists only where the cross-match
     (scripts/build-sales-picture-matches.py) confirmed the identity at
     the Atlas's Confirmed standard; the match carries the pool work's
     image and museum credit. Most records have none — period pictures
     are largely untraced — and the game says so rather than guessing. */
  function salesPicFor(id, w) {
    if (!salesPicDoc || !Array.isArray(salesPicDoc.matches)) return null;
    return salesPicDoc.matches.find((m) => m.source === id && m.artist === w[0] && m.subject === w[2]
      && m.saleDate === w[4] && String(m.lot) === String(w[3]) && m.page === w[15]) || null;
  }
  function salesGamePool() {
    if (salesState.gamePool) return salesState.gamePool;
    const pool = [];
    for (const r of salesGravesRows()) {
      const w = r.w;
      if (w[13] !== 'GBP' || w[9] == null || w[9] <= 0) continue;
      if (w[10] == null || w[11] == null) continue;         // complete £sd triple
      if (w[17] & 1) continue;                              // no braced/shared prices
      if (!w[8] || !w[8].trim()) continue;                  // named buyer preferred — required here
      if (!w[2] || w[2].trim().length < 6) continue;        // a real subject
      if (w[5] == null) continue;
      const pic = salesPicFor(r.id, w);
      if (pic) r.pic = pic;
      pool.push(r);
    }
    salesState.gamePool = pool;
    return pool;
  }
  function salesShuffle(a) {
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  /* Distractor prices are the true price respread at clear steps
     (×0.4, ×2.2, ×5), each rounded to a plausible £sd figure for its
     size — not other records' prices clustered around the truth — so
     the artist, date, size and owner on the card can genuinely
     discriminate between the four. */
  function salesPlausiblePrice(dec) {
    const step = dec < 20 ? 0.25 : dec < 100 ? 1 : dec < 500 ? 5 : dec < 2000 ? 10 : 50;
    const v = Math.max(step, Math.round(dec / step) * step);
    let p = Math.floor(v + 1e-9);
    let s = Math.round((v - p) * 20);
    if (s === 20) { p += 1; s = 0; }
    return { p, s, d: 0, dec: p + s / 20 };
  }
  function newSalesRound() {
    const pool = salesGamePool();
    if (!pool.length) return null;
    let pick = null;
    const picPool = pool.filter((r) => r.pic);
    if (picPool.length && Math.random() < 1 / 3) {
      /* Picture rounds are rare treasure: favour the picture deck
         regularly so they actually occur, without repeating the
         picture just shown. */
      let cands = picPool;
      if (salesState.game && salesState.game.pick) {
        const fresh = picPool.filter((r) => r !== salesState.game.pick);
        if (fresh.length) cands = fresh;
      }
      pick = cands[Math.floor(Math.random() * cands.length)];
    } else {
      pick = pool[Math.floor(Math.random() * pool.length)];
    }
    const trueDec = salesDec(pick.w);
    const seen = new Set([trueDec]);
    const options = [{ price: [pick.w[9], pick.w[10], pick.w[11]], isTrue: true }];
    for (const f of [0.4, 2.2, 5]) {
      let v = trueDec * f;
      let cand = salesPlausiblePrice(v);
      let guard = 0;
      while (seen.has(cand.dec) && guard++ < 60) { v *= f < 1 ? 0.87 : 1.15; cand = salesPlausiblePrice(v); }
      if (seen.has(cand.dec)) return null;
      seen.add(cand.dec);
      options.push({ price: [cand.p, cand.s, cand.d], isTrue: false });
    }
    return { pick, options: salesShuffle(options), answered: -1 };
  }
  /* Saleroom rank for a finished session, by accuracy and rounds. */
  function salesRank(played, correct) {
    if (!played) return 'Novice';
    const acc = correct / played;
    if (played >= 8 && acc >= 0.9) return 'Auctioneer';
    if (played >= 5 && acc >= 0.7) return 'Specialist';
    if (played >= 3 && acc >= 0.5) return 'Cataloguer';
    return 'Novice';
  }
  function renderSalesGame() {
    const el = $('#sales-game');
    if (!el) return;
    const g = salesState.game;
    const s = salesState.score;
    const scoreLine = '<div class="meta">Score this session: ' + s.correct + ' of ' + s.played + '</div>';
    if (salesState.ended) {
      const acc = s.played ? Math.round((s.correct / s.played) * 100) : 0;
      el.innerHTML = '<div class="sales-feature"><div class="sales-feature-label">Guess the price — session over</div>'
        + '<div class="sales-feature-main">You called <strong>' + s.correct + ' of ' + s.played + '</strong> prices right'
        + (s.played ? ' — <strong>' + acc + '%</strong> accuracy' : '')
        + ', with a best streak of <strong>' + s.best + '</strong>.</div>'
        + '<div class="sales-game-q">Saleroom rank: ' + esc(salesRank(s.played, s.correct)) + '</div>'
        + '<div class="pager"><button class="btn btn-primary" id="sales-game-again">Play again</button></div></div>';
      const again = $('#sales-game-again');
      if (again) again.addEventListener('click', () => {
        salesState.score = { played: 0, correct: 0, streak: 0, best: 0 };
        salesState.ended = false;
        salesState.game = newSalesRound();
        renderSalesGame();
      });
      return;
    }
    if (!g) {
      el.innerHTML = '<div class="sales-feature"><div class="sales-feature-label">Guess the price</div><div class="notice">The game could not be set up from the Graves records.</div></div>';
      return;
    }
    const w = g.pick.w;
    const meta = salesSrcMeta(g.pick.id);
    let html = '<div class="sales-feature"><div class="sales-feature-label">Guess the price</div>'
      + '<div class="sales-feature-main"><span class="sales-feature-artist">' + esc(w[0]) + '</span> '
      + '<span class="sales-feature-title">' + esc(w[2]) + '</span></div>'
      + '<div class="meta">' + esc(w[4]) + ' · ' + esc(w[6]) + (w[3] ? ' · lot ' + esc(w[3]) : '') + (w[7] ? ' · owner ' + esc(w[7]) : '') + '</div>';
    if (g.pick.pic) {
      html += '<figure class="sales-game-pic"><img src="' + esc(g.pick.pic.image) + '" alt="' + esc(g.pick.pic.poolTitle + ' by ' + g.pick.pic.poolArtist) + '" loading="lazy" onerror="this.closest(\'figure\').style.display=\'none\'">'
        + '<figcaption class="meta">The picture itself: ' + esc(g.pick.pic.poolTitle) + ' — now at the ' + esc(g.pick.pic.museum) + '. <a href="' + esc(g.pick.pic.objectUrl) + '" target="_blank" rel="noopener">The museum’s record</a></figcaption></figure>';
    }
    html += '<div class="sales-game-q">What did it make?</div><div class="sales-game-options">';
    g.options.forEach((o, i) => {
      let cls = 'sales-game-opt';
      let dis = '';
      if (g.answered >= 0) {
        dis = ' disabled';
        if (o.isTrue) cls += ' right';
        else if (i === g.answered) cls += ' wrong';
      }
      html += '<button class="' + cls + '" data-game-opt="' + i + '"' + dis + '>' + esc(fmtLSD(o.price[0], o.price[1], o.price[2])) + '</button>';
    });
    html += '</div>';
    if (g.answered >= 0) {
      const mode = salesState.equiv !== 'off' ? salesState.equiv : 'prices';
      const eq = salesEquivText(w, mode);
      html += '<div class="sales-game-reveal">' + (g.options[g.answered].isTrue ? '<strong>Right.</strong>' : '<strong>Not quite.</strong>')
        + ' It made <strong>' + esc(salesPriceText(w)) + '</strong> (as printed: ' + esc(w[12]) + ')'
        + (w[8] ? ', bought by ' + esc(w[8]) : '')
        + '.<br><span class="meta">As recorded by ' + esc(meta ? meta.label : g.pick.id) + ', p. ' + esc(w[15]) + '.'
        + (eq ? ' ' + esc(eq) + (salesState.equiv === 'off' ? ' (equivalents are off above — shown here as the payoff)' : '') + '.' : '')
        + '</span></div>'
        + '<div class="pager"><span class="sales-game-btns"><button class="btn btn-primary" id="sales-game-next">Next picture →</button><button class="btn" id="sales-game-end">End game</button></span>' + scoreLine + '</div>';
    } else if (s.played > 0) {
      html += '<div class="pager"><button class="btn" id="sales-game-end">End game</button>' + scoreLine + '</div>';
    } else {
      html += scoreLine;
    }
    html += '</div>';
    el.innerHTML = html;
    el.querySelectorAll('[data-game-opt]').forEach((b) => b.addEventListener('click', () => {
      const i = +b.dataset.gameOpt;
      if (salesState.game.answered >= 0) return;
      salesState.game.answered = i;
      salesState.score.played++;
      if (salesState.game.options[i].isTrue) {
        salesState.score.correct++;
        salesState.score.streak++;
        if (salesState.score.streak > salesState.score.best) salesState.score.best = salesState.score.streak;
      } else {
        salesState.score.streak = 0;
      }
      renderSalesGame();
    }));
    const next = $('#sales-game-next');
    if (next) next.addEventListener('click', () => { salesState.game = newSalesRound(); renderSalesGame(); });
    const end = $('#sales-game-end');
    if (end) end.addEventListener('click', () => { salesState.ended = true; renderSalesGame(); });
  }
  /* --------------------------------------------------------- searching */
  function salesWords(q) {
    return q.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
  }
  function salesMatchHistoric(w, words) {
    const hay = (w[0] + ' ' + w[2] + ' ' + w[6] + ' ' + w[7] + ' ' + w[8]).toLowerCase();
    return words.every((word) => hay.includes(word) || word === String(w[5]));
  }
  function salesMatchModern(r, words) {
    const hay = (r.artist + ' ' + r.work_title + ' ' + r.house + ' ' + (r.city || '') + ' ' + r.sale_date).toLowerCase();
    return words.every((word) => hay.includes(word));
  }
  function runSalesSearch() {
    const words = salesWords(salesState.query);
    const counts = {};
    let results = [];
    for (const meta of salesManifest.sources) {
      const recs = salesData.get(meta.id) || [];
      let matched = [];
      if (meta.kind === 'modern') {
        matched = recs.filter((r) => salesMatchModern(r, words)).map((r) => ({ kind: 'm', id: meta.id, r }));
        matched.sort((a, b) => a.r.sale_date.localeCompare(b.r.sale_date));
      } else {
        matched = recs.filter((w) => salesMatchHistoric(w, words)).map((w) => ({ kind: 'h', id: meta.id, w }));
        matched.sort((a, b) => ((a.w[5] ?? 9999) - (b.w[5] ?? 9999)) || a.w[0].localeCompare(b.w[0]));
      }
      counts[meta.id] = matched.length;
      if (salesState.source === 'all' || salesState.source === meta.id) results = results.concat(matched);
    }
    if (salesState.source === 'all') {
      const yr = (x) => (x.kind === 'm' ? +x.r.sale_date.slice(0, 4) : (x.w[5] ?? 9999));
      results.sort((a, b) => (yr(a) - yr(b)) || (a.kind === 'm' ? a.r.artist : a.w[0]).localeCompare(b.kind === 'm' ? b.r.artist : b.w[0]));
    }
    salesState.counts = counts;
    salesState.results = results;
    salesState.page = 1;
    renderSalesResults();
    renderSalesChips();
    renderSalesModern();
  }
  function salesMoney(v, cur) {
    if (v == null) return '';
    const sym = cur === 'USD' ? '$' : cur === 'EUR' ? '€' : '£';
    return sym + Number(v).toLocaleString('en-GB');
  }
  function renderSalesResults() {
    const wrap = $('#sales-results');
    if (!wrap) return;
    const rows = salesState.results;
    if (!rows) { wrap.innerHTML = ''; return; }
    if (!rows.length) {
      wrap.innerHTML = '<div class="notice">No sales match “' + esc(salesState.query) + '” in the selected source — try the surname alone, a distinctive word from the title, the auction house, or a year.</div>';
      return;
    }
    const pages = Math.max(1, Math.ceil(rows.length / SALES_PAGE_SIZE));
    if (salesState.page > pages) salesState.page = pages;
    const start = (salesState.page - 1) * SALES_PAGE_SIZE;
    const pageRows = rows.slice(start, start + SALES_PAGE_SIZE);
    const hRow = (x) => {
      const w = x.w;
      const meta = salesSrcMeta(x.id);
      return '<tr><td><a href="#/search?q=' + enc(w[0]) + '">' + esc(w[0]) + '</a>' + (w[1] ? '<div class="meta">' + esc(w[1]) + '</div>' : '') + '</td>'
        + '<td>' + esc(w[2]) + salesNoteHtml(w) + '</td>'
        + '<td>' + esc(w[4]) + '<div class="meta">' + esc(w[6]) + '</div></td>'
        + '<td class="salon-num">' + esc(w[3] || '—') + '</td>'
        + '<td>' + (w[7] ? esc(w[7]) : '<span class="muted">—</span>') + (w[8] ? ' → ' + esc(w[8]) : '') + '</td>'
        + '<td>' + salesPriceCell(w) + '</td>'
        + '<td class="meta">' + esc(meta ? meta.short : x.id) + (w[15] != null ? ', p. ' + esc(w[15]) : '') + '</td></tr>';
    };
    const mRow = (x) => {
      const r = x.r;
      const priceBits = [];
      if (r.hammer != null) priceBits.push('Hammer ' + salesMoney(r.hammer, r.currency));
      if (r.price_with_premium != null) priceBits.push('With premium ' + salesMoney(r.price_with_premium, r.currency));
      if (!priceBits.length && r.price_as_reported) priceBits.push('As reported: ' + esc(r.price_as_reported));
      else if (r.price_as_reported) priceBits.push('<span class="meta">As reported: ' + esc(r.price_as_reported) + '</span>');
      return '<tr><td>' + esc(r.artist) + '</td>'
        + '<td>' + esc(r.work_title) + (r.work_year ? ' (' + esc(r.work_year) + ')' : '') + (r.note ? '<div class="meta">' + esc(r.note) + '</div>' : '') + '</td>'
        + '<td>' + esc(r.sale_date) + '<div class="meta">' + esc(r.house) + (r.city ? ', ' + esc(r.city) : '') + ' · ' + esc(r.sale_type) + '</div></td>'
        + '<td class="salon-num">' + (r.lot != null ? esc(r.lot) : '—') + '</td>'
        + '<td class="meta">' + (r.estimate ? 'Estimate ' + esc(r.estimate) : '—') + '</td>'
        + '<td>' + priceBits.join('<br>') + '</td>'
        + '<td class="meta">Modern · <a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">' + esc(r.source_name) + '</a></td></tr>';
    };
    wrap.innerHTML = '<div class="meta" style="margin-bottom:8px">' + plural(rows.length, 'sale') + ' match “' + esc(salesState.query) + '”'
      + (salesState.counts ? ' — ' + salesManifest.sources.map((s) => esc(s.short) + ' ' + (salesState.counts[s.id] || 0).toLocaleString()).join(' · ') : '')
      + (rows.length > 5000 ? ' — a lot; add a year or the auction house to narrow it down' : '') + '</div>'
      + '<div class="table-wrap"><table class="table salon-table"><thead><tr><th>Artist</th><th>Work</th><th>Sale</th><th>Lot</th><th>Owner → Buyer / Estimate</th><th>Price</th><th>Source</th></tr></thead>'
      + '<tbody>' + pageRows.map((x) => (x.kind === 'm' ? mRow(x) : hRow(x))).join('') + '</tbody></table></div>'
      + '<div class="pager"><button class="btn btn-sm" id="sales-prev-page" ' + (salesState.page <= 1 ? 'disabled' : '') + '>← Previous</button>'
      + '<span class="meta">Page ' + salesState.page + ' of ' + pages.toLocaleString() + ' · showing ' + (start + 1).toLocaleString() + '–' + Math.min(start + SALES_PAGE_SIZE, rows.length).toLocaleString() + ' of ' + rows.length.toLocaleString() + ' sales</span>'
      + '<button class="btn btn-sm" id="sales-next-page" ' + (salesState.page >= pages ? 'disabled' : '') + '>Next →</button></div>';
    const prev = $('#sales-prev-page');
    const next = $('#sales-next-page');
    if (prev) prev.addEventListener('click', () => { salesState.page--; renderSalesResults(); });
    if (next) next.addEventListener('click', () => { salesState.page++; renderSalesResults(); });
  }
  function renderSalesChips() {
    const el = $('#sales-chips');
    if (!el || !salesManifest) return;
    const chip = (id, label, n) => '<button class="chip ' + (salesState.source === id ? 'active' : '') + '" data-sales-src="' + esc(id) + '">' + esc(label) + (n != null ? ' (' + n.toLocaleString() + ')' : '') + '</button>';
    let html = chip('all', 'All sources', salesState.counts ? Object.values(salesState.counts).reduce((a, b) => a + b, 0) : salesManifest.totalRecords);
    for (const s of salesManifest.sources) html += chip(s.id, s.short, salesState.counts ? (salesState.counts[s.id] || 0) : s.count);
    el.innerHTML = html;
    el.querySelectorAll('[data-sales-src]').forEach((b) => b.addEventListener('click', () => {
      salesState.source = b.dataset.salesSrc;
      if (salesState.results) runSalesSearch();
      else renderSalesChips();
    }));
  }
  function renderSalesModern() {
    const el = $('#sales-modern');
    if (!el) return;
    if (salesState.results) { el.innerHTML = ''; return; }
    const recs = [...(salesData.get('modern') || [])].sort((a, b) => (b.price_with_premium || 0) - (a.price_with_premium || 0));
    el.innerHTML = '<div class="results-head"><div><h2 style="font-size:26px">Modern landmark sales</h2><div class="meta">Ten landmark sales, each verified against public sources and cited on its record. Hammer and price-with-premium are always separate figures.</div></div></div>'
      + '<div class="table-wrap"><table class="table salon-table"><thead><tr><th>Artist</th><th>Work</th><th>Sale</th><th>Lot</th><th>Estimate</th><th>Price</th><th>Citation</th></tr></thead><tbody>'
      + recs.map((r) => {
        const priceBits = [];
        if (r.hammer != null) priceBits.push('Hammer ' + salesMoney(r.hammer, r.currency));
        if (r.price_with_premium != null) priceBits.push('With premium ' + salesMoney(r.price_with_premium, r.currency));
        if (!priceBits.length && r.price_as_reported) priceBits.push('As reported: ' + esc(r.price_as_reported));
        else if (r.price_as_reported) priceBits.push('<span class="meta">As reported: ' + esc(r.price_as_reported) + '</span>');
        return '<tr><td>' + esc(r.artist) + '</td><td>' + esc(r.work_title) + (r.work_year ? ' (' + esc(r.work_year) + ')' : '') + (r.note ? '<div class="meta">' + esc(r.note) + '</div>' : '') + '</td>'
          + '<td>' + esc(r.sale_date) + '<div class="meta">' + esc(r.house) + (r.city ? ', ' + esc(r.city) : '') + '</div></td>'
          + '<td class="salon-num">' + (r.lot != null ? esc(r.lot) : '—') + '</td><td class="meta">' + esc(r.estimate || '—') + '</td>'
          + '<td>' + priceBits.join('<br>') + '</td>'
          + '<td class="meta"><a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">' + esc(r.source_name) + '</a></td></tr>';
      }).join('') + '</tbody></table></div>';
  }
  async function viewSales(p) {
    salesState.query = (p.q || '').trim();
    salesState.results = null;
    salesState.counts = null;
    salesState.page = 1;
    app.innerHTML = '<h1 style="font-size:38px">Historic Art Sales</h1>'
      + '<p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">What pictures actually made, sale by sale, as the great sale historians printed it — Redford’s “Art Sales” (1888) and Graves’s “Art Sales” (1918–1921), every Graves record checked against the page — together with a small strand of modern landmark sales, each verified and cited. Hammer and price-with-premium are kept separate throughout, and no figure here comes from a paywalled price database.</p>'
      + '<div id="sales-today">' + spinner('Loading the sales archive…') + '</div>'
      + '<div id="sales-game"></div>'
      + '<div class="sales-switch"><span class="meta" style="font-weight:600">Today’s-money equivalents:</span>'
      + '<div class="filters">'
      + '<button class="chip" data-equiv="off">Off</button>'
      + '<button class="chip" data-equiv="prices">By prices</button>'
      + '<button class="chip" data-equiv="earnings">By earnings</button>'
      + '</div></div>'
      + '<form id="sales-form" class="salon-search" style="max-width:640px;display:flex;gap:8px"><input id="sales-q" type="search" placeholder="Artist, title, auction house or year — e.g. Hobbema, Raeburn, Christie’s, 1911" value="' + esc(salesState.query) + '" aria-label="Search historic art sales"><button class="btn btn-primary" type="submit">Search sales</button></form>'
      + '<div class="filters" id="sales-chips" style="margin-bottom:12px"></div>'
      + '<div id="sales-results"></div>'
      + '<div id="sales-modern"></div>'
      + '<div id="sales-about"></div>';
    const syncSwitch = () => app.querySelectorAll('[data-equiv]').forEach((b) => b.classList.toggle('active', b.dataset.equiv === salesState.equiv));
    syncSwitch();
    app.querySelectorAll('[data-equiv]').forEach((b) => b.addEventListener('click', () => {
      salesState.equiv = b.dataset.equiv;
      syncSwitch();
      renderSalesToday();
      if (salesState.results) renderSalesResults();
      if (salesState.game && salesState.game.answered >= 0) renderSalesGame();
    }));
    $('#sales-form').addEventListener('submit', (e) => {
      e.preventDefault();
      salesState.query = $('#sales-q').value.trim();
      if (!salesManifest) return;
      if (salesState.query) runSalesSearch();
      else { salesState.results = null; salesState.counts = null; renderSalesResults(); renderSalesChips(); renderSalesModern(); }
    });
    try {
      await loadSales();
    } catch (e) {
      $('#sales-today').innerHTML = '<div class="notice error">The sales archive could not be loaded: ' + esc(e.message) + '</div>';
      return;
    }
    salesState.today = pickSalesToday(new Date());
    renderSalesToday();
    salesState.game = newSalesRound();
    renderSalesGame();
    renderSalesChips();
    renderSalesModern();
    const countsLine = salesManifest.sources.map((s) => esc(s.short) + ' ' + s.count.toLocaleString()).join(' · ');
    $('#sales-about').innerHTML = '<div class="notice">About these records — ' + countsLine + ' · ' + salesManifest.totalRecords.toLocaleString() + ' sales in all. The historic records stand exactly as Redford and Graves printed them, including their spelling and their errors; Graves set out to correct Redford, and where Redford gives only the year, Graves usually gives the full date and lot number. One caveat travels with the Graves set: for some early sales whose catalogues printed no prices, Graves supplied the figures “to the best of my ability”, unmarked — those figures are his estimates, not catalogue records. Prices are in pounds, shillings and pence as printed; the small number of franc-priced Paris sales stand in francs. A “braced” price is one printed figure covering two lots together, and it stands on both records.</div>'
      + '<details class="more"><summary>About the today’s-money conversions</summary><div class="notice">Equivalents are expressed in ' + salesConv.baseYear + ' pounds, and are built from two published sources. The Bank of England’s “A millennium of macroeconomic data for the UK” (version 3.1, Thomas &amp; Dimsdale), sheet A1. Headline series, runs to 2016: its consumer price index (2015 = 100) is used for “By prices” and its average weekly earnings for “By earnings”. From 2017 to ' + salesConv.baseYear + ' both series are extended with Office for National Statistics figures compounded onto the 2016 values — the CPI annual rate (series D7G7) for “By prices” and Average Weekly Earnings growth (series KAB9, whole economy total pay) for “By earnings”. Sources accessed November 2026. The multiplier for a sale year is the ' + salesConv.baseYear + ' index value divided by that year’s. Results are rounded to three significant figures and marked “≈”; the printed historic figure is always the primary number. Sterling records only: franc-priced sales show no equivalent, and the modern landmark sales are given as reported.</div></details>';
    if (salesState.query) runSalesSearch();
  }

  /* ================================================ who painted it? */
  /* The pool (public/data/game/pool.json, built by
     scripts/build-game-pool.py) holds open-access museum records only:
     every work is a museum's own record for that object, and the artist
     is the artist that record names. Levels are curatorial — canonical
     works pinned low, the rest banded by the artist's fame; distractor
     closeness is ruled by level from per-artist metadata (century,
     movement, nationality, circle). See public/data/game/POOL.md. */
  let gamePool = null;
  let gameLoadPromise = null;
  const gameState = { level: 1, phase: null, set: null, score: 0, streak: 0, best: 0, played: 0, correct: 0, round: null, bad: new Set(), bags: {}, lastByLevel: {}, recentDistractors: [], setServed: new Set(), setDone: false };
  const GAME_RANKS = [[5800, 'Chief Curator'], [4600, 'Curator'], [3400, 'Connoisseur'], [2200, 'Docent'], [1000, 'Art Lover'], [0, 'Gallery Visitor']];
  const gameRank = (score) => GAME_RANKS.find(([min]) => score >= min)[1];
  /* The question follows the work's own kind (pool.json, derived from
     the holding museum's classification of that exact object): a
     drawing was not painted, and a print was made, not painted. Any
     other or unknown kind falls back to the neutral wording. */
  const GAME_QUESTIONS = { painting: 'Who painted this?', drawing: 'Who drew this?', print: 'Who made this print?', sculpture: 'Who sculpted this?', photograph: 'Who took this photograph?' };
  const gameQuestion = (work) => GAME_QUESTIONS[work && work.kind] || 'Who created this?';
  const gameNormName = (s) => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

  async function loadGamePool() {
    if (!gameLoadPromise) {
      gameLoadPromise = salonFetchJSON('/data/game/pool.json').then((d) => { gamePool = d; return d; })
        .catch((e) => { gameLoadPromise = null; throw e; });
    }
    return gameLoadPromise;
  }

  /* Distractor rule by level: 1–2 far eras; 3–4 same broad period,
     different movement; 5–6 same movement, or same nationality nearby;
     7–8 same movement; 9–10 the artist's own circle. Each rule falls
     back through looser ones until three names are found. */
  function gameDistractors(work, level) {
    const meta = gamePool.artists[work.artist];
    if (!meta) return [];
    const names = Object.keys(gamePool.artists).filter((n) => n !== work.artist);
    const M = (n) => gamePool.artists[n];
    const cdiff = (n) => Math.abs(M(n).century - meta.century);
    let rule;
    if (level <= 2) rule = (n) => cdiff(n) >= 2;
    else if (level <= 4) rule = (n) => cdiff(n) <= 1 && M(n).movement !== meta.movement;
    else if (level <= 6) rule = (n) => M(n).movement === meta.movement || (M(n).nationality === meta.nationality && cdiff(n) <= 1);
    else if (level <= 8) rule = (n) => M(n).movement === meta.movement;
    else rule = (n) => M(n).circle === meta.circle;
    const chain = [rule,
      (n) => M(n).movement === meta.movement,
      (n) => M(n).circle === meta.circle,
      (n) => M(n).nationality === meta.nationality && cdiff(n) <= 1,
      (n) => cdiff(n) <= 1,
      () => true];
    const picked = [];
    const seen = new Set([gameNormName(work.artist)]);
    for (const f of chain) {
      if (picked.length >= 3) break;
      /* Within a rule's candidates, names not used as distractors in
         the last few rounds come first — variety across a session,
         without ever loosening the level's closeness rule itself. */
      const cand = names.filter((n) => f(n) && !seen.has(gameNormName(n)));
      const fresh = cand.filter((n) => !gameState.recentDistractors.includes(n));
      const stale = cand.filter((n) => gameState.recentDistractors.includes(n));
      for (const c of [...salesShuffle(fresh), ...salesShuffle(stale)]) {
        if (picked.length >= 3) break;
        seen.add(gameNormName(c));
        picked.push(c);
      }
    }
    return picked;
  }

  /* Shuffle-bag serving, per level, for the whole session: a work is
     not served again at a level until every work in that level's pool
     has been served once, then the bag refills — shuffled so the work
     served last does not come straight back when the pool allows a
     different one. Within the bag, the same correct artist is not
     served twice in a row while the bag still holds another artist.
     (Level 1's pool is nine works, so a long sitting used to re-serve
     the same pictures; the bag is what stops that.) A refill also
     holds out the works already served in the current set, so a set
     never repeats a work even when it straddles a refill. */
  function gameServe(level) {
    for (let attempt = 0; attempt < 2; attempt++) {
      let bag = gameState.bags[level];
      if (!bag || !bag.length) {
        const pool = gamePool.works.filter((w) => w.level === level && !gameState.bad.has(w.image) && !gameState.setServed.has(w.image));
        if (!pool.length) return null;
        bag = salesShuffle(pool.slice());
        const last = gameState.lastByLevel[level];
        if (pool.length > 1 && last && bag[bag.length - 1].image === last.image) {
          [bag[0], bag[bag.length - 1]] = [bag[bag.length - 1], bag[0]];
        }
        gameState.bags[level] = bag;
      }
      while (bag.length) {
        let idx = bag.length - 1;
        const last = gameState.lastByLevel[level];
        if (last && bag[idx].artist === last.artist) {
          for (let i = bag.length - 2; i >= 0; i--) {
            if (bag[i].artist !== last.artist) { idx = i; break; }
          }
        }
        const work = bag.splice(idx, 1)[0];
        if (gameState.bad.has(work.image)) continue;
        gameState.lastByLevel[level] = { image: work.image, artist: work.artist };
        gameState.setServed.add(work.image);
        return work;
      }
    }
    return null;
  }

  function newGameRound(level) {
    const work = gameServe(level);
    if (!work) return null;
    const distract = gameDistractors(work, level);
    if (distract.length < 3) return null;
    gameState.recentDistractors = [...gameState.recentDistractors, ...distract].slice(-12);
    return { work, options: salesShuffle([work.artist, ...distract]), answered: -1, level, gained: 0, bonus: 0 };
  }

  /* A level is played as a set: GAME_SET_ROUNDS rounds, or the
     level's whole pool when that is smaller (level 1's pool is nine
     works, so its set is nine rounds). Starting a level — by the
     ladder button, a level chip, "Next level" or "Replay" — always
     begins a fresh set; the session score runs on across sets and
     levels until the player finishes or starts a new session.
     Finishing a set earns the move-on invitation whatever the score:
     there is no pass mark. */
  const GAME_SET_ROUNDS = 10;
  function gameLevelSize(level) {
    return gamePool.works.filter((w) => w.level === level && !gameState.bad.has(w.image)).length;
  }

  function startSet(level) {
    gameState.level = level;
    gameState.setServed = new Set();
    gameState.setDone = false;
    gameState.set = { level, size: Math.min(GAME_SET_ROUNDS, gameLevelSize(level)), played: 0, correct: 0, points: 0 };
    gameState.phase = 'playing';
    gameState.round = gameState.set.size ? newGameRound(level) : null;
    renderGame();
  }

  function startGame(level, fresh) {
    if (fresh) {
      gameState.score = 0; gameState.streak = 0; gameState.best = 0;
      gameState.played = 0; gameState.correct = 0;
    }
    startSet(level);
  }

  function completeSet() {
    gameState.round = null;
    gameState.setDone = true;
    /* Level 10 has no next level: its completion is the final
       summary. Lower levels pause on the invitation screen. */
    gameState.phase = gameState.set && gameState.set.level >= 10 ? 'finished' : 'complete';
    renderGame();
  }

  function finishSession() {
    gameState.round = null;
    gameState.phase = 'finished';
    renderGame();
  }

  function gameAnswer(i) {
    const g = gameState.round;
    if (!g || g.answered >= 0 || gameState.phase !== 'playing') return;
    g.answered = i;
    gameState.played++;
    if (gameState.set) gameState.set.played++;
    if (g.options[i] === g.work.artist) {
      gameState.correct++;
      gameState.streak++;
      gameState.best = Math.max(gameState.best, gameState.streak);
      g.bonus = gameState.streak >= 2 ? Math.min(250, 50 * (gameState.streak - 1)) : 0;
      g.gained = g.level * 100 + g.bonus;
      gameState.score += g.gained;
      if (gameState.set) { gameState.set.correct++; gameState.set.points += g.gained; }
    } else {
      gameState.streak = 0;
    }
    renderGameStage();
  }

  function gameNext() {
    if (gameState.phase !== 'playing' || !gameState.set) return;
    if (gameState.set.played >= gameState.set.size) { completeSet(); return; }
    gameState.round = newGameRound(gameState.set.level);
    if (!gameState.round) { completeSet(); return; }
    renderGameStage();
    renderGameControls();
  }

  async function viewGame() {
    app.innerHTML = '<h1 style="font-size:38px">Who Painted It?</h1>'
      + '<p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">One painting, four names. The works are all open-access museum pictures, and the higher the level, the closer the wrong answers crowd in — by level 10 the alternatives are the artist’s own circle. A correct answer scores the level × 100, and a streak adds a bonus. Each level is a set of up to ten pictures, none repeated; finish the set and you choose — climb to the next level, replay this one, or stop and take your rank.</p>'
      + '<div id="game-main">' + spinner('Loading the gallery…') + '</div>';
    try {
      await loadGamePool();
    } catch (e) {
      $('#game-main').innerHTML = '<div class="notice error">The game pictures could not be loaded: ' + esc(e.message) + '</div>';
      return;
    }
    if (!gameState.phase) startGame(1, true);
    else renderGame();
  }

  function renderGame() {
    const main = $('#game-main');
    if (!main) return;
    main.innerHTML = '<div id="game-controls"></div><div id="game-stage"></div>'
      + '<div class="notice">Every picture is an open-access image from the museum that holds the work — the Metropolitan Museum of Art, the Art Institute of Chicago or the Cleveland Museum of Art — and the answer is the artist that museum’s own record names. Levels are set curatorially: the most famous pictures sit at levels 1–3, and obscurer works by closer-matched artists rise to 10. <a href="/data/game/POOL.md" target="_blank" rel="noopener">How the pool was built</a>.</div>';
    renderGameControls();
    renderGameStage();
  }

  function renderGameControls() {
    const el = $('#game-controls');
    if (!el || !gamePool) return;
    const counts = {};
    for (const w of gamePool.works) counts[w.level] = (counts[w.level] || 0) + 1;
    const chips = [];
    for (let l = 1; l <= 10; l++) {
      chips.push('<button class="chip' + (gameState.level === l ? ' active' : '') + '" data-game-level="' + l + '">Level ' + l + '</button>');
    }
    el.innerHTML = '<div class="game-modes">'
      + '<button class="btn btn-primary" id="game-ladder">Play the ladder · levels 1 → 10</button>'
      + '<span class="meta">or play one level:</span>'
      + '<span class="filters">' + chips.join('') + '</span></div>'
      + '<div class="game-scorebar"><span>Score <b>' + gameState.score.toLocaleString() + '</b></span>'
      + '<span>Streak <b>' + gameState.streak + '</b></span>'
      + '<span>Right <b>' + gameState.correct + '</b> of <b>' + gameState.played + '</b></span>'
      + (gameState.set && gameState.phase === 'playing' ? '<span>Level <b>' + gameState.set.level + '</b> · Round <b>' + Math.min(gameState.set.played + 1, gameState.set.size) + '</b> of <b>' + gameState.set.size + '</b></span>' : '')
      + (gameState.set && gameState.phase === 'complete' ? '<span>Level <b>' + gameState.set.level + '</b> complete</span>' : '')
      + '</div>';
    $('#game-ladder').addEventListener('click', () => startGame(1, true));
    el.querySelectorAll('[data-game-level]').forEach((b) => b.addEventListener('click', () => startGame(+b.dataset.gameLevel, false)));
  }

  function renderGameStage() {
    const el = $('#game-stage');
    if (!el || !gamePool) return;
    const sb = $('.game-scorebar');
    if (sb) renderGameControls();
    if (gameState.phase === 'complete' && gameState.set) {
      const s = gameState.set;
      const acc = gameState.played ? Math.round((100 * gameState.correct) / gameState.played) : 0;
      el.innerHTML = '<div class="game-stage"><h2 style="font-size:30px">Level ' + s.level + ' complete</h2>'
        + '<p>You got <b>' + s.correct + '</b> right of <b>' + s.played + '</b> rounds at this level, earning <b>' + s.points.toLocaleString() + '</b> points.</p>'
        + '<p>Session so far: <b>' + gameState.score.toLocaleString() + ' points</b> · rank <b>' + esc(gameRank(gameState.score)) + '</b> · ' + gameState.correct + ' right of ' + gameState.played + ' (' + acc + '%) overall.</p>'
        + '<p class="game-rank">Care to move to the next?</p>'
        + '<div class="game-modes"><button class="btn btn-primary" id="game-next-level">Next level →</button>'
        + '<button class="btn" id="game-replay-level">Replay this level</button>'
        + '<button class="btn" id="game-finish">Finish</button></div></div>';
      $('#game-next-level').addEventListener('click', () => startGame(s.level + 1, false));
      $('#game-replay-level').addEventListener('click', () => startGame(s.level, false));
      $('#game-finish').addEventListener('click', finishSession);
      return;
    }
    if (gameState.phase === 'finished') {
      const acc = gameState.played ? Math.round((100 * gameState.correct) / gameState.played) : 0;
      const s = gameState.set;
      el.innerHTML = '<div class="game-stage"><h2 style="font-size:30px">Session complete</h2>'
        + (gameState.setDone && s && s.level >= 10 ? '<p>Level 10 complete: <b>' + s.correct + '</b> right of <b>' + s.played + '</b> rounds, earning <b>' + s.points.toLocaleString() + '</b> points at the top level.</p>' : '')
        + '<p class="game-final-score">' + gameState.score.toLocaleString() + ' points</p>'
        + '<p>' + gameState.correct + ' right of ' + gameState.played + ' (' + acc + '%), best streak ' + gameState.best + '.</p>'
        + '<p class="game-rank">Your rank: <b>' + esc(gameRank(gameState.score)) + '</b></p>'
        + '<p class="meta">Ranks run Gallery Visitor · Art Lover · Docent · Connoisseur · Curator · Chief Curator.</p>'
        + '<div class="game-modes"><button class="btn btn-primary" id="game-again">Play again</button></div></div>';
      $('#game-again').addEventListener('click', () => startGame(1, true));
      return;
    }
    const g = gameState.round;
    if (!g) {
      el.innerHTML = '<div class="game-stage"><div class="notice">No picture is available at this level just now — try another level.</div></div>';
      return;
    }
    const w = g.work;
    let html = '<div class="game-stage">'
      + '<div class="sales-feature-label">Level ' + g.level + (gameState.set ? ' · Round ' + Math.min(gameState.set.played + 1, gameState.set.size) + ' of ' + gameState.set.size : '') + ' · ' + (g.level * 100) + ' points</div>'
      + '<figure class="game-figure"><img id="game-img" src="' + esc(w.image) + '" alt="A painting to identify">'
      + '<figcaption class="game-credit">Image: ' + esc(w.museum) + ' · open access</figcaption></figure>'
      + '<div class="game-q">' + esc(gameQuestion(w)) + '</div><div class="game-options">';
    g.options.forEach((name, i) => {
      let cls = 'game-opt';
      let dis = '';
      if (g.answered >= 0) {
        dis = ' disabled';
        if (name === w.artist) cls += ' right';
        else if (i === g.answered) cls += ' wrong';
      }
      html += '<button class="' + cls + '" data-game-opt="' + i + '"' + dis + '><span class="game-letter">' + 'ABCD'[i] + '</span>' + esc(name) + '</button>';
    });
    html += '</div>';
    if (g.answered >= 0) {
      const right = g.options[g.answered] === w.artist;
      const meta = gamePool.artists[w.artist];
      html += '<div class="game-verdict ' + (right ? 'is-right' : 'is-wrong') + '">'
        + (right ? '<strong>Right — +' + g.gained + ' points</strong>' + (g.bonus ? ' (including a ' + g.bonus + '-point streak bonus)' : '') + '.'
                 : '<strong>Not quite.</strong> It is ' + esc(w.artist) + '.')
        + '<div class="game-work"><i>' + esc(w.title) + '</i>' + (w.date ? ', ' + esc(w.date) : '')
        + ' — ' + esc(w.artist) + (meta && (meta.birth || meta.death) ? ' (' + (meta.birth || '?') + '–' + (meta.death || '?') + ')' : '')
        + '<br>' + esc(w.museum) + ' · ' + link(w.objectUrl, 'the museum’s object page')
        + (w.medium ? '<br>' + esc(w.medium) : '')
        + '<br><a href="#/search?q=' + enc(w.artist) + '">Research ' + esc(w.artist) + ' in the Atlas →</a></div></div>'
        + '<div class="pager"><button class="btn btn-primary" id="game-next">'
        + (gameState.set && gameState.set.played >= gameState.set.size ? 'See how you did →' : 'Next painting →')
        + '</button></div>';
    }
    html += '</div>';
    el.innerHTML = html;
    const img = $('#game-img');
    if (img) img.addEventListener('error', () => {
      if (g.answered >= 0) return;
      gameState.bad.add(w.image);
      gameState.round = newGameRound(g.level);
      if (!gameState.round) { completeSet(); return; }
      renderGameStage();
    });
    el.querySelectorAll('[data-game-opt]').forEach((b) => b.addEventListener('click', () => gameAnswer(+b.dataset.gameOpt)));
    const next = $('#game-next');
    if (next) next.addEventListener('click', gameNext);
  }

  async function viewReport(p) {
    const cached = JSON.parse(sessionStorage.getItem('cand:' + (p.wd || p.ulan)) || 'null');
    const state = { p, refs: Object.fromEntries(REF_CATS.map(([k]) => [k, new Map()])), prof: null, data: {} };
    window.__report = state;
    const secs = SECTIONS.filter(([k]) => k !== 'synthesis' || config.ai);
    app.innerHTML = `<div class="report">
      <aside class="toc"><h4>Report contents</h4>${secs.map(([k, l], i) => `<a href="#sec-${k}" data-toc="${k}"${k === 'catalogue' ? ' class="hl"' : ''}><span>${k === 'synthesis' ? '★' : i + (config.ai ? 0 : 1)}. ${l}</span><span class="st loading-dot" id="st-${k}"></span></a>${k === 'references' ? REF_CATS.map(([rk, rl]) => `<a class="sub" href="#ref-${rk}"><span>${rl}</span><span class="st" id="rc-${rk}"></span></a>`).join('') : ''}`).join('')}</aside>
      <div>
        <div class="rep-head" id="rep-head">${cached ? headHtml({ name: cached.name, births: [cached.birth].filter(Boolean), deaths: [cached.death].filter(Boolean), birthPlace: cached.birthPlace, deathPlace: cached.deathPlace, description: cached.description, image: cached.image?.replace('?width=160', '?width=400') }, true) : spinner('Loading artist record…')}</div>
        ${secs.map(([k, l], i) => `<section class="rs${k === 'catalogue' ? ' hl' : ''}" id="sec-${k}"><h2><span><span class="num">${k === 'synthesis' ? '★' : i + (config.ai ? 0 : 1)}</span>${l}</span><small id="sm-${k}"></small></h2><div id="body-${k}">${k === 'synthesis' ? '' : spinner()}</div></section>`).join('')}
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
      catalogue: api('/api/report/catalogue', common).then((d) => renderCatalogue(state, d)),
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
    renderTimeline(state);
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

  /* --------------------------------------------------- Timeline */
  // One chronological spine merging the dated records the report has
  // already gathered — life, works, exhibitions, publications and
  // catalogues raisonnés. No new data source: everything comes from
  // state.prof and state.data as filled by the section renderers.
  // Events after the artist's death are marked POSTHUMOUS so later
  // scholarship, catalogues and retrospectives are not read as life
  // events. Undated works stay off the spine and are counted in the
  // note, and the works shown are the report's sample, not an oeuvre.
  function renderTimeline(state) {
    const el = $('#body-timeline');
    if (!el) return;
    const pr = state.prof;
    const yrOf = (s) => {
      const m = String(s || '').match(/\b(1\d{3}|[5-9]\d{2})\b/);
      return m ? +m[1] : null;
    };
    const by = pr.birthYear || yrOf((pr.births || [])[0]);
    const dy = pr.deathYear || yrOf((pr.deaths || [])[0]);
    const ev = [];
    const KIND = { life: ['Life', 0], work: ['Work', 1], exhibition: ['Exhibition', 2], publication: ['Publication', 3], catalogue: ['Catalogue', 4] };
    const push = (y, k, html, sub, label) => {
      if (y) ev.push({ y, k, html, sub: sub || '', label: label || String(y), post: !!(dy && y > dy && k !== 'life') });
    };
    if (by) push(by, 'life', `<b>Born</b>${pr.birthPlace ? ' — ' + esc(pr.birthPlace) : ''}`, (pr.births || []).join(' / '));
    if (dy) push(dy, 'life', `<b>Died</b>${pr.deathPlace ? ' — ' + esc(pr.deathPlace) : ''}`, (pr.deaths || []).join(' / '));
    // Works — the collections sample and museum objects, deduplicated.
    const cw = state.data.collections;
    let undated = 0;
    if (cw) {
      const seen = new Set();
      for (const w of [...(cw.works || []), ...(cw.museumObjects || [])]) {
        if (!w.title) continue;
        const y = w.year || yrOf(w.date);
        const key = w.title.toLowerCase() + '|' + (y || '');
        if (seen.has(key)) continue;
        seen.add(key);
        if (!y) { undated++; continue; }
        push(y, 'work', link(w.url, w.title), [w.institution || w.museum || (w.collections || []).join(', '), w.date && String(w.date) !== String(y) ? w.date : ''].filter(Boolean).join(' · '));
      }
    }
    // Exhibitions — Wikidata chronology and the Art Institute's.
    const ex = state.data.exhibitions;
    if (ex) {
      for (const e of ex.wikidata || [])
        if (e.start) push(e.start, 'exhibition', link(e.url, /^Q\d+$/.test(e.title) ? `Untitled exhibition record (${e.title})` : e.title), (e.venues || []).join(', '));
      for (const e of ex.aic || []) {
        const y = yrOf(e.date);
        if (y) push(y, 'exhibition', link(e.url, e.title), 'Art Institute of Chicago');
      }
    }
    // Publications — books, subject works and scholarship, deduplicated
    // the same way as the bibliography export (DOI, else title + year).
    const ac = state.data.academic;
    if (ac) {
      const seen = new Set();
      for (const w of [...(ac.books || []), ...(ac.subjectWorks || []), ...(ac.scholarly || [])]) {
        if (!w.title || !w.year) continue;
        const key = w.doi || (w.title.toLowerCase().replace(/[^a-z0-9]+/g, ' ') + '|' + w.year);
        if (seen.has(key)) continue;
        seen.add(key);
        push(w.year, 'publication', link(w.doi ? 'https://doi.org/' + w.doi : w.url, w.title), [(w.authors || []).slice(0, 3).join(', '), w.venue].filter(Boolean).join(' · '));
      }
    }
    // Catalogues raisonnés, in the chronological order of the section.
    const cat = state.data.catalogue;
    if (cat) for (const x of cat.items || [])
      if (x.year) push(x.year, 'catalogue', link(x.url, x.title), [(x.authors || []).join(', '), x.note].filter(Boolean).join(' · '), x.yearEnd ? `${x.year}–${x.yearEnd}` : String(x.year));
    ev.sort((a, b) => a.y - b.y || KIND[a.k][1] - KIND[b.k][1]);
    const counts = {};
    for (const e of ev) counts[e.k] = (counts[e.k] || 0) + 1;
    const PLURAL = { life: 'Life', work: 'Works', exhibition: 'Exhibitions', catalogue: 'Catalogues', publication: 'Publications' };
    const chips = [['all', 'All'], ...Object.keys(KIND).filter((k) => counts[k]).map((k) => [k, PLURAL[k]])]
      .map(([k, l]) => `<button class="chip${k === 'all' ? ' active' : ''}" data-tl="${k}">${l} (${k === 'all' ? ev.length : counts[k]})</button>`).join(' ');
    $('#sm-timeline').textContent = ev.length ? `${plural(ev.length, 'dated event')} · ${ev[0].y}–${ev[ev.length - 1].y}` : '';
    el.innerHTML = `
      <p class="source-line">One chronology for the dated records gathered in this report. It is only as complete as the open record: exhibition coverage is incomplete, especially before 1900${cw ? `; the works are the dated works gathered for Works &amp; collections, drawn from ${cw.totalWorks.toLocaleString()} catalogued works — not the complete oeuvre` : ''}${undated ? `; ${plural(undated, 'undated work')} among them ${undated === 1 ? 'is' : 'are'} left off the spine` : ''}. Events after the artist’s death are marked <span class="tag-post">POSTHUMOUS</span>.</p>
      ${ev.length ? `<div class="filters" style="margin:0 0 10px">${chips}</div>
      <div>${ev.map((e) => `<div class="tl-row" data-kind="${e.k}"><span class="yr">${esc(e.label)}</span> ${e.html}<span class="tl-tag">${KIND[e.k][0]}</span>${e.post ? '<span class="tag-post">POSTHUMOUS</span>' : ''}${e.sub ? `<div class="sub">${esc(e.sub)}</div>` : ''}</div>`).join('')}</div>`
      : '<div class="notice">No dated records were found in the open sources for this artist — the report’s other sections hold what is known.</div>'}`;
    el.querySelectorAll('[data-tl]').forEach((b) => b.addEventListener('click', () => {
      el.querySelectorAll('[data-tl]').forEach((x) => x.classList.toggle('active', x === b));
      const k = b.dataset.tl;
      el.querySelectorAll('.tl-row').forEach((r) => { r.style.display = k === 'all' || r.dataset.kind === k ? '' : 'none'; });
    }));
    done('timeline');
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
    for (const w of d.books || []) addRef(state, 'acad', w.cite, { year: w.year });     
    $('#sm-academic').textContent = `${d.subjectWorks.length + d.scholarly.length + (d.books?.length || 0)} publications`;
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
      <div class="sub">${esc([w.authors?.slice(0, 4).join(', '), w.venue, w.type].filter(Boolean).join(' · '))}${w.citedBy != null ? ` · cited by ${w.citedBy}` : ''}${w.field ? ` · ${esc(w.field)}` : ''}${w.openAccess ? ' · ' + link(w.openAccess, 'open-access copy') : ''}${w.editions ? ` · ${w.editions} edition${w.editions > 1 ? 's' : ''}` : ''}${w.url?.includes('openlibrary.org') ? ' · ' + link('https://search.worldcat.org/search?q=' + encodeURIComponent([w.title, w.authors?.[0]].filter(Boolean).join(' ')), 'find in a library') : ''}</div>
      ${w.abstract ? `<details><summary>Abstract</summary><div class="abs">${esc(w.abstract)}</div></details>` : ''}</li>`;
    const startHere = [d.books?.[0], d.scholarly?.[0]].filter(Boolean); 
    const recent = d.scholarly.filter((w) => w.year && w.year >= new Date().getFullYear() - 10).slice(0, 8); 
    $('#body-academic').innerHTML = `
      ${errs(d.errors)} 
      <p class="source-line">Bibliography drawn from open indexes — Wikidata, OpenAlex/Crossref and Open Library. It is not exhaustive: JSTOR, Art Full Text and the Bibliography of the History of Art hold more, behind paywalls or library logins; use the database links below. <button class="btn btn-sm" data-export="bib">Download BibTeX (.bib)</button> <button class="btn btn-sm" data-export="ris">Download RIS (.ris)</button></p> 
      ${startHere.length ? `<h3>Start here — the essential reading</h3><p class="source-line">The most widely held book (by number of editions) and the most-cited article. If you read two things about ${esc(pr.name)}, read these.</p>${list(startHere, pub, 5)}` : ''} 
      ${d.books?.length ? `<h3>Key books & monographs (${d.books.length})</h3><p class="source-line">Books with ${esc(pr.name)} as subject, from Open Library — ranked by number of editions, a rough measure of how widely a book is held and read. Fiction and children's books are excluded.</p>${list(d.books, pub, 10)}` : ''}
      ${d.subjectWorks.length ? `<h3>Scholarship with the artist as principal subject (${d.subjectWorks.length})</h3><p class="source-line">Books, articles, catalogues raisonnés and theses catalogued in Wikidata with the artist as main subject — a curated, high-precision list, in chronological order.</p>${list(d.subjectWorks, pub, 15)}` : ''}
      ${d.scholarly.length ? `<h3>Most-cited scholarly literature (${d.scholarly.length})</h3><p class="source-line">Peer-reviewed articles, books and chapters mentioning “${esc(pr.name)}” in the title or abstract, ranked by citations (${esc(d.scholarlySource || 'OpenAlex')}). ${d.scholarlySource === 'Crossref' ? 'Crossref has no subject filter, so results are kept only when they name the artist in full or in an art context, and non-art venues (medicine, the sciences) and other people with the same surname are excluded.' : 'Restricted to Arts and Humanities, so namesake studies from other fields (medicine, the natural sciences, patent law) are excluded.'}</p>${list(d.scholarly, pub, 15)}` : ''}
      ${recent.length ? `<h3>Recent scholarship — last 10 years (${recent.length})</h3>${list(recent, pub, 8)}` : ''} 
      ${d.reviews.length ? `<h3>Reviews (${d.reviews.length})</h3>${list(d.reviews, pub, 8)}` : ''}
      ${quoteHtml}
      ${!d.subjectWorks.length && !d.scholarly.length && !(d.books?.length) && !wq ? '<div class="notice">No scholarly literature was found in the open indexes. Search the specialist databases below.</div>' : ''}
      <h3>Continue in research databases</h3><div class="links">${d.databases.map((x) => link(x.url, x.label)).join('')}</div>`;
      // Bibliography export (BibTeX / RIS for Zotero): books, subject works and
  // scholarly literature combined, deduplicated by DOI or title + year.
  const bibItems = (() => {
    const seen = new Set();
    return [...(d.books || []), ...(d.subjectWorks || []), ...(d.scholarly || [])].filter((w) => {
      const k = w.doi || `${(w.title || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ')}|${w.year || ''}`;
      if (!w.title || seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  })();
    const bibKey = (w) => {
    const last = (w.authors?.[0] || 'anon').trim().split(/\s+/).pop().toLowerCase().replace(/[^a-z]/g, '') || 'anon';
    const first = (w.title || 'untitled').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean)[0] || 'work';
    return `${last}${w.year || 'nd'}${first}`;
  };
    const bibAuthor = (w) => (w.authors || []).map((a) => {
    const parts = String(a).trim().split(/\s+/);
    return parts.length > 1 ? `${parts.pop()}, ${parts.join(' ')}` : a;
  }).join(' and ');
  const isBook = (w) => /book/i.test(w.type || '') || w.url?.includes('openlibrary.org');
    const toBibtex = () => bibItems.map((w) => {
    const fields = [`  author = {${bibAuthor(w)}}`, `  title = {${(w.title || '').replace(/[{}]/g, '')}}`, w.year ? `  year = {${w.year}}` : '', !isBook(w) && w.venue ? `  journal = {${w.venue}}` : '', w.doi ? `  doi = {${w.doi}}` : '', w.url ? `  url = {${w.url}}` : ''].filter(Boolean).join(',\n');
    return `@${isBook(w) ? 'book' : 'article'}{${bibKey(w)},\n${fields}\n}`;
  }).join('\n\n');
    const toRis = () => bibItems.map((w) => [`TY  - ${isBook(w) ? 'BOOK' : 'JOUR'}`, ...(w.authors || []).map((a) => `AU  - ${a}`), `TI  - ${w.title || ''}`, w.year ? `PY  - ${w.year}` : '', !isBook(w) && w.venue ? `JO  - ${w.venue}` : '', w.doi ? `DO  - ${w.doi}` : '', w.url ? `UR  - ${w.url}` : '', 'ER  - '].filter(Boolean).join('\n')).join('\n\n');
    const download = (filename, text) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }));
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  };
  const base = pr.name.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '');
  $('#body-academic').querySelectorAll('[data-export]').forEach((b) => b.addEventListener('click', () => {
    download(`${base}-bibliography.${b.dataset.export}`, b.dataset.export === 'bib' ? toBibtex() : toRis());
    toast(`Bibliography downloaded (${bibItems.length} items)`);
  }));
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
    for (const r of d.recorded) addRef(state, 'mkt', `“${r.work}” — ${r.event || 'price'}${r.year ? ', ' + r.year : ''}${r.amount ? `, ${r.amount.toLocaleString()} ${r.unit}` : ''}. ${r.institution ? r.institution + '. ' : 'Wikidata. '}${r.workUrl}${r.wikidataUrl && r.wikidataUrl !== r.workUrl ? ` Wikidata: ${r.wikidataUrl}` : ''}`, { year: r.year });
    $('#sm-market').textContent = `${d.recorded.length} recorded transactions · ${d.provenance.length} provenance records`;
    const priced = d.recorded.filter((r) => r.amount);
    const wpMkt = wikiSections(pr.wikipedia, 'market');
    $('#body-market').innerHTML = `
      <div class="notice">${esc(d.note)}</div>${errs(d.errors)}
      ${priced.length ? `<h3>Documented prices</h3><table class="table"><tr><th>Year</th><th>Work</th><th>Price</th><th>Context</th></tr>${priced.map((r) => `<tr><td>${esc(r.year || 'n.d.')}</td><td>${link(r.workUrl, r.work)}${r.wikidataUrl && r.wikidataUrl !== r.workUrl ? ` <span class="sub">[${link(r.wikidataUrl, 'Wikidata')}]</span>` : ''}</td><td><b>${esc(r.amount.toLocaleString())} ${esc(r.unit)}</b></td><td>${esc([r.event, r.buyer && 'buyer: ' + r.buyer, r.seller && 'seller: ' + r.seller].filter(Boolean).join(' · '))}</td></tr>`).join('')}</table>` : ''}
      ${d.recorded.filter((r) => !r.amount).length ? `<h3>Sales, acquisitions & ownership events</h3>${list(d.recorded.filter((r) => !r.amount), (r) => `<li><span class="yr">${esc(r.year || 'n.d.')}</span> ${link(r.workUrl, r.work)}${r.wikidataUrl && r.wikidataUrl !== r.workUrl ? ` <span class="sub">[${link(r.wikidataUrl, 'Wikidata')}]</span>` : ''} — ${esc(r.event)}${r.buyer ? ` · to ${esc(r.buyer)}` : ''}${r.seller ? ` · from ${esc(r.seller)}` : ''}${r.year && pr.birthYear && r.year >= pr.birthYear && r.year <= (pr.deathYear || 9999) ? '<span class="tag-life">LIFETIME</span>' : ''}</li>`, 15)}` : ''}
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
    // The work's title links to the holding institution's verified page; the
    // Wikidata link, where it differs, follows small and secondary — never
    // first, never styled as the authority. A work with no institutional
    // page links plainly to Wikidata.
    const fig = (o) => `<figure>${o.image ? `<a href="${esc(o.url)}" target="_blank" rel="noopener"><img src="${esc(o.image)}" alt="${esc(o.title)}" loading="lazy"></a>` : ''}<figcaption>${link(o.url, o.title)}${o.wikidataUrl && o.wikidataUrl !== o.url ? ` <span class="sub">[${link(o.wikidataUrl, 'Wikidata')}]</span>` : ''}<br><span class="muted">${esc([o.date || o.year, o.museum || o.institution || (o.collections || []).join(', ')].filter(Boolean).join(' · '))}</span></figcaption></figure>`;
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

    /* ------------------------------------------- 9. Catalogue raisonné */
  function renderCatalogue(state, d) {
        if (!(d.items || []).length) {
      // No catalogue raisonné exists for this artist: drop the section
      // entirely (contents entry and card) and renumber what follows it.
      document.querySelector('.toc a[data-toc="catalogue"]')?.remove();
      document.getElementById('sec-catalogue')?.remove();
      let n = 0;
      document.querySelectorAll('.toc a[data-toc]').forEach((a) => {
        const span = a.querySelector('span');
        if (!span || span.textContent.includes('★')) return;
        n += 1;
        span.textContent = span.textContent.replace(/^\d+\.\s*/, `${n}. `);
      });
      let m = 0;
      document.querySelectorAll('section.rs h2 .num').forEach((el) => {
        if (el.textContent.trim() === '★') return;
        m += 1;
        el.textContent = String(m);
      });
      return;
    }
    state.data.catalogue = d;
    $('#sm-catalogue').textContent = `${plural(d.items.length, 'volume')} · earliest ${d.items[0].year || 'undated'}`;
    for (const x of d.items) addRef(state, 'acad', x.cite, { year: x.year });
    $('#body-catalogue').innerHTML = `
      ${errs(d.errors)}
      <p class="source-line">The catalogue raisonné is the standard complete, authenticated listing of an artist's works — the reference scholars cite first. Volumes below are drawn from Open Library and Wikidata, in chronological order, including catalogues later superseded by newer ones; the history of cataloguing is part of the record. Where a standard modern catalogue is published under another title (for example, "A Corpus of Rembrandt Paintings"), it is listed from a short curated set.</p>
      ${list(d.items, (x) => `<li>${link(x.url, x.title)} <span class="sub">— ${esc([x.authors.join(', '), x.year ? (x.yearEnd ? `${x.year}–${x.yearEnd}` : x.year) : null, x.note, x.publisher].filter(Boolean).join(' · '))}</span>${x.iaUrl ? ` <span class="sub">[${link(x.iaUrl, 'Read on Internet Archive')}]</span>` : ''}</li>`, 15)}
      <h4>Search further</h4><div class="links">${d.links.map((x) => link(x.url, x.label)).join('')}</div>`;
    done('catalogue');
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

  /* ============================================================= feedback */
  function viewFeedback() {
    app.innerHTML = `<section class="rs prose" style="max-width:760px;margin:0 auto">
      <h2>Feedback</h2>
      <p>Comments, corrections and suggestions about the Atlas are welcome. Messages go to the editor and help decide what is built next. The two boxes are optional individually — please write in at least one of them.</p>
      <form id="feedback-form" class="feedback-form" novalidate>
        <label for="fb-comments">Comments</label>
        <textarea id="fb-comments" rows="6" maxlength="5000" placeholder="Corrections, problems, questions — anything about the site as it stands."></textarea>
        <label for="fb-wishes">What else would you like to see on the site?</label>
        <textarea id="fb-wishes" rows="4" maxlength="5000" placeholder="Artists, exhibitions, records or tools you would like the Atlas to cover."></textarea>
        <label for="fb-name">Your name and email (optional — only if you’d like a reply)</label>
        <div class="feedback-contact">
          <input id="fb-name" type="text" autocomplete="name" placeholder="Name" maxlength="120" />
          <input id="fb-email" type="email" autocomplete="email" placeholder="Email" maxlength="254" />
        </div>
        <div class="fb-hp" aria-hidden="true">
          <label for="fb-website">Leave this field empty</label>
          <input id="fb-website" name="website" type="text" tabindex="-1" autocomplete="off" />
        </div>
        <div id="fb-status" role="status" aria-live="polite"></div>
        <button type="submit" class="btn btn-primary" id="fb-send">Send feedback</button>
      </form>
    </section>`;
    const form = $('#feedback-form');
    const status = $('#fb-status');
    const showError = (msg) => { status.innerHTML = `<div class="notice error">${esc(msg)}</div>`; };
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const comments = $('#fb-comments').value.trim();
      const wishes = $('#fb-wishes').value.trim();
      const name = $('#fb-name').value.trim();
      const email = $('#fb-email').value.trim();
      if (!comments && !wishes) {
        showError('Please write something in one of the two boxes before sending.');
        $('#fb-comments').focus();
        return;
      }
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showError('That email address does not look complete — please check it, or leave it blank.');
        $('#fb-email').focus();
        return;
      }
      const btn = $('#fb-send');
      btn.disabled = true;
      status.innerHTML = `<div class="loading"><div class="spinner"></div><span>Sending…</span></div>`;
      let r, d;
      try {
        r = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ comments, wishes, name, email, website: $('#fb-website').value }),
        });
        d = await r.json().catch(() => ({}));
      } catch {
        // Nothing was sent and nothing is lost: the typed text stays put.
        btn.disabled = false;
        showError('Your message could not be sent — please check your connection and try again. Your text is still in the form.');
        return;
      }
      if (r.ok && d.ok) {
        form.innerHTML = `<div class="notice">Thank you — your feedback has been sent.</div>`;
        return;
      }
      btn.disabled = false;
      showError(d.error || 'Your message could not be sent just now. Please try again later — your text is still in the form.');
    });
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
        <li><b>Timeline</b> — one chronological spine merging the dated records gathered for the report: birth and death, dated works (with the same verified institutional links as Works &amp; collections), exhibitions, publications, and catalogues raisonnés in chronological order, including superseded ones. Anything dated after the artist’s death — later scholarship, catalogues, retrospectives — is marked posthumous, not presented as a life event. Undated works are left off the spine and counted in the section’s note; exhibition coverage in open sources is incomplete, especially before 1900; and the works are those gathered for the report, not the complete oeuvre.</li>
        <li><b>Exhibition record</b> — Wikidata exhibition items (including exhibitions at which individual works were shown), Art Institute of Chicago exhibitions, object-level exhibition histories from museum records, and exhibition catalogues from Open Library, plus links to DoME, Paris Salon, Royal Academy, RKD, MoMA and Artfacts.</li>
        <li><b>Bibliography & scholarship</b> — key books and monographs with the artist as subject (Open Library, ranked by number of editions), curated scholarship with the artist as main subject (Wikidata), the most-cited literature in OpenAlex (250M+ scholarly works) and Crossref, reviews, and chronologically arranged quotations from contemporaries, fellow artists and critics (Wikiquote). Start with the "Start here" shelf; the whole bibliography downloads as BibTeX or RIS for Zotero.</li>
        <li><b>Critical analyses</b> — encyclopaedic discussion of style, technique, reception and legacy, and arguments drawn from leading scholarship.</li>
        <li><b>Auction & art sales</b> — documented prices, sales and ownership events, provenance chains published by museums, the artist’s pages on Artnet, Artsy, MutualArt, Invaluable and others, and pre-filled searches of auction archives. Full auction records are in subscription databases and are linked rather than reproduced.</li>
        <li><b>Works & collections — linking to the holding institution</b> — a work's title links to the holding museum's own object page wherever one exists and can be verified; Wikidata is the finding aid, never the authority. How a link is resolved: the work list comes from Wikidata (a SPARQL query for works with the artist as creator, <i>wdt:P170</i>), together with the museum identifiers recorded there — the <i>Met object ID</i> (property P3634) and the <i>Art Institute of Chicago artwork ID</i> (property P4610). Each identifier is checked against the institution's own open API — the Met Collection API (<code>collectionapi.metmuseum.org/public/collection/v1/objects/{id}</code>), which returns the museum's canonical object page (<code>objectURL</code>), and the Art Institute of Chicago API (<code>api.artic.edu/api/v1/artworks/{id}</code>), whose public page is <code>artic.edu/artworks/{id}</code>. Only an identifier the institution's API confirms becomes the work's link; if it does not resolve, the work links to its Wikidata item page instead. Museum open-access records are fetched directly from the same APIs — the Met, the Art Institute of Chicago, and the Cleveland Museum of Art's open-access API (<code>openaccess-api.clevelandart.org</code>), which returns each object's own page URL with the record — and Europeana records link to the Europeana item page. Where no institutional page exists, the work links to its Wikidata page, shown plainly as such and never presented as a museum source. Direct automated checks of museum web pages are not reliable (their servers reject them), which is why verification runs through the institutions' open APIs.</li>
        <li><b>Browse</b> — the browse page lists artists by century (12th–20th), country, movement or medium, and any combination of the four: pick from the dropdowns and press GO. The country list is every country with eligible artists (a live count of citizenships, including the historical states grouped under the modern country — Rembrandt and Vermeer are recorded as citizens of the Dutch Republic, Leonardo of the Republic of Florence — so the Dutch masters and the Italian Renaissance appear where they belong; states that map to no modern country appear under their own name). Each list is a live Wikidata query restricted to painters, sculptors, draftsmen, engravers and printmakers, capped at 50 artists, best-documented first — plus a curated index of the twenty homepage artists grouped the same way. As everywhere on the site, Wikidata is the finding aid: it finds the artist, and the report then links each work to the holding institution's verified page.</li>
        <li><b>Salon Time Machine</b> — the Paris Salon catalogues, 1673–1898: 188,028 works by year, section and catalogue number, transcribed from the printed livrets (the years to 1881 from the Garland reprints, the Société des Artistes Français livrets of 1882–1897 direct from the Internet Archive; 1898 from Baschet's Catalogue illustré, which prints the Painting and Sculpture sections only, so that year is partial) and parsed from OCR. Catalogue numbers marked ~ were inferred from the sequence or look suspect in the printed text; some titles carry OCR noise and a few artist names are fragments. Years with no surviving livret are simply absent; nine years between 1882 and 1900 (1883, 1887, 1888, 1889, 1892, 1894, 1896, 1899, 1900) are missing because no digitised livret is available to us, and the 1886 volume's poor scan files most of its Architecture entries under Gravure and loses its opening entries. Each artist name links to the usual name search, so a Salon exhibitor leads straight to the full research report. No images in this first version: most Salon works have no surviving image in the open sources.</li>
        <li><b>Royal Academy Time Machine</b> — the Royal Academy Summer Exhibition catalogues, 1769–1905: 161,019 works by year, occupation and catalogue number, compiled from Algernon Graves’s <i>The Royal Academy of Arts: A Complete Dictionary of Contributors and Their Work</i> (1905–06), with the 1905 exhibition recovered from the Paul Mellon Centre’s RA Chronicle catalogue transcription, and parsed from OCR. Names, addresses and titles are as printed, with the OCR noise of the source scans. Catalogue numbers marked ~ are uncertain in the source; about 12,200 records have no readable catalogue number and show —, and no number has been invented for them. A further 1,543 records in the full database, whose year could not be resolved, are not in this browser. Each artist name links to the usual name search, so an exhibitor leads straight to the full research report. No images in this first version.</li>
        <li><b>Loan Exhibitions (UK)</b> — Algernon Graves’s <i>A Century of Loan Exhibitions 1813–1912</i> (1913–15): 42,727 works lent to a century of loan exhibitions, arranged by artist as Graves printed them, each with the exhibition, year, catalogue number, size and the owner who lent it — so the page searches three ways: by artist (the complete loan record in one view), by title (a work traced across exhibitions), and by owner (everything a collector or institution lent). It is also browsable letter by letter. Parsed from the Internet Archive scan of the Kingsmead reprint; names, titles and owners are as printed, with the scan’s OCR noise — sizes suffer most, their printed fractions often read as plain digits. Numbers marked ~ had ambiguous digits in the scan (the systematic confusions normalised, none invented); about 1,790 records have no readable number and show —. An owner marked ~ was split from the title by column position alone and may be mis-split. “Unknown Painters” is Graves’s own heading for unattributed works. Each artist name links to the usual name search. No images in this first version.</li>
        <li><b>Record of Exhibitions</b> — original exhibition catalogues, digitised and parsed into searchable records (catalogue number, artist, title, medium, size and lender): the primary sources themselves, not a digest of them. Forty-nine catalogues are recorded so far: eleven Guildhall catalogues, all parsed from Internet Archive scans (Getty scans) of the Art Gallery of the Corporation of London’s catalogues, the six Salons de la Rose+Croix (1892–1897) — the five later ones recorded from John Finnegan’s compilation of their printed catalogues, the first parsed from Gallica’s OCR text of the Bibliothèque nationale de France digitisation — and the American Water Color Society’s twenty-fourth, twenty-fifth, twenty-sixth, twenty-seventh, twenty-eighth, twenty-ninth, thirtieth, thirty-first, thirty-second, thirty-third, thirty-fourth, thirty-fifth, thirty-sixth, thirty-seventh, thirty-eighth, thirty-ninth, fortieth, forty-first, forty-second, forty-third, forty-fourth, forty-fifth, forty-sixth, forty-seventh, forty-eighth, forty-ninth, fiftieth, fifty-first, fifty-second, fifty-third and fifty-fourth annual exhibitions (New York, 1891–1921), and the Combined Annual Exhibition of the American Water Color Society and the New York Water Color Club (New York, 1922–23), parsed from Frick Library scans supplied by John Finnegan — the thirty-sixth and thirty-seventh from the Internet Archive’s scans of the Philadelphia Museum of Art’s copies (items 1903AWS and 1904AWS), the thirty-eighth from the Internet Archive’s scan of the Metropolitan Museum Library’s copy (item 1905AWS), the fifty-third and fifty-fourth from the Internet Archive’s scans of the Philadelphia Museum of Art’s copies. The <i>Illustrated Catalogue of the Twenty-Fourth Annual Exhibition of the American Water Color Society</i> (2–28 February 1891, National Academy of Design, New York): 661 works in four galleries — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (617 works are priced for sale, the prices including frames) and an owner standing as lender on 20; the scan’s text layer displaces the price and artist columns, so every one of the catalogue’s 29 pages was read against the page images during the parse. The <i>Illustrated Catalogue of the Twenty-Fifth Annual Exhibition of the American Water Color Society</i> (1–27 February 1892, National Academy of Design, New York): 676 works in four galleries — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (647 works are priced for sale, the prices including frames) and an owner standing as lender on 10; 27 works are illustrated, an asterisk in this catalogue marking illustrations from the artists’ own drawings; the dearest work in the catalogue is John La Farge’s ‘The Peak of Maona Roa Morea, Society Islands’ (no. 178), priced at $4,200; one entry (no. 232, by Louis C. Tiffany) prints no title at all; two catalogue numbers (378 and 672) were restored from their sequence position, each flagged in its record’s note; the scan’s text layer displaces the price and artist columns, so every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Twenty-Sixth Annual Exhibition of the American Water Color Society</i> (30 January–25 February 1893, National Academy of Design, New York): 646 works in four galleries — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (608 works are priced for sale, the prices including frames) and an owner standing as lender on 8; 21 works are illustrated, identified from the captions of the plates themselves, this catalogue printing no illustration marks in the body; the dearest works are five pictures priced at $1,000 each, among them H. F. Farney’s ‘A Mountain Trail—Crow Indians’ (no. 256) and John La Farge’s portrait of Faase of Samoa (no. 309); two catalogue numbers (110 and 111) were restored from their sequence position, each flagged in its record’s note; the scan’s text layer displaces the price and artist columns, so every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Twenty-Seventh Annual Exhibition of the American Water Color Society</i> (5 February–3 March 1894, National Academy of Design, New York): 607 works in four galleries — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (577 works are priced for sale, the prices including frames) and an owner standing as lender on 5; 21 works are illustrated — nineteen marked in the body and two identified from the captions of the plates themselves, the plate of no. 347 serving as the frontispiece; the dearest work in the catalogue is Wm. Magrath’s ‘Trafalgar Square, London’ (no. 160), priced at $1,500; one entry (no. 47, James D. Smillie’s ‘Well, Capuchin Monastery, Italy’) is marked ‘Not for sale’, the catalogue’s only sale mark; three catalogue numbers (110, 111 and 295) were restored from their sequence position, each flagged in its record’s note; the scan’s text layer displaces the price and artist columns, so every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Twenty-Eighth Annual Exhibition of the American Water Color Society</i> (4 February–2 March 1895, National Academy of Design, New York): 510 works in four galleries — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (475 works are priced for sale, the prices including frames) and an owner standing as lender on 5; 19 works are illustrated — sixteen marked in the body and three identified from the captions of the plates themselves, the plate of no. 302 serving as the frontispiece; the dearest works are two pictures priced at $1,000 each, Henry Farrer’s ‘When leaves are brown, and the year is old’ (no. 312) and Frank Russell Green’s ‘A Pastoral’ (no. 324); no. 446 is printed as a bare number, with no artist, title or price against it; one entry (no. 347, Beatrice C. Wilcox’s ‘Roses’) is marked ‘Not for sale’, the catalogue’s only sale mark; one catalogue number (111) was restored from its sequence position, flagged in its record’s note; the scan’s text layer displaces the price and artist columns, so every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Twenty-Ninth Annual Exhibition of the American Water Color Society</i> (3–29 February 1896, National Academy of Design, New York): 608 works in five sections — the four galleries and, new this year, the Corridor — the catalogue’s ‘Owner or Price’ column is carried into the records, the price standing in each record’s note (588 works are priced for sale, the prices including frames) and an owner standing as lender on 9; 19 works are illustrated, each marked ‘(Illustration),’ in the body — with a comma where the 1894 and 1895 catalogues print a full stop — and eighteen captioned plates are bound in, every one naming a body-marked work; the dearest work in the catalogue is W. Louis Sonntag, Jr.’s ‘Coup de Grace’ (no. 462), priced at $750, no price in the catalogue reaching $1,000; one sub-numbered entry, no. 530a, stands between nos. 530 and 531; two entries (nos. 535 and 590, both by Miss Holgate) print no title at all; two entries (nos. 115 and 170) are marked ‘Not for sale’; four catalogue numbers (105, 110, 113 and 115) were restored from their sequence position, each flagged in its record’s note; the scan’s text layer displaces the price and artist columns, so every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirtieth Annual Exhibition of the American Water Color Society</i> (1–27 February 1897, National Academy of Design, New York): 509 works in five sections — the four galleries and the Corridor — this catalogue departs from every earlier volume in the run: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; 20 works are illustrated, each marked ‘(Illustration).’ in the body — with the full stop again, where 1896 prints a comma — and twenty captioned plates are bound in, every one naming a body-marked work, one of them, for no. 322, captioned ‘22.’ in the book’s own error; four catalogue numbers (7, 111, 317 and 371) were restored from their sequence position, each flagged in its record’s note — no. 317 is printed ‘417’ in the book itself, a misprint the sequence and the book’s own index both correct; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-First Annual Exhibition of the American Water Color Society</i> (31 January–26 February 1898, National Academy of Design, New York): 517 works in five sections — the four galleries and the Corridor — this catalogue keeps the form of 1897: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; 16 works are illustrated — fourteen marked ‘(Illustration).’ in the body, and two more, no. 143, James Symington’s ‘Hypatia’, and no. 163, George Wharton Edwards’s ‘Breakfast at the Blue Grape’, identified from the captions of their plates alone, the body printing no mark against them; one catalogue number (12) was restored from its sequence position, flagged in its record’s note — an ink blot in this copy obscures its printed figures — and corroborated by the book’s own index; this copy is a former owner’s annotated copy, its pencil marks corrupting the text layer of the book’s index, though no body reading; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-Second Annual Exhibition of the American Water Color Society</i> (13 February–11 March 1899, National Academy of Design, New York): 491 works in five sections — the four galleries and the Corridor, the Corridor shrinking to nineteen works this year — this catalogue keeps the form of 1897 and 1898: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; 21 works are illustrated — twenty marked ‘(Illustration).’ in the body, and one more, no. 340, L. C. Earle’s ‘Nimrod and his Granddaughter’, identified from the caption of its plate alone, the body printing no mark against it; twenty-two catalogue numbers were restored from their sequence position, each flagged in its record’s note, and corroborated by the book’s own index; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-Third Annual Exhibition of the American Water Color Society</i> (5–17 February 1900, Waldorf-Astoria, New York): 260 works in two rooms — the Large Room and the Small Room — the exhibition leaving the National Academy of Design for a single year at the Waldorf-Astoria; this catalogue keeps the price-less form of 1897–1899 for a fourth year: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; the numbering runs continuously through the two rooms, with four lettered inserts — 143a and 143b after no. 143, 169a and 169b after no. 169; 19 works are illustrated, identified from the captions of the plates alone, this catalogue printing no illustration marks in the body at all, the plate of no. 16 serving as the frontispiece; twelve catalogue numbers were restored from their sequence position, each flagged in its record’s note, and corroborated by the book’s own index — the cleanest index of the ten volumes, agreeing with the body on every point the scan lets it be read; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-Fourth Annual Exhibition of the American Water Color Society</i> (11 February–28 March 1901, National Academy of Design, New York): 500 works in five galleries — the exhibition returning to the galleries of the building formerly the National Academy of Design, at Twenty-Third Street and Fourth Avenue, after 1900’s single year at the Waldorf-Astoria; this catalogue keeps the price-less form of 1897–1900 for a fifth year: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; the hang is arranged by gallery again, in one continuous numbering 1–500 with no lettered inserts; 22 works are illustrated, identified from the captions of the plates alone, this catalogue printing no illustration marks in the body at all, the plate of no. 131 serving as the frontispiece; six catalogue numbers were restored from their sequence position, each flagged in its record’s note — one of them, no. 141, read from the printed page of a leaf bound into the scan twice, in two different print states; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-Fifth Annual Exhibition of the American Water Color Society</i> (21 April–4 May 1902, American Art Galleries, Madison Square South, New York): 479 works in a single alphabetical sequence — the exhibition held at the American Art Galleries, Madison Square South, under the management of the American Art Association, and the catalogue changing its form entirely: the galleries are gone, the body arranged alphabetically by artist under each artist’s heading (the addresses printed beneath the headings are not carried into the records), the works numbered continuously 1–479 down the alphabet in the single section the book heads ‘CATALOGUE’; this catalogue keeps the price-less form of 1897–1901 for a sixth year: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender; 21 works are illustrated, each marked in the body itself with a bracketed ‘[Illustration]’ after its title and agreeing exactly with the book’s own List of Illustrations, though the plate for no. 35 is not bound in this copy; three catalogue numbers were restored from their sequence position, each flagged in its record’s note — nos. 110 and 111 among them, their printed lines fused in the scan into interleaved type and their titles read from the printed page; the book prints no artist index this year, so no index cross-check was possible; every catalogue page was read against the page images during the parse. The <i>Illustrated Catalogue of the Thirty-Sixth Annual Exhibition of the American Water Color Society</i> (20–30 April 1903, American Art Galleries, Madison Square South, New York): 299 works in a single alphabetical sequence — the exhibition held at the American Art Galleries, Madison Square South, under the management of the American Art Association, and the catalogue keeping the form of 1902 entire: the body arranged alphabetically by artist under each artist’s heading (the addresses printed beneath the headings are not carried into the records), the works numbered continuously 1–299 down the alphabet in the single section the book heads ‘CATALOGUE’; this catalogue keeps the price-less form of 1897–1902 for a seventh year: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender, though the notices still state that prices include frames; 16 works are illustrated, each marked in the body itself with a bracketed ‘[Illustration]’ after its title and agreeing exactly with the book’s own List of Illustrations, all sixteen plates bound in, seven of their captions printed vertically at the leaf’s right side; two catalogue numbers were restored from their sequence position, each flagged in its record’s note — no. 118 and no. 206, whose figures the scan reads as letterforms; one heading prints ‘Deceased’ in place of the artist’s address: Henry Farrer, whose seventeen works (nos. 75–91) each carry a note; the book prints no artist index this year, so no index cross-check was possible — its member lists were cross-checked against the headings’ marks instead; every catalogue page was read against the page images during the parse, and the copy recorded is the Internet Archive’s scan of the Philadelphia Museum of Art’s copy (item 1903AWS), not one of the Frick Library scans. The <i>Illustrated Catalogue of the Thirty-Seventh Annual Exhibition of the American Water Color Society</i> (29 April–13 May 1904, American Art Galleries, Madison Square South, New York): 349 works in a single alphabetical sequence — the exhibition held at the American Art Galleries, Madison Square South, under the management of the American Art Association, and the catalogue keeping the form of 1902 and 1903 entire: the body arranged alphabetically by artist under each artist’s heading (the addresses printed beneath the headings are not carried into the records), the works numbered 1–345 down the alphabet with four lettered inserts the book prints with a capital letter after the figure (167A, 270A, 270B and 321A), in the single section the book heads ‘CATALOGUE’; this catalogue keeps the price-less form of 1897–1903 for an eighth year: its body has no ‘Owner or Price’ column at all, so no price and no owner is printed for any work, and no record carries a price note or a lender — the absence verified directly, a sweep of the body’s text finding no ‘$’, ‘price’, ‘loaned’, ‘owner’ or ‘for sale’ token anywhere in it — though the notices still state that prices include frames; 16 works are illustrated, each marked in the body itself with a bracketed ‘[Illustration]’ after its title and agreeing exactly with the book’s own List of Illustrations, all sixteen plates bound in, no. 16 serving as the frontispiece, five of their captions printed vertically at the leaf’s right side; three catalogue numbers were restored from their sequence position, each flagged in its record’s note — no. 8, whose printed figure the scan reads as the letter ‘K’, and nos. 98 and 180, whose figures it reads as letterforms; two entries stand transposed in print, Harry Fenn’s no. 91, ‘Mill Street, Warwick’, printed above his no. 90, the records standing in the printed order; the book prints no artist index this year, so no index cross-check was possible — its member lists were cross-checked against the headings’ marks instead; every catalogue page was read against the page images during the parse, and the copy recorded is the Internet Archive’s scan of the Philadelphia Museum of Art’s copy (item 1904AWS), not one of the Frick Library scans. The <i>Catalogue of the Thirty-Eighth Annual Exhibition of the American Water Color Society</i> (10–27 March 1905, National Arts Club, New York): 73 works in a single alphabetical sequence — a much smaller show than the years around it, held at the National Arts Club by courtesy of the Club, the catalogue keeping the alphabetical form of 1902–1904 for a last year: the body arranged by artist under each artist’s heading (the addresses printed beneath the headings are not carried into the records), the works numbered 1–69 down the alphabet with four lettered inserts the book prints (5A, 26A, 66A and 66B — no. 26A, Winslow Homer’s ‘Pulling in the Anchor’, standing at the foot of its page), in the single section the book heads ‘CATALOGUE’, under 47 artists’ headings; this catalogue keeps the price-less form for a ninth year: its body prints no price and no owner for any work, and no record carries a price note or a lender, though the notices still direct buyers to inquire at the desk, payments to be made to the order of James Symington, Treasurer, and state that prices include frames; unlike 1902–1904, no heading carries the Society’s ‘A.W.C.S.’ mark, and no artist string carries it; the book is not illustrated — it prints no plates, no List of Illustrations and no illustration mark against any entry; one catalogue number was restored from its sequence position, no. 33, whose printed figure the scan garbles beyond reading, flagged in its record’s note; the book prints no artist index, so its member rolls were cross-checked against the body instead — all 47 surnames stand in the rolls; every catalogue page was read against the page images during the parse, and the copy recorded is the Internet Archive’s scan of the Metropolitan Museum Library’s copy (item 1905AWS), not one of the Frick Library scans; the Wm. T. Evans Prize was $300, and this book’s winners list, running 1888–1905 complete, records this year’s award itself: W. Granville Smith’s ‘The Bay’, which hangs in this body as no. 63. The <i>Illustrated Catalogue of the Thirty-Ninth Annual Exhibition of the American Water Color Society</i> (3–26 May 1906, American Fine Arts Galleries, New York): 594 works in five galleries — the South, Central, East and West Galleries and the Vanderbilt Gallery, the largest of the five — the galleries and the price element both returning after the alphabetical catalogues of 1902–1905 and the nine price-less years 1897–1905: the works numbered continuously 1–593 in the order hung, under each title a price, a lender line or nothing — 427 works are priced for sale, the price standing in each record’s note (the prices include frames), 75 name a lender and 92 have neither; the dearest work is Horatio Walker’s ‘The First Snow’ (no. 437), priced at $1,200; one number is printed twice — no. 368, Arthur I. Keller’s ‘Illustration, Bret Harte’s “Her Letter”’, stands twice in succession in the West Gallery, the same number, title and price repeated, and both printings are recorded, each flagged in its note; 18 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all eighteen plates are bound in; three catalogue numbers (110, 111 and 584 — the last the book’s own misprint, printed ‘548.’) were restored from their sequence position, each flagged in its record’s note; the artists’ addresses stand only in the book’s artist index, which was cross-checked against the body during the parse; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list runs 1888–1905, its latest line the 1905 award, W. Granville Smith’s ‘The Bay’. The <i>Illustrated Catalogue of the Fortieth Annual Exhibition of the American Water Color Society</i> (2–26 May 1907, American Fine Arts Galleries, New York): 561 works in five galleries — the form of 1906 continuing unchanged: the South, Central, East and West Galleries and the Vanderbilt Gallery, the largest of the five — the works numbered continuously 1–561 in the order hung, under each title a price, a lender line or nothing — 451 works are priced for sale, the price standing in each record’s note (the prices include frames), 44 name a lender and 66 have neither; the dearest work is Alphonse Mucha’s ‘Beatitudes’ (no. 339), priced at $5,000 — the highest price in any of the Society’s catalogues recorded here; one entry stands under two numbers in a single printed line — Will H. Bradley’s ‘Two Decorations’, entered as ‘295. 296.’ and loaned by Collier’s Weekly — and both numbers are recorded, each carrying the entry with a reciprocal note; 9 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record — no. 512, Arthur I. Keller’s ‘The Golden Wedding’, is the frontispiece, and the plate of no. 111, Charles P. Gruppé’s ‘November Evening’, is not bound in this copy, that record resting on the List’s authority alone; one catalogue number (110) was restored from its sequence position, flagged in its record’s note; the artists’ addresses stand only in the book’s artist index, which was cross-checked against the body during the parse; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list runs 1888–1906, its latest line the 1906 award, H. L. Hildebrandt’s ‘Sally’. The <i>Illustrated Catalogue of the Forty-first Annual Exhibition of the American Water Color Society</i> (30 April–24 May 1908, American Fine Arts Galleries, New York): 610 works in three galleries — the five galleries of 1906–1907 shrunk to three, the South, Central and Vanderbilt Galleries, and the printed sub-headings gone altogether — the works numbered continuously 1–610 in the order hung, under each title a price, a lender line or nothing — 507 works are priced for sale, the price standing in each record’s note (the prices include frames), 52 name a lender and 47 have neither, and four entries (Jules Guerin’s nos. 376, 378, 381 and 413) carry ‘Made for the Century Magazine’ in the element’s place; no price in the book reaches $1,000 — the dearest work is Childe Hassam’s ‘The Green Jade Gown’ (no. 508), priced at $850; 9 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all nine plates are bound in this copy — no. 600, Colin Campbell Cooper’s ‘Grande Place, Antwerp’, is the frontispiece; three catalogue numbers were restored from the printed page — no. 11 stands in the book without a printed number at all, flagged in its record’s note, no. 111’s figures reach the scan only as letter debris, and no. 246’s number is glued to its title by a dash; the artists’ addresses stand only in the book’s artist index, which is incomplete in this copy — two of its leaves, carrying the surnames Nicholls to Smith, are wanting — and was cross-checked against the body on its surviving leaves during the parse; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list runs 1888–1907, its latest line the 1907 award, W. H. Drake’s ‘The Lion’s Lair’. The <i>Illustrated Catalogue of the Forty-second Annual Exhibition of the American Water Color Society</i> (29 April–23 May 1909, American Fine Arts Galleries, New York): 598 works in three galleries — the three galleries of 1908 standing again, the South, Central and Vanderbilt Galleries, headed in roman capitals with no printed sub-headings anywhere — the works numbered continuously 1–598 in the order hung, each entry standing on one line, its element on the same line: a price in whole dollars, an ‘Owned by …’ or ‘Courtesy of …’ line, or nothing — 466 works are priced for sale, the price standing in each record’s note (the prices include frames), 54 name a lender and 78 have neither; the dearest work is Clara T. MacChesney’s ‘Still Life’ (no. 57), priced at $1,000 — the book’s only four-figure price; 23 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all 23 plates are bound in this copy — no. 578 is the frontispiece; three catalogue numbers (110, 111 and 519) were restored from the sequence, each flagged in its record’s note; the artists’ addresses stand only in the book’s artist index, which is complete in this copy (Abbatt to Zogbaum) and was cross-checked against the body during the parse, the body governing every disagreement; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list runs 1888–1908, its latest line the 1908 award, Ross Turner’s ‘The Dawn’. The <i>Illustrated Catalogue of the Forty-third Annual Exhibition of the American Water Color Society</i> (28 April–22 May 1910, American Fine Arts Galleries, New York): 556 works in three galleries — the three galleries of 1908–1909 standing again, the South, Central and Vanderbilt Galleries, headed in display capitals with no printed sub-headings anywhere — the works numbered continuously 1–556 in the order hung, each entry standing on one line, its element on the same line: a price in whole dollars, an ‘Owned by …’ or ‘Courtesy of …’ line, or nothing — 455 works are priced for sale, the price standing in each record’s note (the prices include frames), 26 name a lender and 75 have neither; the dearest work is E. Irving Couse’s ‘The Magic Flute’ (no. 526), priced at $1,000 — the book’s only four-figure price; the numbering is the cleanest of the run so far — no gaps, no lettered inserts, no joint entries, no number printed twice and none needing restoration; the artists’ headings are printed in both orders, surname-first and natural order alike; 23 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all 23 plates are bound in this copy; the artists’ addresses stand only in the book’s artist index, which is complete in this copy (Abbatt to Zeigler) and was cross-checked against the body during the parse, the body governing every disagreement; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list runs 1888–1909, its latest line the 1909 award, Edward Dufner’s ‘Reflections’. The <i>Illustrated Catalogue of the Forty-fourth Annual Exhibition of the American Water Color Society</i> (27 April–21 May 1911, American Fine Arts Galleries, New York): 191 works in two galleries — the book shrinks back to two sections only, the South Gallery (nos. 1–109) and the Second Gallery (nos. 110–192), 1910’s Central and Vanderbilt Galleries gone — the works numbered continuously 1–192 in the order hung, each entry standing on one line, its element a price in whole dollars, a ‘Lent by …’ line standing beneath the title, or nothing — 169 works are priced for sale, the price standing in each record’s note (the prices include frames), 9 name a lender — ‘Lent by’ is the book’s only lender form — and 13 have neither; the dearest work is Mary Cassatt’s ‘A Cup of Tea—Pastel’ (no. 102), priced at $1,600; the numbering runs 1–192 with no no. 14 — the sequence passes directly from no. 13 to no. 15, and the book’s own artist index cites a Davies work at 14, the index’s error — with no lettered inserts, no joint entries and no number printed twice; one number (172, Winslow Homer’s ‘Channel Bass, Florida’) was restored from the printed page, flagged in its record’s note; 16 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all sixteen plates are bound in this copy; the artists’ addresses stand only in the book’s artist index, which is complete in this copy (Abbatt to Young) and was cross-checked against the body during the parse, the body governing every disagreement; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list ends with the 1910 award, R. M. Shurtleff’s ‘June’. The <i>Illustrated Catalogue of the Forty-fifth Annual Exhibition of the American Water Color Society</i> (25 April–12 May 1912, American Fine Arts Galleries, New York): 272 works in two galleries — the exhibition grows again after 1911’s small hang, the First Gallery (nos. 1–130) and the Second Gallery (nos. 131–272) — the works numbered continuously 1–272 in the order hung, each entry standing on one line, its element a price in whole dollars, an ‘Owned by …’ line standing beneath the title, or nothing — 244 works are priced for sale, the price standing in each record’s note (the prices include frames), 9 name a lender — ‘Owned by’ is the book’s only lender form — and 19 have neither; the dearest works are two at $1,000 — F. Hopkinson Smith’s ‘The Rug Market’ (no. 59) and Leonard Ochtman’s ‘The Brook in the Winter’ (no. 166); the numbering runs 1–272 complete — the cleanest of the 1906–1912 volumes — with no number restored, none printed twice, no lettered inserts, no joint entries and no absent numbers; 8 works are illustrated, named by the book’s List of Illustrations (the body prints no illustration marks), each flagged in its record, and all eight plates are bound in this copy; the artists’ addresses stand only in the book’s artist index, which is complete in this copy (Abbatt to Wigand) and was cross-checked against the body during the parse, the body governing every disagreement; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300, and the book’s winners list ends with the 1911 award, Charles H. Woodbury’s ‘Evening’. The <i>Catalogue of the Forty-sixth Annual Exhibition of the American Water Color Society</i> (3–15 March 1913, Galleries of M. Knoedler & Co., New York): 143 works in a single alphabetical sequence — the exhibition leaves the American Fine Arts Galleries for Knoedler’s and shrinks sharply, the works arranged alphabetically by artist (as in 1902) under 108 surname-first headings; the book prints no price, lender or any other element for any entry — no price column and no ‘Owned by’, ‘Lent by’ or ‘Courtesy of’ lines — so all 143 records stand with neither price nor lender; the book is not styled ‘Illustrated’ and prints no plates and no List of Illustrations; the numbering runs 1–143 complete, with five numbers restored from the sequence, each flagged in its record — three garbled in the scan’s text layer (nos. 11, 110 and 111) and two misprinted by the book itself, no. 87 printed ‘7.’ and no. 137 printed ‘17.’; every catalogue page was read against the page images during the parse; the Wm. T. Evans Prize was $300 — its last year, the prize being discontinued after 1913 — and the book’s winners list ends with the 1912 award, Childe Hassam’s ‘The Minuet’. The <i>Catalogue of the Forty-seventh Annual Exhibition of the American Water Color Society</i> (16–28 February 1914, Galleries of M. Knoedler & Co., New York): 113 works in a single alphabetical sequence — the works arranged alphabetically by artist under 89 surname-first headings; the book prints no prices anywhere — no price column, no price lines and no sale marks — but the element stands in one form, an ‘Owned by’ line beneath the title on seven records (no. 35’s owner printed in quotation marks, ‘The Delineator’); the book is illustrated, its List of Illustrations naming eight works (nos. 4, 20, 21, 65, 71, 88, 91 and 94), all eight plates bound in, every List entry agreeing with its plate caption and with the body entry of that number; the numbering runs 1–112 complete with one lettered insert standing as printed, no. 55A (G. Glenn Newell’s ‘A Bleak Day in the Pasture’, between nos. 55 and 56), and one number restored from the sequence, no. 111, flagged in its record; every catalogue page was read against the page images during the parse; this is the hinge year for the Society’s prizes — the prize page announces the new Hudnut Prize of $200, Alexander M. Hudnut’s prize for the most meritorious water colour in the exhibition (no winner is named in this book; the 1915 catalogue records the 1914 award, Edward H. Potthast’s ‘A Holiday’, no. 71 here), and prints the Evans Prize winners 1888–1913, ending with Arthur Schneider’s ‘A Morning Walk’, with the words ‘This Prize has been discontinued.’ The <i>Catalogue of the Forty-eighth Annual Exhibition of the American Water Color Society</i> (4–25 February 1915, Galleries of the National Arts Club, New York): 267 works in a single alphabetical sequence — the works arranged alphabetically by artist under 150 surname-first headings, the exhibition leaving Knoedler’s for the National Arts Club; the book prints no prices anywhere — no price column, no price lines, no sale marks and no notices page — but the element stands in one form, an ‘Owned by’ line beneath the title on five records (nos. 4, 84, 89, 222 and 261); the book is illustrated, its List of Illustrations naming ten works (nos. 13, 67, 75, 160, 172, 179, 190, 192, 197 and 267), all ten plates bound in, each matched to its body entry on artist and title — no. 267’s plate caption misprints the title as ‘Landscape in Blue and Cold’, the body and the List reading ‘Gold’; the numbering runs 1–267 complete and clean — no number restored, duplicated, lettered or absent, the cleanest numbering since 1912 — though two headings stand out of alphabetical order in print, Aylward (no. 4) after Arms and De Haas (no. 95) between Gruppe and Hartman; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913, ending with Arthur Schneider’s ‘A Morning Walk’, with the words ‘This Prize has been discontinued’, and announces the Hudnut Prize of $200, recording its first award, in 1914, to Edward H. Potthast for ‘A Holiday’. The <i>Catalogue of the Forty-ninth Annual Exhibition of the American Water Color Society</i> (3–27 February 1916, Galleries of the National Arts Club, New York): 358 works in a single alphabetical sequence — the works arranged alphabetically by artist under 175 headings, now printed in natural order, given names first, the exhibition staying at the National Arts Club; prices are back, absent in 1913 and 1915 — 328 works are priced for sale, the price standing in each record’s note, the dearest F. Hopkinson Smith’s ‘Rio Fontega, Venice’ (no. 297) at $1,000, the book’s only four-figure price — and the element stands otherwise in one form, an ‘Owned by’ line beneath the title on four records (nos. 19, 70, 174 and 232); the book is illustrated, its List of Illustrations naming eleven works (nos. 38, 73, 76, 86, 88, 249, 257, 269, 271, 326 and 328), ten plates bound in and the eleventh, no. 73, standing on the catalogue’s own printed cover, which survives inside the binding; the numbering runs 1–352 with six lettered inserts (90a, 116a, 178a, 233a, 233b and 233c), and six numbers are restored from the sequence, each flagged in its record’s note — nos. 86, 88, 89 and 98 dropped entire by the scan’s text layer, no. 158 read as letter debris, and no. 177 printed without a number at all; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at two awards — in 1914, to Edward H. Potthast for ‘A Holiday’, and in 1915, to Hilda Belcher for ‘Winifred Hunt’. The <i>Catalogue of the Fiftieth Annual Exhibition of the American Water Color Society</i> (1–24 February 1917, Galleries of the National Arts Club, New York): 330 works in a single alphabetical sequence — the works arranged alphabetically by artist under 189 headings, the headings returning to surname-first order after 1916’s natural order, the exhibition staying at the National Arts Club; prices stand at the end of each entry line — 293 works are priced for sale, the price standing in each record’s note, the dearest Horatio Walker’s ‘Swine and Swineherd’ (no. 314) at $2,000, three four-figure prices in all — and a lender is named on fourteen records, in two forms: an ‘Owned by’ line beneath the title (nos. 127 and 128) and a parenthetical ‘(owned by …)’ credit (nos. 14, 25, 100, 103, 167, 180, 190, 191, 230, 277, 292 and 295); the book is illustrated, its List of Illustrations naming nine works — eight matched to body entries (nos. 11, 68, 90, 96, 127, 142, 260 and 300) and Albert Sterner’s ‘Nude in Studio’, which has no entry in the body at all — nine plates bound in, no. 127 standing as the frontispiece; the numbering runs 1–327 with two lettered inserts (24a and 108a) and one entry printed without a number — Grace H. Fletcher’s ‘A Winter Morn in Venice’, between nos. 101 and 102, recorded with its number empty, no number being supplied; the book misprints Kleen’s ‘Tic-Tac’ as ‘150.’, duplicating Klaw’s genuine 150, and the record stands under 153, restored from the sequence, three further numbers (1, 15 and 47) being likewise restored, each flagged in its record’s note; one record (no. 170) prints a rule in place of a title; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at three awards — in 1914, to Edward H. Potthast for ‘A Holiday’, in 1915, to Hilda Belcher for ‘Winifred Hunt’, and in 1916, to W. Granville-Smith for ‘Old Philadelphia’. The <i>Catalogue of the Fifty-First Annual Exhibition of the American Water Color Society</i> (7 February–1 March 1918, Galleries of the National Arts Club, New York): 309 works in a single alphabetical sequence — the works arranged alphabetically by artist under 171 headings, the headings surname-first as in 1917, the exhibition staying at the National Arts Club; prices stand at the end of each entry line — 294 works are priced for sale, the price standing in each record’s note, the dearest Edward Dufner’s ‘Summer Evening’ (no. 71) at $800, itself one of the eight illustrated works, four records standing at $600 or more — and a lender is named on four records, in one form only: a parenthetical ‘(Owned by …)’ credit appended to the title line (nos. 9, 29, 272 and 300); the book is illustrated, its List of Illustrations naming eight works, all eight matched to body entries (nos. 31, 50, 52, 71, 98, 151, 228 and 245) and eight plates bound in, with no frontispiece and no unmatched plate; the numbering runs 1–310 with one absence — no. 118 is not printed, the sequence passing from Hartman’s no. 117 directly to Hasler’s no. 119 — and no lettered inserts, no duplicated numbers and nothing restored; two records (nos. 82 and 84) print a rule in place of a title, and eleven records stand with no element at all; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at four awards — in 1914, to Edward H. Potthast for ‘A Holiday’, in 1915, to Hilda Belcher for ‘Winifred Hunt’, in 1916, to W. Granville-Smith for ‘Old Philadelphia’, and in 1917, to Sidney Dale Shaw for ‘Snowy Roofs’. The <i>Catalogue of the Fifty-Second Annual Exhibition of the American Water Color Society</i> (6–28 February 1919, Galleries of the National Arts Club, New York): 360 works in a single alphabetical sequence — the works arranged alphabetically by artist under 184 headings, the headings surname-first as in 1917 and 1918, the exhibition staying at the National Arts Club; prices stand at the end of each entry line — 326 works are priced for sale, the price standing in each record’s note, the dearest Childe Hassam’s six pictures (nos. 146–151) at $1,500 each, eight records standing at $1,000 or more — and a lender is named on two records, in one form only: a ‘, owner …’ credit appended to the title line (nos. 301 and 312); the book is illustrated — eight plates are bound in, all eight matched to body entries (nos. 5, 15, 126, 149, 206, 232, 261 and 280), the book printing no List of Illustrations this year, so the plates are identified from their captions, with no frontispiece and no unmatched plate; the numbering runs 1–359 with one lettered insert, no. 111a, and no absences, no duplicated numbers and nothing restored; one record (no. 310) prints a rule in place of a title, and thirty-two records stand with no element at all; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at five awards — in 1914, to Edward H. Potthast for ‘A Holiday’, in 1915, to Hilda Belcher for ‘Winifred Hunt’, in 1916, to W. Granville-Smith for ‘Old Philadelphia’, in 1917, to Sidney Dale Shaw for ‘Snowy Roofs’, and in 1918, to Hilda Belcher for ‘The Bouncing Baby’. The <i>Catalogue of the Fifty-Third Annual Exhibition of the American Water Color Society</i> (5–27 February 1920, Galleries of the National Arts Club, New York): 326 works in a single alphabetical sequence — the works arranged alphabetically by artist under 165 headings, the headings surname-first as in 1917, 1918 and 1919, the exhibition staying at the National Arts Club; the book prints no artist index, its back matter being the lists of members only; prices stand at the end of each entry line — 294 works are priced for sale, the price standing in each record’s note, the dearest John S. Eland’s ‘Hail! Mary’ (no. 87) at $3,500, fifteen records standing at $1,000 or more — and a lender is named on one record only, in one form: a ‘, owner …’ credit appended to the title line (no. 272, owner Mrs. Robert De Forest); one price (no. 78c) is printed without its dollar sign, and one (no. 291) is misprinted by the book itself as ‘$2.000.’; the book is illustrated — its List of Illustrations names eight works and eight plates are bound in, seven matched to body entries (nos. 22, 40, 50, 97, 136, 243 and 275), the eighth, Charles W. Hawthorne’s ‘Interior’, standing in frontispiece position and matching no body entry, three captions differing from their body titles; the numbering runs 1–315 with eleven lettered inserts (78a–78f, 188a–188d and 274a), and no absences, no duplicated numbers and nothing restored; one heading line is a cross-reference only — ‘DE HAAS, ALICT TUCKER PREBLE,’ the book misprinting Alice as Alict, ‘(See Nos. 109-110.)’ — and creates no records; every catalogue page was read against the page images during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at six awards — in 1914, to Edward H. Potthast for ‘A Holiday’, in 1915, to Hilda Belcher for ‘Winifred Hunt’, in 1916, to W. Granville-Smith for ‘Old Philadelphia’, in 1917, to Sidney Dale Shaw for ‘Snowy Roofs’, in 1918, to Hilda Belcher for ‘The Bouncing Baby’, and in 1919, to Childe Hassam for ‘Mount Beacon—From Broadway, Newburgh’ — the book naming no winner for the 1920 exhibition itself, Horatio Walker’s award for it being first printed in the 1921 volume. The <i>Catalogue of the Fifty-Fourth Annual Exhibition of the American Water Color Society</i> (3–24 February 1921, Galleries of the National Arts Club, New York): 257 works in a single sequence — the book changes its format this year: the entries are no longer grouped under artist headings in an alphabetical run but stand in hanging order, each a title line with the price at its end and the artist’s name, given-name-first, on the line beneath, the works standing under 160 artists’ names as printed, the exhibition staying at the National Arts Club; unlike the 1920 book, this book has an index of exhibitors citing catalogue numbers, and every citation was checked against the body — the body governs in the six places where the two conflict, among them no. 168, which the body prints under John F. Lane and the index cites under Carlson; prices stand at the end of the title line, printed with cents — 236 works are priced for sale, the price standing in each record’s note, the dearest Francis McComas’s ‘Storm Clouds’ (no. 79) and ‘Arizona Cliffs’ (no. 81) at $2,000 each, seven records standing at $1,000 or more — and no lender, no medium and no size is printed anywhere in the book, so Lender, Medium and Size stand empty throughout; two prices (nos. 76 and 123) are printed without their dollar signs; the book is illustrated — its List of Illustrations names seven works and seven plates are bound in, six matched to body entries (nos. 72, 94, 100, 167, 176 and 221), three of them under captions differing from the body titles, the seventh, Francis McComas’s ‘Hopi Adobes’, matching no body entry; the numbering runs 1–256 with one lettered insert, 120A (Evelyn Cohen’s second ‘A Swiss Interior’), complete, with no absences and no duplicated numbers; the scan’s text layer is much poorer than 1920’s — whole lines drop out, and the hundreds digits 3 and 5 are confusable in both directions — so every price, and every doubtful artist or title reading, was settled on the printed page during the parse; the prize page prints the Evans Prize winners 1888–1913 with the words ‘This Prize has been discontinued’, and records the Hudnut Prize of $200 now standing at seven awards — in 1914, to Edward H. Potthast for ‘A Holiday’, in 1915, to Hilda Belcher for ‘Winifred Hunt’, in 1916, to W. Granville-Smith for ‘Old Philadelphia’, in 1917, to Sidney Dale Shaw for ‘Snowy Roofs’, in 1918, to Hilda Belcher for ‘The Bouncing Baby’, in 1919, to Childe Hassam for ‘Mount Beacon—From Broadway, Newburgh’, and in 1920, to Horatio Walker for ‘Pastoral—Sow and Pigs’, Walker’s award being first printed in this book — the book naming no winner for the 1921 exhibition itself. The <i>Combined Annual Exhibition of the American Water Color Society and the New York Water Color Club</i> (22 December 1922–9 January 1923, American Fine Arts Building, New York): 609 works in four galleries — the two societies exhibiting together, the book’s title page printing no ordinal and no annual number for either society (its foreword calls the previous year’s show the ‘First Combined Exhibition’, so this is the second combined exhibition by inference), and the works hung and listed by gallery under one continuous numbering — South Gallery (nos. 1–167), Centre Gallery (nos. 168–372), Vanderbilt Gallery (nos. 373–565) and Sculpture (nos. 566–609), the Sculpture section selected by the National Sculpture Society by invitation of the Exhibition Committee; each entry gives the title, the artist in natural order and the price in whole dollars or a printed dash — 550 works are priced for sale, the price standing in each record’s note, the printed dash standing on 56 and three Sculpture entries (nos. 586, 588 and 589) printing ‘On application’, the dearest Max. Wieczorek’s ‘Ruth St. Denis’ (no. 420) at $3,500 — and no lender, no medium and no size is printed anywhere in the book, so Lender, Medium and Size stand empty throughout; the book is illustrated — fifteen plates stand on twelve leaves, there is no List of Illustrations, fourteen plates match body entries (nos. 2, 32, 37, 40, 50, 66, 96, 221, 381, 404, 439, 478, 538 and 548), six of them under captions differing from the body titles, and the frontispiece, Hilda Belcher’s portrait plate, is captioned with the artist’s name only and matches no single entry; the numbering runs 1–609 complete, with no lettered inserts, no absences and no duplicated numbers, one number being the book’s own misprint — the entry between 279 and 281 (Egbert Cadmus, ‘Jagged Rocks, Maine’) is printed ‘200’ and stands restored at 280, corroborated by the book’s own Index of Contributors, which cites Cadmus at 277, 278, 280 and 281 — and one entry (no. 511, Joseph Rayner) is printed with no title at all; the index contains no entry for any Sculpture artist, and its disagreements with the body are the book’s, the body governing in every case; the scan’s text layer drops the entire price column on one body page (the prices of nos. 215–265 are image-only) and the artist’s name on 27 entries on another, so every doubtful reading was settled on the printed page during the parse, every body page being verified record by record against its render; both societies’ prize pages are printed and neither names a winner for this exhibition — the AWS page records the Hudnut Prize of $200 now standing at eight awards, adding Francis McComas’s 1921 award for ‘The Storm Cloud’, first printed in this book, and prints the Evans Prize winners 1889–1913 with the words ‘This Prize has been discontinued’, while the Club’s page prints its Beal Prize of $200 (awards 1904–1911) and its own Hudnut Prize of $100 (awards 1916–1919). The <i>Descriptive Catalogue of the Loan Collection of Pictures</i> (28 March–30 June 1892, catalogued by A. G. Temple): 180 works in three rooms — the scan is rough and its ‘Lent by’ lines are the worst-read part of it, so 167 of the 180 lenders have been supplied from the catalogue’s own Index of Contributors, each flagged in its record’s note, and two lenders could not be recovered at all; Graves’s <i>Century of Loan Exhibitions</i> digests this exhibition but covers only 154 of its 180 works — the printed catalogue is the authority here. The <i>Descriptive Catalogue of the Loan Collection of Pictures</i> (2 April–30 June 1894, prepared by A. G. Temple): 154 works in three galleries — two lenders were supplied from the catalogue’s own Index of Contributors, each flagged, and two could not be recovered at all; Graves’s <i>Century of Loan Exhibitions</i> digests this exhibition but covers only 143 of its 154 works — the printed catalogue is the authority here. The <i>Catalogue of the Loan Collection of Pictures</i> (23 April–21 July 1895, prepared by A. G. Temple): 138 works in three galleries — this scan’s OCR drops most of the printed catalogue numbers, so 71 have been restored from their sequence position, each flagged in its record’s note and corroborated by the catalogue’s Index of Artists; Graves’s <i>Century of Loan Exhibitions</i> digests this exhibition and omits no work outright, but keys only 127 of its 138 numbers correctly, merging or misnumbering the rest — the printed catalogue is the authority here. The <i>Catalogue of the Loan Collection of Pictures</i> (7 April–14 July 1897, by painters of the British School, prepared by A. G. Temple): 167 works in three galleries — this scan drops the printed margin numbers wholesale, so 73 have been restored from their sequence position, each flagged in its record’s note and corroborated by the catalogue’s Index of Artists; Graves’s <i>Century of Loan Exhibitions</i> digests this exhibition but keys only 139 of its 167 works, folding several pictures into merged records and missing the lettered inserts — the printed catalogue is the authority here. The <i>Catalogue of the Loan Collection of Pictures by Painters of the French School</i> (6 June–31 August 1898, prepared by A. G. Temple): 156 works in three galleries — this copy of the catalogue is the pre-opening issue, marked ‘UNDER REVISION’ on its cover, and the records are taken from that text; 46 catalogue numbers have been restored from their sequence position, each flagged in its record’s note; Graves’s <i>Century of Loan Exhibitions</i> covers 143 of these 156 works in substance — the printed catalogue is the authority here. The <i>Catalogue of the Loan Collection of Pictures and Drawings by J. M. W. Turner, R.A.</i> (11 April–11 July 1899, prepared by A. G. Temple): 195 works in three galleries — a single-artist loan exhibition of Turner, with a selection of pictures by some of his contemporaries; nos. 66–69 do not exist in the printed catalogue — a gap in the Liber Studiorum list, which passes from 65 to 70; Graves’s <i>Century of Loan Exhibitions</i> keys only 119 of these 195 works, omitting the Liber Studiorum impressions and folding whole runs into unnumbered digests — the printed catalogue is the authority here. The <i>Descriptive and Biographical Catalogue of the Exhibition of the Works of Spanish Painters</i> (30 April–31 July 1901, prepared by A. G. Temple): 209 works in four galleries — a single-nation exhibition of Spanish painting, its third gallery given over entirely to Velasquez. This copy of the catalogue is the pre-opening issue, marked ‘Under revision’ on its cover, and the records are taken from that text; Graves’s <i>Century of Loan Exhibitions</i> mixes this exhibition with another Guildhall show of 1901, and covers 200 of its 209 works in substance — the printed catalogue is the authority here. The <i>Catalogue of the Exhibition of a Selection of Works by French and English Painters of the Eighteenth Century</i> (22 April–26 July 1902, prepared by A. G. Temple): 153 works in four galleries — a selection of French and English painting of the eighteenth century; Graves’s <i>Century of Loan Exhibitions</i> keys 124 of its 153 numbers and covers 136 in substance, folding eleven Gainsboroughs into one digest record and missing all seven Lancrets — the printed catalogue is the authority here. The <i>Catalogue of the Exhibition of a Selection of Works by Early and Modern Painters of the Dutch School</i> (28 April–25 July 1903, prepared by A. G. Temple): 196 works in Galleries II, III and IV — the twelfth exhibition of the Guildhall series; Gallery I held the Gassiot bequest as part of the exhibition, but the catalogue prints no list of it, so those works are not recorded here; eight catalogue numbers have been restored from their sequence position, each flagged in its record’s note; Graves’s <i>Century of Loan Exhibitions</i> keys 144 of these 196 numbers and covers 158 in substance, lacking 38 outright — the printed catalogue is the authority here. The <i>Catalogue of the Exhibition of Works by Irish Painters</i> (31 May–23 July 1904, organised by Hugh P. Lane): 466 works in four galleries. Catalogue no. 258 does not exist in the printed catalogue — a gap in the original numbering; 27 numbers illegible in the scan were restored from their sequence position and are flagged in each record’s note; entries that print no size, medium or lender show none — nothing has been inferred. The text carries the scans’ ordinary OCR noise. The <i>Catalogue of the Exhibition of Works by Flemish and Modern Belgian Painters</i> (3 May–28 July 1906, prepared by A. G. Temple): 221 works in four galleries — the fourteenth exhibition of the Guildhall series; this copy of the catalogue is the pre-opening issue, marked ‘UNDER REVISION’ on its cover, and the records stand as that text prints them; twenty-seven catalogue numbers have been restored from their sequence position, each flagged in its record’s note; no lender has been taken from the book’s indexes; Graves’s <i>Century of Loan Exhibitions</i> keys 191 of these 221 numbers and, counting his unnumbered records, covers 194 in substance, lacking 27 outright — the printed catalogue is the authority here. The <i>Catalogue du Salon de la Rose+Croix : Geste esthétique</i> (10 March–10 April 1892, Galeries Durand-Ruel, Paris, by Joséphin Péladan): 53 works in a single unnumbered list headed ‘Dessins’ — the first salon; the illustrated catalogue prints no catalogue numbers, the book’s own note says many drawings sent in late could not be included, two entries print no title, and the records are parsed from Gallica’s OCR text of the Bibliothèque nationale de France digitisation, not from page images, so names and titles carry that text’s noise, with readings that had to be interpreted flagged in the individual records. The <i>Catalogue officiel illustré du second Salon de la Rose+Croix (IIe Geste esthétique)</i> (28 March–30 April 1893, Palais du Champ-de-Mars, Paris, by Joséphin Péladan): 270 works in a single numbered sequence — from John Finnegan’s compilation of the printed catalogue, not a scan parse; the numbers run to 275, but nos. 249–253 do not appear in the compilation. The <i>Catalogue du Salon de la Rose+Croix (IIIe Geste esthétique)</i> (May 1894, Galerie des Artistes Contemporains, rue de la Paix, Paris, by Joséphin Péladan): 84 works — the small room limited the hang to 83 works, plus the inserted 73A. The <i>Catalogue du Salon de la Rose+Croix (IVe Geste esthétique)</i> (20 March–20 April 1895, Galerie des Artistes Contemporains, rue de la Paix, Paris, by Joséphin Péladan): 109 works — the numbering is the catalogue’s own tangle: two notices for Louis Hawkins state in terms that the catalogue gives neither number nor title, three entries stand under no. 48, and no. 99 is shared by two works. The <i>Salon de la Rose+Croix (Ve Geste esthétique)</i> (20 March–20 April 1896, Galerie des Arts Réunis, avenue de l’Opéra, Paris, by Joséphin Péladan): 110 works, the numbering complete 1–110. The <i>VIe Geste esthétique — Sixième Salon de la Rose+Croix</i> (5–31 March 1897, Galerie Georges Petit, Paris, by Joséphin Péladan): 217 works, the numbering complete 1–217 — the sixth and last salon. For the five later Rose+Croix salons (1893–1897) the records stand exactly as compiled; titles are as catalogued, with the medium often in parentheses within the title; those salons print no sizes and no lenders; and each artist’s address, as the catalogue prints it, is carried in the record’s note. A search across all recorded exhibitions (by artist, by title, or by lender) sits above the list of exhibitions, and each artist name links to the usual name search. On the Record pages, names and titles are shown in standard capitalisation for readability; the underlying records stand exactly as printed in each catalogue. More catalogues will be added one at a time, as their scans surface.</li>
        <li><b>Six Degrees</b> — the shortest chain between any two artists, up to six steps, through links Wikidata records: <i>student</i> (P802, taught), <i>student of</i> (P1066, taught by) and <i>influenced by</i> (P737, in both directions). The search is a breadth-first search over those links only, one batched query per step, with each link labeled by its direction; neighbors are verified to be people, so groups, schools and works never appear as a link. If no chain is recorded within six steps the page says so, with the number of artists explored — a missing chain means no chain is recorded, not that no connection existed.</li>
        <li><b>Catalogue raisonné</b> — the standard catalogue raisonné of the artist’s works, where one exists, drawn from Open Library and Wikidata and shown in chronological order, including catalogues later superseded by newer ones; where a standard catalogue is published under another title it is listed from a short curated set.</li>
        <li><b>References</b> — every source is captured as a Chicago-style citation, grouped as biographical, exhibitions, academic, lifetime, market and database/authority records. <span class="tag-life">LIFETIME</span> marks sources dated within the artist’s life, drawn from historic dictionaries, the Internet Archive, the Library of Congress’s Chronicling America newspapers, Europeana and Open Library.</li>
      </ul>
      <h3>3 · Optional AI synthesis</h3>
      <p>If the server operator configures an API key, a narrative synthesis can be generated <i>only</i> from the sources collected for the report, with numbered citations and explicit gaps.</p>
      <h3>Limitations</h3>
      <p>Open data is uneven: famous artists are richly documented, lesser-known ones may have few records. Name-based searches (academic literature, period sources) can include namesakes for common names — check each item. Always verify against the cited original.</p>
      <h3>Privacy &amp; analytics</h3>
      <p>The Atlas is free to use. It has no accounts, no sign-in and no payments, and it does not ask for or store your name, email address or any personal information. To understand how the site is used, visits are counted by two analytics services. <b>GoatCounter</b> counts page views without cookies and without tracking you across sites. <b>Google Analytics</b> uses cookies to measure visits, the pages viewed and approximate location (country and region). Google Signals is enabled: if you are signed in to a Google account when you visit, Google may associate the visit with that account in order to give this site aggregated, anonymous statistics — the age ranges, genders and interests of its readers as a group — and to count a reader who uses more than one device as one person. No individual reader is identified to us, and nothing recorded here is used to contact you. Questions about this note: <a href="mailto:john@sterlingfineart.com">john@sterlingfineart.com</a>.</p>
    </section>`;
  }

  fetch('/api/config').then((r) => r.json()).then((c) => (config = c)).catch(() => {}).finally(route);
})();
