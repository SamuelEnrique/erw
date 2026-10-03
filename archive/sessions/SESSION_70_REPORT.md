# Session 70 report: battery game v4, three rule fixes

Energy Research Warehouse (ERW), session 70, a follow-up to session 66 in the same worktree (`C:\Users\samen\Documents\erw-game`) on the same branch (`wip/066-battery-game-v4`), 2026-10-02, ending about 21:05 UTC. **Model spend: USD 0.00** (the cap was USD 0.00). No paid service, no data pulls, no model calls, no force push. No Supabase write, migration 019 **not applied**, the data lock not taken, no builder run, nothing pushed to main or to any `task/` branch. The main folder (`C:\Users\samen\Documents\erw`) was not read, written or used for git; only its Python interpreter was called by path. The finish step below was **not run**.

Version 4 is still unreleased, so these changes are version 4: no new rules version, no new migration.

## To finish

This is session 66's finish step, restated in full. Session 70 changed no command in it; it adds one test module to step 3 and changes what the checks in step 6 print. This report alone is enough to finish version 4.

Run these on the machine that holds the raw EIA-930 workbooks and `warehouse/output` (the main folder), once no other session is using it. Version 4 is not live until step 4. `main` has moved ahead of this branch's base since session 66; step 4's workflow merges it.

**1. Take the data lock** (in the main folder):

```bash
python warehouse/lock.py acquire --task "session 70 finish: migration 019, battery solar shapes" --minutes 90 --wait 30
```

