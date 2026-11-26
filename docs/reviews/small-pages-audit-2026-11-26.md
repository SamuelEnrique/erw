# The small pages, audited as a hostile first reader would: `/about`, `/resources`, `/shoulder`, `/attention`, `/subscribe`

Session 10238, 26 November 2026, chain 710 (part D), the old laptop. Read as a first reader who opens each page cold and wants the first sentence that is not true: a fund analyst on `/about`, a developer on the resource map, a battery planner on `/shoulder`, a reporter on `/attention`, and someone deciding whether to give the ERW an email address on `/subscribe`. In the form of `docs/reviews/home-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/small-pages-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called (`ERW_SPEND_CAP_USD=0` for every python run), no request to any service; the subscribe route was never called.
- Each finding's test is on its own branch, `wip/audit-small-<n>`. Branches that change only words are for landing, merged as `wip/audit-small-words`; a branch whose fix would change what is drawn, stored or printed as a figure carries the test only and is not for landing.
- `/privacy` and `/terms` are Samuel's words: where they disagree with the code it is listed at the foot, and neither is changed.

## In short

- **The numbers are right.** Every figure each page's default view prints came out to the digit in an independent restatement from the page's own files: `/shoulder`'s ERCOT, all 2,132 monthly figures of 93 months re-done from EIA's own workbook by the method's words (the default, August 2026: a 5-hour shoulder from 19:00 to midnight, the fleet's 1.65 hours, 3.66 needed, 6.58 on the ten worst days of 2026), the ten worst days and their ranks; `/attention`'s default cell (data centers, the week of 2 November: 63 of 631 judged stories, 9.98, 30.16, -0.11, the 19 opposition stories by kind), its 30 rising rows and its footer; the resource map's legend (1.591 to 13.582 m/s, the files' own lowest and highest cells) and its ten decisions; `/about`'s 31 tools (6, 19, 2, 4). One note counts two stories no week holds (27,419 for 27,417, finding 14).
- **`/subscribe` says the public site cannot read an address back (finding 1).** Since migration 034 the site's server writes every sign-up with the warehouse's service key, which reads the whole table. `/terms` says the same; listed for Samuel. Fixed in words, with the suppression list named.
- **`/subscribe` describes an email the sender no longer makes (finding 2):** "the top 5 headlines", the hubs' day-ahead averages and the three closes, "every number ... names its table". An issue in the v2 form goes out as its opening number, its four-line numbers block (two of 12 November's four are outlets' figures), the first three stories, the chart and the fun fact. Fixed in words.
- **`/about` names the wrong model for scoring (finding 3)** ("the newest Sonnet-class model"; Claude Haiku 4.5 since 12 October), says the Digest covers "the 24 hours before it is written" (up to 96 since session 2701) and that the Roundup opens with the weekend's stories (finding 8). Fixed in words.
- **"4 PM Pacific" is 3 PM until mid-March (finding 5)**, on `/about` and `/subscribe`; "a signed unsubscribe link that works in one click" opens a page that asks (finding 6); "never shared" leaves out Resend, which receives every address (finding 7). Fixed in words; how to ask for removal is Samuel's to say.
- **The confirmation link confirms on a GET (finding 4, for ruling)**, the very weakness that moved the unsubscribe link to a button in session 59: a mail scanner that follows it confirms an address that may never have asked.
- **The resource map says coal has no layer (finding 9)** though the coal fields are drawn since 19 November, and says its queue overlay draws "the grids whose operators allow it", naming ISO-NE, whose queue table the ERW holds as "license needed" (finding 10; the drawing is the map audit's open ruling). `/shoulder` dates ERCOT's battery output "from January 2019" (November 2024) (finding 11); `/attention` says "the four weeks before" where early weeks have one to three (finding 12). Fixed in words.
- **Eleven branches fix words and move no figure** (`-1` to `-3`, `-5` to `-12`, merged as `wip/audit-small-words`), drawn and read: pass; **three carry a test only, for ruling** (`-4`, `-13`, `-14`). No data request. Nothing needs the key. No security weakness of high severity was found.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/about/page.tsx` | `/about`: what the ERW is; how the Digest and the Roundup are made (stories, scoring, headlines, sections, links, numbers, schedule, the chart, the fun fact, the five numbers); the platform's counts (`DOCS.platform`, from `docs/platform-tools.md` by `site/scripts/build-content.mjs`); Ask's rule and score; every tool's line (`site/lib/pages.ts`); the glossary |
| `site/app/resources/view.tsx`, `ResourceMap.tsx`, `Decisions.tsx`, `grid.worker.ts`, `layer/[name]/route.ts`, `overlay/{plants,queue,datacenters}/route.ts` | The Resources tab of `/map` (`/resources` opens it): the switches, the canvas map, the legends, the hover, the decisions, the method note; the layer files and the overlays behind the release gate |
| `site/lib/resources.ts`, `site/lib/resourcesdata.ts` | The contract with the lists of layers (`site/data/resources/manifest.json`, `manifest_added.json`, `hover_fields_added.json`), the grid decoder, the levels, the plane (`KX`), the toggles (`GROUPS`, `EXPECTED`, `MEASURE`), the queue's grids (`QUEUE_GRIDS`); the server's reads of the files and of `energy_projects` and `datacenter_facilities` |
| `docs/methods/resources.md`, `map_layers.md`, `resource_layer_notes.md`, `resource_layers_table.md`; `warehouse/connectors/resource_layers.py`, `warehouse/derived/resource_*.py` | The method document drawn under the map; the data side's builders |
| `site/app/shoulder/page.tsx`, `read.ts`, `Decisions.tsx`; `site/lib/shoulder.ts` | `/shoulder`: every figure a row of `shoulder_hours_monthly` with its check key; the opening month (the latest holding every figure); 17 decisions |
| `warehouse/derived/shoulder_hours.py`; `docs/methods/shoulder_hours.md`, `shoulder.md`, `impossible_hours.md`, `eia930_caiso_break.md` | The builder (EIA-930's per-BA workbooks, CAISO's supply by fuel, `storage_buildout_monthly`, `caiso_curtailment_daily`) and its notes |
| `site/app/attention/page.tsx`, `AttentionView.tsx`; `site/lib/attention.ts` | `/attention`: the view over `site/data/attention.json` and the week files `site/public/attention/stories/<monday>.json`; the opening week, the cells, the rising rows, the places, the keys |
| `warehouse/derived/attention_index.py`, `attention_classify.py`, `attention_trace.py`; `docs/methods/attention.md` | The builder of the three tables and the page's files; the classifier; the note with the accuracy measured on 200 stories |
| `site/app/subscribe/page.tsx`; `site/app/api/subscribe/route.ts`, `confirm/route.ts`; `site/app/api/unsubscribe/route.ts`; `site/lib/supabase.ts` (`insertRow`, `writeConfig`), `site/lib/guard.ts`, `site/lib/emailtoken.ts`, `site/lib/topics.ts` | `/subscribe` and the three routes behind it |
| `warehouse/supabase/migrations/005`, `006`, `007`, `018`, `028`, `034`; `warehouse/news/email_digest.py` | The subscribers table, its grants and functions, the suppression list, the send claims; the sender |
| `site/app/privacy/page.tsx`, `site/app/terms/page.tsx` | Samuel's words on what is stored; read, not changed |
| Read from the main copy, never written | `shoulder_hours_monthly` (built 2026-10-04 19:34 UTC), `storage_buildout_monthly` (2026-10-03), EIA's ERCO workbook of 2026-10-04 (`warehouse/raw/eia930_emissions/20261004T021545Z/`), `energy_projects` (2026-10-03) |

