# Session 1435 report: the first dry run of the Digest, read as a reader, the preview sent

Energy Research Warehouse (ERW), session 1435 (chain 149's "1432"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 01:20 to 01:35 UTC. Model Fable 5.1, high effort. **Model spend USD 0.0312** (the Digest's headlines USD 0.0255, the numbers summary USD 0.0057; cap USD 4; the ledger off as session 2705 ran it, the cost from the run log `warehouse/output/logs/news_brief_20261106T012255Z.log`). No warehouse data written; one preview email to the fixed recipient; web requests to the Claude API (two calls), the ERW's own database (reads) and Resend (one send).

## What is in your inbox

- 01:27 UTC, **"[preview, dry run 1435] ERW Daily | Henry Hub natural gas: 2.63 USD/MMBtu, up 3.5% on the close before"** (Resend id `01a1ae78-2528-723b-893b-6d4d6b405b07`), to the one fixed recipient of `DIGEST_RECIPIENTS`, never a subscriber; the day's real send not claimed. The before: the v2 code as landed by session 1434 on the stories held; the after comes from session 1451 on the same stories.

## What it did, with commits

- **The stories**: `warehouse/output/news_stories.csv` on main holds scored stories to about 08:00 UTC on 26 October (scored at 15:02 UTC that day); the daily run's `news_score` failed every day from 27 October to 5 November, so the missed days are not pulled. The dry run is the Digest of **Monday 26 October 2026** (`--date 2026-10-26 --now 2026-10-26T15:45Z`), its window from the previous issue's end (23 October 15:45 UTC, item 3's rule) to the cutoff: 72 hours, 311 scored stories. The numbers are the live set's as read on 6 November (fault 1).
- **The run**: `runs/periodicals_dryrun/s1435/run.sh` (the main checkout's code, which is the v2 since 01:17 UTC): `digest/2026-10-26.md` (the markdown), `email/2026-10-26-daily.txt` and `.html` (rendered by `email_digest.render`, then the send's own copies), `page/2026-10-26.html` (rendered by the site's `renderDigest` through `site/lib/markdown.ts`, in the gate's worktree: 35 check marks, one fold), `shots/email-390.png`, `shots/page-390.png`, `shots/page-1280.png` (the page render carries no site stylesheet, its structure only).
- **The reading**: `docs/reviews/periodicals-faults-2026-11-05.md` (`95fc7e54b` on `wip/1435-periodicals`): 24 rows, each with the line quoted, the fix and the session; 22 open for sessions 1437 to 1450, 2 for the owner.
- `scripts/periodicals_counts.py` committed (session 800's measures, never in git): adjectives, repeated figures, sector concentration, Google addresses, fold words, figures without a key, one row an issue.

## What a sharp reader sees (the short list; the file has the rest)

1. **The opening number is a 9-cent Henry Hub move dated 3 November** in an issue cut off on 26 October: the numbers block reads the newest rows with no bound at the cutoff (fault 1), and the chooser takes a move no story names while four stories put oil at 114 to 120 USD/bbl (fault 2).
2. **The numbers block's story rows print the headline whole** with the figure twice ("1,000 MW: Gingerah Energy refers 1,000 MW data centre ..."), carry no key, and the policy row holds a Brent price from an outlet beside EIA's Brent in the market row (faults 4 to 6).
3. **The why lines restate the headline** ("LNG or gas project faces executive departures and alleged Russian involvement claims; geopolitical risk to US energy sector") or carry a verb instead of a fact: five of thirty say "signals" (faults 7 to 11); one why line is the headline again because "$100" and "USD 100" count as different (fault 10).
4. **The chart is a county-level ONRR revenue line item in Louisiana**, matched to the day by the token "oil" in its entity id, captioned by the id, "552.53 robust standard deviations" (faults 14, 15). The 23 October preview had the same (Fremont County, Wyoming).
5. **Two oil items in the top ten** (fault 12); 15 of 37 links reach Google (fault 23); 295 words above the fold, under the floor (fault 22); the email overflows at 390 (fault 17).
6. On the page, "What moved" is drawn as the news index's hold line, so a visitor's issue is a numbers card (fault 19, the owner's).

Counts (`scripts/periodicals_counts.py` and `brief.above_fold_words`): items 30, adjectives of the list 0 (the landed rule holds), repeated figures in items 0, top-ten sector concentration 2 (lng), Google links 15 of 37, fold words 295 (176 by the script's narrower count), figures without a key in the block 1 by the script (2 by hand: both story rows).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1435"` | 0 | on duty to 17:22 UTC |
| `brief.py --date 2026-10-26 --now 2026-10-26T15:45Z` (the model, cap USD 4) | 0 | 311 stories, 286 clusters, 2 calls, USD 0.0312 |
| `email_digest.render` (daily) | | 672 words of text, the character once, two images |
| `renderDigest` (the site's renderer) | 0 | 16,420 bytes, 35 marks, 1 fold |
| the three screenshots | 0 | under `shots/` |
| `send_preview` (prefix "[preview, dry run 1435] ") | 0 | 1 of 1 fixed recipient, 01:27 UTC |
| em dashes in the files written | | none |

## Decisions made without you

- The dry run is of 26 October, the newest day the warehouse holds scored stories, not of 5 November (no story since 26 October is scored); said in the faults file's head.
- The subject's prefix is set by assigning `email_digest.PREVIEW_PREFIX` in a six-line wrapper (`runs/periodicals_dryrun/s1435/`), not by a flag: the module's send path is unchanged.
- The page's HTML is the site's renderer over the markdown (no build of a page for a file outside `docs/digest`); its screenshots show structure, not the brand's styling.
- The counts script is committed now (session 1453's step), since sessions 1437 to 1444 measure before and after with it.
- Faults 19 and 20 are the owner's (the news index hold's scope on the page; the email's fold link while the site is in review), not fixed.

## For Samuel's ruling

- The news index hold on the page covers whole sections ("What moved" shows only the hold line), so the v2 issue a visitor sees is the opening number, the numbers, the chart and the fun fact. Whether the hold should cover the held outlets' titles and links only.
- The email's "More on the site" link goes to GitHub's copy of the issue while every page is in review.
