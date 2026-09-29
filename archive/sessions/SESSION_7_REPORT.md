# Session 7 report

Energy Research Warehouse (ERW), session 7, run 2026-09-25 (UTC). Tasks 1, 3 and 4 of SESSION_7_PROMPT.md were carried out in full. Task 2 was carried out through its fifth item, (e). Items (f) and (g) are listed under "What remains", as the prompt allows when the session runs long. Nothing was pushed. No key is printed, logged or committed: a search of `warehouse/output`, `warehouse/metadata`, `warehouse/raw` and `docs` for a fragment of the EIA key found nothing, and FRED, PJM, CARB and RGGI need no key.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | The four news rulings applied, then ingest, score and brief rerun (details in the commit message and Decision 16). Nothing was re-scored: the 632 stories scored in session 6 keep their scores, so today's digest still ranks mostly by the old rubric. 23 new stories used the new one. None of the 464 Google News links resolved to the outlet (Google serves a JavaScript page, not a redirect). Each keeps its Google link and is flagged. `news_index` is public; `news_stories` stays internal | `b88ae79` |
| 2 | Four connectors, 10 new tables (below). Each one captures raw files, writes run status, registers its sources with a license, and is in `run_daily.sh` and the workflow | `56452c9` |
| 3 | 13 units added to the validator and recorded in Decision 17. A `sector` column in `coverage.csv` (Decision 18) and `erw.filter(sector=...)`. Package tests cover every new table. All 41 tables pass `erw_validate`; 189 package tests and 11 repo tests pass | `74835fc` |
| 4 | This report | final commit |

## Series now in the ERW

Ten new tables, 134,900 rows. Each was run twice; the second run added no rows (0 new, all replaced).

| Table | Series | Freq | History | Unit | License | Sector |
|---|---|---|---|---|---|---|
| `eia_product_spot_prices` | NYH and USGC conventional gasoline, LA RBOB, NYH and USGC ULSD, LA CARB diesel, USGC jet, NYH heating oil, Mont Belvieu propane (9) | P1D | 1986-06-02 to 2026-09-22 | USD/gal | public | products |
| `eia_retail_fuel_prices` | US regular gasoline, all-grades gasoline, on-highway diesel (3) | P1W | 1990-08-20 to 2026-09-21 | USD/gal | public | products |
| `eia_petroleum_trade_weekly` | Crude, product and total exports and imports, crude net imports (7) | P1W | 1990-01-05 to 2026-09-18 | kbbl/d | public | oil, products |
| `eia_petroleum_stocks_weekly` | Commercial crude, SPR, total crude, gasoline, distillate, jet, propane, total (8) | P1W | 1982-08-20 to 2026-09-18 | kbbl | public | oil, products |
| `eia_lng_exports_monthly` | LNG export volume and price for 9 terminals: Sabine Pass, Corpus Christi, Cameron, Freeport, Calcasieu Pass, Plaquemines, Cove Point, Elba Island, Golden Pass | P1M | 2013-11 to 2026-06 | MMcf, USD/Mcf | public | lng |
| `pjm_rpm_capacity_prices` | BRA clearing price, 18 LDAs, delivery years 2007/08 to 2028/29 | P1Y | 2007-06-01 to 2028-06-01 | USD/MW-day | internal | capacity |
| `carb_auction_allowance_prices` | Current and advance auction settlement price, allowances offered and sold, 56 auctions | P3M | 2012-11 to 2026-08 | USD/tCO2, count | internal | carbon |
| `rggi_auction_allowance_prices` | Clearing price, allowances offered, sold and CCR sold, 73 auctions plus 12 future-vintage auctions | P3M | 2008-09-25 to 2026-09-09 | USD/short_ton, count | internal | carbon |
| `fred_daily_spot_prices` | DCOILWTICO, DCOILBRENTEU, DHHNGSP | P1D | 1986-01-02 to 2026-09-22 | USD/bbl, USD/MMBtu | public | oil, gas |
| `fred_imf_commodity_prices` | IMF EU gas (TTF proxy), Asia LNG (JKM proxy, not JKM), Australian coal, uranium, nickel | P1M | 1992-01 to 2026-07 | USD/MMBtu, USD/t, USD/lb | internal | gas, lng, coal, uranium, metals |

