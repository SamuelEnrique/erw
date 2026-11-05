# Session 426 report: the datacenter cost tool's cross-check table

21 October 2026, about 13:40 to 13:50 UTC, unattended, on portable-laptop (code role), in the worktree `C:\Users\samen\Documents\erw-426` on `wip/426-dc-cost-checks` (from `origin/wip/461-combined` at `2289156d`). The chain `queue/done/021-day-21-october-code.md` (written for samueloldlaptop, run here by the owner's instruction to run what the queue prints), session 426. Model spend USD 0; no warehouse data written; no page changed, so no build. No web request: 0 of the session's 10.

## Read these first

- **The table is the last section of `docs/methods/datacenter_cost.md`, "Cross-checks of the tool's defaults (session 426)"**: eight rows, the four Texas utilities' transmission rows of "Delivery and transmission charges, Texas" at the page's defaults (ERCOT, a flat 100 MW), each with its key (`dcd|100|<utility>:transmission`), against the factor its tariff prints (gap 0.00 each) and against the Commission's 2025 ERCOT postage stamp rate, USD 68.547301 per kW a year, 7.83 per MWh for a flat load (Oncor +0.75, CenterPoint -0.91, AEP Texas +0.33, Texas-New Mexico Power -0.77).
- **The eight rows session 381's pack named are not repeated**: they are in `docs/methods/datacenter_pays_algorithm.md#cross-checks` (EIA's retail prices, three ICE indexes, and session 462's cost of capital and years against the ATB and Lazard); the new section refers to them.
- **No request was made.** Every published figure of the table is one the page's own file holds with its document, address, page and sentence (`site/data/datacenter/texas_delivery.json`, built 19 October 2026). Power per GPU and the overhead ratio are not compared: the repository names their sources but holds no address or page, and guessing an address would have spent requests on pages not known to exist.

## What to review

- `docs/methods/datacenter_cost.md`, its last section (`https://github.com/SamuelEnrique/erw/blob/wip/426-dc-cost-checks/docs/methods/datacenter_cost.md`).
- `tests/test_session426.py`.

## Checks

Every gate redirected into `runs/chain_021/s426/` in the worktree (git ignores `runs/`), never piped.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 426"` | 0 | passed; the machine was already on duty from the main checkout, so this worktree could not mark it again (said by the precheck) |
| The page's figures, recomputed by `lib/datacenter/delivery.ts` (`runs/chain_021/s426/dcd.mjs`) | 0 | `dcd|100|oncor:transmission` 8.58, `centerpoint_energy_houston_electric` 6.92, `aep_texas` 8.16, `texas_new_mexico_power` 7.06 |
| `tests.test_session426` | 0 | 9 tests OK: the note before the section unchanged against `origin/wip/461-combined`; no dash; eight rows of six cells, each key the row's utility; each figure the tariff's factor converted; each published figure, page and address the file's; each gap recomputed |
| `tests.test_session426` against the note with a dash and a wrong gap planted | 1 | 2 failures, as it should (the note restored after) |
| The tests that read the note: 138, 140, 149, 154, 163, 194, 195, 370, 426, 462 | 0 | 240 tests OK, 16 skipped |
| Build, check-values, check-methods on a site | none | no page changed; the keys the table names are already named in `datacenter_pays_algorithm.md` (line 226), which is what `check-methods.mjs` reads |

## Decisions made without you

1. **The table compares the delivery rows, not the market price**: the market price's published comparisons (EIA, ICE) are already the algorithm note's; the delivery table's are the figures the pack's part 4 listed and no note's table held.
2. **No web request.** The tariffs and the Commission's matrix are in the repository with their pages and sentences; reading them again would have cost requests and added nothing. NVIDIA's datasheet and the Uptime Institute's survey are named without an address, and the session would not guess one.
3. **kVA read as kW** for CenterPoint and Texas-New Mexico Power, as the page does (a power factor of 1); the table says so.
4. **The Commission's 2025 rate is the comparison**, not 2026's (filed, not approved: session 354).
5. **The key cells escape their pipes** (`dcd\|100\|...`), as `caiso_curtailment_intervals.md` and `grid_network.md` do in their tables, so the table renders in six columns.
6. **The reasons say only what the records support** (the pack's part 4: a factor recovers the Commission's rate and the utility's own costs over its own customers' peaks); no cause of a single utility's gap is claimed.

## For Samuel's ruling

- Whether a later session reads NVIDIA's DGX H100 datasheet and the Uptime Institute's Global Data Center Survey 2024 (their addresses first, robots and terms read) to add the two rows for the page's stated defaults.
- Whether the delivery table's distribution and other riders need a published comparison (none is held; a utility's rate case would be the source).

## To finish

- Land `wip/426-dc-cost-checks` with chain 021's other branches (a method note and a test; no build needed): merge it onto the combined landing branch, run `tests.test_session426` there (its first test reads `origin/wip/461-combined` and skips when that branch is gone after the landing), and the methods page `/data/methods/datacenter_cost` in the landing's snapshot.

## Files

- `docs/methods/datacenter_cost.md` (one section appended; nothing before it changed).
- `tests/test_session426.py` (new).
- This report.
- Not in git: `runs/chain_021/s426/` (the precheck, `dcd.mjs` and its output, `rows.out`, the test outputs).
