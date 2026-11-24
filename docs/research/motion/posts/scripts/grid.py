"""A grid of images (session 9900). Usage: grid.py <out.png> <cols> <img> [<img> ...]"""
import sys

from PIL import Image

out, cols = sys.argv[1], int(sys.argv[2])
ims = [Image.open(f).convert("RGB") for f in sys.argv[3:]]
w = 480
ims = [im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) for im in ims]
h = max(im.height for im in ims)
gap = 12
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * h + (rows + 1) * gap), (200, 196, 188))
for i, im in enumerate(ims):
    r, c = divmod(i, cols)
    sheet.paste(im, (gap + c * (w + gap), gap + r * (h + gap)))
sheet.save(out, optimize=True)
print(out, sheet.size)
