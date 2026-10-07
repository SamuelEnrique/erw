# Related open energy data projects: notes for the paper outline

Read on 7 October 2026 (UTC). Each entry says what the project covers, in what format and under what licence, whether it has a written data standard and an automated validator, how it is versioned and cited, how often it updates, and what it does not do. Each fact carries the address it came from. "Verified today" means the page or file at that address was downloaded and its text read on 7 October 2026. Where a page could not be read, the entry says "not read" and what was tried. Quotation marks hold the source's own words, with link markup and emphasis marks removed and curly quotation marks written as straight ones. Numbers computed here from a downloaded file are marked "computed from the file". The downloaded copies behind this file were kept in a session scratch folder, not in the repository, so each fact is traced by its address and the read date, not by a saved file.

"ERW" below is the Energy Research Warehouse (this repository). Lines that begin "Beyond a small student warehouse" state what a project does that the ERW does not, as a fact about the project.

## 1. Summary table

| Project | Covers | Format, licence | Written standard, automated validator | Versioning, citation | Updates | Does not do |
|---|---|---|---|---|---|---|
| PUDL (Catalyst Cooperative) | US federal filings: EIA 860, 861, 923, 930, FERC 1, 714, EQR, EPA CEMS, others | Parquet, DuckDB, SQLite (ending 2027); code MIT, data CC-BY-4.0 | Naming conventions in the docs; a dbt project of data tests; pytest | Calendar versions (v2026.9.0); Zenodo DOI for data releases; a DOI for each raw input archive | Nightly builds; versioned releases described as quarterly | Its source list has no ISO price feeds, no interconnection queues, no large-load requests |
| gridstatus (library) | Live and recent data from 9 ISOs or grids plus EIA | Python library returning tables; BSD-3-Clause | No cross-source standard: "Minimally processed data" | Library releases (v0.36.0); no dataset to cite | On call: fetches from the source | Stores no history of its own |
| Grid Status (hosted) | The same sources, stored | REST API; "free and paid plans" | "consistent column names, timestamp formats, and DST handling" | API key; licence not read | Continuous (not verified) | Not an open dataset; pricing and terms not read |
| EIA Open Data API | EIA's time series across fuels | JSON API, bulk files; US public domain | EIA's own survey forms and API schema | No DOI; EIA asks for an acknowledgment with a date | By series | Not a warehouse of non-EIA sources |
| EIA-930 (Hourly Grid Monitor) | Hourly demand, forecast, net generation by source, interchange, by balancing authority | Via the API and the grid monitor; public domain | Form EIA-930 instructions fix content and timing | No DOI | Hourly, within 60 minutes of the hour | No prices, no nodes, no projects |
| OEDI | Datasets from DOE-funded work, any topic | Files and AWS data lakes; CC BY 4.0 "unless otherwise noted" | No common table standard; curators review metadata; "does not review nor validate the quality of data submitted" | Per-dataset records (DOI use not verified today) | Per submitter | Does not reshape datasets into shared shapes |
| Open Power System Data | 32 European countries: load, wind, solar, prices, hourly | CSV with JSON metadata (Frictionless Data Package), Excel, SQLite; scripts MIT; data licence varies by owner | Data Package convention; processing scripts published | Dated versions; DOI per package and version | Latest time series version is 2020-10-06 | No US data; no update since 2020 in the time series package |
| LBNL Queued Up | US generator and storage interconnection requests, 7 ISOs and 50 non-ISO areas, through 2025 | Excel with codebook; CC BY 4.0 | Codebook (data dictionary) | Annual editions; cited as an LBNL publication | Annual | "does not include load interconnection requests" |
| Open Grid Emissions (Singularity) | US hourly, monthly, annual generation and emissions by balancing authority, plant, subplant; 2005 to 2025, hourly from 2019 | CSV downloads, Zenodo archive; code MIT, data CC-BY-4.0 | Documented methodology; data quality metrics published with the data | Releases (v0.8.0); Zenodo DOI | Annual, plus an early release | No real-time data, no prices |
| Electricity Maps | Parsers for electricity data worldwide; a commercial API | Parsers: AGPL-3.0. Processed data: paid API | Parser contribution rules (not read) | Git history for parsers | Parsers: continuous. API: real time | Processed and flow-traced data are sold, not openly licensed (free dataset page not read) |
| WattTime | Marginal and average CO2 and health damage signals, "200+ countries and territories" | API with token; "Basic (free)", "Analyst", "Pro" plans | Methodology and validation page (title seen, not read) | API versions; licence not found | "updated every 5 minutes" (forecast) | Not an open dataset |
| Ember | Country and US state electricity generation, demand, emissions; yearly and monthly | CSV, API with free key; CC-BY-4.0 | Not read today | Dated updates; no DOI seen | Monthly | No hourly US grid data, no nodes, no projects |
| PowerGenome | Builds input files for capacity expansion models (GenX, MacroEnergy.jl) from EIA, NREL, EPA data | Python tool, CSV or Parquet inputs; MIT | Settings file; pytest | Releases (v0.8.0); Zenodo DOI | By release | A tool that prepares model inputs, not a hosted dataset |
| IRW (Item Response Warehouse) | Item response data in education and psychology: 4,918 tables | Tables on Redivis; R and Python clients; per-table source licences | Numbered public standard v1.0 (beta); `irw-validate` on PyPI | Redivis versions; paper DOI 10.3758/s13428-025-02796-y | Continuous; uploads are drafts a person publishes | Not energy; it is the template |
| Large-load requests | See section 3 | Scattered: two public workbooks, slide decks, PDFs, paid products | None shared | None shared | Varies | No national standardized public file found |

## 2. Entries

### 2.1 PUDL, the Public Utility Data Liberation Project (Catalyst Cooperative)

Verified today: `https://raw.githubusercontent.com/catalyst-cooperative/pudl/main/README.rst`; `https://api.github.com/repos/catalyst-cooperative/pudl` and `/releases/latest`; `https://catalystcoop-pudl.readthedocs.io/en/latest/data_access.html`; `https://catalystcoop-pudl.readthedocs.io/en/latest/dev/naming_conventions.html`; `https://catalystcoop-pudl.readthedocs.io/en/latest/dev/data_validation_quickstart.html`.

