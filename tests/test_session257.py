"""Session 257: California on the battery page and the generator page, as sessions 246 and 253 listed it.

Energy Research Warehouse (ERW). What is held here:

  the battery page (site/lib/batterystack.ts, site/app/cost-of-power/battery): the stress events are read from the rows
    of the grid shown, ERCOT's three keep their names and CAISO's are labelled by their days; the sentence with the
    table's download is drawn for whichever grid holds events; beside CAISO's income the market monitor's real-fleet
    figures stand as a cited constant, equal to docs/methods/battery_stack.md, with the model's two figures computed
    from the table under check keys and typed nowhere;
  the generator page: the ten rows of section 12.5 that hold a gap are the last ten rows of the note's "Cross-checks",
    cell for cell, and the page counts 20; the peaker's rule, the stress events and the wind sentence were not touched;
  no page's status changed, and no em dash was written.

The rows the library is tried on here are toy rows, made for the test: no table is read and no request is made. The
environment is read, never set."""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)
WROTE = ["site/lib/batterystack.ts", "site/app/cost-of-power/battery/page.tsx", "site/app/cost-of-power/battery/read.ts", "site/app/cost-of-power/seller/page.tsx",
         "docs/methods/battery_stack.md", "docs/methods/battery_earns_algorithm.md", "docs/methods/generator_earns_algorithm.md", "docs/howitworks/generator.md", "docs/brand/review-257/README.md",
         "tests/test_session257.py", "archive/sessions/SESSION_257_REPORT.md"]


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def node(js):
    exe = shutil.which("node")
    if not exe:
        raise unittest.SkipTest("node is not on this machine")
    r = subprocess.run([exe, "--input-type=module", "-e", js], cwd=os.path.join(ROOT, "site"), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-2000:])
    return json.loads(r.stdout)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


class TheStressEventsAreReadFromTheRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = node("""
const B = await import("./lib/batterystack.ts");
const row = (event, day, stream, value, pre = "dayahead_4h") => ({ event, ts_utc: `${day}T00:00:00+00:00`, variable: `${pre}_revenue_${stream}_usd_per_mw`, value });
const day = (event, d, e, a, pre) => [row(event, d, "energy", e, pre), row(event, d, "ancillary", a, pre), row(event, d, "total", e + a, pre)];
const caiso = [...day("caiso_notices_20250120", "2025-01-21", 5, 6), ...day("caiso_notices_20250120", "2025-01-20", 10, 20),
  ...["04", "05", "06", "07", "08", "09"].flatMap((d, i) => day("caiso_notices_20240904", `2024-09-${d}`, 100 + i, 50)),
  ...day("caiso_notices_20260930", "2026-09-30", 1, 1), ...day("caiso_notices_20260930", "2026-10-01", 1, 1), ...day("caiso_notices_20260930", "2026-10-02", 1, 1),
  ...day("caiso_notices_20251231", "2025-12-31", 2, 2), ...day("caiso_notices_20251231", "2026-01-01", 2, 2),
  ...day("caiso_notices_20250715", "2025-07-15", 3, 3), ...day("caiso_notices_20240904", "2024-09-04", 999, 999, "foresight_4h")];
const ercot = [...day("elliott_2022", "2022-12-19", 1, 2), ...day("uri_2021", "2021-02-07", 3, 4), ...day("uri_2021", "2021-02-08", 30, 40), ...day("ercot_heat_2023", "2023-08-01", 5, 6)];
const x = B.inputsOf({ grid: "caiso", dur: "4", strat: "dayahead", mw: "250" });
console.log(JSON.stringify({
  caiso: B.stress(caiso, "dayahead", 4), ercot: B.stress(ercot, "dayahead", 4), none: B.stress([], "dayahead", 4), other: B.stress(caiso, "dayahead", 8),
  total: B.stat([], caiso, x, "stress:caiso_notices_20240904:total"), best: B.stat([], caiso, x, "stress:caiso_notices_20250120:best"),
  unknown: B.stat([], caiso, x, "stress:uri_2021:total"),
  labels: [B.daysLabel("2024-09-04", "2024-09-09", 6), B.daysLabel("2025-01-20", "2025-01-21", 2), B.daysLabel("2026-09-30", "2026-10-02", 3),
    B.daysLabel("2025-12-31", "2026-01-01", 2), B.daysLabel("2025-07-15", "2025-07-15", 1), B.daysLabel("2024-09-04T00:00:00+00:00", "2024-09-09T00:00:00+00:00", 4)],
  by: B.STRESS_BY, events: B.EVENTS, short: B.EVENT_SHORT,
}));
""")

    def test_californias_events_are_found_without_a_list_and_labelled_by_their_days(self):
        ev = self.got["caiso"]
        self.assertEqual([e["event"] for e in ev], ["caiso_notices_20240904", "caiso_notices_20250120", "caiso_notices_20250715", "caiso_notices_20251231", "caiso_notices_20260930"])   # by first day
        self.assertEqual([e["label"] for e in ev], ["4 to 9 September 2024", "20 and 21 January 2025", "15 July 2025", "31 December 2025 and 1 January 2026", "30 September to 2 October 2026"])
        for e in ev:
            self.assertEqual(e["short"], e["label"])                                     # an event made by the rule has no name: its days are its name
        first = ev[0]
        self.assertEqual((first["days"], first["first"], first["last"]), (6, "2024-09-04", "2024-09-09"))
        self.assertAlmostEqual(first["energy"], sum(100 + i for i in range(6)))          # the other strategy's row of the same day is not counted
        self.assertAlmostEqual(first["total"], sum(150 + i for i in range(6)))
        self.assertEqual(first["best"], {"day": "2024-09-09", "v": 155})
        self.assertEqual(ev[1]["best"], {"day": "2025-01-20", "v": 30})
        self.assertEqual(self.got["none"], [])
        self.assertEqual(self.got["other"], [])                                          # no row of the 8-hour battery was given

    def test_ercots_three_keep_their_names_and_their_order(self):
        ev = self.got["ercot"]
        self.assertEqual([e["event"] for e in ev], ["uri_2021", "elliott_2022", "ercot_heat_2023"])
        self.assertEqual([e["label"] for e in ev], ["Winter Storm Uri, February 2021", "Winter Storm Elliott, December 2022", "The summer 2023 heat"])
        self.assertEqual(", ".join(e["short"] for e in ev), "Uri, Elliott, the 2023 heat")           # the page's sentence, as it read before this session
        self.assertEqual((ev[0]["days"], ev[0]["total"], ev[0]["best"]), (2, 77, {"day": "2021-02-08", "v": 70}))
        self.assertEqual(set(self.got["events"]), set(self.got["short"]))
        self.assertEqual(list(self.got["by"]), ["caiso"])

    def test_the_check_keys_stat_reads_a_california_event(self):
        self.assertEqual(self.got["total"], round(sum(150 + i for i in range(6)) * 250))  # for the reader's 250 MW, whole dollars
        self.assertEqual(self.got["best"], 30 * 250)
        self.assertIsNone(self.got["unknown"])                                           # an event the grid's rows do not hold
        self.assertEqual(self.got["labels"], ["4 to 9 September 2024", "20 and 21 January 2025", "30 September to 2 October 2026", "31 December 2025 and 1 January 2026",
                                              "15 July 2025", "4 to 9 September 2024"])

    def test_the_page_reads_the_rows_of_the_grid_shown_and_draws_the_sentence_for_any_grid_that_holds_events(self):
        page, read = src("site", "app", "cost-of-power", "battery", "page.tsx"), src("site", "app", "cost-of-power", "battery", "read.ts")
        self.assertIn("export async function stressRowsOf(entity: string, x: Pick<Inputs, \"strat\" | \"dur\">): Promise<StressRow[]> {", read)
        self.assertIn('return rest<StressRow>("series", { select: "variable,ts_utc,value,event", table_name: `eq.${STRESS_TABLE}`, entity: `eq.${entity}`,', read)
        self.assertIn("const stressRead = g.review || !read.ok ? null : await attempt(() => stressRowsOf(g.entity!, asked));", page)   # a grid in review is never asked
        self.assertIn("const events = stressRead?.ok ? stress(stressRead.data, x.strat, x.dur) : [];", page)
        self.assertIn('{events.length ? <span data-stress-days={events.map((e) => e.event).join(" ")}> The stress days{STRESS_BY[x.grid] ? `, ${STRESS_BY[x.grid]}` : ""} ({events.map((e) => e.short).join(", ")}): '
                      "<a href={STRESS_DOWNLOAD} download>the table, CSV</a>.</span>\n", page)
        # the events could not be read: the download is still offered, with no event named
        self.assertIn(': stressRead && !stressRead.ok ? <span data-stress-days=""> The stress days: <a href={STRESS_DOWNLOAD} download>the table, CSV</a>.</span> : null}', page)
        self.assertNotIn('{x.grid === "ercot" ? <> The stress days', page)                # the line session 246 named is gone
        self.assertEqual(page.count("The stress days"), 2)
        lib = src("site", "lib", "batterystack.ts")
        self.assertNotIn("for (const event of Object.keys(EVENTS))", lib)                # the fixed list no longer chooses the events
        self.assertIn('export const STRESS_BY: Record<string, string> = { caiso: "the days of CAISO\'s system-wide notices" };', lib)


