# ERW Price Board: Data Source Map

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's hub prices, queue, auction results and reserve prices are not pulled. What is held stays as it is. [`miso_pause.md`](methods/miso_pause.md)

Compiled 2026-09-25. Every URL below was opened during this research, on that date, unless it is marked "not opened" or "unconfirmed". Anything we could not see on an opened page is written as "unconfirmed".

## Read this first

- **EIA futures are frozen.** EIA's NYMEX futures pages and the `petroleum/pri/fut` and `natural-gas/pri/fut` API routes end on 2024-04-05. The EIA futures page itself says "Futures prices after April 5, 2024, are not available". This covers WTI CL1-4, RBOB, heating oil and Henry Hub RNGC1-4. We found no free, redistributable source for a live futures curve.
- **CME and Yahoo show prices but restrict reuse.** CME settlements and Yahoo quotes can be viewed for free, but both sets of terms forbid redistribution. Yahoo's terms also forbid automated collection.
- **Some EIA data is vendor data.** Several EIA-hosted datasets come from vendors and carry their restrictions. The coal spot prices are S&P Global's; EIA calls them proprietary. The wholesale power and gas hub prices are ICE data, republished by EIA "with permission".
- **The EIA API needs a real key.** EIA's `DEMO_KEY` hit its rate limit (HTTP 429) within a few calls. Any EIA API route below that was not seen returning data is marked unconfirmed. The build needs a free registered key. JSON calls return at most 5,000 rows.
- **What "Fits ERW" means here.** The ERW series schema is not in this folder. "Fits ERW" in the tables therefore assumes the shape is one numeric value per series per period (date, value, unit):
  - **Yes**: the data already has that shape.
  - **Derive**: filtering, pivoting or parsing gives that shape.
  - **No**: the data is a curve snapshot, a tariff, or a listing.

License shorthand used in the tables:

| Short form | Meaning | Terms URL |
|---|---|---|
| EIA-PD | Public domain, credit requested ("Source: U.S. Energy Information Administration") | https://www.eia.gov/about/copyrights_reuse.php |
| FRED-PD | FRED series marked "Public Domain: Citation Requested" | https://fred.stlouisfed.org/legal/ |
| FRED-3P | Third-party series on FRED. Cite the source; non-personal use requires contacting the owner | https://fred.stlouisfed.org/legal/ |
| CME-lic | Website terms: "not to sell, copy, distribute, or create derivative works". Redistribution needs a paid license | https://www.cmegroup.com/tools-information/cme-website-terms-of-use.html and https://www.cmegroup.com/market-data/license-data.html |
| Yahoo-personal | No commercial use, no redistribution, no automated collection | https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html |

## 1. Crude oil

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| WTI Cushing spot | EIA spot prices, series RWTC: https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm | FRED DCOILWTICO: https://fred.stlouisfed.org/series/DCOILWTICO | Daily | 1986-01-02 | XLS https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_D.xls; single series https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls; API `/v2/petroleum/pri/spt/data/?frequency=daily&data[0]=value&facets[series][]=RWTC` (route metadata seen, data call unconfirmed) | EIA-PD. FRED copy shows "copyrighted", exact status unconfirmed | Yes |
| Brent spot | EIA series RBRTE, same page | FRED DCOILBRENTEU: https://fred.stlouisfed.org/series/DCOILBRENTEU | Daily | 1987-05-20 | Same XLS; API facet series=RBRTE (data call unconfirmed); FRED text https://fred.stlouisfed.org/data/DCOILBRENTEU.txt | EIA-PD; FRED-PD | Yes |
| WCS (Hardisty) | Government of Alberta economic data API: https://api.economicdata.alberta.ca/data?table=OilPrices&Type=WCS;WTI (seen working) | open.alberta.ca Energy Prices CSV (link seen, not downloaded): https://open.alberta.ca/dataset/6dc97b50-5bbb-482d-8dd5-c9b23cd770dc/resource/05caae97-5ccb-43d5-8c31-a59ec86df2f2/download/energyprices.csv | Monthly | 2005-01 | JSON rows of Date/Type/Unit/Value | Open Government Licence - Alberta, attribution required: https://open.alberta.ca/licence. Upstream WCS provider unconfirmed | Derive (filter Type=WCS) |
| Mars | EIA first purchase price, series F003075793: https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm | Argus Mars daily (not opened, unconfirmed) | Monthly, about 3-month lag | 2004-01 | XLS PET_PRI_DFP2_K_M.xls (link seen, not downloaded) | EIA-PD | Yes |
| Bakken | EIA North Dakota first purchase price, F002038__3. This is a state average and a proxy for Bakken: https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=F002038__3&f=M | No free daily Bakken found. The ND Pipeline Authority page returned 404 | Monthly | 1977-07 | Same leaf page (XLS link) | EIA-PD | Yes (proxy) |
| WTI futures curve (CL1-4+) | EIA RCLC1-4: https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm. Frozen at 2024-04-05 | CME settlements, full strip (viewed in browser): https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.settlements.html; Yahoo CL=F and single months such as CLZ26.NYM | Daily | EIA 1983 to 2024-04-05. CME shows the latest trade date only. Yahoo CL=F from 2000-09-01 | EIA XLS https://www.eia.gov/dnav/pet/xls/PET_PRI_FUT_S1_D.xls. CME page loads undocumented JSON `/CmeWS/mvc/Settlements/Futures/Settlements/425/FUT`. Yahoo undocumented `query1.finance.yahoo.com/v8/finance/chart/CL=F` | EIA-PD (stale); CME-lic; Yahoo-personal | Yes per contract month; No as a curve snapshot |
| WTI daily volume | CME volume and open interest page: https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.volume.html (about 7 trade dates shown) | Yahoo CL=F volume field | Daily | About 7 days on the page. Deeper history via CME DataMine (paid, datasets from 1972): https://www.cmegroup.com/datamine.html | CME page loads undocumented `/CmeWS/mvc/Volume/Details/F/425/{yyyymmdd}/F` | CME-lic; Yahoo-personal | Yes |

