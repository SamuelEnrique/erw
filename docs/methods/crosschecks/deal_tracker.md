# Cross-checks: the deal tracker (`/deals`)

Energy Research Warehouse (ERW). Session 7406, chain 303, 16 November 2026. The done line's cross-check for the tracker, in two parts: **its counts and megawatts by year and kind beside published tallies** of power purchase agreements and of the technology companies' power deals, each with its publisher and date; and **its twenty largest AI-power rows, each against its own story's headline figure**. No figure of the tracker was adjusted to match one.

- **Ours** is `replication/deals/page_figures.json` and the rows behind it: the live set's 590 rows of `energy_deals` as read on 16 November 2026 at 09:49 UTC, the register's five folded pairs counted once (585 deals), by the pages' own functions, which the replication reproduces 1,123 of 1,124 (the one difference named). `tests/test_session7406_trackers.py` holds the figures below to that file and to the do-file's mirror.
- **Theirs** was read by this session from the publisher's own page on 16 November 2026 at about 10:00 UTC, each host's robots file first. Every figure is stated as a fact with a link; no publisher's text is quoted.
- **What could not be read.** LevelTen's index of offered prices in dollars is in a report behind a form; its public page states the changes in percent only, so no price in dollars is set beside the tracker's. S&P Global's tallies are behind a login and were not requested.

## 1. Counts and megawatts by year and kind

What the tracker holds, by the year of the deal's date (the do-file's last table gives every kind):

| Year | Deals | Stating MW | MW stated | Of them power purchases (type) | Stating MW | MW stated | Tagged AI power | Stating MW | MW stated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 (January to April, October to December) | 92 | 1 | 5,000 | 3 | 0 | none | 35 | 1 | 5,000 |
| 2026 (to 13 November) | 493 | 38 | 38,119 | 36 | 14 | 11,990.5 | 182 | 19 | 11,107.5 |

