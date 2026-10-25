# Tomorrow's Digest and this week's Roundup, dry runs: 22 October 2026

Energy Research Warehouse (ERW), sessions 807 and 808, 22 October 2026, on portable-laptop (code role), chain `queue/done/060-night-23-october-code-periodicals.md`. The Digest's and the Roundup's code as it stands on `wip/807-periodicals` (sessions 801 to 807 of this chain over `origin/main`), run with the model under the chain's caps, on the stories scored by the last scheduled run (`warehouse/output/news_stories.csv`, scored to 21 October 15:06 UTC) and the live set's tables (anon key, public rows). Written under `runs/periodicals_dryrun/` only; nothing under `docs/digest/` or `docs/roundup/` was touched. The ledger could not be written (its table takes the data lock, which a code machine does not hold), so it was off (`ERW_LEDGER=0`) and the spend is read from each run's log.

## The three the owner should read

1. **The top ten reads as ten topics now, and the two stories a reader would have missed are in it.** The dry run of 21 October keeps Anthropic's compute spend at the top and puts Amazon's Germany pledge and Nextdc's backlash under it as "also" lines; the oil price above USD 110 and the 23 ship attacks near Hormuz, which the stored issue left in "By sector", are top 9 and 10. Every why line is one sentence without the list's adjectives (0 of 30, against 11 of 33 in the stored issue); the figures line repeats a headline's figure on 2 items instead of 9. The cost of the fold shows too: "generation" as one topic puts Exelon's plans, India's coal stocks and Ormat's geothermal auction under Mexico's 8,200 MW.
2. **The numbers section now says what moved, and every figure of it traces**: ERCOT's day-ahead average up 21.2 percent on the day before leads "What moved most"; the model's summary sentence picks that up ("ERCOT's HB_NORTH rose the most, up 21.2% to 28.38 USD/MWh, while NYISO's N.Y.C. fell 6.2%"); 25 of 25 figures of the dry run equal the live set (`scripts/check_digest.py`). The held grids are named as not ranked; the year-before demand is said not held (the hourly window is 56 days).
3. **The sources are bare names for most items**, because the news index's license hold names Reuters, Bloomberg, POWER Magazine, OilPrice.com and 21 others: the dry run carries 3 links where the stored issue carried 39 (17 of them Google addresses). That is the ruling of 21 October as session 803 read the chain; whether a held outlet's item should keep its link is for the owner (session 803's report).

## The Digest of 21 October, stored and dry-run, side by side

| | Stored issue (written 21 October 15:45 UTC by the code before sessions 470 and 577) | Dry run (this chain's code, the same window) |
|---|---|---|
| Items (top ten, By sector, AI and power) | 33 | 30 (the three policy actions of the day are missing: `policy_actions.csv` is not on this machine's worktree) |
| Why lines with an adjective of the list | 11 | 0 |
| Items whose figures line repeats a headline figure | 9 | 2 |
| Top-ten sectors with three or more items | datacenter power 3 | none (ten sectors) |
| Links, and Google News addresses among them | 39, 17 | 3, 0 (the held outlets are named with no link) |
| Words (addresses left out) | 1,500 | 1,838 (the "also" lines and the movers) |
| Figures traced | 131 of 131 over the 13 stored issues (session 498) | 25 of 25 (the live set, anon key) |
| Model calls, cost | 2 headline calls, 1 summary call (from its run log) | 2 headline calls, 1 summary call; USD 0.0255 + USD 0.0050 |

Top of the industry:

| # | Stored | Dry run |
|---|---|---|
| 1 | Anthropic may spend $750 Billion on computing costs, Bloomberg reports | the same; also: Amazon pledges EUR 16bn in Germany; Nextdc cuts outlook |
| 2 | Amazon pledges EUR 16bn investment in Germany in 2027 | UK approves the long-delayed $3B Jackdaw gas field on energy security grounds |
| 3 | UK approves the long-delayed Jackdaw gas field, a $3B project | The Nuclear Company proposes a 6,600 MW campus of up to six AP1000 reactors in Kentucky; also: the Philippines' nuclear plans; Indiana's CANDU proposal |
| 4 | The Nuclear Company proposes a 6,600 MW campus | DOE announces $967 million in grid resilience funding |
| 5 | DOE announces $967 million in funding for grid resilience projects | Mexico's state utility set to approve up to 60 projects, 8,200 MW, $12.5 billion; also: Exelon's generation plans; India's coal plants; Ormat's auction |
| 6 | Mexico's state utility set to approve up to 60 projects | European electricity demand returns to growth; also: Morgan Stanley on fuel markets |
| 7 | Nextdc cuts outlook as public backlash delays data center power | US Department of Energy asks refiners to raise diesel output; also: the heating oil reserve loan; DOE's USD 1 billion grid upgrades; the Constitution Pipeline's Defense Production Act funds |
| 8 | European electricity demand returns to growth | Ara Partners raises $2.5B for an energy fund |
| 9 | Exelon executive sees possible return to regulated generation | Brent trades at $110.30 per barrel as Middle East supply worries persist |
| 10 | US Department of Energy asks refiners to raise diesel output | At least 23 ship attacks logged in or near Hormuz in the first two weeks of October |

The why lines, top 1 to 3: "Massive AI compute capex signals unprecedented power demand growth and infrastructure investment scale. $750 Billion; parties: Anthropic." became "AI compute capex signals power demand growth and infrastructure investment scale. parties: Anthropic."; "Major datacenter and AI infrastructure expansion ..." is now an "also" line; "Major North Sea gas project approval adds supply ... $3B" became "North Sea gas project approval adds supply; supports energy security amid geopolitical tensions. parties: UK." The adjectives are gone and the figures are not said twice; the lines still describe rather than state a consequence where the scorer's line did, since the stories were scored before the new prompt (session 801's rule in `score.py` applies from the next scoring run).

Every difference of the numbers section: the stored issue's five-column table, its three bare closes and its summary sentence are replaced by "What moved most" (five lines and the "Not ranked" line), the seven-column table (the day before and the change), the closes with their age, and the US48 demand line; the real-time line is the same figure with the same words. The chart changed: the Iowa industrial retail price record (the strongest flag) gave way to Nevada's net generation record, the strongest flag among those related to the day's top ten (it shares "generation" with the Mexico item; relevance 32 of the scanner's 11 flags, rank 6 by strength). The fun fact is the same.

What the dry run shows that a later night should mend: an item whose why line fails the check and whose headline is the title itself prints no why line at all (top 2 of the W43 Roundup below; session 807 chose nothing over the headline twice); a "generation" topic that folds four unrelated stories (session 802's report, for the owner).

## This week's Roundup (2026-W43, to 22 October 10:51 UTC), dry run, beside W41

| | W41, stored (written 11 October, without the model) | W43, dry run (Monday to Thursday morning) |
|---|---|---|
| Stories, clusters | 1,806, headlines the publishers' own | 680, 612 clusters; headlines by the model (USD 0.0049 + the summary USD 0.0040) |
| The week in five numbers | none | WTI up 7.2 percent on the week; the US48 peak 519,415 MW on Tuesday; the deal of the week USD 45 billion (Nscale and Anthropic, as `energy_deals` holds it); the largest new load 400 MW (NAVWAR HQ, San Diego); no chart yet (the engine runs on Sunday) |
| Weekend, the five | 3 and 5 items, two of the five one event with W40's | no weekend yet; 5 items, 5 topics, one "also" line (Anthropic's USD 750 billion under the Nscale deal) |
| Links, Google addresses | 15, 7 | 1, 0 (held outlets named with no link) |
| Figures traced (`check_roundup.py`) | 76 equal, 4 revised (session 498) | 18 equal against the live set, 2 equal against the CSVs (the deal's dollars, the load's MW), 8 gaps stated when written (the week's hub means: 72 of 168 hours so far; MISO paused), 0 failed |
| Real-time line | "lmp_rtm_15m_mean [4], SPP's real-time locational marginal price" | the same, then "a 15-minute interval", and the note that the grids' series differ in interval length |

The W43 dry run's second item, "AEP, Amazon and X-energy plan a 960 MW, 12-SMR nuclear plant in Indiana", prints no why line: the scorer's line names 960 MW, which the headline gives, and the sentence cannot lose the figure, so session 807's rule prints nothing rather than the headline again. The deal of the week is the tracker's row for Nscale and Anthropic's cloud computing deal, which the tracker filed as an offtake; whether a compute contract is an energy deal is the tracker's question, not the Roundup's.

## Where the files are

- `runs/periodicals_dryrun/digest_2026-10-21.md`, `digest_2026-10-21-daily.txt` and `.html`, `charts/2026-10-21.png` and `.json` (not in git).
- `runs/periodicals_dryrun/roundup_2026-W43.md`, `roundup_2026-W43-roundup.txt` and `.html` (not in git).
- The run logs: `warehouse/output/logs/news_brief_20261022T104150Z.log` (the worktree `erw-807`) and `news_roundup_20261022T105138Z.log` (the main checkout, where the Roundup's tables were read).
