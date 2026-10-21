# The daily Digest, read as its most demanding reader: 21 October 2026

Energy Research Warehouse (ERW), session 442, 21 October 2026, about 07:16 to 07:50 UTC, on portable-laptop (code role), branch `wip/441-450-third`. Samuel's ruling of 21 October: the Digest and the Roundup are the only two periodicals and must be perfect before anything else is written for the public. This file reads every Digest issue the site holds and lists what stands between it and that standard. No code was changed; the fixes are for the code machine, ranked in section 12.

## 1. What was read

**12 issues, not 14.** The site renders `docs/digest/<date>.md` (`site/app/digest/page.tsx`, `site/app/digest/[date]/page.tsx`, both through `site/lib/markdown.ts`). The repository holds 12 issue files on every branch (`git log --all -- docs/digest/2026-*.md` names no other), so all 12 were read:

| Issue | File | Window end (UTC) | Stories scored | Items | Links | Google News links | Words |
|---|---|---|---|---|---|---|---|
| 25 Sep (Fri) | `docs/digest/2026-09-25.md` | 25 Sep 21:57 | 471 | 27 | 31 | 15 | 1,157 |
| 26 Sep (Sat) | `docs/digest/2026-09-26.md` | 26 Sep 00:00 | 458 | 27 | 28 | 13 | 1,091 |
| 27 Sep (Sun) | `docs/digest/2026-09-27.md` | 27 Sep 18:27 | 187 | 25 | 30 | 18 | 914 |
| 28 Sep (Mon) | `docs/digest/2026-09-28.md` | 28 Sep 23:52 | 393 | 30 | 35 | 16 | 1,314 |
| 2 Oct (Fri) | `docs/digest/2026-10-02.md` | 2 Oct 00:23 | 326 | 31 | 42 | 15 | 1,366 |
| 7 Oct (Wed) | `docs/digest/2026-10-07.md` | 7 Oct 15:19 | 300 | 33 | 43 | 14 | 1,450 |
| 8 Oct (Thu) | `docs/digest/2026-10-08.md` | 8 Oct 15:41 | 271 | 33 | 38 | 19 | 1,402 |
| 9 Oct (Fri) | `docs/digest/2026-10-09.md` | 9 Oct 15:34 | 268 | 33 | 36 | 11 | 1,455 |
| 12 Oct (Mon) | `docs/digest/2026-10-12.md` | 12 Oct 15:35 | 277 | 30 | 37 | 22 | 1,162 |
| 13 Oct (Tue) | `docs/digest/2026-10-13.md` | 13 Oct 15:36 | 259 | 32 | 36 | 18 | 1,425 |
| 14 Oct (Wed) | `docs/digest/2026-10-14.md` | 14 Oct 16:18 | 243 | 32 | 42 | 21 | 1,463 |
| 20 Oct (Tue) | `docs/digest/2026-10-20.md` | 20 Oct 06:55 | 335 | 31 | 39 | 18 | 1,381 |

Items are the top 10, the "By sector" lines (policy actions included) and "AI and power"; links are counted per item; words exclude addresses and the generation comment. Source: `runs/chain_oct21_third/s442/issues.csv` and `items.json`, built by `runs/chain_oct21_third/s442/parse.py` (git ignores `runs/`).

Beside the issues: the 10 daily emails in `docs/digest/email/` (27 Sep to 20 Oct; none for 25 and 26 Sep), the one check run `docs/digest/checks/2026-09-26T1614Z.md`, the chart records `docs/digest/charts/` (eight days and `held.json`), the fun-fact bank `warehouse/news/facts/bank.csv`, the builder `warehouse/news/brief.py`, the scorer `warehouse/news/score.py` and its rubric `warehouse/news/rubric.md`, the email builder `warehouse/news/email_digest.py`, `warehouse/output/news_stories.csv` (21,087 stories, retrieved 20 October 06:13 UTC) and `warehouse/metadata/run_status.csv` as main holds it.

