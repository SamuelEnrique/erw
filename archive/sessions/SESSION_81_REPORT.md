# Session 81 report: the contracts tracker, scoped

**It can be built, and the data is better than expected: FERC's contract files name the seller, the buyer, the product, the term, the delivery point, and a price in about half the rows.** A tracker of where bilateral power contracts are being struck is honest for everything outside ERCOT, with three limits that the page would have to state: no field says what technology a contract is for, about half the contracts give their price as words, and every contract is re-reported each quarter, so "new" has to be read from the execution date.

**The sample pull stayed under its ceiling: 103,281 rows of 150,000.** Nothing was built, nothing is in coverage, nothing was uploaded. One decision needs your approval before anything more is pulled; it is at the end.

Energy Research Warehouse (ERW), session 81, last of the chain of 3 October, on the old laptop, 2026-10-03 from about 20:47 to 21:10 UTC, unattended. **Model spend: USD 0.00.** One approved pull, a sample, under its ceiling; one web search to find FERC's pages; no model call, no force push. Branch `wip/081-eqr-scope` (it holds 077 to 080). The data lock was never taken.

## To finish

```bash
# 1. Nothing to merge but this report (the branch holds 077 to 080; merge them in their order first).
git checkout wip/081-eqr-scope && git fetch origin && git merge origin/main
git push origin wip/081-eqr-scope:task/081-eqr-scope     # a report only: no live page changes with it

# 2. The sample is local, on the old laptop, under runs/session81/ (runs/ is not in git):
#      raw/2026_Q2/                         573 filings' zips as FERC serves them, 4.4 MB
#      eqr_sample_2026_Q2_contracts.csv     6,508 rows      eqr_sample_2026_Q2_transactions.csv   95,592 rows
#      eqr_sample_2026_Q2_ident.csv         1,181 rows      eqr_sample_2026_Q2_indexpub.csv       0 rows
#      listing_2026_Q2.json                 the quarter's 4,077 filings and their sizes (no data rows)
#      history_sizes.json                   the size of each of the 53 quarterly files (headers only)
#      pull_sample.py, httpzip.py           how it was pulled; pull_log_2026_Q2.json, what was fetched
#    Nothing else to run. The next step is a ruling ("For Samuel").
```

## In plain words

### What FERC's Electric Quarterly Reports are

