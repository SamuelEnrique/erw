# The reader's questions: a utility's large-load rule (chain 302, session 7200, 16 November 2026)

Energy Research Warehouse (ERW). What three readers need to know about a utility's large-load rule before they choose a site, and which column of the three tables answers each question. The design of the large-load rules section on the All grids tab (`/cost-of-power?view=allgrids`) and on `/policy` follows from this page.

## The readers

- **The energy lead of an AI lab** has a load of 300 MW to 1 GW and a date it must run. They need to know whether the utility can take the load, what the rule makes them sign, and when the load can energize.
- **A developer** puts the land, the power and the building together and sells or leases the result. They need the money they must put up before anything is built, the money at risk if the tenant walks away, and the timed steps.
- **A fund analyst** prices the risk. They need the same figures for many utilities at once, the rule's status (a proposal can change), and what changed lately.

## The questions, and the columns that answer them

| # | Question | Who asks first | Column (`utility_large_load_rules` unless named) | Public rows that print a value (of 100) |
|---:|---|---|---|---:|
| 1 | Does the rule cover my load? The smallest load it covers. | all three | `x_threshold_mw` (a phrase: MW, load factor, contiguous site) | 66 |
| 2 | How long must I sign for? | lab, fund | `x_contract_term` | 50 |
| 3 | What must I pay if I use less? The minimum bill or take-or-pay share. | fund, developer | `x_min_demand` | 48 |
| 4 | What must I post before anything is built? The collateral. | developer | `x_collateral` | 65 |
| 5 | What does leaving early cost? The exit fee. | fund, developer | `x_exit_fee` | 44 |
| 6 | Who pays for the upgrades? | developer | No column. Some rows print it inside the minimum demand, collateral or exit fee words, or the notes (35 rows name upgrades, contributions or facilities charges there). Written so on the page, not filled in. | not a field |
| 7 | How long do the studies take? | lab | `x_study_timeline` | 30 |
| 8 | When can the load energize? | lab | `x_connection_timeline` | 29 |
| 9 | How many others are ahead of me? | lab, fund | `x_queue_size` (28 more rows point to the same utility's row that holds the figure) | 37 |
| 10 | Is the rule settled? Its status and the date. | fund | `status`, `x_status_date`, `x_docket` | 100 |
| 11 | What changed in the last 90 days? | fund | `utility_large_load_rule_changes` (94 public rows, 18 August to 13 November 2026), `x_affects` names the rule | 94 |
| 12 | What does the state's law require? | all three | `state_large_load_laws` (27 public rows, 26 states) | 27 |

Every value carries its cite (`<field>_cite`: the page or section and the words). A value is drawn as the document prints it, never shortened into a number the document does not print.

## What follows for the page

- **One row a rule, the questions as columns,** in the order of the table above. A value too long for a cell is cut at a word, and the whole value and its cite are in the hover.
- **"not published"** is drawn as such: the documents read do not state it. The hover says what was searched.
- **A field held in the ERW's own registry** (`x_held`) is drawn as "in the registry", the file named on hover, not repeated.
- **A held row or a withheld field** (a source whose terms ask permission) is drawn blank with "license needed" on hover. The utility's name is printed: the table's header names it.
- **Two rules side by side (A and B),** because the fund analyst compares.
- **On the All grids tab, each row's Utility cell and its Time to connect cell** open the rule of the row's utility, where one was read. A row whose utility has no rule says so in the same place.
- **The 90 days of changes, newest first,** by region, each with the rule it changed.
- **The state's laws on `/policy`,** linked from the rule's state.
