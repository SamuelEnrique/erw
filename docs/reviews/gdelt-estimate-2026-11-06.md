# GDELT as a second corpus for the Attention and Friction indices: an estimate for the owner's approval

Session 3408 (chain 202), 6 November 2026, lab-desktop, fourth window. Ten requests were made, as the prompt allowed:
two robots files, two terms pages, the master file list's size (HEAD), the latest-files pointer, one sample slice
(GET, June 2026), the newest slice (GET, answered 404 a minute after it was announced) and two older slices' sizes
(HEAD). Nothing else was pulled, and nothing is proposed to be pulled without the owner's word. Every request is a row
of `runs/c202/gdelt/probe.csv`; the bodies are under `runs/license_reads/c202_gdelt/` (not in git).

## What the probe read

| Request | Answer |
|---|---|
| `https://www.gdeltproject.org/robots.txt` | `User-agent: *`, `Disallow: /data/`. The data files are not under this host's `/data/`; they are on `data.gdeltproject.org` |
| `http://data.gdeltproject.org/robots.txt` | HTTP 404: no robots file on the data host |
| Terms of use (`gdeltproject.org/about.html`) | "all datasets released by the GDELT Project are available for unlimited and unrestricted use for any academic, commercial, or governmental use of any kind without fee. ... You may redistribute, rehost, republish, and mirror any of the GDELT datasets in any form. However, any use or redistribution of the data must include a citation to the GDELT Project and a link to this website (https://www.gdeltproject.org/)." |
| The GDELT 2.0 announcement (blog, 19 February 2015) | the GKG 2.0 format: every article's themes, locations, persons, organizations, tone, every fifteen minutes, with translation of 65 languages |
| `gdeltv2/masterfilelist.txt` (HEAD) | 129,253,263 bytes: one line a file since February 2015, three files a slice (export, mentions, gkg); not pulled |
| `gdeltv2/lastupdate.txt` | the newest slice's three files with sizes: export 82,938 bytes, mentions 134,602, **gkg 6,598,771** (20:30 UTC, 6 November 2026) |
| `20250115120000.gkg.csv.zip` (HEAD) | 5,644,361 bytes |
| `20260601120000.gkg.csv.zip` (HEAD, then GET) | 5,105,266 bytes zipped, 15,755,046 unzipped, **1,218 records, 27 fields** |

## The fields that would give the same indices

The GKG 2.1 record (one a news article) carries, among its 27 tab-separated fields:

- **`V2SourceCommonName` and `DocumentIdentifier`** (fields 3 and 4): the outlet's domain and the article's URL. The
  June sample slice holds 1,218 articles of 241 outlets; the five largest are the Manila Times, Free Press Journal,
  iHeart, This Is Oxfordshire and the Liverpool Echo: a world corpus, with many small outlets, not the ERW's 43 feeds.
- **`V2EnhancedThemes`** (field 8): a list of GDELT themes with character offsets. The energy ones seen in the sample:
  `WB_507_ENERGY_AND_EXTRACTIVES` (95 articles of 1,218), `ENV_OIL` (60), `ENV_NATURALGAS` (34),
  `WB_539_OIL_AND_GAS_POLICY_STRATEGY_AND_INSTITUTIONS` (32), `FUELPRICES` (30), `WB_2299_PIPELINES` (24),
  `ECON_ELECTRICALGENERATION` (15), `ENV_SOLAR` (14), `WB_525_RENEWABLE_ENERGY` (14), `ECON_ELECTRICALGRID` (13),
  `ENV_COAL` (12), `WB_508_POWER_SYSTEMS` (12), `WB_509_NUCLEAR_ENERGY` (9), `ENV_NUCLEARPOWER` (5),
  `WB_1751_LIQUEFIED_NATURAL_GAS` (3). These map onto the indices' sectors (oil and LNG, gas, nuclear, solar and wind,
  transmission) by a written rule; **there is no data center theme** in the taxonomy seen, so the data center sector
  would need a word rule on the URL or a model's reading, as the ERW does today. No URL in the sample slice held
  "data center".
