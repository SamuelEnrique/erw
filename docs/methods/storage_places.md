# Batteries in every authority and state (`/storage/places`)

Session 8014, chain 581 (part F1), 20 November 2026. Builder: `warehouse/derived/storage_places.py`, a step of the data machine's daily run (`dm_storage_places`). Page file: `site/data/storage/places.json`. Page: `site/app/storage/places/page.tsx`. License: public (EIA).

## What exists, read first

`/storage` (three tabs) draws the battery fleet from `storage_capacity` (EIA-860M's battery units, prime mover BA) by status, by the seven ISOs (a unit's authority when it is one of them) and by state; the build-out by duration and grid; the owners. No view gave every balancing authority, or two places side by side. This page adds that; `/storage` does not change.

## Rules

- A battery is a unit of EIA-860M with prime mover BA, as `/storage` counts; pumped hydro, flywheels and compressed air are not counted.
- A unit is placed by the balancing authority code and the state EIA-860M prints; a unit with no authority is counted under "not named".
- Operating MW is nameplate; MWh is EIA's nameplate energy capacity, summed only over the units that give it, with those units' MW beside it. Planned units have no MWh (EIA's planned sheet has no such column).
- By year of start: the MW of today's operating units by their operating year. A unit retired since is not in it.
- Planned: the units planned or under construction by the year of EIA's planned operation date, with the MW under construction.

On the edition of September 2026: 56,120.7 MW operating in 1,156 units, 154,272.4 MWh over the units that give it (56,103.2 MW of them), 44 authorities (and "not named", 238.9 MW) and 51 states. The operating MW equals the sum of `/storage`'s "Batteries operating in the US" from the same edition when both read the same file.

### Decisions (session 8014)

| Key | Decision | Default |
|---|---|---|
| `batteries` | Prime mover BA only | BA |
| `placed-as-printed` | By EIA-860M's authority and state | as printed |
| `mwh-as-given` | MWh only where EIA gives it | where given |
| `year-of-start` | Today's units by operating year | today's fleet by age |
| `first-two` | Opens on ERCOT and CAISO | ERCOT and CAISO |
