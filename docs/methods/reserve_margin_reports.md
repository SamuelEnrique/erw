# Grid operators' reserve margins, as their own assessments print them (`iso_reserve_margin_reports`)

Energy Research Warehouse (ERW), session 3798 (chain 215), 12 November 2026.

## What it holds

One row a figure that a grid operator's own resource adequacy assessment prints for a season or a year. A session reads
the document and writes each figure into the registry (`warehouse/sources/reserve_margins/`, one file a document) with
its page and its printed words. `warehouse/connectors/reserve_margin_reports.py` turns the files into rows; it makes no
request. Nothing is estimated, derived or converted.

| Variable | Unit | What the document says it is |
|---|---|---|
| `prm_achieved_pct` | pct | the planning reserve margin its model achieves in its tightest hour |
| `prm_required_pct` | pct | the margin it finds is needed to meet its reliability target |
| `capacity_surplus_mw` | MW | the capacity above that target |
| `peak_forecast_mw` | MW | the peak the assessment plans for |
| `ra_prm_load_weighted_pct` | pct | the margin the load-serving entities must carry, load-weighted |

## What it holds now

- **CAISO, 2026 Summer Loads and Resources Assessment (May 2026)**, for the summer of 2026 (`ts_utc` 2026-06-01):
  - an achieved PRM of 30.8 percent in the tightest hour (page 15);
  - a requirement of 25 percent to meet the 0.1 LOLE target (page 15);
  - a surplus of 2,547 MW above that target (page 3);
  - the CEC's 1-in-2 peak of 46,844 MW in September, hour ending 18 (page 3);
  - a load-weighted RA planning reserve margin of 17.5 percent (page 15).
  - Read from www.caiso.com (robots allow `/documents/`; the CAISO's terms on file).

## What it does not hold, and why

- **ERCOT:** its Capacity, Demand and Reserves report is its own table, `ercot_cdr_reserve_margins` (session 1027).
- **NERC's Long-Term Reliability Assessment** (every assessment area's anticipated reserve margin): www.nerc.com's robots file disallows `ClaudeBot`, `anthropic-ai` and `Claude-Web` by name, so it is not read (session 3798).
- **PJM, MISO, SPP, NYISO and ISO-NE's own reports:**
  - PJM's non-member terms bar this use;
  - MISO is paused;
  - SPP's license is unanswered;
  - NYISO's and ISO-NE's tables are held for a license.

## Limits

- A reserve margin is a forecast for a season, by each operator's own method; the CAISO's and ERCOT's are not the same measure. The CAISO's achieved PRM is in its tightest net-peak hour after battery dispatch; ERCOT's is at its peak load hour with wind, solar and storage at their ELCCs. They are not compared across grids.
- A document's period is its own ("summer 2026"); `ts_utc` is that period's first day.

## License

Public, row by row: a document is written here only where its publisher's terms allow it (`warehouse/metadata/license_verdicts.csv`: the CAISO's says its materials are "freely available for public use").

## Replication

`python warehouse/connectors/reserve_margin_reports.py --out-dir <folder>` writes the table from the registry; each row's `source_url` and `x_page` lead to the figure.
