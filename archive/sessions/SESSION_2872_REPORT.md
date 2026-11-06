# Session 2872 report: the registry filled, the first utilities

5 November 2026, about 21:37 to 21:56 UTC, on lab-desktop (the data machine), chain 147, unattended, done while session 2863's landing gate ran. Model spend USD 0. Pulls: 5 of 25, all to AEP's hosts (www.aepohio.com 3, www.aep.com 2). The schedules written here were read from copies the data machine saved on 8 October 2026; no request was made for them.

## Read these first

- **Four schedules of three utilities are in the registry** (`warehouse/sources/large_load_tariffs/`, commit after `2871`). Each figure carries its page and printed words. `large_load_tariffs.py --check` gives 4 schedules, 10 rows, 3 utilities:

  | Utility | Schedule | Figures | Filing |
  |---|---|---|---|
  | Georgia Power (EIA 7140, SOCO) | Rules and Regulations A1, D13, D14, customers of 100 MW or more, effective 1 February 2025 | min_demand_mw 100; the minimum bill, credit and termination terms in the rules' words | GA PSC Docket 44280, the request of 11 December 2024 (pages 4, 16), approved 23 January 2025 |
  | Indiana Michigan Power (EIA 9324, PJM) | Tariff I.P., terms for customers at or over 70 MW individually or 150 MW aggregated | min_demand_mw 70; min_contract_years 12; min_bill_pct 80; collateral_months 24; the ramp (5 years at most), notice (42 months) and exit fee in the tariff's words | IURC Cause 46097, the order of 19 February 2025 and its Attachment A (sheets 21.3 to 21.7, PDF pages 69 to 73) |
  | Indiana Michigan Power | Tariff I.P., transmission service (code 324), effective 28 May 2024 | demand_charge 10.194 USD/kW-month; fixed_charge 275 USD a month | the same order's Attachment A, sheet 21 (PDF page 66) |
  | Portland General Electric (EIA 15248, PGE) | Schedule 96, data centers of 20 MW and above | min_demand_mw 20; min_contract_years 10 (scaling to 30 at 220 MW, in the order's words); min_bill_pct 90; the exit fee in the order's words | Oregon PUC Order No. 26-309 (UM 2377), pages 1, 7, 16 |

- **AEP Ohio was not read.** AEP's legal notice (www.aep.com/terms, which aepohio.com's footer links) authorizes copies "for your personal use only" and forbids copying "for redistribution to third parties for commercial purposes ... without the prior written permission of AEP". So the utility's site bars this reader. PUCO's docketing system is a host this project never asks: its document viewer answers with a reCAPTCHA (`policy_monitor_refresh.NEVER`). PGE's Schedule 96 replaces it, as the chain allows.
- **Dominion Energy Virginia was not read.** The Virginia SCC is paused (`paused_sources.csv`, its robots file disallows every automated request). Copies of SCC documents saved on 8 October, before the pause, are on this machine (the GS-5 case, PUR-2025-00058). They were not used: the pause came because the robots file refuses automated reading.
- **Entergy Louisiana and Entergy Texas** were not reached in this session's time.
- **Cross-check (I&M), a check, not a correction:** EIA-861 for 2024 gives I&M Indiana's retail revenue as USD 2,113,375,000. Over its summer peak of 3,924 MW that is USD 44.88 per kW-month, all classes and all charges (energy included). Tariff I.P.'s transmission demand charge of USD 10.194 per kW-month is the demand part of one class's bill, so it should be well below that figure, and it is.
- **The table is not written yet.** The registry is filled by sessions 2872 to 2874, and the write (data lock, validator, coverage, archive) comes with them (see session 2874).

## Decisions made without you

- **Saved copies of public filings were read in place of a new request.** Georgia PSC, IURC and Oregon PUC documents fetched by `large_load_rules.py` on 8 October 2026; each row's `retrieved_at` is that fetch's time.
- **This table is licensed public, as the chain rules.** The rows those documents fed in `large_load_rules_internal` were held internal: that table quotes sentences at length, and Georgia PSC links no terms page.
- **Two I&M schedules, not one.** The rates (effective 28 May 2024) and the large-load terms (approved 19 February 2025) have different dates.
- **The Large Load sheets' own effective date is a blank line,** so the order's date stands for it. For PGE, the date of Order No. 26-154 stands for Schedule 96's.
- **No energy charge for I&M:** Tariff I.P. prints two energy blocks per kWh of demand, not one charge.
- **Bundled demand charges are recorded as printed.** The tab's rule (siting decision 22) keeps a bundled rate's energy apart.

## Errors

- **I asked www.aep.com/terms before www.aep.com/robots.txt,** and the data center tariff page on aepohio.com before reading the terms. The robots file, asked afterwards, does not exist (HTTP 404). Nothing was taken from either page.

## For Samuel's ruling

- **AEP's terms** ("personal use only"): whether the ERW may read AEP Ohio's and AEP's other utilities' tariff pages, or only PUCO's docket, which needs a person past its reCAPTCHA.
- **The Virginia SCC copies saved before the pause:** whether they may be used for Dominion's GS-5 figures.
- **This table's license versus `large_load_rules_internal`'s:** the same filings are quoted there under an internal license.

## Files

- On `wip/c147-data`: `warehouse/sources/large_load_tariffs/georgia_power_rules_100mw.yaml`, `indiana_michigan_power_tariff_ip_large_load.yaml`, `indiana_michigan_power_tariff_ip_transmission.yaml`, `portland_general_electric_schedule_96.yaml`, this report.
- On the data machine only: `runs/s2872/` (probe, notes, `pages.py`, `text.py`, I&M's extracted sheets), `runs/license_reads/s2872/`.
