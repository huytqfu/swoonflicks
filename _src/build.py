"""Website swoonflicks.com: hub (kệ phim) + handcliff (1 trang / phim) + bản bio theo nguồn. Sếp giao 13/10 16:23.
Đọc ke/shelf.csv (ready=CO + link, phim RS lấy RS_LINK) → hub/site/ (repo huytqfu/swoonflicks, GitHub Pages).
Chạy: py -3.14 hub/build.py
- Concept brand v3c: đen hồng, Poppins, logo lockup "oo" móc xích + "Romance novels, now on screen" (sếp 14/10: bỏ vàng royal). CSS: hub/site.css.
- Không hiện tên network (ReelShort/DramaCPS) cho người xem; f["app"] chỉ còn trong tracking nội bộ (sếp 14/10).
- Tracking: hub/t.js (GA4 + Meta + TikTok, ID ở hub/config.json, trống = không tải). Nút ra app = link CPS gốc, không cloak.
- Video: trang phim lướt dọc kiểu Reels (_src/reel.js + reel.css), tập lấy từ hub/episodes.json (make_episodes.py: mp4 gốc DramaCPS tự host R2 > iframe chính chủ RS Boost > chưa có nguồn).
  Lưới tập đồng đều, không lộ số tập free; chạm tập trả phí đầu thì tự nhảy link app (sếp 14/10). Không ghi tên app trên trang trừ dòng "Continue Episode N on <app>" khi khách quay lại.
- Build xoá thư mục sinh (có file .gen), img/, assets/; giữ .git + CNAME.
"""
import csv, html, json, re, shutil
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw

SD = Path(__file__).resolve().parent.parent
HUB = SD / "hub"
OUT = HUB / "site"
BASE = "https://swoonflicks.com"
FONTS = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap"

# Link CPS RS Boost (reelslink) lấy từ caption X/YT đã đăng
RS_LINK = {
    "rejected-luna-is-the-alpha-queen-69fa0a97": "https://reelslink.com/cps/xwAWVb",
    "the-empresss-final-wish-6a06bb65": "https://reelslink.com/cps/uGhlNR",
}
# Thứ tự: phim đang đăng gần nhất lên đầu
ORDER = ["dragons-bow-to-the-trash-638707", "mommy-i-m-not-lying-646011", "mech-god-from-the-dark-side-of-the-moon-635894",
         "the-unbound-rise-of-the-godslayer-647593", "i-spoke-baby-dragon-and-won-everyone-over-628653"]
# Web chỉ chiếu tập GỐC chưa cook (sếp 15/10): bản cook trên YouTube/Facebook để lại cho social, không nhúng nữa.
# Map để trống nhưng giữ khung (make_episodes.py đọc bằng regex); 3 phim DramaCPS chiếu mp4 gốc tự host R2, phim RS dùng iframe RS Boost.
YT = {
}
FB = {
}
GENRE = {
    "dragons-bow-to-the-trash-638707": ["Fantasy"],
    "mommy-i-m-not-lying-646011": ["Family"],
    "mech-god-from-the-dark-side-of-the-moon-635894": ["Sci-Fi", "Revenge"],
    "the-unbound-rise-of-the-godslayer-647593": ["Fantasy"],
    "i-spoke-baby-dragon-and-won-everyone-over-628653": ["Fantasy"],
    "rejected-luna-is-the-alpha-queen-69fa0a97": ["Fantasy", "Romance", "Revenge"],
    "the-empresss-final-wish-6a06bb65": ["Royal", "Family"],
    "my-billionaire-boss-wont-let-me-quit-6a792e03": ["Romance"],
    # lô DramaCPS 15/10, suy từ description trong info.json
    "my-voice-saves-my-family-643562": ["Family", "Fantasy"],
    "my-sister-s-boyfriend-arrested-me-639196": ["Family", "Revenge"],
    "don-t-touch-the-legendary-lawyer-s-grandson-636806": ["Family", "Revenge"],
    "not-your-average-crow-634222": ["Fantasy"],
    "the-little-jinx-is-a-lucky-star-133039": ["Family", "Fantasy"],
    "she-dumped-a-ceo-for-her-sugar-baby-649297": ["Revenge", "Romance"],  # tag RS: Romance, Billionaire, Workplace (material/rs/films/<slug>/info.json)
}
# 6 kênh, handle chung @swoonflicks (sếp 14/10 02:21: đủ 6 nền, có logo + handle). Logo: Simple Icons (CC0).
SOCIAL = [
    ("TikTok", "https://www.tiktok.com/@swoonflicks", "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"),
    ("Instagram", "https://www.instagram.com/swoonflicks", "M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"),
    ("YouTube", "https://www.youtube.com/@swoonflicks", "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"),
    ("Facebook", "https://www.facebook.com/swoonflicks", "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"),
    ("Threads", "https://www.threads.net/@swoonflicks", "M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285 1.33-3.082.88-.76 2.119-1.207 3.583-1.291a13.853 13.853 0 0 1 3.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844 0-1.992.232-2.721 1.32L7.734 7.847c.98-1.454 2.568-2.256 4.478-2.256h.044c3.194.02 5.097 1.975 5.287 5.388.108.046.216.094.321.142 1.49.7 2.58 1.761 3.154 3.07.797 1.82.871 4.79-1.548 7.158-1.85 1.81-4.094 2.628-7.277 2.65Zm1.003-11.69c-.242 0-.487.007-.739.021-1.836.103-2.98.946-2.916 2.143.067 1.256 1.452 1.839 2.784 1.767 1.224-.065 2.818-.543 3.086-3.71a10.5 10.5 0 0 0-2.215-.221z"),
    ("X", "https://x.com/swoonflicks", "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"),
]
# Link bio từng nền: lưới poster, bấm poster phim nào ra thẳng link CPS gốc phim đó (sếp 14/10 02:04). Phim đang đăng xếp đầu:
# config.json "bio_first" (slug). Link ads: /go/<slug>/ một phim một nút. Không nhúng phim, không tự chuyển. Nguồn gắn khi URL không mang utm.
BIO = {"ig": "instagram", "tt": "tiktok", "yt": "youtube", "fb": "facebook", "th": "threads", "x": "x"}

e = html.escape
CFG_F = HUB / "config.json"
if not CFG_F.exists():
    CFG_F.write_text(json.dumps({"ga4": "", "meta": "", "tiktok": ""}, indent=1), encoding="utf-8")
