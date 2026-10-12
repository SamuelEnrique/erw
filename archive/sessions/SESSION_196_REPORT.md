# Session 196 report: the three tools against the outside world

11 October 2026, 20:48 to about 21:40 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/196-cross-checks`, on top of session 195, pushed as `wip/196-cross-checks`. Model spend USD 0, no model call. Reads: 21 requests of the 25 allowed, each listed below. No data lock taken.

## Read these first

- **Not landed, for session 195's reason.** `main` still fails GitHub's check on five tests of sessions 153, 183 and 190 (the page files of this morning), so no code branch merges. This session is complete and checked locally, on `wip/196-cross-checks`. Production is untouched.
- **Lazard prints the equity half.** Its June 2025 report says "60% debt at an 8% interest rate and 40% equity at a 12% cost". By your ruling the hurdle rate default on the three pages is that weighted cost, **9.6 percent** (it was 8), cited.
- **The ATB holds no degradation rate.** Its battery does not fade: augmentation is paid inside a fixed O&M of 4 percent of capital cost a year. Lazard's storage cases give **2.6 percent a year**, with the costs the pages already use. That is now the battery's cited default (it was 0), on the battery page and for the generator page's battery. Yours to confirm (item 3 below).
- **No headline number moved.** NPV moved on the battery and generator pages, present value of the cost on the datacenter page, and one IRR. Every one is listed below.
- **Two findings from Lazard's own pages:** its storage cases carry 20 percent debt, not the 60 percent the battery page uses; and its method discounts equity's flows at the cost of equity, 12 percent, not at the weighted cost. Both are items for your ruling.
- Each of the three Method notes ends with a section "Cross-checks" (9, 10 and 6 rows), and each page's source line says "Checked against: ..." with a link to it.

## What to review

On production after the landing (internal view); until then `runs/session196/shots/`.

1. `https://erw-flame.vercel.app/cost-of-power/battery`, "Scenarios A and B":
   - Hurdle rate reads 9.6: "Default 9.6. Lazard, Levelized Cost of Energy+, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost". The default is that weighted cost, 0.6 x 8 + 0.4 x 12 = 9.6 percent."
   - Degradation reads 2.6: "Default 2.6. Lazard, Levelized Cost of Energy+, June 2025 (LCOS v10.0): battery degradation of 2.6 percent a year in its utility-scale cases of 2 and 4 hours. The model itself has no capacity fade: here the rate is a yearly cut to revenue."
   - NPV at the hurdle rate: USD -62.59 million, "USD -625.91 per kW at 9.6 percent". The headline above is as it was: 81.40, 475,477, 0.88.
   - At the foot of the page: "Checked against: 9 published figures (Lazard, the Annual Technology Baseline, CAISO's market monitor, ERCOT's awards, EIA). Each comparison, with its gap and the reason." Click the link.
2. `https://erw-flame.vercel.app/data/methods/battery_earns_algorithm#cross-checks`: a table of nine rows. Read the rows on CAISO's fleet (ours 92 against 53), on the debt share (60 against Lazard's 20 for storage) and on degradation.
3. `https://erw-flame.vercel.app/cost-of-power/seller`: Hurdle rate 9.6; Degradation 0, "No cited rate is held" (solar). NPV USD -78.43 million. Foot: "Checked against: 10 published figures (Lazard, the Annual Technology Baseline, EIA)."
4. `https://erw-flame.vercel.app/cost-of-power/seller?asset=battery`: Degradation 2.6 with Lazard's line. NPV USD -79.57 million.
5. `https://erw-flame.vercel.app/data/methods/generator_earns_algorithm#cross-checks`: ten rows. The solar contract price, USD 39.14, sits at the low end of Lazard's 38 to 78.
6. `https://erw-flame.vercel.app/cost-of-power`: Hurdle rate 9.6, with the sentence that it is a power plant builder's cost of capital. Present value of the cost: USD 258.57 million, "20 years at 9.6 percent". Foot: "Checked against: 6 published figures (EIA)."
7. `https://erw-flame.vercel.app/data/methods/datacenter_pays_algorithm#cross-checks`: six rows. Texas industry paid USD 70.70 per MWh in July 2026 against our USD 30.59 of wholesale energy.