- **What it is:** "an open source data processing pipeline that makes US energy data easier to access and use programmatically." Three parts in its README: "Raw Data Archives", "Data Pipeline", "Data Warehouse".
- **Sources integrated (README list):** EIA Forms 176 and 191 (work in progress), 860, 860m, 861, 923, 930; EIA Annual Energy Outlook (a few tables); EPA CEMS; FERC Form 1 ("dozens of fully processed tables, plus raw data converted to SQLite"), Form 714 ("a few fully processed tables"), Electric Quarterly Reports, Forms 2, 6 and 60 (raw, converted to SQLite); PHMSA natural gas annual reports; USDA Rural Utilities Service Forms 7 and 12 (via FOIA requests); SEC Form 10-K Exhibit 21; NREL Annual Technology Baseline; GridPath Resource Adequacy Toolkit (partial); Vibrant Clean Energy renewable profiles; a Census geodatabase.
- **Years and granularity:** not read today source by source. The outputs range from annual plant and utility tables to hourly tables (the docs say "The hourly data tables are distributed only as Parquet files").
- **Format:** "writes the resulting tables to Apache Parquet files, with some accompanying metadata stored as JSON", also one DuckDB database and a SQLite database; "the `pudl.sqlite` output is **deprecated** and will no longer be produced starting in 2027". Access: a data viewer with "search, live preview, and CSV export", Kaggle ("updated weekly"), cloud storage that "is free to access thanks to the AWS Open Data Registry", and Zenodo.
- **Licence:** "The PUDL software is released under the MIT License." "The PUDL data and documentation are published under the Creative Commons Attribution License v4.0 (CC-BY-4.0)."
- **Standard and validator:** a naming conventions page ("PUDL's data processing is divided into three layers of Dagster assets: Raw, Core and Output."); a data validation page ("The dbt/ directory contains the PUDL dbt project which manages our data tests"); a pytest badge and a code coverage badge in the README. Metadata for each table is published as JSON.
- **Versioning and citation:** "We assign a version number to our quarterly data releases"; these "stable releases" are "archived for long-term access". Latest release tag: v2026.9.0, published 12 September 2026 (GitHub API). "Zenodo provides stable long-term access to our versioned data releases with a citeable DOI: https://doi.org/10.5281/zenodo.3653158". Raw inputs: "Each of the data inputs may have several different versions archived, and all are assigned a unique DOI"; "Each release of the PUDL software contains a set of DOIs indicating which versions of the raw inputs it processes."
- **Update frequency:** outputs "are updated each night by an automated build process"; the nightly build "may not be as well validated as the stable releases."
- **Who and how funded (README):** Catalyst Cooperative, "a small group of data wranglers and policy wonks organized as a worker-owned cooperative consultancy"; "four grants from the Alfred P. Sloan Foundation's Energy and Environment Program, in 2019, 2021, 2024, and 2026"; a National Science Foundation POSE grant in 2024 ("award 2346139"); sustainers RMI and GridLab at "≥$25,000/year". GitHub stars: 610.
- **What it does not do:** the README's list of integrated sources contains no ISO or RTO price feed (nodal or zonal LMPs), no interconnection queue, no large-load request data, no news or event tables. Its "High Priority Target Datasets" are more FERC Form 1 tables, more AEO tables, EIA thermoelectric water use, FERC Form 2 and mine data.
- **Beyond a small student warehouse:** archives every raw input with its own DOI; processes FERC Form 1 and EQR, which are large and irregular filings; nightly automated builds of "hundreds of tables"; a Zenodo DOI for each data release; paid staff and multi-year grants; named downstream users (RMI, Princeton ZERO Lab, PyPSA-USA, PowerGenome, Singularity's Open Grid Emissions).

### 2.2 gridstatus (the open-source library) and Grid Status (the company's hosted data)

Verified today: `https://raw.githubusercontent.com/gridstatus/gridstatus/main/README.md`; `https://api.github.com/repos/gridstatus/gridstatus` and `/releases/latest`. Not read: `https://www.gridstatus.io/pricing` and `https://www.gridstatus.io/terms` (curl returned a page shell with no text; the fetch tool returned HTTP 403).

- **The library:** "`gridstatus` is an open source Python library, maintained by Grid Status, that fetches electricity market data directly from North American independent system operators (ISOs), regional transmission organizations (RTOs), and the U.S. EIA."
- **Coverage:** "ISOs / RTOs / grids: CAISO, ERCOT, PJM, MISO, SPP, NYISO, ISO-NE, IESO, and AESO, plus the U.S. EIA." "Datasets (vary by ISO): fuel mix, load (demand), load forecasts, locational marginal prices (LMP, day-ahead & real-time), storage, ancillary-service prices, interconnection queues, and more." "Coverage and historical availability vary by source."
- **Licence:** BSD-3-Clause (GitHub API). Stars: 447. Latest release v0.36.0, published 21 April 2026 UTC (its notes are headed "v0.36.0 - April 20, 2026").
- **Library against hosted API, from the README's own table:** library: "Minimally processed data fetched directly from ISO and EIA sources", "No Grid Status account; most datasets require no API key", "Historical availability depends on each source's retention policy", "Filtering capabilities vary by source". Hosted: "Hosted data with consistent column names, timestamp formats, and DST handling", "Grid Status API key with free and paid plans", "Historical data queryable immediately", "Consistent server-side filtering by time, columns, and row values".
- **Standard and validator:** the library has no cross-source table standard (see "Minimally processed" above). The README carries a code coverage badge and a commented-out tests badge with the note "disable until tests more reliable". The hosted product's schema is described as consistent; its documentation was not read today.
- **Versioning and citation:** software releases on GitHub and PyPI. No DOI or citation line appears in the README (searched "doi", "zenodo", "cite").
- **What it does not do:** the library keeps no archive, so a past value is available only while the source still serves it. The hosted archive is a commercial service; its plan limits, price and redistribution terms were not read today, so nothing is stated here about them.
- **Beyond a small student warehouse:** nine ISOs or grids and many dataset types per ISO, maintained by a company; a hosted archive "queryable immediately" with one schema.

### 2.3 EIA Open Data API and the Hourly Electric Grid Monitor (Form EIA-930)

Verified today: `https://www.eia.gov/opendata/`; `https://www.eia.gov/about/copyrights_reuse.php`; `https://www.eia.gov/survey/form/eia_930/instructions.pdf`. Not read: `https://www.eia.gov/electricity/gridmonitor/about` (the page's text is loaded by script; curl and the fetch tool returned only the site menu), so the number of balancing authorities and the first date of the series are not stated here.

- **API:** "The U.S. Energy Information Administration is committed to its free and open data by making it available through an Application Programming Interface (API) and its open data tools." Registration gives a key. "EIA data is provided free of charge and should be used in compliance with our Copyrights and Reuse Policy." Bulk files are listed on the same page.
- **Licence:** "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". EIA asks for an acknowledgment "which includes the publication date".
- **EIA-930, what is collected (instructions):** "This collection provides a centralized and comprehensive source for hourly electric industry operating data." Items named in the instructions include "Hourly total actual demand", "Yesterday's hourly day-ahead demand forecast for today", "Yesterday's hourly net generation by energy source" and, "As soon as available, within one month after the operating day, hourly actual demand by sub-region". "Report all data as hourly integrated values in megawatts by hour ending time." "Report hourly date-time stamps using the Coordinated Universal Time (UTC)".
- **Timing:** "Same-day files are to be submitted hourly, no later than within 60 minutes of the end of the operating hour." "Daily files are to be submitted daily by 7:00 a.m. Eastern Prevailing (Standard or Daylight Saving) Time."
- **Standard and validator:** the survey form and its instructions are the standard for respondents. EIA's handling of anomalies and imputation is described on the grid monitor's about page, which was not read today.
- **Versioning and citation:** no DOI. Series can be revised by respondents; the API serves the current values.
- **What it does not do:** no prices, no nodes or zones below sub-regions, no project or queue data. It is the primary source, so it is not a join of several publishers.
- **Beyond a small student warehouse:** a mandatory federal collection ("Compliance Registry as a balancing authority must submit information as required by this data collection") with hourly reporting from the operators themselves.

### 2.4 Open Energy Data Initiative (OEDI)

Verified today: `https://data.openei.org/about`. Not read: `https://openei.org/wiki/Open_Energy_Data_Initiative_(OEDI)` (HTTP 503).

- **What it is:** "Provides free access to data generated from efforts funded by the U.S. Department of Energy (DOE) and supporting projects and partnerships." "OEDI is powered by OpenEI, an open energy information portal sponsored by the U.S. Department of Energy and developed by the National Laboratory of the Rockies".
- **Coverage:** "OEDI contains data from all aspects of energy research, development, and operations", with marine, geothermal, solar and wind energy, device engineering, performance and testing, and economic analysis listed. "The OEDI Data Lake is a centralized repository of datasets aggregated from the U.S. Department of Energy's Programs, Offices, and National Laboratories."
- **Licence:** "Content is available under Creative Commons Attribution 4.0 unless otherwise noted."
- **Standard and validator:** "Our data curators review the metadata provided with each data submission for accuracy, completeness, and relevance to the data submitted." "The OEDI team does not review nor validate the quality of data submitted." The page states FAIR and "FARR (FAIR, AI Readiness & Reproducibility) guiding principles" and that "OEDI metadata is machine-readable". No shared table shape across datasets is described.
- **Versioning and citation:** per dataset. Whether each submission receives a DOI was not verified today.
- **What it does not do:** it is a catalogue and store of submitted datasets, each in its submitter's own structure. It does not reshape them into common tables, and it does not check the values.
- **Beyond a small student warehouse:** federal sponsorship, laboratory-scale datasets hosted in cloud data lakes, and a curation staff.

### 2.5 Open Power System Data (OPSD)

Verified today: `https://open-power-system-data.org/`; `https://data.open-power-system-data.org/time_series/latest/`.

- **Coverage:** the time series package: "Load, wind and solar, prices in hourly resolution", "32 European countries", "aggregated either by country, control area or bidding zone". Variables are named for their sources, for example "load_actual_entsoe_transparency" (the ENTSO-E Transparency platform).
- **Format:** "we follow the Data Package convention and publish data primarily as CSV files and metadata as JSON files (Excel and SQLite files are also available)."
- **Licence:** scripts "are open source and available under the MIT license on GitHub". Data: "We would like to publish all data under a Creative Commons Attribution license", "However, at this point, several data owners do not allow us to do so. Beware that some data published here might be subject to copyright".
- **Standard and validator:** the Frictionless Data Package convention with a JSON descriptor per package; the processing notebooks are published per version. No separate validator is described on the pages read.
- **Versioning and citation:** dated versions with stable addresses and a DOI: "https://doi.org/10.25832/time_series"; the page gives a citation line: "Open Power System Data. 2020. Data Package Time series. Version 2020-10-06." Versions listed run from "2016-07-14" to "2020-10-06 (latest)", ten in all.
- **Update frequency:** the latest time series version is dated 6 October 2020. The home page says the packages "are actively maintained (current funding until 2020)" and "This website is maintained by Neon."
- **What it does not do:** no US data. "We focus on long historical time series rather than high frequency updates of real-time information." "We provide boring CSV files rather than fancy visualization."
- **Beyond a small student warehouse:** a DOI for every version of every package, and original input data kept beside each version ("View original input data").

### 2.6 LBNL "Queued Up" (interconnection queue dataset)

Verified today: `https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics`; the slide deck `https://emp.lbl.gov/sites/default/files/2026-06/Queued%20Up%202026%20Edition.pdf`. Not read: `https://emp.lbl.gov/queues` (HTTP 403 to curl and to the fetch tool).

- **Coverage:** "Berkeley Lab compiled, aggregated, and cleaned interconnection queue data from >50 transmission grid operators (7 ISO/RTOs and 50 non-ISO balancing areas), which collectively represent ~98% of currently installed U.S. electric generating capacity. The dataset includes requests submitted to queues through the end of 2025, and only includes generation requests seeking to connect to the transmission grid (i.e., does not include load interconnection requests nor distribution-connected or behind-the-meter projects)." Done "In collaboration with GridTracker".
- **Format:** "The Excel data file includes (a) the full project-level interconnection queue dataset through 2025, (b) a codebook (data dictionary) describing each data field, and (c) 36 additional tabs featuring tables summarizing a range of interconnection metrics."
- **Licence:** "The Queued Up data file is licensed CC BY 4.0. You may use, share, or adapt the dataset as long as you attribute it to Lawrence Berkeley National Laboratory and GridTracker."
- **Standard and validator:** a codebook. No validator is described. The deck notes "In some cases, the analysis leverages additional (non-public) data provided to LBNL directly from transmission providers to fill in gaps from the public data."
- **Versioning and citation:** annual editions ("Queued Up: 2026 Edition", data file "thru2025"); a "Download citation" link on the publication page. A DOI was not seen on the page read.
- **Update frequency:** "Queued Up presents an annual snapshot".
- **Headline figures (2026 edition):** "there were ~8,200 projects actively seeking grid interconnection in the U.S., representing 1,312 GW of generation and approximately 749 GW of storage"; "the median duration from IR to COD was over 5 years for projects built in 2025."
- **What it does not do:** load. The deck says: "there are separate queues for large loads and those are not included in this report."
- **Beyond a small student warehouse:** more than 50 operators' queues cleaned into one project-level file each year, with non-public data from operators filling gaps, and duration statistics from request to operation.

### 2.7 Open Grid Emissions (Singularity Energy)

Verified today: `https://singularity.energy/open-grid-emissions`; `https://raw.githubusercontent.com/singularity-energy/open-grid-emissions/main/README.md`; GitHub API for the repository and its latest release.

- **Coverage:** "Consumption-based and generation-based emissions factors, individual generator data, and data quality metrics for U.S. balancing authorities. 2005-2025." (The page prints an en dash in the year range.) "Annual and monthly data from 2005 through 2025, with hourly data available from 2019 onward. The data includes all greenhouse gas (GHG) emissions (CO₂, CH₄, N₂O, and CO₂-eq) and several criteria pollutants (NOₓ, SO₂). Regions are currently aggregated at the balancing authority level." Download levels: "Balancing Area", "Plant-level", "Subplant-level".
- **Format and licence:** downloads from the page and a Zenodo archive (`https://zenodo.org/records/22052851`). "This data is made available under the Creative Commons Attribution 4.0 International license (CC-BY-4.0)." Code: MIT (GitHub API).
- **Standard and validator:** the README describes "peer-reviewed, well-documented, and validated methodologies" and links a documentation site; the dataset ships "data quality metrics". The documentation site itself was not read today (the address tried returned 404).
- **Versioning and citation:** DOI badge in the README: "10.5281/zenodo.7062459". "All previous versions of the data will be archived on Zenodo." Latest software release v0.8.0, 14 August 2026, which "makes 2025 Early Release data available".
- **Update frequency:** annual. The page lists "Expected 2025 data release: October 2026", "2025 early release data: published August 2026", "2024 data released: December 2025".
- **Inputs:** it runs on PUDL data (the README explains the `PUDL_DATA_STORE` and `PUDL_BUILD` settings).
- **What it does not do:** nothing in real time; a year's final data arrives late in the following year. No prices.
- **Beyond a small student warehouse:** hourly emissions at plant and subplant level for the whole country, with a published method and a versioned DOI archive.
- A discrepancy seen today: the README still says "The latest release includes data for year 2005-2022"; the download page says 2005 to 2025.

### 2.8 Electricity Maps and WattTime: what is open and what is not

**Electricity Maps.** Verified today: `https://raw.githubusercontent.com/electricitymaps/electricitymaps-contrib/master/README.md`; GitHub API for that repository; `https://www.electricitymaps.com/pricing`. Not read: the free datasets page (`https://portal.electricitymaps.com/datasets` redirects to `https://app.electricitymaps.com/datasets`, HTTP 403) and the API documentation (HTTP 403).

- **Open:** the parsers. "A collection of parsers to collect and standardize electricity data such as production, exchanges and price from across the globe." "This repository is licensed under GNU-AGPLv3 since v1.5.0". "We fetch the raw data from public, free, and official sources." Stars: 4,039.
- **Not open, per the pages read:** the processed data. The README says the parsers' data "powers the Electricity Maps platform, which includes our flow-tracing algorithm, estimation models, forecast engine and much more", and points to "Our Commercial Website". The pricing page prints per-signal plans at "€6,000 / Year" and "Custom", a trial ("Ready to try the API for 14 days?"), and "Real-time data includes 3 months of trailing history." "We cover 130+ zones worldwide."
- **Not verified:** whether free historical files are offered, their years and their licence. The page that would say so could not be read today.

**WattTime.** Verified today: `https://watttime.org/data-science/data-signals/`; `https://watttime.org/docs-dev/data-plans/`.

- **Signals:** "co2_moer": "Marginal Operating Emissions Rate of carbon dioxide. The change in emissions caused by a change in load or generation."; an average rate: "Average Operating Emissions Rate of carbon dioxide."; and a health damage signal.
- **Access:** "Data access through the WattTime API", "Secure, token-based authentication". Plans named on the page: "Basic (free)", "Analyst", "Pro". Feature rows on the page include "All signals & endpoints for one region: CAISO_NORTH", "CO2 percentile, all regions", "Regions: Choose from global coverage of 200+ countries and territories", "Historical data: 2+ years of history", "Forecast data: 72-hour rolling, updated every 5 minutes". The page marks which row belongs to which plan with symbols that did not survive as text, so the split between the free and paid plans is not stated here.
- **Licence:** not found on the two pages read.
- **What neither does:** neither publishes its processed signal history as an openly licensed bulk dataset on the pages read. Both are services reached by key.
- **Beyond a small student warehouse:** marginal emissions models and forecasts, and coverage outside the United States.

### 2.9 Ember

Verified today: `https://ember-energy.org/data/`; `https://ember-energy.org/data/api/`; `https://ember-energy.org/creative-commons/`; `https://ember-energy.org/data/us-electricity-data-explorer/`.

- **Coverage:** "Yearly Electricity Data": "Ember's latest yearly data on electricity generation, capacity, emissions and demand from over 200 geographies." "Monthly Electricity Data": "The latest monthly data on electricity generation, emissions, and demand from Ember for 88 geographical areas." "Monthly Wind and Solar Capacity Data" for 25 countries. For the United States: "Monthly generation data for all 50 states are provided by the U.S. Energy Information Administration (EIA). Data is reported on a 3 month lag."
- **Format and licence:** downloadable datasets and "Ember's API for open electricity data on yearly and monthly electricity generation, demand, power sector emissions and carbon intensity", with a key issued by email. "Ember content is released under a Creative Commons Attribution Licence (CC-BY-4.0)".
- **Standard and validator:** methodology pages were not looked for today. No validator is described on the pages read.
- **Versioning and citation:** each dataset shows a "Last Updated" date ("20/03/2026" on the API page for the yearly and monthly sets). No DOI seen.
- **Update frequency:** the US explorer says "Updated monthly".
- **What it does not do:** country and state totals by month or year. No hourly US grid data, no prices by node or zone for the US, no projects.
- **Beyond a small student warehouse:** more than 200 geographies kept consistent by a staffed organisation, with an API.

### 2.10 PowerGenome and other model-input projects

Verified today: `https://raw.githubusercontent.com/PowerGenome/PowerGenome/master/README.md`; GitHub API for PowerGenome (and its latest release) and for PyPSA-USA; `https://raw.githubusercontent.com/PyPSA/pypsa-usa/master/README.md`.

- **PowerGenome:** "The goal of PowerGenome is to let a user make all of these choices in a settings file and then run a single script that generates input files for the power system model. PowerGenome currently generates input files for GenX." Release v0.8.0 (2 September 2026) adds an "Optional MacroEnergy.jl (Macro) simpleCSV input output mode". "PowerGenome uses data from a number of different sources, including EIA, NREL, and EPA." Inputs are "Database tables or files (CSV/Parquet)" plus renewable generation profiles. Licence MIT. DOI badge "10.5281/zenodo.4426097". Badges for pytest, coverage and documentation. PUDL's README lists "The PowerGenome Project" among its users.
- **PyPSA-USA:** "PyPSA-USA is an open-source power systems model of the bulk transmission systems in the United States", for "capacity expansion modeling, production cost simulation, and power flow analysis". Licence MIT. DOI badge "10.5281/zenodo.10815964". PUDL's README lists it as a user.
- **NREL Annual Technology Baseline:** integrated by PUDL (PUDL README). Its own page was not read today.
- **What these do not do:** they assemble inputs for a model run chosen by the user (regions, clusters, years). They are not a continuously updated record of observed prices, flows or projects, and they publish code and settings, with data drawn from PUDL, EIA, NREL and EPA.
- **Beyond a small student warehouse:** clustering of generators, transmission constraints between regions and hourly profiles prepared for optimization models.

### 2.11 The Item Response Warehouse (IRW): the template

Verified today: `https://raw.githubusercontent.com/ben-domingue/irw/main/README.md`, `CLAUDE.md`, `ARCHITECTURE.md` and `datastandard.md` in the same repository; `https://itemresponsewarehouse.org/` and `https://datapages.github.io/irw/standard.html`; `https://link.springer.com/article/10.3758/s13428-025-02796-y`; GitHub API for the repository.

- **What it is:** "The **Item Response Warehouse (IRW)** is an open-source repository that standardizes and aggregates item response datasets to advance psychometric research." "The data itself lives on Redivis." Field: educational and psychological measurement, not energy.
- **Size:** the paper (Behavior Research Methods, "Published: 05 September 2025", "Volume 57, article number 276 (2025)", open access) describes "the over 900 datasets in the current iteration of the IRW (version 28.2)". The site's home page on 7 October 2026 carries these totals in its page data: 4,918 tables, 3,367,932,818 responses, 93,697,015 participants, 1,080,520 items.
- **Format:** tables in one fixed column format (its guidance file lists, for example, a `resp` column for the response value); "Output saved as `.csv` only" for processing; delivered through Redivis and through R and Python client packages ("The R package reads every table without a Redivis login").
- **Licence:** per table, taken from the source and recorded; the intake rule is written down ("Verify the license first", with CC0, CC BY and CC BY-SA proceeding, non-commercial licences carried through, and no licence meaning "stop, and email the owner for written permission"). The GitHub API reports no licence file for the code repository.
- **Standard and validator:** a public numbered standard: "Version 1.0 (beta) · 2026-09-19". "The standard is a set of numbered clauses. MUST marks a requirement: a file that breaks one does not conform. SHOULD marks a strong expectation that a validator will warn about". The validator: "`irw_validate/` | The format validator (`irw-validate` on PyPI), the gate a finished table passes before upload", with an R twin. The standard page states that older tables may not conform: "Tables published before version 1.0 may not conform."
- **Versioning and citation:** Redivis dataset versions; the paper's DOI (10.3758/s13428-025-02796-y); the standard has its own "Cite as" line.
- **Publishing rule:** "`red_up/` | The one Redivis uploader (`red_up`); every upload writes a draft for a human to publish". "Redivis caps any single dataset at 1000 tables", which is why the IRW is split across several Redivis datasets of the same structure.
- **What it does not do:** it has no live layer and no time series; its tables are static research datasets. It holds no energy data.
- **What the ERW takes from it:** the pattern of one self-contained script per source, one written standard, one validator as the gate before upload, Redivis as the published copy, and drafts that only a person releases (this repository's `CLAUDE.md`, which says it is adapted from the IRW's).
- **Beyond a small student warehouse:** 4,918 tables, a peer-reviewed paper, a numbered public standard with a citable version, and client packages in two languages.

## 3. Large-load and datacenter interconnection requests: testing the claim

**The claim to test:** that no public dataset exists of how much large load is waiting for power by place, or of how long a new large load waits.

**Result in one paragraph.** The claim in that strict form is not supported by what was read today. Two grid operators publish project-level lists of load interconnection requests, with megawatts, county, request date and status, as downloadable workbooks: NYISO and the Bonneville Power Administration. A free website, interconnection.fyi, shows 581 load requests in 11 states. What was not found, within the limits listed in 3.12, is narrower: (a) a public project-level or county-level list for ERCOT, PJM, the Southeast or the Southwest; (b) any public dataset of realized waits for large loads, from request to energization; (c) one national file in one format under an open licence. Each source is described below with what it holds and what it does not.

### 3.1 Table of counterexamples

| Source | Public and machine-readable? | What it contains | What it does not contain |
|---|---|---|---|
| NYISO interconnection queue, sheet "Load Projects" | Yes, Excel | 74 load requests: queue number, developer, project name, request date, peak MW, end-use code, county, zone, point of interconnection, utility, status, proposed initial backfeed date. A summary by zone and status | New York only. No realized energization date column |
| BPA Interconnection Request Queue | Yes, Excel | 458 line and load requests ("LL") since 2004: request date, requestor, state, county, status (including "ENERGIZED"), requested in-service date, MW | BPA's system only. Lines and loads of every size together; no end-use field; no actual energization date |
| interconnection.fyi (GridTracker) | Free to browse; export is paid | 581 load requests, 90.84 GW, in 11 states | No rows for Texas, Virginia, Georgia, Ohio or Arizona. "All rights reserved" |
| LBNL Queued Up | Yes, Excel, CC BY 4.0 | Generators and storage | "does not include load interconnection requests" |
| ERCOT large load updates | Public slide decks (PDF) | System totals by date, by status group and by type: about 410 GW (26 March 2026), about 474 GW (June 2026) | No project list, no county or zone table in the documents read; not machine-readable |
| PJM load forecast, Table B-9b | Yes, Excel | Forecast adjustments to summer peak by transmission zone, 2026 to 2046 | A forecast, not requests; zone level; no request dates, no waits |
| Georgia Power quarterly large load report | Public PDF, partly redacted | Pipeline totals; one row per project with stage, announced MW, initial in-service date, annual ramp | Project name, city, county and coordinates are "REDACTED"; one utility |
| Grid Strategies load growth report | Public PDF | National and regional five-year forecasts summed from FERC Form 714 and ISO plans | Not a request dataset; its data center benchmark uses a commercial tracker |
| EPRI, WECC and other studies | Public reports | Estimates built from commercial trackers, utility forecasts or a questionnaire | No released request-level data |
| Epoch AI, IM3 atlas, DELTa | Yes, open files | Existing or building data center sites; large-load tariffs | Not requests to a utility; no waiting megawatts |
| GridTracker, datacenter.fyi, Cleanview, Halcyon and others | Paid or partly free | Project and site trackers | Not open; fields and method not read |

### 3.2 NYISO: a public load queue

Verified today: `https://www.nyiso.com/interconnections` (the page links "Interconnection Queue") and the workbook `https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue-08312026.xlsx/ff0e2005-e8d3-e75d-3e81-fa7027a52685?t=1789147562327`, downloaded and opened.

- The workbook has a sheet named "Load Projects" with the columns "Queue Number", "Developer Name", "Project: Project Name", "IR Submission Date", "Peak MW load", "End-Use", "Record Type Name", "Type/Fuel", "County", "State", "NYISO Zone", "Points of Interconnection", "CTO/Utility", "Affected Transmission Owner (ATO)", "Project Status #", "SIS Bundle", "Last Updated Date", "Availability of Studies", "IA Tender Date", "FS Completion Date", "Proposed Initial Backfeed Date".
- Computed from the file: 74 rows of type "L", with request dates from 2 November 2005 to 28 August 2026 and peak load summing to 17,672 MW. End-use codes present: "DAT" (24 rows, 5,877 MW), "DAT-AI" (12 rows, 5,266 MW), "DAT-CM" (4 rows, 745 MW), "M-CH", "M-CG", "M-IN", "RD", "O", and 23 rows with no code (4,060 MW). The meaning of the codes was not looked up.
- A second sheet, "Load Project Tracking", is titled "Load Project Tracking Summary (by NYISO Zone and Requested MW)" and gives megawatts by status and zone. Its "Total" row for the New York Control Area reads 14,473.1 MW, with "Withdrawn (not included in NYCA total)" at 3,078.88 MW, "SIS Pending" 5,503 MW, "SIS In-Progress" 4,431 MW, "Under Construction" 1,515 MW and "In-service" 360.2 MW.
- What it does not hold: a column for the date a load was energized. A wait could be approximated only from "IR Submission Date" and a status change seen across successive monthly files, which this session did not attempt.

### 3.3 Bonneville Power Administration: a public line and load queue

Verified today: `https://www.bpa.gov/energy-and-services/transmission/interconnection` (links "Interconnection Request Queue" and says requests for new points of delivery "are evaluated under BPA's Line and Load Interconnection process") and the workbook `https://www.bpa.gov/-/media/Aep/transmission-media-documents/InterconnectionQueueOutput.xlsx`, downloaded and opened; its header cell is dated 6 October 2026.

- Columns include "Request Number", "Request Date", "Project Name", "Requestor", "Connection Type", "State", "County", "Status", "Original Requested In-Service Date", "Agreed To: (Blank=TBD)", "Max Summer Interconnection Service MW", "Max Winter Interconnection Service MW", "Point of Interconnection".
- Computed from the file: 1,468 requests, of which 458 have connection type "LL" and 1,010 "GI". The "LL" rows run from 17 May 2004 to 28 September 2026; 457 of them name a county; states: Washington 202, Oregon 158, Idaho 24, Montana 9, Nevada 4, California 3, Wyoming 1, blank 57. Status of the "LL" rows: "WITHDRAWN" 170, "STUDY" 92, "ENERGIZED" 85, "BPA COMPLETED" 35, "STUDY COMPLETED" 32, "CONST AGRMT EXE" 24, "RECEIVED" 19, "E&P EXECUTED" 1. Of the 355 "LL" rows with a summer MW value, rows in "STUDY" sum to 28,545 MW and rows in "RECEIVED" to 10,557 MW. 129 "LL" rows are 75 MW or more.
- What it does not hold: the kind of load (no end-use field; sample rows include a 17.1 MW substation and a 37 MW mine load beside a 300 MW request), and the actual date of energization. "LL" covers line interconnections as well as loads.

### 3.4 interconnection.fyi (GridTracker)

Verified today: `https://www.interconnection.fyi/?status=All&type=Load` and `https://www.interconnection.fyi/data-center`.

- With the filter "Type: Load" and "Status: All" the page shows "581 requests" and "90.84 GW" for the United States. The counts by state in the page's data: Washington 266, Oregon 184, New York 71, Idaho 25, California 14, Montana 12, Nevada 4, Pennsylvania 2, New Jersey 1, Utah 1, Wyoming 1. Washington, Oregon, Idaho, Montana and New York, the states of the two public queues above, account for 558 of the 581; which queue each row comes from was not checked.
- "Interconnection.fyi is a free public resource by GridTracker, the research firm behind the interconnection data in LBNL's Queued Up." "we update this data at least once a day" was reported by the fetch tool; the page text read directly says "Data last updated today".
- "Developer names, contacts, documents, and full export are available in GridTracker". "The complete dataset" is offered "with monthly CSV delivery and daily Snowflake direct-share subscription options." Footer: "© 2026 Interconnection.fyi. All rights reserved."
- The site's "U.S. Data Center Records Directory" page says "Browse 12,538 records across 48 states" with "4,055 Operational", "1,020 Construction", "2,534 Proposed", and sends readers to datacenter.fyi for detail. Its fields and sources were not read.
- What it does not hold: load requests in the regions where most data center load is reported (no Texas, Virginia, Georgia, Ohio or Arizona rows under "Type: Load"). No open licence.

### 3.5 ERCOT

Verified today: `https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf` (Board of Directors, 20 to 21 April 2026); `https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf`; `https://www.ercot.com/services/rq/large-load-integration`; `https://www.ercot.com/committees/tac/llwg`.

- April deck: "ERCOT received 198 new Large Load Interconnection requests in Q1 2026 resulting in the total LLI request queue increasing to ~410 GW." "ERCOT is tracking approximately 410 GW of Large Loads seeking interconnection, of which ~87% are data centers. This is an increase of 178 GW since the end of 2025." (as of 26 March 2026). It has charts "By Submitted Quarter".
- July deck: "ERCOT is tracking approximately 474 GW of Large Loads seeking interconnection, of which ~90% are data centers." (as of June 2026), with charts "Actual and Projected Large Loads Growth 2022-2033" and "Large Loads by Project Type". On the first batch study: "Approximately 205 GW of Large Load is eligible for inclusion in Batch Zero based on existing studies", with project counts by eligibility class, "Data as of July 28, 2026".
- The April deck says ERCOT set up a team "to begin providing periodic status reports for all Large Load projects" and "At this time, status reports will be available via Transmission Service Providers". The slide shows a sample report layout (columns "LLI Number", "TSP", "Owner", "MW", "Likely Treatment in Batch Zero") filled with placeholder owners such as "Big Data" and "ABC".
- The Large Load Integration page holds forms and guides for the "Batch Zero" process ("Entities wishing to interconnect a load facility of 75 MW or greater through the Batch Zero process should consult PGRR145"), not data files.
- What was not found: a public file listing large load requests by project, county, load zone or utility. The two decks give system totals and charts. Other ERCOT monthly reports and working group postings were not all opened, so a table by zone may exist in one not read.

### 3.6 PJM

Verified today: `https://www.pjm.com/planning/resource-adequacy-planning/load-forecast-dev-process`; the 2026 Load Forecast Report PDF and the workbook `https://www.pjm.com/-/media/DotCom/planning/res-adeq/load-forecast/total-load-adjustments-breakdown.xlsx`, downloaded and opened; the 2026 Load Forecast Accuracy Report PDF.

- The page lists Excel files under "Load Adjustments": "Total Load Adjustments Breakdown XLS", "Total Monthly Load Adjustments XLS", and "Load Adjustment Breakdown for Capacity Obligations XLS", and a "Data Center Accuracy Report" with "Data XLS".
- The workbook's sheet is "Table B-9b", "Total Adjustments to Summer Peak Load (MW) for Each PJM Zone and RTO (2026 - 2046)": one row per zone or area, one column per year.
- The report says the forecasts of named zones "have been adjusted to account for large, unanticipated load changes", with reasons printed as "Growth in data center load", "Growth in data center load and a voltage optimization program", "Growth in data center load and port electrification" and "A peak shaving program that commenced in the 2023 DY", and that PJM "created and published a Load Adjustment Request Implementation (PDF) document to provide transparency in how PJM evaluates large load adjustment requests".
- The accuracy report describes dashboards of "Monthly Data Center Load Peak & Annual Summer Large Load Adjustments by Zone/EDC/LSE".
- What it does not hold: requests. These are megawatts that PJM accepted into its forecast after review, by transmission zone and year. There is no request date, no count of requests, no county, and no waiting time.

### 3.7 State commission dockets: Georgia Power

Verified today: `https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/226607/107887` (Georgia Power's "Quarterly Large Load Economic Development Report" for the period ending 31 March 2026, filed 15 May 2026, "Docket No. 55378" in the cover letter and "Docket No. 56002" on the report).

- Totals: "the portfolio of large load customers committed to receiving service from Georgia Power has grown by 500 MW, reaching a total of 12,400 MW across 31 customers" (the source prints a footnote number after "MW"; it is left out here); "the total pipeline of economic development projects through the mid-2030s has increased by 7,100 MW to 76,200 MW. Of this, 73,100 MW represents large load economic development projects"; changes in the quarter: "12,600 MW that entered the pipeline", "2,900 MW that exited the pipeline".
- The attachment has one row per project with the columns "Project Name", "City", "County", "GPS Coordinates", "Facility Type", "Segment", "Territory", "Project Stage", "Announced Load", "Initial In Service Date" and yearly load ramps. In the public version the stage, the announced megawatts, the in-service quarter, the segment (for example "Data Center/Crypto") and the territory ("Inside" or "Outside") are printed; the name, city, county and coordinates read "REDACTED". The filing says it "contains certain information that is being filed under the Commission's trade secret rules".
- What it does not hold: place. It is a PDF, one utility, quarterly.
- Other utilities' filings (Dominion, AEP, Arizona Public Service, Oncor, CenterPoint, Duke and others) were not opened today. Whether any of them prints megawatts by county is not known from this session.

### 3.8 Reports that estimate the total

- **Grid Strategies**, "Power Demand Forecasts Revised Up for Third Year Running, Led by Data Centers", November 2025 (`https://gridstrategiesllc.com/wp-content/uploads/Grid-Strategies-National-Load-Growth-Report-2025.pdf`, read today): "The 166 GW forecast is equivalent to adding 15 times the peak load of New York City." It sums utility and ISO forecasts (FERC Form 714 with later adjustments). "Data center load forecast for 2030 aggregates to about 90 GW"; "The data center portion of utility load forecasts is likely overstated by roughly 25 GW"; "Cleanview is tracking ~60 GW of data centers scheduled to begin operation before 2029"; "Similar growth is shown in one proprietary database of data center projects." It is a forecast compilation, not a list of requests, and it releases no request-level data.
- **LBNL, "2026 Large Load Literature Review and Data Sources"** (`https://datacenters.lbl.gov/publications/2026-large-load-literature-review`, read today): "The Large Load Literature Review and Data Sources reports are updated monthly, summarizing reports and data published in 2026 that focus on large loads. The September update catalogs 41 publications focused on large loads". Its companion deck, "Large Load Literature Review: Data Sources", "May 2026 Update" (`https://eta-publications.lbl.gov/sites/default/files/2026-08/lbnl_lllreview_datasources.pdf`, read today), lists the inputs of twelve quantitative reports. The inputs it names for data center pipelines are commercial or utility sources: "Halcyon Large Load Tariff Tracker"; for EPRI's "Powering Intelligence 2026", a "Synthesis of nominal capacity estimates from Aterio, Avison Young, Baxtel, BloombergNEF, CBRE, Cushman & Wakefield, JLL, S&P Global, and Wood Mackenzie" with "FERC Form 714 data"; for Grid Strategies, "Cleanview Tracker" and "TD Cowen"; "PJM Forecasted Data Center Additions"; "Pacific Gas & Electric Projected Data Center Pipeline"; for the WECC study by Elevate Energy Consulting (February 2025), a "Self-administered questionnaire" to WECC's large load advisory group, used "to estimate the large load interconnection queue size and breakdown by category". None of the twelve slides names a public national dataset of large-load requests as an input.
- **EPRI** and **WECC**: their reports were not opened today; the lines above are LBNL's descriptions of them. The WECC document page (`https://www.wecc.org/wecc-document/19111`, title "An Assessment of Large Load Interconnection Risks in the Western Interconnection") was seen.

### 3.9 Open datasets about data centers that are not request data

- **Epoch AI, "AI data centers"** (`https://epoch.ai/data/data-centers`, read today): "Rigorous public data on the world's largest AI data centers. Independent estimates of power, AI compute, and cost built from high-resolution satellite imagery, permits, and our understanding of how data centers are constructed." "We cover 93 data centers"; "13.8 GW IT power"; licence "CC-BY"; a "Download this data" link. It describes facilities being built or running, worldwide. It holds no utility requests and no queue dates.
- **IM3 Open Source Data Center Atlas** (`https://data.msdlive.org/records/65g71-a4731`, read today): "This dataset contains locations of existing data center facilities in the United States. Data center locations were derived from OpenStreetMap (OSM), a crowd-sourced database." Open Database License; DOI "10.57931/2550666". Existing sites only; no megawatts requested.
- **DELTa, the Database of Emerging Large-Load Tariffs** (NC Clean Energy Technology Center and SEPA; `https://nccleantech.ncsu.edu/2025/11/18/delta-navigates-new-challenges-for-large-electric-loads/`, read today): "a public, user-friendly resource that aggregates, summarizes, and tracks utility rates and contracts designed for large electric loads"; "a total of 65 approved and proposed tariffs" after the update of 10 November 2025; "The full database can be downloaded by completing a brief form on SEPA's website." It covers tariffs, not requests.

### 3.10 Commercial products

Seen today by name and front page only; fields, method and price were not read: GridTracker (`https://gridtracker.io`, the paid product behind interconnection.fyi); datacenter.fyi; Cleanview (`https://cleanview.co/data-centers`, which lists a "Data Center Map" under "Free Trackers" and a "Pricing" page); Halcyon (`https://halcyon.io/`, "Large Load Tariff Tracker", "New Substation Development Tracker"). Named in LBNL's deck and not opened: Aterio, Baxtel, BloombergNEF, S&P Global, Wood Mackenzie, TD Cowen. These products exist and are not open; several of the public reports in 3.8 take their data center figures from them.

### 3.11 Federal proceedings that may change this

Not verified from primary documents. A law firm page (`https://www.mcguirewoods.com/client-resources/alerts/2026/6/ferc-issues-section-206-show-cause-orders-directing-all-six-rtos-isos-to-justify-or-reform-large-load-integration-rules/`), read only through a fetch tool's summary because curl received HTTP 403, reports that FERC issued show cause orders on 18 June 2026 to six grid operators (dockets EL26-67 PJM, EL26-70 MISO, EL26-68 SPP, EL26-71 CAISO, EL26-72 ISO-NE, EL26-69 NYISO) on large load interconnection rules, one category being "Cost transparency and cost shifting protections". A web search summary also said the orders direct operators to post searchable data on large load additions; that sentence was not found on any page read today and is not relied on. FERC's own pages returned HTTP 403. If the orders lead to public queue postings, the gap in 3.1 would narrow.

### 3.12 What today's reading supports, stated as narrowly as the evidence

1. **By place:** public project-level load request lists exist for New York (NYISO, 74 requests) and for BPA's system in the Pacific Northwest (458 line and load requests). For ERCOT the public figures read today are system totals in slide decks. For PJM they are forecast adjustments by transmission zone. For Georgia Power they are project rows with the place redacted. No public list by county or by utility was found for Texas, Virginia, Georgia, Ohio or Arizona.
2. **How long a load waits:** no public dataset of realized waits (request date to energization) for large loads was found. LBNL publishes such durations for generators and says large loads are in "separate queues" that its report does not include. The NYISO and BPA workbooks hold request dates and current status, which would allow a wait to be measured from successive copies of the files; no source read today has done so.
3. **One national file:** no single public, standardized, openly licensed dataset of large-load requests across operators was found. The nearest is interconnection.fyi, which is free to browse, covers 11 states under "Type: Load", reserves all rights and sells the export.
4. **Limits of this search:** one session, about thirty addresses on this topic. Not opened: utility filings other than Georgia Power's, MISO, SPP and CAISO materials, ERCOT's monthly working group postings, the EPRI and WECC reports themselves, and every paid product's contents. What this search supports is "we found no", not "there is no".

## 4. Addresses that could not be read today

| Address | What happened |
|---|---|
| `https://emp.lbl.gov/queues` | HTTP 403 to curl and to the fetch tool; the publication page on eta-publications.lbl.gov was read instead |
| `https://www.eia.gov/electricity/gridmonitor/about` | Text loaded by script; only the menu came back |
| `https://www.gridstatus.io/pricing`, `/terms`, `/api` | Page shell with no text to curl; the pricing page also returned HTTP 403 to the fetch tool |
| `https://portal.electricitymaps.com/datasets`, `https://docs.electricitymaps.com/` | HTTP 403 |
| `https://openei.org/wiki/Open_Energy_Data_Initiative_(OEDI)` | HTTP 503 |
| `https://zenodo.org/doi/10.5281/zenodo.3653158` and Zenodo's API | HTTP 403; the DOIs are quoted from the projects' own READMEs |
| `https://docs.singularity.energy/docs/open-grid-emissions` | HTTP 404 at the address tried |
| `https://www.ferc.gov/` news pages, two law firm pages | HTTP 403 |
