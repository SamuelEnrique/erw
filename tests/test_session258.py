"""Session 258: a finding card's source line names only the tables whose rows the finding uses (session 252's ruling 6).

The rule is decided from what the finding read (findings_common.record_reads), on small made-up tables written to a
temporary folder (test inputs, never data): an ERCOT draft names no table without ERCOT rows in the draft, a table that
does bring its rows is never dropped, a finding of several grids still names all of its tables, the stored drafts are
rewritten with nothing but the source line changed, and every card file in git obeys the rule as far as a machine
without the warehouse's tables can check it. No network, no model, no warehouse table. The environment is not set here.
"""
import base64
import glob
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIND = os.path.join(ROOT, "warehouse", "analysis", "findings")
sys.path.insert(0, FIND)
import findings_common as common  # noqa: E402
import hunt  # noqa: E402
import negative_prices_west as npw  # noqa: E402
import run_finding  # noqa: E402

EM = chr(0x2014)
NEG = next(p for p in hunt.PATTERNS if p["name"] == "negative_prices")
YEARS = [str(y) for y in range(2019, 2026)]
SHARED = ("iso_rtm_hub_prices", "iso_hub_prices_history", "iso_zone_prices_history")   # 'license needed' from 21 October for other grids' rows


def write_table(d, name, header, rows):
    with open(os.path.join(d, name + ".csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# a made-up table of a test (session 258), never data\n" + header + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")


def tables(d, history_ends=2026, live_from=(2026, 8)):
    """The three tables negative_prices_west reads, a few hours a year. ERCOT's history holds 2019 to August of
    history_ends; the live table holds ERCOT and SPP from live_from on (August twice: once in each table) and another
    grid's rows; the hub history holds SPP from 2019 and another grid's rows."""
    hist, live, hubs = [], [], []
    for y in range(2018, history_ends + 1):
        for m in range(1, 13):
            if y == history_ends and m > 8:
                break
            for hub in ("HB_WEST", "HB_HOUSTON", "HB_NORTH", "HB_SOUTH"):
                for hr in (10, 11, 12, 13):
                    v = -5.0 if (y >= 2022 and hr == 12 and m <= y - 2019) else 20.0 + hr
                    hist.append((f"{y}-{m:02d}-15T{hr}:00:00Z", v, "ercot_rtm", hub, y))
    y0, m0 = live_from
    for y in range(y0, 2027):
        for m in range(m0 if y == y0 else 1, 11 if y == 2026 else 13):
            for hr in (10, 11, 12, 13):
                for hub in ("HB_WEST", "HB_HOUSTON", "HB_NORTH", "HB_SOUTH"):
                    live.append((f"{y}-{m:02d}-15T{hr}:00:00Z", 30.0, "ercot_rtm", hub))
                live.append((f"{y}-{m:02d}-15T{hr}:00:00Z", 12.0, "spp_rtm", "SPPNORTH_HUB"))
                live.append((f"{y}-{m:02d}-15T{hr}:00:00Z", 44.0, "miso_rtm", "INDIANA.HUB"))
    for y in range(2019, 2027):
        for m in range(1, 9 if y == 2026 else 13):
            for hr in (10, 11, 12, 13):
                hubs.append((f"{y}-{m:02d}-15T{hr}:00:00Z", -2.0 if (hr == 11 and m <= y - 2018) else 15.0, "spp_rtm", "SPPNORTH_HUB"))
                hubs.append((f"{y}-{m:02d}-15T{hr}:00:00Z", 50.0, "isone_rtm", ".H.INTERNAL_HUB"))
    write_table(d, "ercot_all_hub_prices_history", "ts_utc,value,market,node,year", hist)
    write_table(d, "iso_rtm_hub_prices", "ts_utc,value,market,node", live)
    write_table(d, "iso_hub_prices_history", "ts_utc,value,market,node", hubs)


def reads_of(d):
    with common.record_reads() as reads:
        rows, meta = npw.compute({"first_year": 2019, "threshold": 0.0}, d)
    return reads, rows


class TheRecordOfWhatAFindingRead(unittest.TestCase):
    def test_nothing_is_recorded_until_a_caller_asks_and_the_rows_are_the_same(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            self.assertIsNone(common.READS)
            plain, _ = npw.compute({"first_year": 2019, "threshold": 0.0}, d)
            self.assertIsNone(common.READS)
            reads, rows = reads_of(d)
            self.assertIsNone(common.READS)
            self.assertEqual(json.dumps(plain, sort_keys=True), json.dumps(rows, sort_keys=True))
            self.assertEqual({r["table"] for r in reads}, set(npw.TABLES))
            self.assertTrue(all(r["rows"] > 0 and r["groups"] for r in reads))
            self.assertEqual({k[0] for r in reads for k in r["groups"]}, {"ercot_rtm", "spp_rtm"})   # the finding kept no other grid's row

    def test_a_table_without_a_market_has_no_groups(self):
        with tempfile.TemporaryDirectory() as d:
            write_table(d, "eia_fuel_spot_prices", "entity,variable,ts_utc,value", [("eia:henry_hub", "spot_price", "2024-01-02T00:00:00Z", 2.5)])
            with common.record_reads() as reads:
                common.read_table("eia_fuel_spot_prices", d)
            self.assertEqual(reads, [{"table": "eia_fuel_spot_prices", "rows": 1, "groups": None}])


class AnErcotDraftNamesOnlyErcotsTables(unittest.TestCase):
    def test_no_table_without_ercot_rows_in_the_draft_is_named(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            reads, _ = reads_of(d)
            u = hunt.tables_used(reads, "ercot_north", YEARS, YEARS + ["2026"], NEG)
            self.assertEqual(u["tables"], ["ercot_all_hub_prices_history"])
            self.assertEqual(u["other_years"], ["iso_rtm_hub_prices"])       # the year under way, after the history ends
            self.assertEqual(u["helpers"], [])
            line = hunt.source_line_of(NEG, "ercot_north", u["tables"], u["helpers"])
            self.assertEqual(line, "Source: ERCOT's rows of the ERW table ercot_all_hub_prices_history; computed by the finding negative_prices_west (warehouse/analysis/findings/).")
            for t in SHARED:
                self.assertNotIn(t, line)
            # the rule of session 233 let the shared tables through: this is the fault session 252 found
            self.assertEqual(hunt.region_tables(list(npw.TABLES), "ercot_north"), list(npw.TABLES))

    def test_a_table_that_brings_the_claims_rows_is_never_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d, history_ends=2024, live_from=(2024, 8))                # the live table holds ERCOT's 2025
            reads, _ = reads_of(d)
            u = hunt.tables_used(reads, "ercot_north", YEARS, YEARS + ["2026"], NEG)
            self.assertEqual(u["tables"], ["ercot_all_hub_prices_history", "iso_rtm_hub_prices"])
            self.assertEqual(u["other_years"], [])
            self.assertIn("the ERW tables ercot_all_hub_prices_history, iso_rtm_hub_prices;", hunt.source_line_of(NEG, "ercot_north", u["tables"]))

    def test_the_first_hours_of_a_utc_year_are_also_the_year_before(self):
        self.assertEqual(hunt._local_years("2026-01-01T05:45:00Z"), ("2026", "2025"))
        self.assertEqual(hunt._local_years("2026-01-01T12:00:00Z"), ("2026",))
        reads = [{"table": "a_history", "rows": 1, "groups": {("ercot_rtm", "X"): {"2024-06-01T00:00:00Z"}}},
                 {"table": "a_live", "rows": 1, "groups": {("ercot_rtm", "X"): {"2026-01-01T03:00:00Z"}}}]
        self.assertEqual(hunt.tables_used(reads, "ercot", ["2024", "2025"])["tables"], ["a_history", "a_live"])

    def test_a_measure_names_the_table_it_needs_beside_the_prices_only_when_it_was_read(self):
        gas = next(p for p in hunt.PATTERNS if p["name"] == "gas_sets_price")
        self.assertEqual(gas["measure_tables"], ["eia_fuel_spot_prices"])
        for p in hunt.PATTERNS:
            if p.get("fn"):                              # session 251: a measure of hunt_measures.py has no finding module and names its own tables
                self.assertNotIn("measure_tables", p, p["name"])
                continue
            self.assertLessEqual(set(p.get("measure_tables", [])), set(run_finding.load(p["module"]).TABLES), p["name"])
        reads = [{"table": "ercot_all_hub_prices_history", "rows": 2, "groups": {("ercot_rtm", "HB_HUBAVG"): {"2019-06-01T00:00:00Z", "2025-06-01T00:00:00Z"}}},
                 {"table": "iso_rtm_hub_prices", "rows": 1, "groups": {("caiso_rtm", "TH_SP15_GEN-APND"): {"2025-06-01T00:00:00Z"}}},
                 {"table": "eia_fuel_spot_prices", "rows": 9, "groups": None}, {"table": "storage_buildout_monthly", "rows": 9, "groups": None}]
        u = hunt.tables_used(reads, "ercot", YEARS, YEARS, gas)
        self.assertEqual((u["tables"], u["helpers"], u["other_years"]), (["ercot_all_hub_prices_history"], ["eia_fuel_spot_prices"], []))
        line = hunt.source_line_of(gas, "ercot", u["tables"], u["helpers"])
        self.assertIn("ERCOT's rows of the ERW table ercot_all_hub_prices_history, with the ERW table eia_fuel_spot_prices;", line)
        self.assertNotIn("iso_rtm_hub_prices", line)
        self.assertNotIn("storage_buildout_monthly", line)
        self.assertEqual(hunt.tables_used(reads[:2], "ercot", YEARS, YEARS, gas)["helpers"], [])


class AFindingOfSeveralGridsNamesAllOfItsTables(unittest.TestCase):
    def test_each_grid_names_its_own_and_together_they_name_every_table(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            reads, _ = reads_of(d)
            spp = hunt.tables_used(reads, "spp_north", YEARS, YEARS + ["2026"], NEG)
            self.assertEqual(spp["tables"], ["iso_hub_prices_history"])
            self.assertEqual(spp["other_years"], ["iso_rtm_hub_prices"])
            ercot = hunt.tables_used(reads, "ercot_west", YEARS, YEARS + ["2026"], NEG)
            self.assertEqual(set(ercot["tables"] + ercot["other_years"] + spp["tables"] + spp["other_years"]), set(npw.TABLES))

    def test_a_full_card_keeps_every_table_that_brought_rows(self):
        with tempfile.TemporaryDirectory() as d:
            tables(d)
            reads, rows = reads_of(d)
            card = {"tables": list(npw.TABLES), "source_line": "Source: ERCOT; SPP RTBM; ERW tables " + ", ".join(npw.TABLES) + ".",
                    "csv_header": ["Sources: " + ", ".join(npw.TABLES)]}
            same, left = common.only_tables_read(card, reads)
            self.assertEqual((same, left), (card, []))
            self.assertEqual(same["source_line"].count(","), len(npw.TABLES) - 1)

    def test_a_full_card_leaves_out_a_table_it_kept_no_row_of_and_says_nothing_of_a_table_it_cannot_see(self):
        card = {"tables": ["a", "b"], "source_line": "Source: X; ERW tables a, b.", "csv_header": ["Sources: a, b"]}
        reads = [{"table": "a", "rows": 5, "groups": None}, {"table": "b", "rows": 0, "groups": {}}]
        fixed, left = common.only_tables_read(card, reads)
        self.assertEqual((fixed["tables"], fixed["source_line"], fixed["csv_header"], left), (["a"], "Source: X; ERW tables a.", ["Sources: a"], ["b"]))
        self.assertEqual(card["tables"], ["a", "b"])                           # the caller's card is not changed in place
        self.assertEqual(common.only_tables_read(card, reads[:1]), (card, []))  # b was read by another reader: nothing is said
        self.assertEqual(common.only_tables_read(card, [dict(reads[0], rows=0), reads[1]]), (card, []))   # never an empty line

    def test_the_builder_of_a_full_card_applies_it(self):
        with open(os.path.join(FIND, "run_finding.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("with common.record_reads() as reads:", s)
        self.assertIn("card, left_out = common.only_tables_read(card, reads)", s)


def hunted(d, out):
    """The hunt's own run of the pattern on the made-up tables, and its draft for ERCOT North."""
    got = hunt.run_pattern(NEG, d, 2026, set(), log=lambda m: None)
    region, words, series, claim, reason, card, module_tables, used = next(g for g in got if g[0] == "ercot_north")
    return hunt.build_draft(NEG, region, words, series, claim, "new: this pattern had not been drafted for this region", card, module_tables, out, used), series, claim, used, module_tables


class TheHuntsDraft(unittest.TestCase):
    def test_the_card_the_caption_and_the_csv_name_only_what_the_draft_rests_on(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            tables(d)
            row, series, claim, used, module_tables = hunted(d, out)
            self.assertEqual(module_tables, list(npw.TABLES))
            self.assertEqual((claim["first_year"], claim["last_year"]), ("2019", "2025"))
            self.assertIn("2026", series)                                       # the year under way is in the file, not in the claim
            card = row["card"]
            self.assertEqual(card["tables"], ["ercot_all_hub_prices_history"])
            self.assertEqual(row["table_name"], "ercot_all_hub_prices_history")
            self.assertTrue(card["source_line"].endswith(" Found by the weekly hunt."))
            for text in (card["source_line"], card["hunt"]["caption"], row["files"][card["hunt"]["files"][5]]["content"]):
                self.assertIn("Source: ERCOT's rows of the ERW table ercot_all_hub_prices_history; computed by the finding negative_prices_west", text)
                for t in SHARED:
                    self.assertNotIn(t, text)
            csv_lines = row["files"][card["hunt"]["files"][0]]["content"].split("\n")
            self.assertEqual(csv_lines[3], "# Sources: ercot_all_hub_prices_history; the rows with full_year 0 also read ERCOT's rows of iso_rtm_hub_prices")
            self.assertEqual(csv_lines[4], "region,year,value,n_observations,full_year")   # the do-file reads names from line five
            self.assertNotIn("iso_hub_prices_history", "\n".join(csv_lines))
            self.assertNotIn(EM, json.dumps(row, ensure_ascii=False))

    def test_a_draft_built_without_the_reads_keeps_session_233s_rule(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            tables(d)
            _, series, claim, _, _ = hunted(d, out)
            with mock.patch.dict(hunt.OWN_TABLES, {}, clear=True):               # a module without a list: the tables by their names
                row = hunt.build_draft(NEG, "ercot_north", "ERCOT North", series, claim, "new", {}, ["ercot_all_hub_prices_history", "nyiso_rtm_zone_prices"], out)
                self.assertEqual(row["card"]["tables"], ["ercot_all_hub_prices_history"])
                row = hunt.build_draft(NEG, "ercot_north", "ERCOT North", series, claim, "new", {}, list(npw.TABLES), out, {"tables": []})
                self.assertEqual(row["card"]["tables"], list(npw.TABLES))        # no reads known: never an empty line
            # session 251 landed while this session ran: without the reads, a finding's draft names its module's own tables
            # for the grid (hunt.OWN_TABLES), whatever list it is handed. With the reads, tables_used decides (the test above)
            own = hunt.OWN_TABLES["negative_prices_west"]["ercot"]
            row = hunt.build_draft(NEG, "ercot_north", "ERCOT North", series, claim, "new", {}, list(npw.TABLES), out)
            self.assertEqual(row["card"]["tables"], list(own))
            self.assertIn("ercot_all_hub_prices_history", own)
            for t in ("iso_hub_prices_history", "iso_zone_prices_history"):
                self.assertNotIn(t, row["card"]["source_line"])

    def test_the_hunt_takes_a_pattern_run_with_or_without_the_reads(self):
        with open(os.path.join(FIND, "hunt.py"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("for region, words, series, claim, reason, card, tables, *more in got:", s)
        self.assertIn("d = build_draft(P, region, words, series, claim, why, card, tables, out_dir, used)", s)


def stored(row):
    """A draft as the review list holds it (JSON), drawn the way session 233 drew it: every table of the module."""
    return json.loads(json.dumps({"id": row["id"], "state": "draft", "table_name": row["table_name"], "flag": row["flag"], "card": row["card"],
                                  "files": row["files"]}, default=common.round6))


class TheStoredDraftsAreRewritten(unittest.TestCase):
    def old_row(self, d, out):
        _, series, claim, used, module_tables = hunted(d, out)
        with mock.patch.dict(hunt.OWN_TABLES, {}, clear=True):   # as the builder stood when the eight drafts were raised, before session 251's list
            old = hunt.build_draft(NEG, "ercot_north", "ERCOT North", series, claim, "new: this pattern had not been drafted for this region", {}, module_tables, out)
        self.assertIn("ercot_all_hub_prices_history, iso_rtm_hub_prices, iso_hub_prices_history;", old["card"]["source_line"])   # the fault
        return stored(old), used

    def test_only_the_source_line_changes_and_a_second_pass_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            tables(d)
            row, used = self.old_row(d, out)
            body, old, new = hunt.rewrite_draft(row, used, os.path.join(out, "again"))
            self.assertIn("iso_hub_prices_history", old)
            self.assertEqual(new, "Source: ERCOT's rows of the ERW table ercot_all_hub_prices_history; computed by the finding negative_prices_west (warehouse/analysis/findings/).")
            self.assertEqual(sorted(body), ["card", "files", "table_name"])
            card, names = body["card"], row["card"]["hunt"]["files"]
            self.assertEqual(card["source_line"], new + " Found by the weekly hunt.")
            self.assertEqual(card["tables"], ["ercot_all_hub_prices_history"])
            for k in ("numbers", "chart", "callouts", "subtitle", "title", "footnote", "scanner", "params", "computed_at", "card_id"):
                self.assertEqual(card[k], row["card"][k], k)
            self.assertEqual({k: v for k, v in card["hunt"].items() if k != "caption"}, {k: v for k, v in row["card"]["hunt"].items() if k != "caption"})
            self.assertEqual(card["hunt"]["caption"], row["card"]["hunt"]["caption"].replace(old, new))
            self.assertEqual(body["files"][names[5]]["content"], card["hunt"]["caption"] + "\n")
            was, now = row["files"][names[0]]["content"].split("\n"), body["files"][names[0]]["content"].split("\n")
            self.assertEqual([i for i, (a, b) in enumerate(zip(was, now)) if a != b], [3])          # the "# Sources:" line and no other
            self.assertEqual(len(was), len(now))
            for n in (names[1], names[2]):
                self.assertEqual(body["files"][n], row["files"][n])                                  # the do-file and the Python mirror
            for n in (names[3], names[4]):
                self.assertEqual(base64.b64decode(body["files"][n]["content"])[:8], b"\x89PNG\r\n\x1a\n")
            again = dict(row, card=body["card"], files=body["files"], table_name=body["table_name"])
            self.assertEqual(hunt.rewrite_draft(again, used, os.path.join(out, "again"))[0], None)

    def test_a_draft_whose_line_is_not_where_the_hunt_writes_it_is_refused(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            tables(d)
            row, used = self.old_row(d, out)
            row["card"]["hunt"]["caption"] = "edited by a person"
            with self.assertRaises(ValueError):
                hunt.rewrite_draft(row, used, out)
            with self.assertRaises(ValueError):
                hunt.rewrite_draft(row, {"tables": []}, out)

    def test_the_command_reads_the_list_runs_each_finding_once_and_writes_only_without_dry_run(self):
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock

        class Reply:
            def __init__(self, body=None):
                self.body = body

            def raise_for_status(self):
                return None

            def json(self):
                return self.body

        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            tables(d)
            row, _ = self.old_row(d, out)
            asked, sent, runs = [], [], []

            def get(url, params=None, headers=None, timeout=None):
                asked.append((url, params))
                return Reply([row, dict(row, id=row["id"] + "b")])

            def patch(url, params=None, data=None, headers=None, timeout=None):
                sent.append((url, params, json.loads(data)))
                return Reply()

            def compute(params, in_dir):
                runs.append(params)
                return npw.compute(params, in_dir)

            with mock.patch.object(lock, "env", create=True, new=lambda k: {"SUPABASE_URL": "https://example.invalid/rest/v1/", "SUPABASE_SERVICE_KEY": "not-a-key"}.get(k)):
                dry = hunt.fix_source_lines(d, dry_run=True, log=lambda m: None, get=get, patch=patch, compute=compute, out_dir=os.path.join(out, "p"))
                self.assertEqual((len(dry), [o["changed"] for o in dry], [o["written"] for o in dry], sent), (2, [True, True], [False, False], []))
                self.assertEqual(len(runs), 1)                                   # two drafts of one finding: it is run once
                done = hunt.fix_source_lines(d, dry_run=False, log=lambda m: None, get=get, patch=patch, compute=compute, out_dir=os.path.join(out, "p"))
            self.assertEqual(asked[0], ("https://example.invalid/rest/v1/scanner_drafts", {"rule": "eq.hunt", "select": "id,state,table_name,flag,card,files", "order": "id"}))
            self.assertEqual([o["written"] for o in done], [True, True])
            self.assertEqual([s[1] for s in sent], [{"id": f"eq.{row['id']}"}, {"id": f"eq.{row['id']}b"}])
            self.assertEqual(sorted(sent[0][2]), ["card", "files", "table_name"])
            for t in SHARED:
                self.assertNotIn(t, sent[0][2]["card"]["source_line"])

    def test_a_draft_of_a_measure_of_session_251_is_left_as_it_is(self):
        """Session 251 landed while this session ran: its twelve drafts are measures of hunt_measures.py, each built from
        its own region's tables. The command runs no finding for them, changes nothing and sends nothing."""
        sys.path.insert(0, os.path.join(ROOT, "warehouse"))
        import lock
        fam = next(p for p in hunt.PATTERNS if p.get("fn"))
        row = {"id": "scan-hunt-000000000000", "state": "draft", "table_name": "t", "flag": {}, "files": {},
               "card": {"source_line": "Source: the rows for CAISO of the ERW tables t; computed by the hunt's measure. Found by the weekly hunt.",
                        "hunt": {"pattern": fam["name"], "region": "caiso"}}}

        class Reply:
            def raise_for_status(self):
                return None

            def json(self):
                return [row]

        sent, runs = [], []
        with tempfile.TemporaryDirectory() as out, mock.patch.object(lock, "env", create=True, new=lambda k: {
                "SUPABASE_URL": "https://example.invalid/rest/v1/", "SUPABASE_SERVICE_KEY": "not-a-key"}.get(k)):
            got = hunt.fix_source_lines(out, dry_run=False, log=lambda m: None, get=lambda *a, **k: Reply(), patch=lambda *a, **k: sent.append(a),
                                        compute=lambda *a: runs.append(a), out_dir=os.path.join(out, "p"))
        self.assertEqual([(o["id"], o["changed"], o["written"], o["old"] == o["new"]) for o in got], [(row["id"], False, False, True)])
        self.assertEqual((sent, runs), ([], []))

    def test_the_command_is_on_the_command_line(self):
        r = subprocess.run([sys.executable, os.path.join(FIND, "hunt.py"), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("--fix-source-lines", r.stdout)


class EveryCardFileInGit(unittest.TestCase):
    """What can be checked without the warehouse's tables: a card in git names exactly the tables its finding's code
    reads (each one by a read in the finding's own files), in its source line and in its tables, and no card of one
    grid names a table that is another grid's by name. That each named table brought rows is checked where the tables
    are: run_finding leaves out a table it kept no row of (above)."""

    def cards(self):
        out = []
        for p in sorted(glob.glob(os.path.join(ROOT, "site", "data", "findings", "*.json"))):
            with open(p, encoding="utf-8") as f:
                c = json.load(f)
            # session 720: a card written outside the findings engine names its generator ("engine"; the All grids
            # tab's card, site/scripts/siting-card.mjs, from the tab's own functions) and is held to that script's checks
            if isinstance(c, dict) and "source_line" in c and not c.get("engine"):
                out.append((os.path.basename(p), c))
        return out

    def test_there_are_cards_and_each_names_its_modules_tables_and_reads_each(self):
        cards = self.cards()
        self.assertGreaterEqual(len(cards), 11)
        code = ""
        for p in glob.glob(os.path.join(FIND, "*.py")):
            with open(p, encoding="utf-8") as f:
                code += f.read()
        for name, c in cards:
            mod = run_finding.load(c["id"])
            if c["id"] != "impact_study":                                       # its tables are the two series a person picks
                self.assertLessEqual(set(c["tables"]), set(mod.TABLES), name)   # never a table its finding does not read
                self.assertTrue(c["tables"], name)
            for t in c["tables"]:
                self.assertIn(t, c["source_line"], f"{name}: {t} is in the card's tables and not in its source line")
                self.assertTrue(f'"{t}"' in code, f"{name}: no file of the findings reads {t}")
            self.assertNotIn(EM, c["source_line"])

    def test_a_card_of_one_grid_names_no_other_grids_table(self):
        one_grid = {"batteries_lunch": "ercot", "batteries_curtailment": "caiso", "batteries_curtailment_hourly": "caiso"}
        seen = 0
        for name, c in self.cards():
            if c["id"] in one_grid:
                seen += 1
                self.assertEqual(hunt.region_tables(c["tables"], one_grid[c["id"]]), c["tables"], name)
                for t in ("iso_hub_prices_history", "iso_zone_prices_history"):   # held for other grids' rows; no row of ERCOT's or CAISO's card
                    self.assertNotIn(t, c["source_line"], name)
        self.assertEqual(seen, 3)

    def test_no_hunt_draft_is_kept_as_a_file_in_git(self):
        r = subprocess.run(["git", "-C", ROOT, "grep", "-l", "Found by the weekly hunt"], capture_output=True, text=True)
        if r.returncode not in (0, 1):
            self.skipTest("not a git checkout")
        files = {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}
        # session 251's verification of its twelve drafts (measures of hunt_measures.py, each built from its own region's tables)
        # session 286: its verification of the hunt of 14 October and the motion proofs of its two strong drafts, each a
        # record of one day's drafts as they then stood
        allowed = ("warehouse/analysis/findings/hunt.py", "tests/", "docs/reviews/findings-verified-2026-10-13/verify_hunt.py", "archive/sessions/", "docs/methods/",
                   "docs/reviews/findings-verified-2026-10-13-session251/", "docs/reviews/findings-verified-2026-10-14-session286/",
                   "docs/research/motion/hunt-2026-10-14/")
        self.assertEqual({f for f in files if not f.startswith(allowed)}, set())


class TheWords(unittest.TestCase):
    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (("warehouse", "analysis", "findings", "hunt.py"), ("warehouse", "analysis", "findings", "findings_common.py"),
                      ("warehouse", "analysis", "findings", "run_finding.py"), ("tests", "test_session258.py"),
                      ("docs", "methods", "automated_analysis_findings.md"), ("archive", "sessions", "SESSION_258_REPORT.md")):
            p = os.path.join(ROOT, *parts)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    self.assertNotIn(EM, f.read(), p)

    def test_the_method_says_the_rule(self):
        with open(os.path.join(ROOT, "docs", "methods", "automated_analysis_findings.md"), encoding="utf-8") as f:
            s = f.read()
        self.assertIn("session 258", s)
        self.assertIn("tables_used", s)


if __name__ == "__main__":
    unittest.main()
