# Session 2535 report: Togo's electricity, 2020 to 2024 (INSEED's national yearbook 2024, from CEET's reports), internal

24 October 2026, about 20:59 to 21:18 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2535.out`). Model spend USD 0. Pulls: 6 requests of 15 (4 by the probe, 2 by fetches).

## Read these first

- **The ERW held no Togolese source** (`sources.csv`, the connectors and the queue searched for Togo, CEET and INSEED).
- **The hosts:** inseed.tg's robots file closes `/wp-admin/` only (read 993). **www.ceet.tg's certificate fails verification** (read 994): CEET's site was not asked again, and it joins the closed hosts. arse.tg redirects to www.arse.tg, whose robots file closes `/wp-admin/` only (read 995). None names an AI agent.
- **INSEED's terms:** its home page states "Copyright 2024 INSEED - Tous droits reserves" and links no terms of reuse (read 996). The table is **internal** until a ruling; session 2537's round reads INSEED.
- **INSEED's monthly bulletin (December 2025, 67 pages; fetched once)** holds no electricity: its energy section is fuel deliveries.
- **The source:** INSEED's Annuaire Statistique National 2024 (776 pages, 18.2 MB; fetched once), chapter 25, whose tables cite CEET's annual activity reports:
  - table 25.2, "Achat et production d'energie", 2020 to 2024: CEET's purchases by supplier (through VRA-TCN-SBEE-Nangbeto, 983.53 GWh in 2024; three small cross-border and local suppliers) with their total (991.38 GWh in 2024), and the production of each producer on its grid (ContourGlobal Togo's gross 530.51 GWh, KEP's net 439.44, AMEA's 120.65, CEET's own gross 4.90 GWh in 2024);
  - table 25.7, "Ventes d'electricite", 2020 to 2023 by voltage (low and medium) and their total (1,500 GWh in 2023); 2024 is given as "-".
- **Read by the words' places, not the page's text:** a cell such as 2023's "1 351" sits beside its neighbours with only spaces between, which the text alone cannot split. The connector joins a figure's words (no more than 6 points apart), places each cell under the year heading whose right edge is nearest, and checks every total against its parts.
- **INSEED's tables disagree with each other:** table 25.1's key figures give purchases of 1,720 GWh for 2022 and 1,975 GWh for 2023, and 1,705 GWh sold in 2023; tables 25.2 and 25.7 give 916.26, 1,360.05 and 1,500 GWh, and each sums to its own parts. Table 25.1 is not taken; the connector's docstring and the table's header say so.
- **A new table, `inseed_togo_electricity_annual`** (series, 55 rows, 11 entities, `power`), in MWh. Written by run `20261024T211320Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T211612Z-local`), held from the live set and from Redivis (internal).
- **The metadata patch conflicted** with sessions 2532 and 2533's rows (the same places in the four sorted files). Resolved as the union of both sides, sorted (`runs/c124/resolve_union.py`); each of the chain's three tables has one row in `sources.csv`, `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`.

## Cross-checks

- Against `eia_world_electricity_annual`'s Togo: the producers' sum (CEET, ContourGlobal, KEP, AMEA) is 823.7 GWh in 2022 against EIA's generation of 899.9 GWh (92%), and 633.1 GWh in 2023 against 716.6 (88%). In 2024 it is 1,095.5 GWh against EIA's 709.5: KEP's net production rose from 148 to 439 GWh, which EIA's figure does not show. CEET's purchases (991.38 GWh in 2024) include the CEB's Nangbeto plant in Togo as well as imports, so they are not EIA's imports (1,500 GWh in 2024).

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | inseed.tg, www.ceet.tg and arse.tg robots files | 200, certificate error, 200 (by www.arse.tg) |
| 4 | INSEED's home page | 200 |
| 5 | the monthly bulletin, December 2025 (a fetch) | 200, 1.7 MB |
| 6 | the Annuaire Statistique National 2024 (the fetch) | 200, 18.2 MB |

Reads recorded: 993 to 996 (the probe's four). Two web searches found nothing on INSEED's or ARSE's hosts; they reached no publisher's host.

## Decisions made without you

- **Tables 25.2 and 25.7, not 25.1,** where INSEED's own tables disagree.
- **Internal** under INSEED's "Tous droits reserves", until a ruling.
- **www.ceet.tg closed** for its certificate.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/inseed_togo_electricity.py`, `tests/test_session2535.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 993 to 996) and `docs/licenses.md`.
- On the data machine only: `runs/c124/s2535/`, `runs/c124/resolve_union.py`, `warehouse/raw/inseed_tg/`, `warehouse/output/inseed_togo_electricity_annual.csv`.
