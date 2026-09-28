# Session 27 report

Energy Research Warehouse (ERW), session 27, run 2026-09-28 (UTC). **API spend: USD 4.7056** (the two Thesis Builder re-runs of Task 1), under the USD 8 stop. Tasks 2 to 4 made no model call. No key was printed or committed. `origin/main` was fetched before the push and had nothing new.

Both rulings on session 26 are applied: both niches were re-run, and `energy_companies` is seeded from the deal tracker's parties.

## What was built

| Task | Result | API cost (USD) | Commit |
|---|---|---|---|
| 1 | Both Thesis Builder niches re-run with the span rules; the workbooks in `docs/thesis/` replaced; a comparison script; Sonnet 5.5 added to the price tables | 4.7056 | `e83d7e1` |
| 2 | `energy_companies` seeded from every party of `energy_deals` (`warehouse/companies/seed_from_deals.py`, in the daily run): 20 rows before, 284 after | 0 | `a1fef67` |
| 3 | The feedback log: `docs/feedback/README.md` (the demo protocol) and `docs/feedback/TEMPLATE.md`; a Feedback row in `docs/platform-tools.md` | 0 | `73499e8` |
| 4 | Briefing, chat spec, validator, coverage, live set, value check, OVERVIEW and STATUS, this report | 0 | final commit |

## Task 1: the two re-runs

### A price fix first

The first attempt stopped before any spend with `KeyError: 'claude-sonnet-5-5'`. The builder picks the newest Sonnet the API lists, and Sonnet 5.5 was not in the price tables.

