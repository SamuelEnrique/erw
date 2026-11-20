# Codebook: interchange

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 derived); 3 documented in full.

- [`interchange_event_pairs`](#interchange_event_pairs): One pair of balancing authorities, or of EIA's regions, over the window of one of the nine events of /events in one year (the event's own year or the same calendar dates in another year held), interchange summed over the window.
- [`interchange_pair_daily`](#interchange_pair_daily): One pair of balancing authorities, or of EIA's regions, and one Eastern day, the interchange between them with each side's report, their mean and gap, July 2018 on.
- [`interchange_pair_monthly`](#interchange_pair_monthly): One pair of balancing authorities, or of EIA's regions, and one Eastern month, the interchange between them with each side's report, their mean and gap.

### `interchange_event_pairs`

One pair of balancing authorities, or of EIA's regions, over the window of one of the nine events of /events in one year (the event's own year or the same calendar dates in another year held), interchange summed over the window.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 13574.

- **Time:** ts_utc is the window's first hour (midnight of its first day in Eastern time), x_window_end the hour after its last (midnight after its last day in Pacific time); freq PT1H, hourly data summed.
- **Revisions:** One build, rebuilt whole by each run of the builder; no vintage column.
- **Source:** erw:interchange_pairs ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interchange_pairs.md)
- **Method note:** [`docs/methods/interchange_pairs.md`](../methods/interchange_pairs.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Who trades with whom: interchange by pair of balancing authorities and of regions, partners, events (docs/methods/interchange_pairs.md). Via the Energy Research Warehouse (ERW), table `interchange_event_pairs`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<A>-<B>, A before B by code | none | text | for example eia930:AEC-MISO, eia930:AEC-SOCO, eia930:AECI-MISO; 204 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-08-01T04:00:00Z to 2026-08-31T04:00:00Z; 75 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -216228202.5 to 93783010.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interchange_pairs | 0 |
| `x_level` | The level of the pair: ba for two balancing authorities, region for two of EIA's regions | none | text | ba, region | 0 |
| `x_a` | A, the first party of the pair (the code that sorts first), EIA-930 code | none | text | for example AEC, AECI, AESO; 73 distinct | 0 |
| `x_b` | B, the second party of the pair, EIA-930 code | none | text | for example BPAT, CENT, CHPD; 65 distinct | 0 |
| `x_event` | The event of /events whose dates set the window (its dates in event_window.py) | none | text | caiso_heat_2020, caiso_heat_2022, cold_2025, cold_2026, covid_2020, east_heat_2025, elliott_2022, ercot_heat_2023, uri_2021 | 0 |
| `x_year` | The year of the window | none | integer | 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 | 0 |
| `x_role` | event for the event's own window, other_year for the same calendar dates in another year | none | text | event, other_year | 0 |
| `x_window_end` | The hour after the window's last hour, UTC | none | utc time | 2018-08-25T07:00:00Z to 2026-09-11T07:00:00Z; 75 distinct | 0 |
| `x_basis` | What value is: mean (the mean of the two reports over the hours both reported), a or b (only that side reported) | none | text | a, b, mean | 0 |
| `x_a_report_mwh` | The sum of A's reported hours, read as power from A to B | MWh | integer | -10739568 to 190237466; more than 5000 distinct | 1278: A reported no hour of the window (x_basis b) |
| `x_b_report_mwh` | The sum of B's reported hours, turned to the direction from A to B | MWh | integer | -430973860 to 11355054; more than 5000 distinct | 272: B reported no hour of the window (x_basis a) |
| `x_gap_mwh` | Over the hours both reported, A's report less B's | MWh | integer | -18173777 to 429491315; 3956 distinct | 1550: No hour of the window has both reports |
| `x_hours_a` | The hours A reported | hour count | integer | 0 to 2210; 107 distinct | 0 |
| `x_hours_b` | The hours B reported | hour count | integer | 0 to 2210; 126 distinct | 0 |
| `x_hours_both` | The hours both reported | hour count | integer | 0 to 2210; 163 distinct | 0 |
| `x_direction` | a_to_b when value is above zero, b_to_a below, none at zero | none | text | a_to_b, b_to_a, none | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `interchange_mwh` | Interchange from A to B summed over the window: the mean of the two sides' reports over the hours both reported, else the one side that reported (x_basis) | MWh | 13574 | 2018-08-01T04:00:00Z | 2026-08-31T04:00:00Z |

### `interchange_pair_daily`

One pair of balancing authorities, or of EIA's regions, and one Eastern day, the interchange between them with each side's report, their mean and gap, July 2018 on.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 553108.

- **Time:** ts_utc is the Eastern day at 00:00:00Z (freq P1D), a label.
- **Revisions:** One build, rebuilt whole by each run of the builder; no vintage column.
- **Source:** erw:interchange_pairs ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interchange_pairs.md)
- **Method note:** [`docs/methods/interchange_pairs.md`](../methods/interchange_pairs.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Who trades with whom: interchange by pair of balancing authorities and of regions, partners, events (docs/methods/interchange_pairs.md). Via the Energy Research Warehouse (ERW), table `interchange_pair_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<A>-<B>, A before B by code | none | text | for example eia930:AEC-MISO, eia930:AEC-SOCO, eia930:AECI-MISO; 205 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-18T00:00:00Z; 3063 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -214770067.5 to 10183497.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interchange_pairs | 0 |
| `x_level` | The level of the pair: ba for two balancing authorities, region for two of EIA's regions | none | text | ba, region | 0 |
| `x_a` | A, the first party of the pair (the code that sorts first), EIA-930 code | none | text | for example AEC, AECI, AESO; 73 distinct | 0 |
| `x_b` | B, the second party of the pair, EIA-930 code | none | text | for example BPAT, CENT, CHPD; 65 distinct | 0 |
| `x_basis` | What value is: mean (the mean of the two reports over the hours both reported), a or b (only that side reported) | none | text | a, b, mean | 0 |
| `x_a_report_mwh` | The sum of A's reported hours, read as power from A to B | MWh | integer | -10708368 to 20367792; more than 5000 distinct | 53533: A reported no hour of the day (x_basis b) |
| `x_b_report_mwh` | The sum of B's reported hours, turned to the direction from A to B | MWh | integer | -429515551 to 10746671; more than 5000 distinct | 13637: B reported no hour of the day (x_basis a) |
| `x_gap_mwh` | Over the hours both reported, A's report less B's | MWh | integer | -10740769 to 429490967; more than 5000 distinct | 67175: No hour of the day has both reports |
| `x_hours_a` | The hours A reported | hour count | integer | 0, 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 22, 23, 24, 25, 3, 4, 5, 6, 8, 9 | 0 |
| `x_hours_b` | The hours B reported | hour count | integer | 0 to 25; 26 distinct | 0 |
| `x_hours_both` | The hours both reported | hour count | integer | 0 to 25; 26 distinct | 0 |
| `x_direction` | a_to_b when value is above zero, b_to_a below, none at zero | none | text | a_to_b, b_to_a, none | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `interchange_mwh` | Interchange from A to B over the day: the mean of the two sides' reports over the hours both reported, else the one side that reported (x_basis) | MWh | 553108 | 2018-07-01T00:00:00Z | 2026-11-18T00:00:00Z |

### `interchange_pair_monthly`

One pair of balancing authorities, or of EIA's regions, and one Eastern month, the interchange between them with each side's report, their mean and gap.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 18284.

- **Time:** ts_utc is the first day of the Eastern month at 00:00:00Z (freq P1M), a label.
- **Revisions:** One build, rebuilt whole by each run of the builder; no vintage column.
- **Source:** erw:interchange_pairs ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interchange_pairs.md)
- **Method note:** [`docs/methods/interchange_pairs.md`](../methods/interchange_pairs.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Who trades with whom: interchange by pair of balancing authorities and of regions, partners, events (docs/methods/interchange_pairs.md). Via the Energy Research Warehouse (ERW), table `interchange_pair_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<A>-<B>, A before B by code | none | text | for example eia930:AEC-MISO, eia930:AEC-SOCO, eia930:AECI-MISO; 205 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -215431847.5 to 48957747.5; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interchange_pairs | 0 |
| `x_level` | The level of the pair: ba for two balancing authorities, region for two of EIA's regions | none | text | ba, region | 0 |
| `x_a` | A, the first party of the pair (the code that sorts first), EIA-930 code | none | text | for example AEC, AECI, AESO; 73 distinct | 0 |
| `x_b` | B, the second party of the pair, EIA-930 code | none | text | for example BPAT, CENT, CHPD; 65 distinct | 0 |
| `x_basis` | What value is: mean (the mean of the two reports over the hours both reported), a or b (only that side reported) | none | text | a, b, mean | 0 |
| `x_a_report_mwh` | The sum of A's reported hours, read as power from A to B | MWh | integer | -10215190 to 100538613; more than 5000 distinct | 1717: A reported no hour of the month (x_basis b) |
| `x_b_report_mwh` | The sum of B's reported hours, turned to the direction from A to B | MWh | integer | -430177411 to 10805407; more than 5000 distinct | 334: B reported no hour of the month (x_basis a) |
| `x_gap_mwh` | Over the hours both reported, A's report less B's | MWh | integer | -10780271 to 429491127; more than 5000 distinct | 2053: No hour of the month has both reports |
| `x_hours_a` | The hours A reported | hour count | integer | 0 to 744; 127 distinct | 0 |
| `x_hours_b` | The hours B reported | hour count | integer | 0 to 744; 147 distinct | 0 |
| `x_hours_both` | The hours both reported | hour count | integer | 0 to 744; 186 distinct | 0 |
| `x_direction` | a_to_b when value is above zero, b_to_a below, none at zero | none | text | a_to_b, b_to_a, none | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `interchange_mwh` | Interchange from A to B over the month: the mean of the two sides' reports over the hours both reported, else the one side that reported (x_basis) | MWh | 18284 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |

