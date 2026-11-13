"""Chain 228 (sessions 1973 to 1999, 13 November 2026): the faults of the Digest of 12 November 2026 and the Roundups of W45
and W46, read as a reader (docs/reviews/periodicals-faults-2026-11-05.md, rows 79 onward). One class a row, on fixtures:
no model, no network."""

import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news"), os.path.join("warehouse", "analysis", "findings"), "scripts"):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402


def cand(label, key, v, pv, pct, table="eia_fuel_spot_prices", unit="USD/MMBtu", reason="", node=""):
    return dict(label=label, key=key, unit=unit, v=v, pv=pv, d=pd.Timestamp("2026-11-11"), pd=pd.Timestamp("2026-11-10"),
                ch=round(v - pv, 4), pct=pct, table=table, reason=reason, node=node, ref="[1]")


def rec(cid, title, sector="datacenter_power", parties="", mw="", price="", why="", links=None, first="2026-11-11T12:00:00Z"):
    return {"cluster_id": cid, "titles": [title], "sector": sector, "parties": parties, "mw": mw, "price": price, "why": why,
            "links": links or [("Bloomberg.com", "https://example.org/a")], "first": first, "region": "USA"}


# 12 November 2026's candidates as the dry run of session 1973 read them (runs/periodicals_dryrun/s1973/)
SPP = cand("SPP SPPSOUTH_HUB day-ahead", "SPP", 20.68, 33.98, -39.14, table="iso_dam_hub_prices", unit="USD/MWh", node="SPPSOUTH_HUB")
HH = cand("Henry Hub natural gas", "Henry Hub natural gas", 3.00, 3.00, 0.0)
BRENT = cand("Brent crude", "Brent crude", 92.14, 90.16, 2.2, unit="USD/bbl")
SPACEX = rec("s", "SpaceX plans USD 74 billion in data center projects in Arizona and Texas", price="$74 billion")


class Row79TheOpeningDoesNotDenyAMove(unittest.TestCase):
    """Row 79: a story's figure leads past a single hub's unnamed move; the opening names that move."""

    def test_the_passed_move_is_named(self):
        op = brief.opening_number([SPP, HH, BRENT], [SPACEX])
        self.assertEqual(op["kind"], "story")
        self.assertEqual(op["passed"]["key"], "SPP")
        line = brief.opening_lines(op, {})[2]
        self.assertNotIn("No price moved enough to lead", line)
        self.assertIn("The day's largest move, SPP SPPSOUTH_HUB day-ahead down 39.1%, is one hub's and no story names it", line)
        self.assertIn("not a warehouse table's", line)

    def test_no_move_past_a_bar_keeps_the_old_sentence(self):
        small = dict(SPP, pct=-4.0, ch=-1.0)
        op = brief.opening_number([small, HH], [SPACEX])
        self.assertIsNone(op["passed"])
        self.assertIn("No price moved enough to lead; this is a reported figure", brief.opening_lines(op, {})[2])

    def test_the_hub_still_leads_when_no_story_states_a_figure(self):
        op = brief.opening_number([SPP, HH], [rec("t", "A story with no figure")])
        self.assertEqual((op["kind"], op["cand"]["key"]), ("mover", "SPP"))


class Row80TheMarketRowMoved(unittest.TestCase):
    """Row 80: the market row is not a price that did not move; an oil headline that settles names the crude benchmarks."""

    def test_a_zero_move_comes_last(self):
        self.assertEqual(brief.best_price([HH, BRENT, SPP], "story:s")["key"], "Brent crude")
        self.assertEqual(brief.best_price([HH], "story:s")["key"], "Henry Hub natural gas")   # alone, it is still the row

    def test_an_oil_headline_names_brent_and_wti(self):
        t = " oil settles $3 higher on attacks on saudi energy sites, strait of hormuz disruptions  ".lower()
        self.assertTrue(brief.names_price("Brent crude", t))
        self.assertTrue(brief.names_price("WTI Cushing crude", " oil jumps after trump says us doesn't need deal with iran "))
        self.assertFalse(brief.names_price("Henry Hub natural gas", t))
        self.assertFalse(brief.names_price("Brent crude", " saudi oil production surges to one of highest levels in years "))
        frame = pd.DataFrame([{"titles": ["Oil settles $3 higher on attacks on Saudi energy sites"], "why": ""}])
        self.assertTrue(brief.price_named("Brent crude", frame))

    def test_a_named_move_leads_the_row(self):
        named = dict(BRENT, named=True)
        spp_named = dict(SPP)
        self.assertEqual(brief.best_price([HH, spp_named, named], "story:s")["key"], "Brent crude")


