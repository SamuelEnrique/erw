# The Digest's figures and a source's revision: a proposal

Session 1061 (chain 072, `queue/done/072-day-23-october-code-allgrids-packages-2.md`), 23 October 2026. A proposal only: nothing here is wired, no past issue is rewritten, and the change it describes is the owner's to approve and the data machine's to make on its side.

## The fault

The Energy Digest of 21 October 2026 (`docs/digest/2026-10-21.md`, line 92) prints:

> WTI Cushing crude: 101.91 USD/bbl on 2026-10-14 [5]

`eia_fuel_spot_prices` now reads 96.34 for `eia:wti_cushing` on 2026-10-14. EIA revised its spot series after the issue was written. The issue was right when it was written, and the table is right now.

`site/scripts/check-values.mjs` reads the Digest's figures (`site/lib/digest.ts`, key `digest_fuel|eia_fuel_spot_prices|eia:wti_cushing|2026-10-14`) and compares each with the live set's row today. It cannot tell a revision from a wrong figure, so it fails the 21 October issue on production and on every build since. That issue stays among the pages it reads until 33 days after its date (`check-values.mjs` line 187), so until 23 November. Every gate of chains 062 to 072 has had to read this failure by hand (siting open items line 33).

The same can happen to every figure a Digest prints: the fuel closes (EIA revises them), a real-time price (an ISO's preliminary to final interval, `miso:rt_lmp_prelim` to `rt_lmp_final`), and a day-ahead mean if an ISO republishes a day. `scripts/check_digest.py`, which traces Digests too old for the live set, has the same blind spot (`check_figure`, `digest_fuel`: `ok` or `FAIL`).

## What the check needs to know

For each figure, two facts: the value the issue printed, and whether the table held that value when the issue was written. If it did, a later difference is the source's revision, not the Digest's error. The check then passes the figure with a note ("revised by the source since the issue: 101.91 then, 96.34 now, retrieved ...") and the page's own figure is never changed.

## Two ways to know it

**A. The issue keeps its own record (recommended).** When `warehouse/news/brief.py` writes an issue, it also writes `docs/digest/figures/<date>.json`: one line a figure, with the check key, the value as printed, the table, the row's key (`entity`, `variable`, `ts_utc`) and the row's `retrieved_at` as the warehouse held it. `check-values.mjs` and `check_digest.py` read it: when today's row differs from the printed figure and the record's value equals the printed figure, the figure passes as "revised by the source", with both values and both retrieval times in the check's line. A printed figure that differs from its own record is still a FAIL (the issue was wrong when written).

- What it changes: `warehouse/news/brief.py` (writes the record; about 30 lines, beside the chart record `docs/digest/charts/<date>.json` it already writes), `site/scripts/check-values.mjs` and `scripts/check_digest.py` (read it; about 20 lines each), a test of each.
- Who makes it: `brief.py` is the data machine's (`warehouse/news/`); the two checks are the code machine's. The data machine's part comes first; until a record exists for an issue, the check behaves as now.
- What it does not do: issues written before the change have no record. The 21 October issue would still fail until 23 November, unless its record is written once by hand from the archive (below) and said so.

**B. The check asks the archive.** `warehouse/archive/` keeps every version of every row (`README.md`: "the rows a run found new or changed", never rewritten), and `restore.py TABLE --as-of <time> --from-bucket` rebuilds a table as it stood. The check could restore `eia_fuel_spot_prices` as of the issue's writing time and compare. No new file is written by the news step.

- What it costs: the bucket is private (the service key), so the check could not run on GitHub's code-branch workflow or on a code machine without that key, and every gate would download a month's archive of the table. Session 1061 did not read the bucket (its requests: none), so whether the archive holds 101.91 for that row is not confirmed here.
- Use: once, by hand, to write the record of the 21 October issue under A, if the owner wants that issue to pass before 23 November.

## What the page says

Nothing changes on `/digest/2026-10-21`: a past issue is never rewritten (the chain's rule). Whether the page should add a line under a revised figure ("EIA has since revised this close to 96.34") is a separate question for the owner. Under A the record holds what such a line would need.

## For Samuel's ruling

- Whether to adopt A (a figure record a Digest issue), B, or neither (the failure is read by hand until 23 November, as now).
- Whether a revised figure on a past issue gets a visible line, or stays as printed with the revision known only to the check.
