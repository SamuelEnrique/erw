"""Session 465: the deal tracker against master plan tool 6.

The kinds of tool 6 the panel's groups gather under Other (nuclear restart, small modular reactor, gas generation,
behind the meter) and the status the stories state, as filters of the tracker; the hold's words with the row count it
covers; the decisions block under every tab. Part one runs site/lib/deals2.ts in Node on the table's rows (git holds
energy_deals) against the same rules written here in Python; part two reads the pages' code and the method note.
"""

import json
import os
import re
import tempfile
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_session113 import ROOT, dup, live_rows, node, src, table  # noqa: E402

DASHES = (chr(0x2014), chr(0x2013))
FILES = [("site", "lib", "deals2.ts"), ("site", "app", "deals", "page.tsx"), ("site", "app", "deals", "v2", "view.tsx"),
         ("site", "app", "deals", "Held.tsx"), ("site", "app", "deals", "Decisions.tsx"), ("docs", "methods", "energy_deals.md"),
         ("docs", "reviews", "deals-tool6-2026-10-21.md"), ("tests", "test_session465.py")]

# the rules of kindsOf(), written again in Python
WORDS = {
    "nuclear_restart": r"\brestart|recommission|\breopen",
    "smr": r"\bsmrs?\b|small modular|micro-?reactor",
    "behind_the_meter": r"behind[- ]the[- ]meter|co-?locat|\bon-?site\b",
}
GAS_TECH, GAS_BUILD = r"\bgas\b|natgas|natural gas", r"plant|turbine|generat|power station|peaker|combined[- ]cycle|\bccgt\b"


def kinds(r):
    text = f"{r['asset']} | {r['technology']}"
    out = []
    for k in ("nuclear_restart", "smr", "gas", "behind_the_meter"):
        if k == "gas":
            if re.search(GAS_TECH, r["technology"], re.I) and re.search(GAS_BUILD, r["asset"], re.I) and r["deal_type"] not in ("m_and_a", "fuel_supply"):
                out.append(k)
        elif r["deal_type"] == k or re.search(WORDS[k], text, re.I):
            out.append(k)
    return out


