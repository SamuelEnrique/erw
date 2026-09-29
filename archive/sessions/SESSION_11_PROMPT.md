Session 11 of the Energy Research Warehouse (ERW). Read CLAUDE.md, docs/platform-tools.md, docs/coverage.md, warehouse/supabase/README.md and SESSION_10_REPORT.md first. Same non-negotiables: real data only, fail loudly, no em dashes anywhere including page copy, never delete existing files, commit after each task, do not push, do not stop to ask questions. The site reads Supabase with SUPABASE_URL and SUPABASE_ANON_KEY only, never the service key. If Supabase cannot be applied, build the site against the local CSVs through a small read layer and say so.

Positioning for every page: the Energy Research Warehouse is the live, citable record of the US energy system, prices, flows, projects, deals and policy across power, gas, oil, nuclear, renewables, storage and transmission, with AI's demand for power as the sharpest lens. Never narrow the copy to AI.

TASK 0. Finish Supabase. With SUPABASE_DB_URL now in .env, run warehouse/supabase/apply.py to apply both migrations, then load.py, reconcile counts against the filtered CSVs, report pg_database_size, run latest_prices.py once and confirm the upsert lands, and run package/tests/test_backends.py with ERW_BACKEND=supabase; the 16 Supabase tests must pass. Confirm with the anon key that internal rows are invisible and public rows are visible. Commit before starting the site.

TASK 1. Scaffold. A Next.js app (App Router, TypeScript, Tailwind) under site/, with a single design token file: background #F7F3EA, text #2E2D29, accent #8C1515, muted #6B665E, borders #D9D2C3, Georgia for headings, a clean sans for body. Data-forward, no marketing copy, no stock imagery. Mobile-responsive. Every number on every page comes from Supabase or a committed metadata file; where data is missing the page shows "no data" with the reason, never a placeholder value.

TASK 2. Pages.
- / (home): a status strip from the tables catalogue (tables, rows, last refresh, validator status); the price board: latest real-time price per main hub for each ISO from latest_prices with the interval time and a 7-day sparkline from the 90-day series rows; latest Henry Hub, WTI and Brent; today's Energy Digest top 5 from docs/digest/latest.md rendered from the committed markdown; a link block to the data page.
- /prices: the full board, every hub and zone, day-ahead and real-time, with a table view and per-entity 30-day chart.
- /digest and /digest/[date]: the archive of committed digests.
- /data: the coverage table (public tables only, with sector, freq, date range, rows, source, license), a link to the Redivis dataset, the erw package install line, and a methodology section linking docs/datastandard.md and docs/methods/*.md rendered as pages.
- /explorer/ercot-peak-premium: the first signature explorer, reading the derived annual and monthly tables: year selector, hub selector, box-style summary (min, Q1, median, Q3, max) per time-of-day block, and the headline metrics, with the method doc linked. Charts in a light charting library; every chart cites its table below it.
- /about: one paragraph on the project, the Stanford independent study, the IRW lineage, and the license rule.
Revalidate server data every 15 minutes for latest prices and hourly for the rest.

TASK 3. Run locally, screenshot each page to site/screenshots/ (headless browser), and check every rendered number against a direct Supabase query for at least ten values. Write site/README.md with the exact steps to deploy on Vercel (import the GitHub repo, root directory site/, the two environment variables), which the human will do by hand.

TASK 4. SESSION_11_REPORT.md in the usual format with the screenshot list and the ten-value check. Final commit.