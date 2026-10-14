"""Báo IndexNow (Bing, Yandex, Seznam...) các URL trong sitemap sau mỗi lần deploy.
Chạy: py -3.14 hub/indexnow.py   (sau khi push main và GitHub Pages đã lên bản mới)
Key nằm ở config.json "indexnow"; build.py ghi file <key>.txt ra gốc site. Tài liệu: https://www.indexnow.org/documentation
"""
import json, re, urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parent
key = json.loads((HUB / "config.json").read_text(encoding="utf-8"))["indexnow"]
urls = re.findall(r"<loc>(.*?)</loc>", (HUB / "site" / "sitemap.xml").read_text(encoding="utf-8"))
body = json.dumps({"host": "swoonflicks.com", "key": key, "keyLocation": f"https://swoonflicks.com/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.status, len(urls), "URL")  # 200/202 = nhận; 422 = key/host lệch; 429 = gửi quá dày