## 2. Refined products

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| Gasoline spot, NY Harbor | EIA EER_EPMRU_PF4_Y35NY_DPG (conventional regular): https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm | FRED DGASNYH (CSV fetch timed out, unconfirmed) | Daily | 1986 | Spot XLS above; API `petroleum/pri/spt` facet series (data call unconfirmed) | EIA-PD | Yes |
| Gasoline spot, Gulf Coast | EIA EER_EPMRU_PF4_RGC_DPG, same page | None verified | Daily | 1986 | Same | EIA-PD | Yes |
| RBOB spot | EIA EER_EPMRR_PF4_Y05LA_DPG (Los Angeles only; the page has no NYH RBOB spot) | None verified | Daily | 2003 | Same | EIA-PD | Yes |
| Diesel (ULSD) spot | EIA ULSD spot, same page: NYH EER_EPD2DXL0_PF4_Y35NY_DPG; USGC EER_EPD2DXL0_PF4_RGC_DPG; LA EER_EPD2DC_PF4_Y05LA_DPG | FRED DDFUELUSGULF (unconfirmed) | Daily | NYH/USGC 2006; LA 1996 | Same | EIA-PD | Yes |
| Jet fuel spot | EIA EER_EPJK_PF4_RGC_DPG (Gulf Coast), same page | None verified | Daily | 1990 | Same | EIA-PD | Yes |
| RBOB futures | EIA EER_EPMRR_PE1..PE4_Y35NY_DPG, frozen at 2024-04-05 | CME settlements (viewed): https://www.cmegroup.com/markets/energy/refined-products/rbob-gasoline.settlements.html; Yahoo RB=F | Daily | EIA 2005 to 2024-04-05 | EIA futures XLS; CME JSON `.../Settlements/429/FUT` (undocumented) | EIA-PD (stale); CME-lic; Yahoo-personal | Yes per contract |
| Heating oil / NYH ULSD futures | EIA EER_EPD2F_PE1..PE4_Y35NY_DPG, frozen at 2024-04-05 | CME settlements (viewed): https://www.cmegroup.com/markets/energy/refined-products/heating-oil.settlements.html; Yahoo HO=F | Daily | EIA 1980 to 2024-04-05 | EIA futures XLS; CME JSON `.../Settlements/426/FUT` | Same as RBOB | Yes per contract |
| US retail gasoline and diesel | EIA weekly retail: https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_nus_w.htm (EMM_EPMR_PTE_NUS_DPG, EMM_EPM0_PTE_NUS_DPG, EMD_EPD2D_PTE_NUS_DPG) | FRED GASREGW / GASDESW (unconfirmed) | Weekly | Regular 1990; diesel 1994 | XLS https://www.eia.gov/dnav/pet/xls/PET_PRI_GND_DCUS_NUS_W.xls; API `petroleum/pri/gnd` (unconfirmed) | EIA-PD | Yes |

