"""Vantage Data Centers: US campuses (session 22, Task 2b).

Source: https://vantage-dc.com/data-center-locations/ , the location list ("Ashburn I, VA,
United States"), and each US campus page it links, whose Campus Overview states the
campus's critical IT load ("206MW of critical IT load", "1.4GW of critical IT load"). Kept:
list entries ending "United States". The state is the postal code in the entry; the city is
the entry's name without the campus numeral ("Ashburn I" -> Ashburn), or the county when the
name ends "County". MW is kept with its exact span from the campus page. No status is stated.
"""
import re

from common import facility, get, mw_checked, page_text, state_of

OPERATOR = "Vantage Data Centers"
SOURCE = "vantage:data-center-locations"
URL = "https://vantage-dc.com/data-center-locations/"
BASE = "https://vantage-dc.com"
_SPAN = re.compile(r"\d[\d,]*(?:\.\d+)?\s?(?:MW|GW) of critical IT (?:load|capacity)")


def facilities(log):
    html = get(URL, log)
    text = page_text(html)
    links = {}
    for href, label in re.findall(r'<a[^>]*href="((?:https://vantage-dc\.com)?/data-center-locations/north-america/'
                                  r'[a-z0-9-]+/?)"[^>]*>([^<]*, United States)</a>', html):
        links.setdefault(label.strip(), href if href.startswith("http") else BASE + href)
    # each list entry is its own element (a link or a list item): read it whole, not from the running text
    entries = sorted(set(" ".join(e.split()) for e in re.findall(r">\s*([^<>]+?, [A-Z]{2}, United States)\s*<", html)))
    entries = [e for e in entries if e in text]
    out = []
    for entry in entries:
        name, code, _ = [p.strip() for p in entry.split(",")]
        st = state_of(code)
        if not st:
            continue
        base = re.sub(r" I{1,3}$", "", name)
        county = base if base.endswith(" County") else ""
        row = facility(operator=OPERATOR, name=f"Vantage {name}", site_type="campus", place_text=entry,
                       city="" if county else base, county=county, state=st, source_url=links.get(entry, URL))
        if entry in links:
            page = page_text(get(links[entry], log))
            m = _SPAN.search(page)
            if m:
                mw, why = mw_checked(m.group(0), page)
                if mw is not None:
                    row["mw"], row["mw_span"] = mw, m.group(0)
                else:
                    log(f"  vantage {name}: MW not kept ({why})")
        out.append(row)
    log(f"  vantage: {len(entries)} US list entries, {sum(1 for r in out if r['mw'] is not None)} with a stated MW")
    return out
