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
