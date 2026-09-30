# Session 45 report: the loader vacuum, run 12, then severance v0.2 (the lease tool)

Energy Research Warehouse (ERW), session 45, run 2026-09-30 from 20:49 to about 21:40 UTC. **Wall time about 50 minutes.**

**API spend: USD 0.00, confirmed.** This session made no model call. It pulled no data, created no Supabase table, uploaded no user data and did not force push.

- **Deployed and checked live:** routes 56 of 56, values 1,669 of 1,669.
- **Nothing to merge:** origin/main had no new commits at either push. Run 12's daily commit (7ea47ab) was already in the tree at the start.

## Part 0

### 1. The loader's vacuum

- **Daily loads:** `warehouse/supabase/load.py` now ends each daily load with a plain `VACUUM (ANALYZE)` of the six shape tables.
  - A plain vacuum takes no exclusive lock. The space of the rows a load replaced is marked for reuse, but `pg_database_size` does not shrink.
  - From session 29 to session 44, the code ran `VACUUM (FULL, ANALYZE)`, although the runbook already said "plain". In run 12 that FULL vacuum held the tables for about ten minutes (session 44).
- **FULL only by hand:** `VACUUM (FULL, ANALYZE)` now runs only with `--vacuum-full`, a person's command. It is documented in `docs/runbook.md` ("Supabase: compacting the database"): when to run it, and that the site's reads wait or time out while it runs.
- **Unchanged:** the 350 MB warning (`warn_mb`) and the `max_mb` failure line.
- **Test:** `tests/test_session45.py` runs the vacuum against a stub connection.
  - The default path issues six `VACUUM (ANALYZE)` statements, and `full=True` issues six `VACUUM (FULL, ANALYZE)`.
  - Neither workflow passes `--vacuum-full`.
- **Commit:** 769f04d.

### 2. Run 12: failed. Routing: fix, dispatch once, then Part B

Daily-prices run 12 (workflow_dispatch, 9fb7d93) **completed with failure** at 20:44 UTC. Its log was read through the GitHub API with the repository's token from `.env` (no gh CLI on this machine).

- **The gate passed.** "Pull, validate, rebuild coverage" ran from 18:53:58 to 20:41:48, and the day's metadata was committed (7ea47ab).
- **The failing step was the last one:** "Package tests", with 11 failed, 285 passed and 3 skipped.
- **Cause:** the package tests required `coverage.csv` and `docs/coverage.md` to list exactly the tables in the machine's `warehouse/output`.
  - By design, `build_coverage.py` carries over tables the runner does not hold (its session 14 rule). Nine were missing on the runner:
    - the ERCOT history and the tables computed from it (`ercot_peak_premium_*`, `cost_of_power_*`, `event_window_daily`);
    - CARB and the NYISO queue, whose connectors failed that day.
  - Tests then fetched those absent tables: the price board, the session 8 entities, the NYISO queue and the tiers.
  - Separately, `api_cost_ledger` held 396 rows against coverage's 391. The model calls that follow the coverage step (the fun fact, the email) append to it.
- **Fix** (5c00e9d), in `package/tests/test_erw.py`:
  - **`CARRIED`:** tables in coverage but absent here. Coverage must still list them, and their contents are tested only where held (`_needs`).
  - **The ledger:** it may hold more rows than coverage counted, never fewer.
- **Pre-existing test bugs found on the way.** These failed only on a laptop, where the derived tables exist:
  - The filter test expected only `price_board_*` among the derived tables on a market. It now counts every derived table carrying the market (the peak premium, the cost of power, the event windows).
  - Its hub check compares only the source price tables.
  - Its balancing-authority (BA) check allows derived tables (`event_window_daily` names each BA).
- **Verified two ways:**
  - **Against a scratch copy holding only the runner's 73 tables and the runner's `coverage.csv`:** all 11 targeted tests pass or skip (25 passed, 2 skipped: CARB and the NYISO queue).
  - **Against the full local warehouse:** the edited tests pass, except rows for `api_cost_ledger`. This laptop's copy of the ledger (351 rows) is older than the committed coverage (391), a local staleness, not a code fault.
