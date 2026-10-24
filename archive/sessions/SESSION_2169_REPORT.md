# Session 2169 report: the Canadian pipelines that cross the U.S. border (the CER's throughput and capacity), a second source of the session's own choosing

24 October 2026, from 00:39 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 14 requests of 20 (below).

## Read these first

- **Why this source:** the Canada Energy Regulator publishes each regulated pipeline's throughput and capacity at its key points, the volumes behind the Canadian oil and gas trade the warehouse holds in `cer_gas_trade` and `cer_electricity_trade`; the ERW held none of it and no queue file plans it.
- **Finding the files:** the CER moved its site, and its old throughput folder and pipeline profile pages answer with a "not found" page served as HTTP 200 (reads 318, 319). The Government of Canada's open data catalogue (open.canada.ca, read 320) lists the dataset "Pipeline Throughput and Capacity Data" with every file's address under `www.cer-rec.gc.ca/open/energy/throughput-capacity/` and its licence, the **Open Government Licence - Canada** (read 321, a new verdict entry, may be public in both columns; the CER's own site terms, read 96, govern its other pages).
- **One table written, validated, archived, in coverage (sectors oil and gas), in the release package, both holds:** `cer_pipeline_throughput`, the nine pipelines that cross the U.S. border: Keystone, Enbridge's Canadian Mainline, Southern Lights and Cochin (oil, a month, by product) and Foothills, Alliance, Westcoast, TC Canadian Mainline and Maritimes & Northeast (gas, a day); 408,073 rows, 2006 to June 2026 (Keystone from 2010).
  - **A new unit, `m3/d` (Decision 69):** the CER gives oil and gas alike in thousand cubic metres a day, written here times 1,000. It is a rate, never summed over days, and oil and gas cubic metres are never added. Chain 090 holds Decision 67 and chain 092 holds 68, so this chain's first is 69, as its agent agreed.
  - **The keys:** an oil line's volumes by key point, product and trade type (Enbridge's ex-Gretna carries one product as export and as intracanada flow); a key point's oil capacity written once a month, not for each product (the run stops if the products disagree); a gas line's rows by key point and direction of flow (Westcoast's Kingsvale carries flow both ways). Enbridge's Mainline file gives no committed or uncommitted volumes.
- **The cross-check** (`runs/c094/s2169/cross.py`):
  - Keystone's and Enbridge Mainline's rows the CER labels export carry 365 to 411 million barrels a year from 2021 to 2025, 0.263 to 0.277 of EIA's crude imports from Canada (`eia_crude_imports_detail_monthly`, 1,372 to 1,487 million barrels): a steady share, the rest reaching the U.S. through other key points and trade types, Trans Mountain's tankers, the Express pipeline and rail.
  - Throughput exceeds the CER's capacity in 5,939 of 202,861 key point periods (2.9%): the CER's capacity is an estimate it revises, and its notes say so.

## The pulls

1. `www.cer-rec.gc.ca/robots.txt` (read 317, read again).
2. The old throughput folder (read 318): a not-found page.
3. Keystone's old profile page (read 319): a not-found page.
4. `open.canada.ca/robots.txt` (read 320): a crawl delay of 20 seconds, kept.
5. The catalogue search (read 321).
6 and 7. Keystone's and Alliance's files, for their columns (seeded into the raw store).
8 to 14. The connector's trial: the other seven files, reused by the write (`--offline`).

## Errors

- **The trial stopped three times before it ran:** Enbridge's shorter oil header, a key given twice at Enbridge's ex-Gretna (export and intracanada), and one at Westcoast's Kingsvale (two directions). Each was met by the key above; the files already fetched were reused.
- **The verdict's first sentence was assembled from the catalogue's fields;** it is now the record's exact text, as the license record requires.

## Decisions made without you

- **The CER's pipeline data as the session's own choice,** nine of its twenty-two pipelines, those that cross the border, within the ceiling.
- **The Open Government Licence - Canada taken for the dataset,** as the catalogue states it.
- **`m3/d` as Decision 69,** the CER's thousands times 1,000.
- **The gas files' GJ/d left out,** the volume being the same flow.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cer_throughput.py`, `tests/test_session2169.py`, this report.
- Changed: `docs/datastandard.md` (Decision 69), `warehouse/validate/erw_validate.py` (`m3/d`), `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (317 to 321), `license_verdicts.csv` (the CER under the Open Government Licence), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c094/s2169/`, `runs/license_reads/s2169/`, `runs/s2169_*`, `warehouse/raw/cer_throughput/`.
