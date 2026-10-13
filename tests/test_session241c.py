"""Session 241, batch C: the leftovers of the overnight chain of 12 to 13 October 2026.

1. One datacenter tracker. /datacenters draws what /datacenters/v2 drew (session 106: ERCOT's large-load status, and the
   Texas sites beside it), every figure with a check key; /datacenters/v2 redirects to it and its file stands in
   site/app/_retired. Nothing the old page showed was dropped: each sentence it wrote is in the file that draws it now.
2. The color literals the chain left in files already on the brand are tokens (site/app/tokens.css), read by the chart.
3. The consumption view's tables scroll inside their own frame on a phone.

Here, the sources. The built pages are checked by site/scripts/check-datacenters.mjs, check-values.mjs and
check-routes.mjs.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def code(text):
    """A source without its comments (a comment may name a color it replaced)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in text.splitlines())


class OneTracker(unittest.TestCase):
    def test_the_old_address_redirects_and_its_file_is_kept(self):
        config = src("site", "next.config.ts")
        self.assertIn('      { source: "/datacenters/v2", destination: "/datacenters", permanent: true },', config)
        self.assertNotIn('//   { source: "/datacenters/v2"', config)                    # the line session 239 left as a comment is the line now
        self.assertFalse(os.path.exists(os.path.join(ROOT, "site", "app", "datacenters", "v2")))
        old = src("site", "app", "_retired", "datacenters-v2", "page.tsx")
        self.assertIn("export default async function TrackerTwo()", old)                # the page as it was, not deleted
        self.assertRegex(src("site", "lib", "release.ts"), r'"/datacenters/v2":\s*"review"')   # an address typed by hand never reads as a page with no status
        self.assertNotIn('href: "/datacenters/v2"', src("site", "lib", "audience.ts"))

    def test_the_tracker_draws_the_block_in_every_state_of_its_read(self):
        page = src("site", "app", "datacenters", "page.tsx")
        self.assertEqual(page.count("<LargeLoad read={res} />"), 3)                     # the table read, empty, or not read: ERCOT's section stands
        self.assertIn("<LargeLoadSource />", page)
        self.assertIn("<Body rows={res.data.map(toFacility)} today={today}><LargeLoad read={res} />{words}</Body>", page)   # after the top block, before the list
        self.assertIn('<section aria-label="Facilities" id="every-site">', src("site", "app", "datacenters", "DatacentersTable.tsx"))

    def test_nothing_the_old_page_showed_was_dropped(self):
        old = src("site", "app", "_retired", "datacenters-v2", "page.tsx")
        new = src("site", "app", "datacenters", "LargeLoad.tsx")
        # every title, label, caption and table head of the old page
        for attr in ("title", "label", "caption"):
            for value in re.findall(attr + r'="([^"]+)"', old):
                if value == "The datacenter tracker":                                    # the old page's own title: the page is the tracker now
                    continue
                self.assertIn(f'{attr}="{value}"', new, value)
        for head in re.findall(r"head=\{(\[[^\]]+\])\}", old):
            self.assertIn(head, new, head)
        # every sentence in bold, and the words the page was built to say
        for strong in re.findall(r"<strong>([^<{]+)</strong>", old):
            self.assertIn(f"<strong>{strong}</strong>", new, strong)
        for words in ("of the load ERCOT has approved to energize, less than half has been observed running", "The ERW does not read a number off a picture",
                      "new LLI submissions&quot; and that &quot;preliminary review indicates these total approximately", "the first cannot be the larger. Both are shown as written.",
                      "No status update has been found on its meeting pages since ", "The two are not added.", "sites outside the US among them",
                      "By where each came from:", "No other operator&apos;s large-load report is in the warehouse.", "so no number is shown",
                      "ERCOT&apos;s terms let raw data in public portions of its website be used and redistributed", "built {f.built.slice(0, 10)}",
                      'data-load-summary="1"', 'data-facilities-summary="1"', "data-load-row={`${r.day}|approved`}"):
            self.assertIn(words, old, words)
            self.assertIn(words, new, words)
        for k in ("approved", "nonsimultaneous", "simultaneous"):
            self.assertIn(f'data-load="{k}"', new)
            self.assertIn(f'{{ label: "{ {"approved": "Approved to energize", "nonsimultaneous": "Observed running", "simultaneous": "Served at one moment"}[k] }", color:', new)   # the chart's three lines

    def test_the_month_of_the_newest_report_is_read_from_the_table(self):
        """The old page wrote "since March 2026" as fixed words. The table grew (its newest report is later), so the
        words stood beside a table that contradicted them; the month is the newest report's own now."""
        new = src("site", "app", "datacenters", "LargeLoad.tsx")
        self.assertIn("const newest = f.reports[f.reports.length - 1];", new)
        self.assertIn('since <span data-last-report={newest.day}>{dayWords(newest.day).split(" ").slice(1).join(" ")}</span>.', new)
        self.assertNotIn("since March 2026", code(new))                                  # (a comment says what stood there)
        self.assertIn("since March 2026", src("site", "app", "_retired", "datacenters-v2", "page.tsx"))   # the page as it was, kept
        import json
        reports = json.loads(src("site", "data", "large_load_status.json"))["reports"]
        self.assertEqual(reports, sorted(reports, key=lambda r: r["day"]))                # the last is the newest

    def test_every_figure_carries_a_check_key(self):
        new = src("site", "app", "datacenters", "LargeLoad.tsx")
        self.assertIn("<Num check={`series|${f.table}|${ENTITY}|${VARIABLE[k]}|${r.day}T00:00:00Z`} raw={r[k] as number}>{whole(r[k] as number)}</Num>", new)
        self.assertIn('const ENTITY = "ercot:large_load";', new)
        for v in ("approved_to_energize_mw", "observed_nonsimultaneous_peak_mw", "observed_simultaneous_peak_mw"):
            self.assertIn(v, new)
            self.assertIn(v, src("warehouse", "connectors", "ercot_large_load_status.py"), v)        # the table's own variables
        self.assertIn('ts_utc=f"{day}T00:00:00Z"', src("warehouse", "connectors", "ercot_large_load_status.py"))   # the key's timestamp is the row's
        checks = src("site", "scripts", "check-values.mjs")
        for key in ("count", "sites_us", "sites_texas", "no_us_state", "sites_n_with_mw", "sites_mw", "texas_n_with_mw", "texas_mw"):
            self.assertIn(f'check="datacenters|{key}"', new, key)
            self.assertIn(f'if (what === "{key}")', checks, key)
        self.assertIn("check={`datacenters|kind_count|${k}`}", new)
        self.assertIn('if (what === "kind_count")', checks)
        self.assertIn("kind:extra->>kind", checks)
        self.assertIn(r"(^series\|ercot_large_load_status\|)", checks)                 # ERCOT's megawatts are written whole
        # no figure of the two sections is written without a key in running words
        bare = re.findall(r"\{whole\(([^)]+)\)\}", new)
        keyed = re.findall(r"<Num [^>]*>\{whole\(([^)]+)\)\}</Num>", new)
        self.assertEqual(sorted(set(bare) - set(keyed)), [])                             # (a Texas row's megawatts is a cell of the table, as the list's rows are)
        for k in ("new_count", "new_mw", "simultaneous", "nonsimultaneous"):                # the figures inside the notes are keyed too
            self.assertIn(f'<Mw f={{f}} r={{r}} k="{k}" />', new, k)
        self.assertIn('new_count: "new_submissions_count", new_mw: "new_submissions_mw"', new)

    def test_the_checks_read_the_one_address(self):
        c = src("site", "scripts", "check-datacenters.mjs")
        self.assertNotIn('get("/datacenters/v2"', c)
        self.assertEqual(c.count("check("), 14)                                         # 11 before the fold; none dropped, three new (the last is asked twice: with and without a query)
        self.assertIn('[["/datacenters/v2", "/datacenters"], ["/datacenters/v2?state=TX", "/datacenters?state=TX"]]', c)
        self.assertIn("r.status === 308 && where === to", c)
        self.assertIn("k(m[2]) + k(m[4]) === k(m[1]) && k(m[3]) <= k(m[2])", c)        # the sentence's sum, as it was asked of /datacenters/v2
        self.assertIn('"/seller/v2", "/datacenters/v2",', src("site", "scripts", "check-routes.mjs"))
        self.assertIn('"/datacenters", "/roundup",', src("site", "scripts", "check-values.mjs"))


