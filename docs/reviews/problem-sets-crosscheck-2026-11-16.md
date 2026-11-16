# The problem sets (/learn/problems): the cross-check, 16 November 2026

Energy Research Warehouse (ERW), session 7534 (chain 304, part A), on samueloldlaptop. The figures the problems rest on,
as the live sets showed them on 16 November 2026 at 22:51 UTC (the reads kept in `replication/problem_sets/`), beside
what a publisher says. No figure is adjusted to match. The method: [`docs/methods/problem_sets.md`](../methods/problem_sets.md).

**What was read, and how.** This session made no new web request. Set C's five event figures are the rows of
`event_window_daily` that the event pages print, and session 7531 read the operators' and FERC's own accounts of the
same events today, robots files first (ferc.gov, caiso.com, ercot.com and pjm.com allow the paths read; nerc.com was
not read, its robots file disallows ClaudeBot; FERC's copies of the joint reports were read instead): its table is
`docs/reviews/events-crosscheck-2026-11-16.md` on `wip/7531-events`, and the rows below cite those documents as it read
them. The other figures stand against files already in the repository: EIA's average retail price
(`eia_retail_electricity_prices`, EIA API v2, retrieved 5 November 2026), the tariffs and statutes quoted word for
word in `site/data/bill_rules.json` and `site/data/severance_rules.json`, and Lazard's illustration as
`docs/methods/cost_of_power.md` quotes it. Not read: ERCOT's and CAISO's own daily load and fuel-mix reports for 15
November 2026, ERCOT's tie-line schedules, the New Mexico Taxation and Revenue Department's rate table from September
2026 on.

**Why they differ, in general.** The sets' grid figures are EIA-930's hourly demand and generation as each operator
reported them to EIA, by UTC or local day. An operator's own record may be an instantaneous reading (CAISO), a settled
hourly load (ERCOT) or a load with losses allocated (PJM).

| # | Set, question, figure | Ours (as the page shows it) | Theirs (publisher, document, date) | Difference | Why |
|---|---|---|---|---|---|
| 1 | C, worked example: Uri, ERCOT's highest hour of demand | 69,215 MW, 2021-02-14 | 69,871 MW, "ERCOT's 2021 all-time winter peak load" (FERC, *The February 2021 Cold Weather Outages in Texas and the South Central United States, Tracking of Responses to Recommendations*, December 2022, page 2; read by session 7531) | -656 MW (-0.9 percent) | EIA-930's hourly demand against ERCOT's peak load as the report gives it, with no hour |
| 2 | C, question 3: Elliott, PJM's highest hour | 135,328 MW, 2022-12-23 | 135,296 MW, PJM's figure in note (c) of Figure 13; 134,189 MW with 500 kV losses allocated, Figure 13 (FERC, NERC and Regional Entity Staff Report, *Inquiry into Bulk-Power System Operations During December 2022 Winter Storm Elliott*, October 2023, pages 30 and 31; read by session 7531) | +32 MW (+0.02 percent); +1,139 MW (+0.8 percent) | The report says the two PJM figures differ by how load is defined; same day |
| 3 | C, question 4: ERCOT's highest hour, summer 2023 | 85,432 MW, 2023-08-10 | 85,464 MW, 10 August, "all-time peak demand record" (ERCOT, *ERCOT Provides New Look at Peak Demand Records*, 14 September 2023; read by session 7531) | -32 MW (-0.04 percent) | Settled hourly load against EIA-930's hour; same day. The highest price fell on 6 September, the day of ERCOT's energy emergency, not on the peak's day, as the answer says |
| 4 | C, question 2: CAISO, August 2020, the day furthest above normal | 18 August (23.50 percent above the baseline); 14 August 10.74 percent | 18 August is the highest of the four days' "Actual Peak": 47,120 MW, against 46,802 MW on 14 August (CAISO, CPUC and CEC, *Final Root Cause Analysis, Mid-August 2020 Extreme Heat Wave*, 13 January 2021, Table 5.1, page 78; read by session 7531) | same day; the report gives no baseline in percent | Both put the window's highest demand after the outage days of 14 and 15 August |
| 5 | C, questions 1 and 5: Uri's highest 15-minute real-time price at ERCOT's hub average | 9,051.55 USD/MWh, 2021-02-17 | none read gives a price | none stands against | Above the USD 9,000 offer cap because the hub average includes ERCOT's real-time adders; the table's daily means stayed between 8,970 and 9,002 USD/MWh on 16 to 18 February (session 7531's row 3) |
| 6 | B, question 4: Oncor's default bill, 600 kWh | 95.27 USD, 158.8 USD/MWh | 158.8 USD/MWh, Texas residential average, July 2026 (EIA, *Electric Power Monthly*, average retail price, as `eia_retail_electricity_prices` holds it, `eia:retail_price:TX:RES`); 159.1 in August 2026 | 0 by construction against July; -0.3 USD/MWh against August | The bill's retail energy charge is set so the default bill equals EIA's July average (`site/data/bill_rules.json`, `energy_default.arithmetic`) |
| 7 | B, question 3: PG&E's default bill, 600 kWh | 229.63 USD, 382.7 USD/MWh | 297.5 USD/MWh, California residential average, August 2026; 336.1 in July (EIA, the same table, `eia:retail_price:CA:RES`) | +85.2 USD/MWh (+28.6 percent) against August | EIA's average is every California utility and every customer, CARE and FERA discounts and the semi-annual climate credit included; the default is PG&E's Income Tier 3 without a discount, in winter, at 20 percent peak use. Not a fault: a definition |
| 8 | B, questions 3 and 4: the wholesale share of the bill | 11.72 percent (PG&E), 24.88 percent (Oncor) | none read for these two bills | none stands against | The share is the bill's kWh at the month's load-weighted hub price over the bill: a figure of the ERW's own |
| 9 | D, question 5: the Comptroller's certified price, August 2026 | 1.36 USD/Mcf (2005 dollars), 100 percent credit | the same price, as `site/data/severance_rules.json` quotes the Texas Comptroller's table (tx_cpa_lp_gas, certified prices as of 2026-08) | 0 | The page reads the file; the tier rule is the Comptroller's ("USD 2.50 or less: 100 percent credit") |
| 10 | D, question 4: the three states' oil tax rates | Texas 4.6 percent (or 4.6 cents a barrel), Louisiana 12.5 percent, New Mexico 3.75 + 3.15 + 0.24 percent | Tex. Tax Code Sec. 202.052(a); La. R.S. 47:633; New Mexico TRD rate table for 1 April to 31 August 2026, each quoted in the rules file | 0 for Texas and Louisiana | New Mexico's table for October 2026 was not read: the period is said on the page (faults row 4) |
| 11 | E, question 4: the battery's annual debt service | 6,783,357 USD (100 MW, 1,110 USD/kW, 60 percent debt at 8 percent over 20 years) | Lazard's own illustration, as `docs/methods/cost_of_power.md` quotes it: 300 MW of wind at 1,900 USD/kW gives 342 million of debt and 30.4 million a year; the same formula gives 30.38 million | -0.02 million (rounding) | The formula reproduces Lazard's own case; the battery's figure is the same formula at Lazard's 4-hour battery midpoint |
| 12 | A, questions 1 and 2: ERCOT's and CAISO's peak hour and gas share on 15 November 2026 | 54,008 MW and 25,964 MW; 47.74 and 34.72 percent | none read | none stands against | EIA-930 is the publisher's own series; the operators' daily reports for the day were not read |
| 13 | E, questions 1 and 2: ERCOT's ties and the top net exporter, 15 November 2026 04:00 UTC | 2 neighbors (SPP, 144 MW in; CENACE, 1 MW); SRP 5,559 MW net out | none read | none stands against | EIA-930's interchange is the publisher's own series; ERCOT's direct-current ties to SPP and Mexico are several each, as the question's why says |

**What none stands against.** The ratios, differences and shares the questions ask for (each is two figures of the
same table, recomputed by the replication: 146 of 146), the merchant plant's capture rate and storm earnings (the
seller's model on its snapshot, `docs/methods/cost_of_power.md`), the game's battery (an assumption), and the dated
edition's figures (the replication recomputes 89 of 92 from the edition's own downloads and names the 3 it cannot).
