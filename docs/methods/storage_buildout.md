# Storage build-out: method

Built in session 69 for the site's `/storage/buildout` ("How much storage has been built"). One table:

| Table | Tier | What |
|---|---|---|
| `storage_buildout_monthly` | derived | Operating battery storage by grid and month, in MW and MWh, split by duration; operating solar beside it; planned battery storage by year online |

Code: `warehouse/derived/storage_buildout.py`. No pull. It reads the three EIA-860M tables the ERW holds: `eia860m_operating_generators`, `eia860m_planned_generators` and `eia860m_retired_generators`. Battery storage method for the hour-by-hour tables: [`storage.md`](storage.md).

## What is counted

- **A battery** is a generator whose prime mover is `BA` (EIA's "Batteries"). Pumped hydro, flywheels and compressed air are not counted.
- **Solar** is EIA's solar technologies: photovoltaic and solar thermal (12 thermal units in the August 2026 inventory). MW is nameplate, as EIA states it.
- **Utility scale** is the form's own floor: EIA-860M covers plants of 1 MW and above. Rooftop solar and batteries behind a customer's meter are not in it.
- **Operating** is EIA's operating inventory, statuses `OP`, `SB` (standby), `OS` and `OA` (out of service).

## Grids

A generator's grid is its **balancing authority code in EIA-860M**:

| EIA code | Entity |
|---|---|
| `CISO` | `iso:caiso` |
| `ERCO` | `iso:ercot` |
| `ISNE` | `iso:isone` |
| `MISO` | `iso:miso` |
| `NYIS` | `iso:nyiso` |
| `PJM` | `iso:pjm` |
| `SWPP` | `iso:spp` |
| any other code, or none | `us:outside_isos` |

`us:total` is every unit in the tables, Puerto Rico's sheet included. So `us:total` equals the seven grids plus `us:outside_isos`, for every variable that is a sum, in every month (a test checks it).

Not assigned to one of the seven, in the August 2026 inventory:

| | Units | MW | Of them, with no code at all |
|---|---|---|---|
| Operating batteries | 252 | 15,567.5 | 21 units, 238.9 MW |
| Operating solar | 2,324 | 57,643.5 | 77 units, 325.3 MW |
| Planned batteries | 124 | 21,019.2 | 5 units, 86.7 MW |

Most of these are in the West and Southeast outside any ISO (Arizona, Nevada, Florida, the Carolinas, Hawaii). They are real and are in the US total; they are only without a grid row of their own.

## Months

The EIA-860M tables are snapshots: the ERW holds one inventory, the newest month. The history is rebuilt from that one inventory:

- A unit is operating in a month when its first operating month (EIA's operating year and month) is that month or earlier, and it had not retired by then.
- A unit of the retired table counts from its first operating month to the month before its retirement month.
- A value is the fleet at the month's end. `ts_utc` is the first of the month.
- Months run from January 2015 to the inventory month. Units operating before 2015 are in every month's total.

What this cannot see:

- **Units retired before the retired table's window.** That table holds retirements of the inventory year and the year before. A battery retired earlier is in no month, so early years are understated by whatever retired since. The eight battery retirements held are 338.5 MW.
- **Changes to a unit.** A unit's MW and MWh are its present ones in every month it operated. A battery whose energy was added to later shows its present energy from its first month.
- **Late reports.** A unit that started in the newest months and has not yet been reported to EIA appears in a later inventory, dated back to its first month. The newest months grow when the next inventory arrives.

## Duration

A unit's duration is its **Nameplate Energy Capacity (MWh) over its nameplate MW**, both EIA's.

| Bucket | Rule |
|---|---|
| `lt2h` | under 2 hours |
| `2to4h` | 2 to under 4 |
| `4to6h` | 4 to under 6 |
| `ge6h` | 6 hours and more |
| `energy_not_reported` | EIA gives no energy value for the unit |

- A unit of exactly 2, 4 or 6 hours is in the bucket that starts there.
- A unit with no energy value is in `energy_not_reported` and in no duration bucket. Its MWh is never estimated from its MW. In the August 2026 inventory every one of the 1,137 operating battery units and all 8 retired ones carry a value, so this bucket is zero in every month.
- Sums are exact: MW and MWh are added as whole ten-thousandths.

## Variables

Every month, every entity:

| Variable | Unit | What |
|---|---|---|
| `battery_operating_mw` | MW | nameplate power of the operating batteries |
| `battery_operating_mwh` | MWh | their energy capacity, where EIA gives it |
| `battery_operating_units` | count | generators |
| `battery_operating_mw_<bucket>` | MW | the five buckets; they sum to `battery_operating_mw` |
| `battery_operating_mwh_<bucket>` | MWh | the four duration buckets; they sum to `battery_operating_mwh` |
| `solar_operating_mw` | MW | nameplate power of operating solar |
| `battery_operating_mwh_per_mw` | MWh/MW | average duration in hours: MWh over the MW of the units that report energy |
| `battery_mwh_per_solar_mw` | MWh/MW | battery MWh over solar MW: the hours the batteries could carry the solar fleet's nameplate |
| `battery_operating_mw_net_added_12m`, `battery_operating_mwh_net_added_12m` | MW, MWh | the month's value less the value twelve months before: additions net of retirements. From January 2016, the thirteenth month |

The two ratios are rounded to four decimals and omitted, never written as zero, where their denominator is zero.

At the inventory month only:

| Variable | Unit | What |
|---|---|---|
| `battery_planned_mw` | MW | every battery unit of the planned table |
| `battery_planned_units` | count | generators |
| `battery_planned_mw_under_construction` | MW | the part EIA reports as under construction |
| `battery_planned_mw_online_<year>` | MW | by the year of EIA's planned operation date |

A new inventory writes its planned rows at its own month and leaves the earlier months' planned rows in place, so the table keeps what was planned as of each inventory it was built from.

## Planned MWh is not held

EIA-860M's Planned sheet has no energy column (checked in the saved August 2026 workbook: Operating and Retired carry "Nameplate Energy Capacity (MWh)", Planned does not). So the table writes no planned MWh and the page says "not held". The annual Form EIA-860 (its energy storage schedule) reports energy capacity for proposed units; adding it needs a person to approve a new source and a pull of the annual files.

## Reading the numbers

- **Added in twelve months** is the newest month's value less the value twelve months before: additions net of retirements. It is a variable of the table, so the page computes nothing.
- **Planned dates** are developers' own estimates as reported to EIA. They slip, and some planned units are never built.
- **The solar ratio** compares energy with power: 1.0 means the grid's batteries hold one hour of its solar fleet's nameplate output. It says nothing about how the batteries are used or whether they sit beside the solar.
- **PJM is shown.** These are EIA's public generator data, not PJM's prices, so the table is public.
