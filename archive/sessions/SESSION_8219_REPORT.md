# Session 8219 report (chain 502, lab-desktop second window)

19 November 2026, 12:52 to 12:55 UTC (read from the clock). Opus 5.5. Model spend: USD 0.

## Part D, second round: forecasts, 12 drafts (revisions)

- `ferc714_planning_area_forecasts`: for each filing, how much a planning area changed its forecast of the year five ahead against its filing of the year before, summer peak and net energy (`ferc714.py --revisions`); areas of at least 3,000 MW with a filing from 2024 on; a revision of more than double or less than half is left out (a figure in the wrong unit).
- The drafts agree with the method note's own table of revisions (Southwest Power Pool +10.9 percent, Sierra Pacific +73.3, Nevada Power +14.4, Duke Energy Carolinas +7.9 for the summer peak).
- The three strongest:
  - Nevada Power's 2025 filing raised its forecast of net energy five years ahead by 31.6 percent against its 2024 filing, where its 2007 filing had lowered it by 5.5 percent.
  - Arizona Public Service's 2025 filing raised its net energy five years ahead by 13.5 percent, against minus 4.1 in 2007.
  - Duke Energy Carolinas' 2025 filing raised its net energy five years ahead by 9.8 percent, against minus 2.3 in 2007.
- Every forecasts draft reproduces (30 of 30); 12 of 12 new do-files hold.

## Code

- `ferc714.py` on `wip/8202-findings` (`04106bd55`).

## Needs the key

- Nothing.