class TheKinds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            d = table("energy_deals")
        except FileNotFoundError:
            raise unittest.SkipTest("energy_deals is not on this machine")
        folds = dup.register()
        folds = folds[folds["ruling"] == "fold"]
        cls.d = d[~d["event_id"].isin(folds["duplicate_event_id"])].copy()
        tmp = tempfile.mkdtemp(prefix="erw465_")
        cls.addClassCleanup(shutil.rmtree, tmp, True)
        path = os.path.join(tmp, "rows.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(live_rows(d), f)
        sels = [{"kind": k} for k in ("nuclear_restart", "smr", "gas", "behind_the_meter", "nonsense")]
        sels += [{"status": s} for s in ("rumored", "announced", "signed", "closed", "cancelled", "maybe")]
        sels += [{"kind": "gas", "status": "signed", "type": "other"}]
        cls.sels = sels
        cls.got = node(
            "const fs = (await import('node:fs')).default; const m = await import('./lib/deals2.ts');"
            f"const rows = JSON.parse(fs.readFileSync({json.dumps(path)}, 'utf-8'));"
            "const pairs = JSON.parse(fs.readFileSync('data/deal_duplicates.json', 'utf-8')).pairs;"
            "const all = m.fold(rows.map(m.toDeal), pairs);"
            f"const out = {json.dumps(sels)}.map((sp) => {{ const x = m.inputsOf(sp, all); const shown = m.select(all, x);"
            " return { x, href: m.hrefOf(x), ids: shown.map((d) => d.id), words: m.selectionWords(x) }; });"
            "console.log(JSON.stringify({ kinds: Object.fromEntries(all.map((d) => [d.id, d.kinds])), out }));")

    def out(self, sp):
        return self.got["out"][self.sels.index(sp)]

    def test_every_deal_has_the_kinds_the_rules_give(self):
        want = {r["event_id"]: kinds(r) for r in self.d.to_dict("records")}
        self.assertEqual(set(want), set(self.got["kinds"]))
        for i, k in want.items():
            self.assertEqual(self.got["kinds"][i], k, i)

    def test_the_kinds_of_the_table_of_20_october(self):
        # 492 rows, extracted 2026-10-20T06:17:34Z: the counts of docs/reviews/deals-tool6-2026-10-21.md; skipped once
        # the table moves, as the review is a record of that day
        if len(table("energy_deals")) != 492:
            raise unittest.SkipTest("energy_deals has moved since 20 October")
        n = {k: sum(k in v for v in self.got["kinds"].values()) for k in ("nuclear_restart", "smr", "gas", "behind_the_meter")}
        self.assertEqual(n, {"nuclear_restart": 1, "smr": 4, "gas": 10, "behind_the_meter": 4})

    def test_a_kind_and_a_status_select_their_deals(self):
        for k in ("nuclear_restart", "smr", "gas", "behind_the_meter"):
            o = self.out({"kind": k})
            self.assertEqual(o["x"]["kind"], k)
            self.assertEqual(sorted(o["ids"]), sorted(i for i, v in self.got["kinds"].items() if k in v))
            self.assertIn(f"kind={k}", o["href"])
        status = dict(zip(self.d["event_id"], self.d["status"]))
        for s in ("rumored", "announced", "signed", "closed", "cancelled"):
            o = self.out({"status": s})
            self.assertEqual(sorted(o["ids"]), sorted(i for i in self.got["kinds"] if status[i] == s), s)
            self.assertIn(f"status {s}", o["words"])

    def test_a_value_the_page_does_not_offer_is_dropped(self):
        for sp in ({"kind": "nonsense"}, {"status": "maybe"}):
            o = self.out(sp)
            self.assertEqual((o["x"]["kind"], o["x"]["status"]), ("", ""))
            self.assertEqual(len(o["ids"]), len(self.got["kinds"]))
            self.assertEqual(o["href"], "/deals?tab=tracker")

    def test_choices_combine(self):
        o = self.out({"kind": "gas", "status": "signed", "type": "other"})
        self.assertEqual(o["href"], "/deals?tab=tracker&type=other&kind=gas&status=signed")
        self.assertEqual(o["words"], "other, gas generation, status signed")


class ThePages(unittest.TestCase):
    def test_the_tracker_offers_the_kinds_and_the_status(self):
        v = src("site", "app", "deals", "v2", "view.tsx")
        self.assertIn('name="kind"', v)
        self.assertIn('name="status"', v)
        self.assertIn("kind, technology, grid, party, year and status", v)

    def test_the_hold_says_how_many_rows_it_covers(self):
        h = src("site", "app", "deals", "Held.tsx")
        self.assertIn('check="catalogue|energy_deals|n_rows"', h)
        self.assertNotIn("attempt(deals", h)  # the count is the catalogue's: no row of the held table is read
        self.assertIn("import { catalogue }", h)
        for f in (("site", "app", "deals", "page.tsx"), ("site", "app", "deals", "v2", "view.tsx")):
            s = src(*f)
            self.assertIn("isLicenseReason", s, f)
            self.assertIn("<DealsHeld />", s, f)

    def test_the_decisions_block_is_under_every_tab_with_a_session_for_each(self):
        p = src("site", "app", "deals", "page.tsx")
        self.assertIn("<DealsDecisions />", p)
        self.assertLess(p.index("<DealsDecisions />"), p.index("<TableDownloads"))
        d = src("site", "app", "deals", "Decisions.tsx")
        entries = re.findall(r'\{ choice: "(.*?)", session: "([^"]+)"', d)
        self.assertGreaterEqual(len(entries), 15)
        for choice, session in entries:
            self.assertRegex(session, r"^\d+( and \d+)?$", choice)
        self.assertNotRegex(d, r"\d+(\.\d+)?\s*(MW|USD|percent)")  # words only: no figure in the block

    def test_the_method_note_names_the_new_figure_and_the_kinds(self):
        n = src("docs", "methods", "energy_deals.md")
        for w in ("catalogue|energy_deals|n_rows", "Master plan tool 6", "nuclear restart", "small modular reactor", "gas generation", "behind the meter", "session 465"):
            self.assertIn(w.lower(), n.lower(), w)

    def test_no_dash(self):
        for f in FILES:
            s = src(*f)
            for c in DASHES:
                self.assertNotIn(c, s, f)


if __name__ == "__main__":
    unittest.main()
