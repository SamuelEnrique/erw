"""Equinix: US data centers (IBX) (session 22, Task 2b).

Source: https://www.equinix.com/data-centers/americas-colocation/united-states-colocation ,
which links one page per US metro; each metro page links one page per data center (IBX,
"DC1"). Each IBX page's description states its address: "Learn about Equinix DC1
carrier-neutral data center, located at 21711 Filigree Court, Suite C, Ashburn, VA." Kept:
the IBX code, the metro, and the city and state from that sentence. Most descriptions stop at
the city ("located at 180 Peachtree Street NW, Atlanta."); then the state is taken from the
page's Address block only where it gives that same city with a state and ZIP ("Atlanta, GA
30303"), else it stays empty. Equinix states no MW and no status on these pages.
"""
import html as htmlmod
import re

from common import facility, get, page_text, state_of

OPERATOR = "Equinix"
SOURCE = "equinix:us-data-centers"
URL = "https://www.equinix.com/data-centers/americas-colocation/united-states-colocation"
BASE = "https://www.equinix.com"
_PATH = "/data-centers/americas-colocation/united-states-colocation/"


def facilities(log):
    html = get(URL, log)
    metros = sorted(set(re.findall(r'href="(' + _PATH + r'[a-z0-9-]+-data-centers)"', html)))
    if not metros:
        raise RuntimeError("equinix: no metro links on the US page")
    out, no_addr = [], 0
    for mpath in metros:
        mhtml = get(BASE + mpath, log)
        ibx = sorted(set(re.findall(r'href="(' + re.escape(mpath) + r'/[a-z0-9-]+)"', mhtml)))
        metro = mpath.rsplit("/", 1)[1].replace("-data-centers", "").replace("-", " ").title()
        for ipath in ibx:
            url = BASE + ipath
            page = get(url, log)
            d = re.search(r'<meta name="description" content="([^"]*)"', page)
            desc = htmlmod.unescape(d.group(1)) if d else ""
            code = ipath.rsplit("/", 1)[1].upper()
            city = st = ""
            place = metro
            a = re.search(r"located at (.+?), ([A-Z][A-Za-z .'-]+), ([A-Z]{2})\b", desc)
            if a:
                city, st, place = a.group(2), state_of(a.group(3)), a.group(0)
            else:
                # most descriptions stop at the city ("located at 180 Peachtree Street NW, Atlanta."); the page's
                # Address block gives the same city with its state and ZIP ("Atlanta, GA 30303")
                c = re.search(r"located at (.+?), ([A-Z][A-Za-z .'-]+?)\.", desc)
                if c:
                    city, place = c.group(2), c.group(0)
                    z = re.search(re.escape(city) + r", ([A-Z]{2}) \d{5}", page_text(page))
                    if z:
                        st, place = state_of(z.group(1)), f"{c.group(0)} {z.group(0)}"
            if not st:
                no_addr += 1
            out.append(facility(operator=OPERATOR, name=f"Equinix {code}", site_type="facility", operator_code=code,
                                place_text=place, city=city, state=st, detail=f"metro: {metro}", source_url=url))
    log(f"  equinix: {len(metros)} US metros, {len(out)} IBX pages, {no_addr} without a stated state")
    return out
