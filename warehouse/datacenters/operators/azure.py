"""Microsoft Azure: the Azure regions in the US (session 22, Task 2b).

Source: https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/ . The
page lists every region in one sentence ("Azure is available or coming soon to the following
regions: South Central US, West US, ..."); kept are the names with the word US. A region's
state is kept when its name names one (US Gov Virginia) or when the page's card for that
region states it ("West US 3 ... located in Arizona"). A card that announces a US state
without a region name ("expand US datacenter ... into the state of Georgia") is kept as an
announced site in that state. Status is not stated per region ("available or coming soon"),
and no MW is stated.
"""
import re

from common import STATES, facility, get, inline_text, page_text, state_of

OPERATOR = "Microsoft"
SOURCE = "microsoft:azure-geographies"
URL = "https://azure.microsoft.com/en-us/explore/global-infrastructure/geographies/"
_STATES = "(" + "|".join(sorted(STATES, key=len, reverse=True)) + ")"


def facilities(log):
    html = get(URL, log)
    text = page_text(html)
    m = re.search(r"available or coming soon to the following regions: (.*?)\.", text)
    if not m:
        raise RuntimeError("azure: the region sentence was not found on the page")
    names = [n.strip() for n in re.split(r",\s*|\s+and\s+", m.group(1)) if n.strip()]
    us = [n for n in names if re.search(r"\bUS\b", n)]
    cards = {}
    for c in re.finditer(r'<h3><span class="d-block h5">([^<]+)</span></h3>', html):
        p = re.search(r'block-feature__paragraph">(.*?)</div>', html[c.end():c.end() + 3000], re.S)
        if p:
            cards[inline_text(c.group(1))] = inline_text(p.group(1))
    out = []
    for n in us:
        w = re.search(r"\b" + _STATES + r"\b", n)
        st, span = (state_of(w.group(1)), n) if w else ("", n)
        card = cards.get(n, "")
        cm = None if st else re.search(r"located in " + _STATES + r"\b", card)
        if cm:
            st, span = state_of(cm.group(1)), cm.group(0)
        out.append(facility(operator=OPERATOR, name=n, site_type="region", place_text=span, state=st,
                            detail=card, source_url=URL))
    n_regions = len(out)
    for title, body in cards.items():
        am = re.search(r"into the state of " + _STATES + r"\b", body)
        if am and title not in us:
            out.append(facility(operator=OPERATOR, name=f"Azure {title} (announced)", site_type="announced_site",
                                place_text=am.group(0), state=state_of(am.group(1)), detail=body, source_url=URL))
    log(f"  azure: {len(names)} regions listed, {n_regions} US regions, {len(out) - n_regions} announced US sites")
    return out
