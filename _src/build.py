"""Website swoonflicks.com: hub (kệ phim) + handcliff (1 trang / phim) + bản bio theo nguồn. Sếp giao 13/10 16:23.
Đọc ke/shelf.csv (ready=CO + link, phim RS lấy RS_LINK) → hub/site/ (repo huytqfu/swoonflicks, GitHub Pages).
Chạy: py -3.14 hub/build.py
- Concept brand v3c: đen hồng, Poppins, logo lockup "oo" móc xích + "Romance novels, now on screen" (sếp 14/10: bỏ vàng royal). CSS: hub/site.css.
- Không hiện tên network (ReelShort/DramaCPS) cho người xem; f["app"] chỉ còn trong tracking nội bộ (sếp 14/10).
- Tracking: hub/t.js (GA4 + Meta + TikTok, ID ở hub/config.json, trống = không tải). Nút ra app = link CPS gốc, không cloak.
- Video: chỉ nhúng Shorts trên YouTube @swoonflicks của mình (map YT). Phim chưa có video thì hiện poster, không giả nút play.
- Build xoá thư mục sinh (có file .gen), img/, assets/; giữ .git + CNAME.
"""
import csv, html, json, re, shutil
from datetime import date
from pathlib import Path
from PIL import Image

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
# Shorts đã đăng trên YouTube @swoonflicks (yt-dlp /shorts 13/10). TikTok tắt nhúng nên không dùng.
YT = {
    "the-unbound-rise-of-the-godslayer-647593": [("Part 1", "VOS5UiGpIV8"), ("Part 2", "ylUIh9I908I"), ("Part 3", "ZkCDRpUW8w8"),
                                                 ("Part 4", "FQGrMJvSNhA"), ("Part 5", "TH9eRUwcubs")],
    "rejected-luna-is-the-alpha-queen-69fa0a97": [("Part 10", "cx-rFqh4x4w")],
}
# ngày đăng YT (lấy từ itemprop uploadDate trang video) cho VideoObject.uploadDate
YT_DATE = {"VOS5UiGpIV8": "2026-10-07T10:38:03-07:00", "cx-rFqh4x4w": "2026-10-02T12:17:04-07:00"}
GENRE = {
    "dragons-bow-to-the-trash-638707": ["Fantasy"],
    "mommy-i-m-not-lying-646011": ["Family"],
    "mech-god-from-the-dark-side-of-the-moon-635894": ["Sci-Fi", "Revenge"],
    "the-unbound-rise-of-the-godslayer-647593": ["Fantasy"],
    "i-spoke-baby-dragon-and-won-everyone-over-628653": ["Fantasy"],
    "rejected-luna-is-the-alpha-queen-69fa0a97": ["Fantasy", "Romance", "Revenge"],
    "the-empresss-final-wish-6a06bb65": ["Royal", "Family"],
    "my-billionaire-boss-wont-let-me-quit-6a792e03": ["Romance"],  # tag RS: Romance, Billionaire, Workplace (material/rs/films/<slug>/info.json)
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
    cfg = dict(CFG, src=src)
    # OG phim là ảnh dọc 600x800: summary_large_image (khung ngang) sẽ cắt nát, dùng summary; home.jpg ngang giữ large
    tw = "summary_large_image" if img and img.endswith("home.jpg") else "summary"
    wh = (1200, 630) if img and img.endswith("home.jpg") else (600, 800)
    og = (f'<meta property="og:image" content="{BASE}{img}"><meta property="og:image:width" content="{wh[0]}">'
          f'<meta property="og:image:height" content="{wh[1]}"><meta name="twitter:card" content="{tw}">') if img else ""
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
{f'<link rel="canonical" href="{BASE}{path}">' if path else ''}{'<meta name="robots" content="noindex,follow">' if noindex else ''}
<meta name="theme-color" content="#0b0709"><link rel="icon" href="/img/logo-64.png">
<meta property="og:type" content="{'video.tv_show' if img and '/og/' in img and not img.endswith('home.jpg') else 'website'}"><meta property="og:site_name" content="Swoonflicks">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">{f'<meta property="og:url" content="{BASE}{path}">' if path else ''}{og}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<style>{CSS}</style>
<script>window.SF={json.dumps(cfg)}</script><script src="/assets/t.js" defer></script>{extra}
</head>'''


FOOT = '''<p class="ft">Swoonflicks shares free episodes of short dramas we love.<br>
Some links are affiliate links: we may earn a commission when you keep watching, at no extra cost to you.<br>
<a href="/privacy/">Privacy</a> · <a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>'''


def social():
    return '<p class="h3">Follow for new parts</p><nav class="soc">' + "".join(
        f'<a href="{u}" rel="noopener" target="_blank">{n}</a>' for n, u in SOCIAL) + "</nav>"


def card(f, big=False, lazy=True):
    img = f"/img/{f['slug']}-w.webp" if big else f"/img/{f['slug']}.webp"
    w, h = (720, 540) if big else (360, 480)
    return f'''<a class="cd{' big' if big else ''}" href="/{f['slug']}/" data-genre="{e('|'.join(f['genre']))}">
<img src="{img}" alt="{e(f['title'])} poster" width="{w}" height="{h}"{' loading="lazy"' if lazy else ' fetchpriority="high"' if big else ''} decoding="async">
<div class="in"><h2>{e(f['title'])}</h2><span class="go">Watch free {ARROW}</span></div></a>'''


JS_HUB = '''<script>(function(){var sel={genre:''},cards=[].slice.call(document.querySelectorAll('.grid .cd')),em=document.querySelector('.empty');
document.querySelectorAll('.chip').forEach(function(c){c.onclick=function(){var k=c.dataset.k;sel[k]=c.dataset.v;
document.querySelectorAll('.chip[data-k='+k+']').forEach(function(x){x.setAttribute('aria-pressed',x===c)});var n=0;
cards.forEach(function(d){var ok=(!sel.genre||d.dataset.genre.split('|').indexOf(sel.genre)>=0);d.hidden=!ok;if(ok)n++});
em.hidden=n>0;if(window.SFT)SFT.track('Filter',{key:k,value:c.dataset.v||'all'})}});
em.querySelector('.clr').onclick=function(){document.querySelectorAll('.chip[data-v=""]').forEach(function(c){c.click()})}})()</script>'''


def hub_page(films, path="/", src=""):
    ig = path != "/"
    genres = sorted({g for f in films for g in f["genre"]})
    chip = lambda k, v, lbl, on=False: f'<button type="button" class="chip" data-k="{k}" data-v="{e(v)}" aria-pressed="{str(on).lower()}">{e(lbl)}</button>'
    flt = ('<div class="flt"><div class="chips" role="group" aria-label="Filter by genre"><b aria-hidden="true">Genre</b>' + chip("genre", "", "All", True) + "".join(chip("genre", g, g) for g in genres) + "</div></div>")
    grid = "\n".join(card(f, big=(i == 0 and not ig), lazy=(i > 3)) for i, f in enumerate(films))
    desc = "Free episodes of the short dramas everyone is binging. Pick a drama and binge every free episode."
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "Swoonflicks", "url": f"{BASE}/", "description": desc},
          {"@context": "https://schema.org", "@type": "Organization", "name": "Swoonflicks", "url": f"{BASE}/",
           "logo": f"{BASE}/img/logo-128.png", "sameAs": [u for _, u in SOCIAL]},
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{BASE}/{f['slug']}/", "name": f["title"]} for i, f in enumerate(films)]}]
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if path == "/" else ""
    return head("Swoonflicks · Free short drama episodes", desc, "/", "/img/og/home.jpg", extra, noindex=(path != "/"), src=src) + f'''
<body><main class="wrap">
<header class="hd{' sm' if ig else ''}"><h1><img class="lk" src="/img/lockup.png" alt="Swoonflicks · Romance novels, now on screen" width="681" height="150"></h1>
<p class="tag">{"Find the drama you saw." if ig else "Tap a drama and watch every free episode."}</p></header>
{flt}<div class="grid">{grid}</div><div class="empty" hidden><p>No drama in this genre yet.</p><button type="button" class="chip clr">Show all</button></div>
{social()}{FOOT}</main>{JS_HUB}</body></html>'''


JS_FILM = '''<script>(function(){var b=document.body.dataset,pl=document.querySelector('.pl'),P=null,cur='',marks={},tick;
function T(n,p){if(window.SFT)SFT.track(n,Object.assign({film:b.film,title:b.title,app:b.app,video_id:cur},p||{}))}
function poll(){clearInterval(tick);tick=setInterval(function(){if(!P||!P.getDuration)return;var d=P.getDuration(),t=P.getCurrentTime();if(!d)return;
[25,50,75,95].forEach(function(m){var k=cur+m;if(!marks[k]&&t/d*100>=m){marks[k]=1;T('VideoProgress',{percent:m})}})},1000)}
var st=document.querySelector('.pst');function fail(){st.innerHTML='Could not load the player. <button type="button" class="chip">Retry</button> <a href="https://www.youtube.com/shorts/'+cur+'" target="_blank" rel="noopener"><u>Open on YouTube</u></a>';
st.querySelector('button').onclick=function(){var v=cur;P=null;var o=pl.querySelector('iframe,.vid');if(o)o.remove();start(v)}}
function start(v){cur=v;if(P){P.loadVideoById(v);return}st.textContent='Loading free part…';var host=document.createElement('div');host.className='vid';
[].forEach.call(pl.querySelectorAll('.play,.lbl'),function(x){x.remove()});pl.appendChild(host);
var go=function(){P=new YT.Player(host,{host:'https://www.youtube-nocookie.com',videoId:v,playerVars:{autoplay:1,playsinline:1,rel:0,modestbranding:1},
events:{onError:fail,onReady:function(e){var f=e.target.getIframe();f.title=b.title+' video';f.className='vid on';st.textContent='';f.focus()},onStateChange:function(s){if(s.data===1){if(!marks[cur+'p']){marks[cur+'p']=1;T('VideoPlay')}poll()}else clearInterval(tick)}}})};
if(window.YT&&YT.Player)go();else{window.onYouTubeIframeAPIReady=go;var s=document.createElement('script');s.src='https://www.youtube.com/iframe_api';s.onerror=fail;document.head.appendChild(s)}}
var btn=pl&&pl.querySelector('.play');if(btn)btn.onclick=function(){start(btn.dataset.v)};
document.querySelectorAll('.parts .chip').forEach(function(c){c.onclick=function(){document.querySelectorAll('.parts .chip').forEach(function(x){x.setAttribute('aria-pressed',x===c)});
start(c.dataset.v);pl.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'center'})}});
var bar=document.querySelector('.bar'),cta=document.querySelector('.cta');if(bar&&cta&&'IntersectionObserver'in window)
new IntersectionObserver(function(es){bar.classList.toggle('on',es[0].intersectionRatio<.9)},{threshold:[0,.9,1]}).observe(cta)})()</script>'''


def content(slug):
    # nội dung riêng từng phim: site/_src/content/<slug>.json (+ .seo.json), viết tay, có thể thiếu
    d = OUT / "_src" / "content"
    rd = lambda n: json.loads((d / n).read_text(encoding="utf-8")) if (d / n).exists() else {}
    return rd(f"{slug}.json"), rd(f"{slug}.seo.json")


def film_page(f, films):
    syn = f["syn"]
    ct, seo = content(f["slug"])
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
<p class="note" style="margin-top:10px">No free part on this site yet. Episodes are coming soon.</p>'''
    aff = lambda place: (f'href="{e(f["link"])}" target="_blank" rel="nofollow sponsored noopener" data-aff="{place}" '
                         f'data-film="{e(f["slug"])}" data-app="{e(f["app"])}" data-title="{e(f["title"])}"')
    more = "".join(card(o) for o in films if o is not f)
    ld = {"@context": "https://schema.org", "@type": "TVSeries", "name": f["title"], "description": cut(syn, 300),
          "image": f"{BASE}/img/og/{f['slug']}.jpg", "url": f"{BASE}/{f['slug']}/", "genre": f["genre"],
          "inLanguage": "en"}
    if yt:
        ld["trailer"] = {"@type": "VideoObject", "name": f"{f['title']} {yt[0][0]}", "embedUrl": f"https://www.youtube.com/embed/{yt[0][1]}",
                         "thumbnailUrl": f"https://i.ytimg.com/vi/{yt[0][1]}/hqdefault.jpg", "description": cut(syn, 200)}
        if yt[0][1] in YT_DATE:
            ld["trailer"]["uploadDate"] = YT_DATE[yt[0][1]]
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Swoonflicks", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": f["title"], "item": f"{BASE}/{f['slug']}/"}]}
    lds = [ld, bc]
    faq = ct.get("faq", [])
    if faq:  # FAQPage khớp đúng chữ hiển thị
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in faq]})
    extra = f'<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>'
    title = seo.get("title") or f"{f['title']} · Watch free | Swoonflicks"
    about = ""
    if ct.get("intro"):
        about = f'<section class="syn ab"><h2>Why watch</h2><p>{e(ct["intro"])}</p>' + (
            "<ul>" + "".join(f"<li>{e(x)}</li>" for x in ct.get("why", [])) + "</ul>" if ct.get("why") else "") + "</section>"
    faqh = ('<section class="syn faq"><h2>Questions</h2>' + "".join(
        f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in faq) + "</section>") if faq else ""
    return head(title, seo.get("description") or cut(syn, 155), f"/{f['slug']}/", f"/img/og/{f['slug']}.jpg", extra) + f'''
<body data-film="{e(f['slug'])}" data-title="{e(f['title'])}" data-app="{e(f['app'])}"><main class="wrap">
<div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="118" height="26"></a></div>
<div class="ttl"><h1>{metal(f['title'])}</h1><p class="meta">{' · '.join(e(x) for x in f['genre'])}</p></div>
{player}<p class="pst" role="status"></p>
<a class="cta" {aff("main")}><span>Continue watching<small>Unlock the next episodes</small></span>{EXT}</a>
<p class="note">Affiliate link: we may earn a commission.</p>
{about}<details class="syn"><summary>The story</summary><p>{e(syn)}</p></details>
{faqh}
<p class="h3">More dramas</p><div class="more">{more}</div>
{social()}{FOOT}<div class="pad"></div></main>
<div class="bar"><a class="cta" {aff("sticky")}><span>Continue watching</span>{EXT}</a></div>{JS_FILM}</body></html>'''


