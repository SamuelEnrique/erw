"""Print a PDF page's words, marking those crossed by a drawn horizontal line ([S], struck) or underlined ([U]).

Used by chain 740 (session 10813) to read which words an Arkansas act strikes: an act printed as
plain text runs struck and inserted words together.
usage: pdf_strike.py PDF PAGE(1-based) [WORD_FILTER]
A word is struck when a horizontal line or thin rectangle passes through its middle; underlined when one lies just below its baseline.
"""
import sys

import pdfplumber

pdf, page_no = sys.argv[1], int(sys.argv[2])
filt = sys.argv[3].lower() if len(sys.argv) > 3 else None
with pdfplumber.open(pdf) as doc:
    page = doc.pages[page_no - 1]
    segs = []
    for ln in page.lines:
        if abs(ln["top"] - ln["bottom"]) < 1.5:
            segs.append((ln["x0"], ln["x1"], (ln["top"] + ln["bottom"]) / 2))
    for r in page.rects:
        if r["height"] < 2.5 and r["width"] > 2:
            segs.append((r["x0"], r["x1"], (r["top"] + r["bottom"]) / 2))
    out = []
    for w in page.extract_words():
        h = w["bottom"] - w["top"]
        mark = ""
        for x0, x1, y in segs:
            if x0 <= (w["x0"] + w["x1"]) / 2 <= x1:
                if w["top"] + h / 3 <= y <= w["bottom"] - h / 4:
                    mark = "[S]"
                elif w["bottom"] - 1 <= y <= w["bottom"] + 3:
                    mark = mark or "[U]"
        out.append((round(w["top"]), w["text"] + mark))
    line, cur = [], None
    for top, t in out:
        if cur is not None and abs(top - cur) > 3:
            s = " ".join(line)
            if not filt or filt in s.lower():
                print(s)
            line = []
        cur = top
        line.append(t)
    s = " ".join(line)
    if not filt or filt in s.lower():
        print(s)