The new connectors:
- `warehouse/connectors/eia_series.py`: EIA API v2, full history each run.
- `capacity_prices.py`: PJM workbook.
- `carbon_auctions.py`: the CARB PDF via pdfplumber, and the RGGI HTML table.
- `fred_series.py`: FRED graph CSV, no key.

Spot checks against the sources are in the package tests:
- PJM RTO: 2007/08 $40.80 and 2028/29 $325.00.
- RGGI: Auction 1 $3.07 and Auction 73 $37.65.
- CARB August 2026: current $32.48 and advance $32.75.

## Skipped, and why

| Item in the prompt | Status | Reason |
|---|---|---|
| (a) Regional gas hubs EIA publishes (SoCal Citygate, Algonquin) | Skipped: unconfirmed | They are ICE data that EIA republishes "with permission"; redistribution is unconfirmed. The 2018+ gas file location is also unconfirmed in docs/price-sources.md |
| (a) Mid-C, Palo Verde (same EIA/ICE files) | Skipped: unconfirmed | Same ICE rights question |
| (b) Baker Hughes rig counts | Blocked | `rigcount.bakerhughes.com` never answered: no response within 25 s with a browser or a default User-Agent, and curl hung. The file already records it as bot-protected (403). No connector was written, since one would fail every day |
| (c) ISO-NE FCA | Skipped: license | "Permission required for non-personal use" |
| (c) MISO PRA | Skipped: license | "No reproduction without permission". The results PDFs also returned 403 |
| (d) EU ETS | Skipped: unconfirmed | The file names Ember (CC-BY-4.0) but found no carbon download route. EEX file URLs are unconfirmed |
| (e) FRED retail electricity indices | Not in the file | docs/price-sources.md assigns no such series to FRED |
| (e) FRED DGASNYH, DDFUELUSGULF, GASREGW, GASDESW | Not needed | The file marks them unconfirmed, and they copy the EIA series now in `eia_product_spot_prices` and `eia_retail_fuel_prices` |
| (f) Equities and ETFs | Not started (remains) | Stopped after (e). The routes: Tiingo's free plan is "Internal Use Only" and needs a key the ERW does not have. Yahoo is personal use only and its terms forbid automated collection. Stooq is behind a JavaScript bot check. Alpha Vantage's terms are unconfirmed |
| (g) CME futures (WTI, RBOB, HO, Henry Hub curves, WTI volume, JKM) | Skipped: paid | CME-lic. EIA's copies ended 2024-04-05 |
| (g) TTF and JKM daily | Skipped: paid | ICE Endex and Platts. The monthly IMF proxies are in `fred_imf_commodity_prices` (internal) |
| (g) Uranium conversion, SWU and daily U3O8 | Skipped: paid | UxC and TradeTech |
| (g) Cameco monthly U3O8 | Skipped: unconfirmed | Cameco terms unconfirmed. FRED PURANUSDM is in instead (internal) |
| (g) Lithium hydroxide, daily carbonate | Skipped: paid | Fastmarkets, Benchmark, Trading Economics |
| (g) IMF lithium and cobalt, USGS lithium | Not started (remains) | IMF terms unconfirmed, and the lithium series code cell is blank. The USGS figure is annual, PDF only, with Benchmark as the underlying source |

## Price board coverage against docs/price-sources.md

All 63 series rows of the file. **In** means a table holds the series (or the named proxy). **Out** means it is not in the ERW, with the reason.

