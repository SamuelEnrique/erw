# site/: the ERW public site

The public site of the Energy Research Warehouse (ERW): Next.js 16 (App Router), TypeScript and Tailwind 4. It reads the Supabase live set (`warehouse/supabase/`) with the anon key, which row-level security limits to public rows, and renders the committed markdown under `docs/` (the Energy Digest, the data standard, method documents).

## Pages

| Route | Shows | Reads | Revalidates |
|---|---|---|---|
| `/` | status strip, real-time price board with 7-day sparklines, Henry Hub, WTI and Brent, the digest's top 5, links to the data page | `catalogue`, `latest_prices`, `series`, `docs/digest/latest.md` | 15 minutes |
| `/prices` | every public hub and zone: latest real-time interval and the day-ahead price for the current hour | `latest_prices`, `series` | 15 minutes |
| `/prices/[entity]` | one hub or zone, last 30 days, real time and day-ahead, with min, mean and max | `series`, `latest_prices` | 1 hour |
| `/digest`, `/digest/[date]` | the Energy Digest archive | `docs/digest/*.md` | 1 hour |
| `/data` | coverage of every public table, the Redivis dataset, the `erw` package install, methodology links | `catalogue`, `data/site.json` | 1 hour |
| `/data/standard`, `/data/methods/[slug]` | `docs/datastandard.md`, `docs/methods/*.md` | committed markdown | at build |
| `/explorer/ercot-peak-premium` | the ERCOT peak-premium explorer: year and hub selectors, box summaries per time-of-day block, headline metrics, yearly and monthly charts | `series` (`ercot_peak_premium_annual`, `ercot_peak_premium_monthly`), `headers` | 1 hour |
| `/about` | the project, its lineage and the license rule | | at build |

Every number comes from Supabase or a committed metadata file (`data/markets.json`, `data/site.json`). Where a read fails or a table has no row, the page says "no data" with the reason. Every chart and table names the ERW table below it.

## Files

- `app/tokens.css`: the single design token file (colors, typefaces).
- `lib/supabase.ts`: the only reader of Supabase. `SUPABASE_URL` and `SUPABASE_ANON_KEY`, server-side only; never the service key.
- `lib/data.ts`, `lib/markdown.ts`, `lib/format.ts`: reads, markdown rendering, number formats.
- `scripts/build-content.mjs`: bundles `../docs` into `content/docs.json` before `dev` and `build` (generated, not committed).
- `scripts/screenshots.mjs`: full-page screenshots of every page in headless Chrome, to `screenshots/`.
- `scripts/check-values.mjs`: compares every rendered number with a direct Supabase query.

## Run locally

```bash
cd site
npm install
# site/.env.local (never committed):
#   SUPABASE_URL=https://<project>.supabase.co
#   SUPABASE_ANON_KEY=<the anon key>
npm run build
npm start                                   # http://localhost:3000
node scripts/check-values.mjs               # every rendered number against Supabase
node scripts/screenshots.mjs                # screenshots/*.png
```

Use `npm run build` and `npm start` rather than `npm run dev`: `next dev`, when it detects an AI coding agent, rewrites `AGENTS.md` with a block that contains em dashes, which this repository does not allow.

## Deploy on Vercel (a human, by hand)

1. On vercel.com, **Add New, Project**, and **Import** the GitHub repository `SamuelEnrique/erw`.
2. In **Configure Project**, set **Root Directory** to `site`. Vercel detects Next.js; keep the default build command (`npm run build`, which runs the `prebuild` content step first) and output settings.
3. Under **Root Directory**, leave **Include files outside the root directory in the Build Step** enabled (the default). The build reads `../docs` for the digest and methodology pages, and fails if it cannot.
4. Under **Environment Variables**, add exactly two, for Production and Preview:
   - `SUPABASE_URL`: the project URL, `https://<project>.supabase.co`
   - `SUPABASE_ANON_KEY`: the project's anon (public) key

   Do not add `SUPABASE_SERVICE_KEY` or any other key, and do not prefix either name with `NEXT_PUBLIC_`: the site reads Supabase on the server only.
5. **Deploy.** Each push to `main` redeploys, so a newly committed digest appears after the daily workflow's commit. Prices refresh on their own schedule (15 minutes for latest prices, hourly for the rest) without a redeploy.
6. Check the deployment: the home page status strip shows the table count and last refresh, and no section says "no data". If one does, its reason names the failing read.
