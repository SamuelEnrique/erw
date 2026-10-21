# Paper outline: a standardized, validated warehouse of US energy data

For the one-unit independent study. Written in session 139 (7 October 2026). An outline, not a draft: each section
says what it will hold and where its facts are. Sources: `docs/accelerator/evidence_pack.md` (the repository's facts,
each with its path), `docs/paper/related_projects_notes.md` (the other projects, each fact with its address and the
date read), and the session reports under `archive/sessions/`.

Working title: **The Energy Research Warehouse: one data standard and one validator across US power markets, and
three things they made visible.**

Target length: 6,000 to 8,000 words, four figures, two tables. A data descriptor with empirical demonstrations, in the
form of the Item Response Warehouse paper (DOI 10.3758/s13428-025-02796-y), whose infrastructure the ERW copies.

## 1. The question

**Can a small set of standard table shapes, with one automated validator in front of every table, make US energy data
from many publishers joinable enough to answer questions that no single source answers, and to catch errors in the
sources themselves?**

Two sub-questions the paper answers with evidence:

1. What does it cost, in rules and in rejected or corrected data, to hold 171 tables from 114 publisher names to one
   standard? (`evidence_pack.md` sections 2, 3, 5 and 7.)
2. What can be computed across sources once they share a shape that could not be computed, or could not be trusted,
   before? (Section 5 below: three demonstrations.)

What the paper does not claim: that the ERW is larger, older or more complete than the projects in section 2. It is
not.

## 2. What the ERW adds beside existing open energy data projects

Stated honestly. Each line is from `related_projects_notes.md`, where every fact has its address.

| Project | What it already does, and does better than the ERW | What it does not do, that the ERW does |
|---|---|---|
| PUDL (Catalyst Cooperative) | A pipeline over the US federal filings (EIA 860, 861, 923, 930, FERC 1, 714, EQR, EPA CEMS and more), nightly builds, quarterly versioned releases with a Zenodo DOI, a DOI for every raw input archive, a dbt project of data tests, CC-BY-4.0. Deeper and more rigorous on federal filings than the ERW, and already citable | Its source list has no ISO price feeds, no interconnection queues, no operator ancillary or capacity prices |
| gridstatus (library) and Grid Status (hosted) | One Python interface to nine ISOs and EIA, maintained against every change in the operators' sites. The ERW's ISO price connectors are built on this library (`warehouse/connectors/iso_prices.py`) | The library stores no history and applies no cross-source standard ("Minimally processed data"); the hosted history is an API with free and paid plans, not an open versioned dataset |
| EIA Open Data API and EIA-930 | The primary source for hourly demand, generation by fuel and interchange by balancing authority, public domain, hourly | No prices, no nodes, no projects; no check of its own series against the operators' (demonstration 1) |
| Open Grid Emissions (Singularity) | Hourly generation and emissions by balancing authority, plant and subplant, 2005 to 2025, a documented methodology, published data quality metrics, a Zenodo DOI. More careful on emissions than the ERW's derived intensity | No real-time data, no prices |
| LBNL Queued Up | The national dataset of generator and storage interconnection requests, with a codebook, annual, CC BY 4.0. The ERW's queue summary is derived from it | "does not include load interconnection requests" |
| OEDI | A catalog and data lake for DOE-funded datasets | No common table standard; it "does not review nor validate the quality of data submitted" |
| Open Power System Data | The closest precedent in method: a Frictionless Data Package standard, published processing scripts, a DOI per version | Europe only; its time series package was last versioned in October 2020 |
| Electricity Maps, WattTime | Worldwide coverage and marginal signals | The processed data are sold or behind a token, not openly licensed |
| Ember | Country and US state generation, monthly, CC-BY-4.0 | No hourly US grid data, no nodes, no projects |
| PowerGenome | Prepares capacity expansion model inputs | A tool, not a hosted dataset |
| Item Response Warehouse | The template: a numbered public standard, a validator on PyPI, Redivis versions, uploads as drafts a person publishes | Not energy |

