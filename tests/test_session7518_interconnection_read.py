"""Session 7518 (chain 304, part B, 16 November 2026): the interconnection queue explorer, /explore/interconnection,
read as a developer deciding where to file (docs/reviews/interconnection-read-2026-11-16.md). What is held here:

- ERCOT's two statuses are headed by what they are ("Agreement signed", "No agreement yet") in its headline numbers and
  its table of years, the six queues' table keeps the common words and ERCOT's row says so in a tip, and the reason
  stands on the queue table itself where it is on the machine (a "completed" position with a projected operation day
  after the pull and no day of approval to synchronize);
- the six queues' table, in positions, draws the withdrawn share, the median wait and the waits counted of the one entry
  year, queue beside queue, and in MW does not;
- the wait's chart says in a tip whose waits a point counts;
- an address that asks for PJM, and a held queue's line, point to the same grid on /queues, which holds it, and no
  figure of a held queue is drawn;
- one line says a large load's request is in no figure and links the two pages of the load side.

The views are drawn by the page's own code on the table file (site/scripts/interconnection-figures.mjs --only), so the
drawn tests skip on a machine without replication/interconnection/rows/ or without node.
"""
import csv
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "interconnection")
ROWS = os.path.join(REP, "rows", "iso_queue_statistics.csv")
ERCOT = os.path.join(REP, "rows", "ercot_interconnection_queue.csv")
DASHES = (chr(0x2014), chr(0x2013))
ONLY = ["queue=ercot", "queue=ercot&measure=mw", "queue=spp&from=2018&to=2018", "queue=caiso&measure=mw&from=2021&to=2021", "queue=pjm", "queue=miso", "queue=nyiso", "queue=isone"]
KEY = "series|iso_queue_statistics|{q}:queue_{y}|{v}|{y}-01-01T00:00:00Z"


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheWords(unittest.TestCase):
    def test_ercots_statuses_have_words_of_their_own_and_no_other_queue_has(self):
        lib = src("site", "lib", "explore", "interconnection.ts")
        self.assertIn('ercot: { operating: { label: "Agreement signed", short: "Signed" }, waiting: { label: "No agreement yet", short: "No agreement" } },', lib)
        block = lib[lib.index("export const STATUS_WORDS"):lib.index("/** Why a queue has words of its own")]
        self.assertEqual(block.count('label: "'), 2, "ERCOT's two and no other")
        self.assertIn("interconnection agreement is signed", lib)
        page = src("site", "app", "explore", "interconnection", "page.tsx")
        self.assertNotIn("`Reached operation, ${unit}`", page)
        self.assertNotIn("`Still waiting, ${unit}`", page)
        self.assertIn("name: words(s.key).short", page)

    def test_the_note_the_replication_and_the_page_say_the_same_words(self):
        note = src("docs", "methods", "interconnection_explorer.md")
        rep = src("replication", "interconnection", "replicate.py")
        for w in ("Agreement signed", "No agreement yet"):
            self.assertIn(w, note)
            self.assertIn(w, rep)
        self.assertIn("### ERCOT's two statuses (session 7518)", note)
        self.assertIn("### Whose wait (session 7518)", note)
        self.assertIn("### Where the other queues and the load side are (session 7518)", note)
        self.assertIn('ERCOT\'s "Completed" is not ERCOT\'s word', src("docs", "methods", "energy_projects.md"))

    def test_the_grids_the_page_points_to_are_views_of_the_queue_page(self):
        lib = src("site", "lib", "explore", "interconnection.ts")
        self.assertIn('export const QUEUED_UP_GRIDS = ["pjm", "miso", "nyiso", "isone"];', lib)
        queues = src("site", "lib", "queues.ts")
        with open(os.path.join(SITE, "data", "queues.json"), encoding="utf-8") as f:
            views = json.load(f)["views"]
        for g in ("pjm", "miso", "nyiso", "isone"):
            self.assertIn('{ slug: "%s",' % g, queues)
            self.assertIn("%s|all" % g, views)

    def test_no_dash_in_what_this_session_wrote(self):
        for parts in [("docs", "reviews", "interconnection-read-2026-11-16.md"), ("tests", "test_session7518_interconnection_read.py"),
                      ("site", "app", "explore", "interconnection", "page.tsx"), ("site", "app", "explore", "interconnection", "Decisions.tsx"),
                      ("site", "lib", "explore", "interconnection.ts"), ("site", "scripts", "interconnection-figures.mjs"),
                      ("replication", "interconnection", "replicate.py"), ("docs", "methods", "interconnection_explorer.md")]:
            s = src(*parts)
            for dash in DASHES:
                self.assertNotIn(dash, s, "/".join(parts))


