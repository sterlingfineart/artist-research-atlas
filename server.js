'use strict';
/* Artist Research Atlas — zero-dependency Node.js server (Node 18+). */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { search } = require('./lib/search');
const { browse, warmCountryFacets, warmBrowseCache } = require('./lib/browse');
const { degrees } = require('./lib/degrees');
const report = require('./lib/report');
const ai = require('./lib/ai');

const PORT = parseInt(process.env.PORT || '3000', 10);
const PUBLIC = path.join(__dirname, 'public');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.json': 'application/json' };

function send(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(body);
}

const QID = /^Q\d+$/;
const ULAN = /^\d{9}$/;
function params(url) {
  const p = Object.fromEntries(url.searchParams);
  const out = {
    wd: QID.test(p.wd || '') ? p.wd : null,
    ulan: ULAN.test(p.ulan || '') ? p.ulan : null,
    name: (p.name || '').slice(0, 150),
    by: p.by && /^-?\d{1,4}$/.test(p.by) ? p.by : null,
    dy: p.dy && /^-?\d{1,4}$/.test(p.dy) ? p.dy : null,
    variants: (p.variants || '').split('|').map((s) => s.trim()).filter(Boolean).slice(0, 8),
  };
  return out;
}

// simple per-IP rate limiting for API routes
const hits = new Map();
function limited(ip) {
  const now = Date.now();
  const h = (hits.get(ip) || []).filter((t) => now - t < 60000);
  h.push(now);
  hits.set(ip, h);
  return h.length > 120;
}

const routes = {
  '/api/health': async () => ({ ok: true }),
  '/api/config': async () => ({ ai: ai.enabled(), aiModel: ai.enabled() ? ai.model : null }),
  '/api/search': async (u) => {
    const q = (u.searchParams.get('q') || '').trim();
    if (q.length < 2) return { query: q, candidates: [], errors: ['Please enter at least two characters.'] };
    return search(q);
  },
  '/api/browse': async (u) => browse({ facet: u.searchParams.get('facet') || null, value: u.searchParams.get('value') || null, century: u.searchParams.get('century') || null, country: u.searchParams.get('country') || null, movement: u.searchParams.get('movement') || null, role: u.searchParams.get('role') || null }),
  '/api/degrees': async (u) => degrees(u.searchParams.get('from'), u.searchParams.get('to')),
  '/api/report/profile': async (u) => {
    const p = params(u);
    if (!p.wd && !p.ulan) throw Object.assign(new Error('Missing artist identifier'), { status: 400 });
    return report.profile(p);
  },
  '/api/report/exhibitions': async (u) => report.exhibitions(need(params(u))),
  '/api/report/academic': async (u) => report.academic(need(params(u))),
  '/api/report/market': async (u) => report.market(need(params(u))),
  '/api/report/collections': async (u) => report.collections(need(params(u))),
  '/api/report/catalogue': async (u) => report.catalogue(need(params(u))),
  '/api/report/lifetime': async (u) => report.lifetime(need(params(u))),
  '/api/report/synthesis': async (u) => ai.synthesize(params(u)),
};
function need(p) {
  if (!p.name) throw Object.assign(new Error('Missing name'), { status: 400 });
  return p;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (url.pathname.startsWith('/api/')) {
    const ip = req.headers['x-forwarded-for']?.split(',')[0] || req.socket.remoteAddress;
    if (limited(ip)) return send(res, 429, { error: 'Too many requests — please wait a minute.' });
    const fn = routes[url.pathname];
    if (!fn) return send(res, 404, { error: 'Not found' });
    const t0 = Date.now();
    try {
      const data = await fn(url);
      send(res, 200, data);
    } catch (e) {
      send(res, e.status || 500, { error: e.message || 'Server error' });
    } finally {
      console.log(`${req.method} ${url.pathname}${url.search.slice(0, 80)} ${Date.now() - t0}ms`);
    }
    return;
  }
  // static files
  let file = path.normalize(path.join(PUBLIC, url.pathname === '/' ? 'index.html' : url.pathname));
  if (!file.startsWith(PUBLIC)) return send(res, 403, { error: 'Forbidden' });
  fs.readFile(file, (err, buf) => {
    if (err) {
      fs.readFile(path.join(PUBLIC, 'index.html'), (e2, html) => {
        if (e2) return send(res, 404, { error: 'Not found' });
        res.writeHead(200, { 'Content-Type': TYPES['.html'] });
        res.end(html);
      });
      return;
    }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'public, max-age=300' });
    res.end(buf);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Artist Research Atlas running at http://localhost:${PORT}  (AI synthesis: ${ai.enabled() ? 'on, ' + ai.model : 'off'})`);
  // Warm the Browse country list and result cache in the background
  // (never blocks startup).
  warmCountryFacets();
  warmBrowseCache();
});
