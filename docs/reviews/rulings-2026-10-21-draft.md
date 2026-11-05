# Every open ruling of sessions 351 to 440, with a recommended answer (a draft)

Energy Research Warehouse (ERW), session 447, 21 October 2026, on portable-laptop (code role), branch `wip/441-450-third`. The agenda for Samuel's review. **Nothing is decided here**: each item gives the evidence its reports give, the reversible choice the session made meanwhile, what each answer would change, and one recommended ruling with its reason. The recommendation is this session's reading of the reports, not a ruling.

## How this list was made

- **50 reports found** for the 90 numbers 351 to 440, **45 with a ruling section** (370's is one paragraph, not a list); the other 5 are notes' sessions whose waits are in their notes (356, 364, 380, 386 and 389). Each report was read from the branch whose newest commit touched it (`runs/chain_oct21_third/s447/extract.py`; its output `sections.md` and `coverage.csv` beside it, outside git). Reports of 402 to 414 were read from `origin/wip/015-land`, 420's from `origin/wip/findings-oct20`, the rest from `origin/main`.
- **The eight notes' waiting lists** that fall in the run were read as well: `docs/state/review_2026-10-20_code.md` (its part for 351 to 356), `review_2026-10-20_day_code.md` (367 to 372), `review_2026-10-20_third.md` (the third machine's 344 to 350, named by 366 and 367), `morning_2026-10-21.md` (357 to 364), `morning_2026-10-21_day.md` (373 to 380), `morning_2026-10-21_night.md` (384 to 386), `review_2026-10-21_night_code.md` (381 to 383) and `note_2026-10-21_day_data.md` (387 to 389).
- **Counts.** 118 list lines in the reports' ruling sections and 43 numbered items in the notes' lists, 161 lines in all. 11 of the report lines say "nothing new", "none new" or point to a note's list, and are not items; 5 are information or steps, not a question (373's page files; 420's four steps to open, check and fold the findings, kept with item 57). The remaining lines make **57 items** below: every line that asks the same thing as another was merged into one item (the notes restate most report lines), and each item cites every report and note that raised it. 15 lines are already answered (five entries at the end) and are not counted in the 57.
- **Sessions in 351 to 440 with no report anywhere** (read-only search of `origin/main` and every `origin/wip/*` and `origin/task/*` branch, after the parent's fetch of 21 October): 390 and 391 (queued in `queue/next/017-day-21-october-data-pm.md`, not yet run); 392 to 400 (no chain file reserves them); 401 and 408 (commits on `origin/wip/401-s` and `origin/wip/408-s`, no report written); 411, 412 and 415 (reserved by `queue/done/015-day-20-october-code-pm.md`, no commit found); 416 to 419 and 421 to 430 (no chain file reserves them); 431 to 440 (reserved by `queue/done/016-night-21-october-data.md`, the data machine's night chain, running while this was written: no report pushed yet).
- **The groups are the ledger's** (`/internal/waits`, session 414, `site/scripts/build-waits.mjs` on `origin/wip/414-s`, `BLOCK_RULES`): money, a data pull, a ruling on a figure, a public page, and "None of the four". The ledger places an item by fixed word rules; here an item is placed by what its answer blocks, with those rules as the guide, and an item the rules would place elsewhere says so.
- **The rank of the first three follows the ledger's rule** (session 414: only a note that says its list is ranked by value ranks, the newest first). The newest such note is session 389's `docs/state/note_2026-10-21_day_data.md`, "Waiting for you, highest value first", items 1 to 3.
- **Samuel's ruling of 21 October** (the chain file of this session) answers sessions 406's and 407's ten items: no long-form piece and no newsletter of any kind, the drafts stay on their branches unused. They are listed under "Already answered".

## The three highest value first

### 1. Redivis storage: 10 GB free, full

- **Raised by:** sessions 358, 363, 376, 377 and 385; notes `morning_2026-10-21.md` item 1, `morning_2026-10-21_day.md` item 1, `morning_2026-10-21_night.md` item 1, `note_2026-10-21_day_data.md` item 1 (session 389).
- **Evidence:** `node_basis_daily` (950,000 rows) could not be drafted (358). Release v1 lists a table the draft lacks (363; `docs/redivis/release-v1-runbook.md`). Since session 385 a refusal removes the table from the draft. `docs/redivis/organization-move.md` sets out four choices: the 41 license-held tables out of the draft (frees 0.94 GB), the private dataset elsewhere (1.09 GB), a paid tier, the organization's storage after the move.
- **Meanwhile:** every growing table's Redivis step is a skip, not a failure (377); `node_basis_daily` is "held: Redivis storage" in v1 (375).
- **What each answer changes:** taking the 41 held tables out frees space today at no cost and changes no public page; a paid tier costs money each month and keeps every table in one place; waiting for the organization's storage keeps the draft behind until the move.
- **Recommended ruling:** take the 41 license-held tables out of the draft now, and decide a paid tier only after the move under Ben's organization (item 3). Reason: the held tables cannot be released anyway, it frees 0.94 GB without spending, and it can be undone by uploading them again.

