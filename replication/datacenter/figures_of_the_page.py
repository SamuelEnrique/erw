#!/usr/bin/env python3
"""ERW, What a datacenter pays (/cost-of-power): the figures the page prints at its bare address, written into
page_figures.json and page_figures.csv from the page's own code on the files of the same run (session 3779, chain 212).

The figures were read by hand from a local build on 6 November 2026 (session 1491). The data machine's daily run
rewrites the page's files and the public hourly and carbon files; the page's figures move with them, and the reading
of 6 November no longer matched, so the run put every refresh back (runs/data_machine_dm_test_replication.out, 9 and
10 November). This script asks the page's own code (site/scripts/datacenter-page-figures.mjs, which runs
lib/datacenter.ts, lib/datacenter/finance.ts and lib/datacenter/answers.ts with node on site/data/datacenter/ and the
public carbon file) for the twelve figures it computes from those files, rounds each to the digits the page shows (the
figure's tolerance is half of the last one), and writes them. The two years by window are the page's reading of the
live set (price_years_by_window), not of these files, and a past year does not move: they are kept as they are.

The replication (replicate.py, the published mirror in Python) stays a second code: tests/test_session1491.py holds it
to these figures, so a difference between the mirror and the page's code still fails the test.

    python replication/datacenter/figures_of_the_page.py [--check]

--check writes nothing and exits 1 when the files differ from what would be written. Needs node and the site's
node_modules. Standard library only.
"""

import argparse
import csv
import datetime as dt
import io
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")
SCRIPT = os.path.join("scripts", "datacenter-page-figures.mjs")
JSON_PATH = os.path.join(HERE, "page_figures.json")
CSV_PATH = os.path.join(HERE, "page_figures.csv")
HOURLY = os.path.join(SITE, "public", "datacenter", "erw_2026_datacenter_hourly.csv")
KEPT = ("year_2016", "year_2021")   # the live set's years by window: not computed from the files


def page_code():
    """The page's own figures on the files as they stand (the node script's JSON)."""
    p = subprocess.run(["node", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"{SCRIPT} exited {p.returncode}: {p.stderr.strip()[-1500:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


def digits(tolerance):
    """The decimals the page shows, from the tolerance (half of the last shown digit); 0 for counts."""
    if tolerance <= 0:
        return 0
    return max(0, round(-math.log10(tolerance * 2)))


def shown(value, tolerance):
    d = digits(tolerance)
    v = round(float(value), d)
    return int(v) if d == 0 else v


def built_on():
    """The day the page's files were built, as the public hourly file's header names it (index.json (built ...))."""
    try:
        with open(HOURLY, encoding="utf-8") as f:
            for _ in range(40):
                line = f.readline()
                if not line.startswith("#"):
                    break
                m = re.search(r"index\.json \(built (20\d\d-\d\d-\d\d)T", line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def day_words(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def rebuilt(page, code):
    """page_figures.json with each computed figure set to the page's code, rounded as the page shows it."""
    out = json.loads(json.dumps(page))
    figs = code["figures"]
    missing = []
    for fig in out["figures"]:
        f = fig["field"]
        if f in KEPT:
            continue
        v = figs.get(f)
        if v is None:
            missing.append(f)
            continue
        fig["page"] = shown(v, fig["tolerance"])
        if f == "bad_usd_mwh" and figs.get("bad_month"):
            fig["name"] = re.sub(r"\(\d{4}-\d{2}\)", f"({figs['bad_month']})", fig["name"])
    if missing:
        raise RuntimeError(f"the page's code gave no figure for {', '.join(missing)}")
    a = code["address"]
    built = built_on()
    about = out["_about"]
    about = re.sub(r"the last twelve months \d{4}-\d{2} to \d{4}-\d{2}", f"the last twelve months {a['l12_first']} to {a['l12_last']}", about)
    if built:
        about = re.sub(r"(exported|the page's files built) \d{1,2} [A-Z][a-z]+ \d{4}", f"the page's files built {day_words(built)}", about)
    tail = (" Since session 3779 the figures the page computes from its files are written by figures_of_the_page.py from"
            " the page's own code (site/scripts/datacenter-page-figures.mjs) on the files of the same run; the two years by"
            " window are the live set's and kept as read.")
    if "Since session 3779" not in about:
        about += tail
    out["_about"] = about
    return out


def as_csv(page):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["field", "name", "key", "page", "tolerance"])
    for fig in page["figures"]:
        w.writerow([fig["field"], fig["name"], fig["key"], fig["page"], fig["tolerance"]])
    return buf.getvalue()


def as_json(page):
    return json.dumps(page, indent=1, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the files would change")
    args = ap.parse_args(argv)
    with open(JSON_PATH, encoding="utf-8") as f:
        page = json.load(f)
    try:
        new = rebuilt(page, page_code())
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"figures_of_the_page: {exc}")
        return 2
    want_json, want_csv = as_json(new), as_csv(new)
    with open(JSON_PATH, encoding="utf-8") as f:
        have_json = f.read()
    with open(CSV_PATH, encoding="utf-8") as f:
        have_csv = f.read()
    changed = [f["field"] for f, o in zip(new["figures"], page["figures"]) if f["page"] != o["page"] or f["name"] != o["name"]]
    if args.check:
        same = json.loads(have_json) == new and have_csv.replace("\r\n", "\n") == want_csv
        print("figures_of_the_page: " + ("the files are the page's code" if same else f"would change: {', '.join(changed) or 'the note'}"))
        return 0 if same else 1
    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(want_json)
    with open(CSV_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(want_csv)
    print(f"figures_of_the_page: written; {len(changed)} figure(s) moved: {', '.join(changed) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
