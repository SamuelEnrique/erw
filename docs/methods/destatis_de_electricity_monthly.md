# Germany's general supply plants, electricity and heat by energy source, a month (Destatis's monthly report)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2807).

Tables: `destatis_de_electricity_monthly`

## Publisher and address

Statistisches Bundesamt (Destatis), the monthly report on electricity and heat generation by the plants for general supply ("Monatsbericht über die Elektrizitäts- und Wärmeerzeugung der Stromerzeugungsanlagen für die allgemeine Versorgung"). Its latest month is published as one table on one page:

`https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Energie/Erzeugung/Tabellen/elekrizitaet-waermeerzeugung-energietraeger-monatsbericht.html`

Source id `destatis:monatsbericht_elektrizitaet_waerme`. Connector: `warehouse/connectors/destatis_electricity_monthly.py` (session 2807), whose raw store is `warehouse/raw/destatis_electricity/`.
- www.destatis.de's robots file (read 1604) disallows `/SiteGlobals/` and a search servlet, names no Claude agent, and sets `Crawl-delay: 30`. The connector's one request needs no delay, but every session's second request to the host waits 30 seconds.
- The long series is GENESIS-Online table 43311-0002, whose API needs a registered account, which the ERW does not make.

## Vintage and revision

Written by run `20261026T044655Z`, which read the page retrieved at 2026-10-26T04:45:04Z: July 2026, provisional ("Vorläufige Angaben"), "Stand 7. Oktober 2026". Each run adds the month the page then shows, and the table keeps the months before it. A provisional month is replaced if a later run reads the same month again.

## Shape and variables

Series, 123 rows, 27 entities, one month (July 2026) so far:
- `entity` `destatis:de` for the total ("Insgesamt"), or `destatis:de:<slug>` for an energy source, its German label transliterated. "Erdgas, Erdölgas" gives `erdgas_erdoelgas`, and the page prints "okereigas" for Kokereigas, kept as printed.
- `variable` `gross_generation`, `net_generation`, `net_generation_chp` (net generation in combined heat and power), `net_heat_generation` and `net_heat_generation_chp`; `unit` MWh, as the page gives them.
- `ts_utc` the month's first day; `freq` P1M; `geo` DE; `node` "Destatis general supply, <label>, <measure>"; `x_label` and `x_cell` the page's label and cell as printed.

**Plants for general supply only:** wind and solar are not in this survey, and industrial plants are not either.

**Figures, July 2026:**
- total gross generation 11,973,315 MWh, net 11,081,937;
- lignite ("Braunkohlen insgesamt") net 4,863,884;
- natural gas net 2,269,301;
- hard coal net 1,705,898;
- nuclear 0.

## Reading the source

- A "." (unknown or confidential) has no row (42 cells). A "-" (nothing) is zero, and "- -" too (Speicherwasser's heat). Nothing is filled.
- **A cell grouped other than in threes is read as its digits and counted:** household waste's net heat, "10 420 92", is 1,042,092 MWh. A cell neither a number, "." nor "-" stops the run.
- **Compared:**
  - Each column's parts against its total. The parts fall short by what the "." cells hide, never above: net, 11,052,072 of 11,081,937.
  - Gross against net, and net against its CHP part, in every row. All hold.
- The run stops, asking nothing, while Destatis is paused. It also stops on:
  - no table on the page;
  - a caption without a German month and year;
  - a header without the report's five measures;
  - no total row.

## License

Destatis's imprint, "Copyright allgemein" (read 1606, session 2807's verdict): "Vervielfältigung und Verbreitung, auch auszugsweise, mit Quellennachweis gestattet". That is reproduction and distribution, in part too, permitted with the source cited. Source: Statistisches Bundesamt (Destatis). In the release package; held from the live set.

## Cross-check

Against `smard_germany_monthly` (SMARD, the Bundesnetzagentur's whole-grid generation), July 2026, MWh:

| Source | Destatis general supply (net) | SMARD | Destatis below SMARD |
|---|---|---|---|
| Lignite | 4,863,884 | 4,882,377 | 0.38 per cent |
| Hard coal | 1,705,898 | 1,839,252 | 7.25 per cent |
| Natural gas | 2,269,301 | 2,622,809 | 13.48 per cent |

Lignite is nearly all general supply. Hard coal and gas are below SMARD by the industrial plants this survey leaves out.