@unittest.skipUnless(os.path.exists(ERCOT), "ERCOT's queue table is not in replication/interconnection/rows (fetch_rows.py)")
class WhyErcotsWordsChanged(unittest.TestCase):
    def test_a_completed_position_of_ercot_is_not_a_plant_in_operation(self):
        # When this fails the connector has changed what "completed" is for ERCOT: read the table again, and if the group
        # is now the plants in operation, take ERCOT out of STATUS_WORDS and out of the note's "ERCOT's two statuses".
        with open(ERCOT, encoding="utf-8", newline="") as f:
            lines = f.read().split("\n")
        n = 0
        while lines[n].startswith("#"):
            n += 1
        rows = list(csv.DictReader(lines[n:]))
        pulled = max(r["retrieved_at"][:10] for r in rows)
        done = [r for r in rows if r["status"] == "completed"]
        self.assertGreater(len(done), 100)
        self.assertEqual({r["iso_status"] for r in done}, {"Completed"})
        not_built = [r for r in done if not r["actual_in_service_date"] and r["proposed_in_service_date"][:10] > pulled]
        self.assertGreater(len(not_built), len(done) // 2, "most completed positions have a projected day after the pull and no day of approval to synchronize")
        newest = max(int(r["queue_date"][:4]) for r in done if r["queue_date"]) - 1
        year = [r for r in done if r["queue_date"][:4] == str(newest)]
        self.assertTrue(year and all(not r["actual_in_service_date"] for r in year), f"entry year {newest}")


@unittest.skipUnless(os.path.exists(ROWS) and shutil.which("node"), "the table is not in replication/interconnection/rows (fetch_rows.py), or node is not on the path")
class ThePageAsDrawn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        out = os.path.join(tempfile.mkdtemp(prefix="erw7518_"), "page.json")
        r = subprocess.run([shutil.which("node"), "--no-warnings", "--import", "./scripts/tsx-register.mjs", "scripts/interconnection-figures.mjs", ROWS, out, "--only=" + ";".join(ONLY)],
                           cwd=SITE, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-800:])
        with open(out, encoding="utf-8") as f:
            cls.page = json.load(f)
        cls.by = {"&".join(f"{k}={v}" for k, v in x["q"].items()): x for x in cls.page["views"]}

    def test_only_the_named_addresses_are_drawn(self):
        self.assertEqual(list(self.by), ONLY)

    def test_ercots_view_is_headed_by_what_its_statuses_are(self):
        v = self.by["queue=ercot"]
        labels = [h["label"] for h in v["headlines"]]
        self.assertEqual(labels, ["Entered, positions, ERCOT, entered 2025", "Agreement signed, positions, ERCOT, entered 2025", "No agreement yet, positions, ERCOT, entered 2025"])
        self.assertEqual(v["headlines"][1]["key"], KEY.format(q="ercot", y=2025, v="positions_operating"))
        self.assertEqual(v["years_table"]["head"][:6], ["Entry year", "Entered", "Agreement signed", "Withdrawn", "No agreement yet", "Status not stated"])
        mw = self.by["queue=ercot&measure=mw"]
        self.assertEqual([h["label"] for h in mw["headlines"]][1:], ["Agreement signed, MW, ERCOT, entered 2025", "No agreement yet, MW, ERCOT, entered 2025"])
        self.assertEqual(mw["years_table"]["head"], ["Entry year", "Entered", "Agreement signed", "Withdrawn", "No agreement yet", "Status not stated"])

    def test_another_queue_keeps_the_common_words(self):
        v = self.by["queue=spp&from=2018&to=2018"]
        self.assertEqual([h["label"] for h in v["headlines"]], ["Entered, positions, SPP, entered 2018", "Reached operation, positions, SPP, entered 2018", "Withdrawn, share of positions entered, SPP, entered 2018"])
        self.assertEqual(v["years_table"]["head"][2:5], ["Reached operation", "Withdrawn", "Still waiting"])

    def test_the_six_queues_stand_side_by_side_on_the_share_and_the_wait(self):
        v = self.by["queue=spp&from=2018&to=2018"]
        t = v["queues_table"]
        self.assertEqual(t["head"], ["Queue", "Entered", "Reached operation", "Withdrawn", "Still waiting", "Status not stated", "Withdrawn, share of entered", "Median wait, years", "Waits counted"])
        rows = {r["label"]: r for r in t["rows"]}
        self.assertEqual(list(rows), ["CAISO", "ERCOT", "NYISO", "MISO", "SPP", "ISO-NE"])
        for q, name in (("caiso", "CAISO"), ("spp", "SPP")):
            self.assertEqual(rows[name]["cells"][5:], [KEY.format(q=q, y=2018, v=x) for x in ("withdrawal_rate", "wait_years_median", "wait_positions")])
        # ERCOT holds no withdrawn share; its wait and its count are rows of the table
        self.assertEqual(rows["ERCOT"]["cells"][5:], ["not held", KEY.format(q="ercot", y=2018, v="wait_years_median"), KEY.format(q="ercot", y=2018, v="wait_positions")])
        self.assertIn('"Reached operation" is "Agreement signed" and "Still waiting" is "No agreement yet"', rows["ERCOT"]["label_tip"])
        self.assertIsNone(rows["SPP"]["label_tip"])
        for held in ("NYISO", "MISO", "ISO-NE"):
            self.assertEqual(rows[held]["cells"], ["license needed"])
        # the figures as written: SPP's 2018 wait stands on 2 positions
        self.assertEqual(self.page["keyed"][KEY.format(q="spp", y=2018, v="wait_years_median")]["text"], "4.40")
        self.assertEqual(self.page["keyed"][KEY.format(q="spp", y=2018, v="wait_positions")]["text"], "2")
        # in MW the table is as it was: entered and the four statuses
        self.assertEqual(self.by["queue=caiso&measure=mw&from=2021&to=2021"]["queues_table"]["head"], ["Queue", "Entered", "Reached operation", "Withdrawn", "Still waiting", "Status not stated"])

    def test_the_waits_chart_says_whose_waits_it_counts(self):
        spp, ercot = self.by["queue=spp&from=2018&to=2018"], self.by["queue=ercot"]
        for v in (spp, ercot):
            self.assertIn("A position still waiting is in no point", v["wait_tip"])
            self.assertIn("by the year a plant came online", v["wait_tip"])
        self.assertIn("approved to synchronize", ercot["wait_tip"])
        self.assertIn("Commercial Operation Date", spp["wait_tip"])
        self.assertEqual(spp["charts"][-1], "SPP: the median wait from entry to operation", "the title is read without its tip")

    def test_pjm_and_a_held_queue_are_told_where_they_are_counted(self):
        pjm = self.by["queue=pjm"]
        self.assertIn("Berkeley Lab's Queued Up counts PJM", pjm["asked_pjm"])
        self.assertIn("/queues?grid=pjm&tech=all", pjm["links"])
        self.assertEqual(pjm["filters"]["queue"]["chosen"], "caiso")
        self.assertIsNone(self.by["queue=ercot"]["asked_pjm"])
        for q in ("miso", "nyiso", "isone"):
            v = self.by[f"queue={q}"]
            self.assertEqual(v["held_elsewhere"], q)
            self.assertIn(f"/queues?grid={q}&tech=all", v["links"])
            self.assertEqual(v["keyed"], 0, "no figure of a held queue")
            self.assertIn("license needed", v["held_line"])
        for key in self.page["keyed"]:
            self.assertNotRegex(key, r"\|(miso|nyiso|isone):queue_")

    def test_the_load_side_is_named_with_its_two_pages(self):
        for q in ("queue=ercot", "queue=spp&from=2018&to=2018", "queue=pjm"):
            v = self.by[q]
            self.assertIn("is in no figure of this page", v["load_side"])
            self.assertIn("/datacenters", v["links"])
            self.assertIn("/cost-of-power?view=allgrids", v["links"])
            self.assertIn("Queued Up is another source", v["related"])


if __name__ == "__main__":
    unittest.main()
