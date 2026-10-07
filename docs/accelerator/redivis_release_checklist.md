# Checklist: a first citable Redivis release of the ERW

Energy Research Warehouse (ERW). Written on 7 October 2026 (UTC) from the repository as it stood at commit `64d7b83` (branch `wip/138-datacenter`, `git log -1`). Nothing on redivis.com was read: every statement about the state of the Redivis datasets is what the repository records, and is marked "to confirm in Redivis" where the repository cannot settle it.

Each item is marked **DONE** (with the path that shows it), **NOT DONE**, or **WAITS ON THE OWNER** (a human action). `CLAUDE.md`, non-negotiable 6: "Nothing publishes to Redivis without a human. Uploads, when they exist, write a draft version only. Releasing a Redivis version is always a human click after reviewing the diff. No scheduled job ever publishes."

## Totals

| Status | Items |
|---|---|
| DONE | 17 |
| NOT DONE | 13 |
| WAITS ON THE OWNER | 11 |
| All | 41 |

## Since this checklist was counted (sessions 138 and 139, 7 October 2026)

The items below were counted at commit `64d7b83`. The two sessions of 7 October added six tables, each uploaded to a
draft by `warehouse/redivis/upload.py` and none released (`warehouse/metadata/redivis_uploads.csv`): three to the
public draft `energy_research_warehouse` (`ercot_zone_load_hourly`, `nyiso_zone_load_hourly`,
`caiso_area_load_hourly`) and three to the private dataset `energy_research_warehouse_internal`
(`isone_zone_load_hourly`, `texas_delivery_charges`, `large_load_statements`). `coverage.csv` now holds 177 tables, 148
public and 29 internal, all with validator `pass`. Item 1's counts become 148 public tables; item 2's four missing
internal tables are as they were. For the first release this adds one thing to review in the diff: the three new
public load tables, whose terms sentences are in each connector and in `sources.csv`.

## What the repository says about the state of the release

- No version has been released, as far as the repository records. `docs/state_2026-10-04.md` line 83: "Release a Redivis version. The ERW calls itself citable, and no released version exists to cite. It is one click after reading the diff." `archive/sessions/SESSION_134_REPORT.md` line 23 (6 October 2026): the session's tables "are already in the Redivis drafts, unreleased". `docs/platform-tools.md`, tool 19: "No Redivis version released yet; no public API". Whether a release has been made on redivis.com since: to confirm in Redivis.
- The release procedure is written in `warehouse/redivis/README.md`, section "How to release a version (a human, on Redivis)" (line 46): reconcile, open the draft (`next`), review what it changes table by table, click Release with a note naming the ERW commit and the date of the daily run, after which the next upload opens a new draft.
- The cadence is in `ARCHITECTURE.md` section 1a: "Once a month, in its first week, a human reviews the draft against the last released version and releases it on Redivis. That version is the citable record of the month before." `archive/sessions/SESSION_28_REPORT.md` line 262 asked: "The first monthly release: the first week of October, once `--fix` has run and the draft is clean?" No answer to that question was found in the repository.
- The store model is in `ARCHITECTURE.md` section 1a: the draft is the working store ("Nobody [cites it]. A draft is scratch space"); the released versions are the citable archive.

## A. The tables in the two datasets

