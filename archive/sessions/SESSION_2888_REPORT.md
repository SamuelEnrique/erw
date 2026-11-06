# Session 2888 report: the connection rules, the wiring and the run's catch-up

6 November 2026, about 03:25 UTC, on lab-desktop (the data machine), chain 148, unattended. Model spend USD 0. Pulls: none (the ISOs' documents were not reached in the time; see below).

## Read these first

- **`large_load_connection_rules` not written.** The session's time went to sessions 2886 and 2893. Its rows are left for chain 151's session 2910, which takes them first. They would be ERCOT's SB 6 and PGRR 115 as ERCOT states them, PJM's large load addition process, and SPP's and CAISO's load interconnection procedures; MISO is paused.
- **Nothing to wire:** no tab row's utility is in the registry (session 2887).
- **The daily run's catch-up (run 42120465428, `days=7`)** committed "Daily prices 2026-11-06" (chain 147's session 2884):
  - The ISO tables' 30 October to 5 November days are in, where the publishers' lists still held them. ERCOT's real-time list keeps seven days, so the hours from 30 October were within it.
  - Three steps failed: EIA-930's CISO demand forecast (25 hours short over the clock change), PortWatch ("Invalid URL") and ERCOT's ancillary prices (HTTP 503 at `/misapp`).
- **Watch the 14:00 UTC run of 6 November** for the runner's rebuild of the CAISO mix and the board: chain 147's session 2885 put back 164 files it had thinned. That run comes after this chain's sessions, and chain 151's session 2913 reads it.

## Decisions made without you

- **The connection rules moved to chain 151** rather than run short.

## For Samuel's ruling

- None new.
