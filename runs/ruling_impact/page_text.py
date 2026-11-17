"""Session 7618 (portable-laptop): the visible words of a saved page (runs/ruling_impact/cache/pages/<name>.html), and
the words around each match of a phrase.  page_text.py <name> <phrase> [chars before] [chars after]"""
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def text_of(name: str) -> str:
    t = (Path(__file__).resolve().parent / "cache" / "pages" / f"{name}.html").read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


if __name__ == "__main__":
    x = text_of(sys.argv[1])
    before = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    after = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    for m in list(re.finditer(re.escape(sys.argv[2]), x))[:5]:
        print("...", x[max(0, m.start() - before):m.end() + after], "...\n")