The contribution, in three sentences the paper must defend:

1. **Scope across source types in one shape.** Operator prices (day-ahead, real time, ancillary, capacity), EIA's
   hourly grid data, plant inventories, interconnection queues, storage awards and offers, FERC contract filings,
   fuels, policy events and news sit in three table shapes (`series`, `entities`, `events`) under one naming rule
   (`docs/datastandard.md`). No project above holds operator prices and federal filings in one standard.
2. **One validator as a gate, with a public record of what it and the cross-checks caught.** Every table passes
   `warehouse/validate/erw_validate.py` before upload (171 of 171 today); the faults found in sources are a table,
   `known_data_faults`, with what was done about each.
3. **Licenses carried per table, with publication withheld where terms forbid it.** 145 public and 26 internal tables;
   a paused publisher (MISO) whose data is held and not shown. This is a cost the paper reports, not a feature: PJM's
   prices are absent for want of a license.

What the ERW lacks and the paper must say: no released, citable version yet (`redivis_release_checklist.md`: 17 of 41
items done); one maintainer; history that is short outside ERCOT (most hubs from September 2024, zones from August
2026); derived tables whose methods have not been reviewed outside the project.

## 3. Method: the data standard and the validator

- **3.1 The standard.** The three shapes, the leading columns, UTC timestamps, units, entity naming, the provenance
  header and per-row `source`, `source_url`, `retrieved_at` (`docs/datastandard.md`; `ARCHITECTURE.md` for which
  document governs). One table as a worked example from source file to standard rows.
- **3.2 The validator.** Its rules, listed from the code (`evidence_pack.md` section 5), its three exit codes, and
  where it sits (before the Redivis draft and before the live set). Table 1: the rules, and for each the number of
  tables it has blocked in the run log, if `run_status.csv` allows the count; if it does not, say so.
- **3.3 Checks beyond the validator.** The rule for impossible values (`docs/methods/impossible_hours.md`), the
  completeness rule for an hour and a month ("nothing is filled"), the before and after snapshot of live pages, the
  1,475 tests. What each is for.
- **3.4 Provenance and licensing.** The source registry (250 sources), the license classes, the pause mechanism.
- **3.5 Distribution.** Redivis as the warehouse of record (drafts; release is a human act), the `erw` client, the
  live subset in Postgres, the site. What a reader can reproduce today and what waits on the first release.
- **3.6 Model-read tables.** Twelve tables are extracted by a language model; each figure is stored with the sentence
  it was read from and checked by code against the document. State the rule and its failure rate where recorded.

## 4. What it cost: faults found in the sources

A short results section before the demonstrations (`evidence_pack.md` section 7). Table 2: each known fault, its
source, how it was found (validator, cross-source comparison, or a reader), and what was done. Two examples in text:
EIA's workbook giving PJM's demand as 2,147,480,000 MW in one hour of 19 October 2021 (`SESSION_118_REPORT.md`), and
ERCOT's large load reports whose two peaks cannot both be right (`site/lib/largeload.ts`, `impossible`).

## 5. Three empirical demonstrations

Each uses only tables held, a written method note, and numbers already stated in a session report. Each is chosen to
need at least two sources in the common shape.

### 5.1 A federal series checked against an operator's own: California in EIA-930

- **Finding.** EIA's hourly figures for California sat one hour late from 1 November 2023 to 2 December 2025 (best
  match at a shift of one hour on 182 of 182 days), and from 16 December 2025 EIA's California figures no longer add
  up: imports measured as demand less generation were 40.6 percent of demand in January 2026 against 28.5 percent by
  interchange.
- **Why it needs the warehouse.** The comparison is EIA-930 against CAISO's own supply by fuel, hour by hour, in the
  same shape.
- **Consequence measured.** A solar revenue figure overstated by 10.3 percent over 16 months (USD 45,617 per MW
  before, 40,916 after).