**2. Apply migration 019** (in the main folder, with a copy of the branch's file; `apply.py` applies every migration in order and each is idempotent):

```bash
git fetch origin
git show origin/wip/066-battery-game-v4:warehouse/supabase/migrations/019_game_v4.sql > warehouse/supabase/migrations/019_game_v4.sql
python warehouse/supabase/apply.py
rm warehouse/supabase/migrations/019_game_v4.sql
```

The copy is removed after it is applied so that the merge in step 4, which brings the same file, finds nothing in its way. The migration only replaces the preset checks of `game_scores` and `game_plays`; old v2 and v3 rows stay valid. Until it is applied the database refuses a v4 play, and the page says the play was not stored.

**3. Run the solar builder** (from this worktree, reading the main folder's data; it writes only `site/data/battery_levels.json` here):

```bash
cd C:/Users/samen/Documents/erw-game
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe warehouse/derived/battery_solar.py --data-root C:/Users/samen/Documents/erw --dry-run
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe warehouse/derived/battery_solar.py --data-root C:/Users/samen/Documents/erw
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe -m unittest tests.test_session70 tests.test_session66 tests.test_session38 tests.test_session56 tests.test_session50
git add site/data/battery_levels.json
git commit -m "Session 70: the famous days' solar shapes (EIA-930 over EIA-860M), written by battery_solar.py"
```

Read the dry run first: it prints, per level, the shape's highest and lowest hour, or why a level has no shape. A level without every hour of its day gets none, and the rooftop add-on stays unavailable for it. The tests then run the required result with the roof on each day that got a shape. **If that test fails for a day with the roof, do not change the price: report the case** (session 70's ruling).

**4. Merge the branch to main** (a push to a `task/` branch runs code-branch.yml: the tests, the site build and check-routes, then the merge and the deploy):

```bash
git push origin wip/066-battery-game-v4:task/066-battery-game-v4
```

**5. Release the lock** (in the main folder):

```bash
python warehouse/lock.py release
```

**6. The live checks**, once the deploy is up (about a minute after the merge):

```bash
cd site
node scripts/check-routes.mjs https://erw-flame.vercel.app
node scripts/check-lights.mjs https://erw-flame.vercel.app
node scripts/play-battery.mjs https://erw-flame.vercel.app
```

- `check-lights.mjs` reads the levels the site serves, today's level included, and checks that the perfect battery never ends in lights out. It posts nothing. Its last line now reads "lights out charged for the whole outage at USD 35000/MWh".
- `play-battery.mjs` posts one v4 play per difficulty (Easy, Normal, Hard, a custom Hard battery) and both add-on states on Hard: off, and rooftop solar on (on a famous day that holds a shape), each marked as an ERW check so it stays off the boards. It also checks that the roof is refused on a day without a shape, and that v2 and v3 boards still read. It makes more than 30 requests, the API's hourly floor from one address: if the later checks answer HTTP 429, wait an hour and run it again.
- In a browser: play Hard on 2021-02-15, sell down to the reserve early and let the lights go out. The end screen should read as in "Test results" below.

## In plain words

**Fix 1: the lights-out charge is now a real, citable number.** Unserved house energy is charged at USD 35,000 per MWh, the value of lost load the Public Utility Commission of Texas approved for the ERCOT region on 29 August 2024. Session 66's "6 times the cap", found by search, is gone, and so are the search and its test. The page and the method say it is a game rule, give the figure and both sources, say it is the system-wide value and that residential customers alone came out far lower in the same study (USD 3,964), and say the Texas figure is used on California's days too.

**Fix 2: going dark costs the whole outage.** If the lights go out at any moment of the outage, the house pays for the power it needed in the whole outage: USD 105.00 for a two-hour outage without a roof. Before, only the time left was charged, so going dark in the last minutes was cheap. The round still ends there. The page's sentence: "If the lights go out at any moment of the outage, you pay for the power the house needed in the whole outage, not only the part it missed."

**The required result holds, with nothing tuned.** The perfect battery does not end in lights out in any of 73 cases where the lights can be kept on: the 7 famous days, the toy days, and the largest inverter the settings allow (11.5 kW) on six batteries. Today's level passes too. The closest case still has a wide margin.

**Fix 3: the roof no longer pays to export.** When the price is below zero and the battery is not charging, the rooftop array is switched off and earns nothing. The add-on's text on the page says so.

**The numbers on the famous days did not move.** The perfect battery already kept the lights on under session 66's rule on all 7 days, so it plays the same plan and earns the same.

## The perfect battery on the 7 famous days

Default battery. "Cost of staying lit" is what the perfect battery gives up by not going dark: its best score if the dark were free, less its score. Session 66's report gave the same two non-zero costs (USD 11.09 on Uri and USD 0.05 on the duck day); they are unchanged.

| Day | Hard, USD | Hard ends | Charge at the outage's start, kWh (need 3.16) | Cost of staying lit, USD | Session 66's Hard, USD | Normal, USD | Normal ends |
|---|---|---|---|---|---|---|---|
| 2021-02-15 Uri | 155.71 | whole day, lights on | 4.02 | 11.09 | 155.71 | 240.23 | whole day |
| 2023-08-10 ERCOT heat | 49.01 | whole day, lights on | 5.59 | 0.00 | 49.01 | 60.97 | whole day |
| 2026-04-26 calm | 29.49 | whole day, lights on | 3.85 | 0.00 | 29.49 | 0.44 | whole day |
| 2026-08-29 solar | 29.61 | whole day, lights on | 3.85 | 0.00 | 29.61 | 0.93 | whole day |
| 2025-01-05 negative | 29.72 | whole day, lights on | 8.23 | 0.00 | 29.72 | 0.79 | whole day |
| 2026-04-27 CAISO solar noon | 29.71 | whole day, lights on | 8.23 | 0.00 | 29.71 | 0.83 | whole day |
| 2026-07-24 CAISO duck | 34.33 | whole day, lights on | 3.32 | 0.05 | 34.33 | 12.98 | whole day |

- What changed is the price of failing, not the perfect plan. Going dark on Uri would now cost USD 105.00 whenever it happens, against USD 11.09 saved at most. Under session 66 going dark in the last fifteen minutes cost USD 11.25 against USD 10.92 saved by that plan, a margin of 33 cents.
- Today's level as the live site serves it (2026-09-30): Hard 29.58 USD, a whole day, 3.85 kWh at the outage's start.
- "Hard with rooftop solar" still cannot be computed: no level holds a solar shape until step 3.

## The sources, as verified

Each document was downloaded and read in this session (2026-10-02). None is cited from the prompt alone.

| Claim | Verified | Where |
|---|---|---|
| The Commission approved a VOLL of USD 35,000 per MWh in August 2024 | **Yes.** "Commissioners approved a VOLL of $35,000 per megawatt-hour", at the open meeting of 29 August 2024 | Public Utility Commission of Texas, press release "Public Utility Commission of Texas Adopts Reliability Standard for the ERCOT Market", 29 August 2024, https://ftp.puc.texas.gov/public/puct-info/agency/resources/pubs/news/2024/PUCT_Adopts_Reliability_Standard_for_the_ERCOT_Market.pdf |
| It was Project No. 55837 | **Yes.** The release points to "PUCT Docket No. 55837" for the VOLL and the survey; the study's cover reads "Project No. 55837, Review of Value of Lost Load in the ERCOT Market" | the same release; the study below |
| The study found a one-hour, system-wide value of USD 35,685 per MWh | **Yes.** "The one-hour, system-wide VOLL for the ERCOT Region yielded by the VOLL survey is $35,685 per MWh" | The Brattle Group (Gibbons and Sergici), *Value of Lost Load Study for the ERCOT Region*, filed by ERCOT in Project No. 55837 on 22 August 2024, https://www.brattle.com/wp-content/uploads/2024/09/Value-of-Lost-Load-Study-for-the-ERCOT-Region.pdf |
| The same study found a lower value for residential customers alone | **Yes: USD 3,964 per MWh** for a one-hour outage (small commercial and industrial 666,907; medium and large 22,721; ERCOT-wide 35,685; 2024 dollars, a weekday afternoon outage without warning) | the study's table of VOLL per unserved MWh by customer class and duration |

**One correction to the prompt's wording: there is no order.** The prompt says to verify against "the PUC's order or announcement". The Commission did not issue a written order for the VOLL. A filing in another docket says so in terms: asked for the order, the answer was that "the Commission issued its directive to use a $35,000 VOLL" at the 29 August 2024 open meeting "and did not memorialize its vote in a written order" (PUC Docket No. 57579, item 61, https://interchange.puc.texas.gov/Documents/57579_61_1474998.PDF). So the page and the method cite the press release, and say there is no written order.

**One more thing the sources say:** the Commission approved the figure for planning (the reliability standard and the study of market changes). Nobody is billed it. The page and the method say that charging a house at it is the game's rule.

## What changed

| File | Change |
|---|---|
| `site/lib/battery.ts` | `LIGHTS_OUT` holds the price, the study's figure, the residential figure and the two links; `Rules.voll` replaces `penaltyMultiple`; lights out is charged from the outage's first interval, in `simulate` and in the DP; `roofSale` (the roof at negative prices), called by both; `Result.curtailedKwh`; the add-on's text |
| `site/app/play/battery/page.tsx` | the lights-out rule and "Where USD 35,000 per MWh comes from", with links |
| `site/app/play/battery/Game.tsx` | the lights-out note and the outage banner; "switched off" beside the roof while curtailed; the end screen's hour gives no price when it is an outage hour |
| `site/scripts/test-battery.mjs` | the multiple search removed; the fixed price, the whole-outage charge, the required result on 73 cases, the curtailment checks; two more brute-force presets |
| `site/scripts/check-lights.mjs`, `check-scorer.mjs` | the new price |
| `docs/methods/battery_game.md` | "Lights out costs money" rewritten with the sources; the roof below zero |
| `tests/test_session70.py`, `tests/test_session66.py` | 10 new tests; session 66's assertions about the multiple replaced |

## Test results

- **`site/scripts/test-battery.mjs`: all pass.** The DP optimum equals brute force over all 3^12 action sequences on the four toy days under eight presets: the six of session 66, the roof with sun in the negative-price intervals (curtailment in play), and the 11.5 kW inverter without a reserve.
- **The required result: 73 cases, the lights can be kept on in all 73, and the perfect battery ends in lights out in none.** The 7 famous days on Hard with the default battery; 12 toy cases (the 2 toy days with an outage under the 6 Hard presets); and 54 with the 11.5 kW inverter (6 batteries: 13.5, 30 and 5 kWh, each with and without the reserve and the wear cost, on the 7 famous days and the 2 toy days). No case failed, so there is nothing to report under "do not tune".
- **The margin.** The closest of the 73 is a toy day with the 11.5 kW inverter: with no charge at all, going dark would earn USD 13.44 more than staying lit; the charge is USD 52.50 (a one-hour outage).
- **Today's level** (2026-09-30, read from the live page, nothing posted): passes, via `check-lights.mjs`.
- **`check-scorer.mjs`: 103 checks pass.** The server's scorer and `lib/battery.ts` agree under the new rules, called directly, nothing posted.
- **Python: 285 tests, all pass, 30 skipped** (the main folder's interpreter by path; the skips read `warehouse/output` tables this worktree does not hold). `tests/test_session70.py` adds 10.
- **`tsc --noEmit`: pass. `npm run build`: pass. eslint on the files touched: pass, no warning.**
- **check-routes on the local build: 68 of 68 pages pass** (no baseline: this folder has no Supabase key).
- **In Chrome on the local site, Hard on 2021-02-15, lights out:** the battery was sold down to its 2.70 kWh reserve early in the day (money USD 38.14) and left alone. The outage banner read "you pay for the power the house needed in the whole outage ($105.00)". The lights went out at 20:30, in the outage's seventh interval. The end screen:
  - "You lost $71.86." (33.14 earned less 105.00)
  - "The perfect battery, which knew every price ahead of time, earned $155.71 on the same day with the same rules."
  - the hour lost most was 20:00 to 21:00: the perfect battery made $0.00, the play -$105.00.
  - "Lights out at 20:30 ... That is 3.00 kWh at USD 35,000 per MWh, the value Texas's utility commission puts on power that is not delivered: $105.00 ... The outage needed 3.16 kWh from the battery; at its start the battery held 2.70 kWh. The charge took your money below $0."
  - The charge is for the whole outage (3.00 kWh, all eight intervals), though the house was dark for only the last two.
- **Not seen in a browser:** the third line's new wording for an outage hour (changed after that play; built and type-checked only), and the roof's curtailment on a real level (no level holds a shape; it is covered by the library tests and by brute force).

## Errors and decisions

- **Decision: while the battery charges at a negative price, the roof's power still goes into it first.** The prompt curtails the roof when the price is below zero "and the battery is not charging". So when it is charging, session 66's rule stands: the roof fills the battery and only what does not fit is curtailed. The consequence: that power takes the place of grid power the battery would have been paid to take, so with the roof on, charging at a negative price earns less than without it. The other reading (switch the roof off whenever the price is negative, and charge from the grid) is one line in `roofSale`. The method states the consequence.
- **Decision:** "not charging" includes a full battery told to charge: it takes nothing, so its roof is curtailed.
- **Decision:** only a price below zero curtails. At exactly zero the roof is on and earns nothing.
- **Decision: "the larger-inverter presets session 66 identified".** Session 66 named a much larger inverter and a tiny battery without giving presets. They are taken here as the largest inverter the settings allow, 11.5 kW, on the default, the largest and the smallest battery, each also without the reserve and the wear cost, where selling pays most.
- **Decision:** the residential figure is stated on the page and in the method, since it was verified.
- **Decision:** the page says the Commission approved the figure for planning and that nobody is billed it. The prompt did not ask for this; the source says it, and leaving it out would let the charge read as a real tariff.
- **Decision:** the end screen's third line gives no price when the hour lost most is an outage hour (the grid is down, so no price applies). This is outside the three fixes; it was changed because the line read wrongly in the browser check.
- **Decision:** two web searches were run to find the documents' addresses. The documents themselves were downloaded and read locally. The fetch tool that summarizes a page with a model was not used, to keep to "no model calls".
- **Seen, not fixed:** in the replay, when the perfect battery keeps holding after the outage, the line still reads "held: grid outage" for the hours after it. It dates from version 3 and is outside this session's scope.
- **Seen, not fixed:** in a hidden browser tab the big price number and the chart's label can show neighbouring intervals for one frame. A visible tab redraws both every frame.
- **Error:** the first browser play sold nothing, because the scripted key press was sent before the game listened for keys; it ran to the end as an idle play and was played again.
- **Error:** one new test assumed a four-interval day at a price of zero has no emergency; on Hard it does. The test was corrected to a three-interval day; the rule was right.

## For Samuel

1. **Run the finish step** (above). Nothing in it has been run. Until step 3 the rooftop add-on is unavailable on every level; until step 2 no v4 play is stored.
2. **There is no PUC order to cite for the USD 35,000.** The Commission voted at an open meeting and recorded it only in a press release. The page and the method cite the release and say so. If the battery expert asks for the order, that is the answer.
3. **The figure is the system-wide one, about nine times the residential one** (USD 3,964). The game charges a house at it because it is the value the Commission approved; the page says both. Whether a house should instead be charged the residential figure is yours to rule: at USD 3,964 a whole two-hour outage would cost USD 11.89, barely above the USD 11.09 that going dark saves on Uri with the default battery. The 73 cases were not run at that price, but the closest larger-inverter case would fail (USD 13.44 saved against USD 5.95 for its one-hour outage), so the required result would not hold for every battery.
4. **The roof at a negative price while charging** (the first decision above): say if you want the roof switched off then too.
5. **When step 3 gives the levels their shapes, the required result is tested with the roof for the first time on real days.** If a day fails, the ruling is to report it, not to change the price.
