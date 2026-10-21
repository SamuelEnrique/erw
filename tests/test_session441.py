"""Session 441: the datacenter and deals tables, row by row, by what their sources allow (the chain of 21 October 2026).

Energy Research Warehouse (ERW). docs/reviews/sources-by-row-2026-10-21.md counts, for datacenter_facilities,
datacenter_projects, datacenter_operator_sites and energy_deals, each row's source publishers (the row's `source`,
every story of its `story_ids` through news_stories, every member of a facility's `member_ids`) against the verdicts of
license_verdicts.csv, and lists the rows that rest only on public sources in
docs/reviews/sources-by-row-2026-10-21-public-rows.csv.

What is held here: no em or en dash in what the session wrote; every snake_case name in backticks is a table of
coverage.csv or a column of the files read; the counts the review states (rows, MW, the three classes, variant B, the
World Nuclear News rows) equal a recount from the tables by this file's own code; the public-rows CSV is exactly the
recount's public rows. The recount needs the tables in warehouse/output (not in git) as they stood on 21 October:
without them, or once a build has moved their row counts, those tests skip.
Nothing here writes a file or makes a request.
"""

import collections
import csv
import io
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
META = os.path.join(ROOT, "warehouse", "metadata")
DOC = os.path.join(ROOT, "docs", "reviews", "sources-by-row-2026-10-21.md")
PUBLIC_CSV = os.path.join(ROOT, "docs", "reviews", "sources-by-row-2026-10-21-public-rows.csv")
WRITTEN = [DOC, PUBLIC_CSV, os.path.join(ROOT, "tests", "test_session441.py"),
           os.path.join(ROOT, "archive", "sessions", "SESSION_441_REPORT.md")]
TABLES = ["datacenter_facilities", "datacenter_projects", "datacenter_operator_sites", "energy_deals"]
NEEDED = TABLES + ["news_stories"]
OPERATORS = {"Amazon Web Services", "Digital Realty", "Equinix", "Google", "Meta", "Microsoft", "Oracle", "Switch", "Vantage Data Centers"}
OTHER_NAMES = {"canon", "hold", "row", "public", "unsettled", "release_v1", "load", "licensebygrid", "licensebyrow", "permission"}


