# Bộ favicon từ logo v3c: nền đen #0b0709, mark căn giữa, chừa lề để không bị cắt (kể cả mask tròn Android).
from PIL import Image
import json
SRC = "../brand/_v3c-khe-nac-2026-09-30/logo-mark-1024-transparent.png"
BG = (11, 7, 9, 255)
mark = Image.open(SRC).convert("RGBA")
mark = mark.crop(mark.getbbox())

def icon(n, fill):
    c = Image.new("RGBA", (n, n), BG)
    s = round(n * fill)
    w, h = mark.size
    k = s / max(w, h)
    m = mark.resize((round(w * k), round(h * k)), Image.LANCZOS)
    c.alpha_composite(m, ((n - m.width) // 2, (n - m.height) // 2))
    return c.convert("RGB")

for n in (48, 96, 192, 512):
    icon(n, 0.84).save(f"site/icon-{n}.png", optimize=True)
icon(180, 0.78).save("site/apple-touch-icon.png", optimize=True)
icon(512, 0.84).save("site/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
json.dump({"name": "Swoonflicks", "short_name": "Swoonflicks", "start_url": "/", "display": "standalone",
           "background_color": "#0b0709", "theme_color": "#0b0709",
           "icons": [{"src": f"/icon-{n}.png", "sizes": f"{n}x{n}", "type": "image/png"} for n in (192, 512)]},
          open("site/site.webmanifest", "w"), indent=1)
print("ok")
