# Landing requests: lab-desktop window 4 (chain 239, the forecast tool, Local impact)

Energy Research Warehouse (ERW). Written by chain 239 (`queue/done/239-day-13-november-desktop-window4-forecast.md`), session 4217, on 13 November 2026. Window B (the landing desk) lands each row through `scripts/land_check.py` with the task and port given, runs the commands it prints each on its own (the snapshot before, the push to `task/`, the snapshot after, the comparison), and marks the row landed with the commit. This window never runs `land_check.py`, never builds outside the build lock, and writes no warehouse data.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