I read its price from the pricing page (https://platform.claude.com/docs/en/about-claude/pricing.md, read 2026-09-28): USD 2 per million input tokens and USD 10 per million output tokens. I added it to the three `PRICES` tables:

- `warehouse/news/score.py`
- `warehouse/deals/extract.py`
- `warehouse/chat/ask.py`

The chat spec was then regenerated.

### Results

| Niche | Cost (USD) | Time | Calls | Searches | Companies | Capital rows | With a quoted investor | With a quoted date | With both |
|---|---|---|---|---|---|---|---|---|---|
| Subsurface heat mapping for geothermal | 2.2310 | 7.3 min | 26 | 37 | 7 | 11 (18 before) | 5 | 11 | 5 |
| Grid-scale battery storage software for merchant operators | 2.4746 | 8.1 min | 27 | 35 | 6 | 3 (8 before) | 1 | 0 | 0 |

The session 25 runs, for comparison: USD 2.41 and 21.3 minutes for geothermal; USD 2.40 and 11.5 minutes for battery storage software.

"Quoted" means the field survived the span rule: its quote is found in a cited passage. Fewer Capital rows is what that rule does. A round is kept only when its sources carry it, and an investor or date only when a passage says it.

### Where the runs disagree

`warehouse/thesis/eval/compare_runs.py OLD NEW` pairs Capital rows of the same company and the same round. The round name must match whole, and the dates must agree as far as both give one. The first version matched on the round's first word only. It paired a Series B with Series A rows and reported disagreements that were not there, so it was fixed and the pairs were checked by hand.

- **Geothermal:** 8 matched rounds. Every amount agrees except one: Bedrock Energy's Series A read "not confirmed" before and reads "$12 million" now. That is a gap filled, not two numbers in conflict.
- **Battery storage software:** 2 matched rounds (Tyba, FlexGen). The amounts agree.
- **Stage:** no disagreement in either niche. Geothermal has 7 of 7 companies in both runs. Battery storage software has 4 companies in both runs (6 now, 7 before).

The old workbooks are kept locally in `runs/s27_old/`, which is not in git.

## Task 2: tool 10 seeded from the deals

`warehouse/companies/seed_from_deals.py` reads `energy_deals`. Every buyer, seller and other party (split on ";") becomes a row of `energy_companies`, or is merged into the row that already holds it. Each such row gets:

- **Sector:** the sector of the deal's stories (`news_stories` through `story_ids`).
- **Niche tags:** `deal:<type>` and `tech:<technology>`.
- **Location:** the deal's state and country, noted as "where a deal is", because a deal's place is not always the company's.
- **Sources:** the deal's story links.
- **first_seen:** the earliest deal date.
- **Confidence:** the Thesis Builder's rule, with the independent sources counted as the distinct source domains. The clause ends "stage and raised not researched".

Nothing is invented. Description, founders, stage and raised are left blank, and the confidence note starts "from deals; not yet researched". `/companies` shows those words in the blank fields.

- **Merge:** on the normalized name (lower case; parentheses, punctuation and legal suffixes removed), plus the website domain when both rows have one. Deal-only rows are rebuilt on every run, and researched rows are never overwritten.
- **Before:** 17 rows at session 26's end, and 20 after Task 1's re-runs merged in, all with a description.
- **After:** 284 rows.
  - 19 are researched. Two researched rows were one company, "Tyba" and "Tyba (Tyba Energy Inc.)", and are now folded into one.
  - 265 come from deals.
  - One deal party merged into a researched row (Fervo Energy).
- **Share with a description:** 19 of 284, or **6.7%**.
- **Confidence of the deal rows:** 40 for 251 rows, 60 for 8, and 80 for 6.
- **Live set and site:**
  - Supabase holds 284 rows.
  - `/companies` renders all 284, with 0 duplicate anchors. `/deals` links to 266 distinct company anchors.
  - The page first failed to prerender with "Cannot read properties of null (reading 'replace')", because Supabase returns null for a blank field. `page.tsx` now turns nulls into empty strings.
- **The same fold in the builder:** `build.merge_companies` now merges on the same normalized name (`build.name_key`), so a later run cannot make the Tyba duplicate again.
- **Daily run and git:** the seeder runs in `run_daily.sh` after the deal extraction. `warehouse/output/energy_companies.csv` is now tracked in git, and the daily workflow commits it.

**A caution:** some deal parties are descriptions, not names. For example, "a Leading Frontier AI Lab" is a row. They are kept, because the deal says exactly that, but they are not companies anyone can look up.

## Task 3: the feedback log

`docs/feedback/README.md` sets out the demo protocol:

- **A 20-minute page order:**
  - `/` from minute 0 to 2
  - `/digest` from 2 to 5
  - `/markets` and `/prices` from 5 to 8
  - `/grid` from 8 to 10
  - `/deals` and `/companies` from 10 to 13
  - `/policy` from 13 to 15
  - `/analysis` from 15 to 17
  - `/ask` from 17 to 20
- **Five questions,** asked at the end.
- **Where notes go:** `docs/feedback/YYYY-MM-DD-<role>.md`, by role only unless the person agrees to be named, plus a running tally.

`docs/feedback/TEMPLATE.md` is the note to copy. `docs/platform-tools.md` has an unnumbered Feedback row pointing at the folder, so the parsers that read the numbered tool rows (`site/scripts/build-content.mjs`, `build_overview.py`) are unaffected. There were no site changes in this task.

## Task 4

- **Briefing:** no table changed shape. The `energy_companies` paragraph in `llms.txt` said "17 companies from two niches", so it now describes the deal-seeded rows and their note. The chat spec was regenerated, and `check_spec.py` passes.
- **Status page and overview:**
  - Tool 10's row in `docs/platform-tools.md` gives the seeding and its counts.
  - The `/companies` line in `site/lib/pages.ts` names the deal tracker.
  - `docs/OVERVIEW.md` and `STATUS.md` are regenerated.
- **Validator:** 113 of 113 tables pass.
- **Coverage:** 113 tables.
- **Live set:**
  - A full load: 65 live tables match, and the catalogue matches (113).
  - One mismatch: sources, CSV 151 against Supabase 152 (see the open questions).
  - `pg_database_size` is 367.3 MB against the 400 MB limit, up from 334.6 MB after Task 2's load.
- **Value check:**
  - 705 of 705 values match Supabase (`/roundup`: 20 of 20).
  - The first pass gave 702 of 705. All three failures were catalogue figures served from Next's fetch cache (`site/.next/cache/fetch-cache`), left from an earlier build: `energy_companies` showed 17 rows rather than 284.
  - I cleared that cache, which is a build artefact outside git, and rebuilt. All values then matched.

## Decisions made without a human

1. **Sonnet 5.5's price was read from the pricing page** and added to the price tables, rather than pinning the older model. The builder is meant to use the newest Sonnet.
2. **A deal's place is recorded as the company's location, with a note.** The ruling says "location where a deal states one". The note, and the words "(where a deal is)" on the page, keep a reader from taking it for a headquarters.
3. **Confidence for a deal-only row counts distinct source domains as its independent sources.** Two stories on one site count as one.
4. **Deal-only rows are rebuilt on every run, and researched rows are never changed** except to gain a deal's sources and tags. The Thesis Builder's fields therefore always win.
5. **Researched rows that are one company were folded** (Tyba), keeping the fields of the higher-confidence row and the sources of both.
6. **I wrote the five demo questions** (the prompt asked for "the five questions" without listing them). They ask:
   - what the person hoped to find;
   - what they would not trust;
   - what they would use in the next month and what is missing;
   - what confused them;
   - who else should see it.

   Please change them if you had others in mind.
7. **The stray `CTVC` source was not pruned** (see below). Only a person runs `load.py --prune`.

## Open questions for a human

1. **The `CTVC` source in Supabase.** It is a news outlet that the news ingest registered in Supabase's sources table today (first and last seen 2026-09-28). It is not in the local `sources.csv` or the local `news_stories.csv`, and `origin/main` has no later commit.
   - My reading is that a scheduled run upserted it without its files reaching git.
   - Until it is pruned, or the story that carries it lands in `news_stories`, the load's sources check fails.
   - Run `python warehouse/supabase/load.py --prune`?
2. **Database size: 367.3 MB of 400 MB.** It rose about 33 MB between Task 2's load and Task 4's. This load rewrote rows of several tables (the weather tables among them), so dead rows are a likely part of it, not yet measured. Should the 90-day window shrink for some tables, or should dead rows be vacuumed, before the limit is reached?
3. **Research the deal-seeded rows?** 265 companies wait for a description, stage and raised amount. A Thesis Builder pass per company would cost money. Which ones first: the most deals, or a sector?
4. **Parties that are not names** ("a Leading Frontier AI Lab"). Keep them, or drop them from `energy_companies` while they stay in `energy_deals`?
