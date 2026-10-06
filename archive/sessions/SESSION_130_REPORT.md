# Session 130 report: the deals tracker, re-aimed at power deals

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October). This session pushed `wip/130-deals-v3` only, deployed nothing, and loaded nothing into the live set. The branch is from main (`e33f4e0`) and builds on no other. When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/130-deals-v3 && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-130
git push origin wip/130-deals-v3 && git push origin wip/130-deals-v3:task/130-deals-v3
python runs/session118/watch_run.py task/130-deals-v3 15
node site/scripts/snapshot-live.mjs take after-130 && node site/scripts/snapshot-live.mjs compare before-130 after-130
cd site && node --import ./scripts/alias-loader.mjs scripts/check-deals-v3.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/130-deals-v3
```

- **What the comparison should show on the three open pages: nothing but the clock.** The page is `review` and not in the menu; `power_deals` is under `catalogue_hold` and is not loaded; `power_deals_evidence` is internal. The page reads its own file (`site/data/deals_v3.json`), not Supabase.
- **If the merge conflicts**, it is in the generated metadata the daily run rewrites (`coverage.csv`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`, `docs/coverage.md`). Take main's copy and run, under the lock: `bash runs/session130/build_writes.sh` (it rebuilds the two tables from the answers in git with no model call, then validator, coverage, archive, Redivis draft).
- **Nothing here touches what the three live tools read.** No table of theirs was written; version 1 and version 2 of the tracker (`energy_deals`, `/deals`, `/deals/v2`) are as they were, and a test says so.

## Verdict: not ready to open as the tracker you described; sound as a list

**The extraction does what you asked and the rule holds: no number is stored without its sentence. But the articles held are titles and summaries, and they do not state what the tracker is for.** Of 242 power deals, 30 state a size, 9 a term, and none a price. A better schema cannot fix that: across all 15,616 stories held, 117 name a megawatt or gigawatt figure anywhere in their words, 23 a megawatt-hour figure, and not one a price per megawatt-hour.

Exactly what is left:

1. **Your ruling on the source of figures.** Sizes, terms and prices are in article bodies, which the ERW does not hold and this session was not allowed to pull. The choices: (a) fetch bodies for the 242 stories' links, which is a pull and a licensing question per outlet; (b) add feeds whose summaries are sentences of the article, not the title again (Energy-Storage.news is the first outlet of 12 of the 242 deals and gave 6 of the 30 sizes; Reuters, held as titles only, is the first outlet of 83 and gave 11); (c) accept the list as it is and send readers to `/contracts` (FERC's filed prices) for price.
2. **Your ruling on showing the sentence.** Every number has its sentence in the internal table. The page shows the number and a link to the story, not the sentence, because outlet text is internal by the house rule. One quoted sentence per number, with its outlet and link, would make the page much stronger; it is your call.
3. **A person's read of a sample.** My hand check found 1 deal in 20 that the story did not really report, and 5 in 20 with a wrong field (none of them a number). Details below.
4. **Keeping it current.** `extract_v3.py` is not in the daily run. A day's new stories would cost about USD 0.03 to read; it needs your approval as a standing model spend.
5. **Which page is the tracker.** `/deals`, `/deals/v2` and `/deals/v3` now all exist in review.
6. Smaller: the deals table scrolls sideways at laptop width (nine columns); no look on a phone.

## Read these first

1. **Everything was read, well under the cap.** All 15,616 stories, USD 4.27 of USD 8.00, 539 calls, none failed. **No article remains.**
2. **On the stories version 2 read, version 3 finds the same sizes: 12 and 12.** Version 2 was not missing figures that were there. The gain (30 sizes) comes from reading the 13,732 stories version 2 never read.
3. **Version 2's two "prices" were not power prices** (C$12 per share; an 80 percent equity share), and 6 of its 10 terms were LNG contracts. Version 3 holds neither.
4. **I added a second read, which you did not ask for.** My first hand check showed the first read letting through things that are not deals. Each deal is now read again alone; 112 of the 376 it read were turned away (76 not about power, 36 no transaction). It cost USD 0.82 of the 4.27, three passes in all because I tightened it twice after hand checks.
5. **The hand check was mine, not a person's, and against titles and summaries, not articles.** There are no article bodies here to read against.

## What was read

