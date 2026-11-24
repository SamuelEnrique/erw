"""Four frames side by side for the review page (session 9900).
Usage: montage.py <out.png> <frame1.png> <frame2.png> <frame3.png> <frame4.png> [--labels a,b,c,d]"""
import sys

from PIL import Image, ImageDraw

out = sys.argv[1]
files = [a for a in sys.argv[2:] if a.endswith(".png")]
ims = [Image.open(f).convert("RGB") for f in files]
w = 540
ims = [im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) for im in ims]
h = max(im.height for im in ims)
gap = 12
sheet = Image.new("RGB", (len(ims) * w + (len(ims) + 1) * gap, h + 2 * gap), (200, 196, 188))
for i, im in enumerate(ims):
    sheet.paste(im, (gap + i * (w + gap), gap))
sheet.save(out, optimize=True)
print(out, sheet.size)
