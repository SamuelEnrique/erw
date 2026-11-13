# Session 4109 report: the test that no table reaches the public site while its verdict is not public

Energy Research Warehouse (ERW). Chain 229, session 10 of 50, lab-desktop third window, 13 November 2026 11:02 to 11:17 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4100-licenses`. (The chain's plan puts this step in sessions 4131 to 4147; it was taken now, as a safety item, before the long tail of reads.)

## The routes by which a table reaches a visitor (read in the code, nothing built)

- **The live set:** row-level security lets the anon key read every row whose license is `public` (migration 002), whatever page reads it. The site masks only a table held "license needed" (`site/lib/license.ts`).
- **Downloads:** `/api/download` refuses a held table and any table whose verdict is not public, before it reads a row.
- **Release v1:** the tables marked `in_v1 = yes`.
- **Findings cards:** their figures are computed into `site/data/findings/*.json` and into charts and CSV files under `site/public/findings/`. **`site/proxy.ts`'s matcher skips any path with a file extension** (since session 5101, merged at 11:43, every extension but `.rsc`), so those files are served by address whatever the review curtain says. They are also in the public GitHub repository.
- **`/api/analysis`** answers only the internal view.

## Found and fixed

- **`large_load_public`:** live, flagged public, verdict "unsettled". It is public by the owner's ruling of 14 October (session 272), which `licenses.py` did not know. `RULED_PUBLIC` now records it: verdict public, standing "ruled". This records the owner's ruling and loosens nothing.
- **`large_load_rules` and `large_load_rule_reads`** were in release v1 with an unsettled verdict (four state commissions unread). `release_v1.py`'s plan now holds out any table whose ERW verdict is unsettled: 133 tables in v1, 51 held out. This is a tightening.

## Found, waiting for your ruling

- **Three findings cards are built from internal tables,** and their files are served by address:
  - `gas_sets_price` uses `isone_zone_prices_history` (ISO-NE asks permission). Its charts and `erw_2026_gas_share_hours.csv` are under `site/public/findings/`.
  - `siting_flexible` and `siting_gigawatt` use `texas_transmission_matrix` (the PUCT asks permission). `siting_gigawatt.csv` carries a `transmission_usd_mwh` column.

## The test (`tests/test_session4109_public_site.py`, 7 tests)

- **Live set:** every live-set table flagged public has a public verdict or is held.
- **Row-level security:** it serves public rows only.
- **Downloads:** the route refuses before it reads.
- **Release v1:** every table in v1 is public.
- **Findings cards:**
  - a card is built only from tables that are public or held, unless it is one of the three named;
  - that list only shrinks;
  - `/` and `/research` (the pages that draw the cards) may not open while one is named.

## Tests

- **462 test files** (the license, package, release and live-set tests): 2,999 passed, 94 skipped, 0 failed (6 min 51 s).

## Decisions made without you

- **No public file was deleted** (the rule against deleting files), and **`site/proxy.ts` was not changed**: how the cards' files are served is the site's design, and the files are already in the public repository.

## For Samuel's ruling

- **The three cards' public files** (`gas_sets_price`, `siting_flexible`, `siting_gigawatt`). **Default: left as they are** while every page is in review. The test stops `/` and `/research` from opening while they wait.
  - Options: build those cards without the internal tables; hold their ISO-NE and Texas transmission parts as "license needed"; or bring `site/public/findings/` under the review curtain.