### 2. The database: statement timeouts and pg_cron's startup timeouts

- **Raised by:** sessions 383 and 387; notes `review_2026-10-21_night_code.md` "First" item 1 and "Waiting" item 1, `note_2026-10-21_day_data.md` item 2.
- **Evidence:** from about 23:30 UTC on 20 October Supabase answered heavier reads with statement timeouts (code 57014); builds failed on required reads (383; GitHub runs 39525362021 and its re-run). In the same hours, 23:30 UTC on 20 October to 05:15 UTC on 21 October, 47 of pg_cron's runs failed with "job startup timeout", against 3,838 successes since 2 October (387). The chain file of this session states the database is timing out again on the night of 21 October.
- **Meanwhile:** landings waited (383); the jobs' own `schedule` fallbacks ran; no setting was changed.
- **What each answer changes:** reading the project's resource graphs (disk input and output budget, connections) names the cause; turning `cron.use_background_workers` on needs a restart and removes the connection to `localhost` each job opens; a larger plan costs money each month.
- **Recommended ruling:** read Supabase's resource graphs for 23:30 to 05:30 UTC first, then turn background workers on if connections are the cause, and change the plan only if the disk budget is spent. Reason: both failures share the same hours, so one limit is likely behind both, and a restart alone does not lift a spent budget. (The ledger's word rules would place this item under money, by "the project's plan".)

### 3. The move under Ben's organization, and its order against the release click

- **Raised by:** session 385; notes `morning_2026-10-21_night.md` item 2, `note_2026-10-21_day_data.md` item 3.
- **Evidence:** `docs/redivis/organization-move.md` (385) gives the steps and the order question; the organization's storage is one of item 1's four choices.
- **Meanwhile:** the dataset stays under its present owner; nothing is released (only a person releases, CLAUDE.md rule 6).
- **What each answer changes:** moving first gives release v1 its permanent address and citation; releasing first gives a citable version sooner, under an address that later changes.
- **Recommended ruling:** move first, then release v1 once under the organization. Reason: a citation's address should not change after the first release, and the move may also answer item 1.

## Money

- Items 1 and 2 above.

No other item of the run asks for money directly. Item 9's SPP letter matters only if the ERW sells anything (378).

## A data pull

Item 3 above, and:

### 4. The uploader's replace

- **Raised by:** session 385; note `morning_2026-10-21_night.md` item 1.
- **Evidence:** a refusal by Redivis now removes the table from the draft; the proposal uploads the new copy under a temporary name and swaps only once it is whole.
- **Meanwhile:** not made; it changes the daily's Redivis step and cannot be proven without an upload.
- **What each answer changes:** made, a full store no longer empties a table from the draft; not made, any growing table can disappear from the draft on a refusal.
- **Recommended ruling:** make it, proven on one small table's upload under the data lock. Reason: it removes a way to lose a table from the draft, whatever is ruled on item 1.

### 5. The four permission letters

- **Raised by:** session 378; notes `morning_2026-10-21_day.md` item 2, `morning_2026-10-21_night.md` item 5, `note_2026-10-21_day_data.md` item 7.
- **Evidence:** four letters drafted, not sent (`docs/reviews/licenses/`); the publishers' prices were not stated on any page read; SPP's letter matters only if the ERW sells anything; a commercial line in brackets in the NYISO, PJM and MISO letters.
- **Meanwhile:** held; the tables they cover stay "license needed".
- **What each answer changes:** sent, the held tables may become public on an answer; held, they stay greyed on every page.
- **Recommended ruling:** send NYISO's, PJM's and MISO's with the commercial line struck, and hold SPP's. Reason: the site sells nothing today, and a narrower ask is likelier to be granted.

### 6. `nyiso_load_queue`: public or internal

