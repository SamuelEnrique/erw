# Session 2821 report: Transelectrica not taken (HTTP 500 at its robots files); Europe's natural gas import dependency by country of origin, 2015 to 2020 (Eurostat, nrg_ind_idogas), in its place

26 October 2026, from about 06:35 to 06:41 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2821.out`). Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 by the fetch).

## Read these first

- **Transelectrica not taken: its host gives no robots file.** www.transelectrica.ro and transelectrica.ro both answer HTTP 500 at `robots.txt`, with the site's page in its place (reads 1635 and 1636). Nothing else was asked; the host is closed, as data.gov.tw's HTTP 500 was. Romania's grid figures are held daily through Energy-Charts.
- **In its place, `eurostat_gas_import_origin_annual`:** Eurostat's natural gas import dependency by country of origin (nrg_ind_idogas), 2015 to 2020.
  - Each European country's dependency on gas from seven partners: Algeria, Nigeria, Norway, Qatar, Russia, the United Kingdom and the United States. In pct.
  - **Eurostat last updated the dataset on 29 September 2022, and it holds no year after 2020**: the record of Europe's dependence on Russian gas before 2022.
  - 1,253 rows, 32 areas. The table has been written, validated, archived and put in coverage (sector `gas`). It is held from the live set and from Redivis storage until session 2829's draft.
- **Figures, 2020:**
  - Russia: Germany 68.66, Finland 82.23, Italy 43.72;
  - Italy also 22.84 on Algeria;
  - Bosnia and Herzegovina, Czechia, Latvia, Moldova, Serbia and North Macedonia 100 on Russia.
- **Zeros for origins not reported:** Austria and Georgia give 0 for every partner in every year. Those 12 country years are not written and are counted. 635 other zeros are kept, and 301 blanks (flag m) have no row.
- **Cross-check, and why it is not an identity:** the seven partners' sum was compared with each country's natural gas import dependency in `eurostat_import_dependency_annual` (nrg_ind_id, G3000), in 176 country years.
  - The median difference is 0.43 points, but 111 differ by more than 5: the sum is above in 41 and below in 70. Poland 2020 gives 95.23 here and 78.25 there; Finland 83.33 and 100.29; Germany 94.51 and 89.10.
  - **The two are different measures** (seven partners only, and Eurostat's own definition of each), so neither is read as the other. The connector's docstring and the note say so.

## The requests

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.transelectrica.ro's and transelectrica.ro's robots files | HTTP 500 |
| 3 | ec.europa.eu's robots file | 200, byte for byte session 2820's |
| 4 | nrg_ind_idogas's data (probe) | 200 |
| 5 | the same, into the connector's raw folder | 200, byte for byte |

Reads recorded: 1635 to 1638.

## Decisions made without you

- **Transelectrica's host closed at its robots files' HTTP 500.**
- **A discontinued dataset taken** (2015 to 2020), its end stated in the header.
- **All-zero partners read as origins not reported,** as for the household and industry splits.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_gas_import_origin.py`
  - `tests/test_session2821.py` (3 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1635 to 1638) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2821/`, `runs/license_reads/s2821/`;
  - `warehouse/raw/eurostat_gas_import_origin/`.