- **Sources.** `docs/methods/eia930_caiso_break.md`; `SESSION_73_REPORT.md`, `SESSION_82_REPORT.md`;
  `evidence_pack.md` findings 1 and 2. **Caveat to carry.** The brief's own: "a change in what EIA-930 reports as
  California's generation, not power that went missing".
- **Figure 1.** The hourly offset by day; the import share by two measures by month.

### 5.2 A model checked against what happened: what Texas batteries earn

- **Finding.** Over January to July 2026 ERCOT's storage fleet was awarded USD 6.53 per kW day-ahead, 22 percent of
  the USD 30.14 per kW the ERW's own perfect-foresight model earns in the same months; 32 percent of what the fleet
  discharged had been sold day-ahead; 88 percent of the energy offered day-ahead was priced above USD 1,000 per MWh.
- **Why it needs the warehouse.** Hub prices, ancillary prices, ERCOT's 60-day disclosure of awards and offers, and
  real-time dispatch joined by hour and resource.
- **Sources.** `docs/methods/battery_stack.md`, `ercot_storage_dam_awards.md`, `ercot_storage_dam_offers.md`,
  `ercot_storage_realtime.md`; `SESSION_115_REPORT.md`, `SESSION_116_REPORT.md`, `SESSION_120_REPORT.md`;
  `evidence_pack.md` findings 3 to 6. **Caveat to carry.** Day-ahead awards are a floor on market revenue, not what
  the batteries earned.
- **Figure 2.** Model against awards by month; the offer curve by price band.

### 5.3 A question for a new kind of load: when Texas is tight, and what flexibility is worth

- **Finding, part one.** Solar's output in Texas's 100 tightest hours fell from 71.1 percent of its installed capacity
  in 2019 to 5.0 percent in 2025: the tight hours moved off the sun (`grid_stress_yearly`; `SESSION_123_REPORT.md`).
- **Finding, part two (session 138).** For a large load at ERCOT's hub average, off in each year's 100 most expensive
  hours: USD 47.93 per MWh against a flat load's 148.19 in 2021, and 28.97 against 32.20 over October 2025 to September
  2026. And the dear hours are no longer the tight hours: in 2023 the grid's demand was within 5 percent of its peak
  in 157 hours at a mean real-time price of USD 525 per MWh, and such a load was off in 46 of them; in 2025, 140 hours
  at USD 42.82, and the load was off in 3 (`SESSION_138_REPORT.md`; `/cost-of-power`). The paper states the flexible
  figures as upper bounds: the hours are chosen with hindsight.
- **Why it needs the warehouse.** Hourly prices by hub, the operator's hourly demand, generation by fuel and installed
  capacity in one frame.
- **Sources.** `docs/methods/grid_stress.md`, `docs/methods/datacenter_cost.md`.
- **Figure 3.** Solar's share of capacity in the tight hours by year; cost per MWh by year, flat and flexible.

## 6. What is missing: large load in line

One page. The warehouse can say what a large load pays and when the grid is tight; it cannot say how much large load
is waiting for power by place, or how long one waits. `related_projects_notes.md` section 3 gives what a search found:
two public project-level load queues (NYISO, 74 requests; BPA, 458 line and load requests), system totals in ERCOT's
slide decks, forecast adjustments in PJM's load forecast, and no national standardized public file. Session 139's
pilot (`docs/accelerator/large_load_pilot.md`) tests whether the scattered statements can be collected with each
number tied to its sentence. The paper reports the pilot's yield and what it shows about why the figures cannot be
summed. **Figure 4.** The pilot's statements by entity and stage as worded.

## 7. Limitations

One maintainer; no outside review of the derived methods; short history outside ERCOT; no PJM prices and MISO paused;
weather not removed from demand growth; model-read tables depend on a commercial model; nothing released yet.

## 8. Availability

The repository, the data standard and validator, the Redivis dataset and its DOI once released, the commit the release
was built from. Until the first release, the paper cannot be cited against a fixed dataset: the checklist
(`docs/accelerator/redivis_release_checklist.md`) is the path.

## What the outline needs before drafting

