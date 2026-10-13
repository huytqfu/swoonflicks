"""Website swoonflicks.com: hub (kệ phim) + handcliff (1 trang / phim) + bản bio theo nguồn. Sếp giao 13/10 16:23.
Đọc ke/shelf.csv (ready=CO + link, phim RS lấy RS_LINK) → hub/site/ (repo huytqfu/swoonflicks, GitHub Pages).
Chạy: py -3.14 hub/build.py
- Concept: Playfair Display 900 ánh kim viền nâu đen, "FREE EPISODES" Cinzel kẹp 2 lằn (cover kênh). CSS: hub/site.css (nhúng inline).
- Tracking: hub/t.js (GA4 + Meta + TikTok, ID ở hub/config.json, trống = không tải). Nút ra app = link CPS gốc, không cloak.
- Video: chỉ nhúng Shorts trên YouTube @swoonflicks của mình (map YT). Phim chưa có video thì hiện poster, không giả nút play.
- Build xoá thư mục sinh (có file .gen), img/, assets/; giữ .git + CNAME.
"""
import csv, html, json, re, shutil
from pathlib import Path
from PIL import Image

SD = Path(__file__).resolve().parent.parent
HUB = SD / "hub"
OUT = HUB / "site"
BASE = "https://swoonflicks.com"
FONTS = "https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Playfair+Display:wght@900&display=swap"

# Link CPS RS Boost (reelslink) lấy từ caption X/YT đã đăng
RS_LINK = {
    "rejected-luna-is-the-alpha-queen-69fa0a97": "https://reelslink.com/cps/xwAWVb",
    "the-empresss-final-wish-6a06bb65": "https://reelslink.com/cps/uGhlNR",
}
# Thứ tự: phim đang đăng gần nhất lên đầu
ORDER = ["dragons-bow-to-the-trash-638707", "mommy-i-m-not-lying-646011", "mech-god-from-the-dark-side-of-the-moon-635894",
         "the-unbound-rise-of-the-godslayer-647593", "i-spoke-baby-dragon-and-won-everyone-over-628653"]
# Shorts đã đăng trên YouTube @swoonflicks (yt-dlp /shorts 13/10). TikTok tắt nhúng nên không dùng.
YT = {
    "the-unbound-rise-of-the-godslayer-647593": [("Part 1", "VOS5UiGpIV8"), ("Part 2", "ylUIh9I908I"), ("Part 3", "ZkCDRpUW8w8"),
                                                 ("Part 4", "FQGrMJvSNhA"), ("Part 5", "TH9eRUwcubs")],
    "rejected-luna-is-the-alpha-queen-69fa0a97": [("Part 10", "cx-rFqh4x4w")],
}
GENRE = {
    "dragons-bow-to-the-trash-638707": ["Fantasy"],
    "mommy-i-m-not-lying-646011": ["Family"],
    "mech-god-from-the-dark-side-of-the-moon-635894": ["Sci-Fi", "Revenge"],
    "the-unbound-rise-of-the-godslayer-647593": ["Fantasy"],
    "i-spoke-baby-dragon-and-won-everyone-over-628653": ["Fantasy"],
    "rejected-luna-is-the-alpha-queen-69fa0a97": ["Fantasy", "Romance", "Revenge"],
    "the-empresss-final-wish-6a06bb65": ["Royal", "Family"],
}
SOCIAL = [("TikTok", "https://www.tiktok.com/@swoonflicks"), ("Instagram", "https://www.instagram.com/swoonflicks"),
          ("YouTube", "https://www.youtube.com/@swoonflicks"), ("Facebook", "https://www.facebook.com/swoonflicks")]
# Bản hub cho link bio từng nền: cùng nội dung, gắn nguồn khi URL không mang utm (ig.swoonflicks.com redirect có utm_source=instagram)
BIO = {"ig": "instagram", "tt": "tiktok", "yt": "youtube", "fb": "facebook"}

