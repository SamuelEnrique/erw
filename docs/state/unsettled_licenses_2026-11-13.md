# The 26 tables whose license is still not settled

Energy Research Warehouse (ERW). Chain 229 (the licensing sweep, lab-desktop third window), session 4114, 13 November 2026. For Samuel. Nothing was sent to anyone. This replaces `docs/state/unsettled_licenses_2026-10-19.md` (19 tables then; 71 at the sweep's start, session 4100). A table is "not settled" when a publisher on it has no verdict in `warehouse/metadata/license_verdicts.csv`: its page could not be read, it states no terms of reuse, or the table rests on many documents rather than one publisher. Every page named here was asked with its robots file read first (`warehouse/metadata/license_reads.csv`). The defaults are taken; each is yours to change.

## Read this first

- **Public-flagged: 5 of the 26.**
  - **Out of release v1:** `large_load_rules` and `large_load_rule_reads` (session 4109). `usace_nid_dams`, `utility_large_load_tariffs` and `large_load_connection_rules` are held from Redivis (not uploaded).
  - **Not held on the site:** none of the five is "license needed", and none is in the live set. `large_load_rules` reaches the site through `site/data/datacenter/rules.json`; every page is in review.
- **The other 21 are internal,** so none reaches a visitor whatever its verdict.
- **Four groups:** pages without terms (7), US federal agencies whose pages refuse or state nothing (12), tables built from many documents (4), and the four state commissions' records-access statements (2), plus `usace_nid_dams`.

## Pages that state no terms of reuse (7 tables, internal)

| Table | Publisher | Pages read | Default |
|---|---|---|---|
| `amm_guatemala_generation_monthly` | Administrador del Mercado Mayorista (AMM), Guatemala | its source page (read 1795) and reads 719 to 732 (session 2408): no terms, no copyright line | stays internal |
| `ens_denmark_electricity_monthly` | Danish Energy Agency (Energistyrelsen) | its statistics page (read 1799) and read 598: no terms; the workbook names Energinet as its source for most data | stays internal |
| `statgl_greenland_electricity_annual` | Statistics Greenland | its Statbank page (read 1802); no terms page found (session 2510) | stays internal |
| `statnett_norway_daily` | Statnett SF | its production and consumption page (read 1803, drawn by script) and session 2350's reads | stays internal |
| `ask_kosovo_electricity_monthly` | Kosovo Agency of Statistics (ASK) | its home page (read 1804): a bare "©" with no owner named; Kosovo's administrative instruction 02/2023 sets the sale of statistical data (session 2524) | stays internal |
| `pse_poland_balance_15min` | PSE S.A. | its home page (read 1805) and reads 431 to 436 and 458 (no terms of use for its data) | stays internal |
| `gastat_saudi_electricity_annual` | Ministry of Energy, Saudi Arabia, as published by GASTAT | GASTAT's use policy (read 1037) allows reuse "Except for trademarks, logos, and any clearly identified third-party material", and each table names the Ministry of Energy as its source | stays internal |

## US federal agencies (12 tables, internal)

A work of the U.S. Government is not subject to copyright (17 U.S.C. 105). The ERW records a verdict only from a sentence on the publisher's page. These agencies' pages refuse the ERW's reader or state no terms, so their tables wait. A "permission" verdict would misstate the statute, and a "public" one would have no page behind it.

| Table | Publisher | Pages read | Default |
|---|---|---|---|
| `ferc_eqr_buyer_doubtful`, `ferc_eqr_buyer_names`, `ferc_eqr_contract_terms`, `ferc_eqr_contracts`, `ferc_eqr_contracts_history`, `ferc_eqr_party_mw`, `ferc_eqr_party_totals`, `ferc_eqr_quarter_changes` | FERC | www.ferc.gov answers 403 (read 58, 12 October; read 1692, its open data catalog, 13 November); its robots file (read 1687) allows the paths | stays internal |
| `nrcs_snotel_swe_daily` | USDA Natural Resources Conservation Service | www.usda.gov answers 403 to its robots file (read 1761) | stays internal |
| `treasury_1603_awards` | U.S. Department of the Treasury | its site policies and notices (read 1765): no terms of reuse | stays internal |
| `usaspending_doe_obligations` | Bureau of the Fiscal Service (USAspending.gov) | its page is drawn by script; not asked | stays internal |
| `ornl_tedb_transportation_annual` | Oak Ridge National Laboratory, Transportation Energy Data Book | its citation page (read 1766): a citation only | stays internal |

## Tables built from many documents (4 tables)

| Table | Flag | What the table rests on | Default |
|---|---|---|---|
| `large_load_connection_rules` | public | grid operators' guides and utilities' filed rules, read into the ERW's registry (no single publisher) | unchanged: not on Redivis, not live; a ruling would settle it (accept public-records filings and fair quotation, or hold it) |
| `utility_large_load_tariffs` | public | the state commissions' filed tariffs, read into the ERW's registry | unchanged: not on Redivis (the uploader refuses it while unsettled) |
| `large_load_statements` | internal | utilities' and operators' statements, each row's own document | stays internal (its public selection, `large_load_public`, is public by your ruling of 14 October) |
| `news_scores_shadow` | internal | a model's scores of the outlets' headlines (the shadow scorer, switched off since session 206) | stays internal |

## The four state commissions (2 tables, public-flagged)

- **The tables:** `large_load_rules` and `large_load_rule_reads`.
- **Unread publishers:** the Arizona Corporation Commission, the Illinois Commerce Commission, the Oregon Public Utility Commission and the Pennsylvania Public Utility Commission.
- **What their pages say:** they speak of access to public records, not of reuse (`docs/methods/datacenter_cost.md`, "Each regulator's terms").
- **Default:** out of release v1 (session 4109); their rows on the datacenter page stay as they are while every page is in review.
- **What would settle them:** your ruling that a commission's filings, quoted briefly with a link, may be public.

## `usace_nid_dams` (public-flagged)

- **The publisher:** the U.S. Army Corps of Engineers' National Inventory of Dams.
- **Why unsettled:** www.usace.army.mil answers 403 to its robots file (read 1762), and the two catalog addresses tried answered 404 (reads 1691, 1699).
- **Default: unchanged** (the flag is an earlier choice; nothing loosens or tightens it without a sentence read).