class Row81TheCloseSaysItsOwnDay(unittest.TestCase):
    """Row 81: the market row names the close's trading day, not a lag of a week; "1 day", not "1 days"."""

    def test_the_market_row(self):
        op = {"kind": "story", "key": "story:s", "rec": SPACEX}
        lines = brief.numbers_block({"cands": [BRENT]}, op, [], {})
        row = next(ln for ln in lines if ln.startswith("- **Market price.**"))
        self.assertIn("Status: observed, EIA's spot close of the trading day 2026-11-11, the newest EIA had published.", row)
        self.assertNotIn("about a week", row)

    def test_the_fuel_lines(self):
        import inspect
        src = inspect.getsource(brief.numbers_today)
        self.assertNotIn("EIA publishes its closes about a week after the day", src)
        self.assertIn("day{'' if age == 1 else 's'} before this issue", src)


class Row82DispatchedIsNotCapacity(unittest.TestCase):
    """Row 82: a story of power dispatched is not named as capacity."""

    def test_the_row(self):
        r = rec("v", "Recent dispatch of VPP power to grid demonstrates viability of coordinated residential storage at scale",
                sector="storage", parties="Sunrun; Tesla", mw="580", links=[("pv magazine USA", "https://example.org/v")])
        line, detail = brief.story_row("Project or capacity", [r], ("storage",), {"v": "Sunrun and Tesla dispatched more than 580 MW"},
                                       None, "a project figure", ("mw",))
        self.assertIn("Storage dispatched, USA: 580 MW (Sunrun, Tesla; pv magazine USA, 2026-11-11)", line)
        self.assertEqual(detail, "story v (mw)")

    def test_a_capacity_story_keeps_its_noun(self):
        r = rec("b", "Developer files for a 300 MW battery in Arizona", sector="storage", mw="300")
        line, _ = brief.story_row("Project or capacity", [r], ("storage",), {}, None, "a project figure", ("mw",))
        self.assertIn("Storage capacity, USA: 300 MW", line)


class Row83TheOutletsName(unittest.TestCase):
    """Row 83: a feed's title is not printed as the outlet's name."""

    def test_names(self):
        self.assertEqual(brief.outlet_name("JPT Homepage"), "JPT")
        self.assertEqual(brief.outlet_name("California State Portal | CA.gov"), "CA.gov")
        self.assertEqual(brief.outlet_name("Reuters"), "Reuters")
        links = [("JPT Homepage", "https://news.google.com/rss/articles/x"), ("Hart Energy", "https://example.org/h")]
        self.assertEqual(brief.link_text(links), "[JPT](https://news.google.com/rss/articles/x) (via Google News), [Hart Energy](https://example.org/h)")
        r = rec("d", "Strathcona pursues growth with a USD 2.1 billion Greenfire deal", sector="deal", parties="Strathcona; Greenfire",
                price="$2.1 billion", links=links)
        line, _ = brief.story_row("Policy, capital or reliability", [r], ("deal",), {}, None, "a figure", ("money",))
        self.assertIn("(Strathcona, Greenfire; JPT, 2026-11-11)", line)


class Row84NoPartyTwice(unittest.TestCase):
    """Row 84: a line with no figure does not print the parties its headline names; beside a figure the field stays as
    the Roundup reads it."""

    def test_the_four_lines_of_12_november(self):
        self.assertEqual(brief.detail({"mw": "", "price": "", "parties": "Repsol"},
                                      "Repsol takes final investment decision on third large-scale green hydrogen project in Spain"), "")
        self.assertEqual(brief.detail({"mw": "580", "price": "", "parties": "Sunrun; Tesla"},
                                      "Sunrun and Tesla dispatched more than 580 MW from over 140,000 home batteries in September"), "")

    def test_a_party_the_headline_lacks(self):
        self.assertEqual(brief.detail({"mw": "", "price": "", "parties": "Google; AEP; Bloom Energy"}, "Google signs a fuel-cell deal"),
                         "Also named: AEP, Bloom Energy. ")

    def test_beside_a_figure_the_field_stays(self):
        import roundup
        out = brief.detail({"mw": "702", "price": "$4 billion", "parties": "Google; AEP"}, "Google and AEP sign a fuel-cell deal")
        self.assertEqual(out, "702 MW; USD 4 billion; parties: Google; AEP. ")
        md = f"1. **Google and AEP sign a fuel-cell deal** (datacenter power)  \n   Why. {out}Sources: [X](https://example.org/x)\n"
        items = roundup.issue_items(md)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][3], 702.0)
        self.assertEqual(len(items[0][2]), 2)


class Row85ThePolicyLineCloses(unittest.TestCase):
    """Row 85: a policy action whose why line fails closes on its bracket, no empty colon, no double space."""

    KINDS = {"press_release": "news release", "notice": "notice"}

    def test_no_why(self):
        r = {"title": "Energy Department Closes $480 Million Loan", "agency": "DOE", "action_type": "press_release", "why": "",
             "source_url": "https://www.energy.gov/x"}
        line = brief.policy_line(r, self.KINDS)
        self.assertTrue(line.endswith("(DOE news release, policy action). [DOE](https://www.energy.gov/x)"), line)
        self.assertNotIn("  ", line)
        self.assertNotIn("):", line)

    def test_with_a_why(self):
        r = {"title": "Long Mott Energy, LLC; Long Mott Generating Station; Construction Permit", "agency": "NRC", "action_type": "notice",
             "why": "The permit, numbered CPAR-3, authorizes Long Mott Energy to begin building the reactor facility.",
             "source_url": "https://www.federalregister.gov/x"}
        line = brief.policy_line(r, self.KINDS)
        self.assertIn("(NRC notice, policy action): The permit", line)
        self.assertTrue(line.endswith(" [NRC](https://www.federalregister.gov/x)"))


class Row86OneMoneyStyle(unittest.TestCase):
    """Row 86: the titles printed as published carry the issue's money style."""

    def test_the_also_line(self):
        x = {"kind": "sector", "sector": "datacenter_power", "links": [("POWER Magazine", "https://example.org/p")],
             "title": "Rowan Digital Infrastructure Secures $1.5 Billion in Financing for Hyperscale Development Platform"}
        line = brief.also_line([x])
        self.assertIn("Rowan Digital Infrastructure Secures USD 1.5 billion in Financing for Hyperscale Development Platform ([POWER", line)
        self.assertNotIn("$", line)

    def test_the_policy_title(self):
        r = {"title": "Energy Department Closes $480 Million Loan to Expand American Energy Production", "agency": "DOE",
             "action_type": "press_release", "why": "", "source_url": "https://www.energy.gov/x"}
        self.assertIn("Energy Department Closes USD 480 million Loan", brief.policy_line(r, {"press_release": "news release"}))


class Row87TheRecordUntilNow(unittest.TestCase):
    """Row 87: the record until now is the highest value before the new point, fresh points included; the held record is
    kept beside it, as Wyoming's gas generation of July and August 2026 needs it."""

    CFG = {"record_min_points": {"monthly": 24}, "record_stood_points": {"monthly": 12}, "record_min_margin_sigmas": 3.0, "version": "t"}

    def series(self, fresh):
        import numpy as np
        import findings_scanner as fs
        vals = [250000.0 + 20000.0 * ((i * 7) % 5) for i in range(36)]
        vals[12] = 765381.0                       # the held record (July 2024 in the table)
        vals += fresh
        s = fs.Series()
        s.table, s.key, s.key_str = "eia_state_generation_monthly", {"entity": "eia:generation:WY:NG", "variable": "net_generation"}, "k"
        s.days = np.array([np.datetime64("2023-01-01", "M") + np.timedelta64(i, "M") for i in range(len(vals))]).astype("datetime64[D]")
        s.v = np.array(vals)
        s.lo = s.hi = s.v
        s.unit, s.grain, s.sub, s.source, s.note, s.geo = "MWh", "monthly", False, "eia", "", "WY"
        return fs, s, 36

    def test_a_fresh_point_had_beaten_it(self):
        fs, s, f = self.series([1034450.83, 1060503.7])
        flags = [x for x in fs.rule_record(s, self.CFG, "2026-11-12", len(s.v), f) if x["direction"] == "high"]
        self.assertEqual(len(flags), 1)
        c = flags[0]["compared"]
        self.assertEqual((c["old_record"], c["old_record_date"]), (1034450.83, "2026-01-01"))
        self.assertEqual((c["held_record"], c["held_record_date"]), (765381.0, "2024-01-01"))
        self.assertAlmostEqual(c["margin"], 1060503.7 - 1034450.83)
        self.assertAlmostEqual(flags[0]["strength"], round(abs(1060503.7 - 1034450.83) / c["sigma"], 4), places=3)
        import daily_chart as dc
        fl = dict(flags[0], statistic="monthly value", label="x")
        fact = dc.fact_from_flag(fl)
        self.assertIn("The record until now was 1,034,451 MWh, in January 2026.", fact)
        self.assertIn("Before the months new in this scan, the record was 765,381 MWh, in January 2024.", fact)

    def test_no_fresh_point_beat_it(self):
        fs, s, f = self.series([500000.0, 1060503.7])
        c = [x for x in fs.rule_record(s, self.CFG, "2026-11-12", len(s.v), f) if x["direction"] == "high"][0]["compared"]
        self.assertEqual(c["old_record"], 765381.0)
        self.assertNotIn("held_record", c)


