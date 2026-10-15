/* Swoonflicks tracking: GA4 + Meta Pixel + TikTok Pixel, một cửa SFT.track().
   Cấu hình: window.SF = {ga4, meta, tiktok, src} do build.py bơm từ hub/config.json. ID trống thì nền đó không tải.
   Mục đích (MASTER-PLAN-v2 §6): tệp retarget/lookalike người xem video + bấm link, đếm click theo phim/nguồn. Không tối ưu purchase.
   Mỗi sự kiện có event_id để sau này gửi trùng qua CAPI / Events API (khử trùng). ?debug=1 in sự kiện ra console. */
(function (W, D) {
  if (W.SFT) return; // nạp 2 lần = mọi sự kiện bắn đôi
  var C = W.SF || {}, LS, SS, q = new URLSearchParams(location.search);
  try { LS = W.localStorage; SS = W.sessionStorage } catch (e) {}
  function get(s, k) { try { return s && s.getItem(k) } catch (e) { return null } }
  function put(s, k, v) { try { s && s.setItem(k, v) } catch (e) {} }
  var DEBUG = q.has('debug');

  // 1. Nguồn: giữ utm + click id lần chạm đầu trong phiên, gắn vào mọi sự kiện
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'ttclid', 'gclid'];
  KEYS.forEach(function (k) { var v = q.get(k); if (v && !get(SS, 'sf_' + k)) put(SS, 'sf_' + k, v.slice(0, 200)) });
  if (!get(SS, 'sf_utm_source') && C.src) { put(SS, 'sf_utm_source', C.src); put(SS, 'sf_utm_medium', 'bio') }
  if (!get(SS, 'sf_utm_source') && D.referrer && D.referrer.indexOf(location.host) < 0) {
    try { put(SS, 'sf_ref', new URL(D.referrer).hostname) } catch (e) {}
  }
  if (!get(SS, 'sf_landing')) put(SS, 'sf_landing', location.pathname);
  function attr() {
    var o = {};
    KEYS.concat(['ref', 'landing']).forEach(function (k) { var v = get(SS, 'sf_' + k); if (v) o[k] = v });
    return o;
  }
  function uid() { return W.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now() + '-' + Math.random().toString(36).slice(2) }

  // 2. Đồng ý cookie: chỉ hỏi khách múi giờ châu Âu/UK; nơi khác bật luôn. Chưa trả lời = chưa tải pixel, sự kiện xếp hàng.
  var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '' } catch (e) {}
  // múi trống / Etc/* (VPN, UTC) coi như EU cho chắc; thêm Síp, Ceuta, Svalbard, lãnh thổ hải ngoại Pháp
  var EU = !tz || /^Etc\//.test(tz) || /^Europe\//.test(tz) || /^Atlantic\/(Reykjavik|Canary|Madeira|Azores|Faroe)/.test(tz) ||
    /^(Asia\/(Nicosia|Famagusta)|Africa\/Ceuta|Arctic\/Longyearbyen|Indian\/(Reunion|Mayotte)|America\/(Martinique|Guadeloupe|Cayenne|Marigot|St_Barthelemy))$/.test(tz);
  var ANY = !!(C.ga4 || C.meta || C.tiktok);
  var consent = EU ? get(LS, 'sf_consent') : 'yes', loaded = false, queue = [];

  function script(src) { var s = D.createElement('script'); s.async = true; s.src = src; D.head.appendChild(s) }
  function load() {
    if (loaded) return; loaded = true;
    if (C.ga4) {
      W.dataLayer = W.dataLayer || []; W.gtag = function () { dataLayer.push(arguments) };
      // load() chỉ chạy sau khi đồng ý hoặc ngoài EU, nên mặc định granted; tín hiệu v2 cần cho remarketing Google Ads ở EEA
      gtag('consent', 'default', { ad_storage: 'granted', analytics_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted' });
      var u = new URL(location.href); u.searchParams.delete('fbclid'); u.searchParams.delete('ttclid');
      gtag('js', new Date()); gtag('config', C.ga4, { transport_type: 'beacon', page_location: u.href });
      script('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(C.ga4));
    }
    if (C.meta) {
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments) };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
        s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s) }(W, D, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', C.meta); fbq('track', 'PageView', {}, { eventID: uid() });
    }
    if (C.tiktok) {
      !function (w, d, t) { w.TiktokAnalyticsObject = t; var ttq = w[t] = w[t] || [];
        ttq.methods = ['page', 'track', 'identify', 'instances', 'debug', 'on', 'off', 'once', 'ready', 'alias', 'group', 'enableCookie', 'disableCookie', 'holdConsent', 'revokeConsent', 'grantConsent'];
        ttq.setAndDefer = function (t, e) { t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))) } };
        for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]);
        ttq.instance = function (t) { for (var e = ttq._i[t] || [], n = 0; n < ttq.methods.length; n++) ttq.setAndDefer(e, ttq.methods[n]); return e };
        ttq.load = function (e, n) { var r = 'https://analytics.tiktok.com/i18n/pixel/events.js'; ttq._i = ttq._i || {}; ttq._i[e] = []; ttq._i[e]._u = r;
          ttq._t = ttq._t || {}; ttq._t[e] = +new Date; ttq._o = ttq._o || {}; ttq._o[e] = n || {};
          var s = d.createElement('script'); s.type = 'text/javascript'; s.async = !0; s.src = r + '?sdkid=' + e + '&lib=' + t;
          var f = d.getElementsByTagName('script')[0]; f.parentNode.insertBefore(s, f) };
        ttq.load(C.tiktok); ttq.page();
      }(W, D, 'ttq');
    }
    queue.splice(0).forEach(function (a) { send(a[0], a[1], a[2]) });
  }

  // 3. Gửi: tên sự kiện chung -> tên chuẩn từng nền
  var TT = { ViewContent: 'ViewContent', ClickAffiliate: 'ClickButton', RequestInvite: 'Lead' }; // chỉ 3 sự kiện này đi Events API
  var FB = { ViewContent: 'ViewContent', ClickAffiliate: 'ClickAffiliate', RequestInvite: 'Lead' }; // 3 sự kiện đi Conversions API; chỉ ClickAffiliate là custom
  var GA = { ViewContent: 'view_item', ClickAffiliate: 'click_affiliate', RequestInvite: 'generate_lead', VideoPlay: 'video_start', VideoProgress: 'video_progress', Filter: 'filter_select' };
  function send(name, p0, id) {
    // click id không gửi thành tham số (pixel Meta/TikTok tự đọc từ URL), tránh nổ cardinality GA4
    var p = Object.assign({}, p0); delete p.fbclid; delete p.ttclid; delete p.gclid;
    var ads = name !== 'Filter'; // lọc kệ chỉ đếm ở GA4, không đổ rác vào tệp quảng cáo
    var item = p.film ? [{ content_id: p.film, content_name: p.title, content_type: 'product', content_category: p.app }] : [];
    if (W.gtag && C.ga4) gtag('event', GA[name] || name, Object.assign({ event_id: id }, p));
    if (W.fbq && C.meta && ads) {
      // Meta không có event chuẩn cho "bấm link ra ngoài": Lead là gửi thông tin liên hệ, nên giữ cho form mã mời; bấm link CPS = custom ClickAffiliate
      // (developers.facebook.com/docs/meta-pixel/reference#standard-events). Muốn tối ưu ads theo click thì tạo custom conversion từ event này.
      if (name === 'ViewContent') fbq('track', 'ViewContent', Object.assign({ content_ids: [p.film], content_name: p.title, content_type: 'product', content_category: p.app }, p), { eventID: id });
      else if (name === 'RequestInvite') fbq('track', 'Lead', p, { eventID: id });
      else fbq('trackCustom', name, p, { eventID: id });
      // Conversions API: bản sao cùng event_name + event_id gửi Worker /fb-event để Meta khử trùng (developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events)
      if (C.fbapi && FB[name]) beacon(C.fbapi, { event: FB[name], event_id: id, url: location.href, content_id: p.film || undefined,
        timestamp: Math.floor(Date.now() / 1000), referrer: D.referrer || undefined, fbp: cookie('_fbp'), fbc: cookie('_fbc') || fbc() });
    }
    if (W.ttq && C.tiktok && ads) {
      // tên chuẩn TikTok: click link CPS = ClickButton (TikTok để tới 2027), gửi form mã mời = Lead (tên mới của SubmitForm từ 05/2025; pixel và API cùng tên để khử trùng)
      var tn = TT[name] || name, tp = Object.assign({ contents: item, content_type: 'product' }, p);
      ttq.track(tn, tp, { event_id: id });
      // Events API: bản sao cùng event + event_id gửi Worker để TikTok khử trùng (help: ads.tiktok.com/help/article/event-deduplication).
      // sendBeacon text/plain: không preflight, sống qua cú chuyển trang, không chặn click.
      if (C.ttapi && TT[name]) {
        beacon(C.ttapi, { event: tn, event_id: id, url: location.href, content_id: p.film || undefined,
          timestamp: Math.floor(Date.now() / 1000), referrer: D.referrer || undefined,
          ttclid: get(SS, 'sf_ttclid') || undefined, ttp: cookie('_ttp') });
      }
    }
  }
  function cookie(k) { var m = D.cookie.match(new RegExp('(?:^|; )' + k + '=([^;]*)')); return m ? decodeURIComponent(m[1]) : undefined }
  // fbc chuẩn Meta: fb.1.<ms lần chạm>.<fbclid>, dùng khi pixel chưa kịp đặt cookie _fbc
  function fbc() { var v = get(SS, 'sf_fbclid'); return v ? 'fb.1.' + Date.now() + '.' + v : undefined }
  // sendBeacon text/plain: không preflight, sống qua cú chuyển trang, không chặn click
  function beacon(u, o) { var b = JSON.stringify(o);
    try { navigator.sendBeacon ? navigator.sendBeacon(u, new Blob([b], { type: 'text/plain' })) : fetch(u, { method: 'POST', body: b, keepalive: true, mode: 'no-cors' }) } catch (e) {} }
  function track(name, params) {
    var p = Object.assign(attr(), params || {}), id = uid();
    (W.sfLog = W.sfLog || []).push([name, p, id]);
    if (DEBUG) console.log('[SFT]', name, p);
    if (consent !== 'yes') { if (consent !== 'no') queue.push([name, p, id]); return }
    loaded ? send(name, p, id) : queue.push([name, p, id]);
  }
  // rút lại đồng ý (GDPR 7(3)): nút "Cookie settings" ở trang privacy gọi SFT.reset()
  W.SFT = { track: track, reset: function () { try { LS.removeItem('sf_consent') } catch (e) {} location.reload() } };

  function banner() {
    var b = D.createElement('div'); b.className = 'cb'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-label', 'Cookie consent');
    b.innerHTML = 'We use cookies to measure which dramas you watch and to show you relevant ads. <a href="/privacy/">Privacy</a>' +
      '<div><button type="button" class="n">Decline</button><button type="button" class="y">Accept</button></div>';
    b.querySelector('.y').onclick = function () { put(LS, 'sf_consent', 'yes'); consent = 'yes'; b.remove(); load() };
    b.querySelector('.n').onclick = function () { put(LS, 'sf_consent', 'no'); consent = 'no'; queue.length = 0; b.remove() };
    D.body.appendChild(b); b.querySelector('.y').focus({ preventScroll: true });
  }

  // 4. Gắn tự động: trang phim -> ViewContent; link có data-aff -> ClickAffiliate (link CPS giữ nguyên, không cloak)
  function film() { var b = D.body.dataset; return b.film ? { film: b.film, title: b.title, app: b.app } : {} }
  function boot() {
    if (consent === 'yes') load(); else if (consent !== 'no' && ANY) banner();
    if (D.body.dataset.film) track('ViewContent', film());
    D.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-aff]');
      if (!a) return;
      track('ClickAffiliate', Object.assign(film(), { film: a.dataset.film || film().film, title: a.dataset.title || film().title,
        app: a.dataset.app || film().app, placement: a.dataset.aff, link_url: a.href,
        episode: a.dataset.ep ? +a.dataset.ep : undefined }));
    }, true);
  }
  D.readyState === 'loading' ? D.addEventListener('DOMContentLoaded', boot) : boot();
})(window, document);
