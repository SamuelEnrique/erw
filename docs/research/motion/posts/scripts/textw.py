"""Width in px of strings set in the post's fonts, from the fontsource woff files (kerning ignored, so a slight
overestimate). Session 9900. Usage: textw.py <serif|sans|mono> <size_px> "text" ["text" ...]"""
import sys

from fontTools.ttLib import TTFont

FILES = {
    "serif": "motion/node_modules/@fontsource/source-serif-4/files/source-serif-4-latin-600-normal.woff",
    "sans": "motion/node_modules/@fontsource/ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff",
    "mono": "motion/node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff",
}
font = TTFont(FILES[sys.argv[1]])
size = float(sys.argv[2])
upm = font["head"].unitsPerEm
cmap = font.getBestCmap()
hmtx = font["hmtx"]
for s in sys.argv[3:]:
    w = sum(hmtx[cmap[ord(ch)]][0] for ch in s) * size / upm
    print(f"{w:7.1f}  {s}")
