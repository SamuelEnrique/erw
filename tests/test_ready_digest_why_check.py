"""wip/ready-digest-why-check (session 11406, chain 770, part C): the other choice of the Digest audit of 26 November,
finding 4 (docs/reviews/digest-model-audit-2026-11-26.md), readied for Samuel's ruling, not requested.

On main the Digest's why line is printed with no number check against its story, and it is one of the headline
check's sources, so a number the scorer wrote verifies a headline. On this branch every number of a why line is read
against the cluster's titles and summary (story_sources) and a line that fails is dropped, as why_line already drops a
line that fails its rule; the why line leaves the headline check's sources. Measured on the ten issues: 3 why lines
would not have printed (6 November's "adds ~2% to nuclear fleet", about 0.2 percent; 23 October's "USD 25 billion";
20 October's "an October 20 decision"); the stored issues are untouched. The audit's test (tests/test_audit_digest_4.py
on wip/audit-digest-4) is carried, turned round. No model, no network."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "chat")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))


def mods():
    try:
        import brief  # noqa: E402
        import ask  # noqa: E402
    except ImportError as exc:
        raise unittest.SkipTest(f"brief or ask does not import here: {exc}")
    return brief, ask


PSEG = {"head": "PSEG executives say Salem nuclear plant expects a 200 MW uprate",
        "title": "Salem power plant planning 200-MW uprate",
        "summary": ("The Salem nuclear power plant is expected to get a 200-MW uprate, executives from PSEG, the co-owners and "
                    "operators of the Hancocks Bridge, N.J., facility, said in the utility's recent third quarter earnings call."),
        "why": "Significant capacity addition at major dual-unit facility adds ~2% to nuclear fleet."}
META = {"head": "Meta's credit risk indicator hits a record high on its increased AI spending plan",
        "title": "Meta's credit risk indicator hits record high on increased AI spending plan",
        "summary": "Meta's credit risk indicator hits record high on increased AI spending plan Reuters",
        "why": "$25B AI spending commitment raises default risk; signals massive datacenter power demand and capital intensity."}


class TheWhyLineIsChecked(unittest.TestCase):
    def test_the_pseg_line_is_dropped(self):
        brief, _ = mods()
        r = {"titles": [PSEG["title"]], "summary": PSEG["summary"]}
        self.assertEqual(brief.why_line(PSEG["why"], PSEG["head"], 200, brief.story_sources(r)), "")
        self.assertEqual(brief.why_line(PSEG["why"], PSEG["head"], 200), "Capacity addition at dual-unit facility adds ~2% to nuclear fleet.")

    def test_a_line_whose_numbers_the_story_gives_stays(self):
        brief, _ = mods()
        r = {"titles": ["Utility files for 300 MW of batteries"], "summary": "The utility asked to add 300 MW of storage by 2028."}
        line = brief.why_line("Adds storage by 2028 to a fast-growing system.", "Utility files for 300 MW of batteries", None, brief.story_sources(r))
        self.assertIn("2028", line)

    def test_the_why_line_lends_no_number_to_a_headline(self):
        brief, _ = mods()
        import pandas as pd
        from types import SimpleNamespace
        clusters = pd.DataFrame([{"cluster_id": "news:meta", "titles": [META["title"]], "summary": META["summary"],
                                  "why": META["why"], "mw": "", "price": ""}])
        head = "Meta plans a USD 25 billion AI spending commitment as its credit risk gauge hits a record"
        real = brief._headline_call
        brief._headline_call = lambda client, model, items, log: ({"news:meta": head}, SimpleNamespace(input_tokens=0, output_tokens=0), 0)
        try:
            with self.assertRaises(RuntimeError):     # asked again, the stand-in returns the same: the brief stops
                brief.headlines(None, "stand-in", clusters, lambda m: None)
        finally:
            brief._headline_call = real


if __name__ == "__main__":
    unittest.main()