CFG = json.loads(CFG_F.read_text(encoding="utf-8"))
CSS = (HUB / "site.css").read_text(encoding="utf-8")
ARROW = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 0l6 5-6 5z"/></svg>'
EXT = '<svg class="ext" viewBox="0 0 12 12" aria-hidden="true"><path d="M4 1h7v7M11 1L3 9M1 4v7h7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'


def film_dir(fid):
    for k in ("dramacps", "rs"):
        d = SD / "material" / k / "films" / fid
        if d.exists():
            return d


def synopsis(d):
    info = json.loads((d / "info.json").read_text(encoding="utf-8")) if (d / "info.json").exists() else {}
    t = info.get("description") or info.get("desc") or ""
    if not t and (d / "desc.txt").exists():
        t = (d / "desc.txt").read_text(encoding="utf-8").split("\n", 2)[-1]
    return " ".join(t.split())


def cut(t, n):
    return t if len(t) <= n else t[:n - 1].rsplit(" ", 1)[0] + "…"


def metal(t):
    return f'<span class="m">{e(t)}</span>'


def head(title, desc, path, img=None, extra="", noindex=False, src="", lang="en"):
    cfg = {k: CFG.get(k, "") for k in ("ga4", "meta", "tiktok", "ttapi", "fbapi")}; cfg["src"] = src  # chỉ ID tracking ra trang; không rò "invite"/"gate" (mã mời) vào HTML
    # Google Ads conversion (AW-ID + label): chỉ ra trang khi config có đủ cả hai; trống thì HTML y như cũ
    if CFG.get("gads") and CFG.get("gads_label"): cfg.update(gads=CFG["gads"], gads_label=CFG["gads_label"])
    # OG phim là ảnh dọc 600x800: summary_large_image (khung ngang) sẽ cắt nát, dùng summary; home.jpg ngang giữ large
    tw = "summary_large_image" if img and img.endswith("home.jpg") else "summary"
    wh = (1200, 630) if img and img.endswith("home.jpg") else (600, 800)
    og = (f'<meta property="og:image" content="{BASE}{img}"><meta property="og:image:width" content="{wh[0]}">'
          f'<meta property="og:image:height" content="{wh[1]}"><meta name="twitter:card" content="{tw}">') if img else ""
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
{f'<link rel="canonical" href="{BASE}{path}">' if path else ''}{'<meta name="robots" content="noindex,follow">' if noindex else ''}
<meta name="theme-color" content="#0b0709"><link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/icon-96.png" sizes="96x96" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="{'video.tv_show' if img and '/og/' in img and not img.endswith('home.jpg') else 'website'}"><meta property="og:site_name" content="Swoonflicks">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">{f'<meta property="og:url" content="{BASE}{path}">' if path else ''}{og}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<style>{CSS}</style>
<script>window.SF={json.dumps(cfg)}</script><script src="/assets/t.js" defer></script>{extra}
</head>'''


FOOT = '''<p class="ft">Swoonflicks shares short dramas we love.<br>
Some links are affiliate links: we may earn a commission when you keep watching, at no extra cost to you.<br>
<a href="/privacy/">Privacy</a> · <a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>'''


def social():
    return '<p class="h3">Follow for new parts</p><nav class="soc">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank" aria-label="{n} @swoonflicks"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg>'
        f'<span><b>{n}</b>@swoonflicks</span></a>' for n, u, d in SOCIAL) + "</nav>"


ADS = CFG.get("ads_links") or {}


def ads_href(f):
    """Link DramaCPS riêng cho Google Ads (config "ads_links": slug → URL). Có thì thêm data-ads-href, t.js đổi href khi phiên đến từ Google Ads; href mặc định vẫn là link organic."""
    u = ADS.get(f["slug"])
    return f' data-ads-href="{e(u)}"' if u else ""


def related(f, films, n=3):
    """Phim cùng nhóm thể loại (GENRE): nhiều thể loại chung xếp trước, hoà thì theo thứ tự kệ. Không trùng thể loại thì không gợi ý."""
    g = set(f["genre"])
    pool = [(-len(g & set(o["genre"])), i, o) for i, o in enumerate(films) if o is not f and g & set(o["genre"])]
    return [o for _, _, o in sorted(pool, key=lambda x: x[:2])[:n]]


def card(f, big=False, lazy=True):
    img = f"/img/{f['slug']}-h.webp" if big else f"/img/{f['slug']}.webp"  # thẻ to = poster 3:4 nguyên khung, không cắt tên phim (sếp 15/10)
    w, h = (720, 960) if big else (360, 480)
    return f'''<a class="cd{' big' if big else ''}" href="/{f['slug']}/" data-genre="{e('|'.join(f['genre']))}">
<img src="{img}" alt="{e(f['title'])} poster" width="{w}" height="{h}"{' loading="lazy"' if lazy else ' fetchpriority="high"' if big else ''} decoding="async">
<div class="in"><h2>{e(f['title'])}</h2><span class="go">Watch now {ARROW}</span></div></a>'''


JS_HUB = '''<script>(function(){var sel={genre:''},cards=[].slice.call(document.querySelectorAll('.grid .cd')),em=document.querySelector('.empty');
document.querySelectorAll('.chip').forEach(function(c){c.onclick=function(){var k=c.dataset.k;sel[k]=c.dataset.v;
document.querySelectorAll('.chip[data-k='+k+']').forEach(function(x){x.setAttribute('aria-pressed',x===c)});var n=0;
cards.forEach(function(d){var ok=(!sel.genre||d.dataset.genre.split('|').indexOf(sel.genre)>=0);d.hidden=!ok;if(ok)n++});
em.hidden=n>0;if(window.SFT)SFT.track('Filter',{key:k,value:c.dataset.v||'all'})}});
em.querySelector('.clr').onclick=function(){document.querySelectorAll('.chip[data-v=""]').forEach(function(c){c.click()})}})()</script>'''


def hub_page(films, path="/", src=""):
    ig = path != "/"
    genres = sorted({g for f in films for g in f["genre"]}, key=lambda g: (g != "Romance", g))
    chip = lambda k, v, lbl, on=False: f'<button type="button" class="chip" data-k="{k}" data-v="{e(v)}" aria-pressed="{str(on).lower()}">{e(lbl)}</button>'
    flt = ('<div class="flt"><div class="chips" role="group" aria-label="Filter by genre"><b aria-hidden="true">Genre</b>' + chip("genre", "", "All", True) + "".join(chip("genre", g, g) for g in genres) + "</div></div>")
    grid = "\n".join(card(f, big=(i == 0 and not ig), lazy=(i > 3)) for i, f in enumerate(films))
    desc = "The short dramas everyone is binging. Pick a drama and start watching."
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Swoonflicks", "url": f"{BASE}/", "description": desc},
          {"@context": "https://schema.org", "@type": "Organization", "name": "Swoonflicks", "url": f"{BASE}/",
           "logo": f"{BASE}/img/logo-128.png", "sameAs": [u for _, u, _ in SOCIAL]},
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{BASE}/{f['slug']}/", "name": f["title"]} for i, f in enumerate(films)]}]
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if path == "/" else ""
    return head("Swoonflicks · Short dramas to binge", desc, "/", "/img/og/home.jpg", extra, noindex=(path != "/"), src=src) + f'''
