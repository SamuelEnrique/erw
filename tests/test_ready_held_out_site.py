"""Session 11405 (chain 770; the weekend page of 28 November 2026, decision 1, branch wip/ready-held-out): the held
figures still public on five pages, taken out in one batch. This file counts the held values left in each place, from
the repository's own files, and asserts every count is 0.

The places and their counts, measured on origin/main (ae43cdc96, 28 November 2026) and on this branch:
  /curtailment, ISO-NE's and NYISO's hours under USD 5 (the curtailment audit's finding 1; the test of
    wip/audit-curtailment-1 carried over): 38 before (36 counts of hours under USD 5 in free_energy.json, by place and
    window and each grid's leading place; the widest gap of the year naming NYISO, 13.09 USD/MWh; and the page printing
    the count with no license gate), 0 after.
  What a generator earns (/cost-of-power/seller), ISO-NE and NYISO offered: 43 before (19 hubs and zones in capture.json,
    2 grids in merchant_snapshot.json, 21 hub files under site/data/seller/hubs, the grid list with no license gate),
    0 after.
  The policy monitor (/policy?view=monitor), records drawn from the PUCT's or the Texas Governor's pages (the policy
    audit's finding 1; the test of wip/audit-policy-7 carried over): 38 before (11 of them shown as the view opens:
    295 to 284; 1,584 records to 1,546), 0 after.
  The map (/map), ISO-NE's queue positions: 414 before (21,901.8 MW), 0 after (counted in "held", as MISO's and NYISO's).
  The companies tab of /deals, the rows seeded from the held deals' parties: 541 before (of 562), 0 after (21 shown).

A site file that only a data-machine run rebuilds was rewritten here as its changed builder writes it (the builders:
free_energy.py, capture_price.py, merchant_revenue.py, merchant_hubs.py, monitor_site.py, project_map.py); the scripts
are runs/c770/11405/strip_*.py in the session's worktree. No table, no request, no model call; the environment is read,
never set."""
import csv
import glob
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE = {"ISO-NE": "isone", "NYISO": "nyiso"}   # MISO is paused, not this file's: the other part of the branch
HELD_HOSTS = re.compile(r"puc\.texas\.gov|gov\.texas\.gov")


def path(*p):
    return os.path.join(ROOT, *p)


def src(*p):
    with open(path(*p), encoding="utf-8") as f:
        return f.read()


def js(*p):
    return json.loads(src(*p))


def held_grids():
    """The grids (gallery codes) whose tables the site's license file marks "license needed" today, MISO aside."""
    out = set()
    for t in js("site", "data", "license_status.json")["tables"].values():
        if t.get("status") == "license needed":
            out |= {CODE[p] for p in t.get("publishers", []) if p in CODE}
    return out


def curtailment():
    held, f = held_grids(), js("site", "data", "curtailment", "free_energy.json")
    n = 0
    for g in held & set(f["grids"]):
        G = f["grids"][g]
        n += sum("under5" in L.get(w, {}) for L in G["locations"] for w in ("month", "year"))
        n += sum("under5" in v for v in G.get("most_cheap_hours", {}).values())
    n += sum(1 for v in f.get("widest_gap", {}).values() if v.get("grid") in held)
    n += sum(1 for v in f.get("compare", {}).values() if v.get("grid") in held)
    page = src("site", "app", "curtailment", "page.tsx")
    top = re.search(r"const top = (.*?);\n", page).group(1)
    if "priceHeld" not in top:
        n += 1
    return n


def seller():
    held = held_grids()
    cap = js("site", "data", "seller", "capture.json")
    n = sum(len(cap["grids"][g]["hubs"]) for g in held & set(cap["grids"]))
    n += len(held & set(js("site", "data", "merchant_snapshot.json")["isos"]))
    n += sum(len(glob.glob(path("site", "data", "seller", "hubs", g, "*.json"))) for g in held)
    model = src("site", "app", "cost-of-power", "seller", "model.ts")
    open_line = re.search(r"const open = (.*?);\n", model).group(1)
    if "licenseHeldGrid" not in open_line:
        n += 1
    return n


def policy_monitor():
    rows = js("site", "data", "policy", "monitor.json")["rows"]
    return sum(any(HELD_HOSTS.search(u) for u in r.get("sources", [])) for r in rows)


def map_queue():
    f = js("site", "data", "map.json")
    qk = [k["slug"] for k in f["kinds"]].index("queue")
    gi = [g["slug"] for g in f["grids"]].index("isone")
    return sum(1 for k, g in zip(f["k"], f["g"]) if k == qk and g == gi)


def companies_tab():
    data = src("site", "lib", "data.ts")
    body = data[data.index("export async function companies()"):]
    body = body[:body.index("\n}\n")]
    if "neq.${DEAL_SEED_SOURCE}" in body and 'DEAL_SEED_SOURCE = "erw:energy_deals"' in data:
        return 0
    p = path("warehouse", "output", "energy_companies.csv")
    if not os.path.exists(p):
        return 1
    with open(p, encoding="utf-8") as f:
        rows = csv.DictReader(ln for ln in f if not ln.startswith("#"))
        return sum(1 for r in rows if r.get("source") == "erw:energy_deals")


