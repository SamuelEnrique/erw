# Redivis version 1 on the Stanford dataset: prepared for the click

Energy Research Warehouse (ERW), session 664 (chain 043, run on 22 October 2026 UTC), for Samuel. **Nothing was
released.** The click is the owner's (`warehouse/redivis/README.md`, "The rule"). 5 requests to Redivis's API, all reads.

## Where

- Dataset: `datapages.erw:b9wm`, the Datapages organization's (`https://stanford.redivis.com/datasets/b9wm-3hb080mtm`,
  DOI `10.57761/4f55-6d55`), public access `data`. The draft (`next`) was opened by session 661's first upload.
- ERW commit of the draft's code and records: `512e85af` on `wip/660-683-redivis-gaps` (the uploader's Stanford target is
  session 661's; the branch lands with this chain).
- The package for the dataset's page: [`docs/redivis/release-v1-stanford/`](../redivis/release-v1-stanford/) (`README.md`
  to paste as the description, `tables.csv` with each table's citation, `variables.csv` with 4,646 variables and
  columns), built by `python warehouse/redivis/release_v1.py --target stanford` and checked (`--check`, 0 differences).

## What the draft holds against the last release

The last release is **v1.0** (the dataset was created on 2 October 2026 by its `createdAt`; the answers read give no date for the release itself), one table:
`eia930_iso_hourly_demand_2019_2025` (429,525 rows), session 59's starter for Datapages. Against it, **every ERW table in
the draft is new**:

- **186 public tables, 45,816,802 rows, and the three metadata tables** (`erw_headers`, `erw_coverage` 290 rows,
  `erw_sources` 395 rows): every table whose ERW verdict in `docs/licenses.md` is `public`. The reconcile of this
  session: 188 of 188 match their CSVs (the 186 and `erw_coverage`, `erw_sources`), 45,817,197 rows.
- **The starter table** stays, as v1.0 held it.
- **Not in it:** 54 internal tables and 50 unsettled ones (`docs/reviews/redivis-v1-plan-2026-10-23.md` lists them).

**Session 680 added the chain's four public tables**, each proved: `utility_service_territories` (11,893 rows),
`interconnection_durations` (3,098), `interconnection_durations_summary` (1,365), `grid_peak_vs_capacity` (56), with their
header lines merged into `erw_headers` (2,736 lines). The draft now holds **190 public tables** (45,833,616 rows by the
CSVs), and `docs/redivis/release-v1-stanford/` lists 193 in v1 with the metadata tables, none held. **Session 687
refreshed `erw_coverage` and `erw_sources`** (uploaded before the four tables by session 663): `upload.py --target
stanford --prove-by-listing grid_peak_vs_capacity` sent the table again and then `erw_headers` (2,736 lines),
`erw_coverage` (294 rows) and `erw_sources` (398 rows), each proved by the draft's own count. **Session 688's reconcile**
(23 October 2026, 00:08 UTC, 5 requests) read the whole draft against this machine's files: 147 of 194 match; 45 differ,
every one because a daily run has added rows here since its upload (the files hold more, never fewer: `ercot_rtm_node_prices`
+29,952, `eia930_all_interchange` +8,112, `ercot_dam_esr_awards` +8,040, the rest smaller, `erw_coverage` 296 against 294
and `erw_sources` 399 against 398); 2 are chain 041's tables, public and never uploaded here
(`eia930_subba_demand_hourly_2021`, 710,831 rows; `eia_coal_production_annual`, 22,630). Nothing is wrong in the draft: it
is the warehouse as of 21 and 22 October. The list: `runs/c045/s688/redivis_reconcile_stanford.csv` on the data machine.

**The daily run the draft holds:** the data machine's tables as of 21 and 22 October 2026 (111 tables last run on 21
October, 19 on 22 October); 30 were last run here before 15 October (below).

## Five things to look at before clicking

1. **The version's number.** The ERW's documents call this release "version 1"; Redivis numbers it after v1.0, so its
   label on the site will be the dataset's second version. Name it in the release note (for example "ERW v1, Redivis
   v2.0"), or the citations in `tables.csv` (which say "version v1") will not match what a reader sees.
2. **The starter table.** `eia930_iso_hourly_demand_2019_2025` is not an ERW table of the warehouse's list and overlaps
   part of `eia930_all_demand`. Keep it (it is released and cited as v1.0), or delete it from the draft before the click
   (the draft only; v1.0 keeps it).
3. **Tables that stopped on this machine.** The draft holds the data machine's copies. 30 public tables were last run here
   before 15 October, because their daily refresh runs on GitHub's runner, which uploads to the old account's draft, not
   this one: among them `caiso_dam_cleared_energy`, `ercot_dam_cleared_energy`, `spp_dam_cleared_energy` and
   `caiso_area_load_hourly` (to 10 or 11 October), `eia_gas_storage_weekly` and `eia_petroleum_supply_weekly` (to
   2 October), `ercot_grid_notices` (to 15 October). Their windows end early, not wrongly; the daily run's move to this
   dataset (session 660's ruling) closes the gap.
4. **No table doubled or shrank.** Of the 128 tables that are also in the old account's draft, 124 hold the same rows
   and 4 grew by under 1 percent (`noaa_station_weather_hourly` +11,746, `noaa_grid_weather_hourly` +4,704,
   `noaa_grid_weather_daily` +294, `ercot_peak_premium_monthly` +168). The other 58 have never been on Redivis.
5. **The licenses as released.** The dataset's public access is `data`: on release every row is downloadable by anyone.
   Every table in the draft is public by its ERW verdict; spot-check three descriptions for their `License:` line
   (cut at Redivis's 2,000 characters; every line is in `erw_headers`), and note that the 50 unsettled tables (most of
   them by-grid tables held for ISO-NE's, MISO's and NYISO's terms) are absent by design.

## The click, in order

1. `python warehouse/redivis/upload.py --target stanford --reconcile` (read only): every row `match`, or a table that
   differs only because the daily run has grown it since its upload (session 688: 45 such, and 2 not uploaded). To release
   the newest copy instead, upload those first (`--target stanford --prove-by-listing <tables>`, about 5 requests a table).
2. On `stanford.redivis.com`, signed in with edit access to `datapages.erw`, open the draft (`next`).
3. Decide item 2 above; paste `docs/redivis/release-v1-stanford/README.md` into the description.
4. Click Release, with a note naming the ERW commit and the date of the run it holds.
5. Record the release date in `docs/redivis/release-v1-stanford/README.md`'s citation, and the label Redivis gave it.
