# Session 3007 report: generation, the third part: the build-out

6 November 2026, about 11:52 to 12:05 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **11 drafts added to the review list** (module `deep.generation_pipeline`, state draft), from `warehouse/analysis/findings/deep/buildout.py`:
  - **What entered service** (today's operating generators, EIA-860M, by first year of operation):
    - Batteries: 16,372.5 MW in 2025, against 0 in 2010 (strength 121).
    - Utility-scale solar: 29,709.2 MW in 2025, against 242.6 in 2010.
  - **The battery fleet at the year's end:**
    - US: 43,678 MW at the end of 2025, against 250 at the end of 2015.
    - CAISO: 15,777 MW, against 9.
  - **The battery fleet's hours (MWh per MW):**
    - US: 2.77 at the end of 2025, against 0.61 in 2015.
    - ERCOT: 1.55, against 0.38.
  - **New batteries' hours:** 2.86 MWh per MW for the batteries that entered service in 2025. See the fault below.
  - **Wind turbines** (onshore, the US Wind Turbine Database):
    - Mean rated capacity: 3,804 kW for 2025's projects, against 1,512 in 2005.
    - Mean rotor diameter: 141.0 m, against 80.6.
  - **Residential solar's median installed price:**
    - California: USD 4,150 per kW DC in 2023, against 8,308 in 2001.
    - Massachusetts: 3,916, against 8,025 in 2009.
- **Five reproduction scripts printed their expected figures exactly.**
- **One loaded draft needs session 3017's correction:** new batteries' hours (`us_battery_hours`) compares 2025 with 2011, a year when about two units entered service.
  - The code now counts a year only from 100 MW entering service, so the claim starts in 2015 (0.53 MWh per MW).
  - The loader adds no draft while the same claim has an open draft. The row on the review list still says 2011 until the check replaces it.

## What it did

- **`deep/buildout.py`:** eight candidates.
  - **Rejected by the hunt's tests:** coal retired by year (1,200.6 MW in 2002, 2,626.0 in 2025) fails the typical-move floor. Wind, combined-cycle gas and gas turbines entering service fail their tests.
- **Found on the dry runs: session 3006's fault again.** An inventory's year (turbines installed, systems priced) was judged partial by its count, which grows over the years. Turbines had only 2012 to 2020 as full years.
  - Each such year now counts as one observation.
  - Turbines are counted from 2005.
  - A state's solar-price year needs at least 500 priced systems.
- **`tests/test_session3007.py`** (1 test). With session 3006's: 2 passed.

## Decisions made without you

- **The pipeline is hunted by what was built, not by what was planned.** `generator_pipeline_by_grid` holds two months. Planned dates can only slip if the ERW keeps EIA-860M's monthly snapshots, and a later chain can hunt that once a year of snapshots stands.
- **What entered service counts today's operating units.** A unit built and since retired is not counted, and the limits sentence says so.

## For Samuel's ruling

- **Should the ERW keep EIA-860M's planned generators each month as a snapshot** (a derived table for the first window), so that the pipeline's slippage by fuel and grid can be measured by year? The chain asks for that finding, and it cannot be drafted from what is held.
