# A reader's guide to the Energy Research Warehouse

Energy Research Warehouse (ERW), session 445, 21 October 2026. For a reader outside the project: what the ERW is, how to cite it, how to get a table and read it, how to rerun a page's figure, what the licenses mean, how to report a fault, and the Python package. Every path below is in the repository `https://github.com/SamuelEnrique/erw` on `main`; every site address is a route of `site/app/` on `main`. `tests/test_session445.py` checks that each repository path and site route exists.

## What the ERW is

The ERW is a warehouse of public energy data: prices, flows, projects, deals and policy across US power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets. Each source is pulled by one connector (`warehouse/connectors/`) and reshaped into one of three table shapes, `series` (one row an observation: `entity, variable, ts_utc, value`), `entities` (one row a physical or corporate thing) and `events` (one row a deal, filing or announcement), so that tables from different publishers join (`docs/datastandard.md`). Times are UTC; power is MW and prices are USD per MWh unless a `unit` column says otherwise. Every table opens with a provenance header naming the source report, its address and when it was retrieved, and passes one validator before it is published (`warehouse/validate/erw_validate.py`). The ERW is a Stanford student research project; nothing it shows is investment advice (`site/app/terms/page.tsx`). Its infrastructure is adapted, with permission, from the Item Response Warehouse (`docs/redivis/release-v1/README.md`, "Credit").

## Where things are today

- **The store of record is Redivis**, dataset `energy_research_warehouse` (`warehouse/redivis/config.yaml`), at `https://redivis.com/datasets/05yh-65frzyhaz` (`site/data/site.json`). **Version 1 is pending release**: no version has been released, and the dataset was not open to the public when the site last read it (`site/data/site.json`, `"released": false`, checked 2026-09-26). A version is released only by a person, after reading what the draft changes (`warehouse/redivis/README.md`, "The rule"; the steps in `docs/redivis/release-v1.md`).
- **The site is `https://erw-flame.vercel.app`, and every page is in review** (`site/lib/release.ts`): a visitor who asks for a page sees a short in-review page at the same address. The download route `/api/download` and the files of `site/public/` are outside that curtain (`site/proxy.ts`, its `matcher`), so the addresses in the two sections below answer a visitor; the pages that link them, such as `/data`, do not open until they leave review.
- **The code, the methods and the session reports are public on GitHub**: `https://github.com/SamuelEnrique/erw`.

## How to cite it

Cite the organization that published the data first, then the ERW table and the Redivis version you read (`docs/redivis/release-v1.md`, "How to cite v1"):

> \<the publisher\>. \<the report\>. Via the Energy Research Warehouse (ERW), table `<table>`, Redivis dataset `energy_research_warehouse`, version v1 (released YYYY-MM-DD).

For example (`docs/redivis/release-v1/README.md`, "How to cite"):

> U.S. Energy Information Administration (EIA). Spot prices. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, Redivis dataset `energy_research_warehouse`, version v1.

- Each table's own citation line is the column `citation` of `docs/redivis/release-v1/tables.csv`.
- The draft has no version number and is not citable (`warehouse/redivis/README.md`, "How to cite it"). Until version 1 is released, cite the table, the ERW's data commit and the date you read it: `erw.cite("<table>")` writes exactly that (below).
- The numbers belong to the publishers. A table whose tier is `model_extracted` (a field written by a model reading news, filings or the web: `energy_deals`, `datacenter_projects`, `datacenter_facilities`, `policy_reads`, `energy_companies`) is cited with the source each row links, and its figure called model-extracted (`package/llms.txt`, section 5).

## How to download a table and read it

### From the site: `/api/download`

`/api/download?table=<table>` answers one public table of the site's live set as CSV (`site/app/api/download/route.ts`):

- The file opens with the table's provenance header as lines beginning with `#`, then the column names, then the rows in the table's own column order.
- The live set keeps a window of some tables (the last 35 days of ISO prices and EIA-930, `package/llms.txt`, section 6), and the file holds that window; the full history is on Redivis.
- At most 500,000 rows a file, and 60 downloads an hour a visitor; past either, the route answers an error, never a file that looks whole.
- A table held for a license answers 403 with the words "held: license needed" and its publishers; a table that is not public, or not in the live set, answers 404 and names Redivis.

The same route writes a reader of that CSV, the two readers every page's downloads line offers (`site/components/tool/TableDownloads.tsx`):

