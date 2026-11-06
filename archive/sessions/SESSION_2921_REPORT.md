# Session 2921 report: the tariff registry, the utilities still missing

6 November 2026, about 05:26 to 05:32 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: 16 requests of the 25 allowed (`runs/s2921/probe.csv`; bodies in `runs/license_reads/s2921/`). Robots came before every other request to a host, and terms before any tariff.

## Read these first

- **PG&E's Schedule B-20 is in the registry** (`warehouse/sources/large_load_tariffs/pacific_gas_and_electric_schedule_b20_transmission.yaml`). It is the schedule for customers with maximum demands of 1,000 kW or more; new customers above 999 kW are placed on it (Sheet 1). Its figures:
  - **min_demand_mw 1:** "SERVICE TO CUSTOMERS WITH MAXIMUM DEMANDS of 1000 KILOWATTS or MORE" (page 1, Sheet No. 57687-E).
  - **demand_charge_transmission 11.03 USD/kW-month:** "Transmission Maximum Demand* $11.03" at transmission voltage (page 5, Sheet No. 61082-E, Advice 7846-E, effective 1 March 2026).
  - **demand_charge_distribution 6.13 USD/kW-month:** the distribution Maximum Demand at transmission voltage, "$6.13 (R)" (page 5).
  - Left out: the time-of-use generation and peak demand charges, the time-of-use energy rates, and the customer charge. The customer charge is printed "per meter per day", a unit the registry does not take.
  - The document is PG&E's filed tariff book (`https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_B-20.pdf`, read 05:27:32 UTC).
  - Robots: every path but `/mobile/` is open to this reader (GPTBot is disallowed by name).
  - PG&E links no terms of use on its tariff pages or in its 863-address sitemap, only privacy pages.
- **`utility_large_load_tariffs` written again** (`runs/c147/write_table.sh`, the branch's registry, under the data lock): **13 rows, 5 schedules, 4 utilities** (3 new rows). Validator pass, coverage row, archive run `20261106T052944Z-local`. Commit `c6ccbf167`. Test 2871: 9 passed.
- **Also read:** PG&E's Electric Rule 30 (transmission-level retail service, interim, Advice 7772-E, effective 4 December 2025). It prints its terms in days and months: 18 months of fixed design standards, 20 business days to send a CCA a copy of the application, payment within 45 calendar days of an invoice, and a 10-year load forecast. It has no figure of the registry's variables, so it is not written. It is for `large_load_connection_rules` (session 2924).
- **The three others are closed to this reader at their own sites:**
  - **Con Edison:** robots allows all, but its General Terms of Service forbid any "robot, spider, site search/retrieval application or other manual or automatic device to retrieve ... Service content ... without Service Provider's express prior written consent". The tariff (PSC No. 10) was not asked.
  - **Eversource:** robots disallows `/docs/` to every reader. Its terms say "Use of any website material is prohibited without express written permission from Eversource" and that its content is not to be used "for business, commercial, or political purposes".
  - **Duquesne Light:** robots is empty, but the home page answered with an Incapsula script challenge (212 bytes), not the site. Chain 148 found the PA PUC's search runs in its pages' script.

## Decisions made without you

- **PG&E's filed sheets taken as public.** Each is the CPUC-filed sheet itself, the CPUC states its documents are in general public domain, and PG&E states no terms on these pages.
- **Only the two transmission-voltage components printed as one monthly figure** were written. B-20's totals bundle generation, distribution and transmission.
- **No commission search guessed** for Con Edison (NY PSC), Eversource (CT PURA, MA DPU) or Duquesne (PA PUC). Each needs a document address not known here, and 9 requests were left unspent.

## For Samuel's ruling

- **PG&E's tariff book as public:** whether a utility's filed tariff, read from its own site where it states no terms, may stand public in this table.
- **Con Edison and Eversource:** whether to ask each for written permission. Their terms bar automated reading of their sites.