def privacy_page():
    return head("Privacy · Swoonflicks", "How Swoonflicks uses cookies and measurement.", "/privacy/") + '''
<body><main class="wrap doc"><div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="118" height="26"></a></div>
<h1>Privacy</h1>
<p>Swoonflicks is a fan site that shares free episodes of short dramas and links to the apps where you can watch the rest.</p>
<h2>What we measure</h2>
<ul><li>Which drama pages you open, whether you play the free episode and how far you watch.</li>
<li>Whether you tap a link to a drama app, and which page or social profile brought you here (from the link's utm or click id).</li></ul>
<h2>Tools we use</h2>
<p>When enabled, Google Analytics, the Meta Pixel and the TikTok Pixel receive these events so we can count visits and show
our videos to people who are likely to enjoy them. Free episodes play through YouTube's privacy-enhanced mode (youtube-nocookie.com)
and only load when you press play; pressing play also loads YouTube's player script from youtube.com.</p>
<h2>Your choice</h2>
<p>Visitors in the EU and UK are asked before any of these tools load. You can change your answer at any time:
<button type="button" class="chip" onclick="try{localStorage.removeItem('sf_consent')}catch(e){}location.reload()">Cookie settings</button></p>
<h2>Affiliate links</h2>
<p>Links to drama apps are affiliate links. If you watch or subscribe there, we may earn a commission at no extra cost to you.
What you do inside those apps is covered by their own privacy policies.</p>
<h2>Contact</h2><p><a href="mailto:admin@swoonflicks.com">admin@swoonflicks.com</a></p>
''' + FOOT + "</main></body></html>"