| Reader | Address | What it does |
|---|---|---|
| Python | `/api/download?table=<table>&as=py` | fetches the CSV, prints the `#` lines, loads the rows with pandas into a frame named after the table; no number is computed |
| Stata | `/api/download?table=<table>&as=do` | copies the CSV to a temporary file, counts the `#` lines and imports the rows with `import delimited`, the column names from the first line after them |

**R.** No page offers an R reader: the route writes Python (`as=py`) and Stata (`as=do`) only, and no file of the site holds R code. This guide gives no R lines, because none has been run against the route. The one thing any reader must do is the readers' own first step: skip the leading lines that begin with `#`, then read the CSV. Do not do it with a comment character on the whole file, which would also cut a value that holds `#` (an address, for example).

On `/data`, once it leaves review, each public table has the same "Download CSV" link, "Held: license needed" in its place for a held table, and a link to Redivis for a table not in the live set (`site/app/data/page.tsx`).

### From Redivis

Every table, with its full history, is in the Redivis dataset, and the tables not in the site's live set are only there (`warehouse/redivis/README.md`). Each Redivis table's description is its provenance header (cut at 2,000 characters; every header line in full in the table `erw_headers`), and the dataset also holds `erw_coverage` and `erw_sources`. Reading it needs a Redivis account and, until version 1 is released, the dataset's access.

### From the repository

A clone holds the code and the news tables, not the other tables, which are made by running their connectors (`README.md`). The Python package below reads a clone's tables, Redivis or the site's live set.

## How to rerun a page's figure

Four pages and the Research cards carry a replication package: a CSV of the page's inputs as the page read them, a Stata do-file and a Python file that rebuild the page's headline figures of the default case from that CSV alone, standard library only (numpy for Research). Each is in the repository under `site/public/` and served at the same path under the site:

| Page | Files, under `site/public/` | Method |
|---|---|---|
| What a battery earns, `/cost-of-power/battery` | `battery/erw_2026_battery_dispatch.csv`, `battery/erw_2026_battery_replication.do`, `battery/erw_2026_battery_replication.py` | `docs/methods/battery_earns_algorithm.md` |
| What a generator earns, `/cost-of-power/seller` | `seller/erw_2026_generator_hourly.csv`, `seller/erw_2026_generator_replication.do`, `seller/erw_2026_generator_replication.py` | `docs/methods/cost_of_power.md`, `docs/methods/generator_earns_algorithm.md` |
| What a datacenter pays, `/cost-of-power` | `datacenter/erw_2026_datacenter_hourly.csv`, `datacenter/erw_2026_datacenter_carbon.csv`, `datacenter/erw_2026_datacenter_replication.do`, `datacenter/erw_2026_datacenter_replication.py` | `docs/methods/datacenter_pays_algorithm.md` |
| The Grid tool, `/grid?view=network` | `grid/erw_2026_grid_replication.csv`, `grid/erw_2026_grid_replication.do`, `grid/erw_2026_grid_replication.py` | `docs/methods/grid_network.md` |
| Research's cards, `/research` | one `.do` and one `.py` a card, the cards' `erw_2026_*.csv`, and `findings/erw_2026_research_replication.py` for all nine | `docs/methods/automated_analysis_findings.md` |

To rerun one, put the CSV and the file in one folder and run it:

```bash
python erw_2026_battery_replication.py erw_2026_battery_dispatch.csv
python erw_2026_research_replication.py <folder of the cards' CSVs>
```

or `do erw_2026_battery_replication.do` in Stata. Each file's first lines say the default case it rebuilds (the battery's: ERCOT, a 4-hour battery, perfect foresight, 100 MW) and which figures it prints; the figures should equal the page's at its bare address, the default case. A page's other inputs (another grid, another duration) are not in its replication.

## How the licenses work, and what "held" means