## 3. Natural gas

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| Henry Hub spot | EIA RNGWHHD: https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm | FRED DHHNGSP: https://fred.stlouisfed.org/series/DHHNGSP | Daily | 1997-01-07 | XLS https://www.eia.gov/dnav/ng/xls/NG_PRI_FUT_S1_D.xls; API `/v2/natural-gas/pri/fut/data/?frequency=daily&data[0]=value&facets[series][]=RNGWHHD` (route seen working, filtered call unconfirmed); FRED CSV https://fred.stlouisfed.org/graph/fredgraph.csv?id=DHHNGSP | EIA-PD; FRED-PD | Yes |
| Henry Hub futures curve | EIA RNGC1-4, same page, frozen at 2024-04-05 | CME settlements (viewed; OCT 26 to SEP 27 shown, "LOAD ALL" for more): https://www.cmegroup.com/markets/energy/natural-gas/natural-gas.settlements.html; Yahoo NG=F (front month) | Daily | EIA 1993/94 to 2024-04-05 | EIA API route above (unfiltered call seen returning RNGC1 rows) | EIA-PD (stale); CME-lic; Yahoo-personal | Yes per contract |
| Waha | No free source found. NGI Daily Datafeed (paid): https://naturalgasintel.com/services/daily-datafeed/ | NGI free Waha snapshot page (numbers not readable): https://naturalgasintel.com/data-snapshot/daily/WTXWAHA/ | Daily | unconfirmed | NGI API with subscription | Paid | Yes if licensed |
| SoCal Citygate | EIA wholesale market data (ICE, republished with permission): https://www.eia.gov/electricity/wholesale/ | NGI (paid) | Daily trade dates, file updated biweekly | Gas hubs from 2014-03 | https://www.eia.gov/electricity/wholesale/xls/ice_electric-2026.xlsx; gas archives xls/archive/ice_natgas-2014final.xls to ice_natgas-2017final.xlsx. 2018+ gas file location unconfirmed | EIA credit plus ICE rights; redistribution unconfirmed | Derive (filter hub, weighted avg) |
| Algonquin Citygates | EIA wholesale market data, same files | NGI (paid) | Same | 2014-03 | Same | Same | Derive |
| Transco Zone 6 NY | Not in the EIA/ICE files. Cited as NGI data in the EIA Natural Gas Weekly Update: https://www.eia.gov/naturalgas/weekly/ | NGI (paid) | Weekly narrative | n/a | None | NGI proprietary | No |
| TTF | FRED PNGASEUUSDM (IMF, EU gas, $/MMBtu): https://fred.stlouisfed.org/series/PNGASEUUSDM | Yahoo TTF=F (daily, EUR/MWh); ICE Endex Dutch TTF (paid report packages): https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures and https://www.ice.com/report/10 | Monthly (FRED) | 1992-01 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASEUUSDM | FRED-3P (IMF "reprinted with permission"; IMF terms page 403, unconfirmed) | Yes |
| JKM | FRED PNGASJPUSDM (IMF "Global price of LNG, Asia"; a proxy, not JKM): https://fred.stlouisfed.org/series/PNGASJPUSDM | CME JKM (Platts) futures: https://www.cmegroup.com/markets/energy/natural-gas/lng-japan-korea-marker-platts-swap.html | Monthly (FRED) | 1992-01 | https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASJPUSDM | FRED-3P; CME-lic | Yes (proxy) |

## 4. LNG

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| US LNG export volumes by terminal | EIA Exports by Point of Exit: https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENG_Mmcf_m.htm. Covers Sabine Pass, Corpus Christi, Cameron, Freeport, Calcasieu Pass, Plaquemines, Cove Point, Elba Island, Golden Pass | DOE Natural Gas Imports and Exports Monthly (through Jul 2026, fresher): https://www.energy.gov/hgeo/articles/natural-gas-imports-and-exports-monthly-2026 | Monthly | Freeport 2013, Sabine 2016, later terminals from their start dates | XLS https://www.eia.gov/dnav/ng/xls/NG_MOVE_POE2_A_EPG0_ENG_MMCF_M.xls; API `natural-gas/move/poe2` (unconfirmed); DOE xlsx filenames change monthly | EIA-PD; DOE terms page not opened (US government, presumed public domain, unconfirmed) | Yes per terminal |
| LNG cargo counts by terminal | DOE monthly report, table 2a "No. of Cargos": e.g. https://www.energy.gov/sites/default/files/2026-03/Natural%20Gas%20Imports%20and%20Exports%20Monthly%20January%202026_0.pdf | DOE details xlsx "3. U.S. LNG Exports and Re-Exports Details (Jan 2016 - Jul 2026).xlsx" (cargo-level, unconfirmed). The old LNG Monthly ended 2023-11: https://www.energy.gov/fecm/listings/lng-reports | Monthly | 2016 (details xlsx) | PDF/xlsx on the DOE listing page https://www.energy.gov/hgeo/listings/natural-gas-imports-and-exports-monthly-reports | Presumed public domain (unconfirmed) | Derive (count by terminal) |
| US LNG export price by terminal | EIA: https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_PNG_DpMcf_m.htm ($/Mcf) | DOE monthly PDF table 13a ($/MMBtu) | Monthly | Terminal start dates | XLS from the same page | EIA-PD | Yes |
| Spot or landed LNG (Asia, Europe) | No free daily source. Best proxy is FRED PNGASJPUSDM / PNGASEUUSDM (monthly) | CME JKM (CME-lic). The Platts page (spglobal.com) returned 403, so it is unconfirmed as paid | Monthly | 1992 | As TTF/JKM rows | FRED-3P | Yes (proxy) |

