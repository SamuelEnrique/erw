"""Session 11405 (chain 770, wip/ready-held-out, decision 1 of docs/reviews/weekend-2026-11-28.md; not landed until
Samuel rules): no held grid's figure is left in the analysis builders' public files. Carries over the test of
wip/audit-analysis-2 (tests/test_audit_analysis_2.py, Automated Analysis audit finding 2), which showed these on main,
as the new behaviour.

Held: the grids held for a license (warehouse/metadata/license_status.csv: NYISO, ISO-NE, MISO; MISO paused too, not
licensed) and, for the weekly lines, the owner's hold of 12 October 2026 (findings/daily_chart.HELD: NYISO, SPP).

PLACES counts, from the repository's files only, the held values left in each place. Measured on origin/main
(ae43cdc96, 28 November 2026) and on this branch:
  gallery MISO          96: 48 chart files of iso=miso and 48 index combos naming them   -> 0
  network MISO          977 daily hub prices of MISO in four site/public/network files   -> 0
  board MISO            0 hourly files site/public/board/h/miso-*                        -> 0
  impact download       56 days of NYISO New York City as the default card's control    -> 0
  weekly results        36: 24 mentions of watch_nyiso_reg and watch_spp_regup in four weeks' results and charts
                        of the week, 8 rows of history.csv, 2 entries of templates.json, 2 of tables.json's read_by -> 0
  spikes card file      132 rows of NYISO and ISO-NE in erw_2026_grids_spikes_batteries.csv -> 0
  gas share card file   16 rows in erw_2026_gas_share_hours.csv                         -> 0
  peak hour card file   384 rows in erw_2026_grids_peak_hour_solar.csv (found, not on the page's line: the same
                        kind of card, built on NYISO's and ISO-NE's real-time prices)    -> 0
  cards                 255 figures of a held grid in site/data/findings/*.json (four cards): 196 numbers, 10
                        callout sides, 4 chart panels, 45 sentences naming a held grid with a figure       -> 0

The cards' rendered pictures (site/public/findings/*_1080x1350.png and _1600x900.png, docs/analysis/findings/) still
draw the old figures: they are drawn by site/scripts/render-cards.mjs in a browser, at landing by the desk.

No table, no request, no model call; the environment is read, never set."""
import csv
import glob
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELD = {"nyiso", "isone", "miso"}
HELD_WATCH = {"watch_nyiso_reg", "watch_spp_regup"}
WORDS = re.compile(r"\b(NYISO|ISO-NE|New York|New England|MISO)\b")


def _read(root, *p):
    with open(os.path.join(root, *p), encoding="utf-8") as f:
        return f.read()


def gallery_miso(root=ROOT):
    gal = os.path.join(root, "docs", "analysis", "gallery")
    files = glob.glob(os.path.join(gal, "*", "*iso=miso_*.json"))
    idx = json.loads(_read(root, "docs", "analysis", "gallery", "index.json"))
    named = sum(1 for t in idx["templates"] for c in t["combos"].values()
                if str(c.get("params", {}).get("iso", "")).lower() == "miso" and c.get("file"))
    return len(files) + named


def network_miso(root=ROOT):
    n = 0
    for f in glob.glob(os.path.join(root, "site", "public", "network", "*.json")):
        d = json.loads(_read(root, f))
        if isinstance(d, dict) and isinstance(d.get("hub_prices"), dict):
            n += sum(v is not None for v in d["hub_prices"].get("MISO", []))
    return n


def board_miso(root=ROOT):
    return len(glob.glob(os.path.join(root, "site", "public", "board", "h", "miso-*.json")))


def impact_download(root=ROOT):
    t = _read(root, "site", "public", "findings", "erw_2026_impact_event_control.csv")
    head = [ln for ln in t.splitlines() if ln.startswith("#")]
    body = [ln for ln in t.splitlines() if ln and not ln.startswith("#")]
    if not body or not any("control:" in ln and WORDS.search(ln.split("control:", 1)[1]) for ln in head):
        return 0
    rows = list(csv.DictReader(body))
    return sum(1 for r in rows if r.get("control_value") not in (None, "", "nan"))


def weekly_results(root=ROOT):
    n = 0
    for p in glob.glob(os.path.join(root, "docs", "analysis", "2026-W*", "*.json")):
        t = _read(root, p)
        n += sum(t.count(f'"{h}"') for h in HELD_WATCH)
    for line in _read(root, "docs", "analysis", "history.csv").splitlines():
        if line.split(",", 2)[1:2] and line.split(",", 2)[1] in HELD_WATCH:
            n += 1
    tpl = json.loads(_read(root, "docs", "analysis", "templates.json"))
    tpl = tpl["templates"] if isinstance(tpl, dict) else tpl
    n += sum(1 for t in tpl if t.get("template") in HELD_WATCH)
    tab = json.loads(_read(root, "docs", "analysis", "tables.json"))
    tab = tab["tables"] if isinstance(tab, dict) else tab
    n += sum(1 for t in tab for r in t.get("read_by", []) if r in HELD_WATCH)
    return n


