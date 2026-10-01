# Session 57 report: Severance v1, the Texas refund finder and a Louisiana pilot

Energy Research Warehouse (ERW), session 57, run 2026-10-01 from 20:51 to about 22:35 UTC. **Wall time about 1 hour 44 minutes.**

**API spend: USD 0.00, confirmed.**
- No model call.
- **Texas:** read only from the RRC dump already on disk (session 49's, downloaded 2026-10-01); no new download.
- **Louisiana:** web pages read for the terms and the access route, then stopped. No production data was pulled (Part B).
- **Internal data stayed internal:** nothing of it went to git, the public database, public Redivis or any committed JSON. No force push.

| Part | Done |
|---|---|
| A1: the statewide lease-month table | yes: `rrc_lease_production_statewide`, internal |
| A2: the refund finder | yes: `warehouse/derived/severance_screen.py`, three rules |
| A3: summaries | yes: by rule, county, operator (top 50), largest leases |
| A4: `/severance/finder` | yes, internal (404 without the token) |
| B: the Louisiana pilot | **not done**: the terms were read; the production data sits behind a CAPTCHA (below) |
| C: verify and ship | yes, Texas only: hand checks, tests, deploy, live 404 |

## Part A: Texas statewide

### What was read

- **The dump:** `warehouse/raw/rrc_pdq/20261001T041028Z/PDQ_DSV.zip`; production months 1993-01 to 2026-07, extracts of 18-SEP-26.
- **The table:** OG_COUNTY_LEASE_CYCLE, **76,981,666 lines** streamed once in 370 s. Never the whole file in memory.
- **What was kept:**
  - the latest **48** production months, 2022-08 to 2026-07: **10,839,881 lines**, in one gzip per county (**243 county files**) beside the dump;
  - 24 months for the table, and 24 more so the two-year inactive test can see the two years before a resumption.
- **Other tables used:**
  - OG_WELL_COMPLETION: wells listed per lease, and those with no shut-in date;
  - OG_SUMMARY_ONSHORE_LEASE: the RRC's first month for each lease;
  - GP_DISTRICT and GP_DATE_RANGE.

### 1. The statewide table: `rrc_lease_production_statewide` (internal)

- **Size:** **5,443,427 lease-county-months** of **233,118 leases** in **243 counties**, 2024-08 to 2026-07. 48 MB.
- **Layout:** one row per lease, county and month, partitioned by county under `warehouse/output/rrc_lease_production_statewide/`, with an `_index.csv`. Columns:
  - county, district, lease;
  - operator, field;
  - oil, casinghead gas, gas and condensate volumes;
  - whether a report was filed;
  - wells listed, and wells not shut in.
- **Shape: wide, not the series shape.** In the series shape it would be several GB. The provenance is in each partition's header (source, dump path, SHA-256, extract dates, license).
- **Built by:** `warehouse/connectors/rrc_statewide.py`, split once, then built one county at a time.

### 2. The refund finder: `warehouse/derived/severance_screen.py` (internal outputs)

**Scope:**
- **241,462 leases** were tested month by month from 2024-08 to 2026-07, on the three rules the data can test. Each rule and its citation come from `site/data/severance_rules.json` (version 2026-09-30.2).
- 1,674 leases reported in more than one county were tested once, on their sum.

**Money:**
- **Base tax:** 4.6 percent of value for oil and condensate, 7.5 percent for gas, against the tax with the credit or exemption.
- **Prices:** the warehouse's monthly means of EIA daily spot prices, labeled on every flag. WTI Cushing for oil and condensate; Henry Hub for gas, applied per Mcf as if one Mcf held one MMBtu.

**Outputs:**
- `severance_screen_flags.csv.gz`: one row per lease and rule, with:
  - the months;
  - the test met;
  - base tax, tax with the rule, and the potential saving;
  - the price notes;
  - what the flag cannot see.
- `severance_screen_summary.json`.

### 3. Results: candidates and potential savings, 2024-08 to 2026-07

| Rule | Leases flagged | Lease-months | Tax at the base rate, those months | **Potential saving** |
|---|---|---|---|---|
| Low-producing gas well credit | 76,075 (73,854 with a saving) | 1,376,120 | USD 277,993,017 | **USD 236,985,471** |
| Two-year inactive wells | 3,478 (1,007 with a saving) | 21,267 | USD 18,846,703 | **USD 1,139,843** |
| Low-producing oil lease credit | 45,905 | 818,502 | USD 1,290,529,955 | **USD 0** |
| **All** | **122,630 leases** (125,458 flags; 74,861 with a saving) | 2,215,889 | USD 1,587,369,675 | **USD 238,125,315** |

**Why each total is what it is:**
- **Oil saves nothing,** although 45,905 leases meet the volume test (under 15 bbl per well per day). Every certified oil price in the rules file for this window (2025-01 to 2026-07) is over $30, so the credit is zero. The file holds no certified price for 2024-08 to 2024-12, so no credit there either.
- **Gas:** every certified gas price held (2025-01 onward) gives a 100 percent credit. The 2024 months get none, for the same reason as oil.
- **Two-year inactive wells:**
  - **1,104 "seen" leases:** their production before the gap is in the 48 months. The saving is estimated on at most their average producing month before the gap: USD 1,139,843.
  - **2,374 "older" leases:** the gap runs back past 2022-08 and the RRC's first month for the lease is older. They are flagged with no saving estimated.

**By county, the top 10** (potential saving): Panola USD 16.7 million (3,860 leases), Webb 14.9 (4,709), Freestone 12.6 (2,649), Wise 10.8 (3,113), Zapata 8.8 (2,413), Dimmit 8.0 (2,163), Crockett 7.9 (5,763), Denton 7.1 (1,678), Tarrant 7.0 (1,802), Hemphill 6.5 (1,687). These are the gas basins: East Texas, the Barnett, and the Eagle Ford gas window.

**By operator, the top 10** (leases flagged, potential saving):

| Operator | Leases | Saving |
|---|---|---|
| Hilcorp Energy Company | 6,610 | USD 25.7 million |
| Diversified Production LLC | 3,200 | USD 13.9 million |
| BKV Barnett, LLC | 2,552 | USD 12.3 million |
| Burk Royalty Co., Ltd. | 2,966 | USD 9.1 million |
| UPP Operating, LLC | 5,817 | USD 8.8 million |
| Merit Energy Company | 1,585 | USD 6.7 million |
| Javelin Energy Partners Mgmt LLC | 1,490 | USD 6.2 million |
| Eagleridge Operating, LLC | 1,638 | USD 5.3 million |
| BKV North Texas, LLC | 1,058 | USD 5.2 million |
| Scout Energy Management LLC | 3,023 | USD 5.0 million |

**The largest single leases** (counts and totals only):
- The top ten run from USD 152,409 down to USD 30,048.
- Five are low-producing gas wells, three are two-year inactive leases, and two meet both.
- The median gas well's potential saving over the 24 months is USD 2,020.

### What each flag can and cannot see

| Flag | The test the data meets | What it cannot see |
|---|---|---|
| Low-producing oil lease | the lease's oil under 15 bbl per well per day over the months of the 90 days ending with the month; the wells listed and not shut in at the extract (at least one) | certification (Form AP-216); the water test (no water volumes in the dump); which wells produced each month; credits already claimed |
| Low-producing gas well | a gas well (an RRC gas lease is one well) at 90 Mcf a day or less over the three months before, when it produced in each of them, else the month itself | certification (Form AP-217); flared gas; high-cost gas already reported; credits already claimed |
| Two-year inactive well | a lease producing after 24 months or more without production, having produced before; never a new lease | the Commission's designation; which well resumed (a lease-level proxy: a resumed lease may resume from a well that was never inactive, and a producing lease can hide an inactive well); the application dates of Sec. 202.056; exemptions already claimed |

Every flag says "may qualify", never "qualifies". The page and the CSV state that none of it is tax advice.

### 4. `/severance/finder` (internal)

**What the page shows:**
- statewide totals;
- the rules, each with its source and code section;
- counties ranked (the top 25, then every county);
- the top 50 operators;
- the 50 largest leases, each opening in the lease tool;
- a form to open any lease by county and id;
- a method box;
- the flags as a CSV (`/severance/finder/download`).

**How it is served:**
- Both answer 404 without the internal token and are noindex.
- They read the finder's outputs from the warehouse's output directory, the way session 49's real-lease page reads its table. On Vercel those files are absent and no token is set, so the pages are 404 there.

**The lease drill-down:** `/severance/lease/real` gains a statewide branch that opens a lease from its county partition.
- The county is looked up in the partition index, never taken as a path.
- A lease reported in several counties shows the share in the county opened.
- A lease of several wells is marked as read as one well.

**Locally** (production build, the local token):
- the page renders in 0.18 s;
- the CSV is 115 MB;
- no token, or a wrong token: 404;
- a top lease opens in the lease tool with its flags.

## Part B: the Louisiana pilot, not done

**The terms, read first** (Department of Energy and Natural Resources, which became the Department of Conservation and Energy, C&E, on 2025-10-01):
- **The SONRIS app** (https://sonlite.dnr.state.la.us/ords/r/sonris_pub/sonris_public/home, where sonris.com redirects) states: "It is intended for general informational purposes only and should not be considered authoritative for navigational, engineering, other site-specific uses, or any other uses. The Louisiana Department of Conservation and Energy (DCE) does not warrant or guarantee its accuracy, nor does DCE assume any responsibility or liability for any reliance thereon."
- **The DENR archive's SONRIS guides page** says the same.
- **No page read grants reuse or redistribution.** So under the prompt's rule the license would be **internal**.

**The access:**
- The SONRIS Data Portal's production reports all redirect to a CAPTCHA page (`SONRIS_CAPTCHA_PKG.SHOW_CAPTCHA_apex`): "OGP Oil and Gas Production by Area", "OGP Production by LUW" and "Oil and Gas Detail Production by Month".
- A CAPTCHA is not something I solve or route around.
- The legacy "Oil and Gas Production Report" page (`/sundown/cart_prod/CART_CON_OGPDENTRY1`) answers without a CAPTCHA. But it takes one field, one operator and one month per request. Rebuilding a parish's 24 months from it would take thousands of requests, in effect working around the CAPTCHA that guards the same data in bulk. **I did not do it.**
- No bulk download or extract was found on the C&E or DENR sites.

**Result:**
- **Rows: 0** of the 300,000 ceiling. **No parish chosen,** since none could be pulled.
- **Not done:** the lease tool's "Load a real lease" gains no Louisiana parish.
- **The flags are ready:** the rules file and the lease tool already carry Louisiana's flags (stripper, incapable, inactive) for any Louisiana file a reader loads.

## Part C: verify and ship

**Hand checks against the lease tool** (`site/scripts/test-finder.mjs`, on real leases, prices from the same monthly means):
- **A Nueces County gas well,** flagged in all 24 months: the lease tool flags the same 24 months. Base tax USD 16,019.53 in both; potential saving USD 13,711.85 in both, to the cent. The saving covers the 19 months with a certified price (100 percent); the five 2024 months get none.
- **A Crane County one-well oil lease,** flagged in all 24 months: the same months, base tax USD 33,127.97 in both, saving USD 0 in both (no certified price under $30).

**Tests:**
- `tests/test_session57.py`, 7 tests, all passing:
  - the internal files are ignored, and no tracked file holds them;
  - the token gating of the page, the download and the drill-down;
  - the credit tiers are the rules file's bounds;
  - a gas well recomputed in Python from its county file and the Henry Hub means, independently of the finder;
  - the lease-tool agreement;
  - the inactive flags: never a new lease, savings no larger than the tax, none for "older" leases, and one "seen" lease's gap recomputed from its 48 months;
  - no em dashes.
- The lease tool's 93 checks pass, and so do sessions 40, 45 and 49's tests (32).
- **Lint and types:** clean on every changed file. The two errors eslint reports in `app/severance/Calculator.tsx` were there before this session.

**Local, production build:** check-routes 63 of 63; check-values 3,817 of 3,817.

**Live, after the deploy:**
- `/severance/finder` answers **404** with no token and with a wrong one;
- `/severance/finder/download` answers 404 with this session's own "Not found", which confirms the deploy;
- `/severance/lease/real` answers 404;
- check-routes 63 of 63; check-values 3,651 of 3,651.

## Decisions made without a human

1. **48 months read, 24 shown.** The two-year inactive test needs the two years before a resumption.
2. **A wide table, partitioned by county,** not the series shape. In the series shape it would be several GB. The partitions let a page open one lease quickly.
3. **The oil test divides by the wells listed and not shut in** (at least one). The prompt allowed estimating only what the data supports. The lease tool reads a real lease as one well, so the two can differ on multi-well leases; the drill-down says so.
4. **Two corrections to the inactive test,** after the first run flagged 7,647 leases and USD 3.25 billion:
   - new Permian leases file zero reports before their first well produces, and were read as "inactive";
   - and their whole new production was counted as exempt.

   Now a lease must have produced before the gap, and new leases (by the RRC's first month) are excluded. The saving is capped at the lease's average producing month before the gap, because only the designated well is exempt, not new wells. Older leases are flagged without a saving.
5. **Two corrections to the low-producing gas test, in both the finder and the public lease tool** (`lib/lease.ts`, `txGasAverage`):
   - New Haynesville wells were flagged because their filed zeros before first production averaged under 90 Mcf a day (the top lease showed USD 395,758).
   - Then new Eagle Ford and Delaware wells were flagged on a short first month.

   Now the three months before count only when the well produced in each of them, otherwise the month itself. Gas went from 77,256 wells and USD 263.6 million to **76,075 and USD 237.0 million**. This changes the public lease tool's behavior for a reader's own file in the same way; its 93 checks still pass.
6. **No new prices.** Henry Hub and WTI monthly means stand in for the operators' prices, labeled on every flag.
7. **The statewide table stays out of the archive bucket, coverage and Redivis** for now. Session 49's Martin table went to the internal Redivis draft. This one is a working table for the finder; uploading it is a human's call.
8. **`.gitignore`** now covers the partitions, `warehouse/output/*.csv.gz` and the finder's summary. The partitions showed as untracked before the rule was added; nothing internal was committed.
9. **Louisiana stopped at the CAPTCHA,** as above.

## Questions only Samuel can answer from his Ryan work

1. **The certified price's month.** Does the low-producing credit's certified price apply by production month (as the ERW reads it) or by the report month the Comptroller lists?
2. **Credits already claimed.** In practice, how many low-producing gas wells already claim the credit? The USD 237 million is an upper bound on what has not been claimed. Which shows filings already made: the Comptroller's data or the operator's?
3. **"Per well" in the oil lease test.** Is it every well on the lease, the producing wells, or the wells on the latest test (W-10)?
4. **The lookback window.** Texas refunds reach back four years. Should the finder test 48 months instead of 24, now that it reads them?
5. **Two-year inactive wells.** Is a lease-level resumption a useful lead in your work, or mostly noise? Which RRC record shows a designation already granted?
6. **Market value.** How far do posted or contract prices usually sit from Henry Hub and WTI? Should the finder carry a haircut?
7. **The vendor file.** Which vendor and export format does the firm use today (lease or well level, columns)? The finder's CSV could match it.
8. **Louisiana.** Does Ryan, or C&E on request, have a bulk SONRIS extract by parish or LUW? Which parish matters most to the consultant?

## Commits

- `640e8a2`: Part A1 and `.gitignore`.
- `9f43695`: the finder, hand checks, tests and method.
- `748daee`: the page, the download, the drill-down, and the gas test corrected in both tools.
- This report, with the prompt moved to `archive/sessions/SESSION_57_PROMPT.md`.