## How every number here was computed

- **The restatement:** `restate.py` (standard library and `openpyxl`, nothing of the ERW imported) re-does: `/about`'s counts by reading `docs/platform-tools.md`'s rows itself; the resource map's legend by decoding every level of the wind layer's files, its ticks by the page's rule, the toggles from the two lists and the files on disk, the Marcellus's area from the plays file, the queue overlay's rows from `energy_projects`; `/shoulder` from EIA's own ERCO workbook (hour-ending stamps moved to hour starts, the impossible-hour rule A written again from `impossible_hours.md`, Central time by the US rule, the complete days, the 90 percent rule, the average day, the midday surplus, both shoulder measures, the fleet from `storage_buildout_monthly`, the ten worst days of 2026), every ERCOT month set against the table; `/attention` from the week files of the same build (the classified count, the cell, the kinds, the tone, the rising rows from the four weeks' files, the places, the footer), with the one figure no week file holds (the stories scored 0 and not sent) taken from `attention.json`.
- **The pages as drawn:** `draw.mjs`, run from `site/` with `register.mjs` (the site's own loaders and a stand-in for `components/Brand.tsx`), draws `/about`, `/subscribe`, `/shoulder` (its read answered from the main copy's `shoulder_hours_monthly`), the `/attention` view (with its own `data/attention.json`) and the resource view (the canvas is not drawn; every word around it is). `draw2.mjs` renders the two changed method notes fresh through the site's `render`. No request leaves the machine.
- Copies of the scripts and their printouts are in `docs/reviews/small-pages-audit-2026-11-26/` (written to run from `runs/c10238/` of a worktree).
- **Not measured here:** the live figures (the main copy's tables are older than the live set's: the live `/shoulder` opens on a later month than August 2026); `/shoulder`'s two California series, which were not restated from source (their rows were read for the decisions' counts only); the resource layers other than the default one; the subscribers table, which only the service key reads.

