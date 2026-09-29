# SESSION 31: Emissions and storage

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_30_REPORT.md,
the EIA-930 connector and its raw-file and paging logic, the erw-add-connector skill,
the entities tables (eia860m_*_generators), the /grid page as the pattern to follow.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls of any kind.
- Approved pull (Samuel, in chat, Sept 29): EIA-930 hourly CO2 emissions estimates for
  the seven ISO balancing authorities plus US48 from the start of the series, and, only
  if the warehouse does not already hold it, the EIA-930 battery storage series (BAT)
  for the same BAs and range. Ceiling for this session: 1.2 million new rows total.
  Nothing else is pulled. No re-pull of any existing table.
- No time cap; no redundant work; one table in memory at a time; stream with pyarrow;
  pull in pages, save raw pages as the connector already does, resume from the last
  saved page if interrupted, never restart a pull from zero.
- The GitHub daily job runs at 14:00 UTC (7am Pacific) and may land while you work:
  git pull and merge before pushing, never force push.
- Every number on both pages comes from a warehouse table. No placeholders.

## Health gate (first)
This session adds sources, so PRIORITIES.md's health gate applies. Read the last daily
run. If it failed outside the known-gap list, the gate is closed: do only Part C4
(storage capacity from tables we already hold) and the report, and stop. If the gate is
open, proceed.

## Part A: emissions
A1. Find the exact EIA API v2 route for the EIA-930 CO2 emissions estimates (the
    aggregates by BA, and the imports-adjusted series if EIA publishes one), using the
    same API key as the existing EIA-930 connector. Record the route, the series start
    date and EIA's own methodology note in the source registry and docs/methodology.
A2. One connector, one table `eia930_all_emissions` with a `ba` column (the partition-
    column rule), hourly, from the series start, public license, tier source. Raw pages
    saved. Validator, archive, coverage.
A3. Derived table `carbon_intensity_hourly` (tier derived): emissions divided by demand
    and by generation, both, per BA per hour, using EIA's definitions, with the
    difference explained in methodology (imports). Derived `carbon_intensity_daily` and
    `carbon_intensity_monthly` from it.
A4. Page /emissions: intensity now per ISO (kg CO2 per MWh, ranked), last 24 hours as a
    curve per ISO, monthly since the series start, the cleanest and dirtiest hour of the
    last week per ISO, tier chips and citations, methodology link. Stanford palette.

## Part B: storage
B1. Check whether eia930_all_generation already carries the BAT fuel type and how far
    back it goes. If it does and covers the series start, no pull. If not, pull BAT for
    the eight BAs from the series start into `eia930_all_storage` (charge negative,
    discharge positive, as EIA reports it), within the row ceiling.
B2. Derived `storage_daily_cycle` (tier derived): per BA per day, MWh discharged, MWh
    charged, peak discharge hour, peak charge hour, round-trip ratio where both exist.
B3. Page /storage: fleet in operation and planned (from Part C4), by state and by ISO,
    the daily cycle per ISO for the last 30 days as an hourly profile, the last 24 hours
    charge and discharge curve, planned additions by year. Tier chips, citations,
    methodology link.

## Part C: storage capacity from what we hold
C4. Derived `storage_capacity` (tier derived) from the three eia860m generators tables:
    battery units by state, operator, ISO where mappable, status (operating, planned,
    retired), nameplate MW, energy MWh where reported, planned operating year. No pull.

## Part D: plumbing for every new table
Validator, archive (new names, append-only), Supabase live set (hourly tables: the
last 90 days only; daily and monthly derived tables: full), Redivis draft upload
(public), coverage table, llms.txt, chat catalogue, nav links for the two pages,
check-routes and check-values extended with the new pages, package tests. The daily
workflow pulls the new series going forward with the same idempotent merge as EIA-930
demand. Deploy is the last step; live route check after it.

## Do not
No model calls, no pulls beyond the approved scope, no re-pulls, no schema changes to
existing tables, no deletions from Redivis, no gate changes, no force push.

## Report: archive/sessions/SESSION_31_REPORT.md
1. Rows pulled per table against the 1.2M ceiling; the EIA routes and series starts.
2. The two pages: what is shown, from which tables, what is missing and why.
3. Reconciliation: validator, archive, Supabase sizes before and after, Redivis uploads.
4. Decisions made without a human, each reversible.
5. Run health, gate state at start and end, whether the 14:00 UTC run landed.
6. Spend USD 0 confirmed. Open questions for Samuel. What was skipped.
Commit after every working step. Push at the end. Stop.