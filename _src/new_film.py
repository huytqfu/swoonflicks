"""Thêm phim mới: từ 1 file spec JSON sinh _src/content/<slug>.json + <slug>.seo.json đúng schema, tự lọc luật nội dung.

Chạy:  python3 _src/new_film.py spec.json            # kiểm + in kết quả, không ghi
       python3 _src/new_film.py spec.json --write    # ghi file (file đã có: chỉ bổ sung khoá còn thiếu, không đè)
       python3 _src/new_film.py --check [slug ...]   # chỉ lint file content đang có (synopsis lấy từ trang đã build)
Spec: xem _src/new-film.md. Chữ do người viết (intro, why, faq) chỉ được dùng tên riêng / con số có trong synopsis gốc.
Script không viết hộ intro/why: thiếu thì bỏ trống, build vẫn chạy (chỉ có FAQ + synopsis).
"""
import html, json, re, sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent
CONTENT = SRC / "content"
SITE = SRC.parent

NETWORKS = ["ReelShort", "ShortMax", "NetShort", "DramaBox", "GoodShort", "KalosTV", "Kalos", "DramaCPS", "ShortTV", "FlexTV",
            "MoboReels", "DramaWave", "MyDrama", "Sereal+", "TopShort", "StardustTV", "CandyJar", "iDrama", "ReelsGo"]
WEAPONS = ["sword", "blade", "dagger", "knife", "knives", "gun", "guns", "pistol", "rifle", "shotgun", "firearm", "bullet", "bomb",
           "explosive", "grenade", "machete"]
WATCH_Q = "Where can I watch {t}?"
WATCH_A = "Right here. Tap the drama to start watching on Swoonflicks, then tap Continue watching to keep going in the official app."
OK_CAPS = {"Swoonflicks", "Continue"}  # chữ hoa giữa câu luôn được phép (nút "Continue watching")


def ban_re(network=""):
    nets = NETWORKS + ([network] if network else [])
    net = "|".join(re.escape(n).replace(r"\ ", r"\s?") for n in nets)
    return re.compile(rf"(?i)\bfree\b|(?<![a-z])(?:{net})(?![a-z])|\b\d+\s*(?:short\s+)?(?:episodes?|eps?|chapters?)\b"
                      rf"|\bepisodes?\s+\d+|\b(?:dozens?|hundreds?)\s+(?:of\s+)?(?:short\s+)?episodes\b")


WEAPON_RE = re.compile(r"(?i)\b(?:" + "|".join(WEAPONS) + r")\b")


def built_title(slug):
    """Tên phim từ trang đã build (data-title của body)."""
    p = SITE / slug / "index.html"
    m = re.search(r'<body class="reel"[^>]*data-title="([^"]*)"', p.read_text(encoding="utf-8")) if p.exists() else None
    return html.unescape(m.group(1)) if m else ""


def film_titles():
    """Tên các phim đang có (để FAQ "similar" nhắc tên phim khác không bị coi là bịa)."""
    return {t for t in (built_title(p.name[:-9]) for p in CONTENT.glob("*.seo.json")) if t}


def caps_outside(text, allowed):
    """Từ viết hoa giữa câu (không phải đầu câu) không nằm trong allowed: dấu hiệu tên riêng bịa."""
    bad = []
    for m in re.finditer(r"(?<![\w'’-])([A-Z][\w'’-]*)", text):
        before = text[:m.start()].rstrip(' "“(')
        if not before or before[-1] in ".!?:;":
            continue  # đầu câu
        w = re.sub(r"['’]s$", "", m.group(1))
        lw = w.lower()
        if not {lw, lw + "s", lw[:-1] if lw.endswith("s") else lw} & allowed and w not in OK_CAPS:
            bad.append(w)
    return bad


def texts(ct, seo):
    """Mọi chữ khách nhìn thấy: (đường dẫn, chữ)."""
    out = [("seo.title", seo.get("title", "")), ("seo.description", seo.get("description", ""))]
    if ct.get("intro"):
        out.append(("intro", ct["intro"]))
    out += [(f"why[{i}]", x) for i, x in enumerate(ct.get("why", []))]
    for i, x in enumerate(ct.get("faq", [])):
        out += [(f"faq[{i}].q", x["q"]), (f"faq[{i}].a", x["a"])]
    return out


