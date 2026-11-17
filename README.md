# Artist Research Atlas

A research website for **painters, sculptors, draftsmen and engravers**.

1. **Enter an artist's name.** Exact names, partial names, historical spellings, pseudonyms and inverted forms ("Rijn, Rembrandt van") all work.
2. **Choose the correct artist.** The site lists real artists whose name or a recorded variant matches. Each candidate shows birth and death dates (including conflicting dates), birthplace, death place, roles, the variant that matched, and authority IDs (Wikidata / Getty ULAN). Only people whose recorded occupation is painter, sculptor, draftsperson, engraver or printmaker (or a subclass of one) are shown.
3. **Read the report.** It loads section by section:

| # | Section | What it contains | Sources |
|---|---------|------------------|---------|
| 1 | Identity & names | Preferred name, life dates and places, nationality, roles, movements, genres, and every recorded name variant | Wikidata, Getty ULAN |
| 2 | Biography | ULAN biographical note, full encyclopaedic life narrative, documented life facts (education, teachers, pupils, memberships, awards, family, residences), and ULAN relationships | Getty ULAN, Wikipedia (English or best available language), Wikidata |
| 3 | Exhibition record | Exhibition timeline (artist as participant, plus exhibitions where works were shown), museum exhibitions, object-level exhibition histories, exhibition catalogues from 1751 on, and links to DoME, Paris Salon, Royal Academy, RKD, MoMA and Artfacts | Wikidata, Art Institute of Chicago, Cleveland Museum of Art, Open Library |
| 4 | Academic & peer reviews | Curated scholarship with the artist as main subject, most-cited peer-reviewed literature with abstracts, reviews, and chronologically arranged quotations from contemporaries, fellow artists and critics | Wikidata, OpenAlex (falls back to Crossref), Wikiquote |
| 5 | Critical analyses | Style, technique, reception and legacy, plus arguments from leading humanities scholarship. Optional AI synthesis | Wikipedia, OpenAlex/Crossref abstracts |
| 6 | Auction & art sales | Documented prices (with currency), sales, acquisitions and ownership events, sale and price mentions in the literature, museum provenance chains, the artist's own pages on Artnet, Artsy, MutualArt, Invaluable and Christie's, and pre-filled searches of 13 price databases | Wikidata, AIC, CMA, Wikipedia |
| 7 | Works & collections | Number of catalogued works, holdings by institution, image gallery, and museum open-access records | Wikidata, The Met, AIC, CMA, Europeana |
| 8 | References | All sources as Chicago-style citations in six groups: biographical; exhibitions & showings; academic; **sources from the artist's lifetime** (marked LIFETIME); market & provenance; and databases & authority files | Everything above, plus the Internet Archive, Library of Congress *Chronicling America*, Europeana and Open Library, filtered to the artist's lifetime |

The report can be printed or saved as PDF (all collapsed lists expand automatically). You can also copy or download every reference as `.txt` and download all the research data as `.json`.

You can also browse artists without a name: the Browse page lists artists by century (12th–20th), country, movement or medium — pick any combination from the dropdowns and press GO. Each list is a live Wikidata query restricted to the same five occupations, capped at 50 artists, and selecting an artist opens the same report. The country list is every country with eligible artists (a live count of citizenships), counting historical states under the modern country (e.g. the Dutch Republic under the Netherlands, the Republic of Florence under Italy); states that map to no modern country appear under their own name. The page also groups the twenty homepage artists by the same four facets.

The **Salon Time Machine** (`#/salon`) walks the Paris Salon year by year, 1673–1881: pick any of the 100 years with a surviving catalogue and browse every work as the livret listed it — catalogue number, title, artist, birthplace, teacher and medium, by section (Painting, Sculpture, Engraving, Architecture), with a search box for the year and 50 works per page. Every artist name links into the Atlas name search, so a Salon exhibitor leads straight to the full research report. The data is a static snapshot (144,081 records) built by `scripts/build-salon-data.py` from the combined Salon database (`salon-all.json`: the printed livrets, Garland reprints via the Internet Archive, parsed from OCR) into one compact JSON file per year under `public/data/salon/`. Catalogue numbers the parser had to infer, or that look suspect in the printed text, are flagged in the data and marked with a ~ on the page; some titles carry OCR noise and a few artist names are fragments. Artist names are corrected where the OCR misread them, from `public/data/salon/name-corrections.json` (7,775 high-confidence mappings, applied at display time); the original printed spellings are preserved in the data files, and ambiguous names are left as printed. Years with no surviving livret are absent. No images in this first version: most Salon works have no surviving image in the open sources.