class NoColorLiteral(unittest.TestCase):
    FILES = (("site", "components", "board", "Workbench.tsx"), ("site", "lib", "mixpage.ts"), ("site", "app", "storage", "owners", "view.tsx"),
             ("site", "app", "deals", "v2", "view.tsx"), ("site", "app", "map", "ProjectMap.tsx"), ("site", "app", "resources", "ResourceMap.tsx"),
             ("site", "app", "datacenters", "LargeLoad.tsx"), ("site", "app", "datacenters", "page.tsx"), ("site", "app", "datacenters", "Body.tsx"),
             ("site", "app", "datacenters", "DatacentersTable.tsx"), ("site", "app", "consumption", "view.tsx"), ("site", "components", "mix", "Charts.tsx"))

    def test_no_hex_and_no_rgb_literal_in_the_files(self):
        for parts in self.FILES:
            c = code(src(*parts))
            self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b", c), [], "/".join(parts))
            self.assertEqual(re.findall(r"rgba?\(\s*\d", c), [], "/".join(parts))

    def test_the_network_keeps_no_hex_and_says_what_it_computes(self):
        c = code(src("site", "app", "network", "Network.tsx"))
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b", c), [])
        self.assertIn("let PAL: Palette = Object.fromEntries((Object.keys(TOKENS) as (keyof Palette)[]).map((k) => [k, `var(${TOKENS[k]})`])) as Palette;", c)
        self.assertIn("readPalette(box.current);", c)                                   # the canvas takes the tokens' values before a scene is built

    def test_the_two_ramps_are_tokens_with_the_values_the_charts_drew(self):
        css = src("site", "app", "tokens.css")
        block = css.split("/* ---- session 241c:", 1)[1].split("/* ---- session", 1)[0]
        years = ["#C9C2B4", "#B5AC9C", "#A19785", "#8E836F", "#7A6E5A", "#665945", "#52442F"]
        seasons = ["#B8B2A7", "#A39C90", "#8E877B", "#797266", "#645E53"]
        for i, v in enumerate(years, 1):
            self.assertIn(f"  --color-year-{i}: {v};", block)
        for i, v in enumerate(seasons, 1):
            self.assertIn(f"  --color-season-{i}: {v};", block)
        self.assertEqual(sorted(re.findall(r"#[0-9A-Fa-f]{6}\b", block)), sorted(years + seasons))    # nothing else
        self.assertIn(":root {", block)                                                # a chart reads a token at the page's root (components/echarts.ts)
        rules = re.sub(r"/\*.*?\*/", "", "/* ---- session 241c:" + block, flags=re.S)
        self.assertNotRegex(rules, r"board|mix|grid|datacenter")                        # a token names a kind of chart, never a page
        self.assertEqual(css.count("{"), css.count("}"))

    def test_the_charts_read_the_tokens_in_the_same_order(self):
        mix = src("site", "lib", "mixpage.ts")
        self.assertIn('export const YEAR_SHADES = ["--color-year-1", "--color-year-2", "--color-year-3", "--color-year-4", "--color-year-5", "--color-year-6", "--color-year-7", "--color-accent"];', mix)
        self.assertIn('`var(${n <= 1 ? "--color-accent" : YEAR_SHADES[Math.min(7, Math.round((7 * i) / (n - 1)))]})`', mix)   # the same step for the same year
        self.assertIn('const col = (c: string) => (c.startsWith("var(") || c.startsWith("--") ? token(c) : c);', src("site", "components", "mix", "Charts.tsx"))
        bench = src("site", "components", "board", "Workbench.tsx")
        self.assertIn("const greys = [1, 2, 3, 4, 5].map((i) => token(`season-${i}`));", bench)
        self.assertEqual(bench.count("greys[Math.max(0, greys.length - (shown.length - 1) + i)] ?? greys[0]"), 2)   # the line and its marker, as they were
        res = src("site", "app", "resources", "ResourceMap.tsx")
        self.assertIn('none: R.rgbOf(cssVar("--color-not-reported"))', res)
        self.assertIn("tone === null ? R.css(p.none, 0.6) :", res)                     # the grey of a class with no value, at the opacity it had
        self.assertRegex(src("site", "app", "tokens.css"), r"--color-not-reported: #B8B2A7;")   # 184, 178, 167: the literal that stood there


