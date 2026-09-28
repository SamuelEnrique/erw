"""Switch: campuses (session 22, Task 2b).

Source: https://www.switch.com/colocation/ , whose LOCATIONS list links one page per campus
(/las-vegas/, /tahoe-reno/, /atlanta/, /grand-rapids/, /austin/). Each campus page opens with
one sentence that names the campus and its place and, for most, its power: "The Core located
in Las Vegas, Nevada, will have up to 495 MW of power upon completion." Kept: the campus name,
city and state from that sentence, and MW with its exact span ("up to 495 MW of power"). A
page that says "gigawatts of power capacity" without a figure has no MW. "will have ... upon
completion" is not a status, so status is empty.
"""
import re

from common import STATES, facility, get, mw_checked, page_text, state_of

OPERATOR = "Switch"
SOURCE = "switch:locations"
URL = "https://www.switch.com/colocation/"
BASE = "https://www.switch.com"
_STATES = "(" + "|".join(sorted(STATES, key=len, reverse=True)) + ")"
_WHERE = re.compile(r"The ([A-Z][\w ]+?) (?:is )?located in ([A-Z][A-Za-z .]+?), " + _STATES + r"\b")
_SPAN = re.compile(r"up to \d[\d,]*(?:\.\d+)? ?(?:MW|GW) of power")


def facilities(log):
    html = get(URL, log)
    paths = sorted(set(re.findall(r'href="(/(?:las-vegas|tahoe-reno|atlanta|grand-rapids|austin|houston)/?)"', html)))
    paths = sorted({p.rstrip("/") + "/" for p in paths})
    if not paths:
        raise RuntimeError("switch: no location links found on the colocation page")
    out = []
    for p in paths:
        url = BASE + p
        page = page_text(get(url, log))
        m = _WHERE.search(page)
        if not m:
            log(f"  switch {p}: no 'located in <city>, <state>' sentence; not kept")
            continue
        sentence_end = page.find(".", m.end())
        sentence = page[m.start():sentence_end if sentence_end > 0 else m.end() + 300]
        row = facility(operator=OPERATOR, name=f"Switch {m.group(1)}", site_type="campus", place_text=m.group(0),
                       city=m.group(2), state=state_of(m.group(3)), detail=sentence, source_url=url)
        s = _SPAN.search(sentence)
        if s:
            mw, why = mw_checked(s.group(0), page)
            if mw is not None:
                row["mw"], row["mw_span"] = mw, s.group(0)
            else:
                log(f"  switch {p}: MW not kept ({why})")
        out.append(row)
    log(f"  switch: {len(paths)} location pages, {len(out)} campuses, "
        f"{sum(1 for r in out if r['mw'] is not None)} with a stated MW")
    return out