1. The first Redivis release, so that every number in section 5 can be reproduced from a version.
2. A count from `run_status.csv` of what the validator has blocked, or a statement that the log does not record it.
3. An outside reader for one demonstration's method (the California comparison is the most self-contained).
4. A ruling on whether section 5.2 may show ERCOT disclosure data resource by resource or only as fleet totals.

## The outline on what the warehouse can show, session 446, 21 October 2026

Written unattended on the portable laptop (chain `queue/done/017-night-21-october-third.md`). Everything above this
heading is session 139's outline of 7 October and is unchanged. This section lays the same paper out in the shape of
the IRW paper (the data standard, the harmonization, the coverage, the licensing ledger, the validator, the citable
release, the uses) and says, section by section, which figures and tables the warehouse can produce today and which
need work. Where session 139's text already covers a part, it is referred to, not repeated.

**Where the counts come from.** Every count in this section was computed by
`runs/chain_oct21_third/s446/counts.py` (kept outside git, as `runs/` is; its output `counts.json` beside it) from
`warehouse/metadata/coverage.csv`, `sources.csv`, `license_status.csv` and `run_status.csv`, `docs/licenses.md`,
`docs/redivis/release-v1/tables.csv` and `variables.csv`, and `docs/datastandard.md`, as they stand on the branch
`wip/441-450-third` on 21 October 2026. `coverage.csv`'s newest `last_run` is 2026-10-20 20:21 UTC. The counts of
session 139's outline (171 tables, 114 publisher names, 145 public and 26 internal) are of 7 October; the ones below
replace them when the paper is drafted, and are themselves to be read again on the day of the release the paper cites.

**A key, in this section,** is how a figure's numbers are found in a table: the table's key under the standard
(`(entity, variable, ts_utc)` for a `series` table, `event_id` for an `events` table) and the variables a figure
reads. Every variable named below is listed for its table in `docs/redivis/release-v1/variables.csv`.

### The warehouse today, in eight numbers

| Count | Value | Source |
|---|---|---|
| Tables | 212 | `coverage.csv`, one row a table |
| Rows | 40,332,903 (37,357,126 in public tables, 2,975,777 in internal) | `coverage.csv`, `n_rows` |
| Flag | 179 public, 33 internal | `coverage.csv`, `license` |
| Tier | 125 source, 67 derived, 20 model extracted | `coverage.csv`, `tier` |
| Validator | 212 of 212 pass (1 with a warning: `census_metro_population`) | `coverage.csv`, `validator_status` |
| Sources | 338 source rows from 148 publisher names (216 public, 122 internal) | `sources.csv` |
| Licenses | 84 publishers in the record, 82 requests; ERW verdict 130 public, 33 internal, 49 unsettled; 42 tables "license needed" | `docs/licenses.md` ("Read these first", "Every table"); `license_status.csv` |
| Release v1 as packaged | 135 tables and 3 metadata tables in; 42 held for a license; 2 held for storage; 28,830,665 rows in the 138 | `docs/redivis/release-v1/tables.csv`, `in_v1` |

### 1. The data standard

What the IRW paper's section on its format does, for the ERW: the three shapes, the leading columns, UTC, units, the
provenance columns and the naming rule. Session 139's 3.1 is the text; this adds what can be shown.

- **Today.** Table A: the 135 tables of v1 by shape (115 `series`, 10 `events`, 10 `entities`) and by tier, from
  `tables.csv` and `coverage.csv`. The standard's 48 numbered decisions (`docs/datastandard.md`, "Decisions in v0",
  1 to 48) as a timeline in an appendix: each dated by its session, so a reader sees the standard grow with the
  sources. One worked example from source file to rows: `caiso_fuel_supply` (key `(entity, variable, ts_utc)`;
  variables `solar_mw`, `natural_gas_mw`, `imports_mw` and the rest), which is public, in v1, and from one publisher.
- **Needs work.** The standard is "v0" in its own name (`STANDARD = "ERW Data Standard v0"` in
  `warehouse/validate/erw_validate.py`). The paper needs a version a reader can cite: the standard numbered and
  frozen at the release the paper cites. That is a decision (cover note, 4), then a session's work.

