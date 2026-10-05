# Method: what Texas's storage resources were awarded day-ahead

Energy Research Warehouse (ERW), session 115. Tables: `ercot_dam_esr_awards` (series, source, public; one row per
resource and hour) and `ercot_storage_dam_awards_monthly` (series, derived, public; the fleet by month). Code:
`warehouse/connectors/ercot_dam_esr.py` and `warehouse/derived/ercot_storage_dam_awards.py`. Page:
`/cost-of-power/battery/awards` (in review). Tests: `tests/test_session115.py`. It follows the scoping note of
session 108, [`ercot_disclosure_scoping.md`](ercot_disclosure_scoping.md).

## What this is not

**Day-ahead awards only: no real-time settlement, no deployment energy, no contracts.** It is each storage resource's
day-ahead award valued at its day-ahead price. It is a floor on market revenue and not what any battery earned. A
battery in ERCOT does most of its trading in real time, and that is in another report (see "What the real-time side
would take"). The word `revenue` in a variable's name means an award times its day-ahead price and nothing more.

## The source

ERCOT's "60-Day DAM Disclosure Reports" (EMIL NP3-966-ER, report type 13051): one zip a day, public, posted 60 days
after the operating day, under "NP3.2.5(12) PUCT Substantive Rule §25.506". One of its files,
`60d_DAM_ESR_Data-DD-MMM-YY.csv`, has a row for each Energy Storage Resource and hour ending. The date in the file's
name is the day it was posted; the operating day is 60 days before, and the file's own `Delivery Date` says so (the
connector checks the two against each other for every file).

**The file begins with operating day 6 December 2025.** The zip of 5 December 2025, the day ERCOT's Real-Time
Co-optimization began, holds no ESR file, and neither do the zips of 4 December 2025 and 24 January 2024 (the oldest
on ERCOT's list): three zips were opened to learn this. Before the file existed a battery was reported as a
generation resource and a load resource in other files of the same zip. Those were not read.

**License: public.** ERCOT's terms (`https://www.ercot.com/help/terms`), quoted: "The publicly available contents of
this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you
maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the
foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices." Nothing in them forbids republishing, so
neither table is internal. The files name each resource and its scheduling entity; that is ERCOT's own disclosure
under the rule above.

## The pull

Approved in session 115: the ESR file only, every day it exists, USD 0, ceilings of 9,000,000 rows and 3 GB of
downloads. A file cannot be had without its zip, so each day costs the whole zip. The connector:

- asks for one zip at a time and waits two seconds between requests;
- saves each zip once under `warehouse/raw/ercot_60d_dam/zips/`, with a line in `manifest.csv` (the operating day, the
  document, its bytes, its SHA-256, when it was retrieved), and never asks for a zip the machine holds, the sample
  month of session 108 included;
- adds up what it would download before it asks for anything, and stops without a request if that passes the
  ceiling; it checks again before each request, and checks the row ceiling before each day;
- reads, checks and writes one month before the next begins.

## `ercot_dam_esr_awards`: a row per resource and hour

| Column | From ERCOT's file |
|---|---|
| `entity` | `ercot:` and the Resource Name |
| `variable`, `value`, `unit` | `hsl_mw`: the High Sustained Limit that hour, MW |
| `ts_utc` | the hour's start in UTC, from Delivery Date and Hour Ending (Central prevailing time) |
| `node` | Settlement Point Name |
| `x_lsl_mw`, `x_resource_status`, `x_qse`, `x_dme` | LSL (negative: charging), Resource Status, QSE, DME |
| `x_energy_award_mw`, `x_energy_price_usd_per_mwh` | Awarded Quantity (negative is a purchase) and Energy Settlement Point Price, at the resource's own settlement point |
| `x_regup_award_mw`, `x_regup_mcpc` and the same for `regdn`, `ecrs`, `nonspin` | each Ancillary Service's award (MW) and its Market Clearing Price for Capacity (USD per MW per hour) |
| `x_rrspfr_award_mw`, `x_rrsffr_award_mw`, `x_rrsufr_award_mw`, `x_rrs_mcpc` | Responsive Reserve's three kinds of award and their one price |
| `source_url`, `retrieved_at`, `vintage` | the zip, when it was downloaded, when ERCOT posted it |

Every value is written as ERCOT prints it. **A blank award is no award and stays blank**; it is never written as a
zero. The value of the row is the limit, not the award, because a series value may not be empty and most hours have
no award (Decision 40 of the data standard). The offer curve columns are left out. An hour that a clock change makes
ambiguous is refused, not guessed (none has occurred in the days held).

A day is in the table whole or not at all. A day whose zip could not be had, has no ESR file, or fails a check
(the delivery date, a number that is not one, a repeated resource and hour) is a missing day: it has no rows, and
the table's header names it with its reason.

The table is not in the site's database (`catalogue_hold` in `warehouse/supabase/live_set.yaml`).

## `ercot_storage_dam_awards_monthly`: the fleet by month

One entity, `ercot:esr_fleet`; `ts_utc` is the first day of the local (Central) month. For each month:

| Variable | What it is |
|---|---|
| `resources`, `resources_with_award` | resources with a row in the month; those with any award in it |
| `mw` | the sum of each resource's highest HSL in the month |
| `resource_hours`, `resource_hours_energy_award` | rows of the month; those with a day-ahead energy award |
| `energy_sold_mwh`, `energy_bought_mwh` | positive and negative awards |
| `energy_sold_usd`, `energy_bought_usd` | each award times the Energy Settlement Point Price of its own row |
| `revenue_energy_usd` | sold less bought: energy net of charging |
| `revenue_regup_usd`, `revenue_regdn_usd`, `revenue_rrs_usd`, `revenue_ecrs_usd`, `revenue_nspin_usd` | each award times the clearing price of its own row; Responsive Reserve is its three kinds of award together at the one RRS price |
| `revenue_ancillary_usd`, `revenue_total_usd` | the five services; energy and the five |
| each `revenue_*` also `_per_mw` | over the month's `mw`, USD/MW. Per kW is this over 1,000 |
| `days_held`, `days_missing`, `days_in_month` | operating days with rows; days with none between the table's first and last operating day; the calendar's days |

Rules:

- **The MW counts every resource in the file that month**, awarded or not, at its highest limit of the month. A
  resource with no award adds nothing to any sum and is still in the MW: it was there to be awarded. A resource that
  was out or testing all month is in it too, at the limit ERCOT printed. A per kW over nameplate would differ.
- **Nothing is filled.** A missing day adds nothing and is counted in `days_missing`. A month is not scaled up to its
  full length: a month with fewer days held than the calendar has is a partial month, and the page marks it.
  The first month begins on the day the file begins, and the last month ends where ERCOT's 60 days end; those days
  are not "missing", and show only as the difference between `days_in_month` and `days_held`.
- **An award without its price stops the build.** It is never valued at another price.
- **A year** on the page is the sum of its months' per-kW figures, each month over its own MW.
- **The unit is USD/MW**, as `battery_stack_monthly` writes it (Decision 34), so the two tables can be set side by
  side; the session's prompt asked for per kW, which is the same number over 1,000 and is what the page shows.

### No duration class

The prompt asked for the same figures by duration class "where the resource's energy and power are both stated".
ERCOT's file states each resource's power (HSL, LSL) and never its energy, so no resource has both stated and no
duration class row is written. Energy is stated in EIA-860M (`energy_capacity_mwh` in
`eia860m_operating_generators`), by plant and generator. To use it, ERCOT's resource names (for example
`ALP_BESS_ESR1`) have to be matched to EIA's plants. The warehouse holds no such match, the names do not match by
rule, and a guessed match would put a resource in the wrong class. It is a list a person has to check.