class APhone(unittest.TestCase):
    def test_every_table_of_the_consumption_view_stands_in_a_scroll_frame(self):
        v = src("site", "app", "consumption", "view.tsx")
        tables = [m.start() for m in re.finditer(r"<table ", v)]
        self.assertEqual(len(tables), 3)
        for at in tables:
            before = v[:at].rstrip()
            self.assertTrue(before.endswith('<div className="overflow-x-auto">') or before.endswith("*/}"), v[at - 120:at])
        self.assertEqual(v.count('<div className="overflow-x-auto">'), 3)
        self.assertIn(".brand-a .overflow-x-auto {", src("site", "app", "tokens.css"))   # the brand's rule for a wide table is written for this frame


class NoEmDash(unittest.TestCase):
    def test_no_em_dash_in_what_the_session_wrote(self):
        for parts in NoColorLiteral.FILES + (("site", "app", "network", "Network.tsx"), ("site", "app", "tokens.css"), ("site", "next.config.ts"), ("site", "lib", "release.ts"),
                                             ("site", "lib", "audience.ts"), ("site", "scripts", "check-datacenters.mjs"), ("site", "scripts", "check-values.mjs"),
                                             ("site", "scripts", "check-routes.mjs"), ("tests", "test_session241c.py"), ("archive", "sessions", "SESSION_241C_REPORT.md")):
            if parts[-1] == "SESSION_241C_REPORT.md" and not os.path.exists(os.path.join(ROOT, *parts)):
                continue
            self.assertNotIn(EM, src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
