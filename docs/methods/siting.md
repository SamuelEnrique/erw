# Where can a large load go: the All grids tab of "What a datacenter pays"

Version 0, session 700, 22 October 2026 (chain 050, `queue/done/050-night-23-october-code-allgrids.md`). Internal: the tab is in review, like every page.

`/cost-of-power` ("What a datacenter pays") answers, for one chosen region, what a load pays, when it connects and how clean the power is. Its second tab, **All grids** (`/cost-of-power?view=allgrids`), answers the same questions for every grid, hub and zone the warehouse holds a price for, and behind a toggle for every ERCOT node of `node_basis_daily`, in one sortable table. It is the same page and the same model: the rows are "Your load"'s own index, and each column is computed by the library function that computes it for "Your load", so the two views cannot disagree. The tab ranks nothing by a score and expresses no view: it sorts by the column the reader chooses and says what the sort is.

Code: `site/lib/siting.ts` (pure: the profiles, the columns, the rows, the inputs, the check keys), `site/lib/sitingdata.ts` (the files, server only), `site/app/cost-of-power/AllGridsView.tsx` and `AllGridsForm.tsx`. Files: `site/data/datacenter/` (the hub and zone prices, `warehouse/derived/datacenter_page.py`) and `site/data/siting/` (`warehouse/derived/siting_page.py`). Nothing is read from the database by the tab.

## The rows

- **Hubs and zones** (the default row set): every region of `site/data/datacenter/index.json`, the index "Your load" reads, which `datacenter_page.py` builds from the hub and zone price tables (`ercot_all_hub_prices_history`, `ercot_zone_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_zone_prices_history`, the ISO-NE and NYISO zone tables). On 22 October 2026: ERCOT 14 (6 hubs, 8 load zones), CAISO 3, NYISO 11, ISO-NE 9, SPP 2. Then the regions the index names and does not price: MISO's 8 hubs ("paused while terms are reviewed", `docs/methods/miso_pause.md`). Then a grid with no hub or zone price held as one row of its own: PJM ("licensed source needed"), so that the columns a grid holds without a price (queues, carbon, capacity) have a row. 48 rows.
- **ERCOT nodes** (the toggle): every settlement point of `node_basis_daily` that is neither a hub nor a load zone, 873 of its 888 points (7 hubs and 8 zones are the others), each with its class (storage, solar, wind, gas, other, mixed, unknown) and ERCOT's resource types at it. The table holds no list of each node's load zone and settlement hub (its own header says so): a node's zone, hub and wires utility are "not held" until a table holds them.
- The default order: alphabetical by the grid's name, then by the row's name. The row count is a key (`allgrids|rows|hubs`, `allgrids|rows|nodes`).

## The load's profiles

A profile sets three inputs, the load factor, the curtailment rule and whether the load is interruptible, and nothing else. Each default is shown in grey beside its field with its source on hover, and is editable in place within the profile's range. The size is the reader's (default 100 MW, the size "Your load" opens on).

| Profile | Load factor | Curtailment rule | Interruptible | Source of the defaults |
|---|---|---|---|---|
| Datacenter (default) | 0.90, flat in every hour | never curtails | no | the owner's chain prompt of 22 October 2026 |
| Flexible compute | 0.90 while running | off in ERCOT's four summer peak intervals, and in hours at or above a strike of USD 1,000 per MWh | no | the prompt; the strike is the page's scarcity level (`SCARCITY_USD`, `lib/datacenter/answers.ts`) |
| Electrolyzer | 0.55, editable from 0.40 to 0.70 | runs only in hours below a strike; by default each row's own price at the load factor (the cheapest 55 percent of its hours) | no | the prompt's range 0.40 to 0.70; 0.55 its middle |
| Heavy industry | 0.80 | off only when the grid interrupts it | yes | the prompt |

## The eight columns

