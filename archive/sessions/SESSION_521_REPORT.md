# Session 521 report: the EIA-861M gaps, read

21 October 2026, from 20:29 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/027-night-22-october-sources.md`. Model spend USD 0. No pulls; no table changed.

## Read these first

- **The gaps are what the two forms count, not a fault of the reader.** Sessions 511 and 520 found that 11% to 18% of the utility-states differ by over 10% between EIA-861M's twelve months and EIA-861's annual total sales. `runs/s521/gaps.py` (on the data machine) grouped every utility-state of 2017 to 2025 (5,325) by the annual form's parts, service types and ownership.

  | Annual parts | Months low by over 10% | Within 10% | Months high by over 10% |
  |---|---|---|---|
  | A (bundled) only | 28 | 4,547 | 83 |
  | A and C (bundled and delivery-only) | 548 | 98 | 0 |
  | A and B, A and D, A, B and C | 21 | 0 | 0 |

- **A and C, the most of it.** A utility that also delivers energy that others sell, under customer choice (Massachusetts Electric, Baltimore Gas & Electric, Niagara Mohawk, PG&E), reports in EIA-861M only the sales it bundles. The annual total adds the delivery-only service. Against part A alone, the 646 such utility-states agree at a median of 1.0000: 97.8% within 2% and 99.7% within 10%.
- **Part A only, months high: behind-the-meter owners.** 76 of the 83 cases where the months run high, and 22 of the 28 where they run low, have the ownership "Behind the Meter": third-party solar owners such as EverBright and Greenskies. Their 1,471 utility-states agree at a median of 1.000, with a long tail (up to 1,099 times). Their small annual figures make any timing difference large.
- **Parts B and D** (energy-only and power-marketer service) explain the 21 utility-states with those parts, all of whose months run low.
- **Unexplained: 13 utility-states** with part A only that are not behind the meter: 9 investor-owned, 2 federal, 2 cooperative.
- **Nothing to fix.** A reader of both tables should compare EIA-861M against part A for a utility with delivery-only service. The two tables' headers already name the parts and x_part. No table, connector or test was changed.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| none | 0 | |

## For a later session

- The 13 unexplained utility-states, one by one, against EIA's own utility pages, if wanted.

## Files

- New: this report. `runs/s521/gaps.py` and its output stay on the data machine.