<body><main class="wrap">
<header class="hd{' sm' if ig else ''}"><h1><img class="lk" src="/img/lockup.png" alt="Swoonflicks · Romance novels, now on screen" width="681" height="150"></h1>
<p class="tag">{"Find the drama you saw." if ig else "Tap a drama and start watching."}</p></header>
{flt}<div class="grid">{grid}</div><div class="empty" hidden><p>No drama in this genre yet.</p><button type="button" class="chip clr">Show all</button></div>
{social()}{FOOT}</main>{JS_HUB}</body></html>'''


_TD = None


def trailer_date(slug):
    """Ngày đăng thật của trailer (tập 1 trên R2) từ site/_src/trailer-dates.json, dạng ISO 8601. Không có hoặc sai định dạng thì trả None."""
    global _TD
    if _TD is None:
        p = OUT / "_src" / "trailer-dates.json"
        _TD = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    v = _TD.get(slug) or ""
    return v if re.fullmatch(r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?)?", v) else None


def content(slug):
    # nội dung riêng từng phim: site/_src/content/<slug>.json (+ .seo.json), viết tay, có thể thiếu
    d = OUT / "_src" / "content"
    rd = lambda n: json.loads((d / n).read_text(encoding="utf-8")) if (d / n).exists() else {}
    return rd(f"{slug}.json"), rd(f"{slug}.seo.json")


def episodes(f):
    """Từ episodes.json: (tổng tập hoặc None, số tập free, [(n, nền, id|url|None)]). Nền: mp4 (R2) / yt / fb / rs (iframe RS Boost) / None (chưa có nguồn)."""
    x = EPS.get(f["id"], {})
    eps = [(e["n"], e.get("src"), e.get("id") or e.get("url")) for e in x.get("eps", [])]
    return x.get("total"), x.get("free") or len(eps), eps


LOCK = '<svg class="lock" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 10V7a5 5 0 0 1 10 0v3h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V11a1 1 0 0 1 1-1zm2 0h6V7a3 3 0 0 0-6 0z"/></svg>'
PLAY = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M1 0l9 5-9 5z"/></svg>'


def film_page(f, films):
    """Trang phim kiểu Reels: mỗi tập 1 màn, vuốt dọc. Tập free có nguồn thì phát (mp4 gốc tự host R2, hoặc iframe chính chủ RS Boost);
    tập free chưa có nguồn = poster + nút mở app (không giả play). Không lộ số tập free ở đâu (sếp 14/10 02:21).
    Hết tập free: màn khoá + nút lớn, khách tự bấm (không đếm ngược, không tự chuyển).
    Tên app chỉ hiện ở dòng "Continue Episode N on <app>" khi khách quay lại sau khi đã ra app (reel.js)."""
    syn = f["syn"]
    ct, seo = content(f["slug"])
    total, free, eps = episodes(f)
    poster = f"/img/{f['slug']}-h.webp"
    gate = free + 1  # tập trả phí đầu tiên = màn khoá
    aff = lambda place, ep=None: (f'href="{e(f["link"])}"{ads_href(f)} rel="nofollow sponsored noopener" data-aff="{place}" '
                                  f'data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}"' + (f' data-ep="{ep}"' if ep else ""))
    # gộp các tập free liền nhau chưa có nguồn thành 1 màn
    groups = []
    for n, k, v in eps:
        if not k and groups and not groups[-1][1]:
            groups[-1][0].append(n)
        else:
            groups.append(([n], k, v))
    slides = []
    for i, (ns, k, v) in enumerate(groups):
        n = ns[0]
        lbl = f"Episode {n}"
        ttl = f'<h1>{e(f["title"])}</h1>' if i == 0 else f'<p class="t">{e(f["title"])}</p>'
        cap = ttl + f'<p class="ep">{lbl}</p>'
        lazy = '' if i == 0 else ' loading="lazy"'
        if k:
            slides.append(f'''<section class="sl fr" data-ep="{n}" data-k="{k}" data-v="{e(v)}" aria-label="{lbl}">
<div class="stg"><img class="ps" src="{poster}" alt="" width="720" height="960"{' fetchpriority="high"' if i == 0 else lazy}>
<button type="button" class="play" aria-label="Play episode {n}"><span>{PLAY}</span></button>
<div class="cap">{cap}</div></div></section>''')
        else:
            slides.append(f'''<section class="sl lk st" data-ep="{n}" data-last="{ns[-1]}" aria-label="{e(f["title"])}">
<img class="bg" src="{poster}" alt="" width="720" height="960"{' fetchpriority="high"' if i == 0 else lazy}>
<div class="gt">{ttl}<p class="cont" hidden></p><a class="unl" {aff("free", n)}>Watch in the official app {EXT}</a>
<p class="nt">Opens the official app · affiliate link</p></div></section>''')
    if any(k for n, k, v in eps): slides.append(f'''<section class="sl lk gate" data-ep="{gate}" aria-label="Keep watching">
