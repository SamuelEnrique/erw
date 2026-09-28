"""The ERW voice (docs/voice.md), for every script that writes words (session 25).

    from voice import VOICE          # the page, as text
    system = MY_SYSTEM + VOICE_NOTE  # appended to a system prompt

Writers: warehouse/news/brief.py (headlines, the numbers summary; the Roundup uses it too), warehouse/news/funfact.py,
warehouse/analysis/run.py (the chart-of-the-week note and caption), warehouse/policy/reads.py and
warehouse/thesis/build.py. A missing page fails loudly: a writer does not run without its voice.
"""

import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATH = os.path.join(ROOT, "docs", "voice.md")
with open(PATH, encoding="utf-8") as _f:
    VOICE = _f.read()
VOICE_NOTE = "\n\nWrite in the ERW voice (docs/voice.md). Where it and the rules above differ, the rules above win.\n\n" + VOICE
