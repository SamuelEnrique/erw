# Grid alerts, watches and emergency notices in one table

Chain 601, part E (session 9000, 20 November 2026). Builder: `warehouse/derived/grid_alerts.py`. Table: `grid_all_alerts` (the chain named it `grid_alerts`; the data standard asks three parts, and `all` is the standard's word for a table with no one market).

## What it holds

Every row of three held events tables, in one shape, each with its own id, date, type and source document unchanged:

| Input | Rows (20 November 2026) | Span | What |
|---|---|---|---|
| `caiso_grid_emergencies` | 1,906 | 1998-05-30 to 2026-10-08 | CAISO's grid emergencies history: alerts, warnings, Flex Alerts and Power Watches, Restricted Maintenance Operations and No Touch days, stages 1 to 3, transmission emergencies |
| `ercot_grid_notices` | 178 | 2011-02-02 to 2026-10-15 | ERCOT's notices as its news releases print them: weather watches, conservation appeals, EEA levels, rotating outages |
| `doe_oe417_events` | 3,313 | 2016-01-04 to 2025-12-30 | the federal Electric Emergency Incident and Disturbance Reports, every authority, with the area affected and the NERC region as filed |

## Decisions

1. **The source's words.** `x_kind` is each source's own label (CAISO's notice label, ERCOT's headline label, OE-417's event type as published). No kind is renamed or merged across sources.
2. **Where.** `x_grid` is `caiso` or `ercot` for those two, and the NERC region of an OE-417 report (OE-417 names the area affected, not a market). `x_area` carries the source's own area words.
3. **Start and end.** `x_start` and `x_end` are the source's own where it prints them (CAISO's time frame, ERCOT's issue time, OE-417's begin and restoration). An empty end is not a guess.
4. **Nothing changes upstream.** `/grid/caiso/alerts` keeps reading `caiso_grid_emergencies`. The fold is rebuilt from the three tables each day.
5. **Not held:** SPP's conservative operations and EEA notices (published as news on www.spp.org, not read tonight); PJM, NYISO and ISO-NE (held by license); MISO (paused).