## 5. Coal and uranium

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| CAPP spot (12,500 Btu, 1.2 SO2) | EIA Coal Markets: https://www.eia.gov/coal/markets/ ("With permission, S&P Global") | CME CSX coal futures are delisted (search snippet only; the CME page timed out) | Weekly | 2011-01-07 | Undocumented JSON (seen working): https://www.eia.gov/coal/markets/coal_markets_archive_json.php, key CENTRAL_APP in `snl_dpst` ($/st) and `snl_mmbtu` | S&P Global proprietary. EIA says it "cannot release" the history. Internal only | Yes |
| PRB spot (8,800 Btu, 0.8 SO2) | Same page and JSON, key POWDER_RIVER_BASIN | Old NYMEX western rail block in the same JSON (2004 to 2018-11) | Weekly | 2011-01-07 | Same | Same | Yes |
| Global thermal coal (Newcastle), context | FRED PCOALAUUSDM (IMF): https://fred.stlouisfed.org/series/PCOALAUUSDM | IMF external-data.xlsx column PCOALAU | Monthly | 1980-01 (IMF) | fredgraph.csv?id=PCOALAUUSDM | FRED-3P | Yes |
| U3O8 spot | Cameco (average of UxC and TradeTech month-end): https://www.cameco.com/invest/markets/uranium-price | FRED PURANUSDM (IMF/NUEXCO): https://fred.stlouisfed.org/series/PURANUSDM; CME UxC futures (not opened) | Monthly | Cameco 1988-01; FRED 1992-01; IMF xlsx 1980-01 | Cameco HTML table only; https://fred.stlouisfed.org/graph/fredgraph.csv?id=PURANUSDM | Cameco terms unconfirmed; FRED-3P | Yes |
| U3O8 annual contract price | EIA Uranium Marketing Annual Report: https://www.eia.gov/uranium/marketing/ | none | Annual | 1992 to 2025 | PDF /uranium/marketing/pdf/umar.pdf; xlsx table URLs unconfirmed | EIA-PD | Yes |
| Conversion (UF6) | No free series. TradeTech indicators need a login: https://www.uranium.info/ | UxC (paid): https://www.uxc.com/p/data/cme | Weekly/monthly (TradeTech) | unconfirmed | None | Paid: https://www.uranium.info/copyright_and_disclaimer.php | Yes if licensed |
| Enrichment (SWU) | EIA UMAR annual SWU price ($108.70/SWU for 2025): https://www.eia.gov/uranium/marketing/ | TradeTech, UxC (paid) | Annual (EIA) | unconfirmed | UMAR tables | EIA-PD | Yes |