### 2. The harmonization

The IRW's central claim is that many sources in one shape can be pooled. The ERW's equivalent is that sources of
different kinds join by key. The figures must show a join, not a table.

- **Today, in v1.** Figure 5 (list below): EIA's two federal series against each other by balancing authority,
  `eia_annual_crosscheck_ba` (144 rows, 2023 to 2025; key `(entity, variable, ts_utc)`; variables
  `eia923_net_generation_mwh`, `eia930_net_generation_mwh`, `gap_pct`; method `docs/methods/eia_annual_crosscheck.md`).
  It needs only public, released tables and shows the point of a common shape in one chart.
- **Today, in v1.** The three demonstrations of session 139's section 5, where their tables are released:
  `ba_supply_monthly` (158,503 rows, 2019 to 2026; variables `net_import_share_pct`,
  `net_import_balance_share_pct`, `net_import_total_interchange_share_pct`), `battery_stack_monthly`,
  `ercot_storage_dam_awards_monthly`, `ercot_storage_dam_offers_monthly`, `ercot_storage_rt_monthly` and
  `grid_stress_yearly` (detail under "The uses").
- **Needs work.** A figure that joins prices across grids. Every table that holds more than one grid's prices in one
  shape is held out of v1 for a license: `iso_dam_hub_prices` (MISO), `hub_price_comparison` and
  `cost_of_power_monthly` (ISO-NE, MISO, NYISO), each "license needed from 2026-10-21" in `tables.csv`. Release v1's own
  ruling 2 (`docs/redivis/release-v1.md`, "For a ruling before the day") asks whether a copy without the held grids'
  rows could be in v1; until it is ruled, the harmonization of prices can be shown in the paper only for one grid
  (ERCOT, `ercot_hub_prices_daily`, 346,476 rows from 2015) or for tables a reader cannot download from the release.

### 3. The coverage

- **Today.** Figure 1: each table's span, `ts_min` to `ts_max`, grouped by sector, from `coverage.csv` (released as
  `erw_coverage` in v1). The earliest row is 1920 (`eia_crude_imports_by_country`); power is 173 of the 212 tables'
  sectors (a table can have several: carbon 16, oil 16, datacenters 13, gas 12, and ten more). Table B: tables and rows
  by sector and flag.
- **Needs work.** Two honest statements the figure will force, each needing a sentence and not a session: most hourly
  ISO tables begin in late August 2026 (for example `iso_dam_hub_prices` from 2026-08-26), and some families are split
  by period across tables (`caiso_fuel_supply_history` to 2025-06-01, `caiso_fuel_supply` from then). The figure should
  draw a family as one bar where the method notes say they continue each other; that mapping is not written down
  anywhere and is a session's work.

### 4. The licensing ledger

The part with no counterpart in the IRW paper, and the one the ERW can show best today.

- **Today.** Figure 3: the 212 tables by ERW verdict (130 public, 33 internal, 49 unsettled) and, for the 42 "license
  needed", by the publisher that decides them (`docs/licenses.md`, "Every table" and "Read these first": NYISO 31,
  ISO-NE 27, MISO 24, then news and datacenter publishers at 2 to 4 each). Table C: the 84 publishers read, each with
  the verdict "as the ERW is today" and "if the ERW sells anything". The paused publishers (2: MISO, and the Virginia
  State Corporation Commission, `paused_sources.csv`) named with their reasons.
- **Needs work.** The four permission letters (`docs/reviews/licenses/`) are drafted and not sent; the paper reports
  the ledger as of its release, so whatever the letters bring changes Figure 3 before it is drawn. And
  `docs/licenses.md` says of itself that no lawyer has read the verdicts; the paper must say so too.

### 5. The validator

