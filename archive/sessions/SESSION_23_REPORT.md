# Session 23 report

Energy Research Warehouse (ERW), session 23, run 2026-09-28 (UTC). **API spend: USD 0.4085**, under the USD 10 stop:
- **Fun fact bank:** USD 0.3834 in two seeds (0.2010 and 0.1824). The first bank was discarded after review; see Task 2.
- **Chart-of-the-week note and caption:** USD 0.0115 (0.0075 on a run whose pick was then corrected, and 0.0040).
- **Energy Roundup 2026-W39:** USD 0.0136 (headlines 0.0085, numbers summary 0.0051).

The remaining datacenter backfill was not run, as instructed. No key was printed or committed.

**Things to know first:**
- **The chart of the week for 2026-W39 is ERCOT HB_NORTH's peak premium.** The peak-minus-midday median spread over 2026-09-20 to 2026-09-26 was 28.08 USD/MWh, a robust z of 2.46 against 89 earlier weeks (92.1st percentile). The Roundup and its email carry it.

  ![ERCOT HB_NORTH: real-time prices by time of day](docs/analysis/2026-W39/chart_email.png)

  At ERCOT HB_NORTH from 2026-08-28 to 2026-09-26, median real-time prices were 29.01 USD/MWh overnight, 30.11 USD/MWh midday, and 50.09 USD/MWh at peak. In the latest 7 days, 2026-09-20 to 2026-09-26, the peak minus midday median gap was 28.08 USD/MWh, a robust z of 2.46 against its own history. *(The engine's note, as it passed the literal-number check.)*

- **Subscriber sending is switched on but still waits on three secrets:**
  - **`EMAIL_TOKEN_SECRET`** must be added as a GitHub secret and a Vercel variable. Its value is in `.env`, and it is already stored in Supabase's private schema. The GitHub token in `.env` cannot manage secrets (HTTP 403). Until it is set, the sender leaves subscribers out, so no subscriber email can go out without its unsubscribe link.
  - **`RESEND_API_KEY`** is needed on Vercel, so the site can send the confirmation email.
  - **A verified sending domain** is needed: Resend's test sender reaches only the account owner.
- **A word check was added to fun facts after the first seed.** The first seed's checks (span found in the source, numbers in the span) passed drafts that added claims around a true quote, for example "sparking the first American oil boom". Sourced facts are now also checked for word coverage and by an independent judge call. That bank was discarded and re-seeded.

## What was built

| Task | Result | API cost (USD) | Commit |
|---|---|---|---|
| (rulings) | The scorer must fill `mw` and `price_mentioned` when stated; the datacenter extractor excludes financings, chip or server purchases and non-datacenter campuses; matplotlib added | 0 | `2d3d06a` |
| 1 | Weekday digest (no weekend issue); Energy Week becomes the Energy Roundup, Sundays 23:00 UTC, with a Weekend section; Fun fact and Chart of the week sections; `/weekly` redirects to `/roundup` | 0 | `5894dae` |
| 2 | Fun fact engine, bank of 20 verified facts, the day's item re-verified before printing | 0.3834 | `4b044c8` |
| 3 | Automated Analysis (tool 26): ten templates, the engine, the chart of the week, `/analysis` with gallery and archive, the CAISO battery connector, the Roundup for 2026-W39 | 0.0251 | `0fa81df` |
| 4 | Ten topics, double opt-in, a signed unsubscribe in every email, suppression list, per-recipient emails, `EMAIL_SUBSCRIBERS` on | 0 | `eb1cd83` |
| 5 | Validator (107 of 107 pass), coverage (107 tables), live set, briefing, tools list (26), value check 700 of 700, screenshots, this report | 0 | final commit |

## Rulings applied

- **Scorer:** the prompt now says `mw_mentioned` and `price_mentioned` must be filled whenever the title or summary states one. Nothing was re-scored.
- **Datacenter extractor:** the prompt now says a financing, a chip or server purchase, or a non-datacenter campus is not a facility. Nothing was re-extracted.
- **"Other":** stories scored "other" stay "other". The topic map in `warehouse/news/topics.py` leaves "other" unmapped, so those stories reach only the full email.
- **QTS:** skipped.
- **Double opt-in and the tokened unsubscribe:** built in Task 4.

## Task 1: the schedule and the names

- **The digest runs Monday to Friday.**
  - The daily workflow still runs every day for the data.
  - On a Saturday or Sunday (UTC), `brief.py` and `email_digest.py --auto` print "SKIPPED: no weekend issue" and write nothing. `brief.py --weekend` overrides this.
  - `/digest/<date>` answers any weekend date without a digest with "No weekend issue", linking that week's Roundup.
  - The archive lists those weekend days. The two weekend digests already written (2026-09-26 and 27) stay.
- **Energy Week became the Energy Roundup.**
  - It is written and sent Sundays at 23:00 UTC, which is 4 PM Pacific (`.github/workflows/roundup.yml`, renamed with `git mv` from `weekly-brief.yml`).
  - It covers Monday to Sunday and opens with **Weekend**: the top three clusters among the stories published on the week's Saturday and Sunday.
  - The five stories of the week are then taken from the remaining clusters. This is the digest's rule that each section takes only clusters not shown above it.
- **Renames:**
  - `warehouse/news/weekly.py` became `roundup.py`, and the output moved to `docs/roundup/`. The Energy Week file `docs/weekly/2026-W39.md` stays where it was written.
  - The site's `/weekly` became `/roundup`, with permanent redirects from `/weekly` and `/weekly/<week>`.
  - The email is sent with `email_digest.py --roundup`; `--weekly` still works.
  - `pages.ts`, the home page, `/about`, `/subscribe`, `/terms`, the value check and the screenshot list were renamed to match.
- **New sections:** the digest's last section is **Fun fact**, and the Roundup's **Chart of the week** follows its numbers. Both appear in the emails; the chart is linked as an image from GitHub.

## Task 2: the fun fact engine

`warehouse/news/funfact.py` keeps `warehouse/news/facts/bank.csv`. Its stored sources are in `warehouse/news/facts/raw/` and the day's item is in `facts/items/<date>.json`, all in git, so the runner can re-verify.

- **Two kinds of fact:**
  - **Warehouse facts** are written by code from computed values: fuel price extremes, the oldest operating generators, state generation shares, ERCOT price extremes, retail sales leaders, curtailment records, and datacenter operators. The rows used are stored as the fact's source, and every number must pass the chat's literal-number check against them.
  - **History facts** are drafted by the model from one stored page: a Wikipedia plain-text extract or an EIA history page, saved with its URL, revision and retrieval time. The draft must return exact quotes.
- **What a sourced fact must pass:**
  - Every quote must be found in the stored page.
  - Every number must be in its quotes.
  - 85% of the fact's content words (70% of a sourced second half's) must be in the quotes or the page title.
  - At creation, an independent model call must find every claim in the quotes.
  - A pun holds no number, and a conjecture must be phrased as one.
  - A failed fact is kept in the bank as dropped, with its reason.