## 6. Carbon, battery metals, RECs

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| EU ETS (EUA) | Ember European electricity prices tool (includes EU and UK ETS front-month; the carbon-price-viewer URL now points there, unconfirmed): https://ember-energy.org/data/carbon-price-viewer/ | EEX primary auction reports and a 2012-2025 zip: https://www.eex.com/en/markets/environmental-markets/eu-ets-auctions; ICE EUA futures (no data shown): https://www.ice.com/products/197/EUA-Futures/data | Daily (Ember) | unconfirmed | No carbon CSV route found. EEX file URLs unconfirmed | Ember CC-BY-4.0 (site footer); EEX terms unconfirmed | Yes if a route is found |
| California cap-and-trade | CARB auction information: https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information | CARB results summary PDF: https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf | Quarterly | Auction 1, 2012-11 ($11.48) | PDF only, needs parsing | State government, terms unconfirmed | Derive (current and advance prices) |
| RGGI | RGGI prices and volumes: https://www.rggi.org/auctions/auction-results/prices-volumes | RGGI auction results index: https://www.rggi.org/auctions/auction-results | Quarterly | Auction 1, 2008-09-25 ($3.07) to Auction 73, 2026-09-09 ($37.65) | HTML table; no CSV link seen | "(c) RGGI 2026", license unconfirmed | Yes |
| Carbon ETF proxy | KRBN on Yahoo: https://finance.yahoo.com/quote/KRBN/ | none | Daily | unconfirmed | Undocumented chart endpoint | Yahoo-personal | Yes (proxy) |
| Lithium carbonate | USGS MCS 2026 annual battery-grade price (source Benchmark): https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-lithium.pdf | Trading Economics daily China carbonate (CNY/t, API paid): https://tradingeconomics.com/commodity/lithium | Annual (USGS) | 2021 to 2025e in MCS 2026 | PDF only | USGS public domain, but Benchmark is the underlying source | Yes (annual) |
| Lithium (metal, battery grade) | IMF Primary Commodity Prices: https://www.imf.org/en/Research/commodity-prices | IMF data portal: https://data.imf.org/en/datasets/IMF.RES:PCPS | Monthly | 2012-06 | https://www.imf.org/-/media/files/research/commodityprices/monthly/external-data.xlsx (series code cell blank, unconfirmed) | IMF terms page 403, unconfirmed | Yes |
| Lithium hydroxide | No free series found. USGS MCS text gives 2025 China spot of about $10,300 to $11,200/t | LME and CME hydroxide contracts (pages 403 or timed out, unconfirmed) | n/a | n/a | None | Paid (Fastmarkets, not opened) | No |
| Cobalt | IMF PCOBA (LME spot) in external-data.xlsx | FRED has no cobalt series (PCOBAUSDM is 404) | Monthly | 1981-01 | IMF xlsx above | IMF terms unconfirmed | Yes |
| Nickel | FRED PNICKUSDM (IMF, LME): https://fred.stlouisfed.org/series/PNICKUSDM | IMF PNICK in external-data.xlsx (from 1980-01) | Monthly | 1992-01 (FRED) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNICKUSDM | FRED-3P ("Copyrighted: Citation Required") | Yes |
| RECs and SRECs | No free price time series found. PJM-GATS REC bulletin board (asking prices, CSV export): https://gats.pjm-eis.com/gats2/PublicReports/BulletinBoard/RECs | LBNL RPS status report charts (Marex data): https://eta-publications.lbl.gov/sites/default/files/lbnl_rps_ces_status_report_2024_edition.pdf; Xpansiv (paid): https://ms.xpansiv.com/markets/rps/srec/new_jersey | Irregular | n/a | GATS CSV export (offers, not trades) | GATS terms unconfirmed; Marex/Xpansiv proprietary | No |

## 7. Electricity: capacity, non-ISO hubs, retail

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| PJM RPM BRA clearing price | PJM clearing price summary XLSX, linked from https://www.pjm.com/markets-and-operations/rpm | Per-auction BRA results XLSX/PDF on the same page | Annual BRA per delivery year, plus incremental auctions | DY 2007/08 ($40.80/MW-day RTO) to DY 2028/29 ($325.00) | https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/rpm-auctions-resource-clearing-price-summary.xlsx; no Data Miner feed found (unconfirmed) | Data Miner terms: non-members "prohibited from republishing". Internal only: https://www.pjm.com/-/media/DotCom/etools/edatafeed/data-license-agreement-edata-feed-data-miner-2.ashx | Derive (RTO or LDA per delivery year) |
| ISO-NE FCA clearing price | ISO-NE key stats, markets: https://www.iso-ne.com/about/key-stats/markets | FCM page: https://www.iso-ne.com/markets-operations/markets/forward-capacity-market | Annual | FCA 1 (CCP 2010/11) to FCA 18 (CCP 2027/28). FCA 19 replaced by a prompt auction for CCP from 2028-06 | No API seen (unconfirmed) | Permission required for non-personal use: https://www.iso-ne.com/legal-privacy | Derive (per CCP) |
| MISO PRA clearing price | MISO news release for PY 2026/27: https://www.misoenergy.org/meet-miso/media-center/2026---news-releases/misos-planning-resource-auction-shows-sufficient-capacity-for-coming-year | Results posting PDFs on cdn.misoenergy.org (fetch returned 403, unconfirmed) | Annual auction, 4 seasons by zone | Start year unconfirmed | PDF only | No reproduction without permission: https://www.misoenergy.org/meet-miso/legal-and-privacy/ | Derive (season x zone) |
| Mid-C power | EIA wholesale market data (ICE day-ahead peak): https://www.eia.gov/electricity/wholesale/ | ICE Mid-C DA peak future (paid): https://www.ice.com/products/6590351/Mid-Columbia-Day-Ahead-Peak-Fixed-Price-Future; EIA Today in Energy prices (SNL, display only): https://www.eia.gov/todayinenergy/prices.php | Daily trade dates, file updated biweekly | 2001 | https://www.eia.gov/electricity/wholesale/xls/ice_electric-2026.xlsx; https://www.eia.gov/electricity/wholesale/xls/archive/ice_electric-historical.zip. No EIA API route | EIA credit plus ICE rights; redistribution unconfirmed | Derive (filter hub, weighted avg, peak only) |
| Palo Verde power | Same EIA files | ICE Palo Verde future (product 6590378, search result only) | Same | 2001 | Same | Same | Derive |
| Retail rates by state and sector | EIA API retail-sales (tested working): `https://api.eia.gov/v2/electricity/retail-sales/data/?frequency=monthly&data[0]=price` with facets stateid and sectorid | EPM Table 5.6.A: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a | Monthly | Start unconfirmed; latest 2026-07 | API above, cents/kWh | EIA-PD | Yes |
| Retail rates by utility | EIA-861 annual (revenue / sales gives price): https://www.eia.gov/electricity/data/eia861/ | EIA-861M monthly: https://www.eia.gov/electricity/data/eia861m/; OpenEI URDB tariffs (CC0): https://apps.openei.org/services/doc/rest/util_rates/ | Annual (861), monthly (861M) | 1990 to 2024 final, 2025 early release | https://www.eia.gov/electricity/data/eia861/zip/f8612024.zip; URDB `https://api.openei.org/utility_rates` or https://openei.org/apps/USURDB/download/usurdb.csv.gz | EIA-PD; URDB CC0 (https://openei.org/wiki/Utility_Rate_Database) | Derive (861); No (URDB tariffs) |

