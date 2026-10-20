# Draft: permission to republish NYISO's public market data in a research warehouse

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: NYISO's legal notice (read 5 of `warehouse/metadata/license_reads.csv`, https://www.nyiso.com/legal-notice, 12 October 2026; a copy saved on 7 October under `warehouse/raw/nyiso_load_queue/`) says: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety." By the ruling of 12 October 2026 (session 207) the tables below show "license needed" in place of NYISO's numbers from 21 October until a permission is recorded in `warehouse/metadata/license_status.csv`. The page names no contact: the address below is to be found.

---

**To:** [NYISO's legal or market data contact: the page names none]

**Subject:** Permission to republish NYISO's public market data in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open, noncommercial record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw.

What we hold of yours, all from NYISO's public pages and reports:

- NYISO's own tables: day-ahead and real-time zonal prices (`nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`), day-ahead cleared energy (`nyiso_dam_cleared_energy`), ancillary service prices (`nyiso_as_prices`), hourly zone load (`nyiso_zone_load_hourly`), the interconnection queue (`nyiso_interconnection_queue`) and the large-load queue (`nyiso_load_queue`).
- NYISO's rows in tables that compare grids: `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_rt_top_intervals`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `battery_stack_review_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`.
- NYISO's market notices as news items (`news_index`).

What I am asking for:

- Read those public reports by script, at the rate and times NYISO sets.
- Publish the values as NYISO states them, and figures computed from them (averages, spreads, comparisons with other grids), in tables, charts and downloads, with NYISO named as the source and a link to the report.
- The same for a citable archive of those tables (the ERW's dataset on Redivis), version by version.
- [Only if the ERW may sell anything: the same in a paid product. Strike this line otherwise.]

What we offer:

- Attribution to NYISO beside every figure, in the words you prefer.
- A link to NYISO's own report for every series.
- No resale of NYISO's raw files. We publish what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or an API key if you prefer.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]
