# Energy equities: the page files and their rules

Energy Research Warehouse (ERW), method note written in session 10000 (chain 701, part D) on 26 November 2026. Contract: `docs/state/page_files_equities.md`. Sources and verdicts: `docs/reviews/equities-sources-2026-11-26.md`.

## What the files hold today

Builder: `warehouse/derived/equity_page_files.py` (no request; warehouse tables only), a daily step of the data machine. It writes `site/data/equities/index.json`, `board.json` and `energy_prices.json`.

- **The equity side is held.** SEC EDGAR, the one public source of each company's industry code (SIC), share count and statements, refuses the ERW's contact string (HTTP 403, "Undeclared Automated Tool"); and no free source of daily share prices or index levels lets the ERW keep them (Stooq's robots file refuses every reader, Nasdaq forbids storing, Tiingo and Alpha Vantage need keys and are internal). So `index.json` lists the fifteen segments with the reason their rule cannot be applied and no company or index; every row of `board.json` is held (`not_held`) with that reason; no company, index or segment file is written. A page draws each blank with its reason.
- **The energy prices are the warehouse's own** (`energy_prices.json`): WTI, Brent and Henry Hub spot (`eia_fuel_spot_prices`, daily), ERCOT's hub average day-ahead daily mean (`ercot_hub_prices_daily`, `da_mean`), CAISO's SP15 and NP15 day-ahead daily means (`iso_hub_prices_history`, the mean of each complete Pacific day: 24 hours, 23 or 25 on the clock-change days; a day short of an hour is not written), uranium (`imf_commodity_prices`, PURAN, monthly, on its own dates), and California's carbon allowance at its quarterly auctions (`carb_auction_allowance_prices`, current vintage, on its own dates). PJM, NYISO and ISO-NE (held by their terms, `docs/licenses.md`) and MISO (paused) are series with a status and no rows.
- **Span.** Each daily series from 2016-01-01: the contract's span is that of the longest shown equity series, and none is shown yet (a dated line of the contract).

## Moves

Each series' `moves`, as the board computes its own rows': `d` the previous day held; `w` the last day held on or before 7 calendar days back; `m` one calendar month back; `ytd` the last day held of the previous year; `y` one calendar year back. `ch` is the last value less the value then, `pct` that over the value then times 100. No score, no signal, no view.

## The rules that wait for the SEC

When EDGAR can be read, the universe is every company whose SEC industry code is an energy code, one segment by the code (integrated oil and gas 2911 with exploration; exploration and production 1311 and 1381; midstream 4922 to 4924 and 4610; refining 2911 without upstream; oilfield services 1389 and 3533; coal 1220 and 1221; regulated utilities 4911, 4931, 4932, 4939 with a rate base; independent power 4911 without; nuclear and uranium 1094 and the owners of reactors; solar 3674 makers of cells; wind 3511; storage, hydrogen and grid equipment by code 3690, 2810 and 3612 to 3613), a company that fits two codes in both and named in `segments_note`. This list is the draft of the written rule, to be fixed in this note before any company is placed; matched to `company_directory` by SEC number or exact legal name only.

## The universe (the written rule, fixed on 27 November 2026)

The owner's ruling of 26 November 2026 gave the SEC a contact address; it is kept in the data machine's `.env` as
`SEC_USER_AGENT` (the form of the SEC's "Accessing EDGAR Data" page: a name and a contact address) and never written in
the repository. Read first, with that string: www.sec.gov's robots file (it allows `/files/` and `/Archives/edgar/`
and disallows `/cgi-bin`, which nothing here asks), data.sec.gov's (none: HTTP 404), the access page ("Current max
request rate: 10 requests/second"; "Download only what you need") and the privacy and security policy: "Information
presented on sec.gov is considered public information and may be copied or further distributed by users of the web site
without the SEC's permission. Please consider appropriate citation to the SEC as the source." So the two tables are
public, and every row and file names the SEC. The connector, `warehouse/connectors/sec_edgar.py`, waits a quarter of a
second between two requests.

`equity_universe`: every company in the SEC's list of tickers (`company_tickers_exchange.json`) listed on an
exchange (NYSE, Nasdaq, Cboe, TXSE; an over-the-counter name is not listed) whose SEC industry code is one of these. Its
segments are its code's; no company is placed or moved by judgment.

| Segment | SEC industry codes |
|---|---|
| Exploration and production | 1311 |
| Integrated oil and gas, and Refining | 2911 (the code does not separate the two: in both) |
| Oilfield services | 1381, 1382, 1389, 3533 |
| Midstream and pipelines | 4610, 4922; 4923 and 4924 also in regulated utilities |
| Regulated electric and gas utilities | 4931, 4932, 4939; 4911 also in independent power; 4923, 4924 also in midstream |
| Independent power producers | 4991; 4911 also in regulated utilities |
| Coal | 1220, 1221, 1222 |
| Grid and electrical equipment | 3612, 3613 |

The draft of 26 November named codes that, read against the companies filing under them, are not the segment: 3690 holds
Energizer and a flight simulator maker beside the battery makers, 2810 the titanium pigment makers beside the industrial
gases, 3511 every turbine, 3674 every semiconductor maker beside the solar ones. So LNG, nuclear and uranium, solar, wind,
storage, and hydrogen and fuel cells hold no company: no code is any of them alone, and each says so in its `rule_why`.
Cheniere and the other LNG exporters file under 4924 with the local gas distributors, so they are in midstream and in
regulated utilities, with the note. A named list for the six would be judgment: for the owner's ruling.

The SIC of each listed company is read from its submissions file: once from the SEC's nightly bulk file of all of them
(1.6 GB, one request on 27 November 2026), kept in `warehouse/raw/sec_edgar/sic_cache.csv`; afterwards only a listed
company new to the cache is asked for. `directory_id` is the `company_directory` row of the same legal name, case,
commas and periods aside (the directory holds no SEC number): 18 of 307 on 27 November.

## The statements

`equity_fundamentals_quarterly`: each universe company's XBRL company facts, as filed, every filing kept (vintage the
filing date). Five lines: revenue, net income and capital spending (durations of 3, 6, 9 or 12 months as the filing
reports them, the months in the variable's name: a 10-Q's cash flow is year to date), long-term debt and shares
outstanding (instants at the period's end; shares in unit `count`). For each line, period and filing the first concept
of its list that the filing holds is read and named in `x_concept` (revenue: `Revenues`, then
`RevenueFromContractWithCustomerExcludingAssessedTax` and four more; the lists are in the connector). Only us-gaap facts
of 10-Q and 10-K filings and their amendments are read: a foreign filer's 20-F or 40-F (often IFRS) is not, and 64 of the
307 companies have no rows (the page says so for each). A fact whose period ends after its filing date is a tagging error
and is left out (one on 27 November). First written on 27 November 2026: 146,456 rows of 243 companies, periods from 2007.
Afterwards a company's facts are asked again only when EDGAR's daily form index shows it filed a 10-Q, 10-K or an
amendment since the last run.

The page files: `index.json` lists the 307 companies with their segments and SIC; each company's series file holds its
prices as null with the license reason (no source a license allows: the owner's ruling keeps them blank) and its
`quarterly` rows, each filing's own period (the newest period end in that filing, one row a period length), newest
first. The section "The rules that wait for the SEC" above is the draft this section replaces.

## Joint filings (27 November 2026, done-line request 579)

Many utilities file one 10-Q for a parent and its subsidiaries, and the SEC keeps the facts of such a filing in one of the
filers' company-facts files: NextEra Energy's June and September 2026 10-Qs sit in Florida Power & Light's file (CIK
37634), which the SEC names NEXTERA ENERGY, INC. So eighteen utilities seemed to stop at March 2026. The rule: a company's
own 10-Q or 10-K (marked XBRL in its submissions), for a period after the newest its own facts hold, that its facts lack,
is read from a co-registrant's file (the filers named in the filing's EDGAR header, or in the day's form index) only when
that file names the same entity as the company's own (equal but for case, commas, periods and Company, Corporation,
Incorporated, Limited against their abbreviations), and only that filing's facts are taken, credited to the company.
A parent's file, which holds the parent's consolidated figures, is never read for a subsidiary. On 27 November: 30 filings
joined; twelve of the eighteen now reach September 2026 (NextEra, Duke, AEP, Exelon, FirstEnergy and others); Dominion,
DTE, Entergy, PPL, Southern and GFUZ still stop at March 2026, because their later filings sit in a co-registrant's file
under that co-registrant's own name. A header the SEC does not serve (404) and a filer with no company-facts file are kept
as such and not asked again.

