"""Oracle Cloud Infrastructure: the OCI regions in the US (session 22, Task 2b).

Source: https://www.oracle.com/cloud/public-cloud-regions/ , the region tables (one row per
region: <td geo-data="us-ashburn-1">US East (Ashburn)</td> ... <td>Live</td>). Kept: rows
whose region code starts "us-". The page names a city, not a state, so the state is empty
(Ashburn, Phoenix, San Jose and Chicago are not placed: nothing inferred). Status as stated:
Live -> operating, Coming soon -> planned. No MW is stated.
"""
import re

from common import facility, get, inline_text

OPERATOR = "Oracle"
SOURCE = "oracle:public-cloud-regions"
URL = "https://www.oracle.com/cloud/public-cloud-regions/"
STATUS = {"live": "operating", "coming soon": "planned"}


def facilities(log):
    html = get(URL, log)
    out, seen = [], set()
    for row in re.findall(r'<tr>\s*(<td geo-data="us-[^"]+".*?)</tr>', html, re.S):
        code = re.search(r'geo-data="([^"]+)"', row).group(1)
        if code in seen:
            continue
        seen.add(code)
        cells = [inline_text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        name = cells[0]
        word = next((c for c in cells[1:] if c.lower() in STATUS), "")
        city = name[name.find("(") + 1:name.rfind(")")] if "(" in name else ""
        out.append(facility(operator=OPERATOR, name=name, site_type="region", operator_code=code, place_text=name,
                            city=city, status=STATUS.get(word.lower(), ""), status_text=word, source_url=URL))
    log(f"  oracle: {len(out)} US regions")
    return out
