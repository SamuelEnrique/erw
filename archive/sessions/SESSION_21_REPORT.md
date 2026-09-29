# Session 21 report

Energy Research Warehouse (ERW), session 21, run 2026-09-28 (UTC). **API spend: USD 0.0806**, all for briefs, under the USD 3 stop:
- three runs of today's digest (headlines and numbers summary: 0.0152, 0.0194 and 0.0199);
- three runs of Energy Week 2026-W39 (0.0054 for a run that stopped on a date bug, then 0.0103 and 0.0104).

No key was printed or committed. `origin/main` was merged before the push. All twelve rulings are applied.

**Three things to know first:**
- **Numbers share (ruling 4):**
  - **Today's digest:** 1 of the top 10 headlines carries a number, and 0 of the 10 clusters had a scored figure to use. The one number (123 million tons of CO2) comes from its stories' titles.
  - **Energy Week 2026-W39:** 3 of 5 headlines carry a number, all 3 clusters that had a scored figure ($3.2bn; $1.9B and 23 GW; $12 billion).
  - The rule makes the model use a figure wherever the stories' scored fields hold one. The ranking was not changed. Today's stories simply offered none.
- **The duplicate (ruling 5):** each section of the digest chose its clusters on its own. A top-10 cluster came back under By sector and AI and power with the same headline, because it was the same cluster. It is fixed, and a hard check now stops any brief with a repeated normalized headline or source URL. The check fails all three earlier digests (2026-09-25 to 27).
- **Two bugs found and fixed on the way,** both from earlier sessions:
  - **The trader view failed in CI:** it compared kept values as text against a table restored from Redivis with numeric values. Fixed in `be7ab48`.
  - **Energy Week would have failed on Monday:** since the backfill, `energy_deals` has dates without a time. Fixed in Task 1.

## What was built

| Task | Result | API cost | Commit |
|---|---|---|---|
| (fix) | `trader_view.py`: kept values compared as numbers (the CI failure of 2026-09-27) | 0 | `be7ab48` |
| 1 | Rulings 1, 2, 3, 6, 8, 9, 12: name, home copy, one-sentence intros, numbers summaries and footnotes, page leads and glossary, Related lines, scope notes | 0.0402 | `6d790d8` |
| 2 | Rulings 4 and 5: sector labels, headlines with figures, distinct sections and the hard check | 0.0404 | `2a5e3b0` |
| 3 | Rulings 7, 10, 11: email opt-ins, downloads and a data dictionary, `/terms` | 0 | `af3df25` |
| 4 | Screenshots of every page, the value check (684 of 684), this report | 0 | final commit |

## Task 1

- **Ruling 1: the name.**
  - The full name appears once on the home page (its heading) and once on `/about`.
  - Everywhere else it is ERW: the header, page titles (`%s | ERW`), `/data`, `/ask` citations, the digest, Energy Week and the emails.
  - The home opening line is "The live, citable record of the US energy system." The full definition stays on `/about`.
- **Ruling 2:** the home digest subtitle is "What is happening in energy today, from scored news."
- **Ruling 3: the intros.**
  - Each is one sentence: "The ERW's daily brief of energy news for the 24 hours to 2026-09-28 04:09 UTC, from 117 scored stories." Energy Week reads the same way for its week.
  - The method (stories, scoring and the rubric, headlines, numbers, schedule, and why titles are not republished) moved to `/about#digest`. Each brief ends with "How this is made."
  - The generation record (script, time, run log, model) stays in the file as an HTML comment, which the page does not show.
- **Ruling 6: the numbers sections.**
  - **No provenance sentence.** Each number carries a footnote marker, and a "Tables:" list at the end of the section names each table and its source report.
  - **A summary on top:** two or three sentences by the model, checked with the chat's literal-number check (`warehouse/chat/ask.py`). Every number in the summary must appear in the section, footnotes excluded. It gets one regeneration, else it is omitted.
  - **This session:** all four summaries (two digests, two weeklies) passed on the first attempt.
- **Ruling 8: page leads and the glossary.**
  - Every data page opens with one plain sentence: what it shows, the period, and the source by name. These are `/markets`, `/prices`, the explorer, `/grid`, `/mix`, `/curtailment`, `/consumption`, `/map`, `/datacenters` and `/deals`.
  - Acronyms (the ISO names, ISO, EIA, DAM, RTM, LMP, HSL, PADD, RPM) come from `site/lib/glossary.ts`. `/about#glossary` lists them. `components/Term.tsx` links the first use on a page to its entry, with a hover title; later uses get the hover title.
- **Ruling 9:** each data page ends with a "Related" line of two pages, from a `related` field in `site/lib/pages.ts`.
- **Ruling 12:** `/map` and `/datacenters` state their scope: news-derived since 2025-10-01 plus the ISOs' queues; not a census of every facility.
- **Regenerated:** `docs/digest/2026-09-28.md` and Energy Week 2026-W39. The local price, fuel and EIA-930 tables were refreshed first. At 04:09 UTC no real-time table yet holds yesterday's complete operating day, and the digest says so. The daily run at 14:00 UTC rewrites today's digest.
- **Also fixed:** `weekly.py` now parses deal and datacenter dates as ISO 8601. The backfill added date-only values, and the first W39 run stopped on them. The scheduled Monday brief would have too.

