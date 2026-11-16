# Session 7504 report: What a battery saves a customer at the done line (chain 304, part A)

16 November 2026, samueloldlaptop (code role), unattended. Worktree `erw-7504`, branch `wip/7504-battery-customer`, not pushed. Model spend: USD 0. Tool: `/battery/customer` (in review).

## At the top

- **No figure of the arithmetic is wrong.** 331 of 331 figures the page prints, for 12 cases, are inside half the page's last shown digit.
- **One thing the page printed wrong, found by typing real tariffs, fixed with a test:** a typed number was printed back rounded. A demand charge of USD 5.36 read "At $5 per kW that is $536 a month"; a 13.5 kWh battery read "14 kWh"; 25.6 days read "26 days". The figures were made with the number typed; the words beside them did not show it. All nine tariff cases printed their demand charge wrong. The tool's own tests typed whole dollars, so it never showed.
- **A second small site fault fixed:** a field that refuses 0 said its range was "0 to 1,000,000".
- **The largest figure of the page can mislead on a tariff with seasons** (not changed, for Samuel's ruling): "Saved a year" is twelve of the month typed. On Salt River Project's E-32 a reader who types July's rates is shown USD 13,376; the year by the plan's own seasons is USD 8,784 (52.3 percent less).
- **The demand saving is an upper bound** (not changed, for ruling): the tool takes all of a 4 hour battery's power off the peak; NREL's simulation of 98 buildings gives about 85 percent.
- **Not run:** no site build, no browser. The page's promise that nothing typed is sent or stored is held here by the code tests only (the calculator's imports and words are as they were; the new block is words drawn by the server, with no handler, no state and one link that does not prefetch). `site/scripts/check-no-request.mjs` must pass on the landing machine's built site: browser read row 1.
- **Said plainly:** the session that wrote the replication had read the page's code. The replication is in Python, in its own words, from the note, and the note was written first.
- **One test of another tool fails in this worktree** (`tests/test_session161.py`, the `/ask` tool's recorded reads of "this week"): it imports none of the files changed here; see "Tests".
- **Time:** about 85 minutes, over the 75 the brief sized.

## The five parts

- **The method note** (`docs/methods/battery_customer.md`, new: the tool had none): the view; the nine fields and how a typed value is read; the seven rules of the arithmetic; every figure the page prints with its key and rule; the 10 choices with default and source; what the choices do on real tariffs; the cross-check; the cases and the hosts read; the replication; what the tool does not hold.
- **The replication** (`replication/battery_customer/`):
  - `replicate.py` (standard library, no request, writes nothing), `cases.json` (12 cases), `page_figures.json` and `.csv`, `replicate.do`.
  - The tool reads no table, so a case is nine typed numbers. Nine cases are real published rates: Seattle City Light (WA) medium general service time of use, City and Downtown Network, and large general service; Salt River Project (AZ) E-32 in its three seasons; Austin Energy (TX) secondary voltage, both demand classes; Southern California Edison (CA) TOU-GS-2 B of 2013 as NREL's report prints it. Each with its document, address, effective date and time read. The customer's peak and the battery are the case, not data.
  - The page's side: `site/scripts/battery-customer-figures.mjs` draws the page's own calculator with each case's numbers in its fields and reads every number of the words drawn.
  - As printed: `331 of 331 inside the tolerance, 12 cases; computed here and not shown by the page: 0; not replicated here: nothing`.
  - `replicate.do`: five headline figures, expected values at its top. Not run (no Stata here); its Python mirror (`--headline`) printed the same values.
- **The cross-check** (`replicate.py --crosscheck`; robots and terms of each host read first): the table is under "For the pack". Nothing published stands against a named customer's saving in dollars; said in the note.
- **The decisions block** (`site/app/battery/customer/Decisions.tsx`, mounted under the two folds, above the source line): 10 choices, each with its default and source on hover, closed to start, no grey note. The three defaults a reader can change (2 hours, 21 days, 86 percent) were already changed in place, in their fields. The 2 hours has no published source and the block says so.
- **The faults** (`docs/reviews/battery-customer-faults-2026-11-16.md`): 9 rows. Site fixed 2; data machine 0; rulings 7.

## Tests

Command, one file at a time: `.venv\Scripts\python.exe -m unittest tests.<file>` with `ERW_SPEND_CAP_USD=0`, output to `runs/7504/`.

| File | Tests | Result |
|---|---|---|
| `test_session7504_battery_customer` (new) | 16 | pass |
| `test_session88` (the tool's own: arithmetic, nothing sent) | 11 | pass, 1 skipped by its own rule (no served build) |
| `test_session203`, `241a`, `242`, `5162` (they name the page) | 15, 17, 12, 9 | pass |
| `test_session142`, `147` (they sweep the method notes) | 42, 65 | pass |
| `test_session158`, `160`, `301` (they sweep the method notes) | 58, 40, 9 | pass |
| `test_session149`, `1502`, `177`, `182_flow`, `196`, `215`, `371`, `473`, `5155`, `5163`, `5169`, `462`, `465` (they sweep the site's files or the decisions blocks) | 39, 4, 28, 19, 9, 12, 10, 7, 10, 6, 9, 8, 10 | pass (one skipped by its own rule in `149`, `1502` and `465`) |
| `test_session161` (a sweep; it also replays the `/ask` tool's recorded reads) | 11 | 10 pass, 1 fails: `site/scripts/test-ask-161.mjs` asks for a read of "this week" that its fixture does not hold ("a read that was not recorded"). It imports `site/lib/chat/` only, none of the files this session changed. Not run on a clean tree, so not called the base's here: one line under "Seen in another tool" |

- `node --import ./scripts/tsx-register.mjs scripts/test-battery-customer-page.mjs`: 31 of 31 passed.
- `node --import ./scripts/tsx-register.mjs scripts/battery-customer-figures.mjs --check`: 331 figures, as committed.
- A narrow type check: `tsc --noEmit` on `page.tsx`, `Calc.tsx`, `Decisions.tsx`, `lib/customerbattery.ts` and what they import, with the site's settings less Next's plugin: exit 0, no message (`runs/7504/tsc.out`). Not a build.
- Not run: `check-no-request.mjs`, `check-routes.mjs` (they need a served build and a browser).

## What to review

- `https://erw-flame.vercel.app/battery/customer` (in review: open it with the review cookie).
  1. As it opens: "Fill in every field to see what the battery saves. 6 of 9 still needed."
  2. Type: peak 400; demand charge 5.36; peak rate 0.1218; off-peak rate 0.0609; battery power 100; battery energy 400; hours 4; days 26; round trip 86 (Seattle City Light, medium, City of Seattle). See: "lowers the bill by $1,066 a month, $12,795 a year: $536 a month from a lower peak and $530 a month from moving energy." Under "How the two numbers are made": "At $5.36 per kW that is $536 a month." (before: "At $5 per kW").
  3. Change battery energy to 13.5 and battery power to 5: the summary says "a 5 kW battery holding 13.5 kWh" (before: "14 kWh").
  4. Type 0 in the peak: the line under it says "Not a number this page can use (more than 0, up to 1,000,000)."
  5. Scroll under "What it leaves out": "Decisions on this page (each with its default and its source on hover)". Open it: 10 lines. Hover or tap an "i": Default and Source.
  6. The network panel while typing: no request.
- `https://erw-flame.vercel.app/data/methods/battery_customer`: the new note.

## For the pack

- **What Samuel signs:** the calculator computes what its seven rules say, to the dollar, on whatever a reader types; on nine cases of published rates from four utilities every printed figure was recomputed independently; the saving is a saving on the bill under stated assumptions (the battery knows the peak, one cycle a day, twelve months alike), an upper bound on the demand charge, not a return and not advice.
- **The five choices that matter most:**
  1. The battery knows the peak and is full for it: all of the smallest of power, energy over the hours, and the peak comes off. Default: all of it. Source: a choice of session 88; NREL gives about 85 percent for a 4 hour battery (NREL/TP-5400-63162, 2015, page 16).
  2. How long the peak lasts. Default: 2 hours. Source: none published (the tariffs read have peak-rate windows of 4 to 6 hours).
  3. The year is twelve of the month typed. Default: twelve months alike. Source: a choice of session 88; 52 percent over on Salt River Project's July.
  4. One full cycle a day when moving energy pays, whatever the building uses. Default: one cycle. Source: a choice of session 88; NREL calls a daily cycle a worst case for energy used (page 9).
  5. Round trip. Default: 86 percent. Source: Lazard LCOE+, June 2025, page 43 (low end); ATB 2025 gives 85. Both are grid battery figures.
- **The cross-check:**

| What | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| Share of a 4 hour battery's power off the monthly peak | 1.00 | about 0.85 | NREL, Neubauer and Simpson, NREL/TP-5400-63162, January 2015, page 16 | ours 18 percent higher (USD 3,014 against USD 2,562 a month on the report's tariff) | the tool knows the peak; NREL ran a controller on 98 buildings' 5-minute loads |
| The same for a 30 minute battery | 0.25 at the starting 2 hours; 1.00 at half an hour | about 0.60 under 25 kW | the same, page 9 | not one figure | the tool has no load shape, only the hours typed |
| Saving from the peak over saving from energy | 4.5 on the report's tariff; 0.94 to 2.06 on today's six time-of-use cases | demand "dwarfs" energy, "often by an order of magnitude or more" | the same, page 9 | ours gives energy far more | the tool cycles the whole battery daily; the report's tariff charged USD 30.14 per kW |
| Demand charges above USD 15 per kW | 3 of 9 cases above, 6 below | nearly 5 million of 18 million commercial customers can subscribe to such tariffs | NREL and Clean Energy Group, NREL/BR-6A20-68963, August 2017, page 1 | none to take | places the cases |
| A named customer's saving in dollars a year | USD 7,164 to USD 62,059 | nothing published stands against it | NREL's SAM case studies (NREL/TP-6A20-64987, November 2015) give net present values with costs in them | not comparable | said plainly |

- **The Stata commands** (from `replication/battery_customer/`): `do replicate.do`. It should print:
  - `Seattle City Light, medium, City of Seattle, time of use: saved a year (USD): 12795.06`
  - `Seattle City Light, medium, Downtown Network, time of use: saved a year (USD): 21732.89`
  - `Salt River Project E-32, summer peak: saved a month (USD): 1114.70`
  - `Austin Energy, secondary voltage 10 to under 300 kW: saved a year (USD): 8931.16`
  - `Southern California Edison TOU-GS-2 B, summer 2013, as NREL prints it: saved a month (USD): 3676.97`
- **The rulings, in plain words** (each with the default taken): under "For Samuel's ruling".

## Data request rows

None. The tool reads no table and no file a builder writes.

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 | 7504 | wip/7504-battery-customer | /battery/customer | `node scripts/check-no-request.mjs` on the built site; the network panel while typing in every field and while hovering a tip of the new fold | "passed: typing into the page made no request and stored nothing"; no request on a hover or on opening the fold | wanted |
| 2026-11-16 | 7504 | wip/7504-battery-customer | /battery/customer | Type 400, 5.36, 0.1218, 0.0609, 100, 400, 4, 26, 86 | "$1,066 a month, $12,795 a year"; "At $5.36 per kW that is $536 a month."; then battery 5 kW and 13.5 kWh: "holding 13.5 kWh" | wanted |
| 2026-11-16 | 7504 | wip/7504-battery-customer | /battery/customer | The fold "Decisions on this page" under "What it leaves out"; hover and tap an "i"; at 390 px | Closed to start; 10 lines; each tip shows Default and Source, stays inside the screen at 390 px, no sideways scroll | wanted |
| 2026-11-16 | 7504 | wip/7504-battery-customer | /battery/customer | Type 0 in "Your peak demand" | "Not a number this page can use (more than 0, up to 1,000,000)." and no figure | wanted |

## Landing request

- **Head:** the commit that holds this report on `wip/7504-battery-customer` (its hash is in the reply to the orchestrator). Stacked on `wip/7500-done-line`.
- **Tests:** the table above; `site/scripts/test-battery-customer-page.mjs` (31 of 31).
- **What changes:** `/battery/customer` prints a typed number as typed, says a field's range in words, and gains the decisions fold. New: `docs/methods/battery_customer.md`, `replication/battery_customer/`, two scripts under `site/scripts/`, one test file, the faults file.
- **What does not:** the arithmetic (`saving`, `read`, `readAll`, `usd`, `qty` are as they were), the nine fields, the two folds, the promise and its browser proof, `release.ts`, every table.
- **Snapshot:** no difference expected on the 25 addresses read as a visitor (every page is in review). With the review cookie: `/battery/customer` differs by the fold; `/data/methods/battery_customer` is new.
- **Before landing:** a build on the landing machine (the first whole build of the four site files), and `check-no-request.mjs` on it.

## Needs the key

- Nothing. No step of this tool needs a model.

## Decisions made without you

- No tariff was put on the page: it says "your own numbers, not ERW data", and a list of utilities' rates on it would be data. The tariffs are cases of the replication only.
- The customer's peak and the battery of each case were chosen inside the tariff's class (400 kW with 100 kW and 400 kWh; 2,000 kW; 200 kW; 1,000 kW). They are the case, said as such in `cases.json`; no figure of them is called data.
- Where a tariff bills one kW twice (Austin Energy's demand and regulatory charges; Southern California Edison's facility and on-peak charges) the case types the sum. Where it has three energy prices the case types the highest and the lowest.
- Southern California Edison's 2013 rate is taken from NREL's report, not from the utility: it is the tariff the cross-check's report used. `sce.com` was not asked for anything but its robots file.
- Duke Energy was not read (its robots file disallows the folder its tariff files are in). Xcel Energy was left (no robots file answered).
- The decisions block is the tool's own small component, not the shared `DecisionsBlock` (another branch changed the shared one).
- The publishers' files fetched stay in `runs/7504/dl/` (ignored).
- The 14 older grey notes of the page were left (faults row 7).

## For Samuel's ruling

1. **"Saved a year" on a tariff with seasons.** Twelve of the month typed can be 52 percent over. Default taken: unchanged, said in the fold's hover. The other way: ask for the months each season lasts.
2. **The demand saving as an upper bound.** Default taken: unchanged, NREL's 85 percent on hover. The other way: a field "share of the battery's power that comes off", starting at 100.
3. **The starting 2 hours for the peak** has no published source. Default taken: kept, said so. The other way: start the field empty, as the six fields of the bill are.
4. **Energy moved is not capped by the building's use.** Default taken: unchanged, said. The other way: a field for the building's use in the peak-rate hours.
5. **Move the page's 14 grey notes into hover tips,** as the page standard asks? Default taken: left, counted.
6. **Two cases side by side** (two batteries, or two tariffs)? Default taken: not built.
7. **The sentence when the total is below zero** reads "lowers the bill by -$23 a month". Default taken: left.
8. **Salt River Project's and Austin Energy's terms** bar reproducing their materials without written permission (neither says anything of automated access; both robots files allow the files read). The repository keeps only their rates as figures, each cited and linked, in `replication/battery_customer/cases.json` and the note; no text or page of theirs is copied and nothing of theirs is on the site. Default taken: kept so. If a rate is itself to be treated as their material, the four cases come out and the replication stands on Seattle City Light and the NREL report's table.

## Seen in another tool (one line each)

- `/ask`: `tests/test_session161.py` fails in this worktree on `site/scripts/test-ask-161.mjs` (4 of 8: a recorded read of "this week" is not in `tests/fixtures/session161/week_reads.json` for today's date). No file of this session is imported by it. Not checked on a clean tree.
