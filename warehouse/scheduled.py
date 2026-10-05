#!/usr/bin/env python3
"""The builders that used to be run by hand, as steps of a schedule (session 114).

Energy Research Warehouse (ERW). Session 112's state document listed seven pages in review that read a file someone
built by hand. Each builder is now a step of the daily run (the network's replay and the two EIA-930 daily tables it
reads) or of the monthly job (warehouse/run_monthly.sh, the other six), each under warehouse/health.py:

    python warehouse/health.py run --step mix_profile -- python warehouse/scheduled.py mix_profile
    python warehouse/scheduled.py --list            # every step, what it needs and what it runs
    python warehouse/scheduled.py mix_profile --check   # say whether its inputs are here; run nothing
    python warehouse/scheduled.py --monthly-due     # exit 0 when the monthly job has not yet run this month, else 1

The monthly job is due from the third day of the month (UTC: EIA-930's lag of a day or two is past, so the month before
is whole) until it has run: the first daily run on or after the third starts it, so a daily run that did not happen on
the third does not cost the month. "Has run" is read from the built stamp of the site's copy of demand growth
(site/data/demand_growth.json), whose inputs every daily run has; the daily workflow commits that file.

What this script adds to the builder it starts:
- it looks for the builder's inputs first. A table the builder reads that is not on the machine is rebuilt from the
  ERW's own archive (warehouse/archive/restore.py --from-bucket: the private bucket erw-archive, not a publisher) when
  the step says it may be; a table that is still missing, or a workbook the day's EIA-930 pull did not save, is a SKIP
  with the reason, never a partial table. Under warehouse/health.py the skip is exit ERW_SKIP_EXIT (75) and a row of
  erw_health; by hand it is exit 0 with the same line.
- nothing else: the builder runs as it does by hand, with the same arguments, and its exit code is this script's.

No step here asks a paused publisher for anything. The only steps that make a request are the two EIA-930 daily
connectors (EIA's API; --days 5, merged into the table held), and they make none when the table is not on the machine;
and, since session 116, ercot_storage_dam (ERCOT's file list and one zip of its 60-Day DAM Disclosure, the next
operating day: a standing pull approved in that session's prompt), which makes none when its tables are not here.
"""

import argparse
import datetime as dt
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "connectors"))
import iso_prices as ip  # noqa: E402

RAW_930 = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
ISO_BAS = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]
MONTHLY_DAY = 3     # the monthly job is due from this day of the month, UTC
MONTHLY_MARK = os.path.join(ROOT, "site", "data", "demand_growth.json")  # its built stamp says whether the month's job has run
REPLAY_DAYS = "5"  # EIA's daily tables: the days asked for again each day (EIA revises a day for a few days after it)

# tables: read from warehouse/output and required. restore: those of them that may be rebuilt from the archive when
# absent (the GitHub runner holds only what the daily run restores or pulls). workbooks: the EIA-930 workbooks of
# warehouse/raw/eia930_emissions the builder reads, saved by the day's eia930_emissions step. files: other files required.
JOBS = {
    "eia930_daily_interchange": dict(
        cadence="daily", page="/network/v3", tables=["eia930_daily_interchange"], restore=["eia930_daily_interchange"],
        cmd=["warehouse/connectors/eia930_daily_interchange.py", "--days", REPLAY_DAYS]),
    "eia930_daily_demand": dict(
        cadence="daily", page="/network/v3", tables=["eia930_daily_demand"], restore=["eia930_daily_demand"],
        cmd=["warehouse/connectors/eia930_daily_demand.py", "--days", REPLAY_DAYS]),
    "network_replay": dict(
        cadence="daily", page="/network/v3",
        # the two daily tables, the day's carbon intensity, and the price tables of the six hubs the replay prices
        # (price_board.TABLES; the ERCOT price history is not required: where it is absent the file's own prices are kept)
        tables=["eia930_daily_interchange", "eia930_daily_demand", "carbon_intensity_daily", "iso_rtm_hub_prices", "iso_hub_prices_history",
                "nyiso_rtm_zone_prices", "isone_rtm_zone_prices_hourly"],
        files=["site/data/grid_network.json", "site/public/network/daily_index.json"],
        cmd=["warehouse/derived/network_daily.py", "--daily"]),
    # session 116, the standing pull (approved): one zip a day of ERCOT's 60-Day DAM Disclosure, the next operating day,
    # added to the row-level table; then the monthly awards table and the two offers tables. The four tables are rebuilt
    # from the ERW's archive when the machine lacks them (the runner); without them nothing is requested
    "ercot_storage_dam": dict(
        cadence="daily", page="/cost-of-power/battery/awards",
        tables=["ercot_dam_esr_awards", "ercot_storage_dam_awards_monthly", "ercot_storage_dam_offers_daily", "ercot_storage_dam_offers_monthly"],
        restore=["ercot_dam_esr_awards", "ercot_storage_dam_awards_monthly", "ercot_storage_dam_offers_daily", "ercot_storage_dam_offers_monthly"],
        cmd=["warehouse/connectors/ercot_dam_esr.py", "--daily"]),
    "mix_profile": dict(
        cadence="monthly", page="/mix/v2", tables=["caiso_fuel_supply", "carbon_intensity_hourly"], workbooks=ISO_BAS,
        cmd=["warehouse/derived/mix_profile.py", "--snapshot"]),
    "price_compare": dict(
        cadence="monthly", page="/prices/compare",
        # every price table the comparison reads: without one of them it would write fewer hubs than it holds
        tables=["iso_hub_prices_history", "ercot_all_hub_prices_history", "iso_dam_hub_prices", "iso_rtm_hub_prices", "isone_dam_zone_prices",
                "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly", "nyiso_dam_zone_prices", "nyiso_rtm_zone_prices", "carbon_intensity_daily"],
        cmd=["warehouse/derived/price_compare.py", "--snapshot"]),
    "demand_growth": dict(
        cadence="monthly", page="/demand", workbooks=ISO_BAS + ["US48"],
        cmd=["warehouse/derived/demand_growth.py", "--snapshot"]),
    "curtailment_profile": dict(
        cadence="monthly", page="/curtailment/v2", tables=["caiso_curtailment_intervals", "caiso_battery_storage"],
        restore=["caiso_curtailment_intervals"], cmd=["warehouse/derived/curtailment_profile.py", "--snapshot"]),
    "project_map": dict(
        cadence="monthly", page="/map/v2", tables=["eia860m_operating_generators", "eia860m_planned_generators"],
        restore=["eia860m_operating_generators", "eia860m_planned_generators"], cmd=["warehouse/derived/project_map.py"]),
    "large_load_snapshot": dict(
        cadence="monthly", page="/datacenters/v2", tables=["ercot_large_load_status"], restore=["ercot_large_load_status"],
        cmd=["warehouse/derived/large_load_snapshot.py"]),
}