Counts computed on 7 October 2026 from `warehouse/metadata/coverage.csv` (171 tables) and `warehouse/metadata/redivis_uploads.csv` (221 lines: 167 current, 54 marked `migrated_to`).

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 1 | Every public table is in the public draft `energy_research_warehouse` | DONE | `redivis_uploads.csv`: 145 current lines name the dataset `energy_research_warehouse`; they are the 145 tables `coverage.csv` marks `public`, and their `rows` sum to 21,277,210, equal to the sum of `n_rows` of the public tables in `coverage.csv`. No table's dataset disagrees with its license (0 mismatches). The manifest records the last upload, not the present state of the draft: to confirm in Redivis |
| 2 | Every internal table is in the private dataset `energy_research_warehouse_internal` | NOT DONE | 22 of the 26 internal tables have a manifest line under `energy_research_warehouse_internal` (712,018 rows). Four internal tables in `coverage.csv` have no manifest line: `ferc_eqr_contract_terms`, `ferc_eqr_contracts_history`, `ferc_eqr_party_mw`, `ferc_eqr_quarter_changes`. This does not hold a public release; it means the internal dataset is not the whole warehouse |
| 3 | Every public table passes the validator | DONE | `coverage.csv`, column `validator_status`: `pass` for 145 of 145 public tables (171 of 171 in all). The uploader also validates each table before uploading it (`warehouse/redivis/README.md`, "Gate: the validator must pass for a table, or it is not uploaded"). The validator was not run again for this checklist |
| 4 | The draft's row counts are reconciled against the CSVs | NOT DONE | Step 1 of the release procedure is `python warehouse/redivis/upload.py --reconcile`, which writes `runs/redivis_reconcile.csv`. No such file is on this machine. Each upload proves its own table at upload time (`count(*)` equals the CSV's rows), but a whole-draft reconcile before release is not recorded. One line already differs between the manifest and coverage: `api_cost_ledger` (2,226 rows uploaded at 2026-10-06T15:17:10Z, 2,222 in coverage; internal) |
| 5 | The 54 tables consolidated in session 29 are removed from the public draft | WAITS ON THE OWNER | `redivis_uploads.csv` keeps 54 lines with `migrated_to` set, all in the public dataset. `CHANGELOG.md` (session 29): "The old tables stay until a human runs `python warehouse/redivis/upload.py --remove-migrated`". `docs/runbook.md` line 77 gives the command and its dry run. No session report after session 29 records it having been run (searched `archive/sessions/` for `remove-migrated`). Until it runs, a release would publish each of those rows twice, under an old and a new table name: to confirm in Redivis. Tied to it: `CHANGELOG.md` line 64 says the old names keep working in the `erw` package "until the first monthly release" |
| 6 | A ruling on the tables behind pages still in review | WAITS ON THE OWNER | `warehouse/supabase/live_set.yaml` holds 35 tables out of the site's catalogue under `catalogue_hold` (32 of them public) and 16 under `review_hold` (all public), because their pages are in review. All 48 public ones are in the public Redivis draft (item 1). The hold is a Supabase rule; nothing in `warehouse/redivis/` applies it. A release publishes them unless a person decides otherwise |