PLACES = {
    "/curtailment: ISO-NE's and NYISO's hours under USD 5": curtailment,
    "/cost-of-power/seller: ISO-NE and NYISO offered": seller,
    "/policy?view=monitor: the PUCT's and the Texas Governor's records": policy_monitor,
    "/map: ISO-NE's queue positions": map_queue,
    "/deals?tab=companies: the rows seeded from the held deals' parties": companies_tab,
}


class NoHeldValueLeft(unittest.TestCase):
    def test_the_hold_still_covers_isone_and_nyiso(self):
        self.assertEqual(held_grids(), {"isone", "nyiso"})

    def test_each_place_holds_none(self):
        for name, count in PLACES.items():
            with self.subTest(name):
                self.assertEqual(count(), 0)


class Curtailment(unittest.TestCase):
    """wip/audit-curtailment-1's test (session 10210), now asserting the hold."""

    def test_the_held_grids_are_named_with_the_license_words(self):
        f = js("site", "data", "curtailment", "free_energy.json")
        for g in ("isone", "nyiso"):
            self.assertNotIn(g, f["grids"])
            self.assertEqual(f["blank"][g]["words"], "license needed")
            self.assertEqual(f["blank"][g]["regions"], [])

    def test_the_summary_and_headline_are_gated(self):
        p = src("site", "app", "curtailment", "page.tsx")
        self.assertIn("const priceHeld = licenseHeldGrid(c.grid);", p)
        cheap = re.search(r"const cheap = (.*?)\n", p).group(1)
        self.assertTrue(cheap.startswith("priceHeld ? "), cheap[:60])
        tail = p[p.index('<HeadlineNumber label={`Curtailed, ${g.name}`}'):]
        self.assertIn("value={priceHeld ? <Blank words={LICENSE_NEEDED}", tail[:1500])

    def test_the_builder_skips_a_held_grid(self):
        b = src("warehouse", "derived", "free_energy.py")
        self.assertIn("for k in sorted(held_grid_ids()):", b)
        self.assertIn('words="license needed", regions=[]', b)


class Seller(unittest.TestCase):
    def test_the_grids_are_blank_with_the_license_words(self):
        cap = js("site", "data", "seller", "capture.json")
        for g in ("isone", "nyiso"):
            self.assertEqual(cap["blank"][g]["words"], "license needed")
        self.assertFalse(os.path.isdir(path("site", "data", "seller", "hubs", "isone")))
        self.assertNotIn("isone", js("site", "data", "seller", "hubs", "index.json")["grids"])

    def test_the_builders_skip_a_held_grid(self):
        self.assertIn('out["blank"][iso] = dict(name=g["name"], words="license needed")', src("warehouse", "derived", "capture_price.py"))
        self.assertIn("if iso not in held_snapshot_isos():", src("warehouse", "derived", "merchant_revenue.py"))
        self.assertIn('capture["blank"][g].get("words") == "license needed"', src("warehouse", "derived", "merchant_hubs.py"))


class PolicyMonitor(unittest.TestCase):
    """wip/audit-policy-7's test (session 10217), now asserting the held publisher's rows are out."""

    def test_the_table_is_still_held_whole(self):
        status = js("site", "data", "license_status.json")
        self.assertEqual(status["tables"]["policy_actions"]["status"], "license needed")

    def test_the_file_holds_no_puct_row(self):
        d = js("site", "data", "policy", "monitor.json")
        self.assertEqual(d["records"], len(d["rows"]))
        self.assertEqual([r["id"] for r in d["rows"] if r["body"] in ("PUCT", "Texas Governor")], [])

    def test_the_builder_leaves_them_out(self):
        self.assertIn("rows = [r for r in rows if not any(HELD_HOSTS.search(u) for u in r.get(\"sources\", []))]",
                      src("warehouse", "policy", "monitor_site.py"))


class MapQueue(unittest.TestCase):
    def test_isone_is_held_in_the_builder_and_the_list(self):
        b = src("warehouse", "derived", "project_map.py")
        self.assertIn('QUEUE_SHOWN = {"ercot": "ERCOT", "spp": "SPP", "caiso": "CAISO"}', b)
        self.assertIn('"isone": ("ISO-NE", "license needed")}', b)
        self.assertRegex(src("site", "lib", "resources.ts"), r'id: "isone", label: "ISO-NE", shown: false, words: "license needed"')

    def test_the_file_counts_them_held(self):
        f = js("site", "data", "map.json")
        held = {h["grid"]: h["rows"] for h in f["held"]}
        self.assertEqual(held.get("isone"), 414)
        self.assertEqual(f["counts"]["queue_rows_held"], sum(held.values()))
        self.assertEqual(f["counts"]["rows"], len(f["k"]))
        for j, kd in enumerate(f["kinds"]):
            self.assertEqual(kd["rows"], f["k"].count(j))
        qk = [k["slug"] for k in f["kinds"]].index("queue")
        self.assertEqual(len(f["more"]["queue"]["status"]), f["kinds"][qk]["rows"])


if __name__ == "__main__":
    unittest.main()
