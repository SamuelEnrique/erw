# Session 2605 report: Djibouti's electricity not taken (the utility's host does not answer, the statistics office's site is drawn by script, its 2021 yearbook ends in 2020)

25 October 2026, about 05:06 to 05:12 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2605.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 fetch).

## Read these first

- **No table.**
  - **The utility, Electricite de Djibouti (EDD):** www.edd.dj and edd.dj time out over https, and www.edd.dj over http (reads 1194, 1196 and 1197).
  - **The statistics office, INSTAD:** its robots file names `*` with no rule (read 1193). Its home page (read 1195) is empty: the page is drawn by script from an API, with no text, links or terms. Earlier chains did not take sites drawn by script (ANSADE, PNG Power), and INSTAD's terms cannot be read.
  - **Its Annuaire Statistique, Edition 2021,** is copied on the Chamber of Commerce's host, ccd.dj, whose robots file allows `/` (read 1198). It was fetched once (107 pages, 1.9 MB, last modified 20 October 2022). Its Table 3.1.6, "Production et consommation d'electricite (2016-2020)", source EDD/DE, gives subscribers, production (627,111 MWh in 2020), "dont Energie importee", consumption (517,035 MWh in 2020), the commercial yield and the average price.
- **Why the yearbook's table was not taken:**
  - Its figures end in 2020.
  - The copy is a third party's, and the publisher's own terms cannot be read.
  - Its import row prints four figures under five years, so the run cannot place them without guessing.
- **Against EIA** (`eia_world_electricity_annual`, read past its header lines): EIA's Djibouti generation is the yearbook's production less its imports, if the four import figures are 2016 to 2019. That gives 87.8 against EIA's 88.3 GWh (2016), 58.7 against 59.2 (2017) and 54.8 against 55.8 (2018), but 103.4 against 92.3 (2019). EIA's consumption (430.4 GWh in 2016, 503.4 in 2020) is close to the yearbook's (422.8 and 517.0).

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.instad.dj's robots file | 200 |
| 2 | www.edd.dj's robots file | ConnectTimeout |
| 3 | INSTAD's home page | 200, an empty page drawn by script |
| 4, 5 | edd.dj's robots file; www.edd.dj's over http | ConnectTimeout |
| 6 | ccd.dj's robots file | 200 |
| 7 | the Annuaire Statistique 2021 on ccd.dj (a fetch) | 200, 1.9 MB |

Reads recorded: 1193 to 1198. No verdict: no publisher's terms could be read.

## Decisions made without you

- **Djibouti not taken,** for the three reasons above. No figure taken from the French Treasury's country notes or other secondary sources.
- **No other grid source taken in its place:** none was found that is public and first-hand within the ceiling.

## For Samuel's ruling

- **Whether a later chain may take INSTAD's Table 3.1.6 from the copy on ccd.dj** (2016 to 2020, internal), placing the import row's four figures in 2016 to 2019 as EIA's figures suggest.

## Files

- New: this report.
- Changed: the license record (reads 1193 to 1198) and `docs/licenses.md`.
- On the data machine only: `runs/c129/s2605/`, `runs/license_reads/s2605/`, `warehouse/raw/instad_dj/`.
