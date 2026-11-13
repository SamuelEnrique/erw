"""Session 1895: the Roundup's faults of W45 in docs/reviews/periodicals-faults-2026-11-05.md, rows 64, 68 and 71 (its open
part), proved on fixtures. No model call, no network, no warehouse table read: every frame is written here (the real
eia860m_planned_generators is the data machine's; the look-up is fed a small frame of the same columns).

Row 64, the line: "Orsted completes Revolution Wind, a 704 MW offshore wind farm now in commercial operation" / "What the
evidence does not establish: the 704 MW is the outlet's figure, not a warehouse table's."
The fault: "The warehouse holds the plant: `eia860m_planned_generators` lists Revolution Wind (plant 65500, generator
REVWD, Rhode Island) at 715 MW nameplate, under construction more than half complete, planned operation 2026-11-01
(EIA-860M, September 2026). The reader is told no table has it, and not the table's different figure."
The fix: "What the evidence does not establish: EIA-860M (September 2026) lists Revolution Wind at 715 MW nameplate,
planned for 2026-11-01; the 704 MW is the outlet's, and EIA has not yet listed the plant as operating." `evidence_gap`
looks the named plant up in `eia860m_planned_generators` ... first.

Row 68, the line: "**Largest new datacenter load first reported this week:** no facility ... passes the datacenter table's
floor (3 under it); in its place, the week's next price move: WTI Cushing crude closed at 99.64 USD/bbl ..."
The fault: "A second oil price beside Brent's: the five hold two market rows and none of infrastructure or capacity".
The fix: "in its place, capacity: Revolution Wind, offshore wind off Rhode Island, entered commercial operation (EIA-860M
lists it at 715 MW, planned for 2026-11-01; POWER Magazine, Canary Media)." The stand-in comes from a part not yet among
the five (capacity, then policy ...), a second price only when neither is held.

Row 71, the open part: "302.71 USD/MWh at HB_SOUTH (ERCOT), interval starting 2026-11-03 17:45 local (2026-11-03 23:45
UTC), spp_rtm [4], ERCOT's real-time settlement point price": "spp_rtm", a source id, reads as SPP the grid operator in an
ERCOT line. The fix: "302.71 USD/MWh at HB_SOUTH (ERCOT), the 15-minute interval starting 2026-11-03 17:45 Central (23:45
UTC) [4]" (the Tables line keeps the source ids)."""

import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import brief  # noqa: E402
import roundup  # noqa: E402

UTC = "UTC"
START = pd.Timestamp("2026-11-02", tz=UTC)
CUT = pd.Timestamp("2026-11-08 23:26", tz=UTC)

COLS = dict(entity_id="", name="", capacity_mw="", nameplate_mw="", plant_id="", generator_id="", state="", technology="",
            planned_operation_date="", vintage="2026-09")
REV = dict(COLS, entity_id="eia860:65500:REVWD", name="Revolution Wind", capacity_mw="715", nameplate_mw="715", plant_id="65500",
           generator_id="REVWD", state="RI", technology="Offshore Wind Turbine", planned_operation_date="2026-11-01")
# rows the look-up must not take: a plain name, a one-word name, a plant of two generators
PLAIN = dict(COLS, entity_id="eia860:1:1", name="Solar Project, LLC", nameplate_mw="5", plant_id="1", planned_operation_date="2027-01-01")
ONE = dict(COLS, entity_id="eia860:2:1", name="Kalmar", nameplate_mw="20", plant_id="2", planned_operation_date="2027-01-01")
TWO_A = dict(COLS, entity_id="eia860:3:A", name="Sunrise Ridge Solar (SRS)", nameplate_mw="100", plant_id="3", state="NV",
             technology="Solar Photovoltaic", planned_operation_date="2027-03-01")
TWO_B = dict(TWO_A, entity_id="eia860:3:B", generator_id="B", nameplate_mw="50.5", planned_operation_date="2027-06-01")

STORY = dict(cluster_id="news:rev", parties="Orsted", mw="704", price="", outlets=3, kind="event", why="",
             titles=["Orsted completes Revolution Wind offshore wind farm", "Revolution Wind enters commercial operation"],
             links=[("POWER Magazine", "https://www.powermag.com/x")])
