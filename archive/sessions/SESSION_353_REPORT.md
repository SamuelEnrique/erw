# Session 353 report: the generator's tax credits, settlement point and PPA shape

20 October 2026, from about 13:40 UTC, unattended, on samueloldlaptop (the code machine), the third session of the chain of 20 October, night (`queue/done/010-night-20-october-code.md`). Branch `wip/353-seller` in the worktree `erw-296`, from session 352's branch (`wip/352-price-years`, which lands first: the generator's model carries both); lands on main as `task/353-seller`. Model spend USD 0; no warehouse data written; nothing pulled. Precheck exit 0.

## Read these first

On `/cost-of-power/seller`, under "Is it worth building?" and "Your plant". **Every default figure is what it was** (check-values 240 of 240 on the generator's pages; `check-seller-scenarios` all passed).

- **Two tax credits in Financing**, 0 by default: the investment tax credit (a percent of the capital cost, received in year 1) and the production tax credit (USD per MWh of the plant's energy, falling with the degradation, for ten years, the credit's term under sections 45 and 45Y). They reach NPV, IRR and the breakeven PPA price; they are **not counted in debt coverage**, and the coverage row says so when a scenario holds one. Offered for solar and wind (both), a battery (the investment credit), not a gas peaker; a credit not offered is held at 0. A credit's sensitivity row is drawn only when the scenario holds it. At the default ERCOT solar case, an ITC of 30 percent moves NPV from USD -76.66 million to about -39.83 million.
- **The settlement point.** The select is "Settlement point", its hubs and load zones grouped apart. For ERCOT at the hub average, "At a node" prices scenario A and B at the 10th percentile, the median or the 90th percentile of the class's nodes' day-ahead basis to the hub (solar, wind or gas), month by month, from the data machine's `node_basis_summary` (session 358), each month's basis shown with its key in a fold. Solar, 100 MW: USD -15.83 per kW a year at the 10th percentile, 0.17 at the median, 14.69 at the 90th (NPV -88.94, -76.53 and -65.27 million). **The basis is day-ahead on real-time prices**, said on the page: the table holds the real-time basis from September 2026 only. The figures above the scenarios stay at the hub. `node_basis_daily` itself is not read: its summary is the percentiles the prompt names.
- **The PPA's shape**, solar and wind: "As generated" (the default, every contract until now) or "A flat block, every hour", the same MWh a year settled against the hub's average price of every hour; the plant then sells all its energy in the market. The default solar case contracted whole at USD 58.36: NPV about zero as generated, USD -21.27 million as a block; the block's breakeven 68.45.
- `components/tool/ParamChoice.tsx` (new, shared): one address parameter as a select, its default in grey with the source, and a Reset; the node and the shape use it. "Show" keeps both.
- Method note: `generator_earns_algorithm.md`, a section "Session 353" before "Checks"; pack `generator.md` items 2, 3 and 5.

## What to review

In the internal view, after the landing:

1. https://erw-flame.vercel.app/cost-of-power/seller?nb=p10 (and `p50`, `p90`; `&asset=wind`).
2. https://erw-flame.vercel.app/cost-of-power/seller?ai=30&ax=25 (scenario A with both credits).
3. https://erw-flame.vercel.app/cost-of-power/seller?ps=block&an=100&ap=58.36 against `?an=100&ap=58.36`.
4. `docs/brand/review-353/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 353"` | 0 | |
| `tests.test_session353` and every test that reads a file this session changed (21 modules, 324 tests) | 1, then 0 | four pins of lines this session changed (186, 235, 264 twice): updated; then the docs' tests (10 modules, 141): the new method section had to sit before "Checks" (196, 253): moved |
| `scripts/test-seller-finance.mjs` | 1, then 0 | its example of a letter that is no parameter was `ax`, now the production credit's: `az` |
| `tsc --noEmit`; `eslint` on the generator's folder, `lib/seller` and `ParamChoice.tsx` | 0 | one warning, older (`tables.csv/route.ts`, an unused type) |
| `finish_build.sh 353` (`ce417c79`): build | 0 | no statement timeout |
| `check-values` on `/cost-of-power/seller` | 0 | 240 of 240 |
| `check-routes` | 0 | every page |
| `check-seller-scenarios` | 1, then 0 | its New England zone case counted 11 fields; solar now holds 13. Updated, rerun on the same build: all passed |
| `check-table-downloads` | 1 | asked of a page with no downloads line: a mistake of the call, not a result |
| Impeccable `detect --json` on the twelve files | 0 | no finding |
| The probe at 390, at the default and at a node | 0 | 390 within 390 |
| Shots, 1280 and 390 | 0 | `docs/brand/review-353/` |

## Landing

Below, once it is done: no landing from 14:00 to 16:15 UTC.

## Decisions made without you

- **Credits are not counted in coverage.** Lenders size debt on cash from the plant; a credit goes through taxes (or to a tax-equity partner). Count them by typing them into the revenue if you want the other reading.
- **The investment credit arrives in year 1, the production credit for ten years on the plant's energy.** No basis reduction, no normalization, no transferability discount, no bonus adders: the reader types the rate.
- **Which assets are offered which credit**: both for solar and wind, the investment credit for a battery, neither for a gas peaker.
- **The node uses the day-ahead basis** on the real-time prices, said on the page, because the real-time basis is held for two months only. It moves scenario A and B, not the headline, the capture rows or the months above.
- **Not at a battery**: a battery buys at its node too, so one basis on its sales would not describe it; What a battery earns has the node band in session 355.
- **The block settles at the hub's flat average of the same months** (the model's own `flat`), not at a 7x24 or a peak block: one shape, the plainest.

## For Samuel's ruling

- Nothing that changes a number at the default.
- Whether the node should apply to the headline as well (one number for "my plant at my node"), and whether the real-time basis should replace the day-ahead once the data machine holds twelve months of it.

## Files

- `site/lib/seller/finance.ts`; `site/app/cost-of-power/seller/model.ts`, `page.tsx`, `SellerScenarios.tsx`, `SellerForm.tsx`; `site/components/tool/ParamChoice.tsx` (new).
- `site/scripts/test-seller-finance.mjs`, `check-seller-scenarios.mjs` (pins).
- `docs/methods/generator_earns_algorithm.md`, `docs/reviews/packs/generator.md`.
- `tests/test_session353.py` (new); `tests/test_session186.py`, `196`, `235`, `264`, `298` (pins).
- `docs/brand/review-353/` (shots).