e = html.escape
CFG_F = HUB / "config.json"
if not CFG_F.exists():
    CFG_F.write_text(json.dumps({"ga4": "", "meta": "", "tiktok": ""}, indent=1), encoding="utf-8")
CFG = json.loads(CFG_F.read_text(encoding="utf-8"))
CSS = (HUB / "site.css").read_text(encoding="utf-8")
ARROW = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M2 0l6 5-6 5z"/></svg>'


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
    t = e(t)
    return f'<span class="m"><span class="l0">{t}</span><span class="l1" aria-hidden="true">{t}</span><span class="l2" aria-hidden="true">{t}</span></span>'


def head(title, desc, path, img=None, extra="", noindex=False, src=""):
    cfg = dict(CFG, src=src)
    og = f'<meta property="og:image" content="{BASE}{img}"><meta name="twitter:card" content="summary_large_image">' if img else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{path}">{'<meta name="robots" content="noindex,follow">' if noindex else ''}
<meta name="theme-color" content="#0b0806"><link rel="icon" href="/img/logo-64.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Swoonflicks">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}">{og}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<style>{CSS}</style>
<script>window.SF={json.dumps(cfg)}</script><script src="/assets/t.js" defer></script>{extra}
</head>'''


FOOT = '''<p class="ft">Swoonflicks shares free episodes of short dramas we love.<br>
Links to the apps are affiliate links: we may earn a commission when you watch there, at no extra cost to you.<br>
<a href="/privacy/">Privacy</a> · <a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>'''


def social():
    return '<p class="h3">Follow for new parts</p><nav class="soc">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in SOCIAL) + "</nav>"


def card(f, big=False, lazy=True):
    img = f"/img/{f['slug']}-h.webp" if big else f"/img/{f['slug']}.webp"
    w, h = (720, 960) if big else (360, 480)
    return f'''<a class="cd{' big' if big else ''}" href="/{f['slug']}/" data-app="{e(f['app'])}" data-genre="{e('|'.join(f['genre']))}">
<img src="{img}" alt="{e(f['title'])} poster" width="{w}" height="{h}"{' loading="lazy"' if lazy else ' fetchpriority="high"'} decoding="async">
<span class="badge">{e(f['app'])}</span><div class="in"><h2>{e(f['title'])}</h2><span class="go">Watch free {ARROW}</span></div></a>'''


JS_HUB = '''<script>(function(){var sel={app:'',genre:''},cards=[].slice.call(document.querySelectorAll('.grid .cd')),em=document.querySelector('.empty');
document.querySelectorAll('.chip').forEach(function(c){c.onclick=function(){var k=c.dataset.k;sel[k]=c.dataset.v;
document.querySelectorAll('.chip[data-k='+k+']').forEach(function(x){x.setAttribute('aria-pressed',x===c)});var n=0;
cards.forEach(function(d){var ok=(!sel.app||d.dataset.app===sel.app)&&(!sel.genre||d.dataset.genre.split('|').indexOf(sel.genre)>=0);d.hidden=!ok;if(ok)n++});
em.hidden=n>0;if(window.SFT)SFT.track('Filter',{key:k,value:c.dataset.v||'all'})}})})()</script>'''


def hub_page(films, path="/", src=""):
    apps = sorted({f["app"] for f in films})
    genres = sorted({g for f in films for g in f["genre"]})
    chip = lambda k, v, lbl, on=False: f'<button type="button" class="chip" data-k="{k}" data-v="{e(v)}" aria-pressed="{str(on).lower()}">{e(lbl)}</button>'
    flt = ('<div class="flt"><div class="chips"><b>App</b>' + chip("app", "", "All", True) + "".join(chip("app", a, a) for a in apps) +
           '</div><div class="chips"><b>Genre</b>' + chip("genre", "", "All", True) + "".join(chip("genre", g, g) for g in genres) + "</div></div>")
    grid = "\n".join(card(f, big=(i == 0), lazy=(i > 2)) for i, f in enumerate(films))
    desc = "Free episodes of the short dramas everyone is binging. Pick a drama, watch the free part, then finish it on the app."
    return head("Swoonflicks · Free short drama episodes", desc, "/", "/img/og/home.jpg", noindex=(path != "/"), src=src) + f'''
