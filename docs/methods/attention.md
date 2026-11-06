# The Attention Index and the Friction Index

The Attention Index says how much of a week's energy coverage a sector or a place got. The Friction Index says how much
of that coverage reported opposition: a moratorium or ban, a lawsuit, a protest, a permit denied, a fight over rates, an
elected official or government against a project, in whatever words the stories used. Both are counts of a model's
reading of each story's title and summary, by week, sector and place, from the first week the warehouse's news corpus
holds (January 2025). They measure what the feeds the ERW reads wrote about, not what happened, and not why.

- Code: `warehouse/derived/attention_classify.py` (the classification, one story at a time) and
  `warehouse/derived/attention_index.py` (the counting; no model touches a number)
- Input: `news_stories` (internal: titles and summaries of 43 feeds' stories, scored by the news scorer); nothing
  else is read and no request leaves the machine but the model call
- Output: `attention_story_links` (events, one row a classified story), `attention_index_weekly` and
  `friction_index_weekly` (series, `freq` `P1W`, `ts_utc` the Monday 00:00Z of the week); all three public, with no
  outlet text, as `news_index` is
- Page: `/attention`; the page's file `site/data/attention.json` and `site/public/attention/stories/<monday>.json`
  are written by the same run as the tables
- Tier: `model_extracted` (the classification is a model's; the indices are code over its rows)
- Test: `tests/test_session3401_attention.py` (the classification against 200 hand-labeled stories, offline) and
  `tests/test_session3402_attention_index.py` (the counting, every number worked by hand)

## What the model reads and answers

Each story is sent with its title and its summary (a sentence or two; the corpus holds no article body), in batches of
40, to a fixed model (`ATTENTION_MODEL`, Claude Sonnet 5.5 since session 3401's trial) with a JSON schema the API
enforces. It answers, for each story:

| Field | Values | What it means |
|---|---|---|
| sector | datacenters, transmission, gas, nuclear, solar_wind, storage, oil_lng, other_energy, not_energy | what the story is mainly about; `other_energy` holds coal, hydrogen, geothermal, hydro, rates in general, energy policy with no one sector, EVs; `not_energy` is not about energy at all |
| us | true, false | about the United States (a US place, a US company's US project, a federal or state action) |
| state | a postal code or empty | the one US state the story is mainly about; empty when none, several, or not US |
| place, place kind | a name, and county, city or metro | the county, city or metro the text names as the project's or dispute's place, as written |
| opposition | true, false | the story reports opposition to an energy or data center project, plant, line, pipeline, policy, permit, lease or rate |
| kind | moratorium, lawsuit, protest, permit_denied, rate_case, political_opposition, other_opposition, none | the main kind of opposition reported |
| tone | -1, 0, 1 | the story's tone toward what it covers: negative, neutral or mixed, positive |

Every answer is normalised by code (`norm_row`): a value outside the vocabulary is emptied or set to the neutral
value, never guessed, and the row's `fixed` column names what was changed; a state written in words becomes its code;
a state on a story not about the US is dropped; a kind without opposition becomes `none`. The prompt (`SYSTEM` in the
code) tells the model to answer only from the text and never to guess a place or an opposition the text does not state
or clearly imply (ERCOT implies Texas, CAISO California; PJM or MISO alone implies no state).

## How the indices are counted

A week runs Monday to Sunday, UTC, named by its Monday. A cell is a sector, a place and a week. The places are `all`
(every story, wherever it is about), `US` (the stories about the United States) and each state (the stories naming
that state). The sectors are the seven above and `energy` (any energy sector, `other_energy` included).

- **stories**: the cell's classified stories.
- **Attention Index** (`attention_index`, percent): the cell's stories divided by the week's **judged** stories, times
  100. A week's judged stories are the stories classified plus the stories the news scorer gave significance 0,
  which are not sent to the classifier (the scorer's rubric calls them not energy relevant) and are counted as not
  about energy. The denominators stand in the entity `attention:corpus:all` (`stories_week`, every story held;
  `stories_judged`; `stories_classified`; `stories_unsent_zero`).
- **tone_mean** (ratio): the mean of the cell's stories' tone, -1 to 1.
- **opposition_stories**: the cell's stories whose `opposition` is true.
- **Friction Index** (`friction_index`, percent): the cell's opposition stories divided by the cell's stories, times
  100. `kind_<kind>` counts each kind.

A cell with no story has no row. The page's "what rose" lists compare a week's Attention Index with the mean of the
four weeks before (a week without a row counting as zero); the builder writes those differences into the page's
file, so the page computes nothing.

Why a share and not a count: the feeds grew about twenty-fold in the last week of September 2026 (from about 100
stories a week to 1,800 to 3,100), so a raw count of stories is not comparable across the corpus. The count stands
beside the share in every cell.

## Accuracy, measured

Session 3401 drew 200 stories (seed 3400; 100 from stories whose text holds an opposition word, 100 from the rest),
labeled them by hand from their titles and summaries (`tests/fixtures/attention/labeled_200.csv`: 18 report
opposition, 99 are about energy, 84 about the US), and had both candidate models classify them. The test reads the
stored answers; no test calls a model.

| Field | Sonnet 5.5 (the model used) | Haiku 4.5 |
|---|---|---|
| opposition, yes or no | 0.985 | 0.975 |
| friction F1 on the 18 opposition stories (precision, recall) | 0.914 (0.941, 0.889) | 0.857 (0.882, 0.833) |
| kind of opposition | 0.985 | 0.950 |
| sector, all nine classes | 0.920 | 0.915 |
| sector, among the stories labeled in an index sector | 0.987 | 0.934 |
| about the US | 0.930 | 0.795 |
| state | 0.985 | 0.985 |
| tone | 0.870 | 0.725 |

Sonnet's two opposition misses are two stories of industry pressure undoing a European policy, labeled
`other_opposition` by the session, an arguable label; its one false positive is a Senate permitting deal. Tone is the
least reliable field. The 200 stories are a small set: a class with five or fewer labeled stories (lawsuit, protest,
moratorium, permit denied) has an accuracy that one story moves by twenty points or more.

Cost: USD 0.71 a thousand stories on Sonnet 5.5 (USD 0.29 on Haiku 4.5), measured on the 200, with the prompt cached;
every call is a row of `api_cost_ledger`.

A second measure, on 1,320 stories of the newest weeks that both models classified in session 3402 (Haiku's rows
from a run stopped when the model was found to be the wrong one; they are kept in `runs/c202/haiku_rows/`, not in any
table): the two agree on opposition for 98.9 percent of the stories (40 stories both call opposition, 6 only Sonnet, 8
only Haiku), on the kind for 97.5, on the state for 98.1, on the sector for 86.7 (most of the disagreement is
`other_energy` or `oil_lng` against `not_energy`), on the US field for 86.0 (Sonnet calls 678 stories US, Haiku 529)
and on tone for 73.3. Agreement is not accuracy; it says where a second reading would differ.

## What is classified, and what is not

- Stories are classified the newest first, under a cap of USD 3 a session (the owner's rule for this chain). The
  tables say, in the `attention:corpus:all` entity and in each table's header, how many of the week's stories were
  judged; a week whose judged stories are fewer than nine in ten of its stories is drawn hatched on the page, and its
  values are shares of the stories judged so far.
- Stories the news scorer gave significance 0 are not sent and count as not about energy in the denominators.
- A story is classified once; a later run classifies only the stories not yet in the link table or the raw files.

## Cross-checks

- **The tracer** (`warehouse/derived/attention_trace.py`) walks from any value of the two weekly tables to the rows of
  the link table behind it and checks by code that the rows add up to the value (stories, the Attention Index against
  the week's judged stories, the Friction Index against the cell's stories, each kind's count, the mean tone); `--all`
  checks every cell. It runs after every write of the tables.
- **Against the Digest's counts.** Each weekday Energy Digest states "from N scored stories" for its 24 hours. The
  corpus holds more scored stories for those same hours than the issue counted (for the 13 issues held on 6 November
  2026, the Digest's N is 60 to 75 percent of the corpus's count of scored stories published in its window; the gap is
  smallest on a Monday issue, whose window holds a weekend). The Digest counts the stories scored by the time of its
  issue; the scorer's later runs and backfills score stories of the same hours after the issue is written, and those
  are in the corpus the indices read. The two counts agree in direction week by week and are not the same measure.

## Limits, said plainly

- **One corpus.** The indices count the 43 feeds the ERW reads (the outlets' own feeds and Google News searches,
  `warehouse/news/feeds.yaml`), nothing else. A sector or a place a feed does not cover does not appear. Four outlets
  (Reuters, the Financial Times, Bloomberg and the Wall Street Journal) are three quarters of the rows.
- **English only.** The feeds are English-language; coverage in other languages is not read.
- **The feeds' own bias.** What rises in the index is what these outlets chose to write about and how Google News
  ranked it; the ERW adds a reading, not a correction.
- **Counts, not causes.** A rising Friction Index says more of the coverage reported opposition; it does not say
  opposition grew, nor that it mattered, nor why.
- **A title and a summary.** The model reads about 140 characters a story and no body: a place or an opposition
  stated only in the body is missed; a state is set for a small share of stories (17 of 200 in the labeled set).
- **A model's reading.** Every row is a model's; the accuracy above is measured on 200 stories and holds no better
  than that. The `fixed` column shows where code emptied an answer.
- **A week in progress** is partial and is drawn so; the feeds also date a few stories after the day they were read,
  which the tables keep as given.
- **No point of view.** The page and the tables say what the coverage did, not what anyone should do.
- **No record of the deciding bodies.** The indices read the news, not the agendas, minutes or dockets of planning
  commissions and siting boards; the probe of 6 November 2026 (`docs/reviews/local-permitting-estimate-2026-11-06.md`)
  found one machine-readable door (Legistar's web API, where a client switched it on) and two state docket systems
  that bar AI agents by name (`dis.puc.state.oh.us`, `apps.psc.wi.gov`), which the ERW does not read.

## Provenance

Each row of `attention_story_links` carries the story's outlet (`source`), its link (`source_url`), the model
(`model_id`), the prompt version and the time of the classification; each weekly row carries the method's address.
A reader goes from any index value to its stories through the page (every cell opens its list) or by joining the
weekly tables to the link table on sector, geo and week.
