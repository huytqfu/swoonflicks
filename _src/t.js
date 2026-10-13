/* Swoonflicks tracking: GA4 + Meta Pixel + TikTok Pixel, một cửa SFT.track().
   Cấu hình: window.SF = {ga4, meta, tiktok, src} do build.py bơm từ hub/config.json. ID trống thì nền đó không tải.
   Mục đích (MASTER-PLAN-v2 §6): tệp retarget/lookalike người xem video + bấm link, đếm click theo phim/nguồn. Không tối ưu purchase.
   Mỗi sự kiện có event_id để sau này gửi trùng qua CAPI / Events API (khử trùng). ?debug=1 in sự kiện ra console. */
(function (W, D) {
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
  var EU = /^Europe\//.test(tz) || /^Atlantic\/(Reykjavik|Canary|Madeira|Azores|Faroe)/.test(tz);
  var consent = EU ? get(LS, 'sf_consent') : 'yes', loaded = false, queue = [];

  function script(src) { var s = D.createElement('script'); s.async = true; s.src = src; D.head.appendChild(s) }
  function load() {
    if (loaded) return; loaded = true;
    if (C.ga4) {
      W.dataLayer = W.dataLayer || []; W.gtag = function () { dataLayer.push(arguments) };
      gtag('js', new Date()); gtag('config', C.ga4, { transport_type: 'beacon' });
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
  var GA = { ViewContent: 'view_film', ClickAffiliate: 'click_affiliate', VideoPlay: 'video_start', VideoProgress: 'video_progress' };
  function send(name, p, id) {
    var item = p.film ? [{ content_id: p.film, content_name: p.title, content_type: 'product', content_category: p.app }] : [];
    if (W.gtag && C.ga4) gtag('event', GA[name] || name, Object.assign({ event_id: id }, p));
    if (W.fbq && C.meta) {
      if (name === 'ViewContent') fbq('track', 'ViewContent', Object.assign({ content_ids: [p.film], content_name: p.title, content_type: 'product', content_category: p.app }, p), { eventID: id });
      else fbq('trackCustom', name, p, { eventID: id });
    }
    if (W.ttq && C.tiktok) {
      var tp = Object.assign({ contents: item, content_type: 'product' }, p);
      ttq.track(name === 'ClickAffiliate' ? 'ClickButton' : name, tp, { event_id: id });
    }
  }
  function track(name, params) {
    var p = Object.assign(attr(), params || {}), id = uid();
    (W.sfLog = W.sfLog || []).push([name, p, id]);
    if (DEBUG) console.log('[SFT]', name, p);
    if (consent !== 'yes') { if (consent !== 'no') queue.push([name, p, id]); return }
    loaded ? send(name, p, id) : queue.push([name, p, id]);
  }
  W.SFT = { track: track };

  function banner() {
    var b = D.createElement('div'); b.className = 'cb'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-label', 'Cookie consent');
    b.innerHTML = 'We use cookies to measure which dramas you watch and to show you relevant ads. <a href="/privacy/">Privacy</a>' +
      '<div><button type="button" class="n">Decline</button><button type="button" class="y">Accept</button></div>';
    b.querySelector('.y').onclick = function () { put(LS, 'sf_consent', 'yes'); consent = 'yes'; b.remove(); load() };
    b.querySelector('.n').onclick = function () { put(LS, 'sf_consent', 'no'); consent = 'no'; queue.length = 0; b.remove() };
    D.body.appendChild(b);
  }

  // 4. Gắn tự động: trang phim -> ViewContent; link có data-aff -> ClickAffiliate (link CPS giữ nguyên, không cloak)
  function film() { var b = D.body.dataset; return b.film ? { film: b.film, title: b.title, app: b.app } : {} }
  function boot() {
    if (consent === 'yes') load(); else if (consent !== 'no') banner();
    if (D.body.dataset.film) track('ViewContent', film());
    D.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-aff]');
      if (!a) return;
      track('ClickAffiliate', Object.assign(film(), { film: a.dataset.film || film().film, title: a.dataset.title || film().title,
        app: a.dataset.app || film().app, placement: a.dataset.aff, link_url: a.href }));
    }, true);
  }
  D.readyState === 'loading' ? D.addEventListener('DOMContentLoaded', boot) : boot();
})(window, document);
