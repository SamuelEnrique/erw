# Session 720 report: the research card

22 October 2026, from 12:09 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-720` on `wip/720-allgrids` (cut from `wip/719-allgrids`; its one commit replayed over 719's recut at 12:58). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 720. Model spend USD 0. No warehouse data written; no request to a publisher. Written, never posted or sent.

## Read these first

- **One card under `/research`**, in review like every page, in the findings pipeline's format: `site/data/findings/siting_gigawatt.json` and its data `site/public/findings/siting_gigawatt.csv`, at `/research/card/siting_gigawatt`. Its title is "WHERE A GIGAWATT PAYS LEAST".
- **It is written by `site/scripts/siting-card.mjs` from the tab's own functions** (`lib/siting.ts`, through `scripts/siting-files.mjs`), so every figure on it is the tab's figure for the same load: a 1 GW datacenter load (0.90 in every hour, never curtails). `node scripts/siting-card.mjs --check` exits 1 when the files differ from a fresh computation.
- **What it says**:
  - Least all-in: ERCOT HB_WEST, USD 40.83 per MWh (USD 321,907,123 a year).
  - Most all-in: ERCOT LZ_CPS, USD 46.69 per MWh (USD 368,100,514 a year).
  - The ranking is among the 14 of the tab's 48 rows whose every cost part is held, all of them ERCOT's. Elsewhere transmission is not held, or capacity is held under a license (34 rows), and the card says so.
  - Median months to connect, generators: ERCOT 45.80 (least), CAISO 100.00 (most), over the requests that came online from 2023 to 2025 (`interconnection_durations`, Berkeley Lab's Queued Up).
- **One chart**: energy and the four-peak charge per row, paired bars, with its source line. Three callouts and the why line, and no verdict.
- **The card states its generator** (`engine`), so `tests/test_session258.py` (cards written by the pipeline's Python engines) skips it. The research topics gain "transmission" (`/4cp|transmission/`), and "queue" matches `interconnection_durations`; `lib/researchrules.ts` and `tests/test_session238.py` move together.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/internal/open`, then `https://erw-flame.vercel.app/research/card/siting_gigawatt`: the title, the chart (hover a bar), the three callouts, the why line and the footnote naming the tab, the tables and the method.
2. Click "Table" above the chart for the rows, and the CSV link for the download.
3. `https://erw-flame.vercel.app/research/card/siting_gigawatt?render=1`: the 1080 by 1350 frame.
4. Screenshots: `docs/brand/review-720/` (`/research` before and after; the card at 1280 and 390; the render frame).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `node scripts/siting-card.mjs --check` | 0 | the files are the tab's figures |
| `tests.test_session720`, `719`, `258`, `238`, and the chain's 700 to 718 with 215, 237, 408 | 0 | 185 OK, 1 skip |
| `db_probe.py` | 0 | |
| `npm run build` (lock `s720`, beat), twice (before and after 719's recut) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power,/datacenters,/research` | 1 | 2,723 of 2,723 values equal; the card's six figures read and equal; floors added for the card (6) and 719's address (10); the one floor failing is `/research/card/gas_sets_price` (held, production the same) |
| `check-findings-grids.mjs` on the build | 0 | 173 of 173 (its named cards; this card is not among them, so it was checked by the shots at both widths and the render frame) |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |

## The landing

With sessions 719 to 721 in one push (see 721's report).

## Decisions made without you

1. **The card's figures are computed by the site's own library**, not by a Python engine of the findings pipeline, so the card and the tab can never disagree. The card names its generator, and test 258 skips such cards.
2. **The ranking is among the rows with every part held**, which leaves only ERCOT's rows. The card says how many rows are not held and why, rather than ranking a partial figure.
3. **Paired bars, not stacked**: the chart set's `bars_free` kind draws pairs. The all-in figure is in the callouts and the table.

## For Samuel's ruling

- Nothing new.

## Files

- New: `site/scripts/siting-card.mjs`, `site/data/findings/siting_gigawatt.json`, `site/public/findings/siting_gigawatt.csv`, `tests/test_session720.py`, `docs/brand/review-720/`, this report.
- Changed: `site/lib/researchrules.ts`, `site/scripts/check-values.mjs` (one address), `site/scripts/check-values-floor.json` (two floors), `tests/test_session238.py`, `tests/test_session258.py`.
