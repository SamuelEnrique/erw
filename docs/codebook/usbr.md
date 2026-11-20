# Codebook: usbr

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 3 documented in full.

- [`usbr_crsp_reservoirs_daily`](#usbr_crsp_reservoirs_daily): One daily reading (pool elevation, storage, power release or total release) of one of the Colorado River Storage Project's power reservoirs above Lake Powell (Flaming Gorge, Blue Mesa, Morrow Point, Crystal), from Reclamation's Upper Colorado hydrodata.
- [`usbr_hydropower_monthly`](#usbr_hydropower_monthly): One Reclamation hydropower plant's installed capacity, gross generation, plant auxiliary use or net generation in one month, from Reclamation's Monthly and Annual Performance Data workbook.
- [`usbr_mead_powell_daily`](#usbr_mead_powell_daily): One daily reading (pool elevation, storage, total release or inflow) of Lake Powell (Glen Canyon Dam) or Lake Mead (Hoover Dam), from Reclamation's Upper Colorado hydrodata.

### `usbr_crsp_reservoirs_daily`

One daily reading (pool elevation, storage, power release or total release) of one of the Colorado River Storage Project's power reservoirs above Lake Powell (Flaming Gorge, Blue Mesa, Morrow Point, Crystal), from Reclamation's Upper Colorado hydrodata.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 330293.

- **Time:** ts_utc is the day at 00:00:00Z; freq P1D. Reclamation calls all data provisional and subject to revision.
- **Revisions:** A later run merges by (entity, variable, ts_utc), a revised value replacing the old one; a day Reclamation later blanks writes no row, so the earlier value stays. vintage is each file's Last-Modified time.
- **Source:** usbr:hydrodata_crsp_reservoirs U.S. Bureau of Reclamation, Upper Colorado Basin Region, reservoir data (hydrodata) (https://www.usbr.gov/uc/water/hydrodata/reservoir_data/site_map.html)
- **Method note:** [`docs/methods/usbr_crsp_reservoirs_daily.md`](../methods/usbr_crsp_reservoirs_daily.md)
- **Cite as:** U.S. Bureau of Reclamation (USBR). Upper Colorado region's reservoir data (hydrodata): Flaming Gorge, Blue Mesa, Morrow Point and Crystal. Via the Energy Research Warehouse (ERW), table `usbr_crsp_reservoirs_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: usbr_hydrodata:<Reclamation's site number> (917 Flaming Gorge, 913 Blue Mesa, 914 Morrow Point, 915 Crystal) | none | text | usbr_hydrodata:913, usbr_hydrodata:914, usbr_hydrodata:915, usbr_hydrodata:917 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1962-11-01T00:00:00Z to 2026-10-22T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -119.60493 to 3913631.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | acre-ft, ft, ft3/s | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-UT (Flaming Gorge) or US-CO | none | text | US-CO, US-UT | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 330293 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The reservoir's name, not a pricing node | none | text | Blue Mesa Reservoir, Crystal Reservoir, Flaming Gorge Reservoir, Morrow Point Reservoir | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usbr:hydrodata_crsp_reservoirs | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.usbr.gov/uc/water/hydrodata/reservoir_data/913/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/913/csv/39.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/913/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/913/csv/49.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/914/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/914/csv/39.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/914/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/914/csv/49.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/915/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/915/csv/39.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/915/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/915/csv/49.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/917/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/917/csv/39.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/917/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/917/csv/49.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T02:09:29Z, 2026-10-24T02:09:30Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Each data file's Last-Modified time | none | utc time | 2026-10-23T22:06:25Z, 2026-10-23T22:06:27Z, 2026-10-23T22:06:29Z, 2026-10-23T22:06:32Z, 2026-10-23T22:09:44Z, 2026-10-23T22:09:45Z, 2026-10-23T22:09:48Z, 2026-10-23T22:09:51Z, 2026-10-23T22:09:58Z, 2026-10-23T22:10:00Z, 2026-10-23T22:10:01Z, 2026-10-23T22:10:04Z, 2026-10-23T22:11:23Z, 2026-10-23T22:11:24Z, 2026-10-23T22:11:26Z, 2026-10-23T22:11:29Z | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `pool_elevation` | The reservoir's water surface elevation, ft (feet above mean sea level) | ft | 81571 | 1965-11-30T00:00:00Z | 2026-10-22T00:00:00Z |
| `power_release` | Water released through the power plant's turbines, ft3/s (cubic feet per second) | ft3/s | 82624 | 1963-10-01T00:00:00Z | 2026-10-22T00:00:00Z |
| `storage` | The water held in the reservoir, acre-ft | acre-ft | 83052 | 1962-12-02T00:00:00Z | 2026-10-22T00:00:00Z |
| `total_release` | All water released from the dam, ft3/s (cubic feet per second) | ft3/s | 83046 | 1962-11-01T00:00:00Z | 2026-10-22T00:00:00Z |

### `usbr_hydropower_monthly`

One Reclamation hydropower plant's installed capacity, gross generation, plant auxiliary use or net generation in one month, from Reclamation's Monthly and Annual Performance Data workbook.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 31702.

- **Time:** ts_utc is the month's first day at 00:00:00Z; freq P1M. Reclamation calls the facility data provisional.
- **Revisions:** A snapshot of the workbook; each run writes the table again. vintage is the workbook's time (one value).
- **Source:** usbr:power_plant_data U.S. Bureau of Reclamation, Power Resources Office, Reports and Data (https://www.usbr.gov/power/data/data.html)
- **Method note:** [`docs/methods/usbr_hydropower_monthly.md`](../methods/usbr_hydropower_monthly.md)
- **Cite as:** U.S. Bureau of Reclamation (USBR). Active USBR Facilities, Operated and Maintained by Reclamation, Monthly and Annual Performance Data. Via the Energy Research Warehouse (ERW), table `usbr_hydropower_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: usbr_plant:<facility, snake case> | none | text | for example usbr_plant:alcova, usbr_plant:anderson_ranch, usbr_plant:big_thompson; 55 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2013-10-01T00:00:00Z to 2025-10-01T00:00:00Z; 145 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -1141.0 to 2812813.375; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: the workbook gives no state | none | empty | no cell holds a value | 31702 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 31702 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The facility as Reclamation names it, not a pricing node | none | text | for example Alcova, Anderson Ranch, Big Thompson; 55 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usbr:power_plant_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.usbr.gov/power/data/Plant_Data_11_2025.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:16:02Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: One value, the workbook's time | none | utc time | 2025-11-12T17:25:40Z | 0 |
| `x_region` | Reclamation's region of the facility, as the workbook's annual sheet codes it (MB, CGB, CPN, LCB, UCB) | none | text | CGB, CPN, LCB, MB, UCB | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `auxiliary_use` | The electricity the plant used itself in the month (plant auxiliary use), MWh | MWh | 7918 | 2013-10-01T00:00:00Z | 2025-10-01T00:00:00Z |
| `gross_generation` | The electricity the plant generated in the month, before its own use, MWh (Reclamation's kWh over 1,000) | MWh | 7933 | 2013-10-01T00:00:00Z | 2025-10-01T00:00:00Z |
| `installed_capacity` | The plant's installed capacity in the month, MW (Reclamation's kW over 1,000) | MW | 7933 | 2013-10-01T00:00:00Z | 2025-10-01T00:00:00Z |
| `net_generation` | Gross generation less auxiliary use in the month, MWh; below zero when the plant used more than it made | MWh | 7918 | 2013-10-01T00:00:00Z | 2025-10-01T00:00:00Z |

Waiting for a second look: x_region: the codes MB, CGB, CPN, LCB and UCB are not expanded in the header, the method note or the connector..

### `usbr_mead_powell_daily`

One daily reading (pool elevation, storage, total release or inflow) of Lake Powell (Glen Canyon Dam) or Lake Mead (Hoover Dam), from Reclamation's Upper Colorado hydrodata.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 192508.

- **Time:** ts_utc is the day at 00:00:00Z; freq P1D. A day not yet ended when its file was fetched is left out. Reclamation calls all data provisional and subject to revision.
- **Revisions:** A later run merges by (entity, variable, ts_utc), a revised value replacing the old one; a day Reclamation later blanks writes no row, so the earlier value stays. vintage is each file's Last-Modified time.
- **Source:** usbr:hydrodata_reservoirs U.S. Bureau of Reclamation, Upper Colorado Basin Region, reservoir data (hydrodata) (https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/dashboard.html)
- **Method note:** [`docs/methods/usbr_mead_powell_daily.md`](../methods/usbr_mead_powell_daily.md)
- **Cite as:** U.S. Bureau of Reclamation (USBR). Upper Colorado region's reservoir data (hydrodata): Lake Powell and Lake Mead. Via the Energy Research Warehouse (ERW), table `usbr_mead_powell_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: usbr_hydrodata:<Reclamation's site number> (919 Lake Powell, 921 Lake Mead) | none | text | usbr_hydrodata:919, usbr_hydrodata:921 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1934-04-01T00:00:00Z to 2026-10-22T00:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 29904000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | acre-ft, ft, ft3/s | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Always US-AZ | none | text | US-AZ | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 192508 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The lake and its dam, not a pricing node | none | text | Lake Mead (Hoover Dam), Lake Powell (Glen Canyon Dam) | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usbr:hydrodata_reservoirs | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/29.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/49.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/921/csv/17.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/921/csv/42.csv, https://www.usbr.gov/uc/water/hydrodata/reservoir_data/921/csv/49.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T01:35:11Z, 2026-10-24T01:35:12Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Each data file's Last-Modified time | none | utc time | 2026-10-23T22:06:34Z, 2026-10-23T22:08:17Z, 2026-10-23T22:10:06Z, 2026-10-23T22:11:30Z, 2026-10-23T22:37:52Z, 2026-10-23T22:37:54Z, 2026-10-23T22:37:57Z | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `inflow` | Water flowing into the lake, ft3/s (cubic feet per second; Lake Powell only) | ft3/s | 23237 | 1963-03-11T00:00:00Z | 2026-10-22T00:00:00Z |
| `pool_elevation` | The lake's water surface elevation, ft (feet above mean sea level) | ft | 56446 | 1935-02-02T00:00:00Z | 2026-10-22T00:00:00Z |
| `storage` | The water held in the lake, acre-ft | acre-ft | 55783 | 1937-05-28T00:00:00Z | 2026-10-22T00:00:00Z |
| `total_release` | All water released from the dam, ft3/s (cubic feet per second) | ft3/s | 57042 | 1934-04-01T00:00:00Z | 2026-10-22T00:00:00Z |