class Row88TheChartsStoryNamesItsMeasure(unittest.TestCase):
    """Row 88: the chart's line ties it to a story only when the shared words name the measure; the headline quoted is the
    one the issue printed."""

    WY = {"source": "scanner", "key": "wy", "table": "eia_state_generation_monthly",
          "series_key": "entity=eia:generation:WY:NG|variable=net_generation|freq=P1M",
          "fact": "Net generation from natural gas in Wyoming: 1,060,504 MWh in August 2026",
          "flag": {"rule": "record", "strength": 11.0}}

    def test_a_party_named_generation_is_no_reason(self):
        import daily_chart as dc
        opg = {"titles": ["OPG set to revise timeline and cost of first SMR unit"], "sector": "nuclear", "why": "",
               "parties": "Ontario Power Generation", "head": "Ontario Power Generation says first Darlington SMR unit will be late"}
        c = dict(self.WY, _relevance=dc.relevance(self.WY, [opg]))
        self.assertEqual(c["_relevance"][2], ["generation"])
        words = dc.how_words(c)
        self.assertNotIn("most related", words)
        self.assertIn("No top story of the day names this measure.", words)

    def test_a_story_of_the_place_and_fuel(self):
        import daily_chart as dc
        st = {"titles": ["Wyoming gas plants run flat out"], "sector": "generation", "why": "", "parties": "",
              "head": "Wyoming's gas plants run at a record"}
        c = dict(self.WY, _relevance=dc.relevance(self.WY, [st]))
        words = dc.how_words(c)
        self.assertIn("It is the candidate most related to the day's top stories: it shares", words)
        self.assertIn("\"Wyoming's gas plants run at a record\"", words)


class Row89TheSubjectCarriesTheNews(unittest.TestCase):
    """Row 89: with a story's figure as the opening, the subject is the top story's headline with no figure."""

    def test_12_november(self):
        op = {"kind": "story", "key": "story:s", "rec": dict(SPACEX, head="SpaceX plans USD 74 billion in data center projects in Arizona and Texas")}
        self.assertEqual(brief.subject_line(op, "2026-11-12"), "ERW Daily | SpaceX plans data center projects in Arizona and Texas")

    def test_in_kept_after_invests(self):
        self.assertEqual(brief.subject_clause("Repsol invests USD 1 billion in solar parks"), "Repsol invests in solar parks")

    def test_long_and_empty(self):
        long = "Developer plans USD 5 billion in data center campuses across Arizona, Texas, Ohio, Georgia, Virginia and Pennsylvania"
        out = brief.subject_clause(long)
        self.assertLessEqual(len(out), 70)
        self.assertNotIn("...", out)
        self.assertNotRegex(out, r"\d")
        op = {"kind": "story", "key": "story:s", "rec": dict(SPACEX, head="USD 74 billion")}
        self.assertEqual(brief.subject_line(op, "2026-11-12"), "ERW Daily | 12 November 2026")
        self.assertEqual(brief.subject_line({"kind": None, "key": ""}, "2026-11-12"), "ERW Daily | 12 November 2026")


if __name__ == "__main__":
    unittest.main()
