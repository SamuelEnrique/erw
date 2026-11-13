# What a license costs: the published prices for redistribution or a data license

Energy Research Warehouse (ERW). Written by chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), session 4105, 13 November 2026, for Samuel. Nothing was sent or bought. A figure is written here only where the publisher's own page states it, with the read behind it (`warehouse/metadata/license_reads.csv`; the pages are kept outside git, in `erw-w3-work/license_reads` on lab-desktop). It is not legal advice. Every verdict is in [`docs/licenses.md`](licenses.md), and the four letters are in `docs/reviews/licenses/`.

## Read this first

- **Published prices were found for two publishers:**
  - **PJM** sells membership, and its data license lets members republish.
  - **ICE** publishes annual redistribution license fees for its futures exchanges.
- **CME Group publishes a fee list that could not be read:** its site refused the ERW's connection twice (reads 49 and 1704).
- **The other publishers that ask for permission state no price:** the grid operators NYISO, ISO-NE, MISO and SPP; the news outlets; the data center companies.
- **What a figure buys:** the cheapest stated route that would let the ERW republish one of its held publishers' data is **PJM's associate membership, USD 2,500 a year**. Whether it counts as "Member" under PJM's data license is the question the PJM letter asks.

## The prices, publisher by publisher

| Publisher | ERW tables it decides | Verdict today | The price, as the publisher's page states it | Page and read | Note |
|---|---:|---|---|---|---|
| PJM Interconnection | 2 (`pjm_rpm_capacity_prices`, `iso_all_capacity_prices`; internal) | needs a paid license | Associate member: annual membership fee USD 2,500, application fee not required. Voting member: annual fee USD 5,000; for market participants an application fee of USD 2,000 and a risk policy review fee of USD 1,500, both non-refundable. Ex officio member (state offices) and special member (emergency load reduction): USD 500 a year. Affiliate members: no annual fee. | https://www.pjm.com/about-pjm/member-services/membership-enrollment, read 1707, 13 November 2026 | PJM's data license (read 1702): "Members may republish data, however non-members are specifically prohibited from republishing data." Associate members "cannot transact or participate in the competitive wholesale market" (read 1707). Whether an associate member is a "Member" for republishing is not stated; the PJM letter asks. The "Become a Member" address (read 1706) now answers with a not-found page. |
| ICE (Intercontinental Exchange), whose hub prices EIA republishes | 1 (`eia_ice_electricity_daily`; internal) | needs written permission (ICE's data, as EIA's page names them, read 192) | Annual redistribution license, real-time, delayed and historical: ICE Futures U.S. commodities USD 30,000 for a non-member, USD 25,000 for a member; NDEX USD 10,000; public display license for ICE Futures U.S. commodities USD 3,000. Derived data, end of day, for use in indices that are not sublicensed: USD 10,000 per product. | https://www.ice.com/publicdocs/Fee_Overview_2027.pdf, read 1709, 13 November 2026 (the 2026 overview, read 1708, lists trading-screen fees only) | The fees are those of ICE's futures exchanges. The day-ahead hub prices EIA republishes come from ICE's over-the-counter platform, whose data license may be priced separately: ICE Data names no price for it on the pages read. |
| CME Group (NYMEX), whose futures settlements EIA republished | 1 (`eia_all_futures_prices`; internal) | not settled (its page could not be read) | Not read: www.cmegroup.com refused the connection (read 49, 12 October; read 1704, its robots file, 13 November). CME publishes a market data fee list and its licensing schedules on that site. | none | A person reads CME's current fee list. The table is internal, so nothing waits on it. |
| NYISO | 31 (34 held by grid in `license_status.csv`) | needs written permission | None stated. | legal notice, read 1670; contact page, read 1703 | No contact for permissions is named; the letter writes to NYISO's address. |
| ISO New England | 37 | needs written permission | None stated. | legal and privacy page, read 1672 | The page names info@iso-ne.com for permission to use a graph, chart or image. |
| MISO | 30 | needs written permission | Not asked: MISO is paused (its terms forbid automated access). | none since 4 October | The letter's address waits for a person. |
| SPP | 38 | may be public; needs written permission if the ERW sells anything | None stated. | terms, read 1671 | Needed only for a commercial publication. |
| Natural Gas Intelligence | 10 | needs written permission | None stated; the page names an "NGI Data Feed" and a "Corporate Licensing Agreement". | read 28 (12 October) | |
| WSJ (Dow Jones), Bloomberg, Financial Times, Reuters and the other news outlets | 10 or fewer each | needs written permission | None stated on the pages read (October). | `docs/licenses.md`, "The publishers' prices" | The news tables' public fields are links and the ERW's own fields; their text is in internal tables. |
| FRED (Federal Reserve Bank of St. Louis) | its tables retired | needs written permission | None: FRED charges nothing, and its terms limit storage and redistribution. | read 12 (12 October) | Each FRED series has a primary source (EIA, the Federal Reserve Board) that the ERW can read instead: `docs/state/data_requests_licenses.md`. |

## For Samuel's ruling

- **Whether to pay for anything.** Default: **no purchase**. Every held table keeps "license needed" until a permission is recorded in `warehouse/metadata/license_status.csv`. The letters ask first whether a free permission is possible.
