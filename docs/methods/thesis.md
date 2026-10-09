# Thesis Builder: what the report is

Thesis Builder maps one niche for an investor. You type a niche on `/thesis`, with a stage and a geography if you want them, and press Run. Some minutes later the report is on the page, in tabs. This note says what each tab holds, where its numbers come from and what the placeholders mean.

The tool is internal. Runs and their results are kept in an internal table of the ERW. They are not published, not part of any public dataset, and the page has no download.

## Since 9 October 2026: the market is the ERW's work, the companies come from a connector

The owner's ruling of 8 October 2026. A run now studies the market of one niche: what it is, five trends each drawn with a real series, where capital goes, policy, risks, the incumbents its sources name, and timing. **The ERW does not search for companies.** The company landscape, the deal funnel, the pipeline, success stories and investors are filled from a data provider (PitchBook or Harmonic) once its answer is pasted; until then each of those tabs shows "Connect PitchBook or Harmonic to fill this" and the columns it will hold. The report is neutral: it describes the market and never argues which company or approach will win.

**A niche, not a sector.** The form refuses a sector ("geothermal", "oil & gas") or a market topic ("oil & gas demand") before anything is spent, and offers three to five narrower niches to click. A niche names what a startup sells, or to whom. A curated table answers the common broad inputs; for another input one small model call gives the narrower niches, and if it fails the rules decide alone. "Run anyway" starts the run all the same; the run is then marked "run anyway" beside its niche, with the reason on hover.

| Tab | What it holds (a run since 9 October 2026) |
|---|---|
| Scope and definitions | What the niche is, what is in scope and out, its sub-segments, the terms a newcomer needs |
| Trends | Five trends. Each has one sentence, its Fact, with its number, and one chart of a real series with the publisher's source line under it (the values themselves fold out below it). A trend that no real series measures says "no real series: not drawn" and has no chart |
| Capital | Where money goes, from public sources only: programs, grants, loans, project finance and announced rounds |
| Policy | The ERW's own policy actions (its policy monitor's tables) that bear on the niche |
| Risks | What could go wrong for the market, and what is not known |
| Incumbents | The established companies the sources name as active in the niche, and their role |
| Timing | Whether the market is still being installed (research, pilots, first demonstrations) or already deploying, with the evidence |
| References | Every source the report cites, with its link and the day it was read |
| Company landscape, Deal funnel, Pipeline map, Success stories, Investors | Connector tabs: "Connect PitchBook or Harmonic to fill this", with their columns. Once a PitchBook answer is pasted they hold its companies, every row labeled PitchBook's: the landscape all of them; the funnel each as sourced from PitchBook; the pipeline those at an early stage (seed to series B, grants, accelerators); success stories those acquired, merged or listed; investors each investor named and the companies of the answer it backed |

**The series a trend is drawn with.** The ERW's own tables first (its source tables of a monthly, weekly or annual interval); otherwise the U.S. Energy Information Administration's API. A small model picks, for each trend, the one series that measures it or the activity it is about, or none; a series about something else is never used to fill a gap. A series is drawn as its publisher gives it: every value as published, at its own frequency, never filled, smoothed or rescaled. The Fact sentence is written from the series' own numbers (or from the cited pages when there is no series) and every number in it is checked against those: a sentence holding a number no source holds is not shown, and the trend's cited claim stands in its place.

The publishers the ruling named and what was done with each (read 9 October 2026):

