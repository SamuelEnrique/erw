# Session 2228 report: six held tables linked to their method notes (the trader view, the network links, the event interchange, three ERCOT and queue summaries)

24 October 2026, from 02:37 UTC, on lab-desktop (the data machine), chain 099, unattended. A helper agent drafted the notes in the chain's worktree while sessions 2227, 2230 and 2231 ran. This session checked them. Model spend USD 0. Pulls: none.

## Read these first

- **The chain file names `desnz_uk_renewables_quarterly`** among this session's tables, but chain 098's session 2214 has written its note on `wip/2210-2223-data`, so it is not written twice. Chain 098's agent listed its notes (sessions 2214, 2218, 2221, 2222) and chain 097's (session 2180); none of those tables is taken here.
- **The tables:** those whose Method cell in `docs/coverage.md` is empty and that the notes on main and on the running chains' branches name least.
- **Three `Tables:` lines,** where an existing note already describes the table in full, nothing else changed:
  - `ercot_storage_dam_offers_monthly` in `docs/methods/ercot_storage_dam_offers.md` (its 9 months, 819 rows, 91 variables match the file);
  - `ercot_peak_premium_monthly` in `docs/methods/ercot_peak_premium.md` (28 variables, 6 hubs);
  - `interconnection_durations_summary` in `docs/methods/interconnection_durations.md` (1,365 rows, 9 entities).
- **Three new notes:**
  - `docs/methods/iso_trader_daily.md`:
    - 16,618 rows, 39 hubs, 26 August to 24 October 2026, the sum of its six members.
    - `da_mean_usd` and `implied_heat_rate` recomputed from the price tables and Henry Hub: 2,150 of 2,150 agree.
    - MISO ends 3 October (paused).
  - `docs/methods/grid_network_links.md`:
    - 22,608 rows, 157 pairs, 70 balancing authorities, 144 hours.
    - Recomputed from `eia930_all_interchange` by the pair rule: 22,598 agree within 0.05 MW.
  - `docs/methods/eia930_event_hourly_interchange.md`:
    - 266,833 rows over Winter Storm Uri and the June 2025 heat.
    - Its demand agrees with `eia930_daily_demand` on 1,147 of 1,148 and 573 of 603 days.
- **Checked by this session,** recomputed from the tables read past their header lines: the trader table's rows, hubs and dates; the links' rows, pairs and hours; the event table's 223,176 interchange and 43,657 demand rows. Each agrees with its note.
- **The six Method cells set** by `build_coverage.py`'s own lookup; nothing else on the lines changed.

## Contradictions found, written into the notes, no code changed

1. **`eia930_event_hourly.py`** (lines 23 and 24) says demand is kept "not for EIA's regional sums". The code's filter keeps 14 regions among the respondents (6,048 and 3,024 rows).
2. **`iso_trader_daily`'s header** (written by `warehouse/consolidate.py`) says "ts_utc is interval start, UTC". The rows give the local operating day at 00:00:00Z.
3. **`iso_trader_daily`'s header says "License: public".** The license record says "needs written permission" (ISO-NE, NYISO, MISO). `sources.csv`'s `erw:trader_view` row does not list the table. **For a code session:** the header's license line.
4. **`grid_network.py` and its note say "the last 168 hours";** the file holds 144, since `eia930_all_interchange` has no hour of 14 or 15 October.
5. **`grid_network_links`' header** names `eia930_all_demand` and `carbon_intensity_hourly`, which feed only the nodes table.
6. **`eia930_event_hourly.py` asks neither `paused()` nor `paused_host()`;** `iso_prices.py`'s request hook checks no pause either, though CLAUDE.md says `paused_host()` refuses a paused publisher's host "whatever the caller". **For a code session.**

## Decisions made without you

- **The notes drafted by a helper agent and checked here.**
- **Other chains' notes respected;** `desnz_uk_renewables_quarterly` left to chain 098.
- **`ercot_storage_dam_offers_daily`, `ercot_peak_premium_annual` and `grid_network_nodes`** are also unlinked, and their notes describe them. They are left for a later session, to stop at six.

## For Samuel's ruling

- None new.

## Files

- New: `docs/methods/iso_trader_daily.md`, `grid_network_links.md`, `eia930_event_hourly_interchange.md`, this report.
- Changed: `docs/methods/ercot_storage_dam_offers.md`, `ercot_peak_premium.md`, `interconnection_durations.md` (a `Tables:` line each), `docs/coverage.md` (six Method cells).