def table_path(name):
    return os.path.join(ip.OUT_DIR, name + ".csv")


def workbook_held(ba):
    return any(os.path.getsize(f) > 0 for f in glob.glob(os.path.join(RAW_930, "*", f"*_{ba}.xlsx")))


def missing(job):
    """What the step needs and this machine lacks: (tables, workbooks, files)."""
    return ([t for t in job.get("tables", []) if not os.path.exists(table_path(t))],
            [b for b in job.get("workbooks", []) if not workbook_held(b)],
            [f for f in job.get("files", []) if not os.path.exists(os.path.join(ROOT, f))])


def restore(table, run=subprocess.run):
    """Rebuild one table from the ERW's archive bucket into warehouse/output. True when the file is there afterwards."""
    out = table_path(table)
    r = run([sys.executable, os.path.join(HERE, "archive", "restore.py"), table, "--from-bucket", "--out", out], cwd=ROOT)
    if r.returncode != 0 and os.path.exists(out):
        os.remove(out)  # a rebuild that did not finish is not an input
    return r.returncode == 0 and os.path.exists(out)


def skip(name, reason):
    print(f"{name} SKIPPED: {reason}")
    return int(os.environ.get("ERW_SKIP_EXIT") or 0)


def step(name, check=False, run=subprocess.run, restore=restore):
    job = JOBS[name]
    tables, books, files = missing(job)
    if not check:
        for t in [t for t in tables if t in job.get("restore", [])]:
            print(f"{name}: {t} is not on this machine; rebuilding it from the archive (erw-archive)")
            if not restore(t):
                print(f"{name}: {t} could not be rebuilt from the archive")
        tables, books, files = missing(job)
    lacking = ([f"the table {t}" for t in tables] + [f"EIA-930's {b} workbook (warehouse/raw/eia930_emissions)" for b in books]
               + [f"the file {f}" for f in files])
    if lacking:
        return skip(name, f"{'; '.join(lacking)} {'is' if len(lacking) == 1 else 'are'} not on this machine, so nothing was built and "
                          "the page keeps the copy it has")
    if check:
        print(f"{name}: every input is here; it would run {' '.join(job['cmd'])}")
        return 0
    return run([sys.executable, os.path.join(ROOT, job["cmd"][0])] + job["cmd"][1:], cwd=ROOT).returncode


def monthly_due(today=None, mark=None):
    """(due, why): whether the monthly job should run with today's daily run."""
    today = today or dt.datetime.now(dt.timezone.utc).date()
    start = today.replace(day=MONTHLY_DAY)
    if today < start:
        return False, f"the monthly builds run from day {MONTHLY_DAY} of the month (UTC); today is {today}"
    try:
        with open(mark or MONTHLY_MARK, encoding="utf-8") as f:
            built = json.load(f)["built"][:10]
    except (OSError, ValueError, KeyError, TypeError):
        return True, "the site's copy of demand growth carries no built stamp: the monthly builds are due"
    if built >= start.isoformat():
        return False, f"the monthly builds of {today:%Y-%m} have run (the site's copy of demand growth was built {built})"
    return True, f"the monthly builds of {today:%Y-%m} are due (the site's copy of demand growth was built {built}, before {start})"


def main(argv=None):
    ap = argparse.ArgumentParser(description="A builder that used to be run by hand, as a step of a schedule (session 114)")
    ap.add_argument("name", nargs="?", choices=sorted(JOBS))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true", help="say whether the inputs are here; run and rebuild nothing")
    ap.add_argument("--monthly-due", action="store_true", help="exit 0 when the monthly job is due with today's daily run, 1 when not")
    a = ap.parse_args(argv)
    if a.monthly_due:
        due, why = monthly_due()
        print(f"monthly builds: {why}")
        return 0 if due else 1
    if a.list or not a.name:
        for name, j in JOBS.items():
            print(f"{name} ({j['cadence']}, {j['page']}): {' '.join(j['cmd'])}; tables {j.get('tables', [])}; "
                  f"workbooks {j.get('workbooks', [])}; from the archive when absent {j.get('restore', [])}")
        return 0
    return step(a.name, a.check)


if __name__ == "__main__":
    sys.exit(main())
