# Session 2061 report: the licenses' fourteenth round (FEMA, the Drought Monitor, NHC)

23 October 2026, from 20:29 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 2 requests of 20 (the Drought Monitor's home page and its About the Data page). `license_verdicts.csv` was read first.

## Read these first

- **This chain's publishers first:**
  - **FEMA** (`fema_disaster_declarations`): a verdict of its own from OpenFEMA's terms (read 217, the page session 2056 read and saved): "Users should cite the specific API endpoint ... Users must clearly state that 'This product uses the Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA ...' ... The logos and/or seals of FEMA and the Department of Homeland Security (DHS) may not be used without prior written authorization from FEMA or DHS." **May be public**, the statement in the table's header; the terms also let FEMA ask a user to stop using the data.
  - **NHC** (`nhc_hurdat2_track_points`): the National Weather Service's verdict (read 8, public domain) applies through its publisher's name; its robots file is now read 222.
  - **The Drought Monitor** (`usdm_drought_state_weekly`): **not settled yet.** Its home page and About the Data page state no terms; its Permission page (`/About/Permission.aspx`) would be a third page of the host, past the round's two. It is left to chain 068's licenses round (session 2089), which chain 067's agent writes into chain 068's file. The table stays "not settled" until then, so the Stanford target does not take it.
- **Reads 216 to 222** (FEMA's robots file and terms, the Drought Monitor's two robots files and two pages, NHC's robots file), first numbered 196 to 202 after chain 057's last (195), and renumbered 216 to 222 at the merge with chain 058, whose reads 196 to 215 landed first (session 2069).
- **The other unsettled publishers** wait on the rulings sessions 388, 888, 983 and 2019 set out; not asked again.
- **The record:** 400 tables, 86 publishers with a verdict, 200 requests; `licenses.py check` 0 problems.

## Errors

- **The home page was one of the host's two pages:** reading it to find the Permission page left no page for the Permission page itself. Asked directly, it would have been one request.

## Decisions made without you

- **The round's limit of two pages a host kept,** the Drought Monitor's verdict left to the next round.
- **FEMA's verdict may be public** with its required statement, the stricter reading of its "cease using" clause not taken as a bar.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (216 to 222, first numbered 196 to 202), `license_verdicts.csv` (FEMA), `license_tables.csv`, `docs/licenses.md`, this report.
- On the data machine only: `runs/c066/s2061/`, `runs/license_reads/s2061/`.