- **`V2EnhancedLocations`** (field 10): `type#name#country#adm1#adm2#lat#lon#featureid#offset`; the adm1 of a US
  place is the state (`USTX`, `USCA`...). In the sample, 412 of 1,218 articles name a US location and 50 state codes
  appear (the District of Columbia 199 mentions, New York 177, New Jersey 168, California 146, Texas 118, among
  them). A county or city comes as a type 3 location with its name: the ERW's place field.
- **`V2Tone`** (field 15): tone, positive score, negative score, polarity, among others: the tone field, already
  computed, for every article.
- **Friction** has no direct field. GDELT's themes hold `PROTEST`, `LEGISLATION`, `TAX_...` and the CAMEO event codes
  of the export file hold protest and legal-action events, but "opposition to an energy project" as the ERW defines
  it (a moratorium, a lawsuit, a permit denied, a rate case) is not a theme. A Friction Index from GDELT would be a
  rule over themes and event codes (coarse, free) or a model's reading of the article's title (the ERW's method; the
  GKG carries the URL, not the title, so a title would have to be fetched from the outlet, which the ERW does not
  do), or of the GKG's own quotation and name fields.

## The sampling plan, sized

Every slice is one request and about 5 to 7 MB zipped (15 to 20 MB unzipped, about 1,200 articles); there are 96
slices a day.

| Plan | Requests a week | Zipped GB a week | Unzipped GB a week | Articles a week | A year, zipped |
|---|---|---|---|---|---|
| Every slice | 672 | 3.9 | 10.6 | about 800,000 | 200 GB |
| One slice an hour (:00) | 168 | 1.0 | 2.6 | about 200,000 | 50 GB |
| Four slices a day (00, 06, 12, 18 UTC) | 28 | 0.16 | 0.44 | about 34,000 | 8.4 GB |
| One slice a day (12:00 UTC) | 7 | 0.04 | 0.11 | about 8,500 | 2.1 GB |

- **The proposal, if any:** four slices a day, read a day late (every file is final once written). 28 requests a
  week to one host that states no rate limit and no robots rule; kept after reading: the source, the URL, the date,
  the energy themes, the US locations and the tone of the articles with an energy theme (about 8 percent of a slice:
  roughly 2,700 articles a week, under 2 MB a week as CSV). The zipped raw files (160 MB a week) would stay under
  `warehouse/raw/gdelt/` and be pruned by the raw file rule. The history back to February 2015 at four slices a day
  is about 17,000 requests and 100 GB zipped: a backfill the owner would schedule, not this chain.
- **Storage:** the kept rows for a year at four slices a day, about 100 MB; a decade, about 1 GB. Nothing near the
  live set's budget; a Redivis table of a few million rows.
- **Cost:** no model is needed for the Attention Index by sector, state and tone (the themes and locations are given);
  a Friction Index to the ERW's definition would need a model reading of something the GKG does not carry (the
  title), so it would stay the ERW corpus's, or be a coarse theme rule, labeled as such.
- **What it would add:** a world corpus against the ERW's 43 feeds, the same four-slice sample every day since 2015,
  and a check on the ERW's Attention Index (the feeds' bias measured against GDELT's share of energy coverage by
  state). What it would not add: the ERW's reading of opposition, and the data center sector without a word rule.

## For the owner's ruling

1. Pull GDELT at four slices a day (28 requests a week, 160 MB zipped) as a second, world corpus for the Attention
   Index, with the citation and link the terms require on every table and page? Or one slice a day (7 requests)? Or
   not at all?
2. If yes, the backfill's depth: from 2025 (the ERW corpus's first week: 2,700 requests, 16 GB) or from 2015?
3. The data center sector in GDELT: a word rule on the URL (free, coarse) or a model reading of the GKG's names and
   quotations (a cost to estimate from a sample), or left to the ERW corpus alone?

Nothing of this is started. The ten requests are the probe's whole footprint.
