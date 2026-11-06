# Session 2919 report: the controllable load's path, read where ERCOT states it

6 November 2026, about 05:17 to 05:23 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: www.ercot.com, 5 attempts of the 10 allowed (`runs/s2919/probe.csv`, `probe_try1.csv`, `probe_try2.csv`). Two robots attempts failed in this machine's name resolution and never reached ERCOT; the third answered. Then the large-load page and one workbook. Nothing under `/misapp` or `/misdownload` was asked.

## Read these first

- **ERCOT states the steps of a Provisional Controllable Load Resource's connection, and no duration.** No faster path is stated.
  - **Robots** (read with its comments stripped): `/services/` and `/files/` are allowed. No rule names ClaudeBot, anthropic-ai or Claude-Web.
  - **Planning Guide Section 9** (session 2905's copy, `runs/license_reads/s2905/03_*.bin`, read again here):
    - **9.2.2.1(2):** Part A of Protocol Section 23 Form W goes to the Interconnecting DSP or TSP on or before **10 July 2026**, and from there to ERCOT on or before **24 July 2026**.
    - **9.3.2.1(1):** a PCLR's maximum Low Power Consumption is the peak Demand that may be served reliably each year.
    - **9.4.1:** ERCOT completes Form W's end date with the study's results; the ILLE then makes one of four elections in Part B.
    - **9.6.1(1):** Initial Energization is granted under 9.6(1) as for any Large Load, but no consumption above the LPC.
    - **9.6.1(2)** (PGRR145, "upon system implementation"): no consumption above the LPC until five conditions are met. They are registration as a Resource Entity with a QSE, the RIOO data and the Network Operations Model, good telemetry, the qualification tests, and ERCOT's written confirmation. None of the five carries a number of days.
  - **The large-load page** (`/services/rq/large-load-integration`, fetched today): the same Form W dates. Its links are the same as session 2002's copy of 23 October.
  - **The Batch Zero FAQ** (`Batch_Zero_Readiness_FAQs_V8.1.xlsx`, 113 rows): question 19 repeats the 10 July date for Form W. Question 37 says PCLRs carry "additional requirements". Neither states a duration.
- **For session 2924:** these are rows of `large_load_connection_rules` with their stated dates and no duration. The siting gaps row "ERCOT | Time to connect | the faster path for a controllable load" stays open: no faster path or shorter duration is stated.

## Decisions made without you

- **Session 2905's saved copy of Section 9 used**, not asked again. Its paragraphs are the current guide's (`09-071126.docx`).
- **The DNS failures retried** (twice) because no request had reached the host. Each attempt is counted against the ceiling.

## For Samuel's ruling

- None.
