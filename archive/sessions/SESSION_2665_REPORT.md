# Session 2665 report: Alaska's electricity generation a month by service area and fuel, 2001 to 2021 (the Alaska Energy Data Gateway), public, a second source of the session's own choosing

25 October 2026, about 10:34 to 10:43 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2665.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 fetch of the dataset, about 38 MB, into the raw store, which the trial and the write read offline); two web searches.

## Why this source

- **Alaska's small grids,** most of them off any interconnection, are in the ERW only where their plants report to EIA. The Gateway joins the Alaska Energy Authority's PCE reports to EIA's, community by community. It is a US source, and no chain or record had named it.
- **Tried first:**
  - The Palestinian Central Bureau of Statistics: its certificate fails verification (read 1365), so its host is closed.
  - Montenegro (MONSTAT) and El Salvador (UT) were tried by earlier chains.
  - Hawaii (DBEDT) is held (session 2580).
  - The Alaska Energy Authority's own site (read 1366) gives the PCE reports as PDFs. The searches found the Gateway's CSV datasets.

## Read these first

- **The host:** akenergygateway.alaska.edu's robots file closes `/search` to `*`. It closes `/` to GPTBot, Bytespider and some search engines' crawlers by name. The ERW's reader is not named (read 1367).
- **The terms** (read 1368, the dataset's page): "This work is licensed under CC-BY-4.0", with the Gateway's citation given.
  - **Verdict: may be public.** The table is **public**, cited as the page asks.
- **A new table, `aedg_alaska_generation_monthly`** (series, 51,061 rows, 271 entities, `power`), from "Monthly Electrical Generation By Community" v3.0:
  - It covers 2001 to 2021, a row a service area, month and fuel (`aedg:ak:<service area>:<fuel>`), in MWh as published.
  - The Gateway repeats each grid's figure for every community on it. One row is kept per service area, month and fuel; the communities' figures were checked equal, and the run stops otherwise.
  - No plant set is under two service areas, so the service areas do not double a grid and their rows can be summed.
  - The node names a service area's first community and how many others share its grid.
- **Figures:**
  - The service areas make 5.81 TWh in 2001, 4.37 in 2011 and 5.12 in 2021.
  - In 2021: natural gas 2.01, hydro 1.68, distillate oil 0.54, coal 0.50, waste oil 0.21 and wind 0.14.
- **Kept as published:**
  - 581 negative figures: net generation, and the storage row's own use.
  - 123 service-area months with the fuel left blank (item `fuel_not_given`).
  - The records with no year (communities without data) have no row, and the PCE fuel price is not taken.
- **Not all of Alaska:** EIA's state total in the ERW (`eia_state_generation_monthly`) is 6.60 TWh for 2021, against the service areas' 5.12. The header and the connector say so.
- **Its record:** written by run `20261025T103939Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T103945Z-local`), held from the live set, and in the release package (public). Its method note and the Stanford draft are session 2667's.
- **This time** the write's and the finish's results were read before the commit; both passed, with the patch applied cleanly.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.pcbs.gov.ps's robots file | the certificate fails |
| 2 | www.akenergyauthority.org's robots file | 200 |
| 3 | akenergygateway.alaska.edu's robots file | 200 |
| 4 | the dataset's page | 200 |
| 5 | the dataset (the fetch, JSON) | 200 |

Reads recorded: 1365 to 1368.

## Decisions made without you

- **The Gateway as the second own choice; public** under CC BY 4.0.
- **One row a service area,** not a community, so that sums are not doubled. The Gateway's community rows can be rebuilt from its own dataset.
- **Negative figures and blank fuels kept,** as the Gateway gives them.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/aedg_alaska_generation.py`, `tests/test_session2665.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1365 to 1368, the Gateway's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c133/s2665/`, `runs/license_reads/s2665/`, `warehouse/raw/aedg_ak/`, `warehouse/output/aedg_alaska_generation_monthly.csv`.
