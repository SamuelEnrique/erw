# SESSION 32: Emissions from EIA's per-BA files

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_31_REPORT.md
(section 1), the EIA-930 storage connector (the pattern: raw files, paging, resume,
completeness), the /storage page as the page pattern.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- Approved pull (Samuel, Sept 29): EIA-930 hourly CO2 emissions estimates for the seven
  ISO balancing authorities plus US48, from the series start (2018-07-01), from EIA's
  per-balancing-authority Excel workbooks. Ceiling: 1.2 million new rows. Nothing else
  is pulled; no re-pull of any existing table.
- Target: about 90 minutes. Keep the scope below and no more; if the pull is slower
  than that, finish the pull and the table, write the report, and leave the page for
  session 33, saying so.
- One table in memory at a time; stream with pyarrow; save every raw file; resume from
  the last saved file if interrupted.
- The GitHub daily job may land while you work: git pull and merge before pushing,
  never force push.
- Every number on the page comes from a warehouse table. No placeholders.

## Health gate (first)
Read the last daily run. If it failed outside the known-gap list, the gate is closed:
stop and report; do not pull.

## Where the data is
Session 31 looked in the API, the six-month bulk CSVs and the Grid Monitor's code and
found no CO2 series. EIA publishes the hourly CO2 estimates in the per-balancing-
authority Excel workbooks on the EIA-930 site (the Grid Monitor's per-BA download),
with estimated total CO2, CO2 by fuel type, and CO2 for imports and exports, from
2018-07-01. Find those workbooks, record their URLs, sheet layout and EIA's methodology
note (the "About the EIA-930 data" page, estimated CO2 emissions) in the source
registry and docs/methods/emissions.md.

## Part A: the tables
A1. `eia930_all_emissions`: one connector, `ba` partition column, hourly, tier source,
    public license, the eight BAs from the series start. Variables: total CO2, CO2 by
    fuel where the workbook has it, imports and exports CO2. Units as EIA states them.
    Completeness per UTC day (session 16's rule). Validator, archive, coverage.
A2. `carbon_intensity_hourly` and `carbon_intensity_daily` (tier derived): CO2 per MWh
    of generation and per MWh of demand, per BA, from A1 with eia930_all_generation
    and eia930_all_demand; the difference is imports, explained in the method page.
    Monthly comes in session 33.
A3. The daily workflow refreshes the series: pull the newest workbook per BA, merge on
    (entity, variable, ts_utc), keep the raw copy. Supabase live set: last 90 days of
    the hourly tables, the daily table whole. Redivis draft upload, public. llms.txt
    and the chat catalogue.

## Part B: the page, two blocks only
/emissions (nav: Grid, then Emissions, before Storage): carbon intensity now per ISO,
ranked, kg CO2 per MWh; and the last 24 hours per ISO as one chart. Tier chips,
citations, method link, Stanford palette. check-routes and check-values cover it.
Deploy is the last step; live checks after it.

## Do not
No pulls beyond Part A, no re-pulls, no model calls, no deletions from Redivis, no gate
changes, no force push, no estimate of emissions of our own, no extra blocks on the
page.

## Report: archive/sessions/SESSION_32_REPORT.md
The workbooks used, rows pulled against the ceiling, series start per BA, what the page
shows, Supabase size before and after, Redivis counts, decisions made without a human,
run health and whether the daily run landed, spend USD 0 confirmed, wall time, open
questions, skipped. Commit after every working step. Push at the end. Stop.