## B. Documentation in Redivis

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 7 | Each table has a description | DONE | `warehouse/redivis/upload.py`, `description()` (line 165): "ERW table NAME. License: ..." followed by the file's provenance header, cut at 2,000 characters with a note (Redivis's limit, `DESC_MAX`, line 77) |
| 8 | Every provenance header line is held in full | DONE | `warehouse/redivis/README.md`: the table `erw_headers` (`table`, `line_no`, `line`) holds every header line of every table; each dataset gets the headers of its own tables only |
| 9 | Each variable (column) is documented in Redivis: a label, a description, its unit | NOT DONE | The uploader sets a table description and nothing per variable (no call that writes a variable's label or description in `upload.py`). Column meanings are in `docs/datastandard.md` (shapes a, b, c); units are a column of each series row (`unit`), from the closed vocabulary the validator enforces. That Redivis variables accept labels and descriptions: to confirm in Redivis |
| 10 | The public dataset has a description, a methodology and usage notes | NOT DONE | No file in the repository holds that text, and `upload.py` writes a dataset description only when it creates the internal dataset (line 197). The public dataset "must already exist; create it on Redivis first" (`open_draft`, line 183). What is typed on its Redivis page today: to confirm in Redivis. Source text exists: `README.md`, `docs/OVERVIEW.md`, `docs/datastandard.md`, `package/llms.txt`, `docs/methods/` (53 files) |
| 11 | A codebook or coverage document ships with the data | DONE | `warehouse/redivis/config.yaml`, `metadata_tables`: `erw_coverage` (`coverage.csv`) and `erw_sources` (`sources.csv`) go to the public dataset. `docs/coverage.md` is the readable copy, generated; `docs/datastandard.md` is the column standard |
| 12 | Each derived table names its method note | NOT DONE | Of the 54 tables with `tier` = `derived`, 50 name a `docs/methods/` path in their header (read from the files in `warehouse/output` on 7 October 2026). Four do not: `ai_power_regions` (its method is `docs/reports/ai_gigawatts_methods.md`), `known_data_faults` (its rows link `docs/methods/known_data_faults.md` in `source_url`), `storage_buildout_monthly` (`docs/methods/storage_buildout.md` exists) and the internal `ferc_eqr_quarter_changes` |

## C. Licenses

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 13 | A license per source | DONE | `warehouse/metadata/sources.csv` as committed at `64d7b83`, column `license`: 250 rows, 155 `public` and 95 `internal` (74 of the internal ones are news outlets). Uploaded as `erw_sources` |
| 14 | A license per table | DONE | `coverage.csv`, column `license` (145 public, 26 internal); written into each Redivis table description (item 7). Rule: "A table is `internal` if any of its sources is" (`docs/datastandard.md`, General rules) |
| 15 | The terms of every publisher of a public table have been read and quoted | NOT DONE | Quoted in the repository: ERCOT, CAISO, EIA (`docs/methods/generation_mix_hourly.md`, "Terms of the sources session 133 added, quoted"); NYISO, SPP, ISO-NE, MISO (`docs/methods/capacity_and_ancillary.md` lines 46 to 51 and 120 to 127). Not readable when tried: the IMF's terms page answered HTTP 403 (`archive/sessions/SESSION_132_REPORT.md` line 26; `imf_commodity_prices` is public on a reading of a search result's quotation) and the NRC's notice page answered HTTP 403 (`SESSION_133_REPORT.md` line 38; `nrc_reactor_status` is public as a U.S. government work, "for a person to confirm"). No single document lists the terms of every data publisher in the registry (43 publisher names among its 176 data sources) |
| 16 | Rulings on the public tables whose license is in doubt | WAITS ON THE OWNER | Each of these is recorded as waiting for a person: (a) MISO: its terms forbid republishing (`docs/methods/miso_pause.md`: "That is the license question, recorded per table in the source registry; it is a separate matter from the pause and is also for the review"), see item 31; (b) NYISO: "public, with a caution", its legal notice "grants no license" (`capacity_and_ancillary.md` line 51); (c) SPP: citation allowed, "a commercial publication is not" (line 127; `SESSION_136_REPORT.md`, For Samuel 2: "Read SPP's commercial-publication exception"); (d) ISO-NE: its reserve prices are internal on its terms sentence while `isone_dam_zone_prices`, `isone_rtm_zone_prices` and `isone_rtm_zone_prices_hourly` are public (`SESSION_136_REPORT.md`, For Samuel 1: "Rule on ISO-NE's row"); (e) the IMF and NRC pages (item 15); (f) EIA's NYMEX futures, marked internal pending a ruling (`SESSION_127_REPORT.md` line 25); (g) the rights question on `energy_companies`, which comes from web search (`SESSION_29_REPORT.md` line 260, still listed as open there) |
| 17 | A license statement for the collection as a whole | NOT DONE | The repository root has no `LICENSE` file. `README.md`, "License rule", states the per-table rule and how to cite. Nothing states under what terms the ERW's own work is offered: the compilation, the derived tables, the method notes, the code. What license field Redivis asks for on a dataset: to confirm in Redivis |

## D. Citation, DOI, version, changelog

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 18 | A citation form | DONE | `warehouse/redivis/README.md`, "How to cite it" (line 56): the publisher and report, then "Via the Energy Research Warehouse (ERW), table ..., Redivis dataset `energy_research_warehouse`, version vN (released YYYY-MM-DD)". `erw.cite(table)` writes the publisher part from the registry (`package/src/erw/api.py` line 494) |
| 19 | `erw.cite()` names the Redivis version read | NOT DONE | `cite()` appends "data commit ..." only when `version()` gives one; the Redivis backend returns `"data_commit": None` (`package/src/erw/remote.py` line 136), so a citation written while reading Redivis names the table and no version. The README's citation form (item 18) is not what the function prints |
| 20 | A DOI | WAITS ON THE OWNER | The repository's own documents do not mention a DOI anywhere (searched every `.md`, `.py`, `.txt`, `.tsx` and `.yaml` file for the word; the only matches are two saved Wikipedia texts). Whether Redivis issues a DOI on release, and what the owner must enter for it: to confirm in Redivis |
| 21 | A version number for the first release | WAITS ON THE OWNER | None is chosen in the repository. `warehouse/redivis/README.md` writes "vN"; `RedivisBackend`'s docstring gives "v1.0" as an example of a tag. How Redivis numbers a first version: to confirm in Redivis |
| 22 | A changelog that reaches the release | NOT DONE | `CHANGELOG.md` holds three entries, the newest "2026-09-29, session 31: battery storage". It says "The ERW has 65 tables" (session 29). `coverage.csv` holds 171 today. Sessions 32 to 137 have no changelog entry; their changes are in `archive/sessions/` only |
| 23 | The data standard has a stated version | DONE | `docs/datastandard.md` line 1: "ERW Data Standard v0"; `warehouse/validate/erw_validate.py` line 27: `STANDARD = "ERW Data Standard v0"`; the standard lists 41 numbered decisions. Two sentences of its opening are behind the rest of the file: line 7 says "Only the `series` shape has a connector and a validator today", while the validator enforces events (session 6) and entities (session 8); line 22 says "PJM data are `internal`; every other source is `public`", while the registry holds 21 internal data sources. `ARCHITECTURE.md` section 2: where the standard and the validator disagree, "fix one of them the same day" |

