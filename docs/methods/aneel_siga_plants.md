# Brazil's central generation plants, operating, under construction and not yet begun, as of 1 October 2026 (ANEEL, SIGA)

Energy Research Warehouse (ERW), method note written in session 2326 (chain 108) for a table first written on 24 October 2026 (session 2324 of chain 108, its report `archive/sessions/SESSION_2324_REPORT.md`).

Tables: `aneel_siga_plants`

## Publisher and address

Agencia Nacional de Energia Eletrica (ANEEL), SIGA (Sistema de Informacoes de Geracao da ANEEL), the dataset on ANEEL's open data portal (`https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel`, read 571), through its CSV resource, one request:

- `https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv`

Source id `aneel:siga`. The dataset page describes "o novo conjunto de dados extraidos do SIGA ... que contem as informacoes dos empreendimentos de geracao de energia eletrica do parque gerador nacional", names its author SCE/ANEEL and maintainer CEGDI/ANEEL, version 1.1, "Ultima Atualizacao outubro 23, 2026, 07:44 (BRT)", created 27 May 2026, and an update frequency "Mensal e diaria". Its data dictionary (read 572, a PDF, version 1.2 of 30 March 2023) defines the 23 fields: among them `CodCEG`, the "Codigo Unico de Empreendimentos de Geracao: GGG.FF.UF.999999-D.VV" (type of generation, source, main state, core number, check digit, version); `DatEntradaOperacao`, the date the plant's first generating unit entered operation; `MdaPotenciaOutorgadaKw`, the plant's total granted or registered power; `MdaPotenciaFiscalizadaKw`, the power in operation (for a plant no longer operating, the last power considered in operation); `MdaGarantiaFisicaKw`, the physical guarantee approved by the Ministry of Mines and Energy; and the coordinates, an "approximate latitude [longitude] in decimal degrees of the plant's centroid".

The file is a semicolon-separated UTF-8 CSV with a byte order mark and decimal commas, 8,418,652 bytes, 25,045 data lines, every line's `DatGeracaoConjuntoDados` 2026-10-01. Session 2324's probe (`runs/c108/s2324/probe.csv`) made 7 requests, three for Ecuador (not taken: two TLS failures without an answer, reads 567 and 568, and HTTP 403, read 569) and four to ANEEL's portal, at least 10 seconds apart: the robots file (read 570), the dataset page, the CSV (HTTP 200 at 2026-10-24T06:57:16Z, Last-Modified "Thu, 01 Oct 2026 05:01:27 GMT") and the dictionary. The five answered are saved in `runs/license_reads/s2324/`; the CSV was seeded into `warehouse/raw/aneel_siga/20261024T064921Z_probe/`, and the trial and the write read it offline.

