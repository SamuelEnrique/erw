# Zimbabwe's electricity generation, a month (ZIMSTAT's Index of Electricity Generation, Appendix A)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2491).

Tables: `zimstat_zimbabwe_generation_monthly`

## Publisher and address

The Zimbabwe National Statistics Agency (ZIMSTAT), its "Index of Electricity Generation, 1st Quarter 2026" (10 pages), Appendix A "Volume of Electricity Generation in GWh, 2019 to 1st Quarter 2026": `https://www.zimstat.co.zw/wp-content/uploads/production/Energy/2026/Q1/IEG_Q1_2026.pdf`. One GET, no key. Source id `zimstat:index_of_electricity_generation`. Connector: `warehouse/connectors/zimstat_zimbabwe_generation.py` (session 2491). zimstat.co.zw's robots file disallows nothing (read 820). ZIMSTAT compiles the index from the Zimbabwe Electricity Supply Authority's (ZESA) administrative data: Hwange, Kariba and the independent power producers together. ZERA's site has no statistics page (read 823), and ZPC's robots file closes `/wp-admin/` only (read 821).

## Vintage and revision

January 2019 to March 2026, written by run `20261024T162831Z` (the write under the lock, offline), which read the publication saved at 2026-10-24T14:57:35Z. `vintage` is its last-modified time, 2026-08-14T05:40:28Z. Each quarter's publication has its own address; a later one repeats the earlier months and may revise them.

## Shape and variables

Series, 85 rows, one entity: `zimstat:zw:total`, `variable` `generation`, `unit` MWh (ZIMSTAT's GWh times 1,000), `ts_utc` the month's first day 00:00 UTC, `freq` P1M, `geo` ZW, `node` and `x_label` the month as ZIMSTAT labels it with its year.

| TWh | 2019 | 2020 | 2022 | 2024 | 2025 |
|---|---|---|---|---|---|
| Generation (twelve months) | 7.54 | 6.29 | 8.84 | 9.76 | 11.23 |

## Reading the source

- The run stops at once, asking nothing, while `zimstat_electricity_index`, www.zimstat.co.zw or zimstat.co.zw is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved publication.
- **Finding the appendix:** the text after "Appendix A: Volume of Electricity Generation" that holds a line of the eight years 2019 to 2026, up to "Appendix B:". The table of contents names the appendix too, without the header.
- **The rows:** twelve month rows, each with seven or eight figures in the years' order (the 2026 column ends in March), and four quarter rows.
- **Figures:** the form `1,036.1` (a decimal point, commas between thousands). Two figures are out of form and have no row, counted in the header: January and February 2026, printed "971,5" and "916,3" with a comma for the decimal point.
- **The quarter rows are not written:** each is compared with its three months' sum. 26 of 28 agree within 0.15 GWh; 2022's first quarter (2,267.1 against 2,266.8) and 2023's third (2,550.9 against 2,549.5) do not.
- The run stops, and no file is written, for: no appendix with its header, a month row of too few or too many figures, a key given twice.

Nothing is filled. The index itself, imports, exports and distribution (drawn as charts in the publication) are not taken.

## License

Internal. ZIMSTAT's copyright page (read 825): "Unless otherwise stated, the material or information published within the Zimbabwe National Statistics Agency Website is ZIMSTAT copyright". Verdict (session 2495): needs written permission. Held from the Redivis storage and the live set.

## Cross-checks (session 2491)

- Twelve months' generation over `owid_ember_electricity_annual`'s demand for Zimbabwe: 0.71 to 0.82 (2019 to 2024). The difference is imports (371.4 GWh in the first quarter of 2026 alone, by the publication's text).
- Within the publication, the text's figures for the first quarter of 2026 (Hwange 1,647.4 GWh, 56.3 percent; Kariba 926.9 GWh, 31.7 percent) imply about 2,925 GWh; January to March's printed months give 971.5 + 916.3 + 1,036.1 = 2,923.9 GWh.

## What it does not hold

- Generation by station a month (only the quarter's shares in the text); imports, exports and distribution by sector; prices (ZWG).
