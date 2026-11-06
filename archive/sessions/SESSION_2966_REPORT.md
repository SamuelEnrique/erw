# Session 2966 report: the connection rules

6 November 2026, about 09:02 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`large_load_connection_rules` already holds what the named operators' own documents allow** (chains 153 and 155: 39 steps of three documents, each with its threshold, its stated duration or date, and its words and place):
  - **ERCOT, "the rule under SB 6 and PGRR 115":** Planning Guide Section 9 (11 July 2026) is the guide as PGRR 115 and PGRR 145 (Batch Zero) left it, and it is held: 22 steps from the 75 MW threshold to the 9 April 2027 study report. SB 6 itself is the PUCT's rule (16 TAC 25.194), and the PUCT is restricted ("asks permission to copy text", `rules.json`), so it was not read.
  - **SPP's load interconnection procedures:** the High Impact Large Load process (Attachment BA) and its generation assessment (Attachment BB), as FERC's order ER26-247 states them, 13 steps (chain 155's session 2938). The thresholds are 10 MW at 69 kV or below and 50 MW above. The collateral: a USD 10,000 fee and a USD 100,000 deposit within 30 calendar days (page 8).
  - **PJM's large load addition process:** not read. PJM's terms say non-members may not republish (licenses.md #15).
  - **MISO's expedited resource addition:** not read. MISO is paused (`paused_sources.csv`).
  - **CAISO's load interconnection:** CAISO connects no load itself; the utilities do. PG&E's Electric Rule 30 is held (4 steps).
- **No row added, no request made.** The table's "stated duration in months" is in its `x_duration` and `x_duration_unit` columns (days, business days, months, years, as each document states it, never converted).

## Decisions made without you

- **The PUCT's rule under SB 6 not read:** its copy permission is not given.

## For Samuel's ruling

- **PJM's documents for this table:** whether its non-member terms allow a step's words and number to be quoted.