| Order | Stories | Held | Read | Remain | Deals in the table from it |
|---|---|---|---|---|---|
| 1 | read by version 2 | 1,884 | 1,884 | 0 | 86 |
| 2 | scored, a power sector or the words of a deal | 4,214 | 4,214 | 0 | 58 |
| 3 | not scored, the words of a deal | 1,327 | 1,327 | 0 | 56 |
| 4 | scored, the rest | 4,999 | 4,999 | 0 | 1 |
| 5 | not scored, the rest | 3,192 | 3,192 | 0 | 41 |
| | **All** | **15,616** | **15,616** | **0** | **242** |

Model `claude-sonnet-5-5`. First read: 479 calls, USD 3.44. Second read: 60 calls, USD 0.82. **Session total USD 4.2656**, every call in the cost ledger under session 130.

(Version 2's 1,765 eligible stories are 1,884 here because a story in the same cluster as one of them is read with it.)

## Against version 2

A size is megawatts or megawatt-hours. The middle row is version 3 on the stories version 2 read.

**Every deal**

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value, USD |
|---|---|---|---|---|---|---|---|
| 2 | 413 | 12 | 11 | 1 | 2 | 10 | 223 |
| 3, the stories version 2 read | 87 | 12 | 11 | 1 | 0 | 4 | 35 |
| 3, every story read | **242** | **30** | 25 | 6 | **0** | **9** | 75 |

**Storage** (version 2: the words battery or storage in its technology or asset; version 3: technology storage)

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value, USD |
|---|---|---|---|---|---|---|---|
| 2 | 3 | 0 | 0 | 0 | 0 | 0 | 2 |
| 3, the stories version 2 read | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3, every story read | **28** | **8** | 4 | 5 | 0 | 2 | 2 |

**Datacenters** (each version's own flag)

| Version | Deals | State a size | in MW | in MWh | State a price | State a term | State a value, USD |
|---|---|---|---|---|---|---|---|
| 2 | 172 | 5 | 5 | 0 | 0 | 2 | 103 |
| 3, the stories version 2 read | 31 | 5 | 5 | 0 | 0 | 2 | 9 |
| 3, every story read | **78** | **9** | 9 | 0 | 0 | 5 | 20 |

- **Why 413 became 87 on the same stories.** Version 2 kept oil, LNG and gas deals (its types: 109 acquisitions, 68 equity raises, 40 fuel supply and so on) and datacenter financings. Version 3 keeps power deals only, and turns away what a second read does not find to be a transaction.
- **Storage is where the wider reading paid:** 3 deals with no size became 28 with 8 sizes, almost all from stories version 2's sector filter left out.
- **Version 2's datacenter flag was loose** (172 of 413). Version 3's is set by the second read from the words: 78.
- By kind: acquisition 67, other 60, project finance 58, power purchase 53, offtake 3, tolling 1. Of the 53 power purchases, 13 state a size and 7 a term.

## No number without its sentence

For every number the model returns the words and the sentence. The code keeps it only if the sentence is in one story's title or summary, the words are in the sentence, the words state the number with its unit and parse to the same value, and the words are one number, not a range. The stored sentence is the story's whole title or whole sentence.

- 187 numbers given by the first read; **179 passed**; 8 did not (7 belonged to deals with no named party, 1 failed the check).
- **115 are in the table** (25 MW, 6 MWh, 9 terms, 75 dollar values), each with its row in `power_deals_evidence`. The others belonged to deals the second read turned away, were the same figure in a second report, or were 3 figures the second read found were not the deal's own.
- After the tables are written the build checks the rule on the tables themselves and fails if one number has no sentence in a story held. A test removes one sentence and sees it fail.
- A deal that states none keeps blanks: 132 of the 242.
- Not converted, by rule: euros and pounds to dollars; months to years. A limit is kept with its word ("up to 2,800 MW", "about USD 1 billion"): 7 numbers carry one.

## Twenty read by hand, three times

By me, against the titles and summaries held. Each sample is twenty deals drawn at random from the table as it stood (`runs/session130/sample20.py`, seeds 130, 131, 132). The first two led to changes; **the third is the measure**, drawn after the last change to any model instruction.

| Sample | Table then | Not a power deal the story reports | Numbers shown, wrong | Other fields wrong |
|---|---|---|---|---|
| 1 | 270 deals, one read | 1 of 20 | 10, none | sides the story does not state in 3; kind 1; datacenter flag 1; one deal in the table twice |
| 2 | 264 deals | 4 of 20 | 13, one not the deal's own | buyer 1; technology 2 |
| **3** | **242 deals, as built** | **1 of 20 (5 percent)** | **8, none (0 percent)** | **sides 1, kind 1, datacenter flag 1, status 1** |

**The third sample's error rate: 5 of 20 deals carry at least one wrong field (25 percent); 5 of 148 judgments are wrong (3.4 percent); 0 of 8 numbers.** The five:

| Deal | What is wrong |
|---|---|
| Norsk Hydro, wind farm sale | Not a deal the story reports: the story is about compensation after an earlier sale |
| BlackRock, EQT and AES | Datacenter flag set on "bet on AI power boom", which does not say the power serves datacenters |
| ProPetro and Coterra's unit | ProPetro shown as buyer of a "power supply agreement"; the words give no side, and ProPetro is the supplier |
| Ford unit and EDF | "Energy storage deal" called an offtake; the words do not say |
| Arena Renewables and Summit Ridge | "Sells" given the status announced |

What each sample changed:

- **After the first:** a deal naming no party is not kept; the second read was added; sides (buyer, seller) are kept only where the second read finds the story states them (74 deals now list parties with no side); two reports on nearly the same day, one naming one party, fold.
- **After the second:** the second read turns away an investment firm raising its own fund, a deal mentioned in passing, and "energy assets" not shown to be power; it names figures that are not the deal's own (the "$5 billion push") and names that are not parties ("Blackstone-backed").
- **After the third, code only, no model call:** the limiting word was missed when the model's words began with it; a folded deal could list a party twice; "over" in "in talks over $7 billion plant" was read as "more than". All three fixed and tested.
- **Seen and not fixed:** the second read blanked Constellation and Calpine's USD 16.4 billion because another story of the same deal says USD 27 billion. Both are the deal's own (with and without debt). A blank is the safe side.

## The page

`/deals/v3`, in review, in the layout of `/deals/v2` with the shared components. A panel (storage or datacenters in one click, kind, technology, what the story states, counterparty, year), the sentence, the three comparison tables above, and every deal with each number beside a link to the story it was read from. Folds: how a deal gets here, what was read, what this does not tell you.

## Checks

- Tests: `tests/test_session130.py`, 39 tests, on real titles and summaries: the sentence found whole; a size needs its unit and takes its scale; a range, euros and months are not kept; the fold's three cases and its refusals; the second read's four effects; the reading order; and, on the tables rebuilt from the answers in git, the rule itself, the words of every number, a party and an evidence sentence for every deal, and no deal without a second read. The page's library is run in Node against the copy.
- Full suite: `python -m unittest discover -s tests`, exit 0: Ran 1314 tests in 366.581s, OK (skipped=19).
- Site build exit 0. Route check exit 0 (8 live pages and 117 in review, 0 failed). No-request check exit 0. The page's check: 20 of 20, with seven selections each compared with the library's.
- Both tables: validator pass, coverage, archive, Redivis draft (public and internal datasets by license). Nothing released; nothing loaded.

## Decisions made without you

- **Power deals only.** "Aimed at power deals" read as: oil, LNG, pipelines and upstream gas are out.
- **Every story, not version 2's 1,765.** In an order that would have left the least likely unread had the cap bitten. It did not.
- **A value in US dollars is kept too**, by the same rule, though your list did not name it: it is the size of a financing or an acquisition.
- **The second read**, and its cost.
- **New tables, not new columns on `energy_deals`:** that table is in the live set, and versions 1 and 2 read it.
- **Sentences stay internal**; the page links to the story.
- **The answers are in git** (`answers_v3.jsonl`, `second_read_v3.jsonl`, 2.2 MB), as `news_stories.csv` already is, so the tables can be rebuilt and tested anywhere without a model.
- **The data lock was held for the two model runs** (about 5 minutes and 1 minute each), because the cost ledger is a warehouse table written at every call.
- **The calls ran eight at a time** through `llm.record` and my own running total, with USD 0.08 held back per call in flight, so the cap could not be passed.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| The first read returned plant start-ups, plans and datacenter leases as deals | reading the numbers it kept, then the first hand sample | the second read |
| A fund's own fund raising, a passing mention and unnamed "energy assets" passed the second read | the second hand sample | its instructions tightened, and read again |
| A true figure of something else ("$5 billion push") stored as the deal's | the second hand sample | the second read names such figures; 3 blanked |
| "about" missed; a party listed twice; "over" misread | the third hand sample, and reading the list of limits | fixed in code, with tests |
| My patch script stopped on a docstring it did not match, and the shell went on to a step whose script did not exist | exit 127 | rerun; nothing was written in between |

## What is left

The six points under the verdict. The first two are the ones that decide whether this page is worth opening.