## The arithmetic re-done

| Page | Figure | The page (drawn from the same rows) | Restated | Gap |
|---|---|---|---|---|
| `/about` | The platform | "31 tools ... 25 of them have a working data layer (6 complete, 19 partial), 2 are not built and 4 are planned" | 31, 6, 19, 2, 4 | 0 |
| `/resources` | The default layer | wind speed at 100 m, m/s, over the contiguous states | `firstLayer`: the wind speed layer | 0 |
| | Its legend | 1.6, 5.0, 6.0, 7.0, 8.0, 9.0, 13.6 | the list's 1.591 and 13.582 are the files' lowest and highest held cells (433,080 cells of 0.05 degrees); one decimal for a range of 11.99 | 0 |
| | The plane | "(0.7934)" | cos 37.5 degrees = 0.7934 | 0 |
| | The decisions | "Decisions on this page (10)" | 10 | 0 |
| | "the Marcellus is ... 58,326 here" | 58,326 | `Area_sq_mi` 58,326.38 in the plays file | 0 |
| | The switches | 15 layers held, uranium, critical minerals and the gross capacity factor greyed | the same; coal fields held (`manifest_added.json`) | **Finding 9** (the words) |
| `/shoulder` | The default month | August 2026 (September held, not every figure) | the latest ERCOT month with all 20 required figures: 2026-08 | 0 |
| | The summary and headlines | 5 hours, 19:00 to 24:00 (midnight); 1.65 hours at full power, covering 1.65; 3.66 needed; 6.58 on the ten worst days of 2026; 66,629.88 MWh above the mean; 18,204.50 MW holding 30,019.80 MWh | the same, from EIA's workbook | 0 |
| | Every ERCOT month | the table's 2,132 monthly figures, 2019-01 to 2026-09 | 2,132 of 2,132 equal to 0.0001 (no hour of demand blanked by rule A in this workbook) | 0 |
| | The ten worst days of 2026 | ranks, MWh above the mean, hours needed, batteries discharged; 274 days ranked | 10 of 10 equal, 274 | 0 |
| | The decisions' counts | "13,909 MW and 21,579 MWh"; "California 15,760 MW"; "every month of 2026 and eleven of the twelve of 2025" cut at midnight; "01:00 and 04:00 in 60 of the 93 months, the last of them May 2024"; six months both sources hold | 13,909.3, 21,578.8, 15,759.8; 9 of 9 and 11 of 12; 60 of 93, last 2024-05; 6 | 0 |
| | ERCOT's battery output | "from January 2019" (the panel's note) | held from November 2024 | **Finding 11** |
| `/attention` | The opening week and cell | data centers, every story, week of 2026-11-02 | the latest week with 50 classified or more, none after the build's: 2026-11-02 | 0 |
| | The headline row | 63 stories of 631 judged (518 classified, 113 scored 0 and not sent; 631 held); 9.98; 30.16; 19 stories: 11, 6, 1, 1; -0.11 | the same from the week file | 0 |
| | What rose | 30 rows (7 sectors, 23 states) | 30 of 30 equal | 0 |
| | The places, the footer | 3 places; 8,119 stories, 254 reporting opposition, 5 weeks | the same | 0 |
| | The note | "8119 of the 27419 stories held" | the weeks hold 27,417 | **Finding 14** |

## Each claim against the files and the code

