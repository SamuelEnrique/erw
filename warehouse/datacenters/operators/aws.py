"""Amazon Web Services: the AWS Regions in the US (session 22, Task 2b).

Source: the locations list behind the AWS Regions and Availability Zones page,
https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json (name, code, type,
continent). Kept: entries of type "AWS Region" whose name starts "US " or is an AWS GovCloud
(US) region. Local Zones and Wavelength Zones are edge sites inside telecom and colocation
buildings, not regions, and are left out. The state is kept when the name's parenthesis
names one ("US East (Ohio)", "US East (N. Virginia)"); "Kansas City" names a city in two
states and keeps no state. AWS states no MW and no status.
"""
import json

from common import facility, get, state_of

OPERATOR = "Amazon Web Services"
SOURCE = "aws:locations"
URL = "https://b0.p.awsstatic.com/locations/1.0/aws/current/locations.json"
PAGE = "https://aws.amazon.com/about-aws/global-infrastructure/regions_az/"


def facilities(log):
    data = json.loads(get(URL, log))
    out = []
    for name, v in data.items():
        if v.get("type") != "AWS Region" or not (name.startswith("US ") or "GovCloud (US" in name):
            continue
        inner = name[name.find("(") + 1:name.rfind(")")] if "(" in name else ""
        st = state_of(inner)
        city = "" if st or inner.startswith("US") else inner
        out.append(facility(operator=OPERATOR, name=name, site_type="region", operator_code=v.get("code", ""),
                            place_text=name, state=st, city=city, source_url=URL))
    log(f"  aws: {len(data)} locations listed, {len(out)} US regions kept")
    return out