- **Today.** Table D: the validator's rules from the code (`warehouse/validate/erw_validate.py`: the required
  columns, the reserved names, the unit set, the key's uniqueness, the three exit codes), as session 139's 3.2 planned.
  212 of 212 tables pass today. Figure 4: the run log, 6,312 rows from 25 September to 20 October 2026, by day and
  status (3,868 ok, 2,180 gap, 134 failed, 130 skipped; `run_status.csv`). The checks beyond the validator (session
  139's 3.3) with today's count of test files: 320 under `tests/`.
- **Needs work.** Session 139 asked for the number of tables the validator has blocked. The run log cannot give it:
  no `detail` in `run_status.csv` mentions the validator (0 of 6,312), and a blocked table is recorded as a failed
  step without saying which check failed it. Either the validator's exit is logged with its rule from now on (a
  session's work, and then the count starts at that day), or the paper says the log does not record it.

### 6. The citable release

- **Today.** Release v1 is packaged and checked, not released (`docs/redivis/release-v1.md`; session 375 spliced it).
  Table E: what is in it (135 tables, 3 metadata tables, 28,830,665 rows) and what is held (42 for a license, 2 for
  storage: `node_basis_daily`, `ercot_all_hub_prices_history`), from `tables.csv`.
- **Needs work.** The click, by a person. Before it: whether the dataset moves under Ben's Redivis organization first
  (`docs/redivis/organization-move.md`, prepared and not moved), and Redivis's storage (the free 10 GB is full;
  `docs/state/morning_2026-10-21_day.md`, item 1). The paper cannot be cited against a fixed dataset until v1 exists:
  this is session 139's "What the outline needs before drafting", item 1, still open.

### 7. The uses

Session 139's three demonstrations, each checked against what v1 holds.

- **5.1 California in EIA-930.** Today: the monthly figure (imports as a share of demand by two measures) from
  `ba_supply_monthly` (variables `net_import_balance_share_pct` and `net_import_total_interchange_share_pct`, key
  `(entity, variable, ts_utc)`), in v1. Needs work: the hourly offset by day for 1 November 2023 to 2 December 2025.
  `eia930_all_generation` holds hours from 2026-08-26 only, and `eia930_all_history` from 2018-01-01 to 2018-07-01
  (`coverage.csv`); the hourly series the finding rests on is not in a held table today. Either it is pulled again
  into a table (the data machine's work, a pull no chain has approved) or the figure is the monthly one alone.
- **5.2 What Texas batteries earn.** Today, all in v1: `battery_stack_monthly` (the model, variables of the form
  `<strategy>_<N>h_revenue_total_usd_per_mw`, Decision 38), `ercot_storage_dam_awards_monthly` (`energy_sold_usd`,
  `mw`, `days_held`), `ercot_storage_dam_offers_monthly` (the offer by price band) and `ercot_storage_rt_monthly`
  (`revenue_da_usd_per_mw`, `rt_discharge_mwh`). The awards table holds December 2025 to August 2026. Needs work: none
  for the figure; the ruling session 139 named (resource by resource or fleet totals) is still open.
- **5.3 When Texas is tight.** Today, part one: `grid_stress_yearly` (variable `tight_solar_share_of_capacity_pct`,
  2019 to 2026), in v1. Needs work, part two: the flat and flexible cost per MWh is in `cost_of_power_monthly`, held
  out of v1 for the other grids' rows; an ERCOT-only copy, or release ruling 2, is needed for the figure to be
  reproducible from the release.
- **Section 6, large load in line.** Today: `large_load_public` (341 rows, public, in v1; `event_id`; columns
  `stage_class`, `entity_group`, `mw_low`, `mw_high`, `wait_basis`). It replaces the pilot session 139 named as the
  source of Figure 4. The internal `large_load_statements` (798 rows) stays out of the paper.
- **Faults found.** Table 2 of session 139's section 4 is `known_data_faults` (28 rows, 2018-07-20 to 2026-10-05,
  `event_id`; columns `x_publisher_source`, `x_evidence`, `x_erw_does`, `x_resolution`), in v1. Today.

### The figure list

