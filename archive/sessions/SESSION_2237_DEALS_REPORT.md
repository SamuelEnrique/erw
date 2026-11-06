# Session 2237 (chain 156, deals and datacenters) report: the daily step, end to end, offline

6 November 2026, about 08:58 to 09:09 UTC, portable-laptop (code role), unattended. Worktree `erw-2237` on `wip/2237-deals`, cut from `wip/2236-deals`. Model spend **USD 0.5172** (two runs of one stored day: 0.1822 and 0.0854; 0.1716 and 0.0780; every call's tokens and cost in `runs/oneday2237.out` and `runs/oneday2237b.out` of the main checkout). No ledger row (a code machine). Nothing deployed; no warehouse data written (the day ran in a temporary folder with copies of the tables).

- **`warehouse/deals/calls.py`** (new), used by both extractors: the spending limit stops the run with the API's words; a refusal or an answer that is not JSON is tried once more; a busy API twice more; plain words in every failure line. **Both extractors** write no table when no call answers, and put the failure first in the health line's 300 characters.
- **`warehouse/deals/eval/one_day.py`** (new): the two steps on one stored day against copies of every table held; `--fresh` takes that day's rows out first. 5 November: sent again, no duplicate; as a first run, 8 deals and 4 facilities, each better on its parties, AI tag, kind, sum and place (the audit file).
- **`scripts/deals_backfill.py`** (new): `--dry-run` printed the estimate for 27 October to 5 November, **USD 2.93** (scoring 2,038 stories USD 1.93, deals USD 0.74, datacenters USD 0.26), in the audit file for the owner; `--run` is the desktop's. The four days 31 October to 3 November hold no story to backfill.
- **`warehouse/deals/crosscheck.py`**: a figure a year or a target ("targets 1GW annually") is not compared with the deal's MW.
- **The report times of sessions 2231 to 2236 corrected** from their commits (they were estimates, too late by up to four hours).
- **`tests/test_session2237_deals.py`** (9 tests); with 2232 to 2236, 531 and 166: 83 passed.

## Decisions made without you

1. **The spending limit stops the run** at the first call: every later call would fail the same way and cost a request each; the health line names the limit and the day access returns, in the API's words.
2. **No table is rewritten when no call answered**, so the table's header keeps the last good run's retrieval time and no story is marked checked.
3. **The backfill is three steps**, the scorer first, since every eligible story already scored was checked; the extractors' date range is the scorer's (the extractors send every unchecked story). The scorer is run, never changed (its file is not this chain's).
4. **The estimate counts what the stories would be**, not what they are, for the unscored days: the shares of the 14 days before. Said so beside the figure.

## For Samuel's ruling

1. **The backfill: USD 2.93 estimated** (27 October to 5 November: scoring 2,038 stories, then about 17 deal calls and 11 datacenter calls). If approved, on the desktop under the data lock: `.venv\Scripts\python.exe scripts\deals_backfill.py --from 2026-10-27 --to 2026-11-05 --run` (after this chain's code lands).
2. **The four days with no story** (31 October to 3 November): whether the feeds' own archives should be read for them (a pull; the feeds' depth decides what is left), or the gap stays and the Roundups say so.