- **Rotation of the second half:**

  | Day | Second half |
  |---|---|
  | Monday | none |
  | Tuesday | a comparison of scale |
  | Wednesday | an on-this-day line, verbatim from Wikipedia's page for the date, filtered by energy words |
  | Thursday | an etymology, or a cross-field connection on odd ISO weeks |
  | Friday | a pun |

  Cross-field is never the default. When no verified second half of the day's structure exists, the fact runs alone.
- **Re-verification:** `brief.py` re-checks the item against the stored files before printing it, and leaves the section out on any failure.
- **Daily run:** `run_daily.sh` runs `funfact.py` (one new fact, and the day's item) before the brief. The workflow commits `warehouse/news/facts`.
- **The dictionary API was not used.** `api.dictionaryapi.dev` answered HTTP 522, so etymologies come from Wikipedia, whose articles hold them.
- **The first seed was discarded.** I reviewed it quote by quote, and 6 of its 12 history facts claimed more than their quotes said. Examples: Drake "struck oil" on the day the drill reached depth; Shippingport as "the world's first full-scale plant devoted purely to peacetime power"; fracking "first used in 1903 at Mt Airy", when the source says before 1903. The word check and the judge were then added.
- **The second seed:**
  - 20 verified facts: 9 warehouse and 11 history (Wikipedia 10, EIA 1).
  - 3 more were dropped by the checks: two for numbers or words not in the quotes, and one where the judge found a figure's year not stated. One more fact (Chicago Pile-1) lost its second half to the word check and runs alone.
  - One more was dropped at review: daylight saving time is not an energy fact first.
  - The bank's second halves are 3 puns and 1 cross-field; the rest run alone. Scale halves come from warehouse facts as the bank grows.
  - `--verify` re-checks all 20: 0 fail.
- **Em dashes:** stored sources hold them as hyphens (non-negotiable 2). The span check reads the two the same way.

## Task 3: Automated Analysis (tool 26)

- **Library:** `warehouse/analysis/templates/`. Each template has:
  - a method and parameters with defaults;
  - `compute()`, which returns a tidy frame naming its tables, the citations (`erw.cite`), a headline with its own history, and the sentences that hold every number a note may use;
  - `render()` in three sizes: the site's ECharts option, the email PNG (1200 by 750), and social PNGs (1200 by 627 and 1080 by 1080).

  The house style (`style.py`): the Stanford palette with cardinal first, Georgia titles, the ERW mark top right, and the source line burned into every PNG.
- **The ten templates.** "Earlier values" is the headline's own history on this machine, which decides eligibility.

  | Template | Headline this week | Earlier values | Robust z |
  |---|---|---|---|
  | peak premium by block (any 15-minute ISO) | ERCOT HB_NORTH peak minus midday, 28.08 USD/MWh | 89 | 2.46 (picked) |
  | day-ahead minus real-time by hour | 6.19 USD/MWh | 3 | not scored |
  | forecast error (EIA-930) | ERCOT MAPE 1.25% | 3 | not scored |
  | curtailment against midday prices (CAISO) | 28,725.99 MWh | 246 | 0.15 |
  | implied heat rate (trader view) | 14.68 MMBtu/MWh | 3 | not scored |
  | batteries against the evening peak (CAISO) | 6,195.87 MW, 17:00 to 21:00 | 54 | 0.6 |
  | negative-price hours by month | ERCOT HB_WEST, 6 in 2026-08 | 139 | 0.59 |
  | deals by month and type | 11 in 2026-08 | 10 | 1.08 |
  | datacenter facilities by state | 237 with a stated state | 0 | not scored |
  | chokepoint transits (internal) | Hormuz tankers 0.57 per day | 401 | 4.19 (internal, never picked) |

- **The engine, `run.py`:**
  - **The notability rule:** robust z = |x - median| / (1.4826 x MAD), capped at 10, with a mean-deviation fallback when the MAD is 0.
  - **Eligibility:** at least 8 earlier values, and a headline period that ended within 45 days.
  - **The pick:** the highest z among public templates.
  - **The note and caption:** drafted by the model under the literal-number check, with one retry; otherwise the note is the template's own sentences.
  - **Outputs:** `docs/analysis/2026-W39/`, `docs/analysis/social/` (both PNGs and the caption, for manual posting), `history.csv` and `templates.json`.
  - **Internal results** go to `warehouse/output/analysis_internal/`, which git ignores.
- **Two fixes before the pick.** The first run picked the datacenter template with z 10, for two reasons:
  - its history of new news facilities per week was mostly zeros, so the MAD was 0;
  - its headline was not what its chart shows.

  I added the fallback, and made that headline the stated-state count, with history only from stored weekly runs.
- **`/analysis`** shows:
  - the chart of the week (interactive), its note, source, rule and citations;
  - this week's results for every public template;
  - a gallery: pick a template and its parameters (ISO, hub, window and so on);
  - the archive, with `/analysis/<week>`.
- **What "run with its parameters" means here.** The gallery's charts are computed server-side by the same Python templates from public tables only, for every choice in each parameter grid. That is 226 charts, written to `docs/analysis/gallery/` and served from that cache; `run.py` recomputes them every week. The site does not run Python, so a value outside the grid cannot be requested.
- **Unavailable gallery cells:** 13 of 62 for peak premium, 22 of 78 for the spread, and 66 of 78 for negative hours. Each names its reason, for example "no complete month of hourly prices", because the rolling tables hold 30 days.
- **The storage template needed a new table.** EIA-930 returns no battery rows, so I added `warehouse/connectors/caiso_outlook.py` and the table `caiso_battery_storage`:
  - CAISO's Today's Outlook battery output, 5-minute, public;
  - backfilled to 2025-08-24: 398 days, 343,872 rows;
  - the two clock-change days are not written, under the complete-day rule;
  - in the daily run for the last 30 days, and restored from Redivis in CI.

  It is not in the Supabase live set. It is 5-minute data, the database is at 330.8 of 400 MB, and no page reads it live.
- **The Roundup and the email:** `docs/roundup/2026-W39.md` was written with its Weekend section and the chart. The email renders the image from `raw.githubusercontent.com`, which is why the Roundup workflow pushes before it sends.

## Task 4: topics, double opt-in, unsubscribe

- **Topics:** `/subscribe` has ten checkboxes: power prices; gas and LNG; oil; nuclear; renewables and storage; transmission and grid; datacenters and AI power; deals and capital; policy; geopolitics.
  - They are stored per subscriber in `subscribers.topics`, which has a check constraint.
  - They map from the scorer's sectors, in `warehouse/news/topics.py` and `site/lib/topics.ts`.
  - The website digest stays complete. The email's top stories are the brief's first five items in the chosen topics, drawn from all its sections in rank order. The numbers, the fun fact and, on Sundays, the chart are always included.
- **Migration 007:**
  - adds `topics`, `confirmed_at` and `unsubscribed_at`;
  - adds `email_suppressions`;
  - adds a private schema holding the token secret;
  - adds two security-definer functions the anon key may call, `subscribe_confirm` and `subscribe_unsubscribe`.

  A token is HMAC-SHA256 of the lower-cased address plus the purpose, and the database checks it.
- **Tested in a rolled-back transaction as anon:**
  - a token for the wrong purpose is refused, and the right one confirms;
  - anon cannot read subscribers, the suppression list, the settings or the token function;
  - a topic outside the ten is refused;
  - unsubscribe marks the row and adds the address to the suppression list.
- **Tested end to end on a local build:**
  - sign-up stores the row: "unsent", because no Resend key is set locally;
  - a bad link gives "badlink", and the right link "confirmed";
  - the sender then lists the address with its topics;
  - the one-click POST unsubscribe answers 200, and the sender then lists nobody and suppresses the address.

  The test row and its suppression were deleted afterwards. The table holds 0 subscribers, as at the start.
- **The sender, `email_digest.py`, sends one email per recipient:**
  - fixed recipients get the full top five, and confirmed subscribers get their topics;
  - every email carries the recipient's signed unsubscribe link and List-Unsubscribe headers for one-click unsubscribe;
  - suppressed addresses get nothing, fixed recipients included.

  A stubbed send checked both kinds of email.
- **`EMAIL_SUBSCRIBERS: "1"`** is set in the daily and Roundup workflows.

## Task 5

- **Validator:** 107 of 107 tables pass, exit 0.
- **Coverage:** 107 tables, with `caiso_battery_storage` under power.
- **Live set:** loaded. The catalogue and sources match (107 and 141), and `pg_database_size` is 330.8 MB.
- **Briefing:** `package/llms.txt` covers the weekday digest, the Roundup, the battery table and Automated Analysis.
- **Tools list:** `docs/platform-tools.md` has 26 tools. Tools 1, 9, 14 and 25 are updated, and 26 is added. `CLAUDE.md` says 26. `docs/OVERVIEW.md` was regenerated: 23 live tools and 18 pages.
- **Value check:** 700 of 700 values match Supabase (`/roundup`: 20 of 20).
- **Screenshots:** every page at 1280 and 390 px, plus `/roundup/2026-W39`, `/digest/2026-10-03` (no weekend issue), `/analysis` and `/analysis/2026-W39`.

## Decisions made without a human

1. **Weekend before the five stories.** The five stories come from the clusters not shown under Weekend, the digest's rule that each section takes only clusters not shown above it.
2. **Earlier Energy Week files stay.** `docs/weekly/` keeps them, and the Roundup archive shows a week's Energy Week where it has no Roundup.
3. **The gallery is a precomputed grid.** See Task 3 for what that allows.
4. **Stricter fact checks.** I added word coverage and a creation-time judge to the fact checks. The prompt's checks alone passed wrong facts.
5. **New CAISO table.** I added the battery connector rather than ship a storage template with no data.
6. **Fixed recipients get the full email** and the same unsubscribe link, and an unsubscribe suppresses them too.

## Open questions for a human

1. **Secrets:** add `EMAIL_TOKEN_SECRET` (value in `.env`) to GitHub and Vercel, `RESEND_API_KEY` to Vercel, and verify a sending domain for `DIGEST_FROM`.
2. **Most rolling-window templates cannot be picked yet.** They need 8 weeks of stored history, or longer tables in CI; the ERCOT history tables are not on the runner. On GitHub, the first Sunday's candidates will be curtailment, storage and deals.
3. **Social posting is manual.** The files are in `docs/analysis/social/`.
