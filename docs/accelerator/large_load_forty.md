# The missing dataset, from ten entities to forty: one page for the letter

Session 141, 7 October 2026. Facts only. The table is internal and is not in this repository (which is public): it is
`warehouse/output/large_load_statements.csv` on the data machine, with every downloaded document and each pass's
files under `warehouse/raw/large_load_pilot/` and `warehouse/raw/large_load_statements/`. The rule is the pilot's
([`large_load_pilot.md`](large_load_pilot.md)): no number without its sentence; nothing summed across entities.

## What was done

- **Forty entities**, chosen before the search by the pilot's method (those believed to report the most datacenter
  load in public documents; not a ranking, which cannot be made across stages): the pilot's ten; SPP, California ISO
  (with the California Energy Commission's forecast it relies on), New York ISO, Bonneville Power Administration,
  Tennessee Valley Authority, Omaha Public Power District; and PPL, FirstEnergy, PSEG, AES, NiSource, DTE, Xcel,
  Ameren, Evergy, WEC, Alliant, CMS, Arizona Public Service, Salt River Project, Tucson Electric Power, NV Energy,
  PacifiCorp, Idaho Power, Portland General Electric, PG&E, NextEra (Florida Power & Light), CPS Energy, OGE, Black
  Hills. MISO is not among them: its site is not requested while its terms are under review.
- **Six research passes** by AI research agents on 7 October 2026: five on the thirty new entities, one back to the
  pilot's ten for the planning filings, testimony and forecasts the pilot did not reach. Each document was downloaded,
  each PDF read directly and the page recorded, each sentence checked by code as literal text of the document.

## What is held

| | The pilot (ten) | Now (forty) |
|---|---|---|
| Statements in the table | 49 (of 110 verified, five an entity) | **434** (every verified statement, once) |
| Entities with at least one statement | 10 | **38** (none for Salt River Project, whose site refuses a plain request, or for OGE Energy, whose documents state no megawatts) |
| Documents opened | 107 | **629** |
| Documents that yielded a usable figure | 45 (42 percent) | **184 (29 percent)** |
| Statements with the page of the PDF | none recorded by code | 270 |
| Statements from resource plans, load forecasts, commission filings, tariff filings or testimony | not counted | 189 of 434 |
| An agent's minutes searching and reading | 35 | 158 (about 4 an entity) |

## The stage vocabulary

Each entity's own stage words are kept, and placed beside them on one of five stages: **1** request or inquiry;
**2** study or engineering; **3** financial commitment (a construction letter, a deposit, collateral, an equipment
reservation); **4** signed service agreement; **5** under construction or energized; or **none** (a total across
stages, a forecast, a word that does not settle it).

- 164 stage words of 37 entities; 76 carry the document's own definition; 129 are placed on a stage, 35 on none.
- **Funnels that can be placed on the five stages: 15 of 40 whole, 16 in part** (some of the entity's words sit on
  none), 6 with one stage only, 3 not at all. No entity's own order runs against the stages' order.
- The placing is the collecting agent's reading of the document's words, not a person's review.
- Examples of why the words must be kept: Pacific Gas and Electric defines four stages by what was paid and signed
  (an application with a study fee; a work agreement with 10 percent of the project's cost; an interconnection
  construction agreement; construction) and recast its pipeline when it tightened them; Dominion's "contracted
  capacity" is mostly engineering letters, which it leaves out of its own forecast; Georgia Power's "commitments" join
  signed contracts and requests for service.

## How long a load waits

- **33 statements give a duration** (the pilot found one). Of them, **two are measured**, and both are one sentence
  of one utility: Oncor, in its rate case, "the average interconnection time for the 79 retail transmission
  interconnections that were placed in service from January 1, 2022, through December 31, 2024, was 825 days. The
  median time for those interconnections was 687 days."
  (`https://interchange.puc.texas.gov/Documents/58306_210_1533872.PDF`, page 64; all retail transmission
  interconnections, not only large loads, and only those finished). Asked for the time of each step, Oncor answered
  that it does not track it.
- Three more are an operator's general statement of experience (Bonneville: a system impact study "generally takes 6
  months"). The other 28 are targets, plans or expectations: a study promised in 90 days or 180, "several years"
  after an agreement, "3-5 years" assumed in a forecast.
- With the pilot's one (ERCOT's "average project delay of 180 days", a delay against the date requested), **three
  measured figures exist in the whole set, from two entities, both in Texas.** No entity publishes the wait of its
  large loads as data. New York's public queue of load requests prints no in-service date for any request.

## What a full national build would cost

Estimates from the rates measured here, not measurements:

- **Each collection, by agents:** about 6 minutes an entity including the files, so 70 entities are about 7 agent
  hours, under one hour of clock with six at once; about 1,100 documents opened.
- **Each collection, by a person:** the dockets an agent cannot reach (a CAPTCHA, a browser check or a list drawn by
  script was met at more than a dozen commissions and company sites among the forty), and a reading of the rows that are slide lines, chart
  labels or table rows (about a third): on the order of 20 to 25 hours.
- **Once:** a person's review of the stage words (164 so far), and each publisher's terms read and quoted before
  anything is published (none was read one by one; the table is internal for that reason): on the order of 25 hours.
- **Not buyable with hours:** the waits. They come only from successive copies of a queue kept over time, or from
  utilities and operators releasing them.
