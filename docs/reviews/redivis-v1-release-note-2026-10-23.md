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

**Session 863 (23 October 2026, 02:23 UTC)** uploaded 14 public tables with the true replace, each proved by the draft's
count (`upload.py --target stanford --prove-by-listing --tables`, which merges their header lines into `erw_headers`,
2,866 lines, and touches no other table): chain 041's `eia930_subba_demand_hourly_2021` and `eia_coal_production_annual`;
chain 045's `eia_coal_mine_production_annual`, `eia861_utility_reliability`, `eia930_subba_demand_hourly_2020` and the
rewritten `eia861m_utility_sales_monthly` (1,051,488 rows, EIA's aggregates out); chain 046's `ercot_cdr_reserve_margins`,
`ercot_transmission_projects`, `eia861_delivery_only`, `interconnection_agreements_signed`,
`interconnection_agreements_by_grid`, `eia930_subba_demand_hourly_2019`, `eia_petroleum_exports_by_destination`,
`eia_gas_consumers_state_annual`. The reconcile after it: 160 of 205 match; the 45 that differ are the 43 tables a daily
run has grown since their upload and `erw_coverage` (296 rows here, 294 in the draft) and `erw_sources` (407 against 398),
which a plain upload refreshes. 100 requests in all (`runs/c046/s863/`).

**Session 878 (23 October 2026, 03:46 UTC)** uploaded chain 047's ten public tables (EIA-861's utility data, demand response, dynamic pricing, advanced meters, net metering and short form; ERCOT's CDR units; EIA-860's plants; EIA's coal receipts) and `eia861_delivery_only` again, each proved; `erw_headers` holds 2,946 lines, all but the coal receipts' (the ceiling came first). Reconcile: 169 of 214 match; the 45 that differ are, as before, the tables a daily run has grown and the two metadata tables.

**Session 880 (23 October 2026, 03:54 UTC):** five small grown tables, the coal receipts' header lines, `erw_coverage` (316 rows) and `erw_sources` (416 rows) refreshed; reconcile 176 of 214 match. **`ercot_wind_solar_hsl_hourly` is empty in the draft** (its replace was cut off by a request cap): upload it again before the click.

**Session 892 (23 October 2026, 05:22 to 05:27 UTC):** `ercot_wind_solar_hsl_hourly` uploaded again and proved (8,760 rows); the draft no longer holds an empty table. A second request cap fell inside `erw_headers`' true replace (its estimate of 12, then 30, requests for one table and the header merge was too low), which left it empty for four minutes; it was rebuilt in full from this machine's 212 public tables (2,958 lines, proved; every table in the draft is on this machine, so no line was lost). Reconcile: 176 of 214 match; the 38 that differ are tables a daily run has grown since their upload. Chain 048's thirteen new or changed public tables were not uploaded (63 of the session's 100 requests spent): chain 049's session 906 uploads them. Nothing released.

**Session 906 (23 October 2026, 07:04 to 07:11 UTC):** chain 048's thirteen tables and five of chain 049's (`eia411_capacity_margins_annual`, `eia_power_costs_annual`, `eia_uranium_marketing_annual`, `ercot_node_places`, `eia_gas_pipeline_projects`) uploaded with the true replace, each proved by the draft's count; `erw_headers` holds 3,127 lines. 149 of 150 requests. Reconcile: 192 of 238 match; 39 differ (tables a daily run has grown since their upload, and `erw_sources`, 416 in the draft against 428 here, which a plain upload refreshes); 7 are not yet in the draft (among them chain 049's EIA-860 environmental and multifuel tables and EIA-923's monthly and receipts tables, for chain 051's session 919). Nothing released.