<img class="bg" src="{poster}" alt="" width="720" height="960" loading="lazy">
<div class="gt">{LOCK}<p class="t">{e(f["title"])}</p>
<p class="cont" hidden></p>
<a class="unl" {aff("gate", gate)}>Continue watching {EXT}</a>
<p class="nt">Opens the official app · affiliate link</p></div></section>''')
    rel = related(f, films)
    relh = ('<p class="h3">More like this</p><div class="more">' + "".join(card(o) for o in rel) + "</div>") if rel else ""
    more = "".join(card(o) for o in films if o is not f and o not in rel)
    ld = {"@context": "https://schema.org", "@type": "TVSeries", "name": f["title"], "description": cut(syn, 300),
          "image": f"{BASE}/img/og/{f['slug']}.jpg", "url": f"{BASE}/{f['slug']}/", "genre": f["genre"],
          "inLanguage": "en"}
    mp = [(n, v) for n, k, v in eps if k == "mp4"]
    up = trailer_date(f["slug"])
    if mp and up:  # trailer = tập 1 trên R2; Google bắt buộc uploadDate cho VideoObject, chưa có ngày thật thì bỏ hẳn khối trailer
        ld["trailer"] = {"@type": "VideoObject", "name": f"{f['title']} Episode {mp[0][0]}", "contentUrl": mp[0][1],
                         "thumbnailUrl": f"{BASE}/img/og/{f['slug']}.jpg", "description": cut(syn, 200), "uploadDate": up}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Swoonflicks", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": f["title"], "item": f"{BASE}/{f['slug']}/"}]}
    lds = [ld, bc]
    faq = ct.get("faq", [])
    if faq:  # FAQPage khớp đúng chữ hiển thị
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in faq]})
    extra = ('<link rel="stylesheet" href="/assets/reel.css">' + ('<link rel="preconnect" href="https://media.swoonflicks.com">' if mp else "") +
             f'<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>')
    title = seo.get("title") or f"{f['title']} · Watch now | Swoonflicks"
    about = ""
    if ct.get("intro"):
        about = f'<section class="syn ab"><h2>Why watch</h2><p>{e(ct["intro"])}</p>' + (
            "<ul>" + "".join(f"<li>{e(x)}</li>" for x in ct.get("why", [])) + "</ul>" if ct.get("why") else "") + "</section>"
    faqh = ('<section class="syn faq"><h2>Questions</h2>' + "".join(
        f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in faq) + "</section>") if faq else ""
    return head(title, seo.get("description") or cut(syn, 155), f"/{f['slug']}/", f"/img/og/{f['slug']}.jpg", extra) + f'''
<body class="reel" data-film="{e(f['slug'])}" data-title="{e(f['title'])}" data-app="{e(f['app'])}">
<header class="rt"><a class="bk" href="/" aria-label="All dramas">‹</a><span class="ct" aria-live="polite"></span></header>
<img class="rbg" src="{poster}" alt="" width="720" height="960" aria-hidden="true">
<main class="rl">{"".join(slides)}
<section class="sl info"><div class="wrap"><{"h2" if slides else "h1"} class="it">{e(f['title'])}</{"h2" if slides else "h1"}>
{about}<details class="syn" open><summary>The story</summary><p>{e(syn)}</p></details>
{faqh}
{relh}<p class="h3">More dramas</p><div class="more">{more}</div>
{social()}{FOOT}</div></section></main>
<script src="/assets/reel.js" defer></script></body></html>'''


def bio_page(films, path, src):
    """Link-in-bio: lưới poster, mỗi poster là link affiliate gốc của phim đó (bắn ClickAffiliate kèm slug)."""
    k = path.strip("/")
    tiles = "\n".join(f'''<a class="cd" href="{e(f["link"])}"{ads_href(f)} rel="nofollow sponsored noopener" data-aff="{k}" data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}">
<img src="/img/{f['slug']}.webp" alt="{e(f['title'])} poster" width="360" height="480"{'' if i < 4 else ' loading="lazy"'} decoding="async">
<div class="in"><h2>{e(f['title'])}</h2><span class="go">Watch now {ARROW}</span></div></a>''' for i, f in enumerate(films))
    return head("Swoonflicks · Watch the drama", "Tap a drama to keep watching.", path, "/img/og/home.jpg", noindex=True, src=src) + f'''
<body class="bio"><main class="wrap">
<header class="hd sm"><h1><img class="lk" src="/img/lockup.png" alt="Swoonflicks · Romance novels, now on screen" width="681" height="150"></h1>
<p class="tag">Tap the drama you saw to keep watching.</p></header>
<div class="grid">{tiles}</div>
<p class="note">Each poster opens the official app · affiliate link</p>
{social()}{FOOT}</main></body></html>'''


def one_page(f, path, src=""):
    """Trang một nút: poster + tên phim + nút to ra link affiliate gốc (bắn ClickAffiliate qua data-aff). Khách tự bấm, không redirect."""
    aff = (f'href="{e(f["link"])}"{ads_href(f)} rel="nofollow sponsored noopener" data-aff="go" '
           f'data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}"')
    return head(f"{f['title']} · Watch now | Swoonflicks", cut(f["syn"], 155), path, f"/img/og/{f['slug']}.jpg", noindex=True, src=src) + f'''
<body class="one" data-film="{e(f['slug'])}" data-title="{e(f['title'])}" data-app="{e(f['app'])}"><main class="wrap">
<a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="120" height="26"></a>
<a class="po" {aff}><img src="/img/{f['slug']}-h.webp" alt="{e(f['title'])} poster" width="720" height="960" fetchpriority="high"></a>
<h1 class="m">{e(f['title'])}</h1>
<a class="cta" {aff}><span>Watch the full drama</span>{EXT}</a>
<p class="note">Opens the official app · affiliate link</p>
<a class="more1" href="/">More dramas on Swoonflicks</a>
</main></body></html>'''


def privacy_page():
    return head("Privacy · Swoonflicks", "How Swoonflicks uses cookies and measurement.", "/privacy/", "/img/og/home.jpg") + '''