## 8. Chokepoints and flows

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| Strait of Hormuz tanker transits | IMF PortWatch daily chokepoints (ArcGIS FeatureServer, tested) | EIA Today in Energy on Hormuz oil flows (Vortexa, annual/quarterly): https://www.eia.gov/todayinenergy/detail.php?id=65504 | Daily | 2019-01-01 | `https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query?where=portname='Strait of Hormuz'&outFields=*&f=json`, field n_tanker, 1,000 rows per call | Citation "IMF PortWatch". IMF terms page 403, commercial reuse unconfirmed | Yes |
| Suez Canal transits | IMF PortWatch, same route, portname 'Suez Canal' | Suez Canal Authority navigation statistics (report pickers, no API): suezcanal.gov.eg NavigationStatistics.aspx | Daily | 2019 (unconfirmed per canal) | Same | Same | Yes |
| Panama Canal transits | IMF PortWatch, same route, portname 'Panama Canal' | Panama Canal Authority monthly operations PDFs (downloaded, unreadable): https://pancanal.com/wp-content/uploads/2026/01/ADV-01-2026-Monthly-Canal-Operations-Summary-December-2025.pdf | Daily | 2019 (unconfirmed) | Same | Same | Yes |
| US crude and product exports/imports, weekly | EIA API petroleum/move/wkly (tested working) | WPSR tables: https://www.eia.gov/petroleum/supply/weekly/ | Weekly | 1982-08-20 | `https://api.eia.gov/v2/petroleum/move/wkly/data/?frequency=weekly&data[0]=value&facets[process][]=EEX` (series WCREXUS2 crude exports, WRPEXUS2 product exports) | EIA-PD; API terms allow redistribution with EIA credit: https://www.eia.gov/opendata/terms-of-service.php | Yes |
| US imports by country and company | EIA imports by country: https://www.eia.gov/dnav/pet/pet_move_impcus_a2_nus_ep00_im0_mbbl_m.htm | EIA company-level imports: https://www.eia.gov/petroleum/imports/companylevel/; Census trade API `/data/timeseries/intltrade/imports/hs` (key required) | Monthly | 1981 (country); 1986 (company) | XLS PET_MOVE_IMPCUS_A2_NUS_EP00_IM0_MBBL_M.xls; `/petroleum/imports/companylevel/archive/[YEAR]/[YEAR]_[MONTH]/data/import.xlsx`; API `petroleum/move/impcus` (unconfirmed) | EIA-PD; Census terms unconfirmed | Yes (country); Derive (company) |
| Crude pipeline flows, PADD to PADD | EIA API petroleum/move/ptb (metadata tested) | Web table: https://www.eia.gov/dnav/pet/pet_move_ptb_dc_R10-R20_mbbl_m.htm | Monthly | 1986-01 | `/v2/petroleum/move/ptb/data/` | EIA-PD | Yes |
| US gas pipeline flows | EIA interstate movements by state: https://www.eia.gov/dnav/ng/ng_move_ist_a2dcu_nus_a.htm | EIA state-to-state capacity: https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity.xlsx. Daily flows are on each pipeline's informational postings (18 CFR 284.13): https://www.law.cornell.edu/cfr/text/18/284.13 | Annual (EIA) | 1979 | XLS from the page | EIA-PD; pipeline posting terms vary (unconfirmed) | Yes (annual) |
| Canada pipeline throughput (Keystone, Trans Mountain, Mainline) | Canada Energy Regulator open data: https://open.canada.ca/data/en/dataset/dc343c43-a592-4a27-8ee7-c77df56afb34 | Kpler (paid, no free tier): kpler.com | Monthly (oil), daily (gas), published quarterly | 2006 (Keystone 2010-07) | https://www.cer-rec.gc.ca/open/energy/throughput-capacity/keystone-throughput-and-capacity.csv | Open Government Licence - Canada, attribution required | Derive (filter key point) |

