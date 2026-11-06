"""Session 583: AccessLint's scan of every page of check-values' list at 1280 and 390 (docs/reviews/accessibility-2026-10-22.md).

The fixes, each in a shared file:

- components/ScrollRegions.tsx marks two more kinds of scrolling box, a chart's figure on a phone and a table of rendered
  markdown (scrollable-region, WCAG 2.1.1), and gives two regions of one page two names (landmark-unique);
- app/tokens.css underlines a link in a grey note set as a block (link-in-text-block, WCAG 1.4.1), and
  components/grid/YourGrid.tsx its "All datacenters" link;
- app/network/NetworkGravity.tsx: a circle's name begins with the label drawn under it (label-content-mismatch, WCAG 2.5.3).
"""

import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
REVIEW_DIR = os.path.join(ROOT, "docs", "brand", "review-583")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def site(*p):
    return src("site", *p)


# ScrollRegions.tsx is transpiled by the site's own TypeScript and run against stand-in elements (no browser): the
# imports of next/navigation and react are replaced by stubs, since only the two exported functions are called
PROBE = r"""
const ts = (await import("typescript")).default;
const fs = await import("node:fs");
let code = ts.transpileModule(fs.readFileSync("components/ScrollRegions.tsx", "utf-8"),
  { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX } }).outputText;
code = code.replace(/^import .*$/gm, "").replace(/^"use client";/m, "");
code = "const usePathname = () => '/'; const useEffect = () => {};\n" + code;
const M = await import("data:text/javascript;base64," + Buffer.from(code).toString("base64"));
function el(label, ours, name) {
  const attrs = new Map([["role", "region"], ["aria-label", label]]);
  return { dataset: Object.assign(ours ? { scrollLabel: "1" } : {}, name ? { scrollName: name } : {}),
    getAttribute: (k) => attrs.has(k) ? attrs.get(k) : null, setAttribute: (k, v) => attrs.set(k, v), label: () => attrs.get("aria-label") };
}
const run = (els) => { M.uniqueNames({ querySelectorAll: () => els }); return els.map((e) => e.label()); };
const out = {
  twoOurs: run([el("Reliability", true), el("Reliability", true)]),
  pageFirst: run([el("Access", false), el("Access", true)]),
  alone: run([el("Table", true)]),
  again: (() => { const a = [el("Reliability", true), el("Reliability", true)]; run(a); return run(a); })(),
  oneLeft: run([el("Reliability, 1 of 2", true, "Reliability")]),
  scrollers: M.SCROLLERS,
};
console.log(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node") and os.path.isdir(os.path.join(SITE, "node_modules", "typescript")),
                     "node or the site's node_modules is not installed")
class RegionNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run(["node", "--input-type=module", "-e", PROBE], cwd=SITE, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise AssertionError(r.stderr[-1500:])
        cls.out = json.loads(r.stdout.strip().splitlines()[-1])

    def test_two_regions_of_one_name_are_told_apart(self):
        self.assertEqual(self.out["twoOurs"], ["Reliability, 1 of 2", "Reliability, 2 of 2"])

    def test_a_name_the_page_wrote_is_never_changed(self):
        self.assertEqual(self.out["pageFirst"], ["Access", "Access, 2 of 2"])

    def test_a_name_no_other_region_shares_stays_as_it_is(self):
        self.assertEqual(self.out["alone"], ["Table"])

    def test_a_second_pass_does_not_add_to_a_name(self):
        self.assertEqual(self.out["again"], ["Reliability, 1 of 2", "Reliability, 2 of 2"])

    def test_a_name_goes_back_to_its_own_words_when_the_other_is_gone(self):
        self.assertEqual(self.out["oneLeft"], ["Reliability"])

    def test_figures_and_markdown_tables_are_read(self):
        for sel in ("main .overflow-x-auto", "main pre", "main figure", "main .prose-erw table"):
            self.assertIn(sel, self.out["scrollers"])


class TheSharedFiles(unittest.TestCase):
    def test_the_marks_are_taken_back_with_the_kept_name(self):
        c = site("components", "ScrollRegions.tsx")
        self.assertIn('el.removeAttribute("aria-label"); delete el.dataset.scrollLabel; delete el.dataset.scrollName;', c)
        body = c[c.index("export function markScrollers"):c.index("export function uniqueNames")]
        self.assertIn("  uniqueNames(root);", body)
        # session 428's rule still holds: one read of the sizes, before any write
        self.assertEqual(body.count("el.scrollWidth"), 1)

    def test_a_figure_is_a_stop_of_the_keyboard_but_not_a_region(self):
        c = site("components", "ScrollRegions.tsx")
        body = c[c.index("export function markScrollers"):c.index("export function uniqueNames")]
        stop, figure, role = body.index("el.tabIndex = 0;"), body.index('if (el.tagName === "FIGURE") return;'), body.index('el.setAttribute("role", "region")')
        self.assertLess(stop, figure)
        self.assertLess(figure, role)

    def test_the_networks_line_of_help_takes_the_captions_grey(self):
        css = site("app", "tokens.css")
        rule = css[css.index(".brand-a .scene-nav-info {"):]
        rule = rule[:rule.index("}")]
        self.assertIn("color: var(--color-muted);", rule)
        self.assertIn("opacity: 1;", rule)

    def test_a_link_in_a_grey_note_is_underlined(self):
        css = site("app", "tokens.css")
        rule = css[css.index(".brand-a div.text-muted > a:not([class]) {"):]
        rule = rule[:rule.index("}")]
        self.assertIn("text-decoration: underline;", rule)
        self.assertIn(".brand-a div.text-muted > a:not([class]):hover {", css)
        self.assertIn('<Link href="/datacenters" className="underline">All datacenters</Link>.', site("components", "grid", "YourGrid.tsx"))

    def test_a_circles_name_holds_its_label(self):
        g = site("app", "network", "NetworkGravity.tsx")
        self.assertIn('aria-label={nameOf(p.id).includes(p.label) ? nameOf(p.id) : `${p.label}, ${nameOf(p.id)}`}', g)

    def test_no_em_dash_in_the_changed_files(self):
        for p in (("site", "components", "ScrollRegions.tsx"), ("site", "app", "tokens.css"), ("site", "app", "network", "NetworkGravity.tsx"),
                  ("site", "components", "grid", "YourGrid.tsx"), ("docs", "reviews", "accessibility-2026-10-22.md")):
            with self.subTest(file=p[-1]):
                self.assertNotIn(chr(0x2014), src(*p))


class TheRecord(unittest.TestCase):
    def test_the_review_holds_the_counts_and_the_rulings(self):
        r = src("docs", "reviews", "accessibility-2026-10-22.md")
        for words in ("1280", "390", "Before", "After", "scrollable-region", "landmark-unique", "link-in-text-block",
                      "label-content-mismatch", "aria-allowed-role", "heading-order", "color-contrast", "For Samuel's ruling"):
            self.assertIn(words, r)

    def test_the_scan_and_the_shots_are_kept(self):
        names = os.listdir(REVIEW_DIR)
        for f in ("scan-583.mjs", "chrome-583.mjs", "shots-583.mjs", "counts-583.csv"):
            self.assertIn(f, names)
        shots = [f for f in names if f.endswith(".png")]
        for tag in ("before", "after"):
            for w in ("1280", "390"):
                self.assertTrue(any(f.endswith(f"_{w}_{tag}.png") for f in shots), (w, tag))


if __name__ == "__main__":
    unittest.main()