- **Who files.** Public utilities, and non-public utilities "with more than a de minimis market presence" (Order No. 768, 2012). FERC counts 3,672 filers as of the second quarter of 2025. The quarter sampled, the second of 2026, holds 4,077 filings; the count includes refilings.
- **What they file.** Order No. 2001 (2002) requires them to file, each quarter, "transaction information for short-term and long-term cost-based sales and market-based rate sales and the contractual terms and conditions in their agreements for all jurisdictional services" (FERC's words, in its notice of 17 February 2026).
- **The files.** FERC's report viewer (`https://eqrreportviewer.ferc.gov/`, Downloads, "Quarterly Filings, All Companies") gives one zip per quarter from the third quarter of 2013, in CSV and in XML. A quarter's zip holds one small zip per filing, and each of those holds four CSV files:
  - `ident`: the filer, its company identifier, the quarter, and its contact persons;
  - `contracts`: one row per product of each agreement in force (30 columns);
  - `transactions`: one row per sale in the quarter (26 columns);
  - `indexPub`: the index price publishers the filer reports to (empty in every filing sampled).
- **Contracts against transactions.** A contract row is the standing agreement: who sells to whom, under which tariff, executed when, from when to when, which product, how much, at what rate, delivered where. It is filed again every quarter for as long as the agreement is in force. A transaction row is what was actually delivered and billed under an agreement in the quarter: a begin and end time, a quantity, a price, a total charge. The two join on the seller and the agreement's identifier (`contract_service_agreement_id` in contracts, `contract_service_agreement` in transactions). So the contract says what was agreed, and the transactions say what it came to: for a contract whose rate is written as "Market Based Rate", the transactions still give the price paid.
- **The fields a tracker needs, as the contract file names them:**

| What | Columns |
|---|---|
| Seller, buyer, whether affiliates | `seller_company_name`, `customer_company_name`, `contract_affiliate` |
| The agreement | `ferc_tariff_reference`, `contract_service_agreement_id` |
| Term | `contract_execution_date`, `commencement_date_of_contract_term`, `contract_termination_date`, `actual_termination_date`, `extension_provision_description`; `term_name` (LT long, ST short) |
| Product | `product_type_name` (MB market-based, CB cost-based, T transmission), `product_name` (ENERGY, CAPACITY, TOLLING ENERGY, SPINNING RESERVE and others), `class_name` (F firm, NF non-firm, UP unit power), `increment_name`, `increment_peaking_name` |
| Quantity | `quantity`, `units` |
| Price | `rate`, `rate_minimum`, `rate_maximum`, `rate_description`, `rate_units` |
| Delivery point | `point_of_receipt_balancing_authority`, `point_of_receipt_specific_location`, `point_of_delivery_balancing_authority`, `point_of_delivery_specific_location` |

- **The license.** These are filings a federal agency collects and publishes; FERC's notice says the rule exists in part for "making data available to the public". I found no license statement, because FERC's own documentation pages could not be read (below). I would register the source as public, US government publication, with one caution: the `ident` file carries people's names, telephone numbers and email addresses. The scratch table leaves those columns out, and a warehouse table should too.
- **What is missing.**
  - **ERCOT.** Sales inside ERCOT are outside FERC's jurisdiction. In the sample, 0 of 6,508 contract rows name `ERCO` as the delivery or receipt balancing authority.
  - **The technology.** No column says solar, wind, storage or gas. It can only be read from the seller's name ("... Solar, LLC") or the product (`TOLLING ENERGY`). A utility or a marketer selling from a portfolio says nothing about the source.
  - **Buyers that do not file.** A corporate buyer of a power purchase agreement appears only as the customer of a seller that files.
  - **Financial contracts.** Virtual power purchase agreements settle financially and are not sales of power under a FERC tariff; I would not expect them here, and the sample cannot show an absence.
  - **Half the prices.** Below.
- **A change is coming.** Order No. 917 (Federal Register, 24 March 2026, effective 26 May 2026) adopts a new filing standard (XBRL-CSV), extends the filing window to four months after the quarter, drops the index-publisher file and several fields, and adds others. FERC says it will not move the deadline "until the new XBRL-CSV system is operational". The files will change shape at a date the order does not fix; a connector written today reads today's CSV.

**What I could not read.** FERC's documentation pages on `ferc.gov` (the EQR page, the data dictionary, the download-database page, the questions and answers) answered HTTP 403 with a browser challenge. I did not work around it. The description above rests on the Federal Register (FERC's notice of 17 February 2026 and Order No. 917, read in full text), on the report viewer, which does answer, and on the files themselves. The code lists a data dictionary would give (every allowed product name, class and increment) are therefore taken from what the sample holds, not from the dictionary.

### The pull

- **The smallest file that holds a quarter's contracts is the whole quarter:** `CSV_2026_Q2.zip`, 3,601,874,263 bytes, every filing with its transactions. That is far past the ceiling, and it was not downloaded.
- **But the server answers range requests, and the quarter's file is a zip of 4,077 small zips, one per filing.** So a single filing can be fetched alone. I read the file's list of members first (two requests, 8.4 MB, no data rows): a filing's zip is 2,530 bytes at the median and 148 MB at the largest.
- **The sample:** a simple random sample (seed 81) of the filings whose own zip is at most 100,000 bytes, one request each, every row of every file counted, and no further request once the count passed 100,000. It stopped itself after **573 filings: 103,281 rows** (6,508 contract rows, 95,592 transaction rows, 1,181 identification rows), 571 requests, 3,326,552 bytes. The ceiling was 150,000.
- **What the sample is not.** The cap of 100,000 bytes admits 2,877 of the 4,077 filings (70.6 percent) and 0.43 percent of the bytes. The large filers, utilities and power marketers whose filings are mostly transactions, are not in it; fetching one of them means fetching its transactions, and the largest alone would pass the ceiling. **Every count below describes the 573 filings sampled, not the quarter.** They are mostly single-asset project companies, which is where project contracts are filed.