**Session 919 (23 October 2026, 08:48 to 08:52 UTC):** fifteen tables uploaded with the true replace, each proved by the draft's count: the eight chain 049 left out or stale (`eia860_boilers`, `eia860_cooling_systems`, `eia860_emission_controls`, `eia860_multifuel_generators`, `eia923_plant_fuel_monthly` with 660,531 rows, `eia923_fuel_receipts`, and `eia411_capacity_margins_annual` and `eia_gas_pipeline_projects` again after session 905's fixes) and chain 051's seven (`eia_world_electricity_annual`, `cer_gas_trade`, `ornl_eha_hydropower_plants`, `eia_aeo_emm_regions`, `lbnl_ppa_prices`, `ornl_hydropower_pipeline`, `ercot_node_transmission`); `erw_headers` holds 3,256 lines. 104 of 150 requests (98 for the upload, one run, no cap inside a table; 6 for the reconcile). Reconcile: 205 of 245 match; 39 differ (tables a daily run has grown since their upload, `erw_coverage` and `erw_sources`, which a plain upload refreshes); none is missing from the draft. Nothing released.

**Session 933 (23 October 2026, 10:25 to 10:30 UTC):** chain 052's seven public tables uploaded with the true replace, each proved by the draft's count (`eia_world_oil_gas_annual`, `eia_world_oil_monthly`, `nrc_power_reactors`, `wb_commodity_prices_monthly`, `eia_power_fuel_stocks_monthly`, `ornl_hydropower_relicensing`, `ercot_node_planned_generation`), in a plain upload that also refreshed `erw_coverage` (353 rows) and `erw_sources` (451) and rebuilt `erw_headers` in full from disk (3,335 lines; the lines of tables not on this machine kept as the draft had them). 92 of 150 Redivis requests (86 for the upload, 6 for the reconcile). Reconcile: 214 of 252 match; 37 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.

**Session 947 (23 October 2026, 11:35 to 11:41 UTC):** nine public tables uploaded with the true replace, each proved by the draft's count: chain 053's eight (`eia_world_coal_annual` with 317,307 rows, `eia_world_energy_co2_annual`, `ornl_npd_potential`, `lbnl_solar_projects`, `lbnl_hybrid_ppa_prices`, `ornl_eha_hydropower_units`, `lbnl_wind_capacity_factors`, `ercot_node_wires_utilities`) and `uswtdb_wind_turbines` (77,839), settled public by session 888 and never uploaded; in a plain upload that also refreshed `erw_coverage` (361 rows) and `erw_sources` (457) and rebuilt `erw_headers` (3,414 lines). 102 of 150 Redivis requests (6 for a first reconcile, which found the nine; 90 for the upload, one run under a cap of 130, no cap inside a table; 6 for the last reconcile). Reconcile: 223 of 260 match; 37 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.

**Session 961 (23 October 2026, 13:01 to 13:09 UTC):** chain 054's eleven public tables uploaded with the true replace, each proved by the draft's count (`onrr_production_monthly`, `onrr_production_annual`, `onrr_revenue_monthly` with 413,554 rows, `lbnl_wind_costs`, `lbnl_wind_turbine_orders`, `eia_primary_energy_monthly`, `usgs_mcs_critical_minerals`, `blm_ca_renewable_rows`, `eia_coal_distribution_quarterly`, `eia_uranium_production_quarterly`, `eia_uranium_facilities`), in a plain upload that also refreshed `erw_coverage` (372 rows) and `erw_sources` (463) and rebuilt `erw_headers` (3,526 lines); `usgs_mcs_critical_minerals` in a second run, since the uploader's validator on main does not yet know the units `t` and `USD/kg` (Decision 56, on the branch). 142 of 150 Redivis requests (6, 93, 37 and 6). Reconcile: 234 of 271 match; 37 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.

**Session 988 (23 October 2026, 16:38 to 16:42 UTC):** chain 055's public tables uploaded with the true replace, each proved by the draft's count: `eia_ieo_projections` (17,856 rows), `eia_capacity_factors_annual` (374), `eia_capacity_factors_monthly` (1,224), `eia_heat_rates_annual` (44), `egrid_subregions_annual` (540), and `usgs_mcs_critical_minerals` written again with session 981's ten chapters (1,600, from 692), in a plain upload that also refreshed `erw_coverage` (379 rows) and `erw_sources` (468) and rebuilt `erw_headers` (3,576 lines). `lbnl_hybrid_plants` is internal and `usace_nid_dams` has no verdict (session 983), so the target does not take them. 88 of 150 Redivis requests (6, 76 and 6), and 1 to Supabase. Reconcile: 239 of 276 match; 37 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.

