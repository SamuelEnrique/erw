# Session 2701 report: the Digest's rulings applied as their defaults

Energy Research Warehouse (ERW), session 2701, chain 131 (`queue/done/131-night-25-october-code-periodicals-v2.md`), samueloldlaptop, 25 October 2026, about 06:44 to 06:58 UTC. Model Opus 5.5. Model spend USD 0. No warehouse data written; nothing sent or posted; no web request but GitHub; no build.

## Read these first

- **Branch `wip/2701-periodicals`**, cut from `wip/2700-periodicals`, pushed (`848b7eb1`). One commit an item, each with its test in `tests/test_periodicals.py` (a class an item, named `Item<N>...`), proved on fixtures and the saved stories, never on a live feed.
- **The owner's rule of 18 October** applies: `docs/reviews/periodicals-rulings-2026-10-23.md` was written on 23 October at about 09:30 UTC and no item was answered by 22:35 UTC that day, nor since (no `docs/state/rulings_*.md` after 11 October; the rulings file unchanged on main). Every default below can be reversed by exception; each is its own commit, so `git revert <sha>` undoes one.
- **507 tests** of the 28 test files that import the periodicals' code pass together (`brief`, `roundup`, `email_digest`, `daily_chart`, `funfact`, the two checkers), skipped 2.

## Decisions made without you (the 24-hour default)

| Item | What now holds | Commit |
|---|---|---|
| 1 | No held digit anywhere: a held grid's day-ahead row prints "licensed source needed" with no day before and no change; the highest real-time price skips a held grid's table and ends "Not read: MISO, NYISO (licensed source needed)." The email renders the markdown, so it carries no held digit either. | `147b7fd4` |
| 3 | The window opens at the previous issue's end, capped at 96 hours (`brief.previous_end`, `window_start`); the stamp says the window's own hours ("for the 72 hours to ..." on a Monday). `--hours` still gives a fixed window. | `f48c0e45` |
| 4 | The tie-break among equal significance is the number of outlets, then the time; AI relevance no longer counts (session 814's event before commentary kept). | `ac37f16e` |
| 6(b), 6(c) | No scanner flag under 1.5 robust standard deviations is the chart of the day; nor a flag whose draft was dismissed (`daily_chart.dismissed_keys` reads `scanner_drafts`, state dismissed). The record's "why" says how many each rule passed over. | `414210f0` |
| 7 | A pun that states a claim ("no wonder", "because", "since", ", so") is held to its source (`funfact.PUN_CLAIM`). Cut from the bank as the bank cuts a fact (status dropped, with the reason): the kWh pun (`ff_528bbbd5f8`) and the audit's 2 October pun (`ff_6c3f03312f`); the Btu match (`ff_b2e98af092`) was already dropped. | `7bfe4f1a` |
| 8 | The 14 October issue stays as written; its page says so in one line (`site/lib/digest.ts` `ISSUE_NOTES`). | `426c8353` |
| 13 | The topic key is the sector with the region (`brief.same_topic`, `region_key`; a cluster without a region is of every region). | `25edb09b` |
| 14 | The "also" lines do not count toward the words above the fold (`brief.above_fold_words`, which session 2703's word count uses). | `4d6c0123` |
| 15 | A held outlet's item keeps its link (`brief.source_text`). | `de138638` |
| 16 | Nothing to do: the why line's fallback is the headline alone, as landed. | none |
| 2 | Nothing to do: the email already goes to the fixed recipients only (`DIGEST_RECIPIENTS`; subscribers only with `EMAIL_SUBSCRIBERS=1`). | none |

## Other decisions made without you

- **Item 13 with a cap of two items a sector** (`brief.SECTOR_MAX`). With the region alone in the key, 13 October's top ten held four datacenter items (four states), which undid session 802's reason for the rule. The ruling's own words were "lets a sector hold two items", so a third item of a sector folds under the sector's first. Reversible in one constant.
- **Item 7 also cuts the 2 October pun** (the audit's example), which the new rule refuses; the chain named "the two puns the rule refuses" (kWh and Btu), and the Btu match was dropped before, so the kWh pun is the one newly cut beside it.
- **Item 6(c) matches a dismissed draft by its id**, the flag's own id, not by the series: a series flagged again on a later day is a new observation. With no service key on the machine (GitHub's runner, a test), nothing is read and the log says so.
- Tests of earlier sessions changed where the ruling reverses what they pinned, each said in a comment: session 470's and 809's 2 October twin (Korea's framework once, whichever twin the new order keeps), session 802's and 809's 13 October (two a sector at most), session 803's, 807's and 809's held outlet (now linked), session 805's flag strengths (raised over the floor in their order), session 2206's and 807's reading of `main` (the window's new call).

## Still open

- Item 6(a): the sentence "EIA's newest month is preliminary" waits for a source the owner names.
- Item 18 (US48 demand a year before) is the data machine's: one connector change, a US48 row in `eia930_daily_demand`; named here for its next file.
- Item 5 (the two-minute form, fold under "More") is built by session 2703 with the v2 order.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2701"` | 0 | passed |
| `python -m unittest` over the 28 test files importing the periodicals' code | 0 | 507 passed, 2 skipped |
| em dashes in the changed files | | none |

## The landing

None in this session (2700's gate did not run for memory; 2706 lands the chain's branches at once).

## For Samuel's ruling

- None new. The defaults above can be reversed by exception on Monday.
