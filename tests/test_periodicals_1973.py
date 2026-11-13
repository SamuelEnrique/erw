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


class Row90TheFirstLine(unittest.TestCase):
    """Row 90: the first line reads in order, keeps the form STAMP_END reads, and says why a window is long."""

    def write(self, d, *days):
        for day in days:
            with open(os.path.join(d, f"{day}.md"), "w", encoding="utf-8") as f:
                f.write("x\n")

    def test_12_november(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "2026-11-05", "2026-11-06")
            line = brief.stamp_line(96, pd.Timestamp("2026-11-08T22:56:00Z"), pd.Timestamp("2026-11-12T22:56:00Z"), 262, folder=d)
        self.assertEqual(line, "ERW's weekday brief of energy news for the 96 hours to 2026-11-12 22:56 UTC (the window opened "
                               "2026-11-08 22:56 UTC): 262 scored stories, the first issue since 6 November.")
        self.assertEqual(brief.STAMP_END.search(line).group(1), "2026-11-12 22:56")
        self.assertEqual(line.count(" from "), 0)

    def test_a_monday_after_a_friday_says_nothing_more(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "2026-11-13")
            line = brief.stamp_line(72, pd.Timestamp("2026-11-13T22:56:00Z"), pd.Timestamp("2026-11-16T22:56:00Z"), 300, folder=d)
        self.assertTrue(line.endswith("): 300 scored stories."), line)


class Row91AMoverIsNotAnItem(unittest.TestCase):
    """Row 91: a mover whose reason links a story printed above stays in What moved most, and the hard check passes."""

    def test_brent_stays(self):
        url = "https://news.google.com/rss/articles/oil?oc=5"
        L = ["## What moved", "", "2. **Oil settles USD 3 higher on attacks on Saudi energy sites** (oil)  ",
             f"   Sources: [Reuters]({url}) (via Google News)", "", "### ERW's Numbers Today", "",
             f"- Brent crude: 92.14 USD/bbl on 2026-11-11, up 1.98 USD/bbl (2.2%) from 90.16 USD/bbl on 2026-11-10 [5]. Reason, from the "
             f"day's stories: Attacks on Saudi oil sites. ([Reuters]({url}) (via Google News))"]
        out = brief.drop_repeated_items(L, lambda _m: None)
        self.assertTrue(any(ln.startswith("- Brent crude: 92.14") for ln in out))
        self.assertEqual(brief.assert_unique(out), 1)

    def test_unchanged_is_not_a_largest_move(self):
        # row 92: 12 November's six candidates, Henry Hub and WTI unchanged
        ercot = cand("ERCOT HB_NORTH day-ahead", "ERCOT", 40.34, 38.24, 5.49, table="iso_dam_hub_prices", unit="USD/MWh")
        wti = cand("WTI Cushing crude", "WTI Cushing crude", 89.62, 89.62, 0.0, unit="USD/bbl")
        cands = sorted([SPP, ercot, BRENT, HH, wti], key=lambda c: (-abs(c["pct"]), c["label"]))
        L = brief.mover_list(cands, None)
        self.assertIn("**What moved most** (the 3 largest moves in percent", L[1])
        self.assertEqual(sum(1 for ln in L if brief.MOVER_LINE.match(ln)), 3)
        self.assertEqual(brief.unchanged_line(cands), ["- Unchanged: Henry Hub natural gas, WTI Cushing crude."])
        self.assertFalse(any("(0.0%)" in ln for ln in L))
        one = brief.mover_list([SPP, HH], None)
        self.assertIn("(the largest move in percent", one[1])

    def test_a_story_line_is_still_dropped(self):
        L = ["1. **A deal** (deal)  ", "   Sources: [X](https://example.org/a)", "- A deal (deal). [X](https://example.org/a)"]
        out = brief.drop_repeated_items(L, lambda _m: None)
        self.assertEqual(len(out), 2)


class Row95TheWeeklySubjectHasNoOutletFigure(unittest.TestCase):
    """Row 95: the Roundup's subject with no move to lead carries the headline's clause with no figure."""

    def test_w46(self):
        import roundup
        self.assertEqual(roundup.subject_line(None, "SpaceX Plans $74 Billion Data Center Projects in Arizona, Texas"),
                         "ERW Weekly | SpaceX Plans Data Center Projects in Arizona, Texas")
        self.assertEqual(roundup.subject_line(None, "$74 Billion"), "ERW Weekly | the week's energy news")

    def test_a_cut_does_not_split_a_name(self):
        out = brief.subject_clause("Gingerah Energy refers 1,000 MW data centre complex with 5GWh battery in Western Australia to EPBC Act")
        self.assertEqual(out, "Gingerah Energy refers data centre complex with battery")


