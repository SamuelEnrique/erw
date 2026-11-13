# Sessions 3472 to 3487: chain 254, the periodicals continued (13 November 2026)

Energy Research Warehouse (ERW). Chain 254 (`queue/done/254-day-21-november-oldlaptop-periodicals-continued.md`), sessions 3472 to 3487, samueloldlaptop (code role), unattended, Opus 5.5. Taken at 19:50 UTC by chain 252's queue step (session 3471). One report for the chain, a section per session.

## Session 3472: the next file, the ground

- **Numbers:** sessions 3472 to 3487 named by nothing on origin's main or any branch.
- **Next file:** `queue/next/258-day-22-november-oldlaptop-periodicals-continued.md` (sessions 3488 to 3499 and 3501 to 3504; 3500 is a backfill report's), committed alone and pushed (`2ccf18f6a`). The first queue number free in every ref was 258. The 247 that chain 252 passed over has since been taken by another machine (`247-day-15-november-portable-p2-security-continued.md`).
- **Precheck:** exit 0 (on duty for "session 3472" until 14 November 11:48 UTC). **Disk:** 81 GB free. **Memory:** MemFree about 2.15 GB.
- **Worktrees:** `erw-1425` (`wip/1425-grid`) and `erw-1600` (`wip/1642-board`) are not landed and are kept. `erw-3457` is the stack (row 11).
- **Row 11 has not landed:** `wip/3457-periodicals` at `95189fdf8`, requested.
- **Chain 252's unfinished list** is in the file, so this chain takes it in order: the stack's build (3473), the stored W46 Roundup (3474), the 13 November issue's landing and the first issue after it (3475), row 11's clean-up (3476).

## Session 3473: the stack's build waits on memory; rows 173 and 174

- **The build:** `npm ci` is done in `erw-3457/site`, but MemFree stayed between 2.1 and 2.3 GB, under the 2.5 GB the rule asks. A bounded wait runs (`runs/s3473_memwait.sh`, 40 minutes); the build starts when it reports.
- **The stored 13 November issue traced** from its own commit: 22 figures ok, 0 failed. Its two story keys are not in main's `news_stories` (they are on the red branch).
- **Row 173 (new, fixed):** under "Next week", "No dated events held this week: ... dated in the week ahead" read as if no event falls this week. Now: "No event of the week ahead is held: ...".
- **Row 174 (new, fixed):** W46 set "Oil settles $3 higher ..." (the settle of 11 November) beside the week's Brent closes, +0.30 USD/bbl. The line now gives the story's own day's close against the close before it, +1.98 ("92.14 USD/bbl on 2026-11-11, against 90.16 on 2026-11-10"), when held; else the week's pair.
- **Seen, for Samuel:** a story opening prints its figure twice ("**1,200 MW**: ... at 1,200 MW Ohio campus"; "**USD 74 billion**: SpaceX plans USD 74 billion ..."). The leading bold figure is the owner's "numbers first", and taking the figure out of the headline would garble some ("at Ohio campus"). Default: kept.
- Tests: `Row173NextWeekSaysTheWeekAhead` (1), `Row174AStorysMoveBesideItsOwnDay` (3). The 72 files: 1,382 passed, 20 skipped. The Roundup's method note carries both rows.
- **Row 11:** moved to `66e8ea25a`, now chains 252 and 254.
- **Row 11 landed in part** while this session ran: rows 151 to 160 (to `e547f598f`) at `f71fda27e` (desktop window 2's session 4011, 0 snapshot differences). The desk's session 4012 takes the newer head. The rebase conflict on the row was resolved by keeping the desk's state cell and adding the head that waits. `origin/main` was merged into the stack again as `3c8f5cab7` (docs and queue files only), and row 11 moved there: rows 161 to 174 wait.
- **The build step is closed:** row 152, the stack's one site change (`site/lib/digest.ts`), is among rows 151 to 160, and those passed the desk's `land_check.py` with its build (session 4011). Rows 161 to 174 change no site file. The memory wait was stopped. `site/node_modules` in the worktree goes with it at the clean-up.

## Session 3474: the stored W46 Roundup

- Not written yet: the Roundup of W46 is written on Sunday 15 November at 23:00 UTC, and it is Friday evening. Skipped; the next file carries it.

## Session 3475: the 13 November issue's landing

- `wip/red-daily-2026-11-13` (`7423bf708`) has not landed: `docs/digest/2026-11-13.md` is not on main. The first issue after it (Monday 16 November) is not written either. Skipped; the next file carries both.

## Session 3476: row 11's clean-up

- Row 11 has landed only in part (rows 151 to 160), so the worktree `erw-3457` and `wip/3457-periodicals` stay. Skipped.

## Session 3477: the stack's W45 and 28 September read whole, row 175

- **W45 on the stack, read whole:** nothing new in code. Three things seen and kept. The opening's "Named in the week's stories: Oil Prices Rebound Sharply After Brutal Midweek Rout" stands beside Brent's fall of 18.6%; row 104 counts a title with words of both directions as agreeing, and a rule letting the first word decide was tried and reverted, since row 104's own case "swing higher then lower" ends on its last. The Deals table's US-first order follows the rows' place fields (the data machine's). "[source]" after a why line and "[Source]" alone are by design (session 1882).
- **Row 175 (new, fixed):** the stack's 28 September printed "adds export volume at an US LNG project". The scorer wrote "a major US LNG project"; the cleaner took out "major" and chose the article by the spelling of "US". A word in capitals said from "U" now takes "a". Six stored scorer lines have that shape.
- Tests: `Row175AUSProject` (1), failing on main. The 72 files: 1,383 passed, 20 skipped. The Digest's method note carries the row.
- **Row 11:** moved to `ad894d3e8` (rows 161 to 175 wait).

## Session 3478: row 176

- **Row 176 (new, fixed):** the stack's 28 September printed "[bloomberg.com] (via Google News)" beside "[Bloomberg.com]" in every other item. The feed names some stories by their address (jpt.spe.org 50 stored, hartenergy.com 22, bloomberg.com 20, nyiso.com 29, partners.wsj.com 15); rows 133 and 134 had named only ft.com and wsj.com. An outlet named by its address, or a subdomain of it, now reads as its other links name it. An address not listed stays as written.
- Tests: `Row176AnOutletByItsName` (2). The 72 files: 1,385 passed, 20 skipped. The Digest's method note carries the row.
- **Row 11:** moved to `7ce9062d0` (rows 161 to 176 wait).

## Session 3479: every stored Digest again, row 177

- The 17 stored Digests ran again on the stack with rows 165 to 176 and were scanned for mechanical slips: articles, outlets named by address, doubled words, stray spaces, unstyled sums outside the publishers' titles. Clean, apart from "Wagga Wagga" (a place) and 22 October's fun fact, "from US$3/barrel". The fact is printed word for word as its source was checked, and `check_digest.py` holds the issue to that wording, so it is kept.
- **Row 177 (new, fixed):** the block printed the country three ways: "Generation capacity, United States", "Storage dispatched, USA", "Transmission, US". These are the scorer's region as written (US 5,172, United States 794, USA 106), and the topic key read them as three regions. Both now read "US". Over the 17 issues, the block's places change, and two pairs fold as one topic: 21 October's heating oil and diesel policies, and 6 November's Lambda campus under the datacenter commentary (the owner's "one sector in one region" rule).
- Tests: `Row177TheCountryIsUS` (2); 14 pins of `test_periodicals_1973.py` read "US". The 72 files: 1,387 passed, 20 skipped.
- **Row 11:** moved to `48b5fb1df` (rows 161 to 177 wait).
