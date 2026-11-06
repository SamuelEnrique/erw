# The company database (platform tool 10)

Energy Research Warehouse (ERW). Sessions 3301 to 3303 (chain 200, 6 November 2026). The code: `warehouse/derived/companies.py` (the builder), `warehouse/companies/reviewed_aliases.csv` (the reviewed aliases), `warehouse/derived/check_companies.py` (the tracers and the cross-checks), `tests/test_session3301_companies.py`.

## What it is

A directory of the companies the warehouse already names, built from the tables it holds and nothing else: no request, no model call, no figure typed in. Three tables:

| Table | Shape | One row | Rows (6 November 2026) |
|---|---|---|---|
| `company_directory` | entities, `company` | a company: name, id, kind, segment, parent, HQ state, first and last seen, its footprint | 13,964 |
| `company_aliases` | entities, `company_alias` | a name a company goes by, as one table writes it in one role, with the first row and the count of rows | 25,877 |
| `company_links` | entities, `company_link` | a company named in one row of an input table, with the role, the name as written, the rule, a confidence, the row's license and its MW, USD, date, fuel, state and grid | 96,964 |

`energy_companies` (the Thesis Builder's companies and the deal parties, session 25 onward) is a different table and stays as it was; the deals page's Companies tab reads it.

## The inputs

| Input | Role of the name | Anchor |
|---|---|---|
| `energy_deals` | buyer, seller, party (other_parties) | none |
| `datacenter_projects`, `datacenter_facilities` | operator, developer, utility | none |
| `eia860m_operating_generators`, `eia860m_planned_generators` | operator | EIA utility id |
| `eia860_plants_annual` | operator | EIA utility id |
| `eia860_generator_owners` | owner (jointly owned generators only: Form EIA-860 schedule 4) | the owner's EIA utility id |
| `eia861_utility_data`, `utility_service_territories` | utility, service territory (a county) | EIA utility number |
| `ercot_interconnection_queue`, `nyiso_interconnection_queue` | interconnection customer | none |
| `policy_actions` | agency (the parties field) | none |
| `nrc_power_reactors` | licensee, operator, parent (the NRC's parent company field) | none |

The CAISO, ISO-NE, MISO and SPP queues and Berkeley Lab's Queued Up file name no developer, so they add no company. The counterparty directory of chain 156 (`wip/3233-deals`) had not landed on 6 November 2026; three of its aliases are taken with their evidence.

## The rules

1. **Normalization** (`norm`): ASCII; lower case; "&" and "+" read as "and"; apostrophes and punctuation dropped; EIA's abbreviations expanded as whole words (Elec, Coop, Assn, Mun, Pwr, Dept, Util, Svc, Mgmt, Dist, Auth, Admin, Intl, Natl, Pub); "Co" inside a name read as "Company"; a leading "the" dropped; legal forms at the end dropped (Inc, LLC, Corp, Co, Company, LP, LLP, Ltd, Limited, plc, SA, AG, NV, BV, GmbH, SE, SpA and others).
2. **An EIA utility id is a company.** EIA-861's utility number, EIA-860's operator utility id and its owner id are one list of codes: every row that carries an id is that company, whatever name the row gives it. Two ids are never merged by name (two cities of Richmond stay two).
3. **The reviewed aliases** (`warehouse/companies/reviewed_aliases.csv`) map a name to another, and may give an EIA id, a parent or a kind. Each row has its evidence: a stored story's words ("U.S. Department of Energy (DOE)", `news_stories` event id), a policy row (agency NRC, parties Nuclear Regulatory Commission) or an EIA row. A row without evidence stops the build.
4. **A name without an id** joins the anchored company whose normalized name it equals, where exactly one does.
5. **Names left** are grouped on their normalized name. A name that is another with a company word added at its end ("Energy", "Power", "Group": "Constellation Energy", "Constellation") joins the shorter one, where the shorter is not a common word ("American", "National", "Solar" and others) or a place, is at least four letters, and is not the name of an anchored company.
6. **A party field** is split on ";", "," and " and " (a name that holds "and", such as Industrial and Commercial Bank of China, is kept whole). A description is no company: a lower-case start ("investors"), a country, a state or a government ("State of Indiana", "Belgian state"), a thing tied to a company ("Amazon data center unit", "Meta-backed data centre", "Blackstone vehicle", "Standard Lithium-Equinor JV"), a law ("CHIPS Act"). "X's Y" is Y, with X its parent and the row its evidence ("Blackstone's QTS").
7. **A parent** is a second field, never in place of the name, from three places only: the NRC's parent company field ("X with principal subsidiaries ..." is X; "X doing business as Y" is Y), a deal party written "X's Y", and the reviewed aliases.

Each link carries its rule and a confidence: an EIA id 1.0, a reviewed alias 0.95, the name of an anchored company 0.9, a name among names without an id 0.85, a company word added 0.7. A company's `min_confidence` is its weakest link's.

## The columns of `company_directory`

- **entity_id**: `company:eia-<id>` where the company has an EIA id, else `company:<normalized name>` (Decision 76 of the data standard).
- **name**: the reviewed aliases' canonical name, else EIA-861's newest name, else the NRC's parent field's, else the spelling its rows use most.
- **kind**: the first of regulator, lab or hyperscaler, OEM, utility, IPP, lender or investor, developer, operator, other that its rows show; `kind_basis` names the rule. Utility: EIA-861 ownership investor owned, cooperative, municipal, political subdivision, state or federal; EIA-860 sector Electric Utility; a service territory. IPP: EIA-860 sector IPP; a PPA's seller. Lender or investor: the buyer of a debt, equity raise or project finance deal. Developer: an interconnection customer in a queue, an EIA-860M planned generator's operator, a datacenter's developer. Operator: a datacenter's operator, an NRC licensee or operator. Regulator: a policy action's agency with a government word or acronym. A utility that is also a policy party (the power marketing administrations) stays a utility. Lab or hyperscaler and OEM come only from the reviewed file.
- **segment**: the fuel or line with the most MW across the company's plants, plans, queue positions, facilities and deals (`segment_basis` most MW), else with the most deals, else utility or government by kind.
- **hq_state**: the state of the owner's address in EIA-860's owner schedule, the one held table that states a company's address; blank for every company that owns no jointly owned generator.
- **states**, **grids**: the states its rows name, most first; the grids (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP) its plants' balancing authorities, its queue positions and EIA-861's RTO flags name.
- **first_seen**, **last_seen**: the earliest and latest date its rows state: a generator's operating month, a planned generator's planned month, a queue position's queue date, a deal's or a policy action's date, a facility's first story, an EIA-861 year, a reactor's commercial operation.
- **The footprint**: `n_deals`, `deals_mw`, `deals_usd` (each deal once); `n_plants` (EIA plant ids), `n_generators`, `plants_mw` and `mw_<fuel>` (nameplate of operating generators in EIA-860M; fuels solar, wind, gas, coal, nuclear, hydro, storage, oil, geothermal, other, from EIA's energy source codes); `n_owned_generators`, `owned_mw` (nameplate times the percent owned); `n_planned_plants`, `planned_mw`; `n_facilities`, `facilities_mw` (datacenter facilities it operates or develops); `n_queue`, `queue_mw` (positions neither withdrawn nor completed); `n_reactors`, `reactors_mw`; `n_policy_actions`; `n_links`, `n_public_links`, `n_names`, `tables`.
- **footprint_mw**: plants, owned, planned, queue, facilities and deals MW summed: a sort key only (a plant both operated and owned counts twice).
- **license**: public, internal or mixed, by its links.

## Licenses

Every input is public in coverage. Four inputs carry "license needed" in `license_status.csv` (a publisher's own sentence asks for written permission): `energy_deals`, `datacenter_projects`, `datacenter_facilities`, `nyiso_interconnection_queue`. A link or an alias from those is `license` internal; the downloads of the company pages carry only public rows, and the directory's deal, facility and NYISO queue figures are internal figures. The tables themselves are public, as their inputs are in coverage.

## Tracers

`warehouse/derived/check_companies.py` (exit 1 on any failure; 0 on 6 November 2026 over 96,964 links):

1. every link's row is a row of its input table;
2. its name as written is in that row's column for the role;
3. every company of the links is in the directory and every directory row has a link;
4. the directory's counts and MW, recomputed from the links alone by code written apart from the builder's, equal the directory's (to 0.1 MW);
5. every alias is a name of the links for the same company, table and role.

The company pages key every figure to its table, row and column, and their checks are listed in the pages' sessions.

## Cross-checks

Written by `check_companies.py --crosscheck` to `docs/reviews/companies-crosscheck-2026-11-06.md`; checks, never corrections.

- **A utility's retail sales against its fleet.** EIA-861 retail sales (Parts A and B) of the newest year with at least 80% of the median year's utilities (2025) against EIA-860M operated capacity: sales / (capacity x 8,760 h). 295 companies have both; 110 sell more at retail than their own fleet could make running all year (they buy power), 19 sell under a fifth of it (their plants sell at wholesale; the Tennessee Valley Authority's implied use is 0.07, Florida Power & Light's 0.36).
- **A developer's queue MW against its deals' MW.** No company held both a live ERCOT or NYISO queue position and a deal on 6 November 2026: the deals name parents and brands ("NextEra"), the queues name project companies ("NextEra Energy Interconnection Holdings, LLC").

## What it cannot say

- **Corporate families.** EIA files name operating companies, not their holding companies; a parent is known only where the NRC, a deal's "X's Y" or the reviewed file says so. American Electric Power's operating utilities are separate rows with no parent.
- **Queue developers outside ERCOT and NYISO**: the CAISO, ISO-NE, MISO, SPP and Berkeley Lab files name none.
- **Headquarters**: only for owners of jointly owned generators.
- **Project companies**: a solar project's own LLC is a company of its own (it is EIA's operator); grouping it under its sponsor needs a source that states the tie.

## History

- Session 3301: the rules, the reviewed aliases (98 rows), the tests; `company_alias` and `company_link` join the entity types (Decision 76).
- Session 3302: the three tables written under the data lock and archived; coverage's tier (model_extracted) and iso (none) rules.
- Session 3303: this note, the tracers and the cross-checks.