<body><main class="wrap">
<header class="hd"><img class="logo" src="/img/logo-128.png" alt="" width="60" height="60"><h1>{metal("Swoonflicks")}</h1>
<div class="plq"><i></i>{metal("FREE EPISODES")}<i></i></div>
<p class="tag">Pick a drama, watch the free part here, then finish the story on the app.</p></header>
{flt}<div class="grid">{grid}</div><p class="empty" hidden>No drama matches both filters yet.</p>
{social()}{FOOT}</main>{JS_HUB}</body></html>'''


JS_FILM = '''<script>(function(){var b=document.body.dataset,pl=document.querySelector('.pl'),P=null,cur='',marks={},tick;
function T(n,p){if(window.SFT)SFT.track(n,Object.assign({film:b.film,title:b.title,app:b.app,video_id:cur},p||{}))}
function poll(){clearInterval(tick);tick=setInterval(function(){if(!P||!P.getDuration)return;var d=P.getDuration(),t=P.getCurrentTime();if(!d)return;
[25,50,75,95].forEach(function(m){var k=cur+m;if(!marks[k]&&t/d*100>=m){marks[k]=1;T('VideoProgress',{percent:m})}})},1000)}
function start(v){cur=v;if(P){P.loadVideoById(v);return}var host=document.createElement('div');host.className='vid';pl.innerHTML='';pl.appendChild(host);
var go=function(){P=new YT.Player(host,{host:'https://www.youtube-nocookie.com',videoId:v,playerVars:{autoplay:1,playsinline:1,rel:0,modestbranding:1},
events:{onStateChange:function(s){if(s.data===1){if(!marks[cur+'p']){marks[cur+'p']=1;T('VideoPlay')}poll()}else clearInterval(tick)}}})};
if(window.YT&&YT.Player)go();else{window.onYouTubeIframeAPIReady=go;var s=document.createElement('script');s.src='https://www.youtube.com/iframe_api';document.head.appendChild(s)}}
var btn=pl&&pl.querySelector('.play');if(btn)btn.onclick=function(){start(btn.dataset.v)};
document.querySelectorAll('.parts .chip').forEach(function(c){c.onclick=function(){document.querySelectorAll('.parts .chip').forEach(function(x){x.setAttribute('aria-pressed',x===c)});
start(c.dataset.v);pl.scrollIntoView({behavior:'smooth',block:'center'})}});
var bar=document.querySelector('.bar'),cta=document.querySelector('.cta');if(bar&&cta&&'IntersectionObserver'in window)
new IntersectionObserver(function(es){bar.classList.toggle('on',es[0].intersectionRatio<.9)},{threshold:[0,.9,1]}).observe(cta)})()</script>'''


def film_page(f, films):
    syn = f["syn"]
    yt = YT.get(f["id"], [])
    if yt:
        player = f'''<div class="pl"><img src="/img/{f['slug']}-h.webp" alt="" width="720" height="960" fetchpriority="high">
<button type="button" class="play" data-v="{yt[0][1]}" aria-label="Play free {e(yt[0][0])}"><span class="btnp"><svg viewBox="0 0 10 10"><path d="M1 0l9 5-9 5z"/></svg></span></button>
<span class="lbl">Free · {e(yt[0][0])}</span></div>'''
        if len(yt) > 1:
            player += '<div class="parts">' + "".join(
                f'<button type="button" class="chip" data-v="{v}" aria-pressed="{str(i == 0).lower()}">{e(n)}</button>' for i, (n, v) in enumerate(yt)) + "</div>"
    else:
        player = f'''<div class="pl ps"><img src="/img/{f['slug']}-h.webp" alt="{e(f['title'])} poster" width="720" height="960" fetchpriority="high"></div>
