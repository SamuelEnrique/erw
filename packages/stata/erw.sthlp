{smcl}
{* *! version 0.1.0  23oct2026}{...}
{viewerjumpto "Syntax" "erw##syntax"}{...}
{viewerjumpto "Description" "erw##description"}{...}
{viewerjumpto "Install" "erw##install"}{...}
{viewerjumpto "Options" "erw##options"}{...}
{viewerjumpto "Held tables" "erw##held"}{...}
{viewerjumpto "Examples" "erw##examples"}{...}
{viewerjumpto "Stored results" "erw##results"}{...}
{viewerjumpto "Citation" "erw##citation"}{...}
{title:Title}

{phang}
{bf:erw} {hline 2} The Energy Research Warehouse (ERW) in Stata: US power prices, demand, generation, fuel and
project tables, each row traceable to the report it came from


{marker syntax}{...}
{title:Syntax}

{p 8 17 2}
{cmd:erw tables} [{cmd:,} {opt clear}]

{p 8 17 2}
{cmd:erw coverage} [{it:table}] [{cmd:,} {opt clear}]

{p 8 17 2}
{cmd:erw fetch} {it:table} [{cmd:,} {opt ent:ity(list)} {opt var:iable(list)} {opt s:tart(time)} {opt e:nd(time)}
{opt back:end(name)} {opt clear}]

{p 8 17 2}
{cmd:erw cite} {it:table}

{p 8 17 2}
{cmd:erw license} {it:table}

{p 8 17 2}
{cmd:erw standard} {it:table} [{cmd:,} {opt back:end(name)} {opt clear}]


{marker description}{...}
{title:Description}

{pstd}
{cmd:erw} reads the tables of the Energy Research Warehouse with the six calls the ERW's Python and R packages share
(the specification: {browse "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/packages.md"}).
{cmd:erw tables} lists every table with its shape, interval, first and last time, rows, license verdict and whether
the live set holds it. {cmd:erw coverage} gives the coverage rows. {cmd:erw fetch} loads one table's rows, replacing the
data in memory. {cmd:erw cite} displays the citation. {cmd:erw license} displays the license verdict and its words.
{cmd:erw standard} lists the table's columns with their types and whether the ERW's data standard requires them.

{pstd}
Three places hold the tables:

{p2colset 9 22 24 2}{...}
{p2col:{cmd:redivis}}the record, in the Stanford dataset {cmd:datapages.erw:b9wm} (DOI 10.57761/4f55-6d55); set
{cmd:global REDIVIS_API_TOKEN} to a token from your Redivis account{p_end}
{p2col:{cmd:live}}the latest rows, a public subset (the price and demand tables for their last 35 days); set
{cmd:global ERW_LIVE_URL} and {cmd:global ERW_LIVE_KEY} (the ERW gives them on request){p_end}
{p2col:{cmd:local}}the CSV files of a folder; set {cmd:global ERW_DATA_DIR} to it{p_end}
{p2colreset}{...}

{pstd}
The live set and Redivis are read with {cmd:curl}, which Windows 10 and later, macOS and Linux carry, since Stata's
own {cmd:copy} cannot send the headers they ask for. The record files (the coverage table, the source registry, the
license record) are read from {cmd:global ERW_REPO}, a clone of the repository, or else from GitHub.


{marker install}{...}
{title:Install}

{pstd}
From the repository on GitHub (the files {cmd:stata.toc} and {cmd:erw.pkg} of {cmd:packages/stata}):

{phang2}{cmd:. net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace}{p_end}

{pstd}
Or from a clone: {cmd:adopath + "}{it:the clone}{cmd:/packages/stata"}. The do-file {cmd:examples.do} reproduces two of
the site's charts (the Grid tool's ERCOT demand, the price board's Henry Hub) and displays the figures each shows, so
they can be checked against the page.


{marker options}{...}
{title:Options for erw fetch}

