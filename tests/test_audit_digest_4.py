"""Audit of the Digest and the Roundup, finding 4 (session 10235, docs/reviews/digest-model-audit-2026-11-26.md): the why
line under a story is the scorer's own sentence (a model's words, news_stories.why), and the Digest prints it after
why_line's rules (no hype word, one sentence, no figure the headline gives), with no check that its numbers stand in the
story. The headline check (brief.headlines) also counts the why line among its sources, so a number the scorer wrote
verifies a headline. In the ten newest Digests three printed figures stand in no stored story text:

  6 November, By sector: "adds ~2% to nuclear fleet" under PSEG's 200 MW Salem uprate (the story gives no share; 200 MW
    of a US fleet near 97,000 MW is about 0.2 percent);
  23 October, By sector: "USD 25 billion AI spending commitment" under "Meta's credit risk indicator hits a record high"
    (title and summary give no sum);
  20 October, By sector, a policy action: "an October 20 decision" (the Federal Register title gives no date, no summary
    is stored).

The tests use the stored title and summary of the first two (warehouse/output/news_stories.csv, 26 November 2026) and
pass on main: today's why_line still prints the PSEG line as the issue did (the Meta line it now drops for its words,
not its sum), no rule of why_check reads a number against the story, and the literal check, had it been run against the
story, stops each figure; a headline carrying the why line's sum passes the headline check. Checking the why line against the story changes what
the issues say, so it is for Samuel's ruling. No model, no network."""
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
        "why": "Significant capacity addition at major dual-unit facility adds ~2% to nuclear fleet.",
        "printed": "Capacity addition at dual-unit facility adds ~2% to nuclear fleet."}
META = {"head": "Meta's credit risk indicator hits a record high on its increased AI spending plan",
        "title": "Meta's credit risk indicator hits record high on increased AI spending plan",
        "summary": "Meta's credit risk indicator hits record high on increased AI spending plan Reuters",
        "why": "$25B AI spending commitment raises default risk; signals massive datacenter power demand and capital intensity.",
        "printed": "USD 25 billion AI spending commitment raises default risk"}


class TheWhyLineIsPrintedUnchecked(unittest.TestCase):
    def test_the_pseg_line_is_printed_with_a_share_the_story_does_not_give(self):
        brief, ask = mods()
        line = brief.why_line(PSEG["why"], PSEG["head"], 200)
        self.assertEqual(line, PSEG["printed"])           # as the issue of 6 November printed it
        self.assertEqual(brief.why_check(line, PSEG["head"]), [])
        self.assertEqual(ask.unverified(line, [PSEG["title"], PSEG["summary"]]), ["2"])

    def test_the_meta_line_was_printed_with_a_sum_the_story_does_not_give(self):
        # The issue of 23 October printed the line; today's why_line drops this one for its hollow "signals" clause and its
        # words (rows 7 to 11 of the faults file), not for its sum: no rule of why_check reads a number against the story
        brief, ask = mods()
        printed = META["printed"] + "."
        self.assertFalse([p for p in brief.why_check(printed, META["head"]) if "figure" in p and "headline" not in p])
        self.assertEqual(ask.unverified(printed, [META["title"], META["summary"]]), ["25"])


class TheHeadlineCheckCountsTheWhyLineAsASource(unittest.TestCase):
    def test_a_headline_with_the_why_lines_sum_passes(self):
        brief, _ = mods()
        import pandas as pd
        from types import SimpleNamespace
        clusters = pd.DataFrame([{"cluster_id": "news:meta", "titles": [META["title"]], "summary": META["summary"],
                                  "why": META["why"], "mw": "", "price": ""}])
        head = "Meta plans a USD 25 billion AI spending commitment as its credit risk gauge hits a record"
        real = brief._headline_call
        brief._headline_call = lambda client, model, items, log: ({"news:meta": head}, SimpleNamespace(input_tokens=0, output_tokens=0), 0)
        try:
            heads, _, _ = brief.headlines(None, "stand-in", clusters, lambda m: None)
        finally:
            brief._headline_call = real
        self.assertEqual(heads["news:meta"], head)   # passed: the why line lent its 25


if __name__ == "__main__":
    unittest.main()
