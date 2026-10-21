# Chain of 21 to 22 October 2026, night: sessions 510 to 515, data machine (lab-desktop), unattended: more public sources

machine: data

Written by session 489, the landing session of `queue/done/022-evening-21-october-sources.md`, at the owner's instruction of 21 October 2026 ("write the next chain of new public sources and take it"; "if you run out of ruling-free work, probe another public source rather than idle"). Chain 022's probes run while the daily run held the lock were renumbered 507 to 509 at its landing (the code machine's chain 023 holds 497 to 506, and its old laptop's chain 024 holds 531 to 542), so this file holds 510 to 515. Each source session goes through the erw-add-connector skill (`.claude/skills/erw-add-connector/SKILL.md`):

- **its robots file and its terms are read first** (a terms page through `scripts/license_read.py` into `warehouse/metadata/license_reads.csv`, its verdict cut by code from the saved page);
- a probe;
- a trial with `--out-dir`;
- a cross-check against a table the ERW already holds;
- then the real run, the validator, `build_coverage.py --only`, the archive and a sector rule, with tests.

Default-neutral: no page's default figure moves, no ruling is made, nothing is released or uploaded on Redivis, and no letter is sent.

## Rules for every session

The rules of `queue/done/022-evening-21-october-sources.md` hold, word for word:

- the interpreter, the precheck, and unattended choices;
- wip/ on failure, and a memory stop restarted once in the foreground;
- every write under the data lock, with the scheduled daily run first;
- **no session waits for a time of day or for the lock, and none idles** (a session with nothing left that needs no ruling probes another public source);
- the database gate, and no table of this chain loaded into the live set;
- pulls only under a part's ceiling;
- nothing from a paused publisher, no access control worked around, and no key the ERW does not hold;
- **a robots file that disallows the path ends the source** (session 509: BLS);
- real data only (a source's imputed or estimated rows left out where it marks them, and named where it does not);
- model spend USD 0;
- no landing from 14:00 to 16:15 UTC;
- coverage rebuilt with `--only`;
- the deployment and snapshot rules, and the GitHub API's rate;
- `chain_queue.py next` pushed by hand;
- a script's `--help` read first;
- the main checkout on main;
- no em dashes;
- session 364's report form.

Chain 022's lessons are added:

- **A heredoc turns `\n` inside a Python string into a real newline**: write such code with the edit tool, or `chr(10)`.
- **A worktree has no `.erw/machine.json`**: never copy it there.
- **Before a session number is used, look for it** in `queue/next`, `queue/done` and every `wip/` and `task/` branch's `archive/sessions/` and `tests/` (chain 022 used 497 to 499 twice).
- **A new public table needs both holds until a person uploads it**: `catalogue_hold` in `warehouse/supabase/live_set.yaml` and `STORAGE_HELD` in `warehouse/redivis/release_v1.py`, with its rows added to `docs/redivis/release-v1/` (sessions 410 and 275's tests; see session 489's report).
- **Each table's metadata is carried as added lines**, from the data machine's main checkout to the branch, with a merge that keeps both sides' rows (session 494).

Read `docs/master_plan.md`, `docs/state/note_2026-10-22_sources_data.md` and the reports of sessions 483 to 496 and 507 to 509 first.

## Session 510: EIA-923, each plant's generation and fuel by year

Long end 2:00. Pulls: EIA's API v2, route `electricity/facility-fuel`, at most 40 requests, 3 seconds apart.

- **Annual only.** Every plant reports its year, but EIA imputes the monthly figures of plants outside its monthly sample, and the API carries no flag, so no monthly row is taken.
- 2020 to 2024, prime mover ALL, the variables `generation` (MWh) and `total-consumption-btu` (MMBtu, as TBtu).
- Session 496's probe found 29,761 rows for 2024 at prime mover ALL. 14 rows on its first page repeat (plant, fuel2002), so find the field that makes the key unique (fuelType, state) before writing.
- One series table, `eia923_plant_fuel_annual`.
- Cross-check: the plants' generation against `egrid_power_plants` (2023), and the U.S. total against EIA's.

## Session 511: EIA-861M, each utility's monthly sales

Long end 1:30. Pulls: EIA's EIA-861M page and its newest file (`https://www.eia.gov/electricity/data/eia861m/`), at most 6 requests.

- The monthly sales, revenue and customers by utility and state, as `eia861m_utility_sales_monthly`.
- Read by heading (session 495's lesson).
- EIA's imputed rows are left out where it marks them.
- Cross-check: the annual sum against `eia861_utility_sales`, for the latest year both hold.

## Session 512: DOE's Loan Programs Office portfolio

Long end 1:30. Pulls: `www.energy.gov` (its robots file was read in session 508), the LPO portfolio page and its project list, at most 10 requests. DOE's terms page goes through `license_read.py` first.

- Each loan or guarantee (project, borrower, technology, state, amount, status, date), as an events or entities table `doe_lpo_portfolio`.
- Cross-check against `energy_deals`, where the projects meet.

## Session 513: DOE's OE-417 disturbance reports, found again

Long end 1:00. Session 508 found the old host gone and the new form site a JavaScript application.

- Look for the current annual summaries on `www.energy.gov` (CESER) or among `doe417.pnnl.gov`'s published files, at most 8 requests; robots and terms first.
- If found: each event (date, area, type, demand lost, customers affected), as an events table `doe_oe417_disturbances`.
- If not: probe another public source (rule above), and say which.

## Session 514: FERC Form 714's respondents and their balancing authorities

Long end 1:00. Pulls: none, or at most 2. PUDL's stable `core_ferc714__respondent_id` is held in `warehouse/raw/ferc714_demand/`. PUDL's `core_eia__entity_utilities`, or the respondents' balancing-authority links if PUDL publishes them, may take the 2 requests.

- The respondents, as an entities table `ferc714_respondents`: FERC's CSV and XBRL ids, PUDL's id, the name and the EIA code. Then `ferc714_area_demand_*` can be read by name and joined to EIA-930's balancing authorities.
- Cross-check: each respondent with an EIA code against `eia930_all_demand`'s balancing authorities.

## Session 515: the note, the next file, and the queue

Long end 1:00.

1. `docs/state/note_2026-10-22_night_sources_data.md`, in session 364's form: what each session landed, pulls against ceilings, the sources probed and why any was not pulled, decisions, what waits for Samuel (highest value first), and the other machines.
2. The next file, before the queue step: at least six sessions of public sources the ERW does not yet hold, each with its robots file and terms first, numbered from the next free numbers (checked as above). Commit and push it to main on its own, with snapshots, and say so in the note.
3. Land this chain: merge origin/main, run the whole suite, `scripts/freeze.py status`, rule 8's snapshots and a task/ branch, not between 14:00 and 16:15 UTC.
4. Then `python scripts/chain_queue.py next`.