**Session 2038 (23 October 2026, 19:58 to 20:02 UTC):** chain 058's public tables uploaded with the true replace, each proved by the draft's count: `doe_oe417_events` (3,313 rows), `epa_rfs_rins_monthly` (1,632), `epa_rfs_fuel_annual` (568), `eia_biofuel_plants` (511), `msha_coal_mines` (35,736), `msha_coal_production_quarterly` (294,323), `fhwa_motor_fuel_monthly` (7,998) and `afdc_vehicle_registrations_annual` (6,240), in a plain upload under the data lock that also refreshed `erw_coverage` (393 rows, from this chain's branch, which holds chain 056's tables but not chain 057's: that chain's next plain upload or landing puts its rows back; chain 057's session 2024 had left it empty) and `erw_sources` (479) and rebuilt `erw_headers` (3,820 lines). The uploads ran with the branch's validator, which knows the unit `gal` (Decision 59). `eaglei_county_outages_daily` is not written (session 2029); chain 057's rewritten `eia_cbecs_commercial_buildings` has no verdict in this branch's record, so its own chain uploads it. 107 of 150 Redivis requests (6, 94 and 7), and 1 to Supabase. Reconcile: 236 of 282 match; 46 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.

**Session 2094 (23 October 2026, 21:49 to 21:52 UTC):** chain 068's public tables uploaded with the true replace, each proved by the draft's count: `irs_soi_energy_credits_annual` (1,074 rows), `eia_state_to_state_capacity` (19,311) and `noaa_cpc_oni_monthly` (1,840), in a plain upload under the data lock with the branch's validator (the unit `degC`, Decision 62), which also refreshed `erw_coverage` (413 rows, the branch merged with chain 066's landing) and `erw_sources` (499) and rebuilt `erw_headers` (3,930 lines). `irena_capacity_annual` is internal (IRENA's terms unread), so the target does not take it. 79 of 150 Redivis requests (7, 65 and 7), and 1 to Supabase. Reconcile: 257 of 303 match; 46 differ, every one a table a daily run has grown since its upload; none is missing from the draft. Nothing released.
**Session 2024 (23 October 2026, 19:09 to 19:24 UTC):** chain 056's six public tables (its session 2010 did not run) and chain 057's five, uploaded with the true replace, each proved by the draft's count: `doe_useer_employment` (3,311 rows), `nrc_new_reactor_applications` (6), `nrc_advanced_reactor_preapplicants` (43), `usbr_hydropower_monthly` (31,702), `noaa_cpc_degree_days_daily` (118,900), `boem_offshore_platforms` (7,092, in a second run with the branch's validator, which knows the entity type `platform`), `eia_mecs_manufacturing` (5,363), `eia_cbecs_commercial_buildings` (5,944), `eia_recs_households` (2,802), `lbnl_tracking_the_sun` (8,762) and `eia_lng_liquefaction_projects` (48). The first plain upload refreshed `erw_coverage` (391 rows) and `erw_sources` (479) and rebuilt `erw_headers` (3,689 lines); `eia_ice_electricity_daily` is internal, so the target does not take it. **`erw_coverage` is empty in the draft:** the second run's request cap (40) fell inside its replace, which deleted the table, and the session's last 6 requests re-created it but could not upload its rows. Chain 058's session 2038 refreshes the metadata tables in its plain upload; until then, or a run of `python warehouse/redivis/upload.py --target stanford` with any table, the draft's coverage table has no rows. Do not click before it does. 150 of 150 Redivis requests (6, 92, 40, 6 and 6), and 3 to Supabase for the lock. Reconcile: 242 of 287 match; 44 differ, every one a table a daily run has grown since its upload; none is missing. Nothing released.

**Session 2066 (23 October 2026, 20:42 to 20:52 UTC):** `erw_coverage`, which session 2024 left empty, had already been refilled by chain 059's and chain 067's plain uploads (401 rows at the first reconcile). Chain 057's rewritten `eia_cbecs_commercial_buildings` (5,944 rows, its categories' ids joined across EIA's tables) and chain 066's `fema_disaster_declarations` (26,199), `nhc_hurdat2_track_points` (27,812) and `nrc_license_actions` (236) uploaded with the true replace, each proved by the draft's count, in a plain upload that refreshed `erw_coverage` (401) and `erw_sources` (489) and rebuilt `erw_headers` (3,890 lines). `usdm_drought_state_weekly` has no verdict yet, so the target does not take it. 93 of 150 Redivis requests, and 1 to Supabase. Reconcile: 251 of 295 match; 44 differ, every one a table a daily run has grown since its upload; none missing. **The draft's metadata tables are the last uploading branch's:** before the click, a plain upload from main after every chain has landed. Nothing released.

