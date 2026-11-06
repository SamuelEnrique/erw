# Session 2905 report: the controllable load's path, read where ERCOT states it

6 November 2026, about 04:18 to 04:20 UTC, on lab-desktop (the data machine), chain 151, unattended. Model spend USD 0. Pulls: www.ercot.com 2 (the Planning Guide's index, its Section 9); the robots request failed at name resolution and was not repeated, and the robots file read at 03:30 UTC (session 2893) stood.

## Read these first

- **ERCOT Planning Guide Section 9, "Large Load Interconnection or Modification"** (`09-071126.docx`, 464 paragraphs), the Batch Zero process, states:
  - a Large Load is a new Load Facility, or a modification increasing a facility's aggregate peak Demand by **75 MW or more** (9.1);
  - an ILLE has **seven Business Days** from notice to post the financial security of 9.2.1.2(1)(c), and the DSP or TSP informs ERCOT within two Business Days (9.3.1(2)(a));
  - ERCOT gives the Batch Zero Interconnection Study report **on or before 9 April 2027** (9.3.1(2)(b)), and the refinement study's transmission plan within **90 days** after the commitment deadline (9.3.1(2)(d));
  - the TSP's short-circuit study is due at least 60 days before that (9.3.1(3)), and a TSP's cost estimates within 10 Business Days of ERCOT's request;
  - a Large Load that has not met Initial Energization within 365 days after its date (9.6) loses its place.
  - **Provisional Controllable Load Resources (PCLRs)** have their own information (9.2.2.1), treatment in the study (9.3.2.1), commitments (9.4.1) and energization requirements (9.6.1). None states a shorter duration than the Large Load's.
- **Not yet a table:** `large_load_connection_rules` is chain 153's session 2924 (it was chain 151's 2910), which takes these figures with their paragraphs. The document is kept at `runs/license_reads/s2905/`.

## Decisions made without you

- **The figures kept for the connection-rules session,** not written to a table built in haste.

## For Samuel's ruling

- None.
