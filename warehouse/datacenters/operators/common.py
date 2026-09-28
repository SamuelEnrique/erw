"""Shared pieces of the datacenter operator site connectors (session 22, Task 2b).

Energy Research Warehouse (ERW). Each operator has its own connector in this folder
(aws.py, azure.py, google.py, meta.py, oracle.py, digital_realty.py, equinix.py,
vantage.py, switch.py); warehouse/datacenters/operators/run.py runs them all and writes
warehouse/output/datacenter_operator_sites.csv. The connectors are separate, as CLAUDE.md
asks; this module holds only what all nine need: the HTTP get (every response is stored
raw by iso_prices.RAW, which the runner opens), page text, state names, and the MW check.

The rules are the datacenter extractor's (session 16 ruling: nothing inferred beyond the
stated words):
- a state is kept only when the page names it (full name or postal code) in the location
  text; a region named only by a direction ("East US") or a city ("US East (Ashburn)")
  keeps its city and has no state;
- MW is kept only with the exact span it was read from, and the span must be in the page
  text and parse to the same value (GW x 1000);
- a status is kept only where the page states one (Oracle's Live or Coming soon, Google's
  inDevelopment flag); otherwise it is empty.
"""

import html as htmlmod
import os
import re
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

# a plain browser user agent: Equinix answered HTTP 403 when a research note was appended to it (session 22)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0 Safari/537.36")
PAUSE = 0.5  # seconds between requests to one operator's site

STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}
CODES = set(STATES.values())
_DIRECTION = re.compile(r"^(?:N\.|S\.|E\.|W\.|North(?:ern)?|South(?:ern)?|East(?:ern)?|West(?:ern)?|Central) ", re.I)


def state_of(words):
    """The postal code of a state the words name exactly: 'Iowa', 'iowa', 'IA', or a state
    after a direction ('N. Virginia', 'Northern Virginia'). Anything else (a city, 'Kansas
    City', 'Tahoe Reno') is not a state, and returns ''."""
    w = " ".join((words or "").split()).strip(" ,.")
    if not w:
        return ""
    if w.upper() in CODES and len(w) == 2:
        return w.upper()
    by_lower = {k.lower(): v for k, v in STATES.items()}
    if w.lower() in by_lower:
        return by_lower[w.lower()]
    bare = _DIRECTION.sub("", w)
    if bare != w and bare.lower() in by_lower:
        return by_lower[bare.lower()]
    return ""


def get(url, log, session=None, binary=False):
    """GET one public page with retries; the response is stored raw by ip.RAW (the runner
    opens the store). Fails loudly on a non-200 answer."""
    s = session or requests

    def call():
        r = s.get(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} from {url}")
        return r
    r = ip.with_retries(url, call, log, attempts=3, wait=5)
    time.sleep(PAUSE)
    return r.content if binary else r.text


def page_text(html):
    """The visible text of a page: scripts and styles removed, tags to spaces, entities
    decoded, whitespace collapsed. MW spans and location words are checked against this."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(htmlmod.unescape(t).replace(" ", " ").split())


def inline_text(fragment):
    """The text of an HTML fragment with inline tags removed without a space (a year split
    as <strong>202</strong>6 reads 2026) and <br> as a separator."""
    t = re.sub(r"<br\s*/?>", "; ", fragment, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    return " ".join(htmlmod.unescape(t).replace(" ", " ").split()).strip(" ;")


_MW = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?(MW|GW|megawatts?|gigawatts?)\b", re.I)


def mw_checked(span, text):
    """(mw, span) when the span is in the page text and states one MW or GW figure, else
    (None, reason). GW is multiplied by 1000."""
    if not span:
        return None, "no span"
    if " ".join(span.split()) not in text:
        return None, f"span {span!r} not in the page text"
    found = _MW.findall(span)
    if len(found) != 1:
        return None, f"span {span!r} states {len(found)} MW or GW figures"
    num, unit = found[0]
    v = float(num.replace(",", ""))
    if unit.lower().startswith("g"):
        v *= 1000
    return v, ""


def facility(**kw):
    """One facility as a connector yields it. Only what the page states is filled."""
    base = dict(operator="", name="", site_type="", operator_code="", place_text="", city="",
                county="", state="", lat="", lon="", mw=None, mw_span="", status="",
                status_text="", detail="", source_url="")
    unknown = set(kw) - set(base)
    if unknown:
        raise ValueError(f"unknown facility fields {sorted(unknown)}")
    base.update(kw)
    return base
