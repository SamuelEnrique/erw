# Session 3001 report: prices, the first part, and the hunt's builder

6 November 2026, about 11:05 to 11:20 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **10 drafts added to the review list** (`public.scanner_drafts`, rule `hunt`, module `deep.prices`, state draft; `/internal/findings`). All rest on ERCOT's hourly real-time prices from 2015 to 2025:
  - Midday price: the West load zone's midday (11 AM to 4 PM) was 48.9 percent of its all-hours mean in 2025, against 128.9 in 2015. The South load zone's was 74.5, against 131.1.
  - Evening price: the South hub's evening (5 PM to 10 PM) was 161.0 percent of its all-hours mean in 2025, against 109.5 in 2015. The Houston load zone's was 156.9, against 109.6.
  - Daily spread: the median day's highest hour minus its lowest at the West hub was USD 58.47 per MWh in 2025, against 20.35 in 2015. At the South hub it was 50.76, against 18.12.
  - Top days: the top tenth of days carried 36.9 percent of the Houston hub's summed daily spread in 2025, against 61.5 percent in 2015 (South hub: 36.8, against about 61).
  - Hour-to-hour move: the median hour-to-hour move at the Houston hub was USD 3.11 per MWh in 2025, against 1.05 in 2015 (South hub: 3.17).
- **Each draft carries everything the chain file asks for.** Its sentence is computed by code. Its chart is the hunt's `flag_line`. It names its tables and rows. Its strength is the hunt's five tests and the typical-move ratio. It has a limits sentence, the yearly CSV, the hunt's Stata and Python mirrors, and `reproduce.py` and `reproduce.do` that recompute the figure from the tables with the expected values at the top. It also has the two pictures and the caption. Each draft's document is under `docs/findings/prices/`.
- **Five reproduction scripts were run on the main checkout's tables** (one for each candidate that drafted), and all five printed the expected figures exactly. The test also checks every candidate's script against the module on a small table.
- **The builder:** `warehouse/analysis/findings/deep/builder.py`. Each later family is a module beside it. Branch `wip/3001-findings`.

## What it did

- **`deep/builder.py`** reuses the weekly hunt's own claim and five tests (`hunt.test_claim`) and its loader (`hunt.load_drafts`). It writes each draft in the hunt's row form, with this chain's files and document.
  - It folds a hub and its load zone of one name into one story.
  - It keeps at most two regions of a candidate, and the strongest by consequence, then strength.
- **`deep/prices.py`** asks eight candidates, none of them a pattern the weekly hunt already asks. Five drafted. Three passed nowhere:
  - **The dearest one percent of hours' share** fails the window test and the typical-move floor.
  - **The West, Houston and South hubs' basis to North** fails the typical-move floor: the West hub went from USD 0.01 to 0.86 per MWh, but the yearly moves are larger than that change.
  - **The spark spread at a 7.0 heat rate** fails the same floor: the hub average went from USD 6.09 to 9.92 per MWh.
- **`hunt.py`'s `fix_source_lines` now leaves this chain's rows as they are.** It raised `pattern ... is not in the library` on a row it did not know. The fix has a test.
- **Tests:** `tests/test_session3001.py` (7 tests). With the hunt's tests for sessions 233, 251 and 258: 78 passed.

## Decisions made without you

- **Only ERCOT is drafted for prices.** CAISO's hubs hold three full years (the window test needs four). PJM's hub history is not held. ISO-NE, MISO, NYISO and SPP need a license or are held. EIA's ICE daily table holds 2026 only and is internal.
- **No model was called.** Every sentence is a template filled by code, so no figure can come from a model. The model's budget is kept for proposing candidates in families where the tables are less obvious.
- **The reproduction scripts read the table as the Redivis download holds it** (names on the first line). The Python one also takes the ERW's own file with its `#` lines. The Stata one says to delete those lines first. Central time is computed in Stata from the US daylight-time rule.
- **Ten drafts kept, from five candidates, two areas each.** The other 28 passing claims are kept in `runs/deep/2026-11-06/prices/prices.json` on this machine with the reason each was left out.

## For Samuel's ruling

- None new.