| Section | Series | Status | Table or reason |
|---|---|---|---|
| 1 Crude | WTI Cushing spot | In | `eia_fuel_spot_prices` (session 5), `fred_daily_spot_prices` |
| 1 | Brent spot | In | `eia_fuel_spot_prices`, `fred_daily_spot_prices` |
| 1 | WCS (Hardisty) | Out | Monthly Alberta data, outside items (a) to (g); open licence, upstream provider unconfirmed |
| 1 | Mars | Out | Monthly EIA first purchase price; item (a) asked for daily and weekly. EIA-PD, a candidate |
| 1 | Bakken (ND proxy) | Out | Same as Mars |
| 1 | WTI futures curve | Out | Paid: EIA frozen 2024-04-05; CME-lic; Yahoo-personal |
| 1 | WTI daily volume | Out | Paid: CME-lic |
| 2 Products | Gasoline spot, NY Harbor | In | `eia_product_spot_prices` |
| 2 | Gasoline spot, Gulf Coast | In | `eia_product_spot_prices` |
| 2 | RBOB spot (LA) | In | `eia_product_spot_prices` |
| 2 | Diesel (ULSD) spot, NYH, USGC, LA | In | `eia_product_spot_prices` |
| 2 | Jet fuel spot | In | `eia_product_spot_prices` |
| 2 | RBOB futures | Out | Paid: EIA frozen; CME-lic |
| 2 | Heating oil futures | Out | Paid: EIA frozen; CME-lic. NYH heating oil spot is in `eia_product_spot_prices` |
| 2 | US retail gasoline and diesel | In | `eia_retail_fuel_prices` |
| 3 Gas | Henry Hub spot | In | `eia_fuel_spot_prices`, `fred_daily_spot_prices` |
| 3 | Henry Hub futures curve | Out | Paid: EIA frozen; CME-lic |
| 3 | Waha | Out | Paid: NGI |
| 3 | SoCal Citygate | Out | Unconfirmed: ICE rights, 2018+ file location |
| 3 | Algonquin Citygates | Out | Unconfirmed: same |
| 3 | Transco Zone 6 NY | Out | Paid: NGI proprietary |
| 3 | TTF | In (proxy) | `fred_imf_commodity_prices` PNGASEUUSDM, monthly, internal |
| 3 | JKM | In (proxy) | `fred_imf_commodity_prices` PNGASJPUSDM, monthly, internal; a proxy, not JKM |
| 4 LNG | US LNG export volumes by terminal | In | `eia_lng_exports_monthly` |
| 4 | LNG cargo counts by terminal | Out | DOE PDF and xlsx, file names change monthly; terms presumed public but unconfirmed. Outside item (a), which is EIA only |
| 4 | US LNG export price by terminal | In | `eia_lng_exports_monthly` (Golden Pass has volumes but no price yet) |
| 4 | Spot or landed LNG | In (proxy) | `fred_imf_commodity_prices`, internal |
| 5 Coal, uranium | CAPP spot | Out | S&P Global proprietary; the file says internal only; undocumented JSON route. Not built: outside items (a) to (g) |
| 5 | PRB spot | Out | Same |
| 5 | Newcastle coal (context) | In | `fred_imf_commodity_prices` PCOALAUUSDM, internal |
| 5 | U3O8 spot | In | `fred_imf_commodity_prices` PURANUSDM, internal; Cameco not used (terms unconfirmed) |
| 5 | U3O8 annual contract price | Out | EIA UMAR PDF; xlsx table URLs unconfirmed (item (g), remains) |
| 5 | Conversion (UF6) | Out | Paid: TradeTech, UxC |
| 5 | Enrichment (SWU) | Out | EIA UMAR annual; table route unconfirmed (item (g), remains) |
| 6 Carbon, metals | EU ETS | Out | Unconfirmed: no Ember download route |
| 6 | California cap-and-trade | In | `carb_auction_allowance_prices`, internal |
| 6 | RGGI | In | `rggi_auction_allowance_prices`, internal |
| 6 | Carbon ETF proxy (KRBN) | Out | Yahoo-personal; item (f), remains |
| 6 | Lithium carbonate (USGS annual) | Out | PDF only, Benchmark underlying; item (g), remains |
| 6 | Lithium (IMF monthly) | Out | IMF terms unconfirmed; series code blank; item (g), remains |
| 6 | Lithium hydroxide | Out | Paid |
| 6 | Cobalt | Out | IMF terms unconfirmed; item (g), remains |
| 6 | Nickel | In | `fred_imf_commodity_prices` PNICKUSDM, internal |
| 6 | RECs and SRECs | Out | Paid or proprietary; GATS asking prices only, terms unconfirmed |
| 7 Electricity | PJM RPM BRA clearing price | In | `pjm_rpm_capacity_prices`, internal |
| 7 | ISO-NE FCA clearing price | Out | License: permission required |
| 7 | MISO PRA clearing price | Out | License: no reproduction without permission |
| 7 | Mid-C power | Out | Unconfirmed: ICE rights |
| 7 | Palo Verde power | Out | Unconfirmed: ICE rights |
| 7 | Retail rates by state and sector | Out | Outside items (a) to (g); EIA-PD, a candidate |
| 7 | Retail rates by utility | Out | Outside items (a) to (g); EIA-PD and URDB CC0, a candidate |
| 8 Flows | Strait of Hormuz transits | Out | Outside items (a) to (g); IMF PortWatch terms unconfirmed |
| 8 | Suez Canal transits | Out | Same |
| 8 | Panama Canal transits | Out | Same |
| 8 | US crude and product exports and imports, weekly | In | `eia_petroleum_trade_weekly` |
| 8 | US imports by country and company | Out | Monthly; item (a) asked for daily and weekly. EIA-PD, a candidate |
| 8 | Crude pipeline flows, PADD to PADD | Out | Monthly; a candidate |
| 8 | US gas pipeline flows | Out | Annual; a candidate |
| 8 | Canada pipeline throughput | Out | Outside items (a) to (g); OGL-Canada, a candidate |
| 9 Rigs | US and Canada rig count | Out | Blocked: the server never answered |
| 9 | International rig count | Out | Blocked: same |
| 9 | Drilling productivity | Out | STEO route unconfirmed |
| 10 Equities | Daily close for the 34 tickers | Out | Item (f), remains. See "What remains" |

