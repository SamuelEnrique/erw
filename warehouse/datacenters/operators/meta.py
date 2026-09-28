"""Meta: data center locations (session 22, Task 2b).

Source: https://datacenters.atmeta.com/all-locations/ . One card per location: the state as
the eyebrow ("INDIANA"), the site as the title ("Jeffersonville"), and an excerpt with the
investment and the year ground was broken ("$800 million+ investment; 2024 break ground;
..."). Kept: cards whose eyebrow is a US state. The title is the city, or the county when it
ends "County" or "Parish" ("Richland Parish"); a title that is neither ("Sarpy") is kept as
the site name and has no city (nothing inferred), so it is not placed. The excerpt is kept
as detail. Meta states no MW and no status on this page.
"""
import re

from common import facility, get, inline_text, state_of

OPERATOR = "Meta"
SOURCE = "meta:datacenter-locations"
URL = "https://datacenters.atmeta.com/all-locations/"


def facilities(log):
    html = get(URL, log)
    out = []
    cards = re.findall(r'<p class="card__eyebrow-text">(.*?)</p>\s*<h3 class="card__title">(.*?)</h3>\s*'
                       r'<p class="card__excerpt">(.*?)</p>', html, re.S)
    for eyebrow, title, excerpt in cards:
        st = state_of(inline_text(eyebrow))
        if not st:
            continue
        site = inline_text(title)
        county = site if re.search(r" (County|Parish)$", site) else ""
        out.append(facility(operator=OPERATOR, name=f"Meta data center, {site}", site_type="campus",
                            place_text=f"{inline_text(eyebrow)} {site}", city="" if county else site,
                            county=county, state=st, detail=inline_text(excerpt), source_url=URL))
    log(f"  meta: {len(cards)} location cards, {len(out)} in US states")
    return out