class Row96TheDealSaysWhoseSum(unittest.TestCase):
    """Row 96: the deal of the week names the outlet its sum was read from."""

    def test_strathcona(self):
        import roundup
        r = {"deal_type": "m_and_a", "buyer": "Strathcona", "seller": "Greenfire", "asset": "Greenfire", "event_date": "2026-11-11T04:52:11Z",
             "source": "Hart Energy"}
        self.assertEqual(roundup.deal_words(r, "sum"), "Strathcona, Greenfire (acquisition, 2026-11-11; the sum as Hart Energy reported it)")
        self.assertEqual(roundup.deal_words(r), "Strathcona, Greenfire (acquisition, 2026-11-11)")
        self.assertIn("the MW as JPT reported it", roundup.deal_words(dict(r, source="JPT Homepage"), "MW"))
        import check_roundup as cr
        line = ("- **Deal of the week, by US dollars:** USD 2 billion, " + roundup.deal_words(r, "sum") + ".")
        self.assertEqual(cr.FIVE_DEAL_V.search(line).group(1), "USD 2 billion")


class Row97TheStandInMoved(unittest.TestCase):
    """Row 97: a stand-in price move passes the opening's bar; W46's +0.3% does not."""

    def five(self, fuels):
        import tempfile
        from unittest import mock
        import roundup
        utc = "UTC"

        def fuel(label, unit, v1, v0):
            return {"label": label, "a": {"value": v1, "unit": unit, "ts_utc": pd.Timestamp("2026-11-11", tz=utc)},
                    "b": {"value": v0, "unit": unit, "ts_utc": pd.Timestamp("2026-11-04", tz=utc)}, "ref": "[5]"}
        dcs = pd.DataFrame([{"entity_id": "dc:x", "first_story_at": "2026-11-12T10:00:00Z", "capacity_mw": "1400", "operator": "",
                             "site_name": "", "city": "Kemps Creek", "state": "", "confidence": "0.55"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(roundup, "read_table", lambda n: dcs if n == "datacenter_projects" else None), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            L = roundup.five_numbers("2026-W46", pd.Timestamp("2026-11-09", tz=utc), pd.Timestamp("2026-11-12 22:00", tz=utc),
                                     {"fuel": [fuel(*f) for f in fuels]}, lambda *a: None, {}, None)
        return next(ln for ln in L if "datacenter load" in ln)

    def test_w46(self):
        row = self.five([("Henry Hub natural gas", "USD/MMBtu", 3.00, 2.63), ("WTI Cushing crude", "USD/bbl", 89.62, 91.73),
                         ("Brent crude", "USD/bbl", 92.14, 91.84)])
        self.assertNotIn("Brent crude closed", row)
        self.assertNotIn("WTI Cushing crude closed", row)   # -2.3%, under the bar too
        self.assertTrue(row.endswith("no other price moved 3% or more on the week (10% for a hub's weekly mean)."), row)


class Row98AMarketMoveTheWarehouseHolds(unittest.TestCase):
    """Row 98: a story that names a benchmark is told the warehouse's close, and no party is asked of a market move."""

    FACTS = {"fuel": [
        {"label": lbl, "a": {"value": a, "unit": u, "ts_utc": pd.Timestamp("2026-11-11", tz="UTC")},
         "b": {"value": b, "unit": u, "ts_utc": pd.Timestamp("2026-11-04", tz="UTC")}, "ref": "[5]"}
        for lbl, u, a, b in (("Henry Hub natural gas", "USD/MMBtu", 3.00, 2.63), ("WTI Cushing crude", "USD/bbl", 89.62, 91.73),
                             ("Brent crude", "USD/bbl", 92.14, 91.84))]}

    def test_the_oil_story(self):
        import roundup
        r = {"cluster_id": "o", "titles": ["Oil settles $3 higher on attacks on Saudi energy sites, Strait of Hormuz disruptions"],
             "why": "Attacks on Saudi Arabian oil infrastructure and Strait of Hormuz transit risk trigger price move.", "parties": "",
             "mw": "", "price": "$3", "n": 1, "links": [("Reuters", "https://example.org/o")], "sector": "oil"}
        b = roundup.bench_of(r, self.FACTS)
        self.assertEqual(b["label"], "Brent crude")
        gap = roundup.evidence_gap(r, r["titles"][0], None, None, b)
        self.assertIn("the warehouse's Brent crude close is 92.14 USD/bbl on 2026-11-11, against 91.84 on 2026-11-04 [5]", gap)
        self.assertNotIn("not a warehouse table's", gap)
        self.assertNotIn("no party is named", gap)

    def test_a_story_naming_no_benchmark(self):
        import roundup
        r = {"titles": ["Repsol takes final investment decision on a hydrogen project"], "why": ""}
        self.assertIsNone(roundup.bench_of(r, self.FACTS))
        self.assertEqual(roundup.bench_of({"titles": ["WTI slips as stocks build"], "why": ""}, self.FACTS)["label"], "WTI Cushing crude")


class Row99OneColon(unittest.TestCase):
    def test_the_deals_status(self):
        import roundup
        op = roundup.opening_number({"deal": {"usd": 2e9, "text": "USD 2 billion, Strathcona, Greenfire"}})
        self.assertEqual(op["key"], "deal")
        line = roundup.opening_lines(op)[2]
        self.assertEqual(line.count(":"), 1, line)
        self.assertIn("Status: reported, extracted from the week's stories", line)


class Rows100To103W45OnTheStack(unittest.TestCase):
    """Rows 100 to 103, from the W45 dry run on the stack (session 3312)."""

    def test_100_the_masthead_names_the_real_time_tables(self):
        import roundup
        end, cut = pd.Timestamp("2026-11-08 23:59", tz="UTC"), pd.Timestamp("2026-11-08 23:26", tz="UTC")
        L = roundup.masthead_lines("2026-W45", end, cut, None, "A head.", "", pd.Timestamp("2026-11-05 23:07", tz="UTC"),
                                   pd.Timestamp("2026-11-05 07:45", tz="UTC"))
        self.assertIn("; the real-time price tables reach 5 November", L[2])
        self.assertNotIn("the week's tables", L[2])

    def test_101_the_opening_move_says_why(self):
        import roundup
        move = {"label": "Brent crude", "pct": -18.6, "ch": -22.32,
                "text": "Brent crude closed at 97.83 USD/bbl on 2026-11-06, against 120.15 USD/bbl on 2026-10-30 (-22.32 USD/bbl, -18.6%) [5]"}
        stories = pd.DataFrame([{"titles": ["Oil prices slump as Gulf shipping resumes"], "parties": "",
                                 "why": "Tanker traffic through the Strait of Hormuz resumed on 4 November after a ceasefire.",
                                 "links": [("Reuters", "https://example.org/r")]}])
        op = roundup.opening_number({"moves": [move], "move": move}, stories)
        self.assertEqual(op["key"], "move")
        line = roundup.opening_lines(op)[2]
        self.assertIn("Status: calculated from observed prices (the warehouse's tables). Reason, from the week's stories: Tanker traffic", line)
        self.assertNotIn("day's stories", line)

    def test_101_a_failing_line_names_the_story(self):
        import roundup
        move = {"label": "Brent crude", "pct": -18.6, "ch": -22.32, "text": "Brent crude closed at 97.83 USD/bbl on 2026-11-06 [5]"}
        stories = pd.DataFrame([{"titles": ["Oil prices tumble $20 in a week"], "parties": "", "why": "Oil prices fell.",
                                 "links": [("Reuters", "https://example.org/r")]}])
        line = roundup.opening_lines(roundup.opening_number({"moves": [move], "move": move}, stories))[2]
        self.assertIn("Named in the week's stories: Oil prices tumble USD 20 in a week ([Reuters](https://example.org/r)).", line)

    def test_104_a_story_of_higher_prices_names_no_fall(self):
        import roundup
        self.assertFalse(brief.agrees(" conocophillips boosts dividend on higher oil prices ", -18.6))
        self.assertTrue(brief.agrees(" oil settles $3 higher on attacks ", 2.2))
        self.assertTrue(brief.agrees(" oil prices swing higher then lower ", -3.0))
        self.assertTrue(brief.agrees(" anything ", None))
        move = {"label": "Brent crude", "pct": -18.6, "ch": -22.32, "text": "Brent crude closed at 97.83 USD/bbl on 2026-11-06 [5]"}
        stories = pd.DataFrame([{"titles": ["ConocoPhillips boosts dividend after beating estimates on higher oil prices"], "parties": "",
                                 "why": "", "links": [("OilPrice.com", "https://example.org/c")]}])
        self.assertFalse(brief.price_named("Brent crude", stories, -18.6))
        op = roundup.opening_number({"moves": [move], "move": move}, stories)
        self.assertEqual(op["key"], "move")   # by the unnamed benchmark's bar
        self.assertNotIn("ConocoPhillips", roundup.opening_lines(op)[2])

    def test_102_iea(self):
        self.assertEqual(brief.outlet_name("IEA - International Energy Agency"), "IEA")

    def test_103_investment_in(self):
        import roundup
        # buyer holds the money side, seller the company raising (finance_words; deal_cells swaps them for the table)
        r = {"deal_type": "equity_raise", "buyer": "Blackstone", "seller": "Mitsubishi", "asset": "Mitsubishi's stake in LNG Canada",
             "event_date": "2026-11-05"}
        self.assertIn("Blackstone's investment in Mitsubishi's stake in LNG Canada", roundup.finance_words(r))
        loan = dict(r, deal_type="debt", buyer="Apterra", seller="Calibrant Energy", asset="solar and storage projects")
        self.assertIn("Apterra's loan for Calibrant Energy's solar and storage projects", roundup.finance_words(loan))


class Row105AGatedPointerGoes(unittest.TestCase):
    """Row 105: in an email, a link to a page in review whose words only point is dropped with its clause."""

    def test_the_lines(self):
        import email_digest as ed
        g = lambda s: ed.gate_links(s, {})   # no page live
        self.assertEqual(g("Table `t`, series `s`: [the table and its download](/data#t)."), "Table `t`, series `s`.")
        self.assertEqual(g("No top story of the day names this measure. [How the chart is chosen](/data/methods/x)."),
                         "No top story of the day names this measure.")
        self.assertEqual(g("Template `w`; every template's latest run is on [/research](/research)."), "Template `w`.")
        self.assertEqual(g("Table: `energy_deals` (13 deals shown; [the whole table](/data#energy_deals)). Extracted."),
                         "Table: `energy_deals` (13 deals shown). Extracted.")
        self.assertEqual(g("See [the deals tracker](/deals) for more."), "See the deals tracker for more.")
        self.assertEqual(ed.gate_links("[How the chart is chosen](/x).", {"/x": "live"}), "[How the chart is chosen](/x).")


class Row107TheKeyNamesTheFiguresStory(unittest.TestCase):
    """Row 107: a block row's key names the story whose scored field gave the figure, not the cluster's id."""

    def test_strathcona(self):
        base = {"cluster_id": "news:808f", "sig": 7, "ai_power_relevance": "0", "ai": 0, "sector": "deal", "region": "Canada",
                "why": "", "mw": "", "parties": "Strathcona; Greenfire", "summary": "", "source_url": "u", "significance": "7"}
        s = pd.DataFrame([dict(base, event_id="news:808f", event_date="2026-11-11T04:52:11Z", price_mentioned="",
                               title="Strathcona's Greenfire Deal Leaves Few Oil Sands Targets Standing", source="Hart Energy",
                               source_url="https://example.org/h"),
                          dict(base, event_id="news:f3e7", event_date="2026-11-12T18:01:03Z", price_mentioned="$2.1 Billion",
                               title="Strathcona Pursues Growth With $2.1 Billion Greenfire Deal", source="JPT Homepage",
                               source_url="https://example.org/j")])
        c = brief.build_clusters(s).to_dict("records")[0]
        self.assertEqual((c["price"], c["price_id"]), ("$2.1 Billion", "news:f3e7"))
        line, detail = brief.story_row("Policy, capital or reliability", [c], ("deal",), {}, None, "a figure", ("money",))
        self.assertEqual(detail, "story news:f3e7 (price)")


class Row110AGasRallyNamesHenryHub(unittest.TestCase):
    """Row 110: a natural gas headline that rallies names Henry Hub, and the Roundup asks the week's stories, not only the
    printed ones."""

    def test_the_words(self):
        t = " record lng demand ignites natural gas forward rally, but will it last? "
        self.assertTrue(brief.names_price("Henry Hub natural gas", t))
        self.assertFalse(brief.names_price("Henry Hub natural gas", " gas plant rises in texas "))
        self.assertFalse(brief.names_price("Brent crude", t))

    def test_the_w46_opening(self):
        import roundup
        hh = {"label": "Henry Hub natural gas", "pct": 14.1, "ch": 0.37,
              "text": "Henry Hub natural gas closed at 3.00 USD/MMBtu on 2026-11-11, against 2.63 USD/MMBtu on 2026-11-04 (+0.37 USD/MMBtu, +14.1%) [5]"}
        week = pd.DataFrame([{"titles": ["Record LNG Demand Ignites Natural Gas Forward Rally, but Will It Last?"], "parties": "",
                              "why": "Strong feedgas demand from LNG and production outages are pushing natural gas prices higher across the US and Canada.",
                              "links": [("Natural Gas Intelligence", "https://example.org/n")]}])
        op = roundup.opening_number({"moves": [hh], "move": hh, "deal": {"usd": 2e9, "text": "USD 2 billion, Strathcona, Greenfire"}}, week)
        self.assertEqual(op["key"], "move")
        self.assertIn("Reason, from the week's stories: Strong feedgas demand", roundup.opening_lines(op)[2])
        src = open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8").read()
        self.assertIn("op = opening_number(picked, clusters)", src)


class Rows111To113The11NovemberDryRun(unittest.TestCase):
    """Rows 111 to 113, from the dry run of 11 November on the stack (session 3332)."""

    def test_111_and_112_the_rigzone_row(self):
        r = rec("m", "US Oil and Gas M&A Activity Accelerates With $12.6 Billion in Third-Quarter Deals", sector="deal",
                price="$12.6 billion", links=[("Rigzone", "https://example.org/r")])
        line, _ = brief.story_row("Policy, capital or reliability", [r], ("deal",), {}, None, "a figure", ("money",))
        self.assertIn("Deals in total, USA: USD 12.6 billion (Rigzone, 2026-11-11)", line)
        self.assertNotIn("Rigzone; Rigzone", line)
        one = rec("d", "Strathcona pursues growth with a USD 2.1 billion deal", sector="deal", price="$2.1 billion", parties="Strathcona")
        self.assertIn("Deal value, USA", brief.story_row("x", [one], ("deal",), {}, None, "a figure", ("money",))[0])

    def test_113_saudi(self):
        self.assertTrue(brief.party_in_head("Saudi Arabia", "Saudi Oil Production Surges to One of Highest Levels in Years"))
        self.assertFalse(brief.party_in_head("United Kingdom", "United Airlines buys fuel"))
        self.assertEqual(brief.detail({"mw": "", "price": "", "parties": "Saudi Arabia; OPEC"},
                                      "Saudi Oil Production Surges to One of Highest Levels in Years"), "Also named: OPEC. ")


class Row114AThinOrUnscoredWindow(unittest.TestCase):
    """Row 114: a window that holds few stories, or many unscored ones, is said; '1 scored story'."""

    def frame(self, n_scored, n_unscored, day="2026-11-10T12:00:00Z"):
        rows = [{"event_date": day, "scored_at": "2026-11-10T13:00:00Z"}] * n_scored + [{"event_date": day, "scored_at": ""}] * n_unscored
        return pd.DataFrame(rows)

    def test_the_lines(self):
        start, now = pd.Timestamp("2026-11-06T22:56Z"), pd.Timestamp("2026-11-10T22:56Z")
        self.assertEqual(brief.held_lines(self.frame(1, 2), start, now, 96),
                         ["The warehouse holds 3 stories of these 96 hours, where a weekday usually brings several hundred.", ""])
        self.assertEqual(brief.held_lines(self.frame(400, 234), start, now, 96),
                         ["A further 234 stories of the window are held but not scored yet, so this issue does not rank them.", ""])
        self.assertEqual(brief.held_lines(self.frame(400, 5), start, now, 96), [])
        line = brief.stamp_line(96, start, now, 1, folder=os.path.join(ROOT, "docs", "digest"))
        self.assertIn("): 1 scored story", line)


class Rows115To117W44OnTheStack(unittest.TestCase):
    """Rows 115 to 117, from W44 on the stack (session 3334)."""

    def test_115_european_gas_names_no_henry_hub_move(self):
        t = " natural gas prices hit 100 euros per mwh as eu confronts refinery closures and diesel shortage "
        self.assertFalse(brief.names_price("Henry Hub natural gas", t))
        self.assertTrue(brief.names_price("Henry Hub natural gas", " henry hub gas prices slump in europe's mild weather "))
        self.assertTrue(brief.names_price("Henry Hub natural gas", " us natural gas prices fall on mild weather "))

    def test_116_the_cut_goes_back_to_the_comma(self):
        import roundup
        out = roundup.head_clause("EQT to Buy Range Resources, Creating Largest US Gas Producer", 37)
        self.assertEqual(out, "EQT to Buy Range Resources")

    def test_117_thousands(self):
        import inspect, roundup
        self.assertIn("{len(s):,} scored stories", inspect.getsource(roundup.main))
        line = brief.stamp_line(168, pd.Timestamp("2026-10-26T00:00Z"), pd.Timestamp("2026-11-01T23:59Z"), 1253, folder=os.path.join(ROOT, "docs", "digest"))
        self.assertIn("1,253 scored stories", line)


class Row118TheLoadRowSaysWhatItLeavesOut(unittest.TestCase):
    """Row 118: the datacenter load row says how many larger loads of the week name no operator or site."""

    def test_w44(self):
        import tempfile
        from unittest import mock
        import roundup
        dcs = pd.DataFrame([
            {"entity_id": "dc:v", "first_story_at": "2026-10-30T10:00:00Z", "capacity_mw": "52", "mw": "52", "operator": "Vyoma", "site_name": "",
             "city": "Chennai", "state": "", "confidence": "0.8"},
            {"entity_id": "dc:o", "first_story_at": "2026-10-29T10:00:00Z", "capacity_mw": "10400", "mw": "10400", "operator": "", "site_name": "",
             "city": "", "state": "OH", "confidence": "0.8"},
            {"entity_id": "dc:l", "first_story_at": "2026-10-29T11:00:00Z", "capacity_mw": "700", "mw": "700", "operator": "", "site_name": "",
             "city": "Lansing", "state": "MI", "confidence": "0.8"}])
        with tempfile.TemporaryDirectory() as d, mock.patch.object(roundup, "read_table", lambda n: dcs if n == "datacenter_projects" else None), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            L = roundup.five_numbers("2026-W44", pd.Timestamp("2026-10-26", tz="UTC"), pd.Timestamp("2026-11-01 23:59", tz="UTC"),
                                     {}, lambda *a: None, {}, None)
        row = next(ln for ln in L if "datacenter load" in ln)
        self.assertEqual(row, "- **Largest new datacenter load first reported this week:** 52 MW, Vyoma, Chennai (2 larger loads of the "
                              "week name no operator or site; they are in the table below).")
        import check_roundup as cr
        self.assertEqual(cr.FIVE_LOAD_V.search(row).group(1), "52")


class Row119NoEnDashNoPublishersTail(unittest.TestCase):
    """Row 119: an en dash in a publisher's title is not printed, and its own tail goes from an "Also" line."""

    def test_the_also_line(self):
        x = {"kind": "topic", "links": [("Financial Times", "https://news.google.com/rss/articles/f")],
             "title": "NTT DATA Announces Agreement with Bloom Energy for 900 MW of Onsite Power Generation Across Multiple Data "
                      "Center Projects " + chr(0x2013) + " Company Announcement - FT.com"}
        line = brief.also_line([x])
        self.assertNotIn(chr(0x2013), line)
        self.assertNotIn("FT.com", line)
        self.assertIn("Across Multiple Data Center Projects ([Financial Times]", line)

    def test_nodash(self):
        from score import nodash
        self.assertEqual(nodash("2015" + chr(0x2013) + "2025"), "2015-2025")
        self.assertNotIn(chr(0x2013), nodash("a " + chr(0x2013) + " b"))

    def test_a_dash_inside_a_title_stays(self):
        x = {"kind": "topic", "links": [("Reuters", "https://example.org/r")], "title": "Shell - Exxon talks stall over Guyana"}
        self.assertIn("Shell - Exxon talks stall over Guyana ([Reuters]", brief.also_line([x]))


class Row120RefiningIsOil(unittest.TestCase):
    def test_the_titles(self):
        self.assertEqual(brief.sector_of({"sector": "power_prices", "title": "U.S. Refineries Make Dramatic Shift Away From Gasoline"}), "oil")
        self.assertEqual(brief.sector_of({"sector": "generation", "title": "Data centers lean on diesel generators in Virginia"}), "generation")
        self.assertEqual(brief.sector_of({"sector": "generation", "title": "APS plans extending coal use to 2038"}), "generation")


class Row121AnInvestment(unittest.TestCase):
    def test_w43(self):
        import roundup
        r = {"deal_type": "equity_raise", "buyer": "", "seller": "Blackstone Energy Transition Partners V", "asset": "",
             "event_date": "2026-10-19"}
        self.assertTrue(roundup.finance_words(r).startswith("an investment in Blackstone Energy Transition Partners V"), roundup.finance_words(r))
        loan = dict(r, deal_type="debt", seller="Calibrant Energy")
        self.assertTrue(roundup.finance_words(loan).startswith("a loan for Calibrant Energy"))


class Row122EachListFromOne(unittest.TestCase):
    def test_the_weekend_and_the_five(self):
        L = ["## More", "", "### Weekend", "", "1. **A** (oil)  ", "2. **B** (gas)  ", "", "### The five stories of the week", "",
             "3. **C** (lng)  ", "4. **D** (deal)  "]
        out = brief.drop_repeated_items(L, lambda _m: None)
        self.assertIn("1. **C** (lng)  ", out)
        self.assertIn("2. **D** (deal)  ", out)
        self.assertIn("2. **B** (gas)  ", out)


class Row93TheRoundupHoldsTheHeldGrids(unittest.TestCase):
    """Row 93: a grid held for license prints no weekly mean in the Roundup's table, and its real-time table is not read."""

    def numbers(self):
        from unittest import mock
        import roundup
        utc = "UTC"

        def fetch(table, start=None, end=None, market=None, **k):
            if table == "iso_rtm_hub_prices":
                return pd.DataFrame({"ts_utc": [pd.Timestamp("2026-11-10 22:00", tz=utc)], "value": [926.42], "node": ["HB_WEST"],
                                     "variable": ["spp_rtm"], "freq": ["PT15M"]})
            if table == "nyiso_rtm_zone_prices":
                return pd.DataFrame({"ts_utc": [pd.Timestamp("2026-11-10 22:00", tz=utc)], "value": [2000.0], "node": ["N.Y.C."],
                                     "variable": ["lbmp_rtm"], "freq": ["PT5M"]})
            raise RuntimeError("not on this machine")
        parts = [("ercot", "iso_rtm_hub_prices", "ercot_rtm"), ("nyiso", "nyiso_rtm_zone_prices", None)]
        with mock.patch.object(roundup, "dam_week", lambda *a: (40.9, 168, 168)), mock.patch.object(roundup.erw, "fetch", fetch), \
                mock.patch.object(brief, "held_grids", lambda *a: {"NYISO", "ISO-NE", "MISO"}), \
                mock.patch.object(brief, "held_rt", lambda p, *a: {("nyiso", "nyiso_rtm_zone_prices")}), \
                mock.patch.object(brief, "paused_row", lambda label: {"paused_on": "2026-10-04"} if label == "MISO" else None), \
                mock.patch.object(brief, "rt_parts", lambda: parts), mock.patch.object(brief, "cite_short", lambda t: f"`{t}`"):
            return roundup.numbers(pd.Timestamp("2026-11-09", tz=utc), pd.Timestamp("2026-11-12 22:00", tz=utc), lambda *a: None, {})

    def test_the_table_and_the_real_time_line(self):
        L = self.numbers()
        nyiso = next(ln for ln in L if ln.startswith("| NYISO |"))
        self.assertEqual(nyiso.split(" | ")[2:5], ["licensed source needed", "licensed source needed", "not computed"])
        isone = next(ln for ln in L if ln.startswith("| ISO-NE |"))
        self.assertNotIn("40.9", isone)
        self.assertIn("paused by the ERW", next(ln for ln in L if ln.startswith("| MISO |")))
        self.assertIn("| 40.9 | 40.9 |", next(ln for ln in L if ln.startswith("| ERCOT |")))
        rt = next(ln for ln in L if ln.startswith("**Highest real-time price of the week:**"))
        self.assertIn("926.42 USD/MWh at HB_WEST (ERCOT)", rt)
        self.assertNotIn("2000", rt)
        self.assertTrue(rt.endswith("Not read: NYISO (licensed source needed)."), rt)


if __name__ == "__main__":
    unittest.main()