<body><main class="wrap doc"><div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="120" height="26"></a></div>
<h1>Privacy</h1>
<p>Swoonflicks is a fan site that shares episodes of short dramas and links to the apps where you can watch the rest.</p>
<h2>What we measure</h2>
<ul><li>Which drama pages you open, whether you play an episode and how far you watch.</li>
<li>Whether you tap a link to a drama app, and which page or social profile brought you here (from the link's utm or click id).</li></ul>
<h2>Tools we use</h2>
<p>When enabled, Google Analytics, the Meta Pixel and the TikTok Pixel receive these events so we can count visits and show
our videos to people who are likely to enjoy them. Episodes play through YouTube's privacy-enhanced mode (youtube-nocookie.com)
and only load when you press play; pressing play also loads YouTube's player script from youtube.com.</p>
<h2>Your choice</h2>
<p>Visitors in the EU and UK are asked before any of these tools load. You can change your answer at any time:
<button type="button" class="chip" onclick="try{localStorage.removeItem('sf_consent')}catch(e){}location.reload()">Cookie settings</button></p>
<h2>Invite code emails</h2>
<p>If you ask for a creator invitation code on our invite pages, we use the email address you enter to send you that one email
(the code, the sign-up link and a short checklist) and keep it, with the date and page, so we can answer questions and stop abuse.
We do not add you to a newsletter. Write to <a href="mailto:partner@swoonflicks.com">partner@swoonflicks.com</a> to have it deleted.
The form is protected by Cloudflare Turnstile, which checks that you are not a bot.</p>
<h2>Affiliate links</h2>
<p>Links to drama apps are affiliate links. If you watch or subscribe there, we may earn a commission at no extra cost to you.
What you do inside those apps is covered by their own privacy policies.</p>
<h2>Contact</h2><p><a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>
''' + FOOT + "</main></body></html>"


def invite_page(inv):
    """Trang /invite/: mã mời làm affiliate (RS Boost, DramaCPS...). Chỉ mục có code thật trong config.json "invite" mới hiện."""
    def block(i):
        if GATE.get("endpoint"):  # cổng email: mã không in ra trang, form gửi mã qua mail
            return f'''<section class="syn ab"><h2>{e(i["program"])}</h2><p>{e(i.get("note", ""))}</p>
{f'<p class="note"><a href="{e(i["guide"])}"><u>Step-by-step guide and FAQ</u></a></p>' if i.get("guide") else ""}</section>''' + gate_box(i, "en", i.get("disclosure", ""))
        return f'''<section class="syn inv"><h2>{html.escape(i["program"])}</h2>
<p>{html.escape(i.get("note", ""))}</p>
<div class="code"><b>{html.escape(i["code"])}</b><button type="button" data-copy="{html.escape(i["code"])}" data-prog="{html.escape(i["program"])}">Copy</button></div>
{f'<a class="cta" href="{html.escape(i["signup"])}" rel="noopener" target="_blank">Sign up for {html.escape(i["program"])} {ARROW}</a>' if i.get("signup") else ""}
{f'<p class="note"><a href="{html.escape(i["guide"])}"><u>Step-by-step guide and FAQ</u></a></p>' if i.get("guide") else ""}
</section>'''
    rows = "".join(block(i) for i in inv)
    gl = [g for g in GUIDES if g.get("lang", "en") == "en"]
    if gl:
        rows += '<section class="syn ab"><h2>Guides</h2><ul>' + "".join(
            f'<li><a href="{e(g["path"])}"><u>{e(g["h1"])}</u></a></li>' for g in gl) + "</ul></section>"
    return head("Invitation codes · Swoonflicks", "Invitation codes to join short drama affiliate programs like RS Boost.", "/invite/", "/img/og/home.jpg", extra=TURNSTILE_JS) + f'''
<body><main class="wrap"><div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="120" height="26"></a></div>
<div class="ttl"><h1>{metal("Invitation codes")}</h1></div>
<p class="tag" style="text-align:center">For creators who want to earn by sharing short dramas. These affiliate programs ask for an invitation code when you sign up. {"Request ours below and paste it in the sign-up form." if GATE.get("endpoint") else "Copy ours and paste it in the sign-up form."}</p>
<p class="note" style="text-align:center">This is a creator sign-up code, not a viewer code: it does not unlock episodes or give coins. Earnings depend on each program's own terms.</p>
{rows}{FOOT}</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-copy]');if(!b)return;
navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);b.textContent='Copied';
window.SFT&&SFT.track('CopyInvite',{{program:b.dataset.prog}})}})</script>{JS_GATE if GATE.get("endpoint") else ""}</body></html>'''


# ---------- trang guide (_src/guides/*.json): invite code RS Boost EN/ES/PT + bài hướng dẫn ----------
# Chữ thường, build tự escape. Khối "code" lấy code thật từ config.json "invite" theo tên program (không có code thì bỏ khối).
# Không số coin/hoa hồng nếu không có link nguồn trong "sources".
UI = {"en": dict(back="‹ All dramas", copy="Copy", copied="Copied", checked="Last checked", src="Sources", faq="Questions",
                 code="invitation code", signup="Open {p} sign-up", more="Dramas we share", rel="Related guides",
                 gate_h="Get the {p} invite code by email", badge="By request only",
                 gate_p="We send the code personally, to people who ask for it. Enter the email you will use for {p} and it arrives within a minute, with the sign-up link and a short checklist.",
                 email="Your email", send="Send my invite code", sending="Sending…", ok_h="Check your inbox",
                 ok_p="Your invite code is on its way to {e}. If it is not there in a few minutes, look in spam or promotions.",
                 err="Something went wrong. Try again in a minute, or write to partner@swoonflicks.com.",
                 limit="You already requested this code today. Check your inbox and spam folder.",
                 bad="Please enter a valid email address.", fine="One email with the code. No newsletter, no follow-ups."),
      "es": dict(back="‹ Todos los dramas", copy="Copiar", copied="Copiado", checked="Última revisión", src="Fuentes", faq="Preguntas",
                 code="código de invitación", signup="Abrir el registro de {p}", more="Dramas que compartimos", rel="Guías relacionadas",
                 gate_h="Recibe el código de invitación de {p} por correo", badge="Solo a quien lo pide",
                 gate_p="Enviamos el código personalmente, a quien lo pide. Escribe el correo que usarás en {p} y te llega en un minuto, con el enlace de registro y una lista breve de pasos.",
                 email="Tu correo", send="Enviar mi código", sending="Enviando…", ok_h="Revisa tu correo",
                 ok_p="Tu código va camino a {e}. Si no llega en unos minutos, mira en spam o promociones.",
                 err="Algo salió mal. Inténtalo de nuevo en un minuto o escribe a partner@swoonflicks.com.",
                 limit="Ya pediste este código hoy. Revisa tu bandeja de entrada y el spam.",
                 bad="Escribe un correo válido.", fine="Un solo correo con el código. Sin boletín ni seguimientos."),
      "pt": dict(back="‹ Todos os dramas", copy="Copiar", copied="Copiado", checked="Última revisão", src="Fontes", faq="Perguntas",
                 code="código de convite", signup="Abrir o cadastro do {p}", more="Dramas que compartilhamos", rel="Guias relacionados",
                 gate_h="Receba o código de convite do {p} por e-mail", badge="Só a pedido",
                 gate_p="Enviamos o código pessoalmente, a quem pede. Digite o e-mail que você vai usar no {p} e ele chega em um minuto, com o link de cadastro e um checklist curto.",
                 email="Seu e-mail", send="Enviar meu código", sending="Enviando…", ok_h="Confira sua caixa de entrada",
                 ok_p="Seu código está a caminho de {e}. Se não chegar em alguns minutos, veja o spam ou promoções.",
                 err="Algo deu errado. Tente de novo em um minuto ou escreva para partner@swoonflicks.com.",
                 limit="Você já pediu este código hoje. Confira a caixa de entrada e o spam.",
                 bad="Digite um e-mail válido.", fine="Um único e-mail com o código. Sem newsletter, sem cobranças.")}
# Cổng email (sếp 14/10 09:31: "điền mail vào và gửi qua mail... y chang drama partner"): config.json "gate" {endpoint, turnstile}.
# endpoint = URL Worker (worker/README.md); có endpoint thì khối code đổi thành form, mã KHÔNG in ra HTML. Trống = hiện code như cũ.
GATE = CFG.get("gate") or {}
TURNSTILE_JS = '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>' if GATE.get("endpoint") and GATE.get("turnstile") else ""


def gate_box(inv, lang, disclosure=""):
    """Form xin mã qua email thay khối code. Chữ theo UI[lang]; Worker trả 200 ok / 429 limit / 4xx-5xx lỗi."""
    u = UI[lang]; p = inv["program"]
    ts = f'<div class="cf-turnstile" data-sitekey="{e(GATE["turnstile"])}" data-theme="dark" data-size="flexible" data-action="invite" data-callback="sfTsOk" data-expired-callback="sfTsNo" data-error-callback="sfTsNo"></div>' if GATE.get("turnstile") else ""
    # Nút gửi khoá tới khi Turnstile trả token (test live 15/10: bấm nhanh trước khi Turnstile xong thì lỗi). Callback khai trước div để api.js async luôn thấy.
    tsjs = "<script>function sfTsB(){return document.querySelector('form.gf button')}function sfTsOk(){var b=sfTsB();if(b)b.disabled=false}function sfTsNo(){var b=sfTsB();if(b)b.disabled=true}</script>" if ts else ""
    return f'''<section class="syn inv gate" id="invite"><span class="bd">{e(u["badge"])}</span><h2>{e(u["gate_h"].format(p=p))}</h2>
