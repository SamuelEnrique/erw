"""Session 822: the deal tracker's public rows (chain 080, sessions 821 and 822).

The sort of warehouse/deals/public_rows.py on fixtures of five deals of each kind (shown, held, unsettled), the site's
file it writes (no held outlet's name or address in it), the pure functions of site/lib/dealspublic.ts run by node, the
file in site/data as committed, and the page's code. No request is made: the fixtures are in this file.
"""

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
import public_rows as P  # noqa: E402

REGISTRY = {"Bloomberg.com": "Bloomberg.com", "jpt.spe.org": "jpt.spe.org", "World Nuclear News": "World Nuclear News",
            "DOE newsroom": "DOE newsroom", "Reuters": "Reuters", "Electrek": "Electrek"}
VERDICTS = {"Bloomberg": "needs written permission", "JPT": "needs written permission", "Reuters": "needs written permission",
            "World Nuclear News": "may be public", "DOE newsroom": "may be public", "PJM": "needs a paid license"}
EVENT = {c: "" for c in P.EVENT_COLS}


def deal(i, **kw):
    d = dict(EVENT, event_id=f"deal:{i:016x}", event_date=f"2026-10-{(i % 28) + 1:02d}T10:00:00Z", event_type="deal", source="Reuters",
             source_url="https://www.reuters.com/x", deal_type="ppa", buyer=f"Buyer {i}", seller=f"Seller {i}", other_parties="", asset=f"asset {i}",
             technology="nuclear", state="", country="", mwh="", dollars="", price_value="", price_unit="", term_years="", announced_date="",
             date_basis="first_story_published", ai_power="false", confidence="0.8", n_stories="1", story_ids=f"news:{i}", story_urls="https://www.reuters.com/x",
             model_id="m", extracted_at="2026-10-22T15:02:19Z")
    d.update(kw)
    return d


def ev(deal_id, source, url, story="s"):
    return {"event_id": f"{deal_id}:{story}", "event_date": "2026-10-20T00:00:00Z", "event_type": "deal_evidence", "parties": "", "entity_ids": "",
            "mw": "", "price": "", "currency": "", "status": "", "source": source, "source_url": url, "deal_id": deal_id, "story_id": f"news:{story}",
            "evidence": "a sentence of the outlet's text"}


def fixtures():
    """15 deals: 1 to 5 shown (a public evidence row, some beside held ones), 6 to 10 held, 11 to 15 unsettled."""
    deals, evidence = [], []
    for i in range(1, 6):
        deals.append(deal(i, mw=str(100 * i), dollars=str(1_000_000 * i), source="Bloomberg.com", source_url="https://www.bloomberg.com/held"))
        evidence.append(ev(deals[-1]["event_id"], "World Nuclear News" if i < 5 else "DOE newsroom", f"https://www.world-nuclear-news.org/{i}", "a"))
        if i % 2 == 0:  # a held outlet reports it too
            evidence.append(ev(deals[-1]["event_id"], "Bloomberg.com", "https://www.bloomberg.com/held", "b"))
    for i in range(6, 11):
        deals.append(deal(i, mw=str(10 * i)))
        evidence.append(ev(deals[-1]["event_id"], ["Reuters", "Bloomberg.com", "jpt.spe.org", "Reuters", "Reuters"][i - 6], f"https://held.example/{i}", "a"))
        if i == 10:
            evidence.append(ev(deals[-1]["event_id"], "jpt.spe.org", "https://jpt.spe.org/x", "b"))
    for i in range(11, 16):
        deals.append(deal(i))
        evidence.append(ev(deals[-1]["event_id"], "Electrek", f"https://electrek.co/{i}", "a"))
        if i == 15:  # a held outlet beside the unread one: still unsettled (reading Electrek could show it)
            evidence.append(ev(deals[-1]["event_id"], "Reuters", "https://www.reuters.com/y", "b"))
    return deals, evidence


