# Session 870 report: coal shipped to power plants: not written, for want of a key

23 October 2026, from 03:24 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0.

## Read these first

- **No table written.** EIA's route `coal/shipments/by-mine-by-plant` (69,067 annual records, 2008 to 2025) gives several records for one mine, plant, supplier, coal type and year, with different quantities, prices and qualities, and no field that tells them apart: 16,078 records (about 23 percent, among them the largest flows, such as Drummond's Mary Lee No. 1 to Gorgas in 2008, three records). They are separate deliveries (contracts or transport) that the route does not name. Chain 030's rule: such records have no key; do not invent one or sum them; take a unique route of the same subject. A table without them would leave out a quarter of the flows, so none was written and the trial's connector was removed.
- **The unique route is `coal/shipments/receipts`**: it carries the contract type and the transport mode (and the mine's basin and county), 57,066 annual records from 2008 (12 pages). It needs a session of its own; chain 048 gets one (session 879 adds it).
- **Decision 52 kept:** `Btu/lb` (a fuel's heat content per pound) joins the unit vocabulary for the receipts table, in the validator and `docs/datastandard.md`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 19 of 20 | the route list, two routes' metadata, one count, the trial's 14 pages, the receipts route's metadata and count |

## Decisions made without you

- Nothing written rather than a table missing a quarter of the shipments.
- The unit `Btu/lb` added now (it serves the receipts table next).

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: `warehouse/validate/erw_validate.py`, `docs/datastandard.md` (Decision 52). On the data machine only: the saved pages under `warehouse/raw/eia_coal_shipments/`, `runs/c047/s870/`.