| Claim | Where | What the files and code do | Verdict |
|---|---|---|---|
| "Scoring. A model (the newest Sonnet-class Claude model the API lists) scores every story" | `/about` | `NEWS_SCORE_MODEL = "claude-haiku-4-5"`, fixed since session 206 | **Finding 3** |
| "The digest covers the 24 hours before it is written"; the Roundup "opens with the weekend's top stories" | `/about` | `window_start`: from the previous issue's end, at most 96 hours (12 November: 96 hours); the v2 Roundup opens with its opening number and five numbers, "Weekend" under More | **Finding 8** |
| "written and sent on Sundays at 23:00 UTC (4 PM Pacific)" | `/about`, `/subscribe` | `0 23 * * 0`: 3 PM on Pacific standard time | **Finding 5** (the same words on `/digest/<day>` and `/roundup` are not this audit's pages and are not changed) |
| Ask "states no number a query of the warehouse did not return", "19 of 30" | `/about` | the Ask audit's finding 4 (`wip/audit-ask-4`) | Cited, not repeated |
| "Tables licensed for internal use only, such as PJM market data ... never shown" | `/about` | the data audit's finding 6 (the standard's rule names PJM alone; held tables read "license needed") | Cited |
| The sections, one event once, links, numbers, chart, fun fact, five numbers | `/about` | as `brief.py` and `roundup.py` say beside each claim (`AI_MIN_SIG = 5`, `ALSO_MAX = 3`, `MOVERS_N = 5`, `WINDOW_CAP_HOURS`); tonight's Digest audit read the issues | Right as far as read here |
| "A kind with no layer among the files (coal, uranium, critical minerals, and the gross capacity factor of wind) is a greyed switch" | `/resources`, decision `kinds-named`; the method document | the coal fields are a layer since 19 November (drawn in their own group) | **Finding 9** |
| "from the queue reports of the grids whose operators allow it: ERCOT, SPP, CAISO, ISO-NE" | `/resources`, the method note | `isone_interconnection_queue` "license needed" since 21 October; 1,594 ISO-NE rows at a county (149,817.7 MW) on this copy are drawn | **Finding 10** (words); the drawing is the map audit's open ruling (faults row 6, `wip/alt-map-1`) |
| "The reports give a county, not a site ... nothing is drawn at a site" | `/resources` | the code draws a row of `geo_precision` point at its point; no queue row of this copy has one (county or none) | Right on the rows held |
| "Every file is read from this site; the page asks nothing of any other" | `/resources` | the layers and overlays are this site's addresses | **Right** |
| "within 0.01 degrees of it for most layers, and no feature is dropped" | decision `simplified` | 6 of 9 shape layers within 0.01 (two not simplified), three at 0.015 to 0.03 | **Right** |
| "The average speed of the wind 100 meters above the ground, modelled over 2007 to 2013" | `/resources`, the switch's line | the file's metadata, 2007 to 2013 | **Right** |
| The shoulder's definitions (the fold, the decisions) | `/shoulder` | written again from the words and set against EIA's workbook: 2,132 of 2,132 | **Right** |
| "EIA-930 hourly demand, solar, wind and battery output, from January 2019" | `/shoulder`, the panel | battery output from November 2024 | **Finding 11** |
| "an hour of demand that could not have happened (zero, or more than a quarter away ...)" | `/shoulder`, the fold | rule A has a third test, one third to three times the grid's median (its own decision says so) | **Finding 11** |
| "The fleet is the batteries operating that month in EIA's monthly generator inventory" | `/shoulder` | `storage_buildout_monthly` by balancing authority; "operating" holds EIA's standby and out-of-service units (the home audit's finding 5: 200 MW of ERCOT's 18,204.5) | Cited, not repeated |
| "Each story was read once by a model from its title and summary" | `/attention` | a story is classified once; `claude-sonnet-5-5` | **Right** |
| Tone, "the least reliable field (0.87 against the hand labels)" | `/attention` | 0.870, the lowest of the eight fields measured | **Right** |
| "against the mean of the four weeks before (a week without a row counts as zero)" | `/attention`, What rose; the hovers; the note | the classified weeks among the four: 1, 2, 3 and 4 for the weeks of 12, 19, 26 October and 2 November | **Finding 12** (the default week is right) |
| "The headline is the warehouse's own one-line reading; the outlet's title is not republished" | `/attention` | the week files carry the ERW's headline | **Right** |
| "The public site can add an address but cannot read one back; only the warehouse's own service key can" | `/subscribe` (and `/terms`) | the site's server writes with the service key since session 301 | **Finding 1** |
| What the weekday and Sunday emails hold; "Every number comes from the warehouse and names its table" | `/subscribe` | the sender's v2 form: opening number, numbers block, three stories, chart, fun fact; outlets' figures | **Finding 2** |
| "Nothing is sent to the address until the link in it is followed" | `/subscribe` (and `/terms`) | a GET of the link confirms | **Finding 4** |
| "a signed unsubscribe link that works in one click" | `/subscribe` (and `/terms`) | the link opens a page that asks; one click only from a mail program's own button | **Finding 6** |
| "never shared or sold"; "never shared" | `/subscribe` | each address goes to Resend for the confirmation and every issue | **Finding 7** |
| "you can ask for it to be removed at any time" | `/subscribe` | no address or form for the request is named on the page | For Samuel (finding 7) |
| "Too many sign-ups just now ... try again in an hour"; five an hour, 200 confirmations a day | `/subscribe` | `limited(req, "subscribe", 5, 3600)`, `subscribe_day` 200 | **Right** |

## What is stored about a subscriber, and where it goes