class SortTest(unittest.TestCase):
    def setUp(self):
        self.deals, self.evidence = fixtures()
        self.sorted = P.sort_deals(self.deals, self.evidence, REGISTRY, VERDICTS)

    def test_five_of_each(self):
        self.assertEqual(P.counts(self.sorted), {"shown": 5, "held": 5, "unsettled": 5})
        for i in range(1, 16):
            want = "shown" if i <= 5 else "held" if i <= 10 else "unsettled"
            self.assertEqual(self.sorted[f"deal:{i:016x}"]["sort"], want, i)

    def test_publishers_canon(self):
        s = self.sorted["deal:%016x" % 2]
        self.assertEqual(s["public"], ["World Nuclear News"])
        self.assertEqual(s["held"], ["Bloomberg"])   # Bloomberg.com is Bloomberg
        self.assertEqual(self.sorted["deal:%016x" % 10]["held"], ["Reuters", "JPT"])   # jpt.spe.org is JPT
        self.assertEqual(self.sorted["deal:%016x" % 15]["unsettled"], ["Electrek"])
        self.assertEqual(self.sorted["deal:%016x" % 15]["held"], ["Reuters"])

    def test_no_evidence_is_held(self):
        s = P.sort_deals([deal(99)], [], REGISTRY, VERDICTS)
        self.assertEqual(s["deal:%016x" % 99]["sort"], "held")

    def test_held_publishers_ranked(self):
        top = P.held_publishers(self.sorted)
        self.assertEqual(top[0], ("Reuters", 3, 3))
        self.assertEqual([p for p, _, _ in top], ["Reuters", "JPT", "Bloomberg"])   # 2 deals rest on JPT, 1 on Bloomberg
        self.assertEqual(P.unsettled_publishers(self.sorted), [("Electrek", 5)])

    def test_site_json_names_no_held_outlet(self):
        out = P.site_json(self.deals, self.sorted, os.path.join(ROOT, "warehouse", "deals", "public_rows.py"))
        self.assertEqual(out["counts"], {"shown": 5, "held": 5, "unsettled": 5})
        self.assertEqual(len(out["shown"]), 5)
        text = json.dumps(out)
        for word in ("Bloomberg", "bloomberg.com", "Reuters", "reuters.com", "jpt.spe.org", "electrek"):
            self.assertNotIn(word.lower(), text.lower(), word)
        r = next(x for x in out["shown"] if x["event_id"] == "deal:%016x" % 2)
        self.assertEqual(r["source"], "World Nuclear News")
        self.assertEqual(r["source_url"], "https://www.world-nuclear-news.org/2")
        self.assertEqual(r["extra"]["story_urls"], "https://www.world-nuclear-news.org/2")
        self.assertEqual(r["other_publishers"], 1)
        self.assertEqual(r["mw"], 200.0)
        self.assertEqual(r["extra"]["dollars"], "2000000")
        self.assertNotIn("", r["extra"].values())   # a blank is left out, as the loader leaves it
        self.assertEqual(out["shown"][0]["event_id"], max(x["event_id"] for x in out["shown"] if x["event_date"] == out["shown"][0]["event_date"]))


