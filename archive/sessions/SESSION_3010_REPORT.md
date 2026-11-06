# Session 3010 report: datacenters, by the Census Bureau's years

6 November 2026, about 12:15 to 12:25 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **10 drafts added to the review list** (module `deep.queues_deals_datacenters`, state draft), from `warehouse/analysis/findings/deep/datacenters.py`:
  - **Building data centers:**
    - Private data center construction put in place: USD 49.7 billion in 2025, against 1.8 billion in 2014 (strength 20.9).
    - Its share of private nonresidential construction: 6.35 percent in 2025, against 0.50.
  - **Building power:** private electric power construction put in place: USD 128.0 billion in 2025, against 16.4 billion in 1993.
  - **Data processing and hosting (NAICS 518210, County Business Patterns, 2012 to 2023):**
    - Mid-March employment: 629,527 in the US in 2023, against 433,438 in 2012. California: 123,859, against 70,508.
    - Establishments: 18,544 in the US, against 13,950. California: 2,698, against 2,097.
    - Annual payroll per employee: USD 147.7 thousand in the US, against 90.0 thousand. New York: 247.2 thousand, against 101.1.
  - **Revenue of NAICS 518** (Quarterly Services Survey): USD 374.9 billion in 2024, against 55.4 billion in 2004.
- **Five reproduction scripts printed their expected figures exactly.**

## What it did

- **`deep/datacenters.py`:** seven candidates on three public Census series, with a test (`tests/test_session3010.py`, 1 test, passed). 160 claims, 134 passed; the states kept are the largest moves after the US.

## Decisions made without you

- **The ERW's own deal and datacenter tables are not hunted by year.** `energy_deals`, `datacenter_projects` and `datacenter_facilities` begin in 2025, and the hunt's tests need four full years. The chain's questions on them need another test:
  - the AI-power deals' MW by quarter
  - the deals' prices by technology
  - the facilities' MW against each grid's peak

  Session 3011 asks them as levels, not as changes.
- **The construction figures are nominal dollars,** and the limits sentence says so.

## For Samuel's ruling

- None new.
