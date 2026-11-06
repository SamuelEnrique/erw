# Session 821 report: the deal rows, sorted by who stands behind them

23 October 2026, 07:32 to about 07:55 UTC, unattended, on portable-laptop (the code machine), from the main checkout (documents and one reader; no build). Chain `queue/done/080-night-23-october-portable-landing-deals-.md`, session 821. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no web request (the two tables read from this machine's copies, current with the warehouse of record by `scripts/sync.py --check`).

## Read these first

- **16 of 505 deals can be shown, 486 are held, 3 are unsettled**: `docs/reviews/deals-public-rows-2026-10-23.md`, with the shown rows and their public evidence, the ten publishers behind the held rows and the three unsettled rows.
- **Every shown deal rests on World Nuclear News**, the one outlet of the deals' feeds whose terms read as public; the subset is nuclear, 3 of 16 state MW (1,583 MW) and 4 state dollars (USD 26.8 billion).
- **The one sort lives in `warehouse/deals/public_rows.py`** (a reader; `--markdown` prints the review's tables, `--json` writes one entry a deal for the site). Sessions 822 to 827 read it.

## What to review

- `docs/reviews/deals-public-rows-2026-10-23.md`, "Read these first" and the two ruling items at its end.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 821"` | 0 | on duty |
| `scripts/sync.py --check --no-git --tables <the six deal and datacenter tables>` | 0 | 6 current, 0 behind, 0 diverged |
| `warehouse/deals/public_rows.py --markdown` | 0 | 505 deals, 557 evidence rows: shown 16, held 486, unsettled 3 |
| cross-check of the 16 shown deals' `story_ids` against `news_stories` (790 ids, all found) | | no sort changes; story-only outlets listed in the review |

## The landing

Documents and the reader pushed to main (no page changed; no snapshot needed).

## Decisions made without you

1. The evidence table is the rule's input (the chain's words), `story_ids` the cross-check.
2. A deal with no evidence row is held, not unsettled.
3. The reader is a module under `warehouse/deals/` (files this chain owns), not a script under `runs/`, so the site's JSON and the tests use the same sort.

## For Samuel's ruling

- Whether a shown deal's figures may be drawn when its cluster holds a held outlet's story too (4 of 16); the stricter every-story rule shows 11.
- Whether Energy-Storage.news and Electrek are read (3 unsettled deals).

## Files

- New: this report; `docs/reviews/deals-public-rows-2026-10-23.md`; `warehouse/deals/public_rows.py`.