**Session 2116 (23 October 2026, 22:46 to 22:57 UTC):** a first reconcile found every table of chains 066, 067 and 068 in the draft (312 tables: 261 match, 46 differ, every one a table a daily run has grown, or the metadata tables), and this chain's five public tables not yet uploaded. `blm_oil_gas_statistics_annual` (12,500 rows), `noaa_uscrn_solar_monthly` (2,025), `eia_seds_residential_annual` (20,020), `cec_total_system_generation_annual` (795) and `usgs_streamflow_daily` (33,421) were uploaded with the true replace, each proved by the draft's count, in a plain upload that refreshed `erw_coverage` (419) and `erw_sources` (505) and rebuilt `erw_headers` (3,980 lines). `treasury_1603_awards` is not settled (the Treasury states no terms) and is held internal, so the target does not take it. 91 of 150 Redivis requests (7, 77 and 7), and 1 to Supabase. Reconcile: 268 of 312 match, 44 differ (daily-grown tables), none missing. After the upload the method notes' checks rewrote three of these tables' headers or `retrieved_at` (the Energy Commission's license line, SEDS's retrieval times); the draft holds the earlier words until the next plain upload. Nothing released.

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

## After the click: prove the release in each language (session 1010, chain 070)

Once the version is released, each package reads it by default (Redivis's latest released version), and the version line and the citation name its tag. Set your Redivis token first (`REDIVIS_API_TOKEN`). The three fetches below should each give 247 rows, Henry Hub's daily price in 2025 (conformance call 1, `packages/conformance/conformance.json`), and each citation should end with the tag Redivis shows.

Python (`pip install "erw-energy[redivis] @ git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"`):

```python
import erw
df = erw.fetch("eia_fuel_spot_prices", entity="eia:henry_hub", start="2025-01-01", end="2026-01-01", backend="redivis")
print(len(df), df.attrs["erw"]["version_line"]); print(erw.cite("eia_fuel_spot_prices", backend="redivis"))
```

Stata (`net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace`):

```stata
global REDIVIS_API_TOKEN "your token"
erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) backend(redivis) clear
erw cite eia_fuel_spot_prices
```

R (`remotes::install_github("SamuelEnrique/erw", subdir = "packages/r/erw")`):

```r
Sys.setenv(REDIVIS_API_TOKEN = "your token")
h <- erw::erw_fetch("eia_fuel_spot_prices", entity = "eia:henry_hub", start = "2025-01-01", end = "2026-01-01", backend = "redivis")
print(c(nrow(h), attr(h, "erw_version"))); print(erw::erw_cite("eia_fuel_spot_prices", h))
```

What session 1010 found on the way (23 October 2026, 11 of its 100 Redivis requests outside the remote test, all reads):

- **The Stata and R packages read Redivis through `https://redivis.com/api/v1/tables/<reference>/rows?format=csv`**, the address Redivis's own client reads small tables with. Redivis answered on it. For the draft, though, the answer was the 100 GB streaming cap of the token's user ("Cannot stream more than 100GB to external environments within a 30 day period. Please use the export API instead."), so the CSV form itself is not yet proven. A reader under the cap is not affected. The Python package falls back to the export when the cap answers (session 665), and the Stata and R packages do not yet.
- **The released v1.0 holds no ERW table** (404 on `datapages.erw:b9wm.eia_fuel_spot_prices`), as this note says: until the click, the packages' default reads find only the starter table, and they say so.
- **The draft against the record**: 207 tables listed. Of the 203 in `coverage.csv`, 160 have its row count, and 43 have fewer rows than the record, each a table that grew after its upload. None has more.
- **`docs/redivis/release-v1-stanford/tables.csv`** now carries each table's fetch line in each package (`fetch_python`, `fetch_stata`, `fetch_r`), and the dataset's `README.md` a section "Read it in Python, Stata or R" (`python warehouse/redivis/release_v1.py --target stanford --calls-only`). `release_v1.py --check` reports 13 tables the record now puts in version 1 that the table list lacks (the data machine's new tables since session 664). A rebuild of the list on the data machine, which holds the tables, adds them: `python warehouse/redivis/release_v1.py --target stanford`.

## Chain 059's upload (session 2052, 23 October 2026, 19:28 to 19:32 UTC)

- **Five public tables uploaded to the Stanford draft, each proved by the draft's count:** `noaa_ncei_storm_events` (411,139), `nrc_event_notifications` (25), `doe_lng_export_applications` (135), `noaa_climdiv_state_monthly` (31,458) and `doe_grip_selections` (105). `ornl_tedb_transportation_annual` is internal and not uploaded.
- **The three metadata tables were refreshed by the same run:** `erw_headers` (3,739 lines), `erw_coverage` (385 rows) and `erw_sources` (473). So `erw_coverage`, which chain 057's session 2024 left empty, holds rows again; they are main's coverage as it stood at 19:32 UTC (chain 056's tables included, chains 057, 058 and 059's not), because the run's metadata step read the main checkout's files after this session had put main's back (the run's shell was stopped for low memory while its Python went on).
- **Two of the five were written again after the upload** (session 2052's corrections): `noaa_ncei_storm_events` now codes the territories' 690 rows, and `nrc_event_notifications` gives every last update as a date. Their row counts are unchanged, so a reconcile counts them as matching; the draft holds the versions before the corrections until a later upload.
- **No reconcile after the upload:** 80 of the session's 150 requests were spent (6 and 74); the last reconcile was part of the run the system stopped.
- Nothing released. **Samuel: do not click before chains 057, 058 and 059 have landed and a full upload has refreshed `erw_coverage` with their tables** (chain 058's session 2038 or chain 066's session 2066).

## Chain 067's upload (session 2080, 23 October 2026, 20:30 to 20:33 UTC)

- **Four public tables uploaded to the Stanford draft, each proved by the draft's count:** `ieso_ontario_demand_hourly` (31,680), `aeso_alberta_load_hourly` (15,853), `epa_ghgrp_facility_emissions` (70,338) and `noaa_ncei_billion_disasters` (403).
- **The metadata tables refreshed from a branch that holds chains 057, 059 and 067's tables:** `erw_coverage` 401 rows (chain 059's upload had left main's 385), `erw_sources` 489, `erw_headers` 3,860 lines.
- **A reconcile:** 292 tables, 248 match, 44 differ (tables daily runs have grown since their upload), none missing.
- **Two tables' headers in the draft are their earlier ones** (`epa_ghgrp_facility_emissions`, `noaa_ncei_billion_disasters`, written again for their headers' words after the upload; same rows).
- Nothing released. **Samuel: do not click before chains 058 and 066 have landed and uploaded their tables.**

## Chain 079's upload (session 2130, 23 October 2026, 23:21 to 23:28 UTC)

- **Five public tables uploaded to the Stanford draft, each proved by the draft's count:** `usgs_comcat_earthquakes_south_central` (16,000), `epa_tri_energy_releases_annual` (384,483), `eurostat_renewable_capacity_annual` (49,313), `owid_ember_electricity_annual` (12,406) and `epa_lmop_landfill_projects` (3,399).
- **The metadata tables refreshed from this chain's branch:** `erw_coverage` 418 rows, `erw_sources` 505, `erw_headers` 4,032 lines. The branch was cut before chain 068 landed, so this `erw_coverage` lacks chain 068's four tables (and chain 069's, unlanded); session 2133 refreshes it again from the branch merged with main (a plain upload of one small table, within this session's ceiling).
- **Two reconciles:** before, 312 tables, 262 match, 45 differ, none missing; after, 268 match, 44 differ (tables daily runs have grown since their upload), none missing.
- 94 requests of 150. Nothing released. **Samuel: do not click before chain 069 has landed and uploaded its tables, and an upload has refreshed `erw_coverage` from main.**
