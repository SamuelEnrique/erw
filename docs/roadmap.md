# Roadmap

Energy Research Warehouse (ERW). What the machines do next, in the owner's words. `scripts/planner.py` reads this file, and no other, to decide what to plan (`docs/machines.md`, "The planner"); it never edits it. Only a person writes here. Until a person writes `planner: on` under "Status", the planner is off and nothing is planned.

## Status

What goes here, one line each: `planner: on` or `planner: off` (absent means off); `budget: N sessions a day per machine`; `earliest start: HH:MM UTC` and `latest start: HH:MM UTC`, the hours between which a session may start; `deploy cutoffs: HH:MM to HH:MM UTC` (several are separated by semicolons; `none` when there is none).

## This week

What goes here: numbered items, `N. [ ] title` while open and `N. [x] title` once closed, each followed by indented lines: `machine: code` or `data`; `where:` the page or table; `done:` what done means; `rulings:` a ruling already made, one a line; and, where wanted, `session:` one session's work (up to three), `cap: USD n` for model spend, `lands: yes` or `no`.

## Rulings

What goes here: what Samuel has decided, one dated line each. The planner pastes this section into every chain it plans.

## Holds

What goes here: what no session may touch, one line each. The planner pastes this section into every chain it plans.

## Input from Ben and Khalid

What goes here: dated lines of what Ben and Khalid asked for or said. Read by people; the planner does not use it.

## Review log

What goes here: one dated section per review of this roadmap, the newest last. Nothing here is ever deleted.
