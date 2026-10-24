"""Session 1181 (chain 091): when a read fails, on the Grid tool's panels of chains 077 and 078.

Energy Research Warehouse (ERW).

Every panel chains 077 and 078 added was drawn with one read failing at a time (a statement timeout past the retries,
an HTTP 500, an empty answer; the snapshot's Storage object; the replay's committed file not found). Where a panel drew a
wrong statement ("not held", "no hour of the week holds all three", "0 days", "no alert", "not in the warehouse yet") or
dropped its name, it now says the read could not be read, in the tool's one look (Missing "could not be read", the table
and the reason on hover), and draws no figure of it. The two whole-table notice reads take an empty answer as a failed
read. No read of the Grid page is required(): the page is drawn on demand. site/scripts/test-grid-failed-reads.mjs holds
a case a panel and a failure kind on committed real rows (scripts/fixtures/grid_failed_reads.json and the fixtures of
sessions 1154, 1155, 1165 and 1174).

    python -m unittest tests.test_session1181 -v
"""

import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
NODE = shutil.which("node")
MODULES = all(os.path.isdir(os.path.join(SITE, "node_modules", p)) for p in ("typescript", "react"))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def node_env():
    return {k: v for k, v in os.environ.items()
            if k not in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "NEXT_PHASE", "NEXT_RUNTIME", "ERW_PAGES_TOGETHER", "ERW_READ_TIMING")}


@unittest.skipUnless(NODE and MODULES, "node or site/node_modules (typescript, react) is not on this machine")
class TheNodeTest(unittest.TestCase):
    def test_every_case_holds(self):
        r = subprocess.run([NODE, "--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", "scripts/test-grid-failed-reads.mjs"],
                           cwd=SITE, capture_output=True, text=True, timeout=600, env=node_env())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])
        self.assertIn("every case holds", r.stdout)
        self.assertNotIn("FAIL", r.stdout)
        self.assertGreaterEqual(len(re.findall(r"^ok   ", r.stdout, re.M)), 55)
        for panel in ("grid_network_ercot", "balance_ERCO", "grid_gravity_ercot", "grid_clean24_ercot", "grid_mix_ercot", "grid_scarcity_ercot",
                      "grid_scarcity_caiso", "grid_caisoalert_caiso", "grid_ercotnotice_ercot", "grid_ask_ercot", "mixview_stress", "mixview_day",
                      "replay_ERCO", "gravityday", "preliminary"):
            self.assertIn(panel, r.stdout)
        for kind in ("timeout", "http500", "empty"):
            self.assertIn(f", {kind}:", r.stdout)


