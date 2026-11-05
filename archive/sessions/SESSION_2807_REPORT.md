# Session 2807 report: Germany's general supply plants' electricity and heat by energy source (Destatis's monthly report)

26 October 2026, from about 04:40 to 04:49 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2807.out`). Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 by the fetch), each at least 30 seconds after the last (the robots file's crawl delay); one web search.

## Read these first

- **`destatis_de_electricity_monthly` is new:** Destatis's monthly report on electricity and heat generation by the plants for general supply ("Monatsbericht über die Elektrizitäts- und Wärmeerzeugung der Stromerzeugungsanlagen für die allgemeine Versorgung"), by 32 energy sources and the total. Five measures, in MWh:
  - gross generation;
  - net generation;
  - net generation in CHP;
  - net heat generation;
  - net heat generation in CHP.

  The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft.
- **One month: July 2026,** provisional, as of the page's "Stand 7. Oktober 2026". The page shows only the latest month. Each run adds the month then published, and the table keeps the earlier ones.
  - The long series is GENESIS-Online table 43311-0002. Its API needs a registered account, which file 143 says the session does not make, so it was not asked.
  - 123 rows, 27 entities. 42 cells are "." (unknown or confidential) and have no row; "-" is read as zero.
- **The figures, July 2026, net:**

  | Source | MWh |
  |---|---|
  | total | 11,081,937 |
  | lignite | 4,863,884 |
  | natural gas | 2,269,301 |
  | hard coal | 1,705,898 |
  | run-of-river hydro | 764,531 |
  | household waste | 772,644 |
  | nuclear | 0 |

  **Wind and solar are not in this survey,** nor are industrial plants.
- **Cross-check** against `smard_germany_monthly` (SMARD, the whole grid), July 2026:
  - **lignite 4,863,884 MWh here against 4,882,377** (0.4 per cent under: nearly all lignite plants are general supply);
  - hard coal 1,705,898 against 1,839,252 (7 per cent under);
  - natural gas 2,269,301 against 2,622,809 (13.5 per cent under), as industrial plants are outside this survey.
- **Reading the page:**
  - Each column's parts fall short of its total by what the "." cells hide, never above (net: 11,052,072 of 11,081,937). Gross is at least net, and net at least its CHP part, in every row.
  - **One cell is grouped oddly:** household waste's net heat, "10 420 92". It is read as its digits, 1,042,092 MWh, and counted in the header. The label "okereigas" (Kokereigas, coke oven gas) is kept as printed.
- **Terms:**
  - **Destatis's verdict is new** (read 1606): its imprint's "Copyright allgemein" says "Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellennachweis gestattet" (reproduction and distribution, in part too, permitted with the source cited). GENESIS-Online's contents are under the Datenlizenz Deutschland, Namensnennung 2.0.
  - The license record shows the table as agreed, public: 617 tables, 258 publishers with a verdict, 0 problems.
  - www.destatis.de's robots file (read 1604) disallows `/SiteGlobals/` and a search servlet, names no Claude agent, and sets `Crawl-delay: 30`, kept with real sleeps.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | www.destatis.de's robots file | 200, Crawl-delay 30 |
| 2 | the monthly report's table page (probe) | 200 |
| 3 | the imprint | 200, the verdict's sentence |
| 4 | the table page again, into the connector's raw folder | 200 |

Reads recorded: 1604 to 1606.

## Decisions made without you

- **A one-month table taken,** rather than none, since GENESIS's history needs an account. It grows by a month each run.
- **An oddly grouped cell read as its digits,** counted, rather than stopping the run.
- **Heat kept beside electricity,** as the report gives both in MWh.

## For Samuel's ruling

- **A GENESIS-Online account** would give the report's long series (43311-0002) and Destatis's other energy tables. The session made none.

## Files

- New:
  - `warehouse/connectors/destatis_electricity_monthly.py`
  - `tests/test_session2807.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1604 to 1606, Destatis's verdict) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2807/`, `runs/c143/s2807_verdict.py`, `runs/license_reads/s2807/`;
  - `warehouse/raw/destatis_electricity/`.
