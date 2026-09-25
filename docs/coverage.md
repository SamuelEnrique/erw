# ERW coverage

What the Energy Research Warehouse (ERW) holds today: one row per table in `warehouse/output/`. The machine-readable copy is `warehouse/metadata/coverage.csv`, the ERW equivalent of the metadata table the IRW (Item Response Warehouse) calls `metadata.csv`.

**Generated, do not edit by hand.** Rebuilt by the daily workflow, or with `python warehouse/metadata/build_coverage.py`. Every value comes from the table's own rows, its provenance header, or `erw_validate.py`. Interval timestamps are interval starts; day-ahead tables can run past today because a published next-day auction is included.

| Table | ISO | Market | Variable | Nodes | Interval | First interval (UTC) | Last interval (UTC) | Rows | Source report | Last run (UTC) | Validator |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `caiso_dam_hub_prices` | CAISO | caiso_dam | lmp_dam | 3: TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | PT1H | 2026-08-26 07:00:00 | 2026-09-26 06:00:00 | 2,232 | caiso:PRC_LMP | 2026-09-25 07:12:46 | pass |
| `caiso_rtm_hub_prices` | CAISO | caiso_rtm | lmp_rtm_15m_mean | 3: TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | PT15M | 2026-08-26 07:00:00 | 2026-09-25 06:45:00 | 8,640 | caiso:PRC_INTVL_LMP | 2026-09-25 07:12:46 | pass |
| `ercot_dam_hub_prices` | ERCOT | ercot_dam | spp_dam | 5: HB_BUSAVG, HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST | PT1H | 2026-08-26 05:00:00 | 2026-09-26 04:00:00 | 3,720 | ercot:NP4-190-CD | 2026-09-25 06:37:20 | pass |
| `ercot_rtm_hub_prices` | ERCOT | ercot_rtm | spp_rtm | 5: HB_BUSAVG, HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST | PT15M | 2026-08-26 05:00:00 | 2026-09-25 04:45:00 | 14,400 | ercot:NP6-785-ER; ercot:NP6-905-CD | 2026-09-25 06:37:20 | pass |
| `isone_dam_zone_prices` | ISO-NE | isone_dam | lmp_dam | 9: .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE, .Z.NEMASSBOST, .Z.NEWHAMPSHIRE, .Z.RHODEISLAND, .Z.SEMASS, .Z.VERMONT, .Z.WCMASS | PT1H | 2026-08-26 04:00:00 | 2026-09-26 03:00:00 | 6,696 | isone:da_lmp_hourly | 2026-09-25 07:12:46 | pass |
| `miso_dam_hub_prices` | MISO | miso_dam | lmp_dam | 8: ARKANSAS.HUB, ILLINOIS.HUB, INDIANA.HUB, LOUISIANA.HUB, MICHIGAN.HUB, MINN.HUB, MS.HUB, TEXAS.HUB | PT1H | 2026-08-26 05:00:00 | 2026-09-26 04:00:00 | 5,952 | miso:da_expost_lmp | 2026-09-25 07:12:46 | pass |
| `nyiso_dam_zone_prices` | NYISO | nyiso_dam | lmp_dam | 11: CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | PT1H | 2026-08-26 04:00:00 | 2026-09-26 03:00:00 | 8,184 | nyiso:damlbmp | 2026-09-25 07:12:46 | pass |
| `nyiso_rtm_zone_prices` | NYISO | nyiso_rtm | lmp_rtm_15m_mean | 11: CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST | PT15M | 2026-08-26 04:00:00 | 2026-09-25 03:45:00 | 31,680 | nyiso:realtime | 2026-09-25 07:12:46 | pass |
| `spp_dam_hub_prices` | SPP | spp_dam | lmp_dam | 2: SPPNORTH_HUB, SPPSOUTH_HUB | PT1H | 2026-08-26 05:00:00 | 2026-09-26 04:00:00 | 1,488 | spp:DA-LMP-SL | 2026-09-25 06:59:20 | pass |

Markets with no table: MISO RTM, SPP RTM, ISO-NE RTM. PJM is not covered: its data API needs a key the ERW does not have yet. Why a market is missing is in the latest session report and the ISO's run log in `warehouse/output/logs/`.