### From the sample

| | |
|---|---|
| Contract rows | 6,508, in 391 of the 573 filings (182 filings hold none) |
| Distinct agreements (a filing and its agreement identifier) | 2,273 |
| Sellers, buyers | 391, 1,174 |
| Product | ENERGY 4,244 rows (two spellings); CAPACITY 581; POINT-TO-POINT AGREEMENT 409; OTHER 371; INTERCONNECTION AGREEMENT 158; SPINNING RESERVE 76; **TOLLING ENERGY 22**; the rest ancillary and transmission products |
| Long term, short term | 5,597, 616 |
| **Rows that state a price as a number** | **3,497 of 6,508 (54 percent)**; 2,961 give only words ("Market Based Rate", a formula, a description); 20 give neither |
| Agreements with a number in at least one row | 994 of 2,273 (44 percent) |
| Energy rows priced in USD per MWh | 2,314; median 56.05, the middle half 34.98 to 80.68 |
| Term, where start and end are both stated | 4,190 rows, median 20.1 years; 2,314 rows give no end date |
| Affiliate contracts | 471 rows |
| Agreements by year of execution | 147 in 2024, 100 in 2025, 107 in 2026 to June (the file holds agreements back to 1954; 288 of the 2,273 were executed before 2000) |

**Storage, solar, wind, tolling.** Read from the seller's name, since no field says it:

| | Rows | Agreements | Sellers | Rows stating a price |
|---|---|---|---|---|
| "Solar" in the seller's name | 1,057 | 174 | 109 | 606 |
| "Wind" | 1,037 | 116 | 60 | 784 |
| "Storage" or "battery" | 98 | 29 | 19 | 5 |
| Product TOLLING ENERGY (any seller) | 22 | | 14 | 0: every tolling row says "Market Based Rate" |

Storage contracts are mostly sales of capacity (54 of the 98 rows), not of energy.

**The largest sellers, by contract rows:** NextEra Energy Point Beach, LLC (497), Sierra Pacific Power Company (455), Cassia Gulch Wind Park, LLC (361), Tuana Springs Energy, LLC (361), Deseret Generation & Transmission Co-operative, Inc. (342), Twin Eagle Resource Management, LLC (189), Lone Valley Solar Park I LLC (176), Entergy Services, LLC (173). A row is a product of an agreement, so a seller with one contract priced year by year has many rows.

**The largest buyers, by agreements:** North Carolina Municipal Power Agency Number 1 (76), PacifiCorp (70), Long Island Lighting Company, d/b/a LIPA (61), PJM Settlement, Inc. (48), FirstEnergy Pennsylvania Electric Company (28), Commonwealth Edison Company (26), Deseret Generation & Transmission Co-operative, Inc. (26), Southern California Edison Company (22). By contract rows: IDAHO POWER COMPANY (722), Wisconsin Electric Power Company (264), Southern California Edison Company (250), WPPI Energy (243).

**By what was billed in the quarter** (transactions, 95,592 rows in 337 filings, USD 2,095,696,295 in all): sellers NextEra Energy Point Beach, LLC (USD 192.8 million), National Grid Generation LLC (97.0), Indiana-Kentucky Electric Corporation (83.3); buyers Wisconsin Electric Power Company (168.4), Southern California Edison Company (117.9), Long Island Lighting Company, d/b/a LIPA (103.4), New York Independent System Operator (96.5).

**Where delivered:** CISO 840 rows, IPCO 765, PJM 443, SWPP 303, MISO 294, PACE 214, ISNE 165, NYIS 145, NEVP 117; 2,806 rows leave the delivery balancing authority empty.

