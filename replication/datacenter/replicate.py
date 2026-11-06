#!/usr/bin/env python3
"""ERW, What a datacenter pays (/cost-of-power): the replication a reader can run (session 1491, chain 158).

It reads only the page's public downloads (the default case's hours, erw_2026_datacenter_hourly.csv, and the grid's
carbon intensity, erw_2026_datacenter_carbon.csv, beside it; linked from the page and served under /datacenter/) and this
folder's assumptions.json (the page's defaults), recomputes the page's headline figures with the page's published Python
mirror (erw_2026_datacenter_replication.py, the do-file's steps line for line), and prints each beside the figure the
page shows for the same months (page_figures.json), with the difference and whether it is inside the tolerance (half of
the page's last shown digit). A difference page_figures.json names as known is printed as such and does not fail the run.

    python replication/datacenter/replicate.py [path or URL of the hourly CSV; the carbon file is read beside it]

Exit 0 when every figure is inside its tolerance or a known difference, 1 when one is not, 2 when the inputs cannot be
read. Standard library only. Method: docs/methods/datacenter_pays_algorithm.md.
"""
import importlib.util
import json
import os
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PUBLIC = os.path.join(ROOT, "site", "public", "datacenter")
MIRROR = os.path.join(PUBLIC, "erw_2026_datacenter_replication.py")
CSV = os.path.join(PUBLIC, "erw_2026_datacenter_hourly.csv")
SITE_URL = "https://erw-flame.vercel.app/datacenter/erw_2026_datacenter_hourly.csv"
# the mirror's module constants and the assumptions that set them
CONSTANTS = {"MW": "mw", "GPU_KW": "gpu_kw", "PUE": "pue"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mirror(assumptions):
    """The page's published mirror, its constants set from the assumptions."""
    spec = importlib.util.spec_from_file_location("erw_datacenter_mirror", MIRROR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for const, name in CONSTANTS.items():
        setattr(m, const, assumptions[name]["value"])
    return m


def fetch(src):
    """A local path as it is; a URL downloaded, with the carbon file beside it, to a temporary folder."""
    if not src.startswith(("http://", "https://")):
        return src
    d = tempfile.mkdtemp()
    for name in ("erw_2026_datacenter_hourly.csv", "erw_2026_datacenter_carbon.csv"):
        url = src.rsplit("/", 1)[0] + "/" + name
        req = urllib.request.Request(url, headers={"User-Agent": "ERW replication (github.com/SamuelEnrique/erw)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(os.path.join(d, name), "wb") as f:
            f.write(r.read())
    return os.path.join(d, "erw_2026_datacenter_hourly.csv")


def numbers_of(m, path):
    """The mirror's numbers for the hourly file at path and the carbon file beside it (as the mirror's own main reads
    them), with the years the page shows by year."""
    rows = m.read(path)
    n = m.numbers(rows)
    n["rows"] = rows
    carbon = os.path.join(os.path.dirname(os.path.abspath(path)), m.CARBON_NAME)
    if os.path.exists(carbon):
        n.update(m.carbon(carbon, n))
    for y in n["years"]:
        n[f"year_{y['year']}"] = y["usd_mwh"]
    return n


def compare(numbers, page):
    """[(name, key, replicated, page, difference, ok, inside)] for every figure of page_figures.json: inside when inside
    the tolerance, ok when inside or a difference page_figures.json names as known."""
    rows = []
    known = page.get("known_differences", {})
    for fig in page["figures"]:
        got = numbers.get(fig["field"])
        if got is None:
            rows.append((fig["name"], fig["key"], None, fig["page"], None, False, False))
            continue
        diff = float(got) - float(fig["page"])
        inside = abs(diff) <= fig["tolerance"] + 1e-9
        rows.append((fig["name"], fig["key"], got, fig["page"], diff, inside or fig["field"] in known, inside))
    return rows


def main(argv):
    src = argv[1] if len(argv) > 1 else (CSV if os.path.exists(CSV) else SITE_URL)
    try:
        assumptions = load(os.path.join(HERE, "assumptions.json"))
        page = load(os.path.join(HERE, "page_figures.json"))
        m = mirror(assumptions)
        n = numbers_of(m, fetch(src))
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    rows = compare(n, page)
    print(f"What a datacenter pays, the default case, from {src}")
    print(f"months held {n['first_held']} to {n['last_held']}; the last twelve {n['l12_first']} to {n['l12_last']}")
    print("figure | key | replication | the page | difference | inside the tolerance")
    for name, key, got, shown, diff, ok, inside in rows:
        g = "not computed" if got is None else (f"{got:,.4f}" if isinstance(got, float) else f"{got:,}")
        d = "" if diff is None else f"{diff:+.4f}"
        print(f"{name} | {key} | {g} | {shown:,} | {d} | {'yes' if inside else ('no: a known difference' if ok else 'NO')}")
    bad = [r for r in rows if not r[5]]
    print(f"{sum(1 for r in rows if r[6])} of {len(rows)} inside the tolerance, {sum(1 for r in rows if r[5] and not r[6])} a known "
          f"difference ({', '.join(page.get('known_differences', {}))}); not replicated here: {page['not_replicated']}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
