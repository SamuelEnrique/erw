"""Session 412: the accessibility pass on every visitor page (docs/reviews/accessibility-2026-10-20.md).

AccessLint (audit_live, WCAG 2.2 A and AA) and the browser's accessibility tree with a walk of the keyboard (Tab from the
top of each page, the focus ring read at each stop) on the 25 addresses of scripts/snapshot-live.mjs and every page of the
menus, in the internal view of a local production build. Each fix has a test here; the shared components first:

- the footer's links take the brand's focus ring, and a date field shows one while a part of it has the keyboard;
- the menus mark the page in view with aria-current, where only its color said so;
- a table or block wider than its frame is one stop of the keyboard, a named region (components/ScrollRegions.tsx);
- an empty header cell of the shared tables is a plain cell (lib/cells.ts, ToolTable, DataTable);
- the board's rows open the workbench from a button in the row's name, not from a focusable table row;
- the pages' own: demand's ranking headers (white on white), the curtailment tiles' words and its note's link, the
  events' titles, the network's replay day (its name was not its label), the impact page's four fields (no name).
"""

import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.join(ROOT, "site")
REVIEW = os.path.join(ROOT, "docs", "reviews", "accessibility-2026-10-20.md")
SHOTS = os.path.join(ROOT, "docs", "brand", "review-412")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def site(*p):
    return src("site", *p)


def contrast(a, b):
    def lum(rgb):
        out = []
        for c in rgb:
            c = c / 255
            out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


class SharedFocus(unittest.TestCase):
    def test_the_footer_takes_the_brands_focus_ring(self):
        css = site("app", "tokens.css")
        rule = css[css.index("/* ---- focus: one outline for every link and control */"):]
        rule = rule[:rule.index("}") + 1]
        self.assertIn("body:has(.brand-a) > footer :focus-visible", rule)
        self.assertIn("outline: 2px solid var(--color-ink);", rule)

    def test_a_date_field_shows_the_ring_while_a_part_of_it_has_the_keyboard(self):
        css = site("app", "tokens.css")
        m = re.search(r'\.brand-a input\[type="date"\]:focus-within \{([^}]*)\}', css)
        self.assertIsNotNone(m)
        self.assertIn("outline: 2px solid var(--color-ink);", m.group(1))

    def test_no_color_but_the_tokens_in_the_new_rules(self):
        css = site("app", "tokens.css")
        block = css[css.index("/* Session 412"):css.index("/* ---- panels and controls */")]
        self.assertIsNone(re.search(r"#[0-9A-Fa-f]{3,8}\b|rgba?\(", block))
        self.assertNotIn(chr(0x2014), block)


class TheMenusSayWhichPageIsShown(unittest.TestCase):
    def test_each_kind_of_menu_link_carries_aria_current(self):
        nav = site("components", "Nav.tsx")
        # the single link of a group, a menu's link, an inline sub-link, a sub-list's link, and the grey links at the right
        self.assertEqual(nav.count('aria-current={path === p.href ? "page" : undefined}'), 4)
        self.assertEqual(nav.count('aria-current={path === l.href ? "page" : undefined}'), 1)


