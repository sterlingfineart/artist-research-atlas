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
  async function viewBrowse(p) {
    app.innerHTML = `<h1 style="font-size:38px">Browse artists</h1>
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Browse by century, country, movement or medium — pick any combination and press GO. Every list is a live query of Wikidata, restricted to painters, sculptors, draftsmen, engravers and printmakers — select an artist to generate the full research report.</p>
      <div id="browse-facets">${spinner('Loading browse lists…')}</div>
      <div id="browse-results"></div>
      <section class="rs" id="browse-index"></section>`;
    renderShowcaseIndex();
    let defs;
    try {
      defs = await api('/api/browse', {});
    } catch (e) {
      $('#browse-facets').innerHTML = `<div class="notice error">Browse lists could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    if (defs?.facets) {
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
      <div class="notice">About these records — transcribed from the printed Salon livrets (Garland reprints, via the Internet Archive) and parsed from OCR, so some titles carry OCR noise and a few artist names are fragments. Artist names have been corrected where the OCR misread them, against authority records (Wikidata artist lists and the frequent clean spellings in the livrets themselves); only high-confidence corrections are applied, ambiguous names are left as printed, and the original printed spellings are preserved in the data files. A “~” after a catalogue number means the number was inferred from the sequence or looks suspect in the printed text. Every artist name links to the Atlas name search — pick the right person there to read the full research report. No images yet: most Salon works have no surviving image in the open sources, so this first version is the catalogue itself, browsable year by year.</div>`;
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
      <p class="lede" style="text-align:left;margin:0 0 20px;max-width:900px">Step into any Paris Salon, 1673–1881, as it was catalogued: every work, every exhibitor, in the sections the livret itself used. Pick a year — or walk year by year — and every artist name opens the Atlas name search, so a Salon exhibitor leads straight to the full research report.</p>
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
      <div id="ra-year"></div>`;
    let idx;
    try {
      idx = await loadRAIndex();
    } catch (e) {
      $('#ra-controls').innerHTML = `<div class="notice error">The Royal Academy catalogue could not be loaded: ${esc(e.message)}</div>`;
      return;
    }
    renderRAControls(idx, year);
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

  /* ========================================================== report view */
  const SECTIONS = [
    ['synthesis', 'Research synthesis (AI)'],
    ['identity', 'Identity & names'],
    ['biography', 'Biography'],
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
        <li><b>Bibliography & scholarship</b> — key books and monographs with the artist as subject (Open Library, ranked by number of editions), curated scholarship with the artist as main subject (Wikidata), the most-cited literature in OpenAlex (250M+ scholarly works) and Crossref, reviews, and chronologically arranged quotations from contemporaries, fellow artists and critics (Wikiquote). Start with the "Start here" shelf; the whole bibliography downloads as BibTeX or RIS for Zotero.</li>
        <li><b>Critical analyses</b> — encyclopaedic discussion of style, technique, reception and legacy, and arguments drawn from leading scholarship.</li>
        <li><b>Auction & art sales</b> — documented prices, sales and ownership events, provenance chains published by museums, the artist’s pages on Artnet, Artsy, MutualArt, Invaluable and others, and pre-filled searches of auction archives. Full auction records are in subscription databases and are linked rather than reproduced.</li>
        <li><b>Works & collections — linking to the holding institution</b> — a work's title links to the holding museum's own object page wherever one exists and can be verified; Wikidata is the finding aid, never the authority. How a link is resolved: the work list comes from Wikidata (a SPARQL query for works with the artist as creator, <i>wdt:P170</i>), together with the museum identifiers recorded there — the <i>Met object ID</i> (property P3634) and the <i>Art Institute of Chicago artwork ID</i> (property P4610). Each identifier is checked against the institution's own open API — the Met Collection API (<code>collectionapi.metmuseum.org/public/collection/v1/objects/{id}</code>), which returns the museum's canonical object page (<code>objectURL</code>), and the Art Institute of Chicago API (<code>api.artic.edu/api/v1/artworks/{id}</code>), whose public page is <code>artic.edu/artworks/{id}</code>. Only an identifier the institution's API confirms becomes the work's link; if it does not resolve, the work links to its Wikidata item page instead. Museum open-access records are fetched directly from the same APIs — the Met, the Art Institute of Chicago, and the Cleveland Museum of Art's open-access API (<code>openaccess-api.clevelandart.org</code>), which returns each object's own page URL with the record — and Europeana records link to the Europeana item page. Where no institutional page exists, the work links to its Wikidata page, shown plainly as such and never presented as a museum source. Direct automated checks of museum web pages are not reliable (their servers reject them), which is why verification runs through the institutions' open APIs.</li>
        <li><b>Browse</b> — the browse page lists artists by century (12th–20th), country, movement or medium, and any combination of the four: pick from the dropdowns and press GO. The country list is every country with eligible artists (a live count of citizenships, including the historical states grouped under the modern country — Rembrandt and Vermeer are recorded as citizens of the Dutch Republic, Leonardo of the Republic of Florence — so the Dutch masters and the Italian Renaissance appear where they belong; states that map to no modern country appear under their own name). Each list is a live Wikidata query restricted to painters, sculptors, draftsmen, engravers and printmakers, capped at 50 artists, best-documented first — plus a curated index of the twenty homepage artists grouped the same way. As everywhere on the site, Wikidata is the finding aid: it finds the artist, and the report then links each work to the holding institution's verified page.</li>
        <li><b>Salon Time Machine</b> — the Paris Salon catalogues, 1673–1881: 144,081 works by year, section and catalogue number, transcribed from the printed livrets (Garland reprints via the Internet Archive) and parsed from OCR. Catalogue numbers marked ~ were inferred from the sequence or look suspect in the printed text; some titles carry OCR noise and a few artist names are fragments. Years with no surviving livret are simply absent. Each artist name links to the usual name search, so a Salon exhibitor leads straight to the full research report. No images in this first version: most Salon works have no surviving image in the open sources.</li>
        <li><b>Royal Academy Time Machine</b> — the Royal Academy Summer Exhibition catalogues, 1769–1905: 161,019 works by year, occupation and catalogue number, compiled from Algernon Graves’s <i>The Royal Academy of Arts: A Complete Dictionary of Contributors and Their Work</i> (1905–06), with the 1905 exhibition recovered from the Paul Mellon Centre’s RA Chronicle catalogue transcription, and parsed from OCR. Names, addresses and titles are as printed, with the OCR noise of the source scans. Catalogue numbers marked ~ are uncertain in the source; about 12,200 records have no readable catalogue number and show —, and no number has been invented for them. A further 1,543 records in the full database, whose year could not be resolved, are not in this browser. Each artist name links to the usual name search, so an exhibitor leads straight to the full research report. No images in this first version.</li>
        <li><b>Six Degrees</b> — the shortest chain between any two artists, up to six steps, through links Wikidata records: <i>student</i> (P802, taught), <i>student of</i> (P1066, taught by) and <i>influenced by</i> (P737, in both directions). The search is a breadth-first search over those links only, one batched query per step, with each link labeled by its direction; neighbors are verified to be people, so groups, schools and works never appear as a link. If no chain is recorded within six steps the page says so, with the number of artists explored — a missing chain means no chain is recorded, not that no connection existed.</li>
        <li><b>Catalogue raisonné</b> — the standard catalogue raisonné of the artist’s works, where one exists, drawn from Open Library and Wikidata and shown in chronological order, including catalogues later superseded by newer ones; where a standard catalogue is published under another title it is listed from a short curated set.</li>
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
