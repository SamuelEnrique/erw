# Note: chain 164, the desktop's second window (6 November 2026): the findings hunt over the whole warehouse, and the landing service

Sessions 3000 to 3023, lab-desktop, second window, unattended, about 10:54 to 14:10 UTC. Model spend USD 0 (no model was called). Pulls: none. Reports: `archive/sessions/SESSION_3000_REPORT.md` to `SESSION_3023_REPORT.md`. Branch: `wip/3023-findings`, which holds every session's branch.

## The drafts, by family

All 156 drafts are rows of `public.scanner_drafts` under rule `hunt` (module `deep.<family>`), and all are still drafts. Each is at `/internal/findings` with its chart, its five tests, its CSV, its Python and Stata reproduction scripts, its pictures and its caption, and in `docs/findings/<family>/` as a document. The code is `warehouse/analysis/findings/deep/` (`builder.py` and one module a family).

| Family | Drafts | Sessions |
|---|---:|---|
| prices (ERCOT's hourly shape and spreads, Henry Hub, gas by state, world gas, carbon, Brent and WTI) | 33 | 3001 to 3003 |
| demand (EIA-930 by authority and by sub-region) | 12 | 3004 |
| generation and the pipeline (the mix, nuclear, heat rates, the build-out) | 35 | 3005 to 3007 |
| gas (the balance, states, flaring, Mexico, storage) | 11 | 3008 |
| queues, deals and datacenters (Queued Up; the Census datacenter series) | 27 | 3009 to 3011 |
| tariffs and policy (retail sales and prices, reliability, meters, net metering) | 12 | 3012 |
| oil, products and the world | 18 | 3013 to 3015 |
| across families | 8 | 3016 |
| all | 156 | |

- **Checked:**
  - All 156 reproduce from their own scripts, each run alone in an empty folder on the tables (`deep/check.py`).
  - All 156 cards hold against their own files (`deep/check_cards.py`).
  - All 156 do-files hold to your rules and to their Python twin (`deep/check_do.py`).
- **Corrected in place** (same ids, still drafts):
  - the ten queue drafts, on the fixed reader
  - new batteries' hours, from 2015
  - four sentences reworded
  - eleven do-files rid of `gsort` before `by`

## The twenty to read first

`docs/reviews/findings-ranked-2026-11-06.md` (session 3020) holds the rubric, its reasoning and every draft's rank. Its first twenty all score 9 (consequence 3, novelty 3, strength 3), ordered by strength. Among them:

- **Batteries entering service in the US:** 16,372.5 MW in 2025, against 0 in 2010.
- **Pipeline gas exports to Mexico:** 2,423 Bcf in 2025, against 14 in 1973.
- **Utility-scale solar's share of US net generation:** 6.8 percent in 2025, against 0.0 in 2001.
- **The gas fleet's heat rate:** 8.30 MMBtu per MWh in 2024, against 10.84 in 2001.
- **Pennsylvania's share of US marketed gas:** 17.8 percent in 2025, against 0.6 in 2001.
- **The average US residential price:** USD 172.6 per MWh in 2025, against 85.8 in 2001.
- **Private data center construction:** USD 49.7 billion in 2025, against 1.8 billion in 2014.
- **Batteries' share of the MW requested in queues:** 29.7 percent in 2024, against 0 in 2005.
- **Texas's share of US crude:** 42.2 percent in 2025, against 20.0 in 2001.
- **Canada's share of US crude imports:** 63.4 percent in 2025, against 30.9 in 1973.

Outside the top twenty but worth a look: CAISO's battery fleet at 46.6 percent of its peak days' average GW in 2025; ERCOT's cheapest hour moving from about 6 AM to near 11 AM; and the US median wait from request to operation at 62.8 months for 2024's projects.

## The landings done for the laptops

- **The old laptop's board (chain 165 and 167, the price board):**
  - Rows 1 and 2 landed at `0aa1dbd02` (session 3008 to 3012). The gate's first run failed on three older board tests that chain 165's changes broke. They were updated to its intended changes, and the gate passed.
  - Rows 3 to 8 landed at `6331a953a` (session 3016).
  - Every snapshot comparison: 0 differences. The request file's rows are marked.
- **This chain's own fix:** `/internal/findings` lists every draft, not the newest 100. It landed at `b86a54119`, alone, before 14:00, because this chain's 156 drafts had pushed the scanner's 66 older rows off the page.
- **The gate's check-values failed every time on main's two known floors** (`/deals`, `/learn/problems/know-your-grid`). Every other value matched, and check-routes, check-cross-checks and check-csp were run by hand on a build of the same commit, as chain 157 did.

## What did not finish, and why

- **The portable laptop's rows 1 (`wip/2252-deals`) and 2 (`wip/3059-policy`), and this chain's branch, are not landed.** The 14:00 to 16:15 UTC window closed with the old laptop's board and the review page's fix done. They are chain 166's first landings, after 16:15. The deals branch is merged with main in `C:\Users\Shared\Documents\erw-land2252`.
- **Families left to chain 166:** coal, uranium and metals; emissions and climate; the rest of the US tables; the markets' own operating tables (node basis, scarcity, stress days, the battery awards).
- **Not drafted, because the data cannot support a yearly finding:**
  - the AI-power deals by quarter, and the deals' prices (`energy_deals` begins in 2025, and its quarters follow the news taken in)
  - the facilities against each grid's peak (a partial inventory)
  - the planned pipeline's slippage (two months of snapshots)
  - EIA's capacity factors (2023 to 2025)
  - the chokepoints (they fail the tests; PortWatch is held internal)
- **Not deleted:** the 11 remote branches `wip/1600-board` to `wip/1610-board` (ancestors of main; the permission check refuses deleting remote branches).

## Decisions made without you

- The chain was taken through `chain_queue.take(who='lab-desktop-window2')`, because `next --file` refuses a window's name on a data machine. The first queue move went to main before a before snapshot; the comparison with the newest one was 0 differences.
- No model was called: every sentence is a template filled by code.
- Only ERCOT is hunted for hourly prices (CAISO holds three full years, PJM's hub history is not held, and four grids are held).
- A year of an annual or inventory series is one observation; the hunt's fullness rule by count misread them, three times, until fixed.
- Drafts are corrected in place, only while still drafts.
- Landings whose gate stopped on main's two known floors were completed with the remaining checks run by hand on the same commit.

## For Samuel's ruling

1. **`queue_divorce`:** the site's card read Queued Up through the faulty reader and understates it by 590 projects (14 of 19 numbers move). Should it be computed again once the fixed reader is on main?
2. **May this window delete the remote branches a landing makes ancestors of main?**
3. **Should `chain_queue.py next --file` take a file marked with a window's name** (`lab-desktop-window2`) on the desktop?
4. **Should the ERW keep EIA-860M's planned generators as a monthly snapshot,** so that the pipeline's slippage can be measured by year?
5. **ERCOT's reserve prices fell about 80 percent from 2018 to 2025** but fail the hunt's typical-move floor because of 2021 to 2023. Should a family whose middle years hold one event be tested without them?

## The cost

USD 0 of the model: no call was made. GitHub reads stayed under 60 per session, with the token.