class ScrollingBoxesTakeTheKeyboard(unittest.TestCase):
    def test_the_component_is_mounted_once_in_the_layout(self):
        layout = site("app", "layout.tsx")
        self.assertIn('import { ScrollRegions } from "@/components/ScrollRegions";', layout)
        self.assertEqual(layout.count("<ScrollRegions />"), 1)
        self.assertLess(layout.index("</main>"), layout.index("<ScrollRegions />"))

    def test_it_marks_a_scrolling_box_with_nothing_focusable_and_puts_it_back(self):
        c = site("components", "ScrollRegions.tsx")
        self.assertTrue(c.startswith('"use client";'))
        for sel in ("main .overflow-x-auto", "main pre"):
            self.assertIn(sel, c)
        for piece in ("el.tabIndex = 0;", 'el.setAttribute("role", "region")', 'el.setAttribute("aria-label", regionName(el))',
                      'el.removeAttribute("tabindex")', "el.scrollWidth > el.clientWidth + 1", "!el.querySelector(FOCUSABLE)",
                      "new MutationObserver(soon)", 'addEventListener("resize", soon)', 'addEventListener("toggle", soon, true)'):
            self.assertIn(piece, c)
        # its name is the table's caption first: words the page already shows or already gives a screen reader
        self.assertLess(c.index('querySelector("caption")'), c.index('querySelector("figcaption")'))

    def test_its_ring_is_drawn_inside_the_box(self):
        self.assertIn(".brand-a [data-scroll-focus]:focus-visible", site("app", "tokens.css"))


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class EmptyHeaderCells(unittest.TestCase):
    PROBE = """
const C = await import("@/lib/cells");
console.log(JSON.stringify(["", null, undefined, false, "Grid", 0, "0"].map((v) => C.emptyCell(v))));
"""

    def test_what_counts_as_empty(self):
        r = subprocess.run(["node", "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", self.PROBE],
                           cwd=SITE, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1]), [True, True, True, True, False, False, False])

    def test_the_two_shared_tables_draw_an_empty_header_as_a_plain_cell(self):
        tool, chart = site("components", "tool", "ToolPage.tsx"), site("components", "svgchart.tsx")
        self.assertIn('import { emptyCell, scrollRegion } from "@/lib/cells";', tool)
        self.assertIn('import { emptyCell, scrollRegion } from "@/lib/cells";', chart)
        self.assertIn('(emptyCell(h) ? <td key={i} data-empty-head="1" className="px-3 py-1.5" /> : <th key={i} scope="col"', tool)
        self.assertIn('(emptyCell(c) ? <td key={i} data-empty-head="1" className="px-3 py-1.5" /> : <th key={i} scope="row"', tool)
        self.assertIn('(emptyCell(h) ? <td key={i} data-empty-head="1" className="px-3 py-1.5" /> : <th key={i} scope="col"', chart)

    def test_the_shared_tables_frames_are_marked_on_the_server(self):
        tool, chart, cells = site("components", "tool", "ToolPage.tsx"), site("components", "svgchart.tsx"), site("lib", "cells.ts")
        self.assertIn('<div className="overflow-x-auto" {...scrollRegion(caption)}>', tool)
        self.assertIn("{...scrollRegion(`${label}, as a table`)}>", chart)
        # the same three marks the script takes back from a frame that fits (components/ScrollRegions.tsx)
        for mark in ('"data-scroll-focus": "1"', '"data-scroll-role": "1"', '"data-scroll-label": "1"', "tabIndex: 0", 'role: "region"'):
            self.assertIn(mark, cells)
        script = site("components", "ScrollRegions.tsx")
        for back in ("el.dataset.scrollRole", "el.dataset.scrollLabel", 'const ours = el.dataset.scrollFocus === "1";'):
            self.assertIn(back, script)

    def test_the_empty_corner_keeps_the_first_columns_place(self):
        css = site("app", "tokens.css")
        self.assertIn(".brand-a .overflow-x-auto table:not([data-scenario-table]) td[data-empty-head]:first-child {", css)
        self.assertIn(".brand-a .overflow-x-auto table:not([data-scenario-table]) tr.bg-paper td[data-empty-head]:first-child {", css)


class TheBoardsRows(unittest.TestCase):
    def test_no_table_row_is_a_stop_of_the_keyboard(self):
        b = site("components", "board", "BoardView.tsx")
        self.assertIsNone(re.search(r"<tr[^>]*tabIndex", b))
        self.assertNotIn("aria-selected={", b)

    def test_the_rows_name_is_a_button_and_the_row_still_opens_on_a_click(self):
        b = site("components", "board", "BoardView.tsx")
        self.assertIn('<button type="button" aria-pressed={open} data-row-open={row.id} className="text-left">{words}</button>', b)
        self.assertIn('<button type="button" data-row-open={`${w.hub}-da`} className="text-left">', b)
        self.assertIn("onClick={() => onOpen(row.id)}>", b)
        self.assertIn("onClick={() => onOpen(`${w.hub}-da`)}>", b)
        # a blank row (paused, licensed) opens nothing, so it has no button
        self.assertIn('{row.status === "ok" ? <button', b)


