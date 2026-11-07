# Coverage friction and project outcomes: notes toward a short paper, and three candidate findings

Session 3410 (chain 202), 6 November 2026, lab-desktop, fourth window. Everything here is a draft for the findings
hunt and for the owner's reading: nothing is approved, nothing is on the site, and every figure is from the tables
as written on 6 November 2026 (`attention_story_links`, `attention_index_weekly`, `friction_index_weekly`; the
classified weeks are listed in the first table below). The tables will grow as the next chain classifies the older
weeks; each finding names the rows it rests on so it can be computed again.

## What the tables hold today

8,120 stories classified of the 26,438 held (30.7 percent), the newest first, by Claude Sonnet 5.5 (sessions 3402 and
3403, USD 5.65 together); 5,025 of them about energy, 250 of those reporting opposition. The weeks:

| Week of | Stories held | Classified | Scored 0, unsent | Judged, percent of held | Energy stories | Reporting opposition |
|---|---|---|---|---|---|---|
| 2026-10-05 | 3,110 | 1,944 | 854 | 90.0 | 1,251 | 69 (5.5 percent) |
| 2026-10-12 | 1,954 | 1,438 | 516 | 100.0 | 925 | 53 (5.7) |
| 2026-10-19 | 3,146 | 1,920 | 1,226 | 100.0 | 1,292 | 54 (4.2) |
| 2026-10-26 | 2,342 | 2,299 | 43 | 100.0 | 1,207 | 42 (3.5) |
| 2026-11-02 (to the 6th) | 631 | 518 | 113 | 100.0 | 349 | 32 (9.2) |

The 94 weeks before 2026-10-05 (about 13,100 eligible stories) wait for the next chain. Five weeks are a short series:
every statement below is a cross-section of those weeks, not a trend.

## Three candidate findings

Each is a statement about the coverage the ERW reads, with its figure, the chart that would draw it and the link
table rows behind it (the rows are reachable on `/attention`: the cell's stories list, and by the tracer
`warehouse/derived/attention_trace.py`). None is a statement about the world.

### 1. Data center coverage carries more than twice the friction of energy coverage as a whole

- **Figure:** 90 of the 799 data center stories report opposition, a Friction Index of **11.3 percent**, against
  **5.0 percent** for all energy coverage (250 of 5,025). Solar and wind are the only other sector near it (22 of
  203, 10.8 percent); nuclear is 2.3 percent (6 of 264), gas 2.0 (8 of 393), storage 1.2 (3 of 258), oil and LNG 3.6
  (62 of 1,708), transmission 3.7 (10 of 270).
- **Week by week** the data center figure holds: 10.2, 9.0, 9.0 and 10.4 percent in the four full weeks (17, 15, 19
  and 20 opposition stories of 167, 166, 210 and 192), then 30.2 percent in the part week of 2 to 6 November 2026 (19
  of 63), the week of the ballot measures on data center moratoria in Texas, Georgia and Iowa.
- **What the opposition is:** protest 30, political opposition 25, other 12, moratorium 12, lawsuit 4, rate case 4,
  permit denied 3.

- **Chart:** the Friction Index by sector, one bar a sector, the "all energy" bar beside them, for the classified
  weeks; and the same by week, one line a sector, to show whether the gap holds week by week.
- **Link table:** `attention_story_links` where `sector = datacenters` (the opposition rows are those with
  `opposition = true`), against every row whose sector is an energy sector.
- **Caveat:** the ERW's feeds include four data center trade outlets (Data Center Dynamics, Data Center Knowledge,
  among them) whose beat is the industry; a trade outlet writes about siting fights more than a wire does. The
  finding is about the corpus.

### 2. Opposition is a US story: the Friction Index of US energy coverage is twice the rest of the world's

- **Figure:** 167 of the 2,463 energy stories about the United States report opposition, **6.8 percent**, against 83
  of 2,562 for the rest of the world, **3.2 percent**. By sector: data centers 14.7 percent in the US (450 stories)
  against 6.9 abroad (349); solar and wind 16.4 (122) against 2.5 (81); oil and LNG 5.7 (597) against 2.5 (1,111);
  transmission 4.3 (231) against none (39). The order reverses for gas (0.8 against 4.2) and nuclear (0.6 against
  4.8), where the opposition stories are European and Asian.
- **By state** (energy stories naming one state): California 156 stories, 5 opposition (3.2 percent); Texas 133, 2
  (1.5); **Virginia 25, 10 (40.0 percent)**; Michigan 22, 3 (13.6); New York 22, 1; Indiana 18, 0. Virginia's ten are
  the Dominion and NextEra merger hearings and the data center corridor's county fights.

- **Chart:** the Friction Index of the `US` entity against the `all` entity by sector (paired bars), and the states
  with the most energy stories with their Friction Index (a bar a state, the count written on it).