| The tracker's figure | Ours | Published figure | Publisher, document, date | Gap | Why they differ |
|---|---|---|---|---|---|
| Power purchase agreements dated 2025 | 3 deals, none stating MW | 27,300 MW of clean energy contracted by US companies in 2025, 12 percent more than in 2024; more than 130,000 MW since 2014 | Corporate Energy Buyers Association (CEBA), [press release of 17 March 2026](https://ceba.org/ceba-analysis-shows-corporate-clean-energy-breaks-130-gw/), from its Deal Tracker | -27,300 MW | Coverage and source. CEBA counts the contracts its members and public records report. The tracker reads only the news the ERW scores, from October 2025 on in earnest (no deal is dated May to September 2025), and keeps megawatts only where a headline or a short summary states them. It is not a tally of the PPA market. |
| The same | 3 deals, none stating MW | 29,500 MW of corporate clean power deals in the United States in 2025, a record; 55,900 MW worldwide, 10 percent down on 2024 | BloombergNEF, [release of 19 February 2026](https://about.bnef.com/insights/clean-energy/corporate-clean-energy-buying-fell-in-2025-after-nearly-a-decade-of-growth/) on its 1H 2026 Corporate Energy Market Outlook | -29,500 MW | The same. The two publishers differ from each other by 2,200 MW on the United States: each tracker has its own list of what counts. |
| Power purchase agreements dated 2026, to 13 November | 36 deals, 14 stating MW, 11,990.5 MW | No full-year tally exists yet; the 2025 pace above is about 2,300 to 2,500 MW a month in the United States (this file's arithmetic: 27,300 and 29,500 over twelve months) | the same two documents | not a gap: about 1,140 MW a month stated by 14 deals, against about 2,300 to 2,500 | The tracker's megawatts are of every country and of the 14 power purchases whose stories state a size; the other 22 state none. Three of the 36 name a country other than the United States, and 33 name no country. |
| Megawatts of deals that name Meta, Amazon, Google (Alphabet) or Microsoft as a party | 72 deals, 7 stating MW, 7,198 MW in all; in 2025, 9 deals and none stating MW | Those four companies made 49 percent of the world's corporate clean power deals in 2025; Meta and Amazon together contracted 20,400 MW, 4,700 MW of it nuclear | BloombergNEF, the same release | -20,400 MW against two of the four, for 2025 | The tracker's rows that name the four are mostly not power purchases: funding rounds, compute contracts and acquisitions are among them (the AI-power tag is of the parties, not of the asset: the method note, section 5). A megawatt figure is in 7 of the 72. |
| Deals whose supply is nuclear | 57 deals, 6 stating MW, 12,220 MW; 11 of them tagged AI power, 1 stating MW (1,200) | 4,700 MW of nuclear power contracted by Meta and Amazon in 2025 | BloombergNEF, the same release | not a gap: different years and different deals | Half of the tracker's nuclear megawatts are one plan of 6,000 MW whose kind is "other"; three of the six rows are power purchases (4,060 MW in all, one of them for a restarted reactor), one is a small modular reactor deal and one a fuel supply. Every one is dated 2026, and five of the six are not tagged AI power. |
| Deals that state a price in US dollars per MWh | 0 of 585 | The offered price of solar and of wind power purchase agreements in North America rose in the first quarter of 2026 (the 25th percentile of offers: solar by 4.6 percent, wind by nearly 8); the dollar figures are not on the public page | LevelTen Energy, [North American PPA Price Index, Q1 2026](https://www.leveltenenergy.com/post/levelten-north-american-ppa-price-index-q1-2026), 14 April 2026 | no figure to stand against | The news almost never states a price: none of the deals held does. The comparables say so and show no median price. |

## 2. The twenty largest AI-power rows, each against its story's headline

The AI view's two lists as they stand on 16 November (the ten with the most megawatts, the ten with the most US dollars, the capital deals left out), read against the titles of each row's stories in this machine's copy of `news_stories` and against the row's evidence sentence. A word search for the figure, then each line read by eye. No model.

- **Session 1851 read twenty rows of 5 November. These lists are not the same twenty**: the dollar list then held acquisitions and funding rounds, which the fix of faults row 3 took out, and four megawatt rows are new since (extracted 12 and 13 November). All twenty of today's lists were read.
- **17 of the 20 figures are in a headline of their own story**: all ten dollar figures, and seven of the ten megawatt figures.
- **3 megawatt figures could not be set beside a headline here**: the rows of 11 and 13 November (1,200 MW, 1,000 MW and 600 MW). Their stories are not in this machine's copy of the stories table, or the one title held states no megawatts. They are not called wrong; they are not checked.
- **What the headlines show that the rows do not** (faults rows 25 to 27 of `docs/reviews/deals-faults-2026-11-11.md`):
  - Three of the ten largest dollar rows are a pledge, a plan or a bet with one party, which the stricter prompt would not return (USD 52 billion, 40 billion and 33 billion).
  - Two are compute or infrastructure contracts whose kind is still "other" or "offtake" (USD 100 billion and 27 billion); the second is read as grid supply.
  - One megawatt row's kind is a power purchase where its headline says a step toward one (1,200 MW of generation equipment ordered).
  - One dollar row is a capital deal by its kind and is listed because its story names nuclear (USD 100 billion): the kind of supply reads a technology's word before the form.
- **Megawatts that are a ceiling**: one of the ten (2,800 MW, stated as "up to"). The row keeps the ceiling.

| List | Rows | Figure in a headline of the row's own story | Not checkable on this machine | New since 5 November |
|---|---:|---:|---:|---:|
| The ten with the most megawatts | 10 | 7 | 3 | 4 |
| The ten with the most US dollars | 10 | 10 | 0 | 0 |

## What the two parts say of the tracker

- **It is a reading of the news, not a tally of the market.** Against the two published tallies of 2025 it holds almost nothing, because its scored stories begin in earnest in October 2025 and a headline rarely states megawatts.
- **Its figures are the headlines' figures**: where a row states megawatts or dollars, the number is in its story's words (17 of 17 that could be checked).
- **Its weakness is what a row is, not what a row states**: pledges kept as deals, and funding rounds tagged AI power. That is the second reading the method note describes (section 10), which needs the key.

## The hosts read

| Host | Robots file | Read |
|---|---|---|
| `ceba.org` (reached from `cebuyers.org`) | allows every path, with a crawl delay of 10 seconds, which was kept | the press release of 17 March 2026 |
| `about.bnef.com` | allows every path | the release of 19 February 2026 |
| `www.leveltenenergy.com` | no rule (a sitemap only) | the index page of 14 April 2026 |