def invite_page(inv):
    """Trang /invite/: mã mời làm affiliate (RS Boost, DramaCPS...). Chỉ mục có code thật trong config.json "invite" mới hiện."""
    rows = "".join(f'''<section class="syn inv"><h2>{html.escape(i["program"])}</h2>
<p>{html.escape(i.get("note", ""))}</p>
<div class="code"><b>{html.escape(i["code"])}</b><button type="button" data-copy="{html.escape(i["code"])}" data-prog="{html.escape(i["program"])}">Copy</button></div>
{f'<a class="cta" href="{html.escape(i["signup"])}" rel="noopener" target="_blank">Sign up for {html.escape(i["program"])} {ARROW}</a>' if i.get("signup") else ""}
{f'<p class="note"><a href="{html.escape(i["guide"])}"><u>Step-by-step guide and FAQ</u></a></p>' if i.get("guide") else ""}
</section>''' for i in inv)
    gl = [g for g in GUIDES if g.get("lang", "en") == "en"]
    if gl:
        rows += '<section class="syn ab"><h2>Guides</h2><ul>' + "".join(
            f'<li><a href="{e(g["path"])}"><u>{e(g["h1"])}</u></a></li>' for g in gl) + "</ul></section>"
    return head("Invitation codes · Swoonflicks", "Invitation codes to join short drama affiliate programs like RS Boost.", "/invite/") + f'''
<body><main class="wrap"><div class="top"><a class="back" href="/">‹ All dramas</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="118" height="26"></a></div>
<div class="ttl"><h1>{metal("Invitation codes")}</h1></div>
<p class="tag" style="text-align:center">For creators who want to earn by sharing short dramas. These affiliate programs ask for an invitation code when you sign up. Copy ours and paste it in the sign-up form.</p>
<p class="note" style="text-align:center">This is a creator sign-up code, not a viewer code: it does not unlock episodes or give coins. Earnings depend on each program's own terms.</p>
{rows}{FOOT}</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-copy]');if(!b)return;
navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);b.textContent='Copied';
window.SFT&&SFT.track('CopyInvite',{{program:b.dataset.prog}})}})</script></body></html>'''


