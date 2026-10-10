#!/usr/bin/env python3
"""Make this machine's cost ledger whole again (session 176, found on 10 October 2026).

Energy Research Warehouse (ERW). The cost ledger (warehouse/output/api_cost_ledger.csv, docs/methods/api_cost_ledger.md)
is written on two machines: GitHub's runner (the daily run and the Roundup) and the data machine (sessions). Since
session 166 loaded the live set from the data machine on 9 October 2026, the copies have parted:

    the runner's copy     restored each day from the Redivis draft, plus the day's calls (2,457 rows on 10 October)
    Supabase's copy       what the data machine loaded on 9 October (3,179 rows)
    the archive bucket    every row either machine archived (the union so far)
    the data machine      its own rows, without the daily run's rows since 5 October

So the daily run's load step refuses the ledger every day ("refused, older than the live copy: it has 2,457 rows here
and 3,179 in Supabase"), /internal/costs stops at 8 October, and the same-day email reports a failed step each day.

This script adds to the data machine's ledger the rows the archive holds and this machine lacks, with the ledger's own
writer (keyed by event_id: a second run adds nothing; no row is ever removed or changed). It makes no model call.

    python warehouse/archive/restore.py api_cost_ledger --from-bucket --out runs/ledger_union/from_bucket.csv
    python scripts/ledger_union.py runs/ledger_union/from_bucket.csv            # reports only; writes nothing
    python warehouse/lock.py run --task "ledger union" -- <the venv's python> scripts/ledger_union.py runs/ledger_union/from_bucket.csv --write

Then, each its own command under the data lock, as .github/workflows/roundup.yml does for the ledger:

    python warehouse/metadata/build_coverage.py --only '^api_cost_ledger$'
    python warehouse/archive/archive.py write --tables '^api_cost_ledger$'
    python warehouse/supabase/load.py --only '^api_cost_ledger$' --no-vacuum
    python warehouse/redivis/upload.py api_cost_ledger          # the draft only; the runner restores from it the next day

Exit 0: done or nothing to add. Exit 1: the archive's file could not be read, or it lacks rows this machine holds in a
way the union cannot explain. Exit 2: bad input.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for p in ("warehouse/connectors", "warehouse"):
    sys.path.insert(0, os.path.join(ROOT, p))


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or not os.path.exists(args[0]):
        print("ledger_union: give the ledger rebuilt from the archive (restore.py api_cost_ledger --from-bucket --out <file>)")
        return 2
    import pandas as pd
    import iso_prices as ip
    import llm
    theirs = ip.read_series(args[0], llm.COLS)
    mine = llm.read_ledger()
    new = theirs[~theirs["event_id"].isin(set(mine["event_id"]))]
    only_here = mine[~mine["event_id"].isin(set(theirs["event_id"]))]
    usd = lambda d: float(pd.to_numeric(d["usd"], errors="coerce").fillna(0).sum())  # noqa: E731
    print(f"this machine's ledger: {len(mine)} rows, USD {usd(mine):.2f}, newest {mine['ts_utc'].max() if len(mine) else 'none'}")
    print(f"the archive's ledger:  {len(theirs)} rows, USD {usd(theirs):.2f}, newest {theirs['ts_utc'].max() if len(theirs) else 'none'}")
    print(f"rows the archive holds and this machine lacks: {len(new)}, USD {usd(new):.2f}")
    if len(new):
        by = new.assign(day=new["ts_utc"].str.slice(0, 10)).groupby(["day", "session"]).size()
        for (day, session), n in by.items():
            print(f"  {day} session {session}: {n} rows")
    print(f"rows this machine holds and the archive lacks: {len(only_here)}, USD {usd(only_here):.2f} "
          "(they reach the archive with the archive write after this)")
    print(f"the union: {len(mine) + len(new)} rows, USD {usd(mine) + usd(new):.2f}")
    if "--write" not in argv:
        print("reported only; nothing written (pass --write, under the data lock, to add the rows)")
        return 0
    if not len(new):
        print("nothing to add")
        return 0
    ip.write_csv(new[llm.COLS], llm.NAME, llm.header_lines(os.environ.get("ERW_RUN_ID", "") or llm._START), print,
                 cols=llm.COLS, key=["event_id"], time_col="event_date")
    after = llm.read_ledger()
    print(f"this machine's ledger after: {len(after)} rows, USD {usd(after):.2f}")
    return 0 if len(after) == len(mine) + len(new) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
