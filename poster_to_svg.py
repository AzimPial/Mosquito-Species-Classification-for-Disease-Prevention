import os

MAIN = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(MAIN, "poster_A0.png")
SVG = os.path.join(MAIN, "poster_A0.svg")

# A0 in mm: 841 x 1189
A0_W_MM = 841
A0_H_MM = 1189

svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{A0_W_MM}mm" height="{A0_H_MM}mm"
     viewBox="0 0 {A0_W_MM} {A0_H_MM}">
  <title>Mosquito Species Classification Poster</title>
  <image xlink:href="poster_A0.png"
         x="0" y="0" width="{A0_W_MM}" height="{A0_H_MM}"
         preserveAspectRatio="none"/>
</svg>'''

with open(SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

total = os.path.getsize(SVG)
print(f"[OK] wrote {SVG}  ({total:,} bytes)  A0: {A0_W_MM}x{A0_H_MM}mm")
print(f"References external file: poster_A0.png (must stay in same folder)")