## Task 2

- **Ruling 4: no scores, figures in headlines.**
  - The brief lists show the sector, never the significance score. That covers Top of the industry, By sector, AI and power (no AI score either) and the week's five stories.
  - The headline prompt gets each cluster's scored figures and must use one where they exist. The figures are the MW and the price mentioned (from any of the cluster's stories), and the MW, dollar, price and percent figures in its why line.
  - **Every headline's numbers are checked** against its cluster's titles, summary, why line and figures, with the chat's literal check. A failure is asked again once; a second failure stops the brief. No headline needed the retry this session.
  - **The share is logged and recorded in the run status:** "top 10 with a number 1 of 10 (0 with a scored figure)".
- **Ruling 5: the duplicate and the hard check.**
  - **Cause:** the top 10, the three per sector group, and the five on AI and power were each taken from all clusters. A cluster in the top 10 therefore reappeared, with the same headline. The 2026-09-27 digest repeated eight events this way.
  - **Fix:** each section now takes only clusters not shown above it. A later cluster whose normalized headline or first source URL repeats an earlier item is dropped and logged.
  - **The hard check:** `brief.assert_unique` raises before anything is written if two items share a normalized headline or a source URL. It runs for the digest and Energy Week. Today's digest: 19 items, no repeats.

## Task 3

- **Ruling 7: email opt-ins.**
  - `/subscribe` has two checkboxes: the daily Energy Digest (checked by default) and Energy Week. Either or both may be chosen; neither is refused.
  - Migration 006 adds `daily` and `weekly` to `subscribers` and requires at least one. It is applied, and was checked in rolled-back transactions: both combinations accepted, neither refused, anon cannot read, 0 rows.
  - `email_digest.py` sends each kind only to the subscribers who chose it, when `EMAIL_SUBSCRIBERS=1`. That is off, because double opt-in and a tokened unsubscribe come first (your ruling).
  - A one-line privacy promise is on the page.
- **Ruling 10: downloads and the data dictionary.**
  - **Downloads:** `/data` has a Download column. Every public live-set table links to `/api/download`, which streams from Supabase with the anon key: the provenance header lines as `#` lines, then the table's columns, at most 200,000 rows (a larger table answers 413 with the Redivis link). Tables not in the live set link to Redivis, noting that version 1 is pending release.
  - **Tested:** `energy_deals` downloads with its 10 header lines and 191 rows; `eia860m_operating_generators` points to Redivis; `news_stories` (internal) is refused.
  - **The data dictionary** section renders the three shape sections of the data standard.
- **Ruling 11: `/terms`.**
  - Data licensing per source, from `sources.csv` (62 data sources listed with their licenses; 65 news outlets, internal).
  - What is stored about subscribers.
  - Ask questions are logged without identity. This was not true before: `/api/ask` logged no questions. It now logs the time, the question and the outcome; the IP address stays only in memory for the hourly limit.
  - A Stanford student research project, not investment advice.
  - Linked from the footer and listed in `pages.ts` under About.

## Task 4

- **Value check: 684 of 684 values match Supabase.**
  - **First run:** one miss. Energy Week, regenerated from this machine's refreshed EIA-930 table, shows US48 demand at 608,317 MW (EIA's revision). Supabase still held 608,314 from CI's earlier load.
  - **The fix:** loading the refreshed `eia930_us48_demand` with `--only`. The site was rebuilt with an empty fetch cache (`/grid` had been built before the load).
  - **After the load:** `pg_database_size` is 327.1 MB (limit 400) after your prune, and the sources match (127 and 127).
- **Screenshots:** every page, desktop and mobile, including the new `/terms`.
  - The capture had started timing out on every page. Chrome's headless GPU path hangs on this machine now, and the screenshot script passes `--disable-gpu`.
  - Four leftover headless Chrome processes from the failed attempts were stopped.

## Decisions

1. **Figures for a headline come from the whole cluster's scored fields,** not only the lead story's, so a figure any story scored can be used. With the lead story only, W39 would have offered fewer figures.
2. **A headline that still fails the number check stops the brief** rather than being published or dropped. Dropping it would change the ranking.
3. **The generation record of each brief stays in the file as an HTML comment.** Non-negotiable 5 wants files to name their provenance; the page no longer shows it.
4. **`/ask` now logs questions without identity,** so that `/terms` states a fact.
5. **Sending to subscribers stays switched off** (`EMAIL_SUBSCRIBERS`), per your ruling on double opt-in.

## Open questions for the human

1. **Today's digest carries few figures** because few stories get a scored MW or price. Should the scorer be asked to fill `mw` and `price_mentioned` more often? That would change the scoring prompt, and re-scoring costs about USD 0.10 per 43 stories.
2. **Double opt-in and unsubscribe:** when they are built, set `EMAIL_SUBSCRIBERS=1` with the Resend secrets.
