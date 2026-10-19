# The stress days of the battery page: one rule for every grid

Energy Research Warehouse (ERW), session 297 (19 October 2026), from the chain prompt of 19 October, item 3: "use the rule recorded in the repository; if none is recorded, use this one and list it under Decisions made without you". The repository recorded no one rule: ERCOT's stress days were three named events chosen by hand (Winter Storm Uri, Winter Storm Elliott, the summer 2023 heat: `event_window.py`, `battery_stack.md`), and CAISO's a rule from its own notices (`battery_stack.md`, "CAISO's stress days", session 246). This note writes the one rule, which the data machine's builder (`warehouse/derived/battery_stack.py`, the table `battery_stack_stress_daily`) is to apply to every grid, and which the battery page's "leave out" boxes and its stress repeats read through that table.

## The rule

A **stress day** of a grid is a local operating day on which either holds:

1. **The price test:** the day's mean real-time hub price (the hub the page prices energy at: ERCOT `HB_HUBAVG`, CAISO SP15) is above the **98th percentile of the daily means of the 365 days before it** (the trailing year, the day itself left out). A day with any hour missing is not tested.
2. **The notice test:** the operator declared an emergency notice for that day, as the notices tables the warehouse holds say: for CAISO the system-wide notices of session 246's rule (`caiso_grid_emergencies`: a Flex Alert, Restricted Maintenance Operations, an Energy Emergency Alert watch or level 1 to 3, a Stage 1 to 3 emergency, a Warning, an Alert or a load interruption; not a Transmission Emergency or a voluntary load reduction). The warehouse holds no table of ERCOT's notices today (its Energy Emergency Alerts, Watches and Advisories are read from no source yet), so for ERCOT the price test alone applies until one is held; when one is, an Energy Emergency Alert of any level, a Watch or an Advisory for a reserve shortage or a load shed is a notice under this rule. Session 322 (the owner's default of 19 October 2026): `ercot_grid_notices` holds them, and the rows it marks `x_counts` yes are the notices: an EEA of any level, rotating outages, a conservation appeal or Voluntary Conservation Notice, a Power or Weather Watch, an Operating Condition Notice for extreme weather (as CAISO's Restricted Maintenance Operations count), and the day a release ends an emergency. The control room's Advisories and Watches held (May 2026 on) concern its own tools (a geomagnetic disturbance, a study that did not solve), not a reserve shortage, so none counts (`docs/methods/ercot_grid_notices.md`).

Days at most three days apart are **one event**, named for its first day (`<grid>_stress_<YYYYMMDD>`); an event that holds the days of a named event keeps the name the warehouse already uses for it (`uri_2021`, `elliott_2022`, `ercot_heat_2023`), so the page's words and the check keys that name them do not move. Only days the model solved count, as before.

## What it changes and what it does not

- **ERCOT's three named events stay** (each meets the price test on its own: February 2021, December 2022, August 2023) and the rule can add others: a day above the 98th percentile of the trailing year outside those windows becomes an event of its own, and so does a notice day. CAISO's events are the same as session 246's rule makes them, with the price test added.
- **One rule, no hand in it:** nothing is picked; an event appears when the prices or the operator's notice make it. The page's "leave out" boxes (session 296) list whatever events the table holds for the grid shown; the stress repeats (session 297) take the event whose window paid the most.
- **Not applied yet.** A code machine writes no warehouse data (the chain's rule 5): this note is the rule; the builder's change and the table's rebuild are the data machine's (listed under "For Samuel's ruling" in session 297's report). Until then the table holds ERCOT's three named events and CAISO's notice days, and the page reads those.

## Why these two tests

- The price test is the market's own word on a stress day, with a threshold that moves with the grid (the trailing year, not a fixed dollar figure), so a grid whose prices are low keeps its own stress days and a cap change does not break the rule. The 98th percentile is about seven days a year.
- The notice test catches the days the operator called an emergency that prices did not show (a day with a price cap, or a shortage met by load shed), as CAISO's rule already does.
- A trailing year, not a calendar year, so January's days are tested against the twelve months before them, not against a year with eleven months to come.

## Where it is read

- `warehouse/derived/battery_stack.py` (to apply it): the daily revenue by stream for the event's days into `battery_stack_stress_daily`, `event` the event's id.
- `site/lib/batterystack.ts` (`stress`, `eventMonths`, `windowMonths`): the events the rows hold, by id, for the page's "leave out" boxes and the income table's window; `EVENTS` and `EVENT_SHORT` name the three ERCOT events, any other event is labelled by its days.
- `site/app/cost-of-power/battery/Scenarios.tsx` (`StressRepeats`, session 297): the event whose window paid the most, repeated N times over the life.