**Three contracts, quoted exactly** (the file's header, then each row as the file holds it):

```
contract_unique_id,seller_company_name,customer_company_name,contract_affiliate,ferc_tariff_reference,contract_service_agreement_id,contract_execution_date,commencement_date_of_contract_term,contract_termination_date,actual_termination_date,extension_provision_description,class_name,term_name,increment_name,increment_peaking_name,product_type_name,product_name,quantity,units,rate,rate_minimum,rate_maximum,rate_description,rate_units,point_of_receipt_balancing_authority,point_of_receipt_specific_location,point_of_delivery_balancing_authority,point_of_delivery_specific_location,begin_date,end_date
```

1. A solar contract with its price, executed in 2025 (filing `CSV_2026_Q2_6671142_1776243.ZIP`): 70 MW of energy to Southern California Edison at USD 60.70 per MWh, July 2025 to January 2041.
```
C200917690,"BigBeau Solar, LLC",SOUTHERN CALIFORNIA EDISON COMPANY,N,"MBR Tariff, FERC Electric Tariff Original Vol. No. 1, 1.0.0",SCE Solar PPA 5191,20250723,20250723,20410131,,None,F,LT,Y,FP,MB,ENERGY,70.0000,MW,60.7000,,,,$/MWH,,,CISO,230 kV bus of the Whirlwind Substation,,
```
2. A storage contract (filing `CSV_2026_Q2_6654590_1773008.ZIP`): 230 MW of capacity to Pacific Gas and Electric at USD 15.38 per kW-month, to May 2039.
```
C1480195,"Sunlight Storage II, LLC",Pacific Gas and Electric Company,N,"Market-Based Rate Tariff, Volume No. 1, 0.0.0",21898,20230123,20230123,20390531,,None,UP,LT,Y,FP,MB,CAPACITY,230,MW,15.3800,,,,$/KW-MO,,,CISO,Red Bluff 230 kV Substation,202406010000,203905312359
```
3. A tolling contract (filing `CSV_2026_Q2_6663803_1775501.ZIP`): a gas plant's output tolled to Puget Sound Energy for 2025 to 2027, with no number.
```
C4,Grays Harbor Energy LLC,"Puget Sound Energy, Inc.",N,FERC Electric Tariff Vol. No. 1,PSE11072024,20241107,20250101,20271231,,None,UP,LT,M,FP,MB,TOLLING ENERGY,,MWH,,,,Market Based Rate,$/MWH,BPAT,,BPAT,Satsop 230kV substation,,
```

**Flagged as implausible, as found:** one storage row gives a rate of 132000 in `$/MW-MO` for 1.056 MW (AFTW Storage, LLC to Pacific Gas and Electric): USD 132,000 per MW a month is about nine times the highest of the other storage capacity prices in the sample (USD 2,000 to 15,380 per MW a month, in their own units). It is what the filer wrote. Product names come in more than one spelling (`ENERGY` and `Energy`), and so do buyers (`Southern California Edison Company` and `Southern California Edison`). A tracker would need a name table, kept by hand and shown.

### How large the full history is

Measured from the files' headers, no download: **53 quarterly CSV files, the third quarter of 2013 to the third of 2026, 120.6 GB compressed.** By year: 0.8 GB in 2013 (two quarters), 2.4 in 2014, 2.8 in 2015, 3.2 in 2016, 4.4 in 2017, 8.9 in 2018, 11.0 in 2019, 11.1 in 2020, 12.2 in 2021, 13.5 in 2022, 14.0 in 2023, 14.3 in 2024, 14.7 in 2025, 7.3 so far in 2026. Before the third quarter of 2013 the data is in an older system the viewer links to separately; I did not look at it.

**In rows, an estimate and no more:** the sample holds one row per 32 bytes of filing zip. At that rate the second quarter of 2026 is about 115 million rows and the history about 3.7 billion, nearly all of them transactions. The large filings are not in the sample and may compress differently, so read this as an order of magnitude.

**Contract rows are a small part, and I cannot bound them from the sample.** The sampled filings hold 11.4 contract rows each. If every one of the quarter's 4,077 filings held that many, the quarter would hold about 46,000 contract rows; the large filers hold more than the small ones, so that is a floor.

### What a tracker page could honestly show

- **New agreements by quarter of execution:** seller, buyer, product, start, end, the delivery balancing authority and point, and the price where the filer gave a number. Because every agreement in force is filed again each quarter with its execution date, **one quarter's file is enough to start**: it holds the standing agreements whenever they were signed. Each new quarter then adds the agreements executed since.
- **Where:** a count and a list by balancing authority, with ERCOT absent and said to be absent.
- **Prices, with their coverage stated:** "a price is stated for 54 percent of rows", by product and by year of execution, never as if it were all contracts. For the rest, the transactions give what was paid, which is a second, larger table.
- **Technology, labelled as read from the seller's name:** solar, wind and storage project companies can be picked out; portfolios cannot. The page would say "sellers whose name says solar", not "solar contracts".
- **What it should not show:** a total of contracted MW (quantity is empty in many rows and its units vary), a market share, or anything about ERCOT, corporate buyers that do not file, or financial contracts.

## Tests and checks

| Check | Result |
|---|---|
| The row count against the ceiling | 103,281 of 150,000; the script stops asking once the count passes 100,000, and a filing is at most 100,000 bytes |
| Every sampled file's header equals the first file's of its kind | yes: 30 contract columns, 26 transaction columns, in all 573 filings |
| The three quoted rows | copied from the raw files' lines, not from the scratch table |
| `python -m unittest discover -s tests` | not rerun: no code in the repository changed in this session (session 80's run: 443 tests, 1 failure, the known one) |

No validator, coverage, archive, upload or load: the sample is not a warehouse table.

## Errors and decisions

- **Decision: a sample of filings by range request, not the quarter's file.** The prompt said not to pull if the smallest download is larger than the ceiling. The smallest download turned out to be one filing, not the quarter, so a sample within the ceiling was possible. I counted every row fetched, transactions included, against the ceiling, not contract rows alone.
- **Decision: the sample is of small filings only,** and the report says so wherever a count appears. A sample that included large filers would have passed the ceiling with their transactions.
- **Decision: FERC's documentation was not read past its 403.** The Federal Register and the files themselves stand in for it; where that leaves a gap (the full code lists, the license statement) the report says so.
- **Decision: the scratch identification table leaves out the contact persons.** The raw zips, as FERC serves them, are kept as they are.
- **Decision: the scripts stay under `runs/session81/`,** with the sample. "Scope it; do not build it": nothing was added to `warehouse/`.
- **Requests made that were not the pull:** the report viewer's Downloads tab (four page requests), the quarter's list of members (two range requests, 8.4 MB), and about 65 header-only requests for file sizes.
- **Error, mine:** I first tried a download address remembered from elsewhere; it answered 404 (headers only, nothing fetched). The real addresses are the ones the viewer lists.

## For Samuel

**One decision: approve, or not, one pull of one quarter, kept to its contracts.**

- **What:** `CSV_2026_Q2.zip` from FERC's report viewer, 3.6 GB, read as a stream; from each of its 4,077 filings keep the `contracts` file and the filer's company identifier, and discard the transactions unread. USD 0, public.
- **Why one quarter:** it holds every agreement in force with its execution date, which is what a tracker of new contracts needs. The history (120.6 GB) adds only agreements that had already ended.
- **Proposed ceiling: 400,000 contract rows,** with a stop if it is passed. The sample puts the floor at about 46,000; the large filers are unknown.
- **Where it would run:** not on this laptop's 8 GB if the stream is held in memory; a filing at a time it needs little.
- **What it would give:** an internal table first (`ferc_eqr_contracts`, events shape, one row per product of an agreement), a name table for sellers and buyers, and a review page. Public only after you have looked at what the names and prices look like in bulk.
- **Then, each quarter:** one such pull, about two months after the quarter ends (four months once Order No. 917's system is running).

Two smaller things: say whether transactions should be scoped next (they hold the prices the contracts leave out, at about a hundred million rows a quarter), and whether someone with a browser should fetch FERC's data dictionary, which this machine could not read.
