"""Session 169: Thesis Builder (warehouse/thesis), the owner's rulings of 8 October 2026.

Part B, the bug: "run.py:150-151 (words_of, [a-z][a-z-]{3,}) and :883 drop every word under four letters, so "oil"
and "gas" are never searched. Keep short domain words: oil, gas, ev, ai, lng, smr, ccs, dac, pv, h2, co2."

No network, no model call, no database. The tables a test reads are written by the test into a folder of its own
(every row there is made up for the test and says so); a machine without the warehouse's tables runs every test.
"""
import importlib.util
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LEDGER_BEFORE = []


def setUpModule():
    """The ledger is off while this module's tests run and is put back after them (never set at import)."""
    _LEDGER_BEFORE.append(os.environ.get("ERW_LEDGER"))
    os.environ["ERW_LEDGER"] = "0"


def tearDownModule():
    old = _LEDGER_BEFORE.pop()
    if old is None:
        os.environ.pop("ERW_LEDGER", None)
    else:
        os.environ["ERW_LEDGER"] = old


def load(name, *parts):
    """By path, under a name of its own: the suite already holds other modules named run, build and store."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *parts))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = load("erw_thesis_run", "warehouse", "thesis", "run.py")
tb = R.tb
SHORT = ["oil", "gas", "ev", "ai", "lng", "smr", "ccs", "dac", "pv", "h2", "co2"]
OLD = lambda text: [w for w in re.findall(r"[a-z][a-z-]{3,}", text.lower()) if w not in R.STOP]      # noqa: E731  words_of before session 169


class Quiet:
    def __init__(self):
        self.lines, self.erw, self.sources = [], [], {}

    def __call__(self, line):
        self.lines.append(line)


def write_table(folder, name, columns, rows):
    with open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8", newline="") as f:
        f.write("# made up for tests/test_session169.py: no row here is a real company, deal or policy action\n")
        f.write(",".join(columns) + "\n")
        for r in rows:
            f.write(",".join('"' + str(r.get(c, "")).replace('"', '""') + '"' for c in columns) + "\n")


class ShortWords(unittest.TestCase):
    """Part B: the short words of the domain are kept, each as a whole word; every longer word is read as before."""

    def test_the_owners_list_is_the_list(self):
        self.assertEqual(sorted(R.SHORT), sorted(SHORT))
        self.assertEqual(sorted(tb.SHORT), sorted(SHORT))

    def test_each_short_word_is_kept(self):
        for w in SHORT:
            self.assertEqual(R.words_of(f"{w.upper()} monitoring"), [w, "monitoring"], w)
            self.assertIn(w, R.words_of(f"sensors for {w}"), w)

    def test_oil_and_gas_are_searched(self):
        self.assertEqual(R.words_of("oil & gas demand"), ["oil", "gas", "demand"])
        self.assertEqual(R.words_of("Methane leak detection for oil and gas operators"), ["methane", "leak", "detection", "oil", "gas", "operators"])
        self.assertEqual(R.words_of("CO2 capture, DAC and CCS hubs; H2 for LNG; SMR sites; PV for EV; AI"),
                         ["co2", "capture", "dac", "ccs", "hubs", "h2", "lng", "smr", "sites", "pv", "ev", "ai"])

    def test_a_short_word_inside_another_word_is_not_a_word(self):
        self.assertEqual(R.words_of("soil boiling maintain development gasket evening"), ["soil", "boiling", "maintain", "development", "gasket", "evening"])
        self.assertEqual(R.words_of("h2o co2e pvc evs"), [])                 # neither a short domain word nor four letters
        self.assertEqual(R.words_of("an old cat sat"), [])                    # other short words stay out, as before

    def test_longer_words_are_read_as_before(self):
        for text in ("Geothermal mapping and sensing, US startups", "Grid-scale battery storage software for merchant operators",
                     "Subsurface heat mapping for geothermal", "long-duration storage for data centers", "closed-loop well technology"):
            self.assertEqual(R.words_of(text), OLD(text), text)
        text = "oil-field services and bio-gas upgrading"      # a hyphenated word is one word, as before
        self.assertEqual(R.words_of(text), OLD(text))

    def test_the_stop_words_still_stop(self):
        self.assertEqual(R.words_of("energy and power for the market"), [])

    def test_a_short_word_matches_a_text_as_a_whole_word_only(self):
        self.assertTrue(R.has_word("methane sensors for oil and gas wells", "oil"))
        self.assertTrue(R.has_word("methane sensors for oil and gas wells", "gas"))
        self.assertTrue(R.has_word("oil/gas (upstream)", "gas"))
        self.assertFalse(R.has_word("soil moisture sensing", "oil"))
        self.assertFalse(R.has_word("las vegas gasoline", "gas"))
        self.assertFalse(R.has_word("project development", "ev"))
        self.assertFalse(R.has_word("maintain the air", "ai"))
        self.assertTrue(R.has_word("geothermal mapping", "therm"))           # a long word anywhere, as before

    def test_the_policy_words_hold_the_short_words(self):
        drop = {"merchant", "operators", "software", "mapping", "sensing"}
        self.assertEqual(tb.policy_words("oil & gas demand", drop), ["demand", "oil", "gas"])
        self.assertEqual(tb.policy_words("Methane leak detection for oil and gas operators", drop), ["methane", "detection", "oil", "gas"])
        self.assertEqual(tb.policy_words("Geothermal mapping and sensing", drop), ["geothermal"])      # as before
        self.assertEqual(tb.policy_words("AI for EV fleets"), ["fleets", "ai", "ev"])
        self.assertEqual(tb.policy_words("gas, gas and gas"), ["gas"])
        self.assertEqual(tb.policy_words("soil and boilers"), ["boilers"])

    def test_the_run_reads_its_words_through_the_one_reader(self):
        with open(os.path.join(ROOT, "warehouse", "thesis", "run.py"), encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn('re.findall(r"[a-z]{5,}"', text)                    # line 883 as it was
        self.assertNotIn('re.findall(r"[a-z][a-z-]{3,}", text.lower())', text)      # lines 150 to 151 as they were


class ShortWordsAgainstTables(unittest.TestCase):
    """The two places the words are used: the warehouse's own candidates and the policy candidates."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.before = (R.TABLE_DIR, tb.TABLE_DIR)
        R.TABLE_DIR = tb.TABLE_DIR = self.dir.name
        write_table(self.dir.name, "energy_companies", ["name", "description", "niche_tags", "sector", "stage", "raised", "location", "founders", "website", "source_url"], [
            {"name": "Test Row One", "description": "Methane sensors for oil and gas wells", "sector": "oil and gas"},
            {"name": "Test Row Two", "description": "Soil moisture sensing for farms, boiling point", "sector": "agriculture"},
            {"name": "Test Row Three", "description": "Gas turbine inspection", "sector": "power"},
        ])
        write_table(self.dir.name, "energy_deals", ["event_id", "event_date", "deal_type", "parties", "asset", "technology", "state", "country", "dollars", "status", "source", "source_url"], [
            {"event_id": "test:1", "technology": "oil", "asset": "a test asset"},
            {"event_id": "test:2", "technology": "solar", "asset": "Las Vegas gasoline depot"},
        ])
        write_table(self.dir.name, "policy_actions", ["event_id", "agency", "action_type", "event_date", "title", "abstract", "sector_tags", "significance", "source_url"], [
            {"event_id": "test:p1", "title": "A test rule on gas flaring", "significance": "3"},
            {"event_id": "test:p2", "title": "A test rule on soil carbon and gasoline", "significance": "9"},
            {"event_id": "test:p3", "title": "A test order on EV charging", "abstract": "development of chargers", "significance": "5"},
            {"event_id": "test:p4", "title": "A test notice on project development", "significance": "8"},
        ])

    def tearDown(self):
        R.TABLE_DIR, tb.TABLE_DIR = self.before
        self.dir.cleanup()

    def test_the_warehouse_candidates_of_an_oil_and_gas_niche(self):
        r = Quiet()
        rows = R.warehouse_candidates("oil and gas", r, r)
        names = [row.get("name") or row.get("event_id") for _, _, row in rows]
        self.assertEqual(names, ["Test Row One", "test:1"])                  # "oil" as a whole word; not "soil", not "boiling"
        self.assertEqual(R.words_of(R.head_of("oil and gas")), ["oil", "gas"])

    def test_before_the_fix_the_niche_had_no_word_at_all(self):
        self.assertEqual(OLD(R.head_of("oil and gas")), [])                  # so warehouse_candidates returned [] at once
        self.assertEqual(OLD(R.head_of("oil & gas demand")), ["demand"])

    def test_gas_alone(self):
        r = Quiet()
        rows = R.warehouse_candidates("gas, US startups", r, r)
        self.assertEqual([row.get("name") or row.get("event_id") for _, _, row in rows], ["Test Row One", "Test Row Three"])

    def test_the_policy_candidates_match_whole_short_words(self):
        got = lambda words: sorted(tb.policy_candidates(words)["event_id"])      # noqa: E731
        self.assertEqual(got(tb.policy_words("oil & gas")), ["test:p1"])     # not "gasoline", not "soil"
        self.assertEqual(got(tb.policy_words("EV charging")), ["test:p3"])   # "ev" is not in "development"; "charging" is a long word
        self.assertEqual(got(["EV"]), ["test:p3"])
        self.assertEqual(got(["develop"]), ["test:p3", "test:p4"])           # a long word anywhere, as before


if __name__ == "__main__":
    unittest.main()
