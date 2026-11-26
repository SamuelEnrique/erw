"""Session 10226: read the words of a drawn page around each phrase named, as visible text (tags out, entities read).
Prints the sentence or hover around each phrase, PASS when every phrase is found, and the page's em dash count.

    python runs/c10226/read_words.py <page.html> "<phrase>" ["<phrase>" ...]
"""
import html as H
import re
import sys

page = open(sys.argv[1], encoding="utf-8").read()
text = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", page.replace("<!-- -->", "")))).strip()
text = re.sub(r" ([.,:;)])", r"\1", text)
ok = True
for phrase in sys.argv[2:]:
    i = text.find(phrase)
    if i < 0:
        ok = False
        print(f"NOT FOUND: {phrase!r}")
        continue
    a = max(0, text.rfind(". ", 0, max(0, i - 200)) + 2)
    b = text.find(". ", i + len(phrase))
    b = len(text) if b < 0 else min(b + 1, i + len(phrase) + 500)
    print(f"FOUND: ...{text[a:b]}")
print(f"em dashes in the page: {page.count(chr(0x2014))}")
print("PASS" if ok else "FAIL")
