"""Google: data center campuses and Google Cloud regions in the US (session 22, Task 2b).

Sources:
- https://datacenters.google/locations/ (Google data centers): each location as JSON in the
  page ({"location": "Council Bluffs, Iowa", "latitude": ..., "longitude": ...,
  "inDevelopment": false}). Kept: locations whose last part is a US state. The first part is
  the city, or the county when it ends "County"; coordinates where the page gives them.
  inDevelopment true -> planned, false -> operating (the page's own flag).
- https://cloud.google.com/compute/docs/regions-zones (Google Cloud): the zones table
  (zone code, "Council Bluffs, Iowa, North America"). One facility per US region (zone code
  without its letter); the location as the table states it.
No MW is stated on either page.
"""
import re

from common import facility, get, inline_text, state_of

OPERATOR = "Google"
SOURCE = "google:datacenter-locations"
URL = "https://datacenters.google/locations/"
CLOUD_URL = "https://cloud.google.com/compute/docs/regions-zones"


def _place(parts):
    """(city, county) from the parts of a location before its state."""
    city = county = ""
    for p in parts:
        if re.search(r" (County|Parish)$", p):
            county = p
        elif not city:
            city = p
    return city, county


def facilities(log):
    out = []
    html = get(URL, log)
    locs = re.findall(r'\{\s*"location":\s*"([^"]+)",\s*"latitude":\s*([^,]+),\s*"longitude":\s*([^,]+),'
                      r'\s*"inDevelopment":\s*(true|false)', html)
    for loc, lat, lon, dev in locs:
        parts = [p.strip() for p in loc.split(",")]
        st = state_of(parts[-1]) if len(parts) > 1 else ""
        if not st:
            continue
        city, county = _place(parts[:-1])
        ok = lat.strip() not in ("null", "") and lon.strip() not in ("null", "")
        out.append(facility(operator=OPERATOR, name=f"Google data center, {loc}", site_type="campus", place_text=loc,
                            city=city, county=county, state=st, lat=lat.strip() if ok else "",
                            lon=lon.strip() if ok else "", status="planned" if dev == "true" else "operating",
                            status_text=f'"inDevelopment": {dev}', source_url=URL))
    n_campus = len(out)
    html = get(CLOUD_URL, log)
    regions = {}
    for zone, where in re.findall(r'<td><code[^>]*>(us-[a-z0-9]+-[a-z])</code></td>\s*<td>(.*?)</td>', html, re.S):
        regions.setdefault(zone.rsplit("-", 1)[0], inline_text(where))
    for code, where in sorted(regions.items()):
        parts = [p.strip() for p in where.split(",") if p.strip() != "North America"]
        st = state_of(parts[-1]) if len(parts) > 1 else ""
        city, county = _place(parts[:-1]) if st else ("", "")
        out.append(facility(operator=OPERATOR, name=f"Google Cloud {code}", site_type="region", operator_code=code,
                            place_text=where, city=city, county=county, state=st, source_url=CLOUD_URL))
    log(f"  google: {len(locs)} data center locations listed, {n_campus} in the US; {len(regions)} US cloud regions")
    return out