## Numbers on the page, before and after

Read from the pages' own cells before and after the change (`runs/session196/text/ours_before.json`, `ours_after.json`). 100 MW, the defaults.

| Page and case | Number | Before (hurdle 8, degradation 0) | After (9.6; battery 2.6) | Why |
|---|---|---|---|---|
| Battery, ERCOT, 4-hour, perfect foresight | NPV | USD -52.68 million | USD -62.59 million | both defaults |
| Battery, ERCOT, 4-hour, day-ahead schedule | NPV | USD -60.93 million | USD -68.83 million | both |
| Battery, ERCOT, 2-hour | NPV; IRR | USD -14.43 million; -1.7 percent | USD -23.30 million; none | both; with degradation no rate sets NPV to zero |
| Battery, ERCOT, 8-hour | NPV | USD -156.66 million | USD -161.95 million | both |
| Battery, CAISO, 4-hour, perfect foresight | NPV | USD -54.99 million | USD -64.34 million | both |
| Battery, CAISO, 4-hour, day-ahead schedule | NPV | USD -68.82 million | USD -74.79 million | both |
| Generator, ERCOT solar | NPV | USD -82.31 million | USD -78.43 million | hurdle |
| Generator, ERCOT wind | NPV | USD -152.23 million | USD -143.09 million | hurdle |
| Generator, ERCOT battery | NPV | USD -75.13 million | USD -79.57 million | both |
| Generator, ERCOT gas peaker | NPV | USD -91.00 million | USD -85.78 million | hurdle |
| Generator, CAISO solar | NPV | USD -118.91 million | USD -109.81 million | hurdle |
| Datacenter, ERCOT `LZ_NORTH` | present value of the cost | USD 290.09 million | USD 258.57 million | hurdle |
| Datacenter, CAISO SP15 | present value of the cost | USD 245.13 million | USD 218.49 million | hurdle |

- The sentence under each table moves with its NPV or present value, and reads "at a hurdle rate of 9.6 percent".
- The chart's bars move with them (the hurdle rate's step is now 8.6 and 10.6; degradation's, 1.6 and 3.6).
- **Unchanged:** every headline number, every check key (3,289 of 3,289), coverage, the breakeven toll, the contract prices, the merchant tail (0), the fixed price and the all-in power per GPU-hour on the datacenter page (no upfront cost and no change of prices at the defaults).
- An address that already holds `ah`, `bh`, `ad` or `bd` keeps its values. An address that named none now opens the new defaults.

## The reads: 21 of 25

Every request, in order (`runs/session196/reads.csv`; the bodies are under `runs/session196/reads/`, outside git). Contact string: "ERW research project, github.com/SamuelEnrique/erw". No retry. No request to a paused publisher, to PJM or to MISO.