<p class="note" style="margin-top:10px">Free parts are on our <a href="https://www.tiktok.com/@swoonflicks" rel="noopener" target="_blank"><u>TikTok</u></a>
and <a href="https://www.instagram.com/swoonflicks" rel="noopener" target="_blank"><u>Instagram</u></a>.</p>'''
    aff = lambda place: (f'href="{e(f["link"])}" target="_blank" rel="nofollow sponsored noopener" data-aff="{place}" '
                         f'data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}"')
    more = "".join(card(o) for o in films if o is not f)
    ld = {"@context": "https://schema.org", "@type": "TVSeries", "name": f["title"], "description": cut(syn, 300),
          "image": f"{BASE}/img/og/{f['slug']}.jpg", "url": f"{BASE}/{f['slug']}/", "genre": f["genre"]}
    if yt:
        ld["trailer"] = {"@type": "VideoObject", "name": f"{f['title']} {yt[0][0]}", "embedUrl": f"https://www.youtube.com/embed/{yt[0][1]}",
                         "thumbnailUrl": f"https://i.ytimg.com/vi/{yt[0][1]}/hqdefault.jpg", "description": cut(syn, 200)}
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    title = f"{f['title']} · Watch free | Swoonflicks"
    return head(title, cut(syn, 155), f"/{f['slug']}/", f"/img/og/{f['slug']}.jpg", extra) + f'''
<body data-film="{e(f['slug'])}" data-title="{e(f['title'])}" data-app="{e(f['app'])}"><main class="wrap">
<div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/">SWOONFLICKS</a></div>
{player}
<div class="ttl"><h1>{metal(f['title'])}</h1><div class="meta"><span>{e(f['app'])}</span>{''.join(f'<span>{e(g)}</span>' for g in f['genre'])}</div></div>
<a class="cta" {aff("main")}><span>Watch the full drama on {e(f['app'])}<small>Continue the story in the app</small></span>{ARROW}</a>
<p class="note">Opens {e(f['app'])}. Affiliate link: we may earn a commission.</p>
<section class="syn"><h2>The story</h2><p>{e(syn)}</p></section>
<p class="h3">More dramas</p><div class="more">{more}</div>
{social()}{FOOT}<div class="pad"></div></main>
<div class="bar"><a class="cta" {aff("sticky")}><span>Watch full on {e(f['app'])}</span>{ARROW}</a></div>{JS_FILM}</body></html>'''


def privacy_page():
    return head("Privacy · Swoonflicks", "How Swoonflicks uses cookies and measurement.", "/privacy/") + '''
