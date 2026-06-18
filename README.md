# Dashboard Analytics Templates

A library of **production-grade web dashboard templates** for data analytics — browse them, reskin them, and use them as **design blueprints to rebuild the same dashboards in Power BI** (so you never have to design from a blank canvas).

> All data in this project is **realistic mock data**. "BYD" appears only as an illustrative example brand for an automotive use case — this project is fictional and **not affiliated with or endorsed by BYD**.

## Concept

> **Every dashboard = Archetype × Skin × Data**

- **Archetype** — the layout/structure for a decision type (monitor, diagnose, compare, explain, forecast, detail, present)
- **Skin** — the visual theme (swap a single CSS class)
- **Data** — swap in your own source; the structure stays

## What's inside

- **13 archetypes** — Executive Overview, Operational Monitor, Financial P&L, Funnel & Conversion, Geo / Distribution, Marketing, Workforce, Inventory, After-sales & Service, Customer Lifecycle / CRM, Forecast & Planning, Detail / Drillthrough, and an **Executive Brief** (board-ready, minimal)
- **5 skins** — BYD Red, Finance Dark, SaaS Violet, Luxury Gold, Command Center (switchable live on every page)
- **Chart-Pattern Catalog** — ~24 chart types with "use when" + Power BI mapping
- **Reference Links** — curated links to world-class data-viz galleries (links + notes only)
- **Moodboard** — upload your own AI-generated inspiration images (local server only)

## Quick start (local)

```bash
python serve.py
# open http://localhost:8000/
```

`serve.py` is a single dev hub: it serves all static files **and** mocks the project APIs at `/api/...` on one port.

## Project structure

```
_design-system/   tokens.css · components.css · charts.js · skins/      (the foundation)
_templates/       13 archetypes + gallery + chart-patterns + references (the library)
_moodboard/       image inspiration board (upload / star / categorize)
Projects/         API-connected instances (BYD Overviews, Ops Monitor Live)
serve.py          dev hub: static server + mock API
index.html        hub landing page
```

## Power BI bridge

Each template maps to **native Power BI visuals**. Deliverables for rebuilding in Power BI:

- `theme.json` per skin → `_design-system/skins/powerbi/` (import directly)
- `build-spec.md` per archetype → visual-by-visual mapping + field wells + measures (archetypes 01–04 done; more to follow)
- Full example: `Projects/BYD-Overviews/02-build-spec/`

## Deployment notes

- **Static parts** (template library, gallery, chart-patterns) → deployable to **GitHub Pages** as-is.
- **Dynamic parts** (`serve.py` `/api/...`, moodboard upload/delete) → need a real server host; they run locally and degrade gracefully (read-only / empty state) when no API is present.

## Tech

Vanilla HTML / CSS / JS · [Chart.js](https://www.chartjs.org/) · Python standard-library HTTP server. No build step, no framework.