| # | Figure | Tables (all in `coverage.csv`) | In v1 | Today or needs work |
|---|---|---|---|---|
| 1 | Each table's span by sector | `erw_coverage` (from `coverage.csv`) | yes | today; a family drawn as one bar needs the mapping written |
| 2 | Tables and rows by shape and tier | `coverage.csv`, `tables.csv` | yes | today |
| 3 | The licensing ledger: tables by verdict and deciding publisher | `docs/licenses.md`, `license_status.csv` | the ledger is a document | today; redrawn after the letters |
| 4 | The run log by day and status | `run_status.csv` | not a table of v1 | today; validator blocks need logging |
| 5 | EIA-923 against EIA-930 by balancing authority | `eia_annual_crosscheck_ba` | yes | today |
| 6 | California: imports by two measures by month; the hourly offset | `ba_supply_monthly`; the hourly offset needs a table | yes; no | monthly today; hourly needs a pull |
| 7 | Battery model against day-ahead awards; the offer curve | `battery_stack_monthly`, `ercot_storage_dam_awards_monthly`, `ercot_storage_dam_offers_monthly`, `ercot_storage_rt_monthly` | yes | today |
| 8 | Solar in Texas's tight hours by year | `grid_stress_yearly` | yes | today |
| 9 | Flat and flexible cost per MWh by year | `cost_of_power_monthly` | no (held) | needs release ruling 2 or an ERCOT-only table |
| 10 | Large load statements by entity and stage | `large_load_public` | yes | today |

The tables of the paper: A (v1 by shape and tier), B (tables and rows by sector and flag), C (the publishers and their
verdicts), D (the validator's rules), E (what v1 holds and holds out), and session 139's Table 2, now
`known_data_faults`.

### The author roles

**The master plan is not in the repository.** The chain asks for the author roles "as the master plan states them";
a search of every file for `02_master_plan` and for "master plan" finds only references to it (the chain files of
20 and 21 October, `docs/reviews/research/ask-the-grid-landscape-2026-10.md`, `site/lib/board4.ts`), not the plan.
No role is quoted here for that reason. What the repository records, for Samuel's and Ben's ruling:

- Samuel builds and maintains the ERW, "as a Stanford independent study" (`README.md`, "Lineage"); one maintainer
  (session 139's section 7).
- Ben Domingue's Item Response Warehouse is the template the ERW copies with its owner's permission (`README.md`,
  "Lineage"); Ben reviewed the ERW on 28 September 2026 (`docs/feedback/ben-2026-09-28.md`), and the review changed the
  standard (decision 28) and the store design (`ARCHITECTURE.md`, section 1a); the Redivis dataset is prepared to move
  under Ben's organization (`docs/redivis/organization-move.md`).
- `docs/roadmap.md` names Ben and Khalid as giving input ("Input from Ben and Khalid", empty today).

Samuel pastes the master plan's lines on authorship into this file, or rules them here.

### Cover note: five decisions the paper needs from Samuel and Ben

1. **Authors and their order**, with what each did, against the master plan's lines (not in the repository; above).
2. **Which release the paper cites, and under whose name.** v1 as packaged (135 tables, 42 held for a license), and
   whether it is released under Ben's Redivis organization or the owner's account (`docs/redivis/release-v1.md`,
   ruling 3). The citation, every figure's reproduction and section 6 of the paper all wait on this click.
3. **The held tables.** Whether the paper uses only what v1 holds (then Figure 9 and every cross-grid price figure
   leave the paper, and harmonization is shown on EIA's series and one grid), or v1 first takes copies without the
   held grids' rows (release ruling 2).
4. **The standard as cited.** Whether "ERW Data Standard v0" with its 48 decisions is frozen and numbered at the
   release, so that the paper and the validator cite one version.
5. **The demonstrations.** Whether the California demonstration stays with its hourly figure (which needs EIA-930's
   hourly generation for November 2023 to December 2025 pulled again into a table, a pull no chain has approved) or
   becomes the monthly figure only; and whether the 20 model-extracted tables (`coverage.csv`, tier) are in the paper's
   scope at all, given that each depends on a commercial model (session 139's section 7).
