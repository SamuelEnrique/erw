# Session 3811 report: NYISO's real time, refused for one second

Energy Research Warehouse (ERW). Chain 216, data machine (lab-desktop), 12 November 2026 21:19 to 21:26 UTC. Opus 5.5. Model spend USD 0. Requests: 7 to mis.nyiso.com (the address the daily run asks): the file of 9 November, then the connector's trial of three days.

## Read these first

- **The fault was this repository's, not NYISO's.**
  - NYISO's real-time zone file of 9 November stamps `09:40:01` after `09:35:00` (EST) in every zone: a regular stamp published one second late.
  - `iso_prices.rebuild_irregular_intervals` refused any interval over 300 seconds, so the 301-second interval failed the whole window ("11 intervals longer than 5 minutes ... first at CAPITL 2026-11-09T14:40:01Z").
  - Three daily runs (the catch-up, 14:00 and 18:04 UTC) therefore wrote none of NYISO's real time. The function's own docstring already said a regular stamp "is sometimes published a few seconds late (12:10:03 for 12:10)".
- **Fixed** (`9db769198`): an interval may run up to `LATE_STAMP_S` = 10 seconds over 5 minutes. A missing stamp leaves an interval of about 600 seconds, which the allowance never bridges; nothing is filled.
- **Proved:**
  - test 3811 (a stamp one second late passes; a missing stamp still refuses; the allowance is small), and test 2807;
  - a trial of `iso_prices.py nyiso --days 3` into `runs/c216/trial_nyiso/` with the fixed connector wrote `nyiso_rtm_zone_prices.csv` in full: 3,168 rows (11 zones, 96 quarter hours, 3 days), with "110 stamped off the regular 5-minute grid; none longer than 5 minutes". The validator passed. The trial's files stay outside the warehouse.
- **Without the fix it would have healed by itself tomorrow** (the window is the last 3 days, and 9 November leaves it), with 9 November lost. With it, the next run on main writes all three days.

## Decisions made without you

- **Ten seconds:** NYISO's late stamps seen so far are 1 to 3 seconds. Ten covers them with room and stays far from a missing stamp's 300 extra seconds.

## For Samuel's ruling

- None.