| # | UTC | Address | Status, bytes | What was taken |
|---|---|---|---|---|
| 1 | 20:49:36 | `https://www.lazard.com/robots.txt` | 200, 23 | "User-agent: * / Disallow:" (nothing disallowed) |
| 2 | 20:49:48 | `https://www.lazard.com/terms-of-use/` | 200, 65,682 | "Lazard authorizes you to view and access a single copy of the content ... for your own use"; no rule on automated reading |
| 3 | 20:49:59 | `https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf` | 200, 1,823,102 | the financing sentence; LCOE 38 to 78 (solar), 37 to 86 (wind), 149 to 251 (gas peaking); LCOS 115 to 254 (4-hour); storage's 20 percent debt; degradation 2.6 percent; 126,000 MWh a year |
| 4 | 20:51:14 | `https://atb.nrel.gov/robots.txt` | failed, 0 | the host no longer resolves (the laboratory was renamed) |
| 5 | 20:51:23 | `https://atb.nlr.gov/robots.txt` | 200, 24 | nothing disallowed |
| 6 | 20:51:32 | `https://www.nlr.gov/robots.txt` | 200, 24 | nothing disallowed |
| 7 | 20:51:39 | `https://www.nlr.gov/disclaimer` | 200, 30,098 | "The user is granted the right, without any fee or cost, to use or copy the Data", with credit |
| 8 | 20:51:48 | `https://atb.nlr.gov/electricity/` | 302, 414 | the current edition is 2025 |
| 9 | 20:51:57 | `https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage` | 200, 49,427 | no fade: augmentation inside fixed O&M of 4 percent of capital cost; 15-year life; 85 percent round trip |
| 10 | 20:52:46 | `https://atb.nlr.gov/electricity/2025/utility-scale_pv` | 200, 108,506 | USD 1.49 per W (AC) in 2024, 1.62 in 2023; fixed O&M 24.66; degradation 0.7 percent a year |
| 11 | 20:52:58 | `https://atb.nlr.gov/electricity/2025/land-based_wind` | 200, 83,584 | USD 1,968 per kW and USD 43 per kW a year, 2023 |
| 12 | 20:53:14 | `https://www.caiso.com/robots.txt` | 200, 47 | "Disallow: /resources/*"; `/documents/` allowed |
| 13 | 20:53:23 | `https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf` | 200, 680,268 | fleet net market revenue: USD 53 per kW-year in 2024, 78 in 2023, 103 in 2022; 82 percent energy |
| 14 | 20:54:05 | `https://www.eia.gov/robots.txt` | 200, 718 | "Allow: /"; archives disallowed |
| 15 | 20:54:14 | `https://www.eia.gov/electricity/wholesale/xls/ice_electric-2026.xlsx` | 200, 74,748 | ICE day-ahead peak prices, SP15, NP15, the New England hub, by delivery period |
| 16 | 20:54:26 | `https://www.eia.gov/about/copyrights_reuse.php` | 200, 52,528 | "U.S. government publications are in the public domain" |
| 17 | 20:56:23 | `https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a` | 200, 105,648 | industrial price, July 2026: Texas 7.07, California 25.11, New York 10.81 cents per kWh |
| 18 | 20:58:03 | `https://modoenergy.com/robots.txt` | 200, 444 | every agent allowed, Anthropic's by name |
| 19 | 20:58:11 | `https://modoenergy.com/research/sitemap.xml` | 200, 1,272,816 | the addresses of its posts; nothing else |
| 20 | 20:58:27 | `https://modoenergy.com/terms` | 307 to `/404`, 259,116 | no terms there |
| 21 | 20:58:46 | `https://modoenergy.com/terms-and-conditions` | 307 to `/404`, 259,146 | no terms there |

- **Two errors of order, mine:** EIA's price file (15) was read before EIA's reuse page (16). Modo's sitemap (19) was read before its terms were looked for.
- **CAISO's terms were not read again:** the source registry quotes them as read on 6 October 2026 ("may be used by you provided that you ... credit the California ISO").
- **Modo Energy: no post read.** Its terms were not found in two tries, so the rule stopped it there.
- **Not reached:** GridStatus's posts, ERCOT's own storage reports, a datacenter's filing or press release.
- **Not used:** the web search tool. A search is not one of the approved reads.
- Of EIA's price file, the rows of PJM's and MISO's hubs were not read into anything.

## What was written

- The three notes, section "Cross-checks" at the end, with an anchor: `battery_earns_algorithm.md` (9 rows), `generator_earns_algorithm.md` (10), `datacenter_pays_algorithm.md` (6). Each row: our figure, the published figure, its source and date, the gap, the reason.
- The same notes' default tables and worked figures, at the new defaults.
- One sentence in each page's source line: "Checked against: N published figures (...)", linked to the section.
- `site/lib/battery/finance.ts`, `seller/finance.ts`, `datacenter/finance.ts`: `HURDLE = 9.6`, `DEG = 2.6`, `BATTERY_DEG = 2.6`, each with its source.
- `site/scripts/check-cross-checks.mjs` (new, 18 assertions); `tests/test_session196.py` (new, 9 tests).
- `site/public` holds no copied file.