<p class="gp">{e(u["gate_p"].format(p=p))}</p>
<form class="gf" method="post" action="{e(GATE["endpoint"])}" novalidate data-program="{e(p)}" data-lang="{lang}" data-ok-h="{e(u["ok_h"])}" data-ok-p="{e(u["ok_p"])}"
 data-err="{e(u["err"])}" data-limit="{e(u["limit"])}" data-bad="{e(u["bad"])}" data-sending="{e(u["sending"])}">
<label for="ge">{e(u["email"])}</label>
<div class="row"><input id="ge" type="email" name="email" required autocomplete="email" inputmode="email" spellcheck="false" placeholder="you@mail.com" maxlength="254"><button type="submit"{" disabled" if ts else ""}>{e(u["send"])}</button></div>
{tsjs}{ts}<p class="fine">{e(u["fine"])}</p><p class="msg" role="status" aria-live="polite" hidden></p></form>
{f'<p class="note">{e(disclosure)}</p>' if disclosure else ""}</section>'''


# JS form: gửi JSON {email, lang, program, page, token} tới Worker; thành công thì thay form bằng lời cảm ơn; bắn event RequestInvite.
JS_GATE = '''<script>(function(){var f=document.querySelector('form.gf');if(!f)return;var m=f.querySelector('.msg'),b=f.querySelector('button'),i=f.querySelector('input[type=email]');
function say(t,ok){m.textContent=t;m.hidden=!t;m.className='msg'+(ok?' ok':'')}
f.addEventListener('submit',function(ev){ev.preventDefault();var em=(i.value||'').trim();
if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(em)){say(f.dataset.bad);i.focus();return}
var tk=f.querySelector('[name=cf-turnstile-response]');var body={email:em,lang:f.dataset.lang,program:f.dataset.program,page:location.pathname,token:tk?tk.value:''};
b.disabled=true;var t0=b.textContent;b.textContent=f.dataset.sending;say('');
fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{s:r.status,j:j}})})
.then(function(r){if(r.s===200&&r.j.ok){f.innerHTML='<p class="okh">'+f.dataset.okH+'</p><p class="okp">'+f.dataset.okP.replace('{e}','<b></b>')+'</p>';f.querySelector('.okp b').textContent=em;
window.SFT&&SFT.track('RequestInvite',{program:f.dataset.program,page:location.pathname,lang:f.dataset.lang});return}
say(r.s===429?f.dataset.limit:(r.j&&r.j.error==='bad_email'?f.dataset.bad:f.dataset.err));b.disabled=!!tk;b.textContent=t0;if(window.turnstile)try{turnstile.reset()}catch(e){}})
.catch(function(){say(f.dataset.err);b.disabled=false;b.textContent=t0})})})()</script>'''



def load_guides():
    d = OUT / "_src" / "guides"
    gs = [json.loads(x.read_text(encoding="utf-8")) for x in sorted(d.glob("*.json"))] if d.exists() else []
    paths = [g["path"] for g in gs]
    assert len(paths) == len(set(paths)), "guide path trùng"
    return gs


def guide_page(g, films):
    lang = g.get("lang", "en")
    u = UI[lang]
    inv = next((i for i in CFG.get("invite", []) if i.get("code") and i["program"] == g.get("code")), None)
    codebox = ""
    if inv and GATE.get("endpoint"):
        codebox = gate_box(inv, lang, g.get("disclosure", ""))
    elif inv:
        codebox = f'''<section class="syn inv"><h2>{e(inv["program"])} {e(u["code"])}</h2>