## 9. Rigs and drilling

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| US and Canada rig count (oil, gas, total, by basin) | Baker Hughes North America: https://rigcount.bakerhughes.com/na-rig-count | Enverus daily US rig count (view only): https://www.enverus.com/dailyrigcount/ | Weekly, Friday | 2000 (pivot archive) | XLSX under `/static-files/{id}`; the id changes each release, so scrape the page for the link. Bot-protected: WebFetch/curl got 403 | Attribution required ("BH and this website are cited as the source"): https://rigcount.bakerhughes.com/rig-count-faqs | Derive (pivot) |
| International rig count | Baker Hughes worldwide: https://rigcount.bakerhughes.com/intl-rig-count | none | Monthly | 2007-01 (archive) | Same pattern | Same | Derive |
| Drilling productivity (new-well production, DUCs) | EIA STEO data tables (the DPR moved there on 2024-06-11): https://www.eia.gov/petroleum/drilling/ | STEO browser: https://www.eia.gov/outlooks/steo/data/browser/ | Monthly | unconfirmed | STEO tables; API route unconfirmed | EIA-PD | Yes |

## 10. Energy equities and ETFs

All 34 tickers below were confirmed live on 2026-09-25 via Nasdaq's quote endpoint. That endpoint is undocumented, its terms are unknown, and it was used only as a check, not as a feed.

| Group | Tickers |
|---|---|
| Majors | XOM, CVX, COP, OXY |
| Midstream | KMI, WMB, ET, EPD, OKE, LNG |
| Utilities | NEE, DUK, SO, D, AEP |
| IPPs | VST, CEG, NRG, TLN |
| Uranium | CCJ, UEC, NXE (stocks); URA, URNM (ETFs) |
| Solar | FSLR, ENPH, NXT (now "Nextpower Inc."); TAN (ETF) |
| Sector ETFs | XLE, XOP, XLU (SPDR), AMLP, ICLN, OIH |

| Series | Best free source | Alternative | Freq | History | API or file route | License | Fits ERW |
|---|---|---|---|---|---|---|---|
| Daily close for the list above | Tiingo free tier (50 req/hour, 1,000/day, 500 symbols a month): https://www.tiingo.com/about/pricing | Alpha Vantage free tier (25 req/day): https://www.alphavantage.co/premium/; Yahoo (Yahoo-personal); Stooq CSV https://stooq.com/q/d/l/?s=xom.us&i=d (blocked by a JavaScript bot check) | Daily | 30+ years (Tiingo) | Tiingo EOD API (exact route not opened, unconfirmed) | Tiingo free plan is "Internal Use Only"; Alpha Vantage terms PDF unparsed, unconfirmed | Yes |

## Source ranking: board coverage per connector

Counts are the rows above (63 series rows in sections 1 to 10; counts are approximate) where the connector is the best or alternative source. Coverage does not mean the data can be redistributed.