## E. Provenance and reproducibility

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 24 | A provenance header on every table file | DONE | All 171 files in `warehouse/output` named by `coverage.csv` begin with `#` comment lines (read on 7 October 2026) |
| 25 | `source` and `source_url` on every row | DONE | All 171 tables have both columns (headers read on 7 October 2026). The validator blocks a series row with an empty `source` (`source_present`), an events row with an empty `source` or `source_url`, and an entities row with an empty `source` |
| 26 | `retrieved_at` on every row | NOT DONE | 160 of 171 tables have the column. Of the 11 without it, four are public: `caiso_grid_emergencies`, `energy_deals`, `news_index`, `policy_reads`. The standard lists `retrieved_at` as reserved, not required, so the validator passes them; their retrieval time is in the file header only |
| 27 | Each table says what kind of number it holds | DONE | `coverage.csv`, column `tier`: 105 `source`, 54 `derived`, 12 `model_extracted` (`docs/datastandard.md`, "Provenance tiers"; set by `TIER_RULES` in `warehouse/metadata/build_coverage.py` line 86) |
| 28 | The history survives outside the draft | DONE | `warehouse/archive/` and the private bucket `erw-archive` (`ARCHITECTURE.md` section 1a); `warehouse/metadata/archive_manifest.csv` holds 221 lines; `warehouse/archive/restore.py` rebuilds a table |
| 29 | A reproducibility statement: the commit the release was built from | WAITS ON THE OWNER | `warehouse/redivis/README.md`, release step 4: "give the version a note naming the ERW commit (`git rev-parse HEAD`) and the date of the daily run it holds". One fact the note must face: the draft was not built from one commit. `redivis_uploads.csv` records uploads from 2026-09-26T04:16:54Z to 2026-10-06T20:42:05Z, by the daily run and by sessions on their own branches. The manifest's `data_sha256` per table is the nearest thing to a build record |

## F. What must stay out of the public dataset

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 30 | No internal table in the public dataset | DONE | `upload.py`, `push()` (line 276) refuses a non-public license for the public dataset; `upload.py --check-license` fails when an internal table is found there, and `warehouse/run_daily.sh` line 406 runs it after every upload and stops the run on it. The manifest shows no internal table under the public dataset |
| 31 | A ruling on the paused publisher's rows | WAITS ON THE OWNER | MISO's pulls are paused since 4 October 2026 (`warehouse/metadata/paused_sources.csv`). The pause stops requests and removes nothing: "Every MISO table and page stays as it is; nothing is deleted." MISO's public-licensed data is therefore in the public draft: `miso_interconnection_queue` (3,881 rows), MISO's markets in `iso_dam_hub_prices`, `iso_rtm_hub_prices` and `iso_hub_prices_history`, and the tables derived from them. MISO's terms, quoted in `docs/methods/capacity_and_ancillary.md` line 126, say a user is "not permitted to modify, publish, transmit, ... reproduce, create derivative works of, distribute" its content. No code keeps a paused publisher's rows out of a release |

## G. The client

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 32 | The `erw` package can read a named released version | DONE | `package/src/erw/remote.py` line 81, `RedivisBackend(owner, dataset, version="next")`: "pass a released version tag (for example "v1.0") to read what the public reads" |
| 33 | A reader outside the project can read the released version without help | NOT DONE | `ERW_BACKEND=redivis` builds `RedivisBackend()` with its default, the draft `next` (`remote.py` line 251); no environment variable selects a version. The backend needs `REDIVIS_API_TOKEN` and `REDIVIS_OWNER`; the owner's Redivis name is read from `.env` and is not written in the repository (`warehouse/redivis/config.yaml`, `owner_env`). `README.md` gives the dataset's page (`https://redivis.com/datasets/05yh-65frzyhaz`) |
| 34 | The client has been tested against a released version | NOT DONE | No released version exists to test against. The remote backend tests (`package/tests/test_backends.py`, marker `remote`) are "skipped by default since session 34" (`package/README.md` line 64) and read the draft |