def _held_rows(name, root):
    t = _read(root, "site", "public", "findings", name)
    body = [ln for ln in t.splitlines() if ln and not ln.startswith("#")]
    return sum(1 for r in csv.DictReader(body) if str(r.get("grid", "")).lower() in HELD)


def spikes_card_file(root=ROOT):
    return _held_rows("erw_2026_grids_spikes_batteries.csv", root)


def gas_share_card_file(root=ROOT):
    return _held_rows("erw_2026_gas_share_hours.csv", root)


def peak_hour_card_file(root=ROOT):
    return _held_rows("erw_2026_grids_peak_hour_solar.csv", root)


def _strings(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v)
    elif isinstance(x, str):
        yield x


def _panels(x):
    if isinstance(x, dict):
        if str(x.get("grid", "")).lower() in HELD and ("values" in x or "series" in x or "x" in x or "rows" in x):
            yield x
        for v in x.values():
            yield from _panels(v)
    elif isinstance(x, list):
        for v in x:
            yield from _panels(v)


def cards(root=ROOT):
    n = 0
    for p in glob.glob(os.path.join(root, "site", "data", "findings", "*.json")):
        if os.path.basename(p) == "catalogue.json":
            continue   # the inputs a person picks from: names, never a figure
        c = json.loads(_read(root, p))
        if not isinstance(c, dict):
            continue
        n += sum(1 for k, v in (c.get("numbers") or {}).items() if k.split("_", 1)[0] in HELD and v is not None)
        for co in c.get("callouts") or []:
            for side in ("before", "after"):
                s = co.get(side) or {}
                if (WORDS.search(co.get("label", "")) or WORDS.search(str(s.get("period", "")))) and s.get("text") != "license needed":
                    n += 1
        n += sum(1 for _ in _panels(c.get("chart")))
        for s in _strings({k: v for k, v in c.items() if k not in ("meta", "params", "inputs_words", "placeholders", "grid_words", "callouts")}):
            for sent in re.split(r"(?<=[;!?])\s+|(?<=[a-z0-9)%]\.)\s+(?=[A-Z])", s):
                if re.search(r"\b(NYISO|ISO-NE|New York|New England)\b", sent) and re.search(r"\d", sent):
                    n += 1
    return n


PLACES = {
    "gallery MISO": gallery_miso,
    "network MISO": network_miso,
    "board MISO": board_miso,
    "impact download": impact_download,
    "weekly results": weekly_results,
    "spikes card file": spikes_card_file,
    "gas share card file": gas_share_card_file,
    "peak hour card file": peak_hour_card_file,
    "cards": cards,
}


class NoHeldValueLeft(unittest.TestCase):
    def test_every_place_counts_zero(self):
        left = {k: f() for k, f in PLACES.items()}
        self.assertEqual({k: v for k, v in left.items() if v}, {})

    def test_the_builders_skip_a_held_grid(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis"))
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import findings_common as fc
        import watch
        self.assertIn("miso", fc.held_grid_codes())
        self.assertFalse({s["name"] for s in watch.WATCH} & HELD_WATCH)
        self.assertEqual({s["name"] for s in watch.HELD_WATCH}, HELD_WATCH)
        self.assertIn('"MISO": "miso"', _read(ROOT, "warehouse", "analysis", "run.py"))
        self.assertIn('"MISO": "MISO"', _read(ROOT, "warehouse", "derived", "network_stories.py"))
        self.assertNotIn('grid != "MISO"', _read(ROOT, "warehouse", "derived", "page_keep.py"))
        self.assertTrue("common.withhold(card, rows, recompute=" in _read(ROOT, "warehouse", "analysis", "findings", "run_finding.py"))

    def test_impact_study_refuses_a_held_control(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import impact_study
        rows, meta = impact_study.compute({}, in_dir=os.path.join(ROOT, "no-such-folder"))
        self.assertEqual(rows, [])
        self.assertIn("license needed", meta["refusal"])

    def test_withhold_takes_out_a_held_grid(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "analysis", "findings"))
        import findings_common as fc
        card = {"title": "T", "why": "ERCOT fell 5 percent. NYISO rose 9 percent.", "footnote": "F.",
                "numbers": {"ercot_x": 1, "nyiso_x": 2}, "callouts": [{"label": "NYISO x", "before": {"period": "2019", "text": "8.8x"}, "after": {"period": "2025", "text": "9x"}}],
                "chart": {"kind": "multiples", "panels": [{"grid": "ercot", "x": [1]}, {"grid": "nyiso", "x": [1]}]}}
        rows = [{"grid": "ercot", "v": 1}, {"grid": "nyiso", "v": 2}]
        c, r = fc.withhold(card, rows, held={"nyiso"})
        self.assertEqual(r, [{"grid": "ercot", "v": 1}])
        self.assertEqual(c["why"], "ERCOT fell 5 percent.")
        self.assertNotIn("nyiso_x", c["numbers"])
        self.assertEqual(c["callouts"][0]["before"]["text"], "license needed")
        self.assertEqual([p["grid"] for p in c["chart"]["panels"]], ["ercot"])
        self.assertIn("license needed", c["footnote"])
        c2, _ = fc.withhold(c, r, held={"nyiso"})
        self.assertEqual(c2, c)   # applied twice, the same card


if __name__ == "__main__":
    unittest.main()
