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
- **Status** is one of `proposed` (filed, pending), `approved` (approved by the commission or board, not yet in effect or with no sheet yet) or `in effect`, with the date the document states and its cite.
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

## What is not done

- No value is read from a news article, a law firm's summary or a trade press piece; these are leads only.
- Business days are not turned into calendar days; ranges stay ranges; nothing is summed.
- No figure a chart or a picture shows is read; only the document's text.