{phang}
{opt entity(list)} keeps these entities, as the table writes them ({cmd:ercot:HB_NORTH}), or nodes as the grid
operator writes them ({cmd:HB_NORTH}); for an events table, these sources; for an entities table, these ids or names.

{phang}
{opt variable(list)} keeps these variables (a series), entity types (entities) or event types (events).

{phang}
{opt start(time)} and {opt end(time)} keep the rows whose interval starts in [start, end), in UTC, written
{cmd:YYYY-MM-DD} or {cmd:YYYY-MM-DDThh:mm:ssZ}. An entities table is filtered on {cmd:status_date}, an events table on
{cmd:event_date}.

{phang}
{opt backend(name)} is {cmd:auto} (the default), {cmd:local}, {cmd:live} or {cmd:redivis}. {cmd:auto} reads local
files when the table's CSV is in {cmd:$ERW_DATA_DIR}, else the live set when it holds the window asked for, else
Redivis.

{phang}
{opt clear} replaces the data in memory even when it has changed since it was saved.

{pstd}
The columns are typed as the specification says: a series' {cmd:value} is a double and {cmd:ts_utc} a {cmd:%tc} time
in UTC; an entities table's {cmd:lat}, {cmd:lon}, {cmd:capacity_mw} and every {cmd:*_mw} are doubles and every
{cmd:*_date} a {cmd:%td} date; an events table's {cmd:event_date} is a {cmd:%tc} time and {cmd:mw}, {cmd:price},
{cmd:significance} and {cmd:ai_power_relevance} doubles. Every other column stays text. From the live set, a table's own
extra columns arrive together in one text column, {cmd:extra}, as JSON.


{marker held}{...}
{title:Held tables}

{pstd}
A table whose license verdict is not {cmd:public} ({cmd:internal} or {cmd:unsettled}) is refused on the live set and
on Redivis, with the license's words (error 498), never with an empty dataset. Read from your own local files, it is
loaded with a note in the same words. {cmd:erw license} {it:table} says why.


{marker examples}{...}
{title:Examples}

{phang2}{cmd:. global ERW_LIVE_URL "the address the ERW gave you"}{p_end}
{phang2}{cmd:. global ERW_LIVE_KEY "the key the ERW gave you"}{p_end}
{phang2}{cmd:. erw tables, clear}{p_end}
{phang2}{cmd:. erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) clear}{p_end}
{phang2}{cmd:. tsset ts_utc, clocktime delta(1 day)}{p_end}
{phang2}{cmd:. erw cite eia_fuel_spot_prices}{p_end}
{phang2}{cmd:. erw license iso_rtm_hub_prices}{p_end}
{phang2}{cmd:. erw standard eia860m_retired_generators, clear}{p_end}


{marker results}{...}
{title:Stored results}

{pstd}
{cmd:erw fetch} stores {cmd:r(version)} (the version line: the table, where the rows came from, the fetch time and
the rows), {cmd:r(backend)} and {cmd:r(N)}, and the dataset's characteristics {cmd:_dta[erw_version]} and
{cmd:_dta[erw_license]}. {cmd:erw cite} stores {cmd:r(cite)}. {cmd:erw license} stores {cmd:r(verdict)},
{cmd:r(status)}, {cmd:r(status_from)}, {cmd:r(decided_by)}, {cmd:r(publishers)} and {cmd:r(words)}.
{cmd:erw standard} stores {cmd:r(shape)} and {cmd:r(key)}.


{marker citation}{...}
{title:Citation}

{pstd}
Cite the organization that published the data, then the ERW table and the Redivis version you read, in the
release's words: {it:the publishers}. {it:the reports}. Via the Energy Research Warehouse (ERW), table
{it:table}, Redivis dataset datapages.erw, version {it:tag} (released {it:YYYY-MM-DD}). {cmd:erw cite} writes it.


{title:Also see}

{pstd}
The ERW's Python package, {cmd:erw-energy}, and R package, {cmd:erw}, take the same six calls:
{browse "https://github.com/SamuelEnrique/erw"}.
