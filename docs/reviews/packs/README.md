# The review packs: read them in this order

Session 269, 14 October 2026. One pack a tool, for Samuel's technical review, written by sessions 263 to 267 and landed on `main` the same day (batches A and B: `f49246af`, `92024431`). Each replaces the tool's how-it-works note and has the same nine parts: what it is for; the model step by step, each step naming its function and file; every assumption with its default, source and the 12 October ruling; at least ten cross-checks; the edge cases tested on 14 October; what the model cannot see, ranked; the ten hardest questions; what the Stata run must reproduce; the questions only Samuel can answer. `tests/test_session262.py` holds that form.

Every page is in review: open `https://erw-flame.vercel.app/internal/open` first.

| Order | Pack | Page | The screenshot to open beside it | Questions for Samuel |
|---|---|---|---|---|
| 1 | [What a battery earns](battery.md) (session 263) | `https://erw-flame.vercel.app/cost-of-power/battery` | [`docs/brand/review-final-2/cost-of-power-battery_1280.png`](../../brand/review-final-2/cost-of-power-battery_1280.png) | 12 |
| 2 | [What a datacenter pays](datacenter.md) (sessions 265 and 265b) | `https://erw-flame.vercel.app/cost-of-power` | [`docs/brand/review-final-2/cost-of-power_1280.png`](../../brand/review-final-2/cost-of-power_1280.png) | 8 |
| 3 | [What a generator earns](generator.md) (session 264) | `https://erw-flame.vercel.app/cost-of-power/seller` | [`docs/brand/review-final-2/cost-of-power-seller_1280.png`](../../brand/review-final-2/cost-of-power-seller_1280.png) | 9 |
| 4 | [The Grid tool](grid.md) (session 266) | `https://erw-flame.vercel.app/grid?grid=ercot&view=network&shape=gravity` | [`docs/brand/review-266/gravity_1280.png`](../../brand/review-266/gravity_1280.png) (the gravity view); the Now view: [`docs/brand/review-final-2/grid_1280.png`](../../brand/review-final-2/grid_1280.png) | 6 |
| 5 | [Research](research.md) (session 267) | `https://erw-flame.vercel.app/research` | [`docs/brand/review-final-2/research_1280.png`](../../brand/review-final-2/research_1280.png) | 6 |

- **Questions awaiting Samuel: 41** (12, 8, 9, 6 and 6), each numbered in its pack's part 9 with its options. Some repeat across packs (Berkeley Lab's terms in the battery's and the generator's; who runs Stata in every pack): answer once, in the first pack that asks.
- **Every page at 1280 and 390 px:** `docs/brand/review-final-2/` (session 270), with a table of what differs from the battery page.
- **No Stata run has been made.** Stata is not on the code machine. Each pack's Python mirror was run on 14 October and equals the page value by value (part 8 of each pack gives the values the do-file must display).

## Every Stata command, in one block

From the repository's root (or from the folder a page's source line links, which holds the same files):

```stata
* 1. What a battery earns: the default case, ERCOT, 4 hours, perfect foresight, 100 MW (pack part 8)
cd "<repository>/site/public/battery"
do erw_2026_battery_replication.do

* 2. What a datacenter pays: the default load (pack part 8)
cd "<repository>/site/public/datacenter"
do erw_2026_datacenter_replication.do

* 3. What a generator earns: ERCOT solar at the hub, the page's defaults (pack part 8)
cd "<repository>/site/public/seller"
do erw_2026_generator_replication.do

* 4. The Grid tool: the network's figures for the hour shown (pack part 8; the CSV is written from the page's own
*    reads by site/scripts/write-grid-replication.mjs, so write it just before when comparing with the live page)
cd "<repository>/site/public/grid"
do erw_2026_grid_replication.do

* 5. Research: the six findings whose do-files were fixed by session 267 (pack part 8)
cd "<repository>/site/public/findings"
do batteries_lunch_grids.do
do batteries_curtailment.do
do impact_study.do
do gas_sets_price.do
do peak_hour_moved.do
do queue_divorce.do
```

The same without Stata, one line a tool, each run in its own folder (each prints what its do-file displays; a finding's mirror is the `.py` beside its `.do`):

```
cd site/public/battery    && python erw_2026_battery_replication.py
cd site/public/datacenter && python erw_2026_datacenter_replication.py
cd site/public/seller     && python erw_2026_generator_replication.py erw_2026_generator_hourly.csv
cd site/public/grid       && python erw_2026_grid_replication.py erw_2026_grid_replication.csv
```