HEAD = "Orsted completes Revolution Wind, a 704 MW offshore wind farm now in commercial operation"
OLD_GAP = "What the evidence does not establish: the 704 MW is the outlet's figure, not a warehouse table's."
NEW_GAP = ("What the evidence does not establish: EIA-860M (September 2026) lists Revolution Wind at 715 MW nameplate, planned "
           "for 2026-11-01; the 704 MW is the outlet's, and EIA has not yet listed the plant as operating.")


def index(*rows):
    return roundup.plant_index(pd.DataFrame(list(rows)))


class Row64TheLookUp(unittest.TestCase):
    def test_the_named_plant_is_found(self):
        p = roundup.planned_plant(STORY, HEAD, index(REV, PLAIN, ONE, TWO_A, TWO_B))
        self.assertEqual((p["name"], p["mw"], p["dates"], p["ids"]), ("Revolution Wind", 715.0, ["2026-11-01"], ["eia860:65500:REVWD"]))

    def test_a_possessive_and_signs_still_match(self):
        p = roundup.planned_plant(dict(STORY, titles=[]), "Orsted's Revolution-Wind is done", index(REV))
        self.assertEqual(p["plant_id"], "65500")

    def test_plain_and_one_word_names_are_not_keys(self):
        self.assertEqual(roundup.plant_key("Solar Project, LLC"), "")
        self.assertEqual(roundup.plant_key("Kalmar"), "")
        self.assertEqual(roundup.plant_key("Sunrise Ridge Solar (SRS)"), "sunrise ridge solar")
        self.assertIsNone(roundup.planned_plant(dict(STORY, titles=["A solar project in Kalmar"]), "Kalmar solar project", index(PLAIN, ONE)))

    def test_a_plant_of_two_generators_is_summed(self):
        p = roundup.planned_plant(dict(STORY, titles=[]), "Sunrise Ridge Solar reaches financing", index(TWO_A, TWO_B))
        self.assertEqual((p["mw"], p["dates"]), (150.5, ["2027-03-01", "2027-06-01"]))
        self.assertTrue(roundup.plant_words(p).startswith("EIA-860M (September 2026) lists Sunrise Ridge Solar (SRS) at 150.5 MW "
                                                          "nameplate, planned for 2027-03-01 to 2027-06-01"))

    def test_a_name_two_plants_share_names_neither(self):
        twin = dict(REV, entity_id="eia860:9:X", plant_id="9")
        self.assertIsNone(roundup.planned_plant(STORY, HEAD, index(REV, twin)))

    def test_no_table_no_plant(self):
        self.assertEqual(roundup.plant_index(None), {})
        self.assertEqual(roundup.plant_index(pd.DataFrame([{"name": "Revolution Wind"}])), {})   # columns missing
        self.assertIsNone(roundup.planned_plant(STORY, HEAD, {}))