The **Royal Academy Time Machine** (`#/ra`) walks the Royal Academy Summer Exhibition year by year, 1769–1905: pick any of the 137 years and browse every work as Graves's dictionary listed it — catalogue number, title, artist, address, occupation and medium, filtered by occupation (Painter, Sculptor, Architect, Engraver, other crafts), with a search box for the year and 50 works per page. A **search-all-years** panel on the same page searches across every year at once, from a combined index of all 161,019 dated works (`public/data/ra/all.json`, downloaded on first use): by artist, giving that artist's complete Royal Academy record in one view (grouped case-insensitively, since Graves prints surnames in capitals and the 1905 transcription does not), or by title, matching every word given against the printed titles — the way to trace an unsigned painting that was exhibited under a known title. Every artist name links into the Atlas name search, so an exhibitor leads straight to the full research report. The data is a static snapshot (161,019 of the combined database's 162,562 records; the 1,543 whose year could not be resolved are in the full database but not in this browser) built by `scripts/build-ra-data.py` from the combined Royal Academy database (`ra-all.json`: Algernon Graves, *The Royal Academy of Arts: A Complete Dictionary of Contributors and Their Work*, 1905–06, via the Internet Archive, parsed from OCR, with the 1905 exhibition recovered from the Paul Mellon Centre's RA Chronicle catalogue transcription) into one compact JSON file per year under `public/data/ra/`. Catalogue numbers that look suspect in the source are flagged in the data and marked with a ~ on the page; about 12,200 records have no readable catalogue number and show — — no number has been invented for them. Names, addresses and titles are as printed and carry the OCR noise of the source scans. No images in this first version.

