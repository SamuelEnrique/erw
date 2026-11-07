# Session 3301 report (chain 200, session 2 of 13): the entity resolution, its rules and tests

lab-desktop, 6 November 2026, 19:19 to 19:31 UTC. Branch `wip/3300-companies`.

## What was done

- **`warehouse/derived/companies.py`**: the company database's builder: thirteen held inputs read, one mention a name in a row, the resolution, three tables (`company_directory`, `company_aliases`, `company_links`). No request, no model call. Runs in about 10 s.
- **The rules, in code:** `norm` (ASCII, lower case, "&" as "and", punctuation dropped, EIA's abbreviations expanded: Elec, Coop, Assn, Mun, Pwr and nine more; "Co" inside a name is "Company"; a leading "the" and the legal forms at the end dropped); `split_parties` (";", "," and " and ", with names that hold "and" kept whole); `is_description` (a lower-case start, countries, descriptions such as "Amazon data center unit", "Meta-backed data centre", "Japanese firms", "CHIPS Act", "State of Indiana"); `split_possessive` ("Blackstone's QTS" is QTS with parent Blackstone, the row its evidence); `parse_parent` (the NRC's parent field: "X with principal subsidiaries ..." is X, "X doing business as Y" is Y, "X (ACR)" adds ACR as an alias).
- **The resolution:** an EIA utility id is an anchor (EIA-861's number, EIA-860's operator id and owner id: one code list); two ids never merge by name; a name without an id joins the one anchored company of that name (none where two share it); names left group on the normalized name, and a name with a company word added ("Energy", "Power", "Group") joins the shorter one where the shorter is no common word and is not an anchored name. A confidence per link: 1.0 id, 0.95 reviewed alias, 0.9 anchored name, 0.85 name, 0.7 company word.
- **Kinds** by the first of regulator, lab or hyperscaler, OEM, utility, IPP, lender or investor, developer, operator, other that a company's rows show (`kind_basis` names the row's rule: EIA-861 ownership, EIA-860 sector, a finance deal's buyer, a PPA's seller, a queue's interconnection customer, a facility's developer or operator, an NRC licensee, a policy action's agency, or the reviewed file).
- **`warehouse/companies/reviewed_aliases.csv`**: 98 rows, each with evidence: 22 aliases and parents (NRC, DOE and three spellings of the Department of Energy, FERC, CPUC, TVA with id 18642, AEP, AWS with parent Amazon, Delfin, GM, CFS, BWXT, NY Power Authority with id 15296, three power marketing administrations with their EIA ids and parent the Energy Department, two Interior bureaus) cited to stored stories' "Name (ACRONYM)" words, policy rows or EIA rows; and 76 kinds (11 labs and hyperscalers, 24 OEMs, 41 lenders and investors), each cited to the first row that names the company. Three of chain 156's aliases (`wip/3233-deals`, not landed) are taken with its evidence.
- **Validator:** `company_alias` and `company_link` join the entity_type vocabulary (`erw_validate.py`, `docs/datastandard.md` Decision 76). The main table is `company_directory`: the validator wants two parts in a name and `energy_companies` is the Thesis Builder's.
- **Tests:** `tests/test_session3301_companies.py`, 20 tests (exit 0).
- **Trial** (read from main's `warehouse/output`, written to the scratchpad, no lock needed): 13,964 companies, 25,877 aliases, 96,964 links; the validator passes all three (exit 0, branch validator).

## Checked

- Every cross-table match from the deals, the datacenter tables and the NRC (67 names) read by hand: all right (e.g. "Vistra" to Vistra Corp, EIA 5504; "South Carolina Electric & Gas Co." to Dominion Energy South Carolina, EIA 17539, the NRC's older name for the same licensee; "Constellation Energy Corporation" to the deals' "Constellation"). 25 queue matches drawn at random: all the same company written two ways.

## Decisions made without you

- **`company_directory`** for the prompt's "companies" table (the validator's two-part rule).
- **A company's name**: the reviewed file's canonical name, else EIA-861's newest, else the NRC's parent field, else the most used spelling.
- **HQ state** only from EIA-860's owner address (the one held table that states a company's address); blank elsewhere.
- **Holding companies** (American Electric Power, Duke Energy, NextEra Energy) stay their own rows beside their EIA-anchored operating companies; a subsidiary names its parent only where the NRC or the reviewed file does.
- Government buyers in deals that are not countries (US Navy, Pentagon) are kept, kind other; countries, states and ministries are left out as descriptions (session 28's ruling for `energy_companies`).

## For Samuel's ruling

- The 76 kind rows of the reviewed file are a session's judgement of well-known companies (Nvidia an OEM, Blackstone a lender or investor); a row's evidence shows the name in the warehouse, not the kind. Keep, or limit kinds to the rules on rows?

## Cost

- No model call. USD 0.00.
