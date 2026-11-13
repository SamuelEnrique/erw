"""Session 1891: the trader path walked 13 November 2026 (session 1885), fault 5, step 14.

The fault: "clicking a tile sets the address to /board?s=ercot-hb-hubavg-da and opens the markets workbench 1,174 px
below the first screen, beside 'Power, by hub and zone', with no scroll and no focus move: a reader sees nothing happen."

The fix: a click on any control that opens the workbench by s= (BoardView's onOpen: a tile, a headline cell, a row of a
table or of the week, a spike) sets a flag; once the workbench is drawn, an effect takes the flag, scrolls the
workbench's heading into view with block "start" when it is not already in view (smooth, except for a reader whose
system asks for reduced motion: then no smoothing) and moves the focus to it (the heading holds tabIndex -1, so it takes
the focus without joining the tab order). An address that already holds s= as the page opens does not jump: the flag is
set by a click alone. The workbench is not moved or redrawn.

No network, no model, no browser (the built page's check is in the session's report). Nothing here sets the environment
at import.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read().replace(chr(13), "")


def board_view():
    s = src("site", "components", "board", "BoardView.tsx")
    return s[s.index("export function BoardView("):]


def jump_effect():
    v = board_view()
    e = v[v.index("if (!jump.current || !openRow) return;"):]
    return e[:e.index("}, [jumps, openRow]);")]


class TheHeadingTakesTheFocus(unittest.TestCase):
    def test_the_workbench_heading_has_tab_index_minus_one_and_a_mark(self):
        w = src("site", "components", "board", "Workbench.tsx")
        h2 = re.search(r'<h2 className="font-serif text-xl leading-tight text-accent"[^>]*>\{row\.label\}</h2>', w)
        self.assertIsNotNone(h2)
        self.assertIn("tabIndex={-1}", h2.group(0))
        self.assertIn("data-bench-heading={row.id}", h2.group(0))
        # the heading is inside the box that carries data-workbench, the box the effect looks in
        self.assertLess(w.index("data-workbench={row.id}"), h2.start())


class AClickSetsTheFlag(unittest.TestCase):
    def test_on_open_sets_the_flag_and_counts_the_click(self):
        v = board_view()
        on = v[v.index("const onOpen = useCallback("):]
        on = on[:on.index("}, [file, setBench]);")]
        self.assertIn("jump.current = true;", on)
        self.assertIn("setJumps((n) => n + 1);", on)
        self.assertIn("setBench({ s: id });", on)
        # a row that is not shown opens nothing and sets nothing
        self.assertLess(on.index("return;"), on.index("jump.current = true;"))

    def test_the_flag_starts_down_so_an_address_with_s_does_not_jump(self):
        v = board_view()
        self.assertIn("const jump = useRef(false);", v)
        # the flag is raised in onOpen alone
        self.assertEqual(v.count("jump.current = true;"), 1)

    def test_every_opener_on_the_board_goes_through_on_open(self):
        s = src("site", "components", "board", "BoardView.tsx")
        self.assertNotIn("setBench({ s: r.id })", s)
        self.assertNotIn("setBench({ s: row.id })", s)
        # the tile, the row, the headline cell, the week's row and the spike
        for opener in ("onOpen={() => onOpen(r.id)}", "onClick={() => onOpen(row.id)}", "onClick={() => c.r && onOpen(c.r.id)}",
                       "onClick={() => onOpen(`${w.hub}-da`)}", "onClick={() => onOpen(`${s.hub}-rt`)}"):
            self.assertIn(opener, s)
        # setBench opens a row in onOpen alone
        self.assertEqual(len(re.findall(r"setBench\(\{ s: ", s)), 1)


class TheEffectScrollsAndFocuses(unittest.TestCase):
    def test_it_takes_the_flag_once(self):
        e = jump_effect()
        self.assertIn("jump.current = false;", e)

    def test_it_finds_the_heading_of_the_open_row(self):
        self.assertIn('document.querySelector<HTMLElement>(`[data-workbench="${openRow.id}"] [data-bench-heading]`)', jump_effect())

    def test_it_scrolls_to_the_start_and_honours_reduced_motion(self):
        e = jump_effect()
        self.assertIn('matchMedia?.("(prefers-reduced-motion: reduce)").matches', e)
        self.assertIn('h.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });', e)
        # only when the heading is out of view
        self.assertIn("if (box.top < 0 || box.bottom > window.innerHeight) {", e)

    def test_it_moves_the_focus_without_a_second_scroll(self):
        e = jump_effect()
        self.assertIn("h.focus({ preventScroll: true });", e)
        self.assertLess(e.index("scrollIntoView"), e.index("h.focus("))

    def test_the_effect_runs_after_each_click(self):
        v = board_view()
        self.assertIn("}, [jumps, openRow]);", v)
        self.assertIn("const [jumps, setJumps] = useState(0);", v)
        imp = re.search(r'import \{([^}]*)\} from "react";', src("site", "components", "board", "BoardView.tsx"))
        self.assertIn("useRef", imp.group(1))


if __name__ == "__main__":
    unittest.main()
