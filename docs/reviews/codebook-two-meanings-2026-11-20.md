# Names that mean two things: for Samuel's ruling (codebook, chain 630, part F)

Energy Research Warehouse (ERW). Found while the codebook (`warehouse/metadata/variables/`, `docs/codebook/`) was written from every table's header, method note, connector and rows, 20 November 2026. Nothing has been renamed and no data changed: each table's codebook file already says what the name means in that table (its `particular` or its label). Each item ends with one plain line for your ruling and the default taken until you rule.

## 1. The data standard's own names used for something else

The data standard (`docs/datastandard.md`, `/data/standard`) gives each of these one meaning; `warehouse/metadata/variables/_shared.yaml` defines it once.

### `node`: a pricing node, hub or zone

Used for other things in these tables:

- a county name: `census_county_population`; a metro or other name or label in every census table; a name or label in every eurostat table (27) and every World Bank table;
- a grid name: `grid_peak_vs_capacity`; an ISO name: `weather_obs_hourly`;
- a series name or identifier: `wb_commodity_prices_monthly`, the Federal Reserve tables (`frb_treasury_yields`, `frb_utility_output_monthly`);
- a weather station identifier: `event_window_daily`; an area name: `eia411_capacity_margins_annual`; a commodity: `imf_commodity_prices`; an auction number: `carb_auction_allowance_prices`;
- a sub-balancing-authority: `eia930_subba_demand_hourly`;
- in several ISO tables, a document title, a season and hour, an ancillary service or a price adder; in the cleared-energy tables a figure's name (`Total Demand`, `ISO_TOT_LOAD_MW`);
- a station: `noaa_region_stations`; a facility, fuel, segment, reactor or region in the EPA, NRC, ORNL, LBNL and DOE tables; a STATEC code, a flow, a gauge, a utility or an operator in the EIA-form, UK, Canada and federal tables; a mine, a reactor or utility name, or the ISO an airport stands for in the other sources; the publisher's row label in almost every national statistics table (empty in the KPX, Statnett and SvK tables; the month in the ZimStat table).

In short: `node` is a price location in the ISO price tables and the publisher's own row label in most others.

Ruling: keep `node` for price locations only, and move the other uses to a column of the table's own (`x_...`)? Default taken: unchanged; each file says what `node` holds there.

### `vintage`: when the publisher published the document, a UTC time