The **Loan Exhibitions (UK)** page (`#/loan`) opens Algernon Graves's *A Century of Loan Exhibitions 1813–1912* (1913–15) — 42,727 works lent to a century of loan exhibitions, arranged by artist as Graves printed them, each with the exhibition, year, catalogue number, size and the owner who lent it. It searches three ways: by artist (that artist's complete loan record in one view), by title (a work traced across exhibitions, matching every word given against the printed titles), and by owner (everything a collector or institution lent — a provenance record in itself), and it is also browsable letter by letter. Every artist name links into the Atlas name search. The data is a static snapshot built by `scripts/build-loan-data.py` from the parsed database (`~/workspace/graves-loan/data/loan-all.json`: the Kingsmead reprint via the Internet Archive, parsed from the scan's word coordinates) into per-letter JSON files plus a combined search index (`public/data/loan/all.json`, downloaded on first search). Catalogue numbers that needed OCR digit-confusion normalisation are flagged in the data and marked with a ~ on the page, as are owners split from the title by column position alone; about 1,790 records have no readable catalogue number and show — — no number has been invented for them. Names, titles, sizes and owners are as printed and carry the OCR noise of the source scans; sizes suffer most, their printed fractions often read as plain digits. No images in this first version.

**Six Degrees of Rembrandt** (`#/degrees`) finds the shortest chain between any two artists — up to six steps — through recorded teacher/pupil/influence links: Wikidata *student* (P802), *student of* (P1066) and *influenced by* (P737, in both directions). The backend (`lib/degrees.js`, `GET /api/degrees?from=Q…&to=Q…`) runs a breadth-first search, one batched SPARQL query per level for the whole frontier, with neighbor sets cached in-process and completed searches cached too. Each link in the chain is labeled by its direction and every name links to that artist's report. Neighbors are verified to be people (a separate batched P31 check — joining P31 inside the neighbor query times Wikidata out), so groups, schools and works never appear as a link. If no chain is recorded within six steps the page says so honestly, with the number of artists explored. Verified chains: Rembrandt → Vermeer in 2 steps (Rembrandt taught Carel Fabritius, who influenced Vermeer), Rembrandt → Monet in 2, Hokusai → Van Gogh in 1, Rembrandt → Picasso in 3.

## Running it

Requires **Node.js 18 or newer**. There are no npm dependencies.

```bash
cd artist-research-atlas
npm start            # → http://localhost:3000
# or: PORT=8080 node server.js
```

### Optional configuration (environment variables)

| Variable | Purpose |
|----------|---------|
| `PORT` | HTTP port (default 3000) |
| `AI_API_KEY` (or `OPENAI_API_KEY`) | Turns on the **AI research synthesis** section. The model writes a narrative only from the sources gathered for the report and cites them as [S1], [S2]… |
| `AI_BASE_URL` | Any OpenAI-compatible endpoint (default `https://api.openai.com/v1`; also works with Azure, OpenRouter, a local Ollama or LM Studio, etc.) |
| `AI_MODEL` | Model name (default `gpt-4o-mini`) |
| `OPENALEX_API_KEY` | **Recommended in production.** OpenAlex's free tier shares one small daily budget per IP. A free key is available at https://openalex.org/settings/api. Without it, the site falls back to Crossref |
| `CONTACT_EMAIL` | Sent to OpenAlex and Crossref ("polite pool"; faster and more reliable) |
| `EUROPEANA_KEY` | Your own Europeana API key (the public demo key is used otherwise) |
| `USER_AGENT` | Custom User-Agent for outbound requests. Wikimedia asks for a contact address |

### Deploying on Render (free)

1. Put this folder in a GitHub repository. `package.json`, `server.js` and `render.yaml` must be at the top level of the repo.
2. Go to https://dashboard.render.com and choose **New → Blueprint**. Pick the repository; Render reads `render.yaml`.
3. Fill in the optional variables (`CONTACT_EMAIL`, `OPENALEX_API_KEY`, `AI_API_KEY`), then click **Apply**.
4. After a couple of minutes the site is live at `https://artist-research-atlas.onrender.com` (or a similar name). The health check is `/api/health`.

Free Render services go to sleep after 15 minutes without visitors. The first visit after that takes about 30–60 seconds to wake the site up.

A `Dockerfile` (for Fly.io, Railway, Cloud Run or any Docker host) and a `Procfile` (Heroku-style hosts) are included too.

### Other hosts

The app is a single Node process, so it runs on any Node host: Render, Railway, Fly.io, Heroku, a VPS with `pm2`, and so on. Set the start command to `node server.js` and the environment variables above. Responses are cached in memory for 3–6 hours. There's a basic per-IP rate limit (120 API calls/minute).

## Project structure

```
server.js          HTTP server, API routes, static files
lib/util.js        cached fetch with retry, SPARQL clients, date formatting, Chicago citations
lib/search.js      candidate search (Wikidata + Getty ULAN), occupation filter, name-variant matching
lib/browse.js      browse lists by century, country, movement or role (live Wikidata queries, capped at 50)
lib/degrees.js     Six Degrees: shortest chain between two artists through recorded teacher/pupil/influence links (BFS to depth 6)
lib/report.js      report modules: profile, exhibitions, academic, market, collections, lifetime
lib/ai.js          optional grounded AI synthesis
public/            index.html, app.js (UI), styles.css (screen + print)
public/data/salon/ one compact JSON file per Salon year + index.json (built by scripts/build-salon-data.py)
scripts/build-salon-data.py  converts salon-all.json (144,081 Paris Salon records, 1673-1881) into public/data/salon/
public/data/ra/    one compact JSON file per Royal Academy year + index.json + all.json (the all-years search index; built by scripts/build-ra-data.py)
scripts/build-ra-data.py  converts ra-all.json (162,562 Royal Academy records, 1769-1905) into public/data/ra/
```

### API

```
GET /api/search?q=NAME
GET /api/browse
GET /api/browse?facet=movement&value=Q40415
GET /api/browse?century=19&country=Q96&movement=Q40415&role=Q1028181
GET /api/degrees?from=Q5598&to=Q41264
GET /api/report/profile?wd=Q5598&ulan=500011051
GET /api/report/{exhibitions|academic|market|collections|catalogue}?wd=…&name=…&by=1606&dy=1669
GET /api/report/lifetime?wd=…&name=…&by=…&dy=…&variants=A|B|C
GET /api/report/synthesis?wd=…          (only when AI is configured)
```

## Limitations

- **Coverage depends on the open record.** Major artists produce very large reports; obscure artists may have only an authority record and a few period sources.
- **Auction results:** lot-by-lot hammer prices are kept in subscription databases (Artnet, Artprice, MutualArt), which have no open APIs and do not allow redistribution. The site reports openly documented sales and provenance and links straight to the artist's pages and searches on those services.
- **Namesakes:** name-based searches (scholarship, newspapers, digitised books) can include other people with the same name, especially for common names. Museum records are filtered by surname plus life dates, but you should still check each item.
- Citations are generated automatically from catalogue metadata. Check page numbers and editions against the originals before publishing.