<div class="code"><b>{e(inv["code"])}</b><button type="button" data-copy="{e(inv["code"])}" data-prog="{e(inv["program"])}" data-done="{e(u["copied"])}">{e(u["copy"])}</button></div>
{f'<a class="cta" href="{e(inv["signup"])}" rel="noopener" target="_blank" data-signup="{e(inv["program"])}">{e(u["signup"].format(p=inv["program"]))} {ARROW}</a>' if inv.get("signup") else ""}
{f'<p class="note">{e(g["disclosure"])}</p>' if g.get("disclosure") else ""}</section>'''
    body = ""
    for s in g.get("sections", []):
        body += f'<h2>{e(s["h2"])}</h2>' + "".join(f"<p>{e(x)}</p>" for x in s.get("p", []))
        if s.get("steps"):
            body += "<ol>" + "".join(f"<li>{e(x)}</li>" for x in s["steps"]) + "</ol>"
        if s.get("ul"):
            body += "<ul>" + "".join(f"<li>{e(x)}</li>" for x in s["ul"]) + "</ul>"
        if s.get("links"):
            body += "<ul>" + "".join(f'<li><a href="{e(l["href"])}"{" rel=\"noopener\" target=\"_blank\"" if l["href"].startswith("http") else ""}><u>{e(l["text"])}</u></a></li>'
                                     for l in s["links"]) + "</ul>"
        body += "".join(f"<p>{e(x)}</p>" for x in s.get("after", []))
    faq = g.get("faq", [])
    faqh = (f'<section class="syn faq"><h2>{e(u["faq"])}</h2>' + "".join(
        f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in faq) + "</section>") if faq else ""
    rel = [x for x in GUIDES if x["path"] in g.get("related", [])]
    relh = (f'<h2>{e(u["rel"])}</h2><ul>' + "".join(f'<li><a href="{e(x["path"])}"><u>{e(x["h1"])}</u></a></li>' for x in rel) + "</ul>") if rel else ""
    srcs = g.get("sources", [])
    srch = (f'<h2>{e(u["src"])}</h2><ul style="overflow-wrap:anywhere">' + "".join(f'<li><a href="{e(x)}" rel="noopener" target="_blank"><u>{e(x)}</u></a></li>' for x in srcs) + "</ul>") if srcs else ""
    # "watch": [slug...] = lưới poster ra thẳng link CPS gốc, cùng tab, giống trang bio (bắn ClickAffiliate placement=guide)
    wl = [f for s in g.get("watch", []) for f in films if f["slug"] == s]
    watchh = (f'<h2>{e(g.get("watch_h2", "Start watching"))}</h2><div class="more">' + "".join(
        f'''<a class="cd" href="{e(f["link"])}"{ads_href(f)} rel="nofollow sponsored noopener" data-aff="guide" data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}">
<img src="/img/{f['slug']}.webp" alt="{e(f['title'])} poster" width="360" height="480" loading="lazy" decoding="async">
<div class="in"><h2>{e(f['title'])}</h2><span class="go">Watch now {ARROW}</span></div></a>''' for f in wl) +
              '</div><p class="note">Each poster opens the official app · affiliate link</p>') if wl else ""
    fl = [f for f in films if f["app"] == g.get("films_app")] if g.get("films_app") else []
    # "films": [slug...] = thẻ phim link NỘI BỘ sang trang /<slug>/ (khác "watch" ra thẳng link CPS); ghép sau films_app, không trùng
    fl += [f for s in g.get("films", []) for f in films if f["slug"] == s and f not in fl]
    moreh = (f'<p class="h3">{e(u["more"])}</p><div class="more">' + "".join(card(f) for f in fl) + "</div>") if fl else ""
    alt = g.get("alternates", {})
    altl = "".join(f'<link rel="alternate" hreflang="{k}" href="{BASE}{v}">' for k, v in alt.items())
    if "en" in alt:
        altl += f'<link rel="alternate" hreflang="x-default" href="{BASE}{alt["en"]}">'
    crumbs = [("Swoonflicks", "/")] + [(c["name"], c["path"]) for c in g.get("crumbs", [])] + [(g["h1"], g["path"])]
    lds = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{BASE}{p}"} for i, (n, p) in enumerate(crumbs)]},
           {"@context": "https://schema.org", "@type": "WebPage", "name": g["title"], "url": f"{BASE}{g['path']}", "inLanguage": lang,
            "description": g["description"], "dateModified": g.get("checked", date.today().isoformat()),
            "publisher": {"@type": "Organization", "name": "Swoonflicks", "url": f"{BASE}/"}}]
    if faq:
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in faq]})
    extra = altl + f'<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>' + (TURNSTILE_JS if inv else "")
    return head(g["title"], g["description"], g["path"], "/img/og/home.jpg", extra, lang=lang) + f'''
<body><main class="wrap doc"><div class="top"><a class="back" href="/">{e(u["back"])}</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="120" height="26"></a></div>
<h1>{e(g["h1"])}</h1>{f'<p>{e(g["lead"])}</p>' if g.get("lead") else ""}
{codebox}{body}{watchh}{faqh}{relh}{srch}
{f'<p class="note">{e(u["checked"])}: {e(g["checked"])}</p>' if g.get("checked") else ""}
{moreh}{FOOT}</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-copy]');if(b){{
navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);b.textContent=b.dataset.done||'Copied';
window.SFT&&SFT.track('CopyInvite',{{program:b.dataset.prog,page:location.pathname}});return}}
var s=e.target.closest('[data-signup]');if(s&&window.SFT)SFT.track('ClickSignup',{{program:s.dataset.signup,page:location.pathname}})}})</script>{JS_GATE if inv and GATE.get("endpoint") else ""}</body></html>'''


def nf_page():
    return head("Not found · Swoonflicks", "This page does not exist.", None, noindex=True) + f'''
