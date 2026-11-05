# The nation's dams (the U.S. Army Corps of Engineers' National Inventory of Dams)

Energy Research Warehouse (ERW), method note written in session 987 (chain 055) for a table first written on 23 October 2026.

Tables: `usace_nid_dams`

## Publisher and address

U.S. Army Corps of Engineers (USACE), National Inventory of Dams (`https://nid.sec.usace.army.mil/`), its national download `https://nid.sec.usace.army.mil/api/nation/csv` (one CSV, 70 MB, its first line the date the data were last updated). Connector: `warehouse/connectors/usace_nid.py` (session 982). The host has no robots file (HTTP 404).

## Vintage and revision

Data last updated 22 October 2026 (the file's first line, written as `vintage`), retrieved 23 October. A snapshot (ceiling one request).

## Shape and variables

Entities, 92,788 dams in 52 states and territories. `entity_id` `usace_nid:<Federal ID>` (unique; the NID ID repeats for a dam's associated structures, 787 times, and is kept in `nid_id`); `entity_type` `dam` (Decision 57 of `docs/datastandard.md`); `name` the dam's name; `geo` US-<state>; `lat`, `lon`; `capacity_mw` and `status` empty; `operator` the owners' names. The rest are the inventory's fields renamed with their units: owner types and the primary one, primary purpose and purposes (2,532 dams list hydroelectric), associated structure, county, river, primary dam type, NID height (ft), dam length (ft), year completed, NID and normal storage (acre-ft), surface area (acres), drainage area (sq mi), maximum discharge (cfs), number of locks, the source agency and the record's date.

## Reading the file

- The first line must be the date; the headings must hold the fields above; a state not in the map, a dam without a Federal ID or a Federal ID given twice stops the run.
- Two dams give one coordinate of the two: the pair is left empty and the one given kept in `coordinate_given` (the validator refuses half a pair).
- The inventory's inspection, condition assessment, hazard potential and emergency action plan fields are not taken: the ERW holds dams for the energy they hold or could. A blank stays blank; nothing is filled.

## License

Not settled: the Corps' main site refuses the ERW's reader (read 165, HTTP 403) and the inventory's own site states no terms in its page (read 166). The data are a federal agency's; the question is Samuel's (session 983). The table is flagged public and held from the Stanford upload until it is settled.

## Cross-checks (sessions 982 and 987)

- `ornl_npd_potential`'s 597 non-powered dams (the 2012 assessment): 545 are in today's inventory by NID id, every one in the same state where ORNL gives one; 18 of them now list hydroelectric among their purposes.
- `ornl_eha_hydropower_plants` carries no NID id and cannot be joined.
- Session 987, against the code: `FIELDS` and `STATES` give the columns and states above; the counts computed from the rows.

## What it does not hold

- The safety fields (above), the dams' inundation maps, and the inventory's history.
