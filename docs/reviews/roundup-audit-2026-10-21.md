# The weekly Roundup, read as its most demanding reader

Energy Research Warehouse (ERW), session 444, 21 October 2026, the chain `queue/done/017-night-21-october-third.md`, on portable-laptop (code role). Samuel's ruling of 21 October: the Digest and the Roundup are the only two periodicals, and both must be perfect before anything else is written for the public. This file reads every Roundup the repository holds as session 442 reads the Digest (`docs/reviews/digest-audit-2026-10-21.md`, written in parallel). No code was changed, nothing was posted or sent, no model was called.

## What the repository holds

| Issue | Page | Email as sent | Chart files | Written |
|---|---|---|---|---|
| 2026-W39 (21 to 27 September) | `docs/roundup/2026-W39.md` | no copy kept | `docs/analysis/2026-W39/` | 28 September 08:55 UTC, model claude-sonnet-5 |
| 2026-W40 (28 September to 4 October) | `docs/roundup/2026-W40.md` | `docs/digest/email/2026-W40-roundup.txt` and `.html` | `docs/analysis/2026-W40/` | 4 October 23:05 UTC, model claude-sonnet-5-5 |
| 2026-W41 (5 to 11 October) | `docs/roundup/2026-W41.md` (and `latest.md`, identical) | `docs/digest/email/2026-W41-roundup.txt` and `.html` | `docs/analysis/findings/peak_hour_moved_1600x900.png` | 11 October 23:22 UTC, no model (the daily cap was reached) |
| 2026-W42 (12 to 18 October) | **none: not written, not sent** | none | none | the run of 18 October stopped at its restore (Redivis's 100 GB export cap, `archive/sessions/SESSION_305_REPORT.md`); session 326 ran it dry to `runs/s326/` on lab-desktop |

Beside them, not an issue: `docs/roundup/drafts/2026-W43.md` on `wip/findings-oct20` (the findings hunt's draft of the chart section for 25 October; not on main, not sent). It is not audited here.

**Three issues in 21 days; one Sunday missed.** A reader who subscribed on 12 October has received nothing from the Roundup. W42's week held the PJM "Maximum Gen Alert" with a DOE emergency order (T&D World, 13 October), Google's 20-year PPA with AEP for a 702 MW Wyoming fuel cell project (Bloomberg, Reuters, Data Center Dynamics, Hart Energy, 14 October), FERC's first LNG authorization program (FERC, 15 October) and Brookfield and NextEra's USD 100 billion AI hub (OilPrice.com, 15 October), all in `news_stories`. No later issue says the week was missed.

## How the numbers were traced

Every figure of each "Numbers" section, chart and table was recomputed from `warehouse/output` on this machine by `runs/chain_oct21_third/s444/trace*.py` (not in git; outputs beside them), with the Roundup's own rules (`warehouse/news/roundup.py` `numbers()`, `brief.mean2`, the ISO's local week). Key form: `table|filter|period`.

**A limit of this machine.** Its copies of the rolling-window tables end on 3 October (`iso_dam_hub_prices` to 2026-10-03 14:07 retrieval, `nyiso_dam_zone_prices` and `isone_dam_zone_prices` to 1 October, `policy_actions` to 1 October, `eia_fuel_spot_prices` to 29 September). A read of the same tables through the `erw` package with `ERW_BACKEND=supabase` returned the same rows as the local files (the database is timing out tonight, the chain's preamble). So W39 is traced whole; W40 in part; W41's numbers are **untraceable here**, not wrong: they wait for a machine with current tables (the code machine's fix list, item 13).

### 2026-W39

| Figure in the issue | Key | Recomputed | Verdict |
|---|---|---|---|
| ERCOT HB_NORTH 41.84, before 39.90, +1.94 | `iso_dam_hub_prices\|ercot_dam,HB_NORTH\|2026-09-21..27 America/Chicago` | 41.84 (168 of 168 h); 39.90 | equal |
| CAISO TH_SP15_GEN-APND 36.84, 36.79, +0.05 | `iso_dam_hub_prices\|caiso_dam,TH_SP15_GEN-APND\|...` | 36.84; 36.79 | equal |
| NYISO N.Y.C. 39.36, 45.97, -6.61 | `nyiso_dam_zone_prices\|N.Y.C.\|...` | 39.36; 45.97 | equal |
| MISO INDIANA.HUB 40.45, 75.37, -34.92 | `iso_dam_hub_prices\|miso_dam,INDIANA.HUB\|... EST` | 40.45; 75.37 | equal |
| SPP SPPSOUTH_HUB 33.96, 46.44, -12.48 | `iso_dam_hub_prices\|spp_dam,SPPSOUTH_HUB\|...` | 33.96; 46.44 | equal |
| ISO-NE .H.INTERNAL_HUB 36.12, 44.30, -8.18 | `isone_dam_zone_prices\|.H.INTERNAL_HUB\|...` | 36.12; 44.30 | equal |
| Highest real-time price 521.36 at N.Y.C., 2026-09-25 22:45 UTC | `nyiso_rtm_zone_prices\|max\|2026-09-21..28 08:55 UTC` | 521.36, N.Y.C., same interval | equal |
| Henry Hub 2.90 on 09-22, 2.97 on 09-18 | `eia_fuel_spot_prices\|eia:henry_hub` | 2.90; 2.97 | equal (but see fix 2) |
| WTI 96.41, 101.44, -5.03 | `eia_fuel_spot_prices\|eia:wti_cushing` | 96.41; 101.44 | equal |
| Brent 114.89, 119.66, -4.77 | `eia_fuel_spot_prices\|eia:brent` | 114.89; 119.66 | equal |
| US48 peak 608,317 MW, 2026-09-21 21:00 UTC | `eia930_all_demand\|ba=us48,demand_mw\|max` | 608,317, same hour | equal |
| Chart: medians 29.01, 30.11, 50.09; quartiles; latest-7-day gap 28.08 | `iso_rtm_hub_prices\|ercot_rtm,HB_NORTH\|2026-08-28..09-26 local` (the template's blocks) | 29.01, 30.11, 50.09; Q1 23.02, 25.21, 34.43; Q3 34.88, 39.34, 70.68; gap 28.08 | equal |
| 27 deals, 3 datacenter facilities | `energy_deals\|event_date in week`; `datacenter_projects\|first_story_at in week` | 29 and 3 today | 2 deals were extracted after the issue; not a fault of the issue |

The written summary above the table (model-written) restates the table's numbers correctly. Its words "edging up slightly" for ERCOT's +1.94 (4.9 percent) are a judgement the table does not need.

### 2026-W40

| Figure in the issue | Key | Recomputed | Verdict |
|---|---|---|---|
| Day-ahead: ERCOT 37.45, CAISO 44.53, NYISO 45.94, SPP 29.60, ISO-NE 39.11 | as W39 | this machine holds 144 or 120 of 168 hours of the week | untraceable here |
| The "week before" column (41.84, 36.84, 39.36, 40.45, 33.96, 36.12) | as W39 | equal to W39's figures | equal |
| MISO "not in the warehouse (144 of 168 hours)" | `iso_dam_hub_prices\|miso_dam,INDIANA.HUB` | 144 of 168 here too | consistent |
| Highest real-time 1372.09 at N.Y.C., 2026-10-04 02:45 UTC | `nyiso_rtm_zone_prices` | this machine's copy ends 1 October | untraceable here |
| Henry Hub 3.18 on 09-29, 3.21 on 09-25, -0.03 | `eia_fuel_spot_prices\|eia:henry_hub` | 3.18; 3.21 | equal |
| WTI 96.16 on 09-29, 85.23 on 09-25, +10.93 (+12.8%) | `eia_fuel_spot_prices\|eia:wti_cushing` | 96.16; 85.23 | equal, **but the base is an outlier**: WTI read 95.88 on 09-24, 85.23 on 09-25, 99.37 on 09-28 (-11.1 then +16.6 percent), while Brent read 120.92, 116.01, 119.97 (-4.1, +3.4). The issue's headline sentence ("WTI crude rose 10.93 USD/bbl") rests on one close. For the data machine: confirm 85.23 against EIA's page |
| Brent 113.96, 116.01, -2.05 | `eia_fuel_spot_prices\|eia:brent` | 113.96; 116.01 | equal |
| US48 peak 585,887 MW at 2026-09-30 21:00 UTC | `eia930_all_demand\|ba=us48` | 585,785 at the same hour (this copy retrieved 1 October; EIA revises its hourly demand) | same hour; the value moved by EIA's revision, not a fault |
| Chart: 59 deals in 2026-09, robust z 2.73; m and a 91 | `energy_deals\|event_date month\|2025-10..2026-09` | 59 in 2026-09; m_and_a 91; every month equal (17, 22, 11, 33, 41, 42, 38, 33, 23, 15, 11, 59) | equal, **but the fact is the ERW's coverage, not the market** (fix 3) |
| 40 deals, 22 datacenter facilities | as W39 | 40 and 22 | equal |
| Policy of the week: Sabine Pass Stage 5 FEIS, 2026-09-30; SMR Palisades, 10-01; DOE reserve release, 09-29 | `policy_actions\|title` | the Sabine Pass row (09-30, significance 7) and the DOE release (09-29, 6) are held; the Palisades SMR notice of 10-01 is past this copy's end | 2 of 3 traced |

### 2026-W41

Every day-ahead figure of the week (41.94, 57.60, 39.78, 34.67), the highest real-time price (1027.12 at SPPNORTH_HUB, 2026-10-08 22:45 UTC), the three fuel closes of 10-06 and 10-02, the US48 peak (575,114 MW) and the policy rows (Clinch River construction permit, Project Matador draft EIS) lie past this machine's copies: **untraceable here**. The "week before" column equals W40's printed figures (37.45, 44.53, 45.94, 39.11), so the two issues agree with each other.

The chart of the week traces: from `site/public/findings/erw_2026_peak_hour_solar.csv` (the card's own download), ERCOT's median peak hour 15 (2019) and 19 (2025), evening share 24.9 and 71.0 percent, midday share 32.9 and 3.8 percent, solar 2,592 and 30,018 MW, most common hour 16 (15.3 percent) and 19 (22.2 percent), 365 and 365 days; CAISO 2025 median 17, evening 34.3 percent, solar 24,009 MW. All equal. Session 381 replicated the card's figures from its CSVs (304 of 304 for the nine library cards, `site/public/findings/erw_2026_research_replication.py`).

## Every link

All 200 distinct addresses of the three pages and the two saved emails were listed (`runs/chain_oct21_third/s444/links_all.txt`). Each host's robots file was read first; then one HEAD a link (a GET, body discarded, only where HEAD was refused), 15 s timeout, a User-Agent naming the ERW, no paused host. **147 requests of the ceiling of 150**, each in `runs/chain_oct21_third/s444/links.csv`.

| Result | Links |
|---|---|
| Answered 200 | 117 of the 121 asked |
| Refused to an automated agent (HEAD 403, then GET 403): Utility Dive | 4 (not shown broken; a person's browser opens them) |
| Not asked: the robots file disallows the path (news.google.com, 3 sampled) or refused itself (naturalgasintel.com, energy-storage.news: robots 403) | 7 |
| Not asked: the other Google News links (the ceiling; the robots file closes the path anyway) | 72 |

**75 of the 200 links (37.5 percent) are `news.google.com/rss/articles/...` addresses**, and 80 percent of the scored stories since 21 September carry one. `news_stories.url_resolved` says, for every one of the 75: "no: Google served its own page, no redirect to the outlet". A reader sees "Reuters" and lands on Google, if Google lets them through; the ERW cannot check those links at all under its own robots rule. Fix 4.

The site's own links resolve: `/about#digest`, `/policy`, `/roundup/2026-W40`, `/roundup/2026-W41` answer 200; `/analysis` and `/analysis/card/peak_hour_moved` redirect to `/research` and `/research/card/peak_hour_moved` (the redirect in `site/next.config.ts`). Every page is in review, so a visitor who clicks "All of ERW's Roundup" in the email sees the in-review page, not the issue. The W41 email's chart (`raw.githubusercontent.com/.../peak_hour_moved_1600x900.png`) answers 200.

## The selection, against what a reader of the week would expect

The rule (`roundup.py`, `brief.build_clusters`): the five clusters with the highest significance, ties broken by AI-power relevance, then story count. Judged against the week's scored stories in `news_stories` (the ERW's own record of what the feeds carried).

**W39.** The five match the ranking. Weekend item 1 (TotalEnergies' Absheron FID, significance 9) was the week's single highest story. Left out at significance 8, each beaten by the AI tie-break: Fervo's first power at the 900 MW Cape Station geothermal plant (Data Center Dynamics, JPT, 25 September), the second federal ruling against the Solar for All cancellation (Utility Dive, 25 September), Qatar's extended LNG force majeure (Reuters, Bloomberg, LNG Prime, OilPrice.com, 28 September; in the next week by date). A US power reader would expect Fervo.

**W40.** Two of the five are one event: item 1 "South Korea to invest $120 billion in U.S. nuclear projects" (ANS) and item 2 "US Commerce outlines USD120 billion framework for six AP1000 and two APR1400 units" (World Nuclear News) are the same package, in two clusters; a third and fourth cluster of it ("Trump to unveil $200 billion investment ... by South Korea", Bloomberg, FT, Reuters; the Commerce and Korea "Project Star" row) sat below. Weekend items 2 and 3 are one event too (OPEC+ keeping November quotas: WSJ and Reuters; then Bloomberg's "deal outline"). So W40 showed 8 items for 6 events. Left out: "Over 600 Projects Enter Phase 1 of PJM's New Interconnection Process" (PJM newsroom, 30 September, significance 8) and TVA's Clinch River approval (ANS, Heatmap, Reuters, T&D World, 29 September, 6 stories), which became W41's policy of the week a week later.

**W41.** Item 2, "Amazon, Constellation sign 20-year PPA to expand Maryland nuclear plant" (Utility Dive, 5 October), repeats W40's item 4 (the same PPA, 30 September, 6 stories). The Roundup keeps no memory of the issues before it. Item 1's headline is a publisher's own title ("Google enters massive 3.6-GW power deal"): the no-model path prints "massive", a word `docs/voice.md` forbids. Left out at significance 8: the Supreme Court's questions on oil companies' bid to end climate suits (Bloomberg, Reuters, WSJ, Heatmap; 8 stories), which sat below on the AI tie-break.

**Deals and datacenters.** Every row the extractors dated in the week is printed, with no floor and no US filter: W40 printed 40 deals (35 with no `country`) and 22 datacenter facilities, of which 6 carry a US state and 8 have no operator, no site and no MW; W41 printed 41 and 21 (6 with a US state). Sydney, Macau, Evora, Salo, Inzai, Incheon and Kaluga lead a section of a warehouse whose coverage is "US first, world later". Rows a reader would question as printed: "US" buying diesel from "Russia" (`fuel_supply`, confidence 0.6, from the story of Russia lifting its export ban, W41); Vistra's DOE loan twice (W40, 2 October, USD 4.0 billion, buyer "US"; W41, 5 October, USD 4.2 billion, buyer "Department of Energy"); Amazon and Constellation twice (W40, 190 MW; W41, "nuclear expansions", whose printed story link is the Google and Constellation story); Sempra as LNG seller to Petrobras on a story whose first link is "cheniere-petrobras-seal-long-term-lng-spa" (W40); "Virtus" with US dollars "not stated" on a story whose address reads "virtus-secures-245bn" (W40). Two datacenter rows (ME and AK, W40) are one Heatmap story.

## The charts

| Issue | Fact | Chart | Caption | Verdict |
|---|---|---|---|---|
| W39 | The latest seven days' peak-minus-midday median gap at HB_NORTH, 28.08 USD/MWh, robust z 2.46 | three grouped bars (Q1, median, Q3) for three blocks over 30 days | traced, plain | **right fact, wrong chart**: the notable number (the week's gap against its own 89-value history) is not on the chart; quartiles as side-by-side bars read as three categories, not a spread |
| W40 | 59 deals in September 2026, robust z 2.73 | stacked bars by nine deal types, twelve months | "the most common type was m and a" | **wrong fact**: September's count rose with the ERW's own news volume, not the market. Scored stories: 221 in August, 3,199 in September (`news_stories`, the live feeds' first retrieval is 2026-09-25; earlier months are a thinner backfill). The z measures the ERW's coverage. The second-largest type is "other" (58) |
| W41 | ERCOT's peak hour moved from 15 to 19 as solar went from 2.6 to 30.0 GW | the card's wide chart | long, traced, states what it does not separate | right fact, right chart. Two gaps: CAISO's most common peak hour in 2025 is 06:00 (14.8 percent of days, the card's CSV), which the caption leaves out while it gives ERCOT's; and "midday" is 10:00 to 15:59 here but 12:00 to 15:59 in `peak_premium_block` (W39), two definitions of one word across the ERW's charts. The card is now superseded by `peak_hour_grids` (five grids); the email's link still resolves |

## The wording

- No em or en dash in any issue or email (counted: 0 and 0 in each of the seven files).
- "massive" (W41 item 1, a publisher's title printed by the no-model path).
- "docket Docket No. CP24-75-001, Docket No. CP25-505-000, ..." (W40) and "docket Docket No. 50-615" (W41): the word twice.
- Federal Register titles printed whole: W40's policy title runs to 260 characters.
- W41's policy header dates the notice 2026-10-05 (publication); its Timeline line says "The notice is dated 2026-10-01" (signature). A reader sees two dates for one notice.
- Code labels printed as words: `m_and_a`, `project_finance`, `equity_raise`, `behind_the_meter`, `smr`, `fuel_supply` in the deals tables; "m and a" in the W40 chart's legend and note; sector labels in parentheses ("datacenter power").
- "Fuel spot prices, weekly change": each "change" is between two closes two trading days apart (W39: 09-22 against 09-18; W40: 09-29 against 09-25; W41: 10-06 against 10-02). The base is right (the previous week's last close); the newest close is only the week's Tuesday, because EIA's spot series lags by about five days. The label says weekly; the figure is not (fix 2).
- "Highest real-time price of the week" compares 15-minute series with MISO's hourly one and with ISO-NE's hourly table; the unit of the maximum is not the same across ISOs.
- The issue's title changed between W39 ("Energy Roundup") and W40 ("ERW's Roundup"); the W39 page is still titled the old way. Not a fault of the issue; a reader of the archive sees two names.

## The email as sent

The two saved emails (`docs/digest/email/2026-W40-roundup.*`, `2026-W41-roundup.*`) were rendered by `warehouse/news/email_digest.py` `render()`:

- **W41's email does not say its headlines are the publishers' own titles.** The page carries the line (`brief.NO_MODEL_LINE`); `render()` skips every line above "## Weekend", so the email reader is not told (0 matches of "publishers' own" in either email file, 1 on the page).
- The period and story count ("for 2026-10-05 to 2026-10-11, to 2026-10-11 23:22 UTC, from 1806 scored stories") is dropped the same way.
- The deals and datacenter sections are not in the email by design; the email does not say they exist beyond "All of ERW's Roundup".
- The order differs: the email puts the numbers before the policy of the week; the page puts policy first.
- The text email prints the chart's subtitle with its markdown asterisks (`*In Texas the day's dearest hour ...*`).
- The numbers table becomes "ISO: ERCOT; Hub or zone: HB_NORTH; This week USD/MWh: 41.94; ..." lines in the text part: complete, but long.
- No copy of W39's email is in the repository; whether it was sent is not recorded here.

## Fixes for the code machine, ranked

Each with the file it lives in and the test that would prove it. None was made here.

1. **One event, one item, within an issue and across issues.** W40 showed 8 items for 6 events; W41 repeated W40's Amazon and Constellation PPA. `score.py` clusters by the model's `is_duplicate_of` against at most `REFERENCE_MAX = 400` earlier stories while a week holds 1,092 to 1,850 scored ones; `brief.unique_items` compares only a normalized headline and the first link. Files: `warehouse/news/brief.py` (`unique_items`: a second key of shared parties and a shared figure, such as "$120 billion"), `warehouse/news/roundup.py` (drop a cluster whose lead story is already an item of the previous issue's page). Test: `tests/` fixture of W40's two South Korea clusters and two OPEC+ clusters gives one item each; a fixture W41 with W40's page present drops the Maryland PPA.
2. **The fuel table's "weekly change" is a two-trading-day change.** File: `warehouse/news/roundup.py` `numbers()` (report the latest complete trading week EIA holds, last close against the last close of the week before, with both dates; flag a close that moved over 8 percent in a day while the other crude moved under 5). Test: with `eia_fuel_spot_prices` as it stood on 4 October (closes to 09-29), W40's rows compare 09-25 with 09-18 and are labelled "the week to 25 September"; WTI's 85.23 of 09-25 is flagged.
3. **A chart of the week must not measure the ERW's own coverage.** File: `warehouse/analysis/templates/deals_by_month.py` (and `datacenters_by_state.py`, which reads the same extracted tables): divide by scored stories in the month, or make the template ineligible in `warehouse/analysis/run.py` until twelve months of live feeds are held (from 2026-09-25). Test: with the `energy_deals` and `news_stories` of 4 October, the template's headline is not eligible, and W40's pick would have been the next eligible template.
4. **Google News links.** File: `warehouse/news/ingest.py` (the resolver that writes `url_resolved`) and `warehouse/news/brief.py` `link_text`. Until a link can be resolved, say so beside it ("via Google News") so the reader knows where it goes. Test: a rendered issue has no `news.google.com` link without the words beside it; a resolved story prints the outlet's address.
5. **The email must carry the page's disclosures.** File: `warehouse/news/email_digest.py` `render()`: keep the line under the title (period, story count, and `NO_MODEL_LINE` when present); strip markdown emphasis in the text part. Test: `render("docs/roundup/2026-W41.md", "roundup")` text and HTML contain "publishers' own titles" and "1806 scored stories"; the text part has no `*` emphasis markers.
6. **A missed week is said.** File: `warehouse/news/roundup.py` (when the previous ISO week has no `docs/roundup/<week>.md`, a line under the title names it and points to the week's stories on the site); `.github/workflows/roundup.yml` already alerts the owner (session 119). Test: a run for 2026-W43 with no W42 file writes the line naming 2026-W42.
7. **Deals and datacenters: a floor, US first.** File: `warehouse/news/roundup.py` (the two table sections: rows with `confidence` at or above 0.7 and at least one of operator, site or MW; US rows first; at most 15 a section with the count of the rest and a link to `/deals` and `/datacenters`). Test: on W40's rows the datacenter section prints no row with no operator, site and MW, and US rows lead.
8. **Deal rows extracted twice or wrongly.** File: `warehouse/deals/extract.py` (one deal across weeks by buyer, seller and asset; a deal needs two parties named in the story as parties to it). Test: the Vistra loan of 2 and 5 October and the Amazon and Constellation PPA of 30 September and 6 October each resolve to one `event_id`; "US" and "Russia" for the export-ban story yields no deal.
9. **Policy wording.** File: `warehouse/news/roundup.py` `policy_of_the_week` (strip "Docket No." before joining; shorten a Federal Register title at its first semicolon with the full title on `/policy`; one date, labelled "published" or "signed"). Test: W40's and W41's sections contain no "docket Docket" and no title over 160 characters.
10. **Codes as words.** File: `warehouse/news/roundup.py` (a label map for `deal_type`) and `warehouse/analysis/templates/deals_by_month.py` (the legend). Test: no `_` inside a Type cell; "M&A" or "mergers and acquisitions" in the legend.
11. **The chart shows the number it calls notable.** File: `warehouse/analysis/templates/peak_premium_block.py` (a weekly peak-minus-midday gap series with the latest week marked, or the latest week's blocks beside the 30-day blocks). Test: the template's chart series holds the headline value at its period.
12. **One definition of midday.** Files: `warehouse/analysis/templates/peak_premium_block.py` (12:00 to 15:59) and `site/public/findings/peak_hour_moved.py` (10:00 to 15:59). Test: a shared constant both import, or each caption states its hours.
13. **Trace W40 and W41 where they can be traced.** On a machine with current tables, run `runs/chain_oct21_third/s444/trace.py` (copy it; `runs/` is not in git) with the two weeks' cuts, and add the results to this file. Test: the trace's printed figures equal the issues'.

## What the two periodicals share, so that one fix lands in both

| Shared part | Where | Used by the Digest | Used by the Roundup | Fixes above that land in both |
|---|---|---|---|---|
| Clustering | `warehouse/news/score.py` (`cluster_id` from `is_duplicate_of`, `REFERENCE_MAX`), `warehouse/news/brief.py` `build_clusters` | yes | yes | 1 |
| Ranking | `brief.build_clusters` sort (significance, AI relevance, story count, first date); `warehouse/news/rubric.md` | yes | yes | the AI tie-break (Samuel's ruling) |
| Repeats | `brief.unique_items`, `brief.assert_unique`, `brief.without_repeats` | yes | yes (and `roundup.policy_section`) | 1 |
| Headlines without a model | `brief.own_titles`, `brief.NO_MODEL_LINE`, `score.nodash` | yes | yes | the "massive" fault; 5 |
| Links | `brief.link_text`; `warehouse/news/ingest.py` (`url_resolved`) | yes | yes | 4 |
| Numbers | `brief.MAIN_HUBS`, `FUELS`, `mean2`, `rt_parts`, `Notes`, `cite_short`, `numbers_summary` | `brief.numbers_today` | `roundup.numbers` | 2 (the base close rule); the real-time granularity |
| Email | `warehouse/news/email_digest.py` `render`, `block`, `numbers`, `story_list` | yes | yes | 5 |
| Charts | `warehouse/analysis/style.py`; the findings' `daily_chart.py` (Digest) and `roundup_pick.py` (Roundup); `warehouse/analysis/run.py` templates | chart of the day | chart of the week | 3, 11, 12 |
| Deals and datacenters | `warehouse/deals/extract.py`, `warehouse/datacenters/extract.py` | where the Digest prints them | yes | 7, 8, 10 |

## Side findings outside the Roundup

- On this machine's copy of `iso_rtm_hub_prices` (retrieved to 3 October), every `ercot_rtm` row carries `variable` = `spp_rtm` (21,888 rows). A Roundup that printed an ERCOT maximum would have printed "spp_rtm" as its variable. For the data machine: check the current table and the connector.
- The same Amazon and Constellation event scored 8 on 1 October and 9 on 5 October: significance is not stable across clusters of one event, and the selection rests on it.

## Sources

The issues and emails named above; `warehouse/news/roundup.py`, `brief.py`, `score.py`, `ingest.py`, `email_digest.py`; `warehouse/analysis/templates/peak_premium_block.py`, `deals_by_month.py`; `warehouse/analysis/run.py`; `.github/workflows/roundup.yml`; `archive/sessions/SESSION_305_REPORT.md` and `SESSION_326_REPORT.md`; `docs/voice.md`; the tables `iso_dam_hub_prices`, `nyiso_dam_zone_prices`, `isone_dam_zone_prices`, `iso_rtm_hub_prices`, `nyiso_rtm_zone_prices`, `eia_fuel_spot_prices`, `eia930_all_demand`, `energy_deals`, `datacenter_projects`, `policy_actions`, `news_stories` in `warehouse/output` on portable-laptop; `site/public/findings/erw_2026_peak_hour_solar.csv`. The outputs of every trace are in `runs/chain_oct21_third/s444/` (not in git).

## State on 22 October

Written by session 577 (`archive/sessions/SESSION_577_REPORT.md`), from session 470's report and the branches since. "On main" means the commit is an ancestor of `origin/main` at 00:00 UTC on 22 October.

| Rank | Fix | State | Where |
|---|---|---|---|
| 1 | One event once, not the previous Roundup's story | landed (the Digest's functions; the previous ISO week's page as the ledger). Not caught: W40's two OPEC+ weekend items, which share no amount and too few title words | session 470, `239e78cf`, on main; `TheNamedDays` |
| 2 | The fuel change a week, an outlying close flagged | landed | session 470, `239e78cf`, on main; `TheRoundup` |
| 3 | A chart of the week must not measure the ERW's coverage | waiting: Samuel's ruling (session 470's list). Note: session 119 (5 October, the day after W40 was written) already keeps every `ABOUT = "coverage"` template, `deals_by_month` and `datacenters_by_state` among them, from being chosen (`warehouse/analysis/run.py`, step 2a; `tests/test_session119.py`); what is left to rule is whether to divide by scored stories | session 119, on main |
| 4 | Google News links | landed (the Digest's fix 7) | session 470, `63dcc2e3`, on main |
| 5 | The email carries the page's disclosures | landed | session 470, `239e78cf`, on main; `TheEmail` |
| 6 | A missed week said | waiting: Samuel's ruling (week 42) | |
| 7 | Deals and datacenters: a floor, US first | waiting: Samuel's ruling | |
| 8 | Deal rows extracted twice or wrongly | landed | session 531, `warehouse/deals/deal_parties.py`, on main; `tests/test_session531.py` |
| 9 | Policy wording | landed; since session 577 the read or why line under the policy of the week ends with a stop before its link and carries the one money style | session 470, `239e78cf`, on main; 577 `wip/577-s`, `EveryWhyLineGoesThroughIt` |
| 10 | Codes as words | landed: the deal table by session 470 (`roundup.DEAL_LABEL`); the deals-by-month chart's legend and note by session 577 (`deals_by_month.LABEL`, "acquisition" for `m_and_a`, as the tracker and the table say it) | 470 on main; 577 `wip/577-s`; `DealTypesInWordsInTheChart` |
| 11 | The chart shows the number it calls notable | landed | session 533, on main (`warehouse/analysis/style.py`, `templates/common.py`, `peak_premium_block.py`, `site/components/svgchart.tsx`); `tests/test_session533.py` |
| 12 | One definition of midday | landed: each block's hours stated in the template's fact | session 470, `a8afc37c`, on main |
| 13 | Trace W40 and W41 | done: 76 figures equal, 4 revised by the publisher after the issue (W40's highest real-time price, 1372.09, now reads 42.72; the US48 peaks 0.2 to 0.5 percent higher), 4 gaps stated when written, 0 failed | session 498, `scripts/check_roundup.py`, on `wip/506-combined`, landing with chain 023 |

Beside the ranked fixes, left as they are: the email puts the numbers before the policy of the week and does not name the deals and datacenter sections (no fix asked it); W41's no-model headline "massive" is the publisher's own title, said as such on the page and in the email (whether those titles may be edited is in session 577's report, for Samuel).

## Issues written after this audit

Added by session 2777 (chain 140, data machine), 26 October 2026, so that the list above stays complete; these issues are not audited here.

| Issue | Page | Email as sent | Chart files | Written |
|---|---|---|---|---|
| 2026-W43 (19 to 25 October) | `docs/roundup/2026-W43.md` | `docs/digest/email/2026-W43-roundup.txt` and `.html` | `docs/analysis/2026-W43/` | 25 October 23:20 UTC, the Sunday energy roundup workflow (commit `28a803da`) |