| What | Where it goes | What is stored, and where |
|---|---|---|
| The address, the two choices, the topics | `POST /api/subscribe` (same origin, not a scripted client, 5 an hour per visitor, 8 kB at most); written by the site's server with the service key | `subscribers`: id, email, created_at, source `site`, daily, weekly, topics; no unique constraint, so a second sign-up is a second row (the sender keeps an address's latest confirmed choice) |
| The confirmation | Resend's API (the address, the choices, the topics' names, the signed link) | nothing more in the ERW; Resend's own records under its terms |
| The confirmation link followed (a GET) | `subscribe_confirm` checks the HMAC in the database | `confirmed_at` on every unconfirmed row of the address; the address taken off the suppression list |
| Each issue | the sender reads confirmed, not unsubscribed rows with the service key and posts each email to Resend with the unsubscribe headers | `digest_sends`: the issue, the day, the count of recipients, no address |
| An unsubscribe (the page's button, or a mail program's one-click POST) | `subscribe_unsubscribe` | `unsubscribed_at`; the address in `email_suppressions` for good |
| The visitor's IP address | the limits | in the server's memory for the hour; a keyed code of it for the day with a count (`/privacy`, "Limits on requests") |
| A failed write | the server's log | Supabase's answer, its first 200 characters |

## For Samuel: the words of /privacy and /terms (his own, not changed)

- `/terms`, "Subscribers": "The public site can add an address but cannot read one back; only the warehouse's own service key can." Since session 301 the site's server holds that key and writes every sign-up with it (finding 1).
- `/terms`: "every email carries a signed one-click unsubscribe link". The link opens `/subscribe`, which asks; one click unsubscribes only from a mail program's own button (finding 6).
- `/terms`: "Nothing is sent to an address until it confirms through the signed link in its confirmation email". A mail scanner's GET of that link confirms (finding 4).
- `/terms`: "is removed on request"; `/subscribe`: "you can ask for it to be removed". Neither says where to ask, and no route removes an address.
- `/privacy`, "Other parties": names Vercel, Supabase and cdnjs; not Resend, which receives every subscriber's address and every email sent to it (finding 7).
- `/privacy`, "What else the site stores": the sign-up line is right; it does not name the suppression list (`/terms` does).

## What a first reader's own check would hold that this does not

| Item | Size | From |
|---|---|---|
| The date of the rows behind `/shoulder`'s opening month | the table's build is not printed on the page | `shoulder_hours_monthly`'s header |
| On `/attention`, the build's date beside the week picker | printed at the foot only ("Built 2026-11-16 09:24 UTC") | `attention.json` |
| On `/subscribe`, a sample of the email | none on the page | `email_digest.py` writes a saved copy, not published |
| On the resource map, which layers are switched on by default and why | one, the wind speed | decision `opens-on-wind` |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | `/subscribe` says the site cannot read an address back | every sign-up since session 301 | words | `wip/audit-small-1` (`9696b1783`) |
| 2 | Medium | `/subscribe` describes the email before the v2 form | 4 of its sentences; 3 stories sent, not 5 | words | `wip/audit-small-2` (`b48778ff5`) |
| 3 | Medium | `/about` names the newest Sonnet as the scorer | every story scored since 12 October | words | `wip/audit-small-3` (`43992c658`) |
| 4 | Medium | The confirmation link confirms on a GET | not measurable here | for ruling | `wip/audit-small-4` (`4464dd488`, test only) |
| 5 | Low | "4 PM Pacific" | 3 PM from 1 November to 14 March | words | `wip/audit-small-5` (`420770019`) |
| 6 | Low | "a signed unsubscribe link that works in one click" | two steps from the link | words | `wip/audit-small-6` (`495120029`) |
| 7 | Low | "never shared" leaves out Resend; no way to ask for removal named | every address | words; the contact for ruling | `wip/audit-small-7` (`a2352b08a`) |
| 8 | Low | `/about`'s Digest window and the Roundup's opening | 96 hours on 12 November | words | `wip/audit-small-8` (`ec48c699e`) |
| 9 | Low | The resource map says coal has no layer | 1 of 10 decisions; a note's sentence | words | `wip/audit-small-9` (`2d37d45b2`) |
| 10 | Low | "the grids whose operators allow it" names ISO-NE | 1,594 rows, 149,817.7 MW on this copy | words | `wip/audit-small-10` (`e24758f97`) |
| 11 | Low | `/shoulder`'s battery dates and the impossible-hour sentence | 2 sentences | words | `wip/audit-small-11` (`628ab2117`) |
| 12 | Low | `/attention`'s "four weeks before" | 3 of the 4 weeks with rising rows | words | `wip/audit-small-12` (`65ab20199`) |
| 13 | Low | `/subscribe`'s unsubscribe form draws any address text | crafted links only | for ruling | `wip/audit-small-13` (`4e2d847a7`, test only) |
| 14 | Very low | `/attention`'s note counts two stories no week holds | 27,419 for 27,417; 29.6 percent either way | for ruling | `wip/audit-small-14` (`aa5f77be1`, test only) |