**Totals:** 21 of 63 rows are in the ERW.
- 12 are public: WTI, Brent, five product spot rows, retail fuels, Henry Hub, LNG volumes, LNG prices, weekly trade.
- 9 are internal: TTF, JKM and spot LNG proxies, Newcastle coal, U3O8, CARB, RGGI, nickel, PJM capacity.
- The other 42 rows are out. Of these:
  - 12 are paid or need permission: CME futures and volume, NGI hubs, TradeTech, lithium hydroxide, RECs, ISO-NE, MISO.
  - 2 are blocked: Baker Hughes.
  - The rest have unconfirmed terms or routes, fell outside items (a) to (g), or remain from (f) and (g). The table gives each reason.

Beyond the file's rows, the ERW also gained:
- weekly petroleum stocks (asked for in item (a));
- Mont Belvieu propane spot;
- NYH heating oil spot.

## Decisions

1. **Table names.** The prompt's `capacity_prices` has two parts, but series tables need three and a publisher first. The PJM table is therefore `pjm_rpm_capacity_prices`, with the prompt's variable and `iso:zone` entities (Decision 19). ISO-NE and MISO would get their own tables with the same variable.
2. **One PJM number per LDA and delivery year:** the headline product. That is the only product to 2013/14, Annual from 2014/15 to 2017/18, and CP from 2018/19. A "**" cell (PJM: "LDA was not modeled") is omitted, never filled from the parent LDA. Incremental auctions are not included.
3. **Licenses follow docs/price-sources.md.**
   - EIA-PD and FRED "Public Domain" series are public.
   - Three groups are internal: PJM (non-members may not republish), CARB and RGGI (terms unconfirmed), and FRED "Copyrighted: Citation Required" IMF series. The last follow the prompt's rule for internal-use-only sources.
   - `fred_series.py` reads each series page's rights line and units every run, and fails if either changes.
4. **Dates.**
   - EIA: the reported date at 00:00Z, meaning the week-ending date for weekly series and the first of the month for monthly ones.
   - Auctions: the auction date, or the first of the month where CARB gives only the month. freq is P3M for carbon auctions and P1Y for capacity.
   - Dates EIA or FRED list without a value are omitted and counted in the header:
     - EIA LNG prices for months with no cargo;
     - 6 weeks of retail regular gasoline;
     - FRED holiday rows, shown as ".".
