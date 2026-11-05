# Session 574 report: petroleum supply and disposition, twelve more products

21 October 2026, from 23:52 UTC, on lab-desktop (the data machine), a session of `queue/done/033-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_petroleum_snd_monthly` now holds twenty products**: 222,496 rows, 1,832 series, January 2015 to July 2026. Session 555 held eight products.
  - The twelve added: kerosene, aviation gasoline, asphalt and road oil, petroleum coke, lubricants, natural gas plant liquids, ethane, normal butane, isobutane, unfinished oils, biodiesel and renewable diesel.
- **Not all the route's products, within the ceiling.** The other twenty products would have been about 89 pages, so the twelve most used were taken (26 pages). The rest are left for a later run, as a third group.
- **The connector reads its products in groups** (`GROUPS` in `eia_petroleum_snd.py`). The first group's request is session 555's own, so its saved pages were reused, and only the second group was asked.
- **Cross-checks**:
  - the 144 new series that `eia_product_supplied_monthly` (session 556) also holds are equal on all 15,088 rows;
  - all 100,340 of session 555's rows are unchanged.
- **Written under the data lock** (23:56 UTC) with `--offline` (0 requests): 122,156 new rows archived. The release row was replaced. Session 555's test now reads the first group; `tests/test_session574.py` (with 575's) holds the groups.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 26 of 30 | the second group (the trial); the first group reused |

## Files

- New: `tests/test_session574.py`, this report. Changed: `warehouse/connectors/eia_petroleum_snd.py`, `tests/test_session555.py`, `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `warehouse/metadata/{coverage,archive_manifest}.csv`.
