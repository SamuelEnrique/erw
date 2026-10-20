# Draft: permission to read MISO's public market data by script and to republish it in a research warehouse

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent, and nothing was asked of MISO: MISO is paused since 4 October 2026 (`warehouse/metadata/paused_sources.csv`, [`docs/methods/miso_pause.md`](../../methods/miso_pause.md)). Fill what stands in brackets first.

Why it is needed: MISO's legal page (https://www.misoenergy.org/meet-miso/legal-and-privacy/, as the pause file holds it from 4 October 2026; not asked again, read 7 of `warehouse/metadata/license_reads.csv`) says: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." Every pull from MISO's servers is paused, and by the ruling of 12 October 2026 (session 207) the tables below show "license needed" in place of MISO's numbers from 21 October until a permission is recorded in `warehouse/metadata/license_status.csv`. The contact is not known (the page was not asked).

---

**To:** [MISO's legal or market data contact]

**Subject:** Permission to read MISO's public market data by script and republish it in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open, noncommercial record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw.

Your site's terms forbid automated access, so since 4 October we have stopped every request to MISO's servers. I write to ask whether we may resume, and on what terms.

What we hold of yours, read before the pause from MISO's public pages and reports:

- MISO's own tables: ancillary service prices (`miso_as_prices`, internal) and the interconnection queue (`miso_interconnection_queue`).
- MISO's rows in tables that compare grids: `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`.
- MISO's news releases as news items (`news_index`).

What I am asking for:

- Read MISO's public market reports by script, once a day, at the rate, times and file routes MISO sets (or through an API key or a bulk file, if you prefer).
- Publish the values as MISO states them, and figures computed from them, in tables, charts and downloads, with MISO named as the source and a link to the report.
- The same for a citable archive of those tables (the ERW's dataset on Redivis).
- [Only if the ERW may sell anything: the same in a paid product. Strike this line otherwise.]

What we offer:

- Attribution to MISO beside every figure, in the words you prefer.
- A link to MISO's own report for every series.
- No resale of MISO's raw files. We publish what we compute from them.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]