**The plan's description.** The master plan (02_master_plan) is not in the repository. Its description of the Digest is taken as the chain prompt quotes it: "what moved energy, two minutes, not an RSS dump"; beside it `docs/platform-tools.md`, tool 1 ("daily AI-curated news brief across the whole energy industry"), and the rubric: significance measures how much a story changes what an informed energy professional believes; commentary scores 1 to 3; "An AI or datacenter angle earns no significance credit by itself".

## 2. The seven findings that matter most

1. **From today the Digest prints numbers from tables held for a license.** `warehouse/metadata/license_status.csv` holds `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`, `isone_dam_zone_prices`, `isone_rtm_zone_prices` and `isone_rtm_zone_prices_hourly` as "license needed" from 2026-10-21, and `iso_dam_hub_prices` and `iso_rtm_hub_prices` for their MISO rows. `warehouse/news/brief.py` and `warehouse/news/email_digest.py` read no license file: the next issue prints NYISO's and ISO-NE's day-ahead averages and may name a NYISO interval as the day's highest real-time price, on the page and in the email. `news_index` is also "license needed" from 21 October (Bloomberg, Financial Times, Heatmap News, Natural Gas Intelligence and 30 others), and the Digest is made of those stories' titles and links. The page is in review, so no visitor reads it; the email is the open question (section 11).
2. **41 percent of the stories of the period fell in no issue's window.** Of the 10,088 stories published from 24 September 21:57 to 20 October 06:55 UTC, 4,152 fall outside every issue's 24 hours; 2,928 of them were published on a weekday. Among them are 31 clusters the scorer rated 8 or 9; 14 of them, all published on a weekday, reached no issue in any form, among them the NRC's approval of the first US small modular reactor's construction and the G7's release of 100 million barrels (section 8). The window is "24 hours to the time of the run" (`warehouse/news/brief.py`, line 541), and the runs ended at times from 00:00 to 23:52 UTC, so consecutive issues overlap or leave gaps, and a missed day is never caught up.
3. **8 of the 18 weekdays from 25 September to 20 October had no issue**, and the site says nothing about them: `/digest/2026-10-15` answers 404 (only a weekend date gets a page), and the archive simply skips the date (section 10).
4. **Every number under "Numbers Today" traces to its table: 118 of 118 recomputed exactly** (section 3). The faults are elsewhere: the story figures are the scorer's extraction, not checked against the article; and the real-time line prints a variable code (`spp_rtm`, ERCOT's settlement point price) that reads as the Southwest Power Pool.
5. **177 of the 393 distinct source links (45 percent) are Google News redirect addresses**, not the outlet's. The ingest tries to resolve each and records the result in `news_stories.csv`: 18,976 of 18,981 attempts say "Google served its own page, no redirect to the outlet". A reader who clicks reaches Google's page.
6. **The same event appears twice in one issue, and the same story on two or three days.** Within an issue: 2 Oct (the USD 120 billion Korean nuclear framework, top 1 and top 2), 12 Oct (oil up on Saudi attacks, top 2 and top 9), 13 Oct (Saudi Arabia and the Houthi attacks, top 7 and top 8), 14 Oct (the attack on Aramco's headquarters, top 6 and top 7), 20 Oct (the Defense Production Act funds for the Constitution Pipeline, twice under Policy). Across days: Google and Constellation's 890 MW (7, 8 and 9 Oct), Voltus's USD 225 million (8, 9 and 12 Oct), the Palisades SMR construction permit notice (2, 8 and 9 Oct). The 26 September issue repeats 26 of the 25 September issue's links (section 7).
7. **An issue takes six minutes, not two.** 914 to 1,463 words, 25 to 33 items and 28 to 43 links an issue; 147 of the 364 items carry a word the voice guide would cut ("major" 79 times, "signals" 56, "significant" 17, "massive" 8, "boom" 6). The why lines are the scorer's reasons printed as written, and they read as an RSS summary with adjectives (section 9).

## 3. Every number, traced

`runs/chain_oct21_third/s442/trace.py` recomputed each number of the "Numbers Today" block of every issue: the six main-hub day-ahead averages (the mean of the 24 hourly prices of the ISO's local operating day, rounded half up to cents as `brief.py`'s `mean2` does), the three EIA spot closes, and the value of the real-time interval named as the day's highest. Issues of 25 September to 2 October were read from this machine's tables (`warehouse/output`, retrieved up to 3 October); later ones from the Supabase live set, one entity and one day a read (67 small reads; the database answered every one).

| Issue | Day-ahead averages | MISO | Fuel closes | Real-time maximum | Result |
|---|---|---|---|---|---|
| 25 Sep to 2 Oct (5 issues) | 25 of 25 equal | a value each day, 5 of 5 equal | 15 of 15 equal | 3 of 3 equal (2 issues print "no real-time table covers yesterday") | equal |
| 7 Oct to 20 Oct (7 issues) | 35 of 35 equal | "not in the warehouse (0 of 24 hours)", 0 rows found, 7 of 7 | 21 of 21 equal | 7 of 7 equal | equal |

Total: **118 of 118 equal** (`runs/chain_oct21_third/s442/trace.csv`). Keys: `iso_dam_hub_prices` entity `ercot:HB_NORTH`, `caiso:TH_SP15_GEN-APND`, `miso:INDIANA.HUB`, `spp:SPPSOUTH_HUB`; `nyiso_dam_zone_prices` `nyiso:N.Y.C.`; `isone_dam_zone_prices` `isone:.H.INTERNAL_HUB`; `eia_fuel_spot_prices` `eia:henry_hub`, `eia:wti_cushing`, `eia:brent`; the real-time intervals in `iso_rtm_hub_prices`, `nyiso_rtm_zone_prices`.

What the recomputation does not cover, and what a demanding reader would still mark:

- **The real-time line was checked at its stated interval only.** That the interval is the day's highest across every real-time table was not recomputed (it needs a full day of every table; the database is slow tonight).
- **The real-time line prints a variable code.** 7 and 8 October: "HB_WEST (ERCOT) ... PT15M `spp_rtm`". `spp_rtm` is ERCOT's real-time settlement point price; a reader takes it for the Southwest Power Pool.
- **MISO's row says "not in the warehouse (0 of 24 hours)"** on every issue from 7 October. The reason is the ERW's own pause of MISO since 4 October (`warehouse/metadata/paused_sources.csv`), not a gap in MISO's publication; the page does not say so.
- **The fuel closes lag up to eight days** (14 October prints the closes of 6 October): EIA publishes the series weekly. The line says "trading dates" but not that.
- **The numbers summary sentence** (the model's sentence above the table, from 28 September) repeats the table's figures; each one in the 12 issues equals its table row. On 12 October it is left out (the day's model budget, said on the page).
- **Story figures are untraceable to an ERW table by design**: the MW, prices and parties after each why line are the scorer's extraction from the story (`news_stories.csv` columns `mw`, `price_mentioned`, `parties`). They trace to their story row, not to the article; no check compares them with the article's text.
- **The chart captions** (section 5) were recomputed from local tables: 3 of 3 equal.
- **The fun facts** (section 6) trace to a stored Wikipedia page or an ERW table through `warehouse/news/facts/bank.csv`; the bank's verification is what proves them, and it passed for every one printed.

## 4. Every link

393 distinct addresses across the 12 issues. One HEAD request a link (a GET, body not read, only when HEAD was refused), each host's `robots.txt` read first, 15 s timeout, an ERW user agent, at most 250 requests. No host in `warehouse/metadata/paused_sources.csv` is among them. Log: `runs/chain_oct21_third/s442/links.csv` (every request with its time and answer) and `link_results.csv` (one row a link).

| | Count |
|---|---|
| Requests made | 250 of 250: 24 `robots.txt`, 203 HEAD, 23 GET after a refused HEAD |
| Links answered 200 | 182 |
| Links answered 403 | 21: Natural Gas Intelligence 14, Energy-Storage.news 5, Utility Dive 2 |
| Links not checked, cap reached | 190: the 177 Google News links, World Nuclear News 11, Utility Dive 2 |
| Links answered 404 or failed | 0 |

The 403 answers are the outlets refusing an automated client (both Natural Gas Intelligence and Energy-Storage.news refused their own `robots.txt` too); they say nothing about whether a reader's browser reaches the page. The Google News links were not requested: `news_stories.csv` already records the ingest's attempt on each (`url_resolved`), and 18,976 of 18,981 say Google served its own page with no redirect to the outlet.

## 5. The chart of the day

Three issues carry one (13, 14 and 20 October; it began with session 232).

| Issue | Fact | Table and key | Recomputed | Judgement |
|---|---|---|---|---|
| 13 Oct | Wyoming net generation from gas, 1,028,747 MWh in July 2026, a record; the old one 765,381 MWh, July 2024 | `eia_state_generation_monthly`, `eia:generation:WY:NG` | equal | The figure is 82 percent above June's 563,755 MWh in the same table: the newest month of EIA's state data is its preliminary estimate, and the caption gives no caveat. Its scanner draft, `scan-record-483f592bf064`, is one of the three a check marked in production without a person (the note of 20 October, item 1: "dismissed") |
| 14 Oct | District of Columbia industrial retail price, USD 321.5 per MWh in July 2026; the old record USD 272.6, June 2006 | `eia_retail_electricity_prices`, `eia:retail_price:DC:IND` | equal | June held USD 162.1 and May USD 146.0 in the same table: the price doubled in a month in a sector of very few customers. A record in a sector this small, unexplained, is not what moved energy. Its draft, `scan-record-6e1d1cff0ae4`, is another of the three ("full card asked") |
| 20 Oct | Utah residential retail sales, 1,658,263 MWh in July 2026; the old record 1,484,757 MWh, July 2024 | `eia_retail_sales_monthly`, `eia:retail_sales:UT:RES` | equal | Chosen at 1.01 robust standard deviations past its threshold, the weakest of the three. A July record printed on 20 October is three months old |

Right fact: the three are true to their tables, but each is a state-month record of July data, chosen by statistical strength alone, with no tie to the day's news and no preliminary-data caveat. Right chart: a long monthly line with the record marked fits a record. Right caption: the caption repeats the fact; "the highest monthly value held since January 2001" says "of every month held since January 2001" in fewer clear words. The same three facts were drawn first for 6, 8 and 9 October in session 232's trial (`docs/digest/charts/2026-10-06.json`, `2026-10-08.json`, `2026-10-09.json`), so the pool is narrow.

## 6. The fun fact

Eight issues carry one (from 28 September; none on 12 October, the model budget day, and none before 28 September).

- 2 October: "That is a lot of ground to cover, no wonder it moves at a crawl instead of a sprint." The pun makes a claim (that the Colonial Pipeline is slow) that its source does not state; `warehouse/news/funfact.py` says a pun makes no claim.
- 14 October: Pearl Street Station, then "On this day in 1913: Senghenydd colliery disaster ... claims the lives of 439 miners." A mining disaster with 439 dead under the heading "Fun Fact" is the gravest wording fault of the 12 issues.
- 20 October: "US oil extraction peaked at 10.2 million barrels per day in 1970 before declining for the next 35 years." The bank quotes its Wikipedia span faithfully, but a reader takes "peaked" as the all-time peak. Whether US output has since passed 10.2 million barrels a day can be answered from the ERW's own tables; `eia_petroleum_supply_weekly` was not on this machine and is not in the live set, so it was not read here.
- 7, 8, 9 and 13 October: sound; two are ERW numbers with their tables (`state_generation_mix_monthly`, `eia_fuel_spot_prices`).

## 7. Scoring and clustering, against "what moved energy, two minutes, not an RSS dump"

**What moved energy.** The top 10s are mostly right in kind: oil 25 of 120 places, nuclear 12, deals 11, policy 11, LNG 10, datacenter power 17. Four faults against the rubric:

- **The tie-break favours AI.** Clusters are sorted by significance, then by AI relevance (`warehouse/news/brief.py`, line 132). Most top-10 places are ties at 7, so AI relevance decides them, which the rubric forbids ("An AI or datacenter angle earns no significance credit by itself"). 13 October: 5 of the top 10 are datacenter stories, among them a 42 MW site in Norway at 7, where the rubric's 7 is "hundreds of MW".
- **Commentary scores 7.** "Land & Expand tracks North America's data center pipeline" (13 Oct, top 4) is a recurring column; "Brookfield's Teskey sees no slowdown in AI infrastructure build" (13 Oct, top 5) an interview; "Iran war tilts balance of global oil power towards the Americas" (20 Oct, top 3) an analysis piece; the rubric puts commentary at 1 to 3. "How Low Can the Strategic Petroleum Reserve Actually Go?" (12 Oct) scored 6.
- **The AI section fills with the weakest items.** 28 September lists two stories the scorer itself called "Sponsored-style piece ... no specific MW or deals" and "general commentary", both at significance 3.
- **Sectors misfiled.** Saudi Arabia's East-West oil pipeline under Power as "transmission" (13 Oct); Anthropic's computing deal with Akamai and Nscale's raise under Policy (25 and 26 Sep).

**Clustering.** The scorer joins a story to an earlier one it names as a duplicate within a scoring batch (`warehouse/news/score.py`, from line 290); stories of the same event scored in different batches stay apart, and nothing joins today's story to yesterday's issue.

| Kind | Where |
|---|---|
| Same event twice in one top 10 | 2 Oct, top 1 and 2 (Korea's USD 120 billion nuclear framework); 2 Oct, top 5 and 10 (China halting fuel exports); 12 Oct, top 2 and 9 (oil up on Saudi attacks); 13 Oct, top 7 and 8 (Saudi Arabia and the Houthis); 14 Oct, top 6 and 7 (Aramco's headquarters) |
| Same event twice in one issue, elsewhere | 7 Oct, Policy (the Australian High Court coal ruling, Reuters and Bloomberg); 9 Oct, top 6 and Oil and gas (Hurricane Isaias); 12 Oct, Oil and gas (two more Saudi attack items); 20 Oct, Policy (the Constitution Pipeline's Defense Production Act funds, DOE and Bloomberg) |
| Same story on two or three days | Google and Constellation, 890 MW (7, 8, 9 Oct); Emera and Canadian Utilities (7, 8 Oct); Devon's Eagle Ford sale (8, 9 Oct); Venture Global and Galp (8, 9 Oct); Voltus, USD 225 million (8, 9, 12 Oct); Oracle trucking gas (9, 13 Oct); TotalEnergies and KKR, 700 MW (12, 13 Oct); FERC on PJM's data center registry (13, 14 Oct); Westinghouse in Poland (8, 14 Oct); the EU windfall tax (9, 13 Oct); uranium past its 2007 peak (2, 12 Oct); Sabine Pass's final environmental statement (25, 26, 28 Sep) |
| The same policy action reprinted | the Palisades SMR construction permit notice (2, 8, 9 Oct); Colorado's Class VI primacy rule (13, 14 Oct) |
| An issue that repeats its day before | 26 Sep: 26 of its items link where 25 Sep linked (its window ended 2 hours after the 25 September run's) |
| One story in three sections | 25, 26 and 27 Sep: the top stories repeated under "By sector" and "AI and power" (fixed from 28 September by `unique_items`) |

**Two minutes.** At a reading pace of 220 words a minute the issues take 4.2 to 6.7 minutes before a link is opened. The plan's two minutes holds the top five and the numbers, about the email's length.

**Not an RSS dump.** The headlines are rewritten by the model (but on 12 October); the why lines are not. They are the scorer's one-line reasons, printed as written (`warehouse/news/score.py`, line 311), and they carry the adjectives and the "signals" of a feed summary (section 9).

## 8. Stale items and missing stories

**Stale.** By publish time no item is older than its window (0 of 364 by `news_stories.csv`'s `event_date`). Staleness comes from repeats instead (the table in section 7) and from follow-up stories of an event already shown.

**Missing stories a reader would expect**, named from the ERW's own `news_stories.csv`, each with the outlet that carried it. 31 clusters scored 8 or 9 fell outside every window (the list is `runs/chain_oct21_third/s442/gaps.txt`). Read one by one: 4 were published on a weekend (the Roundup's); 13 reached an issue under another cluster, often days late (Shell's LNG Canada expansion, 30 September, appeared on 8 October as the phase 2 FID; TotalEnergies' Absheron FID, 26 September, on 13 October); and these 14, all weekday stories, reached no issue in any form:

| Published (UTC) | Significance | Story | Outlet |
|---|---|---|---|
| 29 Sep 22:03 | 8 | The NRC approves construction of the first US small modular reactor | Reuters |
| 30 Sep 14:00 | 8 | Iran warns no energy infrastructure will be safe if it cannot sell oil | OilPrice.com |
| 30 Sep 21:44 | 8 | FERC accepts PJM's reliability backstop proposal | PJM newsroom |
| 30 Sep 13:48 | 8 | FERC's chair criticises PJM as it delays its capacity auction | Utility Dive |
| 30 Sep 20:52 | 8 | Over 600 projects enter phase 1 of PJM's new interconnection process | PJM newsroom |
| 2 Oct 16:49 | 9 | G7 to release 100 million barrels of diesel and other reserves through the IEA | Reuters |
| 2 Oct 16:50 | 8 | Dated Brent above USD 120 | OilPrice.com |
| 5 Oct 11:00 | 8 | Oil majors take the climate damages claim to the US Supreme Court | Financial Times |
| 5 Oct 16:31 | 8 | YPF targets a late-November FID for a 12 Mt a year Argentina LNG project | Natural Gas Intelligence |
| 9 Oct 17:45 | 8 | US officials pushed to use the Defense Production Act to raise oil and fuel output | Reuters |
| 9 Oct 20:30 | 8 | Hurricane Isaias shuts in 71 percent of US Gulf oil production (13 October carried "about 30%", after the peak) | OilPrice.com |
| 9 Oct 21:45 | 8 | DOE supports FERC's call for PJM to protect ratepayers | DOE newsroom |
| 15 Oct 00:00 | 8 | Brookfield and NextEra's USD 100 billion AI hub on a Cold War nuclear site | OilPrice.com |
| 15 Oct 15:10 | 8 | FERC launches its first LNG authorization program | FERC |

The reading of "reached an issue under another cluster" is this session's judgement of the titles, not a computed match. One cluster of significance 8 fell inside a window and was still left out: "QatarEnergy's LNG expansion project poised to start operations in November" (Reuters, 7 Oct 15:15, four minutes before that day's run ended its window).

Where the 4,152 uncovered stories fall, by publish day: 29 and 30 Sep (779, no issue), 2 Oct after 00:23 (377), 5 and 6 Oct (889; the two runs failed), 9 Oct after 15:34 (244), 14 Oct after 16:18 (141), 15 Oct (340), 19 Oct before 06:55 (119), and the weekends. Friday's evening stories are in no Digest window by construction: Monday's window opens on Sunday afternoon.

## 9. Wording

- **Em and en dashes: none** in any of the 12 issues.
- **Hype.** 147 of 364 items carry "major", "massive", "significant", "signals", "boom", "surge", "record" or "critical" (count by `parse.py`; "record" is sometimes a fact). Worst lines: "Massive AI data center capex; major power demand commitment in final negotiation stages" (13 Oct, top 1); "Major AI datacenter infrastructure deal signals massive power demand and capital commitment" (20 Oct, top 1); "Breakthrough in heat pump technology" (13 Oct).
- **Vague.** "Major geopolitical shift affecting global oil supply and market structure" (20 Oct, top 3); "Significant renewable energy deal with major counterparties and capital commitment" (13 Oct); "a notable deal signal" (9 Oct).
- **Punctuation.** A why line without a final stop runs into the figures: "affecting global oil markets and prices parties: Iran." (20 Oct, top 8); "for 20-year supply agreement $4.4 Billion; parties" (14 Oct, top 2); also 27 Sep, top 3 and top 7. `detail()` in `warehouse/news/brief.py` (line 297) adds the figures without checking the stop.
- **Amounts in five styles.** "$45 Billion", "$3.2bn", "$4.2B", "$800MM", "USD120 billion": 22 capitalised "Billion" or "Million" in 8 issues. The voice guide's form is "USD 45 billion".
- **Publisher titles** on 12 October (the model budget day, said on the page): "Exclusive | FTX’s Old Bitcoin-Mining Assets ...", "United States: TotalEnergies Expands its Joint Venture ...", in title case with curly quotes.
- **Labels shown raw**: "(significance 8, datacenter_power)" in the first three issues; "datacenter power" as a sector name throughout.
- **The schedule line is wrong.** `/digest` and `/about#digest` say the Digest is written "Monday to Friday at 14:00 UTC" (`site/app/digest/page.tsx`, line 26; `site/app/about/page.tsx`, line 56). The workflow starts at 14:00 (`.github/workflows/daily-prices.yml`, line 54); the issues were written at 15:19 to 16:18 UTC from 7 to 14 October, and at 00:00, 00:23, 06:55, 18:27, 21:57 and 23:52 UTC on the other days.

## 10. Days without a brief, and what the page said

| Weekday | What happened (`run_status.csv`) | What the site shows |
|---|---|---|
| 29 Sep (Tue) | a local run wrote an issue at 10:51 UTC; it was never committed | not in the archive; `/digest/2026-09-29` answers 404 |
| 30 Sep (Wed) | three runs failed on a date parse ("passing `format='mixed'`") | the same |
| 1 Oct (Thu) | no run (the issue dated 2 October covers 1 October to 00:23 on 2 October) | the same |
| 5 Oct (Mon) | failed: "duplicate items in the brief" (a repeated headline) | the same |
| 6 Oct (Tue) | failed: "duplicate items in the brief" (a repeated DOE address) | the same |
| 15, 16 Oct (Thu, Fri) | no row: the daily run stopped at its first step on 15 to 18 October (`docs/machines.md`) | the same |
| 19 Oct (Mon) | no brief row (only the local EIA-930 runs of the data machine) | the same |
| 21 Oct (Wed) | not yet run at the time of reading | |

Two of the eight were lost to the builder's own uniqueness check: `assert_unique` (`warehouse/news/brief.py`, line 257) refuses the whole issue when two items share a headline or an address, rather than dropping the later one. The weekend issues of 26 and 27 September predate the weekday rule of session 23 and are still in the archive.

## 11. The email

The 10 daily emails in `docs/digest/email/` are the files `email_digest.py` writes; whether each was sent is in Supabase's send records, not read here. Read as a reader of the 20 October email:

- The top five carry the page's why lines and figures, with the same Google News addresses printed in full in the text version (each over 200 characters).
- The numbers table becomes one line a row ("ISO: ERCOT; Hub or zone: HB_NORTH; Operating day: ..."), longer than the table it replaces.
- The chart image is served from `raw.githubusercontent.com`; its link and "All of ERW's Energy Digest" lead to `erw-flame.vercel.app`, where every page is in review (`site/lib/release.ts`): a reader who clicks sees the in-review page.
- No license line: from 21 October it would carry the held NYISO and ISO-NE figures (finding 1).

## 12. The fixes, ranked, for the code machine

Each fix names the file it lives in and the test that would prove it. None was made here.

| Rank | Fix | File | Test that would prove it |
|---|---|---|---|
| 1 | Read `license_status.csv` before any number: a held table's figure prints "held: license needed" with no value, on the page and in the email; the real-time maximum skips held tables | `warehouse/news/brief.py` | A fixture status file holding `nyiso_dam_zone_prices`: the NYISO row prints the hold and no digits; the real-time line never names a held table; the same for the email text |
| 2 | Open each window at the previous issue's end (capped, say, at 96 hours), not 24 hours before the run; a missed weekday is caught up by the next issue | `warehouse/news/brief.py` | Two runs at T1 and T2 over a fixture of stories: every story in (T1, T2] is a candidate once; none falls between |
| 3 | Never lose an issue to a duplicate: drop the later item and log it, instead of raising | `warehouse/news/brief.py` | Two clusters sharing an address: the issue is written with one of them, and the log names the other |
| 4 | Do not reprint a story or a policy action an earlier issue showed (a ledger of shown cluster ids and addresses), unless the cluster has a new figure | `warehouse/news/brief.py` | Fixture: day 2 holds day 1's Voltus cluster; it is left out of day 2 |
| 5 | Join clusters of one event across scoring batches (same parties and sector within 48 hours, or the scorer asked against the last issue's items) | `warehouse/news/score.py` | The 14 October Aramco pair and the 2 October Korea pair as fixtures: one cluster each |
| 6 | Remove AI relevance from the ranking's tie-break (significance, then the number of outlets, then time) | `warehouse/news/brief.py` | Two clusters at 7, one with AI relevance 9 and one outlet, one with 0 and three outlets: the second ranks first |
| 7 | Link the outlet, not Google News: use the address the feed item names for the outlet where it has one, else print the outlet's name with no link | `warehouse/news/ingest.py` | No `news.google.com` address in an issue built from a fixture of Google items |
| 8 | Hold the why lines to the voice: strip or reject "major", "massive", "significant", "signals", "boom", "breakthrough"; end each with a stop before the figures | `warehouse/news/score.py` | A why line with "Major ... signals" fails the scorer's check (as `nodash` does for dashes); `detail()` output always follows ". " |
| 9 | One amount style: "USD 45 billion", "USD 800 million", "CAD 14.3 billion" | `warehouse/news/brief.py` | `detail()` on "$45 Billion", "$800MM", "C$14.3 Billion" gives the voice form |
| 10 | The chart of the day: a caveat when the month is the newest of a preliminary EIA series; a strength floor (1.01 is too weak); never a draft with a ruling of "dismissed" or "full card asked" | `warehouse/news/brief.py` | A fixture flag on the newest month of `eia_state_generation_monthly` prints the caveat; a flag at strength 1.0 is not chosen; a dismissed key is not chosen |
| 11 | The fun fact: no "on this day" item about deaths or disasters; a pun that states a fact needs a source like any second half | `warehouse/news/funfact.py` | `check_record` rejects the 14 October Senghenydd second half and the 2 October pun |
| 12 | Print a plain label for the real-time price ("ERCOT real-time settlement point price, 15-minute") and say why MISO is absent ("paused by the ERW since 4 October") | `warehouse/news/brief.py` | The 7 October fixture prints no `spp_rtm`; MISO's row names the pause when `paused_sources.csv` holds it |
| 13 | The archive lists a missed weekday with its reason instead of a 404 | `site/lib/markdown.ts` | `archiveDays()` over a fixture with no 15 October issue returns that day with "no issue" and the reason |
| 14 | The schedule line says what happens: "after the daily run that starts at 14:00 UTC" | `site/app/about/page.tsx` | A check that the page's stated time matches `.github/workflows/daily-prices.yml` or names the run |
| 15 | Two minutes: the issue's top is the top five and the numbers; "By sector" and "AI and power" fold below, or are cut | `warehouse/news/brief.py` | The words above the fold of a built issue are 450 or fewer (about two minutes at 220 a minute) |
| 16 | The AI section takes no story the scorer called commentary (significance under 5) | `warehouse/news/brief.py` | A fixture AI story at 3 is left out |
| 17 | The email links to a page a reader can open (a live page, or none while every page is in review) | `warehouse/news/email_digest.py` | The text and HTML of a built email hold no address of a page `release.ts` marks in review |

## 13. For Samuel's ruling

- Whether the Digest may print the held ISO prices at all, before or after fix 1, and whether the email goes out while `news_index` is "license needed".
- Whether a Digest is written on a day the window holds fewer stories than usual, or the next issue catches up (fix 2 changes what a Monday covers).
- The two-minute form (fix 15): which sections stay.
- Whether the 14 October issue is corrected in place (the fun fact) or left as written.

## 14. Requests made in this session

250 requests, all logged in `runs/chain_oct21_third/s442/links.csv`: 24 `robots.txt` files and 226 requests of the issues' own source addresses (203 HEAD, 23 GET whose body was not read). 67 reads of the ERW's own Supabase live set for the trace. No data pull from any publisher; no model call.