## The cross-checks in one place

- **Hub prices hold.** Over 396 delivery periods of January to September 2026 (a day, or two or three days sold as one), our cleared day-ahead peak-block averages against the ICE indices EIA publishes: SP15 24.04 against 23.97; NP15 34.35 against 34.58; New England 77.72 against 78.55.
- **Battery, CAISO:** ours 92 (2025, perfect foresight) and 85 (day-ahead schedule) against the fleet's 53 (2024). No common year; an upper bound for one battery against a settled fleet.
- **Battery, ERCOT:** the model's day-ahead ancillary income is 5.66 times the fleet's awards (the page's own line).
- **Battery against Lazard's cost:** revenue 81.40 and a breakeven toll of 106.79 per kW-year against a cost of 144.90 to 320.04.
- **Generator against Lazard:** the solar contract price 39.14 inside 38 to 78; wind 56.85 inside 37 to 86.
- **Costs against the ATB:** solar capital cost 1,375 against 1,490; wind 2,100 against 1,968; fixed O&M lower than the ATB's on all three.
- **Datacenter against EIA:** wholesale energy 30.59 against an all-in industrial price of 70.70 in Texas (July 2026); 39.47 against 251.10 in California; 77.45 against 108.10 in New York.
- **A gap without a reason:** none. One row states no gap (the gas peaker's toll against a cost per MWh) and says why.

## Checks run

Outputs under `runs/session196/`. Local production build on port 3195.

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit`, twice | 0, 0 | no type error |
| Site build, twice | 0, 0 | no "statement timeout" line |
| `check-cross-checks.mjs` | 0 | 18 of 18; the three lines read from the pages |
| `check-battery-scenarios`, `check-seller-scenarios`, `check-datacenter-scenarios` | 1 then 0 each | first runs failed on the old defaults they pinned (4, 5 and 5 assertions); then 81, 89 and 86 |
| `check-battery-face`, `check-seller-face`, `check-datacenter-face` | 0 each | 20, 24, 23 |
| `check-decisions-face.mjs` | 0, 0 | 144 of 144, twice |
| `check-seller`, `check-seller-deeper`, `check-datacenter`, `check-how-soon` | 0 each | 45, 51, 58, 42 |
| `check-routes.mjs` | 0 | 0 failed |
| `check-values`, pages under `/cost-of-power` | 0 | 3,289 of 3,289 |
| `test-battery-finance`, `test-seller-finance`, `test-datacenter-finance` | 1 then 0 each | first runs failed on the old defaults (5, 2, 5); the hand cases now stay on the values they were worked at, and the new defaults are held beside them |
| `test-decisions-195.mjs` | 0 | 30 of 30 |
| Tests of 178, 179, 186, 190, 194, 195, 196 | 1, then 0 but for 190 | pins on the old defaults and on the notes' last heading, followed; `test_session190`'s one failure is `main`'s |
| Whole suite, clean copy, at `6c58cd0b` | 1 | 3,355 tests, 6 failures: the same 6 that fail on a clean copy of `origin/main` (sessions 149, 153, 183, 190), none of this session's |

- **Not run:** the full `check-values`; every check on production (not landed). The notes' wording was corrected once after the last build ("delivery periods" for "delivery days"); the build was not repeated for it.
- **Not verified:** the published figures were read from each file's text by pattern and by eye; nobody else has read them. The ICE comparison assumes ICE's stated peak blocks and the NERC holidays of 2026.

## The landing

- **Not made:** `main` fails "Tests (tests/)" on GitHub (session 195's report, first bullet). Looked again at 21:28 UTC: `main` is still `27a10ea0`, and no code branch has passed since.
- No snapshot taken, none needed: nothing was pushed to `main` or to a `task/` branch.
- Pushed: `wip/196-cross-checks`.

## To finish

- After session 195 is landed (its report, "To finish"), each its own command:
  1. `git checkout task/196-cross-checks`, `git merge origin/main`
  2. `cd site && npm run build`; the whole suite in a clean copy
  3. `python scripts/freeze.py status`
  4. `node site/scripts/snapshot-live.mjs take s196-before`
  5. `git push origin task/196-cross-checks`
  6. after the deploy: `node site/scripts/snapshot-live.mjs take s196-after`, then `compare s196-before s196-after` (expected 0 differences)
  7. `node site/scripts/check-cross-checks.mjs https://erw-flame.vercel.app` (the three lines on production), and the three scenario checks
  8. delete the remote `wip/196-cross-checks`

## Decisions made without you

- **Degradation from Lazard, not the ATB.** The ruling named the ATB; it holds no rate. Lazard's 2.6 percent goes with Lazard's costs. The other reading (0, cited to the ATB, with its fixed O&M of 4 percent) is one line to switch.
- **2.6 percent at 8 hours too.** Lazard prints it for 2 and 4 hours; the 8-hour costs are already an extrapolation.
- **Solar, wind and the peaker keep a degradation default of none**, with the page's "No cited rate is held": the ruling names the battery.
- **The datacenter page takes 9.6 as well**, as ruled, and says it is a power plant builder's cost of capital.
- **"Checked against" stands in each page's source line**, the grey line at the foot. No page has a box named "Method notes".
- **Requests counted strictly:** robots files, terms pages, a redirect and a failed lookup all count toward the 25.
- **A redirect is not followed** by the read tool; the new host's robots file is read first.
- **The laboratory's new host.** `atb.nrel.gov` no longer resolves; the same baseline is at `atb.nlr.gov`, read after its own robots file and notice.
- **The hub-price check uses ICE's peak block**, computed from the page's own hourly files, since EIA publishes peak indices, not all-hours averages.
- **Not landing on a red `main`**, as in session 195.

## For Samuel's ruling

1. `main` still fails GitHub's check (session 195, item 1). Sessions 195 and 196 wait on `wip/` branches; land 195, then 196.
2. The hurdle rate is 9.6 percent on the three pages, as ruled. Lazard's own method discounts equity's flows at the cost of equity, 12 percent; the battery and generator pages' NPV is to equity. Whether those two take 12.
3. A battery's degradation default is Lazard's 2.6 percent a year, because the ATB holds no rate. Confirm, or rule 0 with the ATB's fixed O&M of 4 percent of capital cost.
4. Lazard's storage cases carry 20 percent debt and 80 percent equity; the battery page gives a battery 60 percent debt. At 20 percent the default coverage is 2.63 times, not 0.88. Which structure the battery takes.
5. Solar's degradation: the ATB states 0.7 percent a year. Whether solar takes it (the default is none today).
6. The datacenter page's hurdle rate is a power plant builder's. Whether to look for a published cost of capital of a datacenter's owner.
7. No published datacenter power price was read. Name the filings or releases to read, and their ceiling.
8. Modo Energy's terms were not found, so no post was read; GridStatus and ERCOT's storage reports were not reached. Name the addresses if they are wanted.
9. Whether a web search may be used to find a published report's address, and whether it counts against a read ceiling.

## The prompt

Chain of 11 October (day), sessions 195 to 197; its text for this session: "Session 196: the three tools against the outside world. Long end 2:30. Model spend USD 0. Pulls: approved reads, at most 25 pages or files in total ... Branch task/196-cross-checks", with five reads in order of priority (Lazard; NREL ATB; battery fleet revenue from ERCOT, CAISO's market monitor, Modo Energy and GridStatus; EIA and the operators' price reports; published datacenter power costs), two rulings on defaults, and a section "Cross-checks" at the end of each of the three Method notes with one line in each page's Method notes box.