def lint(title, synopsis, ct, seo, network="", warn=None):
    """Trả danh sách lỗi (chuỗi). Rỗng = sạch. warn (list): nhận cảnh báo không chặn (keywords: build không đọc, khách không thấy)."""
    err, ban = [], ban_re(network)
    words = re.findall(r"[\w'’-]+", " ".join([synopsis, title, *film_titles()]).lower())
    allowed = set(words) | {re.sub(r"['’]s$", "", w) for w in words}  # so khớp không phân biệt hoa thường
    src_nums = set(re.findall(r"\d+", synopsis + " " + title))
    for path, s in texts(ct, seo):
        if title:
            s = re.sub(re.escape(title).replace("'", "['’]"), "", s, flags=re.I)  # tên phim được phép chứa mọi thứ (vd "Bow")
        for m in ban.finditer(s):
            err.append(f"{path}: chữ cấm {m.group()!r}")
        for m in WEAPON_RE.finditer(s):
            err.append(f"{path}: chi tiết vũ khí {m.group()!r}")
        for n in set(re.findall(r"\d+", s)) - src_nums:
            err.append(f"{path}: số {n} không có trong synopsis")
        if path not in ("faq[0].a", "seo.title"):  # câu "where to watch" và title theo mẫu cố định
            for w in caps_outside(s, allowed):
                err.append(f"{path}: tên riêng {w!r} không có trong synopsis/title")
    for k in ("episodes", "app"):
        u = (seo.get("sources") or {}).get(k)
        if u and not re.match(r"https?://[^/]+/.+", u):
            err.append(f"sources.{k}: phải là URL trang cụ thể, không phải trang chủ: {u}")
    for x in seo.get("keywords", []):
        if ban.search(x):
            (warn if warn is not None else err).append(f"keywords: chữ cấm trong {x!r}")
    t, d = seo.get("title", ""), seo.get("description", "")
    if len(t) > 60:
        err.append(f"seo.title dài {len(t)} > 60")
    if len(d) > 155:
        err.append(f"seo.description dài {len(d)} > 155")
    if re.search(r"(?i)episode", t):
        err.append("seo.title có chữ episode")
    return err


def sentences(s):
    s = re.sub(r"\s+", " ", s).strip()
    parts = re.split(r"(?<=[.!?])\s+", s)
    return [p for p in parts if p and not p.endswith(("...", "…"))]  # câu cụt cuối synopsis bị bỏ


def make(spec):
    """spec → (content, seo, việc máy nhà). Không bịa: chữ tự sinh chỉ lấy từ title + synopsis."""
    t, syn = spec["title"].strip(), spec["synopsis"].strip()
    genre = spec.get("genre", [])
    sents = sentences(syn)
    st = spec.get("seo_title") or next((x for x in (f"{t}: Where to Watch", f"{t}: Watch", t) if len(x) <= 60), t)
    desc = spec.get("seo_description")
    if not desc:
        tail = (f" A {' '.join(g.lower() for g in genre[:2])} short drama." if genre else "") + " Where to watch."
        desc = next((sents[0] + x for x in (tail, " Where to watch.") if sents and len(sents[0] + x) <= 155), "")
    low = t.lower()
    kw = [low, f"{low} short drama", f"{low} where to watch", f"watch {low} online"]
    kw += [f"{g.lower()} short drama" for g in genre] + [k.lower() for k in spec.get("keywords", [])]
    src = spec.get("sources") or {}
    seo = {"title": st, "description": desc, "keywords": list(dict.fromkeys(kw)),
           "sources": {"episodes": src.get("episodes"), "app": src.get("app"), **({"note": src["note"]} if src.get("note") else {})},
           "checked": spec.get("checked") or date.today().isoformat()}
    about = spec.get("about") or " ".join(sents[:3])
    faq = [{"q": WATCH_Q.format(t=t), "a": WATCH_A}, {"q": f"What is {t} about?", "a": about}] + spec.get("faq", [])
    ct = {**({"intro": spec["intro"]} if spec.get("intro") else {}), **({"why": spec["why"]} if spec.get("why") else {}), "faq": faq}
    slug = spec["slug"]
    home = [f"shelf.csv: thêm dòng film=<slug>-<id>, title={t!r}, app={spec.get('network', '?')}, link={spec.get('drama_url') or '?'}, ready=…",
            f"build.py GENRE: \"<slug>-<id>\": {json.dumps(genre)}",
            f"poster: material/.../films/<slug>-<id>/banner.jpg  (nguồn: {spec.get('poster') or 'chưa có'})"]
    if spec.get("app_home_url"):
        home.append(f"config.json ads_links: \"{slug}\": \"{spec['app_home_url']}\"  (chỉ khi đã chốt dùng cho ads)")
    if spec.get("trailer_url"):
        home.append(f"trailer: {spec['trailer_url']} → make_episodes.py / R2; trailer-dates.json chỉ điền ngày thật (Last-Modified)")
    return ct, seo, home