- **Raised by:** sessions 375 and 410; notes `morning_2026-10-21_day.md` item 3, `morning_2026-10-21_night.md` item 5, `note_2026-10-21_day_data.md` item 7.
- **Evidence:** the header says "License: public, with a caution" and `coverage.csv` says public; the registry row `nyiso:load_queue` (Samuel's ruling of 7 October) says internal; `license_status.csv` holds it.
- **Meanwhile:** coverage kept public as main had it (375).
- **What each answer changes:** internal: coverage, `license_status.csv` and `site/data/license_status.json` lose it (41 to 40 license-needed tables), `test_session207` and `test_session275` follow; public: the registry row changes.
- **Recommended ruling:** internal, with the header brought to agree. Reason: the 7 October ruling is the only record a person made, and NYISO's terms are among those the letters of item 5 ask about.

### 7. The loader's guard: compare values when the stamps differ

- **Raised by:** sessions 374 and 384 (part c); notes `morning_2026-10-21_day.md` item 4, `morning_2026-10-21_night.md` item 3, `note_2026-10-21_day_data.md` item 5.
- **Evidence:** 31 tables refused as "older than the live copy" though the three read were equal value for value (374); 384 drafts `same_values()` with a 2,000,000-row ceiling.
- **Meanwhile:** `load.py` not changed; no `--allow-older` used.
- **What each answer changes:** the 31 load as unchanged instead of failing the load; a copy that differs is still refused; one whole-table read for each table with older stamps.
- **Recommended ruling:** adopt the draft, with both sides sorted by key before the hash and the live stamps kept. Reason: it removes a false failure without letting a different copy through.

### 8. `ferc_eqr_contracts`: 452 rows fewer on the data machine than live

- **Raised by:** session 374; notes `morning_2026-10-21_day.md` item 4, `morning_2026-10-21_night.md` item 3.
- **Evidence:** the data machine's copy has 452 rows fewer than the live set, which GitHub's run built.
- **Meanwhile:** not loaded; still refused under item 7's draft.
- **What each answer changes:** whichever copy is ruled right is loaded; the other is rebuilt.
- **Recommended ruling:** a data machine session compares the two copies row by row from the archive before either is loaded. Reason: the live copy may be right, and a load cannot be undone except from the archive.

### 9. `restore_tables.py`'s note as a restored table's first header line

- **Raised by:** session 375; notes `morning_2026-10-21_day.md` item 6, `morning_2026-10-21_night.md` item 5, `note_2026-10-21_day_data.md` item 7.
- **Evidence:** `release_v1.py` and the uploader read the first header line as the table's description; 63 tables would take the restore's note as their description after a whole rewrite.
- **Meanwhile:** the release package was spliced, not rewritten.
- **What each answer changes:** the note last: descriptions stay the source's; as is: every restored table's description is the note.
- **Recommended ruling:** write the note last. Reason: the description is the source's words, and the note is provenance, which the run log also holds.

### 10. 2021's four summer intervals from ERCOT (an information request)

- **Raised by:** sessions 354, 359 and 379; note `morning_2026-10-21.md` item 7, `morning_2026-10-21_day.md` item 6.
- **Evidence:** not found in the Wayback Machine (379, 6 requests); ERCOT's workbook for 2021 would need a request.
- **Meanwhile:** the year is left out of `ercot_4cp_intervals`.
- **What each answer changes:** asked, the four-peak saving on the datacenter page gains a year; not asked, it keeps the years it holds.
- **Recommended ruling:** leave 2021 out. Reason: one more year changes no default figure, and a request costs a person's time.

### 11. Summer 2026's four intervals, and NYISO's ICAP spot rows

- **Raised by:** session 354; note `review_2026-10-20_code.md` (part for 351 to 356) item 4.
- **Evidence:** the datacenter page counts ERCOT's four peaks from `ercot_4cp_intervals`, newest summer held 2025; NYISO's ICAP rows are in an internal table only.
- **Meanwhile:** 2025 used; capacity outside ERCOT is words.
- **What each answer changes:** summer 2026 moves the four-peak figure when ERCOT posts it; a public ICAP table lets the page show NYISO's capacity cost.
- **Recommended ruling:** add summer 2026 when ERCOT posts it, and leave ICAP internal. Reason: ERCOT's intervals are public; the one table of auction results is internal (the note's decision 6 for 351 to 356).

### 12. ERCOT's settlement point list (NP4-160-SG) as a new source

- **Raised by:** session 358; note `morning_2026-10-21.md` item 4.
- **Evidence:** each node's basis is taken against one hub; the list gives each point's load zone and hub; coordinates are not in it.
- **Meanwhile:** the basis is against the hub the table names.
- **What each answer changes:** each node's basis against its own zonal hub, on the generator's node band (session 353) and the storage nodes' spread (355).
- **Recommended ruling:** add the list, without coordinates for now. Reason: it is ERCOT's own public file and makes every node's basis exact.

### 13. An ERCOT Data Access Portal account

- **Raised by:** session 358; note `morning_2026-10-21.md` item 4.
- **Evidence:** today the ERW keeps what ERCOT's seven-day list shows, daily (376: real time held 28 September to 19 October, 22 days).
- **Meanwhile:** the daily keep.
- **What each answer changes:** a signed-in account gives the history of real-time node prices; it adds an account's terms to the license record.
- **Recommended ruling:** hold until twelve months of the daily keep exist or a page needs earlier history. Reason: the daily keep fills the gap at no cost, and an account brings terms to read.

### 14. `sync.py`'s "ahead" for a snapshot table

