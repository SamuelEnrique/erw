# Draft: whether a non-member research project may republish PJM's capacity auction results

Written by session 378 (20 October 2026), brought up to date by chain 229, session 4104 (13 November 2026), for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: PJM's Data Miner 2 data license agreement, read again on 13 November 2026 (read 1702, https://www.pjm.com/-/media/DotCom/etools/edatafeed/data-license-agreement-edata-feed-data-miner-2.ashx; the same bytes as read 15 and the same sentence), says: "Permitted Use. Subject to Section 2 below, you may use the Data and the Tools for your internal business use or commercial purposes, including publishing and making derivatives of the Data, Members may republish data, however non-members are specifically prohibited from republishing data." The ERW is not a member, so its two PJM tables are internal. PJM's legal page (read 1701) adds: "Access to this website does not confer any license or ownership interest in either the form or content of the website", and names the General Counsel for inquiries.

Who to write to: General Counsel, PJM Interconnection, 2750 Monroe Blvd., Audubon, PA 19403 (PJM's legal page names this address for inquiries about its terms, read 1701, 13 November 2026). No email address is printed on either page.

---

**To:** General Counsel, PJM Interconnection, 2750 Monroe Blvd., Audubon, PA 19403

**Subject:** Republishing PJM's capacity auction results in an open research data warehouse

Hello,

I am Samuel [surname], [role] at Stanford University. I run the Energy Research Warehouse (ERW), an open, citable research warehouse of the US energy system at Stanford: prices, flows, projects and policy, each number traced to its source report. Its tables are versioned and citable as a dataset on Redivis, and its code and documentation are public at github.com/SamuelEnrique/erw. A public site shows figures derived from the tables (averages, spreads, comparisons between grids); it is in review and not yet open to visitors. The ERW sells nothing.

What we hold from PJM, all from PJM's public pages and reports (2 tables; the fields of each are listed in the appendix below):

- `pjm_rpm_capacity_prices`, `iso_all_capacity_prices`.

What I am asking for:

- Whether a non-member, noncommercial research project may republish the Base Residual Auction clearing prices by LDA (the tables listed below), with PJM named as the source and a link to each auction report.
- If not: the license or the membership class that would allow it, and its price.
- The same for the ERW's citable dataset on Redivis.

What we offer:

- PJM named as the source beside every figure, in the words you prefer, with a link to PJM's own report.
- No resale or redistribution of PJM's raw files as such: we publish the values in our tables and what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or a key if you prefer.
- A line in our records for your answer, so that every table shows the permission it rests on.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]

---

## Appendix: the exact tables and fields

Read on 13 November 2026 from each table's file on the data machine (its header's title, its columns, and for a series table the variables and units in PJM's rows, found by the entity, grid or market column). A table whose rows name no grid holds a figure computed across grids.

### `pjm_rpm_capacity_prices`

- Energy Research Warehouse (ERW): PJM RPM Base Residual Auction clearing prices by LDA
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- PJM's rows: 234; variables: `capacity_price_usd_per_mw_day` (USD/MW-day)

### `iso_all_capacity_prices`

- Energy Research Warehouse (ERW): capacity prices, PJM Base Residual Auction, NYISO ICAP spot auction, ISO-NE Forward Capacity Auction, MISO Planning Resource Auction
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_auction, x_period_end, x_note, x_license
- PJM's rows: 234; variables: `capacity_price` (USD/MW-day)

---

## The first draft (session 378), kept as it was

# Draft: whether a non-member research project may republish PJM's capacity auction results

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: PJM's Data Miner 2 agreement (read 15 of `warehouse/metadata/license_reads.csv`, the data license agreement of eData Feed and Data Miner 2 on pjm.com, 12 October 2026) says: "Permitted Use. Subject to Section 2 below, you may use the Data and the Tools for your internal business use or commercial purposes, including publishing and making derivatives of the Data, Members may republish data, however non-members are specifically prohibited from republishing data." The ERW is not a member; its two PJM tables are internal (`docs/licenses.md`: "needs a paid license", the price "not stated on the page", membership named as "Member or Associate Member status"). The page names no contact.

---

**To:** [PJM's market data or legal contact: the page names none]

**Subject:** Republishing PJM's capacity auction results in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open, noncommercial record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw.

What we hold of yours, kept internal and shown to no one today:

- The Reliability Pricing Model's capacity auction results (`pjm_rpm_capacity_prices`).
- PJM's rows in a table of every grid's capacity prices (`iso_all_capacity_prices`).

What I am asking:

- Whether a research project that is not a PJM member may publish those auction results, as PJM states them, in tables, charts and downloads, with PJM named as the source and a link to PJM's report.
- If membership is the only way: which membership class would cover it, and its annual cost.
- [Only if the ERW may sell anything: the same in a paid product. Strike this line otherwise.]

What we offer:

- Attribution to PJM beside every figure, in the words you prefer.
- A link to PJM's own report for every series.
- No resale of PJM's raw files. We publish what we compute from them.
- Data Miner 2's limit of six requests a minute, or any rate you set.

Thank you,
Samuel [surname]
[email address]
