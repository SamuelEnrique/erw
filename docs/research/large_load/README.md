# US utilities' large-load connection rules: the research pass of November 2026

Energy Research Warehouse (ERW). Started by session 5300 (portable laptop, window P4, 13 November 2026), on `wip/5300-large-load`. Research only: nothing here is warehouse data until window A (the data machine) loads it as a table under its license rules (`docs/state/data_requests_large_load.md`).

## What this is

One row a large-load rule of one US utility: a tariff schedule, a set of rules or terms for loads of roughly 20 MW and up, a settlement or a proposal. Each row gives the rule's threshold, its minimum demand or take-or-pay share, its contract term, its collateral, its exit fees, its study and connection timelines and the utility's large-load queue where one is published. Every value carries the document, the page or section and the words it is printed in.

It starts from window A's two hand-read tables and does not repeat them:
- `large_load_connection_rules` (84 rows on 13 November 2026, the Redivis draft of 11:52 UTC; the prompt's 75 was the count of an earlier draft): the steps of 12 documents, mostly grid operators' (ERCOT, PJM, SPP, CAISO, PUCT, the Pennsylvania model tariff) and two utilities' (PG&E Rule 30, Utah's S.B. 132 and R746-318 for Rocky Mountain Power). Registry: `warehouse/sources/large_load_connection_rules/`.
- `utility_large_load_tariffs` (95 rows): the figures of 30 utility schedules. Registry: `warehouse/sources/large_load_tariffs/`.

## The files

| File | What |
|---|---|
| `utilities_<date>.csv` | The dataset: one row a rule, built by `build_csv.py` from `rows/*.json` |
| `rows/<group>.json` | The rows of one utility group as the reading subagent returned them, after my checks |
| `notes/<utility>.md` | One short note a utility: what was read, what was refused, what waits |
| `fetch_doc.py` | The only reader: robots first, a paused or barred host refused, text kept with page marks |
| `verify_quotes.py` | Matches every quote in `rows/*.json` against the cached text of its document |
| `build_csv.py` | Writes the CSV from the rows |

## The rules of a value

