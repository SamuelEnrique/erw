# Session 3302 report (chain 200, session 3 of 13): the three tables written and checked

lab-desktop, 6 November 2026, 19:31 to 19:36 UTC. Branch `wip/3300-companies`.

## What was done

- **The write**, under the data lock (`runs/c200/write_table.sh 3302`, from chain 147's): the builder and its reviewed aliases copied into the main checkout for the run and removed after; the branch's validator in for the run (Decision 76). Lock taken 19:32:06, released 19:32:45. Builder exit 0; the validator exit 0 on each table; coverage exit 0; archive exit 0 (run `20261106T193229Z-local`: 3 tables, 136,805 rows, bucket `erw-archive`); the metadata diff applied to the branch, main's files put back; `done, fail=0`.
- **Rows:** `company_directory` 13,964 companies (11,593 with an EIA utility id, 9,229 named in two or more inputs); `company_aliases` 25,877 names; `company_links` 96,964 links. Licenses: 12,655 companies wholly from public rows, 1,176 wholly from internal rows (deals, datacenter tables, NYISO queue), 133 mixed.
- **Coverage:** `build_coverage.py` had no sector rule for the tables (added: power;deals), gave them the iso `company` (now `none`) and the tier `source` (now `model_extracted`: their names come from the deals', datacenters' and policy actions' model extraction). Rebuilt with `runs/c200/coverage_only.sh` under the lock (19:34:02 to 19:34:07).

## Match rates by input

| Input | Links | Rows named | Companies | To an EIA company | In 2+ inputs | Rule: id / reviewed / anchored name / name / company word | License |
|---|---|---|---|---|---|---|---|
| energy_deals | 853 | 500 of 529 | 480 | 7.7% | 31.3% | 0 / 11 / 66 / 764 / 12 | internal |
| datacenter_facilities | 457 | 410 of 428 | 115 | 30.4% | 99.8% | 0 / 3 / 139 / 314 / 1 | internal |
| datacenter_projects | 191 | 145 of 163 | 110 | 6.3% | 100% | 0 / 3 / 12 / 175 / 1 | internal |
| eia860m_operating_generators | 28,712 | all | 6,060 | 100% | 99.5% | all id | public |
| eia860m_planned_generators | 2,361 | all | 1,000 | 100% | 97.5% | all id | public |
| eia860_plants_annual | 17,349 | all | 6,945 | 100% | 98.8% | all id | public |
| eia860_generator_owners | 5,680 | all | 2,047 | 100% | 35.0% | all id | public |
| eia861_utility_data | 22,716 | all | 3,542 | 100% | 82.2% | all id | public |
| utility_service_territories | 11,893 | all | 2,909 | 100% | 99.5% | all id | public |
| ercot_interconnection_queue | 1,758 | all | 1,291 | 12.5% | 14.5% | 0 / 0 / 220 / 1,538 / 0 | public |
| nyiso_interconnection_queue | 1,604 | 1,604 of 1,814 | 765 | 13.7% | 18.1% | 0 / 16 / 204 / 1,383 / 1 | internal |
| policy_actions | 3,178 | 2,020 | 67 | 0.3% | 35.6% | 0 / 242 / 0 / 2,936 / 0 | public |
| nrc_power_reactors | 212 | 95 of 130 | 45 | 45.8% | 72.2% | 0 / 14 / 83 / 84 / 31 | public |

- The deal rows not named (29) hold only descriptions or countries; the NYISO rows not named (210) have no developer; the NRC rows not named are the 35 reactors with no licensee, operator or parent in the file.

## Checked

- The fifteen companies with the most names: each is one company (an EIA id across a rename: "Lyon Electric Cooperative" and "Lyon-Lincoln Electric Coop" are utility 11345; "South Carolina Electric & Gas" and "Dominion Energy South Carolina" are 17539; spellings of "ACE DevCo NC"; "Cheyenne Light Fuel & Power d/b/a Black Hills Energy").
- A miss seen: "Consolidated Edison Co. of NY" (NYISO) is its own row beside EIA's utility 4226: left for the next chain's resolution faults (queue/next/201, sessions 7 and 8).
- Main's checkout clean after the write (no tracked file changed; the copied builder and aliases removed).

## Decisions made without you

- `derived` stays `no` in coverage for these tables, as for every entities table: `build_coverage.entities_row` never reads the "Derived from:" line (interconnection_durations and energy_projects show the same). Not changed here: a fix flips other tables' rows.
- The coverage rebuild's conflict in the branch (the first write's rows against the rebuild's) was resolved to the rebuild's rows; the tier commit had also taken in the write's metadata, said in its follow-up commit's message.

## For Samuel's ruling

- Whether `build_coverage.py` should read "Derived from:" for entities tables too (it would mark about a dozen tables derived and check their licenses).

## Cost

- No model call. USD 0.00.
