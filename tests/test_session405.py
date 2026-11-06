"""Session 405 (the chain of 20 October 2026, afternoon): the interconnection explorer, /explore/interconnection, the
third signature explorer (platform tool 5), in review. The six ISO queues by entry year and status from
iso_queue_statistics as it stands, on session 403's shared frame; the fault of the table's first build said in one line
from its header; the held queues (NYISO, MISO, ISO-NE from 21 October 2026) held as the map's Queues tab holds them;
every figure a Num with a check key, and the header's count read by check-values. Energy Research Warehouse (ERW)."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
DASH = chr(0x2014)
PAGE = ("site", "app", "explore", "interconnection", "page.tsx")
LIB = ("site", "lib", "explore", "interconnection.ts")


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node_eval(code):
    """Run a module snippet with node from site/ (node strips the types of a .ts file that imports nothing)."""
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node is not on the path")
    out = subprocess.run([node, "--no-warnings", "--input-type=module", "-e", code], cwd=SITE, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(out.stderr[-2000:])
    return json.loads(out.stdout)


class ThePage(unittest.TestCase):
    def setUp(self):
        self.p = src(*PAGE)

    def test_it_is_in_review_and_not_in_the_menu(self):
        self.assertIn('"/explore/interconnection": "review",', src("site", "lib", "release.ts"))
        self.assertNotIn("/explore/", src("site", "lib", "pages.ts"))

    def test_it_stands_on_the_shared_frame_and_charts(self):
        p = self.p
        self.assertIn('import { ExploreFrame, FilterForm, Freshness } from "@/components/explore/Explore";', p)
        self.assertIn('import { SeriesChart } from "@/components/tool/SeriesChart";', p)
        self.assertIn('import { LineChart, type Line } from "@/components/LineChart";', p)
        for i in re.findall(r'from "([^"]+)"', p):
            self.assertFalse(i.startswith("./") or "echarts" in i, i)
        self.assertNotIn("<svg", p)
        self.assertIn('method={{ href: METHOD, label: "Energy projects, Queue statistics" }}', p)
        self.assertIn("tables={[TABLE]}", p)

    def test_every_figure_is_a_row_of_the_table_with_its_key(self):
        p = self.p
        self.assertIn("const key = (q: string, y: number, v: string) => `series|${TABLE}|${entityOf(q, y)}|${v}|${isoKey(yearTs(y))}`;", p)
        self.assertEqual(p.count("<Num "), 2)       # the row writer N, and the header's one count
        self.assertIn("<Num check={key(q, y, v)} raw={x} source={sourceWords(q, y, v)}>{shown(x)}</Num>", p)  # session 2202: the source words in the hover
        self.assertIn("<Num check={headerKey(iso, UNDATED, name)} raw={undated} source={`${TABLE}: the header line", p)  # session 2202: the header count names its header line
        self.assertEqual(set(re.findall(r'table_name: `eq\.\$\{(\w+)\}`', p)), {"TABLE"})
        self.assertIn('export const TABLE = "iso_queue_statistics";', src(*LIB))
        # no sum: the page adds no figure up (the parts of a bar are the table's own rows)
        self.assertNotIn(".reduce(", p)

    def test_the_held_queues_are_held_as_on_the_map(self):
        p = self.p
        self.assertIn("const held = licenseHeldGrid(iso);", p)
        self.assertIn("held ? Promise.resolve(null) : attempt(", p)               # a held queue is not read
        self.assertIn("const others = QUEUES.filter(([k]) => !licenseHeldGrid(k));", p)
        self.assertIn("data-license-held={TABLE}", p)
        self.assertIn("{name}&apos;s queue is held: {LICENSE_NEEDED}. Its figures are not shown;", p)
        self.assertIn("data-license-held={QUEUE_TABLE}", src("site", "app", "map", "QueuesView.tsx"))

    def test_the_fault_is_one_line_from_the_header_never_a_corrected_figure(self):
        p = self.p
        self.assertIn(") : faultyBuild(head) ? (", p)
        self.assertIn("data-queue-fault=", p)
        self.assertIn("corrects none", p)
        for n in ("450", "169", "104", "94 ", "456"):           # the method note's counts are not written into the page
            self.assertNotIn(n, p)
        self.assertIn('export const FIXED_AT = "2026-10-20T19:45:54Z";', src(*LIB))

    def test_a_value_the_table_does_not_hold_falls_back_and_is_said(self):
        p = self.p
        self.assertIn('const [iso, badIso] = choose(sp, "queue", QUEUES.map(([k]) => k), QUEUES[0][0]);', p)
        self.assertIn("data-asked-unknown", p)

    def test_no_em_dash_in_what_this_session_wrote(self):
        for parts in (PAGE, LIB, ("tests", "test_session405.py"), ("docs", "methods", "energy_projects.md")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


HEADER = [
    "Positions with no queue date, counted in no year: ERCOT 456, CAISO 169, NYISO 104, MISO 36, SPP 64, ISO-NE 94",
    "Inputs read: ercot_interconnection_queue (1758 rows; retrieved 20261019T203101Z; as of run x); "
    "nyiso_interconnection_queue (1814 rows; retrieved 20260926T000645Z; as of run y)",
    "Retrieved: 20261020T093659Z (UTC) by warehouse/derived/iso_queue_statistics.py",
]


class TheHelpers(unittest.TestCase):
    def test_the_header_is_read_as_it_is_written(self):
        r = node_eval(
            'const m = await import("./lib/explore/interconnection.ts");'
            f'const h = {json.dumps(HEADER)};'
            'console.log(JSON.stringify([m.builtAt(h), m.faultyBuild(h), m.faultyBuild(["Retrieved: 20261022T010000Z (UTC) by x"]), m.faultyBuild([]),'
            ' m.inputRetrieved(h, "ercot"), m.inputRetrieved(h, "nyiso"), m.inputRetrieved(h, "spp"),'
            ' m.headerCount(h, m.UNDATED, "ISO-NE"), m.headerCount(h, m.UNDATED, "ERCOT"), m.headerCount(h, m.UNDATED, "PJM"),'
            ' m.headerKey("isone", m.UNDATED, "ISO-NE"), m.yearOf("ercot:queue_2019"), m.yearOf("ercot:x"),'
            ' m.partialYear(2026, "2026-10-19T20:31:01Z"), m.partialYear(2025, "2026-10-19T20:31:01Z"),'
            ' m.valueOf([{entity: "spp:queue_2024", variable: "positions_waiting", ts_utc: "2024-01-01T00:00:00+00:00", value: 61}], "spp", 2024, "positions_waiting")]))')
        self.assertEqual(r, ["2026-10-20T09:36:59Z", True, False, True, "2026-10-19T20:31:01Z", "2026-09-26T00:06:45Z", None,
                             94, 456, None, "series_hdr|iso_queue_statistics|iso:isone|Positions with no queue date|ISO-NE",
                             2019, None, True, False, 61])

    def test_the_four_statuses_are_the_tables_variables(self):
        lib = src(*LIB)
        for k in ("operating", "withdrawn", "waiting", "status_not_stated"):
            self.assertIn(f'key: "{k}"', lib)
        gen = src("warehouse", "derived", "queue_statistics.py")
        self.assertIn('groups = {"entered": pd.Series(True, index=s.index), "operating": s == "completed", "waiting": s.isin(["active", "suspended"]),', gen)
        self.assertIn('"status_not_stated": s == ""}', gen)


class TheChecks(unittest.TestCase):
    def test_check_values_reads_the_views_and_the_header_count(self):
        cv = src("site", "scripts", "check-values.mjs")
        for page in ('"/explore/interconnection"', '"/explore/interconnection?queue=ercot&measure=mw&from=2018&to=2025"',
                     '"/explore/interconnection?queue=spp"', '"/explore/interconnection?queue=nyiso"'):
            self.assertIn(page, cv)
        self.assertIn('if (p[0] === "series_hdr") {', cv)
        self.assertIn('"/explore/interconnection", "/explore/interconnection?queue=ercot&measure=mw", "/explore/interconnection?queue=isone",',
                      src("site", "scripts", "check-routes.mjs"))

    def test_a_held_grids_header_count_is_held_by_num(self):
        # components/Num.tsx reads a key whose head begins "series" as naming its table in the second part, and the grid
        # from an entity among the parts: series_hdr|iso_queue_statistics|iso:isone|... is held as ISO-NE's rows are
        num = src("site", "components", "Num.tsx")
        self.assertIn('if (head.startsWith("series")) table = p[1] ?? "";', num)
        self.assertIn('const entity = p.slice(1).find((x) => gridOfEntity(x) !== "")', num)

    def test_the_method_note_says_what_the_explorer_draws(self):
        m = src("docs", "methods", "energy_projects.md")
        self.assertIn("### The explorer (session 405, 21 October 2026)", m)
        self.assertIn("`/explore/interconnection`", m)


if __name__ == "__main__":
    unittest.main()