| Publisher | Used | Terms, word for word |
|---|---|---|
| EIA (api.eia.gov, API v2, with the ERW's key) | Yes | "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service. However, if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date, such as: "Source: U.S. Energy Information Administration (Oct 2008)."" (www.eia.gov/about/copyrights_reuse.php, SHA-256 28ef6560399ba7c7..., read 06:59:31 UTC). Every EIA chart's source line is written that way. api.eia.gov holds no robots.txt: every path answers with the API's own "No api_key was supplied" |
| Census (api.census.gov) | No | Its robots.txt allows the path, but the API answered "Missing Key" to a request without one, and the ERW holds no Census key. Its terms ask that a product using it say: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau." (www.census.gov/data/developers/about/terms-of-service.html, SHA-256 12659f08763e185b..., read 06:59:32 UTC) |
| BLS (api.bls.gov) | No | Its robots.txt reads "User-agent: *" and "Disallow: /", and www.bls.gov refused the request for its terms (HTTP 403) |
| FRED | No | Its API needs a key the ERW does not hold. FRED series the warehouse already holds would be drawn from the warehouse |

A run asks the EIA for at most five series (one request each, and its robots file), under a ceiling of 20 requests a run.

**Runs written before 9 October 2026** open as they always did: their company landscape, deal funnel and pipeline map are drawn exactly as before, with every PitchBook figure; their trends keep the table and chart they had. They have no Timing tab (it says so); their References tab lists the sources they cite; their Success stories and Investors tabs are connector tabs.

## The tabs of a run written before 9 October 2026

| Tab | What it holds |
|---|---|
| Scope and definitions | What the niche is, the terms a newcomer needs, its value chain, and the neighbouring niches kept out |
| Trends | Five numbered trends. Each has a Fact paragraph, a table and a chart drawn from that table |
| Company landscape | The companies on the map, each with the trends it serves and the reason it is there, in one sentence from a source |
| Deal funnel | Every organisation the run found, the stage of the funnel it reached, why it stopped there, its score, and where it was found |
| Pipeline map | The companies selected from the landscape, with founders, the signal that surfaced them, the route in, and the size of their market where a source gives one |
| Capital | Rounds, grants, project finance and acquisitions in the niche |
| Incumbents | The large players and public comparables, each with the one metric that matters |
| Risks | What could break the thesis, and what is not known |
| Policy | The ERW's own policy actions that bear on the niche |

## Where a number comes from

Every fact, row and figure carries the sources it rests on, as small numbered links. A source is either a web page the run fetched or a table of the ERW.

**A number is written only if it appears in a fetched source that its row cites.** A figure that could not be found there is not shown. Nothing is estimated to fill a gap, and nothing is smoothed.

## The placeholders

| On the page | Meaning |
|---|---|
| not disclosed | No fetched source gives this |
| not confirmed | A figure was offered but does not appear in a fetched source, so it is not shown |
| not held yet | The ERW has no source for this |
| PitchBook pending | Asked of PitchBook; shown when the PitchBook answer is submitted |

Each placeholder says why on hover.

## Which companies are on the map

A company is on the landscape when it is a private company, fits the stage and geography you asked for, and a fetched source ties it to at least one of the five trends. Its row says which trends and why.

An organisation that does not meet this is not dropped silently: it stays in the Deal funnel with the stage it reached and the reason it stopped, for example "outside the geography asked for" or "no fetched source ties it to one of the five trends".

Companies come from three places: the ERW's own companies and deals tables, web search, and PitchBook (below). The funnel says which for each.

## The confidence score

Each company has a score from 0 to 100 that says how well documented it is, with one line beside it saying what it rests on. A high score means several independent, recent sources agree and the company or an investor confirms its stage and funding. It is a measure of the evidence, not of the company's quality.

## PitchBook

The ERW cannot sign in to PitchBook and holds no PitchBook data of its own. A finished run shows a request: the companies it wants looked up, and a text to paste into a Claude chat that has your own PitchBook connector. That Claude returns the figures in a stated format, you paste its answer into the box on `/thesis`, and the report completes.

- Every figure from PitchBook is labeled "PitchBook" wherever it is shown, and is never mixed into a figure from another source.
- PitchBook's figures are shown as PitchBook returned them, through your own account. The ERW does not check them.
- They are kept with the run, in the internal table, and nowhere else.
- The key in the request works once, for that run only.

## Harmonic and Crunchbase

Since session 150 the same stage takes two more providers. In the panel of a finished run you choose the provider before copying the request: PitchBook (chosen when the panel opens), Harmonic or Crunchbase. The request text changes with the choice, and the answer box takes only the format of the provider chosen: given another provider's answer it stores nothing and says which format it was given.

- **Whose data it is.** As with PitchBook, the ERW signs in to neither and holds no data of theirs. What you paste is your own licensed copy, brought by you from your own account and shown to you. It is not published, not redistributed and not kept in the public warehouse: it is kept with the run, in the internal tables, and nowhere else.
- **The label.** Every figure a provider supplied stands with that provider's name. The label's hover says where the figure came from, the provider's own sentence on redistribution where its public terms could be read, the format, when the answer was pasted and the first characters of the hash of the pasted text. A figure with no provider keeps the label it has always had.
- **Where two providers differ.** When two providers give the same fact differently (total raised, the last round's date or amount, the post-money valuation, the headquarters, the founding year, the number of employees, the founders, the investors, the lead investors of the last round), each value is shown as its provider gave it and the lines are marked "differs". None is averaged, none is preferred and none is dropped. Descriptions and other prose are shown side by side and are not marked.
- **Which fields are read.** Only fields that the provider's own public documentation names, under its own names. Anything else in an answer is kept exactly as given, is not used for any figure, and is counted beside its company as "not mapped", with its names on hover.
- **Harmonic's amounts.** Harmonic's documentation does not state the currency of a company's total funding or last round, so those two are shown as the plain numbers Harmonic returned. Its valuations are documented as US dollars.
- **Crunchbase's employees.** Crunchbase gives a range, not a count. It is shown as the range and is marked as differing from another provider's count only when the count falls outside it.

## What the report cannot tell you

- **It finds what is written down.** A company with no public trace, in stealth or with no press, is not found.
- **The landscape depends on the trends.** A real company in the niche that no source ties to one of the run's five trends is in the funnel, not on the map.
- **Two runs of the same niche are not identical.** Web search returns different pages on different days. Run a niche again if a company you expected is missing, and read the funnel.
- **A source can be wrong.** The report repeats what its sources say, with the link, so you can read the source yourself.
