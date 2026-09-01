import os, base64

MAIN = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(MAIN, "poster_A0.png")
SVG = os.path.join(MAIN, "poster_A0.svg")

A0_W_MM = 841
A0_H_MM = 1189

with open(PNG, "rb") as f:
    png_data = f.read()
b64 = base64.b64encode(png_data).decode("ascii")

svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{A0_W_MM}mm" height="{A0_H_MM}mm"
     viewBox="0 0 {A0_W_MM} {A0_H_MM}">
  <title>Mosquito Species Classification Poster</title>
  <desc>Research poster for mosquito species classification using CNN architectures - A0 size</desc>
  <image xlink:href="data:image/png;base64,{b64}"
         x="0" y="0"
         width="{A0_W_MM}" height="{A0_H_MM}"
         preserveAspectRatio="none"/>
</svg>'''

with open(SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

total = os.path.getsize(SVG)
print(f"[OK] wrote {SVG}  ({total:,} bytes)")
print(f"  A0: {A0_W_MM} x {A0_H_MM} mm ({int(A0_W_MM/25.4*100)/100} x {int(A0_H_MM/25.4*100)/100} in)")
print(f"  Self-contained (base64 embedded PNG inside) - opens on any device")