## 1. "The public site ... cannot read one back" (Medium)

- **Where.** `site/app/subscribe/page.tsx`, "What is stored".
- **Why it is wrong.** Migration 034 (session 301, the security review's M1) took the anon key's insert right away; `insertRow` writes with `writeConfig()`, the service key when the server holds it, and the subscribe route writes the row with it. That key reads every row. The page's promise is about the anon key, which no longer writes at all. It also leaves out the suppression list, which keeps an unsubscribed address for good.
- **The test.** `tests/test_audit_small_1.py` (the write path and migration 034; the words fail on main).
- **The fix, words only.** "... in the ERW's Supabase database; an address that unsubscribes is also kept on a suppression list, so that it is never emailed again. The site's server writes the address with the warehouse's service key, which can read the table and which no browser is given; no page of the site reads an address back."

## 2. The email described (Medium)

- **Where.** `site/app/subscribe/page.tsx`, "What the email is".
- **Why it is wrong.** For an issue in the v2 form (the newest Digest, of 12 November, and the newest Roundup, W45) `render` sends the opening number, the issue's own "The numbers" (on 12 November: Henry Hub, US48 demand, a 580 MW storage figure and a USD 2.1 billion deal, the last two "the outlet's figure, not a table's"), the first three stories (`numbered(..., 3)`), the chart and the fun fact; with fewer topics than all, up to five stories in them. The page promised the top 5, the hubs' day-ahead averages and three closes, and that every number names its table.
- **The test.** `tests/test_audit_small_2.py` (the sender's lines and the newest issue's form; the words fail on main).
- **The fix, words only.** The two bullets say what goes out (opening number; numbers; the first three stories; the chart; the fun fact; the rest one link away); "Each figure says where it came from: a warehouse table, as on this site, or, for a figure a news story reported, its outlet"; the topics' rule with three and five.

## 3. The scoring model (Medium)

- **Where.** `site/app/about/page.tsx`, "Scoring".
- **Why it is wrong.** `warehouse/news/score.py` scores with `NEWS_SCORE_MODEL = "claude-haiku-4-5"` since the owner's ruling of 12 October (session 206); `pick_model`, the newest Sonnet-class model, is for the other steps.
- **The test.** `tests/test_audit_small_3.py`.
- **The fix, words only.** "A model (Claude Haiku 4.5, the one model fixed for scoring since 12 October 2026; the digest's other steps use the newest Sonnet-class model the API lists) scores every story ...".

## 4. The confirmation link confirms on a GET (Medium, for ruling)

- **Where.** `site/app/api/subscribe/confirm/route.ts`.
- **Why it matters.** On 29 September a mail scanner or link prefetcher followed an unsubscribe link in a sent email and unsubscribed the only fixed recipient; session 59 made that link open a page that asks. The confirmation link is the same kind of link and still acts on a GET: a scanner that follows it confirms the address, so a sign-up made by someone else becomes a confirmed subscription without the owner of the address acting. The page's "Nothing is sent to the address until the link in it is followed" holds only for people.
- **The test.** `tests/test_audit_small_4.py` (test only; its second class fails on main).
- **For Samuel's ruling.** The link opens `/subscribe`, which asks, and a POST confirms (as the unsubscribe does). Default "left as it is". The effect: no confirmation by a link's GET alone; how many past confirmations were a scanner's cannot be told (the table keeps only `confirmed_at`, and is not read here).

## 5. "4 PM Pacific" (Low)

- **Where.** `site/app/about/page.tsx`, "Schedule"; `site/app/subscribe/page.tsx`, the Sunday line.
- **Why it is wrong.** The Roundup runs at 23:00 UTC (`roundup.yml`; pg_cron, migration 015): 4 PM on daylight time, 3 PM from the first Sunday of November to the second Sunday of March (this Sunday, 29 November, 3 PM).
- **The test.** `tests/test_audit_small_5.py`. **The fix, words only.** "23:00 UTC (4 PM Pacific in summer time; 3 PM from early November to mid-March ...)"; on `/subscribe`, "Sundays, 23:00 UTC (4 PM Pacific in summer time, 3 PM in winter)". `/digest/<day>` and `/roundup` print the same "(4 PM Pacific)"; they are the Digest audit's pages and are not changed here.

## 6. "Works in one click" (Low)

- **Where.** `site/app/subscribe/page.tsx`, "Double opt-in".
- **Why it is wrong.** Since session 59 a GET of the link redirects to `/subscribe?confirm=1`, which asks; the button posts. One click unsubscribes only from a mail program that shows its own button (RFC 8058, the List-Unsubscribe headers the sender sets).
- **The test.** `tests/test_audit_small_6.py`. **The fix, words only.** "it opens this page, and one press of its button stops every email (the link alone changes nothing, so a mail scanner that follows it cannot unsubscribe you); a mail program that shows its own unsubscribe button stops them in one click."

## 7. "Never shared" (Low)

- **Where.** `site/app/subscribe/page.tsx`, the privacy line and "What is stored".
- **Why it is wrong.** The route posts the address to `api.resend.com` for the confirmation, and the sender posts it for every issue. And the page says one may ask for removal without saying where.
- **The test.** `tests/test_audit_small_7.py`. **The fix, words only.** "... is never sold; it is shared with no one but Resend, the service that sends the emails (the confirmation and every issue), and you can ask for it to be removed at any time."
- **For Samuel's ruling.** Where a reader asks for removal (an address or a form). Default "left as it is" (nothing named).

## 8. The Digest's window and the Roundup's opening (Low)

- **Where.** `site/app/about/page.tsx`, "Schedule".
- **Why it is wrong.** Since session 2701 the window opens at the previous issue's end, at most 96 hours back (`WINDOW_CAP_HOURS`); the issue of 12 November covers 96 hours. The Roundup in the v2 form opens with its opening number and the week in five numbers; "Weekend" is under More.
- **The test.** `tests/test_audit_small_8.py`. **The fix, words only.** "The digest covers the news since the previous issue was written, at most 96 hours back (about 24 hours on a weekday after a weekday, the weekend in Monday's issue) ..."; "opens with its opening number and the week in five numbers (the weekend's stories are under More)".

## 9. Coal, said to have no layer (Low)

- **Where.** `site/app/resources/Decisions.tsx`, `kinds-named`; `docs/methods/resources.md`, session 8603's "Coal, uranium and critical minerals are named".
- **Why it is wrong.** The data machine's list (`manifest_added.json`, built 19 November 16:51 UTC) holds the coal fields, their file is on the server, and the map draws them in their own group; the same method document says so further down.
- **The test.** `tests/test_audit_small_9.py`. **The fix, words only.** The decision's list drops coal and adds "Coal has a layer since 19 November 2026, the coal fields."; the note's dated section gains one sentence saying the coal fields arrived that day. `test_session8603`'s rule (the fold and the note one list) holds.

## 10. "The grids whose operators allow it" (Low)

- **Where.** `site/app/resources/view.tsx`, the method note's queue paragraph.
- **Why it is wrong.** It names ISO-NE among the grids whose operators allow their rows, while the ERW's own license status holds `isone_interconnection_queue` as "license needed" (needs written permission, ISO-NE's terms) since 21 October. On this copy 1,594 ISO-NE rows at a county (149,817.7 MW) would be drawn.
- **The test.** `tests/test_audit_small_10.py`. **The fix, words only.** "from the queue reports of these grids: ERCOT, SPP, CAISO, ISO-NE". Whether ISO-NE's rows (and the datacenters) are drawn is the map audit's open ruling (`docs/reviews/map-model-audit-2026-11-26.md`, faults row 6, `wip/alt-map-1`), the same tables on this tab; not repeated.

