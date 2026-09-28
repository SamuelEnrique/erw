"""Digital Realty: US data centers (session 22, Task 2b).

Source: https://www.digitalrealty.com/data-centers . The page carries its facility list as
JSON (__NEXT_DATA__): per facility the site code (title, "IAD39"), metro, country, and
latitude and longitude. Kept: facilities with country USA. Each facility's own page
(url-alias) is read for its address, which names the city and state ("IAD39 44274 Round
Table Plaza (Bldg L), Ashburn, VA 20147"). The coordinates are the operator's own.
The list also has a field_utility_power_capacity number with no unit on the page or in the
data ("120000" for IAD39); a number without a stated unit is not an MW, so it is not kept.
No status is stated.
"""
import json
import re

from common import facility, get, page_text, state_of

OPERATOR = "Digital Realty"
SOURCE = "digitalrealty:data-centers"
URL = "https://www.digitalrealty.com/data-centers"
BASE = "https://www.digitalrealty.com"


def _nodes(o, out):
    if isinstance(o, dict):
        alias = o.get("url-alias") or ""
        if o.get("country") == "USA" and alias.count("/") == 4 and o.get("title"):
            out.setdefault(alias, o)
        for v in o.values():
            _nodes(v, out)
    elif isinstance(o, list):
        for v in o:
            _nodes(v, out)
    return out


def _val(o, field):
    v = o.get(field) or []
    return str(v[0].get("value", "")) if v and isinstance(v[0], dict) else ""


def facilities(log):
    html = get(URL, log)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("digital realty: no __NEXT_DATA__ facility list on the page")
    nodes = _nodes(json.loads(m.group(1)), {})
    out, no_addr = [], 0
    for alias, o in sorted(nodes.items()):
        code = o["title"].strip()
        url = BASE + alias
        text = page_text(get(url, log))
        a = re.search(r"\b" + re.escape(code) + r" (\d[^|]{2,120}?), ([A-Z][A-Za-z .'-]+?), ([A-Z]{2}) \d{5}", text)
        st = state_of(a.group(3)) if a else ""
        if not a:
            no_addr += 1
        out.append(facility(operator=OPERATOR, name=f"Digital Realty {code}", site_type="facility",
                            operator_code=code, place_text=a.group(0) if a else o.get("metro", ""),
                            city=a.group(2) if a else "", state=st, lat=_val(o, "field_latitude"),
                            lon=_val(o, "field_longitude"), detail=f"metro: {o.get('metro', '')}", source_url=url))
    log(f"  digital realty: {len(nodes)} US facilities, {no_addr} without an address on their page")
    return out
