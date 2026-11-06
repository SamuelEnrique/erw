# Session 3011 report: the queue by type; the deals and facilities not drafted

6 November 2026, about 12:17 to 12:25 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **7 drafts added to the review list** (module `deep.queues_deals_datacenters`, Berkeley Lab's Queued Up, US):
  - **The wait, by type:** the median months from request to commercial operation of the projects that came online in 2024 was:
    - wind: 81.1, against 21.1 for 2005's
    - solar: 69.8, against 22.2 for 2011's
    - batteries: 49.6, against 22.3 for 2015's
  - **Solar withdrawn rather than built:** 76.0 percent of the solar MW leaving the queue in 2024, against 100.0 in 2008 (2008's solar exits were nearly all withdrawals).
  - **The median request:**
    - solar: 120 MW in 2024, against 250 in 2006
    - wind: 200, against 81 in 2005
    - batteries: 152.8, against 20.0 in 2008
- **Three reproduction scripts printed their expected figures exactly.**
- **Not drafted, and why:**
  - **The AI-power deals' MW by quarter, and the deals' prices.** `energy_deals` begins in January 2025, and its quarters follow the news the ERW took in rather than the market: 2025's third quarter holds no deal, its second nine. MW is stated for few deals, and 2 of 529 carry a price.
  - **The datacenter facilities' MW against each grid's peak.** `datacenter_facilities` is an inventory begun in 2025, partial by its own method. A level against a peak would measure the inventory's coverage as much as the facilities.

## What it did

- **`deep/queues.py`:** three candidates by type: `months_by_type`, `withdrawn_by_type`, `request_size`.
  - Each was loaded by itself (`--only`), so that the session cap did not stand in for the drafts already on the list.
  - Gas's wait and the withdrawn shares of batteries, gas and wind fail the hunt's tests.
- **`tests/test_session3011.py`** (1 test). With session 3009's: 4 passed.

## Decisions made without you

- **The deals and facilities are left to a later chain,** when their own years exist. A finding the data cannot support is not drafted.

## For Samuel's ruling

- None new.