- **A value is what the document prints.** Never estimated, summed or inferred. A field the documents read do not state is `not published`, with what was read in `searched`.
- **Every value has at least one cite:** the document's URL (the row's `source_url` unless another is named), the page (the PDF's own page order, from 1, as `fetch_doc.py` prints it) or the section, and the words, verbatim.
- **A field window A already holds, with the same value, is not repeated.** It is written `held: <registry>/<file>.yaml`. A field that differs from what window A holds is written with its value and cite, and `erw_overlap` names the file and the old value (a correction for window A to check).
- **Status** is one of `ordered` (a commission ordered the rule filed and no filing was read, window A's word), `proposed` (filed, pending), `approved` (approved by the commission or board, not yet in effect or with no sheet yet), `in effect`, `denied` (a commission rejected the proposal) or `withdrawn`, with the date the document states and its cite. A date the documents do not print is left out, never inferred.
- **A value quoted only by another party is a note, not a value** (window A's rule for its registries). Words that only an intervenor's testimony, another party's filing or a news report gives for a utility's filing go to the row's notes with their cite, and the field is `not published` with `searched` naming where the primary was sought. The utility's own filing, its tariff, its SEC filing, or the commission's order or record are primary.
- **ISO or region** is the ERW's classification of where the load would sit (an ISO, or a balancing authority outside one), not a cited value.
- **License.** A row read from a commission's copy or a filed tariff book is `public` (the owner's ruling 4 of 6 November 2026). A row whose only source is a host whose terms ask written permission, or allow personal use only, is `internal`.
- **Queue size** is taken only from a document the utility, its commission or its grid operator publishes (a filing, a report, an integrated resource plan, an investor presentation the utility posts), never from a news report alone. A news figure is a lead in `notes`.

## How a document is read

- Found with a web search; read only with `fetch_doc.py` (`C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe -I docs/research/large_load/fetch_doc.py URL --grep REGEX`).
- The script reads the host's robots file first, for its own agent, for `*` and for Anthropic's agents by name (ClaudeBot, Claude-User, Claude-Web, Claude-SearchBot, anthropic-ai), and refuses a disallowed path.
- It never asks the paused publishers (MISO; the Virginia SCC) or the hosts that bar this reader (Con Edison, Eversource, Duquesne Light).
- A bot check is recorded as `blocked` and never retried with another agent string.
- The copy read is kept under `runs/s5300/docs/` (not in git) with its retrieval time, so that every quote can be matched again with no second request.
- A host's terms of use are read where the host is a utility's own site. Terms that bar automated reading mean the document is not read; terms that allow personal use only make the row `internal`.

## The row form (`rows/<group>.json`)

```json
{
  "group": "dominion",
  "rows": [
    {
      "utility": "Virginia Electric and Power Company (Dominion Energy Virginia)",
      "state": "VA",
      "iso_region": "PJM",
      "rule_name": "Schedule GS-5 ...",
      "source_url": "https://...",
      "source_title": "the document's own title",
      "quoted_clause": {"page": "1", "section": "Applicability", "quote": "the words that make it a large-load rule"},
      "docket": {"value": "PUR-2025-00058", "cites": [{"page": "1", "quote": "..."}]},
      "status": {"value": "in effect", "date": "2026-01-01", "cites": [{"page": "1", "quote": "Effective for usage on and after January 1, 2026"}]},
      "fields": {
        "threshold_mw": {"value": "25 MW", "cites": [{"page": "1", "section": "I", "quote": "..."}]},
        "min_demand": {"value": "85 percent of contract demand (T&D); 60 percent (generation)", "cites": [{"page": "2", "quote": "..."}]},
        "contract_term": {"value": "not published", "searched": "Schedule GS-5 pp. 1-6"},
        "collateral": {"value": "held: large_load_tariffs/dominion_virginia_schedule_gs4.yaml"},
        "exit_fee": {"value": "...", "cites": [{"url": "https://another-document", "page": "12", "quote": "..."}]},
        "study_timeline": {"value": "not published", "searched": "..."},
        "connection_timeline": {"value": "not published", "searched": "..."},
        "queue_size": {"value": "...", "cites": [{"url": "...", "page": "7", "quote": "..."}]}
      },
      "license": "public",
      "license_basis": "the commission's docket copy",
      "erw_overlap": "large_load_tariffs/dominion_virginia_schedule_gs4.yaml: threshold and min_demand differ (GS-4 is the old class) ...",
      "notes": "leads, refusals, what waits"
    }
  ],
  "refused": [{"url": "...", "reason": "the script's reason"}]
}
```

The eight fields are always all present. A cite's `url` is left out when it is the row's `source_url`. `quote` is copied from the script's output exactly; an omission inside a quote is written ` ... ` and each part must still be found in the text.

## The second pass: what changed in the 90 days to 13 November 2026 (`changes/<group>.json`, `changes_<date>.csv`)

One entry a change: a filing, an order, a tariff taking effect, an amendment, a denial, a withdrawal, a suspension or a hearing set, from 15 August to 13 November 2026, for a utility of the list or a document of window A's `large_load_connection_rules`. Each entry is printed in the document it cites, as every value is. A change that alters a row of `utilities_<date>.csv` is also written into that row by the parent.

```json
{
  "group": "southeast_changes",
  "changes": [
    {
      "utility": "Duke Energy Florida, LLC", "state": "FL",
      "rule_name": "the rule as the dataset or window A names it",
      "affects": "duke-04 | large_load_tariffs/<file>.yaml | large_load_connection_rules/<file>.yaml | new",
      "change": "filed | approved | in effect | amended | denied | withdrawn | suspended | hearing set | order issued | other",
      "date": "YYYY-MM-DD (or YYYY-MM when the document gives only the month)",
      "docket": "as printed, or not published",
      "source_url": "https://...", "source_title": "the document's own title",
      "what": "one plain sentence of what changed, in the document's own terms",
      "cites": [{"page": "3", "section": "", "quote": "the words that state the change and its date"}],
      "license": "public", "license_basis": "..."
    }
  ],
  "no_change": [{"utility": "...", "searched": "what was read, with dates"}],
  "refused": [{"utility": "...", "url": "...", "reason": "..."}]
}
```

## The third pass: the states' large-load laws (`legislation/<group>.json`, `legislation_<date>.csv`)

One entry a state law or bill of the 2025 and 2026 sessions that sets terms for large loads (data centers and others of roughly 20 MW and up) or tells the utilities or the commission to set them. Each entry is read in the legislature's own text or the state code, never in a summary.

```json
{
  "group": "laws_south",
  "laws": [
    {
      "state": "TX", "bill": "S.B. 6", "session": "89th Legislature, 2025 regular",
      "title": "the bill's or act's own title",
      "status": "introduced | passed one chamber | passed | enacted | in effect | vetoed | died",
      "status_date": "YYYY-MM-DD", "effective_date": "YYYY-MM-DD or not published",
      "source_url": "the legislature's or the code's own page or PDF", "source_title": "...",
      "cites": [{"page": "1", "section": "", "quote": "the words that state the status and dates"}],
      "threshold_mw": {"value": "75 MW", "cites": [{"page": "4", "section": "Sec. 37.0561(a)", "quote": "..."}]},
      "requirements": [
        {"topic": "cost allocation | minimum term | minimum bill | collateral | exit fee | interconnection study | curtailment or backup generation | disclosure | commission rulemaking | siting or tax | other",
         "value": "what the text requires, in its own terms", "cites": [{"page": "5", "section": "...", "quote": "..."}]}
      ],
      "license": "public", "notes": "..."
    }
  ],
  "none_found": [{"state": "...", "searched": "..."}],
  "refused": [{"state": "...", "url": "...", "reason": "..."}]
}
```

`threshold_mw` is `{"value": "not published", "searched": "..."}` when the text sets no size.

## The hosts' terms (the license audit of session 5300)

Each utility host this pass met was read once for its terms, through the reader, on 13 November 2026. A row read only from a host whose terms ask written permission, or allow personal use only, is `internal` (the owner's ruling 4 of 6 November 2026). A host whose terms bar robots is not read at all: the reader now refuses it.

| Host | Terms (where read) | The clause | Effect |
|---|---|---|---|
| Entergy's sites | https://www.entergy.com/terms | the Site Terms bar any robot, spider, scraper or other automatic means of access | not read (refused) |
| dominionenergy.com | https://www.dominionenergy.com/terms-and-conditions | "use spiders, robots, data mining techniques or other automated devices or programs to catalog, download or otherwise reproduce, store or distribute content" is barred | not read (refused) |
| pplelectric.com | https://www.pplelectric.com/terms-of-use | automated means of access barred | not read (refused) |
| Exelon's sites (ComEd, PECO, BGE, Pepco, Delmarva, ACE) | https://www.exeloncorp.com/terms-and-conditions | automated access barred | not read (refused) |
| fpl.com | FPL's legal notice | bots and spiders barred | not read (refused) |
| centerpointenergy.com | https://www.centerpointenergy.com/en-us/about-us/legal/terms-of-use | "Use or attempt to use any deep-link, scraper, robot, bot, spider ... without prior express written consent" is barred; content "for your personal and non-commercial use" | refused from now; `texas-02` read before the terms were read, so `internal`, to be re-read from the PUCT's copy |
| ameren.com | Ameren's terms | bots barred | not read (refused) |
| Southern Company's sites (georgiapower.com, alabamapower.com) | https://www.southerncompany.com/terms-and-conditions.html | "You may not reproduce, republish, transmit, distribute ... any of the Contents of the Web Sites without the prior written consent of Southern Company subsidiaries" | `internal` (`southern_florida-03`) |
| pge.com | https://www.pge.com/en/privacy-center/disclosure.html | "Use of these materials in publications, other websites or presentations is prohibited without PG&E's prior written consent" | `internal` (`southwest_california-01`) |
| aps.com | https://www.aps.com/en/Utility/Regulatory-and-Legal/Terms-of-Use | "for your personal, noncommercial use"; no distribution "without written permission from APS" | `internal` (no row of this pass is read only there) |
| oncor.com | https://www.oncor.com/content/oncorwww/us/en/home/legal.html | "for personal, noncommercial, and, as applicable, educational purposes only" | `internal` (no row of this pass is read only there) |
| AEP's sites, srpnet.com, epelectric.com, IN.gov | read by the groups (each group's `refused` list and row `license_basis`) | personal use only, or no reproduction without permission | `internal` |
| nvenergy.com | https://www.nvenergy.com/about-nvenergy/privacy-legal | the page is built by script, and the reader saw no text | terms not read; NV Energy's posted copy of its PUCN application kept `public`, as a filing |

Several of window A's registry files were read from these hosts. That is data request row 8, for Samuel's ruling.

## What is not done

- No value is read from a news article, a law firm's summary or a trade press piece; these are leads only.
- Business days are not turned into calendar days; ranges stay ranges; nothing is summed.
- No figure a chart or a picture shows is read; only the document's text.
