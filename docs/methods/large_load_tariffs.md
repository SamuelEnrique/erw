# Large loads' filed tariffs (`utility_large_load_tariffs`)

Tables: `utility_large_load_tariffs`

Energy Research Warehouse (ERW). Started by session 2871 (chain 147, 5 November 2026). The table records what a load
of 100 MW to 1 GW pays a utility to connect and take delivery, figure by figure, from the tariffs the utilities file
with their state commissions. Nobody publishes this in one table. The All grids tab of `/cost-of-power` reads it
through `site/data/siting/tariffs.json` (`warehouse/derived/siting_page.py`, `tariffs_file`, written by session 730
against this shape and not yet wired).

## What a row is

One figure that one schedule prints: the smallest load it takes, a demand charge, an energy charge, a fixed charge,
the shortest contract term, a minimum bill as a share, collateral or an exit fee stated in months. The row keys on the
schedule (`filed:<EIA utility id>:<schedule>`), the figure (`variable`) and the schedule's effective date (`ts_utc`).

## What is not done

- **Nothing is derived.** No all-in price, no sum of a schedule's demand charges, no estimate. Each value is the
  printed figure in the table's unit, converted only between units (cents to dollars, kWh to MWh, kW to MW). The
  printed words are kept beside it in `x_printed`, with the page in `x_page` and the document in `source_url`.
- **A figure the schedule does not print has no row.** A minimum bill stated in words, not as a share, stays in
  `x_min_bill` and gets no `min_bill_pct` row. The same goes for collateral, exit fees, ramp provisions and terms.
- **Riders are not added.** Fuel, transmission cost recovery and other riders change often and are filed apart from
  the schedule. A schedule's own charges are recorded; a rider is named in `x_term` when the schedule names it.

## The registry

`warehouse/sources/large_load_tariffs/` holds one YAML file a schedule (its README has the form). A session reads the
filed tariff after the host's robots file and terms, and writes each figure with its page and words. The connector
`warehouse/connectors/large_load_tariffs.py` makes no request. It checks every file (each figure has a page and its
words, units are from the list, the license is public or internal, dates are well formed) and refuses the whole write if any
file fails. The validator refuses a row without `source_url`, or a filed row without `x_page` (check `filing_cited`).

## License

Public, row by row (the table's license line reads "public (row-level holds)"). A filed tariff is a public regulatory
record, and each row cites the commission's copy or the utility's filed tariff book (the owner's ruling 4 of 6 November
2026, `docs/state/rulings_2026-11-06.md`). A schedule whose only readable source is a host whose terms ask written
permission (AEP's "personal use only", IN.gov's statewide terms) is `license: internal` in its registry file. Since session
3760 the connector keeps such a file but writes none of its rows to the table, and names it in the header as held for a
license. So no held figure reaches a public copy, and the All grids tab shows the cell as needing a license. AEP Ohio's
Schedule DCT is the first such file.

Session 2921 (chain 153): PG&E's Schedule B-20 rows cite PG&E's own filed tariff book (`www.pge.com/tariffs/`), whose
sheets are the CPUC-filed sheets themselves ("Cal. P.U.C. Sheet No."). PG&E's site states no terms of use on its tariff
pages or in its sitemap, and its robots file is open to this reader. Whether such a book may stand public without a
commission's copy is a question for the owner (session 2921's report). Con Edison's and Eversource's sites bar
automated reading in their terms, and Duquesne Light's answers with a bot challenge: none of them was read.

Session 3847 (chain 221): New York's utilities are read from the Commission's own copy instead. The Department of Public
Service's Electronic Tariff System (`ets.dps.ny.gov`) serves each effective tariff as one PDF of its leaves. Its host has
no robots file, and the DPS's Disclaimer sets no condition on reuse, so the rows are public:
- Niagara Mohawk's S.C. No. 3A, PSC No. 220;
- NYSEG's S.C. 7-4, PSC No. 120;
- Con Edison's S.C. No. 9 Rate II, PSC No. 10.

Each file's `document_url` is the system's listing of the tariff's effective leaves, because the PDF's own address there
is a per-request token. Each page is the PDF's page, with the leaf named in `tariff_sheet`. Con Edison's demand charges
are printed by time period and summed on the bill. The registry does not sum them, so only the one charge a high tension
customer pays outside June to September is written (`demand_charge_winter`).

## The OpenEI rows

`warehouse/connectors/openei_large_load_tariffs.py` (session 670) writes the same table from OpenEI's Utility Rate
Database, under entities `openei_urdb:*`, with derived figures (an hour-weighted energy charge, an all-in figure). It
has never run: no key is held. If it runs, its rows and these merge by key and neither overwrites the other's. The
tab's builder reads both kinds; the method of each row is its source's.