Each column's head carries a one-line source and method in its hover. A cell the warehouse cannot fill says why in its hover, in short words in ink ("not held", "license needed", "no capacity market"); no visible grey text. A figure from a table that is internal, or whose publisher's terms ask for a license (`site/lib/license.ts`), is computed and keyed and drawn as "license needed" in place (session 408's rule).

| Column | Table, filter | Vintage held (22 October 2026) | License | The function that computes it today | Where it cannot be filled |
|---|---|---|---|---|---|
| Energy, USD per MWh | the page's hourly files (`data/datacenter/<grid>_<year>.json`), day-ahead, real time beside it; ERCOT nodes: `node_basis_daily`, `variable = dam_basis` | ERCOT 2015 to October 2026; CAISO from 2023; NYISO from 2019; ISO-NE from 2024; SPP from 2019; nodes 1 October 2025 to 20 October 2026 (day-ahead), 28 September 2026 on (real time) | public; ISO-NE, MISO and NYISO prices license-held since 20 October 2026 | `lib/datacenter.ts`: `monthsOf`, `lastTwelve`, `span` (the flat price over the last twelve whole months) | MISO "paused while terms are reviewed"; PJM "license needed" (no PJM price is held) |
| Transmission and 4CP, USD per MWh | `ercot_4cp_intervals` (the four summer intervals), the Commission's rate from `texas_transmission_matrix` | intervals 2018 to summer 2025; matrices of 2025 and 2026 | intervals public; matrix internal | `app/cost-of-power/model.ts`, the `cp` block (summers, rate, avoided share) | every grid but ERCOT: "not held", the utility's large-load tariff would fill it |
| Capacity, USD per MWh | `iso_all_capacity_prices` (ISO-NE, MISO, NYISO, PJM), `pjm_rpm_capacity_prices` | auctions to delivery year 2028/29 | internal | none yet (the existing tab says "no public figure") | ERCOT, CAISO, SPP: "no capacity market"; the four held grids: computed, "license needed" |
| Time to connect, months | `lbnl_interconnection_queue` (projects finished in the last three years), `iso_queue_statistics`; `large_load_rules`, `large_load_waits`, `ercot_large_load_status`, `nyiso_load_queue` | Berkeley Lab's snapshot of 2 October 2026; rules to 22 September 2026; waits to 8 October 2026 | queues and rules public; waits internal; NYISO's load queue license-held | `lib/queues.ts` (`viewOf`), `lib/howsoon.ts` (`blockOf`), `lib/rules.ts` | timelines by utility: "not held" |
| Headroom, percent and MW | `eia930_demand_growth`; `eia860m_planned_generators`; `eia_state_capacity_annual` | demand to 2026; planned generators snapshot of 21 October 2026; state capacity to 2024 | public | `lib/demandgrowth.ts` | reserve margin by zone: "not held" |
| Carbon, kg CO2 per MWh | `egrid_power_plants` (the row's eGRID subregion); `carbon_intensity_hourly` for a profile that runs in some hours | eGRID snapshot of 21 October 2026; hourly intensity to 18 October 2026 | public | `lib/datacenter/answers.ts` (`l12Carbon`, `windowCarbon`) for the grid's own intensity | a row whose subregion is not known: "not held" |
| Utility | `eia861_utility_sales` (the largest utility by industrial sales in the row's state) | 2015 to 2025 | public | none yet | service territories: "not held" |
| All-in, USD per MWh | energy plus transmission plus capacity | as its parts | as its parts | none yet | drawn only where each of the three is held or zero by market design |

`egrid_power_plants`, `eia861_utility_sales`, `eia_state_capacity_annual` and `node_basis_daily` are not in the live set (held for Redivis's storage, `warehouse/supabase/live_set.yaml`): the tab reads them only through its own files under `site/data/siting/`, built on a machine that holds the tables.

## Check keys

Every figure is a key of the form `allgrids|<column>|<row>`, with the inputs it depends on after it where it depends on them; `scripts/check-values.mjs` recomputes each from the same files with the same functions (`site/scripts/siting-files.mjs`). The chain prompt's `allgrids_<column>_<row>` is written in the site's form, with `|`.

## Decisions (session 700, each reversible)

1. The tab is a third view of the one page, "All grids", between "Your load" and "Grid by grid"; "Grid by grid" (session 37's tab) stays.
2. The profile dropdown is in the All grids tab's own input box, not in "Your load"'s: there it would change nothing, and no default figure of "Your load" may move.
3. PJM is one row of its own ("the grid"), since no PJM hub or zone price is held; MISO's 8 hubs are rows with the existing tab's words.
4. The flexible profile's strike is the page's scarcity level, USD 1,000 per MWh; the electrolyzer's load factor is 0.55, the middle of the stated range; its strike is each row's own price at that share of hours.
5. A node's twelve-month price is the hub's twelve-month mean plus the node's mean daily day-ahead basis over the same months (the daily table: `node_basis_daily` holds days, not hours).

## Limits

The tab's figures are those of the files on the day they were built. A cell that is empty in version 0 is a column not yet computed; each later session of the chain fills one column.
