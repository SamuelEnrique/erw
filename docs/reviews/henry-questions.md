# Ten questions for Henry (battery game v2)

Energy Research Warehouse (ERW), session 50. For a former Tesla battery engineer reviewing `/play/battery`.

Each question is tied to one setting or rule of the game (`site/lib/battery.ts`, `docs/methods/battery_game.md`). His answer becomes the design decision written next to it. The game's battery, brand and fleet are fictional; the prices are ERCOT's real ones.

1. **Usable energy and power (defaults 13.5 kWh and 5 kW; ranges 5 to 30 kWh and 1 to 11.5 kW).**
   - Are these the right defaults and bounds for one home battery today?
   - Should a player be able to set power above what the usable energy supports for a full hour, or should the game cap the ratio?
   - *Decides:* `SETTINGS.kwh` and `SETTINGS.kw`, and whether to add a power-to-energy check.
2. **Round-trip efficiency (default 90 percent, split as the square root each way).**
   - Is an even split between charge and discharge losses right, or is one side lossier at the meter?
   - Should efficiency fall at high power or at the ends of the state of charge?
   - *Decides:* `step`'s efficiency model.
3. **The degradation cost (default $0.11 per kWh discharged: Lazard 2025's low-end capital cost, $721/kWh x 25 kWh, spread over 158 MWh of lifetime output).**
   - Is "capital over lifetime throughput" a fair proxy for the cost of one more cycle?
   - What would you use instead: a warranty's throughput, a depth-of-discharge curve, or a calendar-aging floor?
   - *Decides:* `SETTINGS.deg`'s default and its source.
4. **Where the degradation cost is charged (per kWh taken out of the battery, never on charging).**
   - Is per-kWh-discharged the right unit?
   - Should deep cycles or high power cost more per kWh than shallow, slow ones?
   - *Decides:* whether `step` charges wear by depth, by power, or flat.
5. **The backup reserve (default 20 percent, enforced on Hard, never crossed even in the fleet call).**
   - In practice, does a VPP dispatch override the owner's backup reserve, or is the reserve sacred?
   - Is 20 percent a typical setting?
   - *Decides:* whether the call may dip into the reserve, and `SETTINGS.reserve`'s default.
6. **Starting half full, every day.**
   - Would a real battery more often start the day full (charged overnight or by solar), empty, or at its reserve?
   - Should the level's start depend on the day?
   - *Decides:* `rulesOf().start`.
7. **The fleet call: one hour, the day's dearest, with 15 minutes' notice (modeled on ERCOT's ADER pilot, where dispatch comes from SCED every five minutes).**
   - How much notice does a VPP fleet get in practice, and how long does a typical event last?
   - Is "the day's dearest hour" a fair proxy for when a fleet is called?
   - *Decides:* the notice (now one interval) and the length (now four intervals).
8. **What the battery is paid in the call (the hub's real-time price for energy, plus a bonus of the hour's mean price per kWh delivered).**
   - How are homeowners in a real Texas VPP actually paid: per kWh delivered, per event, or a flat monthly credit?
   - What share of the market value reaches the home?
   - *Decides:* the bonus rule, which is now a labelled stand-in.
9. **The continuous-power limit inside each 15-minute interval (the battery moves exactly kW x 0.25 kWh, or less at full or empty).**
   - Does a real inverter hold full power to the last percent of charge, or taper near full and near empty?
   - *Decides:* whether `step` adds a taper near the ends.
10. **What the game leaves out (the home's own load, rooftop solar, retail time-of-use rates).**
    - Which of these changes a homeowner's best plan the most, and should the next version add it?
    - *Decides:* v3's first new rule.

**Answers:** write each answer under its question with the date. The design change follows in the next session, with the method updated to cite "Henry, review of 2026-10" as the source where his answer sets a default.
