# Energy per AI query, as published: the page audited as a hostile expert would

Session 10221, 26 November 2026, chain 710 (part D), the old laptop. `/ai-energy` ("Energy per AI query, as published") read as three hostile readers would: an AI lab's energy lead, who knows which of these numbers are disputed; a utility load forecaster, who wants megawatts he can put in a forecast; and a journalist who will quote one figure from the page and wants to know what it is of. In the form of `docs/reviews/tracker-model-audit-2026-11-26.md`.

- Nothing changed on main but this file, its folder of evidence (`docs/reviews/ai-energy-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding's test is on its own branch, `wip/audit-ai-energy-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move what a reader sees carries the test only and is not for landing.
- Not repeated: the browser read of 20 November (`docs/reviews/browser-read-2026-11-20.md`, section 16: the page at both widths, the keyboard, the four orders, the thirteen measures; "Quiet faults: none"); the tracker and cost audits of tonight (no figure of this page is theirs).
- **What kind of page this is.** It computes nothing. Each of its 23 rows is one number a publication printed, with the words it was cut from. So the arithmetic to re-do is small (counts, an order, a filter, a number written out), and the audit's weight is on what the page's words say the rows are.

## In short

- **The arithmetic is right.** An independent restatement from the page's own file (`site/data/ai_energy.json`), written from the method note and the page's words, gives every item the default view prints, to the digit: 96 of 96 equal to the page as the site's own code draws it (23 figures, 9 publications, 2 of them peer-reviewed papers, the newest July 9, 2026; the 23 figures with their units; the default order and the other three; the 13 measures and each filter's rows; the publishers' list; every hover; the five decisions). Each figure is a number of its own quoted words (23 of 23), and the page file equals the session's source rows field for field.
- **The largest numbers on the page are not AI's (finding 1).** 5 of the 23 rows are a company's whole consumption in a year: Google's total energy (12.2 TWh in 2019, 15.4 in 2020), Microsoft's (10.8 TWh in 2020; 37,026,353 MWh in fiscal 2025, its datacenters and offices together) and Meta's data centers (18,061,781 MWh in 2024). Each holds AI and every other use, in every country the company runs; no row gives AI's share. The table is captioned "Every published figure of the energy of AI". A journalist quoting "Microsoft, 37 TWh" from a page named "Energy per AI query" quotes a fleet as AI. Fixed in words.
- **"No two publications measure the same thing" is false once (finding 2).** Strubell and others (2019) estimated the neural architecture search behind the Evolved Transformer at 656,347 kWh (times PUE); Google's own authors (2022) printed 7.5 MWh for the same search: 87.5 times less. The two rows sit under two different measures of the filter and nothing on the page joins them, while the decisions say no two publications measure the same thing. Fixed in words, without a comparison of the ERW's own.
- **The lead promises what the rows do not hold (finding 3).** "Every figure ... has printed for the energy of an AI query, a token, ...": no row is per token (0 of 23), and the method note calls the 23 "the first reading, not every figure ever printed". Fixed in words.
- **Smaller, in words.** "2 of them peer-reviewed papers" counts a venue named on the page read, and the publisher kind puts a venue where a publisher belongs (finding 4); the newest date, July 9, 2026, is not the fact sheet's own (it prints none) and the headline does not say so (finding 5); the method note says each estimate of another maker's model says so in its basis, and Strubell's two rows do not (finding 8).
- **Two choices for Samuel, each a test on its branch, default "left as it is":** the figure drops digits the publication printed (0.10 Wh shows as 0.1; 1.0x10-4 kWh as 0.0001; a value under 0.000001 would show as 0) (finding 6); the filter splits one measure by its parenthesis, 13 choices for 8 measures, so "energy of a fleet in a year" shows 3 of the 5 fleet rows (finding 7).
- **What an expert's own number would hold:** AI's share of each fleet (none held); the average draw in MW a forecaster uses (Microsoft fiscal 2025: 4,227 MW; Meta 2024: 2,056 MW, worldwide); the series the quoted words already print (Microsoft 3.44 times its fiscal 2020, Meta 2.59 times its 2020); a training figure newer than BLOOM's of November 2022 (4.06 years old); any per-query figure from a maker other than OpenAI and Google.
- **Six branches fix words and move no figure (1 to 5 and 8, merged as `wip/audit-ai-energy-words` for landing); two show a choice for ruling (6, 7).** Three data requests (the saved copies are on the data machine). Nothing needs the key.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/ai-energy/page.tsx` | The page: the lead with two hints, the license line and the file's build date; three headline figures (figures, publications with the peer-reviewed count, the newest date); the form (order, what is measured); the table of every figure with three hovers a row; the publishers' list; the decisions; the downloads and the source line. Reads the file at build, `force-dynamic` for the form |
| `site/app/ai-energy/Decisions.tsx` | The five decisions (`as-printed`, `no-sum`, `order`, `no-pair`, `which-publications`), each with its default, source and session; the method note carries the same list |
| `site/lib/aienergy.ts` | The file's shape (`readAiFile`), the four orders (`ordered`: by publisher, by measure, newest, oldest; ties in the file's order; never by size), the measures and publishers each once, A to Z, and `figure` (the value written out, grouped). No import, nothing computed from the figures |
| `site/data/ai_energy.json` | The page's file: 23 rows, built 19 November 2026 19:42 UTC by the builder below, with the table's provenance lines |
| `warehouse/derived/ai_energy_page.py` | Writes the page file from `warehouse/output/ai_energy_published.csv`: the table's rows as they stand, the value as a float, an em dash refused |
| `warehouse/connectors/ai_energy_published.py` | The table, from `warehouse/sources/ai_energy_published/rows.csv` (written by a session that read each publication): refuses a row whose printed words are not in the saved text of its publication, or whose value is not a number of those words. The saved copies are under `warehouse/raw/ai_energy_published/`, on the data machine only |
| `warehouse/sources/ai_energy_published/rows.csv` | The 23 rows as the session wrote them (in git) |
| `docs/methods/ai_energy_published.md` ("the method note") | The rule, the nine publications read, the limits, the build, the page, the replication and the decisions |
| `replication/ai_energy/replicate.py` | Reads the page as served and sets every marked figure beside the file; cross-checks each row's words in its saved copy (data machine only). Not run here: it reads a served page |
| `tests/test_session8012_ai_energy.py`, `tests/test_session8005_ai_energy_and_resources.py`, `site/scripts/test-reader-pages-render.mjs` | The page's tests: every row has its words and source, nothing computed (no `reduce(`, no `Math.`), no order by size, the decisions and the note one list, the orders keep every row; the page drawn with its three headline figures the file's counts |
| `site/lib/tour.ts` | The tour's stop for the page: "The energy a query to an AI model uses, as each publisher printed it" |
| `docs/redivis/codebook/tables.csv` and the files built from it | The table's one-line description: "One energy figure for AI (per query, per token, of a training run or of a fleet)" (window B's codebook; not changed here) |

## How every number here was computed

- **The default view:** `/ai-energy` with no query, drawn with the site's own code (`draw_ai.mjs`, through the site's own loaders and the two stand-ins of `site/scripts/test-reader-pages-render.mjs`), with each of the four orders and each of the 13 measures drawn too. No server, no request.
- **The independent restatement:** `restate.py` (standard library), written from the method note's "The page" and the page's own words, not from `lib/aienergy.ts`: counts by title and by publisher kind, the newest by date, the dates in words, each value written in its shortest decimal and grouped, the orders by their stated keys, the measures and the publishers' list, every hover's sentence. It reads the drawn HTML and sets each item beside it.
- **The page's own `figure`** on every row and on seven probe values: `figure_probe.mjs`.
- **One rule at a time and each claim's size:** `measures.py` (the page file, the source rows, the probe). The scale of a fleet against the United States: `us_sales.py`, streamed from the main copy's `eia_retail_sales_monthly.csv` (read, not written).
- Copies of every script and its printout: `docs/reviews/ai-energy-model-audit-2026-11-26/` (written to run from `runs/c10221/` of a worktree, `draw_ai.mjs` and `figure_probe.mjs` from `site/`).

## The arithmetic re-done

| Figure | Drawn by the site's code | Restated | Gap |
|---|---|---|---|
| Figures; publications; peer-reviewed papers | 23; 9; "2 of them peer-reviewed papers" | 23 rows; 9 distinct titles; 2 titles whose publisher kind is "peer-reviewed paper" (Strubell and others, ACL 2019; Luccioni and others, ACM FAccT '24) | 0 |
| Newest | July 9, 2026; "Microsoft: 2026 Environmental Sustainability Report Data Fact Sheet" | the latest `event_date` | 0 |
| File built | 2026-11-19 | the file's `built` | 0 |
| The 23 figures | 1,507 kWh; 656,347 kWh; 86, 232, 24, 179, 1,287 MWh; 12.2, 15.4, 10.8 TWh; 7.5 MWh; 433,196, 914, 1,163,032 kWh; 0.047, 2.9, 0.0001 kWh; 0.34, 0.24, 0.14, 0.1 Wh; 18,061,781 MWh; 37,026,353 MWh | each value in its shortest decimal, grouped, with its unit | 0 (23 of 23) |
| The default order | Google (3), Google and UC Berkeley (9, the 2021 paper first), Hugging Face (BigScience) (3), Hugging Face and Carnegie Mellon (3), Meta, Microsoft, OpenAI, UMass Amherst (2) | publisher, then date, then the file's order | 0 |
| The other three orders | by measure, newest, oldest | by their stated keys, ties in the file's order | 0 (each holds all 23) |
| What is measured | 13 choices, A to Z | the distinct `x_measures`, A to Z | 0; each of the 13 filters shows exactly its rows |
| The publishers | 8 lines, e.g. "Google and the University of California at Berkeley: 9 figures in 2 publications (2021, 2022)" | the same | 0 |
| Every hover | 3 a row (period and peer review; basis, source, page, the day saved, the first 12 characters of the checksum; the page of the words) | the same sentences from the row | 0 (69 of 69) |
| The decisions | 5 | 5, the same keys | 0 |

- **96 of 96 items equal** (`restate.out`). Where `figure` writes a number and the restatement writes its shortest decimal, they agree on all 23 rows; the two places where neither writes the publication's own digits are finding 6.
- **The build's two checks restated where this machine can:** each value is a number of its own printed words (23 of 23, `1.0x10-4` read as 0.0001); the page file equals `rows.csv` field for field (23 of 23). The words-in-the-saved-copy check needs the saved copies, on the data machine; the connector made it at the build of 19 November and refused nothing. It is not asked for again.
- **What a visitor sees today:** the page is in review (`robots: noindex`, in no menu); it is reached from the tour (stop "Energy per AI query").

## One rule changed at a time

Each line changes one choice and keeps every other. The base is the page file of 19 November: 23 figures from 9 publications.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The filter offers each `x_measures` as worded, parentheses and all | the words before the parenthesis | 13 choices to 8; "energy of a fleet in a year" shows 3 rows (Google's two, Microsoft's 2020 as Google's paper cites it) to 5 (Meta's and Microsoft's own reports join); "energy of a training run" 7 to 9 (Strubell's two join) | no (finding 7) |
| `figure` writes the float's shortest decimal | the digits the publication printed | 2 of 23 rows look different: 0.1 Wh to 0.10 Wh (Google's narrow boundary); 0.0001 kWh to 1.0x10-4 kWh (BLOOMz-7B); no value moves. A value under 0.000001 in its unit (a per-token figure in kWh, say 9e-7) would show as "0"; 3.4e-7 shows as "3.4e-7" | `figure`'s own comment says "digits as given" (finding 6) |
| The peer-reviewed count reads the publisher kind, "yes" only where the page read names a venue | the venues as an expert knows them (not verified here: no web read) | 2 of 9 to 4 of 9, if BLOOM's paper is the one in the Journal of Machine Learning Research (2023) and the 2022 Patterson paper the one in IEEE Computer (2022) | the rule is in the method note, not beside the count (finding 4) |
| The newest is the latest `event_date` | the latest date a publication prints itself | Microsoft's July 9, 2026 (from the address of its launch post) to Google's August 21, 2025: the fact sheet and Meta's index print no date; 2 of 9 dates are the ERW's reading | in the figure's hover, not the headline (finding 5) |
| One table of every figure, none set beside another | the same subject's rows read together | the search behind the Evolved Transformer: 656,347 kWh (Strubell and others, an estimate) and 7,500 kWh (Google's authors): 87.51 to 1. Microsoft's 2020: 10.8 TWh as Google's paper cites it, 10,770,714 MWh as Microsoft's fact sheet prints its fiscal 2020 (a gap of 0.27 percent, in the printed words, not a row) | the decisions say no two publications measure the same thing (finding 2) |
| A fleet's figure is shown as the energy of AI | a fleet as a fleet | 5 of 23 rows; the two largest numbers on the page (37,026,353 and 18,061,781 MWh) | no (finding 1) |

## Each claim against the code

| Claim, or question | Where | What the code and the rows do | Verdict |
|---|---|---|---|
| AI load against all datacenter load against all of a company's load | the caption ("the energy of AI"), the lead, the tour | 5 rows are whole fleets: Google's "total energy consumption" (2019, 2020), Microsoft's "annual energy consumption" (2020) and its electricity within the organization (fiscal 2025, datacenters and offices), Meta's data centers' electricity (2024). Three boundaries, under three measures; no row gives AI's share | **Finding 1**. The page never sets a fleet against a query, as it says |
| Announced against energized MW | (none) | No MW anywhere; no project | Not applicable |
| MW against TWh, with a load factor said or assumed | the decisions (`as-printed`) | No unit converted, no MW derived | **Right as stated**. A forecaster's MW is below, as the audit's own arithmetic |
| Forecasts quoted from others, and their vintage | (none) | No forecast in the table | **Right**: none is quoted |
| A growth worded as caused by AI | the lead, the publishers' list | No growth on the page. The quoted words of Meta's and Microsoft's rows print five and six years, of which the row keeps the last | **Right**: nothing is worded as growth, let alone as caused by AI |
| One project counted in two sources | the decisions (`no-pair`), the hint "what it measures" | The search behind the Evolved Transformer is two rows of two publications; Microsoft's 2020 is a row (as Google's paper cites it) and a number in another row's quoted words | Nothing is summed, so nothing is counted twice; the claim that no two publications measure the same thing is false (**finding 2**) |
| Shares of what total | Google's 0.14 Wh row ("58% of total" in its words) | The page computes no share | **Right** |
| Held or internal rows reaching a public figure | the license line | `ai_energy_published` is public in the license registry and the verdicts ("every publisher's terms the ERW read allow it to be shared, with credit"); no held table is read | **Right** |
| The as-of date | the license line ("File built 2026-11-19"), the decisions ("Nine publications on 19 November 2026") | Both from the file and the note | **Right**. Each row's own date is the publication's, except two (**finding 5**) |
| "Every figure ... has printed" | the lead | 23 figures from the nine publications read on 19 November; the note: "the first reading, not every figure ever printed"; Google's environmental reports not read (their host's robots file disallows it) | **Finding 3** |
| "... the energy of an AI query, a token, a training run or a fleet" | the lead | 0 of 23 rows per token; the one per-token figure read ("From Words to Watts", about 3 to 4 joules a token) was left out, its venue not named | **Finding 3** |
| "Energy per AI query" (the name) | the title, the tour | 7 of 23 rows are per query, prompt or inference; 9 are training runs, 5 fleets, 2 a deployment or a project | The lead says what the rows hold; the name is the owner's (for Samuel's ruling, words, default the name as it is) |
| "Nothing here is the ERW's own. No figure is averaged, summed, converted to another unit or ranked" | the lead's hint, `no-sum` | No sum, no mean, no conversion, no order by size (the tests hold `reduce(` and `Math.` out of the page); the value is the ERW's reading of which number in a table row is meant (Meta's fifth of five, Microsoft's sixth of six, Strubell's third of four) | **Right**. The ERW's reading is said in the license line ("and the ERW's own reading of them") |
| "Each publication measures something different ... The figures are not comparable with one another" | the lead's hint | Google's 0.24 and 0.10 Wh are the same prompt on two boundaries (the note: they "stand side by side"); the search behind the Evolved Transformer is two publications' figures for one thing | **Finding 2** |
| "2 of them peer-reviewed papers" | the headline note | Counts the publisher kind "peer-reviewed paper", "yes" only where the page read names a venue | **Finding 4** |
| "Newest: July 9, 2026" | the headline | Microsoft's date is that of its launch post's address; the fact sheet prints none | **Finding 5** |
| The figure "as printed" | the table, `as-printed` | `figure` writes the float: 0.10 shows as 0.1 | **Finding 6** (for ruling) |
| "Several figures are one publisher's estimate of another's model ... `x_basis` says so" | the method note, Limits | GPT-3's subject names OpenAI; the search's subject names So and others; BERT's row says only "the paper's estimate"; no basis names the other maker | **Finding 8** (the note) |
| The filter, "What is measured" | the form | 13 choices, one a distinct `x_measures` | **Finding 7** (for ruling) |
| The order shown first: "No order by the figure's size is offered, so no company is ranked" | the hint, `order` | Four orders, none by value; ties in the file's order | **Right** |

## What an AI lab's energy lead, a load forecaster or a journalist would hold that this does not

| Item | Size | From |
|---|---|---|
| AI's share of each fleet | not held: no row gives one. Google's 2022 paper is known to print a share of machine learning in Google's energy use; whether the saved copy prints it is data request 2 | the page file |
| The average draw in MW (a forecaster's unit; the page converts nothing, by its rule) | Google 2019: 1,393 MW; 2020: 1,753 MW; Microsoft 2020: 1,230 MW; Meta's data centers 2024: 2,056 MW; Microsoft fiscal 2025: 4,227 MW. Each worldwide | `measures.py` (energy over the year's hours) |
| The scale against the United States | Microsoft fiscal 2025, 37.03 TWh worldwide: 2.51 percent of US commercial retail sales over July 2024 to June 2025 (1,476.5 TWh), 0.92 percent of all sectors (4,037.9 TWh). Meta 2024, 18.06 TWh: 1.24 percent of US commercial (1,450.9 TWh), 0.45 percent of all (3,975.4 TWh). An upper bound on their US share: each company counts every country | `us_sales.py`, `eia_retail_sales_monthly` |
| The series the quoted words already print | Meta's data centers 6,966,000 MWh (2020) to 18,061,781 (2024): 2.59 times. Microsoft 10,770,714 MWh (fiscal 2020) to 37,026,353 (fiscal 2025): 3.44 times. The row keeps the last year only | the rows' own `x_printed` |
| A training figure for a model of the last four years | none: the newest training figure is BLOOM's (3 November 2022, 4.06 years before today); the training rows are of 2019 to 2022 | the page file |
| Per-query figures from more makers | 7 rows of 3 publishers (Google, OpenAI's chief executive, Hugging Face and Carnegie Mellon), dated June 2024 to August 2025; none from Anthropic, Meta, Microsoft or another maker | the page file |
| The boundary's own size | Google's two boundaries for one prompt: 0.24 and 0.10 Wh, 2.4 to 1, in one publication | the page file |
| A per-token figure | none (the one read was left out) | the method note |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | The caption and the tour say the rows are AI's; 5 of 23 are a company's whole consumption (AI and all else, every country), the two largest numbers on the page among them | a fleet quoted as AI | words | `wip/audit-ai-energy-1` (`f1a90f3ec`) |
| 2 | Medium | "No two publications measure the same thing": the search behind the Evolved Transformer is two publications' rows, 87.5 to 1, under two measures, never joined | the most quoted figure on the page stands without the publisher's own | words | `wip/audit-ai-energy-2` (`e9d8f1080`) |
| 3 | Low | The lead: "every figure", "a token" | 0 rows per token; 9 publications, a first reading | words | `wip/audit-ai-energy-3` (`198c462f4`) |
| 4 | Low | "2 of them peer-reviewed papers": a venue named on the page read; the publisher kind holds a venue | 2 of 9, perhaps 4 | words | `wip/audit-ai-energy-4` (`c35769b54`) |
| 5 | Low | The newest date is not the publication's own, unsaid in the headline | 2 of 9 dates are the ERW's reading | words | `wip/audit-ai-energy-5` (`42e7fef63`) |
| 6 | Low | The figure drops printed digits; a value under 0.000001 would show as 0 | 2 of 23 rows' look | for ruling | `wip/audit-ai-energy-6` (`643901d36`, test only) |
| 7 | Low | The filter splits one measure by its parenthesis | 13 choices for 8 measures; 3 of 5 fleet rows | for ruling | `wip/audit-ai-energy-7` (`5ad31bf5f`, test only) |
| 8 | Low | The note says each estimate of another's model says so in its basis; Strubell's two do not | the note only | words | `wip/audit-ai-energy-8` (`ad595f0cf`) |

The six words branches conflict in `page.tsx` (the lead and its hint, 2 and 3; the two headline notes, 4 and 5), so they are also merged, conflicts resolved by keeping every change: `wip/audit-ai-energy-words` (`a97ee059e`).

## 1. The largest numbers on the page are not AI's (Medium)

- **Where.** `site/app/ai-energy/page.tsx`, the table's caption ("Every published figure of the energy of AI, as printed") and the page's name; `site/lib/tour.ts`, the tour's line ("The energy a query to an AI model uses").
- **Why it is wrong.** Five rows are a company's consumption in a year: Google's total energy, 12.2 TWh (2019) and 15.4 TWh (2020), as Google's papers cite Google's reports; Microsoft's, 10.8 TWh (2020, the same) and 37,026,353 MWh (fiscal 2025, "its datacenters and offices together"); Meta's data centers, 18,061,781 MWh (2024). Each holds AI work and everything else (search, mail, advertising, offices), and each company counts every country it runs in. No row gives AI's share. The two largest numbers on the page are of this kind. An expert sets Microsoft's 37.03 TWh beside the United States and finds it 2.51 percent of US commercial sales over the same twelve months; a journalist who reads "the energy of AI" above it reports that AI.
- **The test.** `tests/test_audit_ai_energy_1.py`: five rows measure a fleet, none states AI's share or the United States, the largest is Microsoft's (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Above the table: "A fleet's figure is a company's whole consumption in a year, as the company reports it (its data centers, or its data centers and offices together): AI and every other use in it, wherever the company runs them, not the United States alone. No figure here gives AI's share of a fleet." The caption: "Every figure read, as printed: the energy of AI work, and of whole fleets that run AI among everything else". The tour: "Energy figures as each publisher printed them: an AI query, a training run, or a company's whole fleet with AI among the rest, with who measured it and how." No figure moves.
- **For Samuel's ruling (words).** The page's name, "Energy per AI query, as published", fits 7 of its 23 rows. Default: the name as it is.
- **Data request 3** asks the saved copies for each fleet's stated geography.

## 2. One search, two publications, never joined (Medium)

- **Where.** `site/app/ai-energy/Decisions.tsx`, `no-pair` ("since no two publications measure the same thing in the same way"); the lead's hint "what it measures" ("Each publication measures something different ... The figures are not comparable with one another"); the method note's decisions table.
- **Why it is wrong.** Strubell and others (ACL 2019) estimated the neural architecture search that produced the Evolved Transformer at 656,347 kWh times PUE, on 8 P100 GPUs; the authors of the search's own company (Patterson and others, 2022) printed 7.5 MWh for it. Both rows name the search in their subject; the first is 87.5 times the second. Strubell's is a widely quoted figure of AI's energy; whether the 2022 paper's saved copy answers it in so many words is data request 2. On the page the two rows sit under two measures ("energy of a training run (kWh times PUE)" and "energy of a training run"), so a reader filtering either sees one of them; nothing says the other exists, and the decisions say it cannot.
- **The test.** `tests/test_audit_ai_energy_2.py`: the two rows name the same search, in two publications, under two measures (passes on main); the words test fails on main, and holds that no ratio of the ERW's own is printed.
- **The fix on the branch, words only.** The decision: "Most publications measure different things; where two give a figure for the same thing, both rows stand, each with its subject, and neither is preferred: the neural architecture search that produced the Evolved Transformer has Strubell and others' estimate (2019, in kWh times PUE) and Google's authors' own figure (2022), under two measures." The hint and the note's line say the same. The page computes no ratio, by its rule. No figure moves.
- **Data request 2** asks whether the saved copy of the 2022 paper prints its own comparison with Strubell's estimate (a printed figure could then be a row by the table's rule).

## 3. The lead promises what the rows do not hold (Low)

- **Where.** `site/app/ai-energy/page.tsx`, the lead: "Every figure a model maker, a cloud operator or a peer-reviewed paper has printed for the energy of an AI query, a token, a training run or a fleet".
- **Why it is wrong.** "Every figure" is nine publications read on 19 November, which the method note calls "the first reading, not every figure ever printed" (Google's own environmental reports were not read, their host's robots file disallowing it). "A token": no row is per token; the one per-token figure read ("From Words to Watts", about 3 to 4 joules a token) was left out because its arXiv page names no venue. The decisions' last line says which publications; the lead, read first, says every.
- **The test.** `tests/test_audit_ai_energy_3.py`: no row measures a token and the note says a first reading (passes on main); the words test fails on main.
- **The fix on the branch, words only.** "Each figure the publications read so far print for the energy of an AI query, a training run, a deployment or a fleet (a model maker's, a cloud operator's or a peer-reviewed paper's), not every figure ever printed, in the publication's own words, ...". No figure moves.
- **Not changed here:** the table's one-line description in the codebook (`docs/redivis/codebook/tables.csv` and the files built from it: "per query, per token, ...") is window B's; a row for it is returned to the chain's main session.

## 4. "2 of them peer-reviewed papers" (Low)

- **Where.** `site/app/ai-energy/page.tsx`, the headline note; the publisher kind in the table.
- **Why it matters.** The count reads rows whose publisher kind is "peer-reviewed paper", "yes" only where the page the session read names a venue (the method note's rule). A paper that appeared in a journal whose arXiv page does not say so counts as a preprint: by an expert's knowledge (not verified here, no web read) BLOOM's paper is the one in the Journal of Machine Learning Research (2023) and the 2022 Patterson paper the one in IEEE Computer (2022), which would make 4 of 9. And the publisher kind puts a venue where a publisher belongs: Hugging Face's FAccT paper is listed under "peer-reviewed paper", its BLOOM paper under "model maker".
- **The test.** `tests/test_audit_ai_energy_4.py`: two titles by the rule, each naming its venue; the publisher kinds as said (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note reads "2 of them peer-reviewed papers, counted only where the page the ERW read names the venue". The count does not move.
- **Data request 1** asks the saved copies whether they print a venue.

## 5. The newest date is the ERW's reading (Low)

- **Where.** `site/app/ai-energy/page.tsx`, the headline "Newest: July 9, 2026" and its note.
- **Why it matters.** Microsoft's fact sheet prints no date; the session took July 9, 2026 from the address of the post that launched the report. Meta's index is dated by Meta's news page. Each figure's hover says so in its basis; the headline, the one date a reader sees first, does not. By the dates the publications print themselves, the newest would be Google's paper of August 21, 2025.
- **The test.** `tests/test_audit_ai_energy_5.py`: the newest row is Microsoft's, its basis says the fact sheet prints no date, and two publishers' dates are taken this way (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note adds "A date is the one the publication prints, or, for a company report that prints none, the date of the post that launched it (the figure's hover says which)". No figure moves.

## 6. The figure drops printed digits (Low, for ruling)

- **Where.** `site/lib/aienergy.ts`, `figure` ("digits as given, grouped, never converted"); the decision `as-printed` ("the number its publication printed").
- **Why it matters.** `figure` writes the float. Google's narrow-boundary figure, printed "0.10 Wh", shows as "0.1 Wh"; Luccioni and others' "1.0x10-4 kWh" shows as "0.0001 kWh". No value changes, but a reader comparing the figure with the quoted words beside it sees a different number of digits. And a value under 0.000001 in its unit (a per-token figure in kWh, if one is added) would show as "0"; 3.4e-7 shows as "3.4e-7".
- **The test.** `tests/test_audit_ai_energy_6.py` on `wip/audit-ai-energy-6` (a test only, passes on main, through `tests/audit_ai_energy_6_figure.mjs`, the page's own `figure` under Node): the two rows, the other 21 equal to their printed digits, the small values.
- **For Samuel's ruling.** Default "left as it is". The other choice: the figure written with the digits printed (the source row would carry them as text). Measured: 2 of 23 figures change how they look (0.1 to 0.10 Wh; 0.0001 to 1.0x10-4 kWh); no value moves; the zero for a small value goes.

## 7. The filter splits one measure (Low, for ruling)

- **Where.** `site/app/ai-energy/page.tsx`, "What is measured"; `measures` in `site/lib/aienergy.ts` (each `x_measures` once).
- **Why it matters.** A qualifier in parentheses makes a measure of its own: 13 choices hold 8 measures. A forecaster who chooses "energy of a fleet in a year" sees 3 rows (Google's 2019 and 2020 and Microsoft's 2020, as Google's papers cite them) and not Meta's or Microsoft's own reports, which sit under two further choices; "energy of a training run" shows 7 of the 9 training rows, not Strubell and others' two. The browser read of 20 November took the fleet choice as answering the forecaster; it answers three fifths of him.
- **The test.** `tests/test_audit_ai_energy_7.py` on `wip/audit-ai-energy-7` (a test only, passes on main, through `tests/audit_ai_energy_7_measures.mjs`).
- **For Samuel's ruling.** Default "left as it is". The other choice: the filter groups on the words before the parenthesis, the qualifier kept in the row. Measured: 13 choices to 8; the fleet choice 3 rows to 5; the training choice 7 to 9.

## 8. The method note says the basis names the other maker (Low)

- **Where.** `docs/methods/ai_energy_published.md`, Limits: "Several figures are one publisher's estimate of another's model ...; `x_basis` says so."
- **Why it is wrong.** The three rows' basis says "the paper's estimate" and names no other maker. The subject names it for GPT-3 ("OpenAI's model") and for the search ("So et al."); BERT's row ("BERT base on 64 V100 GPUs") names no maker, though BERT is Google's model, which Strubell and others priced on hardware it was not trained on.
- **The test.** `tests/test_audit_ai_energy_8.py`: the basis and subjects as said (passes on main); the note's words fail on main.
- **The fix on the branch, words only (the note).** The note says what the rows say. Making BERT's subject name Google would change the source row and the page file (the connector, on the data machine): not done; a row for the data machine.

## The words branches drawn and read

Each branch's page was drawn to HTML with the site's own code (`draw_ai.mjs`: `app/ai-energy/page.tsx` whole, as a visitor meets it, with every order and measure), and its new sentences read in the drawn text; the hint's words are drawn in the hover's `title`, where they were read. The tour's line was drawn by the site's own `scripts/test-tour-render.mjs` (exit 0 on branch 1 and on the merge). No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-ai-energy-1` | above the table; the caption; the tour's stop | pass: "A fleet's figure is a company's whole consumption in a year, ... not the United States alone." follows "Every figure, as printed"; the caption reads "Every figure read, as printed: the energy of AI work, and of whole fleets that run AI among everything else"; the tour draws |
| `wip/audit-ai-energy-2` | the decisions fold; the hint "what it measures" (its hover) | pass: "... where two give a figure for the same thing, both rows stand, each with its subject, and neither is preferred: the neural architecture search that produced the Evolved Transformer ..."; the hover ends "both rows stand, each with its subject." |
| `wip/audit-ai-energy-3` | the lead | pass: "Each figure the publications read so far print for the energy of an AI query, a training run, a deployment or a fleet (...), not every figure ever printed, in the publication's own words, with its date and what it measures." |
| `wip/audit-ai-energy-4` | the headline | pass: "Publications 9 2 of them peer-reviewed papers, counted only where the page the ERW read names the venue" |
| `wip/audit-ai-energy-5` | the headline | pass: "... Data Fact Sheet. A date is the one the publication prints, or, for a company report that prints none, the date of the post that launched it (the figure's hover says which)" |
| `wip/audit-ai-energy-8` | the method note (not drawn: a note) | read in the file |
| `wip/audit-ai-energy-words` | every place above | pass: all six sentences drawn; the restatement run on the merged drawing gives 95 of 96 equal, the one difference the Newest note's new words: no figure moved |

- Tests on the merge: the six words tests with every test file that reads the changed files (`test_session8012_ai_energy`, `8005_ai_energy_and_resources`, `9871`, `8902_tour`, `8905_tour_resources`, `9203_tour_stop8`, `9601_tour_headings`, `9601_back_button`, `292`, `53`): 68 passed. On origin/main the six words tests fail (6 failed) and the six behaviour tests pass (6 passed) (`on_main.out`). Branches 6 and 7: 18 passed each with the page's two test files.

## The decisions block, line by line

1. `as-printed`, the printed number and unit, no unit converted: **right** for the value and the unit; the digits drop twice (finding 6).
2. `no-sum`, nothing averaged, summed or set against another: **right** (the tests hold it).
3. `order`, publisher A to Z, never by size: **right**.
4. `no-pair`: the rule is kept; its reason is false once (finding 2).
5. `which-publications`, nine publications on 19 November 2026: **right**, and it is what the lead should say (finding 3).

## Not covered, or left open

- **The saved copies.** The words-in-the-copy check and the venue, share and geography questions need `warehouse/raw/ai_energy_published/`, on the data machine (data requests 1 to 3). The connector refused nothing on 19 November, and the replication's cross-check ran then.
- **The publications not read.** Whether a figure was misread from its publication can only be checked against the publication; no web read here.
- **The words cell's page.** The Altman row's page is "the post (one page)", drawn as "(p. the post (one page))" and in its hover "Page the post (one page) of the publication": awkward, not false. No branch.
- **The page in a browser:** drawn to HTML; the browser read of 20 November covers widths and the keyboard.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-ai-energy-words` (`a97ee059e`), the merge of `wip/audit-ai-energy-1` (`f1a90f3ec`), `-2` (`e9d8f1080`), `-3` (`198c462f4`), `-4` (`c35769b54`), `-5` (`42e7fef63`) and `-8` (`ad595f0cf`), conflicts resolved by keeping every change. Each was drawn and read (pass). The page's figures do not move. Files: `site/app/ai-energy/page.tsx`, `site/app/ai-energy/Decisions.tsx`, `site/lib/tour.ts`, `docs/methods/ai_energy_published.md`, six test files.
- **For Samuel's ruling, default "left as it is":**
  - Finding 6, `wip/audit-ai-energy-6` (`643901d36`), not for landing: write each figure with the digits printed; 2 of 23 figures change how they look (0.1 to 0.10 Wh, 0.0001 to 1.0x10-4 kWh), no value moves.
  - Finding 7, `wip/audit-ai-energy-7` (`5ad31bf5f`), not for landing: group the filter on the words before the parenthesis; 13 choices to 8, the fleet choice 3 rows to 5, the training choice 7 to 9.
  - Finding 1, words, no branch: the page's name "Energy per AI query" fits 7 of 23 rows; default the name as it is.
- **Data requests (the data machine, `warehouse/raw/ai_energy_published/20261119T1230Z/`, no request to any service):**
  1. In `bloom_2022` and `patterson_2022`'s saved text, is a venue printed (the Journal of Machine Learning Research; IEEE Computer)? Return each line that names one, or "none". Feeds finding 4.
  2. In `patterson_2022`'s saved text, the sentences that give machine learning's share of Google's energy use and that compare the search behind the Evolved Transformer with Strubell and others' estimate, each with its page. Feeds finding 2 and the expert's AI share.
  3. In `microsoft_2026_fact_sheet` and `meta_2025_data_index`'s saved text, the words that state the geography of the electricity tables (global, worldwide, by country, United States). Feeds finding 1.
- **For window B (the codebook):** the table's one-line description says "per query, per token, of a training run or of a fleet"; no row is per token (finding 3).
- **Needs the key:** nothing.
