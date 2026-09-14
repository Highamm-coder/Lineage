# Lineage of the Church

Catholic, Anglican and Orthodox lines of succession, from the apostles to today, drawn on shared century rows so figures level with each other held office in the same century. Open any century to see every holder; click anyone for their bio, dates, lifespan and something that happened in the world during their tenure; follow a dotted circle to explore a family of churches.

A static web app: plain HTML, CSS and JavaScript, no framework.

## Run it locally

```bash
python3 -m http.server 8750
```

Then open http://127.0.0.1:8750. It must be served over HTTP (not opened as a file) because person data is fetched from `data/people.json`.

## Pages

| Page | What it shows |
|---|---|
| `index.html` | The three main lines, Jesus above them, and four dotted circles |
| `oriental-orthodox.html` (+ `-ethiopian`) | Coptic, Syriac and Armenian lines, after Chalcedon (451) |
| `orthodox.html` (+ `-georgia`, `-jerusalem`, `-alexandria`) | Constantinople for context, Moscow, Antioch |
| `protestant.html` | Lutheran, Reformed and Free-church founders (no single succession) |
| `anglican-north-america.html` | Canterbury for context, the Episcopal Church, ACNA |

## Structure

```
*.html                  generated pages (do not edit by hand)
assets/css/app.css      all styles, light and dark (edit directly)
assets/js/app.js        century toggles, find-in-page, the person dialog (edit directly)
data/people.json        generated: bio, terms, lifespan, world event and portrait for every person
img/landmarks/          portraits for featured figures
img/holders/            portraits for every other holder (lazy-loaded)
pipeline/
  site.py               builds every page and data/people.json
  views.py              which pages exist and which lines each shows (edit to add a family)
  figures.py            hand-curated featured figures for the three main lines
  worldevents.py        picks one unique, during-tenure world event per person
  events.py             hand-checked world-events timeline (used alongside Wikipedia's year articles)
  fetch_people.py       fetches bios, portraits and birth/death years from Wikipedia and Wikidata
  family_links.py       matches register names to Wikipedia articles for the family lines
  fetch_years.py        downloads the Events section of every Wikipedia year article
  data/                 cached source data (registers, links, bios, lifespans, year events)
```

## Rebuild

```bash
cd pipeline
python3 site.py
```

Rebuild after editing `app.css` or `app.js` too: pages link them with a content hash (`app.css?v=…`) so browsers never run a stale copy.

To refresh source data first: `python3 family_links.py`, `python3 fetch_people.py`, `python3 fetch_years.py` (these call Wikipedia and Wikidata and are slow; results are cached in `pipeline/data/`).

## Before publishing

- Re-check the status of ACNA's archbishop (a church trial was scheduled for September 2026). ACNA cards show title and dates only.

## Deploy

Any static host works (Netlify, Cloudflare Pages, GitHub Pages, S3): publish the project root. `pipeline/` is not needed at runtime.

## Sources

English Wikipedia succession lists, articles and year articles; Wikidata for birth and death years. Current as of September 2026.