## 11. Two sentences of /shoulder (Low)

- **Where.** `site/lib/shoulder.ts`, ERCOT's panel note; `site/app/shoulder/page.tsx`, the fold's "Demand".
- **Why it is wrong.** EIA's ERCO battery series begins on 23 October 2024 (the page's own decision); the table holds an average day of battery output from November 2024, and the note said "battery output, from January 2019". The fold named two of the three impossible-hour tests.
- **The test.** `tests/test_audit_small_11.py`. **The fix, words only.** "EIA-930 hourly demand, solar and wind from January 2019, and battery output from November 2024 (EIA's series of it begins on 23 October 2024)"; "(zero, more than a quarter away from the four hours around it, or outside one third to three times the grid's median hour)".

## 12. "The four weeks before" (Low)

- **Where.** `site/app/attention/AttentionView.tsx` (the note and two column heads), `site/lib/attention.ts` (`risingSource`), `docs/methods/attention.md`.
- **Why it is wrong.** Since session 7001 the builder takes the classified weeks among the four before; the weeks of 12, 19 and 26 October are set against 1, 2 and 3 weeks. The default week, 2 November, has all four, so the default view is right.
- **The test.** `tests/test_audit_small_12.py`. **The fix, words only.** "against its mean over the classified weeks among the four before (a classified week without a row counts as zero; a week the classifier has not reached does not count, so an early week is set against fewer than four)"; the heads read "Mean before %"; the hover and the note likewise.