class Row64TheLimitation(unittest.TestCase):
    def test_without_the_table_the_line_is_as_before(self):
        self.assertEqual(roundup.evidence_gap(STORY, HEAD), OLD_GAP)
        self.assertEqual(roundup.evidence_gap(STORY, HEAD, None, None), OLD_GAP)

    def test_the_w45_line_after_the_fix(self):
        p = roundup.planned_plant(STORY, HEAD, index(REV))
        self.assertEqual(roundup.evidence_gap(STORY, HEAD, None, p), NEW_GAP)

    def test_the_same_figure_is_said_so(self):
        p = roundup.planned_plant(STORY, HEAD, index(dict(REV, nameplate_mw="704")))
        self.assertEqual(roundup.evidence_gap(STORY, HEAD, None, p),
                         "What the evidence does not establish: EIA-860M (September 2026) lists Revolution Wind at 704 MW "
                         "nameplate, planned for 2026-11-01, as the outlet reports; EIA has not yet listed the plant as operating.")

    def test_a_story_with_no_figure_is_given_the_table_s(self):
        r = dict(STORY, mw="", outlets=1)
        p = roundup.planned_plant(r, "Orsted completes Revolution Wind", index(REV))
        self.assertEqual(roundup.evidence_gap(r, "Orsted completes Revolution Wind", None, p),
                         "What the evidence does not establish: EIA-860M (September 2026) lists Revolution Wind at 715 MW "
                         "nameplate, planned for 2026-11-01; EIA has not yet listed the plant as operating; one outlet has "
                         "reported it so far.")

    def test_main_reads_the_table_and_passes_the_plant(self):
        with open(roundup.__file__, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("plant_ix = plant_index(read_table(\"eia860m_planned_generators\"))", src)
        self.assertIn("plants.get(r['cluster_id'])", src)
        self.assertIn("picked[\"capacity\"] = cap", src)
        self.assertIn("five = five_numbers(label, start, cut, facts, log, picked)", src)


class Row68TheCapacityStandIn(unittest.TestCase):
    def facts(self):
        def fuel(label, v1, v0):
            return {"label": label, "a": {"value": v1, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-11-03", tz=UTC)},
                    "b": {"value": v0, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-10-27", tz=UTC)}, "ref": "[5]"}
        return {"fuel": [fuel("Brent crude", 107.03, 123.10), fuel("WTI Cushing crude", 99.64, 103.37),
                         {"label": "Henry Hub natural gas", "a": {"value": 2.70, "unit": "USD/MMBtu", "ts_utc": pd.Timestamp("2026-11-03", tz=UTC)},
                          "b": {"value": 2.63, "unit": "USD/MMBtu", "ts_utc": pd.Timestamp("2026-10-27", tz=UTC)}, "ref": "[5]"}]}

    def five(self, capacity):
        dcs = pd.DataFrame([{"entity_id": "dc:x", "first_story_at": "2026-11-05T10:00:00Z", "capacity_mw": "702", "operator": "Google",
                             "site_name": "", "city": "Cheyenne", "state": "WY", "confidence": "0.55"}])
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(roundup, "read_table", lambda n: dcs if n == "datacenter_projects" else None), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            return roundup.five_numbers("2026-W45", START, CUT, self.facts(), lambda *a: None, {}, capacity)

    def test_without_a_plant_the_second_price_as_before(self):
        L = self.five(None)
        row = next(ln for ln in L if "datacenter load" in ln)
        self.assertIn("in its place, the week's next price move:", row)

    def test_the_capacity_line_comes_before_a_second_price(self):
        p = roundup.planned_plant(STORY, HEAD, index(REV))
        L = self.five({"plant": p, "rec": STORY})
        row = next(ln for ln in L if "datacenter load" in ln)
        self.assertEqual(row, "- **Largest new datacenter load first reported this week:** no facility first reported this week "
                              "with its MW passes the datacenter table's floor (1 under it); in its place, capacity: Revolution "
                              "Wind (offshore wind turbine, RI), named in the week's stories (POWER Magazine): EIA-860M "
                              "(September 2026) lists it at 715 MW nameplate, planned for 2026-11-01.")
        self.assertIn("the capacity, `eia860m_planned_generators` eia860:65500:REVWD", L[-1])
        self.assertNotIn("WTI Cushing crude closed", row)

    def test_the_capacity_line_is_used_once(self):
        p = roundup.planned_plant(STORY, HEAD, index(REV))
        L = self.five({"plant": p, "rec": STORY})   # no energy_deals: the deal row says so, no stand-in
        self.assertEqual(sum("in its place, capacity:" in ln for ln in L), 1)

    def test_the_checker_reads_no_load_from_the_stand_in(self):
        import check_roundup as cr
        p = roundup.planned_plant(STORY, HEAD, index(REV))
        text = "\n".join(self.five({"plant": p, "rec": STORY}))
        self.assertIsNone(cr.five_keyed(text)[2])


OLD_RT = ("**Highest real-time price of the week:** 302.71 USD/MWh at HB_SOUTH (ERCOT), interval starting 2026-11-03 17:45 local "
          "(2026-11-03 23:45 UTC), spp_rtm [4], ERCOT's real-time settlement point price, a 15-minute interval.")


class Row71TheRealTimeLine(unittest.TestCase):
    """The open part of row 71: the source id and "local" leave the line; the Tables line keeps the source ids."""

    def numbers(self, ts):
        def fetch(table, start=None, end=None, market=None, **k):
            if table == "iso_rtm_hub_prices":
                return pd.DataFrame({"ts_utc": [pd.Timestamp(ts, tz=UTC), pd.Timestamp("2026-11-05 05:45", tz=UTC)],
                                     "value": [302.71, 40.0], "node": ["HB_SOUTH", "HB_SOUTH"], "variable": ["spp_rtm", "spp_rtm"],
                                     "freq": ["PT15M", "PT15M"]})
            raise RuntimeError("not on this machine")
        with mock.patch.object(roundup, "dam_week", lambda *a: (None, 0, 168)), mock.patch.object(roundup.erw, "fetch", fetch), \
                mock.patch.object(brief, "held_grids", lambda *a: set()), mock.patch.object(brief, "paused_row", lambda *a: None), \
                mock.patch.object(brief, "rt_parts", lambda: [("ercot", "iso_rtm_hub_prices", "ercot_rtm")]), \
                mock.patch.object(brief, "cite_short", lambda t: f"`{t}`"):
            return roundup.numbers(START, CUT, lambda *a: None, {})

    def test_the_w45_line(self):
        L = self.numbers("2026-11-03 23:45")
        rt = next(ln for ln in L if ln.startswith("**Highest real-time price of the week:**"))
        self.assertTrue(rt.startswith("**Highest real-time price of the week:** 302.71 USD/MWh at HB_SOUTH (ERCOT), the 15-minute "
                                      "interval starting 2026-11-03 17:45 Central (23:45 UTC) [4], ERCOT's real-time settlement "
                                      "point price. The grids' real-time series differ in interval length"), rt)
        self.assertNotIn("spp_rtm", rt)
        self.assertNotIn(" local ", rt)
        tables = next(ln for ln in L if ln.startswith("Tables: "))
        self.assertIn("iso_rtm_hub_prices (ercot_rtm) to 2026-11-05 05:45 UTC", tables)
        self.assertIn("the week's highest real-time price is variable `spp_rtm`", tables)

    def test_the_utc_date_when_it_is_not_the_local_one(self):
        self.assertEqual(roundup.rt_when(pd.Timestamp("2026-11-04 01:00", tz=UTC), "America/Chicago"),
                         "2026-11-03 19:00 Central (2026-11-04 01:00 UTC)")
        self.assertEqual(roundup.rt_when(pd.Timestamp("2026-11-03 23:45", tz=UTC), "America/Chicago"), "2026-11-03 17:45 Central (23:45 UTC)")
        self.assertEqual(roundup.rt_when(pd.Timestamp("2026-07-03 23:45", tz=UTC), "America/Los_Angeles"), "2026-07-03 16:45 Pacific (23:45 UTC)")
        self.assertEqual(roundup.rt_when(pd.Timestamp("2026-11-03 23:45", tz=UTC), "UTC"), "2026-11-03 23:45 UTC")

    def test_the_checker_reads_the_new_line_and_the_old(self):
        import check_roundup as cr
        L = self.numbers("2026-11-04 01:00")
        self.assertEqual(cr.rt_line("\n".join(L)), ("302.71", "HB_SOUTH", "ERCOT", "2026-11-04 01:00", "spp_rtm", "4"))
        L = self.numbers("2026-11-03 23:45")
        self.assertEqual(cr.rt_line("\n".join(L)), ("302.71", "HB_SOUTH", "ERCOT", "2026-11-03 23:45", "spp_rtm", "4"))
        self.assertEqual(cr.rt_line(OLD_RT), ("302.71", "HB_SOUTH", "ERCOT", "2026-11-03 23:45", "spp_rtm", "4"))

    def test_the_checker_keys_the_new_line(self):
        import check_roundup as cr
        md = "# ERW Weekly Roundup, 2026-W45\n\n### ERW's Numbers This Week\n\n" + "\n".join(self.numbers("2026-11-03 23:45")) + "\n"
        keys = [k for k, _, _ in cr.checks("2026-W45", md)]
        self.assertIn("rdp_rt|iso_rtm_hub_prices|ercot:HB_SOUTH|spp_rtm|2026-11-03T23:45:00Z", keys)

    def test_the_site_checker_reads_both_forms(self):
        with open(os.path.join(ROOT, "site", "scripts", "check-values.mjs"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("highest real-time price is variable `?([a-z0-9_]+)", src)
        self.assertIn("m1 && v1 ? [m1[0], m1[1], m1[2], `${m1[5] ?? m1[3]} ${m1[6] ?? m1[4]}`, v1[1], foot[m1[7]]] : null", src)


if __name__ == "__main__":
    unittest.main()
