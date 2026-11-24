# LinkedIn video posts, 24 November 2026 (session 9900)

Unattended chain on lab-desktop, 10:18 to about 11:05 UTC. Worktree `C:\Users\Shared\Documents\erw-posts`, branch
`wip/linkedin-posts-2026-11-24` from origin/main `156fa60ac`. Not landed. No site file changed; `site/lib/release.ts`
untouched; no warehouse table written or changed; nothing posted or published anywhere. Model spend USD 0. Session
numbers 9900 to 9939 checked free on origin/main and every branch (file names under `archive/sessions/` and `queue/`,
commit subjects); this chain used 9900.

Review page: https://github.com/SamuelEnrique/erw/blob/wip/linkedin-posts-2026-11-24/docs/reviews/linkedin/posts-2026-11-24.md

## What was done

- Part A: `motion/src/Post.tsx` takes optional `max`, `prefix`, `suffix`, `rows[].display`, `rows[].second`,
  `labelWidth`, and 7 to 10 rows (row height divides by rows minus one). `motion/stills_post.mjs` renders stills at
  chosen frames or at each row's highlight peak.
- B1 (Nvidia): blocked at SEC EDGAR; not rendered (below).
- B2 (Thanksgiving peak hour), B3 (gasoline, versions A and B): rendered, square and tall.
- Part C: sections 37 (versions A and B), 21, 24 (versions A and B), 1, 8, 10 and 3: rendered, square and tall.
- Sections 9 and 12 not added: the chain adds them only if all ten posts pass, and B1 did not.
- 26 videos in `docs/research/motion/posts/` (the two of queue_withdrawn untouched, 24 new), each with its last-frame PNG.
  Data files in `docs/research/motion/posts/data/`, the scripts in `docs/research/motion/posts/scripts/`.

## Part A: the regression comparison

Stills of `queue_withdrawn` at frames 0, 90, 200, 330 and 449, 2160 x 2160 and 2160 x 2700, from origin/main's
`Post.tsx` and then from the extended one, compared pixel by pixel (`scripts/pixcmp.py`):

- First comparison: the five square stills identical; four of the five tall stills differed (374 to 2,522 pixels,
  largest channel difference 38), all inside the number column. Cause: the extension printed the number and "%" as
  one string, where the template's JSX gives two text nodes, and the browser shapes them differently at the tall
  size. A rerender of the extended code was identical to itself, so it was not noise.
- Fix: the number and suffix stay separate text nodes (`{spec.prefix}{value}{spec.suffix ?? "%"}`).
- Second comparison: all ten stills identical, 0 differing pixels, max channel difference 0.
- Later changes touch only specs with a display text or a second figure (the number column's 18 px slack, and the
  200 px track floor applied to the 1080 x 1080 layout); the default path is the one compared.

## Outside sources read, with terms verdicts

Every request sent only the User-Agent "ERW research project, github.com/SamuelEnrique/erw"; no redirect followed.

| Address | When (UTC) | Answer | Verdict |
|---|---|---|---|
| https://www.sec.gov/robots.txt | 2026-11-24 10:24:39 | HTTP 403, "SEC.gov, Request Rate Threshold Exceeded", 1,925 bytes, sha256 3ae480a0... | Refused: SEC's fair access rule asks for a company name and a contact email; the ERW sends no person's email unasked. Nothing more asked of www.sec.gov or data.sec.gov. |
| https://stooq.com/robots.txt | 2026-11-24 10:54:03 | HTTP 200, 96 bytes: `User-agent: *` `Disallow: /` (Bingbot and Googlebot allowed) | Not allowed. No other Stooq address asked. |
| https://www.nasdaq.com/robots.txt | 2026-11-24 10:54 | Connection reset by the server (HTTP/2 stream reset, error 0x2) | Refused; not asked again. |
| https://api.eia.gov/v2/petroleum/pri/gnd/data/ (two series, from 2026-11-01) | 2026-11-24 10:32:45 | HTTP 200; newest week 2026-11-16 | The ERW's registered source (`eia:petroleum/pri/gnd`, the daily connector's API); read only, saved with the key removed. |

Local tables read (no request): `eia930_ba_demand_hourly` (20261123T193514Z) and its raw six-month files,
`caiso_fuel_supply`, `caiso_fuel_supply_history`, `eia_retail_fuel_prices` (20261120T150214Z), `eia_world_oil_monthly`,
`eia_uranium_marketing_annual`, `eia930_region_pair_hourly`, `storage_buildout_monthly`, `eia930_daily_demand`,
`grid_stress_yearly`, `eia930_subba_demand_hourly_2019` to `_2025`.

## B2 findings worth keeping

- EIA's six-month files stamp MISO's "local time" in Eastern Standard Time in November (hour 1 ends 06:00 UTC on
  27 November 2025), not Central; the post uses Central, so its MISO hours are one earlier than EIA's stamp.
- CAISO's EIA-930 demand counts battery charging as demand, while evening demand stays in line with the forecast (13 November 2025, hour ending 11:
  demand 29,706 MW, CAISO's forecast 23,813 MW, batteries charging 6,899 MW; the battery column empty). As the fleet
  grew, California's November days began to peak at midday (2025's three Thursdays, Thanksgiving 2024 and 2025). Any
  ERW finding on CISO's EIA-930 demand by hour since 2024 may carry this.

## What failed

- B1: SEC refusal (above). The data file holds the header and the block only.
- Tall regression (fixed, above).
- The first Texas title took three lines; shortened.
- The fit checker first skipped the last row's band at its peak (it lies below the rule's position); fixed and rerun.
- `motion/` npm ci: esbuild's postinstall not run (as on 17 November); the bundle and every render worked.
