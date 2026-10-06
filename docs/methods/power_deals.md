# Power deals: the deals tracker, version 3

Tables `power_deals` (public) and `power_deals_evidence` (internal), built by `warehouse/deals/extract_v3.py`. Page:
`/deals/v3`, in review. Session 130. Versions 1 and 2 (`/deals` and `/deals/v2`, table `energy_deals`,
`warehouse/deals/extract.py`) are untouched.

## What it is

Power deals as the news reported them: a specific transaction between named parties whose subject is electricity, or
an asset that generates, stores or transmits it. Six kinds: power purchase, tolling, offtake, project finance,
acquisition, other. Oil, LNG, pipeline and upstream gas deals, which version 2 kept, are not here.

**What is read is a title and a summary, not an article.** The ERW holds, for each story, the title and the summary its
feed gives (often the title again). It holds no article body, and this session pulled none. Of the 15,616
stories held, 117 name a figure in megawatts or gigawatts anywhere in those words, 23 a figure in megawatt-hours, and
none a price per megawatt-hour. That, not the schema, is the limit on what follows: a blank means the title and
summary did not say, not that the deal has no price.

## The rule: no number without its sentence

For every number (MW, MWh, the price and its unit, the term in years, the value in US dollars) the model must return
the words it read it from and the whole sentence. The code keeps the number only if all four hold:

1. the sentence is in one story's own title or summary (the stored sentence is the story's whole title, or the whole
   sentence of its summary);
2. the words are in that sentence;
3. the words state the number with its unit (MW or GW; MWh, GWh or TWh; a dollar sign; "year"; a price per MWh, kWh or
   kW-month) and parse to the same value, the unit applied and nothing looser;
4. the words are one number, not a range ("200 to 300 MW" is left blank).

Otherwise the number is blank and the run log says why. A euro, pound or other figure is never turned into dollars. A
term in months is not turned into years. The word before a number that limits it ("up to", "about", "more than",
"nearly") is kept beside it. After the tables are written the rule is checked again on the tables themselves
(`no_number_without_its_sentence`): the build fails if any number has no sentence in a story held.

The sentences are outlet text and stay in the internal table (`field`, `value`, `text`, `sentence`, `story_id`). The
public table and the page carry the number and a link to the story it was read from.

Of 187 numbers the first read gave, 179 passed these checks. 115 are in
the table: the rest belonged to deals the second read turned away, were the same figure in a second report of one
deal, or were figures the second read found were not the deal's own (3).

## Two reads

**The first read** (claude-sonnet-5-5, low effort, JSON schema) takes stories by cluster, 20 to 40 clusters a call, and
returns the power deals with every field above. It returned 389 deals. 13 were not
kept because the story's words held no party they named.

**The second read** (the same model, medium effort) takes each of those deals alone with its own stories and answers:

- is this a specific power transaction (`power_deal`), a transaction the words do not show to be about power
  (`not_power`), or no transaction (`not_a_transaction`)? 264, 76 and
  36. Only the first enters the table;
- the kind (it changed 7);
- whether the story states who buys and who sells. Where it does not (partners, a joint venture), the names are kept
  as parties with no side: 74 deals;
- whether the words say the power serves datacenters or AI (the flag changed for 13);
- any figure that is not the deal's own, such as a programme's total (3 blanked), and any
  name that is not a party, such as the backer in "Blackstone-backed X" (18 removed).

The second read was added, and then tightened, because of the hand checks below. The kind, the technology and the
datacenter flag are the model's reading of the words, not a copy of them; names, places and numbers are copies and are
kept only when the story's words hold them.

## One deal, several reports

