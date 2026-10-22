# Session 601 report: petroleum supply and disposition, the fourth group

22 October 2026, from 00:47 UTC, on lab-desktop (the data machine), a session of `queue/done/035-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_petroleum_snd_monthly` now holds 47 products**: 475,869 rows, 4,030 series, January 2015 to July 2026 (119,187 new).
  - The fourth group (`GROUPS[3]`) has seventeen products, among them biofuels excluding ethanol, reformulated blending components, marketable petroleum coke, distillates by sulfur, miscellaneous products, petrochemical feedstocks, refinery olefins, waxes, propylene, oxygenates, butylene, condensate, other biofuels, reformulated gasoline and mid-sulfur residual fuel.
  - The first three groups' pages were reused.
- **Eleven small products are left**: special naphthas, naphtha for petrochemical feedstock, residual fuel above 1% and below 0.31% sulfur, isobutylene, ethylene, aviation gasoline blending components, other hydrocarbons, hydrogen, catalyst coke and still gas. They are named in the connector, for a fifth group if wanted (about 10 pages).
- **Cross-checks**: the 180 new series also in `eia_product_supplied_monthly` are equal on all 18,198 rows, and all 356,682 earlier rows are unchanged.
- **Written under the data lock** (00:53 UTC) with `--offline` (0 requests); validated and archived.
  - The metadata patch conflicted with session 600's version of the same row.
  - The branch's files were kept and only this table's line was replaced, as in session 549. There are no duplicate rows.
  - The release row was replaced. Session 600's test now checks the third and fourth groups.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 26 of 30 | the fourth group (the trial) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_petroleum_snd.py`, `tests/test_session600.py`, `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `warehouse/metadata/{coverage,archive_manifest}.csv`.