43 tables hold something else (read by `runs/c630/misuse.py` from the codebook's types): a date (most), a month (`storage_capacity`, `eia_hgl_pipelines`, "2020-01"), a year (`census_metro_population`, "2025"), an edition name (`eia_county_region`, "EIA-861 2025"; the eGRID tables, the edition), a filing due date (`ferc714_forecast_growth`, `ferc714_planning_area_forecasts`), or a file's Last-Modified time (`wb_commodity_prices_monthly`, `eia930_all_history`, `census_bps_state_annual`, and the API answer's in `wb_iea_electricity_annual`). Also: edition text in `interconnection_agreements_signed` and `ercot_node_wires_utilities` ("EIA-861 2025"), a retrieval time in `doe_lead`, a run id in `deal_counterparties`, edition or period text in `resource_layer_features`, an epoch date on one file of `irs_soi_energy_credits_annual`, and JSON-stat's `updated` field (which can be older than the newest data) in `ask_kosovo_electricity_monthly`, `csp_latvia_electricity_monthly` and `statgl_greenland_electricity_annual`. The full list is in each table's file (`vintage`, its `particular`).

Ruling: allow `vintage` to be a date as well as a UTC time, and move an edition name, a due date or a Last-Modified time to a column of its own? Default taken: unchanged.

### `geo`: an ISO 3166-2 code of the smallest region that holds the thing

- a country code (ISO 3166-1 alpha-2, Greece as GR, Eurostat's own) in all 27 eurostat tables, `wb_electricity_access_annual` and `eia_international_electricity_annual` (CA, MX, US); empty for the EU's aggregates;
- "US" for regions below the country (the petroleum districts, storage regions, producing basins, state crude prices) in five EIA tables;
- a country code in the Energy-Charts tables and the other non-US national tables; the country even on regional rows (the CZSO, NVE, EMI and INE tables); GB for the whole United Kingdom in the DESNZ tables;
- US-MX on 18 rows of `caiso_interconnection_queue`; empty in the BPA, eGRID, GFZ, IRENA and PortWatch tables and on every OWID row; `noaa_ncei_storm_events` keeps its place in `x_geo` instead.

Ruling: let the standard say a country is written by its ISO 3166-1 code, and give a region below the country that has no ISO code a column of its own? Default taken: unchanged.

### `market`: the market the value belongs to (`ercot_dam`)

Holds the ISO's name, not a market code, in `iso_trader_daily` and `iso_rt_top_intervals`; a product (`bra`, the capacity auction) in the internal `pjm_rpm_capacity_prices`.

Ruling: write the market code there as elsewhere? Default taken: unchanged.

### `capacity_mw`: nameplate capacity

Holds the request's peak load in `nyiso_load_queue` (a load queue, not generators).

Ruling: move the load to a column named for it (`x_peak_load_mw`)? Default taken: unchanged.

### `entity_ids`: the `entity_id` values of things involved

Holds table names in `known_data_faults`, and US state codes in the internal `treasury_1603_awards`.

Ruling: rename it in those two (`x_tables`, `x_states`)? Default taken: unchanged.

### `entity`, `status`, `price` and `year`: one table each, or a few

- `entity` is a county in `noaa_region_stations`, and the C&SD table code (not a place) in `censtatd_hk_electricity`.
- `status` is the catalogue's review status in `usgs_comcat_earthquakes_south_central`, not a thing's or a deal's state.
- `price` is in USD per kW, not per MWh, in `lbnl_wind_turbine_orders`.
- `year` is the matrix's calendar year in the internal `texas_transmission_matrix`, not the operating year a history table was published by.
- `ts_utc` marks the gas year in the DESNZ gas rows.

Ruling: none needed if each file's words stand (they say so); otherwise a column of the table's own for each. Default taken: unchanged.

### `variable` taking the value `value`

In `eia_seds_state_energy`, `eia_steo_forecasts` and both AEO tables the variable is named `value`, and its rows carry several units; what was measured sits in the table's own columns.

Ruling: let the builders write the measure's name as the variable? Default taken: unchanged.

## 2. Variables and words whose meaning depends on the table

- `spp_dam` and `spp_rtm` on ERCOT's rows mean ERCOT's settlement point price, not the grid SPP (Southwest Power Pool). Ruling: none needed; the codebook says so in each ERCOT file.
- `iso_status` "Completed" in `ercot_interconnection_queue` is ERCOT's word for a signed interconnection agreement, not a plant in operation. Ruling: none needed; the label says so.

## 3. The tables' own column names that two or more tables use for different things

- `confidence`: the model's confidence from 0 to 1 that a row is real (`datacenter_facilities`, `datacenter_projects`, `energy_deals`); a match rule's confidence, 0.7 to 1.0 (`company_aliases`, `company_links`); a score from 0 to 100 by the Thesis Builder's rule (`energy_companies`). Ruling: give the 0 to 100 score its own name (`x_score`)? Default taken: unchanged.
- `grid`: a US grid operator in the datacenter, deal, company and large-load tables; Berkeley Lab's region (the seven ISOs, West and Southeast) in `interconnection_durations`. Ruling: rename it `region` there, as `lbnl_interconnection_queue` does? Default taken: unchanged.
- `region`: four systems: the UK's regions (`desnz_uk_power_stations`), Berkeley Lab's regions (`lbnl_interconnection_queue`, `lbnl_solar_projects`, the latter with AK and HI), and a story's state, country or "global" written by the model (`news_index`). Ruling: none needed if each file's label stands; otherwise prefix the publisher. Default taken: unchanged.
- `kind`: the kind of opposition (`attention_story_links`), of company (`company_directory`), of source (`datacenter_facilities`), of counterparty (`deal_counterparties`), of deal (`energy_deals`), or operating, planned or queue (`energy_projects`). Ruling: none needed; a generic word, defined per table. Default taken: unchanged.
- `state`: a two-letter postal code everywhere, but several codes joined by ";" in `company_links`, and the regulator's state or the states served in `large_load_public`. Ruling: none needed; the label says so. Default taken: unchanged.

- `x_period`, `x_table` and `x_label`: the publisher's period, table and label, each in its own system, in the national statistics tables. Ruling: none needed; generic words, defined per table. Default taken: unchanged.

Names that differ only in wording (`county`, `queue_id`, `plant_id`, `balancing_authority` and others) are not listed: they mean the same thing in every table.

## 4. Faults found on the way (not rulings)

- `interconnection_queue_summary`: the `active_mw_parts_*` variables carry unit `count` but are MW (the builder's `unit_of`). Data request 564 in `docs/state/data_requests_done_line.md`.
- `eia930_region_hourly`, `x_basis`: the method note says "mixed" where a sum is not all adjusted; the data holds only "adjusted" and "reported".
- `ai_power_regions`, `net_import_share_pct`: the report appendix defines it differently from the header and the builder.
- `eia_ieo_projections`, `x_history`: the data holds HISTORIC where the header says HISTORY.
- `eia860` tables: `x_sector` and `x_sector_name` hold the reverse of EIA's headings.
- ORNL's hydropower tables: `huc` holds 11 to 12 digits where ORNL's field description says 10, and five capacity factors exceed ORNL's stated 120 percent cap.
- `texas_transmission_matrix` (internal): the header says the 2026 matrices are "filed"; the connector and the data say approved.
- `ferc_eqr_buyer_doubtful` (internal): `x_rows_a` and `x_rows_b` count the rows of each name's whole group, not of the single name the header describes.
- Several EIA headers carry stale lines (a "survey Monday", "the Outlook's crude", "every run replaces"); the codebook follows the code and the method notes.