class TheWords(unittest.TestCase):
    def test_the_live_week_keeps_its_failed_reads(self):
        d = src("site", "app", "network", "data.ts")
        self.assertIn("  if (!dem.ok) out.failed!.demand = dem.reason;", d)
        self.assertIn("  if (!gen.ok) out.failed!.generation = gen.reason;", d)
        self.assertIn('failed?: Partial<Record<"demand" | "generation", string>> };', src("site", "app", "network", "Network.tsx"))

    def test_the_network_balance_and_gravity_panels_say_could_not_be_read(self):
        n = src("site", "components", "grid", "NetworkFigures.tsx")
        self.assertIn('return <Missing words="could not be read" why={`${table} could not be read just now: ${reason}`} />;', n)
        self.assertIn("not computed: a part could not be read", n)
        self.assertIn("The week&apos;s gap is not computed: its hours", n)
        self.assertIn("genGone ? <Unread key=\"g\" table={GENERATION_TABLE} reason={genGone} />", n)
        # the words for what is not held stand as they were
        self.assertIn("No hour of the week holds all three, so the week&apos;s gap is not computed.", n)
        self.assertIn("not computed: a part is not held", n)
        self.assertIn("its demand in the hour is not held", n)

    def test_the_mix_panel(self):
        m = src("site", "components", "grid", "MixView.tsx")
        self.assertIn('<p className="mb-2 text-sm" data-mix-unread="1">The hourly mix: {failed(hourly.reason)}</p>', m)
        self.assertIn("demandFailed={more && !more.ok ? more.reason : undefined}", m)
        f = src("site", "components", "grid", "MixFigures.tsx")
        self.assertIn('Peak demand: <Missing words="could not be read" why={`${DEMAND} could not be read just now: ${demandFailed}`} />.', f)
        self.assertIn("<>Demand is not held for these hours.</>", f)

    def test_the_clean_panel_keeps_its_name(self):
        e = src("site", "components", "grid", "Emissions.tsx")
        self.assertIn('<div data-grid-panel={`grid_clean24_${grid ?? "all"}`} data-clean24-unread={got.ok ? "empty" : "failed"}>', e)

    def test_the_scarcity_prices(self):
        s = src("site", "components", "grid", "ScarcityPanel.tsx")
        self.assertIn("priceFailed: prices.ok ? null : prices.reason, dailyFailed: daily && !daily.ok ? daily.reason : null,", s)
        self.assertIn("<li data-scarcity-unread={RT_PRICE_TABLE}>", s)
        self.assertIn("<li data-scarcity-unread={DAILY_PRICE_TABLE}>", s)
        lib = src("site", "lib", "scarcityStrip.ts")
        self.assertIn("unread?: { prices?: string | null; daily?: string | null } }, days = SCARCITY_DAYS): Strip {", lib)
        self.assertIn("`No price of this hour is in the live set (it keeps about 35 days of 15-minute prices).`", lib)

    def test_an_empty_whole_notice_table_is_a_failed_read(self):
        g = src("site", "lib", "gridReads.ts")
        self.assertIn("export async function wholeTable<T>(table: string, holds: string, read: () => Promise<T[]>): Promise<T[]> {", g)
        self.assertIn("answered no row for the whole table, which holds ${holds}: read as a failed read`);\n  await markFailedRead(e);\n  throw e;", g)
        self.assertIn('export const CAISO_HOLDS = "every notice since 1998";', g)
        self.assertIn("const rows = await wholeTable(NOTICE_TABLE, \"ERCOT's notices since 2011\", () => rest<Row>(\"events\", {", src("site", "lib", "gridErcotNotices.ts"))
        self.assertIn("export async function wholeRead<T>(table: string, holds: string, read: Promise<", g)
        for f in ("CaisoAlertState.tsx", "ScarcityPanel.tsx", "MixView.tsx", "Reliability.tsx"):
            self.assertRegex(src("site", "components", "grid", f), r"wholeRead\((ALERT_TABLE|EMERGENCIES), CAISO_HOLDS, ", f)
        # the reads sessions 1155 and 1174 pinned stand inside it, word for word
        self.assertIn('wholeRead(ALERT_TABLE, CAISO_HOLDS, g.slug === "caiso" ? attempt(() => gridNotices()) : Promise.resolve(null)),', src("site", "components", "grid", "ScarcityPanel.tsx"))
        # the read itself, and the windowed read, as session 1160 left them
        r = src("site", "lib", "reliability.ts")
        self.assertIn('const everyNotice = cache(async (): Promise<Notice[]> => rest<Notice>("events", noticesQuery(), HOURLY, 20_000));', r)
        self.assertNotIn("wholeTable", r)
        self.assertIn('data-reliability-unread="1"', src("site", "components", "grid", "Reliability.tsx"))

    def test_the_replay_day_and_the_queue(self):
        d = src("site", "components", "grid", "ReplayDay.tsx")
        self.assertIn('<Missing words="could not be read" why={ask.read.why} />', d)
        self.assertIn('<Missing words="not held" why={r?.demandWhy ?? ""} />', d)
        y = src("site", "components", "grid", "YourGrid.tsx")
        self.assertIn("} else if (d.errors.queue) {", y)
        self.assertIn("data-grid-queue-unread={g.queue_table}", y)


class NoGridReadIsRequired(unittest.TestCase):
    def test_no_required_read(self):
        files = [("site", "app", "grid", "page.tsx"), ("site", "app", "network", "data.ts"), ("site", "lib", "grid.ts"), ("site", "lib", "gridReads.ts"),
                 ("site", "lib", "gridErcotNotices.ts"), ("site", "lib", "reliability.ts")]
        files += [("site", "components", "grid", f) for f in os.listdir(os.path.join(SITE, "components", "grid"))]
        for parts in files:
            self.assertNotRegex(src(*parts), r"\brequired\s*\(", "/".join(parts))

    def test_the_method_note_says_so(self):
        m = src("docs", "methods", "grid_network.md")
        self.assertIn("## When a read fails (chain 091, 24 October 2026)", m)
        self.assertIn("Decisions (chain 091, session 1181):", m)


class NoEmDash(unittest.TestCase):
    def test_no_em_dash(self):
        for parts in [("site", "scripts", "test-grid-failed-reads.mjs"), ("site", "scripts", "fixtures", "grid_failed_reads.json"), ("tests", "test_session1181.py"),
                      ("docs", "methods", "grid_network.md")]:
            self.assertNotIn(chr(0x2014), src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
