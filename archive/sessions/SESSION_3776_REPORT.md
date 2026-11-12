# Session 3776 report: chain 211's Stanford draft (its session 3770): refused by the license record, nothing uploaded

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 14:04 to 14:08 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis, the uploader's own few before its refusal (under the data lock); no upload.

## Read these first

- **Nothing was uploaded to the Stanford draft (erw:b9wm), and nothing was released.**
  - `upload.py --target stanford --tables ferc714_planning_area_forecasts ferc714_forecast_growth`, run under the data lock (`lock.py run`), refused both: "the ERW verdict of ... is unsettled (docs/licenses.md, Every table), not public; never uploaded to erw:b9wm".
  - The target uploads only tables whose ERW verdict is public.
- **Why "unsettled":** every FERC-714 table names its publisher as "Catalyst Cooperative (PUDL), from FERC Form 714" (`sources.csv`, `license_tables.csv`), and `license_verdicts.csv` holds no verdict under that key.
  - Its verdict for "Catalyst Cooperative (PUDL)" (session 484: CC-BY-4.0) is "may be public", which is not "public" either.
  - Ruling 1 makes the table's license flag public. The ERW verdict, which is the publisher's own page as read, is a separate record, and only a person settles it.
  - The whole FERC-714 family (the area demand tables of 2006 to 2025, the respondents and the two forecast tables) reads "unsettled" for the same reason.
- **The tariff and rules registries stay off the draft,** as chain 211's ruling item 6 takes by default (held while their verdict is unsettled).
- **`--reconcile` was not run.** It counts every table of the draft, several hundred requests, beyond the session's cap. And the 14:00 daily run needed the data lock.
- **`docs/state/redivis_v1_ready.md` was not rewritten:** nothing changed on the draft. The two FERC-714 tables stay "held" in `docs/redivis/release-v1/tables.csv` with chain 211's reason.
- **The records:** `build_tables.py --check` passes. The tests of sessions 1001, 1008 and 1009 pass (session 3775). `build_llms.py` was run (session 3785).

## Decisions made without you

- **No verdict row was written to make the upload pass.** A publisher's verdict is the reading of its page, so it is yours or a reading session's to record, not this chain's to infer.

## For Samuel's ruling

- **FERC-714's ERW verdict.** Recommendation: record the publisher key "Catalyst Cooperative (PUDL), from FERC Form 714" with PUDL's CC-BY-4.0 verdict, and settle "may be public" as public for a government filing republished under CC-BY (attribution in the table's header). This opens all the FERC-714 tables to the Stanford draft and to v1. Default: held, not uploaded.