class CommittedFileTest(unittest.TestCase):
    """site/data/deals_public.json as committed: sound, and naming no outlet whose verdict asks for permission."""

    def setUp(self):
        with open(os.path.join(SITE, "data", "deals_public.json"), encoding="utf-8") as f:
            self.file = json.load(f)
        with open(os.path.join(ROOT, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8") as f:
            self.asking = [r["key"] for r in csv.DictReader(f) if r["verdict"] != "may be public"]

    def test_sound(self):
        f = self.file
        self.assertEqual(f["counts"]["shown"], len(f["shown"]))
        for r in f["shown"]:
            self.assertTrue(r["public_evidence"], r["event_id"])
            urls = {e["url"] for e in r["public_evidence"]}
            self.assertIn(r["source_url"], urls)
            self.assertIn(r["source"], {e["publisher"] for e in r["public_evidence"]})
            for u in r["extra"].get("story_urls", "").split(";"):
                self.assertIn(u, urls)
            self.assertEqual(len(r["extra"].get("story_ids", "").split(";")), len(r["public_evidence"]))

    def test_no_asking_publisher_named(self):
        text = json.dumps(self.file).lower()
        for p in self.asking:
            if p in ("Google", "Meta", "Oracle", "Switch", "Microsoft"):   # a word that may be a party's own name
                continue
            self.assertNotIn(p.lower(), text, p)
        for host in ("reuters.com", "bloomberg.com", "ft.com", "wsj.com", "hartenergy.com", "rigzone.com", "lngprime.com"):
            self.assertNotIn(host, text, host)


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=SITE, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if "Unknown file extension" in r.stderr or "ERR_UNKNOWN_FILE_EXTENSION" in r.stderr:
            raise unittest.SkipTest("this node does not read TypeScript files")
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class LibTest(unittest.TestCase):
    """The pure functions of site/lib/dealspublic.ts, run by node on the fixtures' file."""

    @classmethod
    def setUpClass(cls):
        deals, evidence = fixtures()
        cls.file = P.site_json(deals, P.sort_deals(deals, evidence, REGISTRY, VERDICTS), os.path.join(ROOT, "warehouse", "deals", "public_rows.py"))
        cls.file["written_by"] = "test"
        bad = json.loads(json.dumps(cls.file))
        bad["shown"][0]["source_url"] = "https://www.bloomberg.com/held"
        cls.got = node(
            "const m = await import('./lib/dealspublic.ts');"
            f"const f = {json.dumps(cls.file)}; const bad = {json.dumps(bad)};"
            "console.log(JSON.stringify({counts: m.publicCounts(f), sound: m.fileIsSound(f), badSound: m.fileIsSound(bad),"
            " line: m.heldLine({shown: 5, held: 5, unsettled: 0}), line1: m.heldLine({shown: 1, held: 1, unsettled: 1}),"
            " keys: [m.countKey('held'), m.rowKey('deal:1', 'mw')]}));"
        )

    def test_counts_and_sound(self):
        self.assertEqual(self.got["counts"], {"shown": 5, "held": 5, "unsettled": 5, "total": 15})
        self.assertTrue(self.got["sound"])
        self.assertFalse(self.got["badSound"])

    def test_words_and_keys(self):
        self.assertEqual(self.got["line"]["unsettled"], "")
        self.assertIn("license needed", self.got["line"]["held"])
        self.assertTrue(self.got["line1"]["held"].startswith("deal rests"))
        self.assertTrue(self.got["line1"]["unsettled"].startswith("deal rests"))
        self.assertEqual(self.got["keys"], ["dealpub|counts|held", "dealpub|deal:1|mw"])


class PageCodeTest(unittest.TestCase):
    def read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_page_draws_public_rows_under_the_hold(self):
        page = self.read("site", "app", "deals", "page.tsx")
        self.assertIn("deals_public.json", page)
        self.assertIn("fileIsSound(", page)
        self.assertIn("<DealsHeld file={PUBLIC} />", page)
        table = self.read("site", "app", "deals", "DealsTable.tsx")
        self.assertIn("dealpub|${d.id}|${field}", table)
        self.assertIn("publicEvidence", table)
        held = self.read("site", "app", "deals", "Held.tsx")
        for k in ("countKey(\"held\")", "countKey(\"unsettled\")", "countKey(\"shown\")"):
            self.assertIn(k, held)
        self.assertIn('if (p[0] === "dealpub")', self.read("site", "scripts", "check-values.mjs"))
        self.assertIn("dealpub|counts|shown", self.read("docs", "methods", "energy_deals.md"))

    def test_no_em_dash(self):
        for p in (("site", "lib", "dealspublic.ts"), ("site", "app", "deals", "Held.tsx"), ("site", "app", "deals", "DealsTable.tsx"),
                  ("site", "app", "deals", "page.tsx"), ("site", "app", "deals", "Decisions.tsx"), ("warehouse", "deals", "public_rows.py"),
                  ("docs", "methods", "energy_deals.md"), ("docs", "reviews", "deals-public-rows-2026-10-23.md"), ("tests", "test_session822.py")):
            self.assertNotIn(chr(0x2014), self.read(*p), p)
            self.assertIsNone(re.search(r"\s--\s", self.read(*p)), p)


if __name__ == "__main__":
    unittest.main()
