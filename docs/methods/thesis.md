# Thesis Builder: what the report is

Thesis Builder maps one niche for an investor. You type a niche on `/thesis`, with a stage and a geography if you want them, and press Run. Some minutes later the report is on the page, in tabs. This note says what each tab holds, where its numbers come from and what the placeholders mean.

The tool is internal. Runs and their results are kept in an internal table of the ERW. They are not published, not part of any public dataset, and the page has no download.

## The tabs

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

## What the report cannot tell you

- **It finds what is written down.** A company with no public trace, in stealth or with no press, is not found.
- **The landscape depends on the trends.** A real company in the niche that no source ties to one of the run's five trends is in the funnel, not on the map.
- **Two runs of the same niche are not identical.** Web search returns different pages on different days. Run a niche again if a company you expected is missing, and read the funnel.
- **A source can be wrong.** The report repeats what its sources say, with the link, so you can read the source yourself.