class ThePagesOwnFindings(unittest.TestCase):
    def test_demands_ranking_headers_are_no_longer_white_on_white(self):
        d = site("app", "demand", "page.tsx")
        line = next(l for l in d.splitlines() if "data-rank={r.slug}" in l)
        self.assertNotIn("color-surface", line)
        self.assertIn('className="underline"', line)

    def test_the_curtailment_tiles_turn_white_where_the_two_colors_meet(self):
        s = site("app", "curtailment", "Sections.tsx")
        m = re.search(r"export const TILE_WHITE = ([0-9.]+);", s)
        self.assertIsNotNone(m)
        self.assertIn('color: s > TILE_WHITE ? "var(--color-surface)" : "var(--color-ink)"', s)
        # the shade is unchanged
        self.assertIn("var(--color-accent) ${(100 * (0.06 + 0.84 * s)).toFixed(1)}%", s)
        accent, ink, white = hexrgb("#8C1515"), hexrgb("#2E2D29"), [255, 255, 255]

        def over(s_):
            p = 0.06 + 0.84 * s_
            return [c * p + 255 * (1 - p) for c in accent]
        t = float(m.group(1))
        # just below the switch the words are ink, just above white: both at least 3.6 to 1
        self.assertGreaterEqual(contrast(over(t - 0.001), ink), 3.6)
        self.assertGreaterEqual(contrast(over(t + 0.001), white), 3.6)
        # the old switch at 0.5 gave white words under 3 to 1
        self.assertLess(contrast(over(0.5001), white), 3.0)

    def test_links_in_a_block_of_text_are_underlined(self):
        self.assertIn('<a href="#free-energy" className="text-ink underline">Where free energy is</a>', site("app", "curtailment", "page.tsx"))
        self.assertIn('<Link href={c.href} className="text-lg underline">{c.title}</Link>', site("app", "events", "page.tsx"))

    def test_the_replay_days_name_is_its_label(self):
        n = site("app", "network", "Network.tsx")
        self.assertIn('htmlFor="replay-day"', n)
        field = n[n.index('<input id="replay-day"'):]
        field = field[:field.index("/>")]
        self.assertNotIn("aria-label", field)

    def test_the_impact_fields_are_named_by_their_labels(self):
        p = site("app", "impact", "page.tsx")
        for k in ("mw", "capex", "local", "life"):
            with self.subTest(field=k):
                self.assertIn(f'<label className="block" htmlFor="impact-{k}">', p)
                self.assertIn(f'<input id="impact-{k}" name="{k}" type="number"', p)


class TheRecord(unittest.TestCase):
    def test_the_review_lists_every_finding_and_what_waits(self):
        r = src("docs", "reviews", "accessibility-2026-10-20.md")
        self.assertNotIn(chr(0x2014), r)
        for words in ("scrollable-region", "empty-table-header", "focus-order", "color-contrast", "link-in-text-block",
                      "label-content-mismatch", "no name", "aria-current", "For Samuel's ruling"):
            self.assertIn(words, r)

    def test_shots_before_and_after_at_both_widths(self):
        names = sorted(f for f in os.listdir(SHOTS) if f.endswith(".png"))
        stems = {re.sub(r"_(before|after)_(1280|390)\.png$", "", f) for f in names}
        self.assertGreaterEqual(len(stems), 10)
        for stem in stems:
            for when in ("before", "after"):
                for w in ("1280", "390"):
                    with self.subTest(shot=f"{stem}_{when}_{w}"):
                        self.assertIn(f"{stem}_{when}_{w}.png", names)


if __name__ == "__main__":
    unittest.main()
