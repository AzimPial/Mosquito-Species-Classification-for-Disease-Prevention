import os, base64

MAIN = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(MAIN, "poster_A0.png")
SVG = os.path.join(MAIN, "poster_A0.svg")

# A0 in mm: 841 x 1189
A0_W_MM = 841
A0_H_MM = 1189

with open(PNG, "rb") as f:
    png_data = f.read()
b64 = base64.b64encode(png_data).decode("ascii")

# Build SVG with proper XML structure
svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{A0_W_MM}mm"
     height="{A0_H_MM}mm"
     viewBox="0 0 {A0_W_MM} {A0_H_MM}"
     preserveAspectRatio="xMidYMid meet">
  <title>Mosquito Species Classification Poster - A0</title>
  <desc>Research poster for mosquito species classification using CNN architectures</desc>
  <rect width="{A0_W_MM}" height="{A0_H_MM}" fill="#F5E9DD"/>
  <image
    xlink:href="data:image/png;base64,{b64}"
    x="0" y="0"
    width="{A0_W_MM}mm" height="{A0_H_MM}mm"
    preserveAspectRatio="xMidYMid meet"
    image-rendering="auto"/>
</svg>'''

with open(SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

size = os.path.getsize(SVG)
print(f"[OK] wrote {SVG}  ({size:,} bytes)")
print(f"  PNG original: {len(png_data):,} bytes")
print(f"  SVG embedded: {len(b64):,} bytes (base64)")
print(f"  A0 dimensions: {A0_W_MM}mm x {A0_H_MM}mm")
