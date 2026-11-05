# Chain 131 on the old laptop (25 October 2026, 06:36 to about 07:55 UTC): the periodicals in the v2 shape, for Samuel

Energy Research Warehouse (ERW), session 2707, written on samueloldlaptop on 25 October 2026. Chain `queue/done/131-night-25-october-code-periodicals-v2.md`, sessions 2700 to 2707. Model Opus 5.5. Model spend USD 0.063 (session 2705 only; cap USD 3). No warehouse data written; nothing posted; two preview emails sent to the fixed recipient.

## First: what to know

1. **Nothing of the chain is on main; Monday's Digest and tonight's Roundup are the old code's.** The landing gate never ran: the chain's line is 4 GB free before a build or a gate, and this laptop (7.3 GB in all) read 2.04, 2.18, 1.96 and 2.06 GB at four reads. The database probe passed (0.40 s). Everything is on `wip/2706-periodicals` (`602d995f`), merged with main at 07:45 UTC, pushed; the commands that land it are in `archive/sessions/SESSION_2706_REPORT.md` on that branch, "To finish".
2. **In your inbox** (sent once each, `email_digest.py --preview`, the fixed recipient only):
   - 07:41 UTC: `PREVIEW v2: ERW Daily | Brent crude: 115.22 USD/bbl, down 3.0% on the close before` (the Digest of 23 October, re-rendered by the v2 code from the saved stories and the live set as read on 25 October).
   - 07:42 UTC: `PREVIEW v2: ERW Weekly | The Nuclear Company proposes 6,600 MW of AP1000 reactors in eastern Kentucky; WTI Cushing crude +13.1% on the week` (W43 to 07:40 UTC on Sunday; no chart of the week yet).
   - Their markdown, HTML and text are on the branch under `docs/digest/preview/` and `docs/roundup/preview/`.
3. **The rulings' defaults are applied on the branch** (your rule of 18 October; each item its own commit, reversible by exception): Digest items 1, 3, 4, 6(b), 6(c), 7, 8, 13, 14, 15 (session 2701); Roundup items 10, 11 and the gate's item 19 (session 2702); items 2, 9, 12 and 16 needed nothing.
4. **Lengths are under the brandbook's bands.** The 13 saved Digests regenerated without the model read 171 to 348 words above the fold (band 350 to 450); the Roundups W40 395, W41 518, W43 307 (band 500 to 650), every development 37 to 54 words (band 60 to 90). Nothing was padded; the modules at their fixed sizes come to less.

## One line a session

| Session | What it did |
|---|---|
| 2700 | `wip/818-periodicals` (sessions 801 to 817) and `wip/2206-periodicals-fixes` merged with main (three conflicts, both sides kept); `check_digest` on the archive 147 ok, 0 failed, 2 revised; the gate not run (memory) |
| 2701 | the Digest's defaults: 1 no held digit; 3 the window from the previous issue's end, 96 hours at most; 4 the tie-break by outlets then time; 6(b) a chart floor of 1.5; 6(c) no dismissed draft as the chart; 7 a pun held to its source (the kWh and 2 October puns cut); 8 the 14 October page's one line; 13 the topic key sector with region (two items a sector at most); 14 the also lines outside the fold count; 15 a held outlet keeps its link |
| 2702 | the Roundup's defaults: 10 the missed week said (W42); 11 the deals and datacenter tables' floor, US first, 15 at most; 19 "license needed" counts toward a page's floor in check-values and land_check |
| 2703 | the Digest in the v2 order (masthead, opening number, numbers block, what moved, More, chart, fun fact, footer); the page's fold; the email; the chart's source line; 13 regenerations and their traces |
| 2704 | the Roundup in the v2 order (masthead with the missed week, opening number, five numbers, what mattered, More, chart with a reading line, next week from the policy monitor's dated deadlines, the week's fun fact, footer); its page, checker and email |
| 2705 | the character (`site/public/brand/erw-character.svg`, `erw-character-48.png`), in the fun-fact module of both emails only; the two previews rendered with the model and sent |
| 2706 | `docs/brand.md` section 10 (the templates, the character's rule, the open send times); the suite after the merge with main (1,261 tests, one wording failure fixed); the gate not run (memory) |
| 2707 | this note; the queue step |

## For Samuel's ruling

- **The send times.** The Digest: the brandbook's weekdays 09:00 Eastern with an 08:30 Eastern cutoff; today the daily run starts at 14:00 UTC (`.github/workflows/daily-prices.yml`, its `schedule` line, and the pg_cron job of migration 015). The Roundup: the brandbook's Fridays 10:00 Eastern with a Thursday 18:00 Eastern cutoff; today Sundays 23:00 UTC (`.github/workflows/roundup.yml`, its `schedule` line, and the pg_cron job of migration 022). No chain changed either.
- **Item 6(a)**: the source for "EIA's newest month is preliminary" under a chart of an EIA state series.
- **Items 17 and 18, for the data machine**: the chart of the week re-drawn for the measure the week's stories point to (`warehouse/analysis/run.py`); a US48 row in `eia930_daily_demand` so the Digest's demand line can compare with the same weekday a year before.
- **The mark's chest** once you choose among the five marks (the character's chest is the current E).
- **The length bands** of both periodicals against their fixed modules (above).
- **A calendar table** for the Roundup's next week (dated hearings, auctions, data releases, CODs), which today can only quote the policy reads' deadlines.
- **Where the landing runs**: this laptop cannot free 4 GB.

## To finish

1. The landing of `wip/2706-periodicals`: the eight steps of `archive/sessions/SESSION_2706_REPORT.md` ("To finish") on that branch, on a machine with 4 GB free, outside 14:00 to 16:15 UTC (and outside 15:00 to 16:00 UTC, which would touch `brief.py` and `email_digest.py` while the daily run writes and sends).
2. Screenshots of the v2 pages at 390 and 1280 (sessions 2703 and 2704) from the gate's kept build.
