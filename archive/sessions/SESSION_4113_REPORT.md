# Session 4113 report: the foreign publishers' source pages read again

Energy Research Warehouse (ERW). Chain 229, session 14 of 50, lab-desktop third window, 13 November 2026 11:34 to 11:38 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4110-licenses`.

## Read (reads 1784 to 1808)

- **12 robots files.** None refuses. CEB asks a 30-second crawl delay and ELES 5 seconds, both honoured. ens.dk names Claude-User but allows the page.
- **13 pages:**
  - the source page each table is read from, for AMM, CEB, ELES, Ghana's Energy Commission, the Danish Energy Agency, Mongolia's ERC, REN, Statistics Greenland, Statnett, Kosovo's ASK and PSE;
  - REN's linked "terms" page, which is about privacy;
  - ELES's English basic data page.

## Verdicts (5 new, each a copyright line with no grant: CNDC's precedent; 279 publishers with a verdict)

- **Ceylon Electricity Board:** "Copyright @ 2026 Ceylon Electricity Board Web Solution by slt.lk" (read 1796).
- **Energy Commission, Ghana:** "© 2026 Energy Commission." (read 1798).
- **Energy Regulatory Commission of Mongolia:** "© 2019 ERC | Developed by Creative Apps" (read 1800).
- **REN:** "© 2021 REN All rights reserved" (read 1801, the Data Hub's footer; the linked page, read 1807, is about privacy only).
- **ELES:** "© 2016 ELES, ALL RIGHTS RESERVED" (read 1808).
- **Their tables are all internal,** so they now agree.

## Still no terms on any page read

- AMM (Guatemala), the Danish Energy Agency, Statistics Greenland, Statnett, Kosovo's ASK (a bare "©" with no name), PSE, and Saudi Arabia's Ministry of Energy (its data reach the ERW through GASTAT, whose own policy excludes third-party material).
- Their seven internal tables stay "not settled".

## The tool

- **`license_confirm.py verdict --end PHRASE`:** ends the cut after a phrase, as `--start` begins it. Tested.

## Counts

- **Agreement:** 544 agree, 52 settled by a ruling, **0 disagree**, **26 not settled** (71 at session 4100), 24 waiting for a ruling.

## Tests

- **Test 205's read bound** raised by 40 more for this session's reads.
- **Tests 205, 4101, 4109 and 378:** 43 passed.

## Decisions made without you

- **Only a notice naming its owner counts as a copyright line** under CNDC's precedent. A bare "©" (Kosovo's) does not.

## For Samuel's ruling

- None new.
