"""Print the lines of saved PDF bulletins (.bin as the probe keeps them) that state a rate per MCF or a percent. Usage:
pdf_rates.py FILE..."""
import io
import re
import sys

import pdfplumber

for p in sys.argv[1:]:
    r = pdfplumber.open(io.BytesIO(open(p, "rb").read()))
    text = "\n".join((pg.extract_text() or "") for pg in r.pages)
    print("==", p[-70:], len(r.pages), "pages")
    for ln in text.splitlines():
        if re.search(r"\$\s?0?\.\d+|per\s+mcf|per\s+MCF|percent|%|horizontal|Horizontal", ln):
            print("  ", " ".join(ln.split())[:220])
