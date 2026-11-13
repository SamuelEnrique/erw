# Spot-check log: the large-load research pass of 13 November 2026

Energy Research Warehouse (ERW), session 5300 (portable laptop, window P4). Two checks are made on every group before its rows enter `utilities_2026-11-13.csv`:

- **The quote check, every cite.** `verify_quotes.py` matches each quote, part by part, against the text of the copy the reader kept, on the page the cite names. A group enters only with every cite matched.
- **The reading check, one row in five.** `spotcheck.py` prints rows 1, 6, 11 and so on of each group, each value beside its words in place. I read whether the value is what the words say.

## The quote check

| Group | Rows | Cites | Matched |
|---|---:|---:|---:|
| entergy | 7 | 59 (68 before the changes below) | 59 |
| duke | 5 | 70 | 70 |
| dominion | 7 | 82 | 82 |
| southwest_california | 5 | 74 | 74 |
| pjm_east | 3 | 46 | 46 |
| aep | 7 | 103 | 103 |
| texas | 8 | 119 | 119 |
| southern_florida | 5 | 80 | 80 |

## The reading check

| Row | Verdict | What I read |
|---|---|---|
| entergy-01 | **corrected** | The ESA's term (20 years, 3-year non-renewal notice), its minimum monthly charge and its early termination fee came from the AAE/UCS intervenor witness's summary of ELL's Table 4, not from ELL's own filing (the LPSC e-docket's document list answered HTTP 500). Window A's method writes a figure only quoted by an intervenor as a note, never as a value. These three fields are now "not published", with the words kept in the notes. The collateral keeps only ELL's own discovery answer (p. 103, reproduced as an exhibit). |
| entergy-02 | **corrected** (found while reading entergy-01) | The 15-year term and the description of the minimum charges came from IEEFA witness Kunkel's testimony (an intervenor). The term is now "not published", with the words in the notes. The minimum charge keeps only the settlement term sheet's words (p. 19). |
| entergy-06 | pass | The Minimum Demand Charge and the twenty-year term are EAL's own witness's words in EAL's application (APSC 25-055-P, doc. 94). The status date is the filing stamp, 19 October 2026. |
| duke-01 | pass | Settlement Exhibit 1, pp. 22 to 24: the contract term by size, the 24-month extension notice, the letter of credit, the security equal to the liquidated damages, and the notification periods of 24, 36 and 48 months all read as written. |
| dominion-01 | pass | The SCC's Final Order of 25 November 2025 (PUR-2025-00058), read as Exhibit A of a Florida PSC filing (the SCC's host is paused). pp. 31 to 35: 25 MW and a 75 percent load factor, minimums of 85, 85 and 60 percent, a 14-year term with a ramp of up to four years, 1.5 million USD per MW of collateral, and the exit fee. The queue comes from Dominion's slides to PJM (29 September 2026), pp. 2 and 6. |
| dominion-06 | pass | NOVEC's news release of 17 July 2026. It says only that a filing was made: no terms, all fields "not published". |
| southwest_california-01 | pass | PG&E Rule 30 (tariff book): no MW figure printed (50 to 230 kV); the Advance and the pre-funding loan; no exit fee as such. The queue comes from PG&E's Q3 2026 deck on EDGAR. |
| pjm_east-01 | pass | PPL LP-6 in the PA PUC's copy of the compliance tariff. The filing prints the LP-6 sheets twice, a marked and a clean copy; the cited pp. 243 to 245 are the clean copy. Threshold, ESA terms (1) to (10), the interruptible option and the exit fee all read as written. The queue comes from PPL's 8-K of 6 November 2026. |
| aep-01 | pass | Schedule DCT 1st Revised Sheets 223-1 to 223-8 (pp. 113 to 118) for the term and the exit fee. The study steps come from AEP Ohio's own pages (internal) and the load-study report (pp. 4 to 5). The queue comes from AEP's slides to PJM (p. 6) and the PUCO Chair's testimony. |
| aep-06 | pass | PSO's large-load terms appear only as an open issue in AEP's 10-Q: no terms, all fields "not published". The status date "2026-01" is printed only to the month. |
| texas-01 | pass | Oncor's Q3 2026 10-Q and its Exhibit 99.1: the 75 MW Batch Zero framework, the 50,000 USD per MW security, the conversion of cash into letters of credit, and the queue of 795 requests (293 GW data centers, 19 GW other). The docket correction (58306) is printed in the 10-Q. |
| southern_florida-01 | pass | Georgia Power's rules (pp. 4 and 16 of the December 2024 filing), the Commission's release of 23 January 2025 for the 5 to 15 year terms, the joint statement of 26 August 2026 on termination, the 2025 annual report for the 30-day contract review, the Q1 2026 large-load report (pp. 5 to 6) for the queue. FPL's approval date (row 4) was read too, beside the sample: the order's own first pages, ORDER NO. PSC-2026-0022-S-EI, issued 22 January 2026. |
| texas-06 | pass | EPE's amended NM filing, Exhibit MC-9 (pp. 235 to 238): 30,000 kW and 85 percent load factor, the billing demand terms, and the 20-year minimum initial term with a ramp of up to 4 years. |

## A fault in the checker, found and fixed

The printer showed the first copy of a quote in a document, not the cited page. A filing that prints a sheet twice (PPL's) looked like a wrong page. The quote check itself was right: it accepts a cite only when the words are on the cited page. The printer now shows the cited page first.
