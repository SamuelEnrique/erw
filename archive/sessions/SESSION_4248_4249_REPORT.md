# Sessions 4227 to 4229, 4248 and 4249 report: faults 17 and 18, the tax check, the note, the next file (chain 239, window 4)

13 November 2026, about 13:36 to 13:46 UTC. Branch `wip/4225-forecast`. Model spend USD 0.

- **4227, fault 17**: a property tax held for only some years (Oregon's 20-year agreement, Kansas's exempt decade) was left out of the taxes chart; drawn now, its unheld years empty. Fault 13 notes the shared chart's figure overlap (a ruling).
- **4228, fault 18**: the table by year was drawn only when opened, so check-values never judged it; always drawn now. Built under the lock (13:38) and read: check-values 633 of 633 on the `/impact` addresses. Landing row 3 moved to `925e9e481` on main.
- **4229, a tax check** (method note, section 9): Minnesota's 2024 wind production tax, from the Center for Rural Affairs' fact sheet (request 70): Lincoln County's USD 1.189 per MWh is the statute's USD 1.20 within 1 percent; the state's fleet implies a capacity factor near 0.31 against the new-plant default 0.42.
- **4230 to 4247**: not needed; the plan's work was done by 4229.
- **4248, the note** `docs/state/note_2026-11-13_desktop_window4.md`: what the tool does, the cross-check, the three landing rows, the sources missing or refused, twelve rulings with defaults, five data requests.
- **4249, the next file**: `queue/next/240-day-14-november-desktop-window4-forecast-continued.md` updated on main with what chain 239 left (a failed landing first, window A's tables, rulings answered, more statutes, two more studies, Stata), pushed alone; the queue step by name follows.
