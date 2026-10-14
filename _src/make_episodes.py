"""Sinh hub/episodes.json: danh sách tập free + tập trả phí cho player lướt dọc.

Mỗi phim (ke/shelf.csv ready=CO):
  total  = tổng số tập (RS: chapter_count; DramaCPS: null = chưa verify)
  free   = số tập free (tập n > free là trả phí, khoá + mở link affiliate)
  cta    = link affiliate của sếp (CPS)
  eps[]  = mỗi tập free: {"n", "src": "yt"|"rs"|null, "id" (yt) | "url" (iframe rs)}
Ưu tiên YouTube @swoonflicks (YT trong build.py), thiếu thì iframe chính chủ RS Boost
(info.json chapters[].iframe_src, có cps_id + code của sếp). src=null = chưa có nguồn nhúng.
"""
import csv, json, re
from pathlib import Path

HUB = Path(__file__).parent
SD = HUB.parent
src = (HUB / "build.py").read_text(encoding="utf-8")
ns = {}
exec(re.search(r"^RS_LINK = \{.*?^\}", src, re.S | re.M).group(0), ns)
exec(re.search(r"^YT = \{.*?^\}", src, re.S | re.M).group(0), ns)
RS_LINK, YT = ns["RS_LINK"], ns["YT"]

out = {}
for r in csv.DictReader(open(SD / "ke" / "shelf.csv", encoding="utf-8")):
    if r["ready"] != "CO":
        continue
    d = next((SD / "material" / k / "films" / r["film"] for k in ("rs", "dramacps")
              if (SD / "material" / k / "films" / r["film"]).exists()), None)
    if not d:
        continue
    info = json.loads((d / "info.json").read_text(encoding="utf-8"))
    free = int(info["pay_start"]) - 1
    total = int(info["chapter_count"]) if info.get("chapter_count") else None
    rs = {int(c["t_chapter_id"]): c["iframe_src"].strip() for c in info.get("chapters") or [] if c.get("iframe_src")}
    yt = {int(re.sub(r"\D", "", lab)): vid for lab, vid in YT.get(r["film"], [])}
    eps = []
    for n in range(1, free + 1):
        if n in yt:
            eps.append({"n": n, "src": "yt", "id": yt[n]})
        elif n in rs:
            eps.append({"n": n, "src": "rs", "url": rs[n]})
        else:
            eps.append({"n": n, "src": None})
    slug = re.sub(r"-[0-9a-f]{6,8}$", "", r["film"])
    ct = HUB / "site" / "_src" / "content" / f"{slug}.json"  # total thiếu → lấy số tập trang chính chủ (sources trong file content)
    if total is None and ct.exists():
        m = re.search(r"(\d+) episodes", json.loads(ct.read_text(encoding="utf-8"))["faq"][0]["a"])
        total = int(m.group(1)) if m else None
    out[r["film"]] = {"slug": slug, "title": r["title"], "total": total,
                      "free": free, "cta": r["link"] or RS_LINK.get(r["film"]) or info.get("link"), "eps": eps}

(HUB / "episodes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in out.items():
    c = {s: sum(1 for e in v["eps"] if e["src"] == s) for s in ("yt", "rs", None)}
    print(f"{v['slug'][:38]:38} total={v['total']} free={v['free']} yt={c['yt']} rs={c['rs']} thieu={c[None]}")