def merge_missing(path, new):
    """File đã có: chỉ thêm khoá còn thiếu (hoặc đang null), không đè chữ người viết. Trả (dict, [khoá đã thêm])."""
    if not path.exists():
        return new, list(new)
    cur = json.loads(path.read_text(encoding="utf-8"))
    added = []
    for k, v in new.items():
        if k not in cur:
            cur[k] = v
            added.append(k)
        elif isinstance(cur[k], dict) and isinstance(v, dict):
            for kk, vv in v.items():
                if cur[k].get(kk) is None and vv is not None:
                    cur[k][kk] = vv
                    added.append(f"{k}.{kk}")
    return cur, added


def dump(d):
    return json.dumps(d, ensure_ascii=False, indent=1) + "\n"


def built_synopsis(slug):
    """Synopsis gốc từ trang đã build (khối "The story")."""
    p = SITE / slug / "index.html"
    m = re.search(r"<summary>The story</summary><p>(.*?)</p>", p.read_text(encoding="utf-8"), re.S) if p.exists() else None
    return html.unescape(m.group(1)) if m else ""


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--check":
        slugs = argv[1:] or sorted(p.name[:-9] for p in CONTENT.glob("*.seo.json"))
        bad = 0
        for s in slugs:
            rd = lambda n: json.loads((CONTENT / n).read_text(encoding="utf-8")) if (CONTENT / n).exists() else {}
            seo, ct = rd(f"{s}.seo.json"), rd(f"{s}.json")
            title, syn, warn = built_title(s), built_synopsis(s), []
            spec = next(SRC.glob(f"lo3/{s}.json"), None)  # phim chưa build: lấy title + synopsis từ spec lô
            if spec and not syn:
                sp = json.loads(spec.read_text(encoding="utf-8"))
                title, syn = title or sp.get("title", ""), sp.get("synopsis", "")
            errs = lint(title, syn, ct, seo, warn=warn) + ([] if syn else ["không đọc được synopsis từ trang đã build"])
            bad += bool(errs)
            print(f"{'SẠCH' if not errs else 'LỖI '} {s}" + "".join(f"\n   - {x}" for x in errs)
                  + "".join(f"\n   ~ cảnh báo {x}" for x in warn))
        return 1 if bad else 0
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    for k in ("slug", "title", "synopsis"):
        if not spec.get(k):
            print(f"spec thiếu {k}")
            return 2
    todo = [k for k, v in spec.items() if v == "TODO"] + (["_draft"] if spec.get("_draft") else [])
    if todo:
        print(f"spec còn nháp, chưa sinh: {', '.join(todo)}")
        return 2
    ct, seo, home = make(spec)
    ban, warn = ban_re(spec.get("network", "")), []
    errs = [f"keywords: chữ cấm trong {x!r}" for x in seo["keywords"] if ban.search(x)]  # keywords sinh mới thì chặn
    cp, sp = CONTENT / f"{spec['slug']}.json", CONTENT / f"{spec['slug']}.seo.json"
    ct, add_c = merge_missing(cp, ct)
    seo, add_s = merge_missing(sp, seo)
    errs += lint(spec["title"], spec["synopsis"], ct, seo, spec.get("network", ""), warn=warn)
    if not seo.get("description"):
        errs.append("seo.description trống: câu đầu synopsis quá dài, điền seo_description tay")
    print(dump(seo) + dump(ct))
    print("Thêm vào file:", f"{cp.name}: {add_c or 'không'}; {sp.name}: {add_s or 'không'}")
    print("Việc máy nhà:\n  - " + "\n  - ".join(home))
    if warn:
        print("Cảnh báo (keywords cũ, build không đọc):\n  ~ " + "\n  ~ ".join(warn))
    if errs:
        print("LỖI (chưa ghi):\n  - " + "\n  - ".join(errs))
        return 1
    if "--write" in argv:
        cp.write_text(dump(ct), encoding="utf-8")
        sp.write_text(dump(seo), encoding="utf-8")
        print(f"Đã ghi {cp.relative_to(SITE)}, {sp.relative_to(SITE)}")
    else:
        print("Sạch. Thêm --write để ghi.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