5. **Freshness.** Newest date within 10 days for daily series, 21 for weekly, 150 for monthly and quarterly. A stale table is not written. A PJM workbook whose newest delivery year starts before this year fails.
6. **The data disagrees with docs/price-sources.md once.** The file gives CARB Auction 1 (2012-11) as $11.48. CARB's own PDF gives $10.09 current and $10.00 advance; $11.48 is the February 2014 and November 2013 price. The ERW holds the PDF's numbers.
7. **Sector** is set per table by rules in `build_coverage.py`, and a table no rule matches fails the build. `erw.filter(sector=...)` raises on an unknown sector. `equities` is in the vocabulary but has no table yet.
8. **The FRED User-Agent.** FRED stalled requests sent with a browser User-Agent and answered at once with the requests default, so `fred_series.py` sends the default. The same probe got no answer at all from Baker Hughes.
9. **Requirements.** `requirements.txt` now names pdfplumber, openpyxl and lxml, which the CARB, PJM and RGGI parsers use directly. They were already installed as gridstatus dependencies.

## Errors hit

1. **RGGI:** every auction first landed under `rggi:future_auction`, because `NaN` is truthy. The merge writer's duplicate-key check refused the write. Fixed with `pd.notna` before anything was written.
2. **FRED:** the first run found no units, because the page puts them in a `series-meta-value-units` span. The run failed and wrote nothing, as intended. Fixed.
3. **Headers:** my first `Source:` lines for PJM, CARB, RGGI and FRED were free text. The erw package parses `Source: <id> <title>, <url>`, so it cited "california:Air". The package tests caught it. The headers were fixed and the tables rewritten; the skill file now states the form.
4. **Package:** `erw.filter` crashed with no sector argument (`_as_list(None)`). Caught by the tests and fixed.
5. **Commit message:** the Task 1 message says it added docs/price-sources.md, but the file was committed with Task 2 (`56452c9`).
6. **Carried from Task 1:** the pandas access violation in `update_sources` (fixed by building from dicts), a missed outlet registration, and 18 one-story scoring calls (USD 0.67), now prevented by a 25-story minimum batch.

## What remains

- **Item (f), equities and ETFs.** No compliant automated route is available today. The prompt says to build a Yahoo connector and register it internal, but Yahoo's terms also forbid automated collection. That, plus stopping after (e), is why it was not built. The best route is a Tiingo key (free plan "Internal Use Only"), stored as `TIINGO_API_KEY` in `.env` and the repository secrets.
- **Item (g):** IMF lithium and cobalt (terms), EIA UMAR uranium contract and SWU prices (table route), USGS lithium (annual PDF).
- **Out of scope but free (EIA-PD, a later session):**
  - monthly EIA series: first purchase prices (Mars, ND), imports by country, PADD pipeline flows;
  - EIA retail electricity prices by state;
  - Canada CER pipeline throughput;
  - IMF PortWatch chokepoints, if its terms are confirmed.
- **Not run:** `run_daily.sh` was not run end to end after Task 2. Each new connector was run twice on its own, then the validator, coverage and tests.

## Rerun

```bash
.venv/Scripts/python warehouse/connectors/eia_series.py       # 5 EIA tables, full history
.venv/Scripts/python warehouse/connectors/capacity_prices.py  # PJM RPM BRA (internal)
.venv/Scripts/python warehouse/connectors/carbon_auctions.py  # CARB and RGGI (internal)
.venv/Scripts/python warehouse/connectors/fred_series.py      # FRED, no key
.venv/Scripts/python warehouse/validate/erw_validate.py warehouse/output/*.csv
.venv/Scripts/python warehouse/metadata/build_coverage.py
.venv/Scripts/python -m pytest package/tests -q
PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh       # everything, as the workflow runs it
```

## Open questions for the human

1. **Equities.** Register a Tiingo key for internal daily closes? Or should the ERW build the Yahoo connector the prompt describes, although Yahoo's terms forbid automated collection?
2. **Permissions.** Ask ISO-NE (info@iso-ne.com), MISO and PJM for permission to publish capacity prices. Ask CARB and RGGI to confirm their terms, which would make those two tables public.
3. **ICE files.** Ask EIA or ICE whether the EIA-hosted ICE hub files (SoCal, Algonquin, Mid-C, Palo Verde) may be redistributed.
4. **Baker Hughes** does not answer automated requests. Accept a manually downloaded weekly file, or drop rig counts?
5. **Carried over:** fill `warehouse/news/eval/eval_sample.csv`; add the `ANTHROPIC_API_KEY` and `EIA_API_KEY` repository secrets; a PJM API key.
