# The missing dataset, from forty entities to eighty, and how long a load waits: one page for the letter

Session 151, 8 October 2026. Facts only. The table is internal and is not in this repository (which is public): it is
`warehouse/output/large_load_statements.csv` on the data machine, with every downloaded document and each pass's
files under `warehouse/raw/`. The rule is the pilot's ([`large_load_pilot.md`](large_load_pilot.md), then
[`large_load_forty.md`](large_load_forty.md)): no number without its sentence; nothing summed across entities.

## What was done

- **Eighty entities**: the forty of session 141 and forty more, chosen before the search by the same method (not a
  ranking; `GROUPS` in the connector lists them): investor-owned utilities, public power systems, cooperatives and
  ISO New England, from California to Florida. MISO's site was never requested.
- **Eleven research passes** by AI research agents: eight on the new entities, and three hunts for every public
  statement of how long a large load waited or will wait (operators and federal bodies; state regulators; the first
  forty's own filings). 368 statements came back; each was proved a second time by separate code against the saved
  document (the sentence literal text, on the page given): 368 of 368.
- **13 bodies outside the eighty** state a figure (six regulators, two national laboratories, the Congressional
  Research Service, an association, a joint filing, two customers): each row is kept once, counted with no entity.

## What is held

| | Forty (session 141) | Now (eighty) |
|---|---|---|
| Statements in the table | 434 (401 megawatt figures, 33 durations) | **796** (596 megawatt figures, 200 durations) |
| Entities with at least one statement | 38 of 40 | **70 of 80**, 761 statements; 35 more from the 13 bodies outside |
| Documents opened | 629 | 1,688 |
| Documents that yielded a usable figure | 184 (29 percent) | 364 (22 percent) |
| Statements with the page of the PDF | 270 | 612 |
| An agent's minutes searching and reading | 158 | 129 more for the forty new entities (about 3 an entity) |

- **Megawatt figures by kind of document** (596): earnings presentations 104, resource plans 92, load forecast
  reports 91, commission filings 90, operator reports 73, earnings releases 36, tariff filings 26, SEC filings 19,
  rate case testimony 10, other 55. No sum across entities and no ranking: 228 sit on no stage (a total, a
  forecast, a threshold, a scenario) and 102 of the pilot's are not classed.
- **Ten entities with none.** Salt River Project (its site refuses) and OGE (no megawatts stated), as before; LADWP,
  Western Farmers, MidAmerican, Associated Electric and Oglethorpe (no large load figure in their public documents);
  Cleco (its site and docket refuse); Con Edison (none of its own); Avangrid (requests in MVA for every customer).

## The stage vocabulary

- 394 stage words of 72 of the eighty and 4 bodies outside (164 of 37 before); 232 carry the document's own
  definition; 330 are placed on one of the five stages, 64 on none. The collecting agent's reading, not a person's
  review. **Funnels of the eighty: 25 placed whole, 37 in part**, 5 with one stage only, 13 not at all.
- **One entity's own order runs against the five stages:** Grant County PUD takes its application fee, a financial
  commitment, before its study. Avista and El Paso Electric are marked the same way only because two ladders from
  two documents were recorded as one sequence: a person should split them.

## How long a load waits

- **171 distinct wait figures** in 200 statements of a duration: 28 held before, 143 new. One figure is one duration
  as written, about one entity, on one stage, for one kind of load; the same figure in two documents or two bodies'
  words counts once. Counts of statements only: no duration is added or averaged.
- **By stage:** request 13, study 66, financial commitment 3, signed agreement 3, construction to energization 43,
  none 43. **By basis:** 12 measured, 4 say what happened and write no duration, 35 general statements of experience, 120 expected.
- **Large loads against all distribution:** 160 against 11. The 11 are California's energization reports, which
  cover every distribution project and not large loads. Of the 160, 20 are not a load's wait (6 generation or
  equipment lead times, 10 a regulator's approval time, 4 a rate or a difference); **140 are a load's wait: 3
  measured**, 2 what happened, 28 general, 107 expected. 40 of the eighty entities state at least one figure.
- **The three measured waits of large loads, from two Texas entities.** Oncor (held): "the average interconnection
  time for the 79 retail transmission interconnections that were placed in service from January 1, 2022, through
  December 31, 2024, was 825 days", median 687 days. ERCOT (new): "all new large loads that had in-service dates
  from 2022 through 2024 were delayed in coming in service on average by approximately 220 days"
  (`https://interchange.puc.texas.gov/Documents/55999_121_1495046.PDF`, page 8, 1 May 2025). The same sentence says
  180 days is the delay ERCOT chose to apply: the 180 held since the pilot is an adjustment, 220 what happened.
- **Measured, all distribution projects (8):** Southern California Edison 480 and 235 business days; San Diego Gas &
  Electric 243 business days; Pacific Gas and Electric 427 and 129 calendar days, 950 and 1,285 calendar days for
  upstream capacity work, and 492 days for 23 projects that needed an upgrade. The twelfth measured figure is a
  regulator's approval time: PG&E's exceptional case filings "have taken approximately a year to resolve".
- **No utility, operator or regulator read here publishes the time from request to energization of its large loads.**

## What refused a plain request

- SEC EDGAR answered 403 to the project's contact string in every pass that tried; filings were read from the
  companies' own sites. Commissions: Ohio and Illinois (a robot check), North Carolina and Minnesota (403), Maine,
  Louisiana, Iowa and Virginia (lists by script). Sites: Cleco, TVA, Sempra, Duquesne Light, JEA. Nothing was forced.
- **For the owner to rule:** the Kentucky commission's public addresses for case documents hold a filer's work
  e-mail address as a folder name. 48 statements rest on such addresses (16 of them since session 141).

## What a quarterly collection would cost

Estimates from the rates measured here, not measurements:

- **By agents:** about 3 minutes of searching and 19 documents an entity, about 6 minutes with the files; eighty
  entities and the three hunts are about 10 agent hours, about an hour of clock; about 1,800 documents opened.
- **By a person, each time:** the dockets an agent cannot reach, and a reading of the rows that are slide lines or
  table rows: on the order of 25 to 30 hours. **Once:** a review of the 394 stage words, and each publisher's terms
  read and quoted before anything is published: on the order of 40 hours.
- **Not buyable with hours: a measured wait.** It comes from successive copies of a queue kept over time: the day a
  request enters a dated copy against the day it leaves energized. Grant County PUD and New York ISO publish a list
  of requests now; Pennsylvania's model tariff and ISO New England's proposal would add more. Keep every copy.
