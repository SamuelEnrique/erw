# The data machine's note of the chain of 21 to 22 October, night: more public sources (written 21 October 2026, about 19:45 UTC)

Energy Research Warehouse (ERW), session 515, for Samuel. The data machine's chain 026 (sessions 510 to 515, `queue/done/026-night-21-october-sources.md`), unattended on lab-desktop, from 19:24 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-22_sources_data.md`](note_2026-10-22_sources_data.md) (chain 022, landed as `5c9e2f66`).

## Read these first

- **Four new tables, 470,426 rows, held on the data machine and in the archive.** None is in the live set, and none was uploaded to Redivis. The three public tables are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Source | Table | Rows | Cross-check |
  |---|---|---|---|---|
  | 510 | Form EIA-923, plants by fuel, annual 2020 to 2024 | `eia923_plant_fuel_annual` | 268,344 | eGRID2023 by plant: median 1.0000, 99.9% within 1%; U.S. totals within 0.5% of EIA's |
  | 511 | Form EIA-861M, sampled utilities, 2025-01 to 2026-07 | `eia861m_utility_sales_monthly` | 180,161 | the annual EIA-861 for 2025: median 1.0000, 81% within 2%; 13% differ by over 10% (cause not established) |
  | 513 | EIA's U.S. nuclear outages, daily 2007 to 2026 | `eia_nuclear_outages_daily` | 21,702 | the NRC's reactor status: correlation 0.989 |
  | 514 | FERC Form 714's respondents (PUDL) | `ferc714_respondents` (internal) | 219 | every demand table's respondent is in it; 109 respondents link to an EIA-930 balancing authority |

- **Not pulled:**
  - **DOE's Loan Programs Office portfolio** (512). The office is now the Office of Energy Dominance Financing. Its projects are only in a map application, with no file (`lpoapps.loanprograms.energy.gov`, whose certificate chain also fails Python's check).
  - **OE-417** (513), again. The old host does not resolve, and EIA's Table B.1 is stale (January to March 2024). EIA's nuclear outages were pulled in its place, by the chain's rule.
- **One fault caught by a test before the write** (514): PUDL's whole-number ids with a blank beside them came out as "200.0".
- **Vercel's deploys are rate limited until about 19:30 UTC on 22 October** ("retry in 24 hours"), for chain 022's landing and every push since. The site did not change, and the snapshots show 0 differences on all 25 pages. All pages are in review.

## What each session landed

All on `task/510-515-sources` (this landing):

| Session | What |
|---|---|
| 510 | `warehouse/connectors/eia923_plant_fuel.py`, with tests; a saved page is reused |
| 511 | `warehouse/connectors/eia861m_sales.py`, with tests; `--offline` |
| 512 | its report |
| 513 | `warehouse/connectors/eia_nuclear_outages.py`, with tests |
| 514 | `warehouse/connectors/ferc714_respondents.py`, with tests |
| 515 | this note and the next file |

Every table's metadata (coverage, archive manifest, sources, licenses) and holds are in the same landing.

## Pulls against their ceilings

| Session | Host | Used | Ceiling |
|---|---|---|---|
| 510 | api.eia.gov | 31 | 40 |
| 511 | www.eia.gov | 6 | 6 |
| 512 | www.energy.gov, lpoapps.loanprograms.energy.gov | 5 | 10 |
| 513 | www.oe.netl.doe.gov, www.eia.gov, api.eia.gov | 8 | 8 |
| 514 | PUDL's bucket | 0 | 2 |

## Decisions made without you (one line each; the reasons are in each report)

- 510: annual only, and each plant's own total kept as its own entity.
- 511: 2025 and 2026 only, to keep within the ceiling.
- 512: no connector built on a map application's undocumented calls.
- 513: EIA's U.S. nuclear outage total in OE-417's place; the plants left for the next chain.
- 514: the balancing-authority link kept as a cross-check, not a column.

## Waiting for Samuel, highest value first

1. Chain 022's list stands unchanged (`docs/state/note_2026-10-22_sources_data.md`): first the daily recompute against the cards' tests, then FERC 714's license. `ferc714_respondents` follows FERC 714's ruling.
2. **EDF's projects**: read from the map application's own data calls, asked of DOE as a file, or left (512).

## The other machines

- The code machine's `queue/next/025-night-21-october-code-506.md` waits for a code machine.
- The old laptop's chain 024 holds sessions 531 to 542.

## The next chain

`queue/next/027-night-22-october-sources.md` (sessions 516 to 522, free in every queue file and branch) was pushed to main on its own, with snapshots, before this landing. It holds:

- 516: EIA's nuclear outages by plant;
- 517 and 518: natural gas prices and consumption by state;
- 519: EIA's coal production by mine;
- 520: EIA-861M's back years;
- 521: the 861M gaps, read;
- 522: the note and the queue.