Connector: `warehouse/connectors/aneel_siga.py` (session 2324): `[--offline] [--out-dir DIR]`, one request. A header not SIGA's, a row of another number of fields, a phase, generation type or state not in its map, a number not in ANEEL's form, a plant given twice with other fields differing or a file of two generation dates stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T070801Z` ("File holds 25042 rows, one snapshot; the previous file held 0 rows"). `retrieved_at` is 2026-10-24T06:57:16Z in every row, the CSV's download time; `vintage` is 2026-10-01T05:01:27Z, its Last-Modified; `x_dataset_date` is ANEEL's generation date, 2026-10-01.

The table is a snapshot: a run replaces the whole file, so a plant ANEEL changes is changed and a plant it removes is gone at the next run. The register carries no provisional flag. `CodCEG`'s last two digits are the plant's version ("se maior que 1 sofreu alteracao"), so a plant whose code changes version at ANEEL appears under a new `entity_id`.

## Shape and variables

Entities, 25,042 rows, one a plant: `entity_id` `aneel_siga:<CodCEG>` (unique), `entity_type` plant, `name` ANEEL's, `geo` BR-<main state> (27 states), `lat` and `lon`, `capacity_mw` the granted or registered capacity (kW / 1,000), `status` from ANEEL's phase, `status_date` ANEEL's `DatEntradaOperacao`, `operator` blank, and 16 `x_` columns, ANEEL's other fields in Portuguese: `x_ceg`, `x_generation_type`, `x_phase`, `x_fuel_origin`, `x_fuel_source`, `x_fuel_name`, `x_grant_type`, `x_capacity_operating_mw`, `x_physical_guarantee_mw`, `x_qualified_generation`, `x_grant_start`, `x_grant_end`, `x_ownership`, `x_sub_basin`, `x_municipalities`, `x_dataset_date`.

| Type (`x_generation_type`) | Operating | MW in operation | Under construction | MW granted | Not yet begun (`planned`) | MW granted |
|---|---|---|---|---|---|---|
| UHE (hydro plant) | 215 | 103,235.1 | 1 | 48.4 | 4 | 211.4 |
| PCH (small hydro) | 433 | 6,064.0 | 23 | 338.7 | 79 | 984.1 |
| CGH (mini hydro) | 711 | 927.7 | 0 | | 7 | 18.4 |
| EOL (wind) | 1,138 | 34,936.7 | 61 | 1,988.1 | 350 | 14,333.6 |
| UFV (solar photovoltaic) | 17,302 | 23,615.3 | 32 | 1,538.0 | 1,628 | 70,848.2 |
| UTE (thermal) | 2,997 | 49,890.2 | 27 | 3,767.6 | 31 | 871.6 |
| UTN (nuclear) | 2 | 1,990.0 | 1 | 1,350.0 | 0 | |
| All | 22,798 | 220,658.9 | 145 | 9,030.8 | 2,099 | 87,267.2 |

From the table (`runs/c108/s2326/notes/br.out`). The operating plants' granted capacity is 221,382.6 MW, their physical guarantee 99,522.6 MW. CGU (wave), in the connector's map, has no plant.

- **By source.** The operating plants' capacity in operation by `x_fuel_source`: hydraulic potential 110,226.8 MW, wind 34,936.7, solar radiation 23,615.3, natural gas 20,180.0, agro-industrial residues 12,685.1, petroleum 7,579.6, forest 5,100.0, mineral coal 3,913.7, uranium 1,990.0, urban solid waste 235.7, other fossil 166.0, liquid biofuels 21.0, animal residues 9.1.
- **The largest.** Belo Monte (11,233.1 MW in operation, BR-PA), Tucurui (8,535.0, BR-PA), Itaipu's Brazilian part (7,000.0, BR-PR), Jirau (3,750.0, BR-RO) and Santo Antonio (3,568.0, BR-RO). By state the largest are BR-SP (25,475 MW), BR-MG (25,257), BR-PA (23,467), BR-BA (22,031) and BR-PR (17,712).
- **Grants.** `x_grant_type` is Registro for 19,682 plants, Autorizacao for 5,101, Concessao for 256 and "Autorizacao;Concessao" for the three plants ANEEL lists twice (Rio Timbo, PCH, BR-SC; Agro Trafo, PCH, BR-TO; Monte Alto, UHE, BR-MG). `x_grant_start` and `x_grant_end` are given for 5,359 and 5,349 plants; `x_sub_basin` is blank for 23,589; `x_qualified_generation` is blank for 15,957, Nao for 9,015 and Sim for 70.
- **Coordinates.** 465 plants have no `lat` or `lon` (377 operating, 84 planned, 4 under construction; 373 UFV, 42 EOL, 30 UTE, 20 CGH): ANEEL writes `,00000000` for both, a point in the Gulf of Guinea. The rest lie between latitudes -33.72 and 4.715 and longitudes -72.81 and -32.42.
- **The placeholder date.** `status_date` is 1900-01-03 for 2,398 plants: all 2,099 planned, 144 of the 145 under construction and 155 operating ones (498.8 MW in operation; 101 UTE, 43 CGH, 5 EOL, 5 UFV, 1 UHE). Leaving those out, the operating plants' first-operation dates run from 1900-12-25 (Supermercado Bahamas, UTE, BR-MG) and 1901-12-04 to 2026-09-02; 354 plants entered operation from 1 January 2025, with 12,276.8 MW.
- **Odd capacities.** 10 operating plants have 0 MW in operation, each with a granted capacity under 0.001 MW; 7 operating plants have more in operation than granted (the largest gap Termobahia, 185.891 against 173.0 MW). One plant under construction, Bom Jardim V (UFV, BR-CE), has 44.681 MW in operation and a first-operation date of 2026-03-21.

## Placing values in time, and what is filled

The table is the register as ANEEL generated it on 1 October 2026; `status_date` is the only date of a plant's history it carries, beside the grant's start and end. Plants ANEEL lists once are one row each; the three it lists twice, every field the same but the grant type, are one row each with the grant types joined. A coordinate pair of 0 and 0 is left empty. No other field is changed, and nothing is filled; the 1900-01-03 dates are kept as ANEEL prints them (point 1).

## License

Header: "License: public, the Open Data Commons Open Database License (ODbL) named on the dataset's page: attribution, and a database adapted from it offered under the ODbL. Cite: ANEEL, SIGA." The dataset page: "Licenca Open Data Commons Open Database License (ODbL)" (read 571). `warehouse/metadata/license_verdicts.csv`: Agencia Nacional de Energia Eletrica (ANEEL), read 571, verdict "may be public", if the ERW sells anything "may be public", its note recording the share-alike. The portal's robots file disallows `/dataset/rate/`, `/revision/`, `/dataset/*/history` and `/api/` to every agent, asks `Crawl-Delay: 10` and names no AI agent (read 570). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public. The report leaves to Samuel whether the ERW accepts the share-alike or keeps the table internal.

## Checks (session 2326)

The figures in this note were computed from the rows of `warehouse/output/aneel_siga_plants.csv`, read past its 10 header lines (counted), and from the saved CSV and dictionary, read only (scripts `runs/c108/s2326/notes/br.py`, `br2.py`, `br3.py` and `br4.py`, outputs `br.out` to `br4.out` beside them; the dictionary's text `aneel_dict.txt`).

- 25,042 rows, one a plant, no `entity_id` twice; 22,798 operating with 220,659 MW in operation and 465 without coordinates, as header line 3 states; no negative capacity; no blank `capacity_mw`, `x_capacity_operating_mw` or `x_physical_guarantee_mw`; every `status` matches its `x_phase` (operating with Operacao, under_construction with Construcao, planned with "Construcao nao iniciada").
- **Against the file:** a parse of the saved CSV gives 25,045 lines, 25,042 distinct codes, one generation date, 465 lines with both coordinates zero and none with one, 2,398 lines with `DatEntradaOperacao` 1900-01-03 and none blank; its operating plants' capacity in operation is 220,685.8 MW with the three doubled plants counted twice, 26.9 MW (the three plants' capacity in operation, counted once) above the table's.
- **The trial against the table:** `runs/c108/s2324/trial/aneel_siga_plants.csv` has the same 25,042 plants with no cell differing.
- Session 2324's cross-check (`runs/c108/s2324/cross.py`, `cross.out`): the counts and capacities by status and source as above; IRENA's Brazil at the end of 2025 (`irena_capacity_annual`): solar photovoltaic 64,690 MW, onshore wind 34,866, renewable hydropower 110,269, against ANEEL's operating UFV 23,615, EOL 34,937 and UHE, PCH and CGH 110,227 MW. `cross.out` was produced on an earlier trial, before the 0 and 0 coordinates were emptied (point 2).
- Session 2326's own: no plant outside latitudes -34 to 6 and longitudes -74 to -28 in the written table; wind 0.20 percent above IRENA's, hydro 0.04 percent below.

## The session report against the table

Every figure of `SESSION_2324_REPORT.md` checked against the table, the saved file and `cross.out` holds (25,042 plants, 22,798 operating with 220,659 MW in operation, 145 under construction, 2,099 not yet begun, 465 plants at 0 and 0 emptied, three plants listed twice, wind 34,937 against 34,866 MW, hydro 110,227 against 110,269 MW, solar 23,615 against 64,690 MW, granted capacity 221,383 against 220,659 MW, the ODbL from read 571, a crawl delay of 10 seconds kept, 7 requests of 15), except:

- "every one has a first-operation date": 155 of those dates are 1900-01-03 (point 1).
- "every one is inside Brazil's bounding box once the 465 blanks are left empty": true of the table, but `cross.out`, named as its source, shows the 465 outside (point 2).
- "disallows only /api/, /revision/ and the datasets' history": it also disallows `/dataset/rate/` (point 3).

## What it does not hold

- Distributed micro and mini generation (MMGD), which ANEEL publishes as another dataset, so solar is far below IRENA's; generating units, monthly generation, plants revoked or retired before October 2026, the owners' names and shares beyond `x_ownership`'s text, and earlier versions of the register.

## Points for the session to act on

1. **1900-01-03 is ANEEL's blank, kept as a date.** `status_date` is 1900-01-03 for 2,398 plants: every planned plant (2,099), 144 of the 145 under construction and 155 operating plants. The saved CSV has the same 2,398 lines and no blank `DatEntradaOperacao`, so ANEEL writes this date where it has none, as it writes 0 and 0 where it has no coordinates. The connector empties the coordinates but keeps the date; header line 2 calls `status_date` "the first unit's entry into operation", the docstring adds "where ANEEL gives it", and header line 3 says "Nothing is filled". The report's "every one has a first-operation date" counts the 155. The date should be emptied as the coordinates were, or the header should name it.
2. **`cross.out` is not the output of `cross.py` on the written table.** `cross.out` shows longitudes up to 0.0 and "outside Brazil's box (lat -34..6, lon -74..-28): 465", and it holds lines `cross.py` as saved does not print ("outside the box: 465 lat==0: 465 lon==0: 465 both 0: 465", a count by status and type, a list of plants at 0 and 0, "zero coordinates in the whole table: 465"). It was written at 07:00:27Z on an earlier trial, before the coordinates were emptied; the saved trial (07:07:52Z) and the table have none outside the box. The script should be run again on the table and its output saved.
3. **The robots file disallows four paths, not three.** The report says it "disallows only /api/, /revision/ and the datasets' history", the docstring "/api/, /revision/ and the datasets' history", and read 570's outcome the same; the saved file (`runs/license_reads/s2324/04_...`) also has `Disallow: /dataset/rate/`. The connector asks none of them.

Compared besides, with no contradiction found: the header's and docstring's counts, the generation date, the fields and their meanings against the dictionary, the phase map, kW / 1,000, the 465 coordinates, the three doubled plants and the license against the rows, the file and the saved pages.

Acted on in session 2326: 1900-01-03 is read as ANEEL's blank, and `status_date` is empty for those 2,398 plants; the docstring and header line 3 say so and count them, and `tests/test_session2324.py` tests it. The plant dated 1900-12-25 is kept as published. The docstring, session 2324's report and read 570's outcome now name the robots file's four disallowed paths, `/dataset/rate/` among them. `runs/c108/s2324/cross.py` was run again on the written table (no plant outside Brazil's box; 155 operating plants without a date). The table was written again offline (2,398 rows changed).
