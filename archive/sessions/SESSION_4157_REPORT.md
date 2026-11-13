# Session 4157 report: the remaining verdicts confirmed, batch 2

Energy Research Warehouse (ERW). Chain 231, session 8 of 16, lab-desktop third window, 13 November 2026, ending 12:18 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4151-licenses`.

## Batch 2 (reads 1855 to 1901)

- **24 robots files and 23 pages.**
- **Not asked:** Hydrogen Insight (its robots file refuses ClaudeBot and anthropic-ai by name), ANEEL (its host timed out), Berkeley Lab's hybrid plants workbook (a data file).
- **20 confirmed on the page:** IEA, Korea Power Exchange, Panama's Secretaria Nacional de Energia, Statistics Austria, ASUB (Aland), SFOE (opendata.swiss), T&D World, MSHA, BLM, World Bank, AEP Texas, ARSEL, Tajikistan's statistics agency, the Alaska Energy Data Gateway, ABS Suriname, Anguilla, ARSE Burkina Faso, BC Hydro, SMARD, Kazakhstan's statistics bureau.
- **Three found changed, none in substance:**
  - **IESO:** its notice's years now read 2004-2026 (2004-2022 before), the licence the same. Cut again from read 1880; verdict unchanged (may be public).
  - **Statistik Liechtenstein:** the verdict quotes the notice inside a workbook, read again by this batch before the rule against data files was added. The bytes equal read 1258's (the same sha256), so the notice is unchanged.
  - **Tracking the Sun on OEDI:** the footer is in the page's text, and the record's `"license"` line is in its embedded data, which text extraction leaves out. Both are on read 1899.
- **Count:** 81 publishers confirmed on current pages, none with a sentence gone.

## Decisions made without you

- **A data file is no terms page:** the batch driver now skips verdicts whose page is a data file (`.xlsx`, `.csv`, `.zip`). Liechtenstein's workbook (113,716 bytes) was the one read this session.

## For Samuel's ruling

- None new.
