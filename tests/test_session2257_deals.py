"""Session 2257 (chain 159): a deal's country as the story's words name it.

The second read (session 2249) found 12 of 106 sampled deals with a place missed. Two had the country the model gave
("Indonesia") refused by the span check because the span was the adjective ("Indonesian assets"); ten had the country
left empty though the headline names it before the asset ("US Shale", "US power deal", "Venezuela gas
infrastructure"). warehouse/deals/fields.py now names a country by its adjective too (country_names) and reads the
country from the words when the model leaves it empty (country_of): the United States by any of its words, another
country by its name, and where the United States and one other are both found, the other (the US words describe the
party). On the replayed 2249 answers: 12 to 3 (two headlines naming two states for one field; Japan's Jera, the
buyer's country, not the asset's).
"""

import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "deals", "eval"))
import deal_fields as fields  # noqa: E402  session 3233: by its own name (deal_fields.py)
import fixture  # noqa: E402


class TheWords(unittest.TestCase):
    def test_the_asset_country(self):
        for text, want in (("Devon, Coterra will merge to create $58 billion US shale giant", "United States"),
                           ("Vistra Buying US Gas-Power Fleet for $4 Billion", "United States"),
                           ("New Brookfield Venture May Restart Abandoned US Nuclear Project", "United States"),
                           ("Baker Hughes signs agreements to expand Venezuela gas infrastructure", "Venezuela"),
                           ("US energy services firm Baker Hughes ... expand Venezuela gas infrastructure", "Venezuela"),
                           ("US firm buys Spain’s solar fleet", "Spain"),
                           ("Spain's Iberdrola buys US wind assets", "United States")):
            self.assertEqual(fields.country_of(text)[0], want, text)

    def test_no_country_where_the_words_do_not_make_it_the_assets(self):
        for text in ("Qatar in Deal to Supply LNG for 27 Years to Japan's Jera",   # the buyer's home
                     "help us power the future",                                   # a pronoun, lower case
                     "Eni and Ares inject capital into the business that holds the Italian oil and gas group",
                     "US firm buys UK wind farm",                                  # an adjective of another country
                     "Prices of USD 3 billion",
                     "Brookfield and Spain's Iberdrola and Japan's Jera sign"):
            self.assertEqual(fields.country_of(text), ("", ""), text)

    def test_a_country_is_named_by_its_adjective(self):
        self.assertIn("indonesian", fields.country_names("Indonesia"))
        self.assertIn("american", fields.country_names("United States"))
        self.assertEqual(fields.country_names("Atlantis"), {"atlantis"})


class TheSample(unittest.TestCase):
    def test_place_missed_twelve_to_three(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "deals", "stories_2249.json"), encoding="utf-8") as f:
            fx = {s["event_id"]: s.get("fixture") for s in json.load(f)}
        rows, log = fixture.replay("2249")
        got = {}
        for r in rows.to_dict("records"):
            for sid in str(r["story_ids"]).split(";"):
                if fx.get(sid):
                    got[fx[sid]] = r["country"]
        want = {"D017": "Indonesia", "D024": "United States", "D025": "Venezuela", "D029": "Indonesia",
                "D037": "United States", "D058": "United States", "D068": "United States", "D073": "United States",
                "D080": "United States", "D089": "United States", "D091": "United States", "D087": ""}
        for n, c in want.items():
            self.assertEqual(got.get(n), c, n)
        self.assertNotIn("does not name the country", log)


if __name__ == "__main__":
    unittest.main()