class TheMarketMonitorsFleetBesideCaisosIncome(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = src("site", "lib", "batterystack.ts")
        cls.page = src("site", "app", "cost-of-power", "battery", "page.tsx")
        doc = src("docs", "methods", "battery_stack.md")
        cls.part = doc.split("## CAISO beside its market monitor (session 246)", 1)[1].split("\n## ", 1)[0]
        cls.doc = doc
        cls.got = node("""
const B = await import("./lib/batterystack.ts");
const rows = [];
const put = (m, k, v) => rows.push({ variable: `dayahead_4h_${k}`, ts_utc: `${m}-01T00:00:00+00:00`, value: v });
for (let i = 1; i <= 12; i++) {
  const m = `2025-${String(i).padStart(2, "0")}`;
  put(m, "days_held", 30); put(m, "days_in_month", 30); put(m, "revenue_energy_usd_per_mw", 1000 * i); put(m, "revenue_ancillary_usd_per_mw", 700);
  put(m, "revenue_total_usd_per_mw", 1000 * i + 700); put(m, "revenue_regup_usd_per_mw", 100); put(m, "revenue_regdn_usd_per_mw", 500); put(m, "revenue_spin_usd_per_mw", 100);
}
for (const [k, v] of [["days_held", 30], ["days_in_month", 30], ["revenue_energy_usd_per_mw", 5000], ["revenue_ancillary_usd_per_mw", 9], ["revenue_total_usd_per_mw", 5009], ["revenue_regup_usd_per_mw", 9]]) put("2026-01", k, v);
const f = B.fleetBeside("caiso"), x = B.fleetCase(f, "caiso", 250);
const short = rows.filter((r) => !r.ts_utc.startsWith("2025-12"));
console.log(JSON.stringify({ f, x, key: B.inputsKey(x), ercot: B.fleetBeside("ercot"), nyiso: B.fleetBeside("nyiso"), grids: Object.keys(B.FLEET_BESIDE),
  energy: B.stat(rows, [], x, `year_kw:${f.year}:energy`), reg: B.stat(rows, [], x, `year_kw:${f.year}:${f.regulationStreams}`), spin: B.stat(rows, [], x, "year_kw:2025:spin"),
  year: B.stat(rows, [], x, "year:2025:energy"), eleven: B.stat(short, [], x, "year_kw:2025:energy"), partial: B.stat(rows, [], x, "year_kw:2026:energy"),
  nothing: B.stat(rows, [], x, "year_kw:2025"), awards: B.awardsBeside({ built: "", cases: {} }, "caiso", "dayahead", 4) }));
""")

    def test_the_published_figures_are_the_notes_and_the_report_is_the_one_it_cites(self):
        f = self.got["f"]
        self.assertEqual((f["year"], f["dur"], f["strat"], f["energy"], f["regulation"], f["regulationStreams"]), ("2025", 4, "dayahead", 35, 9, "regup+regdn"))
        # the report's own words, as the note quotes them, and the row that sets the model beside them
        self.assertIn('"nearly $35/kW-yr in market revenues for energy and $9/kW-yr for regulation"', self.part)
        self.assertIn(f"${f['energy']}/kW-yr in market revenues for energy and ${f['regulation']}/kW-yr for regulation", self.part)
        self.assertIn("| 2025, the real fleet: energy; regulation | 42.31; 42.25 (the page's model, day-ahead) |", self.part)
        self.assertIn(f"[*{f['report']}*, June 2026]({f['url']}), section 1.3.3 (pages 118 to 121 of the report; Tables 1.7 and 1.8)", self.part)
        self.assertEqual(f["publisher"], "CAISO Department of Market Monitoring")
        self.assertEqual(f["where"], "June 2026, section 1.3.3, Tables 1.7 and 1.8")
        self.assertIn("a hypothetical 100 MW, 4-hour battery", self.part)                 # the case the model's figures are computed for
        self.assertEqual(self.got["grids"], ["caiso"])
        self.assertIsNone(self.got["ercot"])                                             # ERCOT has its awards line; a grid in review has neither
        self.assertIsNone(self.got["nyiso"])
        self.assertIsNone(self.got["awards"])                                            # awardsBeside stays ERCOT's (tests/test_session178.py)
        self.assertIn('<a id="caiso-market-monitor"></a>\n\n## CAISO beside its market monitor (session 246)\n', self.doc)

    def test_the_models_two_figures_are_computed_from_the_months_and_typed_nowhere(self):
        self.assertEqual(self.got["key"].split("&")[:4], ["grid=caiso", "dur=4", "strat=dayahead", "mw=250"])
        self.assertAlmostEqual(self.got["energy"], sum(range(1, 13)))                    # USD per kW: the year's months over 1,000, whatever the size
        self.assertAlmostEqual(self.got["energy"], self.got["year"])                     # the stat the year chart already carries
        self.assertAlmostEqual(self.got["reg"], 12 * 0.6)                                # Regulation Up and Down added; Spinning Reserve is not in it
        self.assertAlmostEqual(self.got["spin"], 1.2)
        for k in ("eleven", "partial", "nothing"):
            self.assertIsNone(self.got[k], k)                                            # not a whole year, or no stream named: no figure
        for typed in ("42.31", "42.25", "42.3", "42.2"):
            self.assertNotIn(typed, self.page, typed)
            self.assertNotIn(typed, self.lib.split("export const FLEET_BESIDE", 1)[1].split("};", 1)[0], typed)

    def test_the_page_draws_one_line_for_a_grid_that_has_them_with_check_keys_and_the_citation(self):
        p = self.page
        self.assertEqual(p.count("data-fleet-beside="), 1)
        self.assertEqual(p.count("data-awards-beside="), 1)                              # ERCOT's line is as it was
        line = p[p.index("data-fleet-beside="):]
        line = line[:line.index("</p>")]
        self.assertIn("<V pre={fleetKey} s={`year_kw:${fleet.year}:energy`} v={fleetEnergy} />", line)
        self.assertIn("<V pre={fleetKey} s={`year_kw:${fleet.year}:${fleet.regulationStreams}`} v={fleetReg} />", line)
        for words in ('<span data-fleet-published="energy">{fleet.energy}</span>', '<span data-fleet-published="regulation">{fleet.regulation}</span>',
                      "({fleet.publisher}, <a href={fleet.url} rel=\"noopener\">{fleet.report}</a>, {fleet.where})", "<Link href={MONITOR}>How this is counted</Link>",
                      "on the day-ahead schedule", "with a full year of operation"):
            self.assertIn(words, line, words)
        for word in ("should", "recommend", "better", "worse", "only ", "merely", "far "):  # the facts, no commentary, as ERCOT's line
            self.assertNotIn(word, line.lower(), word)
        self.assertIn("{fleet && fleetEnergy !== null && fleetReg !== null ? (", p)       # a figure that cannot be computed leaves the line out
        self.assertIn("const fleet = g.review || !read.ok ? null : fleetBeside(x.grid);", p)
        self.assertIn("fleet.strat === asked.strat && fleet.dur === asked.dur ? { ok: true as const, data: rows } : await attempt(() => rowsOf(g.entity!, fleet));", p)
        self.assertIn("const MONITOR = `${METHOD}#caiso-market-monitor`;", p)
        check = src("site", "scripts", "check-values.mjs")
        self.assertIn("return B.stat(rows, stress, x, p[2]);", check)                    # the key is recomputed from the script's own read of the case's rows
        self.assertIn('case "year_kw": return yearKw(ms, b, c);', self.lib)

    def test_the_note_says_what_the_page_now_does(self):
        part = self.doc.split("## For the page: what CAISO still lacks beside ERCOT (session 246)", 1)[1].split("\n## ", 1)[0]
        for words in ("**Session 257 (13 October 2026) did the first two rows.**", "`stressRowsOf`", "`FLEET_BESIDE`", "`year_kw:2025:energy` and `year_kw:2025:regup+regdn`",
                      "The third row still waits for a pull."):
            self.assertIn(words, part, words)
        # the step-by-step note explains the line and its two keys (tests/test_session178.py asks that of every key the page prints)
        steps = src("docs", "methods", "battery_earns_algorithm.md")
        for words in ("**For CAISO, since session 257: the line beside its market monitor.**", "`year_kw:2025:energy` and `year_kw:2025:regup+regdn`",
                      "no figure unless all twelve months are held", "**Session 257: the table is read again, for the events' names alone.**"):
            self.assertIn(words, steps, words)


class TheGeneratorsCount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.note = src("docs", "methods", "generator_earns_algorithm.md")
        cls.page = src("site", "app", "cost-of-power", "seller", "page.tsx")
        sec = cls.note[cls.note.index("### 12.5 Beside published figures"):cls.note.index("### 12.6 ")]
        cls.twelve = [cells(ln) for ln in sec.split("\n") if ln.startswith("| ")][1:]
        cross = cls.note[cls.note.index("\n## Cross-checks\n"):]
        cls.cross = [[c.strip() for c in re.split(r"(?<!\\)\|", ln.strip().strip("|"))] for ln in cross.split("\n") if ln.startswith("| ")][1:]

    def test_the_ten_rows_that_hold_a_gap_are_the_last_ten_of_the_cross_checks_cell_for_cell(self):
        self.assertEqual(len(self.twelve), 12)
        gaps = [r for r in self.twelve if not r[3].startswith("not computed")]
        self.assertEqual(len(gaps), 10)
        self.assertEqual(len(self.cross), 20)
        first, last = self.cross[:10], self.cross[10:]
        self.assertTrue(first[0][0].startswith("Solar in ERCOT, the contract price at which coverage reaches 1.25 times: USD 39.14 per MWh"))   # session 196's ten, as they were
        self.assertTrue(first[9][0].startswith("New England's internal hub, day-ahead, the peak block"))
        for moved, r in zip(last, gaps):
            self.assertEqual(len(moved), 5, moved[0][:60])
            self.assertTrue(moved[0].startswith("CAISO: "), moved[0][:60])
            self.assertTrue(moved[0].endswith(": " + r[1]), moved[0][:60])               # "Our figure" ends with the row's "Ours"
            self.assertEqual(moved[1], r[2], moved[0][:60])                              # the published figure
            self.assertEqual(moved[3], r[3], moved[0][:60])                              # the gap
            self.assertEqual(moved[4], r[4], moved[0][:60])                              # the reason
            what = r[0] if not r[0].startswith("The same, run their way") else r[0][len("The same, run their way"):]
            self.assertIn(what, moved[0], moved[0][:60])
        self.assertIn("A gas peaker at NP15, 2025, run their way as far as the model can", last[1][0])
        self.assertIn("A gas peaker at SP15, 2025, run their way as far as the model can", last[3][0])

    def test_each_of_the_ten_names_where_it_was_read(self):
        last = self.cross[10:]
        dmm = "https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf"
        wind = "https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx"
        solar = "https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx"
        want = [dmm, None, None, None, dmm, wind, None, None, solar, wind]
        for r, address in zip(last, want):
            if address is None:
                self.assertEqual(r[2], "the same", r[0][:60])
            else:
                self.assertIn(f"]({address})", r[2], r[0][:60])
                self.assertIn("read 13 October 2026", r[2], r[0][:60])
        self.assertIn("section 1.3.2, Tables 1.5 and 1.6, pages 115 and 116", last[0][2])
        self.assertIn("section 1.2.6, page 94", last[4][2])
        self.assertNotIn("emp.lbl.gov/sites", self.note)                                 # the host that refused the reader is never linked
        intro = self.note[self.note.index("\n## Cross-checks\n"):].split("\n| Our figure")[0]
        self.assertIn("The last ten rows are CAISO's (session 257, 13 October 2026)", intro)
        self.assertIn("for Berkeley Lab's host no terms page was read, which session 253 left for a ruling", intro)

    def test_the_page_counts_twenty_and_names_the_two_new_publishers(self):
        self.assertIn('<span data-checked-against="20">Checked against: 20 published figures (Lazard, the Annual Technology Baseline, EIA, CAISO&apos;s market monitor, Berkeley Lab). '
                      '<Link href="/data/methods/generator_earns_algorithm#cross-checks">Each comparison, with its gap and the reason</Link>.</span>', self.page)
        self.assertEqual(self.page.count("data-checked-against="), 1)
        how = src("docs", "howitworks", "generator.md")
        self.assertNotIn("10 published figures", how)
        self.assertIn('"Checked against: 20 published figures (Lazard, the Annual Technology Baseline, EIA, CAISO\'s market monitor, Berkeley Lab)."', how)

    def test_what_waits_was_not_touched(self):
        lib = src("site", "lib", "merchant.ts")
        self.assertIn("const c = g * hr + vom;", lib)                                    # the peaker's carbon cost waits for a ruling
        self.assertIn('export const EVENTS: Record<string, string> = { uri_2021: "Winter Storm Uri, February 2021", elliott_2022: "Winter Storm Elliott, December 2022", '
                      'ercot_heat_2023: "ERCOT\'s summer 2023 heat" };', lib)             # CAISO's stress days wait for the snapshot
        snap = json.loads(src("site", "data", "merchant_snapshot.json"))
        if "stress" in snap["isos"]["caiso"]:
            self.fail("the snapshot now holds CAISO's stress days: add their labels to lib/merchant.ts (session 253's list, row 3) and move this test")
        self.assertNotIn("SunZia", self.page)                                            # the sentence beside CAISO's wind waits for a ruling
        self.assertIn("**Session 257 (13 October 2026) did the first row, and no other.**", self.note)


class House(unittest.TestCase):
    def test_no_page_changed_its_status(self):
        rel = src("site", "lib", "release.ts")
        for page in ("/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power"):
            self.assertIn(f'"{page}": "review",', rel, page)

    def test_california_is_ready_on_the_battery_page_and_marked_in_review_nowhere(self):
        lib = src("site", "lib", "batterystack.ts")
        self.assertIn('{ id: "caiso", name: "CAISO", ready: true, hub: "SP15", entity: "caiso:TH_SP15_GEN-APND", from: "August 2023" },', lib)   # session 273: CAISO's history pulled back to OASIS's edge
        for parts in (("site", "app", "cost-of-power", "battery", "page.tsx"), ("site", "app", "cost-of-power", "battery", "BatteryForm.tsx"),
                      ("site", "app", "cost-of-power", "seller", "page.tsx"), ("site", "app", "cost-of-power", "seller", "SellerForm.tsx"), ("site", "app", "cost-of-power", "page.tsx")):
            for line in src(*parts).split("\n"):
                if re.search(r"CAISO|California", line) and not line.lstrip().startswith(("//", "*", "/*", "{/*")):
                    self.assertNotRegex(line, r"(CAISO|California)[^.;]{0,80}\b(in review|coming)\b", parts[-1])

    def test_no_em_dash_in_what_the_session_wrote(self):
        for f in WROTE:
            if os.path.exists(os.path.join(ROOT, *f.split("/"))):
                self.assertNotIn(EM, src(*f.split("/")), f)


if __name__ == "__main__":
    unittest.main()
