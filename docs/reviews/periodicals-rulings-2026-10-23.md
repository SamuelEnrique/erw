# The rulings the periodicals wait for, in plain words: 23 October 2026

Energy Research Warehouse (ERW), session 812, 22 October 2026. Every item of the Digest audit and the Roundup audit of 21 October, and of this chain (sessions 800 to 811, `queue/done/060-night-23-october-code-periodicals.md`), that waits for the owner: one a line, what the choice is, what each answer changes, and the session's recommendation with its reason. No session decided any of them. The audits are `docs/reviews/digest-audit-2026-10-21.md` and `roundup-audit-2026-10-21.md`; the chain's plan is `periodicals-plan-2026-10-23.md`; the dry runs are `periodicals-dryrun-2026-10-23.md`.

## From the Digest audit

1. **Held grid prices in the Digest** (audit fix 1). The choice: whether the Digest may print NYISO's and ISO-NE's day-ahead averages and a NYISO or ISO-NE real-time maximum while those publishers' licenses are unanswered. Today the markdown holds the figures, the page draws "license needed" in their place, the email carries them, and since session 804 they are not ranked among the movers. Yes: nothing changes. No: the rows print "licensed source needed" with no digits in the markdown and the email, and the real-time line skips held tables (a day's work, `brief.numbers_today`). Recommendation: no, print no held digit anywhere, since the email is the one copy a reader keeps and the board already says "licensed source needed" for the same series.
2. **The email while the news index is held** (audit fix 1, second half). The choice: whether the Digest's email goes out while `news_index` is "license needed" (the stories' titles and links are the held outlets' text). Yes: it goes out as now, with the held outlets named and not linked (session 803). No: `email_digest.py --auto` renders and does not send until the hold is lifted. Recommendation: send to the fixed recipients only (the owner and the reviewer) and to no subscriber until the hold is answered; the daily run's `DIGEST_RECIPIENTS` does that today, and subscribers are read only with `EMAIL_SUBSCRIBERS=1`.
3. **The window opens at the previous issue's end** (audit fix 2). The choice: a 24-hour window to the run, as now, or a window from the previous issue's end (capped at 96 hours), so a missed weekday is caught up and Friday evening is in Monday's issue. Yes: Monday covers Friday 15:45 to Monday 15:45, and a day the run missed is covered by the next. No: as now; 41 percent of the period's stories fell in no issue. Recommendation: yes, with the cap at 96 hours, because a reader who missed nothing should not be told nothing happened on a day the run failed.
4. **The AI tie-break** (audit fix 6). The choice: whether clusters of equal significance keep being ordered by AI relevance (as now) or by the number of outlets, then time. Yes to the change: a 42 MW datacenter story no longer outranks a 600 MW gas deal at the same score. No: as now. Recommendation: make the change; the rubric says an AI angle earns no credit by itself, and session 802's one-topic rule already keeps datacenter stories to one item in the top ten, so the tie-break is the last place AI counts twice.
5. **The two-minute form** (audit fix 15). The choice: which sections stay above the fold: the top five and the numbers (about 450 words), with "By sector" and "AI and power" folded or cut. Yes: the page and the email open with the five and the numbers; the rest folds. No: as now (1,500 to 1,800 words). Recommendation: fold, do not cut: the top five, the five numbers and the chart first, the sections under a "More" heading; the email keeps the top five and the numbers as it does.
6. **The chart of the day's caveat, floor and the three ruled drafts** (audit fix 10). Three choices: (a) whether a chart of the newest month of an EIA state series carries "EIA's newest month is preliminary" (no source for that sentence is in the repository; the owner can name one); (b) a strength floor below which no flag is the chart (1.01 robust standard deviations was the weakest shown); (c) whether a flag whose draft a check ruled "dismissed" or "full card asked" may be the chart. Recommendation: (a) yes, once a source is named; (b) a floor of 1.5; (c) no, a dismissed draft is not the day's chart. Since session 805 the chart follows the day's stories first, which makes (b) matter less.
7. **A pun that states a fact** (audit fix 11, second half). The choice: whether a fun fact's pun may state something its source does not ("no wonder it moves at a crawl"), held to a source like any second half, or to a rule by pattern that would also refuse two of the bank's eight other puns. Recommendation: hold a pun to its source; cut the two puns the rule refuses rather than keep a rule that lets a claim through.
8. **Whether the 14 October issue is corrected in place** (the Senghenydd fun fact) or left as written. Recommendation: leave it as written and say so on the page in one line; a corrected archive is not a record.

## From the Roundup audit

9. **The coverage charts' division** (audit fix 3). The choice: whether a chart of a count of what the ERW collected (deals by month, facilities by state) divides by the scored stories of the month before it competes, or stays excluded as session 119 has it. Recommendation: keep it excluded; a ratio of two counts the ERW made is still a measure of the ERW.
10. **A missed week said** (audit fix 6). The choice: whether a Roundup whose previous ISO week has no issue (week 42) says so under its title and points to the week's stories. Recommendation: yes, one line; the reader of the archive should not have to count weeks.
11. **Deals and datacenters: a floor and US first** (audit fix 7). The choice: whether the two tables print every extracted row (40 deals, 22 facilities a week, most without a country) or rows with confidence 0.7 or more and at least one of operator, site or MW, US rows first, at most 15 a section with a count of the rest and a link. Recommendation: the floor and US first, since the warehouse's coverage is "US first, world later" and a table of 40 rows is not read.
12. **The no-model headlines' adjectives** (session 577's question). The choice: whether a publisher's own title, printed as the headline when the model is not called, may lose "massive" and the like, or stays the publisher's words said as such. Recommendation: keep the publisher's words; the page says they are the publisher's, and an edited quotation is neither.