<body><main class="wrap doc"><div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/">SWOONFLICKS</a></div>
<h1>Privacy</h1>
<p>Swoonflicks is a fan site that shares free episodes of short dramas and links to the apps where you can watch the rest.</p>
<h2>What we measure</h2>
<ul><li>Which drama pages you open, whether you play the free episode and how far you watch.</li>
<li>Whether you tap a link to a drama app, and which page or social profile brought you here (from the link's utm or click id).</li></ul>
<h2>Tools we use</h2>
<p>When enabled, Google Analytics, the Meta Pixel and the TikTok Pixel receive these events so we can count visits and show
our videos to people who are likely to enjoy them. Free episodes play through YouTube's privacy-enhanced mode (youtube-nocookie.com)
and only load when you press play.</p>
<h2>Your choice</h2>
<p>Visitors in the EU and UK are asked before any of these tools load. You can change your answer by clearing this site's data in your browser.</p>
<h2>Affiliate links</h2>
<p>Links to drama apps are affiliate links. If you watch or subscribe there, we may earn a commission at no extra cost to you.
What you do inside those apps is covered by their own privacy policies.</p>
<h2>Contact</h2><p><a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>
''' + FOOT + "</main></body></html>"


def nf_page():
    return head("Not found · Swoonflicks", "This page does not exist.", "/404.html", noindex=True) + f'''
<body><main class="wrap"><header class="hd"><h1>{metal("Lost the plot?")}</h1>
<p class="tag">This page does not exist. The dramas are all on the shelf.</p>
<a class="cta" href="/" style="max-width:320px;margin:20px auto">Back to all dramas {ARROW}</a></header>{FOOT}</main></body></html>'''


# ---------- dữ liệu ----------
films = []
for r in csv.DictReader(open(SD / "ke" / "shelf.csv", encoding="utf-8")):
    link = r["link"] or RS_LINK.get(r["film"])
    d = film_dir(r["film"])
    if r["ready"] != "CO" or not link or not d:
        continue
    slug = re.sub(r"-[0-9a-f]{6,8}$", "", r["film"])
    films.append(dict(id=r["film"], slug=slug, title=r["title"], app=r["app"] or "ReelShort", link=link, d=d,
                      genre=GENRE.get(r["film"], []), syn=synopsis(d)))
films.sort(key=lambda f: ORDER.index(f["id"]) if f["id"] in ORDER else len(ORDER))

# ---------- dọn bản cũ (giữ .git, CNAME) ----------
for p in OUT.iterdir():
    if p.is_dir() and ((p / ".gen").exists() or p.name in ("img", "assets")):
        shutil.rmtree(p, ignore_errors=True)  # OneDrive hay khoá thư mục rỗng: xoá được file là đủ
for p in ("index.html", "404.html", "sitemap.xml", "robots.txt"):
    (OUT / p).unlink(missing_ok=True)
(OUT / "img" / "og").mkdir(parents=True, exist_ok=True)
(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(HUB / "t.js", OUT / "assets" / "t.js")

# ---------- ảnh ----------
logo = Image.open(SD / "brand" / "logo-mark-1024-transparent.png")
for s in (64, 128):
    im = logo.copy(); im.thumbnail((s, s)); im.save(OUT / "img" / f"logo-{s}.png", optimize=True)


def fit(im, w, h):
    sw, sh = im.size; r = max(w / sw, h / sh)
    im = im.resize((round(sw * r), round(sh * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


for f in films:
    im = Image.open(f["d"] / "banner.jpg").convert("RGB")
    fit(im, 360, 480).save(OUT / "img" / f"{f['slug']}.webp", quality=78, method=6)
    fit(im, 720, 960).save(OUT / "img" / f"{f['slug']}-h.webp", quality=80, method=6)
    fit(im, 600, 800).save(OUT / "img" / "og" / f"{f['slug']}.jpg", quality=82, optimize=True)
og = Image.new("RGB", (1200, 800), (11, 8, 6))
for i, f in enumerate(films[:4]):
    og.paste(fit(Image.open(f["d"] / "banner.jpg").convert("RGB"), 300, 400), (i * 300, 200))
lg = logo.copy(); lg.thumbnail((180, 180)); og.paste(lg, (510, 10), lg)
og.save(OUT / "img" / "og" / "home.jpg", quality=82, optimize=True)


# ---------- trang ----------
def write(rel, text, gen=False):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if gen:
        (p.parent / ".gen").write_text("")


write("index.html", hub_page(films))
for k, src in BIO.items():
    write(f"{k}/index.html", hub_page(films, f"/{k}/", src), gen=True)
for f in films:
    write(f"{f['slug']}/index.html", film_page(f, films), gen=True)
write("privacy/index.html", privacy_page(), gen=True)
write("404.html", nf_page())
urls = ["/", "/privacy/"] + [f"/{f['slug']}/" for f in films]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
      "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
(OUT / ".nojekyll").write_text("")
print("ok", len(films), "phim:", ", ".join(f["slug"] for f in films))