- **Every table is `public` or `internal`** (`warehouse/metadata/coverage.csv`, column `license`; on 21 October 2026, 179 public and 33 internal of 212). An internal table is licensed for internal use only (PJM data, CARB, RGGI, the IMF series through FRED, PortWatch, the text of `news_stories`): it is never on the site or in the public Redivis dataset, and must not be republished (`warehouse/redivis/README.md`; internal tables go to the private dataset `energy_research_warehouse_internal`). A table the ERW derives takes the most restrictive license among its inputs.
- **The license record** is `docs/licenses.md`: for each publisher, the one sentence of its own page that allows or forbids redistribution, as an ERW session read it, with a verdict "as the ERW is today" (an open research project that sells nothing) and "if the ERW sells anything". It is a reading, not legal advice.
- **"Held: license needed".** A table flagged public whose publisher's own page asks for permission or a license is held from 21 October 2026 unless a permission is recorded: 42 tables, the rows of `warehouse/metadata/license_status.csv` (none with a permission recorded on 21 October). The publishers that decide most of them are NYISO, ISO-NE and MISO, and for the datacenter and deals tables the news outlets and companies their rows cite (`docs/licenses.md`, "Read these first"). A held table is not offered on any page or by `/api/download` (`site/lib/license.ts`), and is out of Redivis version 1 (`docs/redivis/release-v1/tables.csv`, `in_v1 = no`, each with its reason). It stays in the warehouse; it is held, not deleted.
- **"Held: Redivis storage"** is the other hold of version 1: a table in it by license that the account's storage could not take yet (`in_v1 = held` in `tables.csv`).

## How to report a fault

- **Known faults in source data** are in the register `warehouse/faults/faults.yaml` and on the page `/data/faults` (`site/app/data/faults/page.tsx`): what the publisher's data hold that is wrong, missing or shifted, when, in which tables, and what the ERW does about it. Read it first: a fault may be known.
- **The site has no fault form.** The one form that reaches a person is the question form on `/research`: Samuel Enrique, who runs the ERW, reads each question and answers by email within a week (`site/app/terms/page.tsx`, the section on Research). Until a fault address is named, a fault can be sent there, with the table, the row (its key: `entity, variable, ts_utc` for a series), the value you expected and the publisher's page that states it.
- The repository is public; whether faults are taken as GitHub issues was not checked by this guide.

## The `erw` package in ten lines

```python
# pip install "git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"   (pandas is the only dependency)
import erw                                       # ERW_BACKEND=local (a clone's tables), redivis or supabase (the site's live set)
erw.info()                                       # what the warehouse holds, and the data commit read
erw.filter(sector="power", license="public")     # table names; never show an internal table
df = erw.fetch("eia_fuel_spot_prices", start="2026-09-01", end="2026-09-08")
df.attrs["erw"]["sources"]                       # the source report(s) behind the rows
erw.sources("eia_fuel_spot_prices")              # report pages and every file address
erw.tier("energy_deals")                         # source, derived or model_extracted
print(erw.cite("eia_fuel_spot_prices"))          # the publisher's report, then the ERW table and data commit
erw.version()                                    # which data you read: give it with any result
```

Every line above was run in a new virtual environment in session 536, on a clone's tables and on the live set with the anon key, and each exited 0 (`archive/sessions/SESSION_536_REPORT.md`). `ERW_BACKEND` counts from the first call since that session (`package/src/erw/api.py`, `get_backend`). The live set's address and anon key are not published (the site reads them on its server only, `docs/reviews/2026-10-10-security.md`), so a reader outside the project reads a clone's tables, or Redivis once its dataset is open.

The functions and the backends' keys are in `package/README.md`; for an AI assistant, `package/llms.txt` says which table answers which question and which reads silently go wrong.

## Where this guide comes from

| Section | Read from |
|---|---|
| What the ERW is | `CLAUDE.md`, `docs/datastandard.md`, `site/app/terms/page.tsx`, `docs/redivis/release-v1/README.md` |
| Where things are today | `site/data/site.json`, `warehouse/redivis/config.yaml`, `site/lib/release.ts`, `site/proxy.ts` |
| How to cite | `docs/redivis/release-v1.md`, `docs/redivis/release-v1/README.md`, `warehouse/redivis/README.md`, `package/src/erw/api.py` (`cite`) |
| Downloads and readers | `site/app/api/download/route.ts`, `site/components/tool/TableDownloads.tsx`, `site/app/data/page.tsx` |
| Replication | `site/public/battery/`, `site/public/seller/`, `site/public/datacenter/`, `site/public/grid/`, `site/public/findings/`, each file's own first lines |
| Licenses | `docs/licenses.md`, `warehouse/metadata/license_status.csv`, `warehouse/metadata/coverage.csv`, `site/lib/license.ts` |
| Faults | `warehouse/faults/faults.yaml`, `site/app/data/faults/page.tsx`, `site/app/terms/page.tsx` |
| The package | `package/README.md`, `package/llms.txt`, `package/src/erw/api.py` |