## Beside the model

The page sets the awards beside one figure of the battery page's model (`battery_stack_monthly`,
[`battery_stack.md`](battery_stack.md)): the day-ahead schedule for a 2-hour battery, labeled as the model's. They
are not the same thing and the page says so:

| | The awards | The model's day-ahead schedule |
|---|---|---|
| Whose | every storage resource in ERCOT's file | one battery of 2 hours |
| Price | each resource's own settlement point | the hub average, `HB_HUBAVG` |
| What it does | what each resource was actually awarded day-ahead; most hours, nothing | a schedule solved against the day's day-ahead prices, every day, all of its power |
| Per kW of | the fleet's MW, resources that were out, testing or never offered included | the battery's rated power |
| Days | the days held | every day of the month |

So the model's figure is what one battery could take from day-ahead prices if it put everything there; the awards
are what the fleet did put there. The distance between them is the share of the fleet's capacity and hours that was
left to real time, was out, or lost to a cheaper offer. It is not a measure of the model's error. Only complete
months are compared.

## What the real-time side would take

1. **The 60-Day SCED Disclosure Reports** (report type 13052): `60d_ESR_Data_in_SCED`, a row per resource and SCED
   run with its base point, telemetered output, state of charge and real-time Ancillary Service awards. ERCOT's list
   put it at about 12 MB a day in session 108, half as much again as the day-ahead zip; for the days this table holds
   that is on the order of 3 GB. One month should be pulled first to learn its shape.
2. **Real-time prices at each resource's own settlement point.** The warehouse holds hubs. ERCOT publishes settlement
   point prices for every resource node; that pull has not been sized.
3. **ERCOT's protocols on settlement under Real-Time Co-optimization**: how real-time energy settles against the
   day-ahead award (the deviation at the real-time price), and how real-time Ancillary Service awards settle against
   day-ahead ones. They have not been read by any session, and they have to be read before the arithmetic is written.
4. **Still not disclosed after that:** contracts and tolls, the charges and make-whole payments of the private
   settlement statement, station power. Even with the real-time side the figure would be market revenue at posted
   prices, 60 days behind, not cash received.
