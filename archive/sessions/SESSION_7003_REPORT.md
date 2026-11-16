# Session 7003 report: the Attention and Friction indices' data faults (attention rows 2, 7, 15 to 18, 20)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0. No request made: the builder reads `news_stories` and the classified rows held.

## What a reader of `/attention` now sees that was wrong (the files rebuilt on the branch)

- **"What rose" no longer counts unclassified weeks as zeros:** the week of 2026-10-05 had "Oil and LNG 17.23 0.00 +17.23" (its four weeks before never classified); it now has no row (no classified week before it), and the next weeks average only the classified weeks before, with their count carried.
- **No week ahead of the corpus:** two feed items listing coming events (dated 17 November and 1 December, read in October) had drawn weeks 2026-11-16 and 2026-11-30; the weeks now end at 2026-11-09.
- **Opposition counted as events beside stories:** the 250 energy opposition stories of the classified weeks are 214 events (news clusters). Data centers: 90 stories, 77 events.
- **The memo** (`docs/reviews/attention-paper-notes-2026-11-06.md`) no longer says the week of 2 November was "the week of the ballot measures in Texas, Georgia and Iowa" (none of its 19 opposition stories names one), and its chart line reads -0.69 and +0.18, as its own figures do.
- **The method note** says the stories are classified from 2026-10-05 (8,119 of 27,419), that the four outlets are 75.8 percent of the corpus and 64.5 percent of the classified rows, that the index counts stories not events, and what the review found of the opposition class.

## Commits (on `wip/c301-data`)

- `attention_index.py`: `us` in the week files; What rose over classified weeks, `weeks_before`; `opposition_events` (table and cells); `together` (each sector over the classified weeks); a story dated more than a day after it was read left out; `columns` names each array's fields. `attention_classify.py`: prompt version 4 (the opposition rule's exclusions: a contract dispute, a government's own policy, an endorsement, a short seller's report, a poll, markets and geopolitics; a poll never protest; an applicant's withdrawal takes the pushback's kind). Test 7003 (5 tests). The tables rebuilt under the data lock, validated, coverage, archived; `site/data/attention.json` and the week files.
- The faults file marked; found row 25 added; `docs/state/data_ready_c301.md` rows 9 to 12.

## Each row's new state

- Rows 2, 7, 16, 17, 18, 20: fixed. Rows 2, 7, 16, 18 also need a page change (data_ready 9 to 12).
- Row 15: the prompt fixed; the opposition rows classified again **need the key** (the 254 opposition stories, about USD 0.10; all 8,120 rows, about USD 2.20).
- Row 25 (found): fixed.

## Needs the key

- Attention row 15: the opposition rows classified again under prompt version 4, about USD 0.10 (or USD 2.20 for every row).

## Decisions made without you

- **The link table keeps the one future-dated row** it already held (its merge writer keeps rows a run does not write); the indices and the page files leave it out. A snapshot write of the link table would drop it; not done, so no classification is lost.
- **A feed item is "ahead" when dated more than a day after it was read:** a day's grace for time zones and feeds that stamp the next morning.

## For Samuel's ruling

- None new.