Stories about one event (the news scorer's clusters) are read together and make one deal. Deals from different
clusters are folded into one when the kind is the same, their dates are within 60 days, no figure both state differs,
and one of these holds: the same named parties, two or more; a party in common and a figure in common; or, within 3
days, a party in common, one report naming no other party, and the same technology stated by both. The earliest is
kept with every story linked, and a number it lacks is filled from the other with its own sentence. 21
were folded. The table holds 242 deals: acquisition 67, other 60, project finance 58, power purchase 53, offtake 3, tolling 1. By technology (a deal may name two): nuclear 33, storage 28, gas 24, solar 20, wind 8, fuel cell 8, geothermal 6, transmission 6, hydro 3, hydrogen 3, other 2.

## What was read

Every story held, in this order, under a cap of USD 8 for the session. The spend was USD 4.27 in 539
calls, so the cap was not reached and 0 stories remain unread.

| Order | Stories | Held | Read | Remain |
|---|---|---|---|---|
| 1 | read by version 2 | 1,884 | 1,884 | 0 |
| 2 | scored, a power sector or the words of a deal | 4,214 | 4,214 | 0 |
| 3 | not scored, the words of a deal | 1,327 | 1,327 | 0 |
| 4 | scored, the rest | 4,999 | 4,999 | 0 |
| 5 | not scored, the rest | 3,192 | 3,192 | 0 |

## Against version 2

Version 2 read 1,884 stories (nine sectors, significance 5 or more) and asked for fourteen types of
energy deal. Version 3 asks for power deals only and read every story. The middle row is version 3 on the stories
version 2 read. A size is megawatts or megawatt-hours.

**Every deal**

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value in US dollars |
|---|---|---|---|---|---|---|---|
| 2 | 413 | 12 | 11 | 1 | 2 | 10 | 223 |
| 3, the stories version 2 read | 87 | 12 | 11 | 1 | 0 | 4 | 35 |
| 3, every story read | 242 | 30 | 25 | 6 | 0 | 9 | 75 |

**Storage** (version 2: the words battery or storage in its technology or asset; version 3: technology storage)

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value in US dollars |
|---|---|---|---|---|---|---|---|
| 2 | 3 | 0 | 0 | 0 | 0 | 0 | 2 |
| 3, the stories version 2 read | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3, every story read | 28 | 8 | 4 | 5 | 0 | 2 | 2 |

**Datacenters** (each version's own flag)

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value in US dollars |
|---|---|---|---|---|---|---|---|
| 2 | 172 | 5 | 5 | 0 | 0 | 2 | 103 |
| 3, the stories version 2 read | 31 | 5 | 5 | 0 | 0 | 2 | 9 |
| 3, every story read | 78 | 9 | 9 | 0 | 0 | 5 | 20 |

How to read it:

- **On the same stories the two versions find the same sizes.** Version 2's 12 sizes are all in version 3. The gain
  in sizes comes from reading the stories version 2 never read (storage, renewables and the unscored stories).
- **Version 2's two prices were not power prices** (a price per share in Canadian dollars, and an 80 percent equity
  share). No title or summary held states a price per MWh, so version 3 holds none.
- **Six of version 2's ten terms are LNG supply deals.** The four that are power deals are in version 3, with five more
  from the wider reading.
- **Version 2's datacenter flag was looser**: it marked datacenter financings and leases with no power in them, which
  version 3 does not keep.

## Twenty read against their stories, three times

Read by the session's model (Claude), not by a person, against the titles and summaries held: the ERW holds no article
body to read against. Each sample is twenty deals drawn at random from the table as it then stood
(`runs/session130/sample20.py`, seeds 130, 131, 132). The first two led to changes; the third is the measure.

| Sample | Table then | Not a power deal reported by the story | Numbers shown, wrong | Other fields wrong |
|---|---|---|---|---|
| 1 (seed 130) | 270 deals, one read | 1 of 20 | 10, none wrong | sides not stated by the story in 3; kind 1; datacenter flag 1; and one deal twice in the table |
| 2 (seed 131) | 264 deals | 4 of 20 (two investment firms raising their own funds, one deal mentioned in passing, one sale of "energy assets") | 13, one not the deal's own (a "$5 billion push") | buyer 1 (the backer in "Blackstone-backed"); technology 2 |
| 3 (seed 132) | 242 deals, the table as built | **1 of 20** (a wind farm sale mentioned in a story about compensation) | **8, none wrong** | **sides 1, kind 1, datacenter flag 1, status 1**; technology and place none |

In the third sample 5 of the 20 deals carry at least one wrong field, and 5 of 148 judgments are wrong (20 deals by
seven fields, and 8 numbers): 3.4 percent. No number shown was wrong in any sample for its value: every one is in its
sentence. The one figure that misled was a true figure of something else, which the second read now asks about.

What the third sample also showed, and was fixed in code with no further model call: the limiting word was missed when
the model's words began with it ("about $1 billion"), and a folded deal could list a party twice. And one thing not
fixed: the second read blanked a figure that was the deal's own, where two stories gave two values for one deal
(USD 16.4 billion and USD 27 billion, the price with and without debt). A blank is the safe side of that error.

## What this does not tell you

- What an article says below its summary: most sizes, nearly every term and every price.
- How many deals were struck: this is what a set of feeds reported and a model read.
- A market total: the megawatts are a sum over the few deals that state them, of every kind together.
- Whether a deal closed: the status is the story's word on the day of the story.

## Files

| File | What |
|---|---|
| `warehouse/deals/extract_v3.py` | `plan`, `run` (the first read), `confirm` (the second read), `build` (the tables, no model) |
| `warehouse/deals/answers_v3.jsonl`, `second_read_v3.jsonl` | every answer as the model returned it; `build` needs nothing else |
| `warehouse/deals/checked_v3.csv` | every story read, with its tier and the number of deals it carries |
| `site/data/deals_v3.json` | the page's copy: public fields only, and the comparison above |
| `tests/test_session130.py` | the checks on real stories, the fold, the second read, and the rule on the tables rebuilt from the answers |