## H. Preconditions the repository's own documents name, and the human steps

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 35 | The draft's history cannot be lost without a failure (review item 2, "before the first release") | DONE | `docs/feedback/ben-2026-09-28.md` section 2; answered in session 28 by three history gates (`warehouse/redivis/README.md`, "History gates"), tested in `tests/test_redivis_gates.py` |
| 36 | Internal tables go to their own private dataset (review item 3, "before the first release") | DONE | `docs/feedback/ben-2026-09-28.md` section 3; `warehouse/redivis/config.yaml`, `dataset_internal`; the manifest's 22 lines under the internal dataset show it exists and has been written to |
| 37 | Ownership: a personal account or an organization (review item 4) | WAITS ON THE OWNER | `warehouse/redivis/config.yaml`: `owner_kind: user`. The review: "moving it under an organization now, while it is small, is much cheaper than later". `SESSION_29_REPORT.md` line 260 lists it as still open. A DOI and a citation would name the owner at the time of release: to confirm in Redivis |
| 38 | The public dataset's access level | WAITS ON THE OWNER | The repository's documents disagree. `SESSION_11_REPORT.md` line 159: "an unreleased draft with public access `none`"; `SESSION_28_REPORT.md` line 25: "the public dataset has no public access and has never been released"; `README.md`: "open once its first version is released by a human". Against these, `docs/release-gate.md` line 5: "the Redivis dataset is still public". `ARCHITECTURE.md` names no owner for this fact: to confirm in Redivis. Setting it is done on Redivis by the owner |
| 39 | A person reviews the draft before release | WAITS ON THE OWNER | Release step 3 (`warehouse/redivis/README.md`): "look for a *wrong* answer, not only an incomplete one: a table whose rows doubled, a window that shrank, a license that changed". For a first release there is no earlier version to compare with, so the review is of the whole draft: 145 public tables, plus `erw_headers`, `erw_coverage`, `erw_sources`, plus the 54 old tables of item 5 if they are still there |
| 40 | The Release click, with its note | WAITS ON THE OWNER | `CLAUDE.md`, non-negotiable 6; release step 4. After it "the next upload opens a new draft by itself (`create_next_version(if_not_exists=True)`)" |

## I. The documents a reader of the release will open

| # | Item | Status | Evidence, and what is missing |
|---|---|---|---|
| 41 | The repository's summary documents agree with what is released | NOT DONE | Four documents state the size of the warehouse and none matches `coverage.csv` today (171 tables, 22,367,753 rows): `README.md` "As of 2026-09-29: 65 tables, 4,812,358 rows"; `docs/OVERVIEW.md` 113 tables, 4,812,358 rows; `STATUS.md` "Generated 2026-09-30 23:49 UTC", 82 tables, 10,425,611 rows (the README says the daily run keeps it current); `docs/state_2026-10-04.md` 132 tables, 16,048,958 rows. `ARCHITECTURE.md` section 2: what the warehouse holds today is `warehouse/metadata/coverage.csv` and `docs/coverage.md`. `README.md`'s "Not in it yet" list also names SPP real-time series and datacenter records, which `coverage.csv` now holds |

## Notes

- **The freeze.** `REVIEW_FREEZE` in the repository root reads `start: 2026-10-05`, `end: 2026-10-07`. `CLAUDE.md` rule 9 forbids, during a freeze, a change to "what a visitor sees on a live page, or any table a live page reads". A Redivis release changes neither the site nor Supabase (the live layer is loaded from the validated tables, not from Redivis: `ARCHITECTURE.md` section 1). Whether the owner wants a release during a freeze is the owner's call.
- **What was not checked.** The state of either dataset on redivis.com; the validator, which was not run again; the 54 old tables' presence in the draft. Each is marked above.
- **How the counts were made.** `coverage.csv`, `sources.csv`, `redivis_uploads.csv` and `live_set.yaml` were read with short scripts on 7 October 2026; the `full`, `recent`, `catalogue_hold` and `review_hold` patterns of `live_set.yaml` were matched against the table names of `coverage.csv`. Table headers were read from the files in `warehouse/output` on this machine.