<body><main class="wrap"><header class="hd"><img class="lk" src="/img/lockup.png" alt="Swoonflicks" width="681" height="150"><h1 style="margin-top:18px">{metal("Lost the plot?")}</h1>
<p class="tag">This page does not exist. The dramas are all on the shelf.</p>
<a class="cta" href="/" style="max-width:320px;margin:20px auto">Back to all dramas {ARROW}</a></header>{FOOT}</main></body></html>'''


# ---------- dữ liệu ----------
films = []
for r in csv.DictReader(open(SD / "ke" / "shelf.csv", encoding="utf-8")):
    link = r["link"] or RS_LINK.get(r["film"])
    d = film_dir(r["film"])
    # Web lên mọi phim đã qua lọc (sếp 15/10: "đưa lên website hết toàn bộ phim trên kệ"), chỉ loại GIU (trượt gate / 18+).
    # Cột ready vẫn là cổng của social; web không đợi lịch đăng giãn cách. Thiếu poster banner.jpg thì chưa lên.
    # config.json "web_only": phim GIU cho social nhưng vẫn lên web (sếp 17/10: Mommy chỉ để website)
    if (r["ready"] == "GIU" and r["film"] not in CFG.get("web_only", [])) or not link or not d or not (d / "banner.jpg").exists():
        continue
    slug = re.sub(r"-[0-9a-f]{6,8}$", "", r["film"])
    films.append(dict(id=r["film"], slug=slug, title=r["title"], app=r["app"] or "ReelShort", link=link, d=d,
                      genre=GENRE.get(r["film"], []), syn=synopsis(d)))
slugs = [f["slug"] for f in films]
assert len(slugs) == len(set(slugs)), f"slug trùng: {sorted({x for x in slugs if slugs.count(x) > 1})}"
for f in films:
    if not f["genre"]:
        print(f"CẢNH BÁO: {f['id']} chưa có genre trong GENRE, sẽ biến mất khi lọc Thể loại")
films.sort(key=lambda f: ORDER.index(f["id"]) if f["id"] in ORDER else len(ORDER))
# tập free + nguồn nhúng từng phim, sinh bằng make_episodes.py (chạy trước build)
EPS = json.loads((HUB / "episodes.json").read_text(encoding="utf-8"))

# ---------- dọn bản cũ (giữ .git, CNAME) ----------
for p in OUT.iterdir():
    if p.is_dir() and ((p / ".gen").exists() or p.name in ("img", "assets")):
        shutil.rmtree(p, ignore_errors=True)  # OneDrive hay khoá thư mục rỗng: xoá được file là đủ
for p in ("index.html", "404.html", "sitemap.xml", "robots.txt", "llms.txt"):
    (OUT / p).unlink(missing_ok=True)
(OUT / "img" / "og").mkdir(parents=True, exist_ok=True)
(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(HUB / "t.js", OUT / "assets" / "t.js")
for x in ("reel.js", "reel.css"):  # player lướt dọc trang phim
    shutil.copy(HUB / x, OUT / "assets" / x)

# ---------- ảnh ----------
logo = Image.open(SD / "brand" / "logo-mark-1024-transparent.png")
for s in (64, 128):
    im = logo.copy(); im.thumbnail((s, s)); im.save(OUT / "img" / f"logo-{s}.png", optimize=True)
lk = Image.open(SD / "brand" / "logo-lockup-transparent.png")  # 1362x300, gồm tagline
lk.resize((681, 150), Image.LANCZOS).save(OUT / "img" / "lockup.png", optimize=True)
sm = lk.copy(); ImageDraw.Draw(sm).rectangle((360, 200, 1361, 299), fill=(0, 0, 0, 0))  # xoá tagline nhưng giữ trọn tim (crop cao 200 từng cắt cụt đáy tim)
sm.crop(sm.getbbox()).resize((240, 52), Image.LANCZOS).save(OUT / "img" / "lockup-sm.png", optimize=True)  # nét 2x cho cao 26px


def fit(im, w, h):
    sw, sh = im.size; r = max(w / sw, h / sh)
    im = im.resize((round(sw * r), round(sh * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


for f in films:
    im = Image.open(f["d"] / "banner.jpg").convert("RGB")
    fit(im, 360, 480).save(OUT / "img" / f"{f['slug']}.webp", quality=78, method=6)
    fit(im, 720, 960).save(OUT / "img" / f"{f['slug']}-h.webp", quality=80, method=6)
    fit(im, 720, 540).save(OUT / "img" / f"{f['slug']}-w.webp", quality=74, method=6)  # thẻ to trang chủ khung 4:3
    fit(im, 600, 800).save(OUT / "img" / "og" / f"{f['slug']}.jpg", quality=82, optimize=True)
# OG trang chủ 1200x630: chụp 1 lần từ HTML đúng concept (chữ kim loại + poster), lưu ở hub/og-home.jpg
shutil.copy(HUB / "og-home.jpg", OUT / "img" / "og" / "home.jpg")


# ---------- trang ----------
GUIDES = load_guides()
def write(rel, text, gen=False):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if gen:
        (p.parent / ".gen").write_text("")


write("index.html", hub_page(films))
bio = sorted(films, key=lambda f: f["slug"] != CFG.get("bio_first"))
for k, src in BIO.items():
    write(f"{k}/index.html", bio_page(bio, f"/{k}/", src), gen=True)
for f in films:
    write(f"go/{f['slug']}/index.html", one_page(f, f"/go/{f['slug']}/"), gen=True)
(OUT / "go" / ".gen").write_text("")
for f in films:
    write(f"{f['slug']}/index.html", film_page(f, films), gen=True)
write("privacy/index.html", privacy_page(), gen=True)
INV = [i for i in CFG.get("invite", []) if i.get("code")]
if INV:
    write("invite/index.html", invite_page(INV), gen=True)
for g in GUIDES:
    rel = g["path"].strip("/") + "/index.html"
    write(rel, guide_page(g, films), gen=True)
    (OUT / rel.split("/")[0] / ".gen").write_text("")  # thư mục gốc (es/, pt/, guides/) cũng là thư mục sinh
# IndexNow: file key ở gốc; ping sau deploy bằng _src/indexnow.py
if CFG.get("indexnow"):
    write(f'{CFG["indexnow"]}.txt', CFG["indexnow"])
write("404.html", nf_page())
urls = ["/", "/privacy/"] + (["/invite/"] if INV else []) + [g["path"] for g in GUIDES] + [f"/{f['slug']}/" for f in films]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
      "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
# llms.txt: bản đồ markdown cho bot AI (rẻ, không kỳ vọng thứ hạng)
write("llms.txt", "# Swoonflicks\n\n> Romance novels, now on screen: English short dramas to binge.\n\n## Dramas\n" +
      "".join(f"- [{f['title']}]({BASE}/{f['slug']}/): {', '.join(f['genre'])} drama\n" for f in films) +
      f"\n## Creators\n- [Invitation codes]({BASE}/invite/): creator sign-up code for short drama affiliate programs\n" +
      ("\n## Guides\n" + "".join(f"- [{g['h1']}]({BASE}{g['path']}) ({g.get('lang', 'en')}): {g['description']}\n" for g in GUIDES) if GUIDES else ""))
(OUT / ".nojekyll").write_text("")
print("ok", len(films), "phim:", ", ".join(f["slug"] for f in films))
