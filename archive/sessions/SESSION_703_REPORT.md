# Session 703 report: transmission and the four peaks on the All grids tab

22 October 2026, from 09:13 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-703` on `wip/703-allgrids` (cut from `wip/702-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 703. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **ERCOT rows now carry the four-peak transmission charge** (`lib/siting.ts`, `cpCharge`).
  - It uses the four intervals of the newest whole summer held (2025, `ercot_4cp_intervals`) and the Commission's newest approved postage stamp rate (2025, USD 68.547301 per kW a year), taken exactly as "Your load"'s four-peak block takes them (`model.ts`; `newestRate` and `hourOf` repeat its steps).
  - USD per MWh = rate x 1,000 x the load's share of the four intervals it ran in / the hours it runs a year (the load's draw cancels).
  - **Three figures**:
    - the profile's own charge (it carries into the all-in figure);
    - **firm** (on in all four), 7.83 for a load that runs every hour: the same figure "Your load"'s matrix row gives a flat load (`tests/test_session703.py`);
    - **off** (a load off in the four intervals' hours, computed from its weights under the rule "off at the four peaks", not assumed): 0.00.
  - Flexible compute pays 0 because its rule is off at the peaks. The electrolyzer's own share is 0 too: each of the four intervals' hours in 2025 was above its strike (computed, hour by hour).
  - The tip names the four intervals as ERCOT prints them, whether the load was on or off in each, the rate and its document, and that the charge is paid the year after.
- **Every other grid: "not held"**, with the large-load tariff that would fill it named on hover. MISO: "paused".
- **The all-in column draws** where energy, transmission and capacity are each held or zero by design: every ERCOT hub, zone and node (capacity zero: no capacity market). It does not draw for CAISO and SPP (transmission not held), nor for the other grids.
  - Datacenter at HB_HUBAVG: 34.30 + 7.83 = 42.13.
  - Flexible compute at HB_HUBAVG: 32.25 + 0 = 32.25.
- **`docs/reviews/siting-gaps.md` is started**: one row a cell the warehouse cannot fill, by grid, with the source that would fill it (transmission for six grids, ERCOT's summer 2026 peaks, the node's wires utility, other grids' peak rules).
- **Keys**:
  - `allgrids|tx|<row>|<profile key>`, `allgrids|tx|<row>|firm|<profile key>`, `allgrids|tx|<row>|curtailing|<profile key>`;
  - `allgrids|allin|<row>|<profile key>`.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view).
2. "ERCOT HB_HUBAVG (hub)": the Transmission column reads 7.83, then "firm 7.83" and "off 0.00". Hover 7.83: the four intervals of 2025 (all "on" for a datacenter), the rate of 2025, and the charge being paid the year after.
3. The All-in column (scroll the table right): 42.13. Hover it: energy 34.30, transmission 7.83, capacity 0.00.
4. Choose Flexible compute: transmission 0.00 (off in all four intervals), all-in 32.25.
5. "CAISO TH_SP15_GEN-APND (hub)": transmission "not held"; hover it for the tariffs that would fill it.
6. Screenshots: `docs/brand/review-705/` (one build holds sessions 703 to 705).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session703` to `700` | 0 | 32 tests OK, 1 skip |
| built and checked on 705's branch, which holds this session (`docs/brand/review-705/`, `SESSION_705_REPORT.md`) | 0 | check-values 7,502 of 7,502 on every `/cost-of-power` address; the existing tab 0 differences |

## The landing

Landed with sessions 700 to 705 in one push at 10:09 UTC (`b25a5c66`); the gate, the snapshots (0 differences) and the deletion of the merged branches are in `SESSION_705_REPORT.md`, "The landing".

## Decisions made without you

1. **The rate is "Your load"'s**: the newest approved rate, matrix A. The 2026 rate is filed, not approved, so it is not used.
2. **The draw cancels**, so the load factor moves the charge only through the hours run. A load that runs fewer hours pays more per MWh for the same peak demand (the electrolyzer's firm figure is 14.23).
3. **A node is charged as its hub's hours** (HB_HUBAVG), as its energy is: the node table is daily.
4. **CAISO and SPP have no all-in figure**: their transmission is not held, even though their capacity is zero by design.

## For Samuel's ruling

- `texas_transmission_matrix` is internal in coverage, yet "Your load" shows its rate (the matrix row) and this tab uses it the same way. If the rate should be held, both views change together.

## Files

- Changed: `site/lib/siting.ts` (`newestRate`, `cpCharge`, `hourOf` as `model.ts`, `peakHours`, `ruleWeight`, `allInCell`, `NO_CAPACITY_MARKET`), `site/lib/sitingdata.ts` (the rate), `site/app/cost-of-power/AllGridsView.tsx` (`TxTd`, `AllInTd`; "An electrolyzer"), `site/scripts/siting-files.mjs`.
- New: `docs/reviews/siting-gaps.md`, `tests/test_session703.py`, this report.