- **Link table:** `attention_story_links` where `us = true` against `us = false`, energy sectors only.
- **Caveat:** the feeds are US-first by design (`CLAUDE.md`: "Coverage is US first"); a US local fight reaches the
  corpus through Google News searches that a fight in another country does not. The model also sets `us` with 0.93
  accuracy. The finding says where the corpus's opposition stories are, not where opposition is.

### 3. The tone of nuclear coverage is the most positive of any sector; oil and LNG the only one below neutral

- **Figure:** mean tone (-1 to 1) by sector: **nuclear +0.62** (264 stories), storage +0.54 (258), solar and wind
  +0.44 (203), other energy +0.21 (1,130), gas +0.18 (393), data centers +0.11 (799), transmission +0.09 (270), **oil
  and LNG -0.07** (1,708). Taking the opposition stories out changes little (nuclear +0.64, data centers +0.22, oil and
  LNG -0.04): the sector gap is not the friction gap. Opposition stories average -0.69 against +0.18 for the rest.
- **Reading:** the corpus's nuclear stories are restarts, agreements and small-reactor announcements, written as
  successes; the oil and LNG stories are prices, attacks and outages, written as events. The tone field says how the
  coverage was written, not how the sector fared.

- **Chart:** the mean tone by sector (a dot a sector on a -1 to 1 axis), with the tone of the opposition stories and
  of the others marked separately (opposition stories average -0.67 against +0.23 for the rest, so the sector gap is
  not only the friction gap).
- **Link table:** `attention_story_links`, `tone` by `sector`.
- **Caveat:** tone is the classification's weakest field (0.87 against the hand labels); the finding needs the second
  pass's larger sample before it is more than a candidate.

## The outline of a short paper: coverage friction and project outcomes

**Question.** Does the friction a project's place draws in the news precede the project's outcome (cancelled,
withdrawn, delayed, permitted, built), and by how long?

**Outcomes.** The warehouse's own records: `datacenter_projects` (163 rows on 6 November 2026, with a
`project_status` of announced, under construction, applied, permitted, operating or cancelled and a `status_date`;
state set for a third, county for one in twenty) and `energy_deals` (529 rows, a state for one in ten; a deal is a
positive outcome for the asset it names). Both are model-extracted from the same news corpus, which is the paper's
first limit (below).

**Exposure.** The Friction Index of the project's state and sector in the weeks before the status date
(`friction_index_weekly`, entity `attention:datacenters:US-<state>`), and the count of opposition stories naming
the project's county or city (`attention_story_links.place`), as a lead of 4, 8 and 12 weeks.

**Design.** An event study around each status change (the ERW already has `warehouse/derived/event_study.py` for
grids): the Friction Index of the project's state in the 12 weeks before against the 12 weeks after, for cancelled
projects against permitted ones; then a simple hazard model of cancellation on the state's lagged friction, with the
state's attention (the volume of coverage) as a control, so that friction is not just more coverage.

**What would be new.** A weekly, place-level measure of reported opposition joined to a project registry, both open,
both traceable to the stories. The literature on siting opposition (surveys of residents, case studies of single
projects, counts of ordinances) has no weekly series by place.

**Limits, in the order a referee would raise them.**

1. **One corpus, two uses.** The outcomes (`datacenter_projects`) and the exposure (the Friction Index) are both
   read from the same news stories by models. A story that reports a cancellation and the opposition that preceded
   it feeds both sides at once. The paper must lag the exposure strictly before the outcome's first story
   (`first_story_at`) and should take outcomes from a second source (the permitting records of
   `docs/reviews/local-permitting-estimate-2026-11-06.md`, or the ISO queues' withdrawals) before any causal word.
2. **Coverage is not opposition.** The Friction Index counts stories that report opposition; a county with a lively
   local paper in the feeds will show more friction than a county without one, at the same opposition.
3. **Few outcomes.** 7 cancelled data center projects on 6 November 2026; the hazard model has no power until the
   registry grows or the queue withdrawals are joined (thousands of rows, with a state and an ISO each).
4. **Short series.** The indices hold the weeks the cap reached; the older weeks arrive with the next chain, and the
   feeds' growth in September 2026 means the early weeks hold about a hundred stories each, so a state-week cell is
   mostly empty before then.
5. **The classification's error** (opposition F1 0.91, state 0.985 on 200 labeled stories) is measured on a sample;
   a paper would relabel a second sample drawn from the study's own weeks and places.
6. **English, the feeds' bias, counts not causes,** as `docs/methods/attention.md` says.

**What to do first.** Join `datacenter_projects` (state, status, status_date, first_story_at) to
`friction_index_weekly` by state and week; draw the event-study chart for the cancelled projects against the
permitted ones; report the counts and the picture before any model. If the picture is empty, say so.
