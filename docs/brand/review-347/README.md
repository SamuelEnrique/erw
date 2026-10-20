# Session 347: the economic impact tool, /impact

Shots of the local production build (`npm run build && npm start`, port 3347) in the internal view, 20 October 2026,
by `site/scripts/shot.mjs`, at 1280 and 390 px wide. Every number in them was checked by `check-values.mjs` (340 of
340 on the four `/impact` addresses).

| File | Address | What it shows |
|---|---|---|
| `impact_1280.png`, `impact_390.png` | `/impact` | the defaults: land-based wind in Texas, JEDI's 300 MW project, its cost and local shares |
| `impact-pv-la-life30_1280.png`, `_390.png` | `/impact?tech=utility_pv&state=la&mw=200&life=30` | a size and a life given: the life column, the swing table, Louisiana's tax rules (no rule held) |
| `impact-gas-dc_1280.png`, `_390.png` | `/impact?tech=natural_gas&state=dc` | a place JEDI gives no figure for (its own #DIV/0!) |

Impeccable was not run: it is not installed on this machine (docs/tooling.md: a third machine has none until session
201's installs are repeated). Its `detect` on the three page files is under "To finish" for the code machine.