def text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def table(t):
    with open(os.path.join(OUT, f"{t}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(io.StringIO("".join(ln for ln in f if not ln.startswith("#")))))


def meta(name):
    with open(os.path.join(META, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# the tables as the review read them (21 October, 07:16 UTC): rows a table. A later build moves them, and the review is
# a record of that day, so the counting tests then skip rather than fail.
SNAPSHOT = {"datacenter_facilities": 420, "datacenter_projects": 143, "datacenter_operator_sites": 275, "energy_deals": 492}


def have_tables():
    return all(os.path.exists(os.path.join(OUT, f"{t}.csv")) for t in NEEDED)


def same_snapshot():
    return have_tables() and all(len(table(t)) == n for t, n in SNAPSHOT.items())


def mwf(s):
    try:
        return float(s)
    except ValueError:
        return None


class Recount:
    """Every row's publisher set and class, counted afresh."""

    def __init__(self):
        reg = {r["source"]: r["publisher"] for r in meta("sources.csv")}
        self.verdict = {r["key"]: r["verdict"] for r in meta("license_verdicts.csv")}
        pub = lambda s: licenses.canon(reg.get(s, s))  # noqa: E731
        story = {s["event_id"]: s["source"] for s in table("news_stories")}
        self.rows = {t: table(t) for t in TABLES}
        self.sets = {}
        for t in ("datacenter_projects", "energy_deals"):
            k = "event_id" if t == "energy_deals" else "entity_id"
            self.sets[t] = {r[k]: {pub(r["source"])} | {pub(story[s]) for s in r["story_ids"].split(";") if s}
                            for r in self.rows[t]}
        self.sets["datacenter_operator_sites"] = {r["entity_id"]: {pub(r["source"])} for r in self.rows["datacenter_operator_sites"]}
        fac = {}
        for r in self.rows["datacenter_facilities"]:
            s = {pub(r["source"])}
            for m in r["member_ids"].split(";"):
                head = m.split(":")[0]
                if head == "datacenter":
                    s |= self.sets["datacenter_projects"][m]
                elif head == "dcsite":
                    s |= self.sets["datacenter_operator_sites"][m]
                else:
                    s.add({"ercot_queue": "ERCOT", "nyiso_queue": "NYISO"}[head])
            fac[r["entity_id"]] = s
        self.sets["datacenter_facilities"] = fac

    def cls(self, pubs, b=False):
        vs = {"may be public" if b and p in OPERATORS else self.verdict.get(p, "none") for p in pubs}
        if vs <= {"may be public"}:
            return "public"
        return "permission" if vs - {"may be public", "none"} else "not settled"

    def mwcol(self, t):
        return "mw" if t == "energy_deals" else "capacity_mw"

    def key(self, t):
        return "event_id" if t == "energy_deals" else "entity_id"

    def classes(self, t, b=False):
        out = collections.defaultdict(lambda: [0, 0, 0.0])
        for r in self.rows[t]:
            g = out[self.cls(self.sets[t][r[self.key(t)]], b)]
            g[0] += 1
            m = mwf(r[self.mwcol(t)])
            if m is not None:
                g[1] += 1
                g[2] += m
        return out


class TestWords(unittest.TestCase):
    def test_no_dashes(self):
        for p in WRITTEN:
            if os.path.exists(p):
                self.assertNotRegex(text(p), "[" + chr(0x2013) + chr(0x2014) + "]", p)

    def test_names_in_backticks(self):
        known = {r["table"] for r in meta("coverage.csv")} | OTHER_NAMES
        for name in ("sources.csv", "license_verdicts.csv", "license_status.csv"):
            known |= set(meta(name)[0])
        for t in TABLES:
            self.assertIn(t, known)
        if not have_tables():
            self.skipTest("the tables' columns are read from warehouse/output, not on this machine")
        for t in NEEDED + ["datacenter_projects_evidence", "energy_deals_evidence"]:
            known |= set(table(t)[0])
        for name in re.findall(r"`([a-z][a-z0-9_]*)`", text(DOC)):
            self.assertIn(name, known, name)


@unittest.skipUnless(same_snapshot(), "the tables of warehouse/output are not on this machine, or have moved since the review")
class TestCounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Recount()
        cls.doc = text(DOC)

    def test_table_row(self):
        for t in TABLES:
            c = self.r.classes(t)
            rows = len(self.r.rows[t])
            withmw = sum(g[1] for g in c.values())
            mw = sum(g[2] for g in c.values())
            pub, perm, ns = c.get("public", [0, 0, 0.0]), c["permission"], c.get("not settled", [0, 0, 0.0])
            line = f"| `{t}` | {rows} | {withmw} | {mw:,.1f} | "
            line += (f"{pub[0]} ({pub[2]:,.0f} MW)" if pub[0] else "0") + " | "
            line += f"{perm[0]} ({perm[1]} with MW, {perm[2]:,.1f} MW) | "
            line += (f"{ns[0]} ({ns[2]:,.0f} MW)" if ns[0] else "0") + " |"
            self.assertIn(line, self.doc, t)

    def test_headline(self):
        total = sum(len(v) for v in self.r.rows.values())
        public = sum(self.r.classes(t).get("public", [0])[0] for t in TABLES)
        self.assertIn(f"**{public} of {total:,} rows rest only on sources", self.doc)

    def test_variant_b(self):
        fb = self.r.classes("datacenter_facilities", b=True)["public"]
        ob = self.r.classes("datacenter_operator_sites", b=True)["public"]
        self.assertIn(f"| {fb[0]} rows ({fb[1]} with MW, {fb[2]:,.1f} MW) | 0 | {ob[0]} rows ({ob[1]} with MW, {ob[2]:,.1f} MW) |", self.doc)

    def test_world_nuclear_news(self):
        d = self.r.sets["energy_deals"]
        rows = [r for r in self.r.rows["energy_deals"] if "World Nuclear News" in d[r["event_id"]]]
        held = [r for r in rows if self.r.cls(d[r["event_id"]]) != "public"]
        mw = sum(mwf(r["mw"]) or 0.0 for r in held)
        self.assertIn(f"World Nuclear News is under {len(rows)} deals and holds {mw:,.1f} MW", self.doc)
        self.assertIn(f"{len(held)} of the {len(rows)} were also carried by a publisher that asks permission", self.doc)
        self.assertTrue(all(self.r.cls(d[r["event_id"]]) == "permission" for r in held))

    def test_public_csv(self):
        want = {(t, k) for t in TABLES for k, s in self.r.sets[t].items() if self.r.cls(s) == "public"}
        with open(PUBLIC_CSV, encoding="utf-8", newline="") as f:
            got = {(r["table"], r["id"]) for r in csv.DictReader(f)}
        self.assertEqual(got, want)
        for _, k in want:
            self.assertIn(f"`{k}`", self.doc)

    def test_every_story_found(self):
        ids = {s["event_id"] for s in table("news_stories")}
        n = 0
        for t in ("datacenter_projects", "energy_deals"):
            for r in self.r.rows[t]:
                for s in filter(None, r["story_ids"].split(";")):
                    self.assertIn(s, ids)
                    n += 1
        self.assertIn(f"All {n} story ids of the two news tables were found there", self.doc)


if __name__ == "__main__":
    unittest.main()
