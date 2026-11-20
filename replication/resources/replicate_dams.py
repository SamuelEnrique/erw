"""Replication of a third layer of the natural resource map (/map?tab=resources): hydropower at non-powered dams.

Energy Research Warehouse (ERW). Session 8621 (chain 504), 19 November 2026.

What it does. The layer `hydropower_npd` of the map is Oak Ridge National Laboratory's own table of non-powered dams
with the capacity and generation each could carry (HydroSource). The layer keeps every row. This script reads the
table as the laboratory publishes it and compares every figure the map holds for the layer: the count of dams; each
dam's place (the source's longitude and latitude to four decimals), name, capacity in MW (the figure the hover shows),
and the nine columns kept beside it; the smallest, mean and largest capacity. Then, as a cross-check of the annual
generation the hover lists, it sets each dam's annual figure beside the sum of the publisher's twelve monthly
figures, which the web file leaves out.

It is written from the layer's method note (docs/methods/resources.md, "Hydropower potential at non-powered dams")
and the publisher's file alone, not from the code that built the layer, with Python's standard library alone.

The publisher's file. https://hydrosource.s3.us-east-2.amazonaws.com/files/data/datasets/hydropower-capacity-us-npd/TechPotentialNPDs.csv
(1,594,027 bytes, sha256 84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f on 7 October and on
19 November 2026). The laboratory's terms: "Data hosted on HydroSource is openly shared, without restriction, in
accordance with Department of Energy's Public Access Plan" (https://hydrosource.ornl.gov/data-use-policy/). The
site's robots file allows the read and asks ten seconds between requests; the file's own host, a storage bucket, has
no robots file (read 19 November 2026).

    python replication/resources/replicate_dams.py --csv path/to/TechPotentialNPDs.csv

Exit 0 when every figure is reproduced, 1 when one differs, 2 when the publisher's file is not the one named above.
It writes hydropower_npd_figures_differ.csv (only the figures that differ, with a first line saying how many were
compared: the figures number tens of thousands) and crosscheck_dams.csv beside itself.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LAYER = os.path.join(ROOT, "site", "data", "resources", "layers", "hydropower_npd.json")
MANIFEST = os.path.join(ROOT, "site", "data", "resources", "manifest.json")
SHA256 = "84635b4faecc332c31ab53fbbd7c42be7469d75bb2c1ca3c6827d2ac296aaf2f"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# the web file's column, and the publisher's column it is
COLUMNS = {"lon": "long", "lat": "lat", "name": "dam_name", "value": "cap_mw"}
PLACE_DECIMALS = 4


def number(text):
    """A cell of the publisher's table as a number, or None when it is blank or not a number."""
    t = (text or "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def same(ours, theirs):
    """The web file's value against the publisher's cell: numbers to nine figures, text as written, blank as none."""
    if isinstance(ours, bool):
        return False
    if isinstance(ours, (int, float)):
        t = number(theirs) if isinstance(theirs, str) else theirs
        return t is not None and abs(ours - t) <= 1e-9 * max(1.0, abs(ours), abs(t))
    if ours is None or ours == "":
        return theirs is None or str(theirs).strip() == ""
    return str(ours) == str(theirs if theirs is not None else "").strip()


def compare(source_rows, layer, entry):
    """Every figure of the layer beside the publisher's. Returns (compared, differing rows, cross-check rows)."""
    columns, rows = layer["columns"], layer["rows"]
    at = {c: i for i, c in enumerate(columns)}
    by_id = {r["nididfull"]: r for r in source_rows}
    assert len(by_id) == len(source_rows), "the publisher's dam ids are not one a dam"
    differ, n = [], 0

    def figure(what, ours, theirs, ok=None):
        nonlocal n
        n += 1
        if not (same(ours, theirs) if ok is None else ok):
            differ.append({"figure": what, "the_map": ours, "the_publisher": theirs})

    figure("dams, count", len(rows), len(source_rows), ok=len(rows) == len(source_rows))
    seen = set()
    for r in rows:
        key = r[at["nididfull"]]
        s = by_id.get(key)
        if s is None:
            figure("%s: a dam of the publisher's file" % key, r[at["name"]], None, ok=False)
            continue
        seen.add(key)
        for c in columns:
            ours, theirs = r[at[c]], s.get(COLUMNS.get(c, c))
            if c in ("lon", "lat"):
                t = number(theirs)
                figure("%s: %s (the source's %s, to %d decimals)" % (key, c, COLUMNS[c], PLACE_DECIMALS), ours, theirs, ok=t is not None and abs(ours - t) <= 0.5 * 10 ** -PLACE_DECIMALS + 1e-12)
            else:
                figure("%s: %s%s" % (key, c, " (the source's %s)" % COLUMNS[c] if c in COLUMNS else ""), ours, theirs)
    for key in sorted(set(by_id) - seen):
        figure("%s: a dam of the map's layer" % key, None, by_id[key]["dam_name"], ok=False)
    caps = [number(s["cap_mw"]) for s in source_rows]
    caps = [c for c in caps if c is not None]
    for name, ours, theirs in (("smallest capacity, MW", entry["stats"]["min"], min(caps)), ("mean capacity, MW", entry["stats"]["mean"], sum(caps) / len(caps)),
                               ("largest capacity, MW", entry["stats"]["max"], max(caps)), ("dams, the list of layers' count", entry["stats"]["n"], len(caps)),
                               ("the unit of the list of layers", entry.get("unit"), "MW")):
        figure(name, ours, theirs)

    check = []
    for s in source_rows:
        year = number(s.get("gen_mwh_yr"))
        months = [number(s.get("gen_mwh_" + m)) for m in MONTHS]
        if year is None or any(m is None for m in months):
            check.append({"dam": s["nididfull"], "name": s["dam_name"], "gen_mwh_yr": s.get("gen_mwh_yr", ""), "sum_of_its_twelve_months": "", "difference_mwh": "", "difference_pct": "", "note": "a month or the year is blank"})
            continue
        total = sum(months)
        check.append({"dam": s["nididfull"], "name": s["dam_name"], "gen_mwh_yr": round(year, 3), "sum_of_its_twelve_months": round(total, 3), "difference_mwh": round(total - year, 3),
                      "difference_pct": round(100 * (total - year) / year, 4) if year else "", "note": ""})
    check.sort(key=lambda c: -abs(c["difference_mwh"]) if c["difference_mwh"] != "" else 1)
    return n, differ, check


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="the publisher's file, TechPotentialNPDs.csv")
    ap.add_argument("--no-write", action="store_true", help="compare and print; write neither csv")
    args = ap.parse_args(argv)
    with open(args.csv, "rb") as f:
        blob = f.read()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256:
        print("the file is not the one the layer was built from: sha256 %s, wanted %s" % (digest, SHA256))
        return 2
    source_rows = list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline="")))
    with open(LAYER, encoding="utf-8") as f:
        layer = json.load(f)
    with open(MANIFEST, encoding="utf-8") as f:
        entry = [l for l in json.load(f)["layers"] if l["id"] == "hydropower_npd"][0]
    n, differ, check = compare(source_rows, layer, entry)
    if not args.no_write:
        with open(os.path.join(HERE, "hydropower_npd_figures_differ.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("# %d figures of the layer compared with the publisher's file (sha256 %s); the rows below are those that differ\n" % (n, digest))
            w = csv.DictWriter(f, fieldnames=["figure", "the_map", "the_publisher"], lineterminator="\n")
            w.writeheader()
            w.writerows(differ)
        with open(os.path.join(HERE, "crosscheck_dams.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(check[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(check)

    print("the publisher's file: %d bytes, sha256 %s (the one the layer names)" % (len(blob), digest))
    print("%d of %d figures of the layer are the publisher's%s" % (n - len(differ), n, "" if not differ else "; %d differ" % len(differ)))
    for r in differ[:12]:
        print("   DIFFERS  %s: the map %r, the publisher %r" % (r["figure"], r["the_map"], r["the_publisher"]))
    # cross-check 1, against a figure the laboratory states in words: the readme's "A total of nearly 4 GW capacity is
    # estimated across all 2,616 NPDs included in the dataset"
    total_mw = sum(c for c in (number(s["cap_mw"]) for s in source_rows) if c is not None)
    print("cross-check 1: the %d dams' capacities sum to %s MW; the laboratory's readme says \"nearly 4 GW\" across 2,616 dams" % (len(source_rows), format(round(total_mw, 1), ",")))
    # cross-check 2: the annual generation beside the twelve monthly figures. The readme calls each an average over
    # 1980 to 2015 of its own ("averaged for each month of the year", and "average annual generation"); they are two
    # summaries of the same daily series and are not built to sum, so this measures how far apart they stand
    held = [c for c in check if c["difference_mwh"] != ""]
    year, months = sum(c["gen_mwh_yr"] for c in held), sum(c["sum_of_its_twelve_months"] for c in held)
    pct = [c["difference_pct"] for c in held if c["difference_pct"] != ""]
    one, five = sum(1 for p in pct if abs(p) <= 1), sum(1 for p in pct if abs(p) <= 5)
    print("cross-check 2: for %d of %d dams the annual generation and the twelve months are both held; the annual figures sum to %s MWh and the months to %s MWh (%+.2f percent); dam by dam the two are within 1 percent for %d and within 5 percent for %d of %d"
          % (len(held), len(check), format(round(year), ","), format(round(months), ","), 100 * (months - year) / year if year else 0.0, one, five, len(pct)))
    for c in check[:5]:
        if c["difference_mwh"] != "":
            print("   %-9s %-34s annual %14s  months %14s  %+.3f MWh" % (c["dam"], c["name"][:34], format(c["gen_mwh_yr"], ",.3f"), format(c["sum_of_its_twelve_months"], ",.3f"), c["difference_mwh"]))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