- **The 15-minute limit:** the fix took about 25 minutes, over the limit, mostly waiting on test runs; I did not stop it partway.
- **One workflow_dispatch was triggered, as approved:** run 13 (5c00e9d, 21:19 UTC).
  - It passed "Merge tests".
  - It was in "Pull, validate, rebuild coverage" at 21:32 UTC.
  - I did not wait for it.

`SESSION_42_PROMPT.md` stays at the root. Session 42 was not run, since run 12 did not pass.

## Part B: severance v0.2, the lease tool

**Where:** `/severance/lease`, linked from `/severance`. It uses the same rules file (version `2026-09-30.2`, unchanged) and the same calculator (`site/lib/severance.ts`).

### What it does

- **Input:** drop a CSV, choose one, or paste rows (comma- or tab-separated, quotes allowed).
  - **Required columns:** `state`, `well_id`, `month`. Volumes are `oil_bbl`, `gas_mcf` and `condensate_bbl`.
  - **Optional prices:** `oil_price`, `gas_price`, `condensate_price`.
  - **Optional well facts:** `completion_date`, `depth_ft`, `horizontal`, `days_produced`, `water_cut_pct`, `well_type`, `inactive_months`, `hcg_cost_ratio`, `nm_district`, `royalty_pct`, `trucking_per_unit`, `transport_per_bbl`.
  - **`exemptions`:** the rule ids a row claims.
  - A well fact given on one row of a well holds for its other rows. Bad rows are listed by line number.
- **The file never leaves the browser.** It is read with the File API (`File.text()`) and computed in the page (`site/lib/lease.ts`). The results download, the template and the sample are Blobs made in the page. The page says all of this at the top: "Your file stays on your computer."
- **Prices:** a blank price takes the month's mean of the warehouse's EIA daily spot prices (`eia_fuel_spot_prices`, January 2023 to September 2026 live).
  - WTI Cushing is used for oil and condensate, Henry Hub for gas (per MMBtu, applied per Mcf).
  - Each price is labeled with the days averaged, and the latest month as possibly partial.
  - A month the warehouse does not hold is not computed, and the row says so.
- **Per well, month and product:**
  - the base tax;
  - the tax with the rules ticked: one reduced rate per well and product, plus the Texas lease credit, as the calculator allows. Ticks come from the file's `exemptions`, from the per-well selects, or from "Tick the best flagged rule of each well";
  - the regulatory fees, shown apart;
  - the "may qualify" flags, each stating the well's numbers against the threshold and citing its rule.
  - Louisiana's oil rate follows the completion date: 6.5 percent from July 1, 2025, else 12.5 percent, and 12.5 percent when no date is given (labeled). New Mexico's ad valorem rate follows `nm_district`, given as a TRD suffix or a label.
- **The flags:**