# ---------- trang guide (_src/guides/*.json): invite code RS Boost EN/ES/PT + bài hướng dẫn ----------
# Chữ thường, build tự escape. Khối "code" lấy code thật từ config.json "invite" theo tên program (không có code thì bỏ khối).
# Không số coin/hoa hồng nếu không có link nguồn trong "sources".
UI = {"en": dict(back="‹ All dramas", copy="Copy", copied="Copied", checked="Last checked", src="Sources", faq="Questions",
                 code="invitation code", signup="Open {p} sign-up", more="Dramas we share", rel="Related guides"),
      "es": dict(back="‹ Todos los dramas", copy="Copiar", copied="Copiado", checked="Última revisión", src="Fuentes", faq="Preguntas",
                 code="código de invitación", signup="Abrir el registro de {p}", more="Dramas que compartimos", rel="Guías relacionadas"),
      "pt": dict(back="‹ Todos os dramas", copy="Copiar", copied="Copiado", checked="Última revisão", src="Fontes", faq="Perguntas",
                 code="código de convite", signup="Abrir o cadastro do {p}", more="Dramas que compartilhamos", rel="Guias relacionados")}


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
    if inv:
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
    srch = (f'<h2>{e(u["src"])}</h2><ul>' + "".join(f'<li><a href="{e(x)}" rel="noopener" target="_blank"><u>{e(x)}</u></a></li>' for x in srcs) + "</ul>") if srcs else ""
    fl = [f for f in films if f["app"] == g.get("films_app")] if g.get("films_app") else []
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
    extra = altl + f'<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>'
    return head(g["title"], g["description"], g["path"], "/img/og/home.jpg", extra, lang=lang) + f'''
<body><main class="wrap doc"><div class="top"><a class="back" href="/">{e(u["back"])}</a><a class="brand" href="/"><img src="/img/lockup-sm.png" alt="Swoonflicks" width="118" height="26"></a></div>
<h1>{e(g["h1"])}</h1>{f'<p>{e(g["lead"])}</p>' if g.get("lead") else ""}
{codebox}{body}{faqh}{relh}{srch}
{f'<p class="note">{e(u["checked"])}: {e(g["checked"])}</p>' if g.get("checked") else ""}
{moreh}{FOOT}</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-copy]');if(b){{
navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy);b.textContent=b.dataset.done||'Copied';
window.SFT&&SFT.track('CopyInvite',{{program:b.dataset.prog,page:location.pathname}});return}}
var s=e.target.closest('[data-signup]');if(s&&window.SFT)SFT.track('ClickSignup',{{program:s.dataset.signup,page:location.pathname}})}})</script></body></html>'''


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
    if r["ready"] != "CO" or not link or not d:
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