- **Raised by:** session 363; note `morning_2026-10-21.md` item 5.
- **Evidence:** judged by row count at an equal newest timestamp, `sync.py` called an older snapshot ahead.
- **Meanwhile:** none recorded.
- **What each answer changes:** comparing by the archive's row hashes (as `warehouse/archive/prove.py` does) ends false "ahead" results at the cost of a hash read.
- **Recommended ruling:** compare by row hashes. Reason: the archive already holds them, and a false "ahead" keeps an older copy in place.

### 15. The four ledger calls of 15 October into the live ledger

- **Raised by:** session 362; note `morning_2026-10-21.md` item 5.
- **Evidence:** the calls of 15 October 16:22 UTC are in the archive, not in the live ledger.
- **Meanwhile:** not loaded.
- **What each answer changes:** the live ledger's day total for 15 October rises by those calls.
- **Recommended ruling:** load them. Reason: the ledger is the record of model spend and should be whole.

### 16. The data machine's rebuilds and loads

- **Raised by:** sessions 370 (`battery_scenario_steps.json` behind CAISO's three Novembers), 381 item 7 (`eia_annual_crosscheck_ba` into the live set), 382 (the board's ERCOT tiles: day-ahead 43.95 on 15 October against the week table's 30.98 on 20 October), 403 (`ercot_peak_premium_annual` and `_monthly`, not computed since 29 September), 404 (`eia930_demand_growth`, not rebuilt since 5 October), 405 (`iso_queue_statistics` not in the live catalogue); notes `review_2026-10-20_day_code.md` item 4, `review_2026-10-21_night_code.md` item 4.
- **Evidence:** each page says its table is stale or absent; none is a ruling in its report's words, but each waits.
- **Meanwhile:** the pages say what is missing.
- **What each answer changes:** each page shows current figures after its rebuild.
- **Recommended ruling:** give all six to the data machine's next chain as one session. Reason: none needs a decision, only a run under the data lock.

### 17. Louisiana Revenue's terms, and so whether `impact_tax_rules` is held

- **Raised by:** session 388; note `note_2026-10-21_day_data.md` item 4.
- **Evidence:** the Louisiana Department of Revenue's page restricts reproduction; the Legislature's page states no terms; 4 requests of 16.
- **Meanwhile:** the verdict drafted, not written.
- **What each answer changes:** written, `impact_tax_rules` joins the license-needed list (41 to 42) and is held on `/impact`.
- **Recommended ruling:** write the verdict and hold the table. Reason: the publisher's own words restrict reproduction, and the rules can be cited by their statute instead.

### 18. A second page read for publishers whose one read gave no sentence

- **Raised by:** session 388; note `note_2026-10-21_day_data.md` item 4.
- **Evidence:** FERC (8 tables), the PUC of Texas and the Federal Register (5), four commissions (2), CME (1); `license_read.py` reads a publisher once.
- **Meanwhile:** the tables stay unsettled.
- **What each answer changes:** a named exception for these publishers could settle up to 16 tables.
- **Recommended ruling:** allow one second page for each, named in the record. Reason: a public agency's terms are usually on a second page, and the rule exists to bound requests, which one more each keeps bounded.

### 19. The impact pack's ten questions

- **Raised by:** session 366; notes `review_2026-10-20_day_code.md` item 5, `review_2026-10-20_third.md` "What waits for Samuel" item 1.
- **Evidence:** `docs/reviews/packs/impact.md`, part 9: the four tax publishers' terms; pulling the property-tax statutes (TX chapters 312 and 313, LA ITEP, NM IRB); a default life; severance on a gas plant's fuel; utility PV as JEDI's Utility option; the wind release; one dollar year; the local content lever exact or approximate; more JEDI models; IMPLAN's multipliers.
- **Meanwhile:** the choices of sessions 345 to 347 stand (the third machine's note).
- **What each answer changes:** each changes `/impact`'s inputs or figures.
- **Recommended ruling:** rule the terms and the statutes pull first and leave the rest as the sessions chose. Reason: the license questions gate what the page may show; the others are defaults a reader can change.

### 20. ERCOT's withdrawn positions from its past GIS reports

- **Raised by:** session 367 (naming 348); note `review_2026-10-20_third.md` item 3.
- **Evidence:** the withdrawal rate on the map's Queues tab is by count from present reports; withdrawn positions need ERCOT's past monthly GIS reports.
- **Meanwhile:** not pulled.
- **What each answer changes:** a withdrawal rate over time for ERCOT.
- **Recommended ruling:** hold. Reason: the Queues tab is in review, and the pull has no page waiting for it.

## A ruling on a figure

### 21. The node in the generator's headline, and the real-time basis

- **Raised by:** session 353; note `review_2026-10-20_code.md` (351 to 356) item 1.
- **Evidence:** the node is priced on the day-ahead basis on scenarios A and B only; real-time basis held from September 2026 only.
- **Meanwhile:** the headline stays at the hub.
- **What each answer changes:** one number for "my plant at my node" in the headline; the real-time basis once twelve months are held.
- **Recommended ruling:** keep the headline at the hub and the node beside it; revisit the real-time basis at twelve months. Reason: the hub is what the page's checks trace, and the node choice is a reader's input.

### 22. Newey-West in a card's sentence

- **Raised by:** sessions 355 and 361; notes `review_2026-10-20_code.md` (351 to 356) item 2, `morning_2026-10-21.md` item 6.
- **Evidence:** HC1 is the card's figure; Newey-West beside it in the fold; none of the nine cards has a p moved across 0.05 today.
- **Meanwhile:** Newey-West in the fold only.
- **What each answer changes:** where it moves a p across 0.05, the card's sentence would say so.
- **Recommended ruling:** state it in the sentence where it moves a p across 0.05. Reason: a reader should not draw a verdict that the robust error does not support, and today no card changes.

### 23. The step flag: a flag, or out of the review list

- **Raised by:** sessions 355 and 361; notes `review_2026-10-20_code.md` (351 to 356) item 2, `morning_2026-10-21.md` item 6.
- **Evidence:** a hunt draft with a step in its series is flagged.
- **Meanwhile:** a flag.
- **What each answer changes:** out of the list, the reviewer sees fewer drafts and may miss a real step.
- **Recommended ruling:** keep it a flag. Reason: a person reviews every draft, and a flag loses nothing.

### 24. Two figures for one thing: one cent at a hub other than the main one

- **Raised by:** session 382; note `review_2026-10-21_night_code.md` item 3.
- **Evidence:** at West the generator's headline capture price is 23.86 (the capture file) and its spans table 23.85 (the hub model); the headline revenue there carries no check key.
- **Meanwhile:** left.
- **What each answer changes:** (a) one source for both; (b) a key on the hub revenue; (c) as is.
- **Recommended ruling:** (a), one source for both, with its key. Reason: a reader who sees two figures for one quantity loses trust in both.

### 25. CAISO's events in the generator's leave-outs

- **Raised by:** session 357; note `morning_2026-10-21.md` item 7.
- **Evidence:** the snapshot holds daily figures for ERCOT's three events only; adding CAISO's means rebuilding `warehouse/derived/merchant_revenue.py`'s snapshot.
- **Meanwhile:** ERCOT's three only.
- **What each answer changes:** the page's input changes for CAISO.
- **Recommended ruling:** add them at the snapshot's next rebuild. Reason: the page offers CAISO, and a leave-out that covers one grid only reads as an omission.

### 26. Screening interchange hours for impossible values

- **Raised by:** session 360 (the Grid pack's item 10).
- **Evidence:** SPP's two hours; the adjusted series would draw the same figures.
- **Meanwhile:** not screened.
- **What each answer changes:** nothing on today's figures.
- **Recommended ruling:** screen and flag, not drop. Reason: the figures do not move, and a flag keeps the source's values.

### 27. `check-battery-scenarios`' CAISO 2-hour case

- **Raised by:** session 352; note `review_2026-10-20_code.md` (351 to 356) item 3.
- **Evidence:** fails on production since before session 352.
- **Meanwhile:** left failing.
- **What each answer changes:** either the check or the page changes.
- **Recommended ruling:** give it to the next battery session to find which is wrong. Reason: a failing check that everyone passes over hides the next failure.

### 28. A row against Samuel's thesis as "against published figures"

- **Raised by:** session 381 item 6; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** three of Research's four cross-check rows are against the thesis.
- **Meanwhile:** counted as written in `docs/methods/automated_analysis_findings.md`.
- **What each answer changes:** not counted, Research has one published-figure row.
- **Recommended ruling:** do not count them. Reason: the thesis is the project's own work, not an outside publication.

### 29. The map's default view: CAISO or a grid with full recent years

- **Raised by:** session 405.
- **Evidence:** CAISO's newest complete entry year held is 2023, with 4 positions, so the headline compares 4 against 1999's 1.
- **Meanwhile:** CAISO kept.
- **What each answer changes:** SPP or ERCOT as default gives a headline on full years.
- **Recommended ruling:** default to ERCOT. Reason: a headline of 4 against 1 says little; ERCOT's recent years are full.

### 30. `/map`'s floor of 1 checked number

- **Raised by:** session 405.
- **Evidence:** its one number is held by the license hold since 21 October, so the floor fails.
- **Meanwhile:** left to the landing.
- **What each answer changes:** floor 0: the check passes with nothing checked.
- **Recommended ruling:** floor 0 while the hold stands, with the reason written beside it. Reason: the hold is a ruling, and the floor's failure says nothing new.

### 31. Whether a figure's label counts as naming it

- **Raised by:** session 409.
- **Evidence:** `check-methods`' rule 3 counts the table and variable only.
- **Meanwhile:** table and variable only.
- **What each answer changes:** counted, more figures pass without a method line.
- **Recommended ruling:** keep table and variable only. Reason: a label is the page's words; the table and variable are what a reader can find.

### 32. Monthly trends whose two ends are different seasons

- **Raised by:** session 420, ruling 1.
- **Evidence:** findings 1, 2 and 5 of the hunt of 20 October.
- **Meanwhile:** published with a caveat sentence on the branch.
- **What each answer changes:** same-month only: the three are redrawn.
- **Recommended ruling:** same-month comparisons only. Reason: a seasonal difference read as a trend is a fault the caveat does not undo.

### 33. A record set in 2024 as news

- **Raised by:** session 420, ruling 2.
- **Evidence:** finding 6, from LBNL's 2026 edition.
- **Meanwhile:** kept among the ten.
- **What each answer changes:** dropped from the captions.
- **Recommended ruling:** keep it, dated "2024" in the caption. Reason: the edition is new, and the year written makes it honest.

### 34. The two shown-before findings again

- **Raised by:** session 420, ruling 3.
- **Evidence:** findings 9 and 10 were shown before.
- **Meanwhile:** kept in this form.
- **What each answer changes:** dropped, the hunt has eight.
- **Recommended ruling:** only with a new figure. Reason: a repeat in the same form adds nothing for a reader.

## A public page

### 35. On a phone the first figure is two and a half screens down

- **Raised by:** session 382; note `review_2026-10-21_night_code.md` item 3.
- **Evidence:** 2,140 to 2,375 px at 390 px wide on the generator and battery pages, below the whole form (the board: 319 px).
- **Meanwhile:** left.
- **What each answer changes:** (a) summary and headline above the form at phone width; (b) the form folded; (c) as is.
- **Recommended ruling:** (a). Reason: the answer first is the project's voice, and the form stays whole below it.

### 36. Who walks the paths, and how an outside reader sees pages in review

- **Raised by:** session 382 (the On.Energy walkthrough; the traders' walk); note `review_2026-10-21_night_code.md` item 3.
- **Evidence:** every page is in review (CLAUDE.md, since session 166); the list is in `docs/reviews/trader-path.md`.
- **Meanwhile:** no walk scheduled.
- **What each answer changes:** an internal-view link for each outside reader, or chosen pages set live.
- **Recommended ruling:** give each outside reader the internal view for a dated window, and set nothing live. Reason: it keeps the freeze rules unchanged and is undone by ending the window.

### 37. Research's `.py` downloads do not run for a reader

- **Raised by:** session 381 item 2; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** they need `findings_common.py` and the warehouse's tables; the new mirror (`erw_2026_research_replication.py`) reproduces 304 of 304 figures from the cards' CSVs.
- **Meanwhile:** unchanged.
- **What each answer changes:** (a) ship the helper and say what is needed; (b) replace with the mirror; (c) keep and point to the mirror.
- **Recommended ruling:** (b), the mirror as the download. Reason: it runs for a reader from what the page offers.

### 38. Links to the replications from `/research` and `/grid`

- **Raised by:** session 381 item 3; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** the replication files exist; neither page links them.
- **Meanwhile:** none.
- **What each answer changes:** two page changes.
- **Recommended ruling:** link them. Reason: a replication no reader can find replicates nothing.

### 39. A decisions block on `/research`

- **Raised by:** session 381 item 4; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** the Grid page states the rulings of 18 October; Research's of 19 October (1b, 2a, 3a, 4b, 5b, 6a) are not on its page.
- **Meanwhile:** none.
- **What each answer changes:** one block on the page.
- **Recommended ruling:** add it, as the Grid's. Reason: the two pages should state their rulings alike.

### 40. "Checked against" lines on `/grid` and `/research`

- **Raised by:** session 381 item 5; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** the three decision pages count their cross-checks; `docs/methods/grid_network.md` (11 rows) and `automated_analysis_findings.md` (4 rows) now hold theirs.
- **Meanwhile:** none on the page.
- **What each answer changes:** a line on each page.
- **Recommended ruling:** add them, counting only outside publications (item 28). Reason: consistency with the decision pages.

### 41. Question 5's answer on the Grid page

- **Raised by:** session 381 item 7; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** the pack says it is done; the live set does not hold `eia_annual_crosscheck_ba` (its load is in item 16).
- **Meanwhile:** not shown.
- **What each answer changes:** the page shows the answer after the load.
- **Recommended ruling:** show it once item 16's load is made. Reason: the work is done and only the load waits.

### 42. Whether "Automated Analysis in its final form" is met

- **Raised by:** session 381 item 8; note `review_2026-10-21_night_code.md` item 2.
- **Evidence:** session 315's form.
- **Meanwhile:** treated as not signed.
- **What each answer changes:** met, roadmap item 2 closes for Research.
- **Recommended ruling:** not yet: met after items 37 to 40. Reason: a reader cannot yet rerun or find the replication.

### 43. Pages drawn twice: the explorers and the tool pages

- **Raised by:** sessions 403 (the ERCOT peak premium: the `/prices` tab and `/explore/ercot-peak-premium`), 404 (demand growth: `/demand` and `/explore/demand-growth`) and 405 (queues: `/map?tab=queues`, `/queues`, `/explore/interconnection`). Merged: the three ask one question of three pages.
- **Evidence:** each figure is drawn at two or three addresses.
- **Meanwhile:** all kept.
- **What each answer changes:** (a) keep all; (b) the tool page links to the explorer and draws less; (c) redirect old addresses.
- **Recommended ruling:** (b) for all three. Reason: one drawing a figure keeps one set of checks, and no address breaks.

### 44. The shared line chart writes a year twice

- **Raised by:** sessions 404 and 405.
- **Evidence:** `components/TimeChart.tsx` with few years (ERCOT's median wait, 2018 to 2025: "2020" twice).
- **Meanwhile:** the demand page moved to bars.
- **What each answer changes:** a fix touches every page that draws years.
- **Recommended ruling:** fix it in the shared chart in one session, with `check-values` over every page after. Reason: the fault is the component's.

### 45. `eia930_demand_growth` held for review in the live set

- **Raised by:** session 404.
- **Evidence:** its two pages offer no CSV.
- **Meanwhile:** held.
- **What each answer changes:** off `review_hold`: the home page's counts of public tables and rows move by one table.
- **Recommended ruling:** keep it held until `/demand` opens. Reason: no visitor sees either page today.

### 46. The empty `ba` and `event` columns of every download

- **Raised by:** session 368; note `review_2026-10-20_day_code.md` item 3.
- **Evidence:** the live set holds them; the CSV has had them empty since session 21; `event_window_daily`'s rows cannot tell their events apart. A one-line patch waits (`runs/chain_oct20d/s368/route_ba_event.patch`); main's `site/app/api/download/route.ts` still lists no `ba` or `event` in its series columns (read 21 October).
- **Meanwhile:** unchanged.
- **What each answer changes:** the bytes of every table that carries either column.
- **Recommended ruling:** apply the patch. Reason: a download that cannot tell its rows apart is wrong, and no page is live.

### 47. The 500,000-row limit of a download

- **Raised by:** session 368; note `review_2026-10-20_day_code.md` item 3.
- **Evidence:** `MAX_ROWS = 500_000` in the route and `/data`'s sentence agree (a test pins it).
- **Meanwhile:** kept.
- **What each answer changes:** a larger table offered whole, at more database load.
- **Recommended ruling:** keep 500,000 and point larger tables to Redivis. Reason: the database's timeouts (item 2) argue against larger reads.

### 48. A Method link on pages that have none

- **Raised by:** session 409.
- **Evidence:** the home page, `/data`, the problem sets, a price's own page, the research cards and the Roundup have none; `check-methods` passes them by.
- **Meanwhile:** none.
- **What each answer changes:** six kinds of page gain a link.
- **Recommended ruling:** add one wherever the page shows a warehouse figure. Reason: every number traces to its source (CLAUDE.md rule 5).

### 49. The Digest's headlines without a permission

- **Raised by:** session 402.
- **Evidence:** the Digest's stories are held with `news_index` since 21 October; the headlines are the ERW's own words from the outlets' titles.
- **Meanwhile:** held.
- **What each answer changes:** shown, the Digest page has its stories again.
- **Recommended ruling:** show the ERW's own headline with the outlet's name and link, no outlet text. Reason: the words are the ERW's, and the Digest is one of the two periodicals that must be right first (Samuel's ruling of 21 October).

### 50. The hold's gaps: the home page's Digest stories, the Roundup and the e-mailed Digest

- **Raised by:** session 402.
- **Evidence:** the home page's five stories (`app/page.tsx`, from `docs/digest/latest.md`) and `/roundup` are not held; `warehouse/news/email_digest.py` carries NYISO's and ISO-NE's figures and the stories.
- **Meanwhile:** the hold of 21 October is the site's only.
- **What each answer changes:** the same hold everywhere the same content appears.
- **Recommended ruling:** apply the hold in all three. Reason: a hold that applies on one page only holds nothing.

### 51. Eight weekdays without a Digest

- **Raised by:** session 402.
- **Evidence:** 29 and 30 September, 1, 5, 6, 15, 16 and 19 October: a date-parse failure (30 September), duplicate items (5 and 6 October), a local run recorded ok but never committed (29 September), no run recorded for 1, 15, 16 and 19 October.
- **Meanwhile:** none.
- **What each answer changes:** an alert for a weekday with no Digest by a set hour.
- **Recommended ruling:** add that alert to the alert policy (item 54). Reason: a missed issue went unseen eight times.

### 52. `/data` and the hold lists

- **Raised by:** session 410.
- **Evidence:** 80 public tables are not on `/data` (48 under `catalogue_hold`, 32 under `review_hold`).
- **Meanwhile:** the page shows what the live catalogue holds.
- **What each answer changes:** (a) list them marked held or in review, no download; (b) as is; (c) release them one by one.
- **Recommended ruling:** (a). Reason: a reader should see what exists and why it cannot be downloaded yet.

## None of the four

### 53. The open security items

- **Raised by:** session 371 (nine items and S3); note `review_2026-10-20_day_code.md` item 2 (eight open, H3 closed in code).
- **Evidence:** `docs/security.md`, "What needs Samuel, with the choice": H1 (retire the old link, then rotate the token), H3 (`SUPABASE_SERVICE_KEY` on Vercel), M6 default privileges, M7 Python packages, L4 the cookie's lifetime, L7 `search_path`, L8 Supabase Auth sign-ups (on), L9 the linter's packages; S3, three internal checks that send the real token in an address.
- **Meanwhile:** each choice written out; S3's checks run on a local build only.
- **What each answer changes:** each closes one finding.
- **Recommended ruling:** H1 and L8 first (retire the link, rotate the token, turn sign-ups off), then the rest as written. Reason: those two are reachable from outside; the others are hardening.

### 54. "One alert policy" in `docs/machines.md`

- **Raised by:** session 377; notes `morning_2026-10-21_day.md` item 5, `morning_2026-10-21_night.md` item 5, `note_2026-10-21_day_data.md` item 7.
- **Evidence:** the draft gathers the alarms into one list.
- **Meanwhile:** a draft, not in force.
- **What each answer changes:** in force, every machine follows one list.
- **Recommended ruling:** in force as written, with item 51's alert added. Reason: it states what already runs.

### 55. `reason_of` names one failure a step

- **Raised by:** session 377 (session 202's ruling 12, still open).
- **Evidence:** it hid two to nine failing tests a day from 6 to 12 October.
- **Meanwhile:** unchanged.
- **What each answer changes:** every failure named in the health row.
- **Recommended ruling:** name every failure, capped at a count with "and N more". Reason: a hidden failure is the fault the health row exists to show.

### 56. The streak, the daily task's window and the reaper

- **Raised by:** sessions 372 (a chain restarting a job the memory reaper stopped), 384 (the daily task with no console window) and 387 (whether a job far below its expected count ends a green day); notes `review_2026-10-20_day_code.md` item 1, `morning_2026-10-21_night.md` item 4, `note_2026-10-21_day_data.md` items 5 and 6. Merged: three settings of the machines' running, each the owner's.
- **Evidence:** the daily run of 20 October ended when its console window closed (0xC000013A) and held the lock until 20:00 UTC (384); the streak did not see a six-hour gap (387); the reaper stopped a chain's job (372).
- **Meanwhile:** `lock.py` releases on a console close (384); no task setting changed.
- **What each answer changes:** "Run whether user is logged on or not" takes the close out of reach; a job under half its expected count ends the streak; `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` lets a chain restart a job.
- **Recommended ruling:** run the task with no window, and count a job under half its runs as a missing day; leave the reaper on. Reason: the first two close faults seen this week; the reaper protects the machine's memory.

### 57. The records' smaller questions

- **Raised by:** sessions 409 (the step-by-step notes or the Method notes carry the figure lines), 410 (the consolidated tables named in the registry's rows), 413 (Enverus, Ask the Grid's, Grid Status's and Yes Energy's terms, and `docs/positioning.md`), 414 (the ledger's groups and its rank rule) and 420 (the fonts in `warehouse/analysis/fonts/`, 1.6 MB, OFL; the ten findings' Stata checks); 381 item 1 (the five signatures and a sign-off block). Merged as items no answer of which changes a figure or a page.
- **Evidence:** each in its report.
- **Meanwhile:** each as the session left it.
- **What each answer changes:** records and documents only.
- **Recommended ruling:** take each as its session chose, and read the competitors' terms by hand before the review is quoted outside the project. Reason: none blocks a page, and the terms are the one that could.

## Already answered (not counted in the 57)

- **Sessions 406 and 407's ten items** (issue 1's question, title, the sentence on other sources, the co-optimization line, the newsletter's reader; the first three posts, posting while in review, the address, the source line, hashtags): answered by Samuel's ruling of 21 October, no newsletter of any kind and the drafts unused.
- **Restoring the data machine from the archive** (session 362; `morning_2026-10-21.md` item 2) and **`battery_stack_monthly` older than the live set** (357): done by session 373 (71 tables restored).
- **The live set's sources check** (`morning_2026-10-21.md` item 3): green since session 374.
- **The CLAUDE.md patch** (371): main's `CLAUDE.md` carries session 371's commit `be202c6f` (the Schedules row, Running things, `scripts/`, `queue/` and `exports/`).
- **The landing of 367 to 382** (372, 383): main holds `bb49c9e0`, "Merge task/381-382: checks passed".
