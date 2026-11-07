# Session 3400 report: the next file and the ground of the Attention and Friction indices (chain 202)

6 November 2026, 19:08 to about 19:30 UTC, on lab-desktop, fourth window, chain 202 (`queue/done/202-day-6-november-desktop-window4-attention.md`), unattended, Fable 5.1. Model spend USD 0 (no API call). Pulls: none.

## Read these first

- **Session numbers.** No session at or above 3400 exists on origin's main (the newest report there is 3231), on any remote branch's `archive/sessions/`, or in any worktree's branch name; the third window's chain 200 runs from 3300. This chain holds 3400 to 3419; file 203 says its chain starts at 3420.
- **Queue files.** The prompt is saved word for word as `queue/done/202-day-6-november-desktop-window4-attention.md` (200 and 201 were taken by the third window's chain minutes before: `queue/done/200-day-6-november-desktop-window3-companies.md`, `queue/next/201-day-7-november-desktop-window3-continued.md`). The next file is `queue/next/203-day-7-november-desktop-window4-continued.md` (`machine: lab-desktop-window4`, twelve sessions). Each was committed alone and pushed to main (`be2ffa978`, `6f24fda18`).
- **The branch.** `wip/3400-attention` in the worktree `C:\Users\Shared\Documents\erw-3400`, cut from `origin/main` at `6f24fda18`. The worktree has no `.venv` and no tables: every python command names the main checkout's interpreter, and a trial reads the main checkout's `warehouse/output` through `--in-dir`.
- **Precheck passed** (lab-desktop on duty for this chain until 2026-11-07 11:08 UTC; it was on duty for the third window's session 3300, which runs beside this one). The data lock is free. No `REVIEW_FREEZE` file: a deploy with rule 8's snapshots is allowed.

## The ground

**The corpus** (`news_stories`, read 2026-11-05T23:26 UTC):

| Fact | Value |
|---|---|
| Stories | 26,438 |
| First and last publish time | 2025-01-01 to 2026-12-01 (two feed-dated stories after today, kept as given) |
| Weeks held (Monday to Sunday) | 99 |
| Stories a week, 2025-01 to 2026-09 | 64 to 317, median about 95 |
| Stories a week from 2026-09-21 | 1,830 to 3,146 (the feeds grew in late September 2026) |
| Scored (significance and sector set) | 69.5 percent |
| Text held a story | title (median 63 characters) and summary (median 77, 90th percentile 150); no body |
| `parties` filled | 44.5 percent; `entity_ids` never |
| `region` | free text: US 4,931, global 4,813, "United States" 663, then countries and two states (California 324, Texas 316) |
| Outlets | 80; Reuters, the Financial Times, Bloomberg and the WSJ hold 19,384 of the rows |

- **The step in late September 2026** means a raw count of stories is not comparable across the corpus. The Attention Index will be a share of the week's stories, with the raw count beside it, and the method note will say so.
- **The scorer's `sector`** has twenty values (`other` 8,078; `policy` 1,576; `oil` 1,214; `geopolitics` 998; `datacenter_power` 903; `nuclear` 425; `lng` 422; `gas` 415; `storage` 304; `renewables` 247; `transmission` 161, among them) and is empty for the 30.5 percent of stories not scored. The classifier will set the index's seven sectors itself (datacenters, transmission, gas, nuclear, solar and wind, storage, oil and LNG) from the text, so that an unscored story is counted, and the scorer's sector stays as a cross-check.
- **Places.** No story carries a state field; `region` names a state in a few hundred rows. The classifier will read the state, and the county, city or metro where the text names one.

**The policy tables:** `policy_actions` 2,020 rows (notices 1,399, news releases 268, rules 198, proposed rules 155; FERC 935, NRC 499, DOE 185, EPA 182; `states` filled 59 percent, `place_words` 9 percent); `policy_reads` 408 rows (`affected_states` filled 72 percent; `direction_buildout` unclear 221, up 82, none 25). **The datacenter and deal records:** `datacenter_projects` 163 rows (state 32 percent, county 5 percent; announced 45, under construction 13, cancelled 7, permitted 5); `energy_deals` 529 rows (state 10 percent).

**The machine.** Disk 247 GB free of 476. Memory 4.4 GB free of 16.0 with three other Claude Code windows open: every build goes through `scripts/buildlock.py`. The Digest's issues (`docs/digest/<date>.md`, 17 held) each state "from N scored stories", the figure the cross-check of session 5 reads.

## What the infrastructure settles

- **Shape and names.** The weekly indices are `series` tables; the validator requires a three-part name for a series table (`NAME_RE`), so they are `attention_index_weekly` and `friction_index_weekly`, the entity `attention:<sector>:<geo>` (the national rows `attention:<sector>:US`), `geo` the ISO 3166-2 code, `freq` `P1W`, units from the closed vocabulary (`count`, `pct`, `ratio`): no new unit, no branch validator. The link table is an `events` table, `attention_story_links`, one row a classified story.
- **License.** The coverage builder makes a table "Derived from:" the internal `news_stories` internal, unless the owner's list `PUBLIC_SELECTIONS` names it. `news_index` is public by the other route: a "Built from" line and a "License: public" line, with no outlet text. The three tables follow `news_index` word for word: links, metadata and the model's own fields, no title or summary.
- **Tier.** `model_extracted` (the classification is a model's), added to `TIER_RULES` and `SECTOR_RULES` (`news;datacenters`) in `build_coverage.py`.
- **The writer** runs in the main checkout under `runs/c202/write_table.sh` (chain 147's, `DIR=derived`), which waits for the data lock, runs the writer, the validator, `build_coverage.py --only`, the archive, and hands the metadata patch to the branch.
- **The page** reads a JSON the writer leaves in `site/data/attention.json` (as the EV game and the large-load page do), and offers the downloads through `TableDownloads` once the three tables are in `live_set.yaml` and loaded. The map uses `us-atlas/states-albers-10m.json` through ECharts as `/map` does; the time charts use `components/tool/SeriesChart.tsx`.

## Decisions made without you

- **Queue numbers 202 and 203**, the first free at or above 199 after the third window took 200 and 201.
- **Session numbers 3400 to 3419** for this chain, file 203's from 3420.
- **Three-part table names** (`attention_index_weekly`, `friction_index_weekly`) in place of the prompt's `attention_weekly` and `friction_weekly`, which the validator's name rule refuses for a series table; the prompt's names stand in the method note as the indices' names.
- **A third table,** `attention_story_links`, as the link table the prompt asks for.
- **Public by the `news_index` route** ("Built from", "License: public", no outlet text), not by adding the tables to `PUBLIC_SELECTIONS`.
- **The index as a share of the week's stories,** because the feeds grew twenty-fold in September 2026.

## For Samuel's ruling

- Nothing yet. The owner's two estimates come from sessions 9 and 10.

## Next

Session 3401: the classification's schema and prompt, the 200-story hand-labeled set in `tests/fixtures/attention/`, the test, the accuracy by class, the cost per thousand stories, the cap.
