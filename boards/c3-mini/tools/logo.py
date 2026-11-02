"""Trace the PKT logo into 1-bit row spans for the silkscreen."""
import json, os
from PIL import Image
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'assets', 'pkt-logo.png')
COLS = 300     # traced resolution; the logo ends up about 16 mm wide, so 0.053 mm per cell
hsv = Image.open(SRC).convert('RGB')
px = hsv.load()
w, h = hsv.size
mask = [[max(px[x, y]) - min(px[x, y]) > 55 for x in range(w)] for y in range(h)]
ys = [y for y in range(h) if any(mask[y])]
xs = [x for x in range(w) if any(mask[y][x] for y in ys)]
x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
s = (x1 - x0) / COLS
rows = int((y1 - y0) / s)
spans = []
for r in range(rows):
    cy = y0 + int((r + .5) * s)
    st = None
    for c in range(COLS + 1):
        on = c < COLS and mask[cy][x0 + int((c + .5) * s)]
        if on and st is None:
            st = c
        if not on and st is not None:
            spans.append((r, st, c))
            st = None
json.dump({'cols': COLS, 'rows': rows, 'spans': spans}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.json'), 'w'))
print(x1 - x0, y1 - y0, COLS, rows, len(spans))
im = Image.new('1', (COLS, rows), 1)
for r, a, b in spans:
    for c in range(a, b):
        im.putpixel((c, r), 0)