## 13. The unsubscribe form draws any address text (Low, for ruling)

- **Where.** `site/app/subscribe/page.tsx`, `confirm`.
- **Why it matters.** The page checks the token's form (64 hex digits) and not the address's, so a crafted link puts any text, of any length, in bold on the ERW's page ("Stop every ERW email to <text>?"). React escapes it; nothing runs. The routes behind it check the address.
- **The test.** `tests/test_audit_small_13.py` (test only). **For Samuel's ruling.** Draw the form only for an address of the routes' form, 254 characters at most. Default "left as it is". The effect: no real link changes (a sent email's address is well formed); a crafted one shows no form.

## 14. Two stories in the note (Very low, for ruling)

- **Where.** `warehouse/derived/attention_index.py`, the note "N of the M stories held are classified".
- **Why it matters.** `M` is counted before the builder leaves out the stories dated more than a day after they were read (session 7003), which no week holds: 27,419 against the weeks' 27,417.
- **The test.** `tests/test_audit_small_14.py` (test only). **For Samuel's ruling.** Count after. Default "left as it is". The effect: 27,419 becomes 27,417; the percent stays 29.6.

## The words branches drawn and read

The eleven words branches merge onto origin/main (`39250e5d5`) as `wip/audit-small-words` (`0f3979b6b`), three conflicts resolved by hand (branches 2 and 5 on the Sunday line, 1 and 7 on "What is stored", 5 and 8 on the Roundup's line in `/about`). `draw.mjs` drew `/about`, `/subscribe`, `/shoulder`, the `/attention` view and the resource view on the merge, and `draw2.mjs` rendered the two changed notes: every new sentence was found (`draw_words.out`, `draw2_words.out`), no em dash in any drawing. `nofig.py` set every number of the five pages against main's drawing of the same rows: 15 numbers differ in count, each one a date, an hour or a count in the new words (12 October, 4.5, 96, 3 PM, 23:00, the "5" of "top 5" gone, 2019, 2024, 19 November); no figure of a page moved (`nofig.out`).

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-small-1` | `/subscribe`, What is stored | pass |
| `wip/audit-small-2` | `/subscribe`, What the email is | pass |
| `wip/audit-small-3` | `/about`, Scoring | pass |
| `wip/audit-small-5` | `/about`, Schedule; `/subscribe`, Sundays | pass |
| `wip/audit-small-6` | `/subscribe`, Double opt-in | pass |
| `wip/audit-small-7` | `/subscribe`, Privacy | pass |
| `wip/audit-small-8` | `/about`, Schedule | pass |
| `wip/audit-small-9` | `/resources`, decisions; the method document (rendered) | pass |
| `wip/audit-small-10` | `/resources`, the method note | pass |
| `wip/audit-small-11` | `/shoulder`, the panel and the fold | pass |
| `wip/audit-small-12` | `/attention`, What rose; the method note (rendered) | pass |

- Tests on the merge: the eleven words tests with every test file that reads a changed file (44 files, `testlist.txt`): 655 passed, 33 skipped, 1 failed, `test_session1880`'s node test of the attention view (8 of its 44 checks expect the file of 6 November), which fails the same way on clean origin/main (`tests_main_1880.out`). No new test runs node, so none needs the guard.

## Not covered, or left open

- **The live figures**: restated and drawn on the main copy's tables, older than the live set's.
- **`/shoulder`'s California series**, not restated from CAISO's or EIA's source here.
- **The resource layers other than the default** (the replication of the plays layer is session 8603's, `replication/resources/`).
- **The pages in a browser**: drawn to HTML with the site's own code; no canvas, no layout.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-small-words` (`0f3979b6b`): `-1` `9696b1783`, `-2` `b48778ff5`, `-3` `43992c658`, `-5` `420770019`, `-6` `495120029`, `-7` `a2352b08a`, `-8` `ec48c699e`, `-9` `2d37d45b2`, `-10` `e24758f97`, `-11` `628ab2117`, `-12` `65ab20199`; each drawn and read (pass); no figure moved.
- **For Samuel's ruling, default "left as it is":**
  - Finding 4, `wip/audit-small-4` (`4464dd488`), not for landing: the confirmation link opens a page that asks, a POST confirms; no confirmation by a scanner's GET (past cases not measurable here).
  - Finding 7, no branch: where a reader asks for an address to be removed.
  - Finding 13, `wip/audit-small-13` (`4e2d847a7`), not for landing: the unsubscribe form drawn only for a well-formed address; no real link changes.
  - Finding 14, `wip/audit-small-14` (`aa5f77be1`), not for landing: `/attention`'s note counts 27,417 stories held, not 27,419.
- **Data requests:** none.
- **Needs the key:** nothing.
