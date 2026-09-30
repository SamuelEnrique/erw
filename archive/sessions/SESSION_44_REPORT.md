# Session 44 report: gate check, then problem sets v0

Energy Research Warehouse (ERW), session 44, run 2026-09-30 from 20:01 to about 20:32 UTC. **Wall time about 31 minutes.**

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC.

- **No data pull, no Supabase table.** No force push.
- **Nothing to merge:** the daily job had not landed on origin at 20:28 UTC.

## Part 0: the gate

**Daily-prices run 12** (workflow_dispatch, commit 9fb7d93) was **still running** at 20:01 UTC:

- "Merge tests" passed (18:53:53).
- "Pull, validate, rebuild coverage" had been in progress since 18:53:58, about 67 minutes. It was still in progress at 20:28 UTC.

**Routing:** as Part 0 directs for a running job, this report says so, and the session did Part B. `SESSION_42_PROMPT.md` stays at the root.

**What run 12 was doing.** At about 20:10 UTC its Supabase loader was running `VACUUM (FULL, ANALYZE) public.entities` (seen in `pg_stat_activity`), and new rows reached Supabase soon after. A full vacuum takes an exclusive lock on each table while it rewrites it. That explains the statement timeouts builds met this evening, and after earlier loads. For about ten minutes this session, every read of a table being vacuumed timed out, even with retries.

## Part B: problem sets v0

**Where they are.** Three sets at `/learn/problems/<slug>`, an index at `/learn/problems`, all listed on the Learn menu. The code is `site/lib/problems.ts`.

**How each question works:**

- the question, and the tables a student would use, linked to `/data#<table>`;
- the answer, computed on the server from those tables at build, never typed. A test checks that no answer holds a number literal;
- a worked solution in the actual numbers, and one sentence on why it matters;
- a "Show answer" toggle, a plain `<details>`, so a teacher can assign the page;
- a note for teachers per set: time, prerequisites, pages.

**The questions follow the data.** Sets A and B use "the latest complete day or month held" wording, so their numbers move as the data updates.

**The answers as computed on 2026-09-30 (local build after the daily load, and live).** Every number is a checked value on the page.

### A. Know your grid: ERCOT and CAISO

| # | Question | Answer | Source tables |
|---|---|---|---|
| 1 | Highest hour of demand on the latest UTC day both report in full, and the ratio | 2026-09-29: ERCOT 80,913 MW, CAISO 32,988 MW; **2.45 times** | `eia930_all_demand` |
| 2 | Share of that day's net generation from natural gas | **ERCOT 42.64%, CAISO 27.98%** | `eia930_all_generation` |
| 3 | Battery discharge on the latest day both are held, and the ratio | 2026-09-28: ERCOT 25,252 MWh, CAISO 31,968.67 MWh; CAISO's **1.27 times** ERCOT's | `storage_daily_cycle` |
| 4 | Carbon intensity of generation, and the difference | 2026-09-27: ERCOT 365.59, CAISO 136.92 kg CO2/MWh; **228.67** higher | `carbon_intensity_daily` |
| 5 | ERCOT's battery discharge as a share of its demand that Central-time day | **1.55%** | `storage_daily_cycle`, `eia930_all_demand` |

(The first build, before the daily load reached `storage_daily_cycle`, read Q3 on 2026-09-27 at 0.99 times and Q5 at 1.58%. The answers moved with the data, as intended.)

### B. Prices and your bill

| # | Question | Answer | Source tables |
|---|---|---|---|
| 1 | ERCOT's latest complete month: load-weighted, simple, shape premium | 2026-08: 36.70 and 35.45 USD/MWh; premium **1.24** | `cost_of_power_monthly` |
| 2 | Largest and smallest shape premium in the latest month all six hubs hold | 2026-09 (partial): **MISO 10.77**, **CAISO 0.33** USD/MWh | `cost_of_power_monthly` |
| 3 | Wholesale energy on the default PG&E bill, and its share | **$23.24 of $262.33, 8.86%** | `cost_of_power_monthly`; `site/data/bill_rules.json` |
| 4 | The same on the default Oncor bill | **$22.02 of $95.27, 23.11%** | the same |
| 5 | ERCOT's cheapest and dearest hour in the latest profile month, and the spread | 2026-09: 09:00 at 22.49, 20:00 at 76.03 USD/MWh; **spread 53.54** | `cost_of_power_hourly_profile` |

### C. When the grid broke

| # | Question | Answer | Source table |
|---|---|---|---|
| 1 | Uri: the storm window's highest 15-minute price against the baseline days' highest | 9,051.55 (2021-02-17) against 1,691.63 (2020-02-10): **5.35 times** | `event_window_daily` |
| 2 | CAISO 2020: the day furthest above baseline, and the gap to 2020-08-14 | 2020-08-18, 23.50%; **12.75 percentage points** above 2020-08-14 (10.74%) | `event_window_daily` |
| 3 | Elliott: PJM's highest hour and its day's peak against baseline | 2022-12-23: **135,328 MW, 41.76%** above | `event_window_daily` |
| 4 | ERCOT 2023: the day of the highest price and of the highest demand | price 2023-09-06, 5,075.46 USD/MWh; demand 2023-08-10, 85,432 MW: **different days** | `event_window_daily` |
| 5 | Uri's highest price against the 2023 heat's | **1.78 times** | `event_window_daily` |

## Verify and ship

**check-values covers every computed answer:**

- rows by their series keys (with the event where there is one);
- daily peaks and sums by `series_max` and `series_sum`;
- bills by the `bill|...` keys of session 43;
- ratios, differences and percentages by a new `calc|<op>|<A>|<B>` key, whose operands (check keys with `~` for `|`) check-values recomputes on its own.

The problem pages hold 19 keys not already checked elsewhere. Its query helper now retries a statement timeout twice, as the site's reader does.

| Check | Result |
|---|---|
| check-routes | covers the index and the three sets |
| `tests/` | 83 OK, including `tests/test_session44.py`: three sets of five, every question with its parts, no number literal in any answer |
| Local, after the daily load and a clean fetch cache | routes 55 of 55, values 1,669 of 1,669 |
| Live | routes 55 of 55, values **1,667 of 1,669** |

**The two live failures** are on `/mix` (`eia930_generation_latest`, US48 and ERCO net generation for 2026-09-28). Run 12 was still loading Supabase when the deploy built, so the page read the table mid-load. The same totals now differ in Supabase (1,499,199 against 2,753,639 MWh for US48). The page catches up at its hourly revalidation. No page of this session failed.

**A note on local builds.** Next.js keeps a fetch cache in `.next/cache` across builds, so a local build after a data load can show values from before it. Clearing `.next/cache/fetch-cache` fixed the local check.

## Decisions made without a human

1. **Days are the latest complete UTC day** where both grids report 24 hours (A1, A2). Batteries use each table's own local day. A5 sums ERCOT's demand over the Central-time day.
2. **CAISO's battery figure** is CAISO's own data (`caiso:ISO`); ERCOT's is EIA-930's, as `/storage` shows them.
3. **B2 ranks the latest month all six hubs hold,** which is partial, and says so.
4. **The `calc` check key** and the retry in check-values' query helper.

## Open questions

1. **The daily loader's VACUUM FULL** locks tables for minutes while the site and checks read them. Run a plain VACUUM (ANALYZE) daily, and FULL only by hand?
2. **Run 12's gate step** had run over 90 minutes by 20:28 UTC. The next session should read its outcome before rerunning Session 42.
3. **More sets:** storage economics (round trip and the price spread), emissions by hour, the severance calculator?