| Flag | Test on the file's numbers |
|---|---|
| TX low-producing oil lease | The lease's oil wells average under 15 bbl per well per day over the months of the 90 days held, or under 5 percent oil per barrel of water. The credit comes from the certified price of the production month |
| TX low-producing gas | 90 Mcf a day or less over the three months before, as held (else the month itself). Not casinghead gas. The certified price of the month sets the credit |
| TX high-cost gas | A cost ratio is given, within 120 months of completion; the Sec. 201.057(c) rate |
| TX and LA two-year inactive | 24 months or more without production (`inactive_months`, or the file's zero months) |
| LA stripper | 10 bbl or less per producing day |
| LA incapable oil | 25 bbl or less per producing day and 50 percent water or more. Without a water cut the row says it is not assessed |
| LA incapable gas | Under 250 Mcf a day, not an oil well |
| LA deep | Over 15,000 ft, completed after July 31, 1994, within 24 months of completion |
| LA horizontal | Within 24 months of completion (18 for gas completed from July 1, 2025) |
| NM district | Information: the district's rate applied, or the range when none is given. No reduced NM rate is flagged (none is in the rules file) |

- **Summary:** four figures for the lease (base, with ticks, potential savings, fees), then the flagged rules with the largest potential savings first, the per-well totals and the full well, month and product table.
  - Potential savings take, per well, month and product, the one flagged rule that saves the most (reduced rates do not stack).
- **Download:** the results as CSV, one row per well, month and product. The file names the rules version and says it is not tax advice.
- **The method** (`docs/methods/severance.md`) has a new section, "The lease tool (session 45, v0.2)", with the tests on the numbers and what a file cannot show (payout, pressure, certification).

### The test leases, worked by hand

All match the tool to a hundredth of a cent (`site/scripts/test-lease.mjs`, run by `tests/test_session45.py`).

**Texas.** Three wells, July and August 2026; ticks: EOR for TX-A, low-producing gas for TX-B, high-cost gas for TX-C.

| Well | Month | Base | With ticks | Flag |
|---|---|---|---|---|
| TX-A oil, 600 bbl x $70 | 07 | $1,932.00 | $966.00 (EOR 2.3%) | none (19.35 bbl/well/day) |
| TX-A gas, 900 Mcf x $3 (casinghead) | 07 | $202.50 | $202.50 | none |
| TX-A oil, 580 x $65 | 08 | $1,734.20 | $867.10 | none |
| TX-A gas, 880 x $3 | 08 | $198.00 | $198.00 | none |
| TX-B gas, 2,500 x $3 (80.65 Mcf/day) | 07 | $562.50 | $0.00 (certified $1.31: 100%) | tx_lp_gas |
| TX-B gas, 2,400 x $2.80 | 08 | $504.00 | $0.00 (certified $1.36) | tx_lp_gas |
| TX-C gas, 40,000 x $3, ratio 0.5: 5.625% | 07 | $9,000.00 | $6,750.00 | tx_hcg |
| TX-C gas, 38,000 x $2.80 | 08 | $7,980.00 | $5,985.00 | tx_hcg |

- **Lease:** base $22,113.20; with ticks $14,968.60; potential savings $5,311.50.
- **Fees:** $63.85656 (oil $7.375, gas $56.48156).
- **Largest first:** TX-C high-cost gas, $4,245.00.

**Louisiana.** Ticks: stripper for LA-A, horizontal for LA-B.

| Well | Month | Base | With ticks | Flags |
|---|---|---|---|---|
| LA-A oil, 250 bbl in 28 days, $70 less $2 transport, 12.5% | 07 | $2,125.00 | $531.25 (stripper 3.125%) | la_stripper, la_incapable |
| LA-A oil, 270 bbl in 30 days, $65 less $2 | 08 | $2,126.25 | $531.5625 | la_stripper, la_incapable |
| LA-B gas, horizontal, completed 2025-10: 7,000 x $0.1514 | 07 | $1,059.80 | $0.00 | la_gas_horizontal, la_gas_incapable |
| LA-B gas, 6,500 x $0.1514 | 08 | $984.10 | $0.00 | la_gas_horizontal, la_gas_incapable |
| LA-C oil, completed 2025-08: 3,000 x $68 x 6.5% | 07 | $13,260.00 | $13,260.00 | none |
| LA-C oil, 2,900 x $63 x 6.5% | 08 | $11,875.50 | $11,875.50 | none |

- **Lease:** base $31,430.65; with ticks $26,198.3125; potential savings $5,232.3375.
- **Largest first:** LA-A stripper, $3,188.4375.

**New Mexico.** No reduced rate in the rules file, so the tax with ticks equals the base.

| Well | Month | Base |
|---|---|---|
| NM-A oil, LEA 2510 (8.7742%): $70,000 - $8,750 - $1,000 = $60,250 | 07 | $5,286.4555 |
| NM-A gas (9.5742%): $9,000 - $1,125 - $3,000 = $4,875 | 07 | $466.74225 |
| NM-A oil: $58,500 - $7,312.50 - $900 = $50,287.50 | 08 | $4,412.325825 |
| NM-A gas: $7,840 - $980 - $2,800 = $4,060 | 08 | $388.71252 |
| NM-B gas, SAN JUAN 4510 (9.3137%): $60,000 - $7,500 | 07 | $4,889.6925 |
| NM-B gas: $53,200 - $6,650 | 08 | $4,335.52735 |
| NM-C oil, no district (7.14%): $7,000 | 07 | $499.80 |
| NM-C oil: $6,500 | 08 | $464.10 |

- **Lease:** $20,743.355945.
- **District flags:** NM-A's names LEA 01/2510 at 1.6342%. NM-C's says the ad valorem tax is left out and gives the range, 0.7105% to 1.7249%.

**Other tests: 83 checks in all pass.**

- **Each threshold from both sides**, for example 14.97 against 15.00 bbl per well per day, 90.0 against 90.03 Mcf a day, 15,000 against 15,001 ft, and 23 against 24 inactive months.
- **The months before**, used when held.
- **An unpublished certified month:** flagged, with no credit.
- **Louisiana's rate** on either side of July 1, 2025.
- **The default price path** and a month with no price.
- **The parser's errors.**
- **No network:** fetch, XMLHttpRequest, WebSocket, EventSource and sendBeacon are trapped while the sample is parsed, analysed, re-ticked and written; zero calls. The page's sources name none of them, nor a form, a server action or a dynamic import.
- **In Chrome on the local build:** loading the sample and ticking made 14 requests, all GETs to fixed paths on the site itself:
  - Next.js link prefetches of `/`, `/events`, `/severance`, `/play/battery` and `/data/methods/severance`;
  - three JS chunks;
  - one `data:` URL.
  - There was no POST, and nothing carried the lease data.

**Other checks:**

- `tests/`: 89 tests; all pass after one fix to the new test file (below).
- `tsc` and eslint are clean.
- `npm run build` passes.
- check-routes: 56 of 56 locally and live. check-values live: 1,669 of 1,669.

### Which flags fire on the sample

The sample's 19 well-months in June to August 2026 are labeled "SAMPLE: FICTIONAL WELLS", with every well named FICTIONAL-.

| Well | Flags | Why |
|---|---|---|
| FICTIONAL-TX-1 | tx_lp_oil | 14 bbl/day, 96% water. Savings $0: the certified oil price for June to August 2026 is over $30 |
| FICTIONAL-TX-2 | tx_lp_gas | About 80 Mcf a day: a 100% credit |
| FICTIONAL-TX-3 | tx_hcg | Ratio 1.2: 3% |
| FICTIONAL-LA-1 | la_stripper, la_incapable | |
| FICTIONAL-LA-2 | la_gas_deep, la_cond_deep, la_gas_horizontal, la_gas_incapable | |
| FICTIONAL-LA-3 and the NM wells | none | LA-3 is a contrast; the NM wells get only the district information flag, and NM-3 has no district |

## Decisions made without a human

1. **Test layer only:** the package tests were fixed, not coverage. Coverage carrying over absent tables is the documented design, and the tests were what disagreed with it.
2. **The lease oil test counts oil wells:** Texas wells with oil that month, over the months of the 90 days that the file holds, measured in calendar days.
3. **Low-producing gas window:** when the file holds none of the three months before, the test uses the month itself, and the row says so.
4. **LA gas and TX high-cost gas** are flagged unless the well is marked an oil well. Without `well_type`, the flag says "for a gas well only".
5. **Commercial production is taken to begin at completion** for the Louisiana 24- and 18-month windows. Payout is never assessed, and every such flag says so.
6. **No New Mexico reduced-rate flag:** none is in the rules file. The district flag is information only, with $0 savings.
7. **The Write tool turned a backslash-u2014 escape in the new test into a literal em dash.** It is now `chr(0x2014)`, and no new file holds an em dash.
8. **Stopping the local server may also have stopped other node processes.** The first command used a broad `taskkill` of node.exe with a window-title filter. No node process remained afterwards.

## Questions for Samuel

1. **Run 13** (5c00e9d) was still running at 21:32 UTC. If it passes, Session 42 (interchange and the 3D network) can run next.
2. **The lease oil test:** should it use producing days instead of calendar days? The Comptroller's text says "per well per day" over a 90-day period.
3. **Next.js link prefetch:** the tool page prefetches its links as they appear (fixed GETs, no data). Should prefetch be turned off on this page, so the network panel shows nothing at all after a file is loaded?
4. **Compacting the database:** with the plain vacuum, the size no longer shrinks after each load. If the 350 MB warning appears and stays, run `python warehouse/supabase/load.py --vacuum-full` at a quiet hour, or trim a live window.