| Rank | Connector | Coverage |
|---|---|---|
| 1 | EIA (API v2 plus dnav XLS) | About 32 rows: WTI, Brent, Mars and Bakken proxies, all product spots, retail fuels, Henry Hub spot, LNG by terminal and price, SoCal and Algonquin, Mid-C and Palo Verde, CAPP and PRB (restricted), uranium annual and SWU, retail power by state and utility, weekly trade, imports, PADD pipeline, gas flows, drilling. Futures are frozen at 2024-04-05. One connector plus one XLS scraper for the ICE wholesale and coal JSON files |
| 2 | CME Group | 7 rows: WTI curve and volume, RBOB, HO, Henry Hub curve, JKM, plus uranium and coal context. The only live futures source; it needs a license (DataMine or a distribution license) |
| 3 | ICE | 6 rows: TTF, EUA, Mid-C and Palo Verde futures, plus the ICE hub data EIA republishes. Paid for direct access |
| 4 | FRED (plus the IMF external-data.xlsx behind it) | 10 rows: WTI, Brent, Henry Hub (public domain); TTF and Asia LNG proxies, Newcastle coal, uranium, nickel, and IMF lithium and cobalt (third-party, citation required). The best free route for global monthly prices |
| 5 | Yahoo Finance | 8 rows: CL=F, BZ=F, RB=F, HO=F, NG=F, TTF=F, KRBN, all equities. Personal use only. Development fallback, not a production feed |
| 6 | Baker Hughes | 2 rows: NA and international rig counts. Attribution required |
| 7 | IMF PortWatch | 3 rows: Hormuz, Suez, Panama. One ArcGIS route |
| 8 | DOE FECM/HGEO LNG reports | 2 rows: cargo counts and the fresher terminal volumes |
| 9 | Single-series publishers | One or two rows each: Alberta (WCS), CER (Canada pipelines), RGGI, CARB, PJM, ISO-NE, MISO, Cameco, OpenEI URDB, Ember, Tiingo |

## Paid-only series and the cheapest route found

Prices are not shown on any page we opened, so costs are unconfirmed.

| Series | Why it is paid | Cheapest route seen |
|---|---|---|
| Live WTI, RBOB, HO, Henry Hub curves and WTI volume | EIA frozen since 2024-04-05; CME terms bar redistribution | CME DataMine self-service history (https://www.cmegroup.com/datamine.html). For live display, a CME license (https://www.cmegroup.com/market-data/license-data.html). Internal-only stopgap: Yahoo CL=F and single months |
| Waha, Transco Z6 NY, other regional gas hubs | NGI or ICE data | NGI Daily Datafeed subscription (https://naturalgasintel.com/services/daily-datafeed/). SoCal and Algonquin are partly covered by the EIA/ICE files |
| TTF and JKM daily | ICE Endex and Platts | ICE end-of-day CSV report packages (https://www.ice.com/report/10). Free monthly proxy: FRED IMF series |
| CAPP and PRB weekly spot | S&P Global proprietary | Ask S&P Global for permission to publish the EIA-hosted series (vendor not opened) |
| Uranium conversion and SWU, daily/weekly U3O8 | UxC and TradeTech | TradeTech subscription (https://www.uranium.info/). Free: Cameco monthly spot, EIA annual SWU |
| Lithium hydroxide, daily lithium carbonate | Fastmarkets, Benchmark (not opened) | Trading Economics API (paid; it has daily China carbonate). Free: IMF monthly lithium, USGS annual |
| EUA daily with redistribution | ICE / EEX | Ember CC-BY-4.0 if a carbon download route exists (unconfirmed) |
| REC and SREC prices | Marex, Xpansiv | Xpansiv market data (not priced). Free: PJM-GATS asking prices |
| Mid-C, Palo Verde futures | ICE | ICE data subscription. Free: EIA/ICE day-ahead files |
| Capacity prices for public display | PJM, ISO-NE and MISO terms bar republication by non-members | Written permission from each ISO (free to request; ISO-NE via info@iso-ne.com) |
| Equities with public display rights | Tiingo free is internal only; Yahoo personal only | Tiingo paid redistribution tier (price not listed) |
| Daily pipeline flows, tanker tracking | Kpler; Genscape page 404 | Scrape individual interstate pipeline informational postings (free, terms per pipeline) |

## Already in the ERW

The ERW codebase is not in this folder. This list comes from the task brief and has not been checked against the warehouse.

| Series | Status per brief | Source mapping and notes from this research |
|---|---|---|
| ISO hub prices (the seven ISOs) | In ERW | Mid-C and Palo Verde from the EIA/ICE files would extend coverage west. The same files also carry SP15, NP15, Mass Hub, PJM West and Indiana peak |
| EIA-930 (hourly grid operations) | In ERW | Same EIA API key as the new EIA rows. The API lists it under `electricity/rto` |
| Henry Hub | In ERW | Spot RNGWHHD is current. If ERW also holds RNGC1-4, those stopped updating on 2024-04-05 |
| WTI | In ERW | Spot RWTC is current. RCLC1-4 futures stopped on 2024-04-05 |
| Brent | In ERW | Spot RBRTE is current via EIA and FRED DCOILBRENTEU |
