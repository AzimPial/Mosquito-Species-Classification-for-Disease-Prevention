import os, base64

MAIN = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(MAIN, "poster_A0.png")
SVG = os.path.join(MAIN, "poster_A0.svg")

A0_W_MM = 841
A0_H_MM = 1189

with open(PNG, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{A0_W_MM}mm" height="{A0_H_MM}mm"
     viewBox="0 0 {A0_W_MM} {A0_H_MM}">
  <image xlink:href="data:image/png;base64,{b64}"
         x="0" y="0"
         width="{A0_W_MM}mm" height="{A0_H_MM}mm"
         preserveAspectRatio="none"/>
</svg>'''

with open(SVG, "w") as f:
    f.write(svg.strip())

size = os.path.getsize(SVG)
print(f"[OK] wrote {SVG}  ({size:,} bytes)")
