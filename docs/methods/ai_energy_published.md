# Energy per AI query, as published (`ai_energy_published`)

Session 8005, chain 501 step D3, 19 November 2026. Connector: `warehouse/connectors/ai_energy_published.py`. Rows: `warehouse/sources/ai_energy_published/rows.csv`, written by the session that read each publication itself; no script called a model. The page that reads the table ("Energy per AI query, as published") is the second window's (chain 502, part C).

## The rule

- **Only what was printed.** Every row is one figure a model maker, a cloud operator or a peer-reviewed paper printed for the energy of a query, a token, a training run or a fleet. `x_printed` is the publication's own words, cut from its saved copy; `x_value` is the number in them, in `x_unit`, the publication's own unit.
- **Nothing of the ERW's own.** No figure is converted, summed, averaged or compared across publishers, and none is computed from another (a training run's GPU hours times a chip's power is not a published energy figure, so a model card that prints only GPU hours has no row). This is the large-load pilot's rule (`docs/accelerator/large_load_pilot.md`).
- **What it measures, in words.** `x_measures` (energy per prompt, per query, per 1,000 inferences, of a training run, of a fleet in a year), `x_subject` (what it is of), `x_period` and `x_basis` (the boundary the publication states, or "not stated"). Two figures for the same thing on different boundaries stand side by side (Google's 0.24 Wh and 0.10 Wh per median Gemini Apps prompt).
- **The check at every build.** The build refuses a row whose printed words are not in the saved text of its publication (spaces aside, since a PDF's text comes out without some of them, and a word broken by a hyphen across two lines read whole; "[...]" marks a cut where a page break or a footnote falls between two pieces). It refuses a value that is not a number of the printed words.
- **Who printed it.** `x_publisher_kind`: model maker, cloud operator (Google is both) or peer-reviewed paper; `x_peer_reviewed` says yes only where the page read names the venue (ACL 2019 for Strubell and others, ACM FAccT '24 for Luccioni and others). A preprint by a model maker is kept as the model maker's figure.

## The publications read (19 November 2026)

Each host's robots file was read first; none names Claude or Anthropic, and none disallows the pages read (arXiv: `Crawl-delay: 15`, kept between requests).

| Publication | Publisher | Date | Rows |
|---|---|---|---|
| Measuring the environmental impact of delivering AI at Google Scale (arXiv 2508.15734) | Google | 21 August 2025 | 3 |
| The Gentle Singularity (blog.samaltman.com) | OpenAI's chief executive | 10 June 2025 (the page's own timestamp) | 1 |
| Carbon Emissions and Large Neural Network Training (arXiv 2104.10350) | Google and UC Berkeley | 21 April 2021 | 6 |
| The Carbon Footprint of Machine Learning Training Will Plateau, Then Shrink (arXiv 2204.05149) | Google and UC Berkeley | 11 April 2022 | 3 |
| Power Hungry Processing: Watts Driving the Cost of AI Deployment? (arXiv 2311.16863; ACM FAccT '24) | Hugging Face and Carnegie Mellon | June 2024 | 3 |
| Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model (arXiv 2211.02001) | Hugging Face (BigScience) | 3 November 2022 | 3 |
| Energy and Policy Considerations for Deep Learning in NLP (arXiv 1906.02243; ACL 2019) | UMass Amherst | 5 June 2019 | 2 |
| 2025 Environmental Data Index (sustainability.atmeta.com) | Meta | 12 September 2025 (the report's launch, as Meta's news page dates it) | 1 |
| 2026 Environmental Sustainability Report Data Fact Sheet (cdn-dynmedia-1.microsoft.com) | Microsoft | 9 July 2026 (the date in the address of Microsoft's post accompanying the report; the fact sheet prints none) | 1 |

Read and with no row: Mistral AI's note of July 2025, "Our contribution to a global environmental standard for AI", prints greenhouse gas emissions (1.14 gCO2e for a 400-token response), water (45 mL) and resource depletion, and no energy figure. "From Words to Watts" (arXiv 2310.03003, MIT and others) prints "about 3-4 Joules for a output token" for its tested model; its arXiv page names no venue, so it is not counted as peer-reviewed and has no row by the rule above.

## Limits

- Twenty-three figures from nine publications: the first reading, not every figure ever printed. A later session adds rows by the same rule.
- Several figures are one publisher's estimate of another's model (Patterson and others on GPT-3; Strubell and others on BERT and a neural architecture search); `x_basis` says so.
- Google's 2019 and 2020 fleet figures and Microsoft's of 2020 are what the papers cite from the companies' reports; Microsoft's own fact sheet of 2026 and Meta's data index were read on the companies' hosts. Google's environmental reports are served from `www.gstatic.com/gumdrop/`, which that host's robots file disallows, so they were not read; Meta's data index was read on its own site.

## Build

    python warehouse/lock.py run --task ai -- <python> warehouse/connectors/ai_energy_published.py

## The page (session 8012, chain 505)

The page "Energy per AI query, as published" (`/ai-energy`, in review, in no menu) reads `site/data/ai_energy.json`, the table's rows as they stand, written by `warehouse/derived/ai_energy_page.py` (run after the connector, whenever its rows change). It shows every figure with its publisher, the publication and its date, what the figure measures and of what, the number in its own unit, and the publication's own words with their page; the basis, the period, the peer review and the saved copy are on hover. It can be put in order of publisher, of what is measured or of date, and filtered by what is measured. It computes nothing from the figures: no average, no sum, no conversion, no order by size, no comparison of one publisher's figure with another's.

### Replication and cross-check

`replication/ai_energy/replicate.py` reads the page as served and sets every figure it marks beside the file (the 23 figures, the count of figures and of publications). Its cross-check finds each row's printed words again, word for word, in the text of the saved copy of its publication (on the data machine, where `warehouse/raw/ai_energy_published/` is); it writes `figures.csv` and `crosscheck.csv`.

### Decisions (session 8012)

| Key | Choice | Default |
|---|---|---|
| `as-printed` | Every figure is the number its publication printed, in its own unit, beside its own words; no unit converted | the printed number and unit |
| `no-sum` | Nothing averaged, summed or set against another figure; the publications measure different things | no figure of the ERW's own |
| `order` | Publisher A to Z, then date; or what is measured, or date; never by size | publisher, A to Z |
| `no-pair` | No two figures set side by side by the page; where two publications give a figure for the same thing, both rows stand, each with its subject, neither preferred (the neural architecture search that produced the Evolved Transformer: Strubell and others' estimate of 2019, in kWh times PUE, and Google's authors' figure of 2022; audit of 26 November 2026, finding 2) | one table of every figure |
| `which-publications` | The publications a session found and could read; a host that refuses automated reading is named under Limits | nine publications on 19 November 2026 |