## Chain 211: the owner's research file, verified row by row (sessions 3760 and 3761)

`docs/reviews/research/large-load-tariffs-2026-11-06.md` (36 tariff rows and 10 operator rules, each with its document,
page and quote) was used as leads, never as data. Each row written was read in the document it cites:
- the host's robots file first (all allowed; none names an AI agent);
- one GET a document (`runs/s3760/probe.py`, `runs/s3761/probe.py`, 36 requests in all);
- the text taken with pdftotext: the layout, and its raw order where the layout interleaves columns;
- the figure found on its page and quoted.

A figure the research file marks secondhand, or one only quoted by an intervenor or a news report, goes to the row's notes
and is not written as a figure.

**New fields and variables (session 3760).**
- `status`, written as `x_status`:
  - `adopted`: in force;
  - `ordered`: a commission ordered it, no sheet yet;
  - `proposed`: filed, pending;
  - `framework`: a statute or a set of customer-specific agreements with no rate schedule.
- `x_license` (public on every written row) and `x_notes`. The notes hold what the schedule prints that has no variable:
  demand blocks, per-kVA charges, the closed status of a schedule.
- Variables for what schedules print by season or voltage:
  - `demand_charge_summer`, `demand_charge_winter`;
  - `energy_charge_summer`, `energy_charge_winter`;
  - `grid_charge_transmission`, `grid_charge_substation` (Evergy's LLPS).

**What is held after chain 211.** 25 schedules in the registry, 24 written: the 5 of chains 147 to 157 and 20 more.
- **Adopted:** Evergy Missouri Metro and West LLPS, Ameren Missouri LLCS, Entergy Louisiana LLHLFPS-L and LPHLF-G, Entergy
  Texas LIPS, Georgia Power TOU-SC-15, SRP E-67, APS XHLF, Alabama Power LPL, Oncor Transmission Service and Rider TCRF,
  CenterPoint Houston Transmission Service, Dominion GS-4, and NV Energy LGS-X (closed to new customers).
- **Proposed:** Duke Energy Carolinas's Large Load Tariff (the settlement of 6 October 2026), Xcel Colorado Schedule TL.
- **Framework:** NV Energy's LLESA, Alabama's Act 2026-610.
- **Held internal:** AEP Ohio Schedule DCT.

**Rows that wait, and why.**
- **Dominion GS-5:** no sheet is published, and its order is on the Virginia SCC's host, which the ERW does not ask (paused).
- **Duke Energy Progress:** the settlement prints only Duke Energy Carolinas's leaf.
- **Utah:** the 100 MW threshold is in Utah Code 54-26, not read; the PSC's notice that was read states none.
- **Evergy Kansas:** its host returns a bot check.
- **APS's pending XHLF revision:** not read.
- **Xcel Colorado's full terms:** only the interim decision was read. The rest are intervenor quotes, kept in notes.
- **PUCT Project 58000:** a rule for every ERCOT TSP, held in `large_load_connection_rules`.

## Cross-checks

Each session that adds utilities checks one utility's demand charge against the revenue per kW that EIA-861 implies
for its largest class. The result is written as a check in the session's report, never as a correction to a row.

**Session 3763's check (Missouri, EIA-861 of 2025).** Each schedule's all-in price at an 80 percent load factor is set beside
the utility's 2025 industrial revenue over industrial sales (`eia861_utility_sales`).
- The all-in price is:
  - the seasons' demand charge averaged over the year, plus the transmission grid charge,
  - divided by the 584 kWh a kW takes in a month at 80 percent,
  - plus the energy charge.
- Riders, the fuel adjustment and the customer charge are left out.
- EIA-861 gives no peak by class, so a revenue per kW cannot be read directly. The comparison is per MWh.

| Utility | LLPS or LLCS all-in at 80 percent, USD/MWh | EIA-861 2025 industrial revenue over sales, USD/MWh | Difference |
|---|---|---|---|
| Evergy Missouri Metro | 67.39 | 74.31 | -9 percent |
| Evergy Missouri West | 63.90 | 62.63 | +2 percent |
| Ameren Missouri | 63.24 | 81.92 | -23 percent |

What it says:
- The large-load schedules land at or below the industrial class's average, as a high-load-factor schedule should.
- Ameren's gap is the widest. Its energy charge is printed before its fuel adjustment clause, and the industrial average
  includes that clause.
- This is a check, not a correction.