# ---------- dọn bản cũ (giữ .git, CNAME) ----------
for p in OUT.iterdir():
    if p.is_dir() and ((p / ".gen").exists() or p.name in ("img", "assets")):
        shutil.rmtree(p, ignore_errors=True)  # OneDrive hay khoá thư mục rỗng: xoá được file là đủ
for p in ("index.html", "404.html", "sitemap.xml", "robots.txt", "llms.txt"):
    (OUT / p).unlink(missing_ok=True)
(OUT / "img" / "og").mkdir(parents=True, exist_ok=True)
(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(HUB / "t.js", OUT / "assets" / "t.js")

# ---------- ảnh ----------
logo = Image.open(SD / "brand" / "logo-mark-1024-transparent.png")
for s in (64, 128):
    im = logo.copy(); im.thumbnail((s, s)); im.save(OUT / "img" / f"logo-{s}.png", optimize=True)
lk = Image.open(SD / "brand" / "logo-lockup-transparent.png")  # 1362x300, gồm tagline
lk.resize((681, 150), Image.LANCZOS).save(OUT / "img" / "lockup.png", optimize=True)
lk.crop((0, 0, 1362, 200)).resize((354, 52), Image.LANCZOS).save(OUT / "img" / "lockup-sm.png", optimize=True)  # bỏ tagline, nét 2x cho cao 26px


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
for k, src in BIO.items():
    write(f"{k}/index.html", hub_page(films, f"/{k}/", src), gen=True)
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
write("llms.txt", "# Swoonflicks\n\n> Romance novels, now on screen: free episodes of English short dramas.\n\n## Dramas\n" +
      "".join(f"- [{f['title']}]({BASE}/{f['slug']}/): {', '.join(f['genre'])} drama\n" for f in films) +
      f"\n## Creators\n- [Invitation codes]({BASE}/invite/): creator sign-up code for short drama affiliate programs\n" +
      ("\n## Guides\n" + "".join(f"- [{g['h1']}]({BASE}{g['path']}) ({g.get('lang', 'en')}): {g['description']}\n" for g in GUIDES) if GUIDES else ""))
(OUT / ".nojekyll").write_text("")
print("ok", len(films), "phim:", ", ".join(f["slug"] for f in films))
