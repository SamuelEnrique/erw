# Session 444 report: the weekly Roundup, read as its most demanding reader

21 October 2026, 07:16 to about 07:40 UTC, unattended, on portable-laptop (the code role), in the main checkout on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 444). Model spend USD 0; no warehouse data written; no `site/` change, so no build. Pulls: none. Link checks only, 147 requests (below).

## Read these first

- **The audit is `docs/reviews/roundup-audit-2026-10-21.md`.** The repository holds three Roundups (2026-W39, W40, W41) and the emails of two (W40, W41). **Week 42 (18 October) was never written or sent**: its run stopped at the restore (Redivis's export cap, session 305), and no later issue says so.
- **W39 traces whole**: all 24 of its figures (six day-ahead hubs and their week before, the real-time maximum, three fuels, US48 peak demand, the chart's medians, quartiles and gap) equal a recomputation from `warehouse/output`. **W40 traces in part** (the fuels, the week-before column, the chart, the deal and datacenter counts); **W41's numbers are untraceable on this machine**, whose tables end on 1 to 3 October. A read through the `erw` package with `ERW_BACKEND=supabase` gave the same rows as the local files. W41's chart traces to its card's CSV.
- **What a demanding reader would object to, most first:** one event shown twice in the same issue (W40: the South Korea nuclear package as items 1 and 2; OPEC+ as Weekend items 2 and 3) and again a week later (the Amazon and Constellation PPA, W40 and W41); "weekly change" for fuels that is a two-trading-day change (EIA's lag), with W40's "WTI rose 10.93 (+12.8%)" measured from one outlier close (85.23 on 25 September, between 95.88 and 99.37 while Brent barely moved); W40's chart of the week measured the ERW's own coverage (59 deals in September from 3,199 scored stories, against 221 stories in August), not the market; 75 of 200 links go through Google News and cannot be resolved or checked; W41's email does not tell its reader its headlines are the publishers' own titles; deal and datacenter tables printed with no floor and no US filter (W40: 6 of 22 facilities in a US state, 8 with no operator, site or MW).
- **13 ranked fixes for the code machine**, each with its file and the test that would prove it, and a table of what the Roundup shares with the Digest (`score.py` clustering, `brief.py` ranking, repeats, own titles, links, numbers; `email_digest.py`; the chart code), so that one fix lands in both.

## What to review

- The audit: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/roundup-audit-2026-10-21.md`
- The test: `tests/test_session444.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s444/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 444"` (run by the chain before this session) | 0 | |
| The traces (`trace.py`, `trace2.py`, `trace3.py`, `trace_chart39`, `trace_chart40`, `trace_chart41`, `selection`, `missed`, `news_by_month`) | 0 each, but `trace.py` | `trace.py` exit 1: W41's week holds no rows on this machine (its last block failed on an empty week); its W38 to W40 output was complete and is the record used. `trace_live.py` exit 0 |
| The link check (`linkcheck.py`) | 0 | 147 requests: 22 robots files, 125 link requests; 117 links answered 200, 4 refused an automated agent (Utility Dive, HEAD and GET 403), 7 not asked (robots), 72 Google News links not asked |
| `tests.test_session444` | 0 | 6 tests OK: no em or en dash; every Roundup page and saved Roundup email named; every path named exists; every fix names an existing file and a test; W39's figures as the page prints them; the link log numbered, within 150, no paused host |
| `tests.test_session444` against a copy of the audit with a dash and an unknown file added | 1 (2 failures) | as it should |
| The whole suite | not run | docs and one test file only; the chain's last session runs it before the landing list |

## Decisions made without you

1. **Link checks counted as allowed under "Pulls: none".** A link check is not a data pull: one HEAD a link (GET with the body discarded only where HEAD was refused), each host's robots file read first, a link the robots file disallows not asked, a host whose robots file refused us treated as disallowing all, 15 s timeouts, a User-Agent naming the ERW and the session, no paused host, at most 150 requests. 147 were made; every one is in `runs/chain_oct21_third/s444/links.csv` (git ignores `runs/`).
2. **Google News links sampled, not checked.** 75 of the 200 distinct links are Google News addresses; the ceiling left room for 3, and the robots file disallowed all 3. The other 72 were not asked. `news_stories.url_resolved` already records that none of the 75 resolved to an outlet.
3. **Supabase read once, through the `erw` package's own backend, for the W40 and W41 numbers.** It is the ERW's own live set, not a publisher. It returned the same rows as the local files; nothing more was asked of it tonight (the database is timing out).
4. **The selection judged from `news_stories` only**, the ERW's own record of what the feeds carried, never from memory; each story named with its outlets as the table holds them.
5. **The W43 draft on `wip/findings-oct20` named, not audited**: it is not an issue and not on main.
6. **The AI tie-break is put to Samuel, not listed as a fault**: it is a rule of the ranking, and changing it changes what both periodicals choose.

## For Samuel's ruling

- **Week 42**: send it late (session 326's dry run built it), say in week 43 that it was missed (fix 6), or leave it.
- **The AI tie-break**: at equal significance an AI-relevant story outranks any other (W39: Fervo's 900 MW geothermal first power and the Solar for All ruling lost to AI stories of the same score). Keep it, or rank US power stories equally with AI ones, since AI is "the sharpest current lens on that system, not its boundary".
- **US first in the deals and datacenter sections** (fix 7): a floor and an order, or every row as now.
- **The chart of the week's eligibility** (fix 3): templates that count extracted news rows wait for twelve months of live feeds, or are normalized by the month's scored stories.
- **WTI's close of 85.23 on 25 September**: for the data machine to confirm against EIA's page before any page quotes the W40 change.

## To finish

- Land `docs/reviews/roundup-audit-2026-10-21.md` and `tests/test_session444.py` with the code machine's next landing (docs and a test only; no build needed for them).
- On a machine with current tables, trace W40 and W41's untraced figures (fix 13) and add them to the audit.

## Files

- `docs/reviews/roundup-audit-2026-10-21.md` (new).
- `tests/test_session444.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s444/` (the traces and their outputs, `links_all.txt`, `links.csv`, `linkcheck.out`, `test.out`, `test_negative.out`).