## Two notes while statements are shown (done-line request 579)

`fundamentals_why` carries a note, the status staying `shown`, by two written rules: the newest filing is more than
two years old (RCON's ends in September 2016: "the company has filed neither since"), or the filed history under the
company's SEC number starts within two years (ExxonMobil's new holding company, from June 2026: "a new registrant, and any
predecessor's filings under another SEC number are not read"). Joining a predecessor's number is not done: nothing in the
SEC's files names it.

## The newest filing in the list (done-line request 578)

Each company of `index.json` carries `newest_filed`: its newest period end and, for it, each statement line's figure
for the shortest period to that end (a 10-Q's 3 months where filed, else its year to date, `months` saying which),
debt and shares outstanding at that end, the later filing's figure where a period was filed twice: the page's own rule
(`site/lib/equities.ts` `newestOf`). Null when nothing is filed.

Since session 11408 (the owner's choice on the weekend page of 28 November 2026) each company also carries `newest_year`: the newest 12 months of revenue it filed (a 10-K's year), with its end, form, filing day and link, the later filing's figure where that year was filed twice (`newest_year` in the builder); null when no year's revenue is filed. "Every company" draws it as a third line of the newest period's cell, "Year to <end>", unless the newest period is that year. On the series files of 28 November: 223 of the 243 companies with filings carry a year, and 216 show it beside a shorter newest period.

## Periods that do not add up (27 November 2026, done-line request 581)

Each figure is the filing's own, and yet a company's periods can disagree: Hornbeck Offshore's September 10-Q tags its revenue `Revenues` (649,316,000 for nine months) where its March and June 10-Qs tagged `RevenueFromContractWithCustomer...`, and its June 10-Q's six months (570,726,000) are less than its two quarters as each was filed (287,946,000 and 304,016,000): a change of concept between filings and a restatement inside a filing. HMH's September 10-Q reports a six-month period from 1 April, a successor's period after its listing, under `ProfitLoss`. A third rule of `fundamentals_why` says so: among a company's newest four quarter ends, where a filed year to date less the year to date a quarter before differs from the quarter filed by more than 1 percent (revenue or net income, the later filing where a period was filed twice), the note names the period end; nothing is changed or left out. 20 companies on 27 November (after the two notes before it, which come first).

## The share count on the cover (27 November 2026, a reader's case of part F)

A utility analyst setting Southern Company beside Duke Energy found Southern's shares outstanding "not filed" in all 112 periods: Southern, like 71 other companies of the 243 with filed statements, tags no balance-sheet `CommonStockSharesOutstanding`. Every 10-Q and 10-K gives the count on its cover (`dei:EntityCommonStockSharesOutstanding`), at a date of its own, usually a few weeks after the period's end (Southern's first 10-Q of 2026: 1,127,301,098 shares, as of the cover). `equity_fundamentals_quarterly` carries it as a line of its own, `shares_outstanding_cover` (unit count, ts_utc the cover's date, x_concept the dei concept), beside the balance-sheet line, which is unchanged: 224 of the 243 companies then have a count (171 before; 10,555 rows on the cached facts of 27 November). The page files leave it out of the period rows, which are keyed by each filing's own period end; whether the page shows the cover's count where the balance sheet has none is the page's choice.

## A joint filer is not a new registrant (27 November 2026, a reader's case of part F)

The second rule of `fundamentals_why` named every company whose own XBRL facts start within two years "a new registrant". Three of the 23 are not: Consumers Energy (10-Qs and 10-Ks under its own SEC number since the period to 30 June 2010), Entergy Arkansas (since 30 September 2009) and Pacific Gas and Electric (since 30 June 2011) file jointly with their parents, and until lately their statements were tagged under the parent's number. The builder now reads each company's first 10-Q or 10-K marked XBRL from the SEC's bulk submissions file the connector keeps (no request; the connector's own rule, `own_filings`), and where that is older than two years the note says the company has filed since then and its own facts start lately. Where the bulk file is not on the machine the note names both possibilities. The 20 others keep the new-registrant note (ExxonMobil Holdings Corp, CIK 2115436, now holds the ticker XOM: Exxon Mobil Corporation's history under CIK 34088 is a predecessor's, not read).
