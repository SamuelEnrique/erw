#!/usr/bin/env python3
"""ERW, What a battery earns (/cost-of-power/battery): the replication a reader can run (session 1487, chain 158).

It reads only the page's public download (the default case's hourly dispatch, erw_2026_battery_dispatch.csv, linked from
the page and served at /battery/erw_2026_battery_dispatch.csv) and this folder's assumptions.json (the page's defaults),
recomputes the page's headline figures with the page's published Python mirror (erw_2026_battery_replication.py, the
do-file's steps line for line), and prints each beside the figure the page shows for the same months (page_figures.json),
with the difference and whether it is inside the tolerance (half of the page's last shown digit).

    python replication/battery/replicate.py [path or URL of the dispatch CSV]

Exit 0 when every figure is inside its tolerance, 1 when one is not, 2 when the inputs cannot be read. Standard
library only (pandas is not needed for this file). Method: docs/methods/battery_earns_algorithm.md, section 7.
"""
import importlib.util
import json
import os
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PUBLIC = os.path.join(ROOT, "site", "public", "battery")
MIRROR = os.path.join(PUBLIC, "erw_2026_battery_replication.py")
CSV = os.path.join(PUBLIC, "erw_2026_battery_dispatch.csv")
SITE_URL = "https://erw-flame.vercel.app/battery/erw_2026_battery_dispatch.csv"
# the mirror's module constants and the assumptions that set them
CONSTANTS = {"MW": "mw", "FOM_USD_KW_YEAR": "fom_usd_kw_year", "CAPEX_USD_KW": "capex_usd_kw", "DEBT_SHARE": "debt_share",
             "DEBT_RATE": "debt_rate", "DEBT_YEARS": "debt_years", "LIFE_YEARS": "life_years", "DEGRADATION": "degradation",
             "HURDLE_PCT": "hurdle_pct", "TOLL_TARGET": "toll_target"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mirror(assumptions):
    """The page's published mirror, its constants set from the assumptions."""
    spec = importlib.util.spec_from_file_location("erw_battery_mirror", MIRROR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for const, name in CONSTANTS.items():
        setattr(m, const, assumptions[name]["value"])
    return m


def fetch(src):
    """A local path as it is; a URL downloaded to a temporary file."""
    if not src.startswith(("http://", "https://")):
        return src
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    req = urllib.request.Request(src, headers={"User-Agent": "ERW replication (github.com/SamuelEnrique/erw)"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())
    return path


def compare(numbers, page):
    """[(name, key, replicated, page, difference, ok)] for every figure of page_figures.json."""
    rows = []
    for fig in page["figures"]:
        got = numbers.get(fig["field"])
        if got is None:
            rows.append((fig["name"], fig["key"], None, fig["page"], None, False))
            continue
        diff = float(got) - float(fig["page"])
        rows.append((fig["name"], fig["key"], got, fig["page"], diff, abs(diff) <= fig["tolerance"] + 1e-9))
    return rows


def main(argv):
    src = argv[1] if len(argv) > 1 else (CSV if os.path.exists(CSV) else SITE_URL)
    try:
        assumptions = load(os.path.join(HERE, "assumptions.json"))
        page = load(os.path.join(HERE, "page_figures.json"))
        m = mirror(assumptions)
        n = m.numbers(m.read(fetch(src)))
    except (OSError, ValueError, KeyError) as exc:
        print(f"the inputs could not be read: {exc}")
        return 2
    rows = compare(n, page)
    print(f"What a battery earns, the default case, from {src}")
    print(f"months {n['months'][0]['month']} to {n['months'][-1]['month']}; the last twelve {n['l12_first']} to {n['l12_last']}")
    print("figure | key | replication | the page | difference | inside the tolerance")
    for name, key, got, shown, diff, ok in rows:
        g = "not computed" if got is None else (f"{got:,.4f}" if isinstance(got, float) else f"{got:,}")
        d = "" if diff is None else f"{diff:+.4f}"
        print(f"{name} | {key} | {g} | {shown:,} | {d} | {'yes' if ok else 'NO'}")
    bad = [r for r in rows if not r[5]]
    print(f"{len(rows) - len(bad)} of {len(rows)} inside the tolerance; not replicated here: {page['not_replicated']}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
