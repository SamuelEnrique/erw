# Sessions 600, 603 and 604 report: petroleum's third group of products, drilling activity, gas wells

21 and 22 October 2026, from 00:21 UTC on 22 October, on lab-desktop (the data machine), three sessions of `queue/done/035-night-22-october-sources.md`, reported together (603 and 604's trials ran while 600's was asking EIA). Model spend USD 0.

## Read these first

- **600: `eia_petroleum_snd_monthly` now holds thirty products**: 356,682 rows, 2,866 series, 2015 to July 2026 (134,186 new).
  - The third group (`GROUPS[2]`) has ten products: NGLs and liquid refinery gases, other liquids, natural gasoline, finished petroleum products, hydrogen, oxygenates and other hydrocarbons, biofuels, gasoline blending components (all and conventional), conventional motor gasoline, and ultra-low-sulfur distillate.
  - The first two groups' pages were reused.
  - Cross-checks: the 120 new series also in `eia_product_supplied_monthly` are equal on all 13,800 rows, and all 222,496 earlier rows are unchanged.
  - 28 products are still left (about 37 pages), for session 601.
- **603: `warehouse/connectors/eia_drilling.py`**, rotary rigs (all, crude oil, natural gas; onshore and offshore) and well service rigs, from route `petroleum/crd/drill`, as `eia_drilling_monthly`: 3,431 rows, 6 series, January 1973 to February 2026 (`count`).
  - Onshore plus offshore equals the U.S. in 584 of 638 months.
  - Gas plus oil rigs fall short of all rigs in many months. My reading, not EIA's statement, is that the total also counts rigs drilling for neither.
- **604: `warehouse/connectors/eia_gas_wells.py`**, producing gas and gas condensate wells by state, from route `natural-gas/prod/wells`, as `eia_gas_wells_annual`: 1,062 rows, 36 series, 1989 to 2020 (`count`; EIA's route ends in 2020). The states and the federal Gulf equal the U.S. in all 32 years (483,326 wells in 2020).
- All three written under the data lock (00:36 UTC) with `--offline` (0 requests); validated, covered, archived and held. The petroleum table's release row was replaced. Tests: `tests/test_session600.py`, 5; session 574's test now checks only the first two groups.

## Pulls against their ceilings

| Session | Requests | Ceiling |
|---|---|---|
| 600 | 28 | 29 |
| 603 | 2 | 10 |
| 604 | 2 | 10 |

## Files

- New: `warehouse/connectors/eia_drilling.py`, `eia_gas_wells.py`, `tests/test_session600.py`, this report. Changed: `warehouse/connectors/eia_petroleum_snd.py`, `tests/test_session574.py`, the shared metadata, holds and package.