## From this chain

13. **The topic key** (session 802). The choice: a topic is the scorer's sector alone (as landed), or the sector with a finer key (the region, or a party). The sector alone folds Mexico's 8,200 MW, Exelon's generation plans, India's coal stocks and Ormat's auction under one "generation" item; a finer key keeps more of them apart and lets a sector hold two items. Recommendation: the sector with the region (a country or a US state) as the key, so Mexico and India are two topics; the constant is `brief.same_topic`.
14. **The "also" lines and the two-minute form** (session 802). The choice: whether the "Also on this topic" lines count toward the words above the fold (item 5). Recommendation: they do not; they are the fold.
15. **The held outlets' links** (session 803). The choice: whether an item from an outlet of the news index's hold shows the outlet's name with no link (as landed, the chain's words) or keeps its link (a link reaches the publisher's own page; the title is the republished text). Recommendation: keep the link; the hold is about republishing text, and a link republishes nothing. One line of `brief.source_text` changes it.
16. **The why line's fallback** (sessions 801 and 807). The choice: when the scorer's line fails the check and cannot be mended, the item prints the headline alone (as landed) or the headline's own clause again. Recommendation: the headline alone, as landed; nothing is invented and nothing is said twice.
17. **The chart of the week re-drawn for the measure the stories point to** (session 806). The choice: the Roundup keeps the rule's chart and names the related measure (as landed), or `warehouse/analysis/run.py` on the data machine renders the related measure's chart too and the Roundup shows it. Recommendation: render both on the data machine and show the related one, with the rule's named; the week's picture should be of the week.
18. **US48 demand a year before** (session 804). The choice: whether the data machine keeps a US48 daily peak history (a US48 row in `eia930_daily_demand`, or a longer window of `eia930_all_demand`), so the Digest's demand line can compare with the same weekday a year before; today the line says the year before is not held. Recommendation: the US48 row in the daily table, one connector change on the data machine.
19. **The ten floors under the license holds** (session 607's standing item, which every landing of this chain met too). The choice: lower the floors of the ten pages whose figures are held, count "license needed" toward them, or keep them failing as a reminder in every gate. Recommendation: count "license needed" toward the floor; the gate should fail on a lost figure, not on a held one.

## Not waiting for a ruling, done by this chain

The why line's rule (801), one topic one item (802), the sources' names and the email's text (803), the numbers section that says what moved (804), the chart that follows the day (805), the Roundup's five numbers, its chart's sentence and the real-time interval (806), the dry runs (807, 808), the regression suite (809), the emails at 390 (810), the method on the page (811).

## State after session 836 (23 October 2026, about 07:55 UTC)

Session 836 of chain 081 (`queue/done/081-night-24-october-portable-deals-2.md`), doing session 835's reading after 835 was stopped by its precheck. Each item's state is open, answered or done; no item is decided by the session. Where an answer was looked for: this file (unchanged since session 812 wrote it); `docs/state/` (no `rulings_*.md` since 11 October, no note of the owner's since); every commit on main since 00:00 UTC on 22 October (each a session's, a workflow's, or one of the owner's uploads and renames of queue files on 22 October, all before this file existed); `warehouse/metadata/license_status.csv` (last changed on 20 October by session 348; NYISO's, ISO-NE's and the news index's rows still "license needed"); `queue/` (no file of the owner's since the morning of 22 October). Chain 080's session 822 was running the landing of `wip/818-periodicals` when this was written, so the items say "as landed" of a branch not yet on main.

| # | Item | State |
|---|---|---|
| 1 | Held grid prices in the Digest | open |
| 2 | The email while the news index is held | open |
| 3 | The window opens at the previous issue's end | open |
| 4 | The AI tie-break | open |
| 5 | The two-minute form | open |
| 6 | The chart of the day's caveat, floor and the three ruled drafts | open |
| 7 | A pun that states a fact | open |
| 8 | Whether the 14 October issue is corrected in place | open |
| 9 | The coverage charts' division | open |
| 10 | A missed week said | open |
| 11 | Deals and datacenters: a floor and US first | open |
| 12 | The no-model headlines' adjectives | open |
| 13 | The topic key | open |
| 14 | The "also" lines and the two-minute form | open |
| 15 | The held outlets' links | open |
| 16 | The why line's fallback | open |
| 17 | The chart of the week re-drawn for the measure the stories point to | open |
| 18 | US48 demand a year before | open |
| 19 | The ten floors under the license holds | open |

Nineteen open, none answered, none done. `docs/reviews/deals-rulings-2026-10-23.md` did not exist yet (chain 080's session 832 writes it); its state section is for the session that next reads the rulings (839 of this chain, or 843 of the next file).
